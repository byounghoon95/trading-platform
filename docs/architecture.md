# Architecture

MarketPulse is a compact market dashboard with a deliberately small product surface and a production-shaped infrastructure path. The architecture is designed to be easy to explain in an interview: each layer has a clear responsibility, and deployment state is traceable from Git to Kubernetes.

## Goals

The architecture optimizes for:

- A stable frontend-facing API contract.
- A backend boundary that hides Binance response shape and provider failures.
- A small but realistic Kubernetes deployment.
- GitOps-based release tracking.
- Basic operational visibility through metrics and dashboards.

The architecture does not optimize for:

- Real-money trading.
- User accounts.
- Low-latency order execution.
- High-availability database operations.
- Complex alerting.
- Multi-region deployment.

Those are outside the project scope.

## High-Level System

```text
Browser
  |
  | HTTPS
  v
Traefik Ingress
  |
  | /
  v
frontend Service
  |
  v
nginx container serving React static assets

Browser
  |
  | HTTPS /api/*
  v
Traefik Ingress
  |
  v
backend Service
  |
  v
FastAPI backend
  |
  +--> PostgreSQL
  |
  +--> Binance public API
```

Monitoring:

```text
FastAPI /metrics
  -> Prometheus
  -> Grafana dashboard
```

GitOps deployment:

```text
main branch
  -> GitHub Actions image build
  -> Docker Hub sha-* tags
  -> GitHub Actions updates Helm values
  -> Argo CD syncs Helm chart
  -> k3s workloads
```

## Frontend

Location:

- `apps/frontend`

Stack:

- React
- Vite
- JavaScript
- Lightweight Charts
- nginx production container

Responsibilities:

- Render the dashboard as the first screen.
- Let the user select symbol and candle interval.
- Render candlestick and volume chart data.
- Compute MA 5 and MA 20 from normalized candle responses.
- Poll ticker data for current price and 24h change.
- Refresh live candle data without a page reload.
- Show loading, error, empty, and stale states.

Important files:

- `apps/frontend/src/components/Dashboard.jsx`
- `apps/frontend/src/components/CandleChart.jsx`
- `apps/frontend/src/components/PricePanel.jsx`
- `apps/frontend/src/api/client.js`

The frontend intentionally does not parse Binance payloads. It consumes project-owned JSON returned by the backend. This keeps chart rendering and UI state separate from external provider details.

### Frontend Data Flow

```text
Dashboard component
  -> listMarkets()
  -> selected symbol
  -> listCandles(symbol, interval, limit)
  -> normalized candle chart data
  -> CandleChart

Dashboard component
  -> getTicker(symbol) every few seconds
  -> PricePanel
  -> stale or refresh error state when polling fails
```

The current implementation uses polling rather than WebSocket streaming. Polling is a simpler MVP choice and still demonstrates live refresh behavior. WebSocket support is documented as future work in backend TASK-08 and frontend TASK-04.

## Backend

Location:

- `apps/backend`

Stack:

- FastAPI
- Python
- Pydantic response models
- httpx-compatible external market data access
- PostgreSQL data access through `psycopg`
- Prometheus-compatible metrics

Responsibilities:

- Serve liveness and readiness checks.
- Expose supported markets.
- Validate market data inputs.
- Request Binance public market data.
- Normalize raw market data into project-owned DTOs.
- Convert DTOs into frontend-friendly API schemas.
- Persist candle and ticker data when `DATABASE_URL` is configured.
- Fall back to stored records when a provider refresh fails and stored data exists.
- Expose basic metrics for operational visibility.

Important files:

- `apps/backend/app/main.py`
- `apps/backend/app/api/`
- `apps/backend/app/services/`
- `apps/backend/app/clients/binance.py`
- `apps/backend/app/clients/postgres.py`
- `apps/backend/app/observability/metrics.py`

## Backend Layering

The backend follows a three-layer structure:

```text
API layer
  -> Service layer
  -> Data access layer
```

API layer:

- Owns FastAPI routers.
- Handles query validation.
- Converts service exceptions into HTTP responses.
- Uses response models to keep output stable.

Service layer:

- Orchestrates use cases such as listing candles or getting a ticker.
- Decides when to read stored records, refresh from Binance, persist data, or fall back.
- Does not depend on FastAPI types.

Data access layer:

- Owns external API calls and database queries.
- Keeps Binance parameter details and PostgreSQL SQL out of route handlers.
- Raises project-owned errors.

This boundary matters because it keeps external provider format, persistence behavior, and HTTP response behavior independently testable.

## API Contract

| Endpoint | Layer | Purpose |
| --- | --- | --- |
| `GET /health` | Backend | Liveness check |
| `GET /ready` | Backend | PostgreSQL readiness check |
| `GET /api/markets` | Backend | Supported market metadata |
| `GET /api/candles` | Backend | Normalized candle list |
| `GET /api/ticker` | Backend | Current price and 24h stats |
| `GET /metrics` | Backend | Prometheus-compatible metrics |

The candle API accepts:

- `symbol`
- `interval`
- `limit`

The ticker API accepts:

- `symbol`

Invalid market data requests are rejected before downstream calls. Provider errors are reported as upstream market data failures rather than leaking low-level client details.

## Market Data

Initial provider:

- Binance public API

Supported symbols:

- `BTCUSDT`
- `ETHUSDT`

Supported candle intervals:

- `1m`
- `5m`
- `15m`
- `1h`
- `1d`

The backend normalizes raw Binance data into project-owned shapes so the frontend does not depend on Binance response arrays or field naming.

## Persistence

PostgreSQL stores normalized market data when `DATABASE_URL` is configured.

Main reasons:

- Keep project-owned market data rather than relying only on live provider calls.
- Demonstrate schema initialization and persistent runtime configuration.
- Allow API fallback to stored data during provider refresh failure.

The k3s Helm chart runs PostgreSQL as a StatefulSet with a persistent volume claim. This is suitable for a compact portfolio deployment. A production system with stronger availability requirements would usually move PostgreSQL to a managed database.

## Kubernetes Runtime

The Helm chart renders:

- Namespace support
- Frontend Deployment and Service
- Backend Deployment and Service
- PostgreSQL StatefulSet and Service
- ConfigMap
- Secret or existing Secret references
- Ingress
- Prometheus Deployment and Service
- Grafana Deployment and Service
- Grafana dashboard ConfigMap
- Optional cert-manager ClusterIssuer

The chart keeps values centralized in:

- `infra/helm/marketpulse/values.yaml`

## Ingress And HTTPS

The public dashboard uses:

- Traefik Ingress
- `marketpulse.byhoon.co.kr`
- cert-manager
- Let's Encrypt ClusterIssuer
- Kubernetes TLS Secret `marketpulse-tls`

The dashboard Ingress routes:

- `/api` to the backend Service
- `/` to the frontend Service

When TLS is enabled, the chart renders Traefik annotations for:

- `web`
- `websecure`
- TLS router behavior

## CI/CD

CI workflow:

- Runs backend `ruff` and `pytest`.
- Runs frontend `npm run lint` and `npm run build`.

Images workflow:

- Builds backend and frontend Docker images.
- Pushes images to Docker Hub on `main`.
- Uses immutable `sha-*` tags.
- Also pushes `latest` for compatibility, but Helm deploys `sha-*`.

Deploy workflow:

- Runs after the Images workflow succeeds on `main`.
- Updates backend and frontend image tags in Helm values.
- Commits GitOps desired state back to `main`.
- Does not connect to Kubernetes.

Argo CD:

- Watches `main`.
- Uses `infra/helm/marketpulse`.
- Syncs automatically.
- Prunes removed resources.
- Self-heals manual cluster drift.

## GitOps Boundary

Git is the source of truth for cluster state.

That means:

- Manual `kubectl patch` can be useful for diagnosis.
- Manual changes should not be treated as durable fixes.
- Argo CD self-heal will revert drift to match Git.
- Durable fixes must be committed through Helm values/templates.

This behavior was visible during HTTPS troubleshooting: manually patching the live Ingress did not persist because Argo CD restored the Git-rendered desired state.

## Observability

Backend metrics include:

- HTTP request counts
- HTTP request duration
- health status
- external API failure counts

Prometheus scrapes the backend metrics endpoint through in-cluster service discovery annotations. Grafana is provisioned with a compact dashboard that visualizes API and provider health.

This is intentionally lightweight. It demonstrates operational readiness without introducing a full production observability stack.

## Failure Modes To Explain

### Chart Is Stale But Current Price Updates

Likely frontend behavior issue:

- ticker polling refreshes current price
- candle data only reloads on symbol/interval change unless candle polling exists

Fix:

- refresh candle data periodically
- keep existing chart visible if background refresh fails

### Deploy Job Is Skipped

Likely CI/CD condition:

- Deploy workflow runs only when Images workflow succeeds
- if image build fails, deploy job is skipped

Fix:

- inspect failed Images run
- rerun failed job if it was transient
- fix build problem if deterministic

### HTTPS Returns 404 But HTTP Works

Likely ingress routing issue:

- DNS reaches Traefik
- HTTP router exists
- HTTPS router does not match host/path

Check:

- Ingress annotations
- TLS section
- Certificate and Secret readiness
- Traefik entrypoints

Fix:

- update GitOps-managed Helm values/templates
- let Argo CD sync the corrected Ingress

## Interview Summary

MarketPulse demonstrates an end-to-end service lifecycle:

1. Build a dashboard UI.
2. Normalize external market data in a backend.
3. Persist project-owned market data.
4. Package frontend/backend as Docker images.
5. Deploy with Helm to k3s.
6. Automate image handoff through GitOps.
7. Use Argo CD for cluster sync and self-heal.
8. Serve HTTPS with cert-manager and Traefik.
9. Expose metrics and a Grafana dashboard.
10. Troubleshoot real deployment issues using logs, GitHub Actions, Kubernetes resources, and public HTTP checks.
