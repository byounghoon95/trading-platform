from fastapi import FastAPI

from app.main import app, create_app


def test_app_imports_successfully() -> None:
    assert isinstance(app, FastAPI)


def test_create_app_uses_marketpulse_title() -> None:
    created_app = create_app()

    assert created_app.title == "MarketPulse API"
