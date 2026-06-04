# Tasks

Task specs are split by track so backend, frontend, and infrastructure work can move in parallel when dependencies allow it.

Use:

```text
$writing-plans backend TASK-01
$implement-task backend TASK-01
$requesting-code-review backend TASK-01
$implement-task frontend TASK-02
$implement-task infra TASK-03
```

Use `$brainstorming` when changing `docs/spec.md` or designing a new feature.
Use `$writing-plans` to refine a task before implementation.
Use `$implement-task` to execute one task.
Use `$requesting-code-review` to review a completed task.

## Status Values

Each row in the Index uses a leading icon plus the status word so the table scans quickly.

- ⬜ `todo`: not started
- 🟡 `doing`: currently being implemented
- ✅ `done`: completed and verified
- ⛔ `blocked`: cannot continue without a decision or external dependency

## Defaults

- Each task uses `implement-task` as its skill unless the task file states otherwise.
- Task files do not pre-fill empty completion blocks. When a task is finished, append the block below before merging.

```md
## Completion Notes

- Status: done
- Skills used: implement-task
- Changed: short summary of changed areas
- Verification: command and result, or reason not run
- Notes: important decisions or follow-up tasks
```

## Index

Status values come from `## Status Values` above. Update this column **and** the matching task file's `## Status` before merging the task branch to `main`.

| Track Task | Status | Depends On | File |
| --- | --- | --- | --- |
| foundation TASK-01 | ✅ done | none | [01-repository-structure.md](foundation/01-repository-structure.md) |
| frontend TASK-01 | ✅ done | foundation TASK-01 | [01-frontend-scaffold.md](frontend/01-frontend-scaffold.md) |
| frontend TASK-02 | ✅ done | frontend TASK-01 | [02-frontend-mocked-candle-chart.md](frontend/02-frontend-mocked-candle-chart.md) |
| frontend TASK-03 | ✅ done | backend TASK-04, backend TASK-05, frontend TASK-02 | [03-frontend-candle-api.md](frontend/03-frontend-candle-api.md) |
| backend TASK-01 | ✅ done | foundation TASK-01 | [01-backend-scaffold.md](backend/01-backend-scaffold.md) |
| backend TASK-02 | ✅ done | backend TASK-01 | [02-backend-health-endpoint.md](backend/02-backend-health-endpoint.md) |
| backend TASK-03 | ✅ done | backend TASK-01 | [03-binance-candle-client.md](backend/03-binance-candle-client.md) |
| backend TASK-04 | ✅ done | backend TASK-02, backend TASK-03 | [04-normalized-candle-endpoint.md](backend/04-normalized-candle-endpoint.md) |
| backend TASK-05 | ✅ done | backend TASK-03 | [05-market-ticker-endpoints.md](backend/05-market-ticker-endpoints.md) |
| backend TASK-06 | ✅ done | backend TASK-04, backend TASK-05 | [06-postgresql-market-data-persistence.md](backend/06-postgresql-market-data-persistence.md) |
| backend TASK-07 | ⬜ todo | backend TASK-06 | [07-redis-response-caching.md](backend/07-redis-response-caching.md) |
| infra TASK-01 | ✅ done | foundation TASK-01 | [01-docker-compose-baseline.md](infra/01-docker-compose-baseline.md) |
| infra TASK-02 | ✅ done | frontend TASK-01, backend TASK-01 | [02-production-dockerfiles.md](infra/02-production-dockerfiles.md) |
| infra TASK-03 | ✅ done | infra TASK-01, infra TASK-02 | [03-k3s-manifests.md](infra/03-k3s-manifests.md) |
| infra TASK-04 | ✅ done | frontend TASK-01, backend TASK-01 | [04-github-actions-ci.md](infra/04-github-actions-ci.md) |
| infra TASK-05 | ✅ done | infra TASK-02, infra TASK-03, infra TASK-04 | [05-image-build-deploy-workflow.md](infra/05-image-build-deploy-workflow.md) |
| backend TASK-08 | ⬜ todo | backend TASK-07 | [08-websocket-price-stream.md](backend/08-websocket-price-stream.md) |
| frontend TASK-04 | ⬜ todo | frontend TASK-03, backend TASK-08 | [04-websocket-price-client.md](frontend/04-websocket-price-client.md) |
| infra TASK-06 | ✅ done | backend TASK-04, backend TASK-05, infra TASK-03 | [06-metrics-prometheus.md](infra/06-metrics-prometheus.md) |
| infra TASK-07 | ✅ done | infra TASK-06 | [07-grafana-dashboard.md](infra/07-grafana-dashboard.md) |
| infra TASK-08 | ⬜ todo | infra TASK-03 | [08-https-cert-manager.md](infra/08-https-cert-manager.md) |
| infra TASK-09 | ⬜ todo | infra TASK-05, infra TASK-08 | [09-k3s-deploy-automation.md](infra/09-k3s-deploy-automation.md) |
| infra TASK-10 | ✅ done | backend TASK-06, infra TASK-03 | [10-postgresql-runtime.md](infra/10-postgresql-runtime.md) |
| portfolio TASK-01 | ⬜ todo | frontend TASK-04, backend TASK-07, backend TASK-08, infra TASK-06, infra TASK-07, infra TASK-08, infra TASK-09, infra TASK-10 | [01-final-readme-portfolio-docs.md](portfolio/01-final-readme-portfolio-docs.md) |

## Parallel Work

After `foundation TASK-01`, these tracks can move independently:

- Backend: `backend TASK-01 -> backend TASK-02/backend TASK-03 -> backend TASK-04/backend TASK-05 -> backend TASK-06 -> backend TASK-07`
- Backend advanced: `backend TASK-08` adds WebSocket streaming after HTTP ticker, PostgreSQL persistence, and Redis cache behavior are stable
- Frontend: `frontend TASK-01 -> frontend TASK-02`, then wait for `backend TASK-04` and `backend TASK-05` before `frontend TASK-03`; `frontend TASK-04` adds WebSocket UI after backend streaming
- Infra: `infra TASK-01`, then `infra TASK-02/infra TASK-04`, then `infra TASK-03/infra TASK-05`; PostgreSQL runtime follows `backend TASK-06`; metrics waits for backend API endpoints, then Grafana/HTTPS/deploy automation follow

## Suggested Flow

```text
foundation TASK-01
  |
  +--> backend:  TASK-01 -> TASK-02 -> TASK-03 -> TASK-04 -> TASK-06 -> TASK-07 -> TASK-08
  |                                      \-----> TASK-05 ----^
  +--> frontend: TASK-01 -> TASK-02 ------------------------> TASK-03 -> TASK-04
  +--> infra:    TASK-01 -> TASK-02 -> TASK-03 -> TASK-05 -> TASK-09
  |                        TASK-04 ----------^
  |                        backend TASK-04/TASK-05 -> infra TASK-06 -> TASK-07
  |                        backend TASK-06 ----------> infra TASK-10
  |                                                 \-----> TASK-08 ----^
  |
  +--> portfolio: TASK-01
```
