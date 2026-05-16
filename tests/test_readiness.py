import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

import halo_swing_mcp.env as local_env
from halo_swing_mcp.audit import read_audit_events
from halo_swing_mcp.config import get_settings
from halo_swing_mcp.env import clear_local_env_cache
from halo_swing_mcp.risk_settings import update_btc_risk_settings
from halo_swing_mcp.secret_store import save_binance_credentials
from halo_swing_mcp.tools.readiness import (
    get_integration_readiness,
    get_integration_setup_checklist,
    get_live_data_api_key_status,
    get_live_data_provider_route,
    run_api_key_pipeline_smoke,
    run_integration_smoke,
    run_live_data_smoke,
    run_live_recording_smoke,
    run_live_signal_workflow_smoke,
    validate_live_data_smoke_result,
)
from halo_swing_mcp.tools.market import (
    get_macro_snapshot,
    get_market_snapshot,
    get_news_bundle,
)


ROOT = Path(__file__).resolve().parents[1]
READINESS_ENV_KEYS = (
    "HALO_SWING_HERMES_CONFIG_PATH",
    "HALO_SWING_HERMES_MCP_CONFIG_REGISTERED",
    "HALO_SWING_DISABLE_DOTENV",
    "HALO_SWING_TELEGRAM_BOT_TOKEN",
    "HALO_SWING_TELEGRAM_GATEWAY",
    "HALO_SWING_TELEGRAM_GATEWAY_URL",
    "TELEGRAM_BOT_TOKEN",
    "FRED_API_KEY",
    "NEWS_API_KEY",
    "HALO_SWING_MACRO_API_KEY",
    "HALO_SWING_FRED_API_KEY",
    "HALO_SWING_NEWS_API_KEY",
    "HALO_SWING_BINANCE_TESTNET",
    "HALO_SWING_BINANCE_FORCE_TESTNET_EXECUTION",
    "HALO_SWING_BINANCE_ENABLE_LIVE_TRADING",
    "HALO_SWING_BINANCE_CREDENTIALS_PATH",
    "HALO_SWING_BINANCE_LIVE_ORDER_APPROVED",
    "HALO_SWING_BINANCE_PASSPHRASE_CONFIRMED",
    "HALO_SWING_BINANCE_TRADE_ONLY_PERMISSION_ATTESTED",
    "HALO_SWING_MARKET_DATA_MODE",
    "HALO_SWING_MARKET_DATA_SOURCE",
    "HALO_SWING_MARKET_DATA_API_KEY",
    "HALO_SWING_MACRO_DATA_MODE",
    "HALO_SWING_MACRO_SOURCE",
    "HALO_SWING_NEWS_DATA_MODE",
    "HALO_SWING_NEWS_SOURCE",
    "HALO_SWING_LIVE_HTTP_TIMEOUT_SECONDS",
    "POLYGON_API_KEY",
    "ALPACA_API_KEY",
    "TIINGO_API_KEY",
)
EXPECTED_READINESS_PAYLOAD_KEYS = [
    "status",
    "gates",
    "next_actions",
    "live_data_required",
]
EXPECTED_READINESS_GATE_NAMES = [
    "hermes",
    "telegram",
    "migration",
    "repository",
    "binance_testnet_read_only",
    "live_order_submission",
    "live_data",
]
EXPECTED_READINESS_GATE_KEYS = ["ready", "status", "missing", "evidence"]
EXPECTED_READINESS_EVIDENCE_KEYS_BY_GATE = {
    "hermes": [
        "schema_version",
        "config_path",
        "config_path_exists",
        "config_path_is_absolute",
        "mcp_config_registered",
        "mcp_server_name",
        "transport",
        "server_module",
        "server_command",
        "runtime_started",
        "network_call",
        "secret_values_returned",
    ],
    "telegram": [
        "schema_version",
        "telegram_configured",
        "bot_token_configured",
        "gateway_configured",
        "delivery_preview_available",
        "telegram_report_format_schema",
        "send_call",
        "network_call",
        "credential_storage_added",
        "secret_values_returned",
    ],
    "migration": [
        "readiness_packet_exists",
        "migration_go_approved",
        "migration_files_allowed",
    ],
    "repository": ["migration_go_approved", "repository_go_approved"],
    "binance_testnet_read_only": [
        "testnet",
        "force_testnet_execution",
        "live_trading_enabled",
        "manual_passphrase_confirmed",
        "credentials",
        "secret_values_returned",
    ],
    "live_order_submission": [
        "live_order_approved",
        "live_trading_enabled",
        "testnet",
        "force_testnet_execution",
        "manual_passphrase_confirmed",
        "trade_only_permission_attested",
        "emergency_kill_switch_enabled",
        "requires_confirmation",
        "order_submission",
        "network_call",
        "credentials",
        "secret_values_returned",
    ],
    "live_data": [
        "schema_version",
        "market_ohlcv_source_configured",
        "macro_source_configured",
        "news_source_configured",
        "live_adapter_added",
        "network_call",
        "secret_values_returned",
    ],
}


def expected_dotenv_file_status(target_path: Path) -> dict[str, Any]:
    source_path = target_path.with_name(".env.example")
    source_exists = source_path.is_file()
    target_exists = target_path.is_file()
    copy_required = source_exists and not target_exists
    next_action = (
        "copy_env_example_to_env"
        if copy_required
        else "fill_live_data_api_keys"
        if target_exists
        else "restore_env_example"
    )
    return {
        "schema_version": "live_data_dotenv_file_status.v1",
        "target_path": ".env",
        "source_path": ".env.example",
        "target_exists": target_exists,
        "source_exists": source_exists,
        "copy_required": copy_required,
        "next_action": next_action,
        "copy_command": {
            "name": "copy_env_example_to_env",
            "command": "cp .env.example .env",
            "required": copy_required,
            "source_path": ".env.example",
            "target_path": ".env",
            "network_call": False,
            "mutates_local_state": True,
            "secret_values_returned": False,
        },
        "fill_keys_after_copy": {
            "required_env_keys": ["POLYGON_API_KEY", "FRED_API_KEY", "NEWS_API_KEY"],
            "secret": True,
            "secret_values_returned": False,
        },
        "mutation": False,
        "network_call": False,
        "mutates_local_state": False,
        "secret_values_returned": False,
    }


def expected_pipeline_smoke_command() -> dict[str, Any]:
    return {
        "name": "run_api_key_pipeline_smoke",
        "purpose": (
            "run readiness, provider, signal workflow, and recording smoke "
            "checks after API keys are configured"
        ),
        "command": (
            "PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness "
            "run_api_key_pipeline_smoke --input-json "
            "'{\"asset\":\"TQQQ\",\"timeframe\":\"swing_3d_10d\","
            "\"symbols\":[\"QQQ\"],\"topic\":\"macro\"}' --no-audit"
        ),
        "network_call": True,
        "network_call_policy": "only_when_matching_api_key_selects_live_provider",
        "mutates_local_state": False,
        "secret_values_returned": False,
    }


def expected_api_key_status_command() -> dict[str, Any]:
    return {
        "name": "get_live_data_api_key_status",
        "purpose": (
            "show live data API-key readiness and configured alias names "
            "without network calls or secret values"
        ),
        "command": (
            "PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness "
            "get_live_data_api_key_status --no-audit"
        ),
        "network_call": False,
        "mutates_local_state": False,
        "secret_values_returned": False,
    }


def expected_live_data_setup_steps(
    *,
    target_path: Path,
    configured_provider_families: list[str],
    missing_provider_families: list[str],
    ready_to_run_live_smoke: bool,
) -> dict[str, Any]:
    dotenv_file_status = expected_dotenv_file_status(target_path)
    configured_count = len(configured_provider_families)
    required_count = 3
    keys_ready = configured_count == required_count
    provider_smoke_plan = expected_provider_smoke_plan(
        market_configured_env_keys=(
            ["POLYGON_API_KEY"] if "market" in configured_provider_families else []
        ),
        macro_configured_env_keys=(
            ["FRED_API_KEY"] if "macro" in configured_provider_families else []
        ),
        news_configured_env_keys=(
            ["NEWS_API_KEY"] if "news" in configured_provider_families else []
        ),
        ready_to_run_live_smoke=ready_to_run_live_smoke,
    )
    next_provider_smoke = next(
        (
            provider_smoke
            for provider_smoke in provider_smoke_plan["provider_smokes"]
            if provider_smoke["status"] == "ready"
        ),
        None,
    )
    if (
        dotenv_file_status["source_exists"] is False
        and dotenv_file_status["target_exists"] is False
    ):
        next_step = "restore_env_example"
        dotenv_status = "blocked"
    elif dotenv_file_status["copy_required"] is True:
        next_step = "prepare_dotenv"
        dotenv_status = "pending"
    else:
        next_step = (
            "run_provider_smokes"
            if ready_to_run_live_smoke
            else "fill_live_data_api_keys"
        )
        dotenv_status = "ready"
    return {
        "schema_version": "live_data_setup_steps.v1",
        "next_step": next_step,
        "steps": [
            {
                "name": "prepare_dotenv",
                "status": dotenv_status,
                "next_action": dotenv_file_status["next_action"],
                "copy_command": dotenv_file_status["copy_command"],
                "network_call": False,
                "mutates_local_state": False,
                "secret_values_returned": False,
            },
            {
                "name": "fill_live_data_api_keys",
                "status": "ready" if keys_ready else "pending",
                "configured_provider_families": configured_provider_families,
                "missing_provider_families": missing_provider_families,
                "configured_count": configured_count,
                "required_count": required_count,
                "required_env_keys": ["POLYGON_API_KEY", "FRED_API_KEY", "NEWS_API_KEY"],
                "network_call": False,
                "mutates_local_state": False,
                "secret_values_returned": False,
            },
            {
                "name": "run_provider_smokes",
                "status": "ready" if ready_to_run_live_smoke else "blocked",
                "provider_smokes": provider_smoke_plan["provider_smokes"],
                "provider_smoke_count": 3,
                "next_provider_smoke": next_provider_smoke,
                "next_provider_smoke_command_name": (
                    next_provider_smoke["smoke_command_name"]
                    if next_provider_smoke
                    else None
                ),
                "ready_provider_smoke_count": provider_smoke_plan[
                    "ready_provider_smoke_count"
                ],
                "blocked_provider_smoke_count": provider_smoke_plan[
                    "blocked_provider_smoke_count"
                ],
                "network_call": True,
                "network_call_policy": "only_when_matching_api_key_selects_live_provider",
                "mutates_local_state": False,
                "secret_values_returned": False,
            },
            {
                "name": "run_api_key_pipeline_smoke",
                "status": "ready" if ready_to_run_live_smoke else "blocked",
                "command": expected_pipeline_smoke_command()["command"],
                "network_call": True,
                "mutates_local_state": False,
                "secret_values_returned": False,
            },
        ],
        "network_call": False,
        "mutates_local_state": False,
        "secret_values_returned": False,
    }


def expected_next_operator_action(
    *,
    target_path: Path,
    configured_provider_families: list[str],
    missing_provider_families: list[str],
    ready_to_run_live_smoke: bool,
) -> dict[str, Any]:
    dotenv_file_status = expected_dotenv_file_status(target_path)
    setup_steps = expected_live_data_setup_steps(
        target_path=target_path,
        configured_provider_families=configured_provider_families,
        missing_provider_families=missing_provider_families,
        ready_to_run_live_smoke=ready_to_run_live_smoke,
    )
    base = {
        "schema_version": "live_data_next_operator_action.v1",
        "name": setup_steps["next_step"],
        "dotenv_target_path": ".env",
        "network_call": False,
        "mutates_local_state": False,
        "secret_values_returned": False,
    }
    if setup_steps["next_step"] == "restore_env_example":
        return {
            **base,
            "status": "blocked",
            "reason": "missing_env_example_and_env",
            "required_file": ".env.example",
            "secret_input_required": False,
        }
    if setup_steps["next_step"] == "prepare_dotenv":
        copy_command = dotenv_file_status["copy_command"]
        return {
            **base,
            "status": "pending",
            "command": copy_command["command"],
            "source_path": copy_command["source_path"],
            "target_path": copy_command["target_path"],
            "next_after_action": "fill_live_data_api_keys",
            "secret_input_required": False,
            "mutates_local_state": True,
        }
    if setup_steps["next_step"] == "run_provider_smokes":
        provider_smoke_step = setup_steps["steps"][2]
        return {
            **base,
            "name": "run_provider_smokes",
            "status": "ready",
            "provider_smokes": provider_smoke_step["provider_smokes"],
            "provider_smoke_count": provider_smoke_step["provider_smoke_count"],
            "next_provider_smoke": provider_smoke_step["next_provider_smoke"],
            "next_provider_smoke_command_name": provider_smoke_step[
                "next_provider_smoke_command_name"
            ],
            "ready_provider_smoke_count": provider_smoke_step[
                "ready_provider_smoke_count"
            ],
            "blocked_provider_smoke_count": provider_smoke_step[
                "blocked_provider_smoke_count"
            ],
            "network_call": True,
            "network_call_policy": provider_smoke_step["network_call_policy"],
            "next_after_action": "run_api_key_pipeline_smoke",
            "secret_input_required": False,
        }
    if ready_to_run_live_smoke:
        smoke_command = expected_pipeline_smoke_command()
        return {
            **base,
            "name": "run_api_key_pipeline_smoke",
            "status": "ready",
            "command": smoke_command["command"],
            "network_call": True,
            "network_call_policy": smoke_command["network_call_policy"],
            "secret_input_required": False,
        }
    return {
        **base,
        "name": "fill_live_data_api_keys",
        "status": "pending",
        "required_env_keys": ["POLYGON_API_KEY", "FRED_API_KEY", "NEWS_API_KEY"],
        "configured_provider_families": configured_provider_families,
        "missing_provider_families": missing_provider_families,
        "next_after_action": "run_provider_smokes",
        "secret_input_required": True,
    }


def expected_provider_smoke_command(name: str) -> dict[str, Any]:
    commands = {
        "get_market_snapshot_live_smoke": {
            "name": "get_market_snapshot_live_smoke",
            "provider": "polygon",
            "required_env_key_groups": [
                ["HALO_SWING_MARKET_DATA_API_KEY", "POLYGON_API_KEY"]
            ],
            "command": (
                "PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness "
                "get_market_snapshot --input-json '{\"symbols\":[\"QQQ\"]}' "
                "--no-audit"
            ),
            "expected_live_contract": "market_snapshot_contract",
            "expected_live_checks": ["live_data_boundary_declared"],
            "network_call_policy": "only_when_matching_api_key_selects_live_provider",
            "mutates_local_state": False,
            "hermes_runtime_started": False,
            "telegram_send_call": False,
            "order_submission": False,
            "secret_values_returned": False,
        },
        "get_macro_snapshot_live_smoke": {
            "name": "get_macro_snapshot_live_smoke",
            "provider": "fred",
            "required_env_key_groups": [
                [
                    "HALO_SWING_MACRO_API_KEY",
                    "HALO_SWING_FRED_API_KEY",
                    "FRED_API_KEY",
                ]
            ],
            "command": (
                "PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness "
                "get_macro_snapshot --no-audit"
            ),
            "expected_live_contract": "macro_filter_contract",
            "expected_live_checks": [
                "live_data_boundary_declared",
                "network_call_declared",
            ],
            "network_call_policy": "only_when_matching_api_key_selects_live_provider",
            "mutates_local_state": False,
            "hermes_runtime_started": False,
            "telegram_send_call": False,
            "order_submission": False,
            "secret_values_returned": False,
        },
        "get_news_bundle_live_smoke": {
            "name": "get_news_bundle_live_smoke",
            "provider": "newsapi",
            "required_env_key_groups": [["HALO_SWING_NEWS_API_KEY", "NEWS_API_KEY"]],
            "command": (
                "PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness "
                "get_news_bundle --input-json '{\"topic\":\"macro\"}' --no-audit"
            ),
            "expected_live_contract": "news_source_policy_contract",
            "expected_live_checks": [
                "live_data_boundary_declared",
                "network_call_declared",
                "secret_values_not_returned",
            ],
            "network_call_policy": "only_when_matching_api_key_selects_live_provider",
            "mutates_local_state": False,
            "hermes_runtime_started": False,
            "telegram_send_call": False,
            "order_submission": False,
            "secret_values_returned": False,
        },
    }
    return commands[name]


def expected_provider_setup_actions(
    *,
    market_configured_env_keys: list[str],
    macro_configured_env_keys: list[str],
    news_configured_env_keys: list[str],
) -> dict[str, dict[str, Any]]:
    provider_rows = [
        (
            "market",
            "polygon",
            market_configured_env_keys,
            "POLYGON_API_KEY",
            ["HALO_SWING_MARKET_DATA_API_KEY", "POLYGON_API_KEY"],
            "POLYGON_API_KEY=your_polygon_key",
            "get_market_snapshot_live_smoke",
        ),
        (
            "macro",
            "fred",
            macro_configured_env_keys,
            "FRED_API_KEY",
            [
                "HALO_SWING_MACRO_API_KEY",
                "HALO_SWING_FRED_API_KEY",
                "FRED_API_KEY",
            ],
            "FRED_API_KEY=your_fred_key",
            "get_macro_snapshot_live_smoke",
        ),
        (
            "news",
            "newsapi",
            news_configured_env_keys,
            "NEWS_API_KEY",
            ["HALO_SWING_NEWS_API_KEY", "NEWS_API_KEY"],
            "NEWS_API_KEY=your_newsapi_key",
            "get_news_bundle_live_smoke",
        ),
    ]
    return {
        provider_family: {
            "provider": provider,
            "configured": bool(configured_env_keys),
            "configured_env_keys": configured_env_keys,
            "preferred_env_key": preferred_env_key,
            "accepted_env_keys": accepted_env_keys,
            "setup_status": "ready" if configured_env_keys else "pending",
            "next_setup_action": (
                "run_provider_smoke"
                if configured_env_keys
                else "fill_preferred_env_key"
            ),
            "dotenv_target_path": ".env",
            "example": example,
            "smoke_command_name": smoke_command_name,
            "smoke_command": expected_provider_smoke_command(smoke_command_name),
            "network_call": False,
            "mutates_local_state": False,
            "secret_values_returned": False,
        }
        for (
            provider_family,
            provider,
            configured_env_keys,
            preferred_env_key,
            accepted_env_keys,
            example,
            smoke_command_name,
        ) in provider_rows
    }


def expected_provider_smoke_plan(
    *,
    market_configured_env_keys: list[str],
    macro_configured_env_keys: list[str],
    news_configured_env_keys: list[str],
    ready_to_run_live_smoke: bool,
) -> dict[str, Any]:
    provider_setup_actions = expected_provider_setup_actions(
        market_configured_env_keys=market_configured_env_keys,
        macro_configured_env_keys=macro_configured_env_keys,
        news_configured_env_keys=news_configured_env_keys,
    )
    provider_smokes = [
        {
            "provider_family": provider_family,
            "provider": action["provider"],
            "status": "ready" if action["configured"] else "blocked",
            "preferred_env_key": action["preferred_env_key"],
            "next_setup_action": action["next_setup_action"],
            "smoke_command_name": action["smoke_command"]["name"],
            "command": action["smoke_command"]["command"],
            "expected_live_contract": action["smoke_command"][
                "expected_live_contract"
            ],
            "expected_live_checks": action["smoke_command"]["expected_live_checks"],
            "network_call_policy": action["smoke_command"]["network_call_policy"],
            "mutates_local_state": False,
            "secret_values_returned": False,
        }
        for provider_family, action in provider_setup_actions.items()
    ]
    ready_provider_smoke_count = sum(
        1 for provider_smoke in provider_smokes if provider_smoke["status"] == "ready"
    )
    return {
        "schema_version": "live_data_provider_smoke_plan.v1",
        "provider_smokes": provider_smokes,
        "provider_smoke_count": 3,
        "ready_provider_smoke_count": ready_provider_smoke_count,
        "blocked_provider_smoke_count": 3 - ready_provider_smoke_count,
        "one_shot_pipeline_smoke": {
            "name": "run_api_key_pipeline_smoke",
            "status": "ready" if ready_to_run_live_smoke else "blocked",
            "command": expected_pipeline_smoke_command()["command"],
            "network_call": True,
            "network_call_policy": "only_when_matching_api_key_selects_live_provider",
            "mutates_local_state": False,
            "secret_values_returned": False,
        },
        "network_call": False,
        "mutates_local_state": False,
        "secret_values_returned": False,
    }


def expected_api_key_requirements_summary(
    *,
    status: str,
    market_configured_env_keys: list[str],
    macro_configured_env_keys: list[str],
    news_configured_env_keys: list[str],
    configured_provider_families: list[str],
    missing_provider_families: list[str],
) -> dict[str, Any]:
    provider_setup_actions = expected_provider_setup_actions(
        market_configured_env_keys=market_configured_env_keys,
        macro_configured_env_keys=macro_configured_env_keys,
        news_configured_env_keys=news_configured_env_keys,
    )
    configured_env_keys = []
    provider_requirements = {}
    for provider_family, action in provider_setup_actions.items():
        configured_env_keys.extend(action["configured_env_keys"])
        provider_requirements[provider_family] = {
            "provider": action["provider"],
            "configured": action["configured"],
            "configured_env_keys": action["configured_env_keys"],
            "preferred_env_key": action["preferred_env_key"],
            "accepted_env_keys": action["accepted_env_keys"],
            "setup_status": action["setup_status"],
            "next_setup_action": action["next_setup_action"],
            "smoke_command_name": action["smoke_command_name"],
            "network_call": False,
            "mutates_local_state": False,
            "secret_values_returned": False,
        }
    return {
        "schema_version": "api_key_pipeline_api_key_requirements_summary.v1",
        "status": status,
        "required_env_keys": ["POLYGON_API_KEY", "FRED_API_KEY", "NEWS_API_KEY"],
        "configured_env_keys": configured_env_keys,
        "missing_provider_families": missing_provider_families,
        "configured_provider_families": configured_provider_families,
        "provider_requirements": provider_requirements,
        "network_call": False,
        "mutates_local_state": False,
        "secret_values_returned": False,
    }


def expected_api_key_command_summary(
    *,
    status: str,
    target_path: Path,
    market_configured_env_keys: list[str],
    macro_configured_env_keys: list[str],
    news_configured_env_keys: list[str],
    ready_to_run_live_smoke: bool,
) -> dict[str, Any]:
    provider_smoke_plan = expected_provider_smoke_plan(
        market_configured_env_keys=market_configured_env_keys,
        macro_configured_env_keys=macro_configured_env_keys,
        news_configured_env_keys=news_configured_env_keys,
        ready_to_run_live_smoke=ready_to_run_live_smoke,
    )
    provider_smoke_commands = [
        {
            "provider_family": provider_smoke["provider_family"],
            "provider": provider_smoke["provider"],
            "status": provider_smoke["status"],
            "smoke_command_name": provider_smoke["smoke_command_name"],
            "command": provider_smoke["command"],
            "network_call_policy": provider_smoke["network_call_policy"],
            "mutates_local_state": False,
            "secret_values_returned": False,
        }
        for provider_smoke in provider_smoke_plan["provider_smokes"]
    ]
    next_provider_smoke = next(
        (
            provider_smoke
            for provider_smoke in provider_smoke_commands
            if provider_smoke["status"] == "ready"
        ),
        None,
    )
    return {
        "schema_version": "api_key_pipeline_api_key_command_summary.v1",
        "status": status,
        "copy_dotenv_command": expected_dotenv_file_status(target_path)[
            "copy_command"
        ],
        "next_smoke_command": (
            expected_pipeline_smoke_command()
            if ready_to_run_live_smoke
            else expected_api_key_status_command()
        ),
        "one_shot_pipeline_smoke": {
            "name": "run_api_key_pipeline_smoke",
            "command": expected_pipeline_smoke_command()["command"],
            "network_call": True,
            "network_call_policy": "only_when_matching_api_key_selects_live_provider",
            "mutates_local_state": False,
            "secret_values_returned": False,
        },
        "next_provider_smoke": next_provider_smoke,
        "next_provider_smoke_command_name": (
            next_provider_smoke["smoke_command_name"]
            if next_provider_smoke
            else None
        ),
        "provider_smoke_commands": provider_smoke_commands,
        "provider_smoke_command_count": 3,
        "network_call": False,
        "mutates_local_state": False,
        "secret_values_returned": False,
    }


def expected_api_key_operator_checklist(
    *,
    status: str,
    current_step: str,
    target_path: Path,
    market_configured_env_keys: list[str],
    macro_configured_env_keys: list[str],
    news_configured_env_keys: list[str],
    configured_provider_families: list[str],
    missing_provider_families: list[str],
    ready_to_run_live_smoke: bool,
    provider_recovery_checklist: dict[str, Any] | None = None,
) -> dict[str, Any]:
    command_summary = expected_api_key_command_summary(
        status=status,
        target_path=target_path,
        market_configured_env_keys=market_configured_env_keys,
        macro_configured_env_keys=macro_configured_env_keys,
        news_configured_env_keys=news_configured_env_keys,
        ready_to_run_live_smoke=ready_to_run_live_smoke,
    )
    requirements_summary = expected_api_key_requirements_summary(
        status=status,
        market_configured_env_keys=market_configured_env_keys,
        macro_configured_env_keys=macro_configured_env_keys,
        news_configured_env_keys=news_configured_env_keys,
        configured_provider_families=configured_provider_families,
        missing_provider_families=missing_provider_families,
    )
    copy_command = command_summary["copy_dotenv_command"]
    dotenv_setup_ready = (
        ready_to_run_live_smoke or copy_command["required"] is not True
    )
    steps = [
        {
            "name": "prepare_dotenv",
            "status": "ready" if dotenv_setup_ready else "pending",
            "command": copy_command["command"],
            "mutates_local_state": copy_command["mutates_local_state"],
            "network_call": False,
            "secret_values_returned": False,
        },
        {
            "name": "fill_live_data_api_keys",
            "status": "ready" if not missing_provider_families else "pending",
            "required_env_keys": requirements_summary["required_env_keys"],
            "configured_env_keys": requirements_summary["configured_env_keys"],
            "missing_provider_families": missing_provider_families,
            "provider_requirements": requirements_summary["provider_requirements"],
            "network_call": False,
            "mutates_local_state": False,
            "secret_values_returned": False,
        },
        {
            "name": "run_provider_smokes",
            "status": "ready" if ready_to_run_live_smoke else "blocked",
            "provider_smoke_commands": command_summary["provider_smoke_commands"],
            "provider_smoke_command_count": 3,
            "next_provider_smoke": command_summary["next_provider_smoke"],
            "next_provider_smoke_command_name": command_summary[
                "next_provider_smoke_command_name"
            ],
            "network_call": True,
            "network_call_policy": "only_when_matching_api_key_selects_live_provider",
            "mutates_local_state": False,
            "secret_values_returned": False,
        },
        {
            "name": "run_api_key_pipeline_smoke",
            "status": "ready" if ready_to_run_live_smoke else "blocked",
            "command": command_summary["one_shot_pipeline_smoke"]["command"],
            "network_call": True,
            "network_call_policy": "only_when_matching_api_key_selects_live_provider",
            "mutates_local_state": False,
            "secret_values_returned": False,
        },
    ]
    blocking_step_names = [
        str(step["name"]) for step in steps if step.get("status") != "ready"
    ]
    ready_step_names = [
        str(step["name"]) for step in steps if step.get("status") == "ready"
    ]
    next_blocking_action = next(
        (step for step in steps if step.get("status") != "ready"),
        None,
    )
    provider_recovery_checklist = provider_recovery_checklist or {
        "schema_version": "api_key_provider_recovery_checklist.v1",
        "status": "ok",
        "provider_error_count": 0,
        "provider_recovery_smoke_count": 0,
        "item_count": 0,
        "items": [],
        "secret_values_returned": False,
    }
    provider_recovery_items = provider_recovery_checklist["items"]
    next_provider_recovery_action = (
        provider_recovery_items[0] if provider_recovery_items else None
    )
    provider_recovery_required = bool(provider_recovery_items)
    return {
        "schema_version": "api_key_pipeline_operator_checklist.v1",
        "status": "conflict" if provider_recovery_required else status,
        "current_step": (
            "recover_failed_providers"
            if provider_recovery_required
            else current_step
        ),
        "provider_recovery_status": provider_recovery_checklist["status"],
        "provider_recovery_required": provider_recovery_required,
        "provider_recovery_item_count": len(provider_recovery_items),
        "next_provider_recovery_action": next_provider_recovery_action,
        "provider_recovery_checklist": provider_recovery_checklist,
        "ready": not blocking_step_names,
        "ready_step_names": ready_step_names,
        "ready_step_count": len(ready_step_names),
        "blocking_step_names": blocking_step_names,
        "blocking_step_count": len(blocking_step_names),
        "next_blocking_step": blocking_step_names[0] if blocking_step_names else None,
        "next_blocking_action": next_blocking_action,
        "steps": steps,
        "step_count": 4,
        "network_call": False,
        "mutates_local_state": False,
        "secret_values_returned": False,
    }


EXPECTED_MISSING_CREDENTIAL_STATUS_KEYS = [
    "configured",
    "provider",
    "credentials_path",
    "credential_policy",
    "secret_values_returned",
    "passphrase_persisted",
    "live_data_required",
]
EXPECTED_CONFIGURED_CREDENTIAL_STATUS_KEYS = [
    "configured",
    "provider",
    "credentials_path",
    "api_key_hint",
    "created_at",
    "updated_at",
    "kdf",
    "cipher",
    "credential_policy",
    "secret_values_returned",
    "passphrase_persisted",
    "live_data_required",
]
EXPECTED_SAFE_CREDENTIAL_KDF_KEYS = ["name", "iterations"]
EXPECTED_SAFE_CREDENTIAL_CIPHER_KEYS = ["name"]
EXPECTED_BINANCE_CREDENTIAL_POLICY_KEYS = [
    "schema_version",
    "provider",
    "testnet_first_required",
    "trade_permission_required",
    "withdraw_permission_allowed",
    "required_permissions",
    "forbidden_permissions",
    "operator_attestation_required",
    "permissions_verified_by_tool",
    "permission_verification",
    "secret_storage",
    "passphrase_handling",
    "passphrase_persistence",
    "secret_values_returned",
]
EXPECTED_DEFAULT_LIVE_DATA_MISSING = [
    "market_ohlcv_api_key",
    "macro_api_key",
    "news_api_key",
]


def clear_readiness_env(monkeypatch) -> None:
    for key in READINESS_ENV_KEYS:
        monkeypatch.delenv(key, raising=False)
    clear_local_env_cache()
    get_settings.cache_clear()


@pytest.fixture(autouse=True)
def clear_settings_cache_after_readiness_env_tests() -> None:
    get_settings.cache_clear()
    clear_local_env_cache()
    yield
    clear_local_env_cache()
    get_settings.cache_clear()


def test_integration_readiness_reports_blocked_defaults(monkeypatch) -> None:
    clear_readiness_env(monkeypatch)

    payload = get_integration_readiness(binance_credentials_path="/missing/credentials.json")

    assert payload["status"] == "blocked"
    assert payload["next_actions"] == [
        "hermes: provide hermes_config_path, hermes_mcp_config_registration",
        "telegram: provide telegram_bot_token_or_gateway",
        "migration: provide explicit_MIGRATION_GO",
        "repository: provide MIGRATION_GO, REPOSITORY_GO",
        (
            "binance_testnet_read_only: provide encrypted_binance_testnet_credentials, "
            "manual_credential_passphrase_at_smoke_time"
        ),
        (
            "live_order_submission: provide explicit_live_order_approval, "
            "HALO_SWING_BINANCE_ENABLE_LIVE_TRADING=true, encrypted_binance_credentials, "
            "manual_credential_passphrase_at_order_time, "
            "binance_console_trade_only_no_withdraw_attestation"
        ),
        (
            "live_data: provide market_ohlcv_api_key, "
            "macro_api_key, news_api_key"
        ),
    ]
    assert payload["gates"]["hermes"]["missing"] == [
        "hermes_config_path",
        "hermes_mcp_config_registration",
    ]
    hermes_gate = payload["gates"]["hermes"]
    assert hermes_gate["evidence"]["schema_version"] == "hermes_mcp_config_readiness.v1"
    assert hermes_gate["evidence"]["mcp_server_name"] == "halo_swing_mcp"
    assert hermes_gate["evidence"]["transport"] == "stdio"
    assert hermes_gate["evidence"]["runtime_started"] is False
    assert hermes_gate["evidence"]["network_call"] is False
    assert payload["gates"]["telegram"]["missing"] == ["telegram_bot_token_or_gateway"]
    telegram_gate = payload["gates"]["telegram"]
    assert telegram_gate["evidence"]["schema_version"] == "telegram_delivery_readiness.v1"
    assert telegram_gate["evidence"]["delivery_preview_available"] is True
    assert telegram_gate["evidence"]["send_call"] is False
    assert telegram_gate["evidence"]["network_call"] is False
    assert telegram_gate["evidence"]["credential_storage_added"] is False
    assert payload["gates"]["migration"]["missing"] == ["explicit_MIGRATION_GO"]
    assert payload["gates"]["repository"]["missing"] == ["MIGRATION_GO", "REPOSITORY_GO"]
    assert "encrypted_binance_testnet_credentials" in payload["gates"]["binance_testnet_read_only"]["missing"]
    assert (
        "manual_credential_passphrase_at_smoke_time"
        in payload["gates"]["binance_testnet_read_only"]["missing"]
    )
    live_order_gate = payload["gates"]["live_order_submission"]
    assert "explicit_live_order_approval" in live_order_gate["missing"]
    assert "HALO_SWING_BINANCE_ENABLE_LIVE_TRADING=true" in live_order_gate["missing"]
    assert "encrypted_binance_credentials" in live_order_gate["missing"]
    assert "manual_credential_passphrase_at_order_time" in live_order_gate["missing"]
    assert "binance_console_trade_only_no_withdraw_attestation" in live_order_gate["missing"]
    assert live_order_gate["evidence"]["order_submission"] is False
    assert live_order_gate["evidence"]["network_call"] is False
    assert payload["gates"]["live_data"]["missing"] == EXPECTED_DEFAULT_LIVE_DATA_MISSING
    assert payload["gates"]["live_data"]["evidence"]["schema_version"] == (
        "live_data_source_readiness.v1"
    )
    assert payload["gates"]["live_data"]["evidence"]["live_adapter_added"] is True
    assert payload["gates"]["live_data"]["evidence"]["network_call"] is False
    assert payload["live_data_required"] is False


