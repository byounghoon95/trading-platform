from app.clients.binance import (
    DEFAULT_CANDLE_LIMIT,
    BinanceClient,
    CandleDTO,
    validate_interval,
    validate_limit,
    validate_symbol,
)
from app.clients.candle_cache import CandleCacheError, RedisCandleCache


async def list_candles(
    symbol: str,
    interval: str,
    limit: int = DEFAULT_CANDLE_LIMIT,
    client: BinanceClient | None = None,
    candle_cache: RedisCandleCache | None = None,
) -> list[CandleDTO]:
    validate_symbol(symbol)
    validate_interval(interval)
    validate_limit(limit)

    cache = candle_cache or RedisCandleCache()
    try:
        cached_candles = await cache.get_candles(symbol=symbol, interval=interval, limit=limit)
    except CandleCacheError:
        cached_candles = None

    if cached_candles is not None:
        return cached_candles

    market_data_client = client or BinanceClient()
    candles = await market_data_client.get_candles(symbol=symbol, interval=interval, limit=limit)

    try:
        await cache.set_candles(symbol=symbol, interval=interval, limit=limit, candles=candles)
    except CandleCacheError:
        pass

    return candles
