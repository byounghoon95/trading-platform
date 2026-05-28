# frontend TASK-02: Render Frontend Candle Chart With Mocked Data

## Status

done

## Goal

Render a candlestick chart in the frontend using mocked candle data.

## Scope

- Add Lightweight Charts
- Create chart component
- Render candle series
- Render volume series if practical within this task
- Render MA 5 and MA 20 overlays computed from the mocked candles
- Keep layout responsive

## Out of Scope

- Do not call the backend API yet.
- Do not add live updates.

## Acceptance Criteria

- Chart renders with mocked data.
- MA 5 and MA 20 lines are visible as overlays on the candle chart.
- Dashboard layout remains usable on desktop and mobile widths.

## Verification

- `npm run build`

## Completion Notes

- Status: done
- Skills used: implement-task, requesting-code-review
- Changed: added Lightweight Charts, mocked candle data, responsive candle chart, volume histogram, and MA 5 / MA 20 overlays.
- Verification: `npm run lint` -> passed; `npm run build` -> passed; `npm test` -> not run because no test script is configured.
- Notes: chart data remains mocked and does not call the backend API; Lightweight Charts attribution is left enabled.
