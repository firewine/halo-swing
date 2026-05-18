# ruff: noqa: F403,F405,F821
"""Live Data Setup readiness implementation."""

from __future__ import annotations

from .context import *


__all__ = ('_live_data_setup_summary', '_live_data_provider_family_summary', '_live_data_provider_setup_actions', '_live_data_provider_setup_actions_from_providers', '_live_data_provider_smoke_plan', '_string_list', '_ordered_unique_strings', '_live_data_dotenv_template', '_live_data_dotenv_examples', '_live_data_dotenv_file_status', '_live_data_setup_steps', '_live_data_next_operator_action')


_LIVE_PROVIDER_CLASS_BY_FAMILY = {
    "market": "PolygonMarketDataProvider",
    "macro": "FredMacroDataProvider",
    "news": "NewsApiDataProvider",
}


def _live_data_setup_summary(
    api_key_status: dict[str, Any],
    provider_route: dict[str, Any],
) -> dict[str, Any]:
    providers = _optional_mapping(api_key_status.get("providers")) or {}
    configured_provider_families = [
        family
        for family, provider in providers.items()
        if _optional_mapping(provider).get("configured") is True
    ]
    route_summary = _api_key_pipeline_provider_route_summary(provider_route)
    raw_route_entries = provider_route.get("route")
    route_entries = (
        [entry for entry in raw_route_entries if isinstance(entry, dict)]
        if isinstance(raw_route_entries, list)
        else []
    )
    route_entries_by_family = {
        entry.get("provider_family"): entry
        for entry in route_entries
        if isinstance(entry.get("provider_family"), str)
    }
    selected_provider_class_by_family = {
        family: route_entries_by_family.get(family, {}).get("provider_class")
        for family in providers
    }
    provider_route_data_mode_by_family = {
        family: route_entries_by_family.get(family, {}).get("data_mode")
        for family in providers
    }
    provider_route_live_data_required_by_family = {
        family: (
            route_entries_by_family.get(family, {}).get("live_data_required") is True
        )
        for family in providers
    }
    selected_route_data_modes = [
        data_mode
        for data_mode in provider_route_data_mode_by_family.values()
        if data_mode is not None
    ]
    missing = _ordered_unique_strings(
        [
            *(api_key_status.get("missing") or []),
            *(provider_route.get("missing") or []),
        ]
    )
    ready_to_run_live_smoke = (
        api_key_status.get("status") == "ready"
        and provider_route.get("status") == "ready"
    )
    provider_family_summary = _live_data_provider_family_summary(
        api_key_status=api_key_status,
        ready_to_run_live_smoke=ready_to_run_live_smoke,
    )
    dotenv_file_status = _live_data_dotenv_file_status()
    one_shot_smoke_command = api_key_status.get("one_shot_smoke_command")
    provider_setup_actions = _live_data_provider_setup_actions(
        api_key_status,
        selected_provider_class_by_family=selected_provider_class_by_family,
        provider_route_data_mode_by_family=provider_route_data_mode_by_family,
        provider_route_live_data_required_by_family=(
            provider_route_live_data_required_by_family
        ),
    )
    provider_smoke_plan = _live_data_provider_smoke_plan(
        provider_setup_actions=provider_setup_actions,
        one_shot_smoke_command=one_shot_smoke_command,
        ready_to_run_live_smoke=ready_to_run_live_smoke,
    )
    live_data_setup_steps = _live_data_setup_steps(
        dotenv_file_status=dotenv_file_status,
        provider_family_summary=provider_family_summary,
        provider_smoke_plan=provider_smoke_plan,
        one_shot_smoke_command=one_shot_smoke_command,
        ready_to_run_live_smoke=ready_to_run_live_smoke,
    )
    return {
        "schema_version": "live_data_setup_summary.v1",
        "status": "ready" if ready_to_run_live_smoke else "blocked",
        "ready_to_run_live_smoke": ready_to_run_live_smoke,
        "api_key_status": api_key_status.get("status"),
        "provider_route_status": provider_route.get("status"),
        "configured_provider_families": configured_provider_families,
        "provider_family_summary": provider_family_summary,
        "provider_setup_actions": provider_setup_actions,
        "provider_smoke_plan": provider_smoke_plan,
        "missing": missing,
        "provider_factory": route_summary.get("provider_factory"),
        "selected_provider_classes": route_summary.get("selected_provider_classes"),
        "selected_provider_class_by_family": selected_provider_class_by_family,
        "provider_route_data_mode_by_family": provider_route_data_mode_by_family,
        "provider_route_live_data_required_by_family": (
            provider_route_live_data_required_by_family
        ),
        "all_selected_routes_live": bool(selected_route_data_modes)
        and all(data_mode == "live" for data_mode in selected_route_data_modes),
        "provider_route_summary": route_summary,
        "dotenv_template": _live_data_dotenv_template(),
        "dotenv_file_status": dotenv_file_status,
        "live_data_setup_steps": live_data_setup_steps,
        "next_operator_action": _live_data_next_operator_action(
            dotenv_file_status=dotenv_file_status,
            provider_family_summary=provider_family_summary,
            live_data_setup_steps=live_data_setup_steps,
            one_shot_smoke_command=one_shot_smoke_command,
            ready_to_run_live_smoke=ready_to_run_live_smoke,
        ),
        "one_shot_smoke_command": one_shot_smoke_command,
        "next_smoke_command": _local_command(
            "run_api_key_pipeline_smoke"
            if ready_to_run_live_smoke
            else "get_live_data_api_key_status"
        ),
        "network_call": False,
        "mutates_local_state": False,
        "secret_values_returned": False,
    }


