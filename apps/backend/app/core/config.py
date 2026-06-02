from dataclasses import dataclass
from os import getenv


@dataclass(frozen=True)
class Settings:
    app_name: str = "MarketPulse API"
    environment: str = "local"
    api_prefix: str = "/api"
    redis_url: str = "redis://localhost:6379/0"


def get_settings() -> Settings:
    return Settings(
        environment=getenv("MARKETPULSE_ENV", "local"),
        redis_url=getenv("REDIS_URL", "redis://localhost:6379/0"),
    )
