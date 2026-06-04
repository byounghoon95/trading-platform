# Kubernetes Manifests

This directory contains the baseline k3s manifests for MarketPulse.

## Resources

- `marketpulse` namespace
- Frontend Deployment, Service, and basic HTTP Ingress
- Backend Deployment and Service
- PostgreSQL StatefulSet, Service, and persistent volume claim
- Redis Deployment and Service
- Shared ConfigMap and placeholder Secret

## Images

The app images are built by the GitHub Actions image workflow and pushed to Docker Hub:

```sh
leebyonghoon/marketpulse-backend:sha-<git-sha>
leebyonghoon/marketpulse-frontend:sha-<git-sha>
```

The current baseline manifests use `latest` for compatibility with the initial k3s deployment, but `docs/deployment.md` shows how to roll out an immutable `sha-<git-sha>` tag.

Use `docs/deployment.md` for the manual k3s rollout handoff.

## Database Configuration

PostgreSQL runs as the `postgres` Service on port `5432` and stores data in the `postgres-data` volume claim created by the StatefulSet.

The backend receives database settings from `marketpulse-config` and `marketpulse-secrets`:

- `POSTGRES_DB`
- `POSTGRES_HOST`
- `POSTGRES_PORT`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `DATABASE_URL`

Replace the `DATABASE_URL` and `POSTGRES_PASSWORD` placeholder values in `infra/k8s/01-config.yaml` before applying these manifests to a shared cluster.

The backend readiness probe uses `/ready` so rollout readiness depends on PostgreSQL connectivity. Liveness stays on `/health` so Kubernetes does not restart the backend only because PostgreSQL is temporarily unavailable.

## Validate

```sh
kubectl apply --dry-run=client -f infra/k8s
```

## Deploy

```sh
kubectl apply -f infra/k8s
```

The frontend Ingress uses `marketpulse.byhoon.co.kr` over HTTP. HTTPS and cert-manager are intentionally left for a later task.

## Troubleshooting

Check database rollout and readiness:

```sh
kubectl -n marketpulse rollout status statefulset/postgres
kubectl -n marketpulse exec statefulset/postgres -- pg_isready -U marketpulse -d marketpulse
```

Inspect persistent storage:

```sh
kubectl -n marketpulse get pvc
```