def _live_data_provider_family_summary(
    *,
    api_key_status: dict[str, Any],
    ready_to_run_live_smoke: bool,
) -> dict[str, Any]:
    providers = _optional_mapping(api_key_status.get("providers")) or {}
    summary = _optional_mapping(api_key_status.get("provider_family_summary")) or {}
    required_provider_families = _string_list(
        summary.get("required_provider_families")
    ) or list(providers)
    configured_provider_families = _string_list(
        summary.get("configured_provider_families")
    ) or [
        family
        for family, provider in providers.items()
        if _optional_mapping(provider).get("configured") is True
    ]
    missing_provider_families = _string_list(
        summary.get("missing_provider_families")
    ) or [
        family
        for family in required_provider_families
        if family not in configured_provider_families
    ]
    return {
        "required_provider_families": required_provider_families,
        "configured_provider_families": configured_provider_families,
        "missing_provider_families": missing_provider_families,
        "configured_count": len(configured_provider_families),
        "required_count": len(required_provider_families),
        "ready_to_run_live_smoke": ready_to_run_live_smoke,
        "network_call": False,
        "mutates_local_state": False,
        "secret_values_returned": False,
    }


def _live_data_provider_setup_actions(
    api_key_status: dict[str, Any],
    *,
    selected_provider_class_by_family: dict[str, Any] | None = None,
    provider_route_data_mode_by_family: dict[str, Any] | None = None,
    provider_route_live_data_required_by_family: dict[str, Any] | None = None,
) -> dict[str, dict[str, Any]]:
    providers = _optional_mapping(api_key_status.get("providers")) or {}
    return _live_data_provider_setup_actions_from_providers(
        providers,
        selected_provider_class_by_family=selected_provider_class_by_family,
        provider_route_data_mode_by_family=provider_route_data_mode_by_family,
        provider_route_live_data_required_by_family=(
            provider_route_live_data_required_by_family
        ),
    )


