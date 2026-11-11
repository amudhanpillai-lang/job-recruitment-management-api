
import redis
import os

# Redis connection URL
REDIS_URL = os.getenv(
    "REDIS_URL",
    "redis://localhost:6379/0"
)

# Create Redis client
redis_client = redis.Redis.from_url(
    REDIS_URL,
    decode_responses=True
)


# Check Redis connection
def check_redis_connection():
    try:
        return redis_client.ping()
    except redis.RedisError:
        return False
