from typing import Any

from redis.asyncio import Redis
from redis.exceptions import RedisError

from app.core.config import get_settings


class RedisClientError(Exception):
    """Raised when Redis cannot serve a client operation."""


def get_redis_client() -> Redis:
    settings = get_settings()
    return Redis.from_url(settings.redis_url, decode_responses=True)


async def check_redis_connection(redis_client: Any | None = None) -> None:
    should_close_client = redis_client is None
    client = redis_client or get_redis_client()

    try:
        await client.ping()
    except RedisError as error:
        raise RedisClientError("Redis is unreachable") from error
    finally:
        if should_close_client:
            await client.aclose()
