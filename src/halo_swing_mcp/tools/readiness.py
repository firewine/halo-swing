"""Offline integration readiness checks for blocked deployment gates."""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Any

from halo_swing_mcp import MCP_SERVER_NAME
from halo_swing_mcp.binance_btc import LIVE_CONFIRMATION
from halo_swing_mcp.config import get_settings
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
    return {
        "schema_version": "integration_setup_checklist.v1",
        "status": readiness["status"],
        "readiness_status": readiness["status"],
        "next_actions": readiness["next_actions"],
        "env_requirements": _setup_env_requirements(gates),
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
            accepted_env_keys=["HALO_SWING_MARKET_DATA_API_KEY", "POLYGON_API_KEY"],
            missing_name="market_ohlcv_api_key",
            smoke_command_name="get_market_snapshot_live_smoke",
            optional_live_mode_env="HALO_SWING_MARKET_DATA_MODE",
        ),
        "macro": _live_data_api_key_provider_status(
            provider_family="macro",
            provider="fred",
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
    return {
        "schema_version": "live_data_api_key_status.v1",
        "status": "ready" if not missing else "blocked",
        "providers": providers,
        "missing": missing,
        "one_shot_smoke_command": _local_command("run_api_key_pipeline_smoke"),
        "dotenv": {
            "supported": True,
            "disabled": _truthy_config_value(get_config_value("HALO_SWING_DISABLE_DOTENV")),
            "precedence": [
                "exported environment variables",
                "repo-root .env",
                "launch-directory .env",
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
        "validation": validation,
        "network_call": network_call,
        "live_data_required": live_data_required,
        "send_call": False,
        "order_submission": False,
        "secret_values_returned": False,
    }


def run_integration_smoke(
    symbols: list[str] | None = None,
    topic: str = "macro",
) -> dict[str, Any]:
    """Run environment readiness and live data smoke in one payload."""

    readiness = get_integration_readiness()
    live_data_smoke = run_live_data_smoke(symbols=symbols, topic=topic)
    readiness_ready = readiness["status"] == "ready"
    live_data_smoke_ok = live_data_smoke["status"] == "ok"
    return {
        "schema_version": "integration_smoke_run.v1",
        "status": "ok" if readiness_ready and live_data_smoke_ok else "blocked",
        "readiness_status": readiness["status"],
        "live_data_smoke_status": live_data_smoke["status"],
        "readiness": readiness,
        "live_data_smoke": live_data_smoke,
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
) -> dict[str, Any]:
    """Run the API-key-backed local integration pipeline smoke checks."""

    readiness = get_integration_readiness()
    live_data_smoke = run_live_data_smoke(symbols=symbols, topic=topic)
    signal_workflow_smoke = run_live_signal_workflow_smoke(
        asset=asset,
        timeframe=timeframe,
    )
    recording_smoke = run_live_recording_smoke(asset=asset, timeframe=timeframe)
    checks = _api_key_pipeline_checks(
        readiness=readiness,
        live_data_smoke=live_data_smoke,
        signal_workflow_smoke=signal_workflow_smoke,
        recording_smoke=recording_smoke,
    )

    return {
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
            "run_live_data_smoke",
            "run_live_signal_workflow_smoke",
            "run_live_recording_smoke",
        ],
        "readiness_summary": _api_key_pipeline_readiness_summary(readiness),
        "live_data_smoke_summary": _api_key_pipeline_smoke_summary(
            live_data_smoke,
        ),
        "signal_workflow_smoke_summary": _api_key_pipeline_smoke_summary(
            signal_workflow_smoke,
        ),
        "recording_smoke_summary": _api_key_pipeline_smoke_summary(
            recording_smoke,
        ),
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
                "run_api_key_pipeline_smoke --input-json "
                "'{\"asset\":\"TQQQ\",\"timeframe\":\"swing_3d_10d\","
                "\"symbols\":[\"QQQ\"],\"topic\":\"macro\"}' --no-audit"
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


def _api_key_pipeline_readiness_summary(readiness: dict[str, Any]) -> dict[str, Any]:
    gates = _optional_mapping(readiness.get("gates")) or {}
    live_data_gate = _optional_mapping(gates.get("live_data")) or {}
    return {
        "status": readiness.get("status"),
        "live_data_status": live_data_gate.get("status"),
        "live_data_ready": live_data_gate.get("ready"),
        "live_data_missing": live_data_gate.get("missing"),
        "next_actions": readiness.get("next_actions"),
    }


def _api_key_pipeline_smoke_summary(smoke: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": smoke.get("schema_version"),
        "status": smoke.get("status"),
        "network_call": smoke.get("network_call"),
        "live_data_required": smoke.get("live_data_required"),
        "mutates_local_state": smoke.get("mutates_local_state", False),
        "secret_values_returned": smoke.get("secret_values_returned"),
    }


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
    accepted_env_keys: list[str],
    missing_name: str,
    smoke_command_name: str,
    optional_live_mode_env: str,
) -> dict[str, Any]:
    configured_env_keys = _configured_env_keys(accepted_env_keys)
    configured = bool(configured_env_keys)
    return {
        "provider_family": provider_family,
        "provider": provider,
        "configured": configured,
        "configured_env_keys": configured_env_keys,
        "accepted_env_keys": accepted_env_keys,
        "missing": [] if configured else [missing_name],
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
