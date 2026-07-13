import json
import redis
import os

redis_client = redis.Redis.from_url(
    os.environ.get("REDIS_URL", "redis://localhost:6379/0"),
    decode_responses=True,
)

CACHE_EXPIRY_SECONDS = 300


def get_cached(key):
    value = redis_client.get(key)
    return json.loads(value) if value else None


def set_cached(key, value, expiry=CACHE_EXPIRY_SECONDS):
    redis_client.setex(key, expiry, json.dumps(value))


def invalidate_cache(pattern):
    for key in redis_client.scan_iter(pattern):
        redis_client.delete(key)