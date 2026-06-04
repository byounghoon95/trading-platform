from fastapi.testclient import TestClient

from app.clients.binance import BinanceClientError
from app.main import app
from app.observability.metrics import reset_metrics


def test_metrics_endpoint_returns_prometheus_text() -> None:
    reset_metrics()
    test_client = TestClient(app)

    response = test_client.get("/metrics")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/plain")
    assert "# HELP marketpulse_http_requests_total" in response.text
    assert "# TYPE marketpulse_health_status gauge" in response.text
    assert "marketpulse_health_status 1" in response.text


def test_metrics_track_request_count_and_latency() -> None:
    reset_metrics()
    test_client = TestClient(app)

    test_client.get("/health")
    response = test_client.get("/metrics")

    assert (
        'marketpulse_http_requests_total{method="GET",path="/health",status="200"} 1'
        in response.text
    )
    assert (
        'marketpulse_http_request_duration_seconds_count{method="GET",path="/health"} 1'
        in response.text
    )
    assert (
        'marketpulse_http_request_duration_seconds_sum{method="GET",path="/health"}'
        in response.text
    )


def test_metrics_track_external_api_failures(monkeypatch) -> None:
    async def get_ticker_stub(symbol: str) -> None:
        raise BinanceClientError("provider failed")

    reset_metrics()
    monkeypatch.setattr("app.api.ticker.get_ticker", get_ticker_stub)
    test_client = TestClient(app)

    test_client.get("/api/ticker?symbol=BTCUSDT")
    response = test_client.get("/metrics")

    assert (
        'marketpulse_external_api_failures_total{method="GET",path="/api/ticker"} 1'
        in response.text
    )
