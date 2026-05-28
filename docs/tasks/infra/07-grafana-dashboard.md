# infra TASK-07: Add Grafana Dashboard

## Status

todo

## Goal

Add a Grafana dashboard or dashboard documentation for the main operational signals.

## Scope

- Create dashboard JSON or documented dashboard panels
- Cover request rate, request latency, error rate, external API failures, and backend availability
- Include import or setup instructions
- Link the dashboard from portfolio documentation

## Files Expected To Change

- `infra/monitoring/grafana/marketpulse-dashboard.json`
- `docs/operations.md`
- `README.md`

## Out of Scope

- Do not require a managed Grafana service.
- Do not add Loki log dashboards in this task.
- Do not create alerting rules unless the metrics task already supports them cleanly.

## Acceptance Criteria

- Dashboard artifact or setup guide exists.
- Dashboard maps directly to metrics exposed by `infra TASK-06`.
- README or docs explain how to import or recreate the dashboard.

## Verification

- Manual dashboard JSON review
- Manual documentation review

