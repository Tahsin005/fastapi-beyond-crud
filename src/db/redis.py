import redis.asyncio as redis
from src.config import Config

JTI_EXPIRY = 3600

token_blocklist = redis.Redis(
    host=Config.REDIS_HOST,
    port=Config.REDIS_PORT,
    db=0,
    decode_responses=True,
)

async def add_jti_to_blacklist(jti: str) -> None:
    await token_blocklist.set(
        name=jti,
        value="",
        ex=JTI_EXPIRY,
    )

async def is_jti_blocklisted(jti: str) -> bool:
    value = await token_blocklist.get(jti)
    return True if value is not None else False