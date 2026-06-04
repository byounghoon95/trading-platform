from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.config import Settings
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


def test_readiness_fails_when_database_url_is_missing() -> None:
    test_client = TestClient(app)

    response = test_client.get("/ready")

    assert response.status_code == 503
    assert response.json() == {
        "detail": {
            "code": "database_not_configured",
            "message": "PostgreSQL database URL is not configured",
        }
    }


def test_readiness_returns_ready_when_database_check_passes(monkeypatch) -> None:
    async def check_database_ready_stub(database_url: str) -> None:
        assert database_url == "postgresql://example"

    monkeypatch.setattr(
        "app.api.health.get_settings",
        lambda: Settings(database_url="postgresql://example"),
    )
    monkeypatch.setattr("app.api.health.check_database_ready", check_database_ready_stub)
    test_client = TestClient(app)

    response = test_client.get("/ready")

    assert response.status_code == 200
    assert response.json() == {"status": "ready"}
