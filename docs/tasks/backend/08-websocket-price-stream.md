# backend TASK-08: Add WebSocket Price Stream

## Status

todo

## Goal

Add a backend WebSocket stream for normalized ticker updates after the HTTP ticker endpoint, PostgreSQL persistence, and Redis caching are stable.

## Scope

- Add backend WebSocket endpoint for selected ticker updates
- Connect backend to Binance stream or a controlled stream adapter
- Normalize stream payloads before sending them to clients
- Validate supported symbols
- Keep the HTTP ticker endpoint available as a fallback
- Add tests for stream payload normalization where practical

## Files Expected To Change

- `apps/backend/app/api/ws.py`
- `apps/backend/app/market_data/binance_stream.py`
- `apps/backend/app/models/ticker.py`
- `apps/backend/app/main.py`
- `apps/backend/tests/test_ticker_stream.py`

## Out of Scope

- Do not add trading orders.
- Do not add private exchange API keys.
- Do not replace the candle HTTP endpoint.
- Do not implement frontend WebSocket UI in this task.

## Acceptance Criteria

- Backend can emit normalized current price updates over WebSocket.
- Invalid symbols are rejected.
- HTTP polling remains available.
- Tests cover stream payload normalization where practical.

## Verification

- `pytest`
- Manual WebSocket smoke test
