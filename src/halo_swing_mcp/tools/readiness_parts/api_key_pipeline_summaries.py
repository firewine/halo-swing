# ruff: noqa: F403,F405,F821
"""Api Key Pipeline Summaries readiness implementation."""

from __future__ import annotations

from .context import *
from .api_key_route_family_fields import (
    _api_key_route_family_fields,
)


__all__ = ('_api_key_pipeline_checks', '_api_key_pipeline_readiness_summary', '_api_key_operator_checklist_summary', '_api_key_operator_checklist_step_summary', '_api_key_pipeline_stage_summary', '_api_key_pipeline_stage_row', '_api_key_pipeline_check_summary', '_api_key_pipeline_stage_recovery_hints_by_tool', '_api_key_pipeline_check_row', '_api_key_pipeline_failure_summary', '_api_key_pipeline_failure_category', '_api_key_live_http_timeout_summary')


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
        **_api_key_route_family_fields(live_data_setup_summary),
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
    summary.update(_api_key_route_family_fields(api_key_operator_checklist))
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
    required_env_keys = _string_list(next_blocking_action.get("required_env_keys"))
    dotenv_examples = _string_list(next_blocking_action.get("dotenv_examples"))
    if required_env_keys:
        summary["next_blocking_action_required_env_keys"] = required_env_keys
    if dotenv_examples:
        summary["next_blocking_action_dotenv_examples"] = dotenv_examples
        summary["next_blocking_action_dotenv_example_count"] = len(dotenv_examples)
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
    dotenv_examples = _string_list(step.get("dotenv_examples"))
    if dotenv_examples:
        summary["dotenv_examples"] = dotenv_examples
        summary["dotenv_example_count"] = len(dotenv_examples)
    return summary


def _api_key_pipeline_stage_summary(
    *,
    live_data_setup_summary: dict[str, Any],
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
    summary = {
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
    summary.update(_api_key_route_family_fields(live_data_setup_summary))
    return summary


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
    summary = {
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
    summary.update(_api_key_route_family_fields(api_key_pipeline_stage_summary or {}))
    return summary


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
    summary.update(_api_key_route_family_fields(api_key_next_action_summary))
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
