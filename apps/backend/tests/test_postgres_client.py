from datetime import UTC, datetime
from decimal import Decimal

from app.clients.binance import CandleDTO, TickerDTO
from app.clients.postgres import (
    CREATE_CANDLES_TABLE_SQL,
    CREATE_TICKERS_TABLE_SQL,
    create_candle_dto,
    create_candle_params,
    create_ticker_dto,
)


def test_schema_defines_market_data_tables() -> None:
    assert "CREATE TABLE IF NOT EXISTS market_candles" in CREATE_CANDLES_TABLE_SQL
    assert "PRIMARY KEY (symbol, interval, open_time)" in CREATE_CANDLES_TABLE_SQL
    assert "CREATE TABLE IF NOT EXISTS market_tickers" in CREATE_TICKERS_TABLE_SQL
    assert "PRIMARY KEY (symbol, updated_at)" in CREATE_TICKERS_TABLE_SQL


def test_create_candle_params_preserves_dto_fields() -> None:
    candle = CandleDTO(
        symbol="BTCUSDT",
        interval="1m",
        open_time=datetime(2023, 11, 14, 22, 13, 20, tzinfo=UTC),
        close_time=datetime(2023, 11, 14, 22, 14, 19, 999000, tzinfo=UTC),
        open=Decimal("100.10"),
        high=Decimal("105.20"),
        low=Decimal("99.90"),
        close=Decimal("101.30"),
        volume=Decimal("12.345"),
    )

    assert create_candle_params(candle) == (
        "BTCUSDT",
        "1m",
        datetime(2023, 11, 14, 22, 13, 20, tzinfo=UTC),
        datetime(2023, 11, 14, 22, 14, 19, 999000, tzinfo=UTC),
        Decimal("100.10"),
        Decimal("105.20"),
        Decimal("99.90"),
        Decimal("101.30"),
        Decimal("12.345"),
    )


def test_create_candle_dto_normalizes_database_row() -> None:
    candle = create_candle_dto(
        {
            "symbol": "BTCUSDT",
            "interval": "1m",
            "open_time": datetime(2023, 11, 14, 22, 13, 20),
            "close_time": datetime(2023, 11, 14, 22, 14, 19, 999000),
            "open": Decimal("100.10"),
            "high": Decimal("105.20"),
            "low": Decimal("99.90"),
            "close": Decimal("101.30"),
            "volume": Decimal("12.345"),
        }
    )

    assert candle == CandleDTO(
        symbol="BTCUSDT",
        interval="1m",
        open_time=datetime(2023, 11, 14, 22, 13, 20, tzinfo=UTC),
        close_time=datetime(2023, 11, 14, 22, 14, 19, 999000, tzinfo=UTC),
        open=Decimal("100.10"),
        high=Decimal("105.20"),
        low=Decimal("99.90"),
        close=Decimal("101.30"),
        volume=Decimal("12.345"),
    )


def test_create_ticker_dto_normalizes_database_row() -> None:
    ticker = create_ticker_dto(
        {
            "symbol": "ETHUSDT",
            "price": Decimal("3400.42"),
            "price_change_percent_24h": Decimal("-1.25"),
            "updated_at": datetime(2023, 11, 14, 22, 13, 20),
        }
    )

    assert ticker == TickerDTO(
        symbol="ETHUSDT",
        price=Decimal("3400.42"),
        price_change_percent_24h=Decimal("-1.25"),
        updated_at=datetime(2023, 11, 14, 22, 13, 20, tzinfo=UTC),
    )
