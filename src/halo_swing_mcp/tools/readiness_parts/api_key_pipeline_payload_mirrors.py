# ruff: noqa: F403,F405,F821
"""API-key pipeline top-level payload mirror projections."""

from __future__ import annotations

from .context import *
from .live_data_setup import _string_list
from .summary_only_provider_route_fields import (
    _api_key_failure_route_top_level_fields,
    _api_key_provider_recovery_route_top_level_fields,
)


__all__ = (
    "_api_key_failure_top_level_fields",
    "_api_key_provider_recovery_top_level_fields",
)


def _api_key_failure_top_level_fields(
    api_key_pipeline_failure_summary: dict[str, Any],
) -> dict[str, Any]:
    return {
        "api_key_failure_status": api_key_pipeline_failure_summary.get(
            "status"
        ),
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
        "api_key_failure_next_action_name": (
            api_key_pipeline_failure_summary.get("next_action_name")
        ),
        "api_key_failure_next_action_command": (
            api_key_pipeline_failure_summary.get("next_action_command")
        ),
        "api_key_failure_next_action_provider_family": (
            api_key_pipeline_failure_summary.get("next_action_provider_family")
        ),
        "api_key_failure_next_action_provider": (
            api_key_pipeline_failure_summary.get("next_action_provider")
        ),
        "api_key_failure_next_action_smoke_command_name": (
            api_key_pipeline_failure_summary.get(
                "next_action_smoke_command_name"
            )
        ),
        "api_key_failure_next_action_expected_live_contract": (
            api_key_pipeline_failure_summary.get(
                "next_action_expected_live_contract"
            )
        ),
        "api_key_failure_next_action_expected_live_checks": _string_list(
            api_key_pipeline_failure_summary.get(
                "next_action_expected_live_checks"
            )
        ),
        "api_key_failure_next_action_is_recovery": (
            api_key_pipeline_failure_summary.get("next_action_is_recovery")
            is True
        ),
        "api_key_failure_provider_recovery_required": (
            api_key_pipeline_failure_summary.get("provider_recovery_required")
            is True
        ),
        "api_key_failure_provider_recovery_item_count": (
            api_key_pipeline_failure_summary.get("provider_recovery_item_count")
        ),
        "api_key_failure_preferred_env_key": (
            api_key_pipeline_failure_summary.get("preferred_env_key")
        ),
        "api_key_failure_accepted_env_keys": _string_list(
            api_key_pipeline_failure_summary.get("accepted_env_keys")
        ),
        **_api_key_failure_route_top_level_fields(
            api_key_pipeline_failure_summary
        ),
        "api_key_failure_network_call": (
            api_key_pipeline_failure_summary.get("network_call") is True
        ),
        "api_key_failure_mutates_local_state": (
            api_key_pipeline_failure_summary.get("mutates_local_state") is True
        ),
        "api_key_failure_secret_values_returned": (
            api_key_pipeline_failure_summary.get("secret_values_returned")
            is True
        ),
    }


def _api_key_provider_recovery_top_level_fields(
    api_key_provider_recovery_summary: dict[str, Any],
) -> dict[str, Any]:
    return {
        "provider_recovery_required": (
            api_key_provider_recovery_summary.get("provider_recovery_required")
            is True
        ),
        **_api_key_provider_recovery_route_top_level_fields(
            api_key_provider_recovery_summary
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
        "next_pending_recovery_selected_provider_class": (
            api_key_provider_recovery_summary.get(
                "next_pending_recovery_selected_provider_class"
            )
        ),
        "next_pending_recovery_provider_route_data_mode": (
            api_key_provider_recovery_summary.get(
                "next_pending_recovery_provider_route_data_mode"
            )
        ),
        "next_pending_recovery_provider_route_live_data_required": (
            api_key_provider_recovery_summary.get(
                "next_pending_recovery_provider_route_live_data_required"
            )
            is True
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
        "next_blocked_recovery_selected_provider_class": (
            api_key_provider_recovery_summary.get(
                "next_blocked_recovery_selected_provider_class"
            )
        ),
        "next_blocked_recovery_provider_route_data_mode": (
            api_key_provider_recovery_summary.get(
                "next_blocked_recovery_provider_route_data_mode"
            )
        ),
        "next_blocked_recovery_provider_route_live_data_required": (
            api_key_provider_recovery_summary.get(
                "next_blocked_recovery_provider_route_live_data_required"
            )
            is True
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
        "next_recovery_selected_provider_class": (
            api_key_provider_recovery_summary.get(
                "next_recovery_selected_provider_class"
            )
        ),
        "next_recovery_provider_route_data_mode": (
            api_key_provider_recovery_summary.get(
                "next_recovery_provider_route_data_mode"
            )
        ),
        "next_recovery_provider_route_live_data_required": (
            api_key_provider_recovery_summary.get(
                "next_recovery_provider_route_live_data_required"
            )
            is True
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
    }
