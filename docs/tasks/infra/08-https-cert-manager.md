# infra TASK-08: Add HTTPS Ingress With cert-manager

## Status

done

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

## Completion Notes

- Status: done
- Skills used: implement-task
- Changed: added configurable cert-manager issuer and TLS support to the Helm chart; documented DNS, email, issuer, and TLS Secret prerequisites while keeping HTTP ingress as the default for local clusters.
- Verification: `docker run --rm -v "$PWD:/apps" -w /apps alpine/helm:3.15.3 lint infra/helm/marketpulse` -> passed; `docker run --rm -v "$PWD:/apps" -w /apps alpine/helm:3.15.3 template marketpulse infra/helm/marketpulse --namespace marketpulse` plus `kubectl apply --dry-run=client -f /tmp/marketpulse-base.yaml` -> passed for the default HTTP chart; TLS-enabled Helm rendering -> rendered frontend TLS and ClusterIssuer as expected; TLS-enabled dry-run with issuer disabled -> passed; TLS-enabled dry-run with issuer enabled -> failed because the local cluster does not have cert-manager CRDs installed; `git diff --check` -> passed; manual documentation review -> passed.
- Notes: HTTPS stays opt-in through Helm values so local/non-HTTPS clusters do not require cert-manager. Applying the generated `ClusterIssuer` requires cert-manager CRDs to be installed first.
