# ruff: noqa: F403,F405,F821
"""Summary-only payload context construction."""

from __future__ import annotations

from .context import *


__all__ = ('_api_key_pipeline_summary_only_context',)


def _api_key_pipeline_summary_only_context(
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
    api_key_integration_status_summary = _optional_mapping(
        payload.get("api_key_integration_status_summary")
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
    api_key_operator_checklist_summary = _api_key_operator_checklist_summary(
        _optional_mapping(payload.get("api_key_operator_checklist")) or {}
    )
    setup_quickstart_steps = api_key_operator_checklist_summary.get("steps")
    setup_quickstart_step_rows = (
        [
            row
            for row in setup_quickstart_steps
            if isinstance(row, dict)
        ]
        if isinstance(setup_quickstart_steps, list)
        else []
    )
    setup_quickstart_rows = [
        {
            "name": row.get("name"),
            "status": row.get("status"),
            "command": row.get("command"),
            "required_env_keys": _string_list(row.get("required_env_keys")),
            "configured_env_keys": _string_list(row.get("configured_env_keys")),
            "missing_provider_families": _string_list(
                row.get("missing_provider_families")
            ),
            "dotenv_examples": _string_list(row.get("dotenv_examples")),
            "dotenv_example_count": row.get("dotenv_example_count"),
            "provider_smoke_command_count": row.get(
                "provider_smoke_command_count"
            ),
            "next_provider_smoke_command_name": row.get(
                "next_provider_smoke_command_name"
            ),
            "network_call": row.get("network_call") is True,
            "network_call_policy": row.get("network_call_policy"),
            "mutates_local_state": row.get("mutates_local_state") is True,
            "secret_values_returned": row.get("secret_values_returned") is True,
        }
        for row in setup_quickstart_step_rows
    ]
    setup_status_summary = _optional_mapping(payload.get("setup_status_summary")) or {}
    api_key_setup_file_summary = _optional_mapping(
        payload.get("api_key_setup_file_summary")
    ) or {}
    api_key_provider_selection_summary = _optional_mapping(
        payload.get("api_key_provider_selection_summary")
    ) or {}
    api_key_requirements_summary = _optional_mapping(
        payload.get("api_key_requirements_summary")
    ) or {}
    provider_requirements = _optional_mapping(
        api_key_requirements_summary.get("provider_requirements")
    ) or {}
    provider_requirement_families = _ordered_unique_strings(
        provider_requirements.keys()
    )
    provider_requirement_rows = {
        family: _optional_mapping(provider_requirements.get(family)) or {}
        for family in provider_requirement_families
    }
    api_key_command_summary = _optional_mapping(
        payload.get("api_key_command_summary")
    ) or {}
    copy_dotenv_command = _optional_mapping(
        api_key_command_summary.get("copy_dotenv_command")
    ) or {}
    next_smoke_command = _optional_mapping(
        api_key_command_summary.get("next_smoke_command")
    ) or {}
    next_provider_smoke = _optional_mapping(
        api_key_command_summary.get("next_provider_smoke")
    ) or {}
    one_shot_pipeline_smoke = _optional_mapping(
        api_key_command_summary.get("one_shot_pipeline_smoke")
    ) or {}
    provider_smoke_commands = api_key_command_summary.get("provider_smoke_commands")
    provider_smoke_command_rows = (
        [
            row
            for row in provider_smoke_commands
            if isinstance(row, dict)
        ]
        if isinstance(provider_smoke_commands, list)
        else []
    )
    raw_provider_smoke_command_count = api_key_command_summary.get(
        "provider_smoke_command_count"
    )
    provider_smoke_command_count = (
        raw_provider_smoke_command_count
        if isinstance(raw_provider_smoke_command_count, int)
        else len(provider_smoke_command_rows)
    )
    provider_smoke_command_rows_by_family = {
        row["provider_family"]: row
        for row in provider_smoke_command_rows
        if isinstance(row.get("provider_family"), str)
    }
    quickstart_command_plan: list[dict[str, Any]] = []
    if copy_dotenv_command.get("command"):
        quickstart_command_plan.append(
            {
                "name": copy_dotenv_command.get("name"),
                "kind": "copy_dotenv",
                "command": copy_dotenv_command.get("command"),
                "provider_family": None,
                "provider": None,
                "selected_provider_class": None,
                "provider_route_data_mode": None,
                "provider_route_live_data_required": False,
                "expected_live_contract": None,
                "expected_live_checks": [],
                "preferred_env_key": None,
                "accepted_env_keys": [],
                "next_setup_action": None,
                "status": "required"
                if copy_dotenv_command.get("required") is True
                else "ready",
                "network_call": copy_dotenv_command.get("network_call") is True,
                "network_call_policy": copy_dotenv_command.get(
                    "network_call_policy"
                ),
                "mutates_local_state": (
                    copy_dotenv_command.get("mutates_local_state") is True
                ),
                "secret_values_returned": (
                    copy_dotenv_command.get("secret_values_returned") is True
                ),
            }
        )
    if (
        next_smoke_command.get("command")
        and next_smoke_command.get("command")
        != one_shot_pipeline_smoke.get("command")
    ):
        quickstart_command_plan.append(
            {
                "name": next_smoke_command.get("name"),
                "kind": "status_check",
                "command": next_smoke_command.get("command"),
                "provider_family": None,
                "provider": None,
                "selected_provider_class": None,
                "provider_route_data_mode": None,
                "provider_route_live_data_required": False,
                "expected_live_contract": None,
                "expected_live_checks": [],
                "preferred_env_key": None,
                "accepted_env_keys": [],
                "next_setup_action": None,
                "status": "ready",
                "network_call": next_smoke_command.get("network_call") is True,
                "network_call_policy": next_smoke_command.get(
                    "network_call_policy"
                ),
                "mutates_local_state": (
                    next_smoke_command.get("mutates_local_state") is True
                ),
                "secret_values_returned": (
                    next_smoke_command.get("secret_values_returned") is True
                ),
            }
        )
    for row in provider_smoke_command_rows:
        quickstart_command_plan.append(
            {
                "name": row.get("smoke_command_name"),
                "kind": "provider_smoke",
                "command": row.get("command"),
                "provider_family": row.get("provider_family"),
                "provider": row.get("provider"),
                "selected_provider_class": row.get("selected_provider_class"),
                "provider_route_data_mode": row.get("provider_route_data_mode"),
                "provider_route_live_data_required": (
                    row.get("provider_route_live_data_required") is True
                ),
                "expected_live_contract": row.get("expected_live_contract"),
                "expected_live_checks": _string_list(
                    row.get("expected_live_checks")
                ),
                "preferred_env_key": row.get("preferred_env_key"),
                "accepted_env_keys": _string_list(row.get("accepted_env_keys")),
                "next_setup_action": row.get("next_setup_action"),
                "status": row.get("status"),
                "network_call": row.get("network_call") is True,
                "network_call_policy": row.get("network_call_policy"),
                "mutates_local_state": row.get("mutates_local_state") is True,
                "secret_values_returned": (
                    row.get("secret_values_returned") is True
                ),
            }
        )
    if one_shot_pipeline_smoke.get("command"):
        quickstart_command_plan.append(
            {
                "name": one_shot_pipeline_smoke.get("name"),
                "kind": "pipeline_smoke",
                "command": one_shot_pipeline_smoke.get("command"),
                "provider_family": None,
                "provider": None,
                "selected_provider_class": None,
                "provider_route_data_mode": None,
                "provider_route_live_data_required": False,
                "expected_live_contract": None,
                "expected_live_checks": [],
                "preferred_env_key": None,
                "accepted_env_keys": [],
                "next_setup_action": None,
                "status": "ready"
                if setup_status_summary.get("ready_to_run_live_smoke") is True
                else "blocked",
                "network_call": one_shot_pipeline_smoke.get("network_call") is True,
                "network_call_policy": one_shot_pipeline_smoke.get(
                    "network_call_policy"
                ),
                "mutates_local_state": (
                    one_shot_pipeline_smoke.get("mutates_local_state") is True
                ),
                "secret_values_returned": (
                    one_shot_pipeline_smoke.get("secret_values_returned") is True
                ),
            }
        )
    next_quickstart_command = api_key_operator_checklist_summary.get(
        "next_blocking_action_command"
    )
    next_quickstart_command_plan_item = next(
        (
            row
            for row in quickstart_command_plan
            if row.get("command") == next_quickstart_command
        ),
        quickstart_command_plan[0] if quickstart_command_plan else None,
    )
    next_quickstart_command_plan_row = next_quickstart_command_plan_item or {}
    return locals()
