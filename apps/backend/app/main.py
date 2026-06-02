from fastapi import FastAPI

from app.api.candles import router as candles_router
from app.api.health import router as health_router
from app.core.config import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    fastapi_app = FastAPI(title=settings.app_name)
    fastapi_app.include_router(health_router)
    fastapi_app.include_router(candles_router)
    return fastapi_app


app = create_app()
