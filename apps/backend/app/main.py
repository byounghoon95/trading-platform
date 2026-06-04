from fastapi import FastAPI

from app.api.candles import router as candles_router
from app.api.health import router as health_router
from app.api.markets import router as markets_router
from app.api.ticker import router as ticker_router
from app.core.config import get_settings
from app.observability.metrics import install_metrics


def create_app() -> FastAPI:
    settings = get_settings()
    fastapi_app = FastAPI(title=settings.app_name)
    install_metrics(fastapi_app)
    fastapi_app.include_router(health_router)
    fastapi_app.include_router(candles_router)
    fastapi_app.include_router(markets_router)
    fastapi_app.include_router(ticker_router)
    return fastapi_app


app = create_app()
