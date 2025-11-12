"""Application configuration and settings management."""

from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[2]
ENV_FILE = BASE_DIR / ".env"


class Settings(BaseSettings):
    """Centralized settings loaded from environment variables or a .env file."""

    # Azure OpenAI Configuration
    azure_openai_key: str
    azure_endpoint: str = "https://draftspeechtotext.cognitiveservices.azure.com"

    # Speech-to-Text Configuration
    stt_deployment_name: str = "gpt-4o-mini-transcribe"
    stt_api_version: str = "2025-03-01-preview"
    default_language: str = "fr"  # French by default

    # LLM Configuration (Mistral)
    mistral_deployment_name: str = "mistral-small-2503"
    mistral_api_version: str = "2024-05-01-preview"

    # Application Configuration
    default_template: str = "rapport_generique"
    project_name: str = "Site Reporter API"
    api_prefix: str = "/api"

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def stt_endpoint(self) -> str:
        """Construct the full STT endpoint URL."""
        return (
            f"{self.azure_endpoint}/openai/deployments/{self.stt_deployment_name}/"
            f"audio/transcriptions?api-version={self.stt_api_version}"
        )

    @property
    def mistral_endpoint(self) -> str:
        """Construct the full Mistral chat completions endpoint URL."""
        return (
            f"{self.azure_endpoint}/openai/deployments/{self.mistral_deployment_name}/"
            f"chat/completions?api-version={self.mistral_api_version}"
        )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached Settings instance to avoid repeated disk I/O."""

    return Settings()
