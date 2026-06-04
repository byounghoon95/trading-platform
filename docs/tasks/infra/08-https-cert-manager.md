# infra TASK-08: Add HTTPS Ingress With cert-manager

## Status

todo

## Goal

Add production-style HTTPS ingress support for the k3s deployment using cert-manager.

## Scope

- Add cert-manager issuer or cluster issuer guidance
- Add configurable TLS values to the Helm-rendered frontend Ingress
- Document DNS, email, and issuer prerequisites
- Keep local non-HTTPS ingress usable for development clusters

## Files Expected To Change

- `infra/helm/marketpulse/values.yaml`
- `infra/helm/marketpulse/templates/ingress.yaml`
- Optional issuer template under `infra/helm/marketpulse/templates/`
- `docs/deployment.md`

## Out of Scope

- Do not buy or require a paid domain.
- Do not hardcode personal email addresses or hostnames.
- Do not remove the basic HTTP ingress path.

## Acceptance Criteria

- HTTPS Helm values/templates exist without breaking local k3s usage.
- Required cluster prerequisites are documented.
- TLS hostnames and issuer values are configurable.

## Verification

- `helm lint infra/helm/marketpulse`
- `helm template marketpulse infra/helm/marketpulse --namespace marketpulse`
- Manual documentation review
