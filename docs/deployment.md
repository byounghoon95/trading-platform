# Deployment

MarketPulse deploys to k3s with the Helm chart in `infra/helm/marketpulse`.

## Image Build Workflow

The `Images` GitHub Actions workflow builds app images on pull requests, then builds and pushes app images to Docker Hub when `main` is updated or when the workflow is run manually.

Images:

- `leebyonghoon/marketpulse-backend`
- `leebyonghoon/marketpulse-frontend`

Tags:

- `sha-<git-sha>` for immutable GitOps deploys
- `latest` is pushed for compatibility, but Helm rollout should use immutable `sha-<git-sha>` tags.

Required repository settings:

- `DOCKERHUB_USERNAME`: Docker Hub username with push access to the `leebyonghoon` namespace.
- `DOCKERHUB_TOKEN`: Docker Hub access token with permission to push images.

No production Kubernetes secrets are required for the image build workflow.

## GitOps Deploy Handoff

The `Deploy` GitHub Actions workflow does not connect to the k3s cluster. It updates the backend and frontend image tags in `infra/helm/marketpulse/values.yaml` and commits that GitOps desired state directly to `main`. Argo CD then deploys the chart from `main`.

Triggers:

- After the `Images` workflow succeeds on `main`
- Manual `workflow_dispatch` with an optional `image_tag`

The image tag must match `sha-<git-sha>`. If no manual tag is provided, the workflow uses the source commit from the completed `Images` workflow or the dispatch commit.

Required GitHub repository settings:

- `Actions > General > Workflow permissions`: allow GitHub Actions to write repository contents.
- Branch protection for `main` must allow the GitHub Actions token to push the image tag commit, or this workflow must be allowed to bypass the required pull request rule.
- `DOCKERHUB_USERNAME`: used by the `Images` workflow, not by the deploy handoff.
- `DOCKERHUB_TOKEN`: used by the `Images` workflow, not by the deploy handoff.

No kubeconfig, SSH key, Argo CD token, or cluster credential is stored in GitHub Actions for deployment.

## Argo CD Application

The Argo CD application manifest is `infra/argocd/marketpulse-application.yaml`. It assumes:

- Argo CD is already installed in the k3s cluster.
- The `argocd` namespace exists.
- Argo CD can read `https://github.com/byounghoon95/trading-platform.git`.
- The `marketpulse-secrets` Kubernetes Secret exists before the app becomes healthy.
- cert-manager is installed before enabling HTTPS issuer values.

Install or update the application from a machine with cluster access:

```sh
kubectl apply -f infra/argocd/marketpulse-application.yaml
argocd app get marketpulse
argocd app sync marketpulse
```

Check the GitOps diff before syncing when needed:

```sh
argocd app diff marketpulse
```

## Database Secret

The Helm chart defaults to using an existing Kubernetes Secret named `marketpulse-secrets`. Create or update it before installing the chart:

```sh
kubectl create namespace marketpulse --dry-run=client -o yaml | kubectl apply -f -

kubectl -n marketpulse create secret generic marketpulse-secrets \
  --from-literal=POSTGRES_USER=marketpulse \
  --from-literal=POSTGRES_PASSWORD='<postgres-password>' \
  --from-literal=DATABASE_URL='postgresql://marketpulse:<postgres-password>@postgres:5432/marketpulse' \
  --dry-run=client -o yaml | kubectl apply -f -
```

Do not commit real database passwords. `infra/helm/marketpulse/values.secret.example.yaml` is only an example for local/manual installs.

## Argo CD Rollout

After the deploy workflow commits updated `sha-*` tags to `values.yaml`, Argo CD sees the GitOps change on `main`. Sync the app if automated sync has not already applied it:

```sh
argocd app sync marketpulse
argocd app wait marketpulse --health --sync --timeout 300
```

Wait for rollouts:

```sh
kubectl -n marketpulse rollout status statefulset/postgres
kubectl -n marketpulse rollout status deployment/backend
kubectl -n marketpulse rollout status deployment/frontend
kubectl -n marketpulse rollout status deployment/prometheus
kubectl -n marketpulse rollout status deployment/grafana
```

Check the public endpoints:

```sh
curl -I http://marketpulse.byhoon.co.kr/
curl -i "http://marketpulse.byhoon.co.kr/api/candles?symbol=BTCUSDT&interval=1m&limit=1"
```

## HTTPS With cert-manager

The Helm chart keeps HTTP ingress enabled by default so local k3s clusters can install the release without cert-manager. Production HTTPS is enabled with chart values.

Prerequisites:

- cert-manager installed in the cluster, including the `cert-manager.io/v1` CRDs.
- The k3s ingress controller can receive public HTTP traffic on port 80 for ACME HTTP-01 challenges.
- DNS for the chosen frontend hostname points at the k3s ingress node.
- A real ACME contact email is configured with `certManager.issuer.email`.

Enable HTTPS for the frontend Ingress by updating `infra/helm/marketpulse/values.yaml` or an Argo CD-managed values override:

```yaml
ingress:
  tls:
    enabled: true
certManager:
  issuer:
    enabled: true
    email: <your-email@example.com>
```

After cert-manager issues the certificate, check the HTTPS endpoint:

```sh
kubectl -n marketpulse describe certificate marketpulse-tls
curl -I https://marketpulse.byhoon.co.kr/
curl -i "https://marketpulse.byhoon.co.kr/api/candles?symbol=BTCUSDT&interval=1m&limit=1"
```

## Rollback
For a GitOps rollback, revert the commit that changed the image tags, then let Argo CD sync the previous desired state:

```sh
git revert <deployment-handoff-commit>
```

Then check sync and rollout:

```sh
argocd app sync marketpulse
argocd app wait marketpulse --health --sync --timeout 300
kubectl -n marketpulse rollout status deployment/backend
kubectl -n marketpulse rollout status deployment/frontend
```

If a cluster operator needs an emergency Helm rollback, run it from a trusted machine with cluster access and then reconcile Git so Argo CD does not reapply the bad desired state:

```sh
helm history marketpulse -n marketpulse
helm rollback marketpulse <revision> -n marketpulse
```
