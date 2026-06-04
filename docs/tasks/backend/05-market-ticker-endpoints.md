# backend TASK-05: Add Market And Ticker Endpoints

## Status

done

## Goal

Expose frontend-friendly market metadata and polling ticker data.

## Scope

- Add `GET /api/markets`
- Add `GET /api/ticker?symbol=BTCUSDT`
- Return normalized market objects with `symbol`, `baseAsset`, `quoteAsset`, `displayName`, and `enabled`
- Return normalized ticker objects with `symbol`, `price`, `priceChangePercent24h`, and `updatedAt`
- Validate supported symbols
- Add tests for valid and invalid requests

## Files Expected To Change

- `apps/backend/app/api/markets.py`
- `apps/backend/app/api/ticker.py`
- `apps/backend/app/schemas/markets.py`
- `apps/backend/app/schemas/ticker.py`
- `apps/backend/app/services/markets.py`
- `apps/backend/app/services/ticker.py`
- `apps/backend/app/main.py`
- `apps/backend/tests/test_markets.py`
- `apps/backend/tests/test_ticker.py`

## Out of Scope

- Do not add PostgreSQL persistence in this task.
- Do not add WebSocket streaming.
- Do not add user watchlists.
- Do not add Redis caching for ticker data unless needed for rate-limit protection.

## Acceptance Criteria

- `GET /api/markets` returns the supported MVP markets from `docs/spec.md`.
- `GET /api/ticker` returns normalized current price and 24h change data.
- Invalid symbols return structured validation errors.
- Tests cover successful and invalid requests.

## Verification

- `pytest`
- `ruff check .`

## Implementation Plan

# Market And Ticker Endpoints Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `implement-task` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add `GET /api/markets` and `GET /api/ticker` with normalized frontend-friendly responses and structured error handling.

**Architecture:** Follow the existing backend 3-tier shape: routers in `app/api/`, use-case functions in `app/services/`, public Pydantic response models in `app/schemas/`, and Binance I/O in `app/clients/binance.py`. `BinanceClient.get_ticker()` and `TickerDTO` already exist, so this task only wires service/schema/router behavior and static MVP market metadata. PostgreSQL and Redis stay out of scope.

**Tech Stack:** FastAPI, Pydantic, frozen dataclass DTOs, pytest, ruff.

---

### Task 1: Market Metadata Endpoint

**Files:**
- Create: `apps/backend/app/services/markets.py`
- Create: `apps/backend/app/schemas/markets.py`
- Create: `apps/backend/app/api/markets.py`
- Modify: `apps/backend/app/main.py`
- Test: `apps/backend/tests/test_markets.py`

- [x] **Step 1: Write the failing market endpoint test**

Create `apps/backend/tests/test_markets.py`:

```python
from fastapi.testclient import TestClient

from app.main import app


def test_markets_endpoint_returns_supported_mvp_markets() -> None:
    test_client = TestClient(app)

    response = test_client.get("/api/markets")

    assert response.status_code == 200
    assert response.json() == [
        {
            "symbol": "BTCUSDT",
            "baseAsset": "BTC",
            "quoteAsset": "USDT",
            "displayName": "BTC / USDT",
            "enabled": True,
        },
        {
            "symbol": "ETHUSDT",
            "baseAsset": "ETH",
            "quoteAsset": "USDT",
            "displayName": "ETH / USDT",
            "enabled": True,
        },
    ]
```

- [x] **Step 2: Run the failing market test**

Run:

```bash
cd apps/backend
pytest tests/test_markets.py -v
```

Expected: fail because `/api/markets` is not registered yet.

- [x] **Step 3: Add market DTOs, schema conversion, service, and router**

Create `apps/backend/app/services/markets.py`:

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class MarketDTO:
    symbol: str
    base_asset: str
    quote_asset: str
    display_name: str
    enabled: bool


SUPPORTED_MARKETS = (
    MarketDTO(
        symbol="BTCUSDT",
        base_asset="BTC",
        quote_asset="USDT",
        display_name="BTC / USDT",
        enabled=True,
    ),
    MarketDTO(
        symbol="ETHUSDT",
        base_asset="ETH",
        quote_asset="USDT",
        display_name="ETH / USDT",
        enabled=True,
    ),
)


def list_markets() -> list[MarketDTO]:
    return list(SUPPORTED_MARKETS)
```

Create `apps/backend/app/schemas/markets.py`:

```python
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
```

Create `apps/backend/app/api/markets.py`:

```python
from fastapi import APIRouter

from app.schemas.markets import MarketResponse, create_market_response
from app.services.markets import list_markets

router = APIRouter(prefix="/api", tags=["markets"])


@router.get("/markets", response_model=list[MarketResponse])
async def list_markets_endpoint() -> list[MarketResponse]:
    markets = list_markets()
    return [create_market_response(market) for market in markets]
```

Update `apps/backend/app/main.py`:

```python
from fastapi import FastAPI

from app.api.candles import router as candles_router
from app.api.health import router as health_router
from app.api.markets import router as markets_router
from app.core.config import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    fastapi_app = FastAPI(title=settings.app_name)
    fastapi_app.include_router(health_router)
    fastapi_app.include_router(candles_router)
    fastapi_app.include_router(markets_router)
    return fastapi_app


