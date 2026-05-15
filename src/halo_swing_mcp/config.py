"""Configuration loading for Halo Swing MCP."""

from functools import lru_cache

from pydantic import ValidationInfo, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


BINANCE_BOOLEAN_ENV_NAMES = {
    "binance_testnet": "HALO_SWING_BINANCE_TESTNET",
    "binance_force_testnet_execution": "HALO_SWING_BINANCE_FORCE_TESTNET_EXECUTION",
    "binance_enable_live_trading": "HALO_SWING_BINANCE_ENABLE_LIVE_TRADING",
}
MARKET_DATA_MODE_ENV_NAME = "HALO_SWING_MARKET_DATA_MODE"
MACRO_DATA_MODE_ENV_NAME = "HALO_SWING_MACRO_DATA_MODE"


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
    runtime_checkpoint_path: str = "state/runtime_checkpoints.jsonl"
    runtime_retention_max_records: int = 1000
    runtime_retention_max_bytes: int = 5_000_000
    runtime_failure_window: int = 20
    runtime_failure_threshold: int = 3
    market_data_mode: str = "fixture"
    market_data_source: str = "polygon"
    market_data_api_key: str | None = None
    macro_data_mode: str = "fixture"
    macro_source: str = "fred"
    macro_api_key: str | None = None

    @field_validator(
        "binance_testnet",
        "binance_force_testnet_execution",
        "binance_enable_live_trading",
        mode="before",
    )
    @classmethod
    def _validate_binance_boolean_env(
        cls,
        value: bool | str,
        info: ValidationInfo,
    ) -> bool:
        if isinstance(value, bool):
            return value
        env_name = BINANCE_BOOLEAN_ENV_NAMES.get(info.field_name or "", info.field_name or "")
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized == "true":
                return True
            if normalized == "false":
                return False
        raise ValueError(f"{env_name} must be 'true' or 'false'")

    @field_validator("market_data_mode", mode="before")
    @classmethod
    def _validate_market_data_mode(cls, value: str) -> str:
        return _validate_data_mode(value, MARKET_DATA_MODE_ENV_NAME)

    @field_validator("macro_data_mode", mode="before")
    @classmethod
    def _validate_macro_data_mode(cls, value: str) -> str:
        return _validate_data_mode(value, MACRO_DATA_MODE_ENV_NAME)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="HALO_SWING_",
        extra="ignore",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


def _validate_data_mode(value: str, env_name: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{env_name} must be fixture or live")
    normalized = value.strip().lower()
    if normalized not in {"fixture", "live"}:
        raise ValueError(f"{env_name} must be fixture or live")
    return normalized
