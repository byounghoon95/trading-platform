from collections.abc import Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

from psycopg import AsyncConnection
from psycopg import Error as PsycopgError
from psycopg.rows import dict_row

from app.clients.binance import CandleDTO, TickerDTO

CREATE_CANDLES_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS market_candles (
    symbol TEXT NOT NULL,
    interval TEXT NOT NULL,
    open_time TIMESTAMPTZ NOT NULL,
    close_time TIMESTAMPTZ NOT NULL,
    open NUMERIC NOT NULL,
    high NUMERIC NOT NULL,
    low NUMERIC NOT NULL,
    close NUMERIC NOT NULL,
    volume NUMERIC NOT NULL,
    PRIMARY KEY (symbol, interval, open_time)
)
"""

CREATE_CANDLES_INDEX_SQL = """
CREATE INDEX IF NOT EXISTS market_candles_lookup_idx
ON market_candles (symbol, interval, open_time DESC)
"""

CREATE_TICKERS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS market_tickers (
    symbol TEXT NOT NULL,
    price NUMERIC NOT NULL,
    price_change_percent_24h NUMERIC NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (symbol, updated_at)
)
"""

CREATE_TICKERS_INDEX_SQL = """
CREATE INDEX IF NOT EXISTS market_tickers_lookup_idx
ON market_tickers (symbol, updated_at DESC)
"""

SCHEMA_SQL = (
    CREATE_CANDLES_TABLE_SQL,
    CREATE_CANDLES_INDEX_SQL,
    CREATE_TICKERS_TABLE_SQL,
    CREATE_TICKERS_INDEX_SQL,
)


class DatabaseClientError(Exception):
    """Raised when PostgreSQL persistence is unavailable or returns invalid rows."""


@dataclass(frozen=True)
class PostgresClient:
    database_url: str

    async def initialize_schema(self) -> None:
        try:
            async with await AsyncConnection.connect(self.database_url) as connection:
                for statement in SCHEMA_SQL:
                    await connection.execute(statement)
        except PsycopgError as error:
            raise DatabaseClientError("PostgreSQL schema initialization failed") from error

    async def get_candles(self, symbol: str, interval: str, limit: int) -> list[CandleDTO]:
        try:
            async with await AsyncConnection.connect(
                self.database_url,
                row_factory=dict_row,
            ) as connection:
                rows = await connection.execute(
                    """
                    SELECT
                        symbol,
                        interval,
                        open_time,
                        close_time,
                        open,
                        high,
                        low,
                        close,
                        volume
                    FROM market_candles
                    WHERE symbol = %s AND interval = %s
                    ORDER BY open_time DESC
                    LIMIT %s
                    """,
                    (symbol, interval, limit),
                )
                candles_raw = await rows.fetchall()
        except PsycopgError as error:
            raise DatabaseClientError("PostgreSQL candle lookup failed") from error

        return [create_candle_dto(row) for row in reversed(candles_raw)]

    async def upsert_candles(self, candles: Sequence[CandleDTO]) -> None:
        if not candles:
            return

        try:
            async with await AsyncConnection.connect(self.database_url) as connection:
                async with connection.cursor() as cursor:
                    await cursor.executemany(
                        """
                        INSERT INTO market_candles (
                            symbol,
                            interval,
                            open_time,
                            close_time,
                            open,
                            high,
                            low,
                            close,
                            volume
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (symbol, interval, open_time)
                        DO UPDATE SET
                            close_time = EXCLUDED.close_time,
                            open = EXCLUDED.open,
                            high = EXCLUDED.high,
                            low = EXCLUDED.low,
                            close = EXCLUDED.close,
                            volume = EXCLUDED.volume
                        """,
                        [create_candle_params(candle) for candle in candles],
                    )
        except PsycopgError as error:
            raise DatabaseClientError("PostgreSQL candle upsert failed") from error

    async def get_latest_ticker(self, symbol: str) -> TickerDTO | None:
        try:
            async with await AsyncConnection.connect(
                self.database_url,
                row_factory=dict_row,
            ) as connection:
                rows = await connection.execute(
                    """
                    SELECT
                        symbol,
                        price,
                        price_change_percent_24h,
                        updated_at
                    FROM market_tickers
                    WHERE symbol = %s
                    ORDER BY updated_at DESC
                    LIMIT 1
                    """,
                    (symbol,),
                )
                ticker_raw = await rows.fetchone()
        except PsycopgError as error:
            raise DatabaseClientError("PostgreSQL ticker lookup failed") from error

        if ticker_raw is None:
            return None
        return create_ticker_dto(ticker_raw)

    async def upsert_ticker(self, ticker: TickerDTO) -> None:
        try:
            async with await AsyncConnection.connect(self.database_url) as connection:
                await connection.execute(
                    """
                    INSERT INTO market_tickers (
                        symbol,
                        price,
                        price_change_percent_24h,
                        updated_at
                    )
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (symbol, updated_at)
                    DO UPDATE SET
                        price = EXCLUDED.price,
                        price_change_percent_24h = EXCLUDED.price_change_percent_24h
                    """,
                    (
                        ticker.symbol,
                        ticker.price,
                        ticker.price_change_percent_24h,
                        ticker.updated_at,
                    ),
                )
        except PsycopgError as error:
            raise DatabaseClientError("PostgreSQL ticker upsert failed") from error


async def initialize_database(database_url: str) -> None:
    await PostgresClient(database_url=database_url).initialize_schema()


async def check_database_ready(database_url: str) -> None:
    try:
        async with await AsyncConnection.connect(database_url) as connection:
            await connection.execute("SELECT 1")
    except PsycopgError as error:
        raise DatabaseClientError("PostgreSQL readiness check failed") from error


def create_candle_params(candle: CandleDTO) -> tuple[Any, ...]:
    return (
        candle.symbol,
        candle.interval,
        candle.open_time,
        candle.close_time,
        candle.open,
        candle.high,
        candle.low,
        candle.close,
        candle.volume,
    )


def create_candle_dto(row: dict[str, Any]) -> CandleDTO:
    return CandleDTO(
        symbol=str(row["symbol"]),
        interval=str(row["interval"]),
        open_time=create_aware_datetime(row["open_time"]),
        close_time=create_aware_datetime(row["close_time"]),
        open=Decimal(row["open"]),
        high=Decimal(row["high"]),
        low=Decimal(row["low"]),
        close=Decimal(row["close"]),
        volume=Decimal(row["volume"]),
    )


def create_ticker_dto(row: dict[str, Any]) -> TickerDTO:
    return TickerDTO(
        symbol=str(row["symbol"]),
        price=Decimal(row["price"]),
        price_change_percent_24h=Decimal(row["price_change_percent_24h"]),
        updated_at=create_aware_datetime(row["updated_at"]),
    )


def create_aware_datetime(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)
