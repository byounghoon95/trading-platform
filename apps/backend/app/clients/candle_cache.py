import json
from dataclasses import asdict
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Any

from redis.exceptions import RedisError

from app.clients.binance import CandleDTO
from app.clients.redis import get_redis_client

CANDLE_CACHE_TTLS_SECONDS = {
    "1m": 15,
    "5m": 45,
    "15m": 90,
    "1h": 240,
    "1d": 1200,
}


class CandleCacheError(Exception):
    """Raised when candle cache data cannot be read or written."""


def build_candle_cache_key(symbol: str, interval: str, limit: int) -> str:
    return f"candles:{symbol}:{interval}:{limit}"


def get_candle_cache_ttl(interval: str) -> int:
    return CANDLE_CACHE_TTLS_SECONDS[interval]


class RedisCandleCache:
    def __init__(self, redis_client: Any | None = None) -> None:
        self.redis_client = redis_client or get_redis_client()

    async def get_candles(self, symbol: str, interval: str, limit: int) -> list[CandleDTO] | None:
        key = build_candle_cache_key(symbol=symbol, interval=interval, limit=limit)

        try:
            candles_json = await self.redis_client.get(key)
        except RedisError as error:
            raise CandleCacheError("Failed to get candles from cache") from error

        if candles_json is None:
            return None

        return deserialize_candles(candles_json)

    async def set_candles(
        self,
        symbol: str,
        interval: str,
        limit: int,
        candles: list[CandleDTO],
    ) -> None:
        key = build_candle_cache_key(symbol=symbol, interval=interval, limit=limit)
        ttl_seconds = get_candle_cache_ttl(interval)
        candles_json = serialize_candles(candles)

        try:
            await self.redis_client.set(key, candles_json, ex=ttl_seconds)
        except RedisError as error:
            raise CandleCacheError("Failed to set candles in cache") from error


def serialize_candles(candles: list[CandleDTO]) -> str:
    candles_raw = []
    for candle in candles:
        candle_raw = asdict(candle)
        candle_raw["open_time"] = candle.open_time.isoformat()
        candle_raw["close_time"] = candle.close_time.isoformat()
        candle_raw["open"] = str(candle.open)
        candle_raw["high"] = str(candle.high)
        candle_raw["low"] = str(candle.low)
        candle_raw["close"] = str(candle.close)
        candle_raw["volume"] = str(candle.volume)
        candles_raw.append(candle_raw)

    return json.dumps(candles_raw)


def deserialize_candles(candles_json: str) -> list[CandleDTO]:
    try:
        candles_raw = json.loads(candles_json)
        if not isinstance(candles_raw, list):
            raise CandleCacheError("Cached candle payload must be a list")

        return [deserialize_candle(candle_raw) for candle_raw in candles_raw]
    except (InvalidOperation, KeyError, TypeError, ValueError, json.JSONDecodeError) as error:
        raise CandleCacheError("Cached candle payload is invalid") from error


def deserialize_candle(candle_raw: dict[str, Any]) -> CandleDTO:
    return CandleDTO(
        symbol=str(candle_raw["symbol"]),
        interval=str(candle_raw["interval"]),
        open_time=datetime.fromisoformat(str(candle_raw["open_time"])),
        close_time=datetime.fromisoformat(str(candle_raw["close_time"])),
        open=Decimal(str(candle_raw["open"])),
        high=Decimal(str(candle_raw["high"])),
        low=Decimal(str(candle_raw["low"])),
        close=Decimal(str(candle_raw["close"])),
        volume=Decimal(str(candle_raw["volume"])),
    )
