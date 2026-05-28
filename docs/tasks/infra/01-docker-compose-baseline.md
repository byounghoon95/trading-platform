# infra TASK-01: Add Docker Compose Baseline

## Status

todo

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

