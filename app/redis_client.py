import redis.asyncio as aioredis
from app.config import Settings

redis_publisher=None
redis_subscriber=None   #Two sepreste clients-one for publish,one for subscribe

async def create_redis():
    global redis_publisher,redis_subscriber
    redis_publisher=aioredis.Redis(
        host=Settings.REDIS_HOST,
        port=Settings.REDIS_PORT,
        decode_responses=True
    )
    redis_subscriber=aioredis.Redis(
        host=Settings.REDIS_HOST,
        port=Settings.REDIS_PORT,
        decode_responses=True
        
    )
    print("Redis connected")
    
async def close_redis():
    if redis_publisher:
        await redis_publisher.close()
    if redis_subscriber:
        await redis_subscriber.close()
    print("redis closed")
    
async def publish(channel:str,message: str):
    await redis_publisher.publish(channel,message)
    
async def is_rate_limited(user_id:int,limit:int =10,window: int=60):
    """
    Returns True if user has exceeded limit messages in window seconds.
    Uses Redis INCR+EXPIRE sliding window.
    limit=10 means max 10 messages per 60 seconds per user"""
    
    key=f"ratelimit:{user_id}"
    count=await redis_publisher.incr(key)
    if count==1:
        await redis_publisher.expire(key,window)
    return count>limit

    