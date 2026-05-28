# Trading Platform Spec

## 1. Project Summary

This project is a compact trading market dashboard built as a portfolio project.

The goal is not to build a full trading service with accounts, orders, payments, or complex user management. The goal is to build a small but production-shaped application that demonstrates frontend, backend, data processing, containerization, Kubernetes deployment, CI/CD, and operational readiness.

The project should stay compact, but it should not be only a local demo. The implementation should progress in two layers:

- MVP: a working dashboard with normalized market data, caching, local Docker runtime, basic Kubernetes manifests, and CI checks.
- Advanced ops layer: production-style deployment, HTTPS ingress, metrics, dashboards, and deployment automation that show operational capability without expanding into trading features.

Working name: `MarketPulse`

Core concept:

> A login-free crypto market dashboard that displays candle charts, volume, moving averages, and near real-time price updates for selected trading pairs.

## 2. Portfolio Goal

The project should show that the developer can design, implement, deploy, and operate a small service end to end.

Primary signals:

- Frontend can render interactive market data cleanly.
- Backend can integrate with an external market data API and normalize data.
- System can handle caching, rate limits, health checks, and failure states.
- Application can run locally with Docker Compose.
- Application can be deployed to k3s with Kubernetes manifests or Helm.
- CI/CD can test, build, and package the application.
- Advanced CI/CD can push images and deploy or hand off to k3s manifests.
- Basic operational health checks, logging, and troubleshooting documentation exist.
- Advanced observability can show metrics and dashboards.

Non-goal:

- This is not a real-money trading platform.
- This is not an exchange.
- This does not place buy/sell orders.
- This does not need login, signup, portfolio management, or payment features.

## 3. Target User Experience

The first screen should be the actual dashboard, not a landing page.

Expected user flow:

1. User opens the dashboard.
2. User selects a market symbol such as `BTCUSDT`, `ETHUSDT`.
3. User selects a candle interval such as `1m`, `5m`, `15m`, `1h`, or `1d`.
4. The dashboard displays candle data, volume, current price, and moving averages.
5. Current price updates without a full page reload.
6. Loading, error, empty, and disconnected states are visible and handled.

MVP real-time behavior:

- The frontend polls the backend ticker endpoint every few seconds.
- The UI shows stale, loading, and failed refresh states.

Advanced real-time behavior:

- The backend connects to Binance streams and forwards simplified updates over WebSocket.
- The frontend shows disconnected and reconnecting states for the stream.

## 4. MVP Scope

### Frontend

- Main dashboard layout
- Symbol selector
- Interval selector
- Candlestick chart
- Volume chart
- MA 5 and MA 20 overlays (computed client-side from the normalized candle response)
- Current price panel
- 24h change panel if available from the selected data source
- Loading state
- Error state
- Polling refresh state for ticker updates
- Stale data state when refresh fails

### Backend

- `GET /health`
- `GET /api/markets`
- `GET /api/candles?symbol=BTCUSDT&interval=1m&limit=200`
- `GET /api/ticker?symbol=BTCUSDT`
- Polling-friendly ticker endpoint for price updates
- External market data API client
- Candle response normalization
- 24h ticker stats fetch and normalization
- Bounded retry with exponential backoff on Binance rate-limit responses (HTTP 429 / 418)
- Input validation
- Structured error responses
- Basic request logging

### Data

- Initial market data source: Binance public API
- Supported symbols for MVP:
  - `BTCUSDT`
  - `ETHUSDT`
- Supported intervals:
  - `1m`
  - `5m`
  - `15m`
  - `1h`
  - `1d`

### Infrastructure

- Dockerfile for frontend
- Dockerfile for backend
- Docker Compose for local development
- k3s deployment manifests or Helm chart
- Basic Ingress for k3s deployment
- ConfigMap and Secret usage
- Readiness and liveness probes
- GitHub Actions CI workflow
- GitHub Actions image build workflow
- Documented deployment workflow or GitOps handoff

### Observability

- Backend health endpoint
- Liveness and readiness behavior
- Structured backend logs for request and external API failures
- Troubleshooting notes for common local, API, Redis, and deployment issues

Advanced observability:

- Basic metrics endpoint
- Prometheus scrape configuration or documented integration
- Grafana dashboard for API health, request rate, latency, and external API failures

Advanced infrastructure:

- HTTPS ingress with cert-manager
- Automated image push and k3s deployment workflow
- GitOps integration such as Argo CD

## 5. Deliberately Out of Scope

The following should not be included in the first portfolio version:

- User authentication
- User-specific watchlists
- Real trading orders
- Exchange API keys
- Payment or billing
- Admin pages
- Complex alerting rules
- News feed
- Social features
- Backtesting engine
- AI trading recommendations

These may be documented as future work, but they should not block the MVP.

