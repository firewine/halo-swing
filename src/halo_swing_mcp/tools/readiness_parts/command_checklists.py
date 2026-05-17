# ruff: noqa: F403,F405,F821
"""Command Checklists readiness implementation."""

from __future__ import annotations

from .context import *


__all__ = ('_api_key_provider_recovery_checklist', '_api_key_pipeline_setup_status_summary', '_api_key_pipeline_api_key_requirements_summary', '_api_key_pipeline_api_key_command_summary', '_api_key_command_provider_smoke_row', '_api_key_command_provider_smoke_env_hint', '_api_key_pipeline_operator_checklist')


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
        "selected_provider_class_by_family": (
            _optional_mapping(
                live_data_setup_summary.get("selected_provider_class_by_family")
            )
            or {}
        ),
        "provider_route_data_mode_by_family": (
            _optional_mapping(
                live_data_setup_summary.get("provider_route_data_mode_by_family")
            )
            or {}
        ),
        "provider_route_live_data_required_by_family": (
            _optional_mapping(
                live_data_setup_summary.get(
                    "provider_route_live_data_required_by_family"
                )
            )
            or {}
        ),
        "all_selected_routes_live": (
            live_data_setup_summary.get("all_selected_routes_live") is True
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
    dotenv_examples = _live_data_dotenv_examples()
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
            "dotenv_examples": dotenv_examples,
            "dotenv_example_count": len(dotenv_examples),
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
