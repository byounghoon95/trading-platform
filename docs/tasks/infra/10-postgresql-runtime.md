# infra TASK-10: Add PostgreSQL Runtime

## Status

done

## Goal

Add PostgreSQL runtime support for local Docker Compose and k3s deployment after backend persistence is implemented.

## Scope

- Add PostgreSQL service to Docker Compose.
- Add PostgreSQL Kubernetes manifests with service, workload, and storage.
- Provide backend database connection configuration through ConfigMap and Secret values as appropriate.
- Keep Redis as a separate optional cache service.
- Update local and k3s documentation for database startup and troubleshooting.
- Validate backend readiness configuration points at PostgreSQL-aware readiness behavior.

## Out of Scope

- Do not add TimescaleDB.
- Do not add managed cloud database provisioning.
- Do not add user data, auth data, or trading order storage.
- Do not remove Redis manifests unless the Redis task explicitly changes cache deployment.

## Acceptance Criteria

- Docker Compose can run frontend, backend, PostgreSQL, and Redis with consistent service names and env vars.
- k3s manifests include PostgreSQL runtime resources needed by the backend.
- Backend receives database connection settings through documented environment variables.
- Redis remains available for the later cache task but is not the durable market data store.

## Verification

- `docker compose config`
- `kubectl apply --dry-run=client -f infra/k8s`

## Completion Notes

- Status: done
- Skills used: implement-task
- Changed: added PostgreSQL runtime support to Docker Compose and k3s manifests; wired backend database environment values through Compose, ConfigMap, and Secret values; pointed backend readiness at PostgreSQL-aware `/ready`; documented local and k3s database startup and troubleshooting.
- Verification: `docker compose -f infra/docker/compose.yaml config` -> passed; `docker compose -f infra/docker/compose.yaml up -d postgres redis` plus `ps` and `pg_isready` -> PostgreSQL and Redis healthy, PostgreSQL accepting connections; `docker compose -f infra/docker/compose.yaml down --volumes` -> cleanup passed; `kubectl apply --dry-run=client -f infra/k8s` -> passed.
- Notes: backend TASK-06 is merged, so k3s readiness now uses `/ready` while liveness remains on `/health`.
