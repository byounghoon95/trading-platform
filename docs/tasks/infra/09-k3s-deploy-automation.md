# infra TASK-09: Add Argo CD Deploy Automation

## Status

done

## Goal

Formalize a GitOps deployment path where GitHub Actions publishes versioned images and Argo CD deploys the Helm release to k3s.

## Scope

- Use Argo CD as the deployment controller for k3s.
- Add or document an Argo CD `Application` that tracks the MarketPulse Helm chart.
- Update the GitHub Actions deployment handoff so it changes GitOps-managed Helm image tags instead of SSHing into the cluster.
- Deploy versioned Docker Hub images by setting immutable `sha-*` tags in Helm values.
- Document required GitHub permissions, optional secrets, Argo CD assumptions, sync checks, and rollback commands.
- Keep the workflow understandable for portfolio review

## Files Expected To Change

- `.github/workflows/deploy.yml`
- `infra/argocd/marketpulse-application.yaml`
- `infra/helm/marketpulse/values.yaml`
- `docs/deployment.md`
- `README.md`

## Out of Scope

- Do not require a cloud-managed Kubernetes service.
- Do not store kubeconfig, SSH keys, or tokens in the repository.
- Do not make GitHub Actions connect directly to the k3s cluster over SSH.
- Do not make GitHub Actions run `kubectl` or `helm` against the production cluster.
- Do not automate Argo CD installation itself; document it as a cluster prerequisite.

## Acceptance Criteria

- GitHub Actions can hand off a versioned release by updating GitOps-managed Helm image tags.
- Argo CD can sync the MarketPulse Helm chart into the `marketpulse` namespace.
- Required GitHub permissions or secrets and Argo CD/k3s assumptions are documented.
- Rollout, sync-status, and rollback steps are documented.
- The workflow does not expose credentials in logs and does not require cluster credentials in GitHub Actions.

## Verification

- Review GitHub Actions workflow syntax
- `helm template marketpulse infra/helm/marketpulse --namespace marketpulse`
- Validate the Argo CD `Application` manifest with `kubectl apply --dry-run=client`
- `argocd app diff marketpulse` or `argocd app get marketpulse` when Argo CD is available
- `kubectl rollout status deployment/<name> -n <namespace>` after Argo CD sync when a cluster is available

## Completion Notes

- Status: done
- Skills used: implement-task
- Changed: added a GitHub Actions deploy handoff workflow that updates Helm image tags in a pull request; added the Argo CD `Application` manifest; documented GitHub permissions, Argo CD assumptions, sync checks, rollout checks, and rollback; updated README and task index.
- Verification: `/tmp/infra09-tools/actionlint .github/workflows/deploy.yml` -> passed; `/tmp/infra09-tools/helm lint infra/helm/marketpulse` -> passed; `/tmp/infra09-tools/helm template marketpulse infra/helm/marketpulse --namespace marketpulse` -> rendered 19 objects; `kubectl apply --dry-run=client --validate=false -f infra/argocd/marketpulse-application.yaml` -> failed because the local cluster context does not have the Argo CD `Application` CRD installed; `python3` YAML parse for deploy workflow, Argo CD manifest, and Helm values -> passed; `git diff --check` -> passed.
- Notes: GitHub Actions does not store cluster credentials and does not run `kubectl`, `helm`, or SSH against production k3s. The workflow creates a GitOps PR; Argo CD applies the release after the PR is merged to `main`.

## Completion Notes

- Status: done
- Skills used: brainstorming, writing-plans
- Changed: revised the deploy handoff workflow to commit Helm image tag updates directly to `main` after a successful image build; updated deployment docs and README to describe the automatic GitOps commit flow.
- Verification: `docker run --rm -v "$PWD:/repo" -w /repo rhysd/actionlint:1.7.3 .github/workflows/deploy.yml` -> passed; `python3` YAML parse for deploy workflow and Helm values -> passed; `git diff --check` -> passed.
- Notes: GitHub Actions still does not store cluster credentials and does not run `kubectl`, `helm`, or SSH against production k3s. Branch protection must allow the GitHub Actions token to push the generated image tag commit to `main`.
