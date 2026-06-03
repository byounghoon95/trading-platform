# infra TASK-04: Add GitHub Actions CI

## Status

done

## Goal

Add CI workflow for frontend and backend checks.

## Scope

- Add workflow under `.github/workflows`
- Run backend `ruff check .` and `pytest`
- Run frontend lint and `npm run build`
- Cache dependencies where it does not add complexity
- Add concurrency to cancel superseded runs on the same ref
- Keep workflow simple and maintainable

## Out of Scope

- Do not push Docker images.
- Do not deploy to k3s.

## Acceptance Criteria

- CI workflow exists and runs on push and pull_request.
- Backend job runs `ruff check .` and `pytest` and fails the run on errors.
- Frontend job runs lint and `npm run build` and fails the run on errors.
- Concurrency cancels superseded runs on the same ref.

## Verification

- Review workflow syntax locally if tooling is available.

## Completion Notes

- Status: done
- Skills used: implement-task
- Changed: added GitHub Actions CI workflow with backend ruff/pytest and frontend lint/build jobs, dependency caching, and ref-scoped concurrency cancellation.
- Verification: `python3` YAML parse check for `.github/workflows/ci.yml` -> passed; `docker run --rm -v "$PWD":/repo -w /repo rhysd/actionlint:latest .github/workflows/ci.yml` -> passed.
- Notes: workflow intentionally does not build/push images or deploy to k3s; that remains infra TASK-05.
