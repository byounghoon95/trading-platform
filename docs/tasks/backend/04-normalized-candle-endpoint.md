# backend TASK-04: Implement Normalized Candle Endpoint

## Status

done

## Goal

Expose normalized candle data through the backend API.

## Scope

- Add `GET /api/candles`
- Accept `symbol`, `interval`, and `limit`
- Validate query parameters
- Return normalized candle objects
- Add tests

## Out of Scope

- Do not add Redis caching.
- Do not add frontend chart integration.

## Acceptance Criteria

- Valid requests return normalized candles.
- Invalid requests return structured errors.
- Tests cover valid and invalid requests.

## Verification

- `pytest`

## Completion Notes

- Status: done
- Skills used: implement-task, requesting-code-review
- Changed: added `/api/candles` route, candle service/schema conversion, and endpoint tests for success and error cases
- Verification: `/tmp/backend-task-04-venv/bin/python -m pytest` -> 15 passed; `/tmp/backend-task-04-venv/bin/ruff check .` -> all checks passed
- Notes: Redis caching and frontend integration remain out of scope for later tasks; current-session code review found no blocking issues

