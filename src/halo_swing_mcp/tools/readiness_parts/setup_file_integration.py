# ruff: noqa: F403,F405,F821
"""Setup File Integration readiness implementation."""

from __future__ import annotations

from .context import *


__all__ = ('_api_key_setup_file_summary', '_api_key_dotenv_loading_summary', '_api_key_pipeline_smoke_summary', '_api_key_pipeline_provider_route_summary', '_api_key_provider_selection_summary', '_api_key_integration_status_summary')


_OPTIONAL_LIVE_MODE_ENV_BY_PROVIDER_FAMILY = {
    "market": "HALO_SWING_MARKET_DATA_MODE",
    "macro": "HALO_SWING_MACRO_DATA_MODE",
    "news": "HALO_SWING_NEWS_DATA_MODE",
}


def _provider_auto_selects_live_provider(row: dict[str, Any]) -> bool:
    if row.get("auto_selects_live_provider") is not None:
        return row.get("auto_selects_live_provider") is True
    return row.get("configured") is True and row.get("live_mode_required") is not True


def _api_key_setup_file_summary(
    live_data_setup_summary: dict[str, Any],
) -> dict[str, Any]:
    dotenv_file_status = _optional_mapping(
        live_data_setup_summary.get("dotenv_file_status")
    ) or {}
    dotenv_template = _optional_mapping(
        live_data_setup_summary.get("dotenv_template")
    ) or {}
    live_data_setup_steps = _optional_mapping(
        live_data_setup_summary.get("live_data_setup_steps")
    ) or {}
    provider_family_summary = _optional_mapping(
        live_data_setup_summary.get("provider_family_summary")
    ) or {}
    entries = dotenv_template.get("entries")
    template_entries = entries if isinstance(entries, list) else []
    preferred_env_keys = [
        entry["preferred_env_key"]
        for entry in template_entries
        if isinstance(entry, dict) and isinstance(entry.get("preferred_env_key"), str)
    ]
    dotenv_examples = [
        entry["example"]
        for entry in template_entries
        if isinstance(entry, dict) and isinstance(entry.get("example"), str)
    ]
    return {
        "schema_version": "api_key_setup_file_summary.v1",
        "source_path": dotenv_file_status.get("source_path"),
        "target_path": dotenv_file_status.get("target_path"),
        "source_exists": dotenv_file_status.get("source_exists") is True,
        "target_exists": dotenv_file_status.get("target_exists") is True,
        "copy_required": dotenv_file_status.get("copy_required") is True,
        "copy_command": _optional_mapping(dotenv_file_status.get("copy_command")),
        "preferred_env_keys": preferred_env_keys,
        "preferred_env_key_count": len(preferred_env_keys),
        "dotenv_examples": dotenv_examples,
        "dotenv_example_count": len(dotenv_examples),
        "configured_provider_families": _string_list(
            provider_family_summary.get("configured_provider_families")
        ),
        "missing_provider_families": _string_list(
            provider_family_summary.get("missing_provider_families")
        ),
        "configured_provider_family_count": provider_family_summary.get(
            "configured_count"
        ),
        "required_provider_family_count": provider_family_summary.get(
            "required_count"
        ),
        "next_setup_step": live_data_setup_steps.get("next_step"),
        "ready_to_run_live_smoke": (
            live_data_setup_summary.get("ready_to_run_live_smoke") is True
        ),
        "network_call": False,
        "mutates_local_state": False,
        "secret_values_returned": False,
    }


def _api_key_dotenv_loading_summary(
    live_data_api_key_status: dict[str, Any],
    live_data_setup_summary: dict[str, Any],
) -> dict[str, Any]:
    dotenv = _optional_mapping(live_data_api_key_status.get("dotenv")) or {}
    dotenv_file_status = _optional_mapping(
        live_data_setup_summary.get("dotenv_file_status")
    ) or {}
    live_data_setup_steps = _optional_mapping(
        live_data_setup_summary.get("live_data_setup_steps")
    ) or {}
    disabled = dotenv.get("disabled") is True
    supported = dotenv.get("supported") is True
    return {
        "schema_version": "api_key_dotenv_loading_summary.v1",
        "dotenv_supported": supported,
        "dotenv_loading_enabled": supported and not disabled,
        "disabled": disabled,
        "disabled_env_key": local_env.DOTENV_DISABLED_ENV,
        "configuration_precedence": _string_list(dotenv.get("precedence")),
        "source_path": dotenv_file_status.get("source_path"),
        "target_path": dotenv_file_status.get("target_path"),
        "source_exists": dotenv_file_status.get("source_exists") is True,
        "target_exists": dotenv_file_status.get("target_exists") is True,
        "copy_required": dotenv_file_status.get("copy_required") is True,
        "next_setup_step": live_data_setup_steps.get("next_step"),
        "ready_to_run_live_smoke": (
            live_data_setup_summary.get("ready_to_run_live_smoke") is True
        ),
        "network_call": False,
        "mutates_local_state": False,
        "secret_values_returned": False,
    }


