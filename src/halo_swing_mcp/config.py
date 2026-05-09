"""Configuration loading for Halo Swing MCP."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Local runtime settings.

    Offline MVP keeps tools deterministic by default. Runtime paths point at
    ignored local artifact locations and must not be committed.
    """

    environment: str = "local"
    log_level: str = "INFO"
    ledger_path: str = "state/signal_ledger.jsonl"
    audit_log_path: str = "state/audit_log.jsonl"
    artifact_dir: str = "artifacts"
    database_url: str | None = None
    binance_testnet: bool = True
    binance_force_testnet_execution: bool = True
    binance_enable_live_trading: bool = False
    binance_recv_window_ms: int = 5000
    binance_credentials_path: str = "state/binance_credentials.enc.json"
    btc_risk_settings_path: str = "state/btc_risk_settings.json"
    btc_risk_state_path: str = "state/btc_risk_state.json"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="HALO_SWING_",
        extra="ignore",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
