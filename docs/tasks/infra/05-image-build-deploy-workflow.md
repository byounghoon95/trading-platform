# infra TASK-05: Add Image Build And Deploy Workflow

## Status

todo

## Goal

Add GitHub Actions workflow for building container images, pushing them to GitHub Container Registry, and documenting the k3s deployment handoff.

## Scope

- Build frontend and backend images
- Push to GitHub Container Registry
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

## Skills

- Required: implement-task
- Optional: none

## Completion Notes

- Status: todo
- Skills used: none
- Verification: not run
- Notes: not started
