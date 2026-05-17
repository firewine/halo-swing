"""Summary-only operator checklist top-level field projection."""

from __future__ import annotations

from typing import Any

from .contract_checks import _optional_mapping
from .live_data_setup import _string_list


__all__ = ("_api_key_operator_checklist_top_level_fields",)


def _api_key_operator_checklist_top_level_fields(
    api_key_operator_checklist_summary: dict[str, Any],
) -> dict[str, Any]:
    return {
        "api_key_operator_checklist_schema_version": (
            api_key_operator_checklist_summary.get("schema_version")
        ),
        "api_key_setup_status": api_key_operator_checklist_summary.get("status"),
        "api_key_setup_current_step": api_key_operator_checklist_summary.get(
            "current_step"
        ),
        "api_key_setup_ready": (
            api_key_operator_checklist_summary.get("ready") is True
        ),
        "api_key_setup_step_count": api_key_operator_checklist_summary.get(
            "step_count"
        ),
        "api_key_setup_ready_step_names": _string_list(
            api_key_operator_checklist_summary.get("ready_step_names")
        ),
        "api_key_setup_ready_step_count": (
            api_key_operator_checklist_summary.get("ready_step_count")
        ),
        "api_key_setup_blocking_step_names": _string_list(
            api_key_operator_checklist_summary.get("blocking_step_names")
        ),
        "api_key_setup_blocking_step_count": (
            api_key_operator_checklist_summary.get("blocking_step_count")
        ),
        "api_key_setup_next_blocking_step": (
            api_key_operator_checklist_summary.get("next_blocking_step")
        ),
        "api_key_setup_next_blocking_action_name": (
            api_key_operator_checklist_summary.get("next_blocking_action_name")
        ),
        "api_key_setup_next_blocking_action_status": (
            api_key_operator_checklist_summary.get("next_blocking_action_status")
        ),
        "api_key_setup_next_blocking_action_command": (
            api_key_operator_checklist_summary.get("next_blocking_action_command")
        ),
        "api_key_setup_next_blocking_action_network_call": (
            api_key_operator_checklist_summary.get(
                "next_blocking_action_network_call"
            )
            is True
        ),
        "api_key_setup_next_blocking_action_network_call_policy": (
            api_key_operator_checklist_summary.get(
                "next_blocking_action_network_call_policy"
            )
        ),
        "api_key_setup_next_blocking_action_mutates_local_state": (
            api_key_operator_checklist_summary.get(
                "next_blocking_action_mutates_local_state"
            )
            is True
        ),
        "api_key_setup_next_blocking_action_secret_values_returned": (
            api_key_operator_checklist_summary.get(
                "next_blocking_action_secret_values_returned"
            )
            is True
        ),
        "api_key_setup_next_blocking_action_provider_family": (
            api_key_operator_checklist_summary.get(
                "next_blocking_action_provider_family"
            )
        ),
        "api_key_setup_next_blocking_action_provider": (
            api_key_operator_checklist_summary.get("next_blocking_action_provider")
        ),
        "api_key_setup_next_blocking_action_smoke_command_name": (
            api_key_operator_checklist_summary.get(
                "next_blocking_action_smoke_command_name"
            )
        ),
        "api_key_setup_next_blocking_action_preferred_env_key": (
            api_key_operator_checklist_summary.get(
                "next_blocking_action_preferred_env_key"
            )
        ),
        "api_key_setup_next_blocking_action_accepted_env_keys": _string_list(
            api_key_operator_checklist_summary.get(
                "next_blocking_action_accepted_env_keys"
            )
        ),
        "api_key_operator_checklist_selected_provider_class_by_family": (
            _optional_mapping(
                api_key_operator_checklist_summary.get(
                    "selected_provider_class_by_family"
                )
            )
            or {}
        ),
        "api_key_operator_checklist_provider_route_data_mode_by_family": (
            _optional_mapping(
                api_key_operator_checklist_summary.get(
                    "provider_route_data_mode_by_family"
                )
            )
            or {}
        ),
        "api_key_operator_checklist_provider_route_live_data_required_by_family": (
            _optional_mapping(
                api_key_operator_checklist_summary.get(
                    "provider_route_live_data_required_by_family"
                )
            )
            or {}
        ),
        "api_key_operator_checklist_all_selected_routes_live": (
            api_key_operator_checklist_summary.get("all_selected_routes_live")
            is True
        ),
        "api_key_operator_checklist_network_call": (
            api_key_operator_checklist_summary.get("network_call") is True
        ),
        "api_key_operator_checklist_mutates_local_state": (
            api_key_operator_checklist_summary.get("mutates_local_state") is True
        ),
        "api_key_operator_checklist_secret_values_returned": (
            api_key_operator_checklist_summary.get("secret_values_returned")
            is True
        ),
    }
