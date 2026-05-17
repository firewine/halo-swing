# ruff: noqa: F403,F405,F821
"""Public Tools readiness implementation."""

from __future__ import annotations

from .context import *


__all__ = ('get_integration_readiness', 'get_integration_setup_checklist', 'get_live_data_api_key_status', 'get_live_data_provider_route', 'validate_live_data_smoke_result', 'run_live_data_smoke', '_provider_error_summaries', '_provider_smoke_summaries', '_provider_error_compact_summary', '_provider_recovery_smoke_commands', '_provider_recovery_smoke_command', 'run_integration_smoke', 'run_live_signal_workflow_smoke', 'run_live_recording_smoke', '_run_live_recording_smoke_with_ledger')


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
