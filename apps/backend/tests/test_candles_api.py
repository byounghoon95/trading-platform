from datetime import UTC, datetime
from decimal import Decimal

from fastapi.testclient import TestClient

from app.clients.binance import BinanceClientError, CandleDTO, InvalidMarketDataRequestError
from app.clients.postgres import DatabaseClientError
from app.main import app


def test_candles_endpoint_returns_normalized_candles(monkeypatch) -> None:
    async def list_candles_stub(symbol: str, interval: str, limit: int) -> list[CandleDTO]:
        assert symbol == "BTCUSDT"
        assert interval == "1m"
        assert limit == 1
        return [
            CandleDTO(
                symbol="BTCUSDT",
                interval="1m",
                open_time=datetime(2023, 11, 14, 22, 13, 20, tzinfo=UTC),
                close_time=datetime(2023, 11, 14, 22, 14, 19, 999000, tzinfo=UTC),
                open=Decimal("100.10"),
                high=Decimal("105.20"),
                low=Decimal("99.90"),
                close=Decimal("101.30"),
                volume=Decimal("12.345"),
            )
        ]

    monkeypatch.setattr("app.api.candles.list_candles", list_candles_stub)
    test_client = TestClient(app)

    response = test_client.get("/api/candles?symbol=BTCUSDT&interval=1m&limit=1")

    assert response.status_code == 200
    assert response.json() == [
        {
            "symbol": "BTCUSDT",
            "interval": "1m",
            "open_time": "2023-11-14T22:13:20Z",
            "close_time": "2023-11-14T22:14:19.999000Z",
            "open": "100.10",
            "high": "105.20",
            "low": "99.90",
            "close": "101.30",
            "volume": "12.345",
        }
    ]


def test_candles_endpoint_returns_structured_error_for_invalid_symbol(monkeypatch) -> None:
    async def list_candles_stub(symbol: str, interval: str, limit: int) -> list[CandleDTO]:
        raise InvalidMarketDataRequestError(f"Unsupported symbol: {symbol}")

    monkeypatch.setattr("app.api.candles.list_candles", list_candles_stub)
    test_client = TestClient(app)

    response = test_client.get("/api/candles?symbol=DOGEUSDT&interval=1m&limit=1")

    assert response.status_code == 422
    assert response.json() == {
        "detail": {
            "code": "invalid_market_data_request",
            "message": "Unsupported symbol: DOGEUSDT",
        }
    }


def test_candles_endpoint_returns_structured_error_for_invalid_interval(monkeypatch) -> None:
    async def list_candles_stub(symbol: str, interval: str, limit: int) -> list[CandleDTO]:
        raise InvalidMarketDataRequestError(f"Unsupported interval: {interval}")

    monkeypatch.setattr("app.api.candles.list_candles", list_candles_stub)
    test_client = TestClient(app)

    response = test_client.get("/api/candles?symbol=BTCUSDT&interval=30m&limit=1")

    assert response.status_code == 422
    assert response.json() == {
        "detail": {
            "code": "invalid_market_data_request",
            "message": "Unsupported interval: 30m",
        }
    }


def test_candles_endpoint_rejects_invalid_limit_before_service_call(monkeypatch) -> None:
    async def list_candles_stub(symbol: str, interval: str, limit: int) -> list[CandleDTO]:
        raise AssertionError("service should not be called")

    monkeypatch.setattr("app.api.candles.list_candles", list_candles_stub)
    test_client = TestClient(app)

    response = test_client.get("/api/candles?symbol=BTCUSDT&interval=1m&limit=0")

    assert response.status_code == 422


def test_candles_endpoint_returns_bad_gateway_for_provider_failure(monkeypatch) -> None:
    async def list_candles_stub(symbol: str, interval: str, limit: int) -> list[CandleDTO]:
        raise BinanceClientError("provider failed")

    monkeypatch.setattr("app.api.candles.list_candles", list_candles_stub)
    test_client = TestClient(app)

    response = test_client.get("/api/candles?symbol=BTCUSDT&interval=1m&limit=1")

    assert response.status_code == 502
    assert response.json() == {
        "detail": {
            "code": "market_data_unavailable",
            "message": "Market data provider request failed",
        }
    }


def test_candles_endpoint_returns_unavailable_for_database_failure(monkeypatch) -> None:
    async def list_candles_stub(symbol: str, interval: str, limit: int) -> list[CandleDTO]:
        raise DatabaseClientError("database failed")

    monkeypatch.setattr("app.api.candles.list_candles", list_candles_stub)
    test_client = TestClient(app)

    response = test_client.get("/api/candles?symbol=BTCUSDT&interval=1m&limit=1")

    assert response.status_code == 503
    assert response.json() == {
        "detail": {
            "code": "data_store_unavailable",
            "message": "Market data store is unavailable",
        }
    }
