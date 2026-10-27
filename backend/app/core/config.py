# Owner: Person 2
# Purpose: Configuration and environment variables management
# TODO(person2): Add dynamic reload support when config files change

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment and defaults."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Miko"
    provider: str = Field(default="mock", description="local | nebius | mock")
    nebius_api_key: str = Field(default="", description="API key for Nebius Token Factory")
    nebius_base_url: str = Field(
        default="https://api.tokenfactory.nebius.com/v1",
        description="Nebius Token Factory base URL",
    )
    ollama_host: str = Field(
        default="http://127.0.0.1:11434",
        description="Local Ollama host (127.0.0.1 only)",
    )
    offline_mode: bool = False
    byo_api_key_enabled: bool = False
    telemetry: bool = False
    host: str = "127.0.0.1"
    port: int = 8000
    db_path: str = "miko.db"

    # Base directory paths
    base_dir: Path = Path(__file__).resolve().parent.parent.parent


settings = Settings()