def _live_data_provider_setup_actions_from_providers(
    providers: dict[str, Any],
    *,
    selected_provider_class_by_family: dict[str, Any] | None = None,
    provider_route_data_mode_by_family: dict[str, Any] | None = None,
    provider_route_live_data_required_by_family: dict[str, Any] | None = None,
) -> dict[str, dict[str, Any]]:
    actions: dict[str, dict[str, Any]] = {}
    selected_provider_class_by_family = selected_provider_class_by_family or {}
    provider_route_data_mode_by_family = provider_route_data_mode_by_family or {}
    provider_route_live_data_required_by_family = (
        provider_route_live_data_required_by_family or {}
    )
    for provider_family, raw_provider_status in providers.items():
        provider_status = _optional_mapping(raw_provider_status) or {}
        smoke_command = _optional_mapping(provider_status.get("smoke_command")) or {}
        configured = provider_status.get("configured") is True
        selected_provider_class = _provider_route_value(
            selected_provider_class_by_family,
            provider_family,
            _LIVE_PROVIDER_CLASS_BY_FAMILY.get(provider_family)
            if configured
            else None,
        )
        provider_route_data_mode = _provider_route_value(
            provider_route_data_mode_by_family,
            provider_family,
            "live" if configured else None,
        )
        provider_route_live_data_required = _provider_route_value(
            provider_route_live_data_required_by_family,
            provider_family,
            configured,
        )
        actions[provider_family] = {
            "provider": provider_status.get("provider"),
            "configured": configured,
            "configured_env_keys": provider_status.get("configured_env_keys"),
            "preferred_env_key": provider_status.get("preferred_env_key"),
            "accepted_env_keys": provider_status.get("accepted_env_keys"),
            "auto_selects_live_provider": provider_status.get(
                "auto_selects_live_provider"
            ),
            "live_mode_required": provider_status.get("live_mode_required"),
            "optional_live_mode_env": provider_status.get("optional_live_mode_env"),
            "setup_status": provider_status.get("setup_status"),
            "next_setup_action": provider_status.get("next_setup_action"),
            "selected_provider_class": selected_provider_class,
            "provider_route_data_mode": provider_route_data_mode,
            "provider_route_live_data_required": (
                provider_route_live_data_required is True
            ),
            "dotenv_target_path": provider_status.get("dotenv_target_path"),
            "example": provider_status.get("example"),
            "smoke_command_name": smoke_command.get("name"),
            "smoke_command": smoke_command,
            "network_call": False,
            "mutates_local_state": False,
            "secret_values_returned": False,
        }
    return actions


def _provider_route_value(
    values_by_family: dict[str, Any],
    provider_family: str,
    fallback: Any,
) -> Any:
    if provider_family in values_by_family:
        return values_by_family.get(provider_family)
    return fallback


def _live_data_provider_smoke_plan(
    *,
    provider_setup_actions: dict[str, dict[str, Any]],
    one_shot_smoke_command: Any,
    ready_to_run_live_smoke: bool,
) -> dict[str, Any]:
    provider_smokes: list[dict[str, Any]] = []
    for provider_family, action in provider_setup_actions.items():
        smoke_command = _optional_mapping(action.get("smoke_command")) or {}
        configured = action.get("configured") is True
        provider_smokes.append(
            {
                "provider_family": provider_family,
                "provider": action.get("provider"),
                "status": "ready" if configured else "blocked",
                "preferred_env_key": action.get("preferred_env_key"),
                "accepted_env_keys": _string_list(action.get("accepted_env_keys")),
                "next_setup_action": action.get("next_setup_action"),
                "selected_provider_class": action.get("selected_provider_class"),
                "provider_route_data_mode": action.get("provider_route_data_mode"),
                "provider_route_live_data_required": (
                    action.get("provider_route_live_data_required") is True
                ),
                "smoke_command_name": smoke_command.get("name"),
                "command": smoke_command.get("command"),
                "network_call": True,
                "expected_live_contract": smoke_command.get(
                    "expected_live_contract"
                ),
                "expected_live_checks": smoke_command.get("expected_live_checks"),
                "network_call_policy": smoke_command.get("network_call_policy"),
                "mutates_local_state": False,
                "secret_values_returned": False,
            }
        )
    ready_provider_smoke_count = sum(
        1 for provider_smoke in provider_smokes if provider_smoke["status"] == "ready"
    )
    one_shot_command = _optional_mapping(one_shot_smoke_command) or {}
    return {
        "schema_version": "live_data_provider_smoke_plan.v1",
        "provider_smokes": provider_smokes,
        "provider_smoke_count": len(provider_smokes),
        "ready_provider_smoke_count": ready_provider_smoke_count,
        "blocked_provider_smoke_count": len(provider_smokes)
        - ready_provider_smoke_count,
        "one_shot_pipeline_smoke": {
            "name": one_shot_command.get("name"),
            "status": "ready" if ready_to_run_live_smoke else "blocked",
            "command": one_shot_command.get("command"),
            "network_call": one_shot_command.get("network_call"),
            "network_call_policy": one_shot_command.get("network_call_policy"),
            "mutates_local_state": one_shot_command.get("mutates_local_state"),
            "secret_values_returned": one_shot_command.get(
                "secret_values_returned"
            ),
        },
        "network_call": False,
        "mutates_local_state": False,
        "secret_values_returned": False,
    }