def _api_key_pipeline_smoke_summary(smoke: dict[str, Any]) -> dict[str, Any]:
    live_data_setup_summary = _optional_mapping(
        smoke.get("live_data_setup_summary")
    ) or {}
    next_smoke_command = _optional_mapping(
        live_data_setup_summary.get("next_smoke_command")
    ) or {}
    provider_family_summary = _optional_mapping(
        live_data_setup_summary.get("provider_family_summary")
    ) or {}
    live_data_setup_steps = _optional_mapping(
        live_data_setup_summary.get("live_data_setup_steps")
    ) or {}
    setup_steps = live_data_setup_steps.get("steps")
    provider_setup_actions = _optional_mapping(
        live_data_setup_summary.get("provider_setup_actions")
    ) or {}
    provider_smoke_plan = _optional_mapping(
        live_data_setup_summary.get("provider_smoke_plan")
    ) or {}
    provider_error_summaries = smoke.get("provider_error_summaries")
    provider_error_rows = (
        [
            row
            for row in provider_error_summaries
            if isinstance(row, dict)
        ]
        if isinstance(provider_error_summaries, list)
        else []
    )
    provider_smoke_summaries = smoke.get("provider_smoke_summaries")
    provider_smoke_rows = (
        [
            row
            for row in provider_smoke_summaries
            if isinstance(row, dict)
        ]
        if isinstance(provider_smoke_summaries, list)
        else []
    )
    provider_error_compact_summary = _provider_error_compact_summary(
        provider_error_rows,
        provider_smoke_plan=provider_smoke_plan,
    )
    next_operator_action = _optional_mapping(
        live_data_setup_summary.get("next_operator_action")
    ) or {}
    return {
        "schema_version": smoke.get("schema_version"),
        "status": smoke.get("status"),
        "error_summary": _optional_mapping(smoke.get("error_summary")),
        "network_call": smoke.get("network_call"),
        "live_data_required": smoke.get("live_data_required"),
        "mutates_local_state": smoke.get("mutates_local_state", False),
        "secret_values_returned": smoke.get("secret_values_returned"),
        "live_data_setup_summary_status": live_data_setup_summary.get("status"),
        "ready_to_run_live_smoke": live_data_setup_summary.get(
            "ready_to_run_live_smoke"
        ),
        "provider_route_status": live_data_setup_summary.get(
            "provider_route_status"
        ),
        "provider_family_summary": provider_family_summary,
        "configured_provider_family_count": provider_family_summary.get(
            "configured_count"
        ),
        "required_provider_family_count": provider_family_summary.get(
            "required_count"
        ),
        "missing_provider_families": provider_family_summary.get(
            "missing_provider_families"
        ),
        "live_data_setup_steps": live_data_setup_steps,
        "next_operator_action": next_operator_action,
        "next_setup_step": live_data_setup_steps.get("next_step"),
        "setup_step_count": len(setup_steps) if isinstance(setup_steps, list) else 0,
        "provider_setup_actions": provider_setup_actions,
        "provider_setup_action_count": len(provider_setup_actions),
        "provider_smoke_plan": provider_smoke_plan,
        "provider_smoke_count": provider_smoke_plan.get("provider_smoke_count"),
        "ready_provider_smoke_count": provider_smoke_plan.get(
            "ready_provider_smoke_count"
        ),
        "blocked_provider_smoke_count": provider_smoke_plan.get(
            "blocked_provider_smoke_count"
        ),
        "provider_smoke_summaries": provider_smoke_rows,
        "provider_smoke_summary_count": len(provider_smoke_rows),
        "provider_error_summaries": provider_error_rows,
        "provider_error_summary_count": len(provider_error_rows),
        "failed_provider_families": provider_error_compact_summary[
            "failed_provider_families"
        ],
        "failed_provider_count": provider_error_compact_summary[
            "failed_provider_count"
        ],
        "first_provider_error_summary": provider_error_compact_summary[
            "first_provider_error_summary"
        ],
        "next_provider_recovery_action": provider_error_compact_summary[
            "next_provider_recovery_action"
        ],
        "next_provider_recovery_smoke": provider_error_compact_summary[
            "next_provider_recovery_smoke"
        ],
        "next_provider_recovery_smoke_command_name": (
            provider_error_compact_summary[
                "next_provider_recovery_smoke_command_name"
            ]
        ),
        "provider_recovery_smokes": provider_error_compact_summary[
            "provider_recovery_smokes"
        ],
        "provider_recovery_smoke_count": provider_error_compact_summary[
            "provider_recovery_smoke_count"
        ],
        "next_smoke_command_name": next_smoke_command.get("name"),
    }


