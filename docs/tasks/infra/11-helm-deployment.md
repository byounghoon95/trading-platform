# infra TASK-11: Replace k3s Manifests With Helm

## Status

done

## Goal

Replace the raw k3s manifest deployment path with a single Helm chart that deploys MarketPulse runtime components and keeps PostgreSQL credentials out of git.

## Scope

- Add a Helm chart under `infra/helm/marketpulse`.
- Template frontend, backend, PostgreSQL, Redis, Ingress, Prometheus, and Grafana resources.
- Move deployment configuration into `values.yaml` with image tags, hosts, ports, probes, and storage settings.
- Support database secrets through an existing Kubernetes Secret by default.
- Provide an optional Helm-managed Secret path for local/manual installs without committing real secret values.
- Replace raw `infra/k8s/*.yaml` deployment files with Helm documentation.
- Update deployment and operations docs for Helm install, upgrade, rollback, and secret handling.

## Out of Scope

- Do not add cert-manager or HTTPS in this task.
- Do not add Argo CD or a full GitOps controller in this task.
- Do not deploy to the live cluster from this task branch.
- Do not commit real database passwords, kubeconfigs, SSH keys, or tokens.

## Acceptance Criteria

- Helm is the documented k3s deployment source for the app.
- Raw k3s manifests are no longer the deployment path.
- PostgreSQL credentials are provided through Kubernetes Secret references, not committed config.
- Backend readiness still uses `/ready`, and liveness still uses `/health`.
- Existing service names remain stable: `backend`, `frontend`, `postgres`, `redis`, `prometheus`, and `grafana`.
- Helm render/lint validation passes.

## Implementation Plan

1. Create `infra/helm/marketpulse/Chart.yaml`, `values.yaml`, and helper templates.
2. Port each existing raw k8s resource into Helm templates with values for names, images, hosts, probes, storage, and enable flags.
3. Move Grafana dashboard JSON into chart files and render it through a ConfigMap template.
4. Replace the committed placeholder Secret with a Secret template that only renders when `secrets.create=true`; default to `secrets.existingSecret=marketpulse-secrets`.
5. Replace raw manifest YAML files with Helm deployment documentation.
6. Update `docs/deployment.md`, `docs/operations.md`, `docs/spec.md`, and the task index.
7. Verify with `helm lint`, `helm template`, rendered manifest dry-run, and docs/diff checks.

## Completion Notes

- Status: done
- Skills used: brainstorming, writing-plans
- Changed: replaced raw `infra/k8s` deployment YAML with `infra/helm/marketpulse`; templated frontend, backend, PostgreSQL, Redis, Ingress, Prometheus, and Grafana; packaged the Grafana dashboard in the chart; moved PostgreSQL credentials to existing Secret or optional Helm-managed Secret values; updated deployment, operations, spec, infra guide, README, and task dependencies.
- Verification: `helm lint infra/helm/marketpulse` -> passed; `helm template marketpulse infra/helm/marketpulse --namespace marketpulse` -> rendered 19 objects; Secret creation render with `secrets.create=true` -> rendered 20 objects including `Secret/marketpulse-secrets`; `kubectl apply --dry-run=client -f /tmp/marketpulse-rendered.yaml` -> passed; `docker compose -f infra/docker/compose.yaml config` -> passed; `jq empty infra/helm/marketpulse/files/grafana/marketpulse-dashboard.json` -> passed; `git diff --check` -> passed.
- Notes: real database passwords are not committed. Production rollout should create `marketpulse-secrets` before `helm upgrade --install`, or pass secret values at install time with `secrets.create=true`.
