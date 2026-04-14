from fastapi import APIRouter,HTTPException,Depends
from app.auth.schemas import RegisterRequest,LoginRequest,TokenResponse
from app.auth.utils import hash_password,verify_password,create_access_token
from app.database import get_db

router=APIRouter(prefix="/auth",tags=["auth"])

@router.post("/register", response_model=TokenResponse)
async def register(body: RegisterRequest, cur=Depends(get_db)):
    await cur.execute("SELECT id FROM users WHERE username = %s", (body.username,))
    if await cur.fetchone():
        raise HTTPException(status_code=400, detail="Username already taken")

    await cur.execute("SELECT id FROM users WHERE email = %s", (body.email,))
    if await cur.fetchone():
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed = hash_password(body.password)
    await cur.execute(
        "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
        (body.username, body.email, hashed)
    )
    user_id = cur.lastrowid

    token = create_access_token({"user_id": user_id, "username": body.username})
    return TokenResponse(access_token=token, username=body.username, user_id=user_id)
@router.post("/login",response_model=TokenResponse)
async def login(body: LoginRequest,cur=Depends(get_db)):
    
    await cur.execute("SELECT * FROM users WHERE username = %s",(body.username,))
    user=await cur.fetchone()
    
    if not user or not verify_password(body.password,user["password_hash"]):
        raise HTTPException(status_code=401,detail="Invalid username or password")
    
    token=create_access_token({"user_id":user["id"],"username":user["username"]})
    return TokenResponse(access_token=token, username=user["username"], user_id=user["id"])

@router.get("/me")
async def get_me(cur=Depends(get_db)):
    
    return {"message": "token validation comes Day 4"}