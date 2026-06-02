from fastapi import APIRouter, HTTPException

from app.clients.redis import RedisClientError, check_redis_connection

router = APIRouter()


@router.get("/health")
async def get_health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/ready")
async def get_readiness() -> dict[str, str]:
    try:
        await check_redis_connection()
    except RedisClientError as error:
        raise HTTPException(
            status_code=503,
            detail={
                "code": "dependency_unavailable",
                "message": "Redis is unreachable",
            },
        ) from error

    return {"status": "ready"}
