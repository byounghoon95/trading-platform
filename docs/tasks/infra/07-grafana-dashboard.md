# infra TASK-07: Add Prometheus And Grafana Runtime

## Status

done

## Goal

Deploy a compact Prometheus and Grafana runtime for k3s and provision a dashboard for the main operational signals.

## Scope

- Add Prometheus Kubernetes manifests that scrape backend metrics from `infra TASK-06`
- Add Grafana Kubernetes manifests with a provisioned Prometheus data source
- Create dashboard JSON and provision it into Grafana
- Cover request rate, request latency, error rate, external API failures, and backend availability
- Include import or setup instructions
- Link the dashboard from portfolio documentation

## Files Expected To Change

- `infra/k8s/06-monitoring.yaml`
- `infra/monitoring/grafana/marketpulse-dashboard.json`
- `docs/operations.md`
- `README.md`

## Out of Scope

- Do not require a managed Grafana service.
- Do not add Loki log dashboards in this task.
- Do not create alerting rules unless the metrics task already supports them cleanly.
- Do not add Prometheus Operator or Helm charts in this task.
- Do not expose Grafana publicly through Ingress before HTTPS is added.

## Acceptance Criteria

- Prometheus and Grafana manifests can be applied to k3s.
- Prometheus is configured to scrape backend metrics from `infra TASK-06`.
- Grafana is configured with a Prometheus data source.
- Dashboard artifact exists and is provisioned into Grafana.
- Dashboard maps directly to metrics exposed by `infra TASK-06`.
- README or docs explain how to import or recreate the dashboard.

## Verification

- `kubectl apply --dry-run=client -f infra/k8s`
- Manual dashboard JSON review
- Manual documentation review

## Completion Notes

- Status: done
- Skills used: writing-plans, implement-task
- Changed: expanded TASK-07 to include Prometheus/Grafana runtime deployment, added monitoring manifests, added a provisioned Grafana dashboard artifact, and documented deploy/access validation commands.
- Verification: `jq empty infra/monitoring/grafana/marketpulse-dashboard.json` -> valid JSON; `kubectl apply --dry-run=client -f infra/k8s` -> all manifests configured in client dry-run; `kubectl apply --dry-run=server -f infra/k8s` -> all manifests accepted by the connected k3s API; manual docs review -> operations and README monitoring sections added.
- Notes: kept Grafana and Prometheus internal-only with port-forward access; public Ingress remains out of scope until HTTPS is added.
