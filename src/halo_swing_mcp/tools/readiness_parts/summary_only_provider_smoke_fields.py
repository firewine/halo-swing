"""Summary-only next-provider-smoke top-level field projection."""

from __future__ import annotations

from typing import Any

from .live_data_setup import _ordered_unique_strings, _string_list
from .summary_only_provider_route_fields import (
    _api_key_provider_smoke_route_count_top_level_fields,
    _route_family_summary_top_level_fields,
)


__all__ = (
    "_api_key_provider_smoke_top_level_fields",
    "_api_key_provider_smoke_success_top_level_fields",
)


def _api_key_provider_smoke_top_level_fields(
    setup_status_summary: dict[str, Any],
    next_provider_smoke: dict[str, Any],
    provider_smoke_command_rows: list[dict[str, Any]],
    provider_smoke_command_count: int,
    provider_smoke_command_rows_by_family: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    setup_next_provider_smoke = _mapping_or_empty(
        setup_status_summary.get("next_provider_smoke")
    )
    selected_provider_class_by_family = _mapping_or_empty(
        setup_status_summary.get("selected_provider_class_by_family")
    )
    provider_route_data_mode_by_family = _mapping_or_empty(
        setup_status_summary.get("provider_route_data_mode_by_family")
    )
    provider_route_live_data_required_by_family = _mapping_or_empty(
        setup_status_summary.get("provider_route_live_data_required_by_family")
    )
    provider_smoke_selected_provider_class_by_family = {
        family: row.get("selected_provider_class")
        or selected_provider_class_by_family.get(family)
        for family, row in provider_smoke_command_rows_by_family.items()
    }
    provider_smoke_provider_route_data_mode_by_family = {
        family: row.get("provider_route_data_mode")
        or provider_route_data_mode_by_family.get(family)
        for family, row in provider_smoke_command_rows_by_family.items()
    }
    provider_smoke_provider_route_live_data_required_by_family = {
        family: row.get("provider_route_live_data_required") is True
        or provider_route_live_data_required_by_family.get(family) is True
        for family, row in provider_smoke_command_rows_by_family.items()
    }
    provider_smoke_route_summary = {
        "selected_provider_class_by_family": (
            provider_smoke_selected_provider_class_by_family
        ),
        "provider_route_data_mode_by_family": (
            provider_smoke_provider_route_data_mode_by_family
        ),
        "provider_route_live_data_required_by_family": (
            provider_smoke_provider_route_live_data_required_by_family
        ),
    }
    provider_smoke_expected_live_check_counts_by_family = {
        family: len(_string_list(row.get("expected_live_checks")))
        for family, row in provider_smoke_command_rows_by_family.items()
    }
    provider_smoke_accepted_env_keys_by_family = {
        family: _string_list(row.get("accepted_env_keys"))
        for family, row in provider_smoke_command_rows_by_family.items()
    }
    provider_smoke_accepted_env_key_groups = [
        _string_list(row.get("accepted_env_keys"))
        for row in provider_smoke_command_rows
    ]
    provider_smoke_unique_accepted_env_keys = _ordered_unique_strings(
        [
            env_key
            for group in provider_smoke_accepted_env_key_groups
            for env_key in group
        ]
    )
    provider_smoke_preferred_env_keys_by_family = {
        family: row.get("preferred_env_key")
        for family, row in provider_smoke_command_rows_by_family.items()
    }
    provider_smoke_preferred_env_keys = _ordered_unique_strings(
        provider_smoke_preferred_env_keys_by_family.values()
    )
    provider_smoke_accepted_env_key_counts_by_family = {
        family: len(accepted_env_keys)
        for family, accepted_env_keys in (
            provider_smoke_accepted_env_keys_by_family.items()
        )
    }
    provider_smoke_ready_preferred_env_keys_by_family = {
        family: row.get("preferred_env_key")
        for family, row in provider_smoke_command_rows_by_family.items()
        if row.get("status") == "ready"
    }
    provider_smoke_ready_accepted_env_keys_by_family = {
        family: _string_list(row.get("accepted_env_keys"))
        for family, row in provider_smoke_command_rows_by_family.items()
        if row.get("status") == "ready"
    }
    provider_smoke_ready_accepted_env_key_counts_by_family = {
        family: len(accepted_env_keys)
        for family, accepted_env_keys in (
            provider_smoke_ready_accepted_env_keys_by_family.items()
        )
    }
    provider_smoke_blocked_preferred_env_keys_by_family = {
        family: row.get("preferred_env_key")
        for family, row in provider_smoke_command_rows_by_family.items()
        if row.get("status") != "ready"
    }
    provider_smoke_blocked_accepted_env_keys_by_family = {
        family: _string_list(row.get("accepted_env_keys"))
        for family, row in provider_smoke_command_rows_by_family.items()
        if row.get("status") != "ready"
    }
    provider_smoke_blocked_accepted_env_key_counts_by_family = {
        family: len(accepted_env_keys)
        for family, accepted_env_keys in (
            provider_smoke_blocked_accepted_env_keys_by_family.items()
        )
    }
    provider_smoke_network_calls_by_family = {
        family: row.get("network_call") is True
        for family, row in provider_smoke_command_rows_by_family.items()
    }
    provider_smoke_mutates_local_state_by_family = {
        family: row.get("mutates_local_state") is True
        for family, row in provider_smoke_command_rows_by_family.items()
    }
    provider_smoke_secret_values_returned_by_family = {
        family: row.get("secret_values_returned") is True
        for family, row in provider_smoke_command_rows_by_family.items()
    }
    provider_smoke_provider_families = _ordered_unique_strings(
        [row.get("provider_family") for row in provider_smoke_command_rows]
    )
    provider_smoke_ready_provider_families = _ordered_unique_strings(
        [
            family
            for family, row in provider_smoke_command_rows_by_family.items()
            if row.get("status") == "ready"
        ]
    )
    provider_smoke_ready_providers = _ordered_unique_strings(
        [
            row.get("provider")
            for row in provider_smoke_command_rows
            if row.get("status") == "ready"
        ]
    )
    provider_smoke_blocked_provider_families = _ordered_unique_strings(
        [
            family
            for family, row in provider_smoke_command_rows_by_family.items()
            if row.get("status") != "ready"
        ]
    )
    provider_smoke_blocked_providers = _ordered_unique_strings(
        [
            row.get("provider")
            for row in provider_smoke_command_rows
            if row.get("status") != "ready"
        ]
    )
    provider_smoke_ready_command_names = _ordered_unique_strings(
        [
            row.get("smoke_command_name")
            for row in provider_smoke_command_rows
            if row.get("status") == "ready"
        ]
    )
    provider_smoke_ready_commands = _string_list(
        [
            row.get("command")
            for row in provider_smoke_command_rows
            if row.get("status") == "ready"
        ]
    )
    provider_smoke_ready_preferred_env_keys = _ordered_unique_strings(
        [
            row.get("preferred_env_key")
            for row in provider_smoke_command_rows
            if row.get("status") == "ready"
        ]
    )
    provider_smoke_ready_accepted_env_key_groups = [
        _string_list(row.get("accepted_env_keys"))
        for row in provider_smoke_command_rows
        if row.get("status") == "ready"
    ]
    provider_smoke_ready_accepted_env_keys = _ordered_unique_strings(
        [
            env_key
            for group in provider_smoke_ready_accepted_env_key_groups
            for env_key in group
        ]
    )
    provider_smoke_blocked_command_names = _ordered_unique_strings(
        [
            row.get("smoke_command_name")
            for row in provider_smoke_command_rows
            if row.get("status") != "ready"
        ]
    )
    provider_smoke_commands = _string_list(
        [row.get("command") for row in provider_smoke_command_rows]
    )
    provider_smoke_blocked_commands = _string_list(
        [
            row.get("command")
            for row in provider_smoke_command_rows
            if row.get("status") != "ready"
        ]
    )
    provider_smoke_blocked_preferred_env_keys = _ordered_unique_strings(
        [
            row.get("preferred_env_key")
            for row in provider_smoke_command_rows
            if row.get("status") != "ready"
        ]
    )
    provider_smoke_blocked_accepted_env_key_groups = [
        _string_list(row.get("accepted_env_keys"))
        for row in provider_smoke_command_rows
        if row.get("status") != "ready"
    ]
    provider_smoke_blocked_accepted_env_keys = _ordered_unique_strings(
        [
            env_key
            for group in provider_smoke_blocked_accepted_env_key_groups
            for env_key in group
        ]
    )
    next_blocked_provider_smoke = next(
        (
            row
            for row in provider_smoke_command_rows
            if row.get("status") != "ready"
        ),
        {},
    )
    ready_provider_smoke_count = setup_status_summary.get("ready_provider_smoke_count")
    blocked_provider_smoke_count = setup_status_summary.get(
        "blocked_provider_smoke_count"
    )
    provider_smoke_action_status = _provider_smoke_action_status(
        provider_smoke_command_count=provider_smoke_command_count,
        ready_provider_smoke_count=len(provider_smoke_ready_command_names),
        blocked_provider_smoke_count=len(provider_smoke_blocked_command_names),
    )
    provider_smoke_next_action = (
        "run_ready_provider_smokes"
        if provider_smoke_ready_command_names
        else "fill_live_data_api_keys"
        if provider_smoke_blocked_command_names
        else None
    )
    provider_smoke_next_action_command_names = (
        provider_smoke_ready_command_names
        if provider_smoke_next_action == "run_ready_provider_smokes"
        else []
    )
    provider_smoke_next_action_commands = (
        provider_smoke_ready_commands
        if provider_smoke_next_action == "run_ready_provider_smokes"
        else []
    )
    provider_smoke_next_action_provider_families = (
        provider_smoke_ready_provider_families
        if provider_smoke_next_action == "run_ready_provider_smokes"
        else provider_smoke_blocked_provider_families
        if provider_smoke_next_action == "fill_live_data_api_keys"
        else []
    )
    provider_smoke_next_action_providers = (
        provider_smoke_ready_providers
        if provider_smoke_next_action == "run_ready_provider_smokes"
        else provider_smoke_blocked_providers
        if provider_smoke_next_action == "fill_live_data_api_keys"
        else []
    )
    provider_smoke_next_action_rows_by_family = (
        {
            family: row
            for family, row in provider_smoke_command_rows_by_family.items()
            if row.get("status") == "ready"
        }
        if provider_smoke_next_action == "run_ready_provider_smokes"
        else {
            family: row
            for family, row in provider_smoke_command_rows_by_family.items()
            if row.get("status") != "ready"
        }
        if provider_smoke_next_action == "fill_live_data_api_keys"
        else {}
    )
    provider_smoke_next_action_kinds_by_family = {
        family: row.get("kind")
        for family, row in provider_smoke_next_action_rows_by_family.items()
    }
    provider_smoke_next_action_command_names_by_family = {
        family: row.get("smoke_command_name")
        for family, row in provider_smoke_next_action_rows_by_family.items()
    }
    provider_smoke_next_action_commands_by_family = {
        family: row.get("command")
        for family, row in provider_smoke_next_action_rows_by_family.items()
    }
    provider_smoke_next_action_provider_by_family = {
        family: row.get("provider")
        for family, row in provider_smoke_next_action_rows_by_family.items()
    }
    provider_smoke_next_action_statuses_by_family = {
        family: row.get("status")
        for family, row in provider_smoke_next_action_rows_by_family.items()
    }
    provider_smoke_next_action_ready_count = sum(
        1
        for status in provider_smoke_next_action_statuses_by_family.values()
        if status == "ready"
    )
    provider_smoke_next_action_blocked_count = sum(
        1
        for status in provider_smoke_next_action_statuses_by_family.values()
        if status != "ready"
    )
    provider_smoke_next_action_statuses = _ordered_unique_strings(
        provider_smoke_next_action_statuses_by_family.values()
    )
    provider_smoke_next_action_setup_actions_by_family = {
        family: row.get("next_setup_action")
        for family, row in provider_smoke_next_action_rows_by_family.items()
    }
    provider_smoke_next_action_setup_actions = _ordered_unique_strings(
        provider_smoke_next_action_setup_actions_by_family.values()
    )
    provider_smoke_next_action_network_call_policies_by_family = {
        family: row.get("network_call_policy")
        for family, row in provider_smoke_next_action_rows_by_family.items()
    }
    provider_smoke_next_action_network_call_policies = _ordered_unique_strings(
        provider_smoke_next_action_network_call_policies_by_family.values()
    )
    provider_smoke_next_action_network_calls_by_family = {
        family: row.get("network_call") is True
        for family, row in provider_smoke_next_action_rows_by_family.items()
    }
    provider_smoke_next_action_mutates_local_state_by_family = {
        family: row.get("mutates_local_state") is True
        for family, row in provider_smoke_next_action_rows_by_family.items()
    }
    provider_smoke_next_action_secret_values_returned_by_family = {
        family: row.get("secret_values_returned") is True
        for family, row in provider_smoke_next_action_rows_by_family.items()
    }
    provider_smoke_next_action_route_summary = {
        "selected_provider_class_by_family": {
            family: row.get("selected_provider_class")
            or selected_provider_class_by_family.get(family)
            for family, row in provider_smoke_next_action_rows_by_family.items()
        },
        "provider_route_data_mode_by_family": {
            family: row.get("provider_route_data_mode")
            or provider_route_data_mode_by_family.get(family)
            for family, row in provider_smoke_next_action_rows_by_family.items()
        },
        "provider_route_live_data_required_by_family": {
            family: row.get("provider_route_live_data_required") is True
            or provider_route_live_data_required_by_family.get(family) is True
            for family, row in provider_smoke_next_action_rows_by_family.items()
        },
        "all_selected_routes_live": (
            bool(provider_smoke_next_action_rows_by_family)
            and all(
                (
                    row.get("provider_route_data_mode")
                    or provider_route_data_mode_by_family.get(family)
                )
                == "live"
                for family, row in provider_smoke_next_action_rows_by_family.items()
            )
        ),
    }
    provider_smoke_next_action_expected_live_contracts_by_family = {
        family: row.get("expected_live_contract")
        for family, row in provider_smoke_next_action_rows_by_family.items()
    }
    provider_smoke_next_action_expected_live_contracts = _ordered_unique_strings(
        provider_smoke_next_action_expected_live_contracts_by_family.values()
    )
    provider_smoke_next_action_expected_live_checks_by_family = {
        family: _string_list(row.get("expected_live_checks"))
        for family, row in provider_smoke_next_action_rows_by_family.items()
    }
    provider_smoke_next_action_expected_live_checks = _ordered_unique_strings(
        [
            check
            for checks in (
                provider_smoke_next_action_expected_live_checks_by_family.values()
            )
            for check in checks
        ]
    )
    provider_smoke_next_action_expected_live_check_counts_by_family = {
        family: len(checks)
        for family, checks in (
            provider_smoke_next_action_expected_live_checks_by_family.items()
        )
    }
    provider_smoke_next_action_preferred_env_keys = (
        provider_smoke_ready_preferred_env_keys
        if provider_smoke_next_action == "run_ready_provider_smokes"
        else provider_smoke_blocked_preferred_env_keys
        if provider_smoke_next_action == "fill_live_data_api_keys"
        else []
    )
    provider_smoke_next_action_accepted_env_key_groups = (
        provider_smoke_ready_accepted_env_key_groups
        if provider_smoke_next_action == "run_ready_provider_smokes"
        else provider_smoke_blocked_accepted_env_key_groups
        if provider_smoke_next_action == "fill_live_data_api_keys"
        else []
    )
    provider_smoke_next_action_accepted_env_keys = _ordered_unique_strings(
        [
            env_key
            for group in provider_smoke_next_action_accepted_env_key_groups
            for env_key in group
        ]
    )
    provider_smoke_next_action_preferred_env_keys_by_family = (
        provider_smoke_ready_preferred_env_keys_by_family
        if provider_smoke_next_action == "run_ready_provider_smokes"
        else provider_smoke_blocked_preferred_env_keys_by_family
        if provider_smoke_next_action == "fill_live_data_api_keys"
        else {}
    )
    provider_smoke_next_action_accepted_env_keys_by_family = (
        provider_smoke_ready_accepted_env_keys_by_family
        if provider_smoke_next_action == "run_ready_provider_smokes"
        else provider_smoke_blocked_accepted_env_keys_by_family
        if provider_smoke_next_action == "fill_live_data_api_keys"
        else {}
    )
    provider_smoke_next_action_accepted_env_key_counts_by_family = (
        provider_smoke_ready_accepted_env_key_counts_by_family
        if provider_smoke_next_action == "run_ready_provider_smokes"
        else provider_smoke_blocked_accepted_env_key_counts_by_family
        if provider_smoke_next_action == "fill_live_data_api_keys"
        else {}
    )
    return {
        "api_key_provider_smoke_total_count": setup_status_summary.get(
            "provider_smoke_count"
        ),
        "api_key_provider_smoke_ready_count": ready_provider_smoke_count,
        "api_key_provider_smoke_blocked_count": blocked_provider_smoke_count,
        "api_key_provider_smoke_all_ready": (
            provider_smoke_command_count > 0
            and ready_provider_smoke_count == provider_smoke_command_count
        ),
        "api_key_provider_smoke_any_blocked": (
            isinstance(blocked_provider_smoke_count, int)
            and blocked_provider_smoke_count > 0
        ),
        "api_key_provider_smoke_action_status": provider_smoke_action_status,
        "api_key_provider_smoke_next_action": provider_smoke_next_action,
        "api_key_provider_smoke_next_action_command_count": len(
            provider_smoke_next_action_command_names
        ),
        "api_key_provider_smoke_next_action_command_names": (
            provider_smoke_next_action_command_names
        ),
        "api_key_provider_smoke_next_action_commands": (
            provider_smoke_next_action_commands
        ),
        "api_key_provider_smoke_next_action_kinds_by_family": (
            provider_smoke_next_action_kinds_by_family
        ),
        "api_key_provider_smoke_next_action_command_names_by_family": (
            provider_smoke_next_action_command_names_by_family
        ),
        "api_key_provider_smoke_next_action_commands_by_family": (
            provider_smoke_next_action_commands_by_family
        ),
        "api_key_provider_smoke_next_action_provider_by_family": (
            provider_smoke_next_action_provider_by_family
        ),
        "api_key_provider_smoke_next_action_provider_families": (
            provider_smoke_next_action_provider_families
        ),
        "api_key_provider_smoke_next_action_provider_family_count": len(
            provider_smoke_next_action_provider_families
        ),
        "api_key_provider_smoke_next_action_providers": (
            provider_smoke_next_action_providers
        ),
        "api_key_provider_smoke_next_action_provider_count": len(
            provider_smoke_next_action_providers
        ),
        "api_key_provider_smoke_next_action_statuses": (
            provider_smoke_next_action_statuses
        ),
        "api_key_provider_smoke_next_action_status_count": len(
            provider_smoke_next_action_statuses
        ),
        "api_key_provider_smoke_next_action_statuses_by_family": (
            provider_smoke_next_action_statuses_by_family
        ),
        "api_key_provider_smoke_next_action_ready_count": (
            provider_smoke_next_action_ready_count
        ),
        "api_key_provider_smoke_next_action_blocked_count": (
            provider_smoke_next_action_blocked_count
        ),
        "api_key_provider_smoke_next_action_all_ready": (
            bool(provider_smoke_next_action_statuses_by_family)
            and provider_smoke_next_action_ready_count
            == len(provider_smoke_next_action_statuses_by_family)
        ),
        "api_key_provider_smoke_next_action_any_blocked": (
            provider_smoke_next_action_blocked_count > 0
        ),
        "api_key_provider_smoke_next_action_setup_actions": (
            provider_smoke_next_action_setup_actions
        ),
        "api_key_provider_smoke_next_action_setup_action_count": len(
            provider_smoke_next_action_setup_actions
        ),
        "api_key_provider_smoke_next_action_setup_actions_by_family": (
            provider_smoke_next_action_setup_actions_by_family
        ),
        "api_key_provider_smoke_next_action_network_call_policies": (
            provider_smoke_next_action_network_call_policies
        ),
        "api_key_provider_smoke_next_action_network_call_policy_count": len(
            provider_smoke_next_action_network_call_policies
        ),
        "api_key_provider_smoke_next_action_network_call_policies_by_family": (
            provider_smoke_next_action_network_call_policies_by_family
        ),
        "api_key_provider_smoke_next_action_network_calls_by_family": (
            provider_smoke_next_action_network_calls_by_family
        ),
        "api_key_provider_smoke_next_action_network_call_count": sum(
            provider_smoke_next_action_network_calls_by_family.values()
        ),
        "api_key_provider_smoke_next_action_all_network_calls": (
            bool(provider_smoke_next_action_network_calls_by_family)
            and all(provider_smoke_next_action_network_calls_by_family.values())
        ),
        "api_key_provider_smoke_next_action_mutates_local_state_by_family": (
            provider_smoke_next_action_mutates_local_state_by_family
        ),
        "api_key_provider_smoke_next_action_mutates_local_state_count": sum(
            provider_smoke_next_action_mutates_local_state_by_family.values()
        ),
        "api_key_provider_smoke_next_action_any_mutates_local_state": any(
            provider_smoke_next_action_mutates_local_state_by_family.values()
        ),
        "api_key_provider_smoke_next_action_secret_values_returned_by_family": (
            provider_smoke_next_action_secret_values_returned_by_family
        ),
        "api_key_provider_smoke_next_action_secret_values_returned_count": sum(
            provider_smoke_next_action_secret_values_returned_by_family.values()
        ),
        "api_key_provider_smoke_next_action_any_secret_values_returned": any(
            provider_smoke_next_action_secret_values_returned_by_family.values()
        ),
        **_route_family_summary_top_level_fields(
            prefix="api_key_provider_smoke_next_action",
            source_summary=provider_smoke_next_action_route_summary,
        ),
        "api_key_provider_smoke_next_action_expected_live_contracts": (
            provider_smoke_next_action_expected_live_contracts
        ),
        "api_key_provider_smoke_next_action_expected_live_contract_count": len(
            provider_smoke_next_action_expected_live_contracts
        ),
        "api_key_provider_smoke_next_action_expected_live_contracts_by_family": (
            provider_smoke_next_action_expected_live_contracts_by_family
        ),
        "api_key_provider_smoke_next_action_expected_live_checks": (
            provider_smoke_next_action_expected_live_checks
        ),
        "api_key_provider_smoke_next_action_expected_live_check_count": len(
            provider_smoke_next_action_expected_live_checks
        ),
        "api_key_provider_smoke_next_action_expected_live_checks_by_family": (
            provider_smoke_next_action_expected_live_checks_by_family
        ),
        "api_key_provider_smoke_next_action_expected_live_check_counts_by_family": (
            provider_smoke_next_action_expected_live_check_counts_by_family
        ),
        "api_key_provider_smoke_next_action_preferred_env_keys": (
            provider_smoke_next_action_preferred_env_keys
        ),
        "api_key_provider_smoke_next_action_preferred_env_key_count": len(
            provider_smoke_next_action_preferred_env_keys
        ),
        "api_key_provider_smoke_next_action_accepted_env_keys": (
            provider_smoke_next_action_accepted_env_keys
        ),
        "api_key_provider_smoke_next_action_accepted_env_key_count": len(
            provider_smoke_next_action_accepted_env_keys
        ),
        "api_key_provider_smoke_next_action_accepted_env_key_groups": (
            provider_smoke_next_action_accepted_env_key_groups
        ),
        "api_key_provider_smoke_next_action_accepted_env_key_group_count": len(
            provider_smoke_next_action_accepted_env_key_groups
        ),
        "api_key_provider_smoke_next_action_preferred_env_keys_by_family": (
            provider_smoke_next_action_preferred_env_keys_by_family
        ),
        "api_key_provider_smoke_next_action_accepted_env_keys_by_family": (
            provider_smoke_next_action_accepted_env_keys_by_family
        ),
        "api_key_provider_smoke_next_action_accepted_env_key_counts_by_family": (
            provider_smoke_next_action_accepted_env_key_counts_by_family
        ),
        "api_key_provider_smoke_ready_preferred_env_keys": (
            provider_smoke_ready_preferred_env_keys
        ),
        "api_key_provider_smoke_ready_preferred_env_key_count": len(
            provider_smoke_ready_preferred_env_keys
        ),
        "api_key_provider_smoke_ready_accepted_env_keys": (
            provider_smoke_ready_accepted_env_keys
        ),
        "api_key_provider_smoke_ready_accepted_env_key_count": len(
            provider_smoke_ready_accepted_env_keys
        ),
        "api_key_provider_smoke_ready_accepted_env_key_groups": (
            provider_smoke_ready_accepted_env_key_groups
        ),
        "api_key_provider_smoke_ready_accepted_env_key_group_count": len(
            provider_smoke_ready_accepted_env_key_groups
        ),
        "api_key_provider_smoke_ready_preferred_env_keys_by_family": (
            provider_smoke_ready_preferred_env_keys_by_family
        ),
        "api_key_provider_smoke_ready_accepted_env_keys_by_family": (
            provider_smoke_ready_accepted_env_keys_by_family
        ),
        "api_key_provider_smoke_ready_accepted_env_key_counts_by_family": (
            provider_smoke_ready_accepted_env_key_counts_by_family
        ),
        "api_key_provider_smoke_blocked_preferred_env_keys": (
            provider_smoke_blocked_preferred_env_keys
        ),
        "api_key_provider_smoke_blocked_preferred_env_key_count": len(
            provider_smoke_blocked_preferred_env_keys
        ),
        "api_key_provider_smoke_blocked_accepted_env_keys": (
            provider_smoke_blocked_accepted_env_keys
        ),
        "api_key_provider_smoke_blocked_accepted_env_key_count": len(
            provider_smoke_blocked_accepted_env_keys
        ),
        "api_key_provider_smoke_blocked_accepted_env_key_groups": (
            provider_smoke_blocked_accepted_env_key_groups
        ),
        "api_key_provider_smoke_blocked_accepted_env_key_group_count": len(
            provider_smoke_blocked_accepted_env_key_groups
        ),
        "api_key_provider_smoke_blocked_preferred_env_keys_by_family": (
            provider_smoke_blocked_preferred_env_keys_by_family
        ),
        "api_key_provider_smoke_blocked_accepted_env_keys_by_family": (
            provider_smoke_blocked_accepted_env_keys_by_family
        ),
        "api_key_provider_smoke_blocked_accepted_env_key_counts_by_family": (
            provider_smoke_blocked_accepted_env_key_counts_by_family
        ),
        "api_key_next_provider_smoke_command_name": (
            setup_status_summary.get("next_provider_smoke_command_name")
            or next_provider_smoke.get("smoke_command_name")
        ),
        "api_key_next_provider_smoke_provider_family": (
            next_provider_smoke.get("provider_family")
        ),
        "api_key_next_provider_smoke_provider": next_provider_smoke.get("provider"),
        "api_key_next_provider_smoke_selected_provider_class": (
            next_provider_smoke.get("selected_provider_class")
            or setup_next_provider_smoke.get("selected_provider_class")
        ),
        "api_key_next_provider_smoke_provider_route_data_mode": (
            next_provider_smoke.get("provider_route_data_mode")
            or setup_next_provider_smoke.get("provider_route_data_mode")
        ),
        "api_key_next_provider_smoke_provider_route_live_data_required": (
            next_provider_smoke.get("provider_route_live_data_required") is True
            or setup_next_provider_smoke.get("provider_route_live_data_required")
            is True
        ),
        "api_key_next_provider_smoke_command": next_provider_smoke.get("command"),
        "api_key_next_provider_smoke_next_setup_action": (
            next_provider_smoke.get("next_setup_action")
            or setup_next_provider_smoke.get("next_setup_action")
        ),
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
        "api_key_next_ready_provider_smoke_provider_family": (
            next_provider_smoke.get("provider_family")
        ),
        "api_key_next_ready_provider_smoke_provider": (
            next_provider_smoke.get("provider")
        ),
        "api_key_next_ready_provider_smoke_selected_provider_class": (
            next_provider_smoke.get("selected_provider_class")
            or setup_next_provider_smoke.get("selected_provider_class")
        ),
        "api_key_next_ready_provider_smoke_provider_route_data_mode": (
            next_provider_smoke.get("provider_route_data_mode")
            or setup_next_provider_smoke.get("provider_route_data_mode")
        ),
        "api_key_next_ready_provider_smoke_provider_route_live_data_required": (
            next_provider_smoke.get("provider_route_live_data_required") is True
            or setup_next_provider_smoke.get("provider_route_live_data_required")
            is True
        ),
        "api_key_next_ready_provider_smoke_command_name": (
            setup_status_summary.get("next_provider_smoke_command_name")
            or next_provider_smoke.get("smoke_command_name")
        ),
        "api_key_next_ready_provider_smoke_command": next_provider_smoke.get(
            "command"
        ),
        "api_key_next_ready_provider_smoke_expected_live_contract": (
            next_provider_smoke.get("expected_live_contract")
        ),
        "api_key_next_ready_provider_smoke_expected_live_checks": _string_list(
            next_provider_smoke.get("expected_live_checks")
        ),
        "api_key_next_ready_provider_smoke_preferred_env_key": (
            next_provider_smoke.get("preferred_env_key")
        ),
        "api_key_next_ready_provider_smoke_accepted_env_keys": _string_list(
            next_provider_smoke.get("accepted_env_keys")
        ),
        "api_key_next_ready_provider_smoke_next_setup_action": (
            next_provider_smoke.get("next_setup_action")
            or setup_next_provider_smoke.get("next_setup_action")
        ),
        "api_key_next_ready_provider_smoke_status": next_provider_smoke.get(
            "status"
        ),
        "api_key_next_ready_provider_smoke_network_call": (
            next_provider_smoke.get("network_call") is True
        ),
        "api_key_next_ready_provider_smoke_network_call_policy": (
            next_provider_smoke.get("network_call_policy")
        ),
        "api_key_next_ready_provider_smoke_mutates_local_state": (
            next_provider_smoke.get("mutates_local_state") is True
        ),
        "api_key_next_ready_provider_smoke_secret_values_returned": (
            next_provider_smoke.get("secret_values_returned") is True
        ),
        "api_key_next_blocked_provider_smoke_provider_family": (
            next_blocked_provider_smoke.get("provider_family")
        ),
        "api_key_next_blocked_provider_smoke_provider": (
            next_blocked_provider_smoke.get("provider")
        ),
        "api_key_next_blocked_provider_smoke_selected_provider_class": (
            next_blocked_provider_smoke.get("selected_provider_class")
        ),
        "api_key_next_blocked_provider_smoke_provider_route_data_mode": (
            next_blocked_provider_smoke.get("provider_route_data_mode")
        ),
        "api_key_next_blocked_provider_smoke_provider_route_live_data_required": (
            next_blocked_provider_smoke.get("provider_route_live_data_required")
            is True
        ),
        "api_key_next_blocked_provider_smoke_command_name": (
            next_blocked_provider_smoke.get("smoke_command_name")
        ),
        "api_key_next_blocked_provider_smoke_command": (
            next_blocked_provider_smoke.get("command")
        ),
        "api_key_next_blocked_provider_smoke_expected_live_contract": (
            next_blocked_provider_smoke.get("expected_live_contract")
        ),
        "api_key_next_blocked_provider_smoke_expected_live_checks": _string_list(
            next_blocked_provider_smoke.get("expected_live_checks")
        ),
        "api_key_next_blocked_provider_smoke_preferred_env_key": (
            next_blocked_provider_smoke.get("preferred_env_key")
        ),
        "api_key_next_blocked_provider_smoke_accepted_env_keys": _string_list(
            next_blocked_provider_smoke.get("accepted_env_keys")
        ),
        "api_key_next_blocked_provider_smoke_next_setup_action": (
            next_blocked_provider_smoke.get("next_setup_action")
        ),
        "api_key_next_blocked_provider_smoke_status": (
            next_blocked_provider_smoke.get("status")
        ),
        "api_key_next_blocked_provider_smoke_network_call": (
            next_blocked_provider_smoke.get("network_call") is True
        ),
        "api_key_next_blocked_provider_smoke_network_call_policy": (
            next_blocked_provider_smoke.get("network_call_policy")
        ),
        "api_key_next_blocked_provider_smoke_mutates_local_state": (
            next_blocked_provider_smoke.get("mutates_local_state") is True
        ),
        "api_key_next_blocked_provider_smoke_secret_values_returned": (
            next_blocked_provider_smoke.get("secret_values_returned") is True
        ),
        "api_key_provider_smoke_command_count": provider_smoke_command_count,
        "api_key_provider_smoke_provider_families": (
            provider_smoke_provider_families
        ),
        "api_key_provider_smoke_provider_family_count": len(
            provider_smoke_provider_families
        ),
        "api_key_provider_smoke_ready_provider_families": (
            provider_smoke_ready_provider_families
        ),
        "api_key_provider_smoke_blocked_provider_families": (
            provider_smoke_blocked_provider_families
        ),
        "api_key_provider_smoke_ready_command_names": (
            provider_smoke_ready_command_names
        ),
        "api_key_provider_smoke_ready_commands": provider_smoke_ready_commands,
        "api_key_provider_smoke_blocked_command_names": (
            provider_smoke_blocked_command_names
        ),
        "api_key_provider_smoke_blocked_commands": (
            provider_smoke_blocked_commands
        ),
        "api_key_provider_smoke_command_names": _ordered_unique_strings(
            [
                row.get("smoke_command_name")
                for row in provider_smoke_command_rows
            ]
        ),
        "api_key_provider_smoke_commands": provider_smoke_commands,
        "api_key_provider_smoke_kinds_by_family": {
            family: row.get("kind")
            for family, row in provider_smoke_command_rows_by_family.items()
        },
        "api_key_provider_smoke_command_names_by_family": {
            family: row.get("smoke_command_name")
            for family, row in provider_smoke_command_rows_by_family.items()
        },
        "api_key_provider_smoke_commands_by_family": {
            family: row.get("command")
            for family, row in provider_smoke_command_rows_by_family.items()
        },
        "api_key_provider_smoke_provider_by_family": {
            family: row.get("provider")
            for family, row in provider_smoke_command_rows_by_family.items()
        },
        "api_key_provider_smoke_next_setup_actions_by_family": {
            family: row.get("next_setup_action")
            for family, row in provider_smoke_command_rows_by_family.items()
        },
        "api_key_provider_smoke_statuses_by_family": {
            family: row.get("status")
            for family, row in provider_smoke_command_rows_by_family.items()
        },
        "api_key_provider_smoke_selected_provider_class_by_family": (
            provider_smoke_selected_provider_class_by_family
        ),
        "api_key_provider_smoke_provider_route_data_mode_by_family": (
            provider_smoke_provider_route_data_mode_by_family
        ),
        "api_key_provider_smoke_provider_route_live_data_required_by_family": (
            provider_smoke_provider_route_live_data_required_by_family
        ),
        "api_key_provider_smoke_all_live_data_required": (
            provider_smoke_command_count > 0
            and all(
                provider_smoke_provider_route_live_data_required_by_family.values()
            )
        ),
        **_api_key_provider_smoke_route_count_top_level_fields(
            provider_smoke_route_summary
        ),
        "api_key_provider_smoke_network_call_policies_by_family": {
            family: row.get("network_call_policy")
            for family, row in provider_smoke_command_rows_by_family.items()
        },
        "api_key_provider_smoke_network_calls_by_family": (
            provider_smoke_network_calls_by_family
        ),
        "api_key_provider_smoke_network_call_count": sum(
            provider_smoke_network_calls_by_family.values()
        ),
        "api_key_provider_smoke_all_network_calls": (
            provider_smoke_command_count > 0
            and all(provider_smoke_network_calls_by_family.values())
        ),
        "api_key_provider_smoke_mutates_local_state_by_family": (
            provider_smoke_mutates_local_state_by_family
        ),
        "api_key_provider_smoke_mutates_local_state_count": sum(
            provider_smoke_mutates_local_state_by_family.values()
        ),
        "api_key_provider_smoke_any_mutates_local_state": any(
            provider_smoke_mutates_local_state_by_family.values()
        ),
        "api_key_provider_smoke_secret_values_returned_by_family": (
            provider_smoke_secret_values_returned_by_family
        ),
        "api_key_provider_smoke_secret_values_returned_count": sum(
            provider_smoke_secret_values_returned_by_family.values()
        ),
        "api_key_provider_smoke_any_secret_values_returned": any(
            provider_smoke_secret_values_returned_by_family.values()
        ),
        "api_key_provider_smoke_expected_live_contracts_by_family": {
            family: row.get("expected_live_contract")
            for family, row in provider_smoke_command_rows_by_family.items()
        },
        "api_key_provider_smoke_expected_live_checks_by_family": {
            family: _string_list(row.get("expected_live_checks"))
            for family, row in provider_smoke_command_rows_by_family.items()
        },
        "api_key_provider_smoke_expected_live_check_count": sum(
            provider_smoke_expected_live_check_counts_by_family.values()
        ),
        "api_key_provider_smoke_expected_live_check_counts_by_family": (
            provider_smoke_expected_live_check_counts_by_family
        ),
        "api_key_provider_smoke_accepted_env_keys_by_family": (
            provider_smoke_accepted_env_keys_by_family
        ),
        "api_key_provider_smoke_accepted_env_key_groups": (
            provider_smoke_accepted_env_key_groups
        ),
        "api_key_provider_smoke_accepted_env_key_group_count": len(
            provider_smoke_accepted_env_key_groups
        ),
        "api_key_provider_smoke_unique_accepted_env_keys": (
            provider_smoke_unique_accepted_env_keys
        ),
        "api_key_provider_smoke_unique_accepted_env_key_count": len(
            provider_smoke_unique_accepted_env_keys
        ),
        "api_key_provider_smoke_preferred_env_keys_by_family": (
            provider_smoke_preferred_env_keys_by_family
        ),
        "api_key_provider_smoke_preferred_env_keys": (
            provider_smoke_preferred_env_keys
        ),
        "api_key_provider_smoke_preferred_env_key_count": len(
            provider_smoke_preferred_env_keys
        ),
        "api_key_provider_smoke_accepted_env_key_count": sum(
            provider_smoke_accepted_env_key_counts_by_family.values()
        ),
        "api_key_provider_smoke_accepted_env_key_counts_by_family": (
            provider_smoke_accepted_env_key_counts_by_family
        ),
    }


def _mapping_or_empty(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _provider_smoke_action_status(
    *,
    provider_smoke_command_count: int,
    ready_provider_smoke_count: int,
    blocked_provider_smoke_count: int,
) -> str:
    if provider_smoke_command_count <= 0:
        return "not_available"
    if ready_provider_smoke_count == provider_smoke_command_count:
        return "ready"
    if ready_provider_smoke_count > 0:
        return "partially_ready"
    if blocked_provider_smoke_count > 0:
        return "blocked"
    return "not_available"


def _api_key_provider_smoke_success_top_level_fields(
    *,
    provider_smoke_summary_count: int,
    provider_smoke_success_rows: list[dict[str, Any]],
    provider_smoke_success_count: int,
    provider_smoke_success_expected_live_checks: list[str],
    provider_smoke_success_network_call_count: int,
    provider_smoke_success_mutates_local_state_count: int,
    provider_smoke_success_secret_values_returned_count: int,
    provider_smoke_success_accepted_env_key_groups: list[list[str]],
) -> dict[str, Any]:
    first_success_row = (
        provider_smoke_success_rows[0] if provider_smoke_success_rows else {}
    )
    return {
        "provider_smoke_success_count": provider_smoke_success_count,
        "provider_smoke_all_successful": (
            provider_smoke_summary_count > 0
            and provider_smoke_success_count == provider_smoke_summary_count
        ),
        "provider_smoke_success_provider_families": _ordered_unique_strings(
            [row.get("provider_family") for row in provider_smoke_success_rows]
        ),
        "provider_smoke_success_providers": _ordered_unique_strings(
            [row.get("provider") for row in provider_smoke_success_rows]
        ),
        "provider_smoke_success_smoke_command_names": _ordered_unique_strings(
            [row.get("smoke_command_name") for row in provider_smoke_success_rows]
        ),
        "provider_smoke_first_success_provider_family": (
            first_success_row.get("provider_family")
        ),
        "provider_smoke_first_success_provider": first_success_row.get("provider"),
        "provider_smoke_first_success_smoke_command_name": (
            first_success_row.get("smoke_command_name")
        ),
        "provider_smoke_first_success_status": first_success_row.get("status"),
        "provider_smoke_first_success_expected_live_contract": (
            first_success_row.get("expected_live_contract")
        ),
        "provider_smoke_first_success_expected_live_checks": _string_list(
            first_success_row.get("expected_live_checks")
        ),
        "provider_smoke_first_success_preferred_env_key": (
            first_success_row.get("preferred_env_key")
        ),
        "provider_smoke_first_success_accepted_env_keys": _string_list(
            first_success_row.get("accepted_env_keys")
        ),
        "provider_smoke_first_success_network_call": (
            first_success_row.get("network_call") is True
        ),
        "provider_smoke_first_success_network_call_policy": (
            first_success_row.get("network_call_policy")
        ),
        "provider_smoke_first_success_mutates_local_state": (
            first_success_row.get("mutates_local_state") is True
        ),
        "provider_smoke_first_success_secret_values_returned": (
            first_success_row.get("secret_values_returned") is True
        ),
        "provider_smoke_success_expected_live_contracts": _ordered_unique_strings(
            [
                row.get("expected_live_contract")
                for row in provider_smoke_success_rows
            ]
        ),
        "provider_smoke_success_expected_live_checks": (
            provider_smoke_success_expected_live_checks
        ),
        "provider_smoke_success_check_count": len(
            provider_smoke_success_expected_live_checks
        ),
        "provider_smoke_success_network_call_count": (
            provider_smoke_success_network_call_count
        ),
        "provider_smoke_success_all_network_calls": (
            provider_smoke_success_count > 0
            and provider_smoke_success_network_call_count
            == provider_smoke_success_count
        ),
        "provider_smoke_success_network_call_policies": _ordered_unique_strings(
            [
                row.get("network_call_policy")
                for row in provider_smoke_success_rows
            ]
        ),
        "provider_smoke_success_mutates_local_state_count": (
            provider_smoke_success_mutates_local_state_count
        ),
        "provider_smoke_success_any_mutates_local_state": (
            provider_smoke_success_mutates_local_state_count > 0
        ),
        "provider_smoke_success_secret_values_returned_count": (
            provider_smoke_success_secret_values_returned_count
        ),
        "provider_smoke_success_any_secret_values_returned": (
            provider_smoke_success_secret_values_returned_count > 0
        ),
        "provider_smoke_success_preferred_env_keys": _ordered_unique_strings(
            [row.get("preferred_env_key") for row in provider_smoke_success_rows]
        ),
        "provider_smoke_success_accepted_env_keys": _ordered_unique_strings(
            [
                env_key
                for group in provider_smoke_success_accepted_env_key_groups
                for env_key in group
            ]
        ),
        "provider_smoke_success_accepted_env_key_groups": (
            provider_smoke_success_accepted_env_key_groups
        ),
    }
