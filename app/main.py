from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query
from fastapi.responses import HTMLResponse
from app.websocket.manager import ConnectionManager
from app.database import create_pool, close_pool,init_db
from app.redis_client import create_redis, close_redis, publish, is_rate_limited
from app import database, redis_client
from app.auth.routes import router as auth_router
from app.rooms.routes import router as rooms_router
from app.auth.utils import decode_token
import json, logging, asyncio

logging.basicConfig(level=logging.INFO)
app = FastAPI(title="Real-Time Chat Server")
manager = ConnectionManager()

app.include_router(auth_router)
app.include_router(rooms_router)

@app.on_event("startup")
async def startup():
    await create_pool()
    await create_redis()
    await init_db()

@app.on_event("shutdown")
async def shutdown():
    await close_pool()
    await close_redis()

@app.get("/health")
async def health():
    return {"status": "ok"}

async def redis_listener(room_id: int, websocket: WebSocket):
    pubsub = redis_client.redis_subscriber.pubsub()
    await pubsub.subscribe(f"room:{room_id}")
    try:
        async for message in pubsub.listen():
            if message["type"] == "message":
                try:
                    await websocket.send_text(message["data"])
                except Exception:
                    break
    except asyncio.CancelledError:
        pass
    except Exception as e:
        logging.error(f"Redis listener error: {e}")
    finally:
        try:
            await pubsub.unsubscribe(f"room:{room_id}")
        except Exception:
            pass

@app.websocket("/ws/{room_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    room_id: int,
    token: str = Query(...)
):
    payload = decode_token(token)
    if not payload:
        await websocket.close(code=1008)
        return

    username = payload["username"]
    user_id = payload["user_id"]

    await manager.connect(websocket, str(room_id))

    await publish(f"room:{room_id}", json.dumps({
        "type": "online",
        "username": username,
        "room_id": room_id,
        "online_count": manager.get_room_count(str(room_id))
    }))

    listener_task = asyncio.create_task(redis_listener(room_id, websocket))

    try:
        while True:
            data = await websocket.receive_text()

            try:
                event = json.loads(data)
                event_type = event.get("type", "message")
            except json.JSONDecodeError:
                event_type = "message"
                event = {"message": data}

            if event_type == "typing":
                await publish(f"room:{room_id}", json.dumps({
                    "type": "typing",
                    "username": username,
                    "room_id": room_id
                }))

            elif event_type == "message":
                content = event.get("message", "")
                if not content.strip():
                    continue

                # Check rate limit
                if await is_rate_limited(user_id):
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "message": "⚠️ You are sending too many messages. Slow down!"
                    }))
                    continue

                # Save to DB
                try:
                    async with database.pool.acquire() as conn:
                        async with conn.cursor() as cur:
                            await cur.execute(
                                "INSERT INTO messages (room_id, user_id, content) VALUES (%s, %s, %s)",
                                (room_id, user_id, content)
                            )
                except Exception as e:
                    logging.error(f"DB insert error: {e}")
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "message": "Failed to save message. Please try again."
                    }))
                    continue

                # Publish to Redis
                try:
                    await publish(f"room:{room_id}", json.dumps({
                        "type": "message",
                        "username": username,
                        "user_id": user_id,
                        "message": content,
                        "room_id": room_id
                    }))
                except Exception as e:
                    logging.error(f"Redis publish error: {e}")

    except WebSocketDisconnect:
        listener_task.cancel()
        manager.disconnect(websocket, str(room_id))
        try:
            await publish(f"room:{room_id}", json.dumps({
                "type": "offline",
                "username": username,
                "room_id": room_id,
                "online_count": manager.get_room_count(str(room_id))
            }))
        except Exception:
            pass

    except Exception as e:
        logging.error(f"Unexpected WebSocket error: {e}")
        listener_task.cancel()
        manager.disconnect(websocket, str(room_id))

