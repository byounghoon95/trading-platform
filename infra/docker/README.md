# Docker Compose

This directory contains the local Docker Compose baseline for MarketPulse.

## Run locally

Validate the Compose file:

```sh
docker compose -f infra/docker/compose.yaml config
```

Start the services:

```sh
docker compose -f infra/docker/compose.yaml up
```

The `postgres` service uses the stable service name `postgres`, stores data in the `postgres-data` volume, and exposes `DATABASE_URL=postgresql://marketpulse:marketpulse@postgres:5432/marketpulse` to the backend.

The `redis` service is functional and uses the stable service name `redis`.

The `frontend` and `backend` services are placeholders that keep their containers running with public base images. They expose the expected local ports, and the backend depends on healthy PostgreSQL and Redis containers so later persistence and cache behavior can start against stable local service names.

## Troubleshooting

Check PostgreSQL health:

```sh
docker compose -f infra/docker/compose.yaml ps postgres
docker compose -f infra/docker/compose.yaml exec postgres pg_isready -U marketpulse -d marketpulse
```

Reset local database state:

```sh
docker compose -f infra/docker/compose.yaml down --volumes
```
