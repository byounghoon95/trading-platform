# frontend TASK-03: Connect Frontend To Candle API

## Status

todo

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

## Skills

- Required: implement-task
- Optional: none

## Completion Notes

- Status: todo
- Skills used: none
- Verification: not run
- Notes: not started
