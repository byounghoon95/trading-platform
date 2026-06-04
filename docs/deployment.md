# Deployment

MarketPulse deploys to k3s with the manifests in `infra/k8s`.

## Image Build Workflow

The `Images` GitHub Actions workflow builds app images on pull requests, then builds and pushes app images to Docker Hub when `main` is updated or when the workflow is run manually.

Images:

- `leebyonghoon/marketpulse-backend`
- `leebyonghoon/marketpulse-frontend`

Tags:

- `sha-<git-sha>` for immutable handoff deploys
- `latest` for compatibility with the current k3s manifests

Required repository settings:

- `DOCKERHUB_USERNAME`: Docker Hub username with push access to the `leebyonghoon` namespace.
- `DOCKERHUB_TOKEN`: Docker Hub access token with permission to push images.

No production secrets are required for this workflow.

## Manual k3s Rollout

After the image workflow succeeds, deploy a specific commit by setting both workload images to the matching `sha-<git-sha>` tag.

```sh
kubectl -n marketpulse set image deployment/backend \
  backend=leebyonghoon/marketpulse-backend:sha-<git-sha>

kubectl -n marketpulse set image deployment/frontend \
  frontend=leebyonghoon/marketpulse-frontend:sha-<git-sha>

kubectl -n marketpulse rollout status deployment/backend
kubectl -n marketpulse rollout status deployment/frontend
```

Check the public endpoints:

```sh
curl -I http://marketpulse.byhoon.co.kr/
curl -i "http://marketpulse.byhoon.co.kr/api/candles?symbol=BTCUSDT&interval=1m&limit=1"
```

Automated SSH deployment is intentionally deferred to infra TASK-09.

## PostgreSQL Runtime

The k3s manifests include a single PostgreSQL StatefulSet exposed through the in-cluster `postgres` Service. The backend reads PostgreSQL configuration from `marketpulse-config` and `marketpulse-secrets`, including `DATABASE_URL`.

Before deploying to a shared cluster, replace the placeholder PostgreSQL password values in `infra/k8s/01-config.yaml`:

```sh
kubectl apply -f infra/k8s
kubectl -n marketpulse rollout status statefulset/postgres
kubectl -n marketpulse rollout status deployment/backend
```
