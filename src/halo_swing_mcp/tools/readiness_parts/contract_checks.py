# ruff: noqa: F403,F405,F821
"""Contract Checks readiness implementation."""

from __future__ import annotations

from .context import *


__all__ = ('_next_ready_provider_smoke', '_extend_workflow_contract_checks', '_extend_latest_signal_report_workflow_checks', '_add_guard_status_check', '_add_guard_check', '_add_smoke_check', '_optional_mapping', '_mapping_value', '_contract_secret_values_returned')


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