## 6. Recommended Tech Stack

The stack should stay familiar, practical, and easy to explain in an interview.

### Frontend

Recommended:

- Next.js or React with Vite
- JavaScript
- Lightweight Charts
- TanStack Query
- Zustand only if global state becomes necessary

Frontend selection rule:

- Use React with Vite if the project should stay simple.
- Use Next.js only if routing, deployment patterns, or SSR-like structure are useful.

Recommended choice for this project:

- React + Vite + JavaScript

Reason:

- The app is a dashboard, not a content-heavy site.
- SSR is not necessary.
- Vite keeps the frontend small and fast to develop.

### Backend

Recommended choice for this project:

- FastAPI + Python

Reason:

- FastAPI has built-in OpenAPI support.
- Pydantic validation is a good fit for market data query parameters and normalized responses.
- Async HTTP clients and WebSocket support are straightforward.
- Python keeps data normalization and future analytics work simple.

### Cache

Recommended:

- Redis

Use cases:

- Cache candle API responses with short TTL.
- Reduce external API calls.
- Show rate-limit-aware backend design.

### Database

MVP recommendation:

- No database for the first version.

Optional portfolio upgrade:

- PostgreSQL or TimescaleDB for historical candle persistence.

Reason:

- A database is not required to show the core dashboard.
- Avoiding DB in MVP keeps the project focused.
- Redis and external API integration already provide enough backend work.

### Infrastructure

Recommended:

- Docker
- Docker Compose
- k3s
- NGINX Ingress or Traefik
- cert-manager
- GitHub Actions
- Container registry such as GitHub Container Registry

## 7. Architecture

MVP architecture:

```text
Browser
  |
  | HTTP
  v
Frontend
  |
  | HTTP
  v
Backend API
  |
  | cache read/write
  v
Redis
  |
  | cache miss
  v
Binance Public API
```

k3s deployment architecture:

```text
Internet
  |
  v
Ingress Controller
  |
  +--> Frontend Service --> Frontend Pod
  |
  +--> Backend Service  --> Backend Pod
                            |
                            v
                          Redis Service --> Redis Pod
```

MVP Kubernetes scope:

- Deploy frontend, backend, and Redis to k3s.
- Use ConfigMaps for non-secret configuration.
- Use Secrets only for values that should not be committed, even if the MVP does not require exchange credentials.
- Add liveness and readiness probes.
- Expose the frontend through an Ingress.

Advanced Kubernetes scope:

- Configure HTTPS ingress with cert-manager.
- Add Prometheus scrape annotations or ServiceMonitor resources when a metrics stack is available.
- Add resource requests and limits after basic workloads are running.

CI/CD flow:

```text
Git push
  |
  v
GitHub Actions
  |
  +--> lint/test
  +--> build Docker images
  +--> push images to registry
  +--> deploy to k3s or update GitOps manifests
```

MVP CI/CD scope:

- Run frontend and backend checks.
- Build Docker images.
- Optionally push images to GitHub Container Registry when registry credentials are configured.

Advanced CI/CD scope:

- Push versioned images to GitHub Container Registry.
- Deploy to k3s directly or update GitOps manifests.
- Document required GitHub secrets and rollback steps.

## 8. Key Technical Problems To Demonstrate

The project should intentionally include a few meaningful engineering problems.

### External API Normalization

Binance API responses should be converted into frontend-friendly candle objects.

Example normalized candle:

```json
{
  "time": 1716883200,
  "open": 68400.12,
  "high": 68520.45,
  "low": 68110.3,
  "close": 68350.78,
  "volume": 1240.52
}
```

Example market object:

```json
{
  "symbol": "BTCUSDT",
  "baseAsset": "BTC",
  "quoteAsset": "USDT",
  "displayName": "BTC / USDT",
  "enabled": true
}
```

Example ticker object:

```json
{
  "symbol": "BTCUSDT",
  "price": 68350.78,
  "priceChangePercent24h": 1.25,
  "updatedAt": "2026-05-28T12:00:00Z"
}
```

The frontend should consume these normalized objects instead of depending on Binance response shapes directly.

### Cache Strategy

The backend should cache candle data by `symbol`, `interval`, and `limit`.

Example cache key:

```text
candles:BTCUSDT:1m:200
```

Suggested TTL:

- `1m`: 10-20 seconds
- `5m`: 30-60 seconds
- `15m`: 60-120 seconds
- `1h`: 3-5 minutes
- `1d`: 10-30 minutes

### Real-Time Updates

MVP:

- Frontend polls backend ticker endpoint every few seconds.
- Polling is easier to operate, test, and explain for the first portfolio version.
- The UI should expose refresh failures and stale data instead of silently showing old prices.

Advanced:

