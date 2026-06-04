from fastapi import APIRouter, HTTPException

from app.clients.postgres import DatabaseClientError, check_database_ready
from app.core.config import get_settings

router = APIRouter()


@router.get("/health")
async def get_health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/ready")
async def get_readiness() -> dict[str, str]:
    database_url = get_settings().database_url
    if database_url is None:
        raise HTTPException(
            status_code=503,
            detail={
                "code": "database_not_configured",
                "message": "PostgreSQL database URL is not configured",
            },
        )

    try:
        await check_database_ready(database_url)
    except DatabaseClientError as error:
        raise HTTPException(
            status_code=503,
            detail={
                "code": "database_unavailable",
                "message": "PostgreSQL readiness check failed",
            },
        ) from error

    return {"status": "ready"}
