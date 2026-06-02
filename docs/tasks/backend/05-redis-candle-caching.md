# backend TASK-05: Add Redis Candle Caching

## Status

done

## Goal

Cache candle API responses in Redis to reduce external API calls.

## Scope

- Add Redis client to backend
- Cache by `symbol`, `interval`, and `limit`
- Use interval-aware TTLs per `docs/spec.md` §8
- Update the readiness path (`/health` or a dedicated `/ready`) to fail when Redis is unreachable, while keeping liveness independent of Redis
- Add tests around cache key and TTL selection
- Add a test that readiness fails when the Redis client cannot connect

## Out of Scope

- Do not persist candles to PostgreSQL or TimescaleDB.
- Do not add distributed locking.

## Acceptance Criteria

- Repeated candle requests can be served from cache.
- Cache keys and TTLs are documented or tested.
- Readiness fails (HTTP 503 or equivalent) when Redis is unreachable; liveness still returns 200.
- `infra/k8s` readiness probe target is updated if a new path is introduced (note for the matching infra task).

## Verification

- `pytest`

## Completion Notes

- Status: done
- Skills used: implement-task, requesting-code-review
- Changed: added Redis candle cache client, Redis readiness check, candle service cache orchestration, Redis dependency metadata, and focused backend tests
- Verification: `.venv/bin/python -m pytest` -> 21 passed; `.venv/bin/ruff check .` -> all checks passed
- Notes: `/health` remains liveness-only; `/ready` now fails with HTTP 503 when Redis is unreachable. Cache read/write failures fall back to Binance so readiness, not the candle route, owns dependency gating. Local code review found no blocking issues.
