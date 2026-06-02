from app.clients.binance import DEFAULT_CANDLE_LIMIT, BinanceClient, CandleDTO


async def list_candles(
    symbol: str,
    interval: str,
    limit: int = DEFAULT_CANDLE_LIMIT,
) -> list[CandleDTO]:
    client = BinanceClient()
    return await client.get_candles(symbol=symbol, interval=interval, limit=limit)
