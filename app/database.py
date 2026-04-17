import aiomysql
import asyncio
from app.config import Settings

pool = None

async def create_pool():
    global pool
    retries = 10
    for i in range(retries):
        try:
            pool = await aiomysql.create_pool(
                host=Settings.DB_HOST,
                port=Settings.DB_PORT,
                user=Settings.DB_USER,
                password=Settings.DB_PASSWORD,
                db=Settings.DB_NAME,
                minsize=2,
                maxsize=10,
                autocommit=True,
                cursorclass=aiomysql.DictCursor,
                connect_timeout=10
            )
            print(" DB pool created")
            return
        except Exception as e:
            print(f"DB connection attempt {i+1}/{retries} failed: {e}")
            await asyncio.sleep(5)
    raise Exception("Could not connect to MySQL after multiple retries")

async def init_db():
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute("""
                CREATE TABLE IF NOT EXISTS users(
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            await cur.execute("""
                CREATE TABLE IF NOT EXISTS rooms(
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100) UNIQUE NOT NULL,
                    description VARCHAR(255),
                    created_by INT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (created_by) REFERENCES users(id)
                )
            """)
            await cur.execute("""
                CREATE TABLE IF NOT EXISTS messages(
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    room_id INT NOT NULL,
                    user_id INT NOT NULL,
                    content TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(room_id) REFERENCES rooms(id),
                    FOREIGN KEY(user_id) REFERENCES users(id)
                )
            """)
    print(" Tables initialized")

async def close_pool():
    global pool
    if pool:
        pool.close()
        await pool.wait_closed()
        print(" DB pool closed")

async def get_db():
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            yield cur