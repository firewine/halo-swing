"""Summary-only integration-status top-level field projection."""

from __future__ import annotations

from typing import Any

from .contract_checks import _optional_mapping
from .live_data_setup import _string_list


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
    api_key_integration_status_summary: dict[str, Any],
    api_key_next_action_summary: dict[str, Any],
    next_operator_action: dict[str, Any],
    next_provider_smoke: dict[str, Any],
) -> dict[str, Any]:
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
            api_key_integration_status_summary.get("ready_to_run_live_smoke")
            is True
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
        "api_key_integration_next_action_name": (
            api_key_integration_status_summary.get("next_action_name")
        ),
        "api_key_integration_next_action_status": (
            api_key_next_action_summary.get("next_action_status")
        ),
        "api_key_integration_next_action_command": (
            api_key_next_action_summary.get("next_action_command")
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
        "api_key_integration_next_action_accepted_env_keys": _string_list(
            api_key_next_action_summary.get("accepted_env_keys")
        ),
        "api_key_integration_next_action_required_env_keys": _string_list(
            api_key_next_action_summary.get("required_env_keys")
        ),
        "api_key_integration_next_action_expected_live_contract": (
            api_key_next_action_summary.get("next_action_expected_live_contract")
        ),
        "api_key_integration_next_action_expected_live_checks": _string_list(
            api_key_next_action_summary.get("next_action_expected_live_checks")
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
            api_key_integration_status_summary.get(
                "next_action_next_provider_smoke_command"
            )
            or next_provider_smoke.get("command")
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
            api_key_integration_status_summary.get(
                "next_action_next_provider_smoke_status"
            )
            or next_provider_smoke.get("status")
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
            _string_list(
                api_key_integration_status_summary.get(
                    "next_action_next_provider_smoke_expected_live_checks"
                )
            )
            or _string_list(next_provider_smoke.get("expected_live_checks"))
        ),
        "api_key_integration_next_action_next_provider_smoke_preferred_env_key": (
            api_key_integration_status_summary.get(
                "next_action_next_provider_smoke_preferred_env_key"
            )
            or next_provider_smoke.get("preferred_env_key")
        ),
        "api_key_integration_next_action_next_provider_smoke_accepted_env_keys": (
            _string_list(
                api_key_integration_status_summary.get(
                    "next_action_next_provider_smoke_accepted_env_keys"
                )
            )
            or _string_list(next_provider_smoke.get("accepted_env_keys"))
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
