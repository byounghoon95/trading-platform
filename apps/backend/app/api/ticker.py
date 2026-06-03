from typing import Annotated

from fastapi import APIRouter, HTTPException, Query

from app.clients.binance import (
    BinanceClientError,
    InvalidMarketDataRequestError,
)
from app.schemas.ticker import TickerResponse, create_ticker_response
from app.services.ticker import get_ticker

router = APIRouter(prefix="/api", tags=["ticker"])


@router.get("/ticker", response_model=TickerResponse)
async def get_ticker_endpoint(
    symbol: Annotated[str, Query(min_length=1)],
) -> TickerResponse:
    try:
        ticker = await get_ticker(symbol=symbol)
    except InvalidMarketDataRequestError as error:
        raise HTTPException(
            status_code=422,
            detail={
                "code": "invalid_market_data_request",
                "message": str(error),
            },
        ) from error
    except BinanceClientError as error:
        raise HTTPException(
            status_code=502,
            detail={
                "code": "market_data_unavailable",
                "message": "Market data provider request failed",
            },
        ) from error

    return create_ticker_response(ticker)