def test_integration_readiness_payload_schema_is_stable(monkeypatch) -> None:
    clear_readiness_env(monkeypatch)

    payload = get_integration_readiness(binance_credentials_path="/missing/credentials.json")

    assert list(payload) == EXPECTED_READINESS_PAYLOAD_KEYS
    assert list(payload["gates"]) == EXPECTED_READINESS_GATE_NAMES
    for gate_name in EXPECTED_READINESS_GATE_NAMES:
        gate = payload["gates"][gate_name]
        assert list(gate) == EXPECTED_READINESS_GATE_KEYS
        assert list(gate["evidence"]) == EXPECTED_READINESS_EVIDENCE_KEYS_BY_GATE[
            gate_name
        ]

    for gate_name in ("binance_testnet_read_only", "live_order_submission"):
        credentials = payload["gates"][gate_name]["evidence"]["credentials"]
        assert list(credentials) == EXPECTED_MISSING_CREDENTIAL_STATUS_KEYS
        assert (
            list(credentials["credential_policy"])
            == EXPECTED_BINANCE_CREDENTIAL_POLICY_KEYS
        )
        assert credentials["secret_values_returned"] is False
        assert credentials["passphrase_persisted"] is False
        assert credentials["live_data_required"] is False


def test_integration_setup_checklist_reports_blocked_defaults(monkeypatch) -> None:
    clear_readiness_env(monkeypatch)

    payload = get_integration_setup_checklist()
    env_requirements = {
        requirement["section"]: requirement
        for requirement in payload["env_requirements"]
    }
    command_names = {command["name"] for command in payload["local_commands"]}
    live_smoke_commands = {
        command["name"]: command
        for command in payload["live_data_smoke_commands"]
    }
    live_data_setup_summary = payload["live_data_setup_summary"]

    assert payload["schema_version"] == "integration_setup_checklist.v1"
    assert payload["status"] == "blocked"
    assert payload["readiness_status"] == "blocked"
    assert payload["secret_values_returned"] is False
    assert payload["network_call"] is False
    assert payload["send_call"] is False
    assert payload["order_submission"] is False
    assert payload["offline_guardrails"] == {
        "network_call": False,
        "hermes_runtime_started": False,
        "telegram_send_call": False,
        "order_submission": False,
        "secret_values_returned": False,
        "dotenv_mutation": False,
        "credential_file_write": False,
    }
    assert env_requirements["hermes"]["env_keys"] == [
        "HALO_SWING_HERMES_CONFIG_PATH",
        "HALO_SWING_HERMES_MCP_CONFIG_REGISTERED",
    ]
    assert env_requirements["telegram"]["secret"] is True
    assert env_requirements["live_data"]["secret"] is True
    assert env_requirements["binance_credentials"]["configured"] is False
    assert env_requirements["binance_credentials"]["missing"] == [
        "encrypted_binance_credentials"
    ]
    assert env_requirements["binance_read_only_smoke"]["configured"] is False
    assert env_requirements["binance_live_order_readiness"]["configured"] is False
    assert live_data_setup_summary == {
        "schema_version": "live_data_setup_summary.v1",
        "status": "blocked",
        "ready_to_run_live_smoke": False,
        "api_key_status": "blocked",
        "provider_route_status": "blocked",
        "configured_provider_families": [],
        "provider_family_summary": {
            "required_provider_families": ["market", "macro", "news"],
            "configured_provider_families": [],
            "missing_provider_families": ["market", "macro", "news"],
            "configured_count": 0,
            "required_count": 3,
            "ready_to_run_live_smoke": False,
            "network_call": False,
            "mutates_local_state": False,
            "secret_values_returned": False,
        },
        "provider_setup_actions": expected_provider_setup_actions(
            market_configured_env_keys=[],
            macro_configured_env_keys=[],
            news_configured_env_keys=[],
        ),
        "provider_smoke_plan": expected_provider_smoke_plan(
            market_configured_env_keys=[],
            macro_configured_env_keys=[],
            news_configured_env_keys=[],
            ready_to_run_live_smoke=False,
        ),
        "missing": [
            "market_ohlcv_api_key",
            "macro_api_key",
            "news_api_key",
        ],
        "provider_factory": "get_market_data_provider",
        "selected_provider_classes": ["ReplayMarketDataProvider"],
        "provider_route_summary": {
            "schema_version": "live_data_provider_route.v1",
            "status": "blocked",
            "provider_factory": "get_market_data_provider",
            "selected_provider_classes": ["ReplayMarketDataProvider"],
            "missing": [
                "market_ohlcv_api_key",
                "macro_api_key",
                "news_api_key",
            ],
            "network_call": False,
            "secret_values_returned": False,
        },
        "dotenv_template": {
            "schema_version": "live_data_dotenv_template.v1",
            "target_path": ".env",
            "source_path": ".env.example",
            "entries": [
                {
                    "provider_family": "market",
                    "provider": "polygon",
                    "preferred_env_key": "POLYGON_API_KEY",
                    "accepted_env_keys": [
                        "HALO_SWING_MARKET_DATA_API_KEY",
                        "POLYGON_API_KEY",
                    ],
                    "example": "POLYGON_API_KEY = your_polygon_key",
                    "secret": True,
                },
                {
                    "provider_family": "macro",
                    "provider": "fred",
                    "preferred_env_key": "FRED_API_KEY",
                    "accepted_env_keys": [
                        "HALO_SWING_MACRO_API_KEY",
                        "HALO_SWING_FRED_API_KEY",
                        "FRED_API_KEY",
                    ],
                    "example": "FRED_API_KEY = your_fred_key",
                    "secret": True,
                },
                {
                    "provider_family": "news",
                    "provider": "newsapi",
                    "preferred_env_key": "NEWS_API_KEY",
                    "accepted_env_keys": [
                        "HALO_SWING_NEWS_API_KEY",
                        "NEWS_API_KEY",
                    ],
                    "example": "NEWS_API_KEY = your_newsapi_key",
                    "secret": True,
                },
            ],
            "network_call": False,
            "mutates_local_state": False,
            "secret_values_returned": False,
        },
        "dotenv_file_status": expected_dotenv_file_status(ROOT / ".env"),
        "live_data_setup_steps": expected_live_data_setup_steps(
            target_path=ROOT / ".env",
            configured_provider_families=[],
            missing_provider_families=["market", "macro", "news"],
            ready_to_run_live_smoke=False,
        ),
        "next_operator_action": expected_next_operator_action(
            target_path=ROOT / ".env",
            configured_provider_families=[],
            missing_provider_families=["market", "macro", "news"],
            ready_to_run_live_smoke=False,
        ),
        "one_shot_smoke_command": expected_pipeline_smoke_command(),
        "next_smoke_command": {
            "name": "get_live_data_api_key_status",
            "purpose": (
                "show live data API-key readiness and configured alias names "
                "without network calls or secret values"
            ),
            "command": (
                "PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness "
                "get_live_data_api_key_status --no-audit"
            ),
            "network_call": False,
            "mutates_local_state": False,
            "secret_values_returned": False,
        },
        "network_call": False,
        "mutates_local_state": False,
        "secret_values_returned": False,
    }
    assert command_names == {
        "save_binance_credentials",
        "get_integration_readiness",
        "get_integration_setup_checklist",
        "get_live_data_api_key_status",
        "get_live_data_provider_route",
        "validate_live_data_smoke_result",
        "run_live_data_smoke",
        "run_integration_smoke",
        "run_live_signal_workflow_smoke",
        "run_live_recording_smoke",
        "run_api_key_pipeline_smoke",
    }
    assert set(live_smoke_commands) == {
        "get_market_snapshot_live_smoke",
        "get_macro_snapshot_live_smoke",
        "get_news_bundle_live_smoke",
    }
    for command in live_smoke_commands.values():
        assert command["command"].startswith(
            "PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness "
        )
        assert command["command"].endswith("--no-audit")
        assert command["network_call_policy"] == (
            "only_when_matching_api_key_selects_live_provider"
        )
        assert command["mutates_local_state"] is False
        assert command["hermes_runtime_started"] is False
        assert command["telegram_send_call"] is False
        assert command["order_submission"] is False
        assert command["secret_values_returned"] is False
    assert live_smoke_commands["get_market_snapshot_live_smoke"][
        "expected_live_contract"
    ] == "market_snapshot_contract"
    assert live_smoke_commands["get_macro_snapshot_live_smoke"][
        "expected_live_contract"
    ] == "macro_filter_contract"
    assert live_smoke_commands["get_news_bundle_live_smoke"][
        "expected_live_contract"
    ] == "news_source_policy_contract"
    assert "POLYGON_API_KEY" in live_smoke_commands[
        "get_market_snapshot_live_smoke"
    ]["required_env_key_groups"][0]
    assert "FRED_API_KEY" in live_smoke_commands[
        "get_macro_snapshot_live_smoke"
    ]["required_env_key_groups"][0]
    assert "NEWS_API_KEY" in live_smoke_commands[
        "get_news_bundle_live_smoke"
    ]["required_env_key_groups"][0]
    assert payload["durable_gate_requirements"] == [
        {
            "gate": "migration",
            "required_approval": "MIGRATION_GO",
            "dotenv_supported": False,
            "configured": False,
            "missing": ["explicit_MIGRATION_GO"],
        },
        {
            "gate": "repository",
            "required_approval": "REPOSITORY_GO",
            "dotenv_supported": False,
            "configured": False,
            "missing": ["MIGRATION_GO", "REPOSITORY_GO"],
        },
    ]


def test_live_data_api_key_status_reports_blocked_defaults(monkeypatch) -> None:
    clear_readiness_env(monkeypatch)

    payload = get_live_data_api_key_status()

    assert payload["schema_version"] == "live_data_api_key_status.v1"
    assert payload["status"] == "blocked"
    assert payload["missing"] == [
        "market_ohlcv_api_key",
        "macro_api_key",
        "news_api_key",
    ]
    assert payload["provider_family_summary"] == {
        "required_provider_families": ["market", "macro", "news"],
        "configured_provider_families": [],
        "missing_provider_families": ["market", "macro", "news"],
        "configured_count": 0,
        "required_count": 3,
        "ready_to_run_live_smoke": False,
        "network_call": False,
        "mutates_local_state": False,
        "secret_values_returned": False,
    }
    assert payload["provider_smoke_plan"] == expected_provider_smoke_plan(
        market_configured_env_keys=[],
        macro_configured_env_keys=[],
        news_configured_env_keys=[],
        ready_to_run_live_smoke=False,
    )
    assert payload["network_call"] is False
    assert payload["mutates_local_state"] is False
    assert payload["secret_values_returned"] is False
    assert payload["dotenv_file_status"] == expected_dotenv_file_status(
        ROOT / ".env"
    )
    assert payload["live_data_setup_steps"] == expected_live_data_setup_steps(
        target_path=ROOT / ".env",
        configured_provider_families=[],
        missing_provider_families=["market", "macro", "news"],
        ready_to_run_live_smoke=False,
    )
    assert payload["next_operator_action"] == expected_next_operator_action(
        target_path=ROOT / ".env",
        configured_provider_families=[],
        missing_provider_families=["market", "macro", "news"],
        ready_to_run_live_smoke=False,
    )
    assert payload["hermes_runtime_started"] is False
    assert payload["telegram_send_call"] is False
    assert payload["order_submission"] is False
    assert payload["live_mode_required"] is False
    assert payload["one_shot_smoke_command"]["name"] == "run_api_key_pipeline_smoke"
    assert payload["one_shot_smoke_command"]["network_call"] is True
    assert payload["dotenv_template"]["target_path"] == ".env"
    assert payload["dotenv_template"]["source_path"] == ".env.example"
    assert payload["dotenv_template"]["entries"][0]["example"] == (
        "POLYGON_API_KEY = your_polygon_key"
    )
    assert payload["dotenv_template"]["entries"][1]["accepted_env_keys"] == [
        "HALO_SWING_MACRO_API_KEY",
        "HALO_SWING_FRED_API_KEY",
        "FRED_API_KEY",
    ]
    assert payload["dotenv_template"]["network_call"] is False
    assert payload["dotenv_template"]["mutates_local_state"] is False
    assert payload["dotenv_template"]["secret_values_returned"] is False
    assert payload["providers"]["market"]["accepted_env_keys"] == [
        "HALO_SWING_MARKET_DATA_API_KEY",
        "POLYGON_API_KEY",
    ]
    assert payload["providers"]["macro"]["accepted_env_keys"] == [
        "HALO_SWING_MACRO_API_KEY",
        "HALO_SWING_FRED_API_KEY",
        "FRED_API_KEY",
    ]
    assert payload["providers"]["news"]["accepted_env_keys"] == [
        "HALO_SWING_NEWS_API_KEY",
        "NEWS_API_KEY",
    ]
    expected_provider_setup = {
        "market": ("POLYGON_API_KEY", "POLYGON_API_KEY=your_polygon_key"),
        "macro": ("FRED_API_KEY", "FRED_API_KEY=your_fred_key"),
        "news": ("NEWS_API_KEY", "NEWS_API_KEY=your_newsapi_key"),
    }
    for provider_family, provider_status in payload["providers"].items():
        preferred_env_key, example = expected_provider_setup[provider_family]
        assert provider_status["configured"] is False
        assert provider_status["configured_env_keys"] == []
        assert provider_status["preferred_env_key"] == preferred_env_key
        assert provider_status["setup_status"] == "pending"
        assert provider_status["next_setup_action"] == "fill_preferred_env_key"
        assert provider_status["dotenv_target_path"] == ".env"
        assert provider_status["example"] == example
        assert provider_status["auto_selects_live_provider"] is False
        assert provider_status["live_mode_required"] is False
        assert provider_status["network_call"] is False
        assert provider_status["mutates_local_state"] is False
        assert provider_status["secret_values_returned"] is False
        assert provider_status["smoke_command"]["network_call_policy"] == (
            "only_when_matching_api_key_selects_live_provider"
        )


def test_live_data_api_key_status_reports_runtime_dotenv_precedence(
    monkeypatch,
) -> None:
    clear_readiness_env(monkeypatch)

    payload = get_live_data_api_key_status()

    assert payload["dotenv"]["precedence"] == [
        "exported environment variables",
        "launch-directory .env",
        "repo-root .env",
    ]
    assert payload["dotenv"]["mutation"] is False


def test_live_data_api_key_status_accepts_repo_dotenv_aliases_without_secret_values(
    tmp_path: Path,
    monkeypatch,
) -> None:
    clear_readiness_env(monkeypatch)
    repo_dir = tmp_path / "repo"
    run_dir = tmp_path / "runner"
    repo_dir.mkdir()
    run_dir.mkdir()
    repo_env = repo_dir / ".env"
    repo_example = repo_dir / ".env.example"
    monkeypatch.setattr(local_env, "REPO_ROOT_ENV_PATH", repo_env)
    monkeypatch.chdir(run_dir)
    monkeypatch.delenv("HALO_SWING_DISABLE_DOTENV", raising=False)
    secret_env = {
        "POLYGON_API_KEY": "polygon-local-secret-key",
        "HALO_SWING_FRED_API_KEY": "fred-local-secret-key",
        "NEWS_API_KEY": "news-local-secret-key",
    }
    repo_env.write_text(
        "\n".join(f"{key}={value}" for key, value in secret_env.items()),
        encoding="utf-8",
    )
    repo_example.write_text("POLYGON_API_KEY=\n", encoding="utf-8")
    clear_local_env_cache()
    get_settings.cache_clear()

    payload = get_live_data_api_key_status()
    serialized = json.dumps(payload, sort_keys=True)

    assert payload["status"] == "ready"
    assert payload["missing"] == []
    assert payload["provider_family_summary"] == {
        "required_provider_families": ["market", "macro", "news"],
        "configured_provider_families": ["market", "macro", "news"],
        "missing_provider_families": [],
        "configured_count": 3,
        "required_count": 3,
        "ready_to_run_live_smoke": True,
        "network_call": False,
        "mutates_local_state": False,
        "secret_values_returned": False,
    }
    assert payload["provider_smoke_plan"] == expected_provider_smoke_plan(
        market_configured_env_keys=["POLYGON_API_KEY"],
        macro_configured_env_keys=["HALO_SWING_FRED_API_KEY"],
        news_configured_env_keys=["NEWS_API_KEY"],
        ready_to_run_live_smoke=True,
    )
    assert payload["providers"]["market"]["configured"] is True
    assert payload["providers"]["market"]["configured_env_keys"] == ["POLYGON_API_KEY"]
    assert payload["providers"]["market"]["preferred_env_key"] == "POLYGON_API_KEY"
    assert payload["providers"]["market"]["setup_status"] == "ready"
    assert (
        payload["providers"]["market"]["next_setup_action"] == "run_provider_smoke"
    )
    assert payload["providers"]["market"]["example"] == (
        "POLYGON_API_KEY=your_polygon_key"
    )
    assert payload["providers"]["macro"]["configured"] is True
    assert payload["providers"]["macro"]["configured_env_keys"] == [
        "HALO_SWING_FRED_API_KEY"
    ]
    assert payload["providers"]["macro"]["preferred_env_key"] == "FRED_API_KEY"
    assert payload["providers"]["macro"]["setup_status"] == "ready"
    assert payload["providers"]["macro"]["next_setup_action"] == "run_provider_smoke"
    assert payload["providers"]["macro"]["dotenv_target_path"] == ".env"
    assert payload["providers"]["news"]["configured"] is True
    assert payload["providers"]["news"]["configured_env_keys"] == ["NEWS_API_KEY"]
    assert payload["providers"]["news"]["preferred_env_key"] == "NEWS_API_KEY"
    assert payload["providers"]["news"]["setup_status"] == "ready"
    assert payload["providers"]["news"]["next_setup_action"] == "run_provider_smoke"
    assert payload["dotenv_template"]["target_path"] == ".env"
    assert payload["dotenv_template"]["entries"][2]["example"] == (
        "NEWS_API_KEY = your_newsapi_key"
    )
    assert payload["dotenv_template"]["secret_values_returned"] is False
    assert payload["dotenv_file_status"] == expected_dotenv_file_status(repo_env)
    assert payload["live_data_setup_steps"] == expected_live_data_setup_steps(
        target_path=repo_env,
        configured_provider_families=["market", "macro", "news"],
        missing_provider_families=[],
        ready_to_run_live_smoke=True,
    )
    assert payload["next_operator_action"] == expected_next_operator_action(
        target_path=repo_env,
        configured_provider_families=["market", "macro", "news"],
        missing_provider_families=[],
        ready_to_run_live_smoke=True,
    )
    assert payload["dotenv"]["supported"] is True
    assert payload["dotenv"]["disabled"] is False
    assert payload["dotenv"]["mutation"] is False
    assert payload["network_call"] is False
    assert payload["secret_values_returned"] is False
    for key, value in secret_env.items():
        assert key in serialized
        assert value not in serialized


