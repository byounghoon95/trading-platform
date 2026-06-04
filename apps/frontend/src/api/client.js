const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? ''

async function requestJson(path, { signal } = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, { signal })

  if (!response.ok) {
    let message = `Request failed with status ${response.status}`

    try {
      const body = await response.json()
      message = body?.detail?.message ?? message
    } catch {
      // Keep the HTTP status message when the backend did not return JSON.
    }

    throw new Error(message)
  }

  return response.json()
}

export function listMarkets({ signal } = {}) {
  return requestJson('/api/markets', { signal })
}

export function listCandles({ symbol, interval, limit = 200, signal }) {
  const params = new URLSearchParams({
    symbol,
    interval,
    limit: String(limit),
  })

  return requestJson(`/api/candles?${params.toString()}`, { signal })
}

export function getTicker({ symbol, signal }) {
  const params = new URLSearchParams({ symbol })

  return requestJson(`/api/ticker?${params.toString()}`, { signal })
}
