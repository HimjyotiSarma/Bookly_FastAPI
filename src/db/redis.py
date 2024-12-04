import redis.asyncio as aioredis  # Use asyncio version of Redis
from src.config import settings

JTI_EXPIRY = 3600  # Expiry time in seconds

# Initialize async Redis client

client = aioredis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    decode_responses=True,  # Ensure responses are decoded to strings
    username=settings.REDIS_USERNAME,
    password=settings.REDIS_PASSWORD,
)

# client = aioredis.from_url(settings.REDIS_URL)


# Asynchronous function to add JTI to the blacklist with expiry
async def add_jti_to_blacklist(jti: str):
    await client.set(
        name=jti, value=jti, ex=JTI_EXPIRY
    )  # Use the actual JTI as the key


# Asynchronous function to check if JTI is in the blacklist
async def token_in_blacklist(jti: str):
    jti_info = await client.get(jti)  # Fetch the JTI using the JTI as the key
    return jti_info is not None
