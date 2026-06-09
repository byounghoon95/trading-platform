# Operations

This document is the day-2 runbook for MarketPulse. It explains how to inspect health, deployment status, metrics, logs, ingress, database readiness, and common failure modes.

## Operating Principles

- Git is the source of truth for Kubernetes resources managed by Argo CD.
- GitHub Actions builds images and updates GitOps values, but does not access the cluster.
- Argo CD syncs and self-heals the cluster from `main`.
- Manual `kubectl` changes are useful for diagnosis, but durable fixes should go through Git.
- PostgreSQL is the durable market data store.

## Quick Health Checklist

Use this order when a user reports that the site is broken:

```text
1. Public URL
2. DNS
3. Ingress
4. Services and endpoints
5. Pods and rollouts
6. Backend logs
7. Backend health/API
8. PostgreSQL readiness
9. Argo CD sync/health
10. GitHub Actions image/deploy history
11. Prometheus/Grafana
```

Commands:

```sh
curl -I https://marketpulse.byhoon.co.kr/
curl -i "https://marketpulse.byhoon.co.kr/api/markets"

dig +short marketpulse.byhoon.co.kr

kubectl -n marketpulse get ingress
kubectl -n marketpulse describe ingress marketpulse

kubectl -n marketpulse get svc
kubectl -n marketpulse get endpoints

kubectl -n marketpulse get pods -o wide
kubectl -n marketpulse rollout status deployment/frontend
kubectl -n marketpulse rollout status deployment/backend

kubectl -n marketpulse logs deployment/backend
kubectl -n argocd get application marketpulse
```

## Public Endpoints

Dashboard:

```sh
curl -I https://marketpulse.byhoon.co.kr/
```

API through Ingress:

```sh
curl -i "https://marketpulse.byhoon.co.kr/api/markets"
curl -i "https://marketpulse.byhoon.co.kr/api/ticker?symbol=BTCUSDT"
curl -i "https://marketpulse.byhoon.co.kr/api/candles?symbol=BTCUSDT&interval=1m&limit=5"
```

Monitoring:

```sh
curl -I http://prometheus.marketpulse.byhoon.co.kr/
curl -I http://grafana.marketpulse.byhoon.co.kr/
```

## Backend Health

The backend exposes:

- `GET /health` for liveness.
- `GET /ready` for PostgreSQL readiness.
- `GET /metrics` for Prometheus-compatible metrics.

Local validation:

```sh
cd apps/backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
curl http://localhost:8000/health
curl http://localhost:8000/ready
curl http://localhost:8000/metrics
```

Cluster validation through port-forward:

```sh
kubectl -n marketpulse port-forward service/backend 8000:8000
curl http://localhost:8000/health
curl http://localhost:8000/ready
curl http://localhost:8000/metrics
```

Readiness behavior:

- `/health` should stay independent of PostgreSQL and return liveness.
- `/ready` returns 503 when `DATABASE_URL` is missing or PostgreSQL is unreachable.

## Backend Metrics

Expected metric families include:

- `marketpulse_http_requests_total`
- `marketpulse_http_request_duration_seconds_count`
- `marketpulse_http_request_duration_seconds_sum`
- `marketpulse_health_status`
- `marketpulse_external_api_failures_total`

The Helm chart annotates the backend pod and service for Prometheus scrape discovery:

```yaml
prometheus.io/scrape: "true"
prometheus.io/path: /metrics
prometheus.io/port: "8000"
```

Prometheus Operator CRDs are intentionally not required for this compact k3s runtime.

## Prometheus And Grafana

The Helm chart deploys Prometheus and Grafana in the `marketpulse` namespace.

Prometheus:

- Scrapes backend metrics from the in-cluster backend service.
- Keeps in-pod data for the configured retention period.
- Exposes the Prometheus UI through HTTP Ingress.

Grafana:

- Uses Prometheus as the default data source.
- Provisions the `MarketPulse Operations` dashboard from a ConfigMap.
- Exposes the Grafana UI through HTTP Ingress.

Deployment checks:

