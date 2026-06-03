# backend TASK-05: Add Market And Ticker Endpoints

## Status

todo

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
- `apps/backend/app/market_data/binance.py`
- `apps/backend/app/models/market.py`
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
