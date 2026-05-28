# Infra Agent Guide

Track-local rules for `infra/` (Docker, Kubernetes, CI/CD). Root rules (behavioral guidelines, worktree, skill usage, scope) live in the repo-root `AGENTS.md`.

## Stack

- Local runtime: Docker Compose
- Deployment target: k3s
- CI/CD: GitHub Actions
- Image registry: GitHub Container Registry

## Coding Standards

- Keep manifests minimal and production-shaped — no speculative components.
- Document environment variables, local run commands, and deployment commands when they change.
- Pin image tags; avoid `latest` in deployment manifests.
- Keep Compose and Kubernetes manifests consistent in service names, ports, and env var names where it reduces friction.

## Verification

Run the checks relevant to what changed:

- Docker image build for any changed `Dockerfile`
- `docker compose config` and a Compose smoke test for changes under `infra/docker/`
- Kubernetes manifest validation (`kubectl apply --dry-run=client -f ...` or `kubeconform`) for changes under `infra/k8s/`
- GitHub Actions workflow lint (e.g. `actionlint`) for changes under `.github/workflows/`

Record the command output in the task's `Completion Notes`. If a check cannot run, state why in the final response.
