"""Summary-only API-key setup quickstart field projection."""

from __future__ import annotations

from typing import Any

from .live_data_setup import _ordered_unique_strings, _string_list
from .summary_only_provider_route_fields import (
    _api_key_quickstart_command_plan_route_count_top_level_fields,
)


__all__ = ("_api_key_setup_quickstart_top_level_fields",)


def _api_key_setup_quickstart_top_level_fields(
    *,
    setup_quickstart_rows: list[dict[str, Any]],
    api_key_operator_checklist_summary: dict[str, Any],
    quickstart_command_plan: list[dict[str, Any]],
    next_quickstart_command_plan_item: dict[str, Any] | None,
    next_quickstart_command_plan_row: dict[str, Any],
) -> dict[str, Any]:
    return {
        "api_key_setup_quickstart_steps": setup_quickstart_rows,
        "api_key_setup_quickstart_step_names": _ordered_unique_strings(
            [row.get("name") for row in setup_quickstart_rows]
        ),
        "api_key_setup_quickstart_step_count": len(setup_quickstart_rows),
        "api_key_setup_quickstart_next_step": (
            api_key_operator_checklist_summary.get("next_blocking_step")
        ),
        "api_key_setup_quickstart_next_command": (
            api_key_operator_checklist_summary.get("next_blocking_action_command")
        ),
        "api_key_setup_quickstart_command_plan": quickstart_command_plan,
        "api_key_setup_quickstart_command_plan_names": _string_list(
            [row.get("name") for row in quickstart_command_plan]
        ),
        "api_key_setup_quickstart_command_plan_count": len(
            quickstart_command_plan
        ),
        **_api_key_setup_quickstart_command_plan_family_fields(
            quickstart_command_plan
        ),
        "api_key_setup_quickstart_next_command_plan_item": (
            next_quickstart_command_plan_item
        ),
        **_api_key_setup_quickstart_next_command_plan_fields(
            next_quickstart_command_plan_row
        ),
    }


