from fastapi.testclient import TestClient

from app.main import app


def test_markets_endpoint_returns_supported_mvp_markets() -> None:
    test_client = TestClient(app)

    response = test_client.get("/api/markets")

    assert response.status_code == 200
    assert response.json() == [
        {
            "symbol": "BTCUSDT",
            "baseAsset": "BTC",
            "quoteAsset": "USDT",
            "displayName": "BTC / USDT",
            "enabled": True,
        },
        {
            "symbol": "ETHUSDT",
            "baseAsset": "ETH",
            "quoteAsset": "USDT",
            "displayName": "ETH / USDT",
            "enabled": True,
        },
    ]
