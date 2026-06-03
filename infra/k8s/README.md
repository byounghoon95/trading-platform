# Kubernetes Manifests

This directory contains the baseline k3s manifests for MarketPulse.

## Resources

- `marketpulse` namespace
- Frontend Deployment, Service, and basic HTTP Ingress
- Backend Deployment and Service
- Redis Deployment and Service
- Shared ConfigMap and placeholder Secret

## Images

The app images are built by the GitHub Actions image workflow and pushed to Docker Hub:

```sh
leebyonghoon/marketpulse-backend:sha-<git-sha>
leebyonghoon/marketpulse-frontend:sha-<git-sha>
```

The current baseline manifests use `latest` for compatibility with the initial k3s deployment, but `docs/deployment.md` shows how to roll out an immutable `sha-<git-sha>` tag.

Use `docs/deployment.md` for the manual k3s rollout handoff.

## Validate

```sh
kubectl apply --dry-run=client -f infra/k8s
```

## Deploy

```sh
kubectl apply -f infra/k8s
```

The frontend Ingress uses `marketpulse.byhoon.co.kr` over HTTP. HTTPS and cert-manager are intentionally left for a later task.
