"""Offline integration readiness checks for blocked deployment gates."""

from __future__ import annotations

import tempfile
from collections.abc import Callable
from pathlib import Path
from typing import Any

from halo_swing_mcp import MCP_SERVER_NAME
import halo_swing_mcp.env as local_env
from halo_swing_mcp.binance_btc import LIVE_CONFIRMATION
from halo_swing_mcp.config import (
    LIVE_HTTP_TIMEOUT_SECONDS_ENV_NAME,
    get_settings,
)
from halo_swing_mcp.env import get_config_value
from halo_swing_mcp.providers import describe_market_data_provider_route
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
    live_data_api_key_status = get_live_data_api_key_status()
    live_data_provider_route = get_live_data_provider_route()
    return {
        "schema_version": "integration_setup_checklist.v1",
        "status": readiness["status"],
        "readiness_status": readiness["status"],
        "next_actions": readiness["next_actions"],
        "env_requirements": _setup_env_requirements(gates),
        "live_data_setup_summary": _live_data_setup_summary(
            live_data_api_key_status,
            live_data_provider_route,
        ),
        "local_commands": _setup_local_commands(),
        "live_data_smoke_commands": _setup_live_data_smoke_commands(),
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


def get_live_data_api_key_status() -> dict[str, Any]:
    """Return no-network live data API-key readiness without exposing secrets."""

    providers = {
        "market": _live_data_api_key_provider_status(
            provider_family="market",
            provider="polygon",
            preferred_env_key="POLYGON_API_KEY",
            accepted_env_keys=["HALO_SWING_MARKET_DATA_API_KEY", "POLYGON_API_KEY"],
            missing_name="market_ohlcv_api_key",
            smoke_command_name="get_market_snapshot_live_smoke",
            optional_live_mode_env="HALO_SWING_MARKET_DATA_MODE",
        ),
        "macro": _live_data_api_key_provider_status(
            provider_family="macro",
            provider="fred",
            preferred_env_key="FRED_API_KEY",
            accepted_env_keys=[
                "HALO_SWING_MACRO_API_KEY",
                "HALO_SWING_FRED_API_KEY",
                "FRED_API_KEY",
            ],
            missing_name="macro_api_key",
            smoke_command_name="get_macro_snapshot_live_smoke",
            optional_live_mode_env="HALO_SWING_MACRO_DATA_MODE",
        ),
        "news": _live_data_api_key_provider_status(
            provider_family="news",
            provider="newsapi",
            preferred_env_key="NEWS_API_KEY",
            accepted_env_keys=["HALO_SWING_NEWS_API_KEY", "NEWS_API_KEY"],
            missing_name="news_api_key",
            smoke_command_name="get_news_bundle_live_smoke",
            optional_live_mode_env="HALO_SWING_NEWS_DATA_MODE",
        ),
    }
    missing = [
        missing
        for provider_status in providers.values()
        for missing in provider_status["missing"]
    ]
    configured_provider_families = [
        family
        for family, provider_status in providers.items()
        if provider_status["configured"] is True
    ]
    missing_provider_families = [
        family
        for family, provider_status in providers.items()
        if provider_status["configured"] is not True
    ]
    provider_family_summary = {
        "required_provider_families": list(providers),
        "configured_provider_families": configured_provider_families,
        "missing_provider_families": missing_provider_families,
        "configured_count": len(configured_provider_families),
        "required_count": len(providers),
        "ready_to_run_live_smoke": not missing,
        "network_call": False,
        "mutates_local_state": False,
        "secret_values_returned": False,
    }
    one_shot_smoke_command = _local_command("run_api_key_pipeline_smoke")
    dotenv_file_status = _live_data_dotenv_file_status()
    provider_setup_actions = _live_data_provider_setup_actions_from_providers(
        providers
    )
    provider_smoke_plan = _live_data_provider_smoke_plan(
        provider_setup_actions=provider_setup_actions,
        one_shot_smoke_command=one_shot_smoke_command,
        ready_to_run_live_smoke=not missing,
    )
    live_data_setup_steps = _live_data_setup_steps(
        dotenv_file_status=dotenv_file_status,
        provider_family_summary=provider_family_summary,
        provider_smoke_plan=provider_smoke_plan,
        one_shot_smoke_command=one_shot_smoke_command,
        ready_to_run_live_smoke=not missing,
    )
    return {
        "schema_version": "live_data_api_key_status.v1",
        "status": "ready" if not missing else "blocked",
        "providers": providers,
        "provider_family_summary": provider_family_summary,
        "provider_smoke_plan": provider_smoke_plan,
        "missing": missing,
        "one_shot_smoke_command": one_shot_smoke_command,
        "dotenv_template": _live_data_dotenv_template(),
        "dotenv_file_status": dotenv_file_status,
        "live_data_setup_steps": live_data_setup_steps,
        "next_operator_action": _live_data_next_operator_action(
            dotenv_file_status=dotenv_file_status,
            provider_family_summary=provider_family_summary,
            live_data_setup_steps=live_data_setup_steps,
            one_shot_smoke_command=one_shot_smoke_command,
            ready_to_run_live_smoke=not missing,
        ),
        "dotenv": {
            "supported": True,
            "disabled": _truthy_config_value(get_config_value("HALO_SWING_DISABLE_DOTENV")),
            "precedence": [
                "exported environment variables",
                "launch-directory .env",
                "repo-root .env",
            ],
            "mutation": False,
        },
        "live_mode_required": False,
        "network_call": False,
        "mutates_local_state": False,
        "secret_values_returned": False,
        "hermes_runtime_started": False,
        "telegram_send_call": False,
        "send_call": False,
        "order_submission": False,
    }


def get_live_data_provider_route() -> dict[str, Any]:
    """Return the actual live data provider factory route without network calls."""

    route = describe_market_data_provider_route()
    return {
        **route,
        "api_key_status": get_live_data_api_key_status(),
        "live_mode_required": False,
        "mutates_local_state": False,
        "hermes_runtime_started": False,
        "telegram_send_call": False,
        "send_call": False,
        "order_submission": False,
    }


def validate_live_data_smoke_result(
    *,
    market_snapshot: dict[str, Any] | None = None,
    macro_snapshot: dict[str, Any] | None = None,
    news_bundle: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Validate caller-supplied live data smoke outputs without calling networks."""

    payloads = {
        "market": _normalize_optional_smoke_payload(market_snapshot, "market_snapshot"),
        "macro": _normalize_optional_smoke_payload(macro_snapshot, "macro_snapshot"),
        "news": _normalize_optional_smoke_payload(news_bundle, "news_bundle"),
    }
    checks: list[dict[str, Any]] = []
    checked_tools: list[str] = []

    if payloads["market"] is not None:
        checked_tools.append("get_market_snapshot")
        _extend_market_smoke_checks(checks, payloads["market"])
    if payloads["macro"] is not None:
        checked_tools.append("get_macro_snapshot")
        _extend_macro_smoke_checks(checks, payloads["macro"])
    if payloads["news"] is not None:
        checked_tools.append("get_news_bundle")
        _extend_news_smoke_checks(checks, payloads["news"])
    if not checked_tools:
        _add_smoke_check(
            checks,
            tool="live_data_smoke",
            name="at_least_one_payload_provided",
            passed=False,
            expected=True,
            actual=False,
        )

    return {
        "schema_version": "live_data_smoke_validation.v1",
        "status": "ok" if checks and all(check["passed"] for check in checks) else "conflict",
        "checked_tools": checked_tools,
        "checks": checks,
        "network_call": False,
        "live_data_required": False,
        "send_call": False,
        "order_submission": False,
        "secret_values_returned": False,
    }


def run_live_data_smoke(
    symbols: list[str] | None = None,
    topic: str = "macro",
) -> dict[str, Any]:
    """Run market, macro, and news smoke paths, then validate their outputs."""

    from halo_swing_mcp.tools import market as market_tools

    smoke_symbols = symbols if symbols is not None else ["QQQ"]
    provider_route = get_live_data_provider_route()
    api_key_status = (
        _optional_mapping(provider_route.get("api_key_status"))
        or get_live_data_api_key_status()
    )
    market_snapshot = market_tools.get_market_snapshot(smoke_symbols)
    macro_snapshot = market_tools.get_macro_snapshot()
    news_bundle = market_tools.get_news_bundle(topic)
    validation = validate_live_data_smoke_result(
        market_snapshot=market_snapshot,
        macro_snapshot=macro_snapshot,
        news_bundle=news_bundle,
    )
    network_call = any(
        [
            _mapping_value(
                _optional_mapping(market_snapshot.get("market_snapshot_contract")),
                "network_call",
            )
            is True,
            _mapping_value(
                _optional_mapping(macro_snapshot.get("macro_filter_contract")),
                "network_call",
            )
            is True,
            _mapping_value(
                _optional_mapping(news_bundle.get("news_source_policy_contract")),
                "network_call",
            )
            is True,
        ]
    )
    live_data_required = any(
        payload.get("live_data_required") is True
        for payload in [market_snapshot, macro_snapshot, news_bundle]
    )
    provider_error_summaries = _provider_error_summaries(
        market_snapshot=market_snapshot,
        macro_snapshot=macro_snapshot,
        news_bundle=news_bundle,
    )
    provider_smoke_summaries = _provider_smoke_summaries(
        market_snapshot=market_snapshot,
        macro_snapshot=macro_snapshot,
        news_bundle=news_bundle,
    )
    live_data_setup_summary = _live_data_setup_summary(
        api_key_status,
        provider_route,
    )
    provider_error_compact_summary = _provider_error_compact_summary(
        provider_error_summaries,
        provider_smoke_plan=_optional_mapping(
            live_data_setup_summary.get("provider_smoke_plan")
        )
        or {},
    )

    return {
        "schema_version": "live_data_smoke_run.v1",
        "status": validation["status"],
        "input": {
            "symbols": smoke_symbols,
            "topic": topic,
        },
        "market_snapshot": market_snapshot,
        "macro_snapshot": macro_snapshot,
        "news_bundle": news_bundle,
        "provider_route": provider_route,
        "live_data_setup_summary": live_data_setup_summary,
        "provider_smoke_summaries": provider_smoke_summaries,
        "provider_smoke_summary_count": len(provider_smoke_summaries),
        "provider_error_summaries": provider_error_summaries,
        "provider_error_summary_count": len(provider_error_summaries),
        "failed_provider_families": provider_error_compact_summary[
            "failed_provider_families"
        ],
        "failed_provider_count": provider_error_compact_summary[
            "failed_provider_count"
        ],
        "first_provider_error_summary": provider_error_compact_summary[
            "first_provider_error_summary"
        ],
        "next_provider_recovery_action": provider_error_compact_summary[
            "next_provider_recovery_action"
        ],
        "next_provider_recovery_smoke": provider_error_compact_summary[
            "next_provider_recovery_smoke"
        ],
        "next_provider_recovery_smoke_command_name": (
            provider_error_compact_summary[
                "next_provider_recovery_smoke_command_name"
            ]
        ),
        "provider_recovery_smokes": provider_error_compact_summary[
            "provider_recovery_smokes"
        ],
        "provider_recovery_smoke_count": provider_error_compact_summary[
            "provider_recovery_smoke_count"
        ],
        "validation": validation,
        "network_call": network_call,
        "live_data_required": live_data_required,
        "send_call": False,
        "order_submission": False,
        "secret_values_returned": False,
    }


def _provider_error_summaries(
    *,
    market_snapshot: dict[str, Any],
    macro_snapshot: dict[str, Any],
    news_bundle: dict[str, Any],
) -> list[dict[str, Any]]:
    summaries: list[dict[str, Any]] = []
    for payload in [market_snapshot, macro_snapshot, news_bundle]:
        summary = _optional_mapping(payload.get("error_summary"))
        if summary is not None:
            summaries.append(summary)
    return summaries


def _provider_smoke_summaries(
    *,
    market_snapshot: dict[str, Any],
    macro_snapshot: dict[str, Any],
    news_bundle: dict[str, Any],
) -> list[dict[str, Any]]:
    summaries: list[dict[str, Any]] = []
    for payload in [market_snapshot, macro_snapshot, news_bundle]:
        summary = _optional_mapping(payload.get("provider_smoke_summary"))
        if summary is not None:
            summaries.append(summary)
    return summaries


def _provider_error_compact_summary(
    provider_error_summaries: list[dict[str, Any]],
    *,
    provider_smoke_plan: dict[str, Any] | None = None,
) -> dict[str, Any]:
    failed_provider_families: list[str] = []
    for summary in provider_error_summaries:
        provider_family = summary.get("provider_family")
        if (
            isinstance(provider_family, str)
            and provider_family not in failed_provider_families
        ):
            failed_provider_families.append(provider_family)
    first_summary = provider_error_summaries[0] if provider_error_summaries else None
    next_provider_recovery_action = (
        first_summary.get("next_setup_action") if first_summary is not None else None
    )
    next_provider_recovery_smoke = _provider_recovery_smoke_command(
        first_summary=first_summary,
        provider_smoke_plan=provider_smoke_plan,
    )
    provider_recovery_smokes = _provider_recovery_smoke_commands(
        provider_error_summaries=provider_error_summaries,
        provider_smoke_plan=provider_smoke_plan,
    )
    return {
        "failed_provider_families": failed_provider_families,
        "failed_provider_count": len(failed_provider_families),
        "first_provider_error_summary": first_summary,
        "next_provider_recovery_action": next_provider_recovery_action,
        "next_provider_recovery_smoke": next_provider_recovery_smoke,
        "next_provider_recovery_smoke_command_name": (
            next_provider_recovery_smoke.get("smoke_command_name")
            if next_provider_recovery_smoke is not None
            else None
        ),
        "provider_recovery_smokes": provider_recovery_smokes,
        "provider_recovery_smoke_count": len(provider_recovery_smokes),
    }


def _provider_recovery_smoke_commands(
    *,
    provider_error_summaries: list[dict[str, Any]],
    provider_smoke_plan: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    recovery_smokes: list[dict[str, Any]] = []
    seen_command_names: set[str] = set()
    for summary in provider_error_summaries:
        smoke_command = _provider_recovery_smoke_command(
            first_summary=summary,
            provider_smoke_plan=provider_smoke_plan,
        )
        if smoke_command is None:
            continue
        smoke_command_name = smoke_command.get("smoke_command_name")
        if not isinstance(smoke_command_name, str):
            continue
        if smoke_command_name in seen_command_names:
            continue
        recovery_smokes.append(smoke_command)
        seen_command_names.add(smoke_command_name)
    return recovery_smokes


def _provider_recovery_smoke_command(
    *,
    first_summary: dict[str, Any] | None,
    provider_smoke_plan: dict[str, Any] | None,
) -> dict[str, Any] | None:
    if first_summary is None or provider_smoke_plan is None:
        return None
    smoke_command_name = first_summary.get("smoke_command_name")
    if not isinstance(smoke_command_name, str):
        return None
    provider_smokes = provider_smoke_plan.get("provider_smokes")
    if not isinstance(provider_smokes, list):
        return None
    for provider_smoke in provider_smokes:
        provider_smoke_row = _optional_mapping(provider_smoke)
        if provider_smoke_row is None:
            continue
        if provider_smoke_row.get("smoke_command_name") == smoke_command_name:
            return provider_smoke_row
    return None


def run_integration_smoke(
    symbols: list[str] | None = None,
    topic: str = "macro",
) -> dict[str, Any]:
    """Run environment readiness and live data smoke in one payload."""

    readiness = get_integration_readiness()
    live_data_api_key_status = get_live_data_api_key_status()
    live_data_smoke = run_live_data_smoke(symbols=symbols, topic=topic)
    provider_route = _optional_mapping(live_data_smoke.get("provider_route")) or {}
    readiness_ready = readiness["status"] == "ready"
    live_data_smoke_ok = live_data_smoke["status"] == "ok"
    return {
        "schema_version": "integration_smoke_run.v1",
        "status": "ok" if readiness_ready and live_data_smoke_ok else "blocked",
        "readiness_status": readiness["status"],
        "live_data_smoke_status": live_data_smoke["status"],
        "readiness": readiness,
        "live_data_smoke": live_data_smoke,
        "live_data_setup_summary": _live_data_setup_summary(
            live_data_api_key_status,
            provider_route,
        ),
        "provider_route_summary": _api_key_pipeline_provider_route_summary(
            provider_route,
        ),
        "network_call": live_data_smoke["network_call"],
        "live_data_required": live_data_smoke["live_data_required"],
        "hermes_runtime_started": False,
        "telegram_send_call": False,
        "send_call": False,
        "order_submission": False,
        "secret_values_returned": False,
        "mutates_local_state": False,
    }


def run_live_signal_workflow_smoke(
    asset: str = "TQQQ",
    timeframe: str = "swing_3d_10d",
) -> dict[str, Any]:
    """Run the live-data-backed signal/report workflow and verify boundaries."""

    from halo_swing_mcp.tools import reporting as reporting_tools
    from halo_swing_mcp.tools import scoring as scoring_tools

    provider_route = get_live_data_provider_route()
    api_key_status = (
        _optional_mapping(provider_route.get("api_key_status"))
        or get_live_data_api_key_status()
    )
    signal = scoring_tools.score_leverage_swing(asset=asset, timeframe=timeframe)
    trade_guide = scoring_tools.generate_trade_guide(asset=asset, timeframe=timeframe)
    position_review = scoring_tools.evaluate_position(asset=asset)
    latest_signal_report = reporting_tools.generate_latest_signal_report(
        asset=asset,
        timeframe=timeframe,
    )
    checks: list[dict[str, Any]] = []
    _extend_live_signal_workflow_checks(
        checks,
        signal=signal,
        trade_guide=trade_guide,
        position_review=position_review,
        latest_signal_report=latest_signal_report,
    )
    source_contract = _optional_mapping(signal.get("source_data_contract"))
    network_call = _mapping_value(source_contract, "network_call") is True
    live_data_required = any(
        payload.get("live_data_required") is True
        for payload in [
            signal,
            trade_guide,
            position_review,
            latest_signal_report,
        ]
    )

    return {
        "schema_version": "live_signal_workflow_smoke_run.v1",
        "status": "ok" if checks and all(check["passed"] for check in checks) else "conflict",
        "input": {
            "asset": asset,
            "timeframe": timeframe,
        },
        "executed_tools": [
            "score_leverage_swing",
            "generate_trade_guide",
            "evaluate_position",
            "generate_latest_signal_report",
        ],
        "live_data_setup_summary": _live_data_setup_summary(
            api_key_status,
            provider_route,
        ),
        "signal_summary": _workflow_signal_summary(signal),
        "trade_guide_summary": _workflow_contract_summary(
            trade_guide,
            contract_key="trade_guide_contract",
            guard_key="trade_guide_guard",
        ),
        "position_review_summary": _workflow_contract_summary(
            position_review,
            contract_key="position_management_contract",
            guard_key="position_management_guard",
        ),
        "latest_signal_report_summary": _workflow_report_summary(
            latest_signal_report,
        ),
        "checks": checks,
        "network_call": network_call,
        "live_data_required": live_data_required,
        "hermes_runtime_started": False,
        "telegram_send_call": False,
        "send_call": False,
        "order_submission": False,
        "mutates_local_state": False,
        "secret_values_returned": False,
    }


def run_live_recording_smoke(
    asset: str = "TQQQ",
    timeframe: str = "swing_3d_10d",
    ledger_path: str | None = None,
) -> dict[str, Any]:
    """Record a generated signal and verify live run-journal boundaries."""

    if ledger_path is None:
        with tempfile.TemporaryDirectory(prefix="halo_swing_recording_smoke_") as tmpdir:
            temporary_ledger_path = str(Path(tmpdir) / "signal_ledger.jsonl")
            return _run_live_recording_smoke_with_ledger(
                asset=asset,
                timeframe=timeframe,
                ledger_path=temporary_ledger_path,
                ledger_persisted=False,
            )

    return _run_live_recording_smoke_with_ledger(
        asset=asset,
        timeframe=timeframe,
        ledger_path=ledger_path,
        ledger_persisted=True,
    )


def _run_live_recording_smoke_with_ledger(
    *,
    asset: str,
    timeframe: str,
    ledger_path: str,
    ledger_persisted: bool,
) -> dict[str, Any]:
    from halo_swing_mcp.tools import recording as recording_tools
    from halo_swing_mcp.tools import scoring as scoring_tools

    provider_route = get_live_data_provider_route()
    api_key_status = (
        _optional_mapping(provider_route.get("api_key_status"))
        or get_live_data_api_key_status()
    )
    signal = scoring_tools.score_leverage_swing(asset=asset, timeframe=timeframe)
    recorded = recording_tools.record_signal(signal=signal, ledger_path=ledger_path)
    checks: list[dict[str, Any]] = []
    _extend_live_recording_checks(checks, signal=signal, recorded=recorded)

    return {
        "schema_version": "live_recording_smoke_run.v1",
        "status": "ok" if checks and all(check["passed"] for check in checks) else "conflict",
        "input": {
            "asset": asset,
            "timeframe": timeframe,
            "ledger_path_provided": ledger_persisted,
        },
        "executed_tools": [
            "score_leverage_swing",
            "record_signal",
        ],
        "live_data_setup_summary": _live_data_setup_summary(
            api_key_status,
            provider_route,
        ),
        "signal_summary": _workflow_signal_summary(signal),
        "recording_summary": _recording_summary(recorded, ledger_persisted),
        "checks": checks,
        "network_call": _recording_network_call(recorded),
        "live_data_required": recorded.get("live_data_required") is True,
        "ledger_persisted": ledger_persisted,
        "mutates_local_state": ledger_persisted,
        "hermes_runtime_started": False,
        "telegram_send_call": False,
        "send_call": False,
        "order_submission": False,
        "secret_values_returned": False,
    }


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
        live_data_smoke_summary
    )
    api_key_provider_recovery_summary = _api_key_provider_recovery_summary(
        api_key_provider_recovery_checklist
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
        next_operator_action=next_operator_action,
    )
    api_key_pipeline_stage_summary = _api_key_pipeline_stage_summary(
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
        "api_key_failure_category": api_key_pipeline_failure_summary.get(
            "failure_category"
        ),
        "api_key_has_failures": (
            api_key_pipeline_failure_summary.get("has_failures") is True
        ),
        "api_key_failed_stage_names": _string_list(
            api_key_pipeline_failure_summary.get("failed_stage_names")
        ),
        "api_key_failed_check_keys": _string_list(
            api_key_pipeline_failure_summary.get("failed_check_keys")
        ),
        "api_key_tools_with_failures": _string_list(
            api_key_pipeline_failure_summary.get("tools_with_failures")
        ),
        "api_key_first_failed_stage_name": api_key_pipeline_failure_summary.get(
            "first_failed_stage_name"
        ),
        "api_key_first_failed_check_key": api_key_pipeline_failure_summary.get(
            "first_failed_check_key"
        ),
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
        "provider_recovery_required": (
            api_key_provider_recovery_summary.get("provider_recovery_required")
            is True
        ),
        "provider_recovery_summary_status": api_key_provider_recovery_summary.get(
            "status"
        ),
        "provider_recovery_action_status": api_key_provider_recovery_summary.get(
            "provider_recovery_action_status"
        ),
        "provider_recovery_item_count": api_key_provider_recovery_summary.get(
            "item_count",
            0,
        ),
        "provider_recovery_pending_count": api_key_provider_recovery_summary.get(
            "provider_recovery_pending_count",
            0,
        ),
        "provider_recovery_blocked_count": api_key_provider_recovery_summary.get(
            "provider_recovery_blocked_count",
            0,
        ),
        "provider_error_count": api_key_provider_recovery_summary.get(
            "provider_error_count",
            0,
        ),
        "provider_recovery_smoke_available_count": (
            api_key_provider_recovery_summary.get(
                "provider_recovery_smoke_available_count"
            )
        ),
        "provider_recovery_smoke_unavailable_count": (
            api_key_provider_recovery_summary.get(
                "provider_recovery_smoke_unavailable_count"
            )
        ),
        "provider_recovery_all_smokes_available": (
            api_key_provider_recovery_summary.get(
                "provider_recovery_all_smokes_available"
            )
            is True
        ),
        "provider_recovery_network_call_count": (
            api_key_provider_recovery_summary.get(
                "provider_recovery_network_call_count"
            )
        ),
        "provider_recovery_all_network_calls": (
            api_key_provider_recovery_summary.get(
                "provider_recovery_all_network_calls"
            )
            is True
        ),
        "provider_recovery_mutates_local_state_count": (
            api_key_provider_recovery_summary.get(
                "provider_recovery_mutates_local_state_count"
            )
        ),
        "provider_recovery_any_mutates_local_state": (
            api_key_provider_recovery_summary.get(
                "provider_recovery_any_mutates_local_state"
            )
            is True
        ),
        "provider_recovery_secret_values_returned_count": (
            api_key_provider_recovery_summary.get(
                "provider_recovery_secret_values_returned_count"
            )
        ),
        "provider_recovery_any_secret_values_returned": (
            api_key_provider_recovery_summary.get(
                "provider_recovery_any_secret_values_returned"
            )
            is True
        ),
        "provider_recovery_next_setup_actions": _string_list(
            api_key_provider_recovery_summary.get(
                "provider_recovery_next_setup_actions"
            )
        ),
        "provider_recovery_exception_types": _string_list(
            api_key_provider_recovery_summary.get(
                "provider_recovery_exception_types"
            )
        ),
        "provider_recovery_exception_message_returned_count": (
            api_key_provider_recovery_summary.get(
                "provider_recovery_exception_message_returned_count"
            )
        ),
        "provider_recovery_any_exception_messages_returned": (
            api_key_provider_recovery_summary.get(
                "provider_recovery_any_exception_messages_returned"
            )
            is True
        ),
        "provider_recovery_url_returned_count": (
            api_key_provider_recovery_summary.get(
                "provider_recovery_url_returned_count"
            )
        ),
        "provider_recovery_any_urls_returned": (
            api_key_provider_recovery_summary.get(
                "provider_recovery_any_urls_returned"
            )
            is True
        ),
        "provider_recovery_statuses": _string_list(
            api_key_provider_recovery_summary.get("provider_recovery_statuses")
        ),
        "provider_recovery_all_pending": (
            api_key_provider_recovery_summary.get("provider_recovery_all_pending")
            is True
        ),
        "provider_recovery_retry_ready": (
            api_key_provider_recovery_summary.get("provider_recovery_retry_ready")
            is True
        ),
        "provider_recovery_all_retryable": (
            api_key_provider_recovery_summary.get(
                "provider_recovery_all_retryable"
            )
            is True
        ),
        "provider_recovery_has_pending": (
            api_key_provider_recovery_summary.get("provider_recovery_has_pending")
            is True
        ),
        "provider_recovery_has_blocked": (
            api_key_provider_recovery_summary.get("provider_recovery_has_blocked")
            is True
        ),
        "provider_recovery_provider_families": _string_list(
            api_key_provider_recovery_summary.get(
                "provider_recovery_provider_families"
            )
        ),
        "provider_recovery_providers": _string_list(
            api_key_provider_recovery_summary.get("provider_recovery_providers")
        ),
        "provider_recovery_pending_provider_families": _string_list(
            api_key_provider_recovery_summary.get(
                "provider_recovery_pending_provider_families"
            )
        ),
        "provider_recovery_pending_providers": _string_list(
            api_key_provider_recovery_summary.get(
                "provider_recovery_pending_providers"
            )
        ),
        "provider_recovery_blocked_provider_families": _string_list(
            api_key_provider_recovery_summary.get(
                "provider_recovery_blocked_provider_families"
            )
        ),
        "provider_recovery_blocked_providers": _string_list(
            api_key_provider_recovery_summary.get(
                "provider_recovery_blocked_providers"
            )
        ),
        "provider_recovery_smoke_command_names": _string_list(
            api_key_provider_recovery_summary.get(
                "provider_recovery_smoke_command_names"
            )
        ),
        "provider_recovery_smoke_commands": _string_list(
            api_key_provider_recovery_summary.get("provider_recovery_smoke_commands")
        ),
        "provider_recovery_pending_smoke_command_names": _string_list(
            api_key_provider_recovery_summary.get(
                "provider_recovery_pending_smoke_command_names"
            )
        ),
        "provider_recovery_pending_smoke_commands": _string_list(
            api_key_provider_recovery_summary.get(
                "provider_recovery_pending_smoke_commands"
            )
        ),
        "provider_recovery_blocked_smoke_command_names": _string_list(
            api_key_provider_recovery_summary.get(
                "provider_recovery_blocked_smoke_command_names"
            )
        ),
        "provider_recovery_blocked_smoke_commands": _string_list(
            api_key_provider_recovery_summary.get(
                "provider_recovery_blocked_smoke_commands"
            )
        ),
        "provider_recovery_network_call_policies": _string_list(
            api_key_provider_recovery_summary.get(
                "provider_recovery_network_call_policies"
            )
        ),
        "provider_recovery_preferred_env_keys": _string_list(
            api_key_provider_recovery_summary.get(
                "provider_recovery_preferred_env_keys"
            )
        ),
        "provider_recovery_accepted_env_keys": _string_list(
            api_key_provider_recovery_summary.get(
                "provider_recovery_accepted_env_keys"
            )
        ),
        "provider_recovery_accepted_env_key_groups": [
            _string_list(group)
            for group in api_key_provider_recovery_summary.get(
                "provider_recovery_accepted_env_key_groups", []
            )
            if isinstance(group, list)
        ],
        "next_pending_recovery_smoke_command_name": (
            api_key_provider_recovery_summary.get(
                "next_pending_recovery_smoke_command_name"
            )
        ),
        "next_pending_recovery_smoke_command": (
            api_key_provider_recovery_summary.get(
                "next_pending_recovery_smoke_command"
            )
        ),
        "next_pending_recovery_provider_family": (
            api_key_provider_recovery_summary.get(
                "next_pending_recovery_provider_family"
            )
        ),
        "next_pending_recovery_provider": (
            api_key_provider_recovery_summary.get("next_pending_recovery_provider")
        ),
        "next_pending_recovery_next_setup_action": (
            api_key_provider_recovery_summary.get(
                "next_pending_recovery_next_setup_action"
            )
        ),
        "next_pending_recovery_preferred_env_key": (
            api_key_provider_recovery_summary.get(
                "next_pending_recovery_preferred_env_key"
            )
        ),
        "next_pending_recovery_accepted_env_keys": _string_list(
            api_key_provider_recovery_summary.get(
                "next_pending_recovery_accepted_env_keys"
            )
        ),
        "next_pending_recovery_network_call_policy": (
            api_key_provider_recovery_summary.get(
                "next_pending_recovery_network_call_policy"
            )
        ),
        "next_pending_recovery_smoke_available": (
            api_key_provider_recovery_summary.get(
                "next_pending_recovery_smoke_available"
            )
            is True
        ),
        "next_pending_recovery_network_call": (
            api_key_provider_recovery_summary.get(
                "next_pending_recovery_network_call"
            )
            is True
        ),
        "next_pending_recovery_mutates_local_state": (
            api_key_provider_recovery_summary.get(
                "next_pending_recovery_mutates_local_state"
            )
            is True
        ),
        "next_pending_recovery_secret_values_returned": False,
        "next_blocked_recovery_smoke_command_name": (
            api_key_provider_recovery_summary.get(
                "next_blocked_recovery_smoke_command_name"
            )
        ),
        "next_blocked_recovery_smoke_command": (
            api_key_provider_recovery_summary.get(
                "next_blocked_recovery_smoke_command"
            )
        ),
        "next_blocked_recovery_provider_family": (
            api_key_provider_recovery_summary.get(
                "next_blocked_recovery_provider_family"
            )
        ),
        "next_blocked_recovery_provider": (
            api_key_provider_recovery_summary.get("next_blocked_recovery_provider")
        ),
        "next_blocked_recovery_next_setup_action": (
            api_key_provider_recovery_summary.get(
                "next_blocked_recovery_next_setup_action"
            )
        ),
        "next_blocked_recovery_preferred_env_key": (
            api_key_provider_recovery_summary.get(
                "next_blocked_recovery_preferred_env_key"
            )
        ),
        "next_blocked_recovery_accepted_env_keys": _string_list(
            api_key_provider_recovery_summary.get(
                "next_blocked_recovery_accepted_env_keys"
            )
        ),
        "next_blocked_recovery_network_call_policy": (
            api_key_provider_recovery_summary.get(
                "next_blocked_recovery_network_call_policy"
            )
        ),
        "next_blocked_recovery_smoke_available": (
            api_key_provider_recovery_summary.get(
                "next_blocked_recovery_smoke_available"
            )
            is True
        ),
        "next_blocked_recovery_network_call": (
            api_key_provider_recovery_summary.get(
                "next_blocked_recovery_network_call"
            )
            is True
        ),
        "next_blocked_recovery_mutates_local_state": (
            api_key_provider_recovery_summary.get(
                "next_blocked_recovery_mutates_local_state"
            )
            is True
        ),
        "next_blocked_recovery_secret_values_returned": False,
        "next_recovery_smoke_command_name": api_key_provider_recovery_summary.get(
            "next_recovery_smoke_command_name"
        ),
        "next_recovery_smoke_command": api_key_provider_recovery_summary.get(
            "next_recovery_smoke_command"
        ),
        "next_recovery_provider_family": api_key_provider_recovery_summary.get(
            "next_recovery_provider_family"
        ),
        "next_recovery_provider": api_key_provider_recovery_summary.get(
            "next_recovery_provider"
        ),
        "next_recovery_next_setup_action": api_key_provider_recovery_summary.get(
            "next_recovery_next_setup_action"
        ),
        "next_recovery_preferred_env_key": api_key_provider_recovery_summary.get(
            "next_recovery_preferred_env_key"
        ),
        "next_recovery_accepted_env_keys": _string_list(
            api_key_provider_recovery_summary.get(
                "next_recovery_accepted_env_keys"
            )
        ),
        "next_recovery_network_call_policy": api_key_provider_recovery_summary.get(
            "next_recovery_network_call_policy"
        ),
        "next_recovery_smoke_available": (
            api_key_provider_recovery_summary.get("next_recovery_smoke_available")
            is True
        ),
        "next_recovery_network_call": (
            api_key_provider_recovery_summary.get("next_recovery_network_call")
            is True
        ),
        "next_recovery_mutates_local_state": (
            api_key_provider_recovery_summary.get("next_recovery_mutates_local_state")
            is True
        ),
        "next_recovery_exception_type": api_key_provider_recovery_summary.get(
            "next_recovery_exception_type"
        ),
        "next_recovery_exception_message_returned": (
            api_key_provider_recovery_summary.get(
                "next_recovery_exception_message_returned"
            )
            is True
        ),
        "next_recovery_url_returned": (
            api_key_provider_recovery_summary.get("next_recovery_url_returned")
            is True
        ),
        "next_recovery_secret_values_returned": False,
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


def _normalize_optional_smoke_payload(
    payload: dict[str, Any] | None,
    field_name: str,
) -> dict[str, Any] | None:
    if payload is None:
        return None
    if not isinstance(payload, dict):
        raise ValueError(f"{field_name} must be an object when provided")
    return payload


def _extend_market_smoke_checks(
    checks: list[dict[str, Any]],
    payload: dict[str, Any],
) -> None:
    contract = _optional_mapping(payload.get("market_snapshot_contract"))
    guard = _optional_mapping(payload.get("market_snapshot_guard"))
    _add_smoke_check(
        checks,
        tool="get_market_snapshot",
        name="payload_live_data_required",
        passed=payload.get("live_data_required") is True,
        expected=True,
        actual=payload.get("live_data_required"),
    )
    _add_smoke_check(
        checks,
        tool="get_market_snapshot",
        name="contract_live_data_required",
        passed=_mapping_value(contract, "live_data_required") is True,
        expected=True,
        actual=_mapping_value(contract, "live_data_required"),
    )
    _add_smoke_check(
        checks,
        tool="get_market_snapshot",
        name="contract_network_call",
        passed=_mapping_value(contract, "network_call") is True,
        expected=True,
        actual=_mapping_value(contract, "network_call"),
    )
    _add_guard_status_check(checks, "get_market_snapshot", guard)
    _add_guard_check(
        checks,
        "get_market_snapshot",
        guard,
        "live_data_boundary_declared",
    )
    _add_smoke_check(
        checks,
        tool="get_market_snapshot",
        name="secret_values_not_returned",
        passed=_contract_secret_values_returned(contract) is False,
        expected=False,
        actual=_contract_secret_values_returned(contract),
    )


def _extend_macro_smoke_checks(
    checks: list[dict[str, Any]],
    payload: dict[str, Any],
) -> None:
    contract = _optional_mapping(payload.get("macro_filter_contract"))
    guard = _optional_mapping(payload.get("macro_filter_guard"))
    _add_smoke_check(
        checks,
        tool="get_macro_snapshot",
        name="payload_live_data_required",
        passed=payload.get("live_data_required") is True,
        expected=True,
        actual=payload.get("live_data_required"),
    )
    _add_smoke_check(
        checks,
        tool="get_macro_snapshot",
        name="contract_live_data_required",
        passed=_mapping_value(contract, "live_data_required") is True,
        expected=True,
        actual=_mapping_value(contract, "live_data_required"),
    )
    _add_smoke_check(
        checks,
        tool="get_macro_snapshot",
        name="contract_network_call",
        passed=_mapping_value(contract, "network_call") is True,
        expected=True,
        actual=_mapping_value(contract, "network_call"),
    )
    _add_guard_status_check(checks, "get_macro_snapshot", guard)
    _add_guard_check(
        checks,
        "get_macro_snapshot",
        guard,
        "live_data_boundary_declared",
    )
    _add_guard_check(checks, "get_macro_snapshot", guard, "network_call_declared")
    _add_smoke_check(
        checks,
        tool="get_macro_snapshot",
        name="secret_values_not_returned",
        passed=_contract_secret_values_returned(contract) is False,
        expected=False,
        actual=_contract_secret_values_returned(contract),
    )


def _extend_news_smoke_checks(
    checks: list[dict[str, Any]],
    payload: dict[str, Any],
) -> None:
    contract = _optional_mapping(payload.get("news_source_policy_contract"))
    score_contract = _optional_mapping(payload.get("news_score_contract"))
    guard = _optional_mapping(payload.get("news_source_policy_guard"))
    _add_smoke_check(
        checks,
        tool="get_news_bundle",
        name="payload_live_data_required",
        passed=payload.get("live_data_required") is True,
        expected=True,
        actual=payload.get("live_data_required"),
    )
    _add_smoke_check(
        checks,
        tool="get_news_bundle",
        name="contract_live_data_required",
        passed=_mapping_value(contract, "live_data_required") is True,
        expected=True,
        actual=_mapping_value(contract, "live_data_required"),
    )
    _add_smoke_check(
        checks,
        tool="get_news_bundle",
        name="contract_network_call",
        passed=_mapping_value(contract, "network_call") is True,
        expected=True,
        actual=_mapping_value(contract, "network_call"),
    )
    _add_guard_status_check(checks, "get_news_bundle", guard)
    _add_guard_check(checks, "get_news_bundle", guard, "live_data_boundary_declared")
    _add_guard_check(checks, "get_news_bundle", guard, "network_call_declared")
    _add_guard_check(checks, "get_news_bundle", guard, "secret_values_not_returned")
    _add_smoke_check(
        checks,
        tool="get_news_bundle",
        name="source_contract_secret_values_not_returned",
        passed=_contract_secret_values_returned(contract) is False,
        expected=False,
        actual=_contract_secret_values_returned(contract),
    )
    _add_smoke_check(
        checks,
        tool="get_news_bundle",
        name="score_contract_secret_values_not_returned",
        passed=_contract_secret_values_returned(score_contract) is False,
        expected=False,
        actual=_contract_secret_values_returned(score_contract),
    )


def _extend_live_signal_workflow_checks(
    checks: list[dict[str, Any]],
    *,
    signal: dict[str, Any],
    trade_guide: dict[str, Any],
    position_review: dict[str, Any],
    latest_signal_report: dict[str, Any],
) -> None:
    source_contract = _optional_mapping(signal.get("source_data_contract"))
    _add_smoke_check(
        checks,
        tool="score_leverage_swing",
        name="payload_live_data_required",
        passed=signal.get("live_data_required") is True,
        expected=True,
        actual=signal.get("live_data_required"),
    )
    _add_smoke_check(
        checks,
        tool="score_leverage_swing",
        name="source_contract_live_data_required",
        passed=_mapping_value(source_contract, "live_data_required") is True,
        expected=True,
        actual=_mapping_value(source_contract, "live_data_required"),
    )
    _add_smoke_check(
        checks,
        tool="score_leverage_swing",
        name="source_contract_network_call",
        passed=_mapping_value(source_contract, "network_call") is True,
        expected=True,
        actual=_mapping_value(source_contract, "network_call"),
    )
    _extend_workflow_contract_checks(
        checks,
        tool="generate_trade_guide",
        payload=trade_guide,
        contract_key="trade_guide_contract",
        guard_key="trade_guide_guard",
        live_check_name="live_data_boundary_declared",
    )
    _extend_workflow_contract_checks(
        checks,
        tool="evaluate_position",
        payload=position_review,
        contract_key="position_management_contract",
        guard_key="position_management_guard",
        live_check_name="live_data_boundary_declared",
    )
    _extend_latest_signal_report_workflow_checks(checks, latest_signal_report)


def _workflow_signal_summary(signal: dict[str, Any]) -> dict[str, Any]:
    return {
        "signal_id": signal.get("signal_id"),
        "run_id": signal.get("run_id"),
        "asset": signal.get("asset"),
        "underlying": signal.get("underlying"),
        "timeframe": signal.get("timeframe"),
        "action": signal.get("action"),
        "source_data_contract": signal.get("source_data_contract"),
        "live_data_required": signal.get("live_data_required"),
    }


def _workflow_contract_summary(
    payload: dict[str, Any],
    *,
    contract_key: str,
    guard_key: str,
) -> dict[str, Any]:
    guard = _optional_mapping(payload.get(guard_key))
    return {
        "asset": payload.get("asset"),
        "underlying": payload.get("underlying"),
        "action": payload.get("action"),
        "contract": payload.get(contract_key),
        "guard_status": _mapping_value(guard, "status"),
        "live_data_required": payload.get("live_data_required"),
    }


def _workflow_report_summary(payload: dict[str, Any]) -> dict[str, Any]:
    guard = _optional_mapping(payload.get("report_contract_guard"))
    return {
        "schema_version": payload.get("schema_version"),
        "asset": payload.get("asset"),
        "underlying": payload.get("underlying"),
        "timeframe": payload.get("timeframe"),
        "action": payload.get("action"),
        "source_signal_ref": payload.get("source_signal_ref"),
        "guard_status": _mapping_value(guard, "status"),
        "live_data_required": payload.get("live_data_required"),
    }


def _extend_live_recording_checks(
    checks: list[dict[str, Any]],
    *,
    signal: dict[str, Any],
    recorded: dict[str, Any],
) -> None:
    source_contract = _optional_mapping(signal.get("source_data_contract"))
    record = _optional_mapping(recorded.get("record"))
    run_journal = _optional_mapping(_mapping_value(record, "run_journal"))
    run_journal_contract = _optional_mapping(recorded.get("run_journal_contract"))
    stored_signal = _optional_mapping(_mapping_value(record, "signal"))
    _add_smoke_check(
        checks,
        tool="score_leverage_swing",
        name="payload_live_data_required",
        passed=signal.get("live_data_required") is True,
        expected=True,
        actual=signal.get("live_data_required"),
    )
    _add_smoke_check(
        checks,
        tool="score_leverage_swing",
        name="source_contract_network_call",
        passed=_mapping_value(source_contract, "network_call") is True,
        expected=True,
        actual=_mapping_value(source_contract, "network_call"),
    )
    _add_smoke_check(
        checks,
        tool="record_signal",
        name="recording_live_data_required",
        passed=recorded.get("live_data_required") is True,
        expected=True,
        actual=recorded.get("live_data_required"),
    )
    _add_smoke_check(
        checks,
        tool="record_signal",
        name="stored_signal_live_data_required",
        passed=_mapping_value(stored_signal, "live_data_required") is True,
        expected=True,
        actual=_mapping_value(stored_signal, "live_data_required"),
    )
    _add_smoke_check(
        checks,
        tool="record_signal",
        name="run_journal_live_data_required",
        passed=_mapping_value(run_journal, "live_data_required") is True,
        expected=True,
        actual=_mapping_value(run_journal, "live_data_required"),
    )
    _add_smoke_check(
        checks,
        tool="record_signal",
        name="run_journal_network_call",
        passed=_mapping_value(run_journal, "network_call") is True,
        expected=True,
        actual=_mapping_value(run_journal, "network_call"),
    )
    _add_smoke_check(
        checks,
        tool="record_signal",
        name="run_journal_contract_network_call",
        passed=_mapping_value(run_journal_contract, "network_call") is True,
        expected=True,
        actual=_mapping_value(run_journal_contract, "network_call"),
    )
    _add_smoke_check(
        checks,
        tool="record_signal",
        name="no_db_required",
        passed=_mapping_value(run_journal, "db_required") is False,
        expected=False,
        actual=_mapping_value(run_journal, "db_required"),
    )


def _recording_summary(
    recorded: dict[str, Any],
    ledger_persisted: bool,
) -> dict[str, Any]:
    record = _optional_mapping(recorded.get("record"))
    run_journal = _optional_mapping(_mapping_value(record, "run_journal"))
    run_journal_contract = _optional_mapping(recorded.get("run_journal_contract"))
    return {
        "status": recorded.get("status"),
        "signal_id": recorded.get("signal_id"),
        "ledger_ref": recorded.get("ledger_ref") if ledger_persisted else "ephemeral",
        "ledger_persisted": ledger_persisted,
        "run_journal": {
            "schema_version": _mapping_value(run_journal, "schema_version"),
            "run_id": _mapping_value(run_journal, "run_id"),
            "signal_id": _mapping_value(run_journal, "signal_id"),
            "network_call": _mapping_value(run_journal, "network_call"),
            "db_required": _mapping_value(run_journal, "db_required"),
            "secret_values_returned": _mapping_value(
                run_journal,
                "secret_values_returned",
            ),
            "live_data_required": _mapping_value(run_journal, "live_data_required"),
        },
        "run_journal_contract": run_journal_contract,
        "live_data_required": recorded.get("live_data_required"),
    }


def _recording_network_call(recorded: dict[str, Any]) -> bool:
    record = _optional_mapping(recorded.get("record"))
    run_journal = _optional_mapping(_mapping_value(record, "run_journal"))
    return _mapping_value(run_journal, "network_call") is True


def _run_api_key_pipeline_sub_smoke(
    *,
    tool_name: str,
    runner: Callable[[], dict[str, Any]],
    live_data_setup_summary: dict[str, Any],
    provider_route: dict[str, Any],
) -> dict[str, Any]:
    try:
        return runner()
    except Exception as exc:
        return _api_key_pipeline_sub_smoke_exception_payload(
            tool_name=tool_name,
            exception=exc,
            live_data_setup_summary=live_data_setup_summary,
            provider_route=provider_route,
        )


def _api_key_pipeline_sub_smoke_exception_payload(
    *,
    tool_name: str,
    exception: Exception,
    live_data_setup_summary: dict[str, Any],
    provider_route: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema_version": "api_key_pipeline_sub_smoke_exception.v1",
        "status": "conflict",
        "tool": tool_name,
        "error_summary": {
            "schema_version": "api_key_pipeline_sub_smoke_error.v1",
            "tool": tool_name,
            "exception_type": type(exception).__name__,
            "exception_message_returned": False,
            "url_returned": False,
            "secret_values_returned": False,
        },
        "provider_route": provider_route,
        "live_data_setup_summary": live_data_setup_summary,
        "network_call": live_data_setup_summary.get("ready_to_run_live_smoke") is True,
        "live_data_required": live_data_setup_summary.get("ready_to_run_live_smoke")
        is True,
        "mutates_local_state": False,
        "hermes_runtime_started": False,
        "telegram_send_call": False,
        "send_call": False,
        "order_submission": False,
        "secret_values_returned": False,
    }


def _api_key_pipeline_checks(
    *,
    readiness: dict[str, Any],
    live_data_smoke: dict[str, Any],
    signal_workflow_smoke: dict[str, Any],
    recording_smoke: dict[str, Any],
) -> list[dict[str, Any]]:
    live_data_gate = _optional_mapping(
        _mapping_value(_optional_mapping(readiness.get("gates")), "live_data")
    )
    provider_route = _optional_mapping(live_data_smoke.get("provider_route"))
    checks: list[dict[str, Any]] = []
    _add_smoke_check(
        checks,
        tool="get_integration_readiness",
        name="live_data_readiness_ready",
        passed=_mapping_value(live_data_gate, "ready") is True,
        expected=True,
        actual=_mapping_value(live_data_gate, "ready"),
    )
    _add_smoke_check(
        checks,
        tool="run_live_data_smoke",
        name="provider_route_status_ok",
        passed=_mapping_value(provider_route, "status") == "ready",
        expected="ready",
        actual=_mapping_value(provider_route, "status"),
    )
    _add_smoke_check(
        checks,
        tool="run_live_data_smoke",
        name="provider_route_no_network_call",
        passed=_mapping_value(provider_route, "network_call") is False,
        expected=False,
        actual=_mapping_value(provider_route, "network_call"),
    )
    _add_smoke_check(
        checks,
        tool="run_live_data_smoke",
        name="provider_route_no_secret_values",
        passed=_mapping_value(provider_route, "secret_values_returned") is False,
        expected=False,
        actual=_mapping_value(provider_route, "secret_values_returned"),
    )
    _add_smoke_check(
        checks,
        tool="run_live_data_smoke",
        name="live_data_smoke_status_ok",
        passed=live_data_smoke.get("status") == "ok",
        expected="ok",
        actual=live_data_smoke.get("status"),
    )
    _add_smoke_check(
        checks,
        tool="run_live_signal_workflow_smoke",
        name="signal_workflow_smoke_status_ok",
        passed=signal_workflow_smoke.get("status") == "ok",
        expected="ok",
        actual=signal_workflow_smoke.get("status"),
    )
    _add_smoke_check(
        checks,
        tool="run_live_recording_smoke",
        name="recording_smoke_status_ok",
        passed=recording_smoke.get("status") == "ok",
        expected="ok",
        actual=recording_smoke.get("status"),
    )
    _add_smoke_check(
        checks,
        tool="run_api_key_pipeline_smoke",
        name="no_retained_state",
        passed=all(
            smoke.get("mutates_local_state", False) is False
            for smoke in [live_data_smoke, signal_workflow_smoke, recording_smoke]
        ),
        expected=False,
        actual={
            "live_data_smoke": live_data_smoke.get("mutates_local_state", False),
            "signal_workflow_smoke": signal_workflow_smoke.get("mutates_local_state"),
            "recording_smoke": recording_smoke.get("mutates_local_state"),
        },
    )
    _add_smoke_check(
        checks,
        tool="run_api_key_pipeline_smoke",
        name="no_secret_values_returned",
        passed=all(
            smoke.get("secret_values_returned") is False
            for smoke in [live_data_smoke, signal_workflow_smoke, recording_smoke]
        ),
        expected=False,
        actual={
            "live_data_smoke": live_data_smoke.get("secret_values_returned"),
            "signal_workflow_smoke": signal_workflow_smoke.get(
                "secret_values_returned"
            ),
            "recording_smoke": recording_smoke.get("secret_values_returned"),
        },
    )
    return checks


def _api_key_pipeline_readiness_summary(
    readiness: dict[str, Any],
    live_data_setup_summary: dict[str, Any],
    *,
    next_operator_action: dict[str, Any] | None = None,
) -> dict[str, Any]:
    gates = _optional_mapping(readiness.get("gates")) or {}
    live_data_gate = _optional_mapping(gates.get("live_data")) or {}
    live_data_setup_steps = _optional_mapping(
        live_data_setup_summary.get("live_data_setup_steps")
    ) or {}
    next_operator_action = next_operator_action or _optional_mapping(
        live_data_setup_summary.get("next_operator_action")
    ) or {}
    next_provider_smoke = _optional_mapping(
        next_operator_action.get("next_provider_smoke")
    ) or {}
    next_provider_recovery_action = _optional_mapping(
        next_operator_action.get("next_provider_recovery_action")
    ) or {}
    next_provider_recovery_smoke = _optional_mapping(
        next_provider_recovery_action.get("recovery_smoke")
    ) or {}
    summary = {
        "status": readiness.get("status"),
        "live_data_status": live_data_gate.get("status"),
        "live_data_ready": live_data_gate.get("ready"),
        "live_data_missing": live_data_gate.get("missing"),
        "api_key_setup_status": live_data_setup_summary.get("status"),
        "api_key_status": live_data_setup_summary.get("api_key_status"),
        "provider_route_status": live_data_setup_summary.get(
            "provider_route_status"
        ),
        "ready_to_run_live_smoke": live_data_setup_summary.get(
            "ready_to_run_live_smoke"
        ),
        "next_setup_step": live_data_setup_steps.get("next_step"),
        "next_operator_action_name": next_operator_action.get("name"),
        "next_operator_action": next_operator_action,
        "next_actions": readiness.get("next_actions"),
        "network_call": False,
        "mutates_local_state": False,
        "secret_values_returned": False,
    }
    preferred_env_key = next_operator_action.get(
        "preferred_env_key"
    ) or next_provider_smoke.get("preferred_env_key")
    accepted_env_keys = _string_list(
        next_operator_action.get("accepted_env_keys")
        or next_provider_smoke.get("accepted_env_keys")
    )
    expected_live_contract = (
        next_operator_action.get("expected_live_contract")
        or next_provider_recovery_action.get("expected_live_contract")
        or next_provider_recovery_smoke.get("expected_live_contract")
        or next_provider_smoke.get("expected_live_contract")
    )
    expected_live_checks = _string_list(
        next_operator_action.get("expected_live_checks")
        or next_provider_recovery_action.get("expected_live_checks")
        or next_provider_recovery_smoke.get("expected_live_checks")
        or next_provider_smoke.get("expected_live_checks")
    )
    if isinstance(preferred_env_key, str):
        summary["preferred_env_key"] = preferred_env_key
    if accepted_env_keys:
        summary["accepted_env_keys"] = accepted_env_keys
    if isinstance(expected_live_contract, str):
        summary["next_operator_action_expected_live_contract"] = (
            expected_live_contract
        )
    if expected_live_checks:
        summary["next_operator_action_expected_live_checks"] = expected_live_checks
    return summary


def _api_key_pipeline_next_operator_action(
    *,
    live_data_setup_summary: dict[str, Any],
    api_key_operator_checklist: dict[str, Any],
) -> dict[str, Any]:
    next_blocking_action = _optional_mapping(
        api_key_operator_checklist.get("next_blocking_action")
    ) or {}
    if next_blocking_action.get("name") == "recover_failed_providers":
        return next_blocking_action
    return _optional_mapping(
        live_data_setup_summary.get("next_operator_action")
    ) or {}


def _api_key_pipeline_next_action_summary(
    *,
    api_key_operator_checklist: dict[str, Any],
    next_operator_action: dict[str, Any],
) -> dict[str, Any]:
    next_provider_smoke = _optional_mapping(
        next_operator_action.get("next_provider_smoke")
    ) or {}
    next_provider_recovery_action = _optional_mapping(
        next_operator_action.get("next_provider_recovery_action")
    ) or {}
    next_provider_recovery_smoke = _optional_mapping(
        next_provider_recovery_action.get("recovery_smoke")
    ) or {}
    next_action_command = (
        next_operator_action.get("recovery_smoke_command")
        or next_operator_action.get("command")
        or next_provider_smoke.get("command")
    )
    next_action_name = next_operator_action.get("name")
    summary = {
        "schema_version": "api_key_next_action_summary.v1",
        "status": api_key_operator_checklist.get("status"),
        "current_step": api_key_operator_checklist.get("current_step"),
        "ready": api_key_operator_checklist.get("ready"),
        "next_action_name": next_action_name,
        "next_action_status": next_operator_action.get("status"),
        "next_action_command": next_action_command,
        "next_action_is_recovery": next_action_name == "recover_failed_providers",
        "next_action_network_call": next_operator_action.get("network_call") is True,
        "next_action_mutates_local_state": (
            next_operator_action.get("mutates_local_state") is True
        ),
        "provider_recovery_status": api_key_operator_checklist.get(
            "provider_recovery_status"
        ),
        "provider_recovery_required": api_key_operator_checklist.get(
            "provider_recovery_required"
        )
        is True,
        "provider_recovery_item_count": api_key_operator_checklist.get(
            "provider_recovery_item_count"
        ),
        "next_blocking_step": api_key_operator_checklist.get(
            "next_blocking_step"
        ),
        "blocking_step_count": api_key_operator_checklist.get(
            "blocking_step_count"
        ),
        "ready_step_count": api_key_operator_checklist.get("ready_step_count"),
        "network_call": False,
        "mutates_local_state": False,
        "secret_values_returned": False,
    }
    next_action_provider_family = (
        next_operator_action.get("provider_family")
        or next_provider_recovery_action.get("provider_family")
        or next_provider_smoke.get("provider_family")
    )
    next_action_provider = (
        next_operator_action.get("provider")
        or next_provider_recovery_action.get("provider")
        or next_provider_smoke.get("provider")
    )
    next_action_smoke_command_name = (
        next_operator_action.get("smoke_command_name")
        or next_operator_action.get("next_provider_smoke_command_name")
        or next_operator_action.get("next_provider_recovery_smoke_command_name")
        or next_provider_recovery_action.get("smoke_command_name")
        or next_provider_smoke.get("smoke_command_name")
    )
    next_action_expected_live_contract = (
        next_operator_action.get("expected_live_contract")
        or next_provider_recovery_action.get("expected_live_contract")
        or next_provider_recovery_smoke.get("expected_live_contract")
        or next_provider_smoke.get("expected_live_contract")
    )
    next_action_expected_live_checks = _string_list(
        next_operator_action.get("expected_live_checks")
        or next_provider_recovery_action.get("expected_live_checks")
        or next_provider_recovery_smoke.get("expected_live_checks")
        or next_provider_smoke.get("expected_live_checks")
    )
    if isinstance(next_action_provider_family, str):
        summary["next_action_provider_family"] = next_action_provider_family
    if isinstance(next_action_provider, str):
        summary["next_action_provider"] = next_action_provider
    if isinstance(next_action_smoke_command_name, str):
        summary["next_action_smoke_command_name"] = next_action_smoke_command_name
    if isinstance(next_action_expected_live_contract, str):
        summary["next_action_expected_live_contract"] = (
            next_action_expected_live_contract
        )
    if next_action_expected_live_checks:
        summary["next_action_expected_live_checks"] = (
            next_action_expected_live_checks
        )
    preferred_env_key = next_operator_action.get(
        "preferred_env_key"
    ) or next_provider_smoke.get("preferred_env_key")
    accepted_env_keys = _string_list(
        next_operator_action.get("accepted_env_keys")
        or next_provider_smoke.get("accepted_env_keys")
    )
    if isinstance(preferred_env_key, str):
        summary["preferred_env_key"] = preferred_env_key
    if accepted_env_keys:
        summary["accepted_env_keys"] = accepted_env_keys
    return summary


def _api_key_operator_checklist_summary(
    api_key_operator_checklist: dict[str, Any],
) -> dict[str, Any]:
    next_blocking_action = _optional_mapping(
        api_key_operator_checklist.get("next_blocking_action")
    ) or {}
    next_provider_smoke = _optional_mapping(
        next_blocking_action.get("next_provider_smoke")
    ) or {}
    next_provider_recovery_action = _optional_mapping(
        api_key_operator_checklist.get("next_provider_recovery_action")
    ) or {}
    next_blocking_command = (
        next_blocking_action.get("recovery_smoke_command")
        or next_blocking_action.get("command")
        or next_provider_smoke.get("command")
    )
    raw_steps = api_key_operator_checklist.get("steps")
    steps = (
        [
            _api_key_operator_checklist_step_summary(step)
            for step in raw_steps
            if isinstance(step, dict)
        ]
        if isinstance(raw_steps, list)
        else []
    )
    summary = {
        "schema_version": "api_key_operator_checklist_summary.v1",
        "status": api_key_operator_checklist.get("status"),
        "current_step": api_key_operator_checklist.get("current_step"),
        "ready": api_key_operator_checklist.get("ready") is True,
        "ready_step_names": _string_list(
            api_key_operator_checklist.get("ready_step_names")
        ),
        "ready_step_count": api_key_operator_checklist.get("ready_step_count"),
        "blocking_step_names": _string_list(
            api_key_operator_checklist.get("blocking_step_names")
        ),
        "blocking_step_count": api_key_operator_checklist.get(
            "blocking_step_count"
        ),
        "next_blocking_step": api_key_operator_checklist.get(
            "next_blocking_step"
        ),
        "next_blocking_action_name": next_blocking_action.get("name"),
        "next_blocking_action_status": next_blocking_action.get("status"),
        "next_blocking_action_command": next_blocking_command,
        "next_blocking_action_network_call": (
            next_blocking_action.get("network_call") is True
        ),
        "next_blocking_action_mutates_local_state": (
            next_blocking_action.get("mutates_local_state") is True
        ),
        "provider_recovery_status": api_key_operator_checklist.get(
            "provider_recovery_status"
        ),
        "provider_recovery_required": api_key_operator_checklist.get(
            "provider_recovery_required"
        )
        is True,
        "provider_recovery_item_count": api_key_operator_checklist.get(
            "provider_recovery_item_count"
        ),
        "next_provider_recovery_smoke_command_name": (
            next_provider_recovery_action.get("smoke_command_name")
        ),
        "step_count": api_key_operator_checklist.get("step_count"),
        "steps": steps,
        "network_call": False,
        "mutates_local_state": False,
        "secret_values_returned": False,
    }
    preferred_env_key = next_blocking_action.get("preferred_env_key")
    accepted_env_keys = _string_list(next_blocking_action.get("accepted_env_keys"))
    next_blocking_provider_family = (
        next_blocking_action.get("provider_family")
        or next_provider_recovery_action.get("provider_family")
        or next_provider_smoke.get("provider_family")
    )
    next_blocking_provider = (
        next_blocking_action.get("provider")
        or next_provider_recovery_action.get("provider")
        or next_provider_smoke.get("provider")
    )
    next_blocking_smoke_command_name = (
        next_blocking_action.get("smoke_command_name")
        or next_blocking_action.get("next_provider_smoke_command_name")
        or next_blocking_action.get("next_provider_recovery_smoke_command_name")
        or next_provider_recovery_action.get("smoke_command_name")
        or next_provider_smoke.get("smoke_command_name")
    )
    if isinstance(next_blocking_provider_family, str):
        summary["next_blocking_action_provider_family"] = (
            next_blocking_provider_family
        )
    if isinstance(next_blocking_provider, str):
        summary["next_blocking_action_provider"] = next_blocking_provider
    if isinstance(next_blocking_smoke_command_name, str):
        summary["next_blocking_action_smoke_command_name"] = (
            next_blocking_smoke_command_name
        )
    if isinstance(preferred_env_key, str):
        summary["next_blocking_action_preferred_env_key"] = preferred_env_key
    if accepted_env_keys:
        summary["next_blocking_action_accepted_env_keys"] = accepted_env_keys
    return summary


def _api_key_operator_checklist_step_summary(
    step: dict[str, Any],
) -> dict[str, Any]:
    next_provider_smoke = _optional_mapping(step.get("next_provider_smoke")) or {}
    next_provider_recovery_action = _optional_mapping(
        step.get("next_provider_recovery_action")
    ) or {}
    summary = {
        "name": step.get("name"),
        "status": step.get("status"),
        "command": step.get("command") or step.get("recovery_smoke_command"),
        "required_env_keys": _string_list(step.get("required_env_keys")),
        "configured_env_keys": _string_list(step.get("configured_env_keys")),
        "missing_provider_families": _string_list(
            step.get("missing_provider_families")
        ),
        "provider_smoke_command_count": step.get("provider_smoke_command_count"),
        "next_provider_smoke_command_name": step.get(
            "next_provider_smoke_command_name"
        )
        or next_provider_smoke.get("smoke_command_name"),
        "provider_recovery_item_count": step.get("provider_recovery_item_count"),
        "next_provider_recovery_smoke_command_name": (
            next_provider_recovery_action.get("smoke_command_name")
        ),
        "recovery_smoke_available": step.get("recovery_smoke_available"),
        "network_call": step.get("network_call") is True,
        "network_call_policy": step.get("network_call_policy"),
        "mutates_local_state": step.get("mutates_local_state") is True,
        "secret_values_returned": False,
    }
    preferred_env_key = step.get("preferred_env_key") or (
        next_provider_recovery_action.get("preferred_env_key")
    )
    accepted_env_keys = _string_list(
        step.get("accepted_env_keys")
        or next_provider_recovery_action.get("accepted_env_keys")
    )
    provider_family = (
        step.get("provider_family")
        or next_provider_recovery_action.get("provider_family")
        or next_provider_smoke.get("provider_family")
    )
    provider = (
        step.get("provider")
        or next_provider_recovery_action.get("provider")
        or next_provider_smoke.get("provider")
    )
    smoke_command_name = (
        step.get("smoke_command_name")
        or step.get("next_provider_smoke_command_name")
        or step.get("next_provider_recovery_smoke_command_name")
        or next_provider_recovery_action.get("smoke_command_name")
        or next_provider_smoke.get("smoke_command_name")
    )
    if isinstance(provider_family, str):
        summary["provider_family"] = provider_family
    if isinstance(provider, str):
        summary["provider"] = provider
    if isinstance(smoke_command_name, str):
        summary["smoke_command_name"] = smoke_command_name
    if isinstance(preferred_env_key, str):
        summary["preferred_env_key"] = preferred_env_key
    if accepted_env_keys:
        summary["accepted_env_keys"] = accepted_env_keys
    return summary


def _api_key_pipeline_stage_summary(
    *,
    live_data_smoke_summary: dict[str, Any],
    signal_workflow_smoke_summary: dict[str, Any],
    recording_smoke_summary: dict[str, Any],
) -> dict[str, Any]:
    stages = [
        _api_key_pipeline_stage_row(
            "run_live_data_smoke",
            live_data_smoke_summary,
        ),
        _api_key_pipeline_stage_row(
            "run_live_signal_workflow_smoke",
            signal_workflow_smoke_summary,
        ),
        _api_key_pipeline_stage_row(
            "run_live_recording_smoke",
            recording_smoke_summary,
        ),
    ]
    failed_stages = [stage for stage in stages if stage["failed"]]
    return {
        "schema_version": "api_key_pipeline_stage_summary.v1",
        "status": "conflict" if failed_stages else "ok",
        "stage_count": len(stages),
        "failed_stage_count": len(failed_stages),
        "failed_stage_names": [
            stage["stage_name"] for stage in failed_stages
        ],
        "first_failed_stage": failed_stages[0] if failed_stages else None,
        "stages": stages,
        "network_call": False,
        "mutates_local_state": False,
        "secret_values_returned": False,
    }


def _api_key_pipeline_stage_row(
    stage_name: str,
    stage_summary: dict[str, Any],
) -> dict[str, Any]:
    status = stage_summary.get("status")
    row = {
        "stage_name": stage_name,
        "status": status,
        "failed": status != "ok",
        "error_summary": stage_summary.get("error_summary"),
        "provider_error_summary_count": stage_summary.get(
            "provider_error_summary_count"
        ),
        "provider_recovery_smoke_count": stage_summary.get(
            "provider_recovery_smoke_count"
        ),
        "next_provider_recovery_smoke_command_name": stage_summary.get(
            "next_provider_recovery_smoke_command_name"
        ),
        "ready_to_run_live_smoke": stage_summary.get(
            "ready_to_run_live_smoke"
        ),
        "provider_route_status": stage_summary.get("provider_route_status"),
        "network_call": stage_summary.get("network_call") is True,
        "live_data_required": stage_summary.get("live_data_required") is True,
        "mutates_local_state": stage_summary.get("mutates_local_state") is True,
        "secret_values_returned": stage_summary.get("secret_values_returned"),
    }
    next_provider_recovery_smoke = _optional_mapping(
        stage_summary.get("next_provider_recovery_smoke")
    ) or {}
    provider_family = next_provider_recovery_smoke.get("provider_family")
    live_data_setup_summary = _optional_mapping(
        stage_summary.get("live_data_setup_summary")
    ) or {}
    provider_setup_actions = _optional_mapping(
        live_data_setup_summary.get("provider_setup_actions")
    ) or _optional_mapping(stage_summary.get("provider_setup_actions")) or {}
    provider_setup_action = (
        _optional_mapping(provider_setup_actions.get(provider_family))
        if isinstance(provider_family, str)
        else None
    ) or {}
    preferred_env_key = next_provider_recovery_smoke.get(
        "preferred_env_key"
    ) or provider_setup_action.get("preferred_env_key")
    accepted_env_keys = _string_list(
        next_provider_recovery_smoke.get("accepted_env_keys")
        or provider_setup_action.get("accepted_env_keys")
    )
    provider = next_provider_recovery_smoke.get("provider") or (
        provider_setup_action.get("provider")
    )
    smoke_command_name = next_provider_recovery_smoke.get(
        "smoke_command_name"
    ) or stage_summary.get("next_provider_recovery_smoke_command_name")
    if isinstance(provider_family, str):
        row["provider_family"] = provider_family
    if isinstance(provider, str):
        row["provider"] = provider
    if isinstance(smoke_command_name, str):
        row["smoke_command_name"] = smoke_command_name
    if isinstance(preferred_env_key, str):
        row["preferred_env_key"] = preferred_env_key
    if accepted_env_keys:
        row["accepted_env_keys"] = accepted_env_keys
    return row


def _api_key_pipeline_check_summary(
    checks: list[dict[str, Any]],
    *,
    api_key_pipeline_stage_summary: dict[str, Any] | None = None,
) -> dict[str, Any]:
    stage_recovery_hints_by_tool = _api_key_pipeline_stage_recovery_hints_by_tool(
        api_key_pipeline_stage_summary
    )
    failed_checks = [
        _api_key_pipeline_check_row(
            check,
            recovery_hint=stage_recovery_hints_by_tool.get(check.get("tool")),
        )
        for check in checks
        if check.get("passed") is not True
    ]
    tool_failure_counts: dict[str, int] = {}
    for check in failed_checks:
        tool = check["tool"]
        tool_failure_counts[tool] = tool_failure_counts.get(tool, 0) + 1
    return {
        "schema_version": "api_key_pipeline_check_summary.v1",
        "status": "conflict" if failed_checks else "ok",
        "check_count": len(checks),
        "passed_check_count": len(checks) - len(failed_checks),
        "failed_check_count": len(failed_checks),
        "failed_check_keys": [check["key"] for check in failed_checks],
        "tools_with_failures": list(tool_failure_counts),
        "tool_failure_counts": tool_failure_counts,
        "first_failed_check": failed_checks[0] if failed_checks else None,
        "failed_checks": failed_checks,
        "network_call": False,
        "mutates_local_state": False,
        "secret_values_returned": False,
    }


def _api_key_pipeline_stage_recovery_hints_by_tool(
    api_key_pipeline_stage_summary: dict[str, Any] | None,
) -> dict[str, dict[str, Any]]:
    if api_key_pipeline_stage_summary is None:
        return {}
    stages = api_key_pipeline_stage_summary.get("stages")
    if not isinstance(stages, list):
        return {}
    hints_by_tool: dict[str, dict[str, Any]] = {}
    for stage in stages:
        stage_row = _optional_mapping(stage)
        if stage_row is None:
            continue
        stage_name = stage_row.get("stage_name")
        preferred_env_key = stage_row.get("preferred_env_key")
        accepted_env_keys = _string_list(stage_row.get("accepted_env_keys"))
        provider_family = stage_row.get("provider_family")
        provider = stage_row.get("provider")
        smoke_command_name = stage_row.get("smoke_command_name")
        if (
            isinstance(stage_name, str)
            and isinstance(preferred_env_key, str)
            and accepted_env_keys
        ):
            hint = {
                "preferred_env_key": preferred_env_key,
                "accepted_env_keys": accepted_env_keys,
            }
            if isinstance(provider_family, str):
                hint["provider_family"] = provider_family
            if isinstance(provider, str):
                hint["provider"] = provider
            if isinstance(smoke_command_name, str):
                hint["smoke_command_name"] = smoke_command_name
            hints_by_tool[stage_name] = hint
    return hints_by_tool


def _api_key_pipeline_check_row(
    check: dict[str, Any],
    *,
    recovery_hint: dict[str, Any] | None = None,
) -> dict[str, Any]:
    tool = str(check.get("tool"))
    name = str(check.get("name"))
    row = {
        "tool": tool,
        "name": name,
        "key": f"{tool}.{name}",
        "passed": False,
        "expected": check.get("expected"),
        "actual": check.get("actual"),
        "secret_values_returned": False,
    }
    if recovery_hint is not None:
        preferred_env_key = recovery_hint.get("preferred_env_key")
        accepted_env_keys = _string_list(recovery_hint.get("accepted_env_keys"))
        provider_family = recovery_hint.get("provider_family")
        provider = recovery_hint.get("provider")
        smoke_command_name = recovery_hint.get("smoke_command_name")
        if isinstance(provider_family, str):
            row["provider_family"] = provider_family
        if isinstance(provider, str):
            row["provider"] = provider
        if isinstance(smoke_command_name, str):
            row["smoke_command_name"] = smoke_command_name
        if isinstance(preferred_env_key, str):
            row["preferred_env_key"] = preferred_env_key
        if accepted_env_keys:
            row["accepted_env_keys"] = accepted_env_keys
    return row


def _api_key_pipeline_failure_summary(
    *,
    api_key_next_action_summary: dict[str, Any],
    api_key_pipeline_stage_summary: dict[str, Any],
    api_key_pipeline_check_summary: dict[str, Any],
) -> dict[str, Any]:
    failed_stage_names = _string_list(
        api_key_pipeline_stage_summary.get("failed_stage_names")
    )
    failed_check_keys = _string_list(
        api_key_pipeline_check_summary.get("failed_check_keys")
    )
    tools_with_failures = _string_list(
        api_key_pipeline_check_summary.get("tools_with_failures")
    )
    has_failures = bool(failed_stage_names or failed_check_keys)
    first_failed_stage = _optional_mapping(
        api_key_pipeline_stage_summary.get("first_failed_stage")
    ) or {}
    first_failed_check = _optional_mapping(
        api_key_pipeline_check_summary.get("first_failed_check")
    ) or {}
    provider_recovery_required = (
        api_key_next_action_summary.get("provider_recovery_required") is True
    )
    next_action_name = api_key_next_action_summary.get("next_action_name")
    summary = {
        "schema_version": "api_key_pipeline_failure_summary.v1",
        "status": "conflict" if has_failures else "ok",
        "has_failures": has_failures,
        "failure_category": _api_key_pipeline_failure_category(
            has_failures=has_failures,
            provider_recovery_required=provider_recovery_required,
            next_action_name=next_action_name,
        ),
        "failed_stage_names": failed_stage_names,
        "failed_check_keys": failed_check_keys,
        "tools_with_failures": tools_with_failures,
        "first_failed_stage_name": first_failed_stage.get("stage_name"),
        "first_failed_check_key": first_failed_check.get("key"),
        "next_action_name": next_action_name,
        "next_action_command": api_key_next_action_summary.get(
            "next_action_command"
        ),
        "next_action_is_recovery": api_key_next_action_summary.get(
            "next_action_is_recovery"
        )
        is True,
        "provider_recovery_required": provider_recovery_required,
        "provider_recovery_item_count": api_key_next_action_summary.get(
            "provider_recovery_item_count"
        ),
        "network_call": False,
        "mutates_local_state": False,
        "secret_values_returned": False,
    }
    preferred_env_key = api_key_next_action_summary.get("preferred_env_key")
    accepted_env_keys = _string_list(
        api_key_next_action_summary.get("accepted_env_keys")
    )
    next_action_provider_family = api_key_next_action_summary.get(
        "next_action_provider_family"
    )
    next_action_provider = api_key_next_action_summary.get("next_action_provider")
    next_action_smoke_command_name = api_key_next_action_summary.get(
        "next_action_smoke_command_name"
    )
    next_action_expected_live_contract = api_key_next_action_summary.get(
        "next_action_expected_live_contract"
    )
    next_action_expected_live_checks = _string_list(
        api_key_next_action_summary.get("next_action_expected_live_checks")
    )
    if isinstance(next_action_provider_family, str):
        summary["next_action_provider_family"] = next_action_provider_family
    if isinstance(next_action_provider, str):
        summary["next_action_provider"] = next_action_provider
    if isinstance(next_action_smoke_command_name, str):
        summary["next_action_smoke_command_name"] = next_action_smoke_command_name
    if isinstance(next_action_expected_live_contract, str):
        summary["next_action_expected_live_contract"] = (
            next_action_expected_live_contract
        )
    if next_action_expected_live_checks:
        summary["next_action_expected_live_checks"] = (
            next_action_expected_live_checks
        )
    if provider_recovery_required and isinstance(preferred_env_key, str):
        summary["preferred_env_key"] = preferred_env_key
    if provider_recovery_required and accepted_env_keys:
        summary["accepted_env_keys"] = accepted_env_keys
    return summary


def _api_key_pipeline_failure_category(
    *,
    has_failures: bool,
    provider_recovery_required: bool,
    next_action_name: Any,
) -> str:
    if not has_failures:
        return "none"
    if provider_recovery_required:
        return "provider_recovery"
    if next_action_name in {
        "restore_env_example",
        "prepare_dotenv",
        "fill_live_data_api_keys",
    }:
        return "setup"
    return "smoke_failure"


def _api_key_live_http_timeout_summary() -> dict[str, Any]:
    return {
        "schema_version": "api_key_live_http_timeout_summary.v1",
        "timeout_seconds": get_settings().live_http_timeout_seconds,
        "env_key": LIVE_HTTP_TIMEOUT_SECONDS_ENV_NAME,
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


def _api_key_pipeline_summary_only_payload(
    payload: dict[str, Any],
) -> dict[str, Any]:
    input_payload = _optional_mapping(payload.get("input")) or {}
    next_operator_action = _optional_mapping(payload.get("next_operator_action")) or {}
    next_provider_smoke = _optional_mapping(
        next_operator_action.get("next_provider_smoke")
    ) or {}
    next_provider_recovery_action = _optional_mapping(
        next_operator_action.get("next_provider_recovery_action")
    ) or {}
    api_key_next_action_summary = _optional_mapping(
        payload.get("api_key_next_action_summary")
    ) or {}
    live_data_smoke_summary = _optional_mapping(
        payload.get("live_data_smoke_summary")
    ) or {}
    provider_smoke_summaries = live_data_smoke_summary.get(
        "provider_smoke_summaries"
    )
    provider_smoke_rows = (
        [
            row
            for row in provider_smoke_summaries
            if isinstance(row, dict)
        ]
        if isinstance(provider_smoke_summaries, list)
        else []
    )
    raw_provider_smoke_summary_count = live_data_smoke_summary.get(
        "provider_smoke_summary_count"
    )
    provider_smoke_summary_count = (
        raw_provider_smoke_summary_count
        if isinstance(raw_provider_smoke_summary_count, int)
        else len(provider_smoke_rows)
    )
    provider_smoke_success_rows = [
        row
        for row in provider_smoke_rows
        if row.get("passed") is True or row.get("status") == "ok"
    ]
    provider_smoke_success_count = len(provider_smoke_success_rows)
    provider_smoke_success_expected_live_checks = _ordered_unique_strings(
        [
            check
            for row in provider_smoke_success_rows
            for check in _string_list(row.get("expected_live_checks"))
        ]
    )
    provider_smoke_success_network_call_count = sum(
        1 for row in provider_smoke_success_rows if row.get("network_call") is True
    )
    provider_smoke_success_mutates_local_state_count = sum(
        1
        for row in provider_smoke_success_rows
        if row.get("mutates_local_state") is True
    )
    provider_smoke_success_secret_values_returned_count = sum(
        1
        for row in provider_smoke_success_rows
        if row.get("secret_values_returned") is True
    )
    provider_smoke_success_accepted_env_key_groups = [
        _string_list(row.get("accepted_env_keys"))
        for row in provider_smoke_success_rows
        if _string_list(row.get("accepted_env_keys"))
    ]
    return {
        "schema_version": "api_key_pipeline_smoke_summary_only.v1",
        "status": payload.get("status"),
        "summary_only": True,
        "input": {
            "asset": input_payload.get("asset"),
            "timeframe": input_payload.get("timeframe"),
            "symbols": input_payload.get("symbols"),
            "topic": input_payload.get("topic"),
            "summary_only": True,
        },
        "executed_tools": _string_list(payload.get("executed_tools")),
        "next_operator_action_name": (
            next_operator_action.get("name")
            or api_key_next_action_summary.get("next_action_name")
        ),
        "next_operator_action_status": (
            next_operator_action.get("status")
            or api_key_next_action_summary.get("next_action_status")
        ),
        "next_operator_action_command": api_key_next_action_summary.get(
            "next_action_command"
        ),
        "next_operator_action_provider_family": (
            next_operator_action.get("provider_family")
            or next_provider_recovery_action.get("provider_family")
            or next_provider_smoke.get("provider_family")
        ),
        "next_operator_action_provider": (
            next_operator_action.get("provider")
            or next_provider_recovery_action.get("provider")
            or next_provider_smoke.get("provider")
        ),
        "next_operator_action_smoke_command_name": (
            next_operator_action.get("smoke_command_name")
            or next_operator_action.get("next_provider_smoke_command_name")
            or next_operator_action.get("next_provider_recovery_smoke_command_name")
            or next_provider_recovery_action.get("smoke_command_name")
            or next_provider_smoke.get("smoke_command_name")
        ),
        "next_operator_action_expected_live_contract": (
            api_key_next_action_summary.get("next_action_expected_live_contract")
        ),
        "next_operator_action_expected_live_checks": _string_list(
            api_key_next_action_summary.get("next_action_expected_live_checks")
        ),
        "next_operator_action_network_call": (
            api_key_next_action_summary.get("next_action_network_call") is True
        ),
        "next_operator_action_network_call_policy": next_operator_action.get(
            "network_call_policy"
        ),
        "next_operator_action_mutates_local_state": (
            api_key_next_action_summary.get("next_action_mutates_local_state")
            is True
        ),
        "next_operator_action_preferred_env_key": api_key_next_action_summary.get(
            "preferred_env_key"
        ),
        "next_operator_action_accepted_env_keys": _string_list(
            api_key_next_action_summary.get("accepted_env_keys")
        ),
        "next_operator_action_secret_values_returned": (
            next_operator_action.get("secret_values_returned") is True
            or api_key_next_action_summary.get("secret_values_returned") is True
        ),
        "next_operator_action": next_operator_action,
        "readiness_summary": _optional_mapping(payload.get("readiness_summary"))
        or {},
        "api_key_integration_status_summary": _optional_mapping(
            payload.get("api_key_integration_status_summary")
        )
        or {},
        "api_key_next_action_summary": api_key_next_action_summary,
        "api_key_operator_checklist_summary": (
            _api_key_operator_checklist_summary(
                _optional_mapping(payload.get("api_key_operator_checklist")) or {}
            )
        ),
        "setup_status_summary": _optional_mapping(
            payload.get("setup_status_summary")
        )
        or {},
        "live_data_setup_summary": _optional_mapping(
            payload.get("live_data_setup_summary")
        )
        or {},
        "api_key_requirements_summary": _optional_mapping(
            payload.get("api_key_requirements_summary")
        )
        or {},
        "api_key_command_summary": _optional_mapping(
            payload.get("api_key_command_summary")
        )
        or {},
        "api_key_setup_file_summary": _optional_mapping(
            payload.get("api_key_setup_file_summary")
        )
        or {},
        "api_key_dotenv_loading_summary": _optional_mapping(
            payload.get("api_key_dotenv_loading_summary")
        )
        or {},
        "api_key_pipeline_failure_summary": _optional_mapping(
            payload.get("api_key_pipeline_failure_summary")
        )
        or {},
        "api_key_pipeline_stage_summary": _optional_mapping(
            payload.get("api_key_pipeline_stage_summary")
        )
        or {},
        "api_key_pipeline_check_summary": _optional_mapping(
            payload.get("api_key_pipeline_check_summary")
        )
        or {},
        "api_key_provider_selection_summary": _optional_mapping(
            payload.get("api_key_provider_selection_summary")
        )
        or {},
        "api_key_live_http_timeout_summary": _optional_mapping(
            payload.get("api_key_live_http_timeout_summary")
        )
        or {},
        "api_key_provider_recovery_summary": (
            _api_key_provider_recovery_summary(
                _optional_mapping(
                    payload.get("api_key_provider_recovery_checklist")
                )
                or {}
            )
        ),
        "provider_smoke_summaries": provider_smoke_rows,
        "provider_smoke_summary_count": provider_smoke_summary_count,
        "provider_smoke_success_count": provider_smoke_success_count,
        "provider_smoke_all_successful": (
            provider_smoke_summary_count > 0
            and provider_smoke_success_count == provider_smoke_summary_count
        ),
        "provider_smoke_success_provider_families": _ordered_unique_strings(
            [row.get("provider_family") for row in provider_smoke_success_rows]
        ),
        "provider_smoke_success_providers": _ordered_unique_strings(
            [row.get("provider") for row in provider_smoke_success_rows]
        ),
        "provider_smoke_success_smoke_command_names": _ordered_unique_strings(
            [row.get("smoke_command_name") for row in provider_smoke_success_rows]
        ),
        "provider_smoke_success_expected_live_contracts": _ordered_unique_strings(
            [
                row.get("expected_live_contract")
                for row in provider_smoke_success_rows
            ]
        ),
        "provider_smoke_success_expected_live_checks": (
            provider_smoke_success_expected_live_checks
        ),
        "provider_smoke_success_check_count": len(
            provider_smoke_success_expected_live_checks
        ),
        "provider_smoke_success_network_call_count": (
            provider_smoke_success_network_call_count
        ),
        "provider_smoke_success_all_network_calls": (
            provider_smoke_success_count > 0
            and provider_smoke_success_network_call_count
            == provider_smoke_success_count
        ),
        "provider_smoke_success_network_call_policies": _ordered_unique_strings(
            [
                row.get("network_call_policy")
                for row in provider_smoke_success_rows
            ]
        ),
        "provider_smoke_success_mutates_local_state_count": (
            provider_smoke_success_mutates_local_state_count
        ),
        "provider_smoke_success_any_mutates_local_state": (
            provider_smoke_success_mutates_local_state_count > 0
        ),
        "provider_smoke_success_secret_values_returned_count": (
            provider_smoke_success_secret_values_returned_count
        ),
        "provider_smoke_success_any_secret_values_returned": (
            provider_smoke_success_secret_values_returned_count > 0
        ),
        "provider_smoke_success_preferred_env_keys": _ordered_unique_strings(
            [row.get("preferred_env_key") for row in provider_smoke_success_rows]
        ),
        "provider_smoke_success_accepted_env_keys": _ordered_unique_strings(
            [
                env_key
                for group in provider_smoke_success_accepted_env_key_groups
                for env_key in group
            ]
        ),
        "provider_smoke_success_accepted_env_key_groups": (
            provider_smoke_success_accepted_env_key_groups
        ),
        "api_key_failure_category": payload.get("api_key_failure_category"),
        "api_key_has_failures": payload.get("api_key_has_failures") is True,
        "api_key_failed_stage_names": _string_list(
            payload.get("api_key_failed_stage_names")
        ),
        "api_key_failed_check_keys": _string_list(
            payload.get("api_key_failed_check_keys")
        ),
        "api_key_tools_with_failures": _string_list(
            payload.get("api_key_tools_with_failures")
        ),
        "api_key_first_failed_stage_name": payload.get(
            "api_key_first_failed_stage_name"
        ),
        "api_key_first_failed_check_key": payload.get(
            "api_key_first_failed_check_key"
        ),
        "provider_route_summary": _optional_mapping(
            payload.get("provider_route_summary")
        )
        or {},
        "checks": _api_key_pipeline_summary_only_checks(payload.get("checks")),
        "failed_provider_families": _string_list(
            payload.get("failed_provider_families")
        ),
        "failed_provider_count": payload.get("failed_provider_count"),
        "next_provider_recovery_action": payload.get(
            "next_provider_recovery_action"
        ),
        "next_provider_recovery_smoke_command_name": payload.get(
            "next_provider_recovery_smoke_command_name"
        ),
        "provider_recovery_smoke_count": payload.get(
            "provider_recovery_smoke_count"
        ),
        "provider_recovery_required": (
            payload.get("provider_recovery_required") is True
        ),
        "provider_recovery_summary_status": payload.get(
            "provider_recovery_summary_status"
        ),
        "provider_recovery_action_status": payload.get(
            "provider_recovery_action_status"
        ),
        "provider_recovery_item_count": payload.get(
            "provider_recovery_item_count"
        ),
        "provider_recovery_pending_count": payload.get(
            "provider_recovery_pending_count"
        ),
        "provider_recovery_blocked_count": payload.get(
            "provider_recovery_blocked_count"
        ),
        "provider_error_count": payload.get("provider_error_count"),
        "provider_recovery_smoke_available_count": payload.get(
            "provider_recovery_smoke_available_count"
        ),
        "provider_recovery_smoke_unavailable_count": payload.get(
            "provider_recovery_smoke_unavailable_count"
        ),
        "provider_recovery_all_smokes_available": (
            payload.get("provider_recovery_all_smokes_available") is True
        ),
        "provider_recovery_network_call_count": payload.get(
            "provider_recovery_network_call_count"
        ),
        "provider_recovery_all_network_calls": (
            payload.get("provider_recovery_all_network_calls") is True
        ),
        "provider_recovery_mutates_local_state_count": payload.get(
            "provider_recovery_mutates_local_state_count"
        ),
        "provider_recovery_any_mutates_local_state": (
            payload.get("provider_recovery_any_mutates_local_state") is True
        ),
        "provider_recovery_secret_values_returned_count": payload.get(
            "provider_recovery_secret_values_returned_count"
        ),
        "provider_recovery_any_secret_values_returned": (
            payload.get("provider_recovery_any_secret_values_returned") is True
        ),
        "provider_recovery_next_setup_actions": _string_list(
            payload.get("provider_recovery_next_setup_actions")
        ),
        "provider_recovery_exception_types": _string_list(
            payload.get("provider_recovery_exception_types")
        ),
        "provider_recovery_exception_message_returned_count": payload.get(
            "provider_recovery_exception_message_returned_count"
        ),
        "provider_recovery_any_exception_messages_returned": (
            payload.get("provider_recovery_any_exception_messages_returned") is True
        ),
        "provider_recovery_url_returned_count": payload.get(
            "provider_recovery_url_returned_count"
        ),
        "provider_recovery_any_urls_returned": (
            payload.get("provider_recovery_any_urls_returned") is True
        ),
        "provider_recovery_statuses": _string_list(
            payload.get("provider_recovery_statuses")
        ),
        "provider_recovery_all_pending": (
            payload.get("provider_recovery_all_pending") is True
        ),
        "provider_recovery_retry_ready": (
            payload.get("provider_recovery_retry_ready") is True
        ),
        "provider_recovery_all_retryable": (
            payload.get("provider_recovery_all_retryable") is True
        ),
        "provider_recovery_has_pending": (
            payload.get("provider_recovery_has_pending") is True
        ),
        "provider_recovery_has_blocked": (
            payload.get("provider_recovery_has_blocked") is True
        ),
        "provider_recovery_provider_families": _string_list(
            payload.get("provider_recovery_provider_families")
        ),
        "provider_recovery_providers": _string_list(
            payload.get("provider_recovery_providers")
        ),
        "provider_recovery_pending_provider_families": _string_list(
            payload.get("provider_recovery_pending_provider_families")
        ),
        "provider_recovery_pending_providers": _string_list(
            payload.get("provider_recovery_pending_providers")
        ),
        "provider_recovery_blocked_provider_families": _string_list(
            payload.get("provider_recovery_blocked_provider_families")
        ),
        "provider_recovery_blocked_providers": _string_list(
            payload.get("provider_recovery_blocked_providers")
        ),
        "provider_recovery_smoke_command_names": _string_list(
            payload.get("provider_recovery_smoke_command_names")
        ),
        "provider_recovery_smoke_commands": _string_list(
            payload.get("provider_recovery_smoke_commands")
        ),
        "provider_recovery_pending_smoke_command_names": _string_list(
            payload.get("provider_recovery_pending_smoke_command_names")
        ),
        "provider_recovery_pending_smoke_commands": _string_list(
            payload.get("provider_recovery_pending_smoke_commands")
        ),
        "provider_recovery_blocked_smoke_command_names": _string_list(
            payload.get("provider_recovery_blocked_smoke_command_names")
        ),
        "provider_recovery_blocked_smoke_commands": _string_list(
            payload.get("provider_recovery_blocked_smoke_commands")
        ),
        "provider_recovery_network_call_policies": _string_list(
            payload.get("provider_recovery_network_call_policies")
        ),
        "provider_recovery_preferred_env_keys": _string_list(
            payload.get("provider_recovery_preferred_env_keys")
        ),
        "provider_recovery_accepted_env_keys": _string_list(
            payload.get("provider_recovery_accepted_env_keys")
        ),
        "provider_recovery_accepted_env_key_groups": [
            _string_list(group)
            for group in payload.get("provider_recovery_accepted_env_key_groups", [])
            if isinstance(group, list)
        ],
        "next_pending_recovery_smoke_command_name": payload.get(
            "next_pending_recovery_smoke_command_name"
        ),
        "next_pending_recovery_smoke_command": payload.get(
            "next_pending_recovery_smoke_command"
        ),
        "next_pending_recovery_provider_family": payload.get(
            "next_pending_recovery_provider_family"
        ),
        "next_pending_recovery_provider": payload.get(
            "next_pending_recovery_provider"
        ),
        "next_pending_recovery_next_setup_action": payload.get(
            "next_pending_recovery_next_setup_action"
        ),
        "next_pending_recovery_preferred_env_key": payload.get(
            "next_pending_recovery_preferred_env_key"
        ),
        "next_pending_recovery_accepted_env_keys": _string_list(
            payload.get("next_pending_recovery_accepted_env_keys")
        ),
        "next_pending_recovery_network_call_policy": payload.get(
            "next_pending_recovery_network_call_policy"
        ),
        "next_pending_recovery_smoke_available": (
            payload.get("next_pending_recovery_smoke_available") is True
        ),
        "next_pending_recovery_network_call": (
            payload.get("next_pending_recovery_network_call") is True
        ),
        "next_pending_recovery_mutates_local_state": (
            payload.get("next_pending_recovery_mutates_local_state") is True
        ),
        "next_pending_recovery_secret_values_returned": False,
        "next_blocked_recovery_smoke_command_name": payload.get(
            "next_blocked_recovery_smoke_command_name"
        ),
        "next_blocked_recovery_smoke_command": payload.get(
            "next_blocked_recovery_smoke_command"
        ),
        "next_blocked_recovery_provider_family": payload.get(
            "next_blocked_recovery_provider_family"
        ),
        "next_blocked_recovery_provider": payload.get(
            "next_blocked_recovery_provider"
        ),
        "next_blocked_recovery_next_setup_action": payload.get(
            "next_blocked_recovery_next_setup_action"
        ),
        "next_blocked_recovery_preferred_env_key": payload.get(
            "next_blocked_recovery_preferred_env_key"
        ),
        "next_blocked_recovery_accepted_env_keys": _string_list(
            payload.get("next_blocked_recovery_accepted_env_keys")
        ),
        "next_blocked_recovery_network_call_policy": payload.get(
            "next_blocked_recovery_network_call_policy"
        ),
        "next_blocked_recovery_smoke_available": (
            payload.get("next_blocked_recovery_smoke_available") is True
        ),
        "next_blocked_recovery_network_call": (
            payload.get("next_blocked_recovery_network_call") is True
        ),
        "next_blocked_recovery_mutates_local_state": (
            payload.get("next_blocked_recovery_mutates_local_state") is True
        ),
        "next_blocked_recovery_secret_values_returned": False,
        "next_recovery_smoke_command_name": payload.get(
            "next_recovery_smoke_command_name"
        ),
        "next_recovery_smoke_command": payload.get("next_recovery_smoke_command"),
        "next_recovery_provider_family": payload.get(
            "next_recovery_provider_family"
        ),
        "next_recovery_provider": payload.get("next_recovery_provider"),
        "next_recovery_next_setup_action": payload.get(
            "next_recovery_next_setup_action"
        ),
        "next_recovery_preferred_env_key": payload.get(
            "next_recovery_preferred_env_key"
        ),
        "next_recovery_accepted_env_keys": _string_list(
            payload.get("next_recovery_accepted_env_keys")
        ),
        "next_recovery_network_call_policy": payload.get(
            "next_recovery_network_call_policy"
        ),
        "next_recovery_smoke_available": (
            payload.get("next_recovery_smoke_available") is True
        ),
        "next_recovery_network_call": (
            payload.get("next_recovery_network_call") is True
        ),
        "next_recovery_mutates_local_state": (
            payload.get("next_recovery_mutates_local_state") is True
        ),
        "next_recovery_exception_type": payload.get("next_recovery_exception_type"),
        "next_recovery_exception_message_returned": (
            payload.get("next_recovery_exception_message_returned") is True
        ),
        "next_recovery_url_returned": (
            payload.get("next_recovery_url_returned") is True
        ),
        "next_recovery_secret_values_returned": False,
        "omitted_sections": [
            "api_key_operator_checklist",
            "api_key_provider_recovery_checklist",
            "live_data_smoke_summary",
            "signal_workflow_smoke_summary",
            "recording_smoke_summary",
            "provider_recovery_smokes",
        ],
        "network_call": payload.get("network_call") is True,
        "live_data_required": payload.get("live_data_required") is True,
        "hermes_runtime_started": False,
        "telegram_send_call": False,
        "send_call": False,
        "order_submission": False,
        "mutates_local_state": False,
        "secret_values_returned": False,
    }


def _api_key_provider_recovery_summary(
    recovery_checklist: dict[str, Any],
) -> dict[str, Any]:
    raw_items = recovery_checklist.get("items")
    items = (
        [item for item in raw_items if isinstance(item, dict)]
        if isinstance(raw_items, list)
        else []
    )
    compact_items = [_api_key_provider_recovery_summary_item(item) for item in items]
    first_item = compact_items[0] if compact_items else None
    smoke_available_count = sum(
        1 for item in compact_items if item.get("recovery_smoke_available") is True
    )
    network_call_count = sum(
        1 for item in compact_items if item.get("network_call") is True
    )
    mutates_local_state_count = sum(
        1 for item in compact_items if item.get("mutates_local_state") is True
    )
    secret_values_returned_count = sum(
        1 for item in compact_items if item.get("secret_values_returned") is True
    )
    exception_message_returned_count = sum(
        1 for item in compact_items if item.get("exception_message_returned") is True
    )
    url_returned_count = sum(
        1 for item in compact_items if item.get("url_returned") is True
    )
    recovery_pending_count = sum(
        1 for item in compact_items if item.get("recovery_status") == "pending"
    )
    recovery_blocked_count = sum(
        1 for item in compact_items if item.get("recovery_status") == "blocked"
    )
    provider_recovery_has_pending = recovery_pending_count > 0
    provider_recovery_has_blocked = recovery_blocked_count > 0
    if not compact_items:
        provider_recovery_action_status = "no_recovery_required"
    elif provider_recovery_has_pending and provider_recovery_has_blocked:
        provider_recovery_action_status = "partially_retryable"
    elif provider_recovery_has_pending:
        provider_recovery_action_status = "ready_to_retry"
    else:
        provider_recovery_action_status = "blocked"
    first_pending_item = next(
        (
            item
            for item in compact_items
            if item.get("recovery_status") == "pending"
        ),
        None,
    )
    first_blocked_item = next(
        (
            item
            for item in compact_items
            if item.get("recovery_status") == "blocked"
        ),
        None,
    )
    summary = {
        "schema_version": "api_key_provider_recovery_summary.v1",
        "status": recovery_checklist.get("status", "ok"),
        "provider_recovery_required": bool(compact_items),
        "provider_error_count": recovery_checklist.get("provider_error_count", 0),
        "provider_recovery_smoke_count": recovery_checklist.get(
            "provider_recovery_smoke_count",
            0,
        ),
        "provider_recovery_smoke_available_count": smoke_available_count,
        "provider_recovery_smoke_unavailable_count": (
            len(compact_items) - smoke_available_count
        ),
        "provider_recovery_all_smokes_available": (
            bool(compact_items) and smoke_available_count == len(compact_items)
        ),
        "provider_recovery_network_call_count": network_call_count,
        "provider_recovery_all_network_calls": (
            bool(compact_items) and network_call_count == len(compact_items)
        ),
        "provider_recovery_mutates_local_state_count": mutates_local_state_count,
        "provider_recovery_any_mutates_local_state": mutates_local_state_count > 0,
        "provider_recovery_secret_values_returned_count": (
            secret_values_returned_count
        ),
        "provider_recovery_any_secret_values_returned": (
            secret_values_returned_count > 0
        ),
        "provider_recovery_next_setup_actions": _ordered_unique_strings(
            [item.get("next_setup_action") for item in compact_items]
        ),
        "provider_recovery_exception_types": _ordered_unique_strings(
            [item.get("exception_type") for item in compact_items]
        ),
        "provider_recovery_exception_message_returned_count": (
            exception_message_returned_count
        ),
        "provider_recovery_any_exception_messages_returned": (
            exception_message_returned_count > 0
        ),
        "provider_recovery_url_returned_count": url_returned_count,
        "provider_recovery_any_urls_returned": url_returned_count > 0,
        "provider_recovery_network_call_policies": _ordered_unique_strings(
            [item.get("network_call_policy") for item in compact_items]
        ),
        "provider_recovery_statuses": _ordered_unique_strings(
            [item.get("recovery_status") for item in compact_items]
        ),
        "provider_recovery_pending_count": recovery_pending_count,
        "provider_recovery_blocked_count": recovery_blocked_count,
        "provider_recovery_has_pending": provider_recovery_has_pending,
        "provider_recovery_has_blocked": provider_recovery_has_blocked,
        "provider_recovery_retry_ready": provider_recovery_has_pending,
        "provider_recovery_all_retryable": (
            bool(compact_items) and not provider_recovery_has_blocked
        ),
        "provider_recovery_action_status": provider_recovery_action_status,
        "provider_recovery_all_pending": (
            bool(compact_items) and recovery_pending_count == len(compact_items)
        ),
        "provider_recovery_pending_provider_families": _ordered_unique_strings(
            [
                item.get("provider_family")
                for item in compact_items
                if item.get("recovery_status") == "pending"
            ]
        ),
        "provider_recovery_blocked_provider_families": _ordered_unique_strings(
            [
                item.get("provider_family")
                for item in compact_items
                if item.get("recovery_status") == "blocked"
            ]
        ),
        "provider_recovery_pending_providers": _ordered_unique_strings(
            [
                item.get("provider")
                for item in compact_items
                if item.get("recovery_status") == "pending"
            ]
        ),
        "provider_recovery_blocked_providers": _ordered_unique_strings(
            [
                item.get("provider")
                for item in compact_items
                if item.get("recovery_status") == "blocked"
            ]
        ),
        "provider_recovery_pending_smoke_command_names": _ordered_unique_strings(
            [
                item.get("smoke_command_name")
                for item in compact_items
                if item.get("recovery_status") == "pending"
            ]
        ),
        "provider_recovery_pending_smoke_commands": _string_list(
            [
                item.get("recovery_smoke_command")
                for item in compact_items
                if item.get("recovery_status") == "pending"
            ]
        ),
        "provider_recovery_blocked_smoke_command_names": _ordered_unique_strings(
            [
                item.get("smoke_command_name")
                for item in compact_items
                if item.get("recovery_status") == "blocked"
            ]
        ),
        "provider_recovery_blocked_smoke_commands": _string_list(
            [
                item.get("recovery_smoke_command")
                for item in compact_items
                if item.get("recovery_status") == "blocked"
            ]
        ),
        "provider_recovery_provider_families": _ordered_unique_strings(
            [item.get("provider_family") for item in compact_items]
        ),
        "provider_recovery_providers": _ordered_unique_strings(
            [item.get("provider") for item in compact_items]
        ),
        "provider_recovery_smoke_command_names": _ordered_unique_strings(
            [item.get("smoke_command_name") for item in compact_items]
        ),
        "provider_recovery_smoke_commands": _string_list(
            [item.get("recovery_smoke_command") for item in compact_items]
        ),
        "provider_recovery_preferred_env_keys": _ordered_unique_strings(
            [item.get("preferred_env_key") for item in compact_items]
        ),
        "provider_recovery_accepted_env_keys": _ordered_unique_strings(
            [
                env_key
                for item in compact_items
                for env_key in _string_list(item.get("accepted_env_keys"))
            ]
        ),
        "provider_recovery_accepted_env_key_groups": [
            accepted_env_keys
            for accepted_env_keys in (
                _string_list(item.get("accepted_env_keys")) for item in compact_items
            )
            if accepted_env_keys
        ],
        "item_count": len(compact_items),
        "next_pending_recovery_smoke_command_name": (
            first_pending_item.get("smoke_command_name")
            if first_pending_item
            else None
        ),
        "next_pending_recovery_smoke_command": (
            first_pending_item.get("recovery_smoke_command")
            if first_pending_item
            else None
        ),
        "next_pending_recovery_provider_family": (
            first_pending_item.get("provider_family")
            if first_pending_item
            else None
        ),
        "next_pending_recovery_provider": (
            first_pending_item.get("provider") if first_pending_item else None
        ),
        "next_pending_recovery_next_setup_action": (
            first_pending_item.get("next_setup_action")
            if first_pending_item
            else None
        ),
        "next_pending_recovery_preferred_env_key": (
            first_pending_item.get("preferred_env_key")
            if first_pending_item
            else None
        ),
        "next_pending_recovery_accepted_env_keys": (
            _string_list(first_pending_item.get("accepted_env_keys"))
            if first_pending_item
            else []
        ),
        "next_pending_recovery_network_call_policy": (
            first_pending_item.get("network_call_policy")
            if first_pending_item
            else None
        ),
        "next_pending_recovery_smoke_available": first_pending_item is not None,
        "next_pending_recovery_network_call": (
            isinstance(first_pending_item.get("recovery_smoke_command"), str)
            if first_pending_item
            else False
        ),
        "next_pending_recovery_mutates_local_state": (
            first_pending_item.get("mutates_local_state") is True
            if first_pending_item
            else False
        ),
        "next_pending_recovery_secret_values_returned": False,
        "next_blocked_recovery_smoke_command_name": (
            first_blocked_item.get("smoke_command_name")
            if first_blocked_item
            else None
        ),
        "next_blocked_recovery_smoke_command": (
            first_blocked_item.get("recovery_smoke_command")
            if first_blocked_item
            else None
        ),
        "next_blocked_recovery_provider_family": (
            first_blocked_item.get("provider_family")
            if first_blocked_item
            else None
        ),
        "next_blocked_recovery_provider": (
            first_blocked_item.get("provider") if first_blocked_item else None
        ),
        "next_blocked_recovery_next_setup_action": (
            first_blocked_item.get("next_setup_action")
            if first_blocked_item
            else None
        ),
        "next_blocked_recovery_preferred_env_key": (
            first_blocked_item.get("preferred_env_key")
            if first_blocked_item
            else None
        ),
        "next_blocked_recovery_accepted_env_keys": (
            _string_list(first_blocked_item.get("accepted_env_keys"))
            if first_blocked_item
            else []
        ),
        "next_blocked_recovery_network_call_policy": (
            first_blocked_item.get("network_call_policy")
            if first_blocked_item
            else None
        ),
        "next_blocked_recovery_smoke_available": False,
        "next_blocked_recovery_network_call": (
            isinstance(first_blocked_item.get("recovery_smoke_command"), str)
            if first_blocked_item
            else False
        ),
        "next_blocked_recovery_mutates_local_state": (
            first_blocked_item.get("mutates_local_state") is True
            if first_blocked_item
            else False
        ),
        "next_blocked_recovery_secret_values_returned": False,
        "next_recovery_smoke_command_name": (
            first_item.get("smoke_command_name") if first_item else None
        ),
        "next_recovery_smoke_command": (
            first_item.get("recovery_smoke_command") if first_item else None
        ),
        "items": compact_items,
        "network_call": False,
        "mutates_local_state": False,
        "secret_values_returned": False,
    }
    if first_item:
        provider_family = first_item.get("provider_family")
        provider = first_item.get("provider")
        preferred_env_key = first_item.get("preferred_env_key")
        accepted_env_keys = _string_list(first_item.get("accepted_env_keys"))
        network_call_policy = first_item.get("network_call_policy")
        next_recovery_command = first_item.get("recovery_smoke_command")
        next_setup_action = first_item.get("next_setup_action")
        if isinstance(provider_family, str):
            summary["next_recovery_provider_family"] = provider_family
        if isinstance(provider, str):
            summary["next_recovery_provider"] = provider
        summary["next_recovery_smoke_available"] = (
            first_item.get("recovery_smoke_available") is True
        )
        if isinstance(next_setup_action, str):
            summary["next_recovery_next_setup_action"] = next_setup_action
        if isinstance(preferred_env_key, str):
            summary["next_recovery_preferred_env_key"] = preferred_env_key
        if accepted_env_keys:
            summary["next_recovery_accepted_env_keys"] = accepted_env_keys
        if isinstance(network_call_policy, str):
            summary["next_recovery_network_call_policy"] = network_call_policy
        summary["next_recovery_network_call"] = isinstance(
            next_recovery_command,
            str,
        )
        summary["next_recovery_mutates_local_state"] = (
            first_item.get("mutates_local_state") is True
        )
        exception_type = first_item.get("exception_type")
        if isinstance(exception_type, str):
            summary["next_recovery_exception_type"] = exception_type
        summary["next_recovery_exception_message_returned"] = (
            first_item.get("exception_message_returned") is True
        )
        summary["next_recovery_url_returned"] = first_item.get("url_returned") is True
        summary["next_recovery_secret_values_returned"] = False
    return summary


def _api_key_provider_recovery_summary_item(
    item: dict[str, Any],
) -> dict[str, Any]:
    recovery_smoke = _optional_mapping(item.get("recovery_smoke")) or {}
    recovery_smoke_available = item.get("recovery_smoke_available") is True
    summary = {
        "provider_family": item.get("provider_family"),
        "provider": item.get("provider"),
        "smoke_command_name": item.get("smoke_command_name"),
        "recovery_smoke_command": item.get("recovery_smoke_command"),
        "recovery_smoke_available": recovery_smoke_available,
        "recovery_status": "pending" if recovery_smoke_available else "blocked",
        "next_setup_action": item.get("next_setup_action"),
        "preferred_env_key": item.get("preferred_env_key"),
        "accepted_env_keys": _string_list(item.get("accepted_env_keys")),
        "network_call": isinstance(item.get("recovery_smoke_command"), str),
        "mutates_local_state": recovery_smoke.get("mutates_local_state") is True,
        "exception_type": item.get("exception_type"),
        "exception_message_returned": item.get("exception_message_returned") is True,
        "url_returned": item.get("url_returned") is True,
        "secret_values_returned": False,
    }
    network_call_policy = recovery_smoke.get("network_call_policy")
    if isinstance(network_call_policy, str):
        summary["network_call_policy"] = network_call_policy
    return summary


def _api_key_pipeline_summary_only_checks(raw_checks: Any) -> list[dict[str, Any]]:
    checks = raw_checks if isinstance(raw_checks, list) else []
    return [
        {
            "tool": check.get("tool"),
            "name": check.get("name"),
            "passed": check.get("passed") is True,
            "secret_values_returned": False,
        }
        for check in checks
        if isinstance(check, dict)
    ]


def _api_key_setup_file_summary(
    live_data_setup_summary: dict[str, Any],
) -> dict[str, Any]:
    dotenv_file_status = _optional_mapping(
        live_data_setup_summary.get("dotenv_file_status")
    ) or {}
    dotenv_template = _optional_mapping(
        live_data_setup_summary.get("dotenv_template")
    ) or {}
    live_data_setup_steps = _optional_mapping(
        live_data_setup_summary.get("live_data_setup_steps")
    ) or {}
    provider_family_summary = _optional_mapping(
        live_data_setup_summary.get("provider_family_summary")
    ) or {}
    entries = dotenv_template.get("entries")
    template_entries = entries if isinstance(entries, list) else []
    preferred_env_keys = [
        entry["preferred_env_key"]
        for entry in template_entries
        if isinstance(entry, dict) and isinstance(entry.get("preferred_env_key"), str)
    ]
    return {
        "schema_version": "api_key_setup_file_summary.v1",
        "source_path": dotenv_file_status.get("source_path"),
        "target_path": dotenv_file_status.get("target_path"),
        "source_exists": dotenv_file_status.get("source_exists") is True,
        "target_exists": dotenv_file_status.get("target_exists") is True,
        "copy_required": dotenv_file_status.get("copy_required") is True,
        "copy_command": _optional_mapping(dotenv_file_status.get("copy_command")),
        "preferred_env_keys": preferred_env_keys,
        "preferred_env_key_count": len(preferred_env_keys),
        "configured_provider_families": _string_list(
            provider_family_summary.get("configured_provider_families")
        ),
        "missing_provider_families": _string_list(
            provider_family_summary.get("missing_provider_families")
        ),
        "configured_provider_family_count": provider_family_summary.get(
            "configured_count"
        ),
        "required_provider_family_count": provider_family_summary.get(
            "required_count"
        ),
        "next_setup_step": live_data_setup_steps.get("next_step"),
        "ready_to_run_live_smoke": (
            live_data_setup_summary.get("ready_to_run_live_smoke") is True
        ),
        "network_call": False,
        "mutates_local_state": False,
        "secret_values_returned": False,
    }


def _api_key_dotenv_loading_summary(
    live_data_api_key_status: dict[str, Any],
    live_data_setup_summary: dict[str, Any],
) -> dict[str, Any]:
    dotenv = _optional_mapping(live_data_api_key_status.get("dotenv")) or {}
    dotenv_file_status = _optional_mapping(
        live_data_setup_summary.get("dotenv_file_status")
    ) or {}
    live_data_setup_steps = _optional_mapping(
        live_data_setup_summary.get("live_data_setup_steps")
    ) or {}
    disabled = dotenv.get("disabled") is True
    supported = dotenv.get("supported") is True
    return {
        "schema_version": "api_key_dotenv_loading_summary.v1",
        "dotenv_supported": supported,
        "dotenv_loading_enabled": supported and not disabled,
        "disabled": disabled,
        "disabled_env_key": local_env.DOTENV_DISABLED_ENV,
        "configuration_precedence": _string_list(dotenv.get("precedence")),
        "source_path": dotenv_file_status.get("source_path"),
        "target_path": dotenv_file_status.get("target_path"),
        "source_exists": dotenv_file_status.get("source_exists") is True,
        "target_exists": dotenv_file_status.get("target_exists") is True,
        "copy_required": dotenv_file_status.get("copy_required") is True,
        "next_setup_step": live_data_setup_steps.get("next_step"),
        "ready_to_run_live_smoke": (
            live_data_setup_summary.get("ready_to_run_live_smoke") is True
        ),
        "network_call": False,
        "mutates_local_state": False,
        "secret_values_returned": False,
    }


def _api_key_pipeline_smoke_summary(smoke: dict[str, Any]) -> dict[str, Any]:
    live_data_setup_summary = _optional_mapping(
        smoke.get("live_data_setup_summary")
    ) or {}
    next_smoke_command = _optional_mapping(
        live_data_setup_summary.get("next_smoke_command")
    ) or {}
    provider_family_summary = _optional_mapping(
        live_data_setup_summary.get("provider_family_summary")
    ) or {}
    live_data_setup_steps = _optional_mapping(
        live_data_setup_summary.get("live_data_setup_steps")
    ) or {}
    setup_steps = live_data_setup_steps.get("steps")
    provider_setup_actions = _optional_mapping(
        live_data_setup_summary.get("provider_setup_actions")
    ) or {}
    provider_smoke_plan = _optional_mapping(
        live_data_setup_summary.get("provider_smoke_plan")
    ) or {}
    provider_error_summaries = smoke.get("provider_error_summaries")
    provider_error_rows = (
        [
            row
            for row in provider_error_summaries
            if isinstance(row, dict)
        ]
        if isinstance(provider_error_summaries, list)
        else []
    )
    provider_smoke_summaries = smoke.get("provider_smoke_summaries")
    provider_smoke_rows = (
        [
            row
            for row in provider_smoke_summaries
            if isinstance(row, dict)
        ]
        if isinstance(provider_smoke_summaries, list)
        else []
    )
    provider_error_compact_summary = _provider_error_compact_summary(
        provider_error_rows,
        provider_smoke_plan=provider_smoke_plan,
    )
    next_operator_action = _optional_mapping(
        live_data_setup_summary.get("next_operator_action")
    ) or {}
    return {
        "schema_version": smoke.get("schema_version"),
        "status": smoke.get("status"),
        "error_summary": _optional_mapping(smoke.get("error_summary")),
        "network_call": smoke.get("network_call"),
        "live_data_required": smoke.get("live_data_required"),
        "mutates_local_state": smoke.get("mutates_local_state", False),
        "secret_values_returned": smoke.get("secret_values_returned"),
        "live_data_setup_summary_status": live_data_setup_summary.get("status"),
        "ready_to_run_live_smoke": live_data_setup_summary.get(
            "ready_to_run_live_smoke"
        ),
        "provider_route_status": live_data_setup_summary.get(
            "provider_route_status"
        ),
        "provider_family_summary": provider_family_summary,
        "configured_provider_family_count": provider_family_summary.get(
            "configured_count"
        ),
        "required_provider_family_count": provider_family_summary.get(
            "required_count"
        ),
        "missing_provider_families": provider_family_summary.get(
            "missing_provider_families"
        ),
        "live_data_setup_steps": live_data_setup_steps,
        "next_operator_action": next_operator_action,
        "next_setup_step": live_data_setup_steps.get("next_step"),
        "setup_step_count": len(setup_steps) if isinstance(setup_steps, list) else 0,
        "provider_setup_actions": provider_setup_actions,
        "provider_setup_action_count": len(provider_setup_actions),
        "provider_smoke_plan": provider_smoke_plan,
        "provider_smoke_count": provider_smoke_plan.get("provider_smoke_count"),
        "ready_provider_smoke_count": provider_smoke_plan.get(
            "ready_provider_smoke_count"
        ),
        "blocked_provider_smoke_count": provider_smoke_plan.get(
            "blocked_provider_smoke_count"
        ),
        "provider_smoke_summaries": provider_smoke_rows,
        "provider_smoke_summary_count": len(provider_smoke_rows),
        "provider_error_summaries": provider_error_rows,
        "provider_error_summary_count": len(provider_error_rows),
        "failed_provider_families": provider_error_compact_summary[
            "failed_provider_families"
        ],
        "failed_provider_count": provider_error_compact_summary[
            "failed_provider_count"
        ],
        "first_provider_error_summary": provider_error_compact_summary[
            "first_provider_error_summary"
        ],
        "next_provider_recovery_action": provider_error_compact_summary[
            "next_provider_recovery_action"
        ],
        "next_provider_recovery_smoke": provider_error_compact_summary[
            "next_provider_recovery_smoke"
        ],
        "next_provider_recovery_smoke_command_name": (
            provider_error_compact_summary[
                "next_provider_recovery_smoke_command_name"
            ]
        ),
        "provider_recovery_smokes": provider_error_compact_summary[
            "provider_recovery_smokes"
        ],
        "provider_recovery_smoke_count": provider_error_compact_summary[
            "provider_recovery_smoke_count"
        ],
        "next_smoke_command_name": next_smoke_command.get("name"),
    }


def _api_key_pipeline_provider_route_summary(route: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": route.get("schema_version"),
        "status": route.get("status"),
        "provider_factory": route.get("provider_factory"),
        "selected_provider_classes": route.get("selected_provider_classes"),
        "missing": route.get("missing"),
        "network_call": route.get("network_call"),
        "secret_values_returned": route.get("secret_values_returned"),
    }


def _api_key_provider_selection_summary(
    provider_route: dict[str, Any],
    live_data_setup_summary: dict[str, Any],
) -> dict[str, Any]:
    provider_setup_actions = (
        _optional_mapping(live_data_setup_summary.get("provider_setup_actions"))
        or {}
    )
    providers = _optional_mapping(provider_route.get("providers")) or {}
    providers_from_route = bool(providers)
    if not providers:
        providers = provider_setup_actions
    provider_rows: list[tuple[str, dict[str, Any]]] = []
    for family, provider in providers.items():
        row = _optional_mapping(provider)
        if row is None:
            continue
        provider_family = row.get("provider_family")
        if isinstance(provider_family, str):
            provider_rows.append((provider_family, row))
        elif isinstance(family, str):
            provider_rows.append((family, row))
    raw_route_entries = provider_route.get("route")
    route_entries = (
        [entry for entry in raw_route_entries if isinstance(entry, dict)]
        if isinstance(raw_route_entries, list)
        else []
    )
    selected_provider_by_route = {
        str(entry["provider_family"]): entry.get("provider")
        for entry in route_entries
        if isinstance(entry.get("provider_family"), str)
        and entry.get("provider_family") != "fixture"
    }
    configured_provider_families = [
        family for family, row in provider_rows if row.get("configured") is True
    ]
    required_provider_families = [family for family, _row in provider_rows]
    missing_provider_families = [
        family
        for family in required_provider_families
        if family not in configured_provider_families
    ]
    configured_env_keys_by_provider_family = {
        family: _string_list(row.get("configured_env_keys"))
        for family, row in provider_rows
    }
    provider_env_key_hints_by_family = {
        family: {
            "preferred_env_key": row.get("preferred_env_key")
            or (
                _optional_mapping(provider_setup_actions.get(family)) or {}
            ).get("preferred_env_key"),
            "accepted_env_keys": _string_list(row.get("accepted_env_keys"))
            or _string_list(
                (
                    _optional_mapping(provider_setup_actions.get(family)) or {}
                ).get("accepted_env_keys")
            ),
        }
        for family, row in provider_rows
    }
    selected_provider_classes = _string_list(
        provider_route.get("selected_provider_classes")
    )
    selected_provider_by_family = {
        family: selected_provider_by_route.get(family)
        or (
            row.get("provider")
            if row.get("selected") is True
            or (
                not providers_from_route
                and row.get("configured") is True
                and selected_provider_classes
            )
            else None
        )
        for family, row in provider_rows
    }
    return {
        "schema_version": "api_key_provider_selection_summary.v1",
        "status": provider_route.get("status"),
        "provider_factory": provider_route.get("provider_factory"),
        "selected_provider_classes": selected_provider_classes,
        "selected_provider_class_count": len(selected_provider_classes),
        "configured_provider_families": configured_provider_families,
        "configured_provider_family_count": len(configured_provider_families),
        "missing_provider_families": missing_provider_families,
        "configured_env_keys_by_provider_family": (
            configured_env_keys_by_provider_family
        ),
        "provider_env_key_hints_by_family": provider_env_key_hints_by_family,
        "selected_provider_by_family": selected_provider_by_family,
        "ready_to_run_live_smoke": (
            provider_route.get("status") == "ready"
            and live_data_setup_summary.get("ready_to_run_live_smoke") is True
        ),
        "network_call": False,
        "mutates_local_state": False,
        "secret_values_returned": False,
    }


def _api_key_integration_status_summary(
    *,
    setup_status_summary: dict[str, Any],
    api_key_next_action_summary: dict[str, Any],
    api_key_pipeline_failure_summary: dict[str, Any],
    api_key_setup_file_summary: dict[str, Any],
    api_key_dotenv_loading_summary: dict[str, Any],
    api_key_provider_selection_summary: dict[str, Any],
    api_key_provider_recovery_summary: dict[str, Any],
) -> dict[str, Any]:
    configured_provider_families = _string_list(
        setup_status_summary.get("configured_provider_families")
    )
    missing_provider_families = _string_list(
        setup_status_summary.get("missing_provider_families")
    )
    selected_provider_classes = _string_list(
        api_key_provider_selection_summary.get("selected_provider_classes")
    )
    configured_provider_family_count = setup_status_summary.get(
        "configured_provider_family_count"
    )
    required_provider_family_count = setup_status_summary.get(
        "required_provider_family_count"
    )
    selected_provider_class_count = api_key_provider_selection_summary.get(
        "selected_provider_class_count"
    )
    api_keys_configured = (
        isinstance(configured_provider_family_count, int)
        and isinstance(required_provider_family_count, int)
        and required_provider_family_count > 0
        and configured_provider_family_count == required_provider_family_count
        and not missing_provider_families
    )
    live_providers_selected = (
        api_keys_configured
        and selected_provider_class_count == configured_provider_family_count
    )
    ready_to_run_live_smoke = (
        setup_status_summary.get("ready_to_run_live_smoke") is True
        and api_key_provider_selection_summary.get("ready_to_run_live_smoke")
        is True
    )
    summary = {
        "schema_version": "api_key_integration_status_summary.v1",
        "status": api_key_next_action_summary.get("status"),
        "api_keys_configured": api_keys_configured,
        "dotenv_loading_enabled": (
            api_key_dotenv_loading_summary.get("dotenv_loading_enabled") is True
        ),
        "dotenv_target_exists": (
            api_key_setup_file_summary.get("target_exists") is True
        ),
        "live_providers_selected": live_providers_selected,
        "ready_to_run_live_smoke": ready_to_run_live_smoke,
        "configured_provider_families": configured_provider_families,
        "missing_provider_families": missing_provider_families,
        "selected_provider_classes": selected_provider_classes,
        "failure_category": api_key_pipeline_failure_summary.get(
            "failure_category"
        ),
        "has_failures": (
            api_key_pipeline_failure_summary.get("has_failures") is True
        ),
        "next_action_name": api_key_next_action_summary.get("next_action_name"),
        "next_action_is_recovery": (
            api_key_next_action_summary.get("next_action_is_recovery") is True
        ),
        "next_action_network_call": (
            api_key_next_action_summary.get("next_action_network_call") is True
        ),
        "provider_recovery_action_status": (
            api_key_provider_recovery_summary.get(
                "provider_recovery_action_status"
            )
        ),
        "provider_recovery_item_count": (
            api_key_provider_recovery_summary.get("item_count", 0)
        ),
        "provider_recovery_pending_count": (
            api_key_provider_recovery_summary.get(
                "provider_recovery_pending_count",
                0,
            )
        ),
        "provider_recovery_blocked_count": (
            api_key_provider_recovery_summary.get(
                "provider_recovery_blocked_count",
                0,
            )
        ),
        "provider_error_count": (
            api_key_provider_recovery_summary.get("provider_error_count", 0)
        ),
        "provider_recovery_smoke_count": (
            api_key_provider_recovery_summary.get(
                "provider_recovery_smoke_count",
                0,
            )
        ),
        "provider_recovery_provider_families": _string_list(
            api_key_provider_recovery_summary.get(
                "provider_recovery_provider_families"
            )
        ),
        "provider_recovery_providers": _string_list(
            api_key_provider_recovery_summary.get("provider_recovery_providers")
        ),
        "provider_recovery_pending_provider_families": _string_list(
            api_key_provider_recovery_summary.get(
                "provider_recovery_pending_provider_families"
            )
        ),
        "provider_recovery_pending_providers": _string_list(
            api_key_provider_recovery_summary.get(
                "provider_recovery_pending_providers"
            )
        ),
        "provider_recovery_blocked_provider_families": _string_list(
            api_key_provider_recovery_summary.get(
                "provider_recovery_blocked_provider_families"
            )
        ),
        "provider_recovery_blocked_providers": _string_list(
            api_key_provider_recovery_summary.get(
                "provider_recovery_blocked_providers"
            )
        ),
        "provider_recovery_smoke_command_names": _string_list(
            api_key_provider_recovery_summary.get(
                "provider_recovery_smoke_command_names"
            )
        ),
        "provider_recovery_smoke_commands": _string_list(
            api_key_provider_recovery_summary.get("provider_recovery_smoke_commands")
        ),
        "provider_recovery_pending_smoke_command_names": _string_list(
            api_key_provider_recovery_summary.get(
                "provider_recovery_pending_smoke_command_names"
            )
        ),
        "provider_recovery_pending_smoke_commands": _string_list(
            api_key_provider_recovery_summary.get(
                "provider_recovery_pending_smoke_commands"
            )
        ),
        "provider_recovery_blocked_smoke_command_names": _string_list(
            api_key_provider_recovery_summary.get(
                "provider_recovery_blocked_smoke_command_names"
            )
        ),
        "provider_recovery_blocked_smoke_commands": _string_list(
            api_key_provider_recovery_summary.get(
                "provider_recovery_blocked_smoke_commands"
            )
        ),
        "provider_recovery_retry_ready": (
            api_key_provider_recovery_summary.get("provider_recovery_retry_ready")
            is True
        ),
        "provider_recovery_all_retryable": (
            api_key_provider_recovery_summary.get(
                "provider_recovery_all_retryable"
            )
            is True
        ),
        "provider_recovery_has_pending": (
            api_key_provider_recovery_summary.get("provider_recovery_has_pending")
            is True
        ),
        "provider_recovery_has_blocked": (
            api_key_provider_recovery_summary.get("provider_recovery_has_blocked")
            is True
        ),
        "next_pending_recovery_smoke_command_name": (
            api_key_provider_recovery_summary.get(
                "next_pending_recovery_smoke_command_name"
            )
        ),
        "next_pending_recovery_smoke_command": (
            api_key_provider_recovery_summary.get(
                "next_pending_recovery_smoke_command"
            )
        ),
        "next_pending_recovery_provider_family": (
            api_key_provider_recovery_summary.get(
                "next_pending_recovery_provider_family"
            )
        ),
        "next_pending_recovery_provider": (
            api_key_provider_recovery_summary.get("next_pending_recovery_provider")
        ),
        "next_pending_recovery_next_setup_action": (
            api_key_provider_recovery_summary.get(
                "next_pending_recovery_next_setup_action"
            )
        ),
        "next_pending_recovery_preferred_env_key": (
            api_key_provider_recovery_summary.get(
                "next_pending_recovery_preferred_env_key"
            )
        ),
        "next_pending_recovery_accepted_env_keys": _string_list(
            api_key_provider_recovery_summary.get(
                "next_pending_recovery_accepted_env_keys"
            )
        ),
        "next_pending_recovery_network_call_policy": (
            api_key_provider_recovery_summary.get(
                "next_pending_recovery_network_call_policy"
            )
        ),
        "next_pending_recovery_smoke_available": (
            api_key_provider_recovery_summary.get(
                "next_pending_recovery_smoke_available"
            )
            is True
        ),
        "next_pending_recovery_network_call": (
            api_key_provider_recovery_summary.get(
                "next_pending_recovery_network_call"
            )
            is True
        ),
        "next_pending_recovery_mutates_local_state": (
            api_key_provider_recovery_summary.get(
                "next_pending_recovery_mutates_local_state"
            )
            is True
        ),
        "next_pending_recovery_secret_values_returned": False,
        "next_blocked_recovery_smoke_command_name": (
            api_key_provider_recovery_summary.get(
                "next_blocked_recovery_smoke_command_name"
            )
        ),
        "next_blocked_recovery_smoke_command": (
            api_key_provider_recovery_summary.get(
                "next_blocked_recovery_smoke_command"
            )
        ),
        "next_blocked_recovery_provider_family": (
            api_key_provider_recovery_summary.get(
                "next_blocked_recovery_provider_family"
            )
        ),
        "next_blocked_recovery_provider": (
            api_key_provider_recovery_summary.get("next_blocked_recovery_provider")
        ),
        "next_blocked_recovery_next_setup_action": (
            api_key_provider_recovery_summary.get(
                "next_blocked_recovery_next_setup_action"
            )
        ),
        "next_blocked_recovery_preferred_env_key": (
            api_key_provider_recovery_summary.get(
                "next_blocked_recovery_preferred_env_key"
            )
        ),
        "next_blocked_recovery_accepted_env_keys": _string_list(
            api_key_provider_recovery_summary.get(
                "next_blocked_recovery_accepted_env_keys"
            )
        ),
        "next_blocked_recovery_network_call_policy": (
            api_key_provider_recovery_summary.get(
                "next_blocked_recovery_network_call_policy"
            )
        ),
        "next_blocked_recovery_smoke_available": (
            api_key_provider_recovery_summary.get(
                "next_blocked_recovery_smoke_available"
            )
            is True
        ),
        "next_blocked_recovery_network_call": (
            api_key_provider_recovery_summary.get(
                "next_blocked_recovery_network_call"
            )
            is True
        ),
        "next_blocked_recovery_mutates_local_state": (
            api_key_provider_recovery_summary.get(
                "next_blocked_recovery_mutates_local_state"
            )
            is True
        ),
        "next_blocked_recovery_secret_values_returned": False,
        "network_call": False,
        "mutates_local_state": False,
        "secret_values_returned": False,
    }
    preferred_env_key = api_key_next_action_summary.get("preferred_env_key")
    accepted_env_keys = _string_list(
        api_key_next_action_summary.get("accepted_env_keys")
    )
    next_action_provider_family = api_key_next_action_summary.get(
        "next_action_provider_family"
    )
    next_action_provider = api_key_next_action_summary.get("next_action_provider")
    next_action_smoke_command_name = api_key_next_action_summary.get(
        "next_action_smoke_command_name"
    )
    next_action_expected_live_contract = api_key_next_action_summary.get(
        "next_action_expected_live_contract"
    )
    next_action_expected_live_checks = _string_list(
        api_key_next_action_summary.get("next_action_expected_live_checks")
    )
    if isinstance(next_action_provider_family, str):
        summary["next_action_provider_family"] = next_action_provider_family
    if isinstance(next_action_provider, str):
        summary["next_action_provider"] = next_action_provider
    if isinstance(next_action_smoke_command_name, str):
        summary["next_action_smoke_command_name"] = next_action_smoke_command_name
    if isinstance(next_action_expected_live_contract, str):
        summary["next_action_expected_live_contract"] = (
            next_action_expected_live_contract
        )
    if next_action_expected_live_checks:
        summary["next_action_expected_live_checks"] = (
            next_action_expected_live_checks
        )
    if isinstance(preferred_env_key, str):
        summary["preferred_env_key"] = preferred_env_key
    if accepted_env_keys:
        summary["accepted_env_keys"] = accepted_env_keys
    return summary


def _api_key_provider_recovery_checklist(
    live_data_smoke_summary: dict[str, Any],
) -> dict[str, Any]:
    provider_errors = live_data_smoke_summary.get("provider_error_summaries")
    provider_error_rows = (
        [row for row in provider_errors if isinstance(row, dict)]
        if isinstance(provider_errors, list)
        else []
    )
    recovery_smokes = live_data_smoke_summary.get("provider_recovery_smokes")
    recovery_smoke_rows = (
        [row for row in recovery_smokes if isinstance(row, dict)]
        if isinstance(recovery_smokes, list)
        else []
    )
    recovery_smokes_by_name = {
        row["smoke_command_name"]: row
        for row in recovery_smoke_rows
        if isinstance(row.get("smoke_command_name"), str)
    }
    live_data_setup_summary = _optional_mapping(
        live_data_smoke_summary.get("live_data_setup_summary")
    ) or {}
    provider_setup_actions = _optional_mapping(
        live_data_setup_summary.get("provider_setup_actions")
    ) or _optional_mapping(live_data_smoke_summary.get("provider_setup_actions")) or {}
    items: list[dict[str, Any]] = []
    for provider_error in provider_error_rows:
        provider_family = provider_error.get("provider_family")
        smoke_command_name = provider_error.get("smoke_command_name")
        recovery_smoke = (
            recovery_smokes_by_name.get(smoke_command_name)
            if isinstance(smoke_command_name, str)
            else None
        )
        provider_setup_action = (
            _optional_mapping(provider_setup_actions.get(provider_family))
            if isinstance(provider_family, str)
            else None
        ) or {}
        items.append(
            {
                "provider_family": provider_family,
                "provider": provider_error.get("provider"),
                "smoke_command_name": smoke_command_name,
                "exception_type": provider_error.get("exception_type"),
                "exception_message_returned": (
                    provider_error.get("exception_message_returned") is True
                ),
                "url_returned": provider_error.get("url_returned") is True,
                "preferred_env_key": provider_setup_action.get("preferred_env_key")
                or (
                    recovery_smoke.get("preferred_env_key")
                    if recovery_smoke is not None
                    else None
                ),
                "accepted_env_keys": _string_list(
                    provider_setup_action.get("accepted_env_keys")
                ),
                "next_setup_action": provider_error.get("next_setup_action"),
                "recovery_smoke": recovery_smoke,
                "recovery_smoke_command": (
                    recovery_smoke.get("command")
                    if recovery_smoke is not None
                    else None
                ),
                "recovery_smoke_available": recovery_smoke is not None,
                "secret_values_returned": False,
            }
        )

    return {
        "schema_version": "api_key_provider_recovery_checklist.v1",
        "status": "conflict" if items else "ok",
        "provider_error_count": len(provider_error_rows),
        "provider_recovery_smoke_count": len(recovery_smoke_rows),
        "item_count": len(items),
        "items": items,
        "secret_values_returned": False,
    }


def _api_key_pipeline_setup_status_summary(
    live_data_setup_summary: dict[str, Any],
) -> dict[str, Any]:
    provider_family_summary = _optional_mapping(
        live_data_setup_summary.get("provider_family_summary")
    ) or {}
    provider_smoke_plan = _optional_mapping(
        live_data_setup_summary.get("provider_smoke_plan")
    ) or {}
    live_data_setup_steps = _optional_mapping(
        live_data_setup_summary.get("live_data_setup_steps")
    ) or {}
    next_operator_action = _optional_mapping(
        live_data_setup_summary.get("next_operator_action")
    ) or {}
    next_provider_smoke = _optional_mapping(
        next_operator_action.get("next_provider_smoke")
    )
    next_smoke_command = _optional_mapping(
        live_data_setup_summary.get("next_smoke_command")
    ) or {}
    return {
        "schema_version": "api_key_pipeline_setup_status_summary.v1",
        "status": live_data_setup_summary.get("status"),
        "ready_to_run_live_smoke": live_data_setup_summary.get(
            "ready_to_run_live_smoke"
        ),
        "api_key_status": live_data_setup_summary.get("api_key_status"),
        "provider_route_status": live_data_setup_summary.get(
            "provider_route_status"
        ),
        "configured_provider_families": live_data_setup_summary.get(
            "configured_provider_families"
        ),
        "missing_provider_families": provider_family_summary.get(
            "missing_provider_families"
        ),
        "configured_provider_family_count": provider_family_summary.get(
            "configured_count"
        ),
        "required_provider_family_count": provider_family_summary.get(
            "required_count"
        ),
        "provider_smoke_count": provider_smoke_plan.get("provider_smoke_count"),
        "ready_provider_smoke_count": provider_smoke_plan.get(
            "ready_provider_smoke_count"
        ),
        "blocked_provider_smoke_count": provider_smoke_plan.get(
            "blocked_provider_smoke_count"
        ),
        "next_setup_step": live_data_setup_steps.get("next_step"),
        "next_operator_action_name": next_operator_action.get("name"),
        "next_smoke_command_name": next_smoke_command.get("name"),
        "next_provider_smoke": next_provider_smoke,
        "next_provider_smoke_command_name": next_operator_action.get(
            "next_provider_smoke_command_name"
        ),
        "selected_provider_classes": live_data_setup_summary.get(
            "selected_provider_classes"
        ),
        "network_call": False,
        "mutates_local_state": False,
        "secret_values_returned": False,
    }


def _api_key_pipeline_api_key_requirements_summary(
    live_data_setup_summary: dict[str, Any],
) -> dict[str, Any]:
    provider_setup_actions = _optional_mapping(
        live_data_setup_summary.get("provider_setup_actions")
    ) or {}
    provider_requirements: dict[str, dict[str, Any]] = {}
    required_env_keys: list[str] = []
    configured_env_keys: list[str] = []
    for provider_family, raw_action in provider_setup_actions.items():
        action = _optional_mapping(raw_action) or {}
        preferred_env_key = action.get("preferred_env_key")
        action_configured_env_keys = _string_list(action.get("configured_env_keys"))
        if isinstance(preferred_env_key, str):
            required_env_keys.append(preferred_env_key)
        configured_env_keys.extend(action_configured_env_keys)
        provider_requirements[provider_family] = {
            "provider": action.get("provider"),
            "configured": action.get("configured"),
            "configured_env_keys": action_configured_env_keys,
            "preferred_env_key": preferred_env_key,
            "accepted_env_keys": _string_list(action.get("accepted_env_keys")),
            "setup_status": action.get("setup_status"),
            "next_setup_action": action.get("next_setup_action"),
            "smoke_command_name": action.get("smoke_command_name"),
            "network_call": False,
            "mutates_local_state": False,
            "secret_values_returned": False,
        }
    provider_family_summary = _optional_mapping(
        live_data_setup_summary.get("provider_family_summary")
    ) or {}
    return {
        "schema_version": "api_key_pipeline_api_key_requirements_summary.v1",
        "status": live_data_setup_summary.get("status"),
        "required_env_keys": required_env_keys,
        "configured_env_keys": _ordered_unique_strings(configured_env_keys),
        "missing_provider_families": provider_family_summary.get(
            "missing_provider_families"
        ),
        "configured_provider_families": provider_family_summary.get(
            "configured_provider_families"
        ),
        "provider_requirements": provider_requirements,
        "network_call": False,
        "mutates_local_state": False,
        "secret_values_returned": False,
    }


def _api_key_pipeline_api_key_command_summary(
    live_data_setup_summary: dict[str, Any],
) -> dict[str, Any]:
    dotenv_file_status = _optional_mapping(
        live_data_setup_summary.get("dotenv_file_status")
    ) or {}
    copy_dotenv_command = _optional_mapping(
        dotenv_file_status.get("copy_command")
    ) or {}
    provider_smoke_plan = _optional_mapping(
        live_data_setup_summary.get("provider_smoke_plan")
    ) or {}
    raw_provider_smokes = provider_smoke_plan.get("provider_smokes")
    provider_smoke_rows = raw_provider_smokes if isinstance(raw_provider_smokes, list) else []
    provider_setup_actions = _optional_mapping(
        live_data_setup_summary.get("provider_setup_actions")
    ) or {}
    provider_smokes = [
        _api_key_command_provider_smoke_row(
            provider_smoke,
            provider_setup_actions,
        )
        for provider_smoke in provider_smoke_rows
        if isinstance(provider_smoke, dict)
    ]
    next_provider_smoke = _next_ready_provider_smoke(provider_smokes)
    next_smoke_command = _optional_mapping(
        live_data_setup_summary.get("next_smoke_command")
    ) or {}
    one_shot_smoke_command = _optional_mapping(
        live_data_setup_summary.get("one_shot_smoke_command")
    ) or {}
    return {
        "schema_version": "api_key_pipeline_api_key_command_summary.v1",
        "status": live_data_setup_summary.get("status"),
        "copy_dotenv_command": copy_dotenv_command,
        "next_smoke_command": next_smoke_command,
        "one_shot_pipeline_smoke": {
            "name": one_shot_smoke_command.get("name"),
            "command": one_shot_smoke_command.get("command"),
            "network_call": one_shot_smoke_command.get("network_call"),
            "network_call_policy": one_shot_smoke_command.get(
                "network_call_policy"
            ),
            "mutates_local_state": one_shot_smoke_command.get(
                "mutates_local_state"
            ),
            "secret_values_returned": one_shot_smoke_command.get(
                "secret_values_returned"
            ),
        },
        "next_provider_smoke": next_provider_smoke,
        "next_provider_smoke_command_name": next_provider_smoke.get(
            "smoke_command_name"
        )
        if next_provider_smoke
        else None,
        "provider_smoke_commands": provider_smokes,
        "provider_smoke_command_count": len(provider_smokes),
        "network_call": False,
        "mutates_local_state": False,
        "secret_values_returned": False,
    }


def _api_key_command_provider_smoke_row(
    provider_smoke: dict[str, Any],
    provider_setup_actions: dict[str, Any],
) -> dict[str, Any]:
    env_hint = _api_key_command_provider_smoke_env_hint(
        provider_smoke,
        provider_setup_actions,
    )
    return {
        "provider_family": provider_smoke.get("provider_family"),
        "provider": provider_smoke.get("provider"),
        "status": provider_smoke.get("status"),
        "smoke_command_name": provider_smoke.get("smoke_command_name"),
        "command": provider_smoke.get("command"),
        "network_call": True,
        "network_call_policy": provider_smoke.get("network_call_policy"),
        "expected_live_contract": provider_smoke.get("expected_live_contract"),
        "expected_live_checks": _string_list(
            provider_smoke.get("expected_live_checks")
        ),
        "preferred_env_key": env_hint.get("preferred_env_key"),
        "accepted_env_keys": env_hint.get("accepted_env_keys", []),
        "mutates_local_state": False,
        "secret_values_returned": False,
    }


def _api_key_command_provider_smoke_env_hint(
    provider_smoke: dict[str, Any],
    provider_setup_actions: dict[str, Any],
) -> dict[str, Any]:
    provider_family = provider_smoke.get("provider_family")
    provider_setup_action = (
        _optional_mapping(provider_setup_actions.get(provider_family))
        if isinstance(provider_family, str)
        else None
    ) or {}
    preferred_env_key = provider_smoke.get(
        "preferred_env_key"
    ) or provider_setup_action.get("preferred_env_key")
    accepted_env_keys = _string_list(
        provider_smoke.get("accepted_env_keys")
        or provider_setup_action.get("accepted_env_keys")
    )
    return {
        "preferred_env_key": preferred_env_key,
        "accepted_env_keys": accepted_env_keys,
    }


def _api_key_pipeline_operator_checklist(
    *,
    setup_status_summary: dict[str, Any],
    api_key_requirements_summary: dict[str, Any],
    api_key_command_summary: dict[str, Any],
    api_key_provider_recovery_checklist: dict[str, Any],
) -> dict[str, Any]:
    copy_dotenv_command = _optional_mapping(
        api_key_command_summary.get("copy_dotenv_command")
    ) or {}
    provider_requirements = _optional_mapping(
        api_key_requirements_summary.get("provider_requirements")
    ) or {}
    provider_smoke_commands = api_key_command_summary.get("provider_smoke_commands")
    provider_smoke_rows = (
        provider_smoke_commands if isinstance(provider_smoke_commands, list) else []
    )
    next_provider_smoke = _optional_mapping(
        api_key_command_summary.get("next_provider_smoke")
    )
    one_shot_pipeline_smoke = _optional_mapping(
        api_key_command_summary.get("one_shot_pipeline_smoke")
    ) or {}
    missing_provider_families = _string_list(
        api_key_requirements_summary.get("missing_provider_families")
    )
    ready_to_run_live_smoke = (
        setup_status_summary.get("ready_to_run_live_smoke") is True
    )
    dotenv_setup_ready = (
        ready_to_run_live_smoke or copy_dotenv_command.get("required") is not True
    )
    provider_recovery_items = api_key_provider_recovery_checklist.get("items")
    provider_recovery_rows = (
        [row for row in provider_recovery_items if isinstance(row, dict)]
        if isinstance(provider_recovery_items, list)
        else []
    )
    provider_recovery_required = bool(provider_recovery_rows)
    next_provider_recovery_action = (
        provider_recovery_rows[0] if provider_recovery_rows else None
    )
    steps = [
        {
            "name": "prepare_dotenv",
            "status": "ready" if dotenv_setup_ready else "pending",
            "command": copy_dotenv_command.get("command"),
            "mutates_local_state": copy_dotenv_command.get("mutates_local_state"),
            "network_call": False,
            "secret_values_returned": False,
        },
        {
            "name": "fill_live_data_api_keys",
            "status": "ready" if not missing_provider_families else "pending",
            "required_env_keys": api_key_requirements_summary.get(
                "required_env_keys"
            ),
            "configured_env_keys": api_key_requirements_summary.get(
                "configured_env_keys"
            ),
            "missing_provider_families": missing_provider_families,
            "provider_requirements": provider_requirements,
            "network_call": False,
            "mutates_local_state": False,
            "secret_values_returned": False,
        },
        {
            "name": "run_provider_smokes",
            "status": "ready" if ready_to_run_live_smoke else "blocked",
            "provider_smoke_commands": provider_smoke_rows,
            "provider_smoke_command_count": len(provider_smoke_rows),
            "next_provider_smoke": next_provider_smoke,
            "next_provider_smoke_command_name": next_provider_smoke.get(
                "smoke_command_name"
            )
            if next_provider_smoke
            else None,
            "network_call": True,
            "network_call_policy": "only_when_matching_api_key_selects_live_provider",
            "mutates_local_state": False,
            "secret_values_returned": False,
        },
        {
            "name": "run_api_key_pipeline_smoke",
            "status": "ready" if ready_to_run_live_smoke else "blocked",
            "command": one_shot_pipeline_smoke.get("command"),
            "network_call": one_shot_pipeline_smoke.get("network_call"),
            "network_call_policy": one_shot_pipeline_smoke.get(
                "network_call_policy"
            ),
            "mutates_local_state": one_shot_pipeline_smoke.get(
                "mutates_local_state"
            ),
            "secret_values_returned": one_shot_pipeline_smoke.get(
                "secret_values_returned"
            ),
        },
    ]
    if provider_recovery_required:
        steps.append(
            {
                "name": "recover_failed_providers",
                "status": "pending",
                "provider_recovery_item_count": len(provider_recovery_rows),
                "next_provider_recovery_action": next_provider_recovery_action,
                "recovery_smoke_command": next_provider_recovery_action.get(
                    "recovery_smoke_command"
                )
                if next_provider_recovery_action is not None
                else None,
                "recovery_smoke_available": next_provider_recovery_action.get(
                    "recovery_smoke_available"
                )
                if next_provider_recovery_action is not None
                else False,
                "preferred_env_key": next_provider_recovery_action.get(
                    "preferred_env_key"
                )
                if next_provider_recovery_action is not None
                else None,
                "accepted_env_keys": next_provider_recovery_action.get(
                    "accepted_env_keys"
                )
                if next_provider_recovery_action is not None
                else [],
                "network_call": True,
                "network_call_policy": "only_when_matching_api_key_selects_live_provider",
                "mutates_local_state": False,
                "secret_values_returned": False,
            }
        )
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
    checklist_status = (
        "conflict"
        if provider_recovery_required
        else setup_status_summary.get("status")
    )
    current_step = (
        "recover_failed_providers"
        if provider_recovery_required
        else setup_status_summary.get("next_setup_step")
    )
    return {
        "schema_version": "api_key_pipeline_operator_checklist.v1",
        "status": checklist_status,
        "current_step": current_step,
        "provider_recovery_status": api_key_provider_recovery_checklist.get(
            "status"
        ),
        "provider_recovery_required": provider_recovery_required,
        "provider_recovery_item_count": len(provider_recovery_rows),
        "next_provider_recovery_action": next_provider_recovery_action,
        "provider_recovery_checklist": api_key_provider_recovery_checklist,
        "ready": not blocking_step_names,
        "ready_step_names": ready_step_names,
        "ready_step_count": len(ready_step_names),
        "blocking_step_names": blocking_step_names,
        "blocking_step_count": len(blocking_step_names),
        "next_blocking_step": blocking_step_names[0] if blocking_step_names else None,
        "next_blocking_action": next_blocking_action,
        "steps": steps,
        "step_count": len(steps),
        "network_call": False,
        "mutates_local_state": False,
        "secret_values_returned": False,
    }


def _live_data_setup_summary(
    api_key_status: dict[str, Any],
    provider_route: dict[str, Any],
) -> dict[str, Any]:
    providers = _optional_mapping(api_key_status.get("providers")) or {}
    configured_provider_families = [
        family
        for family, provider in providers.items()
        if _optional_mapping(provider).get("configured") is True
    ]
    route_summary = _api_key_pipeline_provider_route_summary(provider_route)
    missing = _ordered_unique_strings(
        [
            *(api_key_status.get("missing") or []),
            *(provider_route.get("missing") or []),
        ]
    )
    ready_to_run_live_smoke = (
        api_key_status.get("status") == "ready"
        and provider_route.get("status") == "ready"
    )
    provider_family_summary = _live_data_provider_family_summary(
        api_key_status=api_key_status,
        ready_to_run_live_smoke=ready_to_run_live_smoke,
    )
    dotenv_file_status = _live_data_dotenv_file_status()
    one_shot_smoke_command = api_key_status.get("one_shot_smoke_command")
    provider_setup_actions = _live_data_provider_setup_actions(api_key_status)
    provider_smoke_plan = _live_data_provider_smoke_plan(
        provider_setup_actions=provider_setup_actions,
        one_shot_smoke_command=one_shot_smoke_command,
        ready_to_run_live_smoke=ready_to_run_live_smoke,
    )
    live_data_setup_steps = _live_data_setup_steps(
        dotenv_file_status=dotenv_file_status,
        provider_family_summary=provider_family_summary,
        provider_smoke_plan=provider_smoke_plan,
        one_shot_smoke_command=one_shot_smoke_command,
        ready_to_run_live_smoke=ready_to_run_live_smoke,
    )
    return {
        "schema_version": "live_data_setup_summary.v1",
        "status": "ready" if ready_to_run_live_smoke else "blocked",
        "ready_to_run_live_smoke": ready_to_run_live_smoke,
        "api_key_status": api_key_status.get("status"),
        "provider_route_status": provider_route.get("status"),
        "configured_provider_families": configured_provider_families,
        "provider_family_summary": provider_family_summary,
        "provider_setup_actions": provider_setup_actions,
        "provider_smoke_plan": provider_smoke_plan,
        "missing": missing,
        "provider_factory": route_summary.get("provider_factory"),
        "selected_provider_classes": route_summary.get("selected_provider_classes"),
        "provider_route_summary": route_summary,
        "dotenv_template": _live_data_dotenv_template(),
        "dotenv_file_status": dotenv_file_status,
        "live_data_setup_steps": live_data_setup_steps,
        "next_operator_action": _live_data_next_operator_action(
            dotenv_file_status=dotenv_file_status,
            provider_family_summary=provider_family_summary,
            live_data_setup_steps=live_data_setup_steps,
            one_shot_smoke_command=one_shot_smoke_command,
            ready_to_run_live_smoke=ready_to_run_live_smoke,
        ),
        "one_shot_smoke_command": one_shot_smoke_command,
        "next_smoke_command": _local_command(
            "run_api_key_pipeline_smoke"
            if ready_to_run_live_smoke
            else "get_live_data_api_key_status"
        ),
        "network_call": False,
        "mutates_local_state": False,
        "secret_values_returned": False,
    }


def _live_data_provider_family_summary(
    *,
    api_key_status: dict[str, Any],
    ready_to_run_live_smoke: bool,
) -> dict[str, Any]:
    providers = _optional_mapping(api_key_status.get("providers")) or {}
    summary = _optional_mapping(api_key_status.get("provider_family_summary")) or {}
    required_provider_families = _string_list(
        summary.get("required_provider_families")
    ) or list(providers)
    configured_provider_families = _string_list(
        summary.get("configured_provider_families")
    ) or [
        family
        for family, provider in providers.items()
        if _optional_mapping(provider).get("configured") is True
    ]
    missing_provider_families = _string_list(
        summary.get("missing_provider_families")
    ) or [
        family
        for family in required_provider_families
        if family not in configured_provider_families
    ]
    return {
        "required_provider_families": required_provider_families,
        "configured_provider_families": configured_provider_families,
        "missing_provider_families": missing_provider_families,
        "configured_count": len(configured_provider_families),
        "required_count": len(required_provider_families),
        "ready_to_run_live_smoke": ready_to_run_live_smoke,
        "network_call": False,
        "mutates_local_state": False,
        "secret_values_returned": False,
    }


def _live_data_provider_setup_actions(
    api_key_status: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    providers = _optional_mapping(api_key_status.get("providers")) or {}
    return _live_data_provider_setup_actions_from_providers(providers)


def _live_data_provider_setup_actions_from_providers(
    providers: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    actions: dict[str, dict[str, Any]] = {}
    for provider_family, raw_provider_status in providers.items():
        provider_status = _optional_mapping(raw_provider_status) or {}
        smoke_command = _optional_mapping(provider_status.get("smoke_command")) or {}
        actions[provider_family] = {
            "provider": provider_status.get("provider"),
            "configured": provider_status.get("configured"),
            "configured_env_keys": provider_status.get("configured_env_keys"),
            "preferred_env_key": provider_status.get("preferred_env_key"),
            "accepted_env_keys": provider_status.get("accepted_env_keys"),
            "setup_status": provider_status.get("setup_status"),
            "next_setup_action": provider_status.get("next_setup_action"),
            "dotenv_target_path": provider_status.get("dotenv_target_path"),
            "example": provider_status.get("example"),
            "smoke_command_name": smoke_command.get("name"),
            "smoke_command": smoke_command,
            "network_call": False,
            "mutates_local_state": False,
            "secret_values_returned": False,
        }
    return actions


def _live_data_provider_smoke_plan(
    *,
    provider_setup_actions: dict[str, dict[str, Any]],
    one_shot_smoke_command: Any,
    ready_to_run_live_smoke: bool,
) -> dict[str, Any]:
    provider_smokes: list[dict[str, Any]] = []
    for provider_family, action in provider_setup_actions.items():
        smoke_command = _optional_mapping(action.get("smoke_command")) or {}
        configured = action.get("configured") is True
        provider_smokes.append(
            {
                "provider_family": provider_family,
                "provider": action.get("provider"),
                "status": "ready" if configured else "blocked",
                "preferred_env_key": action.get("preferred_env_key"),
                "accepted_env_keys": _string_list(action.get("accepted_env_keys")),
                "next_setup_action": action.get("next_setup_action"),
                "smoke_command_name": smoke_command.get("name"),
                "command": smoke_command.get("command"),
                "network_call": True,
                "expected_live_contract": smoke_command.get(
                    "expected_live_contract"
                ),
                "expected_live_checks": smoke_command.get("expected_live_checks"),
                "network_call_policy": smoke_command.get("network_call_policy"),
                "mutates_local_state": False,
                "secret_values_returned": False,
            }
        )
    ready_provider_smoke_count = sum(
        1 for provider_smoke in provider_smokes if provider_smoke["status"] == "ready"
    )
    one_shot_command = _optional_mapping(one_shot_smoke_command) or {}
    return {
        "schema_version": "live_data_provider_smoke_plan.v1",
        "provider_smokes": provider_smokes,
        "provider_smoke_count": len(provider_smokes),
        "ready_provider_smoke_count": ready_provider_smoke_count,
        "blocked_provider_smoke_count": len(provider_smokes)
        - ready_provider_smoke_count,
        "one_shot_pipeline_smoke": {
            "name": one_shot_command.get("name"),
            "status": "ready" if ready_to_run_live_smoke else "blocked",
            "command": one_shot_command.get("command"),
            "network_call": one_shot_command.get("network_call"),
            "network_call_policy": one_shot_command.get("network_call_policy"),
            "mutates_local_state": one_shot_command.get("mutates_local_state"),
            "secret_values_returned": one_shot_command.get(
                "secret_values_returned"
            ),
        },
        "network_call": False,
        "mutates_local_state": False,
        "secret_values_returned": False,
    }


def _string_list(values: Any) -> list[str]:
    if not isinstance(values, list):
        return []
    return [value for value in values if isinstance(value, str)]


def _ordered_unique_strings(values: list[Any]) -> list[str]:
    result: list[str] = []
    for value in values:
        if not isinstance(value, str) or value in result:
            continue
        result.append(value)
    return result


def _live_data_dotenv_template() -> dict[str, Any]:
    return {
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
                "example": "POLYGON_API_KEY=your_polygon_key",
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
                "example": "FRED_API_KEY=your_fred_key",
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
                "example": "NEWS_API_KEY=your_newsapi_key",
                "secret": True,
            },
        ],
        "network_call": False,
        "mutates_local_state": False,
        "secret_values_returned": False,
    }


def _live_data_dotenv_file_status() -> dict[str, Any]:
    target_path = local_env.REPO_ROOT_ENV_PATH
    source_path = target_path.with_name(".env.example")
    target_exists = target_path.is_file()
    source_exists = source_path.is_file()
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


def _live_data_setup_steps(
    *,
    dotenv_file_status: dict[str, Any],
    provider_family_summary: dict[str, Any],
    provider_smoke_plan: dict[str, Any],
    one_shot_smoke_command: Any,
    ready_to_run_live_smoke: bool,
) -> dict[str, Any]:
    smoke_command = _optional_mapping(one_shot_smoke_command)
    raw_provider_smokes = provider_smoke_plan.get("provider_smokes")
    provider_smokes = raw_provider_smokes if isinstance(raw_provider_smokes, list) else []
    next_provider_smoke = _next_ready_provider_smoke(provider_smokes)
    target_exists = dotenv_file_status.get("target_exists") is True
    source_exists = dotenv_file_status.get("source_exists") is True
    copy_required = dotenv_file_status.get("copy_required") is True
    configured_count = provider_family_summary.get("configured_count")
    required_count = provider_family_summary.get("required_count")
    keys_ready = (
        isinstance(configured_count, int)
        and isinstance(required_count, int)
        and required_count > 0
        and configured_count == required_count
    )
    if not source_exists and not target_exists and not keys_ready:
        next_step = "restore_env_example"
        dotenv_status = "blocked"
    elif copy_required and not keys_ready:
        next_step = "prepare_dotenv"
        dotenv_status = "pending"
    else:
        dotenv_status = "ready"
        next_step = (
            "run_provider_smokes"
            if ready_to_run_live_smoke
            else "fill_live_data_api_keys"
        )
    return {
        "schema_version": "live_data_setup_steps.v1",
        "next_step": next_step,
        "steps": [
            {
                "name": "prepare_dotenv",
                "status": dotenv_status,
                "next_action": dotenv_file_status.get("next_action"),
                "copy_command": dotenv_file_status.get("copy_command"),
                "network_call": False,
                "mutates_local_state": False,
                "secret_values_returned": False,
            },
            {
                "name": "fill_live_data_api_keys",
                "status": "ready" if keys_ready else "pending",
                "configured_provider_families": provider_family_summary.get(
                    "configured_provider_families"
                ),
                "missing_provider_families": provider_family_summary.get(
                    "missing_provider_families"
                ),
                "configured_count": configured_count,
                "required_count": required_count,
                "required_env_keys": dotenv_file_status.get(
                    "fill_keys_after_copy",
                    {},
                ).get("required_env_keys"),
                "network_call": False,
                "mutates_local_state": False,
                "secret_values_returned": False,
            },
            {
                "name": "run_provider_smokes",
                "status": "ready" if ready_to_run_live_smoke else "blocked",
                "provider_smokes": provider_smokes,
                "provider_smoke_count": len(provider_smokes),
                "next_provider_smoke": next_provider_smoke,
                "next_provider_smoke_command_name": next_provider_smoke.get(
                    "smoke_command_name"
                )
                if next_provider_smoke
                else None,
                "ready_provider_smoke_count": provider_smoke_plan.get(
                    "ready_provider_smoke_count"
                ),
                "blocked_provider_smoke_count": provider_smoke_plan.get(
                    "blocked_provider_smoke_count"
                ),
                "network_call": True,
                "network_call_policy": (
                    "only_when_matching_api_key_selects_live_provider"
                ),
                "mutates_local_state": False,
                "secret_values_returned": False,
            },
            {
                "name": "run_api_key_pipeline_smoke",
                "status": "ready" if ready_to_run_live_smoke else "blocked",
                "command": smoke_command.get("command"),
                "network_call": smoke_command.get("network_call"),
                "mutates_local_state": smoke_command.get("mutates_local_state"),
                "secret_values_returned": smoke_command.get(
                    "secret_values_returned"
                ),
            },
        ],
        "network_call": False,
        "mutates_local_state": False,
        "secret_values_returned": False,
    }


def _live_data_next_operator_action(
    *,
    dotenv_file_status: dict[str, Any],
    provider_family_summary: dict[str, Any],
    live_data_setup_steps: dict[str, Any],
    one_shot_smoke_command: Any,
    ready_to_run_live_smoke: bool,
) -> dict[str, Any]:
    next_step = str(live_data_setup_steps.get("next_step") or "")
    copy_command = _optional_mapping(dotenv_file_status.get("copy_command")) or {}
    smoke_command = _optional_mapping(one_shot_smoke_command) or {}
    setup_step_rows = live_data_setup_steps.get("steps")
    setup_steps = setup_step_rows if isinstance(setup_step_rows, list) else []
    provider_smoke_step: dict[str, Any] = {}
    for step in setup_steps:
        step_mapping = _optional_mapping(step)
        if step_mapping is None or step_mapping.get("name") != "run_provider_smokes":
            continue
        provider_smoke_step = step_mapping
        break
    base = {
        "schema_version": "live_data_next_operator_action.v1",
        "name": next_step,
        "dotenv_target_path": ".env",
        "network_call": False,
        "mutates_local_state": False,
        "secret_values_returned": False,
    }
    if next_step == "restore_env_example":
        return {
            **base,
            "status": "blocked",
            "reason": "missing_env_example_and_env",
            "required_file": ".env.example",
            "secret_input_required": False,
        }
    if next_step == "prepare_dotenv":
        return {
            **base,
            "status": "pending",
            "command": copy_command.get("command"),
            "source_path": copy_command.get("source_path"),
            "target_path": copy_command.get("target_path"),
            "next_after_action": "fill_live_data_api_keys",
            "secret_input_required": False,
            "mutates_local_state": True,
        }
    if next_step == "run_provider_smokes":
        return {
            **base,
            "status": "ready",
            "provider_smokes": provider_smoke_step.get("provider_smokes", []),
            "provider_smoke_count": provider_smoke_step.get("provider_smoke_count"),
            "next_provider_smoke": provider_smoke_step.get("next_provider_smoke"),
            "next_provider_smoke_command_name": provider_smoke_step.get(
                "next_provider_smoke_command_name"
            ),
            "ready_provider_smoke_count": provider_smoke_step.get(
                "ready_provider_smoke_count"
            ),
            "blocked_provider_smoke_count": provider_smoke_step.get(
                "blocked_provider_smoke_count"
            ),
            "network_call": True,
            "network_call_policy": provider_smoke_step.get("network_call_policy"),
            "next_after_action": "run_api_key_pipeline_smoke",
            "secret_input_required": False,
        }
    if ready_to_run_live_smoke:
        return {
            **base,
            "name": "run_api_key_pipeline_smoke",
            "status": "ready",
            "command": smoke_command.get("command"),
            "network_call": bool(smoke_command.get("network_call")),
            "network_call_policy": smoke_command.get("network_call_policy"),
            "secret_input_required": False,
        }
    return {
        **base,
        "name": "fill_live_data_api_keys",
        "status": "pending",
        "required_env_keys": ["POLYGON_API_KEY", "FRED_API_KEY", "NEWS_API_KEY"],
        "configured_provider_families": provider_family_summary.get(
            "configured_provider_families",
            [],
        ),
        "missing_provider_families": provider_family_summary.get(
            "missing_provider_families",
            [],
        ),
        "next_after_action": "run_provider_smokes",
        "secret_input_required": True,
    }


def _next_ready_provider_smoke(provider_smokes: list[Any]) -> dict[str, Any] | None:
    for provider_smoke in provider_smokes:
        smoke = _optional_mapping(provider_smoke)
        if smoke is not None and smoke.get("status") == "ready":
            return smoke
    return None


def _extend_workflow_contract_checks(
    checks: list[dict[str, Any]],
    *,
    tool: str,
    payload: dict[str, Any],
    contract_key: str,
    guard_key: str,
    live_check_name: str,
) -> None:
    contract = _optional_mapping(payload.get(contract_key))
    guard = _optional_mapping(payload.get(guard_key))
    _add_smoke_check(
        checks,
        tool=tool,
        name="payload_live_data_required",
        passed=payload.get("live_data_required") is True,
        expected=True,
        actual=payload.get("live_data_required"),
    )
    _add_smoke_check(
        checks,
        tool=tool,
        name="contract_live_data_required",
        passed=_mapping_value(contract, "live_data_required") is True,
        expected=True,
        actual=_mapping_value(contract, "live_data_required"),
    )
    _add_smoke_check(
        checks,
        tool=tool,
        name="no_order_submission",
        passed=_mapping_value(contract, "order_submission") is False,
        expected=False,
        actual=_mapping_value(contract, "order_submission"),
    )
    _add_guard_status_check(checks, tool, guard)
    _add_guard_check(checks, tool, guard, live_check_name)


def _extend_latest_signal_report_workflow_checks(
    checks: list[dict[str, Any]],
    payload: dict[str, Any],
) -> None:
    guard = _optional_mapping(payload.get("report_contract_guard"))
    _add_smoke_check(
        checks,
        tool="generate_latest_signal_report",
        name="payload_live_data_required",
        passed=payload.get("live_data_required") is True,
        expected=True,
        actual=payload.get("live_data_required"),
    )
    _add_guard_status_check(checks, "generate_latest_signal_report", guard)
    _add_guard_check(
        checks,
        "generate_latest_signal_report",
        guard,
        "report_payload_live_data_required_matches_expected",
    )


def _add_guard_status_check(
    checks: list[dict[str, Any]],
    tool: str,
    guard: dict[str, Any] | None,
) -> None:
    _add_smoke_check(
        checks,
        tool=tool,
        name="guard_status_ok",
        passed=_mapping_value(guard, "status") == "ok",
        expected="ok",
        actual=_mapping_value(guard, "status"),
    )


def _add_guard_check(
    checks: list[dict[str, Any]],
    tool: str,
    guard: dict[str, Any] | None,
    check_name: str,
) -> None:
    actual = _guard_check_passed(guard, check_name)
    _add_smoke_check(
        checks,
        tool=tool,
        name=check_name,
        passed=actual is True,
        expected=True,
        actual=actual,
    )


def _add_smoke_check(
    checks: list[dict[str, Any]],
    *,
    tool: str,
    name: str,
    passed: bool,
    expected: Any,
    actual: Any,
) -> None:
    checks.append(
        {
            "tool": tool,
            "name": name,
            "passed": passed,
            "expected": expected,
            "actual": actual,
        }
    )


def _optional_mapping(value: Any) -> dict[str, Any] | None:
    return value if isinstance(value, dict) else None


def _mapping_value(mapping: dict[str, Any] | None, key: str) -> Any:
    if mapping is None:
        return None
    return mapping.get(key)


def _contract_secret_values_returned(contract: dict[str, Any] | None) -> bool | None:
    if contract is None:
        return None
    return bool(contract.get("secret_values_returned", False))


def _guard_check_passed(guard: dict[str, Any] | None, check_name: str) -> bool | None:
    checks = _mapping_value(guard, "checks")
    if not isinstance(checks, list):
        return None
    for check in checks:
        if not isinstance(check, dict):
            continue
        if check.get("name") == check_name:
            return check.get("passed") is True
    return None


def _setup_live_data_smoke_commands() -> list[dict[str, Any]]:
    return [
        {
            "name": "get_market_snapshot_live_smoke",
            "provider": "polygon",
            "required_env_key_groups": [
                ["HALO_SWING_MARKET_DATA_API_KEY", "POLYGON_API_KEY"]
            ],
            "command": (
                "PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness "
                "get_market_snapshot --input-json '{\"symbols\":[\"QQQ\"]}' --no-audit"
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
        {
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
        {
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
    ]


def _live_data_api_key_provider_status(
    *,
    provider_family: str,
    provider: str,
    preferred_env_key: str,
    accepted_env_keys: list[str],
    missing_name: str,
    smoke_command_name: str,
    optional_live_mode_env: str,
) -> dict[str, Any]:
    configured_env_keys = _configured_env_keys(accepted_env_keys)
    configured = bool(configured_env_keys)
    setup_status = "ready" if configured else "pending"
    return {
        "provider_family": provider_family,
        "provider": provider,
        "configured": configured,
        "configured_env_keys": configured_env_keys,
        "preferred_env_key": preferred_env_key,
        "accepted_env_keys": accepted_env_keys,
        "missing": [] if configured else [missing_name],
        "setup_status": setup_status,
        "next_setup_action": (
            "run_provider_smoke" if configured else "fill_preferred_env_key"
        ),
        "dotenv_target_path": ".env",
        "example": f"{preferred_env_key}=your_{provider}_key",
        "auto_selects_live_provider": configured,
        "live_mode_required": False,
        "optional_live_mode_env": optional_live_mode_env,
        "smoke_command": _live_data_smoke_command(smoke_command_name),
        "network_call": False,
        "mutates_local_state": False,
        "secret_values_returned": False,
    }


def _configured_env_keys(keys: list[str]) -> list[str]:
    return [
        key
        for key in keys
        if _is_env_value_configured(get_config_value(key))
    ]


def _live_data_smoke_command(name: str) -> dict[str, Any]:
    for command in _setup_live_data_smoke_commands():
        if command["name"] == name:
            return command
    raise ValueError(f"unknown live data smoke command: {name}")


def _local_command(name: str) -> dict[str, Any]:
    for command in _setup_local_commands():
        if command["name"] == name:
            return command
    raise ValueError(f"unknown local command: {name}")


def _truthy_config_value(value: str | None) -> bool:
    return isinstance(value, str) and value.strip().lower() in {"1", "true", "yes"}


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