@app.get("/test-client", response_class=HTMLResponse)
async def test_client():
    return """
    <!DOCTYPE html><html><body>
    <h3>Step 1 — Login</h3>
    <input id="uname" placeholder="username" value="lokesh"/>
    <input id="pass" placeholder="password" value="test123"/>
    <button onclick="login()">Login</button>
    <span id="token_status"></span>

    <h3>Step 2 — Connect to Room</h3>
    <input id="room" placeholder="room id" value="1"/>
    <button onclick="connect()">Connect</button>
    <button onclick="loadHistory()">Load History</button><br><br>

    <div id="typing_indicator" style="color:gray;font-style:italic;height:20px"></div>
    <input id="msg" placeholder="type a message..." style="width:300px"/>
    <button onclick="send()">Send</button><br><br>

    <div id="online_list" style="color:green;margin-bottom:8px"></div>
    <div id="log" style="height:300px;overflow-y:auto;border:1px solid #ccc;padding:10px;font-family:monospace"></div>

    <script>
        let ws, token;
        let typing = false;
        let typingTimer;
        let onlineUsers = new Set();
        let retryCount = 0;
        const maxRetries = 5;

        function log(t, c='black'){
            const d = document.getElementById('log');
            d.innerHTML += `<p style="color:${c};margin:2px">${t}</p>`;
            d.scrollTop = d.scrollHeight;
        }

        function updateOnlineList(){
            document.getElementById('online_list').innerText =
                ' Online: ' + [...onlineUsers].join(', ');
        }

        async function login(){
            const res = await fetch(`${window.location.origin}/auth/login`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({username: uname.value, password: pass.value})
            });
            const data = await res.json();
            if(data.access_token){
                token = data.access_token;
                document.getElementById('token_status').innerText = ' Logged in as ' + data.username;
            } else {
                document.getElementById('token_status').innerText = ' Login failed';
            }
        }

        async function loadHistory(){
            if(!token){ log('Login first','red'); return; }
            const res = await fetch(`${window.location.origin}/rooms/${room.value}/messages?token=${token}`);
            const data = await res.json();
            log('--- Chat History ---', 'gray');
            data.forEach(m => log(` ${m.username}: ${m.content} (${m.created_at})`));
            log('--- Live ---', 'gray');
        }

        function connect(){
            if(!token){ log('Login first','red'); return; }
            ws = new WebSocket(`ws://${window.location.host}/ws/${room.value}?token=${token}`);
            ws.onopen = ()=>{
                log(' Connected','green');
                retryCount = 0;
            };
            ws.onmessage = e=>{
                const d = JSON.parse(e.data);
                if(d.type === 'message'){
                    log(` ${d.username}: ${d.message}`);
                    document.getElementById('typing_indicator').innerText = '';
                } else if(d.type === 'error'){
                    log(`${d.message}`, 'orange');
                } else if(d.type === 'typing'){
                    document.getElementById('typing_indicator').innerText = `✏️ ${d.username} is typing...`;
                    clearTimeout(typingTimer);
                    typingTimer = setTimeout(()=>{
                        document.getElementById('typing_indicator').innerText = '';
                    }, 2000);
                } else if(d.type === 'online'){
                    onlineUsers.add(d.username);
                    updateOnlineList();
                    log(` ${d.username} joined (online: ${d.online_count})`, 'green');
                } else if(d.type === 'offline'){
                    onlineUsers.delete(d.username);
                    updateOnlineList();
                    log(` ${d.username} left (online: ${d.online_count})`, 'red');
                } else if(d.type === 'system'){
                    log(` ${d.message}`, 'blue');
                }
            };
            ws.onclose = ()=>{
                log(' Disconnected','red');
                // Auto reconnect
                if(retryCount < maxRetries){
                    retryCount++;
                    log(` Reconnecting... attempt ${retryCount}/${maxRetries}`, 'gray');
                    setTimeout(connect, 3000);
                } else {
                    log(' Max retries reached. Please refresh.', 'red');
                }
            };
        }

        function send(){
            const msg = document.getElementById('msg').value.trim();
            if(ws && msg){
                ws.send(JSON.stringify({ type: 'message', message: msg }));
                document.getElementById('msg').value = '';
            }
        }

        document.getElementById('msg').addEventListener('keyup', function(e){
            if(e.key === 'Enter'){ send(); return; }
            if(ws && !typing){
                typing = true;
                ws.send(JSON.stringify({ type: 'typing' }));
                setTimeout(()=> typing = false, 2000);
            }
        });
    </script>
    </body></html>
    """