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
