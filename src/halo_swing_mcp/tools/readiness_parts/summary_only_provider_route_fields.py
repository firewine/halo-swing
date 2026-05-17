"""Summary-only provider setup/recovery route-family field projection."""

from __future__ import annotations

from typing import Any

from .contract_checks import _optional_mapping


__all__ = (
    "_api_key_provider_recovery_checklist_route_top_level_fields",
    "_api_key_provider_recovery_route_top_level_fields",
    "_api_key_readiness_route_top_level_fields",
    "_api_key_requirement_route_top_level_fields",
    "_api_key_setup_route_top_level_fields",
)


def _api_key_requirement_route_top_level_fields(
    api_key_requirements_summary: dict[str, Any],
) -> dict[str, Any]:
    prefix = "api_key_requirement"
    return {
        **_route_family_top_level_fields(
            prefix=prefix,
            source_summary=api_key_requirements_summary,
        ),
        **_route_family_count_top_level_fields(
            prefix=prefix,
            source_summary=api_key_requirements_summary,
        ),
    }


def _api_key_setup_route_top_level_fields(
    setup_status_summary: dict[str, Any],
) -> dict[str, Any]:
    return {
        **_route_family_top_level_fields(
            prefix="api_key_setup",
            source_summary=setup_status_summary,
        ),
        **_route_family_count_top_level_fields(
            prefix="api_key_setup",
            source_summary=setup_status_summary,
        ),
    }


def _api_key_readiness_route_top_level_fields(
    readiness_summary: dict[str, Any],
) -> dict[str, Any]:
    return {
        **_route_family_top_level_fields(
            prefix="api_key_readiness",
            source_summary=readiness_summary,
        ),
        **_route_family_count_top_level_fields(
            prefix="api_key_readiness",
            source_summary=readiness_summary,
        ),
    }


def _api_key_provider_recovery_route_top_level_fields(
    api_key_provider_recovery_summary: dict[str, Any],
) -> dict[str, Any]:
    return {
        **_route_family_top_level_fields(
            prefix="api_key_provider_recovery",
            source_summary=api_key_provider_recovery_summary,
        ),
        **_route_family_count_top_level_fields(
            prefix="api_key_provider_recovery",
            source_summary=api_key_provider_recovery_summary,
        ),
    }


def _api_key_provider_recovery_checklist_route_top_level_fields(
    api_key_provider_recovery_checklist_summary: dict[str, Any],
) -> dict[str, Any]:
    return {
        **_route_family_top_level_fields(
            prefix="api_key_provider_recovery_checklist",
            source_summary=api_key_provider_recovery_checklist_summary,
        ),
        **_route_family_count_top_level_fields(
            prefix="api_key_provider_recovery_checklist",
            source_summary=api_key_provider_recovery_checklist_summary,
        ),
    }


def _route_family_top_level_fields(
    *,
    prefix: str,
    source_summary: dict[str, Any],
) -> dict[str, Any]:
    return {
        f"{prefix}_selected_provider_class_by_family": (
            _optional_mapping(
                source_summary.get("selected_provider_class_by_family")
            )
            or {}
        ),
        f"{prefix}_provider_route_data_mode_by_family": (
            _optional_mapping(
                source_summary.get("provider_route_data_mode_by_family")
            )
            or {}
        ),
        f"{prefix}_provider_route_live_data_required_by_family": (
            _optional_mapping(
                source_summary.get("provider_route_live_data_required_by_family")
            )
            or {}
        ),
        f"{prefix}_all_selected_routes_live": (
            source_summary.get("all_selected_routes_live") is True
        ),
    }


def _route_family_count_top_level_fields(
    *,
    prefix: str,
    source_summary: dict[str, Any],
) -> dict[str, Any]:
    selected_provider_class_by_family = (
        _optional_mapping(source_summary.get("selected_provider_class_by_family"))
        or {}
    )
    provider_route_data_mode_by_family = (
        _optional_mapping(source_summary.get("provider_route_data_mode_by_family"))
        or {}
    )
    provider_route_live_data_required_by_family = (
        _optional_mapping(
            source_summary.get("provider_route_live_data_required_by_family")
        )
        or {}
    )
    provider_route_data_mode_counts: dict[str, int] = {}
    for data_mode in provider_route_data_mode_by_family.values():
        if isinstance(data_mode, str) and data_mode:
            provider_route_data_mode_counts[data_mode] = (
                provider_route_data_mode_counts.get(data_mode, 0) + 1
            )
    provider_route_families = (
        set(selected_provider_class_by_family)
        | set(provider_route_data_mode_by_family)
        | set(provider_route_live_data_required_by_family)
    )
    return {
        f"{prefix}_provider_route_family_count": len(provider_route_families),
        f"{prefix}_selected_provider_family_count": sum(
            1
            for selected_provider_class in selected_provider_class_by_family.values()
            if isinstance(selected_provider_class, str)
            and bool(selected_provider_class)
        ),
        f"{prefix}_provider_route_live_data_required_family_count": sum(
            1
            for live_data_required in (
                provider_route_live_data_required_by_family.values()
            )
            if live_data_required is True
        ),
        f"{prefix}_provider_route_data_mode_counts": provider_route_data_mode_counts,
    }