def _string_list(values: Any) -> list[str]:
    if not isinstance(values, list):
        return []
    return [value for value in values if isinstance(value, str)]


def _ordered_unique_strings(values: list[Any]) -> list[str]:
    result: list[str] = []
    for value in values:
        if not isinstance(value, str) or value in result:
            continue
        result.append(value)
    return result


def _live_data_dotenv_template() -> dict[str, Any]:
    return {
        "schema_version": "live_data_dotenv_template.v1",
        "target_path": ".env",
        "source_path": ".env.example",
        "entries": [
            {
                "provider_family": "market",
                "provider": "polygon",
                "preferred_env_key": "POLYGON_API_KEY",
                "accepted_env_keys": [
                    "HALO_SWING_MARKET_DATA_API_KEY",
                    "POLYGON_API_KEY",
                ],
                "example": "POLYGON_API_KEY=your_polygon_key",
                "secret": True,
            },
            {
                "provider_family": "macro",
                "provider": "fred",
                "preferred_env_key": "FRED_API_KEY",
                "accepted_env_keys": [
                    "HALO_SWING_MACRO_API_KEY",
                    "HALO_SWING_FRED_API_KEY",
                    "FRED_API_KEY",
                ],
                "example": "FRED_API_KEY=your_fred_key",
                "secret": True,
            },
            {
                "provider_family": "news",
                "provider": "newsapi",
                "preferred_env_key": "NEWS_API_KEY",
                "accepted_env_keys": [
                    "HALO_SWING_NEWS_API_KEY",
                    "NEWS_API_KEY",
                    "NEWSAPI_KEY",
                ],
                "example": "NEWS_API_KEY=your_newsapi_key",
                "secret": True,
            },
        ],
        "network_call": False,
        "mutates_local_state": False,
        "secret_values_returned": False,
    }


def _live_data_dotenv_examples() -> list[str]:
    template = _live_data_dotenv_template()
    entries = template.get("entries")
    template_entries = entries if isinstance(entries, list) else []
    return [
        entry["example"]
        for entry in template_entries
        if isinstance(entry, dict) and isinstance(entry.get("example"), str)
    ]


def _live_data_dotenv_file_status() -> dict[str, Any]:
    target_path = local_env.REPO_ROOT_ENV_PATH
    source_path = target_path.with_name(".env.example")
    target_exists = target_path.is_file()
    source_exists = source_path.is_file()
    copy_required = source_exists and not target_exists
    next_action = (
        "copy_env_example_to_env"
        if copy_required
        else "fill_live_data_api_keys"
        if target_exists
        else "restore_env_example"
    )
    return {
        "schema_version": "live_data_dotenv_file_status.v1",
        "target_path": ".env",
        "source_path": ".env.example",
        "target_exists": target_exists,
        "source_exists": source_exists,
        "copy_required": copy_required,
        "next_action": next_action,
        "copy_command": {
            "name": "copy_env_example_to_env",
            "command": "cp .env.example .env",
            "required": copy_required,
            "source_path": ".env.example",
            "target_path": ".env",
            "network_call": False,
            "mutates_local_state": True,
            "secret_values_returned": False,
        },
        "fill_keys_after_copy": {
            "required_env_keys": ["POLYGON_API_KEY", "FRED_API_KEY", "NEWS_API_KEY"],
            "secret": True,
            "secret_values_returned": False,
        },
        "mutation": False,
        "network_call": False,
        "mutates_local_state": False,
        "secret_values_returned": False,
    }


