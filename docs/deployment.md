# Deployment

MarketPulse deploys to k3s with Helm and Argo CD. GitHub Actions builds immutable Docker images and updates GitOps-managed Helm values; Argo CD applies the desired state to the cluster.

## Deployment Model

```text
Developer merges code to main
  -> CI validates backend and frontend
  -> Images workflow builds Docker images
  -> Images workflow pushes sha-* tags to Docker Hub
  -> Deploy workflow updates Helm values image tags
  -> Deploy workflow commits GitOps desired state to main
  -> Argo CD detects main change
  -> Argo CD syncs infra/helm/marketpulse
  -> k3s rolls out frontend/backend workloads
```

Key rule:

> GitHub Actions does not connect to the k3s cluster. Argo CD owns cluster sync.

This avoids storing kubeconfig, SSH keys, or Argo CD tokens in GitHub Actions.

## Deployment Files

| File | Purpose |
| --- | --- |
| `.github/workflows/ci.yml` | Backend/frontend validation |
| `.github/workflows/images.yml` | Docker image build and push |
| `.github/workflows/deploy.yml` | GitOps image tag update |
| `infra/argocd/marketpulse-application.yaml` | Argo CD Application |
| `infra/helm/marketpulse/Chart.yaml` | Helm chart metadata |
| `infra/helm/marketpulse/values.yaml` | GitOps-managed deployment values |
| `infra/helm/marketpulse/templates/` | Kubernetes resource templates |

## Image Build Workflow

The `Images` workflow runs on:

- Pull requests
- Pushes to `main`
- Manual `workflow_dispatch`

On pull requests:

- Images are built for validation.
- Images are not pushed.

On `main`:

- Backend and frontend images are built.
- Images are pushed to Docker Hub.
- Immutable `sha-*` tags are produced.
- `latest` is also pushed for compatibility, but Helm deploys `sha-*`.

Images:

- `leebyonghoon/marketpulse-backend`
- `leebyonghoon/marketpulse-frontend`

Required GitHub Secrets:

- `DOCKERHUB_USERNAME`
- `DOCKERHUB_TOKEN`

The workflow uses a matrix so backend and frontend images build as separate jobs.

## GitOps Deploy Workflow

The `Deploy` workflow runs on:

- Successful `Images` workflow completion on `main`
- Manual `workflow_dispatch`

The deploy workflow:

1. Resolves the image tag.
2. Validates that it matches `sha-<git-sha>`.
3. Updates `.backend.image.tag` and `.frontend.image.tag` in `infra/helm/marketpulse/values.yaml`.
4. Commits the changed values file to `main`.

The deploy workflow does not run:

- `kubectl`
- `helm upgrade`
- SSH

Required repository setting:

- `Actions > General > Workflow permissions`: allow GitHub Actions to write repository contents.

Branch protection note:

- If `main` has branch protection that blocks direct pushes, the GitHub Actions token must be allowed to push the generated image tag commit, or the deploy workflow must return to a PR-based handoff model.

## Argo CD Application

Application manifest:

```sh
infra/argocd/marketpulse-application.yaml
```

Important fields:

- `repoURL`: GitHub repository
- `targetRevision`: `main`
- `path`: `infra/helm/marketpulse`
- `releaseName`: `marketpulse`
- destination namespace: `marketpulse`
- automated sync enabled
- prune enabled
- self-heal enabled

Install or update the Application from a trusted machine with cluster access:

```sh
kubectl apply -f infra/argocd/marketpulse-application.yaml
kubectl -n argocd get application marketpulse
```

Check through the Argo CD CLI:

```sh
argocd app get marketpulse
argocd app diff marketpulse
argocd app sync marketpulse
argocd app wait marketpulse --health --sync --timeout 300
```

## Cluster Prerequisites

Required:

- k3s cluster
- Traefik Ingress controller
- Argo CD installed in the `argocd` namespace
- Argo CD access to this GitHub repository
- Docker Hub images available under `leebyonghoon`
- DNS records pointing public hostnames at the k3s ingress node
- Kubernetes Secret `marketpulse-secrets`
- cert-manager installed for HTTPS
- `ClusterIssuer/letsencrypt-production` for current production TLS values

Optional but included in the Helm chart:

- Prometheus
- Grafana

## DNS

Current public hosts:

```text
marketpulse.byhoon.co.kr.             A 144.91.100.165
prometheus.marketpulse.byhoon.co.kr.  A 144.91.100.165
grafana.marketpulse.byhoon.co.kr.     A 144.91.100.165
```

Validate DNS:

```sh
dig +short marketpulse.byhoon.co.kr
dig +short prometheus.marketpulse.byhoon.co.kr
dig +short grafana.marketpulse.byhoon.co.kr
```

## Runtime Secrets

The Helm chart defaults to using an existing Kubernetes Secret named `marketpulse-secrets`.

Create or update it before installing the release:

```sh
kubectl create namespace marketpulse --dry-run=client -o yaml | kubectl apply -f -

kubectl -n marketpulse create secret generic marketpulse-secrets \
  --from-literal=POSTGRES_USER=marketpulse \
  --from-literal=POSTGRES_PASSWORD='<postgres-password>' \
  --from-literal=DATABASE_URL='postgresql://marketpulse:<postgres-password>@postgres:5432/marketpulse' \
  --dry-run=client -o yaml | kubectl apply -f -
```

