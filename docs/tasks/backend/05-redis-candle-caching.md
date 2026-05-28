# backend TASK-05: Add Redis Candle Caching

## Status

todo

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

