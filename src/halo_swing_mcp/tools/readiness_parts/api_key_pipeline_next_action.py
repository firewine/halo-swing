# ruff: noqa: F403,F405,F821
"""API-key pipeline next-action summary projection."""

from __future__ import annotations

from .context import *
from .api_key_route_family_fields import _api_key_route_family_fields
from .contract_checks import _optional_mapping
from .live_data_setup import _string_list


__all__ = (
    "_api_key_pipeline_next_operator_action",
    "_api_key_pipeline_next_action_summary",
)


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
    live_data_setup_summary: dict[str, Any],
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
    summary.update(_api_key_route_family_fields(live_data_setup_summary))
    next_after_action = next_operator_action.get("next_after_action")
    dotenv_target_path = next_operator_action.get("dotenv_target_path")
    source_path = next_operator_action.get("source_path")
    target_path = next_operator_action.get("target_path")
    if isinstance(next_after_action, str):
        summary["next_after_action"] = next_after_action
    if isinstance(dotenv_target_path, str):
        summary["dotenv_target_path"] = dotenv_target_path
    if isinstance(source_path, str):
        summary["source_path"] = source_path
    if isinstance(target_path, str):
        summary["target_path"] = target_path
    if "secret_input_required" in next_operator_action:
        summary["secret_input_required"] = (
            next_operator_action.get("secret_input_required") is True
        )
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
    next_action_network_call_policy = (
        next_operator_action.get("network_call_policy")
        or next_provider_recovery_action.get("network_call_policy")
        or next_provider_recovery_smoke.get("network_call_policy")
        or next_provider_smoke.get("network_call_policy")
    )
    selected_provider_class_by_family = _optional_mapping(
        live_data_setup_summary.get("selected_provider_class_by_family")
    ) or {}
    provider_route_data_mode_by_family = _optional_mapping(
        live_data_setup_summary.get("provider_route_data_mode_by_family")
    ) or {}
    provider_route_live_data_required_by_family = _optional_mapping(
        live_data_setup_summary.get("provider_route_live_data_required_by_family")
    ) or {}
    next_action_selected_provider_class = (
        next_operator_action.get("selected_provider_class")
        or next_provider_recovery_action.get("selected_provider_class")
        or next_provider_smoke.get("selected_provider_class")
    )
    next_action_provider_route_data_mode = (
        next_operator_action.get("provider_route_data_mode")
        or next_provider_recovery_action.get("provider_route_data_mode")
        or next_provider_smoke.get("provider_route_data_mode")
    )
    next_action_provider_route_live_data_required = (
        next_operator_action.get("provider_route_live_data_required") is True
        or next_provider_recovery_action.get("provider_route_live_data_required")
        is True
        or next_provider_smoke.get("provider_route_live_data_required") is True
    )
    if isinstance(next_action_provider_family, str):
        if not isinstance(next_action_selected_provider_class, str):
            next_action_selected_provider_class = (
                selected_provider_class_by_family.get(next_action_provider_family)
            )
        if not isinstance(next_action_provider_route_data_mode, str):
            next_action_provider_route_data_mode = (
                provider_route_data_mode_by_family.get(next_action_provider_family)
            )
        next_action_provider_route_live_data_required = (
            next_action_provider_route_live_data_required
            or provider_route_live_data_required_by_family.get(
                next_action_provider_family
            )
            is True
        )
    if isinstance(next_action_provider_family, str):
        summary["next_action_provider_family"] = next_action_provider_family
    if isinstance(next_action_provider, str):
        summary["next_action_provider"] = next_action_provider
    if isinstance(next_action_selected_provider_class, str):
        summary["next_action_selected_provider_class"] = (
            next_action_selected_provider_class
        )
    if isinstance(next_action_provider_route_data_mode, str):
        summary["next_action_provider_route_data_mode"] = (
            next_action_provider_route_data_mode
        )
    if isinstance(next_action_provider_family, str):
        summary["next_action_provider_route_live_data_required"] = (
            next_action_provider_route_live_data_required
        )
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
    if isinstance(next_action_network_call_policy, str):
        summary["next_action_network_call_policy"] = (
            next_action_network_call_policy
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
    required_env_keys = _string_list(next_operator_action.get("required_env_keys"))
    if required_env_keys:
        summary["required_env_keys"] = required_env_keys
    dotenv_examples = _string_list(next_operator_action.get("dotenv_examples"))
    if dotenv_examples:
        summary["dotenv_examples"] = dotenv_examples
        summary["dotenv_example_count"] = len(dotenv_examples)
    return summary
