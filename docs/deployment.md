# Deployment

MarketPulse deploys to k3s with the Helm chart in `infra/helm/marketpulse`.

## Image Build Workflow

The `Images` GitHub Actions workflow builds app images on pull requests, then builds and pushes app images to Docker Hub when `main` is updated or when the workflow is run manually.

Images:

- `leebyonghoon/marketpulse-backend`
- `leebyonghoon/marketpulse-frontend`

Tags:

- `sha-<git-sha>` for immutable handoff deploys
- `latest` is pushed for compatibility, but Helm rollout should use immutable `sha-<git-sha>` tags.

Required repository settings:

- `DOCKERHUB_USERNAME`: Docker Hub username with push access to the `leebyonghoon` namespace.
- `DOCKERHUB_TOKEN`: Docker Hub access token with permission to push images.

No production Kubernetes secrets are required for the image build workflow.

## Database Secret

The Helm chart defaults to using an existing Kubernetes Secret named `marketpulse-secrets`. Create or update it before installing the chart:

```sh
kubectl create namespace marketpulse --dry-run=client -o yaml | kubectl apply -f -

kubectl -n marketpulse create secret generic marketpulse-secrets \
  --from-literal=POSTGRES_USER=marketpulse \
  --from-literal=POSTGRES_PASSWORD='<postgres-password>' \
  --from-literal=DATABASE_URL='postgresql://marketpulse:<postgres-password>@postgres:5432/marketpulse' \
  --dry-run=client -o yaml | kubectl apply -f -
```

Do not commit real database passwords. `infra/helm/marketpulse/values.secret.example.yaml` is only an example for local/manual installs.

## Manual k3s Rollout

After the image workflow succeeds, deploy a specific commit by setting both workload image tags to the matching `sha-<git-sha>` tag.

```sh
helm upgrade --install marketpulse infra/helm/marketpulse \
  --namespace marketpulse \
  --create-namespace \
  --set backend.image.tag=sha-<git-sha> \
  --set frontend.image.tag=sha-<git-sha>
```

Wait for rollouts:

```sh
kubectl -n marketpulse rollout status statefulset/postgres
kubectl -n marketpulse rollout status deployment/backend
kubectl -n marketpulse rollout status deployment/frontend
kubectl -n marketpulse rollout status deployment/prometheus
kubectl -n marketpulse rollout status deployment/grafana
```

Check the public endpoints:

```sh
curl -I http://marketpulse.byhoon.co.kr/
curl -i "http://marketpulse.byhoon.co.kr/api/candles?symbol=BTCUSDT&interval=1m&limit=1"
```

## Rollback

List Helm revisions:

```sh
helm history marketpulse -n marketpulse
```

Roll back to a known-good revision:

```sh
helm rollback marketpulse <revision> -n marketpulse
kubectl -n marketpulse rollout status deployment/backend
kubectl -n marketpulse rollout status deployment/frontend
```

Automated SSH or GitOps deployment remains deferred to infra TASK-09.
