from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation
from typing import Any

import httpx2

SUPPORTED_SYMBOLS = frozenset({"BTCUSDT", "ETHUSDT"})
SUPPORTED_INTERVALS = frozenset({"1m", "5m", "15m", "1h", "1d"})
DEFAULT_CANDLE_LIMIT = 200
MAX_CANDLE_LIMIT = 1000
BINANCE_RATE_LIMIT_STATUS_CODES = frozenset({418, 429})
BINANCE_API_BASE_URL = "https://api.binance.com"


@dataclass(frozen=True)
class CandleDTO:
    symbol: str
    interval: str
    open_time: datetime
    close_time: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal


@dataclass(frozen=True)
class TickerDTO:
    symbol: str
    price: Decimal
    price_change_percent_24h: Decimal
    updated_at: datetime


class BinanceClientError(Exception):
    """Base error for Binance client failures."""


class InvalidMarketDataRequestError(ValueError):
    """Raised when market data inputs are outside the supported MVP set."""


class BinanceRateLimitError(BinanceClientError):
    """Raised when Binance rate-limit responses continue after bounded retry."""


class BinanceHTTPStatusError(BinanceClientError):
    """Raised when Binance returns a non-success HTTP response."""


class BinancePayloadError(BinanceClientError):
    """Raised when Binance returns an unexpected payload shape."""


@dataclass(frozen=True)
class BinanceClient:
    base_url: str = BINANCE_API_BASE_URL
    timeout_seconds: float = 10.0
    max_retries: int = 2
    retry_backoff_seconds: float = 0.25
    http_client: Any | None = None
    sleep: Callable[[float], Awaitable[None]] | None = None

    async def get_candles(
        self,
        symbol: str,
        interval: str,
        limit: int = DEFAULT_CANDLE_LIMIT,
    ) -> list[CandleDTO]:
        validate_symbol(symbol)
        validate_interval(interval)
        validate_limit(limit)

        candles_raw = await self._get_json(
            "/api/v3/klines",
            params={"symbol": symbol, "interval": interval, "limit": limit},
        )
        if not isinstance(candles_raw, list):
            raise BinancePayloadError("Binance kline response must be a list")

        return [normalize_candle(symbol, interval, candle_raw) for candle_raw in candles_raw]

    async def get_ticker(self, symbol: str) -> TickerDTO:
        validate_symbol(symbol)

        ticker_raw = await self._get_json(
            "/api/v3/ticker/24hr",
            params={"symbol": symbol},
        )
        if not isinstance(ticker_raw, dict):
            raise BinancePayloadError("Binance ticker response must be an object")

        return normalize_ticker(ticker_raw)

    async def _get_json(self, path: str, params: dict[str, str | int]) -> Any:
        for attempt in range(self.max_retries + 1):
            response = await self._get(path, params)
            if response.status_code in BINANCE_RATE_LIMIT_STATUS_CODES:
                if attempt == self.max_retries:
                    raise BinanceRateLimitError("Binance rate limit retry cap reached")
                await self._sleep(self.retry_backoff_seconds * (2**attempt))
                continue

            if response.status_code >= 400:
                raise BinanceHTTPStatusError(
                    f"Binance request failed with status {response.status_code}"
                )

            return response.json()

        raise BinanceRateLimitError("Binance rate limit retry cap reached")

    async def _get(self, path: str, params: dict[str, str | int]) -> Any:
        if self.http_client is not None:
            return await self.http_client.get(path, params=params)

        async with httpx2.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout_seconds,
        ) as client:
            return await client.get(path, params=params)

    async def _sleep(self, delay_seconds: float) -> None:
        if self.sleep is not None:
            await self.sleep(delay_seconds)
            return

        import asyncio

        await asyncio.sleep(delay_seconds)


def validate_symbol(symbol: str) -> None:
    if symbol not in SUPPORTED_SYMBOLS:
        raise InvalidMarketDataRequestError(f"Unsupported symbol: {symbol}")


def validate_interval(interval: str) -> None:
    if interval not in SUPPORTED_INTERVALS:
        raise InvalidMarketDataRequestError(f"Unsupported interval: {interval}")


def validate_limit(limit: int) -> None:
    if limit < 1 or limit > MAX_CANDLE_LIMIT:
        raise InvalidMarketDataRequestError(f"Unsupported candle limit: {limit}")


def normalize_candle(symbol: str, interval: str, candle_raw: list[Any]) -> CandleDTO:
    try:
        return CandleDTO(
            symbol=symbol,
            interval=interval,
            open_time=create_utc_datetime(candle_raw[0]),
            open=Decimal(str(candle_raw[1])),
            high=Decimal(str(candle_raw[2])),
            low=Decimal(str(candle_raw[3])),
            close=Decimal(str(candle_raw[4])),
            volume=Decimal(str(candle_raw[5])),
            close_time=create_utc_datetime(candle_raw[6]),
        )
    except (IndexError, InvalidOperation, TypeError, ValueError) as error:
        raise BinancePayloadError("Invalid Binance kline payload") from error


def normalize_ticker(ticker_raw: dict[str, Any]) -> TickerDTO:
    try:
        return TickerDTO(
            symbol=str(ticker_raw["symbol"]),
            price=Decimal(str(ticker_raw["lastPrice"])),
            price_change_percent_24h=Decimal(str(ticker_raw["priceChangePercent"])),
            updated_at=create_utc_datetime(ticker_raw["closeTime"]),
        )
    except (InvalidOperation, KeyError, TypeError, ValueError) as error:
        raise BinancePayloadError("Invalid Binance ticker payload") from error


def create_utc_datetime(timestamp_milliseconds: int | str) -> datetime:
    return datetime.fromtimestamp(int(timestamp_milliseconds) / 1000, tz=UTC)
