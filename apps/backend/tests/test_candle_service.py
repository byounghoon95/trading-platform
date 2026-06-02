import asyncio
from datetime import UTC, datetime
from decimal import Decimal

from app.clients.binance import CandleDTO
from app.services.candles import list_candles


class FakeBinanceClient:
    def __init__(self, candles: list[CandleDTO]) -> None:
        self.candles = candles
        self.calls = 0

    async def get_candles(self, symbol: str, interval: str, limit: int) -> list[CandleDTO]:
        self.calls += 1
        return self.candles


class FakeCandleCache:
    def __init__(self) -> None:
        self.candles: list[CandleDTO] | None = None
        self.get_calls = 0
        self.set_calls = 0

    async def get_candles(self, symbol: str, interval: str, limit: int) -> list[CandleDTO] | None:
        self.get_calls += 1
        return self.candles

    async def set_candles(
        self,
        symbol: str,
        interval: str,
        limit: int,
        candles: list[CandleDTO],
    ) -> None:
        self.set_calls += 1
        self.candles = candles


def test_list_candles_serves_repeated_requests_from_cache() -> None:
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
    client = FakeBinanceClient(candles)
    cache = FakeCandleCache()

    first_response = asyncio.run(
        list_candles("BTCUSDT", "1m", 1, client=client, candle_cache=cache)
    )
    second_response = asyncio.run(
        list_candles("BTCUSDT", "1m", 1, client=client, candle_cache=cache)
    )

    assert first_response == candles
    assert second_response == candles
    assert client.calls == 1
    assert cache.get_calls == 2
    assert cache.set_calls == 1
