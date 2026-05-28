# infra TASK-06: Add Metrics And Prometheus Scrape Config

## Status

todo

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

## Skills

- Required: implement-task
- Optional: none

## Completion Notes

- Status: todo
- Skills used: none
- Verification: not run
- Notes: not started
