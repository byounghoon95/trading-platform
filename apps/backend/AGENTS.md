# Backend Agent Guide

Track-local rules for `apps/backend/`. Root rules (behavioral guidelines, worktree, skill usage, scope) live in the repo-root `AGENTS.md`.

## Stack

- Language: Python
- Framework: FastAPI
- Database: PostgreSQL (added after market and ticker endpoints — do not introduce earlier)
- Cache: Redis (added after PostgreSQL persistence — do not introduce earlier)
- Market data source: Binance public API
- Test runner: `pytest`
- Linter: `ruff`

## Coding Standards

- Use Python for all backend code.
- Keep API responses normalized and frontend-friendly.
- Validate external inputs such as `symbol`, `interval`, and `limit` before reaching downstream calls.
- Prefer clear module boundaries over premature abstraction.
- Add tests around data normalization, validation, and API behavior.
- Do not introduce PostgreSQL, Redis, WebSocket, or external integrations before the task that adds them.

## Naming

- Functions/variables: `snake_case`. Constants: `UPPER_SNAKE_CASE`. Classes: `PascalCase`.
- Use verb-first function names. Avoid vague names (`handle_data`, `process_result`, `do_request`, `run`).
- Do not abbreviate domain words unless the abbreviation is standard in the API domain. Good: `dto`, `api`, `url`, `id`. Avoid: `cfg`, `svc`, `resp`, `req`.
- Function prefixes: `create_*` (build object/resource), `get_*` (fetch existing value, incl. from network/cache/files — even when returning a list), `list_*` (application-level use case exposing a collection), `normalize_*` (raw → project shape), `validate_*`, `build_*` (params/keys/URLs), `parse_*` (string → typed), `is_*`/`has_*`/`can_*` (bool).
- Do not use `fetch_*` or `read_*`; prefer `get_*`.
- Variables: prefer domain names (`symbol`, `interval`, `candles`, `ticker`) over generic ones (`data`, `result`, `item`, `response`) when a precise name is obvious.
- Variable suffixes: `_raw` (external unnormalized), `_dto`, `_response`, `_request`, `_params`.
- Constants: keep close to their domain unless shared broadly (`SUPPORTED_SYMBOLS`, `SUPPORTED_INTERVALS`, `DEFAULT_CANDLE_LIMIT`, `MAX_CANDLE_LIMIT`).
- Class suffixes by role:
  - `*Request` — request body models.
  - `*Response` — API response models.
  - `*DTO` — internal data-transfer objects.
  - `*Client` — external API clients.
  - `*Service` — only when a real stateful/coordinating service object is needed.
  - `*Error` — custom exceptions.
  - `*Params` — grouped query/outbound request params when a plain function signature becomes noisy.
  - Examples: `CandleDTO`, `CandleResponse`, `TickerResponse`, `BinanceClient`, `BinanceRateLimitError`.

## Architecture (3-tier)

`API (app/api/)` → `Service (app/services/)` → `Data access (app/clients/)`.

- **API layer**: owns FastAPI code (`APIRouter`, `Query`, `Path`, `Depends`, `HTTPException`, `response_model`). Converts service results into response schemas by calling the conversion functions in `app/schemas/`. Does not call external APIs/Redis/files directly and does not parse Binance payloads.
- **Service layer**: use-case orchestration (validation, cache, clients, normalization). Returns DTOs or simple values. Must not know FastAPI types (`Request`, `Response`, `Depends`, `HTTPException`).
- **Data access layer**: owns I/O details (paths, database queries, Redis keys, params, timeouts, status handling). Returns raw payloads or DTOs. Raises project-owned errors, never leaks low-level library exceptions.
- Do not skip the service layer for market-data endpoints.

## DTO, Schema, and Conversion

- Three shapes: external raw payload → DTO (project-owned) → response schema (public output). Never return raw payloads from route handlers.
- DTOs: frozen dataclasses, class name ends with `DTO`, Python-native fields. No Pydantic `BaseModel` unless validation/serialization is the reason for the type.
- API schemas: Pydantic models in `app/schemas/`, `snake_case` fields unless a frontend contract explicitly requires aliases. `*Response` / `*Request` suffixes. Prefer FastAPI `Query` validation over request DTOs for simple query params.
- `normalize_*`: raw → DTO. Lives in the client/service layer that owns the raw payload, not in `app/schemas/`.
- `create_*_response`: DTO → response schema. Module-level function in the matching `app/schemas/` module, next to the schema it builds. Do not use `classmethod` constructors (`from_dto`/`to_response`).
- Keep conversions explicit; avoid dict unpacking when field mapping is non-obvious.

## Routers, Services, Clients

- Router modules in `app/api/`; router variable named `router`. Handlers call services/clients only and must not parse external payloads. Use `response_model` for stable shapes. If a handler and service share a name, suffix the handler with `_endpoint`.
- Prefer service functions over service classes, named by use case (`list_candles`, `get_ticker`). Introduce a `*Service` class only when it holds dependencies/state.
- External clients in `app/clients/`; fetch functions use `get_*`. Keep external param names inside client modules. Use explicit timeouts. Raise project-owned exceptions.

## Cache (when introduced)

- Redis/cache access lives in `app/clients/` (e.g. `clients/redis.py`, `clients/candle_cache.py`), not a separate `app/cache/`.
- Cache functions: `get_*` / `set_*` / `delete_*`. Key builders: `build_*_cache_key`.
- Cache modules own Redis keys, TTLs, and DTO serialization/deserialization. Services decide cache-vs-fallback; routers never call cache modules directly.
- Redis is a short-lived performance layer only. PostgreSQL remains the durable market data store.

## Database (when introduced)

- PostgreSQL access lives in `app/clients/` or a focused data-access module under the existing client boundary.
- Database modules own SQL, table names, indexes, and DTO serialization/deserialization from rows.
- Services decide when to read stored data, refresh from Binance, persist refreshed data, or fall back after provider failures.
- Routers never call database modules directly.

## Dependencies, Errors, Async, Imports

- FastAPI dependency providers use `get_*` and live near what they provide; shared ones in `app/api/dependencies.py`. Do not hide simple values behind dependencies unless FastAPI needs to inject them. No `_dependency` suffix unless it prevents a real collision.
- Custom exceptions end with `Error`, live in `app/core/errors.py` or beside the client. Convert to HTTP at the API boundary; never raise `HTTPException` from clients/normalizers.
- `async def` for route handlers and I/O functions; not for CPU-only helpers. Await I/O at the service or route layer.
- Absolute imports from `app`; no relative imports between modules. Let `ruff` sort imports.

## Module Layout

- Layers: `app/{api,services,clients,schemas}/`; cross-cutting in `app/core/` (`config.py`, `constants.py`, `errors.py`).
- Name resource modules (route/schema/service) after the resource: natural plural when countable (`candles.py`, `markets.py`), natural singular when not (`ticker.py`). Use singular for single external systems or core concerns (`binance.py`, `config.py`, `errors.py`).

## Tests

- Files `test_<module_or_behavior>.py`, functions `test_<behavior>` (behavior over implementation names).
- Fixtures describe the value they return (`test_client`, `sample_raw_kline`, `sample_candle_dto`); avoid `mock_data`/`payload`.

## Verification

Run before declaring a backend task complete:

- `pytest`
- `ruff check .`

Record the command output in the task's `Completion Notes`. If a check cannot run, state why in the final response.
