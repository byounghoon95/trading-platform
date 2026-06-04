# infra TASK-06: Add Metrics And Prometheus Scrape Config

## Status

done

## Goal

Expose backend operational metrics and provide Prometheus scrape configuration for k3s.

## Scope

- Add backend metrics endpoint such as `GET /metrics`
- Track basic request count, request latency, health/readiness status, and external API failures
- Add Kubernetes scrape annotations or ServiceMonitor manifests depending on the chosen Prometheus setup
- Document how to validate metrics locally and in k3s

## Files Expected To Change

- `apps/backend/app/observability/metrics.py`
- `apps/backend/app/main.py`
- `apps/backend/tests/test_metrics.py`
- `infra/k8s/backend.yaml`
- `infra/k8s/monitoring.yaml`
- `docs/operations.md`

## Out of Scope

- Do not add Grafana dashboards in this task.
- Do not add Loki log aggregation.
- Do not add business metrics unrelated to operating the service.

## Acceptance Criteria

- Backend exposes metrics in a Prometheus-compatible format.
- Metrics include enough signals to debug API health and Binance failures.
- k3s manifests or docs explain how Prometheus discovers the backend.
- Tests or manual checks verify the metrics endpoint responds.

## Verification

- `pytest`
- `curl http://localhost:<backend-port>/metrics`
- `kubectl apply --dry-run=client -f infra/k8s`

## Completion Notes

- Status: done
- Skills used: implement-task
- Changed: added backend Prometheus text metrics, request/latency/external failure instrumentation, `/metrics` endpoint, backend scrape annotations, operations notes, and focused metrics tests.
- Verification: `uv run --extra dev pytest` -> 22 passed; `uv run --extra dev ruff check .` -> all checks passed; `curl http://127.0.0.1:8001/metrics` -> returned Prometheus text including health and request metrics; `kubectl apply --dry-run=client -f infra/k8s` -> all manifests configured in client dry-run.
- Notes: used annotation-based Prometheus discovery so the MVP manifests do not require Prometheus Operator CRDs; Grafana dashboards remain out of scope for infra TASK-07.
