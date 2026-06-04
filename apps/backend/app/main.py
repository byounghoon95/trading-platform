from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.candles import router as candles_router
from app.api.health import router as health_router
from app.api.markets import router as markets_router
from app.api.ticker import router as ticker_router
from app.clients.postgres import initialize_database
from app.core.config import get_settings
from app.observability.metrics import install_metrics


@asynccontextmanager
async def lifespan(fastapi_app: FastAPI) -> AsyncIterator[None]:
    database_url = get_settings().database_url
    if database_url is not None:
        await initialize_database(database_url)

    yield


def create_app() -> FastAPI:
    settings = get_settings()
    fastapi_app = FastAPI(title=settings.app_name, lifespan=lifespan)
    install_metrics(fastapi_app)
    fastapi_app.include_router(health_router)
    fastapi_app.include_router(candles_router)
    fastapi_app.include_router(markets_router)
    fastapi_app.include_router(ticker_router)
    return fastapi_app


app = create_app()
