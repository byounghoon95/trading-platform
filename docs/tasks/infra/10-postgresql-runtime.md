# infra TASK-10: Add PostgreSQL Runtime

## Status

todo

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
