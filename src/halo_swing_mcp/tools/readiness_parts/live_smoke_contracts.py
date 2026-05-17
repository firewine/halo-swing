# ruff: noqa: F403,F405,F821
"""Live Smoke Contracts readiness implementation."""

from __future__ import annotations

from .context import *


__all__ = ('_normalize_optional_smoke_payload', '_extend_market_smoke_checks', '_extend_macro_smoke_checks', '_extend_news_smoke_checks', '_extend_live_signal_workflow_checks', '_workflow_signal_summary', '_workflow_contract_summary', '_workflow_report_summary', '_extend_live_recording_checks', '_recording_summary', '_recording_network_call', '_run_api_key_pipeline_sub_smoke', '_api_key_pipeline_sub_smoke_exception_payload')


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
