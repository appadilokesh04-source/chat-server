from dotenv import load_dotenv
import os

load_dotenv()

class Settings:
    DB_HOST: str = os.getenv("DB_HOST","localhost")
    DB_PORT: int = int(os.getenv("DB_PORT",3306))
    DB_USER: str = os.getenv("DB_USER","root")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD","")
    DB_NAME: str = os.getenv("DB_NAME","chatdb")
    SECRET_KEY: str = os.getenv("SECRET_KEY","fallback_secret")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES",60))
    REDIS_HOST: str = os.getenv("REDIS_HOST","localhost")
    REDIS_PORT: int=int(os.getenv("REDIS_PORT",6379))
    
    
Settings=Settings()
