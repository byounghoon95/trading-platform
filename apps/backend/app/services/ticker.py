from collections.abc import Callable
from datetime import UTC, datetime, timedelta

from app.clients.binance import BinanceClient, BinanceClientError, TickerDTO, validate_symbol
from app.clients.postgres import PostgresClient
from app.core.config import get_settings

TICKER_STALE_AFTER = timedelta(seconds=15)


async def get_ticker(
    symbol: str,
    *,
    binance_client: BinanceClient | None = None,
    postgres_client: PostgresClient | None = None,
    now: Callable[[], datetime] | None = None,
) -> TickerDTO:
    validate_symbol(symbol)

    database_client = postgres_client or create_postgres_client()
    if database_client is None:
        client = binance_client or BinanceClient()
        return await client.get_ticker(symbol=symbol)

    stored_ticker = await database_client.get_latest_ticker(symbol=symbol)
    current_time = create_current_time(now)
    if stored_ticker is not None and is_fresh_ticker(stored_ticker, current_time):
        return stored_ticker

    client = binance_client or BinanceClient()
    try:
        refreshed_ticker = await client.get_ticker(symbol=symbol)
    except BinanceClientError:
        if stored_ticker is not None:
            return stored_ticker
        raise

    await database_client.upsert_ticker(refreshed_ticker)
    persisted_ticker = await database_client.get_latest_ticker(symbol=symbol)
    return persisted_ticker or refreshed_ticker


def create_postgres_client() -> PostgresClient | None:
    database_url = get_settings().database_url
    if database_url is None:
        return None
    return PostgresClient(database_url=database_url)


def is_fresh_ticker(ticker: TickerDTO, current_time: datetime) -> bool:
    return ticker.updated_at >= current_time - TICKER_STALE_AFTER


def create_current_time(now: Callable[[], datetime] | None) -> datetime:
    if now is None:
        return datetime.now(UTC)

    current_time = now()
    if current_time.tzinfo is None:
        return current_time.replace(tzinfo=UTC)
    return current_time.astimezone(UTC)
