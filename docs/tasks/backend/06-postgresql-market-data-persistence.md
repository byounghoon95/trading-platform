# backend TASK-06: Add PostgreSQL Market Data Persistence

## Status

todo

## Goal

Persist normalized market data in PostgreSQL so backend responses can use project-owned stored data instead of relying only on live Binance calls.

## Scope

- Add PostgreSQL configuration to the backend.
- Add database schema management for market data tables.
- Persist normalized candle data by `symbol`, `interval`, and `open_time`.
- Persist normalized ticker snapshots by `symbol` and `updated_at`.
- Upsert candle data after successful Binance candle responses.
- Insert or upsert ticker snapshots after successful Binance ticker responses.
- Serve API responses from stored DTO-shaped records after persistence is applied.
- Keep Binance as the source used to refresh missing or stale records.
- Add tests for schema setup, candle persistence, ticker persistence, and API fallback behavior.
- Update backend readiness to fail when PostgreSQL is unreachable while keeping liveness independent of PostgreSQL.

## Out of Scope

- Do not add Redis caching in this task.
- Do not add TimescaleDB-specific features.
- Do not add user watchlists or user-specific storage.
- Do not add trading orders or exchange API keys.
- Do not add WebSocket streaming.

## Acceptance Criteria

- Candle responses can be persisted and read back from PostgreSQL.
- Ticker responses can be persisted and read back from PostgreSQL.
- Binance remains available as the refresh source when stored data is missing or stale.
- Backend readiness fails when PostgreSQL is unreachable; liveness still returns 200.
- Tests cover persistence behavior and invalid market input handling.
- Required infrastructure follow-up is documented for Docker Compose and k3s PostgreSQL runtime.

## Verification

- `pytest`
- `ruff check .`
