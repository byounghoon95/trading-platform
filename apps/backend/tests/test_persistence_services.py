import asyncio
from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest

from app.clients.binance import BinanceClientError, CandleDTO, TickerDTO
from app.services.candles import list_candles
from app.services.ticker import get_ticker


class FakeBinanceClient:
    def __init__(
        self,
        *,
        candles: list[CandleDTO] | None = None,
        ticker: TickerDTO | None = None,
        error: Exception | None = None,
    ) -> None:
        self.candles = candles or []
        self.ticker = ticker
        self.error = error
        self.candle_calls = 0
        self.ticker_calls = 0

    async def get_candles(self, symbol: str, interval: str, limit: int) -> list[CandleDTO]:
        self.candle_calls += 1
        if self.error is not None:
            raise self.error
        return self.candles[:limit]

    async def get_ticker(self, symbol: str) -> TickerDTO:
        self.ticker_calls += 1
        if self.error is not None:
            raise self.error
        if self.ticker is None:
            raise AssertionError("ticker was not configured")
        return self.ticker


class FakePostgresClient:
    def __init__(
        self,
        *,
        candles: list[CandleDTO] | None = None,
        ticker: TickerDTO | None = None,
    ) -> None:
        self.candles = candles or []
        self.ticker = ticker
        self.upserted_candles: list[CandleDTO] = []
        self.upserted_tickers: list[TickerDTO] = []

    async def get_candles(self, symbol: str, interval: str, limit: int) -> list[CandleDTO]:
        candles = [
            candle
            for candle in self.candles
            if candle.symbol == symbol and candle.interval == interval
        ]
        return candles[-limit:]

    async def upsert_candles(self, candles: list[CandleDTO]) -> None:
        self.upserted_candles.extend(candles)
        self.candles = candles

    async def get_latest_ticker(self, symbol: str) -> TickerDTO | None:
        if self.ticker is None or self.ticker.symbol != symbol:
            return None
        return self.ticker

    async def upsert_ticker(self, ticker: TickerDTO) -> None:
        self.upserted_tickers.append(ticker)
        self.ticker = ticker


def test_list_candles_returns_fresh_stored_records_without_binance_call() -> None:
    current_time = datetime(2023, 11, 14, 22, 15, tzinfo=UTC)
    stored_candles = [
        create_candle(open_minute=13),
        create_candle(open_minute=14),
    ]
    postgres_client = FakePostgresClient(candles=stored_candles)
    binance_client = FakeBinanceClient(candles=[create_candle(open_minute=15)])

    candles = asyncio.run(
        list_candles(
            symbol="BTCUSDT",
            interval="1m",
            limit=2,
            binance_client=binance_client,
            postgres_client=postgres_client,
            now=lambda: current_time,
        )
    )

    assert candles == stored_candles
    assert binance_client.candle_calls == 0


def test_list_candles_refreshes_and_persists_stale_records() -> None:
    current_time = datetime(2023, 11, 14, 22, 20, tzinfo=UTC)
    refreshed_candles = [
        create_candle(open_minute=19),
        create_candle(open_minute=20),
    ]
    postgres_client = FakePostgresClient(candles=[create_candle(open_minute=10)])
    binance_client = FakeBinanceClient(candles=refreshed_candles)

    candles = asyncio.run(
        list_candles(
            symbol="BTCUSDT",
            interval="1m",
            limit=2,
            binance_client=binance_client,
            postgres_client=postgres_client,
            now=lambda: current_time,
        )
    )

    assert candles == refreshed_candles
    assert postgres_client.upserted_candles == refreshed_candles


def test_list_candles_falls_back_to_stored_records_when_refresh_fails() -> None:
    stored_candles = [create_candle(open_minute=10)]
    postgres_client = FakePostgresClient(candles=stored_candles)
    binance_client = FakeBinanceClient(error=BinanceClientError("provider failed"))

    candles = asyncio.run(
        list_candles(
            symbol="BTCUSDT",
            interval="1m",
            limit=2,
            binance_client=binance_client,
            postgres_client=postgres_client,
            now=lambda: datetime(2023, 11, 14, 22, 20, tzinfo=UTC),
        )
    )

    assert candles == stored_candles


def test_get_ticker_returns_fresh_stored_record_without_binance_call() -> None:
    current_time = datetime(2023, 11, 14, 22, 13, 30, tzinfo=UTC)
    stored_ticker = create_ticker(updated_at=current_time - timedelta(seconds=5))
    postgres_client = FakePostgresClient(ticker=stored_ticker)
    binance_client = FakeBinanceClient(ticker=create_ticker(updated_at=current_time))

    ticker = asyncio.run(
        get_ticker(
            symbol="BTCUSDT",
            binance_client=binance_client,
            postgres_client=postgres_client,
            now=lambda: current_time,
        )
    )

    assert ticker == stored_ticker
    assert binance_client.ticker_calls == 0


def test_get_ticker_refreshes_and_persists_stale_record() -> None:
    current_time = datetime(2023, 11, 14, 22, 13, 30, tzinfo=UTC)
    refreshed_ticker = create_ticker(updated_at=current_time)
    postgres_client = FakePostgresClient(
        ticker=create_ticker(updated_at=current_time - timedelta(minutes=1))
    )
    binance_client = FakeBinanceClient(ticker=refreshed_ticker)

    ticker = asyncio.run(
        get_ticker(
            symbol="BTCUSDT",
            binance_client=binance_client,
            postgres_client=postgres_client,
            now=lambda: current_time,
        )
    )

    assert ticker == refreshed_ticker
    assert postgres_client.upserted_tickers == [refreshed_ticker]


def test_get_ticker_falls_back_to_stored_record_when_refresh_fails() -> None:
    stored_ticker = create_ticker(updated_at=datetime(2023, 11, 14, 22, 12, tzinfo=UTC))
    postgres_client = FakePostgresClient(ticker=stored_ticker)
    binance_client = FakeBinanceClient(error=BinanceClientError("provider failed"))

    ticker = asyncio.run(
        get_ticker(
            symbol="BTCUSDT",
            binance_client=binance_client,
            postgres_client=postgres_client,
            now=lambda: datetime(2023, 11, 14, 22, 13, tzinfo=UTC),
        )
    )

    assert ticker == stored_ticker


def test_list_candles_keeps_invalid_market_validation() -> None:
    with pytest.raises(ValueError, match="Unsupported symbol"):
        asyncio.run(
            list_candles(
                symbol="DOGEUSDT",
                interval="1m",
                postgres_client=FakePostgresClient(),
            )
        )


def create_candle(open_minute: int) -> CandleDTO:
    open_time = datetime(2023, 11, 14, 22, open_minute, tzinfo=UTC)
    return CandleDTO(
        symbol="BTCUSDT",
        interval="1m",
        open_time=open_time,
        close_time=open_time + timedelta(seconds=59, milliseconds=999),
        open=Decimal("100.10"),
        high=Decimal("105.20"),
        low=Decimal("99.90"),
        close=Decimal("101.30"),
        volume=Decimal("12.345"),
    )


def create_ticker(updated_at: datetime) -> TickerDTO:
    return TickerDTO(
        symbol="BTCUSDT",
        price=Decimal("68000.01"),
        price_change_percent_24h=Decimal("2.50"),
        updated_at=updated_at,
    )
