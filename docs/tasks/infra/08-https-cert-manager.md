# infra TASK-08: Add HTTPS Ingress With cert-manager

## Status

done

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

## Completion Notes

- Status: done
- Skills used: implement-task
- Changed: added cert-manager HTTPS manifests under `infra/k8s/https`; documented DNS, email, issuer, and TLS Secret prerequisites while keeping the base HTTP ingress for local clusters.
- Verification: `kubectl apply --dry-run=client -f infra/k8s` -> passed for the base manifests; `kubectl apply --dry-run=client -f infra/k8s/https/ingress.yaml` -> passed for the TLS frontend Ingress; `kubectl apply --dry-run=client -f infra/k8s/https/cert-manager-issuer.yaml` -> failed because the local cluster does not have cert-manager CRDs installed; `git diff --check` -> passed; manual documentation review -> passed.
- Notes: the HTTPS manifests intentionally live outside the base `infra/k8s` apply path so local/non-HTTPS clusters do not require cert-manager.
