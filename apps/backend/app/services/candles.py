from collections.abc import Callable
from datetime import UTC, datetime, timedelta

from app.clients.binance import (
    DEFAULT_CANDLE_LIMIT,
    BinanceClient,
    BinanceClientError,
    CandleDTO,
    validate_interval,
    validate_limit,
    validate_symbol,
)
from app.clients.postgres import PostgresClient
from app.core.config import get_settings

INTERVAL_DURATIONS = {
    "1m": timedelta(minutes=1),
    "5m": timedelta(minutes=5),
    "15m": timedelta(minutes=15),
    "1h": timedelta(hours=1),
    "1d": timedelta(days=1),
}


async def list_candles(
    symbol: str,
    interval: str,
    limit: int = DEFAULT_CANDLE_LIMIT,
    *,
    binance_client: BinanceClient | None = None,
    postgres_client: PostgresClient | None = None,
    now: Callable[[], datetime] | None = None,
) -> list[CandleDTO]:
    validate_symbol(symbol)
    validate_interval(interval)
    validate_limit(limit)

    database_client = postgres_client or create_postgres_client()
    if database_client is None:
        client = binance_client or BinanceClient()
        return await client.get_candles(symbol=symbol, interval=interval, limit=limit)

    stored_candles = await database_client.get_candles(
        symbol=symbol,
        interval=interval,
        limit=limit,
    )
    current_time = create_current_time(now)
    if has_fresh_candles(stored_candles, interval, limit, current_time):
        return stored_candles

    client = binance_client or BinanceClient()
    try:
        refreshed_candles = await client.get_candles(
            symbol=symbol,
            interval=interval,
            limit=limit,
        )
    except BinanceClientError:
        if stored_candles:
            return stored_candles
        raise

    await database_client.upsert_candles(refreshed_candles)
    persisted_candles = await database_client.get_candles(
        symbol=symbol,
        interval=interval,
        limit=limit,
    )
    return persisted_candles or refreshed_candles


def create_postgres_client() -> PostgresClient | None:
    database_url = get_settings().database_url
    if database_url is None:
        return None
    return PostgresClient(database_url=database_url)


def has_fresh_candles(
    candles: list[CandleDTO],
    interval: str,
    limit: int,
    current_time: datetime,
) -> bool:
    if len(candles) < limit:
        return False

    latest_candle = candles[-1]
    return latest_candle.close_time >= current_time - INTERVAL_DURATIONS[interval]


def create_current_time(now: Callable[[], datetime] | None) -> datetime:
    if now is None:
        return datetime.now(UTC)

    current_time = now()
    if current_time.tzinfo is None:
        return current_time.replace(tzinfo=UTC)
    return current_time.astimezone(UTC)
