from dataclasses import dataclass
from os import getenv


@dataclass(frozen=True)
class Settings:
    app_name: str = "MarketPulse API"
    environment: str = "local"
    api_prefix: str = "/api"


def get_settings() -> Settings:
    return Settings(
        environment=getenv("MARKETPULSE_ENV", "local"),
    )
