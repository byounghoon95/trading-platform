# frontend TASK-03: Connect Frontend To Candle API

## Status

done

## Goal

Load market, candle, and ticker data from the backend and render the live dashboard using polling.

## Scope

- Add API client
- Load supported symbols from `GET /api/markets`
- Add symbol selector
- Add interval selector
- Load candle data from `GET /api/candles`
- Poll `GET /api/ticker` every 3 seconds for current price and 24h change
- Mark the ticker as stale when no successful refresh has occurred for 15 seconds
- Add loading, error, and empty states
- Add stale data state when ticker refresh fails
- Render returned candles in the chart with MA 5 and MA 20 overlays computed from the returned candles
- Display the current price and 24h change panel from the ticker response

## Files Expected To Change

- `apps/frontend/src/api/client.js`
- `apps/frontend/src/components/Dashboard.jsx`
- `apps/frontend/src/components/SymbolSelector.jsx`
- `apps/frontend/src/components/IntervalSelector.jsx`
- `apps/frontend/src/components/PricePanel.jsx`
- `apps/frontend/src/components/CandleChart.jsx`

## Out of Scope

- Do not add Redis caching.
- Do not add WebSocket live updates.
- Do not add user watchlists.

## Acceptance Criteria

- Changing symbol or interval reloads chart data.
- Current price updates without a full page reload.
- MA 5 and MA 20 overlays render from the live candle response.
- 24h change is visible in the price panel when the ticker returns it.
- Loading and error states are visible.
- Failed ticker refresh shows a stale or refresh error state after the 15 second threshold.
- Build succeeds.

## Verification

- `npm run build`

## Completion Notes

- Status: done
- Skills used: brainstorming, implement-task
- Changed: replaced mocked dashboard data with API-backed market, candle, and ticker loading; added polling ticker refresh, stale/error/loading/empty states, componentized dashboard controls, price panel, candle chart, and API client; added Vite `/api` dev proxy.
- Verification: `npm run lint` -> passed; `npm run build` -> passed with Node 18 warning because Vite 7 expects Node 20.19+ while the frontend Dockerfile uses Node 22.12; `npm test` -> not run because no test script is configured.
- Notes: depends on backend TASK-04 candle endpoint and backend TASK-05 market/ticker endpoints being merged before this frontend branch is merged/deployed.