def _live_data_setup_steps(
    *,
    dotenv_file_status: dict[str, Any],
    provider_family_summary: dict[str, Any],
    provider_smoke_plan: dict[str, Any],
    one_shot_smoke_command: Any,
    ready_to_run_live_smoke: bool,
) -> dict[str, Any]:
    smoke_command = _optional_mapping(one_shot_smoke_command)
    raw_provider_smokes = provider_smoke_plan.get("provider_smokes")
    provider_smokes = raw_provider_smokes if isinstance(raw_provider_smokes, list) else []
    dotenv_examples = _live_data_dotenv_examples()
    next_provider_smoke = _next_ready_provider_smoke(provider_smokes)
    target_exists = dotenv_file_status.get("target_exists") is True
    source_exists = dotenv_file_status.get("source_exists") is True
    copy_required = dotenv_file_status.get("copy_required") is True
    configured_count = provider_family_summary.get("configured_count")
    required_count = provider_family_summary.get("required_count")
    keys_ready = (
        isinstance(configured_count, int)
        and isinstance(required_count, int)
        and required_count > 0
        and configured_count == required_count
    )
    if not source_exists and not target_exists and not keys_ready:
        next_step = "restore_env_example"
        dotenv_status = "blocked"
    elif copy_required and not keys_ready:
        next_step = "prepare_dotenv"
        dotenv_status = "pending"
    else:
        dotenv_status = "ready"
        next_step = (
            "run_provider_smokes"
            if ready_to_run_live_smoke
            else "fill_live_data_api_keys"
        )
    return {
        "schema_version": "live_data_setup_steps.v1",
        "next_step": next_step,
        "steps": [
            {
                "name": "prepare_dotenv",
                "status": dotenv_status,
                "next_action": dotenv_file_status.get("next_action"),
                "copy_command": dotenv_file_status.get("copy_command"),
                "network_call": False,
                "mutates_local_state": False,
                "secret_values_returned": False,
            },
            {
                "name": "fill_live_data_api_keys",
                "status": "ready" if keys_ready else "pending",
                "configured_provider_families": provider_family_summary.get(
                    "configured_provider_families"
                ),
                "missing_provider_families": provider_family_summary.get(
                    "missing_provider_families"
                ),
                "configured_count": configured_count,
                "required_count": required_count,
                "required_env_keys": dotenv_file_status.get(
                    "fill_keys_after_copy",
                    {},
                ).get("required_env_keys"),
                "dotenv_examples": dotenv_examples,
                "dotenv_example_count": len(dotenv_examples),
                "network_call": False,
                "mutates_local_state": False,
                "secret_values_returned": False,
            },
            {
                "name": "run_provider_smokes",
                "status": "ready" if ready_to_run_live_smoke else "blocked",
                "provider_smokes": provider_smokes,
                "provider_smoke_count": len(provider_smokes),
                "next_provider_smoke": next_provider_smoke,
                "next_provider_smoke_command_name": next_provider_smoke.get(
                    "smoke_command_name"
                )
                if next_provider_smoke
                else None,
                "ready_provider_smoke_count": provider_smoke_plan.get(
                    "ready_provider_smoke_count"
                ),
                "blocked_provider_smoke_count": provider_smoke_plan.get(
                    "blocked_provider_smoke_count"
                ),
                "network_call": True,
                "network_call_policy": (
                    "only_when_matching_api_key_selects_live_provider"
                ),
                "mutates_local_state": False,
                "secret_values_returned": False,
            },
            {
                "name": "run_api_key_pipeline_smoke",
                "status": "ready" if ready_to_run_live_smoke else "blocked",
                "command": smoke_command.get("command"),
                "network_call": smoke_command.get("network_call"),
                "mutates_local_state": smoke_command.get("mutates_local_state"),
                "secret_values_returned": smoke_command.get(
                    "secret_values_returned"
                ),
            },
        ],
        "network_call": False,
        "mutates_local_state": False,
        "secret_values_returned": False,
    }


