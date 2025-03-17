import redis
from app.core.config import settings

redis_client = redis.from_url(settings.REDIS_URL)

def get_url_from_cache(short_key: str) -> str | None:
    return redis_client.get(f"url:{short_key}")

def set_url_in_cache(short_key: str, original_url: str, expire_time: int = 3600):
    redis_client.setex(f"url:{short_key}", expire_time, original_url)

def increment_click_count(short_key: str):
    redis_client.incr(f"clicks:{short_key}") 