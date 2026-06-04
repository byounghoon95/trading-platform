from pydantic import BaseModel, ConfigDict, Field

from app.services.markets import MarketDTO


class MarketResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    symbol: str
    base_asset: str = Field(alias="baseAsset")
    quote_asset: str = Field(alias="quoteAsset")
    display_name: str = Field(alias="displayName")
    enabled: bool


def create_market_response(market: MarketDTO) -> MarketResponse:
    return MarketResponse(
        symbol=market.symbol,
        base_asset=market.base_asset,
        quote_asset=market.quote_asset,
        display_name=market.display_name,
        enabled=market.enabled,
    )
