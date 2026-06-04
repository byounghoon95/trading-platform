function formatUsd(value) {
  if (value == null || Number.isNaN(value)) {
    return '-'
  }

  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    maximumFractionDigits: 2,
  }).format(value)
}

function formatPercent(value) {
  if (value == null || Number.isNaN(value)) {
    return '-'
  }

  return `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`
}

export function PricePanel({ candleCount, ticker }) {
  const price = ticker ? Number(ticker.price) : null
  const priceChangePercent24h = ticker
    ? Number(ticker.priceChangePercent24h)
    : null
  const priceChangeClass =
    priceChangePercent24h == null
      ? undefined
      : priceChangePercent24h >= 0
        ? 'positive'
        : 'negative'
  const updatedAt = ticker ? new Date(ticker.updatedAt) : null

  return (
    <section className="metric-grid" aria-label="Market summary">
      <article className="metric-card">
        <span>Current Price</span>
        <strong>{formatUsd(price)}</strong>
      </article>
      <article className="metric-card">
        <span>24h Change</span>
        <strong className={priceChangeClass}>
          {formatPercent(priceChangePercent24h)}
        </strong>
      </article>
      <article className="metric-card">
        <span>Last Update</span>
        <strong>{updatedAt ? updatedAt.toLocaleTimeString() : '-'}</strong>
        <small>{candleCount} candles loaded</small>
      </article>
    </section>
  )
}