def _api_key_pipeline_provider_route_summary(route: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": route.get("schema_version"),
        "status": route.get("status"),
        "provider_factory": route.get("provider_factory"),
        "selected_provider_classes": route.get("selected_provider_classes"),
        "missing": route.get("missing"),
        "network_call": route.get("network_call"),
        "secret_values_returned": route.get("secret_values_returned"),
    }


def _api_key_provider_selection_summary(
    provider_route: dict[str, Any],
    live_data_setup_summary: dict[str, Any],
) -> dict[str, Any]:
    provider_setup_actions = (
        _optional_mapping(live_data_setup_summary.get("provider_setup_actions"))
        or {}
    )
    providers = _optional_mapping(provider_route.get("providers")) or {}
    providers_from_route = bool(providers)
    if not providers:
        providers = provider_setup_actions
    provider_rows: list[tuple[str, dict[str, Any]]] = []
    for family, provider in providers.items():
        row = _optional_mapping(provider)
        if row is None:
            continue
        provider_family = row.get("provider_family")
        if isinstance(provider_family, str):
            provider_rows.append((provider_family, row))
        elif isinstance(family, str):
            provider_rows.append((family, row))
    raw_route_entries = provider_route.get("route")
    route_entries = (
        [entry for entry in raw_route_entries if isinstance(entry, dict)]
        if isinstance(raw_route_entries, list)
        else []
    )
    selected_provider_by_route = {
        str(entry["provider_family"]): entry.get("provider")
        for entry in route_entries
        if isinstance(entry.get("provider_family"), str)
        and entry.get("provider_family") != "fixture"
    }
    route_entries_by_family = {
        str(entry["provider_family"]): entry
        for entry in route_entries
        if isinstance(entry.get("provider_family"), str)
        and entry.get("provider_family") != "fixture"
    }
    configured_provider_families = [
        family for family, row in provider_rows if row.get("configured") is True
    ]
    required_provider_families = [family for family, _row in provider_rows]
    missing_provider_families = [
        family
        for family in required_provider_families
        if family not in configured_provider_families
    ]
    configured_env_keys_by_provider_family = {
        family: _string_list(row.get("configured_env_keys"))
        for family, row in provider_rows
    }
    provider_env_key_hints_by_family = {
        family: {
            "preferred_env_key": row.get("preferred_env_key")
            or (
                _optional_mapping(provider_setup_actions.get(family)) or {}
            ).get("preferred_env_key"),
            "accepted_env_keys": _string_list(row.get("accepted_env_keys"))
            or _string_list(
                (
                    _optional_mapping(provider_setup_actions.get(family)) or {}
                ).get("accepted_env_keys")
            ),
        }
        for family, row in provider_rows
    }
    provider_auto_selects_live_provider_by_family = {
        family: _provider_auto_selects_live_provider(row)
        for family, row in provider_rows
    }
    provider_optional_live_mode_env_by_family = {
        family: row.get("optional_live_mode_env")
        or (
            _optional_mapping(provider_setup_actions.get(family)) or {}
        ).get("optional_live_mode_env")
        or _OPTIONAL_LIVE_MODE_ENV_BY_PROVIDER_FAMILY.get(family)
        for family, row in provider_rows
    }
    provider_live_mode_required_by_family = {
        family: row.get("live_mode_required") is True
        for family, row in provider_rows
    }
    all_configured_auto_select_live_provider = bool(
        configured_provider_families
    ) and all(
        provider_auto_selects_live_provider_by_family.get(family) is True
        for family in configured_provider_families
    )
    selected_provider_classes = _string_list(
        provider_route.get("selected_provider_classes")
    )
    selected_provider_by_family = {
        family: selected_provider_by_route.get(family)
        or (
            row.get("provider")
            if row.get("selected") is True
            or (
                not providers_from_route
                and row.get("configured") is True
                and selected_provider_classes
            )
            else None
        )
        for family, row in provider_rows
    }
    selected_provider_class_by_family = {
        family: (
            route_entries_by_family.get(family, {}).get("provider_class")
            or (
                row.get("provider_class")
                if selected_provider_by_family.get(family) is not None
                else None
            )
        )
        for family, row in provider_rows
    }
    provider_route_data_mode_by_family = {
        family: route_entries_by_family.get(family, {}).get("data_mode")
        for family, _row in provider_rows
    }
    provider_route_live_data_required_by_family = {
        family: route_entries_by_family.get(family, {}).get(
            "live_data_required"
        )
        is True
        for family, _row in provider_rows
    }
    selected_route_data_modes = [
        data_mode
        for data_mode in provider_route_data_mode_by_family.values()
        if isinstance(data_mode, str)
    ]
    return {
        "schema_version": "api_key_provider_selection_summary.v1",
        "status": provider_route.get("status"),
        "provider_factory": provider_route.get("provider_factory"),
        "selected_provider_classes": selected_provider_classes,
        "selected_provider_class_count": len(selected_provider_classes),
        "configured_provider_families": configured_provider_families,
        "configured_provider_family_count": len(configured_provider_families),
        "missing_provider_families": missing_provider_families,
        "configured_env_keys_by_provider_family": (
            configured_env_keys_by_provider_family
        ),
        "provider_env_key_hints_by_family": provider_env_key_hints_by_family,
        "provider_auto_selects_live_provider_by_family": (
            provider_auto_selects_live_provider_by_family
        ),
        "provider_optional_live_mode_env_by_family": (
            provider_optional_live_mode_env_by_family
        ),
        "provider_live_mode_required_by_family": (
            provider_live_mode_required_by_family
        ),
        "all_configured_auto_select_live_provider": (
            all_configured_auto_select_live_provider
        ),
        "any_live_mode_required": any(
            provider_live_mode_required_by_family.values()
        ),
        "selected_provider_by_family": selected_provider_by_family,
        "selected_provider_class_by_family": selected_provider_class_by_family,
        "provider_route_data_mode_by_family": (
            provider_route_data_mode_by_family
        ),
        "provider_route_live_data_required_by_family": (
            provider_route_live_data_required_by_family
        ),
        "all_selected_routes_live": bool(selected_route_data_modes) and all(
            data_mode == "live" for data_mode in selected_route_data_modes
        ),
        "ready_to_run_live_smoke": (
            provider_route.get("status") == "ready"
            and live_data_setup_summary.get("ready_to_run_live_smoke") is True
        ),
        "network_call": False,
        "mutates_local_state": False,
        "secret_values_returned": False,
    }