def _live_data_next_operator_action(
    *,
    dotenv_file_status: dict[str, Any],
    provider_family_summary: dict[str, Any],
    live_data_setup_steps: dict[str, Any],
    one_shot_smoke_command: Any,
    ready_to_run_live_smoke: bool,
) -> dict[str, Any]:
    next_step = str(live_data_setup_steps.get("next_step") or "")
    copy_command = _optional_mapping(dotenv_file_status.get("copy_command")) or {}
    smoke_command = _optional_mapping(one_shot_smoke_command) or {}
    setup_step_rows = live_data_setup_steps.get("steps")
    setup_steps = setup_step_rows if isinstance(setup_step_rows, list) else []
    provider_smoke_step: dict[str, Any] = {}
    fill_key_step: dict[str, Any] = {}
    for step in setup_steps:
        step_mapping = _optional_mapping(step)
        if step_mapping is None:
            continue
        if step_mapping.get("name") == "run_provider_smokes":
            provider_smoke_step = step_mapping
        if step_mapping.get("name") == "fill_live_data_api_keys":
            fill_key_step = step_mapping
    base = {
        "schema_version": "live_data_next_operator_action.v1",
        "name": next_step,
        "dotenv_target_path": ".env",
        "network_call": False,
        "mutates_local_state": False,
        "secret_values_returned": False,
    }
    if next_step == "restore_env_example":
        return {
            **base,
            "status": "blocked",
            "reason": "missing_env_example_and_env",
            "required_file": ".env.example",
            "secret_input_required": False,
        }
    if next_step == "prepare_dotenv":
        return {
            **base,
            "status": "pending",
            "command": copy_command.get("command"),
            "source_path": copy_command.get("source_path"),
            "target_path": copy_command.get("target_path"),
            "next_after_action": "fill_live_data_api_keys",
            "secret_input_required": False,
            "mutates_local_state": True,
        }
    if next_step == "run_provider_smokes":
        return {
            **base,
            "status": "ready",
            "provider_smokes": provider_smoke_step.get("provider_smokes", []),
            "provider_smoke_count": provider_smoke_step.get("provider_smoke_count"),
            "next_provider_smoke": provider_smoke_step.get("next_provider_smoke"),
            "next_provider_smoke_command_name": provider_smoke_step.get(
                "next_provider_smoke_command_name"
            ),
            "ready_provider_smoke_count": provider_smoke_step.get(
                "ready_provider_smoke_count"
            ),
            "blocked_provider_smoke_count": provider_smoke_step.get(
                "blocked_provider_smoke_count"
            ),
            "network_call": True,
            "network_call_policy": provider_smoke_step.get("network_call_policy"),
            "next_after_action": "run_api_key_pipeline_smoke",
            "secret_input_required": False,
        }
    if ready_to_run_live_smoke:
        return {
            **base,
            "name": "run_api_key_pipeline_smoke",
            "status": "ready",
            "command": smoke_command.get("command"),
            "network_call": bool(smoke_command.get("network_call")),
            "network_call_policy": smoke_command.get("network_call_policy"),
            "secret_input_required": False,
        }
    return {
        **base,
        "name": "fill_live_data_api_keys",
        "status": "pending",
        "required_env_keys": ["POLYGON_API_KEY", "FRED_API_KEY", "NEWS_API_KEY"],
        "dotenv_examples": _string_list(fill_key_step.get("dotenv_examples")),
        "dotenv_example_count": fill_key_step.get("dotenv_example_count"),
        "configured_provider_families": provider_family_summary.get(
            "configured_provider_families",
            [],
        ),
        "missing_provider_families": provider_family_summary.get(
            "missing_provider_families",
            [],
        ),
        "next_after_action": "run_provider_smokes",
        "secret_input_required": True,
    }
