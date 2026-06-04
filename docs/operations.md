# Operations

## Backend Metrics

The backend exposes Prometheus-compatible metrics at `GET /metrics`.

Local validation:

```bash
cd apps/backend
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
curl http://localhost:8000/metrics
```

Expected metric families include:

- `marketpulse_http_requests_total`
- `marketpulse_http_request_duration_seconds_count`
- `marketpulse_http_request_duration_seconds_sum`
- `marketpulse_health_status`
- `marketpulse_external_api_failures_total`

The Kubernetes backend Service and backend pod template include basic Prometheus scrape annotations for annotation-based discovery. This avoids requiring Prometheus Operator CRDs in the MVP k3s manifests.

## Backend PostgreSQL Persistence

Set `DATABASE_URL` to enable PostgreSQL persistence for normalized candle and ticker responses:

```bash
DATABASE_URL=postgresql://marketpulse:<password>@postgres:5432/marketpulse
```

When configured, the backend initializes the market data schema on startup, persists refreshed Binance candle/ticker responses, and serves fresh stored records before calling Binance again. If stored records exist and a refresh fails, the API falls back to the stored records.

Liveness and readiness are separate:

- `GET /health` stays independent of PostgreSQL and returns liveness.
- `GET /ready` checks PostgreSQL and returns 503 when `DATABASE_URL` is missing or the database is unreachable.

Docker Compose and k3s PostgreSQL runtime wiring are tracked by infra TASK-10.

## Prometheus And Grafana

`infra/k8s/06-monitoring.yaml` deploys a compact Prometheus and Grafana runtime in the `marketpulse` namespace.

Prometheus:

- Scrapes backend metrics from `backend.marketpulse.svc.cluster.local:8000/metrics`.
- Keeps in-pod time-series data for 7 days with `emptyDir` storage.
- Exposes the Prometheus UI through HTTP Ingress at `prometheus.marketpulse.byhoon.co.kr`.

Grafana:

- Uses the in-cluster Prometheus service as the default data source.
- Provisions the `MarketPulse Operations` dashboard from a ConfigMap.
- Exposes the Grafana UI through HTTP Ingress at `grafana.marketpulse.byhoon.co.kr`.

Deploy or update monitoring:

```bash
kubectl apply -f infra/k8s/06-monitoring.yaml
kubectl rollout status deployment/prometheus -n marketpulse
kubectl rollout status deployment/grafana -n marketpulse
```

Public monitoring access requires DNS records pointing at the k3s ingress node:

```text
prometheus.marketpulse.byhoon.co.kr. A 144.91.100.165
grafana.marketpulse.byhoon.co.kr.    A 144.91.100.165
```

Validate Prometheus targets:

```bash
kubectl port-forward -n marketpulse service/prometheus 9090:9090
curl http://localhost:9090/api/v1/targets
```

Open Grafana locally or through the public Ingress:

```bash
kubectl port-forward -n marketpulse service/grafana 3000:3000
```

Then open `http://localhost:3000` or `http://grafana.marketpulse.byhoon.co.kr` and sign in with Grafana's development default credentials:

- Username: `admin`
- Password: `admin`

Change the default password after the first public login.

The dashboard artifact also lives at `infra/monitoring/grafana/marketpulse-dashboard.json` for manual import or review.