```sh
kubectl -n marketpulse rollout status deployment/prometheus
kubectl -n marketpulse rollout status deployment/grafana
kubectl -n marketpulse get configmap grafana-dashboard-marketpulse
```

Validate Prometheus targets:

```sh
kubectl -n marketpulse port-forward service/prometheus 9090:9090
curl http://localhost:9090/api/v1/targets
```

Open Grafana locally:

```sh
kubectl -n marketpulse port-forward service/grafana 3000:3000
```

Then open:

```text
http://localhost:3000
```

Public Grafana URL:

```text
http://grafana.marketpulse.byhoon.co.kr
```

Development default credentials:

- Username: `admin`
- Password: `admin`

Change the default password after public login.

Dashboard artifact:

```text
infra/helm/marketpulse/files/grafana/marketpulse-dashboard.json
```

## PostgreSQL Runtime

PostgreSQL stores normalized candle and ticker data when `DATABASE_URL` is configured.

Local Docker Compose uses:

```text
DATABASE_URL=postgresql://marketpulse:marketpulse@postgres:5432/marketpulse
```

Local checks:

```sh
docker compose -f infra/docker/compose.yaml ps postgres
docker compose -f infra/docker/compose.yaml exec postgres pg_isready -U marketpulse -d marketpulse
```

k3s checks:

```sh
kubectl -n marketpulse rollout status statefulset/postgres
kubectl -n marketpulse exec statefulset/postgres -- pg_isready -U marketpulse -d marketpulse
kubectl -n marketpulse get pvc
```

Secret checks:

```sh
kubectl -n marketpulse get secret marketpulse-secrets
kubectl -n marketpulse describe secret marketpulse-secrets
```

Do not print secret values in logs or screenshots.

## Ingress And HTTPS

Main dashboard host:

```text
https://marketpulse.byhoon.co.kr
```

Ingress checks:

```sh
kubectl -n marketpulse get ingress marketpulse
kubectl -n marketpulse describe ingress marketpulse
kubectl -n marketpulse get ingress marketpulse -o yaml
```

TLS checks:

```sh
kubectl get clusterissuer letsencrypt-production
kubectl -n marketpulse get certificate marketpulse-tls
kubectl -n marketpulse describe certificate marketpulse-tls
kubectl -n marketpulse get secret marketpulse-tls
```

Expected:

- `ClusterIssuer/letsencrypt-production` is Ready.
- `Certificate/marketpulse-tls` is Ready.
- `Secret/marketpulse-tls` exists.
- Ingress has TLS for `marketpulse.byhoon.co.kr`.
- Traefik annotations include `websecure` and TLS router behavior.

HTTPS debugging:

```sh
curl -vk https://marketpulse.byhoon.co.kr/
```

Interpretation:

- TLS handshake fails: check cert-manager, TLS Secret, DNS, and port 443.
- TLS succeeds but returns 404: check Traefik router entrypoints and host/path match.
- HTTP works but HTTPS 404: likely `websecure` router configuration is missing.

## Argo CD

Check application state:

```sh
kubectl -n argocd get application marketpulse
kubectl -n argocd get application marketpulse -o yaml
argocd app get marketpulse
```

Sync and wait:

```sh
argocd app sync marketpulse
argocd app wait marketpulse --health --sync --timeout 300
```

Diff:

```sh
argocd app diff marketpulse
```

Important distinction:

- `Synced` means Kubernetes resources match Git-rendered desired state.
- `Healthy` means Argo CD health checks are passing.
- Neither guarantees every public HTTP endpoint behaves correctly; still run curl checks.

## GitHub Actions

List recent runs:

```sh
gh run list --workflow CI --limit 5
gh run list --workflow Images --limit 5
gh run list --workflow Deploy --limit 5
```

Inspect failed logs:

```sh
gh run view <run-id> --log-failed
```

Rerun transient failures:

```sh
gh run rerun <run-id> --failed
```

Common transient failure:

```text
Error response from daemon: Get "https://registry-1.docker.io/v2/": context deadline exceeded
```

