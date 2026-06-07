import { useEffect, useMemo, useState } from 'react'

import { getTicker, listCandles, listMarkets } from '../api/client'
import { CandleChart } from './CandleChart'
import { IntervalSelector } from './IntervalSelector'
import { PricePanel } from './PricePanel'
import { SymbolSelector } from './SymbolSelector'

const DEFAULT_INTERVAL = '1m'
const CANDLE_REFRESH_MS = 10000
const TICKER_REFRESH_MS = 3000
const TICKER_STALE_MS = 15000

function normalizeCandle(candle) {
  return {
    time: Math.floor(Date.parse(candle.open_time) / 1000),
    open: Number(candle.open),
    high: Number(candle.high),
    low: Number(candle.low),
    close: Number(candle.close),
    volume: Number(candle.volume),
  }
}

function buildTickerStatus({ hasTicker, isTickerStale, tickerError }) {
  if (isTickerStale) {
    return { className: 'status-pill status-pill--warning', label: 'Ticker stale' }
  }

  if (tickerError) {
    return { className: 'status-pill status-pill--warning', label: 'Refresh failed' }
  }

  if (hasTicker) {
    return { className: 'status-pill status-pill--ready', label: 'Live data' }
  }

  return { className: 'status-pill', label: 'Connecting' }
}

