# infra TASK-08: Add HTTPS Ingress With cert-manager

## Status

todo

## Goal

Add production-style HTTPS ingress support for the k3s deployment using cert-manager.

## Scope

- Add cert-manager issuer or cluster issuer manifest guidance
- Add TLS configuration to frontend Ingress
- Document DNS, email, and issuer prerequisites
- Keep local non-HTTPS ingress usable for development clusters

## Files Expected To Change

- `infra/k8s/ingress.yaml`
- `infra/k8s/cert-manager-issuer.yaml`
- `docs/deployment.md`

## Out of Scope

- Do not buy or require a paid domain.
- Do not hardcode personal email addresses or hostnames.
- Do not remove the basic HTTP ingress path.

## Acceptance Criteria

- HTTPS manifests or overlays exist without breaking local k3s usage.
- Required cluster prerequisites are documented.
- TLS hostnames and issuer values are configurable.

## Verification

- `kubectl apply --dry-run=client -f infra/k8s`
- Manual documentation review

## Skills

- Required: implement-task
- Optional: none

## Completion Notes

- Status: todo
- Skills used: none
- Verification: not run
- Notes: not started
