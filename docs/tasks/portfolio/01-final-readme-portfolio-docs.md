# portfolio TASK-01: Final README And Portfolio Docs

## Status

done

## Goal

Create the final README and portfolio-ready documentation.

## Scope

- Add project overview
- Add architecture summary
- Add local run instructions
- Add deployment instructions
- Add advanced ops summary for metrics, Grafana, HTTPS, GHCR, and k3s deployment automation
- Add troubleshooting notes
- Link relevant docs

## Files Expected To Change

- `README.md`
- `docs/architecture.md`
- `docs/deployment.md`
- `docs/operations.md`

## Depends On

- frontend TASK-04
- backend TASK-07
- backend TASK-08
- infra TASK-06
- infra TASK-07
- infra TASK-08
- infra TASK-09
- infra TASK-10
- infra TASK-11

## Out of Scope

- Do not add new app features.

## Acceptance Criteria

- README explains what the project is and how to run it.
- README explains the k3s deployment path.
- README explains what is MVP and what is advanced ops scope.
- Documentation is concise and interview-ready.

## Verification

- Manual documentation review

## Completion Notes

- Status: done
- Skills used: implement-task
- Changed: expanded the root README into a deployment-focused portfolio guide; added `docs/assets/architecture.svg`; added `docs/architecture.md`; rewrote `docs/deployment.md` as a GitOps/k3s deployment runbook; rewrote `docs/operations.md` as a day-2 operations and troubleshooting guide; updated the task index.
- Verification: manual documentation review -> passed; `python3` repository link check for Markdown links -> passed; `rg` placeholder scan for task documentation -> passed; `git diff --check` -> passed.
- Notes: README was later tightened to remove document-link hub content, emphasize deployment and AI-assisted development, and embed `docs/assets/architecture.svg` as the current architecture diagram.
