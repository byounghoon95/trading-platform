# backend TASK-03: Implement Binance Market Data Client

## Status

todo

## Goal

Create a backend client that fetches candle and 24h ticker data from Binance public API.

## Scope

- Add Binance HTTP client
- Support `BTCUSDT` and `ETHUSDT`
- Support intervals from `docs/spec.md`
- Fetch candle rows via `/api/v3/klines` and normalize into internal candle objects
- Fetch 24h ticker stats via `/api/v3/ticker/24hr` and normalize into internal ticker objects (`symbol`, `price`, `priceChangePercent24h`, `updatedAt`)
- Handle Binance rate-limit responses (HTTP 429 / 418) with bounded retry and exponential backoff, surfacing a typed error after the cap
- Add tests for candle and ticker normalization and for the 429 backoff path

## Out of Scope

- Do not add Redis caching.
- Do not expose the public API endpoints yet unless needed for testing.
- Do not implement WebSocket streaming.

## Acceptance Criteria

- Binance candle rows are converted into normalized candles.
- Binance 24h ticker payload is converted into normalized ticker objects.
- Invalid symbols and intervals are rejected before any HTTP call.
- 429 / 418 responses trigger bounded retry; the cap and behavior are covered by a test.
- Normalization tests pass.

## Verification

- `pytest`

