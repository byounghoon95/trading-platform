# infra TASK-03: Add k3s Manifests

## Status

todo

## Goal

Add Kubernetes manifests for deploying frontend, backend, and Redis to k3s.

## Scope

- Add namespace
- Add frontend Deployment and Service
- Add backend Deployment and Service
- Add Redis Deployment and Service
- Add ConfigMap and Secret placeholders
- Add liveness and readiness probes (readiness must point at the Redis-aware path defined by `backend TASK-05` once that task is done; until then `/health` is acceptable)
- Add basic Ingress for the frontend

## Out of Scope

- Do not add cert-manager automation yet.
- Do not add GitHub Actions deployment yet.
- Do not require public DNS or HTTPS in this task.

## Acceptance Criteria

- Manifests are present under `infra/k8s`.
- Workloads have probes.
- Config and secrets are separated from deployment specs.
- Frontend can be exposed through a basic Ingress.

## Verification

- `kubectl apply --dry-run=client -f infra/k8s`

## Skills

- Required: implement-task
- Optional: none

## Completion Notes

- Status: todo
- Skills used: none
- Verification: not run
- Notes: not started
