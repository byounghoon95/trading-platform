# Docker Compose

This directory contains the local Docker Compose baseline for MarketPulse.

## Run locally

Validate the Compose file:

```sh
docker compose -f infra/docker/compose.yaml config
```

Start the baseline services:

```sh
docker compose -f infra/docker/compose.yaml up
```

The `redis` service is functional and uses the stable service name `redis`.

The `frontend` and `backend` services are placeholders that keep their containers running with public base images. They expose the expected local ports, but they do not run the application until production Dockerfiles are added in `infra TASK-02`.
