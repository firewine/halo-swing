"""Offline integration readiness checks for blocked deployment gates."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from halo_swing_mcp import MCP_SERVER_NAME
from halo_swing_mcp.binance_btc import LIVE_CONFIRMATION
from halo_swing_mcp.config import get_settings
from halo_swing_mcp.env import get_config_value
from halo_swing_mcp.risk_settings import load_btc_risk_settings, resolve_settings_path
from halo_swing_mcp.secret_store import get_binance_credentials_status


HERMES_SERVER_COMMAND = "PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.server"
HERMES_CONFIG_PATH_ENV = "HALO_SWING_HERMES_CONFIG_PATH"
HERMES_MCP_CONFIG_REGISTERED_ENV = "HALO_SWING_HERMES_MCP_CONFIG_REGISTERED"
BINANCE_PASSPHRASE_CONFIRMED_ENV = "HALO_SWING_BINANCE_PASSPHRASE_CONFIRMED"
BINANCE_TRADE_ONLY_PERMISSION_ATTESTED_ENV = (
    "HALO_SWING_BINANCE_TRADE_ONLY_PERMISSION_ATTESTED"
)
BINANCE_LIVE_ORDER_APPROVED_ENV = "HALO_SWING_BINANCE_LIVE_ORDER_APPROVED"


def get_integration_readiness(
    *,
    hermes_config_path: str | None = None,
    hermes_mcp_config_registered: bool | None = None,
    telegram_configured: bool | None = None,
    telegram_bot_token_configured: bool | None = None,
    telegram_gateway_configured: bool | None = None,
    migration_go_approved: bool = False,
    repository_go_approved: bool = False,
    binance_credentials_path: str | None = None,
    binance_passphrase_confirmed: bool | None = None,
    binance_trade_only_permission_attested: bool | None = None,
    live_order_approved: bool | None = None,
    btc_risk_settings_path: str | None = None,
    market_data_source_configured: bool | None = None,
    macro_source_configured: bool | None = None,
    news_source_configured: bool | None = None,
) -> dict[str, Any]:
    """Return offline readiness for gates that need user environment decisions."""

    normalized_hermes_config_path = _resolve_hermes_config_path(
        hermes_config_path,
    )
    normalized_hermes_registered = _resolve_hermes_mcp_config_registered(
        hermes_mcp_config_registered,
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
    normalized_binance_passphrase_confirmed = _resolve_binance_passphrase_confirmed(
        binance_passphrase_confirmed,
    )
    normalized_binance_trade_only_permission_attested = (
        _resolve_binance_trade_only_permission_attested(
            binance_trade_only_permission_attested,
        )
    )
    normalized_live_order_approved = _resolve_binance_live_order_approved(
        live_order_approved,
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


def get_integration_setup_checklist() -> dict[str, Any]:
    """Return local setup requirements derived from offline readiness state."""

    readiness = get_integration_readiness()
    gates = readiness["gates"]
    return {
        "schema_version": "integration_setup_checklist.v1",
        "status": readiness["status"],
        "readiness_status": readiness["status"],
        "next_actions": readiness["next_actions"],
        "env_requirements": _setup_env_requirements(gates),
        "local_commands": _setup_local_commands(),
        "durable_gate_requirements": [
            {
                "gate": "migration",
                "required_approval": "MIGRATION_GO",
                "dotenv_supported": False,
                "configured": gates["migration"]["ready"],
                "missing": gates["migration"]["missing"],
            },
            {
                "gate": "repository",
                "required_approval": "REPOSITORY_GO",
                "dotenv_supported": False,
                "configured": gates["repository"]["ready"],
                "missing": gates["repository"]["missing"],
            },
        ],
        "offline_guardrails": {
            "network_call": False,
            "hermes_runtime_started": False,
            "telegram_send_call": False,
            "order_submission": False,
            "secret_values_returned": False,
            "dotenv_mutation": False,
            "credential_file_write": False,
        },
        "secret_values_returned": False,
        "network_call": False,
        "send_call": False,
        "order_submission": False,
    }


def _setup_env_requirements(gates: dict[str, Any]) -> list[dict[str, Any]]:
    binance_credentials = gates["binance_testnet_read_only"]["evidence"][
        "credentials"
    ]
    return [
        {
            "section": "hermes",
            "required_for": "Hermes MCP config readiness",
            "env_keys": [
                HERMES_CONFIG_PATH_ENV,
                HERMES_MCP_CONFIG_REGISTERED_ENV,
            ],
            "configured": gates["hermes"]["ready"],
            "secret": False,
            "value_policy": "config path plus non-secret true/false registration flag",
            "missing": gates["hermes"]["missing"],
        },
        {
            "section": "telegram",
            "required_for": "Telegram delivery readiness",
            "env_keys": [
                "HALO_SWING_TELEGRAM_BOT_TOKEN",
                "TELEGRAM_BOT_TOKEN",
                "HALO_SWING_TELEGRAM_GATEWAY",
                "HALO_SWING_TELEGRAM_GATEWAY_URL",
            ],
            "configured": gates["telegram"]["ready"],
            "secret": True,
            "value_policy": "provide a bot token or gateway; values are never returned",
            "missing": gates["telegram"]["missing"],
        },
        {
            "section": "live_data",
            "required_for": "market, macro, and news live-data readiness",
            "env_keys": [
                "HALO_SWING_MARKET_DATA_API_KEY",
                "POLYGON_API_KEY",
                "HALO_SWING_MACRO_API_KEY",
                "HALO_SWING_FRED_API_KEY",
                "FRED_API_KEY",
                "HALO_SWING_NEWS_API_KEY",
                "NEWS_API_KEY",
            ],
            "configured": gates["live_data"]["ready"],
            "secret": True,
            "value_policy": "provide one supported API key per provider family",
            "missing": gates["live_data"]["missing"],
        },
        {
            "section": "binance_credentials",
            "required_for": "Binance COIN-M credential readiness",
            "env_keys": ["HALO_SWING_BINANCE_CREDENTIALS_PATH"],
            "configured": binance_credentials["configured"],
            "secret": False,
            "value_policy": "path to encrypted local credential file",
            "missing": (
                []
                if binance_credentials["configured"]
                else ["encrypted_binance_credentials"]
            ),
        },
        {
            "section": "binance_read_only_smoke",
            "required_for": "Binance testnet read-only account smoke readiness",
            "env_keys": [
                "HALO_SWING_BINANCE_TESTNET",
                "HALO_SWING_BINANCE_FORCE_TESTNET_EXECUTION",
                BINANCE_PASSPHRASE_CONFIRMED_ENV,
            ],
            "configured": gates["binance_testnet_read_only"]["ready"],
            "secret": False,
            "value_policy": "testnet safety flags plus non-secret passphrase availability confirmation",
            "missing": gates["binance_testnet_read_only"]["missing"],
        },
        {
            "section": "binance_live_order_readiness",
            "required_for": "live-order readiness evidence without submitting orders",
            "env_keys": [
                "HALO_SWING_BINANCE_ENABLE_LIVE_TRADING",
                BINANCE_LIVE_ORDER_APPROVED_ENV,
                BINANCE_PASSPHRASE_CONFIRMED_ENV,
                BINANCE_TRADE_ONLY_PERMISSION_ATTESTED_ENV,
            ],
            "configured": gates["live_order_submission"]["ready"],
            "secret": False,
            "value_policy": "explicit operator approvals and safety flags only",
            "missing": gates["live_order_submission"]["missing"],
        },
    ]


def _setup_local_commands() -> list[dict[str, Any]]:
    return [
        {
            "name": "save_binance_credentials",
            "purpose": "encrypt Binance API credentials into the configured local file",
            "command": (
                "PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness "
                "save_binance_credentials --input-json "
                "'{\"api_key\":\"<binance_api_key>\","
                "\"api_secret\":\"<binance_api_secret>\","
                "\"passphrase\":\"<local_passphrase>\","
                "\"credentials_path\":\"state/binance_credentials.enc.json\"}'"
            ),
            "network_call": False,
            "mutates_local_state": True,
            "secret_values_returned": False,
        },
        {
            "name": "get_integration_readiness",
            "purpose": "check current readiness evidence after .env values are set",
            "command": (
                "PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness "
                "get_integration_readiness --no-audit"
            ),
            "network_call": False,
            "mutates_local_state": False,
            "secret_values_returned": False,
        },
        {
            "name": "get_integration_setup_checklist",
            "purpose": "show missing local setup requirements without changing state",
            "command": (
                "PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness "
                "get_integration_setup_checklist --no-audit"
            ),
            "network_call": False,
            "mutates_local_state": False,
            "secret_values_returned": False,
        },
    ]


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
    env_value = get_config_value(HERMES_CONFIG_PATH_ENV)
    if env_value is not None:
        return _normalize_path(env_value, HERMES_CONFIG_PATH_ENV)
    return None


def _resolve_hermes_mcp_config_registered(value: bool | None) -> bool:
    if value is not None:
        return _normalize_boolean(value, "hermes_mcp_config_registered")
    env_value = get_config_value(HERMES_MCP_CONFIG_REGISTERED_ENV)
    if env_value is None or not env_value.strip():
        return False
    return _normalize_env_boolean(env_value, HERMES_MCP_CONFIG_REGISTERED_ENV)


def _resolve_binance_passphrase_confirmed(value: bool | None) -> bool:
    if value is not None:
        return _normalize_boolean(value, "binance_passphrase_confirmed")
    env_value = get_config_value(BINANCE_PASSPHRASE_CONFIRMED_ENV)
    if env_value is None or not env_value.strip():
        return False
    return _normalize_env_boolean(env_value, BINANCE_PASSPHRASE_CONFIRMED_ENV)


def _resolve_binance_trade_only_permission_attested(value: bool | None) -> bool:
    if value is not None:
        return _normalize_boolean(
            value,
            "binance_trade_only_permission_attested",
        )
    env_value = get_config_value(BINANCE_TRADE_ONLY_PERMISSION_ATTESTED_ENV)
    if env_value is None or not env_value.strip():
        return False
    return _normalize_env_boolean(
        env_value,
        BINANCE_TRADE_ONLY_PERMISSION_ATTESTED_ENV,
    )


def _resolve_binance_live_order_approved(value: bool | None) -> bool:
    if value is not None:
        return _normalize_boolean(value, "live_order_approved")
    env_value = get_config_value(BINANCE_LIVE_ORDER_APPROVED_ENV)
    if env_value is None or not env_value.strip():
        return False
    return _normalize_env_boolean(env_value, BINANCE_LIVE_ORDER_APPROVED_ENV)


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
    env_market_configured = _market_data_api_key_env_configured()
    env_macro_configured = _macro_api_key_env_configured()
    env_news_configured = _news_api_key_env_configured()
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
        missing.append("market_ohlcv_api_key")
    if not macro_configured:
        missing.append("macro_api_key")
    if not news_configured:
        missing.append("news_api_key")
    return {
        "ready": ready,
        "status": "ready" if ready else "blocked",
        "missing": missing,
        "evidence": {
            "schema_version": "live_data_source_readiness.v1",
            "market_ohlcv_source_configured": market_configured,
            "macro_source_configured": macro_configured,
            "news_source_configured": news_configured,
            "live_adapter_added": True,
            "network_call": False,
            "secret_values_returned": False,
        },
    }


def _market_data_api_key_env_configured() -> bool:
    return _env_value_configured(
        "HALO_SWING_MARKET_DATA_API_KEY",
        "POLYGON_API_KEY",
    )


def _macro_api_key_env_configured() -> bool:
    return _env_value_configured(
        "HALO_SWING_MACRO_API_KEY",
        "FRED_API_KEY",
        "HALO_SWING_FRED_API_KEY",
    )


def _news_api_key_env_configured() -> bool:
    return _env_value_configured(
        "NEWS_API_KEY",
        "HALO_SWING_NEWS_API_KEY",
    )


def _env_value_configured(*keys: str) -> bool:
    return any(_is_env_value_configured(get_config_value(key)) for key in keys)


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


def _normalize_env_boolean(value: str, env_name: str) -> bool:
    if not _has_no_control_characters(value):
        raise ValueError(f"{env_name} must be 'true' or 'false'")
    normalized = value.strip().lower()
    if normalized == "true":
        return True
    if normalized == "false":
        return False
    raise ValueError(f"{env_name} must be 'true' or 'false'")


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
