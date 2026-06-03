from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from app.clients.binance import TickerDTO


class TickerResponse(BaseModel):
    symbol: str
    price: Decimal
    price_change_percent_24h: Decimal = Field(
        serialization_alias="priceChangePercent24h"
    )
    updated_at: datetime = Field(serialization_alias="updatedAt")


def create_ticker_response(ticker: TickerDTO) -> TickerResponse:
    return TickerResponse(
        symbol=ticker.symbol,
        price=ticker.price,
        price_change_percent_24h=ticker.price_change_percent_24h,
        updated_at=ticker.updated_at,
    )
