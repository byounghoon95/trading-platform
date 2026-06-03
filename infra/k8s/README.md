# Kubernetes Manifests

This directory contains the baseline k3s manifests for MarketPulse.

## Resources

- `marketpulse` namespace
- Frontend Deployment, Service, and basic HTTP Ingress
- Backend Deployment and Service
- Redis Deployment and Service
- Shared ConfigMap and placeholder Secret

## Images

The app manifests use Docker Hub images tagged as `latest`:

```sh
docker build -t leebyonghoon/marketpulse-backend:latest apps/backend
docker build -t leebyonghoon/marketpulse-frontend:latest apps/frontend
docker push leebyonghoon/marketpulse-backend:latest
docker push leebyonghoon/marketpulse-frontend:latest
```

Push those images before applying the manifests so k3s can pull them.

## Validate

```sh
kubectl apply --dry-run=client -f infra/k8s
```

## Deploy

```sh
kubectl apply -f infra/k8s
```

The frontend Ingress uses `marketpulse.byhoon.co.kr` over HTTP. HTTPS and cert-manager are intentionally left for a later task.
