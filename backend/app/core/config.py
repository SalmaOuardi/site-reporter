"""Application configuration and settings management."""

from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[2]
ENV_FILE = BASE_DIR / ".env"


class Settings(BaseSettings):
    """Centralized settings loaded from environment variables or a .env file."""

    openai_api_key: Optional[str] = None
    default_template: str = "daily_summary"
    project_name: str = "Site Reporter API"
    api_prefix: str = "/api"

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached Settings instance to avoid repeated disk I/O."""

    return Settings()
