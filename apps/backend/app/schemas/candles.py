from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel

from app.clients.binance import CandleDTO


class CandleResponse(BaseModel):
    symbol: str
    interval: str
    open_time: datetime
    close_time: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal


def create_candle_response(candle: CandleDTO) -> CandleResponse:
    return CandleResponse(
        symbol=candle.symbol,
        interval=candle.interval,
        open_time=candle.open_time,
        close_time=candle.close_time,
        open=candle.open,
        high=candle.high,
        low=candle.low,
        close=candle.close,
        volume=candle.volume,
    )
