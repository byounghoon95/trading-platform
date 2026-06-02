# Kubernetes Manifests

This directory contains the baseline k3s manifests for MarketPulse.

## Resources

- `marketpulse` namespace
- Frontend Deployment, Service, and basic HTTP Ingress
- Backend Deployment and Service
- Redis Deployment and Service
- Shared ConfigMap and placeholder Secret

## Images

The app manifests use the local tags documented by `infra TASK-02`:

```sh
docker build -t marketpulse-frontend:local apps/frontend
docker build -t marketpulse-backend:local apps/backend
```

Import or build those images into the k3s node before applying the manifests.

## Validate

```sh
kubectl apply --dry-run=client -f infra/k8s
```

## Deploy

```sh
kubectl apply -f infra/k8s
```

The frontend Ingress uses `marketpulse.local` over HTTP. HTTPS and cert-manager are intentionally left for a later task.