export function Dashboard() {
  const [markets, setMarkets] = useState([])
  const [selectedSymbol, setSelectedSymbol] = useState('')
  const [selectedInterval, setSelectedInterval] = useState(DEFAULT_INTERVAL)
  const [candles, setCandles] = useState([])
  const [ticker, setTicker] = useState(null)
  const [marketsError, setMarketsError] = useState('')
  const [candlesError, setCandlesError] = useState('')
  const [tickerError, setTickerError] = useState('')
  const [isMarketsLoading, setIsMarketsLoading] = useState(true)
  const [isCandlesLoading, setIsCandlesLoading] = useState(false)
  const [lastTickerSuccessAt, setLastTickerSuccessAt] = useState(null)
  const [tickerStartedAt, setTickerStartedAt] = useState(Date.now())
  const [now, setNow] = useState(Date.now())

  useEffect(() => {
    const controller = new AbortController()

    async function loadMarkets() {
      setIsMarketsLoading(true)
      setMarketsError('')

      try {
        const marketResponse = await listMarkets({ signal: controller.signal })
        const enabledMarkets = marketResponse.filter((market) => market.enabled)
        setMarkets(enabledMarkets)
        setSelectedSymbol((currentSymbol) => {
          if (currentSymbol) {
            return currentSymbol
          }

          return enabledMarkets[0]?.symbol ?? ''
        })
      } catch (error) {
        if (!controller.signal.aborted) {
          setMarketsError(error.message)
        }
      } finally {
        if (!controller.signal.aborted) {
          setIsMarketsLoading(false)
        }
      }
    }

    loadMarkets()

    return () => {
      controller.abort()
    }
  }, [])

  useEffect(() => {
    if (!selectedSymbol) {
      return undefined
    }

    const controller = new AbortController()

    let isRefreshingCandles = false

    async function loadCandles({ resetData = false, showLoading = false } = {}) {
      if (isRefreshingCandles) {
        return
      }

      isRefreshingCandles = true

      if (showLoading) {
        setIsCandlesLoading(true)
      }
      setCandlesError('')

      if (resetData) {
        setCandles([])
      }

      try {
        const candleResponse = await listCandles({
          symbol: selectedSymbol,
          interval: selectedInterval,
          signal: controller.signal,
        })
        setCandles(candleResponse.map(normalizeCandle))
      } catch (error) {
        if (!controller.signal.aborted) {
          setCandlesError(error.message)
        }
      } finally {
        isRefreshingCandles = false

        if (!controller.signal.aborted) {
          setIsCandlesLoading(false)
        }
      }
    }

    loadCandles({ resetData: true, showLoading: true })
    const refreshId = window.setInterval(loadCandles, CANDLE_REFRESH_MS)

    return () => {
      controller.abort()
      window.clearInterval(refreshId)
    }
  }, [selectedInterval, selectedSymbol])

  useEffect(() => {
    if (!selectedSymbol) {
      return undefined
    }

    const controller = new AbortController()
    setTickerStartedAt(Date.now())
    setLastTickerSuccessAt(null)
    setTicker(null)
    setTickerError('')

    async function refreshTicker() {
      try {
        const tickerResponse = await getTicker({
          symbol: selectedSymbol,
          signal: controller.signal,
        })
        setTicker(tickerResponse)
        setTickerError('')
        setLastTickerSuccessAt(Date.now())
      } catch (error) {
        if (!controller.signal.aborted) {
          setTickerError(error.message)
        }
      }
    }

    refreshTicker()
    const refreshId = window.setInterval(refreshTicker, TICKER_REFRESH_MS)

    return () => {
      controller.abort()
      window.clearInterval(refreshId)
    }
  }, [selectedSymbol])

  useEffect(() => {
    const nowId = window.setInterval(() => setNow(Date.now()), 1000)

    return () => {
      window.clearInterval(nowId)
    }
  }, [])

  const selectedMarket = useMemo(
    () => markets.find((market) => market.symbol === selectedSymbol),
    [markets, selectedSymbol],
  )
  const tickerReferenceAt = lastTickerSuccessAt ?? tickerStartedAt
  const isTickerStale =
    Boolean(tickerError) && now - tickerReferenceAt >= TICKER_STALE_MS
  const tickerStatus = buildTickerStatus({
    hasTicker: Boolean(ticker),
    isTickerStale,
    tickerError,
  })
  const hasCandles = candles.length > 0

  return (
    <main className="dashboard-shell">
      <section className="dashboard-header" aria-labelledby="dashboard-title">
        <div>
          <p className="eyebrow">MarketPulse</p>
          <h1 id="dashboard-title">Crypto Market Dashboard</h1>
        </div>
        <div className="status-strip" aria-label="Market data status">
          <span className={tickerStatus.className}>{tickerStatus.label}</span>
          {isCandlesLoading ? <span className="status-pill">Loading candles</span> : null}
        </div>
      </section>

      <section className="controls-panel" aria-label="Market controls">
        <SymbolSelector
          disabled={isMarketsLoading || markets.length === 0}
          markets={markets}
          value={selectedSymbol}
          onChange={setSelectedSymbol}
        />
        <IntervalSelector
          disabled={!selectedSymbol}
          value={selectedInterval}
          onChange={setSelectedInterval}
        />
      </section>

      {marketsError ? <p className="state-message state-message--error">{marketsError}</p> : null}

      <PricePanel candleCount={candles.length} ticker={ticker} />

      <section className="chart-panel" aria-label={`${selectedSymbol} candle chart`}>
        <div className="chart-toolbar">
          <div>
            <span>{selectedMarket?.displayName ?? selectedSymbol}</span>
            <strong>{selectedInterval} live candles</strong>
          </div>
          <div className="legend" aria-label="Chart legend">
            <span className="legend-item legend-item--ma5">MA 5</span>
            <span className="legend-item legend-item--ma20">MA 20</span>
            <span className="legend-item legend-item--volume">Volume</span>
          </div>
        </div>

        {candlesError ? (
          <div className="chart-state chart-state--error">{candlesError}</div>
        ) : null}
        {isCandlesLoading ? (
          <div className="chart-state">Loading market data</div>
        ) : null}
        {!candlesError && !isCandlesLoading && !hasCandles ? (
          <div className="chart-state">No candle data</div>
        ) : null}
        {hasCandles ? <CandleChart candles={candles} /> : null}
      </section>

      {tickerError ? (
        <p className={isTickerStale ? 'state-message state-message--warning' : 'state-message'}>
          {isTickerStale ? 'Ticker data is stale' : tickerError}
        </p>
      ) : null}
    </main>
  )
}
