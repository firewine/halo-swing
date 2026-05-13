"""Offline integration readiness checks for blocked deployment gates."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from halo_swing_mcp import MCP_SERVER_NAME
from halo_swing_mcp.binance_btc import LIVE_CONFIRMATION
from halo_swing_mcp.config import get_settings
from halo_swing_mcp.risk_settings import load_btc_risk_settings, resolve_settings_path
from halo_swing_mcp.secret_store import get_binance_credentials_status


HERMES_SERVER_COMMAND = "PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.server"
HERMES_CONFIG_PATH_ENV = "HALO_SWING_HERMES_CONFIG_PATH"


def get_integration_readiness(
    *,
    hermes_config_path: str | None = None,
    hermes_mcp_config_registered: bool = False,
    telegram_configured: bool | None = None,
    telegram_bot_token_configured: bool | None = None,
    telegram_gateway_configured: bool | None = None,
    migration_go_approved: bool = False,
    repository_go_approved: bool = False,
    binance_credentials_path: str | None = None,
    binance_passphrase_confirmed: bool = False,
    binance_trade_only_permission_attested: bool = False,
    live_order_approved: bool = False,
    btc_risk_settings_path: str | None = None,
    market_data_source_configured: bool | None = None,
    macro_source_configured: bool | None = None,
    news_source_configured: bool | None = None,
) -> dict[str, Any]:
    """Return offline readiness for gates that need user environment decisions."""

    normalized_hermes_config_path = _resolve_hermes_config_path(
        hermes_config_path,
    )
    normalized_hermes_registered = _normalize_boolean(
        hermes_mcp_config_registered,
        "hermes_mcp_config_registered",
    )
    normalized_telegram_configured = _normalize_optional_boolean(
        telegram_configured,
        "telegram_configured",
    )
    normalized_telegram_bot_token_configured = _normalize_optional_boolean(
        telegram_bot_token_configured,
        "telegram_bot_token_configured",
    )
    normalized_telegram_gateway_configured = _normalize_optional_boolean(
        telegram_gateway_configured,
        "telegram_gateway_configured",
    )
    normalized_migration_go = _normalize_boolean(
        migration_go_approved,
        "migration_go_approved",
    )
    normalized_repository_go = _normalize_boolean(
        repository_go_approved,
        "repository_go_approved",
    )
    normalized_binance_credentials_path = _normalize_optional_path(
        binance_credentials_path,
        "binance_credentials_path",
    )
    normalized_binance_passphrase_confirmed = _normalize_boolean(
        binance_passphrase_confirmed,
        "binance_passphrase_confirmed",
    )
    normalized_binance_trade_only_permission_attested = _normalize_boolean(
        binance_trade_only_permission_attested,
        "binance_trade_only_permission_attested",
    )
    normalized_live_order_approved = _normalize_boolean(
        live_order_approved,
        "live_order_approved",
    )
    normalized_btc_risk_settings_path = _normalize_optional_path(
        btc_risk_settings_path,
        "btc_risk_settings_path",
    )
    normalized_market_data_source_configured = _normalize_optional_boolean(
        market_data_source_configured,
        "market_data_source_configured",
    )
    normalized_macro_source_configured = _normalize_optional_boolean(
        macro_source_configured,
        "macro_source_configured",
    )
    normalized_news_source_configured = _normalize_optional_boolean(
        news_source_configured,
        "news_source_configured",
    )
    credentials_path = normalized_binance_credentials_path
    risk_settings_path = (
        normalized_btc_risk_settings_path
        if normalized_btc_risk_settings_path is not None
        else str(resolve_settings_path())
    )
    hermes = _hermes_readiness(
        normalized_hermes_config_path,
        normalized_hermes_registered,
    )
    telegram = _telegram_readiness(
        normalized_telegram_configured,
        normalized_telegram_bot_token_configured,
        normalized_telegram_gateway_configured,
    )
    migration = _migration_readiness(normalized_migration_go)
    repository = _repository_readiness(
        normalized_repository_go,
        normalized_migration_go,
    )
    binance = _binance_readiness(
        credentials_path,
        normalized_binance_passphrase_confirmed,
    )
    live_order = _live_order_submission_readiness(
        credentials_path,
        normalized_binance_passphrase_confirmed,
        normalized_binance_trade_only_permission_attested,
        normalized_live_order_approved,
        risk_settings_path,
    )
    live_data = _live_data_readiness(
        normalized_market_data_source_configured,
        normalized_macro_source_configured,
        normalized_news_source_configured,
    )
    gates = {
        "hermes": hermes,
        "telegram": telegram,
        "migration": migration,
        "repository": repository,
        "binance_testnet_read_only": binance,
        "live_order_submission": live_order,
        "live_data": live_data,
    }

    return {
        "status": "ready" if all(gate["ready"] for gate in gates.values()) else "blocked",
        "gates": gates,
        "next_actions": _next_actions(gates),
        "live_data_required": False,
    }


def _hermes_readiness(
    hermes_config_path: str | None,
    mcp_config_registered: bool,
) -> dict[str, Any]:
    configured_path = hermes_config_path
    config_path_exists = bool(configured_path and Path(configured_path).exists())
    config_path_is_absolute = bool(
        configured_path and Path(configured_path).is_absolute()
    )
    ready = config_path_exists and mcp_config_registered
    missing: list[str] = []
    if not config_path_exists:
        missing.append("hermes_config_path")
    if not mcp_config_registered:
        missing.append("hermes_mcp_config_registration")
    return {
        "ready": ready,
        "status": "ready" if ready else "blocked",
        "missing": missing,
        "evidence": {
            "schema_version": "hermes_mcp_config_readiness.v1",
            "config_path": configured_path,
            "config_path_exists": config_path_exists,
            "config_path_is_absolute": config_path_is_absolute,
            "mcp_config_registered": mcp_config_registered,
            "mcp_server_name": MCP_SERVER_NAME,
            "transport": "stdio",
            "server_module": "halo_swing_mcp.server",
            "server_command": HERMES_SERVER_COMMAND,
            "runtime_started": False,
            "network_call": False,
            "secret_values_returned": False,
        },
    }


def _resolve_hermes_config_path(hermes_config_path: str | None) -> str | None:
    if hermes_config_path is not None:
        return _normalize_path(hermes_config_path, "hermes_config_path")
    if HERMES_CONFIG_PATH_ENV in os.environ:
        return _normalize_path(os.environ[HERMES_CONFIG_PATH_ENV], HERMES_CONFIG_PATH_ENV)
    return None


def _telegram_readiness(
    telegram_configured: bool | None,
    bot_token_configured: bool | None,
    gateway_configured: bool | None,
) -> dict[str, Any]:
    env_bot_token_configured = _env_value_configured(
        "HALO_SWING_TELEGRAM_BOT_TOKEN",
        "TELEGRAM_BOT_TOKEN",
    )
    env_gateway_configured = _env_value_configured(
        "HALO_SWING_TELEGRAM_GATEWAY",
        "HALO_SWING_TELEGRAM_GATEWAY_URL",
    )
    token_ready = (
        bot_token_configured
        if bot_token_configured is not None
        else env_bot_token_configured
    )
    gateway_ready = (
        gateway_configured
        if gateway_configured is not None
        else env_gateway_configured
    )
    configured = token_ready or gateway_ready
    if telegram_configured is not None:
        configured = telegram_configured
    return {
        "ready": configured,
        "status": "ready" if configured else "blocked",
        "missing": [] if configured else ["telegram_bot_token_or_gateway"],
        "evidence": {
            "schema_version": "telegram_delivery_readiness.v1",
            "telegram_configured": configured,
            "bot_token_configured": token_ready,
            "gateway_configured": gateway_ready,
            "delivery_preview_available": True,
            "telegram_report_format_schema": "telegram_report_format.v1",
            "send_call": False,
            "network_call": False,
            "credential_storage_added": False,
            "secret_values_returned": False,
        },
    }


def _migration_readiness(migration_go_approved: bool) -> dict[str, Any]:
    readiness_packet = Path("docs/gates/P1_MIGRATION_GATE_READINESS_2026-05-10.md")
    ready = migration_go_approved
    return {
        "ready": ready,
        "status": "ready" if ready else "blocked",
        "missing": [] if ready else ["explicit_MIGRATION_GO"],
        "evidence": {
            "readiness_packet_exists": readiness_packet.exists(),
            "migration_go_approved": migration_go_approved,
            "migration_files_allowed": ready,
        },
    }


def _repository_readiness(
    repository_go_approved: bool,
    migration_go_approved: bool,
) -> dict[str, Any]:
    ready = repository_go_approved and migration_go_approved
    missing: list[str] = []
    if not migration_go_approved:
        missing.append("MIGRATION_GO")
    if not repository_go_approved:
        missing.append("REPOSITORY_GO")
    return {
        "ready": ready,
        "status": "ready" if ready else "blocked",
        "missing": missing,
        "evidence": {
            "migration_go_approved": migration_go_approved,
            "repository_go_approved": repository_go_approved,
        },
    }


def _binance_readiness(
    credentials_path: str | None,
    passphrase_confirmed: bool,
) -> dict[str, Any]:
    settings = get_settings()
    credential_status = get_binance_credentials_status(credentials_path)
    ready = (
        settings.binance_testnet
        and settings.binance_force_testnet_execution
        and credential_status["configured"]
        and passphrase_confirmed
    )
    missing: list[str] = []
    if not settings.binance_testnet:
        missing.append("HALO_SWING_BINANCE_TESTNET=true")
    if not settings.binance_force_testnet_execution:
        missing.append("HALO_SWING_BINANCE_FORCE_TESTNET_EXECUTION=true")
    if not credential_status["configured"]:
        missing.append("encrypted_binance_testnet_credentials")
    if not passphrase_confirmed:
        missing.append("manual_credential_passphrase_at_smoke_time")
    return {
        "ready": ready,
        "status": "ready" if ready else "blocked",
        "missing": missing,
        "evidence": {
            "testnet": settings.binance_testnet,
            "force_testnet_execution": settings.binance_force_testnet_execution,
            "live_trading_enabled": settings.binance_enable_live_trading,
            "manual_passphrase_confirmed": passphrase_confirmed,
            "credentials": credential_status,
            "secret_values_returned": False,
        },
    }


def _live_order_submission_readiness(
    credentials_path: str | None,
    passphrase_confirmed: bool,
    trade_only_permission_attested: bool,
    live_order_approved: bool,
    risk_settings_path: str | None,
) -> dict[str, Any]:
    settings = get_settings()
    credential_status = get_binance_credentials_status(credentials_path)
    credential_policy = credential_status["credential_policy"]
    risk_settings = load_btc_risk_settings(risk_settings_path)
    testnet_policy_ready = (
        settings.binance_testnet if settings.binance_force_testnet_execution else True
    )
    ready = (
        live_order_approved
        and settings.binance_enable_live_trading
        and testnet_policy_ready
        and credential_status["configured"]
        and passphrase_confirmed
        and trade_only_permission_attested
        and credential_policy["trade_permission_required"]
        and not credential_policy["withdraw_permission_allowed"]
        and not risk_settings.emergency_kill_switch_enabled
    )
    missing: list[str] = []
    if not live_order_approved:
        missing.append("explicit_live_order_approval")
    if not settings.binance_enable_live_trading:
        missing.append("HALO_SWING_BINANCE_ENABLE_LIVE_TRADING=true")
    if not testnet_policy_ready:
        missing.append("HALO_SWING_BINANCE_TESTNET=true")
    if not credential_status["configured"]:
        missing.append("encrypted_binance_credentials")
    if not passphrase_confirmed:
        missing.append("manual_credential_passphrase_at_order_time")
    if not trade_only_permission_attested:
        missing.append("binance_console_trade_only_no_withdraw_attestation")
    if risk_settings.emergency_kill_switch_enabled:
        missing.append("emergency_kill_switch_disabled")
    return {
        "ready": ready,
        "status": "ready" if ready else "blocked",
        "missing": missing,
        "evidence": {
            "live_order_approved": live_order_approved,
            "live_trading_enabled": settings.binance_enable_live_trading,
            "testnet": settings.binance_testnet,
            "force_testnet_execution": settings.binance_force_testnet_execution,
            "manual_passphrase_confirmed": passphrase_confirmed,
            "trade_only_permission_attested": trade_only_permission_attested,
            "emergency_kill_switch_enabled": risk_settings.emergency_kill_switch_enabled,
            "requires_confirmation": LIVE_CONFIRMATION,
            "order_submission": False,
            "network_call": False,
            "credentials": credential_status,
            "secret_values_returned": False,
        },
    }


def _live_data_readiness(
    market_data_source_configured: bool | None,
    macro_source_configured: bool | None,
    news_source_configured: bool | None,
) -> dict[str, Any]:
    env_market_configured = _market_data_env_configured()
    env_macro_configured = _macro_env_configured()
    env_news_configured = _news_env_configured()
    market_configured = (
        market_data_source_configured
        if market_data_source_configured is not None
        else env_market_configured
    )
    macro_configured = (
        macro_source_configured
        if macro_source_configured is not None
        else env_macro_configured
    )
    news_configured = (
        news_source_configured
        if news_source_configured is not None
        else env_news_configured
    )
    ready = market_configured and macro_configured and news_configured
    missing: list[str] = []
    if not market_configured:
        missing.append("market_ohlcv_source_or_api_key_decision")
    if not macro_configured:
        missing.append("macro_source_or_api_key_decision")
    if not news_configured:
        missing.append("news_source_or_api_key_decision")
    return {
        "ready": ready,
        "status": "ready" if ready else "blocked",
        "missing": missing,
        "evidence": {
            "schema_version": "live_data_source_readiness.v1",
            "market_ohlcv_source_configured": market_configured,
            "macro_source_configured": macro_configured,
            "news_source_configured": news_configured,
            "live_adapter_added": False,
            "network_call": False,
            "secret_values_returned": False,
        },
    }


def _market_data_env_configured() -> bool:
    return _env_value_configured(
        "HALO_SWING_MARKET_DATA_SOURCE",
        "HALO_SWING_MARKET_DATA_API_KEY",
        "POLYGON_API_KEY",
        "ALPACA_API_KEY",
        "TIINGO_API_KEY",
    )


def _macro_env_configured() -> bool:
    return _env_value_configured(
        "HALO_SWING_MACRO_SOURCE",
        "FRED_API_KEY",
        "HALO_SWING_FRED_API_KEY",
    )


def _news_env_configured() -> bool:
    return _env_value_configured(
        "HALO_SWING_NEWS_SOURCE",
        "NEWS_API_KEY",
        "HALO_SWING_NEWS_API_KEY",
    )


def _env_value_configured(*keys: str) -> bool:
    return any(_is_env_value_configured(os.environ.get(key)) for key in keys)


def _is_env_value_configured(value: str | None) -> bool:
    return bool(
        isinstance(value, str)
        and value.strip()
        and _has_no_control_characters(value)
    )


def _normalize_boolean(value: bool, field_name: str) -> bool:
    if type(value) is not bool:
        raise ValueError(f"{field_name} must be a boolean")
    return value


def _normalize_optional_boolean(value: bool | None, field_name: str) -> bool | None:
    if value is None:
        return None
    if type(value) is not bool:
        raise ValueError(f"{field_name} must be a boolean when provided")
    return value


def _normalize_optional_path(value: str | None, field_name: str) -> str | None:
    if value is None:
        return None
    return _normalize_path(value, field_name)


def _normalize_path(value: Any, field_name: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be a nonempty string")
    if not _has_no_control_characters(value):
        raise ValueError(f"{field_name} must not contain control characters")
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{field_name} must be a nonempty string")
    return normalized


def _has_no_control_characters(value: str) -> bool:
    return all(ord(character) >= 32 and ord(character) != 127 for character in value)


def _next_actions(gates: dict[str, dict[str, Any]]) -> list[str]:
    actions: list[str] = []
    for name, gate in gates.items():
        if not gate["ready"]:
            missing = ", ".join(gate["missing"])
            actions.append(f"{name}: provide {missing}")
    return actions
