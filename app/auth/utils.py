import bcrypt
from jose import JWTError,jwt
from datetime import datetime,timedelta
from app.config import Settings
from fastapi import HTTPException,Query

def hash_password(password: str):
    return bcrypt.hashpw(password.encode(),bcrypt.gensalt()).decode()


def verify_password(plain: str,hashed:str):
    return bcrypt.checkpw(plain.encode(),hashed.encode())

def create_access_token(data : dict):
    to_encode=data.copy()
    expire=datetime.utcnow()+timedelta(minutes=Settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode,Settings.SECRET_KEY,algorithm="HS256")

def decode_token(token:str):
    try:
        payload=jwt.decode(token,Settings.SECRET_KEY,algorithms=["HS256"])
        return payload
    except JWTError:
        return None
    
async def get_current_user(token: str = Query(...)):
    payload=decode_token(token)
    if not payload:
        raise HTTPException(status_code=401,detail="Invalid or expired token")
    return payload
