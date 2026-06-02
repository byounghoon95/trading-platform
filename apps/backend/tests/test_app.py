from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.clients.redis import RedisClientError
from app.main import app, create_app


def test_app_imports_successfully() -> None:
    assert isinstance(app, FastAPI)


def test_create_app_uses_marketpulse_title() -> None:
    created_app = create_app()

    assert created_app.title == "MarketPulse API"


def test_health_endpoint_returns_ok() -> None:
    test_client = TestClient(app)

    response = test_client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_readiness_endpoint_returns_ready_when_redis_is_reachable(monkeypatch) -> None:
    async def check_redis_connection_stub() -> None:
        return None

    monkeypatch.setattr("app.api.health.check_redis_connection", check_redis_connection_stub)
    test_client = TestClient(app)

    response = test_client.get("/ready")

    assert response.status_code == 200
    assert response.json() == {"status": "ready"}


def test_readiness_endpoint_fails_when_redis_is_unreachable(monkeypatch) -> None:
    async def check_redis_connection_stub() -> None:
        raise RedisClientError("Redis is unreachable")

    monkeypatch.setattr("app.api.health.check_redis_connection", check_redis_connection_stub)
    test_client = TestClient(app)

    response = test_client.get("/ready")
    health_response = test_client.get("/health")

    assert response.status_code == 503
    assert response.json() == {
        "detail": {
            "code": "dependency_unavailable",
            "message": "Redis is unreachable",
        }
    }
    assert health_response.status_code == 200
