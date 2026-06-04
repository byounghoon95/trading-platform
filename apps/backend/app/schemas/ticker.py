from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.clients.binance import TickerDTO


class TickerResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    symbol: str
    price: Decimal
    price_change_percent_24h: Decimal = Field(alias="priceChangePercent24h")
    updated_at: datetime = Field(alias="updatedAt")


def create_ticker_response(ticker: TickerDTO) -> TickerResponse:
    return TickerResponse(
        symbol=ticker.symbol,
        price=ticker.price,
        price_change_percent_24h=ticker.price_change_percent_24h,
        updated_at=ticker.updated_at,
    )
