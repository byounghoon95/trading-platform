# infra TASK-01: Add Docker Compose Baseline

## Status

done

## Goal

Add a local Docker Compose setup for frontend, backend, and Redis.

## Scope

- Add compose file
- Add frontend service placeholder (use a public base image such as `node:20-alpine` with a command stub until `infra TASK-02` Dockerfiles land)
- Add backend service placeholder (use a public base image such as `python:3.12-slim` with a command stub until `infra TASK-02` Dockerfiles land)
- Add Redis service from the official image
- Document local startup command and the limitation that frontend/backend services only become useful after the corresponding scaffold and Dockerfile tasks

## Out of Scope

- Do not optimize production Dockerfiles.
- Do not add k3s manifests.

## Acceptance Criteria

- Docker Compose file is present.
- Redis service is defined with a stable service name.
- Local run command is documented.

## Verification

- `docker compose config`

## Completion Notes

- Status: done
- Skills used: implement-task
- Changed: added `infra/docker/compose.yaml` with frontend/backend placeholders and Redis; added local Compose usage docs
- Verification: `docker compose -f infra/docker/compose.yaml config` -> passed; `docker compose -f infra/docker/compose.yaml up -d redis` + `docker compose -f infra/docker/compose.yaml ps redis` -> Redis healthy; `docker compose -f infra/docker/compose.yaml down --volumes` -> cleanup passed
- Notes: frontend and backend containers intentionally remain command stubs until `infra TASK-02` adds production Dockerfiles

