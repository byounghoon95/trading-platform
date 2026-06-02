import asyncio
from datetime import UTC, datetime
from decimal import Decimal

from app.clients.binance import CandleDTO
from app.clients.candle_cache import (
    RedisCandleCache,
    build_candle_cache_key,
    get_candle_cache_ttl,
)


class FakeRedis:
    def __init__(self) -> None:
        self.values: dict[str, str] = {}
        self.ttls: dict[str, int] = {}

    async def get(self, key: str) -> str | None:
        return self.values.get(key)

    async def set(self, key: str, value: str, ex: int) -> None:
        self.values[key] = value
        self.ttls[key] = ex


def test_build_candle_cache_key_uses_symbol_interval_and_limit() -> None:
    assert build_candle_cache_key("BTCUSDT", "1m", 200) == "candles:BTCUSDT:1m:200"


def test_get_candle_cache_ttl_selects_interval_aware_ttls() -> None:
    assert get_candle_cache_ttl("1m") == 15
    assert get_candle_cache_ttl("5m") == 45
    assert get_candle_cache_ttl("15m") == 90
    assert get_candle_cache_ttl("1h") == 240
    assert get_candle_cache_ttl("1d") == 1200


def test_redis_candle_cache_round_trips_candles_with_interval_ttl() -> None:
    redis_client = FakeRedis()
    cache = RedisCandleCache(redis_client=redis_client)
    candles = [
        CandleDTO(
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
    ]

    asyncio.run(cache.set_candles("BTCUSDT", "1m", 1, candles))
    cached_candles = asyncio.run(cache.get_candles("BTCUSDT", "1m", 1))

    assert cached_candles == candles
    assert redis_client.ttls["candles:BTCUSDT:1m:1"] == 15
