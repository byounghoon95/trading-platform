import asyncio
from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

import pytest

from app.clients.binance import (
    BinanceClient,
    BinanceRateLimitError,
    CandleDTO,
    InvalidMarketDataRequestError,
    TickerDTO,
    normalize_candle,
    normalize_ticker,
)


@dataclass(frozen=True)
class FakeResponse:
    status_code: int
    payload: Any

    def json(self) -> Any:
        return self.payload


class FakeHTTPClient:
    def __init__(self, responses: list[FakeResponse]) -> None:
        self.responses = responses
        self.calls: list[tuple[str, dict[str, str | int]]] = []

    async def get(self, path: str, params: dict[str, str | int]) -> FakeResponse:
        self.calls.append((path, params))
        return self.responses.pop(0)


class FakeSleeper:
    def __init__(self) -> None:
        self.delays: list[float] = []

    async def sleep(self, delay_seconds: float) -> None:
        self.delays.append(delay_seconds)


def test_normalize_candle_converts_binance_kline_row() -> None:
    candle = normalize_candle(
        "BTCUSDT",
        "1m",
        [
            1_700_000_000_000,
            "100.10",
            "105.20",
            "99.90",
            "101.30",
            "12.345",
            1_700_000_059_999,
            "unused quote volume",
        ],
    )

    assert candle == CandleDTO(
        symbol="BTCUSDT",
        interval="1m",
        open_time=datetime(2023, 11, 14, 22, 13, 20, tzinfo=UTC),
        open=Decimal("100.10"),
        high=Decimal("105.20"),
        low=Decimal("99.90"),
        close=Decimal("101.30"),
        volume=Decimal("12.345"),
        close_time=datetime(2023, 11, 14, 22, 14, 19, 999000, tzinfo=UTC),
    )


def test_normalize_ticker_converts_binance_24h_payload() -> None:
    ticker = normalize_ticker(
        {
            "symbol": "ETHUSDT",
            "lastPrice": "2500.50",
            "priceChangePercent": "-1.25",
            "closeTime": 1_700_000_059_999,
        }
    )

    assert ticker == TickerDTO(
        symbol="ETHUSDT",
        price=Decimal("2500.50"),
        price_change_percent_24h=Decimal("-1.25"),
        updated_at=datetime(2023, 11, 14, 22, 14, 19, 999000, tzinfo=UTC),
    )


def test_get_candles_rejects_invalid_symbol_before_http_call() -> None:
    http_client = FakeHTTPClient([])
    client = BinanceClient(http_client=http_client)

    with pytest.raises(InvalidMarketDataRequestError):
        asyncio.run(client.get_candles("DOGEUSDT", "1m"))

    assert http_client.calls == []


def test_get_candles_rejects_invalid_interval_before_http_call() -> None:
    http_client = FakeHTTPClient([])
    client = BinanceClient(http_client=http_client)

    with pytest.raises(InvalidMarketDataRequestError):
        asyncio.run(client.get_candles("BTCUSDT", "30m"))

    assert http_client.calls == []


def test_get_candles_normalizes_successful_response() -> None:
    http_client = FakeHTTPClient(
        [
            FakeResponse(
                status_code=200,
                payload=[
                    [
                        1_700_000_000_000,
                        "100.10",
                        "105.20",
                        "99.90",
                        "101.30",
                        "12.345",
                        1_700_000_059_999,
                    ]
                ],
            )
        ]
    )
    client = BinanceClient(http_client=http_client)

    candles = asyncio.run(client.get_candles("BTCUSDT", "1m", limit=1))

    assert candles == [
        CandleDTO(
            symbol="BTCUSDT",
            interval="1m",
            open_time=datetime(2023, 11, 14, 22, 13, 20, tzinfo=UTC),
            open=Decimal("100.10"),
            high=Decimal("105.20"),
            low=Decimal("99.90"),
            close=Decimal("101.30"),
            volume=Decimal("12.345"),
            close_time=datetime(2023, 11, 14, 22, 14, 19, 999000, tzinfo=UTC),
        )
    ]
    assert http_client.calls == [
        ("/api/v3/klines", {"symbol": "BTCUSDT", "interval": "1m", "limit": 1})
    ]


def test_get_ticker_normalizes_successful_response() -> None:
    http_client = FakeHTTPClient(
        [
            FakeResponse(
                status_code=200,
                payload={
                    "symbol": "BTCUSDT",
                    "lastPrice": "68000.01",
                    "priceChangePercent": "2.50",
                    "closeTime": 1_700_000_000_000,
                },
            )
        ]
    )
    client = BinanceClient(http_client=http_client)

    ticker = asyncio.run(client.get_ticker("BTCUSDT"))

    assert ticker.price == Decimal("68000.01")
    assert ticker.price_change_percent_24h == Decimal("2.50")
    assert http_client.calls == [("/api/v3/ticker/24hr", {"symbol": "BTCUSDT"})]


def test_rate_limit_responses_retry_with_exponential_backoff_until_cap() -> None:
    http_client = FakeHTTPClient(
        [
            FakeResponse(status_code=429, payload={}),
            FakeResponse(status_code=418, payload={}),
            FakeResponse(status_code=429, payload={}),
        ]
    )
    sleeper = FakeSleeper()
    client = BinanceClient(
        http_client=http_client,
        sleep=sleeper.sleep,
        max_retries=2,
        retry_backoff_seconds=1.0,
    )

    with pytest.raises(BinanceRateLimitError):
        asyncio.run(client.get_ticker("ETHUSDT"))

    assert len(http_client.calls) == 3
    assert sleeper.delays == [1.0, 2.0]
