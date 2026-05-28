const symbols = ['BTCUSDT', 'ETHUSDT']
const intervals = ['1m', '5m', '15m', '1h', '1d']

function App() {
  return (
    <main className="dashboard-shell">
      <section className="dashboard-header" aria-labelledby="dashboard-title">
        <div>
          <p className="eyebrow">MarketPulse</p>
          <h1 id="dashboard-title">Crypto Market Dashboard</h1>
        </div>
        <div className="status-strip" aria-label="Market data status">
          <span className="status-pill status-pill--loading">Loading</span>
          <span className="status-pill">No backend connected</span>
        </div>
      </section>

      <section className="controls-panel" aria-label="Market controls">
        <label>
          Symbol
          <select defaultValue="BTCUSDT">
            {symbols.map((symbol) => (
              <option key={symbol} value={symbol}>
                {symbol}
              </option>
            ))}
          </select>
        </label>

        <label>
          Interval
          <select defaultValue="1m">
            {intervals.map((interval) => (
              <option key={interval} value={interval}>
                {interval}
              </option>
            ))}
          </select>
        </label>
      </section>

      <section className="metric-grid" aria-label="Market summary">
        <article className="metric-card">
          <span>Current Price</span>
          <strong>Waiting for data</strong>
        </article>
        <article className="metric-card">
          <span>24h Change</span>
          <strong>--</strong>
        </article>
        <article className="metric-card">
          <span>Refresh</span>
          <strong>Idle</strong>
        </article>
      </section>

      <section className="chart-panel" aria-label="Chart placeholder">
        <div className="chart-placeholder">
          <span>Candlestick chart area</span>
        </div>
      </section>
    </main>
  )
}

export default App
