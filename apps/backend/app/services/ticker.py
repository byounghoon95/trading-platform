from app.clients.binance import BinanceClient, TickerDTO


async def get_ticker(symbol: str) -> TickerDTO:
    client = BinanceClient()
    return await client.get_ticker(symbol=symbol)
