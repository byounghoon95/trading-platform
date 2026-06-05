# infra TASK-09: Add k3s Deploy Automation

## Status

done

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

## Completion Notes

- Status: done
- Skills used: implement-task
- Changed: added an SSH-based GitHub Actions deploy workflow, documented k3s deploy secrets and rollback steps, noted immutable image-tag override behavior in Helm values, and updated the README deployment summary.
- Verification: `python3` YAML parse for `.github/workflows/deploy.yml`, `.github/workflows/images.yml`, and `.github/workflows/ci.yml` -> parsed; `docker run --rm -v "$PWD":/repo -w /repo rhysd/actionlint:1.7.7 -color=false .github/workflows/ci.yml .github/workflows/images.yml .github/workflows/deploy.yml` -> passed; `docker run --rm -v "$PWD":/work -w /work alpine/helm:3.17.3 lint infra/helm/marketpulse` -> 1 chart linted, 0 failed; `docker run --rm -v "$PWD":/work -w /work alpine/helm:3.17.3 template marketpulse infra/helm/marketpulse --namespace marketpulse` -> rendered successfully; rendered manifests piped to `kubectl apply --dry-run=client -f -` -> configured dry run; `kubectl rollout status deployment/backend -n marketpulse`, `kubectl rollout status deployment/frontend -n marketpulse`, and `kubectl rollout status statefulset/postgres -n marketpulse` -> current local k3s workloads rolled out.
- Notes: The deploy workflow itself was not executed from GitHub Actions in this local run because it requires repository SSH secrets and a pushed workflow run on `main`.
