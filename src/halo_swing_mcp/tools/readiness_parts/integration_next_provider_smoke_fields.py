"""API-key integration next-provider-smoke summary field projection."""

from __future__ import annotations

from typing import Any

from .live_data_setup import _string_list


__all__ = ("_api_key_integration_next_provider_smoke_fields",)


def _api_key_integration_next_provider_smoke_fields(
    next_provider_smoke: dict[str, Any],
) -> dict[str, Any]:
    summary: dict[str, Any] = {}
    selected_provider_class = next_provider_smoke.get("selected_provider_class")
    provider_route_data_mode = next_provider_smoke.get("provider_route_data_mode")
    expected_live_contract = next_provider_smoke.get("expected_live_contract")
    expected_live_checks = _string_list(
        next_provider_smoke.get("expected_live_checks")
    )
    accepted_env_keys = _string_list(next_provider_smoke.get("accepted_env_keys"))

    if isinstance(next_provider_smoke.get("smoke_command_name"), str):
        summary["next_action_next_provider_smoke_command_name"] = (
            next_provider_smoke.get("smoke_command_name")
        )
    if isinstance(next_provider_smoke.get("command"), str):
        summary["next_action_next_provider_smoke_command"] = (
            next_provider_smoke.get("command")
        )
    if isinstance(next_provider_smoke.get("provider_family"), str):
        summary["next_action_next_provider_smoke_provider_family"] = (
            next_provider_smoke.get("provider_family")
        )
    if isinstance(next_provider_smoke.get("provider"), str):
        summary["next_action_next_provider_smoke_provider"] = (
            next_provider_smoke.get("provider")
        )
    if isinstance(selected_provider_class, str):
        summary["next_action_next_provider_smoke_selected_provider_class"] = (
            selected_provider_class
        )
    if isinstance(provider_route_data_mode, str):
        summary["next_action_next_provider_smoke_provider_route_data_mode"] = (
            provider_route_data_mode
        )
    if isinstance(next_provider_smoke.get("provider_family"), str):
        summary["next_action_next_provider_smoke_provider_route_live_data_required"] = (
            next_provider_smoke.get("provider_route_live_data_required") is True
        )
        summary["next_action_next_provider_smoke_mutates_local_state"] = (
            next_provider_smoke.get("mutates_local_state") is True
        )
    if isinstance(next_provider_smoke.get("status"), str):
        summary["next_action_next_provider_smoke_status"] = (
            next_provider_smoke.get("status")
        )
    if "network_call" in next_provider_smoke:
        summary["next_action_next_provider_smoke_network_call"] = (
            next_provider_smoke.get("network_call") is True
        )
    if isinstance(next_provider_smoke.get("network_call_policy"), str):
        summary["next_action_next_provider_smoke_network_call_policy"] = (
            next_provider_smoke.get("network_call_policy")
        )
    if isinstance(expected_live_contract, str):
        summary["next_action_next_provider_smoke_expected_live_contract"] = (
            expected_live_contract
        )
    if expected_live_checks:
        summary["next_action_next_provider_smoke_expected_live_checks"] = (
            expected_live_checks
        )
    if isinstance(next_provider_smoke.get("preferred_env_key"), str):
        summary["next_action_next_provider_smoke_preferred_env_key"] = (
            next_provider_smoke.get("preferred_env_key")
        )
    if accepted_env_keys:
        summary["next_action_next_provider_smoke_accepted_env_keys"] = (
            accepted_env_keys
        )
    if "secret_values_returned" in next_provider_smoke:
        summary["next_action_next_provider_smoke_secret_values_returned"] = (
            next_provider_smoke.get("secret_values_returned") is True
        )
    return summary
