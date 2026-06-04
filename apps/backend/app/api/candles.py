from typing import Annotated

from fastapi import APIRouter, HTTPException, Query

from app.clients.binance import (
    DEFAULT_CANDLE_LIMIT,
    MAX_CANDLE_LIMIT,
    BinanceClientError,
    InvalidMarketDataRequestError,
)
from app.clients.postgres import DatabaseClientError
from app.schemas.candles import CandleResponse, create_candle_response
from app.services.candles import list_candles

router = APIRouter(prefix="/api", tags=["candles"])


@router.get("/candles", response_model=list[CandleResponse])
async def list_candles_endpoint(
    symbol: Annotated[str, Query(min_length=1)],
    interval: Annotated[str, Query(min_length=1)],
    limit: Annotated[int, Query(ge=1, le=MAX_CANDLE_LIMIT)] = DEFAULT_CANDLE_LIMIT,
) -> list[CandleResponse]:
    try:
        candles = await list_candles(symbol=symbol, interval=interval, limit=limit)
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
    except DatabaseClientError as error:
        raise HTTPException(
            status_code=503,
            detail={
                "code": "data_store_unavailable",
                "message": "Market data store is unavailable",
            },
        ) from error

    return [create_candle_response(candle) for candle in candles]
