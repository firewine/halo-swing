"""Summary-only next-provider-smoke top-level field projection."""

from __future__ import annotations

from typing import Any

from .live_data_setup import _ordered_unique_strings, _string_list


__all__ = ("_api_key_provider_smoke_top_level_fields",)


def _api_key_provider_smoke_top_level_fields(
    setup_status_summary: dict[str, Any],
    next_provider_smoke: dict[str, Any],
    provider_smoke_command_rows: list[dict[str, Any]],
    provider_smoke_command_count: int,
    provider_smoke_command_rows_by_family: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    return {
        "api_key_provider_smoke_total_count": setup_status_summary.get(
            "provider_smoke_count"
        ),
        "api_key_provider_smoke_ready_count": setup_status_summary.get(
            "ready_provider_smoke_count"
        ),
        "api_key_provider_smoke_blocked_count": setup_status_summary.get(
            "blocked_provider_smoke_count"
        ),
        "api_key_next_provider_smoke_command_name": (
            setup_status_summary.get("next_provider_smoke_command_name")
            or next_provider_smoke.get("smoke_command_name")
        ),
        "api_key_next_provider_smoke_provider_family": (
            next_provider_smoke.get("provider_family")
        ),
        "api_key_next_provider_smoke_provider": next_provider_smoke.get("provider"),
        "api_key_next_provider_smoke_command": next_provider_smoke.get("command"),
        "api_key_next_provider_smoke_status": next_provider_smoke.get("status"),
        "api_key_next_provider_smoke_network_call": (
            next_provider_smoke.get("network_call") is True
        ),
        "api_key_next_provider_smoke_network_call_policy": (
            next_provider_smoke.get("network_call_policy")
        ),
        "api_key_next_provider_smoke_expected_live_contract": (
            next_provider_smoke.get("expected_live_contract")
        ),
        "api_key_next_provider_smoke_expected_live_checks": _string_list(
            next_provider_smoke.get("expected_live_checks")
        ),
        "api_key_next_provider_smoke_preferred_env_key": (
            next_provider_smoke.get("preferred_env_key")
        ),
        "api_key_next_provider_smoke_accepted_env_keys": _string_list(
            next_provider_smoke.get("accepted_env_keys")
        ),
        "api_key_next_provider_smoke_mutates_local_state": (
            next_provider_smoke.get("mutates_local_state") is True
        ),
        "api_key_next_provider_smoke_secret_values_returned": (
            next_provider_smoke.get("secret_values_returned") is True
        ),
        "api_key_provider_smoke_command_count": provider_smoke_command_count,
        "api_key_provider_smoke_command_names": _ordered_unique_strings(
            [
                row.get("smoke_command_name")
                for row in provider_smoke_command_rows
            ]
        ),
        "api_key_provider_smoke_commands_by_family": {
            family: row.get("command")
            for family, row in provider_smoke_command_rows_by_family.items()
        },
        "api_key_provider_smoke_statuses_by_family": {
            family: row.get("status")
            for family, row in provider_smoke_command_rows_by_family.items()
        },
        "api_key_provider_smoke_network_call_policies_by_family": {
            family: row.get("network_call_policy")
            for family, row in provider_smoke_command_rows_by_family.items()
        },
        "api_key_provider_smoke_expected_live_contracts_by_family": {
            family: row.get("expected_live_contract")
            for family, row in provider_smoke_command_rows_by_family.items()
        },
        "api_key_provider_smoke_expected_live_checks_by_family": {
            family: _string_list(row.get("expected_live_checks"))
            for family, row in provider_smoke_command_rows_by_family.items()
        },
    }
