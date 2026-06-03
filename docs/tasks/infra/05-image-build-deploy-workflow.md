# infra TASK-05: Add Image Build And Deploy Workflow

## Status

done

## Goal

Add GitHub Actions workflow for building container images, pushing them to Docker Hub, and documenting the k3s deployment handoff.

## Scope

- Build frontend and backend images
- Push to Docker Hub
- Document required repository secrets
- Document a manual k3s rollout or GitOps handoff path

## Files Expected To Change

- `.github/workflows/images.yml`
- `docs/deployment.md`
- `README.md`

## Out of Scope

- Do not hardcode production secrets.
- Do not require cloud-managed Kubernetes.
- Do not automate SSH deployment yet; that belongs in `infra TASK-09`.

## Acceptance Criteria

- Workflow defines image build and push.
- Required secrets are documented.
- k3s deployment handoff is clear enough to apply manually.

## Verification

- Review workflow syntax locally if tooling is available.

## Completion Notes

- Status: done
- Skills used: implement-task
- Changed: added GitHub Actions image workflow for backend/frontend Docker Hub builds, added deployment handoff docs, added root README deployment pointers, and updated k8s image notes.
- Verification: `python3` YAML parse check for `.github/workflows/images.yml` -> passed; `docker run --rm -v "$PWD":/repo -w /repo rhysd/actionlint:latest .github/workflows/images.yml` -> passed; `docker build -t marketpulse-backend:ci-test apps/backend` -> passed; `docker build -t marketpulse-frontend:ci-test apps/frontend` -> passed.
- Notes: workflow builds images on pull requests and pushes Docker Hub `sha-*` and `latest` tags on `main` and `workflow_dispatch`; k3s rollout remains a documented manual handoff until infra TASK-09.
