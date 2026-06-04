import { useEffect, useMemo, useRef } from 'react'
import {
  CandlestickSeries,
  ColorType,
  createChart,
  HistogramSeries,
  LineSeries,
} from 'lightweight-charts'

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

export function CandleChart({ candles }) {
  const chartContainerRef = useRef(null)
  const ma5 = useMemo(() => calculateMovingAverage(candles, 5), [candles])
  const ma20 = useMemo(() => calculateMovingAverage(candles, 20), [candles])

  useEffect(() => {
    const container = chartContainerRef.current

    if (!container || candles.length === 0) {
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