def _api_key_setup_quickstart_command_plan_family_fields(
    quickstart_command_plan: list[dict[str, Any]],
) -> dict[str, Any]:
    provider_rows = [
        row
        for row in quickstart_command_plan
        if isinstance(row.get("provider_family"), str)
    ]
    provider_families = _ordered_unique_strings(
        [row.get("provider_family") for row in provider_rows]
    )
    ready_provider_families = _ordered_unique_strings(
        [
            row.get("provider_family")
            for row in provider_rows
            if row.get("status") == "ready"
        ]
    )
    blocked_provider_families = _ordered_unique_strings(
        [
            row.get("provider_family")
            for row in provider_rows
            if row.get("status") != "ready"
        ]
    )
    ready_rows = [row for row in provider_rows if row.get("status") == "ready"]
    blocked_rows = [row for row in provider_rows if row.get("status") != "ready"]
    next_ready_row = ready_rows[0] if ready_rows else {}
    next_blocked_row = blocked_rows[0] if blocked_rows else {}
    provider_smoke_count = len(provider_rows)
    ready_provider_smoke_count = sum(
        row.get("status") == "ready" for row in provider_rows
    )
    has_provider_smokes = provider_smoke_count > 0
    selected_provider_class_by_family = {
        row["provider_family"]: row.get("selected_provider_class")
        for row in provider_rows
    }
    provider_route_data_mode_by_family = {
        row["provider_family"]: row.get("provider_route_data_mode")
        for row in provider_rows
    }
    provider_route_live_data_required_by_family = {
        row["provider_family"]: (
            row.get("provider_route_live_data_required") is True
        )
        for row in provider_rows
    }
    provider_route_summary = {
        "selected_provider_class_by_family": selected_provider_class_by_family,
        "provider_route_data_mode_by_family": provider_route_data_mode_by_family,
        "provider_route_live_data_required_by_family": (
            provider_route_live_data_required_by_family
        ),
    }
    expected_live_check_counts_by_family = {
        row["provider_family"]: len(_string_list(row.get("expected_live_checks")))
        for row in provider_rows
    }
    accepted_env_key_counts_by_family = {
        row["provider_family"]: len(_string_list(row.get("accepted_env_keys")))
        for row in provider_rows
    }
    return {
        "api_key_setup_quickstart_command_plan_provider_families": (
            provider_families
        ),
        "api_key_setup_quickstart_command_plan_provider_family_count": len(
            provider_families
        ),
        "api_key_setup_quickstart_command_plan_ready_provider_families": (
            ready_provider_families
        ),
        "api_key_setup_quickstart_command_plan_blocked_provider_families": (
            blocked_provider_families
        ),
        "api_key_setup_quickstart_command_plan_ready_command_names": (
            _string_list([row.get("name") for row in ready_rows])
        ),
        "api_key_setup_quickstart_command_plan_ready_commands": (
            _string_list([row.get("command") for row in ready_rows])
        ),
        "api_key_setup_quickstart_command_plan_blocked_command_names": (
            _string_list([row.get("name") for row in blocked_rows])
        ),
        "api_key_setup_quickstart_command_plan_blocked_commands": (
            _string_list([row.get("command") for row in blocked_rows])
        ),
        "api_key_setup_quickstart_command_plan_next_ready_provider_smoke_provider_family": (
            next_ready_row.get("provider_family")
        ),
        "api_key_setup_quickstart_command_plan_next_ready_provider_smoke_provider": (
            next_ready_row.get("provider")
        ),
        "api_key_setup_quickstart_command_plan_next_ready_provider_smoke_selected_provider_class": (
            next_ready_row.get("selected_provider_class")
        ),
        "api_key_setup_quickstart_command_plan_next_ready_provider_smoke_provider_route_data_mode": (
            next_ready_row.get("provider_route_data_mode")
        ),
        "api_key_setup_quickstart_command_plan_next_ready_provider_smoke_provider_route_live_data_required": (
            next_ready_row.get("provider_route_live_data_required") is True
        ),
        "api_key_setup_quickstart_command_plan_next_ready_provider_smoke_command_name": (
            next_ready_row.get("name")
        ),
        "api_key_setup_quickstart_command_plan_next_ready_provider_smoke_command": (
            next_ready_row.get("command")
        ),
        "api_key_setup_quickstart_command_plan_next_ready_provider_smoke_expected_live_contract": (
            next_ready_row.get("expected_live_contract")
        ),
        "api_key_setup_quickstart_command_plan_next_ready_provider_smoke_expected_live_checks": (
            _string_list(next_ready_row.get("expected_live_checks"))
        ),
        "api_key_setup_quickstart_command_plan_next_ready_provider_smoke_preferred_env_key": (
            next_ready_row.get("preferred_env_key")
        ),
        "api_key_setup_quickstart_command_plan_next_ready_provider_smoke_accepted_env_keys": (
            _string_list(next_ready_row.get("accepted_env_keys"))
        ),
        "api_key_setup_quickstart_command_plan_next_ready_provider_smoke_next_setup_action": (
            next_ready_row.get("next_setup_action")
        ),
        "api_key_setup_quickstart_command_plan_next_ready_provider_smoke_status": (
            next_ready_row.get("status")
        ),
        "api_key_setup_quickstart_command_plan_next_ready_provider_smoke_network_call": (
            next_ready_row.get("network_call") is True
        ),
        "api_key_setup_quickstart_command_plan_next_ready_provider_smoke_network_call_policy": (
            next_ready_row.get("network_call_policy")
        ),
        "api_key_setup_quickstart_command_plan_next_ready_provider_smoke_mutates_local_state": (
            next_ready_row.get("mutates_local_state") is True
        ),
        "api_key_setup_quickstart_command_plan_next_ready_provider_smoke_secret_values_returned": (
            next_ready_row.get("secret_values_returned") is True
        ),
        "api_key_setup_quickstart_command_plan_next_blocked_provider_smoke_provider_family": (
            next_blocked_row.get("provider_family")
        ),
        "api_key_setup_quickstart_command_plan_next_blocked_provider_smoke_provider": (
            next_blocked_row.get("provider")
        ),
        "api_key_setup_quickstart_command_plan_next_blocked_provider_smoke_selected_provider_class": (
            next_blocked_row.get("selected_provider_class")
        ),
        "api_key_setup_quickstart_command_plan_next_blocked_provider_smoke_provider_route_data_mode": (
            next_blocked_row.get("provider_route_data_mode")
        ),
        "api_key_setup_quickstart_command_plan_next_blocked_provider_smoke_provider_route_live_data_required": (
            next_blocked_row.get("provider_route_live_data_required") is True
        ),
        "api_key_setup_quickstart_command_plan_next_blocked_provider_smoke_command_name": (
            next_blocked_row.get("name")
        ),
        "api_key_setup_quickstart_command_plan_next_blocked_provider_smoke_command": (
            next_blocked_row.get("command")
        ),
        "api_key_setup_quickstart_command_plan_next_blocked_provider_smoke_expected_live_contract": (
            next_blocked_row.get("expected_live_contract")
        ),
        "api_key_setup_quickstart_command_plan_next_blocked_provider_smoke_expected_live_checks": (
            _string_list(next_blocked_row.get("expected_live_checks"))
        ),
        "api_key_setup_quickstart_command_plan_next_blocked_provider_smoke_preferred_env_key": (
            next_blocked_row.get("preferred_env_key")
        ),
        "api_key_setup_quickstart_command_plan_next_blocked_provider_smoke_accepted_env_keys": (
            _string_list(next_blocked_row.get("accepted_env_keys"))
        ),
        "api_key_setup_quickstart_command_plan_next_blocked_provider_smoke_next_setup_action": (
            next_blocked_row.get("next_setup_action")
        ),
        "api_key_setup_quickstart_command_plan_next_blocked_provider_smoke_status": (
            next_blocked_row.get("status")
        ),
        "api_key_setup_quickstart_command_plan_next_blocked_provider_smoke_network_call": (
            next_blocked_row.get("network_call") is True
        ),
        "api_key_setup_quickstart_command_plan_next_blocked_provider_smoke_network_call_policy": (
            next_blocked_row.get("network_call_policy")
        ),
        "api_key_setup_quickstart_command_plan_next_blocked_provider_smoke_mutates_local_state": (
            next_blocked_row.get("mutates_local_state") is True
        ),
        "api_key_setup_quickstart_command_plan_next_blocked_provider_smoke_secret_values_returned": (
            next_blocked_row.get("secret_values_returned") is True
        ),
        "api_key_setup_quickstart_command_plan_ready_provider_smoke_count": (
            ready_provider_smoke_count
        ),
        "api_key_setup_quickstart_command_plan_blocked_provider_smoke_count": (
            provider_smoke_count - ready_provider_smoke_count
        ),
        "api_key_setup_quickstart_command_plan_all_provider_smokes_ready": (
            has_provider_smokes
            and ready_provider_smoke_count == provider_smoke_count
        ),
        "api_key_setup_quickstart_command_plan_all_provider_smokes_network_calls": (
            has_provider_smokes
            and all(row.get("network_call") is True for row in provider_rows)
        ),
        "api_key_setup_quickstart_command_plan_all_provider_smokes_live_required": (
            has_provider_smokes
            and all(
                row.get("provider_route_live_data_required") is True
                for row in provider_rows
            )
        ),
        "api_key_setup_quickstart_command_plan_any_provider_smoke_mutates_local_state": (
            any(row.get("mutates_local_state") is True for row in provider_rows)
        ),
        "api_key_setup_quickstart_command_plan_any_provider_smoke_secret_values_returned": (
            any(row.get("secret_values_returned") is True for row in provider_rows)
        ),
        "api_key_setup_quickstart_command_plan_kinds_by_family": {
            row["provider_family"]: row.get("kind")
            for row in provider_rows
        },
        "api_key_setup_quickstart_command_plan_command_names_by_family": {
            row["provider_family"]: row.get("name")
            for row in provider_rows
        },
        "api_key_setup_quickstart_command_plan_commands_by_family": {
            row["provider_family"]: row.get("command")
            for row in provider_rows
        },
        "api_key_setup_quickstart_command_plan_provider_by_family": {
            row["provider_family"]: row.get("provider")
            for row in provider_rows
        },
        "api_key_setup_quickstart_command_plan_selected_provider_class_by_family": (
            selected_provider_class_by_family
        ),
        "api_key_setup_quickstart_command_plan_provider_route_data_mode_by_family": (
            provider_route_data_mode_by_family
        ),
        "api_key_setup_quickstart_command_plan_provider_route_live_data_required_by_family": (
            provider_route_live_data_required_by_family
        ),
        **_api_key_quickstart_command_plan_route_count_top_level_fields(
            provider_route_summary
        ),
        "api_key_setup_quickstart_command_plan_expected_live_check_count": sum(
            expected_live_check_counts_by_family.values()
        ),
        "api_key_setup_quickstart_command_plan_expected_live_check_counts_by_family": (
            expected_live_check_counts_by_family
        ),
        "api_key_setup_quickstart_command_plan_expected_live_contracts_by_family": {
            row["provider_family"]: row.get("expected_live_contract")
            for row in provider_rows
        },
        "api_key_setup_quickstart_command_plan_expected_live_checks_by_family": {
            row["provider_family"]: _string_list(row.get("expected_live_checks"))
            for row in provider_rows
        },
        "api_key_setup_quickstart_command_plan_accepted_env_key_count": sum(
            accepted_env_key_counts_by_family.values()
        ),
        "api_key_setup_quickstart_command_plan_accepted_env_key_counts_by_family": (
            accepted_env_key_counts_by_family
        ),
        "api_key_setup_quickstart_command_plan_preferred_env_key_by_family": {
            row["provider_family"]: row.get("preferred_env_key")
            for row in provider_rows
        },
        "api_key_setup_quickstart_command_plan_accepted_env_keys_by_family": {
            row["provider_family"]: _string_list(row.get("accepted_env_keys"))
            for row in provider_rows
        },
        "api_key_setup_quickstart_command_plan_next_setup_actions_by_family": {
            row["provider_family"]: row.get("next_setup_action")
            for row in provider_rows
        },
        "api_key_setup_quickstart_command_plan_statuses_by_family": {
            row["provider_family"]: row.get("status")
            for row in provider_rows
        },
        "api_key_setup_quickstart_command_plan_network_calls_by_family": {
            row["provider_family"]: row.get("network_call") is True
            for row in provider_rows
        },
        "api_key_setup_quickstart_command_plan_network_call_policies_by_family": {
            row["provider_family"]: row.get("network_call_policy")
            for row in provider_rows
        },
        "api_key_setup_quickstart_command_plan_mutates_local_state_by_family": {
            row["provider_family"]: row.get("mutates_local_state") is True
            for row in provider_rows
        },
        "api_key_setup_quickstart_command_plan_secret_values_returned_by_family": {
            row["provider_family"]: row.get("secret_values_returned") is True
            for row in provider_rows
        },
    }


