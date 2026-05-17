"""Summary-only provider setup/recovery route-family field projection."""

from __future__ import annotations

from typing import Any

from .contract_checks import _optional_mapping


__all__ = (
    "_api_key_provider_recovery_route_top_level_fields",
    "_api_key_requirement_route_top_level_fields",
)


def _api_key_requirement_route_top_level_fields(
    api_key_requirements_summary: dict[str, Any],
) -> dict[str, Any]:
    return _route_family_top_level_fields(
        prefix="api_key_requirement",
        source_summary=api_key_requirements_summary,
    )


def _api_key_provider_recovery_route_top_level_fields(
    api_key_provider_recovery_summary: dict[str, Any],
) -> dict[str, Any]:
    return _route_family_top_level_fields(
        prefix="api_key_provider_recovery",
        source_summary=api_key_provider_recovery_summary,
    )


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
