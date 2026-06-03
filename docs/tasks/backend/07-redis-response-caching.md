# backend TASK-07: Add Redis Response Caching

## Status

todo

## Goal

Cache recent candle and ticker responses in Redis after PostgreSQL persistence is in place.

## Scope

- Add Redis client to backend
- Cache by `symbol`, `interval`, and `limit`
- Cache the latest ticker response per supported symbol
- Use interval-aware TTLs per `docs/spec.md` §8
- Update the readiness path (`/health` or a dedicated `/ready`) to fail when Redis is unreachable, while keeping liveness independent of Redis
- Add tests around cache key and TTL selection
- Add a test that readiness fails when the Redis client cannot connect

## Out of Scope

- Do not replace PostgreSQL persistence with Redis.
- Do not add TimescaleDB-specific features.
- Do not add distributed locking.

## Acceptance Criteria

- Repeated candle requests can be served from cache.
- Repeated ticker requests can be served from cache.
- Redis stores only short-lived recent responses; PostgreSQL remains the durable store.
- Cache keys and TTLs are documented or tested.
- Readiness fails (HTTP 503 or equivalent) when Redis is unreachable; liveness still returns 200.
- `infra/k8s` readiness probe target is updated if a new path is introduced (note for the matching infra task).

## Verification

- `pytest`