def _api_key_setup_quickstart_next_command_plan_fields(
    next_quickstart_command_plan_row: dict[str, Any],
) -> dict[str, Any]:
    return {
        "api_key_setup_quickstart_next_command_plan_name": (
            next_quickstart_command_plan_row.get("name")
        ),
        "api_key_setup_quickstart_next_command_plan_kind": (
            next_quickstart_command_plan_row.get("kind")
        ),
        "api_key_setup_quickstart_next_command_plan_command": (
            next_quickstart_command_plan_row.get("command")
        ),
        "api_key_setup_quickstart_next_command_plan_provider_family": (
            next_quickstart_command_plan_row.get("provider_family")
        ),
        "api_key_setup_quickstart_next_command_plan_provider": (
            next_quickstart_command_plan_row.get("provider")
        ),
        "api_key_setup_quickstart_next_command_plan_selected_provider_class": (
            next_quickstart_command_plan_row.get("selected_provider_class")
        ),
        "api_key_setup_quickstart_next_command_plan_provider_route_data_mode": (
            next_quickstart_command_plan_row.get("provider_route_data_mode")
        ),
        "api_key_setup_quickstart_next_command_plan_provider_route_live_data_required": (
            next_quickstart_command_plan_row.get(
                "provider_route_live_data_required"
            )
            is True
        ),
        "api_key_setup_quickstart_next_command_plan_expected_live_contract": (
            next_quickstart_command_plan_row.get("expected_live_contract")
        ),
        "api_key_setup_quickstart_next_command_plan_expected_live_checks": (
            _string_list(next_quickstart_command_plan_row.get("expected_live_checks"))
        ),
        "api_key_setup_quickstart_next_command_plan_preferred_env_key": (
            next_quickstart_command_plan_row.get("preferred_env_key")
        ),
        "api_key_setup_quickstart_next_command_plan_accepted_env_keys": (
            _string_list(next_quickstart_command_plan_row.get("accepted_env_keys"))
        ),
        "api_key_setup_quickstart_next_command_plan_next_setup_action": (
            next_quickstart_command_plan_row.get("next_setup_action")
        ),
        "api_key_setup_quickstart_next_command_plan_status": (
            next_quickstart_command_plan_row.get("status")
        ),
        "api_key_setup_quickstart_next_command_plan_network_call": (
            next_quickstart_command_plan_row.get("network_call") is True
        ),
        "api_key_setup_quickstart_next_command_plan_network_call_policy": (
            next_quickstart_command_plan_row.get("network_call_policy")
        ),
        "api_key_setup_quickstart_next_command_plan_mutates_local_state": (
            next_quickstart_command_plan_row.get("mutates_local_state") is True
        ),
        "api_key_setup_quickstart_next_command_plan_secret_values_returned": (
            next_quickstart_command_plan_row.get("secret_values_returned") is True
        ),
    }