- Backend connects to Binance stream and forwards simplified updates to frontend clients over WebSocket.
- The frontend shows disconnected and reconnecting states.
- This is a portfolio upgrade after the normalized HTTP API is stable.

### Frontend Chart Performance

The frontend should avoid rendering excessive data.

Initial limit:

- 200 candles

Later optional limit:

- 500 candles

### Kubernetes Readiness

Backend readiness should fail when required dependencies are unavailable.

Example:

- Liveness: process is alive.
- Readiness: backend can serve requests and Redis is reachable.

## 9. Repository Structure

Recommended structure:

```text
trading-platform/
  apps/
    frontend/
    backend/
  infra/
    docker/
    k8s/
  docs/
    spec.md
    tasks/
      README.md
      foundation/
      backend/
      frontend/
      infra/
      portfolio/
  .github/
    workflows/
```

## 10. Development Method

This project should be developed through spec-based Codex tasks.

Each task should include:

- Goal
- Scope
- Out of scope
- Acceptance criteria
- Verification commands
- Skills required or optional
- Files expected to change

Recommended task prompt:

```text
$writing-plans backend TASK-01
$implement-task backend TASK-01
$requesting-code-review backend TASK-01
```

The `$brainstorming` skill should refine project-level direction before implementation planning.
The `$writing-plans` skill should refine one task file before implementation.
The `$implement-task` skill should read the project specs, implement only the requested task, verify the change, and update the task file with status, skills used, and notes.
The `$requesting-code-review` skill should review the completed task against the spec, task file, and verification expectations.

## 11. Initial Task Roadmap

### Foundation

- foundation TASK-01: Create repository structure

### Backend Track

- backend TASK-01: Create FastAPI backend scaffold
- backend TASK-02: Implement backend health endpoint
- backend TASK-03: Implement Binance candle client
- backend TASK-04: Implement normalized candle endpoint
- backend TASK-05: Add Redis candle caching
- backend TASK-06: Add market and ticker endpoints
- backend TASK-07: Add WebSocket price stream

### Frontend Track

- frontend TASK-01: Create frontend scaffold
- frontend TASK-02: Render frontend candle chart with mocked data
- frontend TASK-03: Connect frontend to market, candle, and ticker APIs
- frontend TASK-04: Add WebSocket price client

### Infrastructure Track

- infra TASK-01: Add Docker Compose baseline
- infra TASK-02: Add production Dockerfiles
- infra TASK-03: Add k3s manifests
- infra TASK-04: Add GitHub Actions CI
- infra TASK-05: Add image build and deploy workflow
- infra TASK-06: Add metrics endpoint and Prometheus scrape configuration
- infra TASK-07: Add Grafana dashboard documentation or dashboard JSON
- infra TASK-08: Add HTTPS ingress with cert-manager
- infra TASK-09: Add k3s deployment automation

### Portfolio Track

- portfolio TASK-01: Final README and portfolio docs

Parallelization rule:

- After foundation TASK-01, backend scaffold, frontend scaffold, and Docker Compose baseline can be worked on independently.
- Frontend mocked chart work can continue before backend API completion.
- Frontend API integration should wait for the normalized candle endpoint and market/ticker endpoints.
- k3s and CI/CD work should wait until the app structure is stable.

## 12. Definition of Done

The portfolio version is done when:

- The dashboard works locally with one command.
- Candle chart, volume, MA lines, and current price are visible.
- Backend hides external API details behind normalized endpoints.
- Redis caching is implemented and documented.
- Docker images build successfully.
- k3s manifests can deploy the app with frontend, backend, Redis, probes, and ingress.
- CI runs tests and builds images.
- README explains architecture, local run, deployment, and tradeoffs.
- At least one operational issue or troubleshooting case is documented.

The advanced ops layer is done when:

- Images can be pushed to GitHub Container Registry.
- A documented or automated deployment path updates k3s.
- HTTPS ingress is configured or clearly documented for the target cluster.
- Metrics can be scraped by Prometheus or the integration is documented.
- A Grafana dashboard or dashboard plan exists for the main operational signals.
- WebSocket streaming is implemented only after the HTTP API and polling flow are stable.

## 13. Interview Talking Points

The project should prepare answers for these questions:

- Why was login excluded?
- Why was k3s selected instead of EKS or GKE?
- Why was Redis used?
- How are external API rate limits handled?
- How is candle data normalized?
- How does the frontend handle reconnecting or stale data?
- What is the difference between liveness and readiness probes?
- How does the deployment pipeline work?
- What would change if this became a real trading platform?

## 14. Future Work

Possible later additions:

- Watchlist without login using local storage
- Alert rules for price thresholds
- PostgreSQL or TimescaleDB candle persistence
- More exchanges
- More indicators such as RSI or MACD
- Backtesting sandbox
- Loki-based log dashboard
