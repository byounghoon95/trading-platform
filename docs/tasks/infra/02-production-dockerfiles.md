# infra TASK-02: Add Production Dockerfiles

## Status

done

## Goal

Add production-oriented Dockerfiles for frontend and backend.

## Scope

- Add frontend Dockerfile
- Add backend Dockerfile
- Use multi-stage builds where appropriate
- Document image build commands

## Out of Scope

- Do not add Kubernetes manifests.
- Do not add GitHub Actions yet.

## Acceptance Criteria

- Frontend image builds.
- Backend image builds.
- Build commands are documented.

## Verification

- `docker build`

## Build Commands

Run from the repository root:

```sh
docker build -t marketpulse-frontend:local apps/frontend
docker build -t marketpulse-backend:local apps/backend
```

## Completion Notes

- Status: done
- Skills used: implement-task
- Changed: added production Dockerfiles for frontend and backend, Docker build ignores, frontend NGINX config, and documented image build commands.
- Verification: `docker build -t marketpulse-frontend:local apps/frontend` -> built successfully; `docker build -t marketpulse-backend:local apps/backend` -> built successfully; `docker run --rm marketpulse-frontend:local nginx -t` -> NGINX config syntax ok; `docker run --rm marketpulse-backend:local python -c "from app.main import app; print(app.title)"` -> printed `MarketPulse API`; `curl -fsS http://localhost:18000/health` against the backend container -> returned `{"status":"ok"}`; `curl -fsSI http://localhost:18080/` against the frontend container -> returned HTTP 200.
- Notes: frontend serves the Vite production build with unprivileged NGINX on port 8080; backend runs FastAPI through Uvicorn on port 8000 as an unprivileged user.
