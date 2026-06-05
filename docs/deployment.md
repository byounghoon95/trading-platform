# Deployment

MarketPulse deploys to k3s with the manifests in `infra/k8s`.

## Image Build Workflow

The `Images` GitHub Actions workflow builds app images on pull requests, then builds and pushes app images to Docker Hub when `main` is updated or when the workflow is run manually.

Images:

- `leebyonghoon/marketpulse-backend`
- `leebyonghoon/marketpulse-frontend`

Tags:

- `sha-<git-sha>` for immutable handoff deploys
- `latest` for compatibility with the current k3s manifests

Required repository settings:

- `DOCKERHUB_USERNAME`: Docker Hub username with push access to the `leebyonghoon` namespace.
- `DOCKERHUB_TOKEN`: Docker Hub access token with permission to push images.

No production secrets are required for this workflow.

## Manual k3s Rollout

After the image workflow succeeds, deploy a specific commit by setting both workload images to the matching `sha-<git-sha>` tag.

```sh
kubectl -n marketpulse set image deployment/backend \
  backend=leebyonghoon/marketpulse-backend:sha-<git-sha>

kubectl -n marketpulse set image deployment/frontend \
  frontend=leebyonghoon/marketpulse-frontend:sha-<git-sha>

kubectl -n marketpulse rollout status deployment/backend
kubectl -n marketpulse rollout status deployment/frontend
```

Check the public endpoints:

```sh
curl -I http://marketpulse.byhoon.co.kr/
curl -i "http://marketpulse.byhoon.co.kr/api/candles?symbol=BTCUSDT&interval=1m&limit=1"
```

Automated SSH deployment is intentionally deferred to infra TASK-09.

## HTTPS With cert-manager

The base k3s manifests keep HTTP ingress usable for local clusters. Production HTTPS is layered on with cert-manager manifests in `infra/k8s/https`.

Prerequisites:

- cert-manager installed in the cluster, including the `cert-manager.io/v1` CRDs.
- The k3s ingress controller can receive public HTTP traffic on port 80 for ACME HTTP-01 challenges.
- DNS for the chosen frontend hostname points at the k3s ingress node.
- A real ACME contact email is configured in `infra/k8s/https/cert-manager-issuer.yaml`.

Before applying HTTPS, replace the sample values:

- `ops@example.com` with the ACME contact email.
- `marketpulse.example.com` with the frontend DNS hostname.
- `letsencrypt-production` if the cluster already has a different cert-manager issuer name.
- `marketpulse-tls` if a different TLS Secret name is preferred.

Apply the base manifests first, then apply the HTTPS manifests:

```sh
kubectl apply -f infra/k8s
kubectl apply -f infra/k8s/https
kubectl -n marketpulse describe certificate marketpulse-tls
```

After cert-manager issues the certificate, check the HTTPS endpoint:

```sh
curl -I https://marketpulse.example.com/
curl -i "https://marketpulse.example.com/api/candles?symbol=BTCUSDT&interval=1m&limit=1"
```

Leave `infra/k8s/05-ingress.yaml` in place for local and non-HTTPS development clusters.

## PostgreSQL Runtime

The k3s manifests include a single PostgreSQL StatefulSet exposed through the in-cluster `postgres` Service. The backend reads PostgreSQL configuration from `marketpulse-config` and `marketpulse-secrets`, including `DATABASE_URL`.

Before deploying to a shared cluster, replace the placeholder PostgreSQL password values in `infra/k8s/01-config.yaml`:

```sh
kubectl apply -f infra/k8s
kubectl -n marketpulse rollout status statefulset/postgres
kubectl -n marketpulse rollout status deployment/backend
```
