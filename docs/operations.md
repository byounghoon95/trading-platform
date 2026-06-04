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

## Prometheus And Grafana

`infra/k8s/06-monitoring.yaml` deploys a compact Prometheus and Grafana runtime in the `marketpulse` namespace.

Prometheus:

- Scrapes backend metrics from `backend.marketpulse.svc.cluster.local:8000/metrics`.
- Keeps in-pod time-series data for 7 days with `emptyDir` storage.
- Runs inside the cluster only and is not exposed through Ingress.

Grafana:

- Uses the in-cluster Prometheus service as the default data source.
- Provisions the `MarketPulse Operations` dashboard from a ConfigMap.
- Runs inside the cluster only and is not exposed through Ingress.

Deploy or update monitoring:

```bash
kubectl apply -f infra/k8s/06-monitoring.yaml
kubectl rollout status deployment/prometheus -n marketpulse
kubectl rollout status deployment/grafana -n marketpulse
```

Validate Prometheus targets:

```bash
kubectl port-forward -n marketpulse service/prometheus 9090:9090
curl http://localhost:9090/api/v1/targets
```

Open Grafana locally:

```bash
kubectl port-forward -n marketpulse service/grafana 3000:3000
```

Then open `http://localhost:3000` and sign in with Grafana's development default credentials:

- Username: `admin`
- Password: `admin`

The dashboard artifact also lives at `infra/monitoring/grafana/marketpulse-dashboard.json` for manual import or review.