app = create_app()
```

- [x] **Step 4: Run the market test**

Run:

```bash
cd apps/backend
pytest tests/test_markets.py -v
```

Expected: pass.

### Task 2: Ticker Endpoint

**Files:**
- Create: `apps/backend/app/services/ticker.py`
- Create: `apps/backend/app/schemas/ticker.py`
- Create: `apps/backend/app/api/ticker.py`
- Modify: `apps/backend/app/main.py`
- Test: `apps/backend/tests/test_ticker.py`

- [x] **Step 1: Write ticker endpoint tests**

Create `apps/backend/tests/test_ticker.py`:

```python
from datetime import UTC, datetime
from decimal import Decimal

from fastapi.testclient import TestClient

from app.clients.binance import BinanceClientError, InvalidMarketDataRequestError, TickerDTO
from app.main import app


def test_ticker_endpoint_returns_normalized_ticker(monkeypatch) -> None:
    async def get_ticker_stub(symbol: str) -> TickerDTO:
        assert symbol == "BTCUSDT"
        return TickerDTO(
            symbol="BTCUSDT",
            price=Decimal("68000.01"),
            price_change_percent_24h=Decimal("2.50"),
            updated_at=datetime(2023, 11, 14, 22, 13, 20, tzinfo=UTC),
        )

    monkeypatch.setattr("app.api.ticker.get_ticker", get_ticker_stub)
    test_client = TestClient(app)

    response = test_client.get("/api/ticker?symbol=BTCUSDT")

    assert response.status_code == 200
    assert response.json() == {
        "symbol": "BTCUSDT",
        "price": "68000.01",
        "priceChangePercent24h": "2.50",
        "updatedAt": "2023-11-14T22:13:20Z",
    }


def test_ticker_endpoint_returns_structured_error_for_invalid_symbol(monkeypatch) -> None:
    async def get_ticker_stub(symbol: str) -> TickerDTO:
        raise InvalidMarketDataRequestError(f"Unsupported symbol: {symbol}")

    monkeypatch.setattr("app.api.ticker.get_ticker", get_ticker_stub)
    test_client = TestClient(app)

    response = test_client.get("/api/ticker?symbol=DOGEUSDT")

    assert response.status_code == 422
    assert response.json() == {
        "detail": {
            "code": "invalid_market_data_request",
            "message": "Unsupported symbol: DOGEUSDT",
        }
    }


def test_ticker_endpoint_returns_bad_gateway_for_provider_failure(monkeypatch) -> None:
    async def get_ticker_stub(symbol: str) -> TickerDTO:
        raise BinanceClientError("provider failed")

    monkeypatch.setattr("app.api.ticker.get_ticker", get_ticker_stub)
    test_client = TestClient(app)

    response = test_client.get("/api/ticker?symbol=ETHUSDT")

    assert response.status_code == 502
    assert response.json() == {
        "detail": {
            "code": "market_data_unavailable",
            "message": "Market data provider request failed",
        }
    }
```

- [x] **Step 2: Run the failing ticker tests**

Run:

```bash
cd apps/backend
pytest tests/test_ticker.py -v
```

Expected: fail because `app.api.ticker` does not exist yet.

- [x] **Step 3: Add ticker service, schema conversion, router, and route registration**

Create `apps/backend/app/services/ticker.py`:

```python
from app.clients.binance import BinanceClient, TickerDTO


async def get_ticker(symbol: str) -> TickerDTO:
    client = BinanceClient()
    return await client.get_ticker(symbol=symbol)
```

Create `apps/backend/app/schemas/ticker.py`:

```python
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
```

Create `apps/backend/app/api/ticker.py`:

```python
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
```

Update `apps/backend/app/main.py` to include the ticker router:

```python
from fastapi import FastAPI

from app.api.candles import router as candles_router
from app.api.health import router as health_router
from app.api.markets import router as markets_router
from app.api.ticker import router as ticker_router
from app.core.config import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    fastapi_app = FastAPI(title=settings.app_name)
    fastapi_app.include_router(health_router)
    fastapi_app.include_router(candles_router)
    fastapi_app.include_router(markets_router)
    fastapi_app.include_router(ticker_router)
    return fastapi_app


app = create_app()
```

- [x] **Step 4: Run ticker tests**

Run:

```bash
cd apps/backend
pytest tests/test_ticker.py -v
```

Expected: pass.

### Task 3: Full Backend Verification And Task Notes

**Files:**
- Modify: `docs/tasks/README.md`
- Modify: `docs/tasks/backend/05-market-ticker-endpoints.md`

- [x] **Step 1: Run full backend checks**

Run:

```bash
cd apps/backend
pytest
ruff check .
```

Expected: all tests pass and ruff reports no issues.

- [x] **Step 2: Update task status and notes**

Update `docs/tasks/README.md` so `backend TASK-05` status is `✅ done`.

Update this file's `## Status` to `done`, then append:

```md
## Completion Notes

- Status: done
- Skills used: writing-plans, implement-task
- Changed: added market metadata and polling ticker API endpoints with service/schema/router boundaries and endpoint tests.
- Verification: `pytest` -> expected full backend test pass count; `ruff check .` -> all checks passed.
- Notes: kept PostgreSQL persistence, Redis caching, WebSocket streaming, and frontend integration out of scope for later tasks.
```

- [x] **Step 3: Commit**

Run:

```bash
git add apps/backend docs/tasks
git commit -m "feature(backend): add market ticker endpoints"
```

## Completion Notes

- Status: done
- Skills used: writing-plans, implement-task
- Changed: added market metadata and polling ticker API endpoints with service/schema/router boundaries and endpoint tests.
- Verification: `.venv/bin/python -m pytest` -> 19 passed; `.venv/bin/ruff check .` -> all checks passed.
- Notes: kept PostgreSQL persistence, Redis caching, WebSocket streaming, and frontend integration out of scope for later tasks.
