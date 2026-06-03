# infra TASK-03: Add k3s Manifests

## Status

done

## Goal

Add Kubernetes manifests for deploying frontend, backend, and Redis to k3s.

## Scope

- Add namespace
- Add frontend Deployment and Service
- Add backend Deployment and Service
- Add Redis Deployment and Service
- Add ConfigMap and Secret placeholders
- Add liveness and readiness probes. `/health` is acceptable until later PostgreSQL-aware and Redis-aware readiness behavior is implemented.
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

## Completion Notes

- Status: done
- Skills used: implement-task
- Changed: added baseline k3s manifests under `infra/k8s` for namespace, config, secret placeholder, frontend, backend, Redis, services, probes, and frontend Ingress; added k8s usage notes.
- Verification: `kubectl apply --dry-run=client -f infra/k8s` -> passed for all 10 Kubernetes objects; `python3` YAML parse check over `infra/k8s/*.yaml` -> parsed 10 Kubernetes objects; `git diff --check` -> passed.
- Notes: backend readiness uses `/health` until later PostgreSQL-aware and Redis-aware readiness behavior exists; app images use `leebyonghoon/marketpulse-backend:latest` and `leebyonghoon/marketpulse-frontend:latest` per deployment request.