def _api_key_integration_status_summary(
    *,
    setup_status_summary: dict[str, Any],
    api_key_next_action_summary: dict[str, Any],
    api_key_pipeline_failure_summary: dict[str, Any],
    api_key_setup_file_summary: dict[str, Any],
    api_key_dotenv_loading_summary: dict[str, Any],
    api_key_provider_selection_summary: dict[str, Any],
    api_key_provider_recovery_summary: dict[str, Any],
) -> dict[str, Any]:
    configured_provider_families = _string_list(
        setup_status_summary.get("configured_provider_families")
    )
    missing_provider_families = _string_list(
        setup_status_summary.get("missing_provider_families")
    )
    selected_provider_classes = _string_list(
        api_key_provider_selection_summary.get("selected_provider_classes")
    )
    selected_provider_class_by_family = _optional_mapping(
        api_key_provider_selection_summary.get("selected_provider_class_by_family")
    ) or {}
    provider_route_data_mode_by_family = _optional_mapping(
        api_key_provider_selection_summary.get("provider_route_data_mode_by_family")
    ) or {}
    provider_route_live_data_required_by_family = _optional_mapping(
        api_key_provider_selection_summary.get(
            "provider_route_live_data_required_by_family"
        )
    ) or {}
    configured_provider_family_count = setup_status_summary.get(
        "configured_provider_family_count"
    )
    required_provider_family_count = setup_status_summary.get(
        "required_provider_family_count"
    )
    selected_provider_class_count = api_key_provider_selection_summary.get(
        "selected_provider_class_count"
    )
    api_keys_configured = (
        isinstance(configured_provider_family_count, int)
        and isinstance(required_provider_family_count, int)
        and required_provider_family_count > 0
        and configured_provider_family_count == required_provider_family_count
        and not missing_provider_families
    )
    live_providers_selected = (
        api_keys_configured
        and selected_provider_class_count == configured_provider_family_count
    )
    ready_to_run_live_smoke = (
        setup_status_summary.get("ready_to_run_live_smoke") is True
        and api_key_provider_selection_summary.get("ready_to_run_live_smoke")
        is True
    )
    summary = {
        "schema_version": "api_key_integration_status_summary.v1",
        "status": api_key_next_action_summary.get("status"),
        "api_keys_configured": api_keys_configured,
        "dotenv_loading_enabled": (
            api_key_dotenv_loading_summary.get("dotenv_loading_enabled") is True
        ),
        "dotenv_target_exists": (
            api_key_setup_file_summary.get("target_exists") is True
        ),
        "live_providers_selected": live_providers_selected,
        "ready_to_run_live_smoke": ready_to_run_live_smoke,
        "configured_provider_families": configured_provider_families,
        "missing_provider_families": missing_provider_families,
        "selected_provider_classes": selected_provider_classes,
        "selected_provider_class_by_family": selected_provider_class_by_family,
        "provider_route_data_mode_by_family": provider_route_data_mode_by_family,
        "provider_route_live_data_required_by_family": (
            provider_route_live_data_required_by_family
        ),
        "all_selected_routes_live": (
            api_key_provider_selection_summary.get("all_selected_routes_live")
            is True
        ),
        "failure_category": api_key_pipeline_failure_summary.get(
            "failure_category"
        ),
        "has_failures": (
            api_key_pipeline_failure_summary.get("has_failures") is True
        ),
        "next_action_name": api_key_next_action_summary.get("next_action_name"),
        "next_action_status": api_key_next_action_summary.get(
            "next_action_status"
        ),
        "next_action_command": api_key_next_action_summary.get(
            "next_action_command"
        ),
        "next_action_is_recovery": (
            api_key_next_action_summary.get("next_action_is_recovery") is True
        ),
        "next_action_network_call": (
            api_key_next_action_summary.get("next_action_network_call") is True
        ),
        "next_action_required_env_keys": _string_list(
            api_key_next_action_summary.get("required_env_keys")
        ),
        "next_action_network_call_policy": api_key_next_action_summary.get(
            "next_action_network_call_policy"
        ),
        "next_action_next_after_action": api_key_next_action_summary.get(
            "next_after_action"
        ),
        "next_action_dotenv_target_path": api_key_next_action_summary.get(
            "dotenv_target_path"
        ),
        "next_action_source_path": api_key_next_action_summary.get(
            "source_path"
        ),
        "next_action_target_path": api_key_next_action_summary.get(
            "target_path"
        ),
        "next_action_secret_input_required": (
            api_key_next_action_summary.get("secret_input_required") is True
        ),
        "next_action_dotenv_examples": _string_list(
            api_key_next_action_summary.get("dotenv_examples")
        ),
        "next_action_dotenv_example_count": (
            api_key_next_action_summary.get("dotenv_example_count")
        ),
        "next_action_mutates_local_state": (
            api_key_next_action_summary.get("next_action_mutates_local_state")
            is True
        ),
        "next_action_secret_values_returned": False,
        "provider_recovery_action_status": (
            api_key_provider_recovery_summary.get(
                "provider_recovery_action_status"
            )
        ),
        "provider_recovery_item_count": (
            api_key_provider_recovery_summary.get("item_count", 0)
        ),
        "provider_recovery_pending_count": (
            api_key_provider_recovery_summary.get(
                "provider_recovery_pending_count",
                0,
            )
        ),
        "provider_recovery_blocked_count": (
            api_key_provider_recovery_summary.get(
                "provider_recovery_blocked_count",
                0,
            )
        ),
        "provider_error_count": (
            api_key_provider_recovery_summary.get("provider_error_count", 0)
        ),
        "provider_recovery_smoke_count": (
            api_key_provider_recovery_summary.get(
                "provider_recovery_smoke_count",
                0,
            )
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
        "network_call": False,
        "mutates_local_state": False,
        "secret_values_returned": False,
    }
    preferred_env_key = api_key_next_action_summary.get("preferred_env_key")
    accepted_env_keys = _string_list(
        api_key_next_action_summary.get("accepted_env_keys")
    )
    next_action_provider_family = api_key_next_action_summary.get(
        "next_action_provider_family"
    )
    next_action_provider = api_key_next_action_summary.get("next_action_provider")
    next_action_smoke_command_name = api_key_next_action_summary.get(
        "next_action_smoke_command_name"
    )
    next_action_expected_live_contract = api_key_next_action_summary.get(
        "next_action_expected_live_contract"
    )
    next_action_expected_live_checks = _string_list(
        api_key_next_action_summary.get("next_action_expected_live_checks")
    )
    if isinstance(next_action_provider_family, str):
        summary["next_action_provider_family"] = next_action_provider_family
    if isinstance(next_action_provider, str):
        summary["next_action_provider"] = next_action_provider
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
    if isinstance(preferred_env_key, str):
        summary["preferred_env_key"] = preferred_env_key
    if accepted_env_keys:
        summary["accepted_env_keys"] = accepted_env_keys
    return summary