def test_live_data_api_key_status_treats_exported_keys_as_ready_without_dotenv_file(
    tmp_path: Path,
    monkeypatch,
) -> None:
    clear_readiness_env(monkeypatch)
    repo_env = tmp_path / ".env"
    repo_env.with_name(".env.example").write_text(
        "POLYGON_API_KEY=\nFRED_API_KEY=\nNEWS_API_KEY=\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(local_env, "REPO_ROOT_ENV_PATH", repo_env)
    monkeypatch.setenv("POLYGON_API_KEY", "polygon-exported-secret")
    monkeypatch.setenv("FRED_API_KEY", "fred-exported-secret")
    monkeypatch.setenv("NEWS_API_KEY", "news-exported-secret")
    clear_local_env_cache()
    get_settings.cache_clear()

    payload = get_live_data_api_key_status()
    serialized = json.dumps(payload, sort_keys=True)
    setup_steps = payload["live_data_setup_steps"]
    prepare_dotenv_step = setup_steps["steps"][0]

    assert payload["status"] == "ready"
    assert payload["missing"] == []
    assert payload["dotenv_file_status"]["target_exists"] is False
    assert payload["dotenv_file_status"]["copy_required"] is True
    assert prepare_dotenv_step["name"] == "prepare_dotenv"
    assert prepare_dotenv_step["status"] == "ready"
    assert setup_steps["next_step"] == "run_provider_smokes"
    assert payload["next_operator_action"]["name"] == "run_provider_smokes"
    assert payload["next_operator_action"]["status"] == "ready"
    assert payload["next_operator_action"]["provider_smoke_count"] == 3
    assert (
        payload["next_operator_action"]["next_provider_smoke_command_name"]
        == "get_market_snapshot_live_smoke"
    )
    assert payload["next_operator_action"]["network_call"] is True
    assert payload["next_operator_action"]["secret_values_returned"] is False
    assert "polygon-exported-secret" not in serialized
    assert "fred-exported-secret" not in serialized
    assert "news-exported-secret" not in serialized


def test_run_api_key_pipeline_smoke_exported_env_keys_marks_operator_checklist_ready_without_dotenv(
    tmp_path: Path,
    monkeypatch,
) -> None:
    from halo_swing_mcp.tools import readiness as readiness_tools

    clear_readiness_env(monkeypatch)
    repo_env = tmp_path / ".env"
    repo_env.with_name(".env.example").write_text(
        "POLYGON_API_KEY=\nFRED_API_KEY=\nNEWS_API_KEY=\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(local_env, "REPO_ROOT_ENV_PATH", repo_env)
    monkeypatch.setenv("POLYGON_API_KEY", "polygon-exported-secret")
    monkeypatch.setenv("FRED_API_KEY", "fred-exported-secret")
    monkeypatch.setenv("NEWS_API_KEY", "news-exported-secret")
    clear_local_env_cache()
    get_settings.cache_clear()

    def fake_live_data_smoke(
        symbols: list[str] | None = None,
        topic: str = "macro",
    ) -> dict[str, Any]:
        return {
            "schema_version": "live_data_smoke_run.v1",
            "status": "conflict",
            "input": {
                "symbols": symbols if symbols is not None else ["QQQ"],
                "topic": topic,
            },
            "provider_route": readiness_tools.get_live_data_provider_route(),
            "network_call": False,
            "live_data_required": True,
            "mutates_local_state": False,
            "secret_values_returned": False,
        }

    def fake_workflow_smoke(
        asset: str = "TQQQ",
        timeframe: str = "swing_3d_10d",
    ) -> dict[str, Any]:
        return {
            "schema_version": "live_signal_workflow_smoke_run.v1",
            "status": "conflict",
            "input": {"asset": asset, "timeframe": timeframe},
            "network_call": False,
            "live_data_required": True,
            "mutates_local_state": False,
            "secret_values_returned": False,
        }

    def fake_recording_smoke(
        asset: str = "TQQQ",
        timeframe: str = "swing_3d_10d",
    ) -> dict[str, Any]:
        return {
            "schema_version": "live_recording_smoke_run.v1",
            "status": "conflict",
            "input": {"asset": asset, "timeframe": timeframe},
            "network_call": False,
            "live_data_required": True,
            "mutates_local_state": False,
            "secret_values_returned": False,
        }

    monkeypatch.setattr(readiness_tools, "run_live_data_smoke", fake_live_data_smoke)
    monkeypatch.setattr(
        readiness_tools,
        "run_live_signal_workflow_smoke",
        fake_workflow_smoke,
    )
    monkeypatch.setattr(
        readiness_tools,
        "run_live_recording_smoke",
        fake_recording_smoke,
    )

    payload = run_api_key_pipeline_smoke(
        asset="TQQQ",
        timeframe="swing_3d_10d",
        symbols=["QQQ"],
        topic="macro",
    )
    serialized = json.dumps(payload, sort_keys=True)
    checklist = payload["api_key_operator_checklist"]

    assert payload["setup_status_summary"]["next_setup_step"] == "run_provider_smokes"
    assert payload["setup_status_summary"]["ready_to_run_live_smoke"] is True
    assert checklist["status"] == "ready"
    assert checklist["current_step"] == "run_provider_smokes"
    assert checklist["ready"] is True
    assert checklist["ready_step_names"] == [
        "prepare_dotenv",
        "fill_live_data_api_keys",
        "run_provider_smokes",
        "run_api_key_pipeline_smoke",
    ]
    assert checklist["ready_step_count"] == 4
    assert checklist["blocking_step_names"] == []
    assert checklist["blocking_step_count"] == 0
    assert checklist["next_blocking_step"] is None
    assert checklist["next_blocking_action"] is None
    assert checklist["steps"][0]["name"] == "prepare_dotenv"
    assert checklist["steps"][0]["status"] == "ready"
    assert checklist["mutates_local_state"] is False
    assert checklist["secret_values_returned"] is False
    assert "polygon-exported-secret" not in serialized
    assert "fred-exported-secret" not in serialized
    assert "news-exported-secret" not in serialized


def test_run_api_key_pipeline_smoke_reports_disabled_dotenv_loading_without_secrets(
    tmp_path: Path,
    monkeypatch,
) -> None:
    clear_readiness_env(monkeypatch)
    repo_env = tmp_path / ".env"
    repo_env.with_name(".env.example").write_text(
        "POLYGON_API_KEY=\nFRED_API_KEY=\nNEWS_API_KEY=\n",
        encoding="utf-8",
    )
    secret_env = {
        "POLYGON_API_KEY": "polygon-dotenv-secret",
        "FRED_API_KEY": "fred-dotenv-secret",
        "NEWS_API_KEY": "news-dotenv-secret",
    }
    repo_env.write_text(
        "\n".join(f"{key}={value}" for key, value in secret_env.items()),
        encoding="utf-8",
    )
    monkeypatch.setattr(local_env, "REPO_ROOT_ENV_PATH", repo_env)
    monkeypatch.setenv(local_env.DOTENV_DISABLED_ENV, "true")
    clear_local_env_cache()
    get_settings.cache_clear()

    payload = run_api_key_pipeline_smoke(
        asset="TQQQ",
        timeframe="swing_3d_10d",
        symbols=["QQQ"],
        topic="macro",
    )
    serialized = json.dumps(payload, sort_keys=True)

    assert payload["status"] == "conflict"
    assert payload["api_key_dotenv_loading_summary"] == {
        "schema_version": "api_key_dotenv_loading_summary.v1",
        "dotenv_supported": True,
        "dotenv_loading_enabled": False,
        "disabled": True,
        "disabled_env_key": "HALO_SWING_DISABLE_DOTENV",
        "configuration_precedence": [
            "exported environment variables",
            "launch-directory .env",
            "repo-root .env",
        ],
        "source_path": ".env.example",
        "target_path": ".env",
        "source_exists": True,
        "target_exists": True,
        "copy_required": False,
        "next_setup_step": "fill_live_data_api_keys",
        "ready_to_run_live_smoke": False,
        "network_call": False,
        "mutates_local_state": False,
        "secret_values_returned": False,
    }
    assert payload["api_key_setup_file_summary"]["target_exists"] is True
    assert payload["api_key_setup_file_summary"]["copy_required"] is False
    assert payload["api_key_setup_file_summary"]["missing_provider_families"] == [
        "market",
        "macro",
        "news",
    ]
    assert payload["api_key_next_action_summary"]["next_action_name"] == (
        "fill_live_data_api_keys"
    )
    assert payload["api_key_dotenv_loading_summary"]["secret_values_returned"] is False
    for value in secret_env.values():
        assert value not in serialized


def test_live_data_provider_route_reports_blocked_defaults(monkeypatch) -> None:
    clear_readiness_env(monkeypatch)

    payload = get_live_data_provider_route()

    assert payload["schema_version"] == "live_data_provider_route.v1"
    assert payload["status"] == "blocked"
    assert payload["provider_factory"] == "get_market_data_provider"
    assert payload["selected_provider_classes"] == ["ReplayMarketDataProvider"]
    assert payload["route"][0]["provider_class"] == "ReplayMarketDataProvider"
    assert payload["route"][0]["network_call"] is False
    assert payload["missing"] == [
        "market_ohlcv_api_key",
        "macro_api_key",
        "news_api_key",
    ]
    assert payload["api_key_status"]["status"] == "blocked"
    assert payload["network_call"] is False
    assert payload["mutates_local_state"] is False
    assert payload["secret_values_returned"] is False
    assert payload["hermes_runtime_started"] is False
    assert payload["telegram_send_call"] is False
    assert payload["order_submission"] is False


def test_live_data_provider_route_accepts_api_key_aliases_without_secret_values(
    monkeypatch,
) -> None:
    clear_readiness_env(monkeypatch)
    secret_env = {
        "POLYGON_API_KEY": "polygon-secret-key",
        "FRED_API_KEY": "fred-secret-key",
        "HALO_SWING_NEWS_API_KEY": "news-secret-key",
    }
    for key, value in secret_env.items():
        monkeypatch.setenv(key, value)
    get_settings.cache_clear()
    clear_local_env_cache()

    payload = get_live_data_provider_route()
    serialized = json.dumps(payload, sort_keys=True)

    assert payload["status"] == "ready"
    assert payload["missing"] == []
    assert payload["selected_provider_classes"] == [
        "PolygonMarketDataProvider",
        "FredMacroDataProvider",
        "NewsApiDataProvider",
    ]
    assert [entry["provider"] for entry in payload["route"]] == [
        "polygon",
        "fred",
        "newsapi",
    ]
    assert payload["providers"]["market"]["configured_env_keys"] == ["POLYGON_API_KEY"]
    assert payload["providers"]["macro"]["configured_env_keys"] == ["FRED_API_KEY"]
    assert payload["providers"]["news"]["configured_env_keys"] == [
        "HALO_SWING_NEWS_API_KEY"
    ]
    assert payload["api_key_status"]["status"] == "ready"
    assert payload["network_call"] is False
    assert payload["mutates_local_state"] is False
    assert payload["secret_values_returned"] is False
    for key, value in secret_env.items():
        assert key in serialized
        assert value not in serialized


def test_validate_live_data_smoke_result_accepts_live_boundaries() -> None:
    payload = validate_live_data_smoke_result(
        market_snapshot={
            "live_data_required": True,
            "market_snapshot_contract": {
                "live_data_required": True,
                "network_call": True,
            },
            "market_snapshot_guard": {
                "status": "ok",
                "checks": [
                    {"name": "live_data_boundary_declared", "passed": True}
                ],
            },
        },
        macro_snapshot={
            "live_data_required": True,
            "macro_filter_contract": {
                "live_data_required": True,
                "network_call": True,
            },
            "macro_filter_guard": {
                "status": "ok",
                "checks": [
                    {"name": "live_data_boundary_declared", "passed": True},
                    {"name": "network_call_declared", "passed": True},
                ],
            },
        },
        news_bundle={
            "live_data_required": True,
            "news_source_policy_contract": {
                "live_data_required": True,
                "network_call": True,
                "secret_values_returned": False,
            },
            "news_source_policy_guard": {
                "status": "ok",
                "checks": [
                    {"name": "live_data_boundary_declared", "passed": True},
                    {"name": "network_call_declared", "passed": True},
                    {"name": "secret_values_not_returned", "passed": True},
                ],
            },
            "news_score_contract": {"secret_values_returned": False},
        },
    )

    assert payload["schema_version"] == "live_data_smoke_validation.v1"
    assert payload["status"] == "ok"
    assert payload["checked_tools"] == [
        "get_market_snapshot",
        "get_macro_snapshot",
        "get_news_bundle",
    ]
    assert payload["network_call"] is False
    assert payload["live_data_required"] is False
    assert payload["send_call"] is False
    assert payload["order_submission"] is False
    assert payload["secret_values_returned"] is False
    assert all(check["passed"] for check in payload["checks"])


def test_validate_live_data_smoke_result_flags_fixture_payloads(monkeypatch) -> None:
    clear_readiness_env(monkeypatch)

    payload = validate_live_data_smoke_result(
        market_snapshot=get_market_snapshot(["QQQ"]),
        macro_snapshot=get_macro_snapshot(),
        news_bundle=get_news_bundle("all"),
    )
    failed_checks = {
        (check["tool"], check["name"])
        for check in payload["checks"]
        if not check["passed"]
    }

    assert payload["status"] == "conflict"
    assert ("get_market_snapshot", "payload_live_data_required") in failed_checks
    assert ("get_market_snapshot", "contract_network_call") in failed_checks
    assert ("get_macro_snapshot", "payload_live_data_required") in failed_checks
    assert ("get_macro_snapshot", "network_call_declared") in failed_checks
    assert ("get_news_bundle", "payload_live_data_required") in failed_checks
    assert ("get_news_bundle", "network_call_declared") in failed_checks
    assert payload["network_call"] is False
    assert payload["secret_values_returned"] is False


def test_run_live_data_smoke_executes_and_validates_with_fake_live_payloads(
    monkeypatch,
) -> None:
    from halo_swing_mcp.tools import market as market_tools

    clear_readiness_env(monkeypatch)
    monkeypatch.setenv("POLYGON_API_KEY", "polygon-secret-key")
    monkeypatch.setenv("HALO_SWING_FRED_API_KEY", "fred-secret-key")
    monkeypatch.setenv("NEWS_API_KEY", "news-secret-key")
    get_settings.cache_clear()
    clear_local_env_cache()

    def fake_market_snapshot(symbols: list[str] | None = None) -> dict[str, Any]:
        return {
            "live_data_required": True,
            "market_snapshot_contract": {
                "live_data_required": True,
                "network_call": True,
            },
            "market_snapshot_guard": {
                "status": "ok",
                "checks": [
                    {"name": "live_data_boundary_declared", "passed": True}
                ],
            },
            "snapshots": [{"symbol": symbols[0] if symbols else "QQQ"}],
        }

    def fake_macro_snapshot() -> dict[str, Any]:
        return {
            "live_data_required": True,
            "macro_filter_contract": {
                "live_data_required": True,
                "network_call": True,
            },
            "macro_filter_guard": {
                "status": "ok",
                "checks": [
                    {"name": "live_data_boundary_declared", "passed": True},
                    {"name": "network_call_declared", "passed": True},
                ],
            },
        }

    def fake_news_bundle(topic: str = "macro") -> dict[str, Any]:
        return {
            "topic": topic,
            "live_data_required": True,
            "news_source_policy_contract": {
                "live_data_required": True,
                "network_call": True,
                "secret_values_returned": False,
            },
            "news_source_policy_guard": {
                "status": "ok",
                "checks": [
                    {"name": "live_data_boundary_declared", "passed": True},
                    {"name": "network_call_declared", "passed": True},
                    {"name": "secret_values_not_returned", "passed": True},
                ],
            },
            "news_score_contract": {"secret_values_returned": False},
        }

    monkeypatch.setattr(market_tools, "get_market_snapshot", fake_market_snapshot)
    monkeypatch.setattr(market_tools, "get_macro_snapshot", fake_macro_snapshot)
    monkeypatch.setattr(market_tools, "get_news_bundle", fake_news_bundle)

    payload = run_live_data_smoke(symbols=["QQQ"], topic="macro")

    assert payload["schema_version"] == "live_data_smoke_run.v1"
    assert payload["status"] == "ok"
    assert payload["input"] == {"symbols": ["QQQ"], "topic": "macro"}
    assert payload["network_call"] is True
    assert payload["live_data_required"] is True
    assert payload["send_call"] is False
    assert payload["order_submission"] is False
    assert payload["secret_values_returned"] is False
    assert payload["provider_route"]["status"] == "ready"
    assert payload["provider_route"]["selected_provider_classes"] == [
        "PolygonMarketDataProvider",
        "FredMacroDataProvider",
        "NewsApiDataProvider",
    ]
    assert payload["provider_route"]["network_call"] is False
    assert payload["provider_route"]["secret_values_returned"] is False
    assert payload["live_data_setup_summary"]["status"] == "ready"
    assert payload["live_data_setup_summary"]["ready_to_run_live_smoke"] is True
    assert payload["live_data_setup_summary"]["api_key_status"] == "ready"
    assert payload["live_data_setup_summary"]["provider_route_status"] == "ready"
    assert payload["live_data_setup_summary"]["configured_provider_families"] == [
        "market",
        "macro",
        "news",
    ]
    assert payload["live_data_setup_summary"]["provider_family_summary"] == {
        "required_provider_families": ["market", "macro", "news"],
        "configured_provider_families": ["market", "macro", "news"],
        "missing_provider_families": [],
        "configured_count": 3,
        "required_count": 3,
        "ready_to_run_live_smoke": True,
        "network_call": False,
        "mutates_local_state": False,
        "secret_values_returned": False,
    }
    assert payload["live_data_setup_summary"]["missing"] == []
    assert payload["live_data_setup_summary"]["ready_to_run_live_smoke"] is True
    assert payload["live_data_setup_summary"]["selected_provider_classes"] == [
        "PolygonMarketDataProvider",
        "FredMacroDataProvider",
        "NewsApiDataProvider",
    ]
    assert (
        payload["live_data_setup_summary"]["one_shot_smoke_command"]["name"]
        == "run_api_key_pipeline_smoke"
    )
    assert (
        payload["live_data_setup_summary"]["next_smoke_command"]["name"]
        == "run_api_key_pipeline_smoke"
    )
    assert payload["live_data_setup_summary"]["network_call"] is False
    assert payload["live_data_setup_summary"]["secret_values_returned"] is False
    assert payload["validation"]["status"] == "ok"
    assert all(check["passed"] for check in payload["validation"]["checks"])
    assert payload["provider_error_summaries"] == []
    assert payload["provider_error_summary_count"] == 0
    assert payload["failed_provider_families"] == []
    assert payload["failed_provider_count"] == 0
    assert payload["first_provider_error_summary"] is None
    assert payload["next_provider_recovery_action"] is None
    assert payload["next_provider_recovery_smoke"] is None
    assert payload["next_provider_recovery_smoke_command_name"] is None
    assert payload["provider_recovery_smokes"] == []
    assert payload["provider_recovery_smoke_count"] == 0


def test_run_live_data_smoke_surfaces_provider_error_summaries(monkeypatch) -> None:
    from halo_swing_mcp.tools import market as market_tools

    clear_readiness_env(monkeypatch)
    monkeypatch.setenv("POLYGON_API_KEY", "polygon-secret-key")
    monkeypatch.setenv("FRED_API_KEY", "fred-secret-key")
    monkeypatch.setenv("NEWS_API_KEY", "news-secret-key")
    get_settings.cache_clear()
    clear_local_env_cache()

    market_error = {
        "schema_version": "provider_smoke_error.v1",
        "tool": "get_market_snapshot",
        "provider_family": "market",
        "provider": "polygon",
        "smoke_command_name": "get_market_snapshot_live_smoke",
        "next_setup_action": "verify_provider_credentials_or_network",
        "network_call_policy": "only_when_matching_provider_selects_live_route",
        "exception_type": "RuntimeError",
        "exception_message_returned": False,
        "url_returned": False,
        "secret_values_returned": False,
    }
    macro_error = {
        "schema_version": "provider_smoke_error.v1",
        "tool": "get_macro_snapshot",
        "provider_family": "macro",
        "provider": "fred",
        "smoke_command_name": "get_macro_snapshot_live_smoke",
        "next_setup_action": "verify_provider_credentials_or_network",
        "network_call_policy": "only_when_matching_provider_selects_live_route",
        "exception_type": "RuntimeError",
        "exception_message_returned": False,
        "url_returned": False,
        "secret_values_returned": False,
    }
    news_error = {
        "schema_version": "provider_smoke_error.v1",
        "tool": "get_news_bundle",
        "provider_family": "news",
        "provider": "newsapi",
        "smoke_command_name": "get_news_bundle_live_smoke",
        "next_setup_action": "verify_provider_credentials_or_network",
        "network_call_policy": "only_when_matching_provider_selects_live_route",
        "exception_type": "RuntimeError",
        "exception_message_returned": False,
        "url_returned": False,
        "secret_values_returned": False,
    }

    def fake_market_snapshot(symbols: list[str] | None = None) -> dict[str, Any]:
        return {
            "status": "conflict",
            "live_data_required": True,
            "market_snapshot_contract": {
                "live_data_required": True,
                "network_call": True,
            },
            "market_snapshot_guard": {
                "status": "conflict",
                "checks": [
                    {"name": "live_data_boundary_declared", "passed": True},
                    {"name": "provider_smoke_completed", "passed": False},
                ],
            },
            "error_summary": market_error,
            "secret_values_returned": False,
        }

    def fake_macro_snapshot() -> dict[str, Any]:
        return {
            "status": "conflict",
            "live_data_required": True,
            "macro_filter_contract": {
                "live_data_required": True,
                "network_call": True,
            },
            "macro_filter_guard": {
                "status": "conflict",
                "checks": [
                    {"name": "live_data_boundary_declared", "passed": True},
                    {"name": "network_call_declared", "passed": True},
                    {"name": "provider_smoke_completed", "passed": False},
                ],
            },
            "error_summary": macro_error,
            "secret_values_returned": False,
        }

    def fake_news_bundle(topic: str = "macro") -> dict[str, Any]:
        return {
            "status": "conflict",
            "topic": topic,
            "live_data_required": True,
            "news_source_policy_contract": {
                "live_data_required": True,
                "network_call": True,
                "secret_values_returned": False,
            },
            "news_source_policy_guard": {
                "status": "conflict",
                "checks": [
                    {"name": "live_data_boundary_declared", "passed": True},
                    {"name": "network_call_declared", "passed": True},
                    {"name": "secret_values_not_returned", "passed": True},
                    {"name": "provider_smoke_completed", "passed": False},
                ],
            },
            "news_score_contract": {"secret_values_returned": False},
            "error_summary": news_error,
            "secret_values_returned": False,
        }

    monkeypatch.setattr(market_tools, "get_market_snapshot", fake_market_snapshot)
    monkeypatch.setattr(market_tools, "get_macro_snapshot", fake_macro_snapshot)
    monkeypatch.setattr(market_tools, "get_news_bundle", fake_news_bundle)

    payload = run_live_data_smoke(symbols=["QQQ"], topic="macro")
    serialized = json.dumps(payload, sort_keys=True)

    assert payload["status"] == "conflict"
    assert payload["provider_error_summaries"] == [
        market_error,
        macro_error,
        news_error,
    ]
    assert payload["provider_error_summary_count"] == 3
    assert payload["failed_provider_families"] == ["market", "macro", "news"]
    assert payload["failed_provider_count"] == 3
    assert payload["first_provider_error_summary"] == market_error
    assert (
        payload["next_provider_recovery_action"]
        == "verify_provider_credentials_or_network"
    )
    assert payload["next_provider_recovery_smoke_command_name"] == (
        "get_market_snapshot_live_smoke"
    )
    assert payload["next_provider_recovery_smoke"]["provider_family"] == "market"
    assert payload["next_provider_recovery_smoke"]["provider"] == "polygon"
    assert payload["next_provider_recovery_smoke"]["smoke_command_name"] == (
        "get_market_snapshot_live_smoke"
    )
    assert payload["next_provider_recovery_smoke"]["command"] == (
        "PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness "
        "get_market_snapshot --input-json '{\"symbols\":[\"QQQ\"]}' --no-audit"
    )
    assert payload["next_provider_recovery_smoke"]["secret_values_returned"] is False
    assert [
        recovery_smoke["smoke_command_name"]
        for recovery_smoke in payload["provider_recovery_smokes"]
    ] == [
        "get_market_snapshot_live_smoke",
        "get_macro_snapshot_live_smoke",
        "get_news_bundle_live_smoke",
    ]
    assert payload["provider_recovery_smoke_count"] == 3
    assert all(
        recovery_smoke["secret_values_returned"] is False
        for recovery_smoke in payload["provider_recovery_smokes"]
    )
    assert payload["secret_values_returned"] is False
    assert "polygon-secret-key" not in serialized
    assert "fred-secret-key" not in serialized
    assert "news-secret-key" not in serialized
    assert "provider.example" not in serialized
    assert "apiKey" not in serialized


def test_run_api_key_pipeline_smoke_surfaces_live_data_provider_error_summaries(
    monkeypatch,
) -> None:
    from halo_swing_mcp.tools import market as market_tools
    from halo_swing_mcp.tools import readiness as readiness_tools

    clear_readiness_env(monkeypatch)
    monkeypatch.setenv("POLYGON_API_KEY", "polygon-secret-key")
    monkeypatch.setenv("FRED_API_KEY", "fred-secret-key")
    monkeypatch.setenv("NEWS_API_KEY", "news-secret-key")
    get_settings.cache_clear()
    clear_local_env_cache()

    provider_errors = [
        {
            "schema_version": "provider_smoke_error.v1",
            "tool": "get_market_snapshot",
            "provider_family": "market",
            "provider": "polygon",
            "smoke_command_name": "get_market_snapshot_live_smoke",
            "next_setup_action": "verify_provider_credentials_or_network",
            "network_call_policy": "only_when_matching_provider_selects_live_route",
            "exception_type": "RuntimeError",
            "exception_message_returned": False,
            "url_returned": False,
            "secret_values_returned": False,
        },
        {
            "schema_version": "provider_smoke_error.v1",
            "tool": "get_macro_snapshot",
            "provider_family": "macro",
            "provider": "fred",
            "smoke_command_name": "get_macro_snapshot_live_smoke",
            "next_setup_action": "verify_provider_credentials_or_network",
            "network_call_policy": "only_when_matching_provider_selects_live_route",
            "exception_type": "RuntimeError",
            "exception_message_returned": False,
            "url_returned": False,
            "secret_values_returned": False,
        },
        {
            "schema_version": "provider_smoke_error.v1",
            "tool": "get_news_bundle",
            "provider_family": "news",
            "provider": "newsapi",
            "smoke_command_name": "get_news_bundle_live_smoke",
            "next_setup_action": "verify_provider_credentials_or_network",
            "network_call_policy": "only_when_matching_provider_selects_live_route",
            "exception_type": "RuntimeError",
            "exception_message_returned": False,
            "url_returned": False,
            "secret_values_returned": False,
        },
    ]

    def fake_market_snapshot(symbols: list[str] | None = None) -> dict[str, Any]:
        return {
            "status": "conflict",
            "live_data_required": True,
            "market_snapshot_contract": {
                "live_data_required": True,
                "network_call": True,
            },
            "market_snapshot_guard": {
                "status": "conflict",
                "checks": [
                    {"name": "live_data_boundary_declared", "passed": True},
                    {"name": "provider_smoke_completed", "passed": False},
                ],
            },
            "error_summary": provider_errors[0],
            "secret_values_returned": False,
        }

    def fake_macro_snapshot() -> dict[str, Any]:
        return {
            "status": "conflict",
            "live_data_required": True,
            "macro_filter_contract": {
                "live_data_required": True,
                "network_call": True,
            },
            "macro_filter_guard": {
                "status": "conflict",
                "checks": [
                    {"name": "live_data_boundary_declared", "passed": True},
                    {"name": "network_call_declared", "passed": True},
                    {"name": "provider_smoke_completed", "passed": False},
                ],
            },
            "error_summary": provider_errors[1],
            "secret_values_returned": False,
        }

    def fake_news_bundle(topic: str = "macro") -> dict[str, Any]:
        return {
            "status": "conflict",
            "topic": topic,
            "live_data_required": True,
            "news_source_policy_contract": {
                "live_data_required": True,
                "network_call": True,
                "secret_values_returned": False,
            },
            "news_source_policy_guard": {
                "status": "conflict",
                "checks": [
                    {"name": "live_data_boundary_declared", "passed": True},
                    {"name": "network_call_declared", "passed": True},
                    {"name": "secret_values_not_returned", "passed": True},
                    {"name": "provider_smoke_completed", "passed": False},
                ],
            },
            "news_score_contract": {"secret_values_returned": False},
            "error_summary": provider_errors[2],
            "secret_values_returned": False,
        }

    def fake_signal_workflow_smoke(
        asset: str = "TQQQ",
        timeframe: str = "swing_3d_10d",
    ) -> dict[str, Any]:
        return {
            "schema_version": "live_signal_workflow_smoke_run.v1",
            "status": "ok",
            "input": {"asset": asset, "timeframe": timeframe},
            "network_call": False,
            "live_data_required": False,
            "mutates_local_state": False,
            "secret_values_returned": False,
        }

    def fake_recording_smoke(
        asset: str = "TQQQ",
        timeframe: str = "swing_3d_10d",
    ) -> dict[str, Any]:
        return {
            "schema_version": "live_recording_smoke_run.v1",
            "status": "ok",
            "input": {"asset": asset, "timeframe": timeframe},
            "network_call": False,
            "live_data_required": False,
            "mutates_local_state": False,
            "secret_values_returned": False,
        }

    monkeypatch.setattr(market_tools, "get_market_snapshot", fake_market_snapshot)
    monkeypatch.setattr(market_tools, "get_macro_snapshot", fake_macro_snapshot)
    monkeypatch.setattr(market_tools, "get_news_bundle", fake_news_bundle)
    monkeypatch.setattr(
        readiness_tools,
        "run_live_signal_workflow_smoke",
        fake_signal_workflow_smoke,
    )
    monkeypatch.setattr(
        readiness_tools,
        "run_live_recording_smoke",
        fake_recording_smoke,
    )

    payload = run_api_key_pipeline_smoke(
        asset="TQQQ",
        timeframe="swing_3d_10d",
        symbols=["QQQ"],
        topic="macro",
    )
    serialized = json.dumps(payload, sort_keys=True)

    assert payload["status"] == "conflict"
    assert payload["live_data_smoke_summary"]["status"] == "conflict"
    assert payload["live_data_smoke_summary"]["provider_error_summaries"] == (
        provider_errors
    )
    assert payload["api_key_pipeline_stage_summary"]["schema_version"] == (
        "api_key_pipeline_stage_summary.v1"
    )
    assert payload["api_key_pipeline_stage_summary"]["status"] == "conflict"
    assert payload["api_key_pipeline_stage_summary"]["stage_count"] == 3
    assert payload["api_key_pipeline_stage_summary"]["failed_stage_count"] == 1
    assert payload["api_key_pipeline_stage_summary"]["failed_stage_names"] == [
        "run_live_data_smoke"
    ]
    assert payload["api_key_pipeline_stage_summary"]["first_failed_stage"] == {
        "stage_name": "run_live_data_smoke",
        "status": "conflict",
        "failed": True,
        "error_summary": None,
        "provider_error_summary_count": 3,
        "provider_recovery_smoke_count": 3,
        "next_provider_recovery_smoke_command_name": (
            "get_market_snapshot_live_smoke"
        ),
        "ready_to_run_live_smoke": True,
        "provider_route_status": "ready",
        "network_call": True,
        "live_data_required": True,
        "mutates_local_state": False,
        "secret_values_returned": False,
    }
    assert payload["api_key_pipeline_stage_summary"]["secret_values_returned"] is False
    assert payload["api_key_pipeline_check_summary"] == {
        "schema_version": "api_key_pipeline_check_summary.v1",
        "status": "conflict",
        "check_count": 9,
        "passed_check_count": 8,
        "failed_check_count": 1,
        "failed_check_keys": ["run_live_data_smoke.live_data_smoke_status_ok"],
        "tools_with_failures": ["run_live_data_smoke"],
        "tool_failure_counts": {"run_live_data_smoke": 1},
        "first_failed_check": {
            "tool": "run_live_data_smoke",
            "name": "live_data_smoke_status_ok",
            "key": "run_live_data_smoke.live_data_smoke_status_ok",
            "passed": False,
            "expected": "ok",
            "actual": "conflict",
            "secret_values_returned": False,
        },
        "failed_checks": [
            {
                "tool": "run_live_data_smoke",
                "name": "live_data_smoke_status_ok",
                "key": "run_live_data_smoke.live_data_smoke_status_ok",
                "passed": False,
                "expected": "ok",
                "actual": "conflict",
                "secret_values_returned": False,
            }
        ],
        "network_call": False,
        "mutates_local_state": False,
        "secret_values_returned": False,
    }
    assert payload["api_key_pipeline_failure_summary"] == {
        "schema_version": "api_key_pipeline_failure_summary.v1",
        "status": "conflict",
        "has_failures": True,
        "failure_category": "provider_recovery",
        "failed_stage_names": ["run_live_data_smoke"],
        "failed_check_keys": ["run_live_data_smoke.live_data_smoke_status_ok"],
        "tools_with_failures": ["run_live_data_smoke"],
        "first_failed_stage_name": "run_live_data_smoke",
        "first_failed_check_key": "run_live_data_smoke.live_data_smoke_status_ok",
        "next_action_name": "recover_failed_providers",
        "next_action_command": payload["provider_recovery_smokes"][0]["command"],
        "next_action_is_recovery": True,
        "provider_recovery_required": True,
        "provider_recovery_item_count": 3,
        "network_call": False,
        "mutates_local_state": False,
        "secret_values_returned": False,
    }
    assert payload["api_key_setup_file_summary"] == {
        "schema_version": "api_key_setup_file_summary.v1",
        "source_path": ".env.example",
        "target_path": ".env",
        "source_exists": True,
        "target_exists": False,
        "copy_required": True,
        "copy_command": {
            "name": "copy_env_example_to_env",
            "command": "cp .env.example .env",
            "required": True,
            "source_path": ".env.example",
            "target_path": ".env",
            "network_call": False,
            "mutates_local_state": True,
            "secret_values_returned": False,
        },
        "preferred_env_keys": ["POLYGON_API_KEY", "FRED_API_KEY", "NEWS_API_KEY"],
        "preferred_env_key_count": 3,
        "configured_provider_families": ["market", "macro", "news"],
        "missing_provider_families": [],
        "configured_provider_family_count": 3,
        "required_provider_family_count": 3,
        "next_setup_step": "run_provider_smokes",
        "ready_to_run_live_smoke": True,
        "network_call": False,
        "mutates_local_state": False,
        "secret_values_returned": False,
    }
    assert payload["api_key_dotenv_loading_summary"] == {
        "schema_version": "api_key_dotenv_loading_summary.v1",
        "dotenv_supported": True,
        "dotenv_loading_enabled": True,
        "disabled": False,
        "disabled_env_key": "HALO_SWING_DISABLE_DOTENV",
        "configuration_precedence": [
            "exported environment variables",
            "launch-directory .env",
            "repo-root .env",
        ],
        "source_path": ".env.example",
        "target_path": ".env",
        "source_exists": True,
        "target_exists": False,
        "copy_required": True,
        "next_setup_step": "run_provider_smokes",
        "ready_to_run_live_smoke": True,
        "network_call": False,
        "mutates_local_state": False,
        "secret_values_returned": False,
    }
    assert payload["api_key_provider_selection_summary"] == {
        "schema_version": "api_key_provider_selection_summary.v1",
        "status": "ready",
        "provider_factory": "get_market_data_provider",
        "selected_provider_classes": [
            "PolygonMarketDataProvider",
            "FredMacroDataProvider",
            "NewsApiDataProvider",
        ],
        "selected_provider_class_count": 3,
        "configured_provider_families": ["market", "macro", "news"],
        "configured_provider_family_count": 3,
        "missing_provider_families": [],
        "configured_env_keys_by_provider_family": {
            "market": ["POLYGON_API_KEY"],
            "macro": ["FRED_API_KEY"],
            "news": ["NEWS_API_KEY"],
        },
        "selected_provider_by_family": {
            "market": "polygon",
            "macro": "fred",
            "news": "newsapi",
        },
        "ready_to_run_live_smoke": True,
        "network_call": False,
        "mutates_local_state": False,
        "secret_values_returned": False,
    }
    assert payload["api_key_integration_status_summary"] == {
        "schema_version": "api_key_integration_status_summary.v1",
        "status": "conflict",
        "api_keys_configured": True,
        "dotenv_loading_enabled": True,
        "dotenv_target_exists": False,
        "live_providers_selected": True,
        "ready_to_run_live_smoke": True,
        "configured_provider_families": ["market", "macro", "news"],
        "missing_provider_families": [],
        "selected_provider_classes": [
            "PolygonMarketDataProvider",
            "FredMacroDataProvider",
            "NewsApiDataProvider",
        ],
        "failure_category": "provider_recovery",
        "has_failures": True,
        "next_action_name": "recover_failed_providers",
        "next_action_is_recovery": True,
        "next_action_network_call": True,
        "network_call": False,
        "mutates_local_state": False,
        "secret_values_returned": False,
    }
    assert payload["live_data_smoke_summary"]["provider_error_summary_count"] == 3
    assert payload["live_data_smoke_summary"]["failed_provider_families"] == [
        "market",
        "macro",
        "news",
    ]
    assert payload["live_data_smoke_summary"]["failed_provider_count"] == 3
    assert (
        payload["live_data_smoke_summary"]["first_provider_error_summary"]
        == provider_errors[0]
    )
    assert (
        payload["live_data_smoke_summary"]["next_provider_recovery_action"]
        == "verify_provider_credentials_or_network"
    )
    assert (
        payload["live_data_smoke_summary"][
            "next_provider_recovery_smoke_command_name"
        ]
        == "get_market_snapshot_live_smoke"
    )
    assert payload["live_data_smoke_summary"]["next_provider_recovery_smoke"][
        "provider_family"
    ] == "market"
    assert payload["live_data_smoke_summary"]["next_provider_recovery_smoke"][
        "provider"
    ] == "polygon"
    assert [
        recovery_smoke["smoke_command_name"]
        for recovery_smoke in payload["live_data_smoke_summary"][
            "provider_recovery_smokes"
        ]
    ] == [
        "get_market_snapshot_live_smoke",
        "get_macro_snapshot_live_smoke",
        "get_news_bundle_live_smoke",
    ]
    assert (
        payload["live_data_smoke_summary"]["provider_recovery_smoke_count"] == 3
    )
    assert payload["failed_provider_families"] == ["market", "macro", "news"]
    assert payload["failed_provider_count"] == 3
    assert payload["first_provider_error_summary"] == provider_errors[0]
    assert (
        payload["next_provider_recovery_action"]
        == "verify_provider_credentials_or_network"
    )
    assert payload["next_provider_recovery_smoke_command_name"] == (
        "get_market_snapshot_live_smoke"
    )
    assert payload["next_provider_recovery_smoke"] == (
        payload["live_data_smoke_summary"]["next_provider_recovery_smoke"]
    )
    assert payload["provider_recovery_smokes"] == (
        payload["live_data_smoke_summary"]["provider_recovery_smokes"]
    )
    assert payload["provider_recovery_smoke_count"] == 3
    recovery_checklist = payload["api_key_provider_recovery_checklist"]
    assert recovery_checklist["schema_version"] == (
        "api_key_provider_recovery_checklist.v1"
    )
    assert recovery_checklist["status"] == "conflict"
    assert recovery_checklist["provider_error_count"] == 3
    assert recovery_checklist["provider_recovery_smoke_count"] == 3
    assert recovery_checklist["item_count"] == 3
    assert [
        item["provider_family"] for item in recovery_checklist["items"]
    ] == ["market", "macro", "news"]
    assert [
        item["smoke_command_name"] for item in recovery_checklist["items"]
    ] == [
        "get_market_snapshot_live_smoke",
        "get_macro_snapshot_live_smoke",
        "get_news_bundle_live_smoke",
    ]
    assert recovery_checklist["items"][0]["exception_type"] == "RuntimeError"
    assert recovery_checklist["items"][0]["next_setup_action"] == (
        "verify_provider_credentials_or_network"
    )
    assert recovery_checklist["items"][0]["recovery_smoke_available"] is True
    assert recovery_checklist["items"][0]["recovery_smoke"] == (
        payload["provider_recovery_smokes"][0]
    )
    assert recovery_checklist["items"][0]["recovery_smoke_command"] == (
        payload["provider_recovery_smokes"][0]["command"]
    )
    assert recovery_checklist["secret_values_returned"] is False
    assert all(
        item["secret_values_returned"] is False
        for item in recovery_checklist["items"]
    )
    summary_payload = run_api_key_pipeline_smoke(
        asset="TQQQ",
        timeframe="swing_3d_10d",
        symbols=["QQQ"],
        topic="macro",
        summary_only=True,
    )
    provider_recovery_summary = summary_payload[
        "api_key_provider_recovery_summary"
    ]
    assert provider_recovery_summary == {
        "schema_version": "api_key_provider_recovery_summary.v1",
        "status": "conflict",
        "provider_recovery_required": True,
        "provider_error_count": 3,
        "provider_recovery_smoke_count": 3,
        "item_count": 3,
        "next_recovery_smoke_command_name": "get_market_snapshot_live_smoke",
        "next_recovery_smoke_command": payload["provider_recovery_smokes"][0][
            "command"
        ],
        "items": [
            {
                "provider_family": "market",
                "provider": "polygon",
                "smoke_command_name": "get_market_snapshot_live_smoke",
                "recovery_smoke_command": payload["provider_recovery_smokes"][0][
                    "command"
                ],
                "recovery_smoke_available": True,
                "next_setup_action": "verify_provider_credentials_or_network",
                "exception_type": "RuntimeError",
                "secret_values_returned": False,
            },
            {
                "provider_family": "macro",
                "provider": "fred",
                "smoke_command_name": "get_macro_snapshot_live_smoke",
                "recovery_smoke_command": payload["provider_recovery_smokes"][1][
                    "command"
                ],
                "recovery_smoke_available": True,
                "next_setup_action": "verify_provider_credentials_or_network",
                "exception_type": "RuntimeError",
                "secret_values_returned": False,
            },
            {
                "provider_family": "news",
                "provider": "newsapi",
                "smoke_command_name": "get_news_bundle_live_smoke",
                "recovery_smoke_command": payload["provider_recovery_smokes"][2][
                    "command"
                ],
                "recovery_smoke_available": True,
                "next_setup_action": "verify_provider_credentials_or_network",
                "exception_type": "RuntimeError",
                "secret_values_returned": False,
            },
        ],
        "network_call": False,
        "mutates_local_state": False,
        "secret_values_returned": False,
    }
    assert "api_key_provider_recovery_checklist" in summary_payload[
        "omitted_sections"
    ]
    assert "api_key_provider_recovery_checklist" not in summary_payload
    assert "provider_recovery_smokes" not in summary_payload
    operator_checklist = payload["api_key_operator_checklist"]
    assert operator_checklist["provider_recovery_status"] == "conflict"
    assert operator_checklist["provider_recovery_required"] is True
    assert operator_checklist["provider_recovery_item_count"] == 3
    assert operator_checklist["provider_recovery_checklist"] == recovery_checklist
    assert operator_checklist["next_provider_recovery_action"] == (
        recovery_checklist["items"][0]
    )
    assert operator_checklist["next_provider_recovery_action"][
        "recovery_smoke_command"
    ] == payload["provider_recovery_smokes"][0]["command"]
    assert (
        operator_checklist["next_provider_recovery_action"][
            "recovery_smoke_available"
        ]
        is True
    )
    assert operator_checklist["ready"] is False
    assert operator_checklist["status"] == "conflict"
    assert operator_checklist["current_step"] == "recover_failed_providers"
    assert operator_checklist["blocking_step_names"] == ["recover_failed_providers"]
    assert operator_checklist["blocking_step_count"] == 1
    assert operator_checklist["next_blocking_step"] == "recover_failed_providers"
    assert operator_checklist["step_count"] == 5
    assert operator_checklist["next_blocking_action"] == {
        "name": "recover_failed_providers",
        "status": "pending",
        "provider_recovery_item_count": 3,
        "next_provider_recovery_action": recovery_checklist["items"][0],
        "recovery_smoke_command": payload["provider_recovery_smokes"][0][
            "command"
        ],
        "recovery_smoke_available": True,
        "network_call": True,
        "network_call_policy": "only_when_matching_api_key_selects_live_provider",
        "mutates_local_state": False,
        "secret_values_returned": False,
    }
    assert operator_checklist["steps"][-1] == operator_checklist[
        "next_blocking_action"
    ]
    assert payload["next_operator_action"] == operator_checklist[
        "next_blocking_action"
    ]
    assert payload["next_operator_action"]["name"] == "recover_failed_providers"
    assert payload["next_operator_action"]["recovery_smoke_command"] == (
        payload["provider_recovery_smokes"][0]["command"]
    )
    assert payload["readiness_summary"]["next_operator_action"] == (
        operator_checklist["next_blocking_action"]
    )
    assert (
        payload["readiness_summary"]["next_operator_action_name"]
        == "recover_failed_providers"
    )
    assert payload["api_key_next_action_summary"] == {
        "schema_version": "api_key_next_action_summary.v1",
        "status": "conflict",
        "current_step": "recover_failed_providers",
        "ready": False,
        "next_action_name": "recover_failed_providers",
        "next_action_status": "pending",
        "next_action_command": payload["provider_recovery_smokes"][0]["command"],
        "next_action_is_recovery": True,
        "next_action_network_call": True,
        "next_action_mutates_local_state": False,
        "provider_recovery_status": "conflict",
        "provider_recovery_required": True,
        "provider_recovery_item_count": 3,
        "next_blocking_step": "recover_failed_providers",
        "blocking_step_count": 1,
        "ready_step_count": 4,
        "network_call": False,
        "mutates_local_state": False,
        "secret_values_returned": False,
    }
    assert payload["secret_values_returned"] is False
    assert "polygon-secret-key" not in serialized
    assert "fred-secret-key" not in serialized
    assert "news-secret-key" not in serialized
    assert "provider.example" not in serialized
    assert "apiKey" not in serialized


def test_run_live_data_smoke_flags_fixture_payloads_without_keys(monkeypatch) -> None:
    clear_readiness_env(monkeypatch)

    payload = run_live_data_smoke(symbols=["QQQ"], topic="all")

    assert payload["schema_version"] == "live_data_smoke_run.v1"
    assert payload["status"] == "conflict"
    assert payload["network_call"] is False
    assert payload["live_data_required"] is False
    assert payload["send_call"] is False
    assert payload["order_submission"] is False
    assert payload["secret_values_returned"] is False
    assert payload["provider_error_summaries"] == []
    assert payload["provider_error_summary_count"] == 0
    assert payload["failed_provider_families"] == []
    assert payload["failed_provider_count"] == 0
    assert payload["first_provider_error_summary"] is None
    assert payload["next_provider_recovery_action"] is None
    assert payload["next_provider_recovery_smoke"] is None
    assert payload["next_provider_recovery_smoke_command_name"] is None
    assert payload["provider_recovery_smokes"] == []
    assert payload["provider_recovery_smoke_count"] == 0
    assert payload["validation"]["status"] == "conflict"
    assert payload["provider_route"]["status"] == "blocked"
    assert payload["provider_route"]["selected_provider_classes"] == [
        "ReplayMarketDataProvider"
    ]
    assert payload["provider_route"]["network_call"] is False
    assert payload["provider_route"]["secret_values_returned"] is False
    assert payload["live_data_setup_summary"]["status"] == "blocked"
    assert payload["live_data_setup_summary"]["ready_to_run_live_smoke"] is False
    assert payload["live_data_setup_summary"]["api_key_status"] == "blocked"
    assert payload["live_data_setup_summary"]["provider_route_status"] == "blocked"
    assert payload["live_data_setup_summary"]["provider_family_summary"] == {
        "required_provider_families": ["market", "macro", "news"],
        "configured_provider_families": [],
        "missing_provider_families": ["market", "macro", "news"],
        "configured_count": 0,
        "required_count": 3,
        "ready_to_run_live_smoke": False,
        "network_call": False,
        "mutates_local_state": False,
        "secret_values_returned": False,
    }
    assert payload["live_data_setup_summary"]["missing"] == [
        "market_ohlcv_api_key",
        "macro_api_key",
        "news_api_key",
    ]
    assert payload["live_data_setup_summary"]["selected_provider_classes"] == [
        "ReplayMarketDataProvider"
    ]
    assert payload["live_data_setup_summary"]["dotenv_template"]["target_path"] == (
        ".env"
    )
    assert payload["live_data_setup_summary"]["dotenv_template"]["source_path"] == (
        ".env.example"
    )
    assert payload["live_data_setup_summary"]["dotenv_template"]["entries"][
        0
    ]["example"] == "POLYGON_API_KEY = your_polygon_key"
    assert payload["live_data_setup_summary"]["dotenv_template"][
        "secret_values_returned"
    ] is False
    assert (
        payload["live_data_setup_summary"]["one_shot_smoke_command"]["name"]
        == "run_api_key_pipeline_smoke"
    )
    assert (
        payload["live_data_setup_summary"]["next_smoke_command"]["name"]
        == "get_live_data_api_key_status"
    )
    assert payload["live_data_setup_summary"]["network_call"] is False
    assert payload["live_data_setup_summary"]["secret_values_returned"] is False
    assert payload["market_snapshot"]["data_mode"] == "fixture"
    assert payload["macro_snapshot"]["data_mode"] == "fixture"
    assert payload["news_bundle"]["data_mode"] == "fixture"


def test_run_integration_smoke_combines_readiness_and_live_data_smoke(
    monkeypatch,
) -> None:
    from halo_swing_mcp.tools import readiness as readiness_tools

    def fake_readiness() -> dict[str, Any]:
        return {
            "status": "blocked",
            "gates": {"migration": {"status": "blocked"}},
            "next_actions": ["migration: provide explicit_MIGRATION_GO"],
            "live_data_required": False,
        }

    def fake_api_key_status() -> dict[str, Any]:
        return {
            "schema_version": "live_data_api_key_status.v1",
            "status": "ready",
            "providers": {
                "market": {"configured": True},
                "macro": {"configured": True},
                "news": {"configured": True},
            },
            "missing": [],
            "dotenv": {
                "supported": True,
                "disabled": False,
                "precedence": [
                    "exported environment variables",
                    "launch-directory .env",
                    "repo-root .env",
                ],
                "mutation": False,
            },
            "one_shot_smoke_command": {
                "name": "run_api_key_pipeline_smoke",
                "command": (
                    "PYTHONPATH=src ./.venv/bin/python -m "
                    "halo_swing_mcp.harness run_api_key_pipeline_smoke "
                    "--input-json "
                    "'{\"asset\":\"TQQQ\",\"timeframe\":\"swing_3d_10d\","
                    "\"symbols\":[\"QQQ\"],\"topic\":\"macro\"}' --no-audit"
                ),
                "network_call": True,
                "network_call_policy": "only_when_matching_api_key_selects_live_provider",
                "mutates_local_state": False,
                "secret_values_returned": False,
            },
        }

    def fake_live_data_smoke(
        symbols: list[str] | None = None,
        topic: str = "macro",
    ) -> dict[str, Any]:
        return {
            "schema_version": "live_data_smoke_run.v1",
            "status": "ok",
            "input": {"symbols": symbols, "topic": topic},
            "provider_route": {
                "schema_version": "live_data_provider_route.v1",
                "status": "ready",
                "provider_factory": "get_market_data_provider",
                "selected_provider_classes": [
                    "PolygonMarketDataProvider",
                    "FredMacroDataProvider",
                    "NewsApiDataProvider",
                ],
                "missing": [],
                "network_call": False,
                "secret_values_returned": False,
            },
            "network_call": True,
            "live_data_required": True,
            "send_call": False,
            "order_submission": False,
            "secret_values_returned": False,
        }

    monkeypatch.setattr(readiness_tools, "get_integration_readiness", fake_readiness)
    monkeypatch.setattr(
        readiness_tools,
        "get_live_data_api_key_status",
        fake_api_key_status,
    )
    monkeypatch.setattr(readiness_tools, "run_live_data_smoke", fake_live_data_smoke)

    payload = run_integration_smoke(symbols=["QQQ"], topic="macro")

    assert payload["schema_version"] == "integration_smoke_run.v1"
    assert payload["status"] == "blocked"
    assert payload["readiness_status"] == "blocked"
    assert payload["live_data_smoke_status"] == "ok"
    assert payload["live_data_setup_summary"]["status"] == "ready"
    assert payload["live_data_setup_summary"]["api_key_status"] == "ready"
    assert payload["live_data_setup_summary"]["provider_route_status"] == "ready"
    assert payload["live_data_setup_summary"]["configured_provider_families"] == [
        "market",
        "macro",
        "news",
    ]
    assert payload["live_data_setup_summary"]["provider_family_summary"] == {
        "required_provider_families": ["market", "macro", "news"],
        "configured_provider_families": ["market", "macro", "news"],
        "missing_provider_families": [],
        "configured_count": 3,
        "required_count": 3,
        "ready_to_run_live_smoke": True,
        "network_call": False,
        "mutates_local_state": False,
        "secret_values_returned": False,
    }
    assert payload["live_data_setup_summary"]["missing"] == []
    assert payload["live_data_setup_summary"]["selected_provider_classes"] == [
        "PolygonMarketDataProvider",
        "FredMacroDataProvider",
        "NewsApiDataProvider",
    ]
    assert (
        payload["live_data_setup_summary"]["one_shot_smoke_command"]["name"]
        == "run_api_key_pipeline_smoke"
    )
    assert (
        payload["live_data_setup_summary"]["next_smoke_command"]["name"]
        == "run_api_key_pipeline_smoke"
    )
    assert payload["live_data_setup_summary"]["network_call"] is False
    assert payload["live_data_setup_summary"]["secret_values_returned"] is False
    assert payload["provider_route_summary"] == {
        "schema_version": "live_data_provider_route.v1",
        "status": "ready",
        "provider_factory": "get_market_data_provider",
        "selected_provider_classes": [
            "PolygonMarketDataProvider",
            "FredMacroDataProvider",
            "NewsApiDataProvider",
        ],
        "missing": [],
        "network_call": False,
        "secret_values_returned": False,
    }
    assert payload["network_call"] is True
    assert payload["live_data_required"] is True
    assert payload["hermes_runtime_started"] is False
    assert payload["telegram_send_call"] is False
    assert payload["send_call"] is False
    assert payload["order_submission"] is False
    assert payload["secret_values_returned"] is False
    assert payload["mutates_local_state"] is False
    assert payload["readiness"]["next_actions"] == [
        "migration: provide explicit_MIGRATION_GO"
    ]
    assert payload["live_data_smoke"]["input"] == {
        "symbols": ["QQQ"],
        "topic": "macro",
    }


def test_run_integration_smoke_keeps_fixture_default_blocked_without_side_effects(
    monkeypatch,
) -> None:
    clear_readiness_env(monkeypatch)

    payload = run_integration_smoke(symbols=["QQQ"], topic="all")

    assert payload["schema_version"] == "integration_smoke_run.v1"
    assert payload["status"] == "blocked"
    assert payload["readiness_status"] == "blocked"
    assert payload["live_data_smoke_status"] == "conflict"
    assert payload["live_data_setup_summary"]["status"] == "blocked"
    assert payload["live_data_setup_summary"]["api_key_status"] == "blocked"
    assert payload["live_data_setup_summary"]["provider_route_status"] == "blocked"
    assert payload["live_data_setup_summary"]["provider_family_summary"] == {
        "required_provider_families": ["market", "macro", "news"],
        "configured_provider_families": [],
        "missing_provider_families": ["market", "macro", "news"],
        "configured_count": 0,
        "required_count": 3,
        "ready_to_run_live_smoke": False,
        "network_call": False,
        "mutates_local_state": False,
        "secret_values_returned": False,
    }
    assert payload["live_data_setup_summary"]["missing"] == [
        "market_ohlcv_api_key",
        "macro_api_key",
        "news_api_key",
    ]
    assert payload["live_data_setup_summary"]["selected_provider_classes"] == [
        "ReplayMarketDataProvider"
    ]
    assert payload["live_data_setup_summary"]["dotenv_template"]["target_path"] == (
        ".env"
    )
    assert payload["live_data_setup_summary"]["dotenv_template"]["source_path"] == (
        ".env.example"
    )
    assert payload["live_data_setup_summary"]["dotenv_template"]["entries"][
        0
    ]["example"] == "POLYGON_API_KEY = your_polygon_key"
    assert payload["live_data_setup_summary"]["dotenv_template"][
        "secret_values_returned"
    ] is False
    assert (
        payload["live_data_setup_summary"]["one_shot_smoke_command"]["name"]
        == "run_api_key_pipeline_smoke"
    )
    assert payload["live_data_setup_summary"]["network_call"] is False
    assert payload["live_data_setup_summary"]["secret_values_returned"] is False
    assert payload["provider_route_summary"]["status"] == "blocked"
    assert payload["provider_route_summary"]["selected_provider_classes"] == [
        "ReplayMarketDataProvider"
    ]
    assert payload["provider_route_summary"]["network_call"] is False
    assert payload["provider_route_summary"]["secret_values_returned"] is False
    assert payload["network_call"] is False
    assert payload["live_data_required"] is False
    assert payload["hermes_runtime_started"] is False
    assert payload["telegram_send_call"] is False
    assert payload["send_call"] is False
    assert payload["order_submission"] is False
    assert payload["secret_values_returned"] is False
    assert payload["mutates_local_state"] is False
    assert payload["readiness"]["gates"]["live_data"]["status"] == "blocked"
    assert payload["live_data_smoke"]["status"] == "conflict"


def test_run_live_signal_workflow_smoke_executes_with_fake_live_metadata(
    monkeypatch,
) -> None:
    from halo_swing_mcp.tools import readiness as readiness_tools
    from halo_swing_mcp.tools import reporting as reporting_tools
    from halo_swing_mcp.tools import scoring as scoring_tools

    fake_provider_route = {
        "schema_version": "live_data_provider_route.v1",
        "status": "ready",
        "provider_factory": "get_market_data_provider",
        "selected_provider_classes": [
            "PolygonMarketDataProvider",
            "FredMacroDataProvider",
            "NewsApiDataProvider",
        ],
        "missing": [],
        "network_call": False,
        "secret_values_returned": False,
        "api_key_status": {
            "schema_version": "live_data_api_key_status.v1",
            "status": "ready",
            "providers": {
                "market": {"configured": True},
                "macro": {"configured": True},
                "news": {"configured": True},
            },
            "missing": [],
            "dotenv": {
                "supported": True,
                "disabled": False,
                "precedence": [
                    "exported environment variables",
                    "launch-directory .env",
                    "repo-root .env",
                ],
                "mutation": False,
            },
            "one_shot_smoke_command": {
                "name": "run_api_key_pipeline_smoke",
                "command": (
                    "PYTHONPATH=src ./.venv/bin/python -m "
                    "halo_swing_mcp.harness run_api_key_pipeline_smoke "
                    "--input-json "
                    "'{\"asset\":\"TQQQ\",\"timeframe\":\"swing_3d_10d\","
                    "\"symbols\":[\"QQQ\"],\"topic\":\"macro\"}' --no-audit"
                ),
                "network_call": True,
                "network_call_policy": "only_when_matching_api_key_selects_live_provider",
                "mutates_local_state": False,
                "secret_values_returned": False,
            },
        },
    }
    fake_signal = {
        "signal_id": "sig_live_tqqq",
        "run_id": "run_live_signal_smoke",
        "asset": "TQQQ",
        "underlying": "QQQ",
        "timeframe": "swing_3d_10d",
        "source_data_contract": {
            "schema_version": "scoring_source_data.v1",
            "network_call": True,
            "live_data_required": True,
        },
        "live_data_required": True,
    }
    fake_guide = {
        "live_data_required": True,
        "trade_guide_contract": {
            "live_data_required": True,
            "order_submission": False,
        },
        "trade_guide_guard": {
            "status": "ok",
            "checks": [
                {"name": "live_data_boundary_declared", "passed": True}
            ],
        },
    }
    fake_position = {
        "live_data_required": True,
        "position_management_contract": {
            "live_data_required": True,
            "order_submission": False,
        },
        "position_management_guard": {
            "status": "ok",
            "checks": [
                {"name": "live_data_boundary_declared", "passed": True}
            ],
        },
    }
    fake_report = {
        "live_data_required": True,
        "report_contract_guard": {
            "status": "ok",
            "checks": [
                {
                    "name": "report_payload_live_data_required_matches_expected",
                    "passed": True,
                }
            ],
        },
    }

    monkeypatch.setattr(
        readiness_tools,
        "get_live_data_provider_route",
        lambda: fake_provider_route,
    )
    monkeypatch.setattr(
        scoring_tools,
        "score_leverage_swing",
        lambda asset="TQQQ", timeframe="swing_3d_10d": fake_signal,
    )
    monkeypatch.setattr(
        scoring_tools,
        "generate_trade_guide",
        lambda asset="TQQQ", timeframe="swing_3d_10d": fake_guide,
    )
    monkeypatch.setattr(
        scoring_tools,
        "evaluate_position",
        lambda asset="TQQQ": fake_position,
    )
    monkeypatch.setattr(
        reporting_tools,
        "generate_latest_signal_report",
        lambda asset="TQQQ", timeframe="swing_3d_10d": fake_report,
    )

    payload = run_live_signal_workflow_smoke(
        asset="TQQQ",
        timeframe="swing_3d_10d",
    )

    assert payload["schema_version"] == "live_signal_workflow_smoke_run.v1"
    assert payload["status"] == "ok"
    assert payload["executed_tools"] == [
        "score_leverage_swing",
        "generate_trade_guide",
        "evaluate_position",
        "generate_latest_signal_report",
    ]
    assert payload["live_data_setup_summary"]["status"] == "ready"
    assert payload["live_data_setup_summary"]["ready_to_run_live_smoke"] is True
    assert payload["live_data_setup_summary"]["api_key_status"] == "ready"
    assert payload["live_data_setup_summary"]["provider_route_status"] == "ready"
    assert payload["live_data_setup_summary"]["selected_provider_classes"] == [
        "PolygonMarketDataProvider",
        "FredMacroDataProvider",
        "NewsApiDataProvider",
    ]
    assert (
        payload["live_data_setup_summary"]["next_smoke_command"]["name"]
        == "run_api_key_pipeline_smoke"
    )
    assert payload["live_data_setup_summary"]["network_call"] is False
    assert payload["live_data_setup_summary"]["secret_values_returned"] is False
    assert payload["network_call"] is True
    assert payload["live_data_required"] is True
    assert payload["hermes_runtime_started"] is False
    assert payload["telegram_send_call"] is False
    assert payload["send_call"] is False
    assert payload["order_submission"] is False
    assert payload["mutates_local_state"] is False
    assert payload["secret_values_returned"] is False
    assert all(check["passed"] for check in payload["checks"])
    serialized = repr(payload).lower()
    assert "api_key=" not in serialized


def test_run_live_signal_workflow_smoke_flags_fixture_defaults_without_keys(
    monkeypatch,
) -> None:
    clear_readiness_env(monkeypatch)

    payload = run_live_signal_workflow_smoke(
        asset="TQQQ",
        timeframe="swing_3d_10d",
    )
    failed_checks = {
        (check["tool"], check["name"])
        for check in payload["checks"]
        if not check["passed"]
    }

    assert payload["schema_version"] == "live_signal_workflow_smoke_run.v1"
    assert payload["status"] == "conflict"
    assert payload["live_data_setup_summary"]["status"] == "blocked"
    assert payload["live_data_setup_summary"]["ready_to_run_live_smoke"] is False
    assert payload["live_data_setup_summary"]["api_key_status"] == "blocked"
    assert payload["live_data_setup_summary"]["provider_route_status"] == "blocked"
    assert payload["live_data_setup_summary"]["selected_provider_classes"] == [
        "ReplayMarketDataProvider"
    ]
    assert (
        payload["live_data_setup_summary"]["next_smoke_command"]["name"]
        == "get_live_data_api_key_status"
    )
    assert payload["live_data_setup_summary"]["network_call"] is False
    assert payload["live_data_setup_summary"]["secret_values_returned"] is False
    assert payload["network_call"] is False
    assert payload["live_data_required"] is False
    assert payload["hermes_runtime_started"] is False
    assert payload["telegram_send_call"] is False
    assert payload["send_call"] is False
    assert payload["order_submission"] is False
    assert payload["mutates_local_state"] is False
    assert payload["secret_values_returned"] is False
    assert (
        "score_leverage_swing",
        "payload_live_data_required",
    ) in failed_checks
    assert (
        "score_leverage_swing",
        "source_contract_network_call",
    ) in failed_checks
    assert (
        "generate_latest_signal_report",
        "payload_live_data_required",
    ) in failed_checks


def test_run_live_recording_smoke_executes_with_fake_live_metadata(
    monkeypatch,
) -> None:
    from halo_swing_mcp.tools import readiness as readiness_tools
    from halo_swing_mcp.tools import recording as recording_tools
    from halo_swing_mcp.tools import scoring as scoring_tools

    fake_provider_route = {
        "schema_version": "live_data_provider_route.v1",
        "status": "ready",
        "provider_factory": "get_market_data_provider",
        "selected_provider_classes": [
            "PolygonMarketDataProvider",
            "FredMacroDataProvider",
            "NewsApiDataProvider",
        ],
        "missing": [],
        "network_call": False,
        "secret_values_returned": False,
        "api_key_status": {
            "schema_version": "live_data_api_key_status.v1",
            "status": "ready",
            "providers": {
                "market": {"configured": True},
                "macro": {"configured": True},
                "news": {"configured": True},
            },
            "missing": [],
            "one_shot_smoke_command": {
                "name": "run_api_key_pipeline_smoke",
                "command": (
                    "PYTHONPATH=src ./.venv/bin/python -m "
                    "halo_swing_mcp.harness run_api_key_pipeline_smoke "
                    "--input-json "
                    "'{\"asset\":\"TQQQ\",\"timeframe\":\"swing_3d_10d\","
                    "\"symbols\":[\"QQQ\"],\"topic\":\"macro\"}' --no-audit"
                ),
                "network_call": True,
                "network_call_policy": "only_when_matching_api_key_selects_live_provider",
                "mutates_local_state": False,
                "secret_values_returned": False,
            },
        },
    }
    fake_signal = {
        "signal_id": "sig_live_recording_tqqq",
        "run_id": "run_live_recording_smoke",
        "asset": "TQQQ",
        "underlying": "QQQ",
        "timeframe": "swing_3d_10d",
        "action": "BUY_WATCH",
        "source_data_contract": {
            "schema_version": "scoring_source_data.v1",
            "network_call": True,
            "live_data_required": True,
        },
        "live_data_required": True,
    }
    fake_recorded = {
        "status": "recorded",
        "signal_id": "sig_live_recording_tqqq",
        "ledger_ref": "not-returned-for-ephemeral-ledger",
        "run_journal_contract": {
            "schema_version": "run_journal.v1",
            "network_call": True,
            "db_required": False,
            "secret_values_returned": False,
        },
        "record": {
            "signal": fake_signal,
            "run_journal": {
                "schema_version": "run_journal.v1",
                "run_id": "run_live_recording_smoke",
                "signal_id": "sig_live_recording_tqqq",
                "network_call": True,
                "db_required": False,
                "secret_values_returned": False,
                "live_data_required": True,
            },
        },
        "live_data_required": True,
    }

    monkeypatch.setattr(
        readiness_tools,
        "get_live_data_provider_route",
        lambda: fake_provider_route,
    )
    monkeypatch.setattr(
        scoring_tools,
        "score_leverage_swing",
        lambda asset="TQQQ", timeframe="swing_3d_10d": fake_signal,
    )
    monkeypatch.setattr(
        recording_tools,
        "record_signal",
        lambda signal=None, ledger_path=None: fake_recorded,
    )

    payload = run_live_recording_smoke(asset="TQQQ", timeframe="swing_3d_10d")

    assert payload["schema_version"] == "live_recording_smoke_run.v1"
    assert payload["status"] == "ok"
    assert payload["executed_tools"] == ["score_leverage_swing", "record_signal"]
    assert payload["live_data_setup_summary"]["status"] == "ready"
    assert payload["live_data_setup_summary"]["ready_to_run_live_smoke"] is True
    assert payload["live_data_setup_summary"]["api_key_status"] == "ready"
    assert payload["live_data_setup_summary"]["provider_route_status"] == "ready"
    assert payload["live_data_setup_summary"]["selected_provider_classes"] == [
        "PolygonMarketDataProvider",
        "FredMacroDataProvider",
        "NewsApiDataProvider",
    ]
    assert (
        payload["live_data_setup_summary"]["next_smoke_command"]["name"]
        == "run_api_key_pipeline_smoke"
    )
    assert payload["live_data_setup_summary"]["network_call"] is False
    assert payload["live_data_setup_summary"]["secret_values_returned"] is False
    assert payload["network_call"] is True
    assert payload["live_data_required"] is True
    assert payload["ledger_persisted"] is False
    assert payload["mutates_local_state"] is False
    assert payload["recording_summary"]["ledger_ref"] == "ephemeral"
    assert payload["hermes_runtime_started"] is False
    assert payload["telegram_send_call"] is False
    assert payload["send_call"] is False
    assert payload["order_submission"] is False
    assert payload["secret_values_returned"] is False
    assert all(check["passed"] for check in payload["checks"])
    payload_repr = repr(payload).lower()
    assert "polygon_api_key=test" not in payload_repr
    assert "fred_api_key=test" not in payload_repr
    assert "news_api_key=test" not in payload_repr
    assert "polygon-local-secret-key" not in payload_repr
    assert "fred-local-secret-key" not in payload_repr
    assert "news-local-secret-key" not in payload_repr


def test_run_live_recording_smoke_uses_ephemeral_ledger_by_default(
    monkeypatch,
) -> None:
    clear_readiness_env(monkeypatch)

    payload = run_live_recording_smoke(asset="TQQQ", timeframe="swing_3d_10d")
    failed_checks = {
        (check["tool"], check["name"])
        for check in payload["checks"]
        if not check["passed"]
    }

    assert payload["schema_version"] == "live_recording_smoke_run.v1"
    assert payload["status"] == "conflict"
    assert payload["live_data_setup_summary"]["status"] == "blocked"
    assert payload["live_data_setup_summary"]["ready_to_run_live_smoke"] is False
    assert payload["live_data_setup_summary"]["api_key_status"] == "blocked"
    assert payload["live_data_setup_summary"]["provider_route_status"] == "blocked"
    assert payload["live_data_setup_summary"]["selected_provider_classes"] == [
        "ReplayMarketDataProvider"
    ]
    assert (
        payload["live_data_setup_summary"]["next_smoke_command"]["name"]
        == "get_live_data_api_key_status"
    )
    assert payload["live_data_setup_summary"]["network_call"] is False
    assert payload["live_data_setup_summary"]["secret_values_returned"] is False
    assert payload["network_call"] is False
    assert payload["live_data_required"] is False
    assert payload["ledger_persisted"] is False
    assert payload["mutates_local_state"] is False
    assert payload["recording_summary"]["ledger_ref"] == "ephemeral"
    assert payload["recording_summary"]["status"] == "recorded"
    assert payload["hermes_runtime_started"] is False
    assert payload["telegram_send_call"] is False
    assert payload["send_call"] is False
    assert payload["order_submission"] is False
    assert payload["secret_values_returned"] is False
    assert (
        "score_leverage_swing",
        "payload_live_data_required",
    ) in failed_checks
    assert ("record_signal", "run_journal_network_call") in failed_checks


def test_run_live_recording_smoke_can_use_caller_supplied_ledger(
    tmp_path: Path,
    monkeypatch,
) -> None:
    clear_readiness_env(monkeypatch)
    ledger_path = tmp_path / "live_recording_smoke.jsonl"

    payload = run_live_recording_smoke(
        asset="TQQQ",
        timeframe="swing_3d_10d",
        ledger_path=str(ledger_path),
    )

    assert payload["status"] == "conflict"
    assert payload["ledger_persisted"] is True
    assert payload["mutates_local_state"] is True
    assert payload["recording_summary"]["ledger_ref"] == str(ledger_path)
    assert ledger_path.exists()


def test_run_api_key_pipeline_smoke_returns_conflict_payload_for_sub_smoke_exception(
    monkeypatch,
) -> None:
    from halo_swing_mcp.tools import readiness as readiness_tools

    clear_readiness_env(monkeypatch)
    secret_env = {
        "POLYGON_API_KEY": "polygon-secret-value",
        "FRED_API_KEY": "fred-secret-value",
        "NEWS_API_KEY": "news-secret-value",
    }
    for key, value in secret_env.items():
        monkeypatch.setenv(key, value)
    clear_local_env_cache()
    get_settings.cache_clear()

    def fake_live_data_smoke(
        symbols: list[str] | None = None,
        topic: str = "macro",
    ) -> dict[str, Any]:
        raise RuntimeError(
            "provider failed at https://provider.example/?apiKey=polygon-secret-value"
        )

    def fake_signal_workflow_smoke(
        asset: str = "TQQQ",
        timeframe: str = "swing_3d_10d",
    ) -> dict[str, Any]:
        return {
            "schema_version": "live_signal_workflow_smoke_run.v1",
            "status": "ok",
            "network_call": False,
            "live_data_required": False,
            "mutates_local_state": False,
            "secret_values_returned": False,
        }

    def fake_recording_smoke(
        asset: str = "TQQQ",
        timeframe: str = "swing_3d_10d",
    ) -> dict[str, Any]:
        return {
            "schema_version": "live_recording_smoke_run.v1",
            "status": "ok",
            "network_call": False,
            "live_data_required": False,
            "mutates_local_state": False,
            "secret_values_returned": False,
        }

    monkeypatch.setattr(readiness_tools, "run_live_data_smoke", fake_live_data_smoke)
    monkeypatch.setattr(
        readiness_tools,
        "run_live_signal_workflow_smoke",
        fake_signal_workflow_smoke,
    )
    monkeypatch.setattr(
        readiness_tools,
        "run_live_recording_smoke",
        fake_recording_smoke,
    )

    payload = run_api_key_pipeline_smoke(
        asset="TQQQ",
        timeframe="swing_3d_10d",
        symbols=["QQQ"],
        topic="macro",
    )
    failed_checks = {
        (check["tool"], check["name"])
        for check in payload["checks"]
        if not check["passed"]
    }
    serialized = json.dumps(payload, sort_keys=True)

    assert payload["status"] == "conflict"
    assert payload["readiness_summary"]["api_key_setup_status"] == "ready"
    assert payload["readiness_summary"]["provider_route_status"] == "ready"
    assert payload["readiness_summary"]["next_operator_action_name"] == (
        "run_provider_smokes"
    )
    assert payload["next_operator_action"]["name"] == "run_provider_smokes"
    assert payload["provider_route_summary"]["status"] == "ready"
    assert payload["live_data_smoke_summary"]["status"] == "conflict"
    assert payload["live_data_smoke_summary"]["error_summary"] == {
        "schema_version": "api_key_pipeline_sub_smoke_error.v1",
        "tool": "run_live_data_smoke",
        "exception_type": "RuntimeError",
        "exception_message_returned": False,
        "url_returned": False,
        "secret_values_returned": False,
    }
    assert payload["api_key_pipeline_stage_summary"]["schema_version"] == (
        "api_key_pipeline_stage_summary.v1"
    )
    assert payload["api_key_pipeline_stage_summary"]["status"] == "conflict"
    assert payload["api_key_pipeline_stage_summary"]["failed_stage_count"] == 1
    assert payload["api_key_pipeline_stage_summary"]["failed_stage_names"] == [
        "run_live_data_smoke"
    ]
    assert payload["api_key_pipeline_stage_summary"]["first_failed_stage"][
        "error_summary"
    ] == payload["live_data_smoke_summary"]["error_summary"]
    assert payload["api_key_pipeline_stage_summary"]["secret_values_returned"] is False
    assert payload["api_key_pipeline_check_summary"]["status"] == "conflict"
    assert payload["api_key_pipeline_check_summary"]["failed_check_count"] == 1
    assert payload["api_key_pipeline_check_summary"]["failed_check_keys"] == [
        "run_live_data_smoke.live_data_smoke_status_ok"
    ]
    assert payload["api_key_pipeline_check_summary"]["first_failed_check"] == {
        "tool": "run_live_data_smoke",
        "name": "live_data_smoke_status_ok",
        "key": "run_live_data_smoke.live_data_smoke_status_ok",
        "passed": False,
        "expected": "ok",
        "actual": "conflict",
        "secret_values_returned": False,
    }
    assert payload["api_key_pipeline_check_summary"]["secret_values_returned"] is False
    assert payload["api_key_pipeline_failure_summary"]["failure_category"] == (
        "smoke_failure"
    )
    assert payload["api_key_pipeline_failure_summary"]["first_failed_stage_name"] == (
        "run_live_data_smoke"
    )
    assert payload["api_key_pipeline_failure_summary"]["first_failed_check_key"] == (
        "run_live_data_smoke.live_data_smoke_status_ok"
    )
    assert payload["api_key_pipeline_failure_summary"]["next_action_name"] == (
        "run_provider_smokes"
    )
    assert (
        payload["api_key_pipeline_failure_summary"]["provider_recovery_required"]
        is False
    )
    assert payload["api_key_pipeline_failure_summary"]["secret_values_returned"] is False
    assert payload["api_key_setup_file_summary"]["ready_to_run_live_smoke"] is True
    assert payload["api_key_setup_file_summary"]["preferred_env_keys"] == [
        "POLYGON_API_KEY",
        "FRED_API_KEY",
        "NEWS_API_KEY",
    ]
    assert payload["api_key_setup_file_summary"]["secret_values_returned"] is False
    assert payload["live_data_smoke_summary"]["ready_to_run_live_smoke"] is True
    assert payload["live_data_smoke_summary"]["provider_route_status"] == "ready"
    assert ("run_live_data_smoke", "live_data_smoke_status_ok") in failed_checks
    assert ("run_live_data_smoke", "provider_route_status_ok") not in failed_checks
    assert payload["network_call"] is True
    assert payload["live_data_required"] is True
    assert payload["mutates_local_state"] is False
    assert payload["secret_values_returned"] is False
    assert "provider.example" not in serialized
    assert "apiKey" not in serialized
    for value in secret_env.values():
        assert value not in serialized


def test_run_api_key_pipeline_smoke_combines_fake_live_smokes(
    tmp_path: Path,
    monkeypatch,
) -> None:
    from halo_swing_mcp.tools import readiness as readiness_tools

    env_path = tmp_path / ".env"
    env_path.with_name(".env.example").write_text(
        "POLYGON_API_KEY=\nFRED_API_KEY=\nNEWS_API_KEY=\n",
        encoding="utf-8",
    )
    env_path.write_text(
        "POLYGON_API_KEY=test\nFRED_API_KEY=test\nNEWS_API_KEY=test\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(local_env, "REPO_ROOT_ENV_PATH", env_path)
    clear_local_env_cache()
    fake_setup_steps = expected_live_data_setup_steps(
        target_path=env_path,
        configured_provider_families=["market", "macro", "news"],
        missing_provider_families=[],
        ready_to_run_live_smoke=True,
    )
    fake_provider_setup_actions = expected_provider_setup_actions(
        market_configured_env_keys=["POLYGON_API_KEY"],
        macro_configured_env_keys=["FRED_API_KEY"],
        news_configured_env_keys=["NEWS_API_KEY"],
    )
    fake_provider_smoke_plan = expected_provider_smoke_plan(
        market_configured_env_keys=["POLYGON_API_KEY"],
        macro_configured_env_keys=["FRED_API_KEY"],
        news_configured_env_keys=["NEWS_API_KEY"],
        ready_to_run_live_smoke=True,
    )
    fake_next_operator_action = expected_next_operator_action(
        target_path=env_path,
        configured_provider_families=["market", "macro", "news"],
        missing_provider_families=[],
        ready_to_run_live_smoke=True,
    )
    fake_setup_summary = {
        "schema_version": "live_data_setup_summary.v1",
        "status": "ready",
        "ready_to_run_live_smoke": True,
        "api_key_status": "ready",
        "provider_route_status": "ready",
        "configured_provider_families": ["market", "macro", "news"],
        "provider_family_summary": {
            "required_provider_families": ["market", "macro", "news"],
            "configured_provider_families": ["market", "macro", "news"],
            "missing_provider_families": [],
            "configured_count": 3,
            "required_count": 3,
            "ready_to_run_live_smoke": True,
            "network_call": False,
            "mutates_local_state": False,
            "secret_values_returned": False,
        },
        "provider_setup_actions": fake_provider_setup_actions,
        "provider_smoke_plan": fake_provider_smoke_plan,
        "next_operator_action": fake_next_operator_action,
        "missing": [],
        "selected_provider_classes": [
            "PolygonMarketDataProvider",
            "FredMacroDataProvider",
            "NewsApiDataProvider",
        ],
        "next_smoke_command": {
            "name": "run_api_key_pipeline_smoke",
            "network_call": True,
            "mutates_local_state": False,
            "secret_values_returned": False,
        },
        "live_data_setup_steps": fake_setup_steps,
        "network_call": False,
        "mutates_local_state": False,
        "secret_values_returned": False,
    }

    def fake_readiness() -> dict[str, Any]:
        return {
            "status": "blocked",
            "gates": {
                "live_data": {
                    "ready": True,
                    "status": "ready",
                    "missing": [],
                },
            },
            "next_actions": ["migration: provide explicit_MIGRATION_GO"],
            "live_data_required": False,
        }

    def fake_api_key_status() -> dict[str, Any]:
        return {
            "schema_version": "live_data_api_key_status.v1",
            "status": "ready",
            "providers": {
                "market": fake_provider_setup_actions["market"],
                "macro": fake_provider_setup_actions["macro"],
                "news": fake_provider_setup_actions["news"],
            },
            "missing": [],
            "dotenv": {
                "supported": True,
                "disabled": False,
                "precedence": [
                    "exported environment variables",
                    "launch-directory .env",
                    "repo-root .env",
                ],
                "mutation": False,
            },
            "one_shot_smoke_command": {
                "name": "run_api_key_pipeline_smoke",
                "command": (
                    "PYTHONPATH=src ./.venv/bin/python -m "
                    "halo_swing_mcp.harness run_api_key_pipeline_smoke "
                    "--input-json "
                    "'{\"asset\":\"TQQQ\",\"timeframe\":\"swing_3d_10d\","
                    "\"symbols\":[\"QQQ\"],\"topic\":\"macro\"}' --no-audit"
                ),
                "network_call": True,
                "network_call_policy": "only_when_matching_api_key_selects_live_provider",
                "mutates_local_state": False,
                "secret_values_returned": False,
            },
        }

    def fake_live_data_smoke(
        symbols: list[str] | None = None,
        topic: str = "macro",
    ) -> dict[str, Any]:
        return {
            "schema_version": "live_data_smoke_run.v1",
            "status": "ok",
            "input": {"symbols": symbols, "topic": topic},
            "provider_route": {
                "schema_version": "live_data_provider_route.v1",
                "status": "ready",
                "provider_factory": "get_market_data_provider",
                "selected_provider_classes": [
                    "PolygonMarketDataProvider",
                    "FredMacroDataProvider",
                    "NewsApiDataProvider",
                ],
                "missing": [],
                "network_call": False,
                "secret_values_returned": False,
            },
            "network_call": True,
            "live_data_required": True,
            "live_data_setup_summary": fake_setup_summary,
            "mutates_local_state": False,
            "secret_values_returned": False,
        }

    def fake_workflow_smoke(
        asset: str = "TQQQ",
        timeframe: str = "swing_3d_10d",
    ) -> dict[str, Any]:
        return {
            "schema_version": "live_signal_workflow_smoke_run.v1",
            "status": "ok",
            "input": {"asset": asset, "timeframe": timeframe},
            "network_call": True,
            "live_data_required": True,
            "live_data_setup_summary": fake_setup_summary,
            "mutates_local_state": False,
            "secret_values_returned": False,
        }

    def fake_recording_smoke(
        asset: str = "TQQQ",
        timeframe: str = "swing_3d_10d",
    ) -> dict[str, Any]:
        return {
            "schema_version": "live_recording_smoke_run.v1",
            "status": "ok",
            "input": {"asset": asset, "timeframe": timeframe},
            "network_call": True,
            "live_data_required": True,
            "live_data_setup_summary": fake_setup_summary,
            "mutates_local_state": False,
            "secret_values_returned": False,
        }

    monkeypatch.setattr(readiness_tools, "get_integration_readiness", fake_readiness)
    monkeypatch.setattr(
        readiness_tools,
        "get_live_data_api_key_status",
        fake_api_key_status,
    )
    monkeypatch.setattr(readiness_tools, "run_live_data_smoke", fake_live_data_smoke)
    monkeypatch.setattr(
        readiness_tools,
        "run_live_signal_workflow_smoke",
        fake_workflow_smoke,
    )
    monkeypatch.setattr(
        readiness_tools,
        "run_live_recording_smoke",
        fake_recording_smoke,
    )

    payload = run_api_key_pipeline_smoke(
        asset="TQQQ",
        timeframe="swing_3d_10d",
        symbols=["QQQ"],
        topic="macro",
    )

    assert payload["schema_version"] == "api_key_pipeline_smoke_run.v1"
    assert payload["status"] == "ok"
    assert payload["readiness_summary"]["live_data_ready"] is True
    assert payload["readiness_summary"]["status"] == "blocked"
    assert payload["readiness_summary"]["api_key_setup_status"] == "ready"
    assert payload["readiness_summary"]["api_key_status"] == "ready"
    assert payload["readiness_summary"]["provider_route_status"] == "ready"
    assert payload["readiness_summary"]["ready_to_run_live_smoke"] is True
    assert payload["readiness_summary"]["next_setup_step"] == "run_provider_smokes"
    assert (
        payload["readiness_summary"]["next_operator_action_name"]
        == "run_provider_smokes"
    )
    assert payload["readiness_summary"]["next_operator_action"] == (
        payload["next_operator_action"]
    )
    assert payload["executed_tools"] == [
        "get_integration_readiness",
        "get_live_data_api_key_status",
        "run_live_data_smoke",
        "get_live_data_provider_route",
        "run_live_signal_workflow_smoke",
        "run_live_recording_smoke",
    ]
    assert payload["live_data_setup_summary"]["status"] == "ready"
    assert payload["live_data_setup_summary"]["api_key_status"] == "ready"
    assert payload["live_data_setup_summary"]["provider_route_status"] == "ready"
    assert payload["next_operator_action"] == (
        payload["live_data_setup_summary"]["next_operator_action"]
    )
    assert payload["next_operator_action"] == fake_next_operator_action
    assert payload["api_key_pipeline_stage_summary"] == {
        "schema_version": "api_key_pipeline_stage_summary.v1",
        "status": "ok",
        "stage_count": 3,
        "failed_stage_count": 0,
        "failed_stage_names": [],
        "first_failed_stage": None,
        "stages": [
            {
                "stage_name": "run_live_data_smoke",
                "status": "ok",
                "failed": False,
                "error_summary": None,
                "provider_error_summary_count": 0,
                "provider_recovery_smoke_count": 0,
                "next_provider_recovery_smoke_command_name": None,
                "ready_to_run_live_smoke": True,
                "provider_route_status": "ready",
                "network_call": True,
                "live_data_required": True,
                "mutates_local_state": False,
                "secret_values_returned": False,
            },
            {
                "stage_name": "run_live_signal_workflow_smoke",
                "status": "ok",
                "failed": False,
                "error_summary": None,
                "provider_error_summary_count": 0,
                "provider_recovery_smoke_count": 0,
                "next_provider_recovery_smoke_command_name": None,
                "ready_to_run_live_smoke": True,
                "provider_route_status": "ready",
                "network_call": True,
                "live_data_required": True,
                "mutates_local_state": False,
                "secret_values_returned": False,
            },
            {
                "stage_name": "run_live_recording_smoke",
                "status": "ok",
                "failed": False,
                "error_summary": None,
                "provider_error_summary_count": 0,
                "provider_recovery_smoke_count": 0,
                "next_provider_recovery_smoke_command_name": None,
                "ready_to_run_live_smoke": True,
                "provider_route_status": "ready",
                "network_call": True,
                "live_data_required": True,
                "mutates_local_state": False,
                "secret_values_returned": False,
            },
        ],
        "network_call": False,
        "mutates_local_state": False,
        "secret_values_returned": False,
    }
    assert payload["api_key_pipeline_check_summary"] == {
        "schema_version": "api_key_pipeline_check_summary.v1",
        "status": "ok",
        "check_count": 9,
        "passed_check_count": 9,
        "failed_check_count": 0,
        "failed_check_keys": [],
        "tools_with_failures": [],
        "tool_failure_counts": {},
        "first_failed_check": None,
        "failed_checks": [],
        "network_call": False,
        "mutates_local_state": False,
        "secret_values_returned": False,
    }
    assert payload["api_key_pipeline_failure_summary"] == {
        "schema_version": "api_key_pipeline_failure_summary.v1",
        "status": "ok",
        "has_failures": False,
        "failure_category": "none",
        "failed_stage_names": [],
        "failed_check_keys": [],
        "tools_with_failures": [],
        "first_failed_stage_name": None,
        "first_failed_check_key": None,
        "next_action_name": "run_provider_smokes",
        "next_action_command": fake_next_operator_action["next_provider_smoke"][
            "command"
        ],
        "next_action_is_recovery": False,
        "provider_recovery_required": False,
        "provider_recovery_item_count": 0,
        "network_call": False,
        "mutates_local_state": False,
        "secret_values_returned": False,
    }
    assert payload["api_key_setup_file_summary"] == {
        "schema_version": "api_key_setup_file_summary.v1",
        "source_path": ".env.example",
        "target_path": ".env",
        "source_exists": True,
        "target_exists": True,
        "copy_required": False,
        "copy_command": {
            "name": "copy_env_example_to_env",
            "command": "cp .env.example .env",
            "required": False,
            "source_path": ".env.example",
            "target_path": ".env",
            "network_call": False,
            "mutates_local_state": True,
            "secret_values_returned": False,
        },
        "preferred_env_keys": ["POLYGON_API_KEY", "FRED_API_KEY", "NEWS_API_KEY"],
        "preferred_env_key_count": 3,
        "configured_provider_families": ["market", "macro", "news"],
        "missing_provider_families": [],
        "configured_provider_family_count": 3,
        "required_provider_family_count": 3,
        "next_setup_step": "run_provider_smokes",
        "ready_to_run_live_smoke": True,
        "network_call": False,
        "mutates_local_state": False,
        "secret_values_returned": False,
    }
    assert payload["api_key_dotenv_loading_summary"] == {
        "schema_version": "api_key_dotenv_loading_summary.v1",
        "dotenv_supported": True,
        "dotenv_loading_enabled": True,
        "disabled": False,
        "disabled_env_key": "HALO_SWING_DISABLE_DOTENV",
        "configuration_precedence": [
            "exported environment variables",
            "launch-directory .env",
            "repo-root .env",
        ],
        "source_path": ".env.example",
        "target_path": ".env",
        "source_exists": True,
        "target_exists": True,
        "copy_required": False,
        "next_setup_step": "run_provider_smokes",
        "ready_to_run_live_smoke": True,
        "network_call": False,
        "mutates_local_state": False,
        "secret_values_returned": False,
    }
    assert payload["api_key_provider_selection_summary"] == {
        "schema_version": "api_key_provider_selection_summary.v1",
        "status": "ready",
        "provider_factory": "get_market_data_provider",
        "selected_provider_classes": [
            "PolygonMarketDataProvider",
            "FredMacroDataProvider",
            "NewsApiDataProvider",
        ],
        "selected_provider_class_count": 3,
        "configured_provider_families": ["market", "macro", "news"],
        "configured_provider_family_count": 3,
        "missing_provider_families": [],
        "configured_env_keys_by_provider_family": {
            "market": ["POLYGON_API_KEY"],
            "macro": ["FRED_API_KEY"],
            "news": ["NEWS_API_KEY"],
        },
        "selected_provider_by_family": {
            "market": "polygon",
            "macro": "fred",
            "news": "newsapi",
        },
        "ready_to_run_live_smoke": True,
        "network_call": False,
        "mutates_local_state": False,
        "secret_values_returned": False,
    }
    assert payload["api_key_integration_status_summary"] == {
        "schema_version": "api_key_integration_status_summary.v1",
        "status": "ready",
        "api_keys_configured": True,
        "dotenv_loading_enabled": True,
        "dotenv_target_exists": True,
        "live_providers_selected": True,
        "ready_to_run_live_smoke": True,
        "configured_provider_families": ["market", "macro", "news"],
        "missing_provider_families": [],
        "selected_provider_classes": [
            "PolygonMarketDataProvider",
            "FredMacroDataProvider",
            "NewsApiDataProvider",
        ],
        "failure_category": "none",
        "has_failures": False,
        "next_action_name": "run_provider_smokes",
        "next_action_is_recovery": False,
        "next_action_network_call": True,
        "network_call": False,
        "mutates_local_state": False,
        "secret_values_returned": False,
    }
    assert payload["api_key_next_action_summary"] == {
        "schema_version": "api_key_next_action_summary.v1",
        "status": "ready",
        "current_step": "run_provider_smokes",
        "ready": True,
        "next_action_name": "run_provider_smokes",
        "next_action_status": "ready",
        "next_action_command": fake_next_operator_action["next_provider_smoke"][
            "command"
        ],
        "next_action_is_recovery": False,
        "next_action_network_call": True,
        "next_action_mutates_local_state": False,
        "provider_recovery_status": "ok",
        "provider_recovery_required": False,
        "provider_recovery_item_count": 0,
        "next_blocking_step": None,
        "blocking_step_count": 0,
        "ready_step_count": 4,
        "network_call": False,
        "mutates_local_state": False,
        "secret_values_returned": False,
    }
    assert payload["setup_status_summary"] == {
        "schema_version": "api_key_pipeline_setup_status_summary.v1",
        "status": "ready",
        "ready_to_run_live_smoke": True,
        "api_key_status": "ready",
        "provider_route_status": "ready",
        "configured_provider_families": ["market", "macro", "news"],
        "missing_provider_families": [],
        "configured_provider_family_count": 3,
        "required_provider_family_count": 3,
        "provider_smoke_count": 3,
        "ready_provider_smoke_count": 3,
        "blocked_provider_smoke_count": 0,
        "next_setup_step": "run_provider_smokes",
        "next_operator_action_name": "run_provider_smokes",
        "next_smoke_command_name": "run_api_key_pipeline_smoke",
        "next_provider_smoke": fake_next_operator_action["next_provider_smoke"],
        "next_provider_smoke_command_name": "get_market_snapshot_live_smoke",
        "selected_provider_classes": [
            "PolygonMarketDataProvider",
            "FredMacroDataProvider",
            "NewsApiDataProvider",
        ],
        "network_call": False,
        "mutates_local_state": False,
        "secret_values_returned": False,
    }
    assert payload["api_key_requirements_summary"] == (
        expected_api_key_requirements_summary(
            status="ready",
            market_configured_env_keys=["POLYGON_API_KEY"],
            macro_configured_env_keys=["FRED_API_KEY"],
            news_configured_env_keys=["NEWS_API_KEY"],
            configured_provider_families=["market", "macro", "news"],
            missing_provider_families=[],
        )
    )
    assert payload["api_key_command_summary"] == expected_api_key_command_summary(
        status="ready",
        target_path=env_path,
        market_configured_env_keys=["POLYGON_API_KEY"],
        macro_configured_env_keys=["FRED_API_KEY"],
        news_configured_env_keys=["NEWS_API_KEY"],
        ready_to_run_live_smoke=True,
    )
    assert payload["api_key_operator_checklist"] == (
        expected_api_key_operator_checklist(
            status="ready",
            current_step="run_provider_smokes",
            target_path=env_path,
            market_configured_env_keys=["POLYGON_API_KEY"],
            macro_configured_env_keys=["FRED_API_KEY"],
            news_configured_env_keys=["NEWS_API_KEY"],
            configured_provider_families=["market", "macro", "news"],
            missing_provider_families=[],
            ready_to_run_live_smoke=True,
        )
    )
    assert payload["api_key_operator_checklist"]["ready_step_names"] == [
        "prepare_dotenv",
        "fill_live_data_api_keys",
        "run_provider_smokes",
        "run_api_key_pipeline_smoke",
    ]
    assert payload["api_key_operator_checklist"]["ready_step_count"] == 4
    assert payload["api_key_operator_checklist"]["blocking_step_count"] == 0
    assert payload["api_key_operator_checklist"]["next_blocking_action"] is None
    assert payload["live_data_setup_summary"]["configured_provider_families"] == [
        "market",
        "macro",
        "news",
    ]
    assert payload["live_data_setup_summary"]["provider_family_summary"] == {
        "required_provider_families": ["market", "macro", "news"],
        "configured_provider_families": ["market", "macro", "news"],
        "missing_provider_families": [],
        "configured_count": 3,
        "required_count": 3,
        "ready_to_run_live_smoke": True,
        "network_call": False,
        "mutates_local_state": False,
        "secret_values_returned": False,
    }
    assert payload["live_data_setup_summary"]["missing"] == []
    assert payload["live_data_setup_summary"]["selected_provider_classes"] == [
        "PolygonMarketDataProvider",
        "FredMacroDataProvider",
        "NewsApiDataProvider",
    ]
    assert (
        payload["live_data_setup_summary"]["one_shot_smoke_command"]["name"]
        == "run_api_key_pipeline_smoke"
    )
    assert payload["live_data_setup_summary"]["network_call"] is False
    assert payload["live_data_setup_summary"]["secret_values_returned"] is False
    assert payload["provider_route_summary"] == {
        "schema_version": "live_data_provider_route.v1",
        "status": "ready",
        "provider_factory": "get_market_data_provider",
        "selected_provider_classes": [
            "PolygonMarketDataProvider",
            "FredMacroDataProvider",
            "NewsApiDataProvider",
        ],
        "missing": [],
        "network_call": False,
        "secret_values_returned": False,
    }
    for summary_name in (
        "live_data_smoke_summary",
        "signal_workflow_smoke_summary",
        "recording_smoke_summary",
    ):
        assert payload[summary_name]["live_data_setup_summary_status"] == "ready"
        assert payload[summary_name]["ready_to_run_live_smoke"] is True
        assert payload[summary_name]["provider_route_status"] == "ready"
        assert payload[summary_name]["provider_family_summary"] == {
            "required_provider_families": ["market", "macro", "news"],
            "configured_provider_families": ["market", "macro", "news"],
            "missing_provider_families": [],
            "configured_count": 3,
            "required_count": 3,
            "ready_to_run_live_smoke": True,
            "network_call": False,
            "mutates_local_state": False,
            "secret_values_returned": False,
        }
        assert payload[summary_name]["configured_provider_family_count"] == 3
        assert payload[summary_name]["required_provider_family_count"] == 3
        assert payload[summary_name]["missing_provider_families"] == []
        assert payload[summary_name]["live_data_setup_steps"] == fake_setup_steps
        assert payload[summary_name]["next_operator_action"] == (
            fake_next_operator_action
        )
        assert payload[summary_name]["next_setup_step"] == (
            "run_provider_smokes"
        )
        assert payload[summary_name]["setup_step_count"] == 4
        assert (
            payload[summary_name]["provider_setup_actions"]
            == fake_provider_setup_actions
        )
        assert payload[summary_name]["provider_setup_action_count"] == 3
        assert payload[summary_name]["provider_smoke_plan"] == fake_provider_smoke_plan
        assert payload[summary_name]["provider_smoke_count"] == 3
        assert payload[summary_name]["ready_provider_smoke_count"] == 3
        assert payload[summary_name]["blocked_provider_smoke_count"] == 0
        assert (
            payload[summary_name]["next_smoke_command_name"]
            == "run_api_key_pipeline_smoke"
        )
    assert payload["network_call"] is True
    assert payload["live_data_required"] is True
    assert payload["hermes_runtime_started"] is False
    assert payload["telegram_send_call"] is False
    assert payload["send_call"] is False
    assert payload["order_submission"] is False
    assert payload["mutates_local_state"] is False
    assert payload["secret_values_returned"] is False
    assert all(check["passed"] for check in payload["checks"])
    payload_repr = repr(payload).lower()
    assert "polygon_api_key=test" not in payload_repr
    assert "fred_api_key=test" not in payload_repr
    assert "news_api_key=test" not in payload_repr


def test_run_api_key_pipeline_smoke_summary_only_returns_compact_status_payload(
    monkeypatch,
) -> None:
    clear_readiness_env(monkeypatch)

    payload = run_api_key_pipeline_smoke(
        asset="TQQQ",
        timeframe="swing_3d_10d",
        symbols=["QQQ"],
        topic="macro",
        summary_only=True,
    )
    serialized = json.dumps(payload, sort_keys=True)

    assert payload["schema_version"] == "api_key_pipeline_smoke_summary_only.v1"
    assert payload["status"] == "conflict"
    assert payload["summary_only"] is True
    assert payload["input"] == {
        "asset": "TQQQ",
        "timeframe": "swing_3d_10d",
        "symbols": ["QQQ"],
        "topic": "macro",
        "summary_only": True,
    }
    assert payload["api_key_integration_status_summary"] == {
        "schema_version": "api_key_integration_status_summary.v1",
        "status": "blocked",
        "api_keys_configured": False,
        "dotenv_loading_enabled": True,
        "dotenv_target_exists": False,
        "live_providers_selected": False,
        "ready_to_run_live_smoke": False,
        "configured_provider_families": [],
        "missing_provider_families": ["market", "macro", "news"],
        "selected_provider_classes": ["ReplayMarketDataProvider"],
        "failure_category": "setup",
        "has_failures": True,
        "next_action_name": "prepare_dotenv",
        "next_action_is_recovery": False,
        "next_action_network_call": False,
        "network_call": False,
        "mutates_local_state": False,
        "secret_values_returned": False,
    }
    assert payload["api_key_next_action_summary"]["next_action_name"] == (
        "prepare_dotenv"
    )
    assert payload["setup_status_summary"]["next_setup_step"] == "prepare_dotenv"
    assert payload["api_key_requirements_summary"] == (
        expected_api_key_requirements_summary(
            status="blocked",
            market_configured_env_keys=[],
            macro_configured_env_keys=[],
            news_configured_env_keys=[],
            configured_provider_families=[],
            missing_provider_families=["market", "macro", "news"],
        )
    )
    assert payload["api_key_command_summary"] == expected_api_key_command_summary(
        status="blocked",
        target_path=local_env.REPO_ROOT_ENV_PATH,
        market_configured_env_keys=[],
        macro_configured_env_keys=[],
        news_configured_env_keys=[],
        ready_to_run_live_smoke=False,
    )
    assert payload["api_key_setup_file_summary"] == {
        "schema_version": "api_key_setup_file_summary.v1",
        "source_path": ".env.example",
        "target_path": ".env",
        "source_exists": True,
        "target_exists": False,
        "copy_required": True,
        "copy_command": {
            "name": "copy_env_example_to_env",
            "command": "cp .env.example .env",
            "required": True,
            "source_path": ".env.example",
            "target_path": ".env",
            "network_call": False,
            "mutates_local_state": True,
            "secret_values_returned": False,
        },
        "preferred_env_keys": [
            "POLYGON_API_KEY",
            "FRED_API_KEY",
            "NEWS_API_KEY",
        ],
        "preferred_env_key_count": 3,
        "configured_provider_families": [],
        "missing_provider_families": ["market", "macro", "news"],
        "configured_provider_family_count": 0,
        "required_provider_family_count": 3,
        "next_setup_step": "prepare_dotenv",
        "ready_to_run_live_smoke": False,
        "network_call": False,
        "mutates_local_state": False,
        "secret_values_returned": False,
    }
    assert payload["api_key_dotenv_loading_summary"] == {
        "schema_version": "api_key_dotenv_loading_summary.v1",
        "dotenv_supported": True,
        "dotenv_loading_enabled": True,
        "disabled": False,
        "disabled_env_key": "HALO_SWING_DISABLE_DOTENV",
        "configuration_precedence": [
            "exported environment variables",
            "launch-directory .env",
            "repo-root .env",
        ],
        "source_path": ".env.example",
        "target_path": ".env",
        "source_exists": True,
        "target_exists": False,
        "copy_required": True,
        "next_setup_step": "prepare_dotenv",
        "ready_to_run_live_smoke": False,
        "network_call": False,
        "mutates_local_state": False,
        "secret_values_returned": False,
    }
    assert (
        payload["api_key_pipeline_failure_summary"]["failure_category"] == "setup"
    )
    assert payload["api_key_pipeline_stage_summary"]["schema_version"] == (
        "api_key_pipeline_stage_summary.v1"
    )
    assert payload["api_key_pipeline_stage_summary"]["status"] == "conflict"
    assert payload["api_key_pipeline_stage_summary"]["stage_count"] == 3
    assert payload["api_key_pipeline_stage_summary"]["failed_stage_count"] == 3
    assert payload["api_key_pipeline_stage_summary"]["failed_stage_names"] == [
        "run_live_data_smoke",
        "run_live_signal_workflow_smoke",
        "run_live_recording_smoke",
    ]
    assert payload["api_key_pipeline_stage_summary"]["first_failed_stage"][
        "stage_name"
    ] == "run_live_data_smoke"
    assert payload["api_key_pipeline_stage_summary"]["first_failed_stage"][
        "provider_route_status"
    ] == "blocked"
    assert all(
        stage["secret_values_returned"] is False
        for stage in payload["api_key_pipeline_stage_summary"]["stages"]
    )
    assert payload["api_key_pipeline_stage_summary"]["secret_values_returned"] is False
    assert payload["api_key_provider_selection_summary"]["status"] == "blocked"
    assert payload["api_key_live_http_timeout_summary"] == {
        "schema_version": "api_key_live_http_timeout_summary.v1",
        "timeout_seconds": 10.0,
        "env_key": "HALO_SWING_LIVE_HTTP_TIMEOUT_SECONDS",
        "default_timeout_seconds": 10.0,
        "applies_to": [
            "PolygonMarketDataProvider",
            "FredMacroDataProvider",
            "NewsApiDataProvider",
        ],
        "network_call": False,
        "mutates_local_state": False,
        "secret_values_returned": False,
    }
    assert payload["api_key_provider_recovery_summary"] == {
        "schema_version": "api_key_provider_recovery_summary.v1",
        "status": "ok",
        "provider_recovery_required": False,
        "provider_error_count": 0,
        "provider_recovery_smoke_count": 0,
        "item_count": 0,
        "next_recovery_smoke_command_name": None,
        "next_recovery_smoke_command": None,
        "items": [],
        "network_call": False,
        "mutates_local_state": False,
        "secret_values_returned": False,
    }
    assert payload["provider_route_summary"]["status"] == "blocked"
    assert len(payload["checks"]) == 9
    assert payload["failed_provider_families"] == []
    assert payload["failed_provider_count"] == 0
    assert payload["provider_recovery_smoke_count"] == 0
    assert "live_data_smoke_summary" in payload["omitted_sections"]
    assert "signal_workflow_smoke_summary" in payload["omitted_sections"]
    assert "recording_smoke_summary" in payload["omitted_sections"]
    assert "api_key_requirements_summary" not in payload["omitted_sections"]
    assert "api_key_command_summary" not in payload["omitted_sections"]
    assert "api_key_setup_file_summary" not in payload["omitted_sections"]
    assert "api_key_dotenv_loading_summary" not in payload["omitted_sections"]
    assert "api_key_pipeline_stage_summary" not in payload["omitted_sections"]
    assert "live_data_smoke_summary" not in payload
    assert "signal_workflow_smoke_summary" not in payload
    assert "recording_smoke_summary" not in payload
    assert "api_key_provider_recovery_checklist" not in payload
    assert "provider_recovery_smokes" not in payload
    assert payload["network_call"] is False
    assert payload["live_data_required"] is False
    assert payload["hermes_runtime_started"] is False
    assert payload["telegram_send_call"] is False
    assert payload["order_submission"] is False
    assert payload["mutates_local_state"] is False
    assert payload["secret_values_returned"] is False
    assert "polygon-secret" not in serialized
    assert "fred-secret" not in serialized
    assert "news-secret" not in serialized


def test_run_api_key_pipeline_smoke_summary_only_keeps_setup_file_summary(
    monkeypatch,
) -> None:
    clear_readiness_env(monkeypatch)
    monkeypatch.setenv("POLYGON_API_KEY", "polygon-secret")
    monkeypatch.setenv("FRED_API_KEY", "fred-secret")
    monkeypatch.setenv("NEWS_API_KEY", "news-secret")
    get_settings.cache_clear()
    clear_local_env_cache()

    payload = run_api_key_pipeline_smoke(summary_only=True)
    setup_file_summary = payload["api_key_setup_file_summary"]
    serialized = json.dumps(payload, sort_keys=True)

    assert setup_file_summary["schema_version"] == "api_key_setup_file_summary.v1"
    assert setup_file_summary["source_path"] == ".env.example"
    assert setup_file_summary["target_path"] == ".env"
    assert setup_file_summary["copy_command"]["command"] == "cp .env.example .env"
    assert setup_file_summary["preferred_env_keys"] == [
        "POLYGON_API_KEY",
        "FRED_API_KEY",
        "NEWS_API_KEY",
    ]
    assert setup_file_summary["configured_provider_families"] == [
        "market",
        "macro",
        "news",
    ]
    assert setup_file_summary["missing_provider_families"] == []
    assert setup_file_summary["ready_to_run_live_smoke"] is True
    assert setup_file_summary["secret_values_returned"] is False
    assert "api_key_setup_file_summary" not in payload["omitted_sections"]
    assert "polygon-secret" not in serialized
    assert "fred-secret" not in serialized
    assert "news-secret" not in serialized


def test_run_api_key_pipeline_smoke_summary_only_keeps_pipeline_stage_summary(
    monkeypatch,
) -> None:
    clear_readiness_env(monkeypatch)
    monkeypatch.setenv("POLYGON_API_KEY", "polygon-secret")
    monkeypatch.setenv("FRED_API_KEY", "fred-secret")
    monkeypatch.setenv("NEWS_API_KEY", "news-secret")
    get_settings.cache_clear()
    clear_local_env_cache()

    payload = run_api_key_pipeline_smoke(summary_only=True)
    stage_summary = payload["api_key_pipeline_stage_summary"]
    serialized = json.dumps(payload, sort_keys=True)

    assert stage_summary["schema_version"] == (
        "api_key_pipeline_stage_summary.v1"
    )
    assert stage_summary["status"] == "conflict"
    assert stage_summary["stage_count"] == 3
    assert stage_summary["failed_stage_count"] == 3
    assert stage_summary["failed_stage_names"] == [
        "run_live_data_smoke",
        "run_live_signal_workflow_smoke",
        "run_live_recording_smoke",
    ]
    assert stage_summary["first_failed_stage"]["stage_name"] == (
        "run_live_data_smoke"
    )
    assert all(
        stage["secret_values_returned"] is False
        for stage in stage_summary["stages"]
    )
    assert stage_summary["secret_values_returned"] is False
    assert "api_key_pipeline_stage_summary" not in payload["omitted_sections"]
    assert "polygon-secret" not in serialized
    assert "fred-secret" not in serialized
    assert "news-secret" not in serialized


def test_run_api_key_pipeline_smoke_summary_only_keeps_dotenv_loading_status(
    monkeypatch,
) -> None:
    clear_readiness_env(monkeypatch)
    monkeypatch.setenv(local_env.DOTENV_DISABLED_ENV, "true")
    get_settings.cache_clear()
    clear_local_env_cache()

    payload = run_api_key_pipeline_smoke(summary_only=True)
    dotenv_summary = payload["api_key_dotenv_loading_summary"]

    assert dotenv_summary == {
        "schema_version": "api_key_dotenv_loading_summary.v1",
        "dotenv_supported": True,
        "dotenv_loading_enabled": False,
        "disabled": True,
        "disabled_env_key": "HALO_SWING_DISABLE_DOTENV",
        "configuration_precedence": [
            "exported environment variables",
            "launch-directory .env",
            "repo-root .env",
        ],
        "source_path": ".env.example",
        "target_path": ".env",
        "source_exists": True,
        "target_exists": False,
        "copy_required": True,
        "next_setup_step": "prepare_dotenv",
        "ready_to_run_live_smoke": False,
        "network_call": False,
        "mutates_local_state": False,
        "secret_values_returned": False,
    }
    assert "api_key_dotenv_loading_summary" not in payload["omitted_sections"]


def test_run_api_key_pipeline_smoke_summary_only_keeps_api_key_requirements(
    monkeypatch,
) -> None:
    clear_readiness_env(monkeypatch)
    monkeypatch.setenv("POLYGON_API_KEY", "polygon-secret")
    get_settings.cache_clear()
    clear_local_env_cache()

    payload = run_api_key_pipeline_smoke(summary_only=True)
    requirements = payload["api_key_requirements_summary"]
    serialized = json.dumps(payload, sort_keys=True)

    assert requirements["schema_version"] == (
        "api_key_pipeline_api_key_requirements_summary.v1"
    )
    assert requirements["required_env_keys"] == [
        "POLYGON_API_KEY",
        "FRED_API_KEY",
        "NEWS_API_KEY",
    ]
    assert requirements["configured_env_keys"] == ["POLYGON_API_KEY"]
    assert requirements["configured_provider_families"] == ["market"]
    assert requirements["missing_provider_families"] == ["macro", "news"]
    assert requirements["provider_requirements"]["market"]["configured"] is True
    assert requirements["provider_requirements"]["macro"]["preferred_env_key"] == (
        "FRED_API_KEY"
    )
    assert requirements["provider_requirements"]["news"]["accepted_env_keys"] == [
        "HALO_SWING_NEWS_API_KEY",
        "NEWS_API_KEY",
    ]
    assert requirements["secret_values_returned"] is False
    assert "api_key_requirements_summary" not in payload["omitted_sections"]
    assert "polygon-secret" not in serialized


def test_run_api_key_pipeline_smoke_summary_only_keeps_api_key_commands(
    monkeypatch,
) -> None:
    clear_readiness_env(monkeypatch)
    monkeypatch.setenv("POLYGON_API_KEY", "polygon-secret")
    monkeypatch.setenv("FRED_API_KEY", "fred-secret")
    monkeypatch.setenv("NEWS_API_KEY", "news-secret")
    get_settings.cache_clear()
    clear_local_env_cache()

    payload = run_api_key_pipeline_smoke(summary_only=True)
    command_summary = payload["api_key_command_summary"]
    serialized = json.dumps(payload, sort_keys=True)

    assert command_summary == expected_api_key_command_summary(
        status="ready",
        target_path=local_env.REPO_ROOT_ENV_PATH,
        market_configured_env_keys=["POLYGON_API_KEY"],
        macro_configured_env_keys=["FRED_API_KEY"],
        news_configured_env_keys=["NEWS_API_KEY"],
        ready_to_run_live_smoke=True,
    )
    assert command_summary["provider_smoke_command_count"] == 3
    assert command_summary["next_provider_smoke_command_name"] == (
        "get_market_snapshot_live_smoke"
    )
    assert command_summary["one_shot_pipeline_smoke"]["name"] == (
        "run_api_key_pipeline_smoke"
    )
    assert command_summary["secret_values_returned"] is False
    assert "api_key_command_summary" not in payload["omitted_sections"]
    assert "polygon-secret" not in serialized
    assert "fred-secret" not in serialized
    assert "news-secret" not in serialized


def test_run_api_key_pipeline_smoke_summary_only_reports_configured_live_http_timeout(
    monkeypatch,
) -> None:
    clear_readiness_env(monkeypatch)
    monkeypatch.setenv("HALO_SWING_LIVE_HTTP_TIMEOUT_SECONDS", "2.5")
    get_settings.cache_clear()
    clear_local_env_cache()

    payload = run_api_key_pipeline_smoke(summary_only=True)

    assert payload["api_key_live_http_timeout_summary"][
        "schema_version"
    ] == "api_key_live_http_timeout_summary.v1"
    assert payload["api_key_live_http_timeout_summary"]["timeout_seconds"] == 2.5
    assert payload["api_key_live_http_timeout_summary"]["env_key"] == (
        "HALO_SWING_LIVE_HTTP_TIMEOUT_SECONDS"
    )
    assert (
        payload["api_key_live_http_timeout_summary"]["secret_values_returned"]
        is False
    )


def test_run_api_key_pipeline_smoke_flags_fixture_defaults_without_keys(
    monkeypatch,
) -> None:
    clear_readiness_env(monkeypatch)

    payload = run_api_key_pipeline_smoke(
        asset="TQQQ",
        timeframe="swing_3d_10d",
        symbols=["QQQ"],
        topic="macro",
    )
    failed_checks = {
        (check["tool"], check["name"])
        for check in payload["checks"]
        if not check["passed"]
    }

    assert payload["schema_version"] == "api_key_pipeline_smoke_run.v1"
    assert payload["status"] == "conflict"
    assert payload["readiness_summary"]["live_data_ready"] is False
    assert payload["readiness_summary"]["api_key_setup_status"] == "blocked"
    assert payload["readiness_summary"]["api_key_status"] == "blocked"
    assert payload["readiness_summary"]["provider_route_status"] == "blocked"
    assert payload["readiness_summary"]["ready_to_run_live_smoke"] is False
    assert payload["readiness_summary"]["next_setup_step"] == "prepare_dotenv"
    assert (
        payload["readiness_summary"]["next_operator_action_name"]
        == "prepare_dotenv"
    )
    assert payload["readiness_summary"]["next_operator_action"] == (
        payload["next_operator_action"]
    )
    assert payload["setup_status_summary"] == {
        "schema_version": "api_key_pipeline_setup_status_summary.v1",
        "status": "blocked",
        "ready_to_run_live_smoke": False,
        "api_key_status": "blocked",
        "provider_route_status": "blocked",
        "configured_provider_families": [],
        "missing_provider_families": ["market", "macro", "news"],
        "configured_provider_family_count": 0,
        "required_provider_family_count": 3,
        "provider_smoke_count": 3,
        "ready_provider_smoke_count": 0,
        "blocked_provider_smoke_count": 3,
        "next_setup_step": "prepare_dotenv",
        "next_operator_action_name": "prepare_dotenv",
        "next_smoke_command_name": "get_live_data_api_key_status",
        "next_provider_smoke": None,
        "next_provider_smoke_command_name": None,
        "selected_provider_classes": ["ReplayMarketDataProvider"],
        "network_call": False,
        "mutates_local_state": False,
        "secret_values_returned": False,
    }
    assert payload["api_key_requirements_summary"] == (
        expected_api_key_requirements_summary(
            status="blocked",
            market_configured_env_keys=[],
            macro_configured_env_keys=[],
            news_configured_env_keys=[],
            configured_provider_families=[],
            missing_provider_families=["market", "macro", "news"],
        )
    )
    assert payload["api_key_command_summary"] == expected_api_key_command_summary(
        status="blocked",
        target_path=local_env.REPO_ROOT_ENV_PATH,
        market_configured_env_keys=[],
        macro_configured_env_keys=[],
        news_configured_env_keys=[],
        ready_to_run_live_smoke=False,
    )
    assert payload["api_key_operator_checklist"] == (
        expected_api_key_operator_checklist(
            status="blocked",
            current_step="prepare_dotenv",
            target_path=local_env.REPO_ROOT_ENV_PATH,
            market_configured_env_keys=[],
            macro_configured_env_keys=[],
            news_configured_env_keys=[],
            configured_provider_families=[],
            missing_provider_families=["market", "macro", "news"],
            ready_to_run_live_smoke=False,
        )
    )
    assert payload["api_key_operator_checklist"]["ready_step_names"] == []
    assert payload["api_key_operator_checklist"]["ready_step_count"] == 0
    assert payload["api_key_operator_checklist"]["blocking_step_count"] == 4
    assert payload["api_key_operator_checklist"]["next_blocking_action"] == {
        "name": "prepare_dotenv",
        "status": "pending",
        "command": "cp .env.example .env",
        "mutates_local_state": True,
        "network_call": False,
        "secret_values_returned": False,
    }
    assert payload["api_key_provider_recovery_checklist"] == {
        "schema_version": "api_key_provider_recovery_checklist.v1",
        "status": "ok",
        "provider_error_count": 0,
        "provider_recovery_smoke_count": 0,
        "item_count": 0,
        "items": [],
        "secret_values_returned": False,
    }
    assert payload["api_key_operator_checklist"]["provider_recovery_status"] == "ok"
    assert payload["api_key_operator_checklist"]["status"] == "blocked"
    assert payload["api_key_operator_checklist"]["current_step"] == "prepare_dotenv"
    assert (
        payload["api_key_operator_checklist"]["provider_recovery_required"] is False
    )
    assert payload["api_key_operator_checklist"]["provider_recovery_item_count"] == 0
    assert payload["api_key_operator_checklist"]["next_provider_recovery_action"] is None
    assert payload["api_key_operator_checklist"]["provider_recovery_checklist"] == (
        payload["api_key_provider_recovery_checklist"]
    )
    assert payload["next_operator_action"] == (
        payload["live_data_setup_summary"]["next_operator_action"]
    )
    assert payload["readiness_summary"]["next_operator_action"] == (
        payload["live_data_setup_summary"]["next_operator_action"]
    )
    assert payload["readiness_summary"]["next_operator_action_name"] == (
        payload["live_data_setup_summary"]["next_operator_action"]["name"]
    )
    assert payload["api_key_next_action_summary"] == {
        "schema_version": "api_key_next_action_summary.v1",
        "status": "blocked",
        "current_step": "prepare_dotenv",
        "ready": False,
        "next_action_name": "prepare_dotenv",
        "next_action_status": "pending",
        "next_action_command": "cp .env.example .env",
        "next_action_is_recovery": False,
        "next_action_network_call": False,
        "next_action_mutates_local_state": True,
        "provider_recovery_status": "ok",
        "provider_recovery_required": False,
        "provider_recovery_item_count": 0,
        "next_blocking_step": "prepare_dotenv",
        "blocking_step_count": 4,
        "ready_step_count": 0,
        "network_call": False,
        "mutates_local_state": False,
        "secret_values_returned": False,
    }
    assert payload["api_key_pipeline_stage_summary"]["schema_version"] == (
        "api_key_pipeline_stage_summary.v1"
    )
    assert payload["api_key_pipeline_stage_summary"]["status"] == "conflict"
    assert payload["api_key_pipeline_stage_summary"]["stage_count"] == 3
    assert payload["api_key_pipeline_stage_summary"]["failed_stage_count"] == 3
    assert payload["api_key_pipeline_stage_summary"]["failed_stage_names"] == [
        "run_live_data_smoke",
        "run_live_signal_workflow_smoke",
        "run_live_recording_smoke",
    ]
    assert payload["api_key_pipeline_stage_summary"]["first_failed_stage"][
        "stage_name"
    ] == "run_live_data_smoke"
    assert payload["api_key_pipeline_stage_summary"]["first_failed_stage"][
        "provider_route_status"
    ] == "blocked"
    assert all(
        stage["secret_values_returned"] is False
        for stage in payload["api_key_pipeline_stage_summary"]["stages"]
    )
    assert payload["api_key_pipeline_stage_summary"]["secret_values_returned"] is False
    assert payload["api_key_pipeline_check_summary"]["status"] == "conflict"
    assert payload["api_key_pipeline_check_summary"]["check_count"] == 9
    assert payload["api_key_pipeline_check_summary"]["failed_check_count"] == 5
    assert payload["api_key_pipeline_check_summary"]["failed_check_keys"] == [
        "get_integration_readiness.live_data_readiness_ready",
        "run_live_data_smoke.provider_route_status_ok",
        "run_live_data_smoke.live_data_smoke_status_ok",
        "run_live_signal_workflow_smoke.signal_workflow_smoke_status_ok",
        "run_live_recording_smoke.recording_smoke_status_ok",
    ]
    assert payload["api_key_pipeline_check_summary"]["tools_with_failures"] == [
        "get_integration_readiness",
        "run_live_data_smoke",
        "run_live_signal_workflow_smoke",
        "run_live_recording_smoke",
    ]
    assert payload["api_key_pipeline_check_summary"]["tool_failure_counts"] == {
        "get_integration_readiness": 1,
        "run_live_data_smoke": 2,
        "run_live_signal_workflow_smoke": 1,
        "run_live_recording_smoke": 1,
    }
    assert payload["api_key_pipeline_check_summary"]["first_failed_check"][
        "key"
    ] == "get_integration_readiness.live_data_readiness_ready"
    assert payload["api_key_pipeline_check_summary"]["secret_values_returned"] is False
    assert payload["api_key_pipeline_failure_summary"]["status"] == "conflict"
    assert payload["api_key_pipeline_failure_summary"]["failure_category"] == "setup"
    assert payload["api_key_pipeline_failure_summary"]["failed_stage_names"] == [
        "run_live_data_smoke",
        "run_live_signal_workflow_smoke",
        "run_live_recording_smoke",
    ]
    assert payload["api_key_pipeline_failure_summary"]["failed_check_keys"] == (
        payload["api_key_pipeline_check_summary"]["failed_check_keys"]
    )
    assert payload["api_key_pipeline_failure_summary"]["next_action_name"] == (
        "prepare_dotenv"
    )
    assert payload["api_key_pipeline_failure_summary"]["next_action_command"] == (
        "cp .env.example .env"
    )
    assert payload["api_key_pipeline_failure_summary"]["next_action_is_recovery"] is False
    assert (
        payload["api_key_pipeline_failure_summary"]["provider_recovery_required"]
        is False
    )
    assert payload["api_key_pipeline_failure_summary"]["secret_values_returned"] is False
    assert payload["api_key_setup_file_summary"]["preferred_env_keys"] == [
        "POLYGON_API_KEY",
        "FRED_API_KEY",
        "NEWS_API_KEY",
    ]
    assert payload["api_key_setup_file_summary"]["missing_provider_families"] == [
        "market",
        "macro",
        "news",
    ]
    assert payload["api_key_setup_file_summary"]["next_setup_step"] == (
        "prepare_dotenv"
    )
    assert payload["api_key_setup_file_summary"]["ready_to_run_live_smoke"] is False
    assert payload["api_key_setup_file_summary"]["secret_values_returned"] is False
    assert payload["api_key_dotenv_loading_summary"]["dotenv_supported"] is True
    assert payload["api_key_dotenv_loading_summary"]["dotenv_loading_enabled"] is True
    assert payload["api_key_dotenv_loading_summary"]["disabled"] is False
    assert payload["api_key_dotenv_loading_summary"]["next_setup_step"] == (
        "prepare_dotenv"
    )
    assert (
        payload["api_key_dotenv_loading_summary"]["ready_to_run_live_smoke"]
        is False
    )
    assert (
        payload["api_key_dotenv_loading_summary"]["secret_values_returned"] is False
    )
    assert payload["api_key_provider_selection_summary"] == {
        "schema_version": "api_key_provider_selection_summary.v1",
        "status": "blocked",
        "provider_factory": "get_market_data_provider",
        "selected_provider_classes": ["ReplayMarketDataProvider"],
        "selected_provider_class_count": 1,
        "configured_provider_families": [],
        "configured_provider_family_count": 0,
        "missing_provider_families": ["market", "macro", "news"],
        "configured_env_keys_by_provider_family": {
            "market": [],
            "macro": [],
            "news": [],
        },
        "selected_provider_by_family": {
            "market": None,
            "macro": None,
            "news": None,
        },
        "ready_to_run_live_smoke": False,
        "network_call": False,
        "mutates_local_state": False,
        "secret_values_returned": False,
    }
    assert payload["api_key_integration_status_summary"] == {
        "schema_version": "api_key_integration_status_summary.v1",
        "status": "blocked",
        "api_keys_configured": False,
        "dotenv_loading_enabled": True,
        "dotenv_target_exists": False,
        "live_providers_selected": False,
        "ready_to_run_live_smoke": False,
        "configured_provider_families": [],
        "missing_provider_families": ["market", "macro", "news"],
        "selected_provider_classes": ["ReplayMarketDataProvider"],
        "failure_category": "setup",
        "has_failures": True,
        "next_action_name": "prepare_dotenv",
        "next_action_is_recovery": False,
        "next_action_network_call": False,
        "network_call": False,
        "mutates_local_state": False,
        "secret_values_returned": False,
    }
    assert payload["api_key_live_http_timeout_summary"] == {
        "schema_version": "api_key_live_http_timeout_summary.v1",
        "timeout_seconds": 10.0,
        "env_key": "HALO_SWING_LIVE_HTTP_TIMEOUT_SECONDS",
        "default_timeout_seconds": 10.0,
        "applies_to": [
            "PolygonMarketDataProvider",
            "FredMacroDataProvider",
            "NewsApiDataProvider",
        ],
        "network_call": False,
        "mutates_local_state": False,
        "secret_values_returned": False,
    }
    assert payload["live_data_smoke_summary"]["status"] == "conflict"
    assert payload["live_data_smoke_summary"]["live_data_setup_summary_status"] == (
        "blocked"
    )
    assert payload["live_data_smoke_summary"]["ready_to_run_live_smoke"] is False
    assert payload["live_data_smoke_summary"]["provider_route_status"] == "blocked"
    assert payload["live_data_smoke_summary"]["live_data_setup_steps"] == (
        payload["live_data_setup_summary"]["live_data_setup_steps"]
    )
    assert payload["live_data_smoke_summary"]["next_operator_action"] == (
        payload["live_data_setup_summary"]["next_operator_action"]
    )
    assert payload["live_data_smoke_summary"]["next_setup_step"] == (
        payload["live_data_setup_summary"]["live_data_setup_steps"]["next_step"]
    )
    assert payload["live_data_smoke_summary"]["setup_step_count"] == 4
    assert payload["live_data_smoke_summary"]["provider_setup_actions"] == (
        payload["live_data_setup_summary"]["provider_setup_actions"]
    )
    assert payload["live_data_smoke_summary"]["provider_setup_action_count"] == 3
    assert payload["live_data_smoke_summary"]["provider_smoke_plan"] == (
        payload["live_data_setup_summary"]["provider_smoke_plan"]
    )
    assert payload["live_data_smoke_summary"]["provider_smoke_count"] == 3
    assert payload["live_data_smoke_summary"]["ready_provider_smoke_count"] == 0
    assert payload["live_data_smoke_summary"]["blocked_provider_smoke_count"] == 3
    assert (
        payload["live_data_smoke_summary"]["next_smoke_command_name"]
        == "get_live_data_api_key_status"
    )
    assert payload["live_data_smoke_summary"]["provider_family_summary"] == {
        "required_provider_families": ["market", "macro", "news"],
        "configured_provider_families": [],
        "missing_provider_families": ["market", "macro", "news"],
        "configured_count": 0,
        "required_count": 3,
        "ready_to_run_live_smoke": False,
        "network_call": False,
        "mutates_local_state": False,
        "secret_values_returned": False,
    }
    assert payload["live_data_smoke_summary"]["configured_provider_family_count"] == 0
    assert payload["live_data_smoke_summary"]["required_provider_family_count"] == 3
    assert payload["live_data_smoke_summary"]["missing_provider_families"] == [
        "market",
        "macro",
        "news",
    ]
    assert payload["live_data_setup_summary"]["status"] == "blocked"
    assert payload["live_data_setup_summary"]["api_key_status"] == "blocked"
    assert payload["live_data_setup_summary"]["provider_route_status"] == "blocked"
    assert payload["live_data_setup_summary"]["provider_family_summary"] == {
        "required_provider_families": ["market", "macro", "news"],
        "configured_provider_families": [],
        "missing_provider_families": ["market", "macro", "news"],
        "configured_count": 0,
        "required_count": 3,
        "ready_to_run_live_smoke": False,
        "network_call": False,
        "mutates_local_state": False,
        "secret_values_returned": False,
    }
    assert payload["live_data_setup_summary"]["missing"] == [
        "market_ohlcv_api_key",
        "macro_api_key",
        "news_api_key",
    ]
    assert payload["live_data_setup_summary"]["selected_provider_classes"] == [
        "ReplayMarketDataProvider"
    ]
    assert (
        payload["live_data_setup_summary"]["one_shot_smoke_command"]["name"]
        == "run_api_key_pipeline_smoke"
    )
    assert payload["live_data_setup_summary"]["network_call"] is False
    assert payload["live_data_setup_summary"]["secret_values_returned"] is False
    assert payload["provider_route_summary"]["status"] == "blocked"
    assert payload["provider_route_summary"]["selected_provider_classes"] == [
        "ReplayMarketDataProvider"
    ]
    assert payload["signal_workflow_smoke_summary"]["status"] == "conflict"
    assert payload["signal_workflow_smoke_summary"][
        "live_data_setup_summary_status"
    ] == "blocked"
    assert payload["signal_workflow_smoke_summary"]["ready_to_run_live_smoke"] is False
    assert (
        payload["signal_workflow_smoke_summary"]["provider_route_status"]
        == "blocked"
    )
    assert (
        payload["signal_workflow_smoke_summary"]["next_smoke_command_name"]
        == "get_live_data_api_key_status"
    )
    assert payload["signal_workflow_smoke_summary"]["live_data_setup_steps"] == (
        payload["live_data_setup_summary"]["live_data_setup_steps"]
    )
    assert payload["signal_workflow_smoke_summary"]["next_operator_action"] == (
        payload["live_data_setup_summary"]["next_operator_action"]
    )
    assert payload["signal_workflow_smoke_summary"]["next_setup_step"] == (
        payload["live_data_setup_summary"]["live_data_setup_steps"]["next_step"]
    )
    assert payload["signal_workflow_smoke_summary"]["setup_step_count"] == 4
    assert payload["signal_workflow_smoke_summary"]["provider_setup_actions"] == (
        payload["live_data_setup_summary"]["provider_setup_actions"]
    )
    assert (
        payload["signal_workflow_smoke_summary"]["provider_setup_action_count"]
        == 3
    )
    assert payload["signal_workflow_smoke_summary"]["provider_smoke_plan"] == (
        payload["live_data_setup_summary"]["provider_smoke_plan"]
    )
    assert payload["signal_workflow_smoke_summary"]["provider_smoke_count"] == 3
    assert (
        payload["signal_workflow_smoke_summary"]["ready_provider_smoke_count"]
        == 0
    )
    assert (
        payload["signal_workflow_smoke_summary"]["blocked_provider_smoke_count"]
        == 3
    )
    assert (
        payload["signal_workflow_smoke_summary"][
            "configured_provider_family_count"
        ]
        == 0
    )
    assert payload["signal_workflow_smoke_summary"]["missing_provider_families"] == [
        "market",
        "macro",
        "news",
    ]
    assert payload["recording_smoke_summary"]["status"] == "conflict"
    assert payload["recording_smoke_summary"]["live_data_setup_summary_status"] == (
        "blocked"
    )
    assert payload["recording_smoke_summary"]["ready_to_run_live_smoke"] is False
    assert payload["recording_smoke_summary"]["provider_route_status"] == "blocked"
    assert (
        payload["recording_smoke_summary"]["next_smoke_command_name"]
        == "get_live_data_api_key_status"
    )
    assert payload["recording_smoke_summary"]["live_data_setup_steps"] == (
        payload["live_data_setup_summary"]["live_data_setup_steps"]
    )
    assert payload["recording_smoke_summary"]["next_operator_action"] == (
        payload["live_data_setup_summary"]["next_operator_action"]
    )
    assert payload["recording_smoke_summary"]["next_setup_step"] == (
        payload["live_data_setup_summary"]["live_data_setup_steps"]["next_step"]
    )
    assert payload["recording_smoke_summary"]["setup_step_count"] == 4
    assert payload["recording_smoke_summary"]["provider_setup_actions"] == (
        payload["live_data_setup_summary"]["provider_setup_actions"]
    )
    assert payload["recording_smoke_summary"]["provider_setup_action_count"] == 3
    assert payload["recording_smoke_summary"]["provider_smoke_plan"] == (
        payload["live_data_setup_summary"]["provider_smoke_plan"]
    )
    assert payload["recording_smoke_summary"]["provider_smoke_count"] == 3
    assert payload["recording_smoke_summary"]["ready_provider_smoke_count"] == 0
    assert payload["recording_smoke_summary"]["blocked_provider_smoke_count"] == 3
    assert payload["recording_smoke_summary"]["provider_family_summary"] == {
        "required_provider_families": ["market", "macro", "news"],
        "configured_provider_families": [],
        "missing_provider_families": ["market", "macro", "news"],
        "configured_count": 0,
        "required_count": 3,
        "ready_to_run_live_smoke": False,
        "network_call": False,
        "mutates_local_state": False,
        "secret_values_returned": False,
    }
    assert payload["recording_smoke_summary"]["required_provider_family_count"] == 3
    assert payload["network_call"] is False
    assert payload["live_data_required"] is False
    assert payload["hermes_runtime_started"] is False
    assert payload["telegram_send_call"] is False
    assert payload["send_call"] is False
    assert payload["order_submission"] is False
    assert payload["mutates_local_state"] is False
    assert payload["secret_values_returned"] is False
    assert (
        "get_integration_readiness",
        "live_data_readiness_ready",
    ) in failed_checks
    assert ("run_live_data_smoke", "live_data_smoke_status_ok") in failed_checks
    assert ("run_live_data_smoke", "provider_route_status_ok") in failed_checks
    assert (
        "run_live_signal_workflow_smoke",
        "signal_workflow_smoke_status_ok",
    ) in failed_checks
    assert ("run_live_recording_smoke", "recording_smoke_status_ok") in failed_checks


def test_integration_readiness_configured_credential_schema_is_stable(
    tmp_path: Path,
    monkeypatch,
) -> None:
    clear_readiness_env(monkeypatch)
    credentials_path = tmp_path / "credentials.enc.json"
    save_binance_credentials(
        api_key="abcde12345key",
        api_secret="super-secret",
        passphrase="local-passphrase",
        credentials_path=str(credentials_path),
    )

    payload = get_integration_readiness(binance_credentials_path=str(credentials_path))

    for gate_name in ("binance_testnet_read_only", "live_order_submission"):
        credentials = payload["gates"][gate_name]["evidence"]["credentials"]
        assert list(credentials) == EXPECTED_CONFIGURED_CREDENTIAL_STATUS_KEYS
        assert list(credentials["kdf"]) == EXPECTED_SAFE_CREDENTIAL_KDF_KEYS
        assert list(credentials["cipher"]) == EXPECTED_SAFE_CREDENTIAL_CIPHER_KEYS
        assert (
            list(credentials["credential_policy"])
            == EXPECTED_BINANCE_CREDENTIAL_POLICY_KEYS
        )
        assert credentials["configured"] is True
        assert credentials["api_key_hint"] == "abcde...5key"
        assert credentials["kdf"]["name"] == "PBKDF2HMAC-SHA256"
        assert credentials["cipher"]["name"] == "Fernet"
        assert credentials["secret_values_returned"] is False
        assert credentials["passphrase_persisted"] is False
        assert credentials["live_data_required"] is False

    serialized = json.dumps(payload)
    assert "abcde12345key" not in serialized
    assert "super-secret" not in serialized
    assert "local-passphrase" not in serialized
    assert "salt_b64" not in serialized
    assert '"token":' not in serialized


def test_integration_readiness_uses_safe_local_evidence(tmp_path: Path, monkeypatch) -> None:
    hermes_config = tmp_path / "hermes.yaml"
    credentials_path = tmp_path / "credentials.enc.json"
    hermes_config.write_text("mcp_servers: {}\n", encoding="utf-8")
    save_binance_credentials(
        api_key="abcde12345key",
        api_secret="super-secret",
        passphrase="local-passphrase",
        credentials_path=str(credentials_path),
    )
    monkeypatch.setenv("FRED_API_KEY", "configured")
    monkeypatch.setenv("NEWS_API_KEY", "configured")
    monkeypatch.setenv("HALO_SWING_MACRO_DATA_MODE", "live")
    monkeypatch.setenv("HALO_SWING_NEWS_DATA_MODE", "live")
    monkeypatch.setenv("HALO_SWING_BINANCE_ENABLE_LIVE_TRADING", "true")
    get_settings.cache_clear()

    payload = get_integration_readiness(
        hermes_config_path=str(hermes_config),
        hermes_mcp_config_registered=True,
        telegram_gateway_configured=True,
        migration_go_approved=True,
        repository_go_approved=True,
        binance_credentials_path=str(credentials_path),
        binance_passphrase_confirmed=True,
        binance_trade_only_permission_attested=True,
        live_order_approved=True,
        btc_risk_settings_path=str(tmp_path / "risk_settings.json"),
        market_data_source_configured=True,
    )

    assert payload["status"] == "ready"
    assert payload["next_actions"] == []
    assert all(gate["ready"] for gate in payload["gates"].values())
    assert payload["gates"]["hermes"]["evidence"]["config_path_exists"] is True
    assert payload["gates"]["hermes"]["evidence"]["config_path_is_absolute"] is True
    assert payload["gates"]["hermes"]["evidence"]["mcp_config_registered"] is True
    assert payload["gates"]["telegram"]["evidence"]["gateway_configured"] is True
    assert payload["gates"]["telegram"]["evidence"]["send_call"] is False
    assert payload["gates"]["binance_testnet_read_only"]["evidence"]["credentials"]["configured"] is True
    assert payload["gates"]["binance_testnet_read_only"]["evidence"]["credentials"]["api_key_hint"] == "abcde...5key"
    assert payload["gates"]["live_order_submission"]["ready"] is True
    assert payload["gates"]["live_order_submission"]["evidence"]["order_submission"] is False
    assert (
        payload["gates"]["live_order_submission"]["evidence"]["credentials"]["credential_policy"][
            "withdraw_permission_allowed"
        ]
        is False
    )
    serialized = json.dumps(payload)
    assert "abcde12345key" not in serialized
    assert "api_secret" not in serialized
    assert "super-secret" not in serialized
    assert "local-passphrase" not in serialized
    assert "salt_b64" not in serialized
    assert '"token":' not in serialized


def test_integration_readiness_normalizes_public_path_inputs(
    tmp_path: Path,
    monkeypatch,
) -> None:
    clear_readiness_env(monkeypatch)
    hermes_config = tmp_path / "hermes.yaml"
    credentials_path = tmp_path / "credentials.enc.json"
    risk_settings_path = tmp_path / "risk_settings.json"
    hermes_config.write_text("mcp_servers: {}\n", encoding="utf-8")
    save_binance_credentials(
        api_key="abcde12345key",
        api_secret="super-secret",
        passphrase="local-passphrase",
        credentials_path=str(credentials_path),
    )
    monkeypatch.setenv("HALO_SWING_BINANCE_ENABLE_LIVE_TRADING", "true")
    get_settings.cache_clear()

    payload = get_integration_readiness(
        hermes_config_path=f" {hermes_config} ",
        hermes_mcp_config_registered=True,
        telegram_configured=True,
        migration_go_approved=True,
        repository_go_approved=True,
        binance_credentials_path=f" {credentials_path} ",
        binance_passphrase_confirmed=True,
        binance_trade_only_permission_attested=True,
        live_order_approved=True,
        btc_risk_settings_path=f" {risk_settings_path} ",
        market_data_source_configured=True,
        macro_source_configured=True,
        news_source_configured=True,
    )

    assert payload["status"] == "ready"
    assert payload["next_actions"] == []
    assert payload["gates"]["hermes"]["evidence"]["config_path"] == str(hermes_config)
    assert payload["gates"]["telegram"]["evidence"]["telegram_configured"] is True
    assert (
        payload["gates"]["binance_testnet_read_only"]["evidence"]["credentials"][
            "credentials_path"
        ]
        == str(credentials_path)
    )
    assert (
        payload["gates"]["live_order_submission"]["evidence"]["credentials"][
            "configured"
        ]
        is True
    )
    serialized = json.dumps(payload)
    assert "abcde12345key" not in serialized
    assert "api_secret" not in serialized
    assert "super-secret" not in serialized
    assert "local-passphrase" not in serialized
    assert "salt_b64" not in serialized
    assert '"token":' not in serialized


def test_integration_readiness_normalizes_env_hermes_config_path(
    tmp_path: Path,
    monkeypatch,
) -> None:
    clear_readiness_env(monkeypatch)
    hermes_config = tmp_path / "hermes.yaml"
    missing_credentials = tmp_path / "missing.enc.json"
    hermes_config.write_text("mcp_servers: {}\n", encoding="utf-8")
    monkeypatch.setenv("HALO_SWING_HERMES_CONFIG_PATH", f" {hermes_config} ")
    get_settings.cache_clear()

    payload = get_integration_readiness(
        hermes_mcp_config_registered=True,
        binance_credentials_path=str(missing_credentials),
    )
    hermes_gate = payload["gates"]["hermes"]

    assert hermes_gate["status"] == "ready"
    assert hermes_gate["missing"] == []
    assert hermes_gate["evidence"]["config_path"] == str(hermes_config)
    assert hermes_gate["evidence"]["config_path_exists"] is True
    assert hermes_gate["evidence"]["config_path_is_absolute"] is True


def test_integration_readiness_accepts_env_hermes_registration_flag(
    tmp_path: Path,
    monkeypatch,
) -> None:
    clear_readiness_env(monkeypatch)
    hermes_config = tmp_path / "hermes.yaml"
    missing_credentials = tmp_path / "missing.enc.json"
    hermes_config.write_text("mcp_servers: {}\n", encoding="utf-8")
    monkeypatch.setenv("HALO_SWING_HERMES_CONFIG_PATH", str(hermes_config))
    monkeypatch.setenv("HALO_SWING_HERMES_MCP_CONFIG_REGISTERED", " true ")
    get_settings.cache_clear()

    payload = get_integration_readiness(
        binance_credentials_path=str(missing_credentials),
    )
    hermes_gate = payload["gates"]["hermes"]

    assert hermes_gate["status"] == "ready"
    assert hermes_gate["missing"] == []
    assert hermes_gate["evidence"]["config_path"] == str(hermes_config)
    assert hermes_gate["evidence"]["mcp_config_registered"] is True


def test_integration_readiness_explicit_hermes_registration_overrides_env(
    tmp_path: Path,
    monkeypatch,
) -> None:
    clear_readiness_env(monkeypatch)
    hermes_config = tmp_path / "hermes.yaml"
    missing_credentials = tmp_path / "missing.enc.json"
    hermes_config.write_text("mcp_servers: {}\n", encoding="utf-8")
    monkeypatch.setenv("HALO_SWING_HERMES_CONFIG_PATH", str(hermes_config))
    monkeypatch.setenv("HALO_SWING_HERMES_MCP_CONFIG_REGISTERED", "true")
    get_settings.cache_clear()

    payload = get_integration_readiness(
        hermes_mcp_config_registered=False,
        binance_credentials_path=str(missing_credentials),
    )
    hermes_gate = payload["gates"]["hermes"]

    assert hermes_gate["status"] == "blocked"
    assert hermes_gate["missing"] == ["hermes_mcp_config_registration"]
    assert hermes_gate["evidence"]["mcp_config_registered"] is False


def test_integration_readiness_rejects_env_hermes_registration_flag_before_credentials(
    tmp_path: Path,
    monkeypatch,
) -> None:
    clear_readiness_env(monkeypatch)
    monkeypatch.setenv("HALO_SWING_HERMES_MCP_CONFIG_REGISTERED", "yes")
    get_settings.cache_clear()

    def fail_credential_status(*_args, **_kwargs):
        raise AssertionError("credential status must not run before Hermes env validation")

    monkeypatch.setattr(
        "halo_swing_mcp.tools.readiness.get_binance_credentials_status",
        fail_credential_status,
    )

    with pytest.raises(
        ValueError,
        match="HALO_SWING_HERMES_MCP_CONFIG_REGISTERED must be 'true' or 'false'",
    ):
        get_integration_readiness(
            binance_credentials_path=str(tmp_path / "missing.enc.json"),
        )


def test_integration_readiness_rejects_env_hermes_config_path_without_fallback(
    tmp_path: Path,
    monkeypatch,
) -> None:
    clear_readiness_env(monkeypatch)
    invalid_cases = [
        (
            "",
            "HALO_SWING_HERMES_CONFIG_PATH must be a nonempty string",
        ),
        (
            "   ",
            "HALO_SWING_HERMES_CONFIG_PATH must be a nonempty string",
        ),
        (
            f"{tmp_path / 'hermes'}\x7f.yaml",
            "HALO_SWING_HERMES_CONFIG_PATH must not contain control characters",
        ),
    ]

    for env_value, expected_error in invalid_cases:
        monkeypatch.setenv("HALO_SWING_HERMES_CONFIG_PATH", env_value)
        get_settings.cache_clear()

        with pytest.raises(ValueError, match=expected_error):
            get_integration_readiness(
                binance_credentials_path=f"{tmp_path / 'credentials.enc.json'}\n",
            )


def test_integration_readiness_normalizes_env_binance_credentials_path(
    tmp_path: Path,
    monkeypatch,
) -> None:
    clear_readiness_env(monkeypatch)
    credentials_path = tmp_path / "credentials.enc.json"
    monkeypatch.setenv(
        "HALO_SWING_BINANCE_CREDENTIALS_PATH",
        f" {credentials_path} ",
    )
    get_settings.cache_clear()

    try:
        payload = get_integration_readiness()
    finally:
        get_settings.cache_clear()

    for gate_name in ("binance_testnet_read_only", "live_order_submission"):
        credentials = payload["gates"][gate_name]["evidence"]["credentials"]
        assert credentials["configured"] is False
        assert credentials["credentials_path"] == str(credentials_path)
    assert not credentials_path.exists()


def test_integration_readiness_uses_env_binance_credentials_path_without_secret_exposure(
    tmp_path: Path,
    monkeypatch,
) -> None:
    clear_readiness_env(monkeypatch)
    credentials_path = tmp_path / "credentials.enc.json"
    save_binance_credentials(
        api_key="abcde12345key",
        api_secret="super-secret",
        passphrase="local-passphrase",
        credentials_path=str(credentials_path),
    )
    monkeypatch.setenv(
        "HALO_SWING_BINANCE_CREDENTIALS_PATH",
        f" {credentials_path} ",
    )
    get_settings.cache_clear()

    try:
        payload = get_integration_readiness()
    finally:
        get_settings.cache_clear()

    for gate_name in ("binance_testnet_read_only", "live_order_submission"):
        credentials = payload["gates"][gate_name]["evidence"]["credentials"]
        assert credentials["configured"] is True
        assert credentials["credentials_path"] == str(credentials_path)
        assert credentials["api_key_hint"] == "abcde...5key"
        assert credentials["secret_values_returned"] is False

    serialized = json.dumps(payload)
    assert "abcde12345key" not in serialized
    assert "api_secret" not in serialized
    assert "super-secret" not in serialized
    assert "local-passphrase" not in serialized
    assert "salt_b64" not in serialized
    assert '"token":' not in serialized


def test_integration_readiness_rejects_env_binance_credentials_path_without_fallback(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.chdir(tmp_path)
    invalid_cases = [
        (
            "",
            "HALO_SWING_BINANCE_CREDENTIALS_PATH must be a nonempty string",
            tmp_path / "state",
        ),
        (
            "   ",
            "HALO_SWING_BINANCE_CREDENTIALS_PATH must be a nonempty string",
            tmp_path / "   ",
        ),
        (
            f"{tmp_path / 'bad'}\x7fcredentials.enc.json",
            "HALO_SWING_BINANCE_CREDENTIALS_PATH must not contain control characters",
            tmp_path / "bad\x7fcredentials.enc.json",
        ),
    ]

    for env_value, expected_error, unexpected_path in invalid_cases:
        clear_readiness_env(monkeypatch)
        monkeypatch.setenv("HALO_SWING_BINANCE_CREDENTIALS_PATH", env_value)
        get_settings.cache_clear()

        try:
            with pytest.raises(ValueError, match=expected_error):
                get_integration_readiness()
        finally:
            get_settings.cache_clear()
        assert not unexpected_path.exists()


def test_integration_readiness_uses_env_btc_risk_settings_path(
    tmp_path: Path,
    monkeypatch,
) -> None:
    clear_readiness_env(monkeypatch)
    risk_settings_path = tmp_path / "risk_settings.json"
    credentials_path = tmp_path / "credentials.enc.json"
    update_btc_risk_settings(
        emergency_kill_switch_enabled=True,
        settings_path=str(risk_settings_path),
    )
    save_binance_credentials(
        api_key="abcde12345key",
        api_secret="super-secret",
        passphrase="local-passphrase",
        credentials_path=str(credentials_path),
    )
    monkeypatch.setenv("HALO_SWING_BTC_RISK_SETTINGS_PATH", f" {risk_settings_path} ")
    get_settings.cache_clear()

    try:
        payload = get_integration_readiness(
            binance_credentials_path=str(credentials_path),
        )
    finally:
        get_settings.cache_clear()

    live_order_gate = payload["gates"]["live_order_submission"]
    assert live_order_gate["evidence"]["emergency_kill_switch_enabled"] is True
    assert live_order_gate["evidence"]["credentials"]["configured"] is True
    assert live_order_gate["evidence"]["credentials"]["api_key_hint"] == "abcde...5key"
    assert "emergency_kill_switch_disabled" in live_order_gate["missing"]
    serialized = json.dumps(payload)
    assert "abcde12345key" not in serialized
    assert "api_secret" not in serialized
    assert "super-secret" not in serialized
    assert "local-passphrase" not in serialized
    assert "salt_b64" not in serialized
    assert '"token":' not in serialized


def test_integration_readiness_rejects_env_btc_risk_settings_path_before_credentials(
    tmp_path: Path,
    monkeypatch,
) -> None:
    clear_readiness_env(monkeypatch)
    monkeypatch.setenv("HALO_SWING_BTC_RISK_SETTINGS_PATH", "   ")
    get_settings.cache_clear()

    def fail_credentials_status(*_args: object, **_kwargs: object) -> None:
        raise AssertionError("credential status must not run before risk path validation")

    monkeypatch.setattr(
        "halo_swing_mcp.tools.readiness.get_binance_credentials_status",
        fail_credentials_status,
    )

    try:
        with pytest.raises(
            ValueError,
            match="HALO_SWING_BTC_RISK_SETTINGS_PATH must be a nonempty string",
        ):
            get_integration_readiness(
                binance_credentials_path=str(tmp_path / "missing.enc.json"),
            )
    finally:
        get_settings.cache_clear()


def test_integration_readiness_uses_canonical_binance_boolean_env(
    tmp_path: Path,
    monkeypatch,
) -> None:
    clear_readiness_env(monkeypatch)
    credentials_path = tmp_path / "credentials.enc.json"
    save_binance_credentials(
        api_key="abcde12345key",
        api_secret="super-secret",
        passphrase="local-passphrase",
        credentials_path=str(credentials_path),
    )
    monkeypatch.setenv("HALO_SWING_BINANCE_TESTNET", "false")
    monkeypatch.setenv("HALO_SWING_BINANCE_FORCE_TESTNET_EXECUTION", "false")
    monkeypatch.setenv("HALO_SWING_BINANCE_ENABLE_LIVE_TRADING", "true")
    get_settings.cache_clear()

    try:
        payload = get_integration_readiness(
            binance_credentials_path=str(credentials_path),
        )
    finally:
        get_settings.cache_clear()

    binance_gate = payload["gates"]["binance_testnet_read_only"]
    live_order_gate = payload["gates"]["live_order_submission"]
    assert binance_gate["evidence"]["testnet"] is False
    assert binance_gate["evidence"]["force_testnet_execution"] is False
    assert binance_gate["evidence"]["live_trading_enabled"] is True
    assert binance_gate["evidence"]["credentials"]["configured"] is True
    assert binance_gate["evidence"]["credentials"]["api_key_hint"] == "abcde...5key"
    assert "HALO_SWING_BINANCE_TESTNET=true" in binance_gate["missing"]
    assert (
        "HALO_SWING_BINANCE_FORCE_TESTNET_EXECUTION=true"
        in binance_gate["missing"]
    )
    assert live_order_gate["evidence"]["live_trading_enabled"] is True
    assert "HALO_SWING_BINANCE_ENABLE_LIVE_TRADING=true" not in live_order_gate[
        "missing"
    ]
    serialized = json.dumps(payload)
    assert "abcde12345key" not in serialized
    assert "api_secret" not in serialized
    assert "super-secret" not in serialized
    assert "local-passphrase" not in serialized
    assert "salt_b64" not in serialized
    assert '"token":' not in serialized


def test_integration_readiness_rejects_noncanonical_binance_boolean_env(
    tmp_path: Path,
    monkeypatch,
) -> None:
    clear_readiness_env(monkeypatch)
    invalid_cases = [
        (
            "HALO_SWING_BINANCE_TESTNET",
            "yes",
            "HALO_SWING_BINANCE_TESTNET must be 'true' or 'false'",
        ),
        (
            "HALO_SWING_BINANCE_FORCE_TESTNET_EXECUTION",
            "on",
            "HALO_SWING_BINANCE_FORCE_TESTNET_EXECUTION must be 'true' or 'false'",
        ),
        (
            "HALO_SWING_BINANCE_ENABLE_LIVE_TRADING",
            "1",
            "HALO_SWING_BINANCE_ENABLE_LIVE_TRADING must be 'true' or 'false'",
        ),
    ]

    def fail_credentials_status(*_args: object, **_kwargs: object) -> None:
        raise AssertionError("credential status must not run before boolean env validation")

    monkeypatch.setattr(
        "halo_swing_mcp.tools.readiness.get_binance_credentials_status",
        fail_credentials_status,
    )

    for env_key, env_value, expected_error in invalid_cases:
        clear_readiness_env(monkeypatch)
        monkeypatch.setenv(env_key, env_value)
        get_settings.cache_clear()

        try:
            with pytest.raises(ValueError, match=expected_error):
                get_integration_readiness(
                    binance_credentials_path=str(tmp_path / "missing.enc.json"),
                )
        finally:
            get_settings.cache_clear()

    assert not (tmp_path / "missing.enc.json").exists()


def test_integration_readiness_rejects_invalid_public_inputs(
    tmp_path: Path,
    monkeypatch,
) -> None:
    missing_credentials = tmp_path / "missing.enc.json"
    invalid_cases = [
        (
            {"hermes_mcp_config_registered": "false"},
            "hermes_mcp_config_registered must be a boolean",
        ),
        (
            {"telegram_configured": "false"},
            "telegram_configured must be a boolean when provided",
        ),
        (
            {"telegram_bot_token_configured": 1},
            "telegram_bot_token_configured must be a boolean when provided",
        ),
        (
            {"telegram_gateway_configured": []},
            "telegram_gateway_configured must be a boolean when provided",
        ),
        (
            {"migration_go_approved": "true"},
            "migration_go_approved must be a boolean",
        ),
        (
            {"repository_go_approved": 1},
            "repository_go_approved must be a boolean",
        ),
        (
            {"binance_passphrase_confirmed": "false"},
            "binance_passphrase_confirmed must be a boolean",
        ),
        (
            {"binance_trade_only_permission_attested": "true"},
            "binance_trade_only_permission_attested must be a boolean",
        ),
        (
            {"live_order_approved": "false"},
            "live_order_approved must be a boolean",
        ),
        (
            {"market_data_source_configured": "true"},
            "market_data_source_configured must be a boolean when provided",
        ),
        (
            {"macro_source_configured": 0},
            "macro_source_configured must be a boolean when provided",
        ),
        (
            {"news_source_configured": "false"},
            "news_source_configured must be a boolean when provided",
        ),
        (
            {"hermes_config_path": "   "},
            "hermes_config_path must be a nonempty string",
        ),
        (
            {"binance_credentials_path": 123},
            "binance_credentials_path must be a nonempty string",
        ),
        (
            {"btc_risk_settings_path": ""},
            "btc_risk_settings_path must be a nonempty string",
        ),
    ]

    def fail_credentials_status(*_args: object, **_kwargs: object) -> None:
        raise AssertionError("credential status must not run before input validation")

    def fail_risk_settings(*_args: object, **_kwargs: object) -> None:
        raise AssertionError("risk settings must not load before input validation")

    monkeypatch.setattr(
        "halo_swing_mcp.tools.readiness.get_binance_credentials_status",
        fail_credentials_status,
    )
    monkeypatch.setattr(
        "halo_swing_mcp.tools.readiness.load_btc_risk_settings",
        fail_risk_settings,
    )

    for overrides, expected_error in invalid_cases:
        payload = {"binance_credentials_path": str(missing_credentials)}
        payload.update(overrides)
        with pytest.raises(ValueError, match=expected_error):
            get_integration_readiness(**payload)


def test_integration_readiness_rejects_path_control_character_inputs(
    tmp_path: Path,
    monkeypatch,
) -> None:
    missing_credentials = tmp_path / "missing.enc.json"
    invalid_cases = [
        (
            {"hermes_config_path": f"{tmp_path / 'hermes.yaml'}\n"},
            "hermes_config_path must not contain control characters",
        ),
        (
            {"binance_credentials_path": f"{missing_credentials}\n"},
            "binance_credentials_path must not contain control characters",
        ),
        (
            {"btc_risk_settings_path": f"{tmp_path / 'risk_settings.json'}\n"},
            "btc_risk_settings_path must not contain control characters",
        ),
    ]

    def fail_credentials_status(*_args: object, **_kwargs: object) -> None:
        raise AssertionError("credential status must not run before path validation")

    def fail_risk_settings(*_args: object, **_kwargs: object) -> None:
        raise AssertionError("risk settings must not load before path validation")

    monkeypatch.setattr(
        "halo_swing_mcp.tools.readiness.get_binance_credentials_status",
        fail_credentials_status,
    )
    monkeypatch.setattr(
        "halo_swing_mcp.tools.readiness.load_btc_risk_settings",
        fail_risk_settings,
    )

    for overrides, expected_error in invalid_cases:
        payload = {"binance_credentials_path": str(missing_credentials)}
        payload.update(overrides)
        with pytest.raises(ValueError, match=expected_error):
            get_integration_readiness(**payload)


def test_harness_rejects_invalid_readiness_input_with_failure_audit(
    tmp_path: Path,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    input_payload = {"migration_go_approved": "false"}
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "get_integration_readiness",
            "--input-json",
            json.dumps(input_payload),
            "--audit-log-path",
            str(audit_path),
        ],
        check=False,
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    events = read_audit_events(audit_log_path=str(audit_path))
    event = events[0]

    assert result.returncode != 0
    assert result.stdout == ""
    assert "migration_go_approved must be a boolean" in result.stderr
    assert "false" not in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "get_integration_readiness"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "migration_go_approved must be a boolean" in event["details"]["error"]


def test_harness_rejects_readiness_path_control_character_with_failure_audit(
    tmp_path: Path,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    credentials_path = tmp_path / "credentials.enc.json"
    invalid_credentials_path = f"{credentials_path}\n"
    input_payload = {"binance_credentials_path": invalid_credentials_path}
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "get_integration_readiness",
            "--input-json",
            json.dumps(input_payload),
            "--audit-log-path",
            str(audit_path),
        ],
        check=False,
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    events = read_audit_events(audit_log_path=str(audit_path))
    event = events[0]

    assert result.returncode != 0
    assert result.stdout == ""
    assert "binance_credentials_path must not contain control characters" in result.stderr
    assert str(credentials_path) not in result.stderr
    assert "credentials.enc.json" not in result.stderr
    assert "\\n" not in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "get_integration_readiness"
    assert event["outcome"] == "failure"
    assert event["details"]["input"]["binance_credentials_path"] == "[REDACTED]"
    assert "output_summary" not in event["details"]
    assert "binance_credentials_path must not contain control characters" in event[
        "details"
    ]["error"]
    serialized_event = json.dumps(event)
    assert invalid_credentials_path not in result.stderr
    assert invalid_credentials_path not in serialized_event
    assert not credentials_path.exists()
    assert not Path(invalid_credentials_path).exists()


def test_harness_rejects_readiness_hermes_path_control_character_without_fallback(
    tmp_path: Path,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    hermes_config_path = tmp_path / "hermes.yaml"
    invalid_hermes_config_path = f"{hermes_config_path}\n"
    input_payload = {
        "hermes_config_path": invalid_hermes_config_path,
        "binance_credentials_path": str(tmp_path / "missing.enc.json"),
    }
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "get_integration_readiness",
            "--input-json",
            json.dumps(input_payload),
            "--audit-log-path",
            str(audit_path),
        ],
        check=False,
        cwd=tmp_path,
        env={**os.environ, "PYTHONPATH": str(ROOT / "src")},
        text=True,
        capture_output=True,
    )
    events = read_audit_events(audit_log_path=str(audit_path))
    event = events[0]

    assert result.returncode != 0
    assert result.stdout == ""
    assert "hermes_config_path must not contain control characters" in result.stderr
    assert str(hermes_config_path) not in result.stderr
    assert "hermes.yaml" not in result.stderr
    assert "\\n" not in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "get_integration_readiness"
    assert event["outcome"] == "failure"
    assert event["details"]["input"]["hermes_config_path"] == invalid_hermes_config_path
    assert event["details"]["input"]["binance_credentials_path"] == "[REDACTED]"
    assert "output_summary" not in event["details"]
    assert "hermes_config_path must not contain control characters" in event[
        "details"
    ]["error"]
    assert not hermes_config_path.exists()
    assert not Path(invalid_hermes_config_path).exists()
    assert not (tmp_path / "state").exists()


def test_harness_rejects_readiness_risk_settings_path_control_without_fallback(
    tmp_path: Path,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    risk_settings_path = tmp_path / "risk_settings.json"
    invalid_risk_settings_path = f"{risk_settings_path}\n"
    input_payload = {
        "binance_credentials_path": str(tmp_path / "missing.enc.json"),
        "btc_risk_settings_path": invalid_risk_settings_path,
    }
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "get_integration_readiness",
            "--input-json",
            json.dumps(input_payload),
            "--audit-log-path",
            str(audit_path),
        ],
        check=False,
        cwd=tmp_path,
        env={**os.environ, "PYTHONPATH": str(ROOT / "src")},
        text=True,
        capture_output=True,
    )
    events = read_audit_events(audit_log_path=str(audit_path))
    event = events[0]

    assert result.returncode != 0
    assert result.stdout == ""
    assert "btc_risk_settings_path must not contain control characters" in result.stderr
    assert str(risk_settings_path) not in result.stderr
    assert "risk_settings.json" not in result.stderr
    assert "\\n" not in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "get_integration_readiness"
    assert event["outcome"] == "failure"
    assert event["details"]["input"]["binance_credentials_path"] == "[REDACTED]"
    assert (
        event["details"]["input"]["btc_risk_settings_path"]
        == invalid_risk_settings_path
    )
    assert "output_summary" not in event["details"]
    assert "btc_risk_settings_path must not contain control characters" in event[
        "details"
    ]["error"]
    assert not risk_settings_path.exists()
    assert not Path(invalid_risk_settings_path).exists()
    assert not (tmp_path / "state").exists()


def test_hermes_readiness_requires_config_path_and_registration(tmp_path: Path) -> None:
    hermes_config = tmp_path / "hermes.yaml"
    hermes_config.write_text("mcp_servers: {}\n", encoding="utf-8")

    payload = get_integration_readiness(hermes_config_path=str(hermes_config))
    hermes_gate = payload["gates"]["hermes"]

    assert payload["status"] == "blocked"
    assert hermes_gate["status"] == "blocked"
    assert hermes_gate["missing"] == ["hermes_mcp_config_registration"]
    assert hermes_gate["evidence"]["schema_version"] == "hermes_mcp_config_readiness.v1"
    assert hermes_gate["evidence"]["config_path_exists"] is True
    assert hermes_gate["evidence"]["config_path_is_absolute"] is True
    assert hermes_gate["evidence"]["mcp_config_registered"] is False
    assert hermes_gate["evidence"]["server_command"] == (
        "PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.server"
    )
    assert hermes_gate["evidence"]["runtime_started"] is False
    assert hermes_gate["evidence"]["network_call"] is False


def test_telegram_readiness_accepts_gateway_without_returning_secrets() -> None:
    payload = get_integration_readiness(
        telegram_gateway_configured=True,
        telegram_bot_token_configured=False,
    )
    telegram_gate = payload["gates"]["telegram"]

    assert payload["status"] == "blocked"
    assert telegram_gate["status"] == "ready"
    assert telegram_gate["missing"] == []
    assert telegram_gate["evidence"]["schema_version"] == "telegram_delivery_readiness.v1"
    assert telegram_gate["evidence"]["gateway_configured"] is True
    assert telegram_gate["evidence"]["bot_token_configured"] is False
    assert telegram_gate["evidence"]["delivery_preview_available"] is True
    assert telegram_gate["evidence"]["telegram_report_format_schema"] == (
        "telegram_report_format.v1"
    )
    assert telegram_gate["evidence"]["send_call"] is False
    assert telegram_gate["evidence"]["network_call"] is False
    assert telegram_gate["evidence"]["secret_values_returned"] is False


def test_live_data_readiness_requires_market_macro_and_news_sources() -> None:
    payload = get_integration_readiness(
        market_data_source_configured=True,
        macro_source_configured=False,
        news_source_configured=True,
    )
    live_data_gate = payload["gates"]["live_data"]

    assert payload["status"] == "blocked"
    assert live_data_gate["status"] == "blocked"
    assert live_data_gate["missing"] == ["macro_api_key"]
    assert live_data_gate["evidence"]["schema_version"] == "live_data_source_readiness.v1"
    assert live_data_gate["evidence"]["market_ohlcv_source_configured"] is True
    assert live_data_gate["evidence"]["macro_source_configured"] is False
    assert live_data_gate["evidence"]["news_source_configured"] is True
    assert live_data_gate["evidence"]["live_adapter_added"] is True
    assert live_data_gate["evidence"]["network_call"] is False
    assert live_data_gate["evidence"]["secret_values_returned"] is False


def test_integration_readiness_env_secrets_are_boolean_only(
    monkeypatch,
) -> None:
    clear_readiness_env(monkeypatch)
    secret_env = {
        "HALO_SWING_TELEGRAM_BOT_TOKEN": "telegram-secret-token",
        "HALO_SWING_TELEGRAM_GATEWAY_URL": "https://gateway.example/secret",
        "HALO_SWING_MARKET_DATA_API_KEY": "market-secret-key",
        "FRED_API_KEY": "fred-secret-key",
        "NEWS_API_KEY": "news-secret-key",
    }
    for key, value in secret_env.items():
        monkeypatch.setenv(key, value)
    live_mode_env = {
        "HALO_SWING_MARKET_DATA_MODE": "live",
        "HALO_SWING_MACRO_DATA_MODE": "live",
        "HALO_SWING_NEWS_DATA_MODE": "live",
    }
    for key, value in live_mode_env.items():
        monkeypatch.setenv(key, value)

    payload = get_integration_readiness(binance_credentials_path="/missing/credentials.json")
    telegram_gate = payload["gates"]["telegram"]
    live_data_gate = payload["gates"]["live_data"]
    serialized = json.dumps(payload, sort_keys=True)

    assert payload["status"] == "blocked"
    assert telegram_gate["status"] == "ready"
    assert telegram_gate["missing"] == []
    assert telegram_gate["evidence"]["bot_token_configured"] is True
    assert telegram_gate["evidence"]["gateway_configured"] is True
    assert telegram_gate["evidence"]["secret_values_returned"] is False
    assert live_data_gate["status"] == "ready"
    assert live_data_gate["missing"] == []
    assert live_data_gate["evidence"]["market_ohlcv_source_configured"] is True
    assert live_data_gate["evidence"]["macro_source_configured"] is True
    assert live_data_gate["evidence"]["news_source_configured"] is True
    assert live_data_gate["evidence"]["secret_values_returned"] is False
    assert "telegram: provide" not in payload["next_actions"]
    assert "live_data: provide" not in payload["next_actions"]
    for key, value in secret_env.items():
        assert key not in serialized
        assert value not in serialized
    for key in live_mode_env:
        assert key not in serialized


def test_integration_readiness_env_secret_aliases_are_boolean_only(
    monkeypatch,
) -> None:
    clear_readiness_env(monkeypatch)
    env_aliases = {
        "TELEGRAM_BOT_TOKEN": "telegram-alias-secret-token",
        "HALO_SWING_TELEGRAM_GATEWAY": "https://gateway.example/alias-secret",
        "POLYGON_API_KEY": "polygon-secret-key",
        "ALPACA_API_KEY": "alpaca-secret-key",
        "TIINGO_API_KEY": "tiingo-secret-key",
        "HALO_SWING_FRED_API_KEY": "fred-alias-secret-key",
        "HALO_SWING_NEWS_API_KEY": "news-alias-secret-key",
    }
    for key, value in env_aliases.items():
        monkeypatch.setenv(key, value)
    live_mode_env = {
        "HALO_SWING_MARKET_DATA_MODE": "live",
        "HALO_SWING_MACRO_DATA_MODE": "live",
        "HALO_SWING_NEWS_DATA_MODE": "live",
    }
    for key, value in live_mode_env.items():
        monkeypatch.setenv(key, value)

    payload = get_integration_readiness(binance_credentials_path="/missing/credentials.json")
    telegram_gate = payload["gates"]["telegram"]
    live_data_gate = payload["gates"]["live_data"]
    serialized = json.dumps(payload, sort_keys=True)

    assert payload["status"] == "blocked"
    assert telegram_gate["status"] == "ready"
    assert telegram_gate["missing"] == []
    assert telegram_gate["evidence"]["bot_token_configured"] is True
    assert telegram_gate["evidence"]["gateway_configured"] is True
    assert telegram_gate["evidence"]["secret_values_returned"] is False
    assert live_data_gate["status"] == "ready"
    assert live_data_gate["missing"] == []
    assert live_data_gate["evidence"]["market_ohlcv_source_configured"] is True
    assert live_data_gate["evidence"]["macro_source_configured"] is True
    assert live_data_gate["evidence"]["news_source_configured"] is True
    assert live_data_gate["evidence"]["secret_values_returned"] is False
    assert "telegram: provide" not in payload["next_actions"]
    assert "live_data: provide" not in payload["next_actions"]
    for key, value in env_aliases.items():
        assert key not in serialized
        assert value not in serialized
    for key in live_mode_env:
        assert key not in serialized


def test_integration_readiness_accepts_project_macro_api_key_alias(
    monkeypatch,
) -> None:
    clear_readiness_env(monkeypatch)
    secret_env = {
        "HALO_SWING_MARKET_DATA_API_KEY": "market-secret-key",
        "HALO_SWING_MACRO_API_KEY": "macro-project-secret-key",
        "HALO_SWING_NEWS_API_KEY": "news-secret-key",
    }
    for key, value in secret_env.items():
        monkeypatch.setenv(key, value)
    live_mode_env = {
        "HALO_SWING_MARKET_DATA_MODE": "live",
        "HALO_SWING_MACRO_DATA_MODE": "live",
        "HALO_SWING_NEWS_DATA_MODE": "live",
    }
    for key, value in live_mode_env.items():
        monkeypatch.setenv(key, value)

    payload = get_integration_readiness(binance_credentials_path="/missing/credentials.json")
    live_data_gate = payload["gates"]["live_data"]
    serialized = json.dumps(payload, sort_keys=True)

    assert payload["status"] == "blocked"
    assert live_data_gate["status"] == "ready"
    assert live_data_gate["missing"] == []
    assert live_data_gate["evidence"]["market_ohlcv_source_configured"] is True
    assert live_data_gate["evidence"]["macro_source_configured"] is True
    assert live_data_gate["evidence"]["news_source_configured"] is True
    assert live_data_gate["evidence"]["secret_values_returned"] is False
    assert "live_data: provide" not in payload["next_actions"]
    for key, value in secret_env.items():
        assert key not in serialized
        assert value not in serialized
    for key in live_mode_env:
        assert key not in serialized


def test_integration_readiness_accepts_api_keys_without_live_modes(
    monkeypatch,
) -> None:
    clear_readiness_env(monkeypatch)
    secret_env = {
        "HALO_SWING_MARKET_DATA_API_KEY": "market-secret-key",
        "HALO_SWING_MACRO_API_KEY": "macro-project-secret-key",
        "HALO_SWING_NEWS_API_KEY": "news-secret-key",
    }
    for key, value in secret_env.items():
        monkeypatch.setenv(key, value)

    payload = get_integration_readiness(binance_credentials_path="/missing/credentials.json")
    live_data_gate = payload["gates"]["live_data"]
    serialized = json.dumps(payload, sort_keys=True)

    assert live_data_gate["status"] == "ready"
    assert live_data_gate["missing"] == []
    assert live_data_gate["evidence"]["market_ohlcv_source_configured"] is True
    assert live_data_gate["evidence"]["macro_source_configured"] is True
    assert live_data_gate["evidence"]["news_source_configured"] is True
    assert live_data_gate["evidence"]["secret_values_returned"] is False
    assert "live_data: provide" not in payload["next_actions"]
    for key, value in secret_env.items():
        assert key not in serialized
        assert value not in serialized


def test_integration_readiness_accepts_local_env_aliases_without_exporting_secrets(
    tmp_path: Path,
    monkeypatch,
) -> None:
    clear_readiness_env(monkeypatch)
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("HALO_SWING_DISABLE_DOTENV", raising=False)
    hermes_config_path = tmp_path / "hermes.yaml"
    hermes_config_path.write_text("mcp_servers: {}\n", encoding="utf-8")
    secret_env = {
        "TELEGRAM_BOT_TOKEN": "telegram-local-secret-token",
        "HALO_SWING_TELEGRAM_GATEWAY_URL": "https://gateway.example/local-secret",
        "POLYGON_API_KEY": "polygon-local-secret-key",
        "HALO_SWING_FRED_API_KEY": "fred-local-secret-key",
        "NEWS_API_KEY": "news-local-secret-key",
    }
    (tmp_path / ".env").write_text(
        "\n".join(
            [
                f"HALO_SWING_HERMES_CONFIG_PATH={hermes_config_path}",
                "HALO_SWING_HERMES_MCP_CONFIG_REGISTERED=true",
                "HALO_SWING_BINANCE_PASSPHRASE_CONFIRMED=true",
                *(f"{key}={value}" for key, value in secret_env.items()),
            ]
        ),
        encoding="utf-8",
    )
    clear_local_env_cache()

    payload = get_integration_readiness(binance_credentials_path="/missing/credentials.json")
    hermes_gate = payload["gates"]["hermes"]
    telegram_gate = payload["gates"]["telegram"]
    binance_gate = payload["gates"]["binance_testnet_read_only"]
    live_data_gate = payload["gates"]["live_data"]
    serialized = json.dumps(payload, sort_keys=True)

    assert hermes_gate["status"] == "ready"
    assert hermes_gate["missing"] == []
    assert hermes_gate["evidence"]["config_path"] == str(hermes_config_path)
    assert hermes_gate["evidence"]["config_path_exists"] is True
    assert hermes_gate["evidence"]["mcp_config_registered"] is True
    assert telegram_gate["status"] == "ready"
    assert telegram_gate["missing"] == []
    assert telegram_gate["evidence"]["bot_token_configured"] is True
    assert telegram_gate["evidence"]["gateway_configured"] is True
    assert telegram_gate["evidence"]["secret_values_returned"] is False
    assert binance_gate["status"] == "blocked"
    assert binance_gate["missing"] == ["encrypted_binance_testnet_credentials"]
    assert binance_gate["evidence"]["manual_passphrase_confirmed"] is True
    assert live_data_gate["status"] == "ready"
    assert live_data_gate["missing"] == []
    assert live_data_gate["evidence"]["market_ohlcv_source_configured"] is True
    assert live_data_gate["evidence"]["macro_source_configured"] is True
    assert live_data_gate["evidence"]["news_source_configured"] is True
    assert live_data_gate["evidence"]["secret_values_returned"] is False
    assert "telegram: provide" not in payload["next_actions"]
    assert "live_data: provide" not in payload["next_actions"]
    for key, value in secret_env.items():
        assert key not in serialized
        assert value not in serialized


def test_integration_readiness_accepts_repo_root_env_from_other_cwd(
    tmp_path: Path,
    monkeypatch,
) -> None:
    clear_readiness_env(monkeypatch)
    repo_dir = tmp_path / "repo"
    run_dir = tmp_path / "runner"
    repo_dir.mkdir()
    run_dir.mkdir()
    repo_env = repo_dir / ".env"
    repo_example = repo_dir / ".env.example"
    monkeypatch.setattr(local_env, "REPO_ROOT_ENV_PATH", repo_env)
    monkeypatch.chdir(run_dir)
    monkeypatch.delenv("HALO_SWING_DISABLE_DOTENV", raising=False)
    hermes_config_path = repo_dir / "hermes.yaml"
    hermes_config_path.write_text("mcp_servers: {}\n", encoding="utf-8")
    secret_env = {
        "HALO_SWING_TELEGRAM_BOT_TOKEN": "telegram-repo-secret-token",
        "HALO_SWING_TELEGRAM_GATEWAY": "https://gateway.example/repo-secret",
        "HALO_SWING_MARKET_DATA_API_KEY": "market-repo-secret-key",
        "HALO_SWING_MACRO_API_KEY": "macro-repo-secret-key",
        "HALO_SWING_NEWS_API_KEY": "news-repo-secret-key",
    }
    repo_env.write_text(
        "\n".join(
            [
                f"HALO_SWING_HERMES_CONFIG_PATH={hermes_config_path}",
                "HALO_SWING_HERMES_MCP_CONFIG_REGISTERED=true",
                *(f"{key}={value}" for key, value in secret_env.items()),
            ]
        ),
        encoding="utf-8",
    )
    repo_example.write_text("POLYGON_API_KEY=\n", encoding="utf-8")
    clear_local_env_cache()
    get_settings.cache_clear()

    payload = get_integration_readiness(binance_credentials_path="/missing/credentials.json")
    hermes_gate = payload["gates"]["hermes"]
    telegram_gate = payload["gates"]["telegram"]
    live_data_gate = payload["gates"]["live_data"]
    serialized = json.dumps(payload, sort_keys=True)

    assert hermes_gate["status"] == "ready"
    assert hermes_gate["missing"] == []
    assert hermes_gate["evidence"]["config_path"] == str(hermes_config_path)
    assert hermes_gate["evidence"]["config_path_exists"] is True
    assert telegram_gate["status"] == "ready"
    assert telegram_gate["missing"] == []
    assert telegram_gate["evidence"]["bot_token_configured"] is True
    assert telegram_gate["evidence"]["gateway_configured"] is True
    assert live_data_gate["status"] == "ready"
    assert live_data_gate["missing"] == []
    assert live_data_gate["evidence"]["market_ohlcv_source_configured"] is True
    assert live_data_gate["evidence"]["macro_source_configured"] is True
    assert live_data_gate["evidence"]["news_source_configured"] is True
    for key, value in secret_env.items():
        assert key not in serialized
        assert value not in serialized


def test_integration_readiness_repo_root_env_clears_integration_gates_without_gate_go(
    tmp_path: Path,
    monkeypatch,
) -> None:
    clear_readiness_env(monkeypatch)
    repo_dir = tmp_path / "repo"
    run_dir = tmp_path / "runner"
    repo_dir.mkdir()
    run_dir.mkdir()
    repo_env = repo_dir / ".env"
    monkeypatch.setattr(local_env, "REPO_ROOT_ENV_PATH", repo_env)
    monkeypatch.chdir(run_dir)
    monkeypatch.delenv("HALO_SWING_DISABLE_DOTENV", raising=False)

    hermes_config_path = repo_dir / "hermes.yaml"
    credentials_path = repo_dir / "credentials.enc.json"
    risk_settings_path = repo_dir / "risk_settings.json"
    hermes_config_path.write_text("mcp_servers: {}\n", encoding="utf-8")
    save_binance_credentials(
        api_key="abcde12345key",
        api_secret="super-secret",
        passphrase="local-passphrase",
        credentials_path=str(credentials_path),
    )
    secret_env = {
        "HALO_SWING_TELEGRAM_BOT_TOKEN": "telegram-env-secret-token",
        "HALO_SWING_TELEGRAM_GATEWAY": "https://gateway.example/env-secret",
        "HALO_SWING_MARKET_DATA_API_KEY": "market-env-secret-key",
        "HALO_SWING_MACRO_API_KEY": "macro-env-secret-key",
        "HALO_SWING_NEWS_API_KEY": "news-env-secret-key",
    }
    repo_env.write_text(
        "\n".join(
            [
                f"HALO_SWING_HERMES_CONFIG_PATH={hermes_config_path}",
                "HALO_SWING_HERMES_MCP_CONFIG_REGISTERED=true",
                f"HALO_SWING_BINANCE_CREDENTIALS_PATH={credentials_path}",
                "HALO_SWING_BINANCE_ENABLE_LIVE_TRADING=true",
                "HALO_SWING_BINANCE_PASSPHRASE_CONFIRMED=true",
                "HALO_SWING_BINANCE_TRADE_ONLY_PERMISSION_ATTESTED=true",
                "HALO_SWING_BINANCE_LIVE_ORDER_APPROVED=true",
                *(f"{key}={value}" for key, value in secret_env.items()),
            ]
        ),
        encoding="utf-8",
    )
    clear_local_env_cache()
    get_settings.cache_clear()

    payload = get_integration_readiness(
        btc_risk_settings_path=str(risk_settings_path),
    )
    serialized = json.dumps(payload, sort_keys=True)

    assert payload["status"] == "blocked"
    assert payload["next_actions"] == [
        "migration: provide explicit_MIGRATION_GO",
        "repository: provide MIGRATION_GO, REPOSITORY_GO",
    ]
    for gate_name in (
        "hermes",
        "telegram",
        "binance_testnet_read_only",
        "live_order_submission",
        "live_data",
    ):
        assert payload["gates"][gate_name]["status"] == "ready"
        assert payload["gates"][gate_name]["missing"] == []
    assert payload["gates"]["migration"]["status"] == "blocked"
    assert payload["gates"]["repository"]["status"] == "blocked"
    assert payload["gates"]["migration"]["missing"] == ["explicit_MIGRATION_GO"]
    assert payload["gates"]["repository"]["missing"] == [
        "MIGRATION_GO",
        "REPOSITORY_GO",
    ]
    assert payload["gates"]["hermes"]["evidence"]["runtime_started"] is False
    assert payload["gates"]["hermes"]["evidence"]["network_call"] is False
    assert payload["gates"]["telegram"]["evidence"]["send_call"] is False
    assert payload["gates"]["telegram"]["evidence"]["network_call"] is False
    assert (
        payload["gates"]["live_order_submission"]["evidence"]["order_submission"]
        is False
    )
    assert payload["gates"]["live_order_submission"]["evidence"]["network_call"] is False
    assert (
        payload["gates"]["live_order_submission"]["evidence"]["requires_confirmation"]
        == "CONFIRM_BTC_BINANCE_COINM_ORDER"
    )
    assert (
        payload["gates"]["binance_testnet_read_only"]["evidence"]["credentials"][
            "api_key_hint"
        ]
        == "abcde...5key"
    )
    for key, value in secret_env.items():
        assert key not in serialized
        assert value not in serialized
    assert "abcde12345key" not in serialized
    assert "api_secret" not in serialized
    assert "super-secret" not in serialized
    assert "local-passphrase" not in serialized
    assert "salt_b64" not in serialized
    assert '"token":' not in serialized


def test_integration_setup_checklist_uses_repo_root_env_without_secret_exposure(
    tmp_path: Path,
    monkeypatch,
) -> None:
    clear_readiness_env(monkeypatch)
    repo_dir = tmp_path / "repo"
    run_dir = tmp_path / "runner"
    repo_dir.mkdir()
    run_dir.mkdir()
    repo_env = repo_dir / ".env"
    monkeypatch.setattr(local_env, "REPO_ROOT_ENV_PATH", repo_env)
    monkeypatch.chdir(run_dir)
    monkeypatch.delenv("HALO_SWING_DISABLE_DOTENV", raising=False)

    hermes_config_path = repo_dir / "hermes.yaml"
    credentials_path = repo_dir / "credentials.enc.json"
    hermes_config_path.write_text("mcp_servers: {}\n", encoding="utf-8")
    save_binance_credentials(
        api_key="abcde12345key",
        api_secret="super-secret",
        passphrase="local-passphrase",
        credentials_path=str(credentials_path),
    )
    secret_env = {
        "HALO_SWING_TELEGRAM_BOT_TOKEN": "telegram-checklist-secret",
        "HALO_SWING_MARKET_DATA_API_KEY": "market-checklist-secret",
        "HALO_SWING_MACRO_API_KEY": "macro-checklist-secret",
        "HALO_SWING_NEWS_API_KEY": "news-checklist-secret",
    }
    repo_env.write_text(
        "\n".join(
            [
                f"HALO_SWING_HERMES_CONFIG_PATH={hermes_config_path}",
                "HALO_SWING_HERMES_MCP_CONFIG_REGISTERED=true",
                f"HALO_SWING_BINANCE_CREDENTIALS_PATH={credentials_path}",
                "HALO_SWING_BINANCE_ENABLE_LIVE_TRADING=true",
                "HALO_SWING_BINANCE_PASSPHRASE_CONFIRMED=true",
                "HALO_SWING_BINANCE_TRADE_ONLY_PERMISSION_ATTESTED=true",
                "HALO_SWING_BINANCE_LIVE_ORDER_APPROVED=true",
                *(f"{key}={value}" for key, value in secret_env.items()),
            ]
        ),
        encoding="utf-8",
    )
    clear_local_env_cache()
    get_settings.cache_clear()

    payload = get_integration_setup_checklist()
    env_requirements = {
        requirement["section"]: requirement
        for requirement in payload["env_requirements"]
    }
    serialized = json.dumps(payload, sort_keys=True)

    assert payload["status"] == "blocked"
    assert payload["next_actions"] == [
        "migration: provide explicit_MIGRATION_GO",
        "repository: provide MIGRATION_GO, REPOSITORY_GO",
    ]
    assert payload["live_data_setup_summary"]["status"] == "ready"
    assert payload["live_data_setup_summary"]["api_key_status"] == "ready"
    assert payload["live_data_setup_summary"]["provider_route_status"] == "ready"
    assert payload["live_data_setup_summary"]["configured_provider_families"] == [
        "market",
        "macro",
        "news",
    ]
    assert payload["live_data_setup_summary"]["provider_family_summary"] == {
        "required_provider_families": ["market", "macro", "news"],
        "configured_provider_families": ["market", "macro", "news"],
        "missing_provider_families": [],
        "configured_count": 3,
        "required_count": 3,
        "ready_to_run_live_smoke": True,
        "network_call": False,
        "mutates_local_state": False,
        "secret_values_returned": False,
    }
    assert payload["live_data_setup_summary"][
        "provider_setup_actions"
    ] == expected_provider_setup_actions(
        market_configured_env_keys=["HALO_SWING_MARKET_DATA_API_KEY"],
        macro_configured_env_keys=["HALO_SWING_MACRO_API_KEY"],
        news_configured_env_keys=["HALO_SWING_NEWS_API_KEY"],
    )
    assert payload["live_data_setup_summary"][
        "provider_smoke_plan"
    ] == expected_provider_smoke_plan(
        market_configured_env_keys=["HALO_SWING_MARKET_DATA_API_KEY"],
        macro_configured_env_keys=["HALO_SWING_MACRO_API_KEY"],
        news_configured_env_keys=["HALO_SWING_NEWS_API_KEY"],
        ready_to_run_live_smoke=True,
    )
    assert payload["live_data_setup_summary"][
        "dotenv_file_status"
    ] == expected_dotenv_file_status(repo_env)
    assert payload["live_data_setup_summary"][
        "live_data_setup_steps"
    ] == expected_live_data_setup_steps(
        target_path=repo_env,
        configured_provider_families=["market", "macro", "news"],
        missing_provider_families=[],
        ready_to_run_live_smoke=True,
    )
    assert payload["live_data_setup_summary"][
        "next_operator_action"
    ] == expected_next_operator_action(
        target_path=repo_env,
        configured_provider_families=["market", "macro", "news"],
        missing_provider_families=[],
        ready_to_run_live_smoke=True,
    )
    assert payload["live_data_setup_summary"]["missing"] == []
    assert payload["live_data_setup_summary"]["selected_provider_classes"] == [
        "PolygonMarketDataProvider",
        "FredMacroDataProvider",
        "NewsApiDataProvider",
    ]
    assert (
        payload["live_data_setup_summary"]["one_shot_smoke_command"]["name"]
        == "run_api_key_pipeline_smoke"
    )
    assert payload["live_data_setup_summary"]["network_call"] is False
    assert payload["live_data_setup_summary"]["secret_values_returned"] is False
    assert env_requirements["hermes"]["configured"] is True
    assert env_requirements["telegram"]["configured"] is True
    assert env_requirements["live_data"]["configured"] is True
    assert env_requirements["binance_credentials"]["configured"] is True
    assert env_requirements["binance_read_only_smoke"]["configured"] is True
    assert env_requirements["binance_live_order_readiness"]["configured"] is True
    assert all(
        not gate["dotenv_supported"]
        for gate in payload["durable_gate_requirements"]
    )
    assert payload["offline_guardrails"]["credential_file_write"] is False
    assert "<binance_api_key>" in serialized
    for key, value in secret_env.items():
        assert key in serialized
        assert value not in serialized
    assert "abcde12345key" not in serialized
    assert "super-secret" not in serialized
    assert "local-passphrase" not in serialized
    assert "salt_b64" not in serialized
    assert '"token":' not in serialized


def test_integration_readiness_requires_api_keys_with_live_modes(
    monkeypatch,
) -> None:
    clear_readiness_env(monkeypatch)
    live_mode_env = {
        "HALO_SWING_MARKET_DATA_MODE": "live",
        "HALO_SWING_MACRO_DATA_MODE": "live",
        "HALO_SWING_NEWS_DATA_MODE": "live",
    }
    for key, value in live_mode_env.items():
        monkeypatch.setenv(key, value)

    payload = get_integration_readiness(binance_credentials_path="/missing/credentials.json")
    live_data_gate = payload["gates"]["live_data"]
    serialized = json.dumps(payload, sort_keys=True)

    assert live_data_gate["status"] == "blocked"
    assert live_data_gate["missing"] == [
        "market_ohlcv_api_key",
        "macro_api_key",
        "news_api_key",
    ]
    assert live_data_gate["evidence"]["market_ohlcv_source_configured"] is False
    assert live_data_gate["evidence"]["macro_source_configured"] is False
    assert live_data_gate["evidence"]["news_source_configured"] is False
    assert live_data_gate["evidence"]["secret_values_returned"] is False
    assert (
        "live_data: provide market_ohlcv_api_key, "
        "macro_api_key, news_api_key"
    ) in payload["next_actions"]
    for key in live_mode_env:
        assert key not in serialized


def test_integration_readiness_ignores_unimplemented_market_api_key_aliases(
    monkeypatch,
) -> None:
    clear_readiness_env(monkeypatch)
    secret_env = {
        "ALPACA_API_KEY": "alpaca-secret-key",
        "TIINGO_API_KEY": "tiingo-secret-key",
        "HALO_SWING_MACRO_API_KEY": "macro-project-secret-key",
        "HALO_SWING_NEWS_API_KEY": "news-secret-key",
    }
    for key, value in secret_env.items():
        monkeypatch.setenv(key, value)
    live_mode_env = {
        "HALO_SWING_MARKET_DATA_MODE": "live",
        "HALO_SWING_MACRO_DATA_MODE": "live",
        "HALO_SWING_NEWS_DATA_MODE": "live",
    }
    for key, value in live_mode_env.items():
        monkeypatch.setenv(key, value)

    payload = get_integration_readiness(binance_credentials_path="/missing/credentials.json")
    live_data_gate = payload["gates"]["live_data"]
    serialized = json.dumps(payload, sort_keys=True)

    assert payload["status"] == "blocked"
    assert live_data_gate["status"] == "blocked"
    assert live_data_gate["missing"] == ["market_ohlcv_api_key"]
    assert live_data_gate["evidence"]["market_ohlcv_source_configured"] is False
    assert live_data_gate["evidence"]["macro_source_configured"] is True
    assert live_data_gate["evidence"]["news_source_configured"] is True
    assert live_data_gate["evidence"]["secret_values_returned"] is False
    assert "live_data: provide market_ohlcv_api_key" in payload[
        "next_actions"
    ]
    for key, value in secret_env.items():
        assert key not in serialized
        assert value not in serialized
    for key in live_mode_env:
        assert key not in serialized


def test_integration_readiness_ignores_invalid_env_secret_values_without_exposure(
    monkeypatch,
) -> None:
    clear_readiness_env(monkeypatch)
    secret_env = {
        "HALO_SWING_TELEGRAM_BOT_TOKEN": "   ",
        "TELEGRAM_BOT_TOKEN": "telegram\x7fsecret",
        "HALO_SWING_TELEGRAM_GATEWAY": "\n",
        "HALO_SWING_TELEGRAM_GATEWAY_URL": "https://gateway.example/\x7fsecret",
        "HALO_SWING_MARKET_DATA_API_KEY": " market\x7fsecret ",
        "HALO_SWING_MACRO_API_KEY": "macro\x7fsecret",
        "FRED_API_KEY": "   ",
        "HALO_SWING_FRED_API_KEY": "fred\nsecret",
        "NEWS_API_KEY": "\x7f",
        "HALO_SWING_NEWS_API_KEY": "news\x7fsecret",
    }
    for key, value in secret_env.items():
        monkeypatch.setenv(key, value)

    payload = get_integration_readiness(binance_credentials_path="/missing/credentials.json")
    telegram_gate = payload["gates"]["telegram"]
    live_data_gate = payload["gates"]["live_data"]
    serialized = json.dumps(payload, sort_keys=True)

    assert telegram_gate["status"] == "blocked"
    assert telegram_gate["missing"] == ["telegram_bot_token_or_gateway"]
    assert telegram_gate["evidence"]["bot_token_configured"] is False
    assert telegram_gate["evidence"]["gateway_configured"] is False
    assert telegram_gate["evidence"]["secret_values_returned"] is False
    assert live_data_gate["status"] == "blocked"
    assert live_data_gate["missing"] == EXPECTED_DEFAULT_LIVE_DATA_MISSING
    assert live_data_gate["evidence"]["market_ohlcv_source_configured"] is False
    assert live_data_gate["evidence"]["macro_source_configured"] is False
    assert live_data_gate["evidence"]["news_source_configured"] is False
    assert live_data_gate["evidence"]["secret_values_returned"] is False
    for key, value in secret_env.items():
        assert key not in serialized
        if value.strip():
            assert value not in serialized


def test_integration_readiness_live_data_source_env_values_do_not_imply_keys(
    monkeypatch,
) -> None:
    clear_readiness_env(monkeypatch)
    source_env = {
        "HALO_SWING_MARKET_DATA_SOURCE": " polygon ",
        "HALO_SWING_MACRO_SOURCE": " FRED ",
        "HALO_SWING_NEWS_SOURCE": " newsapi ",
    }
    for key, value in source_env.items():
        monkeypatch.setenv(key, value)

    payload = get_integration_readiness(binance_credentials_path="/missing/credentials.json")
    live_data_gate = payload["gates"]["live_data"]
    serialized = json.dumps(payload, sort_keys=True)

    assert payload["status"] == "blocked"
    assert live_data_gate["status"] == "blocked"
    assert live_data_gate["missing"] == EXPECTED_DEFAULT_LIVE_DATA_MISSING
    assert live_data_gate["evidence"]["market_ohlcv_source_configured"] is False
    assert live_data_gate["evidence"]["macro_source_configured"] is False
    assert live_data_gate["evidence"]["news_source_configured"] is False
    assert live_data_gate["evidence"]["live_adapter_added"] is True
    assert live_data_gate["evidence"]["network_call"] is False
    assert live_data_gate["evidence"]["secret_values_returned"] is False
    assert "live_data: provide" in payload["next_actions"][-1]
    for key, value in source_env.items():
        assert key not in serialized
        assert value not in serialized


def test_integration_readiness_ignores_unsupported_live_data_source_env_values(
    monkeypatch,
) -> None:
    clear_readiness_env(monkeypatch)
    source_env = {
        "HALO_SWING_MARKET_DATA_SOURCE": "alpaca",
        "HALO_SWING_MACRO_SOURCE": "bea",
        "HALO_SWING_NEWS_SOURCE": "rss",
    }
    for key, value in source_env.items():
        monkeypatch.setenv(key, value)

    payload = get_integration_readiness(binance_credentials_path="/missing/credentials.json")
    live_data_gate = payload["gates"]["live_data"]
    serialized = json.dumps(payload, sort_keys=True)

    assert live_data_gate["status"] == "blocked"
    assert live_data_gate["missing"] == EXPECTED_DEFAULT_LIVE_DATA_MISSING
    assert live_data_gate["evidence"]["market_ohlcv_source_configured"] is False
    assert live_data_gate["evidence"]["macro_source_configured"] is False
    assert live_data_gate["evidence"]["news_source_configured"] is False
    assert live_data_gate["evidence"]["secret_values_returned"] is False
    for key, value in source_env.items():
        assert key not in serialized
        assert value not in serialized


def test_integration_readiness_ignores_invalid_live_data_source_env_values(
    monkeypatch,
) -> None:
    clear_readiness_env(monkeypatch)
    source_env = {
        "HALO_SWING_MARKET_DATA_SOURCE": "   ",
        "POLYGON_API_KEY": "polygon\x7fsource",
        "ALPACA_API_KEY": "\n",
        "TIINGO_API_KEY": "tiingo\x7fsource",
        "HALO_SWING_MACRO_SOURCE": "macro\nsource",
        "HALO_SWING_NEWS_SOURCE": "\x7fnews-source",
    }
    for key, value in source_env.items():
        monkeypatch.setenv(key, value)

    payload = get_integration_readiness(binance_credentials_path="/missing/credentials.json")
    live_data_gate = payload["gates"]["live_data"]
    serialized = json.dumps(payload, sort_keys=True)

    assert live_data_gate["status"] == "blocked"
    assert live_data_gate["missing"] == EXPECTED_DEFAULT_LIVE_DATA_MISSING
    assert live_data_gate["evidence"]["market_ohlcv_source_configured"] is False
    assert live_data_gate["evidence"]["macro_source_configured"] is False
    assert live_data_gate["evidence"]["news_source_configured"] is False
    assert live_data_gate["evidence"]["secret_values_returned"] is False
    assert "live_data: provide" in payload["next_actions"][-1]
    for key, value in source_env.items():
        assert key not in serialized
        if value.strip():
            assert value not in serialized


def test_binance_readiness_requires_passphrase_confirmation(tmp_path: Path) -> None:
    credentials_path = tmp_path / "credentials.enc.json"
    save_binance_credentials(
        api_key="abcde12345key",
        api_secret="super-secret",
        passphrase="local-passphrase",
        credentials_path=str(credentials_path),
    )
    get_settings.cache_clear()

    payload = get_integration_readiness(binance_credentials_path=str(credentials_path))
    binance_gate = payload["gates"]["binance_testnet_read_only"]

    assert payload["status"] == "blocked"
    assert binance_gate["status"] == "blocked"
    assert binance_gate["evidence"]["credentials"]["configured"] is True
    assert binance_gate["evidence"]["manual_passphrase_confirmed"] is False
    assert binance_gate["missing"] == ["manual_credential_passphrase_at_smoke_time"]
    serialized = json.dumps(payload)
    assert "abcde12345key" not in serialized
    assert "super-secret" not in serialized
    assert "local-passphrase" not in serialized


def test_binance_readiness_accepts_env_passphrase_confirmation(
    tmp_path: Path,
    monkeypatch,
) -> None:
    clear_readiness_env(monkeypatch)
    credentials_path = tmp_path / "credentials.enc.json"
    save_binance_credentials(
        api_key="abcde12345key",
        api_secret="super-secret",
        passphrase="local-passphrase",
        credentials_path=str(credentials_path),
    )
    monkeypatch.setenv("HALO_SWING_BINANCE_PASSPHRASE_CONFIRMED", " true ")
    get_settings.cache_clear()

    payload = get_integration_readiness(binance_credentials_path=str(credentials_path))
    binance_gate = payload["gates"]["binance_testnet_read_only"]
    serialized = json.dumps(payload)

    assert binance_gate["status"] == "ready"
    assert binance_gate["missing"] == []
    assert binance_gate["evidence"]["credentials"]["configured"] is True
    assert binance_gate["evidence"]["manual_passphrase_confirmed"] is True
    assert "abcde12345key" not in serialized
    assert "super-secret" not in serialized
    assert "local-passphrase" not in serialized


def test_binance_readiness_explicit_passphrase_confirmation_overrides_env(
    tmp_path: Path,
    monkeypatch,
) -> None:
    clear_readiness_env(monkeypatch)
    credentials_path = tmp_path / "credentials.enc.json"
    save_binance_credentials(
        api_key="abcde12345key",
        api_secret="super-secret",
        passphrase="local-passphrase",
        credentials_path=str(credentials_path),
    )
    monkeypatch.setenv("HALO_SWING_BINANCE_PASSPHRASE_CONFIRMED", "true")
    get_settings.cache_clear()

    payload = get_integration_readiness(
        binance_credentials_path=str(credentials_path),
        binance_passphrase_confirmed=False,
    )
    binance_gate = payload["gates"]["binance_testnet_read_only"]

    assert binance_gate["status"] == "blocked"
    assert binance_gate["missing"] == ["manual_credential_passphrase_at_smoke_time"]
    assert binance_gate["evidence"]["manual_passphrase_confirmed"] is False


def test_binance_readiness_rejects_env_passphrase_confirmation_before_credentials(
    tmp_path: Path,
    monkeypatch,
) -> None:
    clear_readiness_env(monkeypatch)
    monkeypatch.setenv("HALO_SWING_BINANCE_PASSPHRASE_CONFIRMED", "yes")
    get_settings.cache_clear()

    def fail_credential_status(*_args, **_kwargs):
        raise AssertionError(
            "credential status must not run before Binance passphrase env validation"
        )

    monkeypatch.setattr(
        "halo_swing_mcp.tools.readiness.get_binance_credentials_status",
        fail_credential_status,
    )

    with pytest.raises(
        ValueError,
        match="HALO_SWING_BINANCE_PASSPHRASE_CONFIRMED must be 'true' or 'false'",
    ):
        get_integration_readiness(
            binance_credentials_path=str(tmp_path / "missing.enc.json"),
        )


def test_live_order_submission_accepts_env_trade_only_attestation(
    tmp_path: Path,
    monkeypatch,
) -> None:
    clear_readiness_env(monkeypatch)
    credentials_path = tmp_path / "credentials.enc.json"
    save_binance_credentials(
        api_key="abcde12345key",
        api_secret="super-secret",
        passphrase="local-passphrase",
        credentials_path=str(credentials_path),
    )
    monkeypatch.setenv("HALO_SWING_BINANCE_ENABLE_LIVE_TRADING", "true")
    monkeypatch.setenv("HALO_SWING_BINANCE_PASSPHRASE_CONFIRMED", "true")
    monkeypatch.setenv("HALO_SWING_BINANCE_TRADE_ONLY_PERMISSION_ATTESTED", " true ")
    get_settings.cache_clear()

    payload = get_integration_readiness(
        binance_credentials_path=str(credentials_path),
        btc_risk_settings_path=str(tmp_path / "risk_settings.json"),
    )
    live_order_gate = payload["gates"]["live_order_submission"]
    serialized = json.dumps(payload)

    assert live_order_gate["status"] == "blocked"
    assert live_order_gate["missing"] == ["explicit_live_order_approval"]
    assert live_order_gate["evidence"]["manual_passphrase_confirmed"] is True
    assert live_order_gate["evidence"]["trade_only_permission_attested"] is True
    assert live_order_gate["evidence"]["order_submission"] is False
    assert live_order_gate["evidence"]["network_call"] is False
    assert "abcde12345key" not in serialized
    assert "super-secret" not in serialized
    assert "local-passphrase" not in serialized


def test_live_order_submission_explicit_trade_only_attestation_overrides_env(
    tmp_path: Path,
    monkeypatch,
) -> None:
    clear_readiness_env(monkeypatch)
    credentials_path = tmp_path / "credentials.enc.json"
    save_binance_credentials(
        api_key="abcde12345key",
        api_secret="super-secret",
        passphrase="local-passphrase",
        credentials_path=str(credentials_path),
    )
    monkeypatch.setenv("HALO_SWING_BINANCE_ENABLE_LIVE_TRADING", "true")
    monkeypatch.setenv("HALO_SWING_BINANCE_PASSPHRASE_CONFIRMED", "true")
    monkeypatch.setenv("HALO_SWING_BINANCE_TRADE_ONLY_PERMISSION_ATTESTED", "true")
    get_settings.cache_clear()

    payload = get_integration_readiness(
        binance_credentials_path=str(credentials_path),
        binance_trade_only_permission_attested=False,
        btc_risk_settings_path=str(tmp_path / "risk_settings.json"),
    )
    live_order_gate = payload["gates"]["live_order_submission"]

    assert "binance_console_trade_only_no_withdraw_attestation" in live_order_gate[
        "missing"
    ]
    assert live_order_gate["evidence"]["trade_only_permission_attested"] is False


def test_live_order_submission_rejects_env_trade_only_attestation_before_credentials(
    tmp_path: Path,
    monkeypatch,
) -> None:
    clear_readiness_env(monkeypatch)
    monkeypatch.setenv("HALO_SWING_BINANCE_TRADE_ONLY_PERMISSION_ATTESTED", "yes")
    get_settings.cache_clear()

    def fail_credential_status(*_args, **_kwargs):
        raise AssertionError(
            "credential status must not run before Binance attestation env validation"
        )

    monkeypatch.setattr(
        "halo_swing_mcp.tools.readiness.get_binance_credentials_status",
        fail_credential_status,
    )

    with pytest.raises(
        ValueError,
        match=(
            "HALO_SWING_BINANCE_TRADE_ONLY_PERMISSION_ATTESTED "
            "must be 'true' or 'false'"
        ),
    ):
        get_integration_readiness(
            binance_credentials_path=str(tmp_path / "missing.enc.json"),
        )


def test_live_order_submission_accepts_env_live_order_approval(
    tmp_path: Path,
    monkeypatch,
) -> None:
    clear_readiness_env(monkeypatch)
    credentials_path = tmp_path / "credentials.enc.json"
    save_binance_credentials(
        api_key="abcde12345key",
        api_secret="super-secret",
        passphrase="local-passphrase",
        credentials_path=str(credentials_path),
    )
    monkeypatch.setenv("HALO_SWING_BINANCE_ENABLE_LIVE_TRADING", "true")
    monkeypatch.setenv("HALO_SWING_BINANCE_LIVE_ORDER_APPROVED", " true ")
    monkeypatch.setenv("HALO_SWING_BINANCE_PASSPHRASE_CONFIRMED", "true")
    monkeypatch.setenv("HALO_SWING_BINANCE_TRADE_ONLY_PERMISSION_ATTESTED", "true")
    get_settings.cache_clear()

    payload = get_integration_readiness(
        binance_credentials_path=str(credentials_path),
        btc_risk_settings_path=str(tmp_path / "risk_settings.json"),
    )
    live_order_gate = payload["gates"]["live_order_submission"]
    serialized = json.dumps(payload)

    assert live_order_gate["status"] == "ready"
    assert live_order_gate["missing"] == []
    assert live_order_gate["evidence"]["live_order_approved"] is True
    assert live_order_gate["evidence"]["order_submission"] is False
    assert live_order_gate["evidence"]["network_call"] is False
    assert "abcde12345key" not in serialized
    assert "super-secret" not in serialized
    assert "local-passphrase" not in serialized


def test_live_order_submission_explicit_live_order_approval_overrides_env(
    tmp_path: Path,
    monkeypatch,
) -> None:
    clear_readiness_env(monkeypatch)
    credentials_path = tmp_path / "credentials.enc.json"
    save_binance_credentials(
        api_key="abcde12345key",
        api_secret="super-secret",
        passphrase="local-passphrase",
        credentials_path=str(credentials_path),
    )
    monkeypatch.setenv("HALO_SWING_BINANCE_ENABLE_LIVE_TRADING", "true")
    monkeypatch.setenv("HALO_SWING_BINANCE_LIVE_ORDER_APPROVED", "true")
    monkeypatch.setenv("HALO_SWING_BINANCE_PASSPHRASE_CONFIRMED", "true")
    monkeypatch.setenv("HALO_SWING_BINANCE_TRADE_ONLY_PERMISSION_ATTESTED", "true")
    get_settings.cache_clear()

    payload = get_integration_readiness(
        binance_credentials_path=str(credentials_path),
        live_order_approved=False,
        btc_risk_settings_path=str(tmp_path / "risk_settings.json"),
    )
    live_order_gate = payload["gates"]["live_order_submission"]

    assert live_order_gate["status"] == "blocked"
    assert "explicit_live_order_approval" in live_order_gate["missing"]
    assert live_order_gate["evidence"]["live_order_approved"] is False
    assert live_order_gate["evidence"]["order_submission"] is False


def test_live_order_submission_rejects_env_live_order_approval_before_credentials(
    tmp_path: Path,
    monkeypatch,
) -> None:
    clear_readiness_env(monkeypatch)
    monkeypatch.setenv("HALO_SWING_BINANCE_LIVE_ORDER_APPROVED", "yes")
    get_settings.cache_clear()

    def fail_credential_status(*_args, **_kwargs):
        raise AssertionError(
            "credential status must not run before live-order approval env validation"
        )

    monkeypatch.setattr(
        "halo_swing_mcp.tools.readiness.get_binance_credentials_status",
        fail_credential_status,
    )

    with pytest.raises(
        ValueError,
        match="HALO_SWING_BINANCE_LIVE_ORDER_APPROVED must be 'true' or 'false'",
    ):
        get_integration_readiness(
            binance_credentials_path=str(tmp_path / "missing.enc.json"),
        )


def test_live_order_submission_requires_explicit_approval(
    tmp_path: Path,
    monkeypatch,
) -> None:
    credentials_path = tmp_path / "credentials.enc.json"
    save_binance_credentials(
        api_key="abcde12345key",
        api_secret="super-secret",
        passphrase="local-passphrase",
        credentials_path=str(credentials_path),
    )
    monkeypatch.setenv("HALO_SWING_BINANCE_ENABLE_LIVE_TRADING", "true")
    get_settings.cache_clear()

    payload = get_integration_readiness(
        binance_credentials_path=str(credentials_path),
        binance_passphrase_confirmed=True,
        binance_trade_only_permission_attested=True,
        btc_risk_settings_path=str(tmp_path / "risk_settings.json"),
    )
    live_order_gate = payload["gates"]["live_order_submission"]

    assert payload["status"] == "blocked"
    assert live_order_gate["status"] == "blocked"
    assert live_order_gate["missing"] == ["explicit_live_order_approval"]
    assert live_order_gate["evidence"]["live_trading_enabled"] is True
    assert live_order_gate["evidence"]["trade_only_permission_attested"] is True
    assert live_order_gate["evidence"]["credentials"]["configured"] is True
    assert live_order_gate["evidence"]["order_submission"] is False
    assert live_order_gate["evidence"]["network_call"] is False
    serialized = json.dumps(payload)
    assert "abcde12345key" not in serialized
    assert "super-secret" not in serialized
    assert "local-passphrase" not in serialized


def test_harness_returns_integration_readiness(tmp_path: Path) -> None:
    audit_path = tmp_path / "audit.jsonl"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "get_integration_readiness",
            "--input-json",
            json.dumps({"binance_credentials_path": str(tmp_path / "missing.enc.json")}),
            "--audit-log-path",
            str(audit_path),
        ],
        check=True,
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    payload = json.loads(result.stdout)

    assert payload["status"] == "blocked"
    assert payload["gates"]["migration"]["status"] == "blocked"
    assert audit_path.exists()


def test_harness_returns_integration_setup_checklist() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "get_integration_setup_checklist",
            "--no-audit",
        ],
        check=True,
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    payload = json.loads(result.stdout)

    assert payload["schema_version"] == "integration_setup_checklist.v1"
    assert payload["status"] == "blocked"
    assert payload["offline_guardrails"]["network_call"] is False
    assert payload["offline_guardrails"]["credential_file_write"] is False
