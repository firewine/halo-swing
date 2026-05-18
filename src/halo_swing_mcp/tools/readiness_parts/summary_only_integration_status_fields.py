"""Summary-only integration-status top-level field projection."""

from __future__ import annotations

from typing import Any

from .contract_checks import _optional_mapping
from .live_data_setup import _string_list
from .summary_only_provider_route_fields import (
    _api_key_integration_status_route_count_top_level_fields,
)


__all__ = ("_api_key_integration_status_top_level_fields",)


def _bool_from_status_or_provider(
    status_summary: dict[str, Any],
    status_key: str,
    provider_row: dict[str, Any],
    provider_key: str,
) -> bool:
    if status_key in status_summary:
        return status_summary.get(status_key) is True
    return provider_row.get(provider_key) is True


def _api_key_integration_status_top_level_fields(
    *,
    api_key_command_summary: dict[str, Any],
    api_key_integration_status_summary: dict[str, Any],
    api_key_next_action_summary: dict[str, Any],
    next_operator_action: dict[str, Any],
    next_provider_smoke: dict[str, Any],
) -> dict[str, Any]:
    one_shot_pipeline_smoke = (
        _optional_mapping(api_key_command_summary.get("one_shot_pipeline_smoke"))
        or {}
    )
    next_action_command = api_key_next_action_summary.get("next_action_command")
    one_shot_pipeline_smoke_command = one_shot_pipeline_smoke.get("command")
    one_shot_pipeline_smoke_has_command = bool(one_shot_pipeline_smoke_command)
    integration_ready_to_run_live_smoke = (
        api_key_integration_status_summary.get("ready_to_run_live_smoke") is True
    )
    one_shot_pipeline_smoke_ready_to_run = (
        integration_ready_to_run_live_smoke and one_shot_pipeline_smoke_has_command
    )
    one_shot_pipeline_smoke_network_call = (
        one_shot_pipeline_smoke.get("network_call") is True
    )
    one_shot_pipeline_smoke_status = "unavailable"
    if one_shot_pipeline_smoke_ready_to_run:
        one_shot_pipeline_smoke_status = "ready"
    elif one_shot_pipeline_smoke_has_command:
        one_shot_pipeline_smoke_status = "blocked"
    one_shot_pipeline_smoke_blocked_reason = None
    if one_shot_pipeline_smoke_status == "unavailable":
        one_shot_pipeline_smoke_blocked_reason = "command_unavailable"
    elif (
        one_shot_pipeline_smoke_status == "blocked"
        and one_shot_pipeline_smoke_network_call
    ):
        one_shot_pipeline_smoke_blocked_reason = "api_key_setup_not_ready"
    elif one_shot_pipeline_smoke_status == "blocked":
        one_shot_pipeline_smoke_blocked_reason = "live_smoke_not_ready"
    one_shot_pipeline_smoke_unblock_action_name = None
    one_shot_pipeline_smoke_unblock_command = None
    one_shot_pipeline_smoke_unblock_network_call = False
    one_shot_pipeline_smoke_unblock_mutates_local_state = False
    one_shot_pipeline_smoke_unblock_secret_values_returned = False
    if one_shot_pipeline_smoke_blocked_reason == "api_key_setup_not_ready":
        one_shot_pipeline_smoke_unblock_action_name = (
            api_key_integration_status_summary.get("next_action_name")
            or api_key_next_action_summary.get("next_action_name")
        )
        one_shot_pipeline_smoke_unblock_command = next_action_command
        one_shot_pipeline_smoke_unblock_network_call = (
            api_key_next_action_summary.get("next_action_network_call") is True
        )
        one_shot_pipeline_smoke_unblock_mutates_local_state = (
            api_key_next_action_summary.get("next_action_mutates_local_state")
            is True
        )
        one_shot_pipeline_smoke_unblock_secret_values_returned = (
            api_key_next_action_summary.get("secret_values_returned") is True
        )
    next_provider_smoke_command = (
        api_key_integration_status_summary.get(
            "next_action_next_provider_smoke_command"
        )
        or next_provider_smoke.get("command")
    )
    next_provider_smoke_status = (
        api_key_integration_status_summary.get(
            "next_action_next_provider_smoke_status"
        )
        or next_provider_smoke.get("status")
    )
    next_provider_smoke_expected_live_checks = (
        _string_list(
            api_key_integration_status_summary.get(
                "next_action_next_provider_smoke_expected_live_checks"
            )
        )
        or _string_list(next_provider_smoke.get("expected_live_checks"))
    )
    next_provider_smoke_accepted_env_keys = (
        _string_list(
            api_key_integration_status_summary.get(
                "next_action_next_provider_smoke_accepted_env_keys"
            )
        )
        or _string_list(next_provider_smoke.get("accepted_env_keys"))
    )
    next_provider_smoke_has_command = bool(next_provider_smoke_command)
    next_provider_smoke_ready_to_run = (
        next_provider_smoke_status == "ready" and next_provider_smoke_has_command
    )
    next_provider_smoke_requires_api_keys = (
        next_provider_smoke_status != "ready"
        and bool(next_provider_smoke_accepted_env_keys)
    )
    next_action_status = api_key_next_action_summary.get("next_action_status")
    next_action_expected_live_checks = _string_list(
        api_key_next_action_summary.get("next_action_expected_live_checks")
    )
    next_action_accepted_env_keys = _string_list(
        api_key_next_action_summary.get("accepted_env_keys")
    )
    next_action_required_env_keys = _string_list(
        api_key_next_action_summary.get("required_env_keys")
    )
    next_action_has_command = bool(next_action_command)
    next_action_ready_to_run = (
        next_action_status == "ready" and next_action_has_command
    )
    next_action_requires_api_keys = (
        next_action_status != "ready" and bool(next_action_accepted_env_keys)
    )
    return {
        "api_key_integration_status": (
            api_key_integration_status_summary.get("status")
        ),
        "api_key_integration_api_keys_configured": (
            api_key_integration_status_summary.get("api_keys_configured") is True
        ),
        "api_key_integration_dotenv_loading_enabled": (
            api_key_integration_status_summary.get("dotenv_loading_enabled")
            is True
        ),
        "api_key_integration_dotenv_target_exists": (
            api_key_integration_status_summary.get("dotenv_target_exists") is True
        ),
        "api_key_integration_live_providers_selected": (
            api_key_integration_status_summary.get("live_providers_selected")
            is True
        ),
        "api_key_integration_ready_to_run_live_smoke": (
            integration_ready_to_run_live_smoke
        ),
        "api_key_integration_one_shot_pipeline_smoke_name": (
            one_shot_pipeline_smoke.get("name")
        ),
        "api_key_integration_one_shot_pipeline_smoke_command": (
            one_shot_pipeline_smoke_command
        ),
        "api_key_integration_one_shot_pipeline_smoke_status": (
            one_shot_pipeline_smoke_status
        ),
        "api_key_integration_one_shot_pipeline_smoke_blocked_reason": (
            one_shot_pipeline_smoke_blocked_reason
        ),
        "api_key_integration_one_shot_pipeline_smoke_unblock_action_name": (
            one_shot_pipeline_smoke_unblock_action_name
        ),
        "api_key_integration_one_shot_pipeline_smoke_unblock_command": (
            one_shot_pipeline_smoke_unblock_command
        ),
        "api_key_integration_one_shot_pipeline_smoke_unblock_network_call": (
            one_shot_pipeline_smoke_unblock_network_call
        ),
        "api_key_integration_one_shot_pipeline_smoke_unblock_mutates_local_state": (
            one_shot_pipeline_smoke_unblock_mutates_local_state
        ),
        "api_key_integration_one_shot_pipeline_smoke_unblock_secret_values_returned": (
            one_shot_pipeline_smoke_unblock_secret_values_returned
        ),
        "api_key_integration_one_shot_pipeline_smoke_has_command": (
            one_shot_pipeline_smoke_has_command
        ),
        "api_key_integration_one_shot_pipeline_smoke_ready_to_run": (
            one_shot_pipeline_smoke_ready_to_run
        ),
        "api_key_integration_one_shot_pipeline_smoke_requires_api_keys": (
            one_shot_pipeline_smoke_network_call
            and not one_shot_pipeline_smoke_ready_to_run
        ),
        "api_key_integration_one_shot_pipeline_smoke_network_call": (
            one_shot_pipeline_smoke_network_call
        ),
        "api_key_integration_one_shot_pipeline_smoke_network_call_policy": (
            one_shot_pipeline_smoke.get("network_call_policy")
        ),
        "api_key_integration_one_shot_pipeline_smoke_mutates_local_state": (
            one_shot_pipeline_smoke.get("mutates_local_state") is True
        ),
        "api_key_integration_one_shot_pipeline_smoke_secret_values_returned": (
            one_shot_pipeline_smoke.get("secret_values_returned") is True
        ),
        "api_key_integration_provider_smoke_count": (
            api_key_integration_status_summary.get("provider_smoke_count")
        ),
        "api_key_integration_ready_provider_smoke_count": (
            api_key_integration_status_summary.get("ready_provider_smoke_count")
        ),
        "api_key_integration_blocked_provider_smoke_count": (
            api_key_integration_status_summary.get("blocked_provider_smoke_count")
        ),
        "api_key_integration_configured_provider_families": _string_list(
            api_key_integration_status_summary.get(
                "configured_provider_families"
            )
        ),
        "api_key_integration_missing_provider_families": _string_list(
            api_key_integration_status_summary.get("missing_provider_families")
        ),
        "api_key_integration_selected_provider_classes": _string_list(
            api_key_integration_status_summary.get("selected_provider_classes")
        ),
        "api_key_integration_selected_provider_class_by_family": (
            _optional_mapping(
                api_key_integration_status_summary.get(
                    "selected_provider_class_by_family"
                )
            )
            or {}
        ),
        "api_key_integration_provider_route_data_mode_by_family": (
            _optional_mapping(
                api_key_integration_status_summary.get(
                    "provider_route_data_mode_by_family"
                )
            )
            or {}
        ),
        "api_key_integration_provider_route_live_data_required_by_family": (
            _optional_mapping(
                api_key_integration_status_summary.get(
                    "provider_route_live_data_required_by_family"
                )
            )
            or {}
        ),
        "api_key_integration_all_selected_routes_live": (
            api_key_integration_status_summary.get("all_selected_routes_live")
            is True
        ),
        **_api_key_integration_status_route_count_top_level_fields(
            api_key_integration_status_summary
        ),
        "api_key_integration_next_action_name": (
            api_key_integration_status_summary.get("next_action_name")
        ),
        "api_key_integration_next_action_status": next_action_status,
        "api_key_integration_next_action_command": next_action_command,
        "api_key_integration_next_action_has_command": next_action_has_command,
        "api_key_integration_next_action_ready_to_run": next_action_ready_to_run,
        "api_key_integration_next_action_requires_api_keys": (
            next_action_requires_api_keys
        ),
        "api_key_integration_next_action_next_after_action": (
            next_operator_action.get("next_after_action")
        ),
        "api_key_integration_next_action_dotenv_target_path": (
            next_operator_action.get("dotenv_target_path")
        ),
        "api_key_integration_next_action_source_path": (
            next_operator_action.get("source_path")
        ),
        "api_key_integration_next_action_target_path": (
            next_operator_action.get("target_path")
        ),
        "api_key_integration_next_action_provider_family": (
            api_key_integration_status_summary.get(
                "next_action_provider_family"
            )
        ),
        "api_key_integration_next_action_provider": (
            api_key_integration_status_summary.get("next_action_provider")
        ),
        "api_key_integration_next_action_selected_provider_class": (
            api_key_integration_status_summary.get(
                "next_action_selected_provider_class"
            )
        ),
        "api_key_integration_next_action_provider_route_data_mode": (
            api_key_integration_status_summary.get(
                "next_action_provider_route_data_mode"
            )
        ),
        "api_key_integration_next_action_provider_route_live_data_required": (
            api_key_integration_status_summary.get(
                "next_action_provider_route_live_data_required"
            )
            is True
        ),
        "api_key_integration_next_action_smoke_command_name": (
            api_key_integration_status_summary.get(
                "next_action_smoke_command_name"
            )
        ),
        "api_key_integration_next_action_is_recovery": (
            api_key_integration_status_summary.get("next_action_is_recovery")
            is True
        ),
        "api_key_integration_next_action_network_call": (
            api_key_integration_status_summary.get("next_action_network_call")
            is True
        ),
        "api_key_integration_next_action_network_call_policy": (
            next_operator_action.get("network_call_policy")
        ),
        "api_key_integration_next_action_preferred_env_key": (
            api_key_next_action_summary.get("preferred_env_key")
        ),
        "api_key_integration_next_action_accepted_env_keys": (
            next_action_accepted_env_keys
        ),
        "api_key_integration_next_action_accepted_env_key_count": len(
            next_action_accepted_env_keys
        ),
        "api_key_integration_next_action_required_env_keys": (
            next_action_required_env_keys
        ),
        "api_key_integration_next_action_required_env_key_count": len(
            next_action_required_env_keys
        ),
        "api_key_integration_next_action_expected_live_contract": (
            api_key_next_action_summary.get("next_action_expected_live_contract")
        ),
        "api_key_integration_next_action_expected_live_checks": (
            next_action_expected_live_checks
        ),
        "api_key_integration_next_action_expected_live_check_count": len(
            next_action_expected_live_checks
        ),
        "api_key_integration_next_action_mutates_local_state": (
            api_key_next_action_summary.get("next_action_mutates_local_state")
            is True
        ),
        "api_key_integration_next_action_secret_values_returned": (
            api_key_next_action_summary.get("secret_values_returned") is True
        ),
        "api_key_integration_next_action_secret_input_required": (
            next_operator_action.get("secret_input_required") is True
        ),
        "api_key_integration_next_action_dotenv_examples": _string_list(
            api_key_next_action_summary.get("dotenv_examples")
        ),
        "api_key_integration_next_action_dotenv_example_count": (
            api_key_next_action_summary.get("dotenv_example_count")
        ),
        "api_key_integration_next_action_provider_smoke_count": (
            next_operator_action.get("provider_smoke_count")
        ),
        "api_key_integration_next_action_ready_provider_smoke_count": (
            next_operator_action.get("ready_provider_smoke_count")
        ),
        "api_key_integration_next_action_blocked_provider_smoke_count": (
            next_operator_action.get("blocked_provider_smoke_count")
        ),
        "api_key_integration_next_action_next_provider_smoke_command_name": (
            api_key_integration_status_summary.get(
                "next_action_next_provider_smoke_command_name"
            )
            or next_operator_action.get("next_provider_smoke_command_name")
            or next_provider_smoke.get("smoke_command_name")
        ),
        "api_key_integration_next_action_next_provider_smoke_command": (
            next_provider_smoke_command
        ),
        "api_key_integration_next_action_next_provider_smoke_has_command": (
            next_provider_smoke_has_command
        ),
        "api_key_integration_next_action_next_provider_smoke_ready_to_run": (
            next_provider_smoke_ready_to_run
        ),
        "api_key_integration_next_action_next_provider_smoke_requires_api_keys": (
            next_provider_smoke_requires_api_keys
        ),
        "api_key_integration_next_action_next_provider_smoke_next_setup_action": (
            api_key_integration_status_summary.get(
                "next_action_next_provider_smoke_next_setup_action"
            )
            or next_provider_smoke.get("next_setup_action")
        ),
        "api_key_integration_next_action_next_provider_smoke_provider_family": (
            api_key_integration_status_summary.get(
                "next_action_next_provider_smoke_provider_family"
            )
            or next_provider_smoke.get("provider_family")
        ),
        "api_key_integration_next_action_next_provider_smoke_provider": (
            api_key_integration_status_summary.get(
                "next_action_next_provider_smoke_provider"
            )
            or next_provider_smoke.get("provider")
        ),
        "api_key_integration_next_action_next_provider_smoke_selected_provider_class": (
            api_key_integration_status_summary.get(
                "next_action_next_provider_smoke_selected_provider_class"
            )
            or next_provider_smoke.get("selected_provider_class")
        ),
        "api_key_integration_next_action_next_provider_smoke_provider_route_data_mode": (
            api_key_integration_status_summary.get(
                "next_action_next_provider_smoke_provider_route_data_mode"
            )
            or next_provider_smoke.get("provider_route_data_mode")
        ),
        "api_key_integration_next_action_next_provider_smoke_provider_route_live_data_required": (
            api_key_integration_status_summary.get(
                "next_action_next_provider_smoke_provider_route_live_data_required"
            )
            is True
            or next_provider_smoke.get("provider_route_live_data_required") is True
        ),
        "api_key_integration_next_action_next_provider_smoke_status": (
            next_provider_smoke_status
        ),
        "api_key_integration_next_action_next_provider_smoke_network_call": (
            _bool_from_status_or_provider(
                api_key_integration_status_summary,
                "next_action_next_provider_smoke_network_call",
                next_provider_smoke,
                "network_call",
            )
        ),
        "api_key_integration_next_action_next_provider_smoke_network_call_policy": (
            api_key_integration_status_summary.get(
                "next_action_next_provider_smoke_network_call_policy"
            )
            or next_provider_smoke.get("network_call_policy")
        ),
        "api_key_integration_next_action_next_provider_smoke_expected_live_contract": (
            api_key_integration_status_summary.get(
                "next_action_next_provider_smoke_expected_live_contract"
            )
            or next_provider_smoke.get("expected_live_contract")
        ),
        "api_key_integration_next_action_next_provider_smoke_expected_live_checks": (
            next_provider_smoke_expected_live_checks
        ),
        "api_key_integration_next_action_next_provider_smoke_expected_live_check_count": (
            len(next_provider_smoke_expected_live_checks)
        ),
        "api_key_integration_next_action_next_provider_smoke_preferred_env_key": (
            api_key_integration_status_summary.get(
                "next_action_next_provider_smoke_preferred_env_key"
            )
            or next_provider_smoke.get("preferred_env_key")
        ),
        "api_key_integration_next_action_next_provider_smoke_accepted_env_keys": (
            next_provider_smoke_accepted_env_keys
        ),
        "api_key_integration_next_action_next_provider_smoke_accepted_env_key_count": (
            len(next_provider_smoke_accepted_env_keys)
        ),
        "api_key_integration_next_action_next_provider_smoke_mutates_local_state": (
            api_key_integration_status_summary.get(
                "next_action_next_provider_smoke_mutates_local_state"
            )
            is True
            or next_provider_smoke.get("mutates_local_state") is True
        ),
        "api_key_integration_next_action_next_provider_smoke_secret_values_returned": (
            _bool_from_status_or_provider(
                api_key_integration_status_summary,
                "next_action_next_provider_smoke_secret_values_returned",
                next_provider_smoke,
                "secret_values_returned",
            )
        ),
    }
