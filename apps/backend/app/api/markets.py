from fastapi import APIRouter

from app.schemas.markets import MarketResponse, create_market_response
from app.services.markets import list_markets

router = APIRouter(prefix="/api", tags=["markets"])


@router.get("/markets", response_model=list[MarketResponse])
async def list_markets_endpoint() -> list[MarketResponse]:
    markets = list_markets()
    return [create_market_response(market) for market in markets]
