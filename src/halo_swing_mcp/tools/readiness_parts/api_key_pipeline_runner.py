# ruff: noqa: F403,F405,F821
"""Api Key Pipeline Runner readiness implementation."""

from __future__ import annotations

from .context import *
from .api_key_pipeline_next_action import (
    _api_key_pipeline_next_action_summary,
    _api_key_pipeline_next_operator_action,
)
from .api_key_pipeline_payload_mirrors import (
    _api_key_failure_top_level_fields,
    _api_key_provider_recovery_top_level_fields,
)


__all__ = ('run_api_key_pipeline_smoke', '_setup_env_requirements', '_setup_local_commands')


def run_api_key_pipeline_smoke(
    asset: str = "TQQQ",
    timeframe: str = "swing_3d_10d",
    symbols: list[str] | None = None,
    topic: str = "macro",
    summary_only: bool = False,
) -> dict[str, Any]:
    """Run the API-key-backed local integration pipeline smoke checks."""

    readiness = get_integration_readiness()
    live_data_api_key_status = get_live_data_api_key_status()
    provider_route = get_live_data_provider_route()
    live_data_setup_summary = _live_data_setup_summary(
        live_data_api_key_status,
        provider_route,
    )
    live_data_smoke = _run_api_key_pipeline_sub_smoke(
        tool_name="run_live_data_smoke",
        runner=lambda: run_live_data_smoke(symbols=symbols, topic=topic),
        live_data_setup_summary=live_data_setup_summary,
        provider_route=provider_route,
    )
    provider_route = (
        _optional_mapping(live_data_smoke.get("provider_route"))
        or provider_route
    )
    live_data_setup_summary = _live_data_setup_summary(
        live_data_api_key_status,
        provider_route,
    )
    signal_workflow_smoke = _run_api_key_pipeline_sub_smoke(
        tool_name="run_live_signal_workflow_smoke",
        runner=lambda: run_live_signal_workflow_smoke(
            asset=asset,
            timeframe=timeframe,
        ),
        live_data_setup_summary=live_data_setup_summary,
        provider_route=provider_route,
    )
    recording_smoke = _run_api_key_pipeline_sub_smoke(
        tool_name="run_live_recording_smoke",
        runner=lambda: run_live_recording_smoke(asset=asset, timeframe=timeframe),
        live_data_setup_summary=live_data_setup_summary,
        provider_route=provider_route,
    )
    checks = _api_key_pipeline_checks(
        readiness=readiness,
        live_data_smoke=live_data_smoke,
        signal_workflow_smoke=signal_workflow_smoke,
        recording_smoke=recording_smoke,
    )
    setup_status_summary = _api_key_pipeline_setup_status_summary(
        live_data_setup_summary,
    )
    api_key_requirements_summary = _api_key_pipeline_api_key_requirements_summary(
        live_data_setup_summary,
    )
    api_key_command_summary = _api_key_pipeline_api_key_command_summary(
        live_data_setup_summary,
    )
    live_data_smoke_summary = _api_key_pipeline_smoke_summary(
        live_data_smoke,
    )
    signal_workflow_smoke_summary = _api_key_pipeline_smoke_summary(
        signal_workflow_smoke,
    )
    recording_smoke_summary = _api_key_pipeline_smoke_summary(
        recording_smoke,
    )
    api_key_provider_recovery_checklist = _api_key_provider_recovery_checklist(
        live_data_smoke_summary,
        route_family_summary=live_data_setup_summary,
    )
    api_key_provider_recovery_summary = _api_key_provider_recovery_summary(
        api_key_provider_recovery_checklist,
        route_family_summary=live_data_setup_summary,
    )
    api_key_operator_checklist = _api_key_pipeline_operator_checklist(
        setup_status_summary=setup_status_summary,
        api_key_requirements_summary=api_key_requirements_summary,
        api_key_command_summary=api_key_command_summary,
        api_key_provider_recovery_checklist=(
            api_key_provider_recovery_checklist
        ),
    )
    next_operator_action = _api_key_pipeline_next_operator_action(
        live_data_setup_summary=live_data_setup_summary,
        api_key_operator_checklist=api_key_operator_checklist,
    )
    api_key_next_action_summary = _api_key_pipeline_next_action_summary(
        api_key_operator_checklist=api_key_operator_checklist,
        live_data_setup_summary=live_data_setup_summary,
        next_operator_action=next_operator_action,
    )
    api_key_pipeline_stage_summary = _api_key_pipeline_stage_summary(
        live_data_setup_summary=live_data_setup_summary,
        live_data_smoke_summary=live_data_smoke_summary,
        signal_workflow_smoke_summary=signal_workflow_smoke_summary,
        recording_smoke_summary=recording_smoke_summary,
    )
    api_key_pipeline_check_summary = _api_key_pipeline_check_summary(
        checks,
        api_key_pipeline_stage_summary=api_key_pipeline_stage_summary,
    )
    api_key_setup_file_summary = _api_key_setup_file_summary(
        live_data_setup_summary
    )
    api_key_dotenv_loading_summary = _api_key_dotenv_loading_summary(
        live_data_api_key_status,
        live_data_setup_summary,
    )
    api_key_pipeline_failure_summary = _api_key_pipeline_failure_summary(
        api_key_next_action_summary=api_key_next_action_summary,
        api_key_pipeline_stage_summary=api_key_pipeline_stage_summary,
        api_key_pipeline_check_summary=api_key_pipeline_check_summary,
    )
    api_key_provider_selection_summary = _api_key_provider_selection_summary(
        provider_route,
        live_data_setup_summary,
    )
    api_key_integration_status_summary = _api_key_integration_status_summary(
        setup_status_summary=setup_status_summary,
        api_key_next_action_summary=api_key_next_action_summary,
        api_key_pipeline_failure_summary=api_key_pipeline_failure_summary,
        api_key_setup_file_summary=api_key_setup_file_summary,
        api_key_dotenv_loading_summary=api_key_dotenv_loading_summary,
        api_key_provider_selection_summary=api_key_provider_selection_summary,
        api_key_provider_recovery_summary=api_key_provider_recovery_summary,
        api_key_command_summary=api_key_command_summary,
    )
    api_key_live_http_timeout_summary = _api_key_live_http_timeout_summary()

    payload = {
        "schema_version": "api_key_pipeline_smoke_run.v1",
        "status": "ok" if checks and all(check["passed"] for check in checks) else "conflict",
        "input": {
            "asset": asset,
            "timeframe": timeframe,
            "symbols": symbols if symbols is not None else ["QQQ"],
            "topic": topic,
        },
        "executed_tools": [
            "get_integration_readiness",
            "get_live_data_api_key_status",
            "run_live_data_smoke",
            "get_live_data_provider_route",
            "run_live_signal_workflow_smoke",
            "run_live_recording_smoke",
        ],
        "readiness_summary": _api_key_pipeline_readiness_summary(
            readiness,
            live_data_setup_summary,
            next_operator_action=next_operator_action,
        ),
        "live_data_setup_summary": live_data_setup_summary,
        "next_operator_action": next_operator_action,
        "api_key_next_action_summary": api_key_next_action_summary,
        "setup_status_summary": setup_status_summary,
        "api_key_requirements_summary": api_key_requirements_summary,
        "api_key_command_summary": api_key_command_summary,
        "api_key_operator_checklist": api_key_operator_checklist,
        "api_key_provider_recovery_checklist": api_key_provider_recovery_checklist,
        "api_key_provider_recovery_summary": api_key_provider_recovery_summary,
        "api_key_setup_file_summary": api_key_setup_file_summary,
        "api_key_dotenv_loading_summary": api_key_dotenv_loading_summary,
        "api_key_pipeline_stage_summary": api_key_pipeline_stage_summary,
        "api_key_pipeline_check_summary": api_key_pipeline_check_summary,
        "api_key_pipeline_failure_summary": api_key_pipeline_failure_summary,
        "provider_route_summary": _api_key_pipeline_provider_route_summary(
            provider_route,
        ),
        "api_key_provider_selection_summary": api_key_provider_selection_summary,
        "api_key_integration_status_summary": (
            api_key_integration_status_summary
        ),
        "api_key_live_http_timeout_summary": api_key_live_http_timeout_summary,
        **_api_key_failure_top_level_fields(api_key_pipeline_failure_summary),
        "live_data_smoke_summary": live_data_smoke_summary,
        "failed_provider_families": live_data_smoke_summary[
            "failed_provider_families"
        ],
        "failed_provider_count": live_data_smoke_summary["failed_provider_count"],
        "first_provider_error_summary": live_data_smoke_summary[
            "first_provider_error_summary"
        ],
        "next_provider_recovery_action": live_data_smoke_summary[
            "next_provider_recovery_action"
        ],
        "next_provider_recovery_smoke": live_data_smoke_summary[
            "next_provider_recovery_smoke"
        ],
        "next_provider_recovery_smoke_command_name": (
            live_data_smoke_summary["next_provider_recovery_smoke_command_name"]
        ),
        "provider_recovery_smokes": live_data_smoke_summary[
            "provider_recovery_smokes"
        ],
        "provider_recovery_smoke_count": live_data_smoke_summary[
            "provider_recovery_smoke_count"
        ],
        **_api_key_provider_recovery_top_level_fields(
            api_key_provider_recovery_summary
        ),
        "signal_workflow_smoke_summary": signal_workflow_smoke_summary,
        "recording_smoke_summary": recording_smoke_summary,
        "checks": checks,
        "network_call": any(
            smoke.get("network_call") is True
            for smoke in [live_data_smoke, signal_workflow_smoke, recording_smoke]
        ),
        "live_data_required": any(
            smoke.get("live_data_required") is True
            for smoke in [live_data_smoke, signal_workflow_smoke, recording_smoke]
        ),
        "hermes_runtime_started": False,
        "telegram_send_call": False,
        "send_call": False,
        "order_submission": False,
        "mutates_local_state": False,
        "secret_values_returned": False,
    }
    if summary_only:
        return _api_key_pipeline_summary_only_payload(payload)
    return payload


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
        {
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
        {
            "name": "get_live_data_provider_route",
            "purpose": (
                "show the actual provider factory route selected by configured "
                "live data API keys without provider network calls"
            ),
            "command": (
                "PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness "
                "get_live_data_provider_route --no-audit"
            ),
            "network_call": False,
            "mutates_local_state": False,
            "secret_values_returned": False,
        },
        {
            "name": "validate_live_data_smoke_result",
            "purpose": "validate collected live data smoke payloads without calling networks",
            "command": (
                "PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness "
                "validate_live_data_smoke_result --input-file "
                "/path/to/live_data_smoke_payloads.json --no-audit"
            ),
            "network_call": False,
            "mutates_local_state": False,
            "secret_values_returned": False,
        },
        {
            "name": "run_live_data_smoke",
            "purpose": "run market, macro, and news smoke paths and validate the combined result",
            "command": (
                "PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness "
                "run_live_data_smoke --input-json "
                "'{\"symbols\":[\"QQQ\"],\"topic\":\"macro\"}' --no-audit"
            ),
            "network_call": True,
            "network_call_policy": "only_when_matching_api_key_selects_live_provider",
            "mutates_local_state": False,
            "secret_values_returned": False,
        },
        {
            "name": "run_integration_smoke",
            "purpose": "run readiness plus live data smoke in one payload",
            "command": (
                "PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness "
                "run_integration_smoke --input-json "
                "'{\"symbols\":[\"QQQ\"],\"topic\":\"macro\"}' --no-audit"
            ),
            "network_call": True,
            "network_call_policy": "only_when_matching_api_key_selects_live_provider",
            "mutates_local_state": False,
            "secret_values_returned": False,
        },
        {
            "name": "run_live_signal_workflow_smoke",
            "purpose": (
                "run scoring, guide, position review, and latest report with live "
                "source-boundary validation"
            ),
            "command": (
                "PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness "
                "run_live_signal_workflow_smoke --input-json "
                "'{\"asset\":\"TQQQ\",\"timeframe\":\"swing_3d_10d\"}' --no-audit"
            ),
            "network_call": True,
            "network_call_policy": "only_when_matching_api_key_selects_live_provider",
            "mutates_local_state": False,
            "secret_values_returned": False,
        },
        {
            "name": "run_live_recording_smoke",
            "purpose": (
                "generate a signal, record it to an ephemeral or explicit JSONL "
                "ledger, and verify live run-journal boundaries"
            ),
            "command": (
                "PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness "
                "run_live_recording_smoke --input-json "
                "'{\"asset\":\"TQQQ\",\"timeframe\":\"swing_3d_10d\"}' --no-audit"
            ),
            "network_call": True,
            "network_call_policy": "only_when_matching_api_key_selects_live_provider",
            "mutates_local_state": False,
            "state_policy": "uses an ephemeral ledger unless ledger_path is supplied",
            "secret_values_returned": False,
        },
        {
            "name": "run_api_key_pipeline_smoke",
            "purpose": (
                "run readiness, provider, signal workflow, and recording smoke "
                "checks after API keys are configured"
            ),
            "command": (
                "PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness "
                "run_api_key_pipeline_smoke --summary-only --no-audit"
            ),
            "network_call": True,
            "network_call_policy": "only_when_matching_api_key_selects_live_provider",
            "mutates_local_state": False,
            "secret_values_returned": False,
        },
    ]
