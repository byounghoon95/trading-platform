from datetime import UTC, datetime
from decimal import Decimal

from fastapi.testclient import TestClient

from app.clients.binance import BinanceClientError, InvalidMarketDataRequestError, TickerDTO
from app.main import app


def test_ticker_endpoint_returns_normalized_ticker(monkeypatch) -> None:
    async def get_ticker_stub(symbol: str) -> TickerDTO:
        assert symbol == "BTCUSDT"
        return TickerDTO(
            symbol="BTCUSDT",
            price=Decimal("68000.01"),
            price_change_percent_24h=Decimal("2.50"),
            updated_at=datetime(2023, 11, 14, 22, 13, 20, tzinfo=UTC),
        )

    monkeypatch.setattr("app.api.ticker.get_ticker", get_ticker_stub)
    test_client = TestClient(app)

    response = test_client.get("/api/ticker?symbol=BTCUSDT")

    assert response.status_code == 200
    assert response.json() == {
        "symbol": "BTCUSDT",
        "price": "68000.01",
        "priceChangePercent24h": "2.50",
        "updatedAt": "2023-11-14T22:13:20Z",
    }


def test_ticker_endpoint_returns_structured_error_for_invalid_symbol(monkeypatch) -> None:
    async def get_ticker_stub(symbol: str) -> TickerDTO:
        raise InvalidMarketDataRequestError(f"Unsupported symbol: {symbol}")

    monkeypatch.setattr("app.api.ticker.get_ticker", get_ticker_stub)
    test_client = TestClient(app)

    response = test_client.get("/api/ticker?symbol=DOGEUSDT")

    assert response.status_code == 422
    assert response.json() == {
        "detail": {
            "code": "invalid_market_data_request",
            "message": "Unsupported symbol: DOGEUSDT",
        }
    }


def test_ticker_endpoint_returns_bad_gateway_for_provider_failure(monkeypatch) -> None:
    async def get_ticker_stub(symbol: str) -> TickerDTO:
        raise BinanceClientError("provider failed")

    monkeypatch.setattr("app.api.ticker.get_ticker", get_ticker_stub)
    test_client = TestClient(app)

    response = test_client.get("/api/ticker?symbol=BTCUSDT")

    assert response.status_code == 502
    assert response.json() == {
        "detail": {
            "code": "market_data_unavailable",
            "message": "Market data provider request failed",
        }
    }