Do not commit real database passwords. `infra/helm/marketpulse/values.secret.example.yaml` is only an example for local/manual installs.

## Helm Chart

Render locally:

```sh
helm lint infra/helm/marketpulse
helm template marketpulse infra/helm/marketpulse --namespace marketpulse
```

Manual install or upgrade, when not using Argo CD:

```sh
helm upgrade --install marketpulse infra/helm/marketpulse \
  --namespace marketpulse \
  --create-namespace
```

In normal production flow, prefer Argo CD sync instead of manual Helm upgrades so Git remains the source of truth.

## HTTPS With cert-manager

The production values enable TLS for the main dashboard Ingress:

```yaml
ingress:
  tls:
    enabled: true
    secretName: marketpulse-tls
    hosts:
      - marketpulse.byhoon.co.kr
```

The chart renders Traefik HTTPS routing annotations when TLS is enabled:

```yaml
traefik.ingress.kubernetes.io/router.entrypoints: web,websecure
traefik.ingress.kubernetes.io/router.tls: "true"
```

cert-manager state to verify:

```sh
kubectl get clusterissuer letsencrypt-production
kubectl -n marketpulse get certificate marketpulse-tls
kubectl -n marketpulse get secret marketpulse-tls
```

Expected:

- `ClusterIssuer/letsencrypt-production` is `Ready=True`.
- `Certificate/marketpulse-tls` is `Ready=True`.
- `Secret/marketpulse-tls` exists and has type `kubernetes.io/tls`.

Check public HTTPS:

```sh
curl -I https://marketpulse.byhoon.co.kr/
curl -i "https://marketpulse.byhoon.co.kr/api/candles?symbol=BTCUSDT&interval=1m&limit=1"
```

## Rollout Checks

After Argo CD sync:

```sh
kubectl -n marketpulse rollout status statefulset/postgres
kubectl -n marketpulse rollout status deployment/backend
kubectl -n marketpulse rollout status deployment/frontend
kubectl -n marketpulse rollout status deployment/prometheus
kubectl -n marketpulse rollout status deployment/grafana
```

Inspect pods:

```sh
kubectl -n marketpulse get pods -o wide
kubectl -n marketpulse describe pod <pod-name>
```

Check services and endpoints:

```sh
kubectl -n marketpulse get svc
kubectl -n marketpulse get endpoints
```

Check ingress:

```sh
kubectl -n marketpulse get ingress
kubectl -n marketpulse describe ingress marketpulse
```

## Public Endpoint Checks

Dashboard:

```sh
curl -I https://marketpulse.byhoon.co.kr/
```

Backend through ingress:

```sh
curl -i "https://marketpulse.byhoon.co.kr/api/markets"
curl -i "https://marketpulse.byhoon.co.kr/api/ticker?symbol=BTCUSDT"
curl -i "https://marketpulse.byhoon.co.kr/api/candles?symbol=BTCUSDT&interval=1m&limit=5"
```

Prometheus and Grafana:

```sh
curl -I http://prometheus.marketpulse.byhoon.co.kr/
curl -I http://grafana.marketpulse.byhoon.co.kr/
```

## Rollback

GitOps rollback:

```sh
git revert <image-tag-update-commit>
git push origin main
```

Then wait for Argo CD:

```sh
argocd app wait marketpulse --health --sync --timeout 300
kubectl -n marketpulse rollout status deployment/backend
kubectl -n marketpulse rollout status deployment/frontend
```

Emergency Helm rollback from a trusted cluster machine:

```sh
helm history marketpulse -n marketpulse
helm rollback marketpulse <revision> -n marketpulse
```

After any emergency cluster-side rollback, reconcile Git so Argo CD does not reapply the bad desired state.

## Troubleshooting Deployment

### Deploy Workflow Was Skipped

Most likely cause:

- `Images` workflow did not complete successfully.

Check:

```sh
gh run list --workflow Images --limit 5
gh run view <run-id> --log-failed
gh run list --workflow Deploy --limit 5
```

If the failed image job was a transient Docker Hub or runner network issue, rerun failed jobs:

```sh
gh run rerun <run-id> --failed
```

### Argo CD Is Synced But App Is Broken

Synced only means cluster resources match Git. It does not guarantee the application is healthy at the HTTP level.

Check:

```sh
kubectl -n marketpulse get pods
kubectl -n marketpulse logs deployment/backend
kubectl -n marketpulse logs deployment/frontend
kubectl -n marketpulse describe ingress marketpulse
curl -i https://marketpulse.byhoon.co.kr/
```

### Manual kubectl Patch Disappeared

Cause:

- Argo CD self-heal restored Git desired state.

Fix:

- Change the Helm chart or values in Git.
- Let Argo CD sync.

### HTTPS 404

If this happens:

```text
https://marketpulse.byhoon.co.kr/ -> 404 page not found
http://marketpulse.byhoon.co.kr/  -> 200 OK
```

Likely cause:

- Traefik HTTPS router is not attached to `websecure`.

Check:

```sh
kubectl -n marketpulse get ingress marketpulse -o yaml
kubectl -n marketpulse get certificate marketpulse-tls
kubectl -n marketpulse get secret marketpulse-tls
```

Fix:

- Ensure GitOps-rendered Ingress includes TLS and Traefik HTTPS annotations.