That usually indicates a runner or Docker Hub network timeout during Buildx setup. If no code changed and the failure is clearly transient, rerun failed jobs.

Deploy skip behavior:

- The Deploy workflow only updates GitOps image tags after Images succeeds.
- If Images fails, Deploy is skipped by design.
- This prevents Argo CD from deploying image tags that were not successfully built.

## Logs

Backend:

```sh
kubectl -n marketpulse logs deployment/backend
kubectl -n marketpulse logs deployment/backend --tail=100
```

Frontend nginx:

```sh
kubectl -n marketpulse logs deployment/frontend
```

Traefik:

```sh
kubectl -n kube-system logs -l app.kubernetes.io/name=traefik --tail=100
```

Prometheus:

```sh
kubectl -n marketpulse logs deployment/prometheus --tail=100
```

Grafana:

```sh
kubectl -n marketpulse logs deployment/grafana --tail=100
```

## Common Incidents

### Dashboard Does Not Load

Check:

```sh
curl -I https://marketpulse.byhoon.co.kr/
dig +short marketpulse.byhoon.co.kr
kubectl -n marketpulse describe ingress marketpulse
kubectl -n marketpulse rollout status deployment/frontend
kubectl -n marketpulse logs deployment/frontend
```

Likely causes:

- DNS points to the wrong IP.
- Ingress host/path does not match.
- frontend pod is not ready.
- TLS router is missing for HTTPS.

### API Returns 502

Check:

```sh
curl -i "https://marketpulse.byhoon.co.kr/api/candles?symbol=BTCUSDT&interval=1m&limit=5"
kubectl -n marketpulse logs deployment/backend
```

Likely causes:

- Binance request failed.
- Provider rate limit or temporary external failure.
- Backend cannot normalize provider response.

### API Returns 503

Check:

```sh
kubectl -n marketpulse port-forward service/backend 8000:8000
curl -i "http://localhost:8000/ready"
kubectl -n marketpulse rollout status statefulset/postgres
kubectl -n marketpulse exec statefulset/postgres -- pg_isready -U marketpulse -d marketpulse
```

Likely causes:

- PostgreSQL is unavailable.
- `DATABASE_URL` is missing or wrong.
- Secret configuration is wrong.

### Live Price Updates But Chart Does Not

Likely cause:

- ticker polling is working but candle refresh is stale.

Check:

```sh
curl -i "https://marketpulse.byhoon.co.kr/api/ticker?symbol=BTCUSDT"
curl -i "https://marketpulse.byhoon.co.kr/api/candles?symbol=BTCUSDT&interval=1m&limit=5"
```

Frontend behavior to verify:

- ticker polling interval
- candle polling interval
- candle chart receives updated data
- chart does not clear on background refresh failure

### Argo CD Reverts Manual Fixes

Cause:

- self-heal is enabled.
- cluster state drifted from Git desired state.

Correct fix:

1. Change Helm values or templates in Git.
2. Merge to `main`.
3. Let Argo CD sync.

## Rollback Runbook

Rollback app image tags through Git:

```sh
git log --oneline infra/helm/marketpulse/values.yaml
git revert <bad-image-tag-commit>
git push origin main
```

Wait:

```sh
argocd app wait marketpulse --health --sync --timeout 300
kubectl -n marketpulse rollout status deployment/backend
kubectl -n marketpulse rollout status deployment/frontend
```

Emergency cluster rollback:

```sh
helm history marketpulse -n marketpulse
helm rollback marketpulse <revision> -n marketpulse
```

After emergency rollback, reconcile Git immediately.

## Interview Notes

Important operational points to explain:

- A green CI run does not prove the public route works.
- Argo CD `Synced` does not prove the application endpoint returns 200.
- HTTPS 404 can be an ingress router problem even when the certificate is valid.
- Deploy skip can be correct behavior if image build failed.
- Manual Kubernetes fixes do not persist under Argo CD self-heal.
- PostgreSQL in-cluster is acceptable for this compact portfolio but not the default production recommendation for high availability.
