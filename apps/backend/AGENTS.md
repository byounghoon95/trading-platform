# Backend Agent Guide

Track-local rules for `apps/backend/`. Root rules (behavioral guidelines, worktree, skill usage, scope) live in the repo-root `AGENTS.md`.

## Stack

- Language: Python
- Framework: FastAPI
- Cache: Redis (added in a later task — do not introduce earlier)
- Market data source: Binance public API
- Test runner: `pytest`
- Linter: `ruff`

## Coding Standards

- Use Python for all backend code.
- Keep API responses normalized and frontend-friendly.
- Validate external inputs such as `symbol`, `interval`, and `limit` before reaching downstream calls.
- Prefer clear module boundaries over premature abstraction.
- Add tests around data normalization, validation, and API behavior.
- Do not introduce Redis, WebSocket, or external integrations before the task that adds them.

## Verification

Run before declaring a backend task complete:

- `pytest`
- `ruff check .`

Record the command output in the task's `Completion Notes`. If a check cannot run, state why in the final response.
