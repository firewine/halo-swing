"""Configuration loading for Halo Swing MCP."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Local runtime settings.

    P0 keeps health_check deterministic; these settings are scaffolding for later
    live integrations and Hermes registration.
    """

    environment: str = "local"
    log_level: str = "INFO"
    database_url: str = "sqlite:///data/halo_swing.sqlite3"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="HALO_SWING_",
        extra="ignore",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
