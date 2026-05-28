# Frontend Agent Guide

Track-local rules for `apps/frontend/`. Root rules (behavioral guidelines, worktree, skill usage, scope) live in the repo-root `AGENTS.md`.

## Stack

- Language: JavaScript (no TypeScript unless a task asks for it)
- Framework: React
- Bundler / dev server: Vite
- Charting: Lightweight Charts

## Coding Standards

- Use JavaScript for all frontend code.
- Handle loading, error, empty, and disconnected states in the UI.
- Keep API client code thin — let the backend return frontend-friendly shapes.
- Prefer clear module boundaries over premature abstraction.
- Compute light derivations (moving averages, simple aggregates) client-side from the normalized response when the task allows it.

## Verification

Run before declaring a frontend task complete:

- lint (`npm run lint` or the project's configured command)
- test (`npm test` or the project's configured command)
- build (`npm run build`)

Record the command output in the task's `Completion Notes`. If a check cannot run, state why in the final response.
