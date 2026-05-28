import { useEffect, useMemo, useRef } from 'react'
import {
  CandlestickSeries,
  ColorType,
  createChart,
  HistogramSeries,
  LineSeries,
} from 'lightweight-charts'

const symbols = ['BTCUSDT', 'ETHUSDT']
const intervals = ['1m', '5m', '15m', '1h', '1d']

const mockCandles = Array.from({ length: 80 }, (_, index) => {
  const time = Math.floor(Date.UTC(2026, 0, 1, 9, 0, 0) / 1000) + index * 60
  const trend = index * 48
  const wave = Math.sin(index / 4) * 620
  const open = 92800 + trend + wave
  const close = open + Math.cos(index / 3) * 420 + (index % 7 - 3) * 24
  const high = Math.max(open, close) + 260 + (index % 5) * 38
  const low = Math.min(open, close) - 240 - (index % 4) * 42
  const volume = 170 + Math.abs(close - open) / 9 + (index % 9) * 12

  return {
    time,
    open: Number(open.toFixed(2)),
    high: Number(high.toFixed(2)),
    low: Number(low.toFixed(2)),
    close: Number(close.toFixed(2)),
    volume: Number(volume.toFixed(2)),
  }
})

function formatUsd(value) {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    maximumFractionDigits: 2,
  }).format(value)
}

function calculateMovingAverage(candles, windowSize) {
  return candles
    .map((candle, index) => {
      if (index < windowSize - 1) {
        return null
      }

      const window = candles.slice(index - windowSize + 1, index + 1)
      const average =
        window.reduce((total, current) => total + current.close, 0) / windowSize

      return {
        time: candle.time,
        value: Number(average.toFixed(2)),
      }
    })
    .filter(Boolean)
}

function CandleChart({ candles }) {
  const chartContainerRef = useRef(null)
  const ma5 = useMemo(() => calculateMovingAverage(candles, 5), [candles])
  const ma20 = useMemo(() => calculateMovingAverage(candles, 20), [candles])

  useEffect(() => {
    const container = chartContainerRef.current

    if (!container) {
      return undefined
    }

    const chart = createChart(container, {
      autoSize: true,
      layout: {
        background: { type: ColorType.Solid, color: '#18201f' },
        textColor: '#cbd5e1',
        attributionLogo: true,
      },
      grid: {
        vertLines: { color: 'rgba(148, 163, 184, 0.12)' },
        horzLines: { color: 'rgba(148, 163, 184, 0.12)' },
      },
      rightPriceScale: {
        borderColor: 'rgba(148, 163, 184, 0.24)',
        scaleMargins: {
          top: 0.08,
          bottom: 0.28,
        },
      },
      timeScale: {
        borderColor: 'rgba(148, 163, 184, 0.24)',
        timeVisible: true,
        secondsVisible: false,
      },
      crosshair: {
        vertLine: { color: 'rgba(226, 232, 240, 0.35)' },
        horzLine: { color: 'rgba(226, 232, 240, 0.35)' },
      },
    })

    const candleSeries = chart.addSeries(CandlestickSeries, {
      upColor: '#22c55e',
      downColor: '#ef4444',
      borderUpColor: '#22c55e',
      borderDownColor: '#ef4444',
      wickUpColor: '#86efac',
      wickDownColor: '#fca5a5',
    })

    const volumeSeries = chart.addSeries(HistogramSeries, {
      priceFormat: { type: 'volume' },
      priceScaleId: '',
      color: 'rgba(96, 165, 250, 0.34)',
    })

    volumeSeries.priceScale().applyOptions({
      scaleMargins: {
        top: 0.78,
        bottom: 0,
      },
    })

    const ma5Series = chart.addSeries(LineSeries, {
      color: '#f59e0b',
      lineWidth: 2,
      priceLineVisible: false,
      lastValueVisible: false,
    })

    const ma20Series = chart.addSeries(LineSeries, {
      color: '#38bdf8',
      lineWidth: 2,
      priceLineVisible: false,
      lastValueVisible: false,
    })

    candleSeries.setData(candles)
    volumeSeries.setData(
      candles.map((candle) => ({
        time: candle.time,
        value: candle.volume,
        color:
          candle.close >= candle.open
            ? 'rgba(34, 197, 94, 0.28)'
            : 'rgba(239, 68, 68, 0.28)',
      })),
    )
    ma5Series.setData(ma5)
    ma20Series.setData(ma20)
    chart.timeScale().fitContent()

    return () => {
      chart.remove()
    }
  }, [candles, ma5, ma20])

  return <div className="candle-chart" ref={chartContainerRef} />
}

function App() {
  const latestCandle = mockCandles.at(-1)
  const firstCandle = mockCandles[0]
  const priceChange = latestCandle.close - firstCandle.open
  const priceChangePercent = (priceChange / firstCandle.open) * 100

  return (
    <main className="dashboard-shell">
      <section className="dashboard-header" aria-labelledby="dashboard-title">
        <div>
          <p className="eyebrow">MarketPulse</p>
          <h1 id="dashboard-title">Crypto Market Dashboard</h1>
        </div>
        <div className="status-strip" aria-label="Market data status">
          <span className="status-pill status-pill--ready">Mock data</span>
          <span className="status-pill">Backend not connected</span>
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
          <strong>{formatUsd(latestCandle.close)}</strong>
        </article>
        <article className="metric-card">
          <span>Mock Session Change</span>
          <strong className={priceChange >= 0 ? 'positive' : 'negative'}>
            {priceChange >= 0 ? '+' : ''}
            {priceChangePercent.toFixed(2)}%
          </strong>
        </article>
        <article className="metric-card">
          <span>Candles</span>
          <strong>{mockCandles.length}</strong>
        </article>
      </section>

      <section className="chart-panel" aria-label="Mocked BTCUSDT candle chart">
        <div className="chart-toolbar">
          <div>
            <span>BTCUSDT</span>
            <strong>1m mocked candles</strong>
          </div>
          <div className="legend" aria-label="Chart legend">
            <span className="legend-item legend-item--ma5">MA 5</span>
            <span className="legend-item legend-item--ma20">MA 20</span>
            <span className="legend-item legend-item--volume">Volume</span>
          </div>
        </div>
        <CandleChart candles={mockCandles} />
      </section>
    </main>
  )
}

export default App
