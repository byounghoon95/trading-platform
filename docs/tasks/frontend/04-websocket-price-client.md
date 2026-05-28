# frontend TASK-04: Add WebSocket Price Client

## Status

todo

## Goal

Use the backend WebSocket stream for current price updates while keeping polling as a fallback.

## Scope

- Add frontend WebSocket client for ticker updates
- Update current price and 24h change from normalized stream messages
- Show disconnected and reconnecting states
- Fall back to polling when the stream is unavailable
- Keep chart candle loading on the HTTP candle endpoint

## Files Expected To Change

- `apps/frontend/src/api/tickerStream.js`
- `apps/frontend/src/components/PricePanel.jsx`
- `apps/frontend/src/components/ConnectionStatus.jsx`
- `apps/frontend/src/components/Dashboard.jsx`
- `apps/frontend/src/api/client.js`

## Out of Scope

- Do not add trading orders.
- Do not add alerts or watchlists.
- Do not replace the normalized candle API.

## Acceptance Criteria

- Frontend receives current price updates over WebSocket.
- Disconnection and reconnecting states are visible.
- Polling remains available as a fallback.
- Build succeeds.

## Verification

- `npm run build`
- Manual WebSocket smoke test

## Skills

- Required: implement-task
- Optional: none

## Completion Notes

- Status: todo
- Skills used: none
- Verification: not run
- Notes: not started
