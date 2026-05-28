# backend TASK-04: Implement Normalized Candle Endpoint

## Status

todo

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

## Skills

- Required: implement-task
- Optional: none

## Completion Notes

- Status: todo
- Skills used: none
- Verification: not run
- Notes: not started
