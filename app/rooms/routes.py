from fastapi import APIRouter,HTTPException,Depends,Query
from app.rooms.schemas import CreateRoomRequest,RoomResponse
from app.auth.utils import decode_token,get_current_user
from app.database import get_db

router=APIRouter(prefix="/rooms",tags=["rooms"])

async def get_current_user(token: str = Query(...)):
    payload=decode_token(token)
    if not payload:
        raise HTTPException(status_code=401,detail="Invalid Token")
    return payload

@router.post("/", response_model=RoomResponse)
async def create_room(
    body: CreateRoomRequest,
    user=Depends(get_current_user),
    cur=Depends(get_db)
):
    await cur.execute("SELECT id FROM rooms WHERE name = %s", (body.name,))
    if await cur.fetchone():
        raise HTTPException(status_code=400, detail="Room name already exists")

    await cur.execute(
        "INSERT INTO rooms (name, description, created_by) VALUES (%s, %s, %s)",
        (body.name, body.description, user["user_id"])
    )
    room_id = cur.lastrowid

    await cur.execute("SELECT * FROM rooms WHERE id = %s", (room_id,))
    room = await cur.fetchone()
    return room

@router.get("/", response_model=list[RoomResponse])
async def list_rooms(
    user=Depends(get_current_user),
    cur=Depends(get_db)
):
    await cur.execute("SELECT * FROM rooms ORDER BY created_at DESC")
    rooms = await cur.fetchall()
    return rooms

@router.get("/{room_id}/messages")
async def get_messages(
    room_id: int,
    limit: int=50,
    user=Depends(get_current_user),
    cur=Depends(get_db)
    
):
    
    await cur.execute("SELECT id FROM rooms WHERE id =%s",(room_id,))
    if not await cur.fetchone():
        raise HTTPException(status_code=404,detail="Room not found")
    
    await cur.execute("""
                      SELECT m.id,m.content,m.created_at,m.room_id,u.username
                      FROM messages m
                      JOIN users u ON m.user_id=u.id
                      WHERE m.room_id=%s
                      ORDER BY m.created_at DESC
                      LIMIT %s
                      """,(room_id,limit))
    messages=await cur.fetchall()
    messages.reverse()
    return messages
    
        