# Kubernetes Manifests

Raw k3s manifests have been replaced by the Helm chart at `infra/helm/marketpulse`.

Use Helm for rendering, validation, deployment, upgrades, and rollback:

```sh
helm lint infra/helm/marketpulse
helm template marketpulse infra/helm/marketpulse --namespace marketpulse
helm upgrade --install marketpulse infra/helm/marketpulse \
  --namespace marketpulse \
  --create-namespace
```

Production database credentials must be created as a Kubernetes Secret before installing the chart, or supplied with `secrets.create=true` at install time. Do not commit real secret values.

HTTPS ingress is configured through Helm values in `infra/helm/marketpulse`. See `docs/deployment.md` for the cert-manager prerequisites and install command.
