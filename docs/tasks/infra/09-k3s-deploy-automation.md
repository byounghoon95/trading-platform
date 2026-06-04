# infra TASK-09: Add k3s Deploy Automation

## Status

todo

## Goal

Automate or clearly formalize deployment from GitHub Actions to the k3s cluster.

## Scope

- Choose SSH-based deployment or GitOps handoff
- Document required GitHub secrets
- Deploy versioned Docker Hub images to k3s through Helm
- Add rollout and rollback commands
- Keep the workflow understandable for portfolio review

## Files Expected To Change

- `.github/workflows/deploy.yml`
- `infra/helm/marketpulse/values.yaml`
- `docs/deployment.md`
- `README.md`

## Out of Scope

- Do not require a cloud-managed Kubernetes service.
- Do not store kubeconfig, SSH keys, or tokens in the repository.
- Do not add Argo CD unless GitOps is selected for this task.

## Acceptance Criteria

- GitHub Actions can deploy or update the Helm release for k3s.
- Required secrets and cluster assumptions are documented.
- Rollback steps are documented.
- Workflow does not expose credentials in logs.

## Verification

- Review GitHub Actions workflow syntax
- `helm template marketpulse infra/helm/marketpulse --namespace marketpulse`
- `kubectl rollout status deployment/<name> -n <namespace>` after deployment when a cluster is available
