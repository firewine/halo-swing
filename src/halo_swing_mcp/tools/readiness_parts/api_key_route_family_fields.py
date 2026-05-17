"""API-key route-family field projection."""

from __future__ import annotations

from typing import Any

from .contract_checks import _optional_mapping


__all__ = ("_api_key_route_family_fields",)


def _api_key_route_family_fields(
    source_summary: dict[str, Any],
) -> dict[str, Any]:
    return {
        "selected_provider_class_by_family": (
            _optional_mapping(
                source_summary.get("selected_provider_class_by_family")
            )
            or {}
        ),
        "provider_route_data_mode_by_family": (
            _optional_mapping(
                source_summary.get("provider_route_data_mode_by_family")
            )
            or {}
        ),
        "provider_route_live_data_required_by_family": (
            _optional_mapping(
                source_summary.get("provider_route_live_data_required_by_family")
            )
            or {}
        ),
        "all_selected_routes_live": (
            source_summary.get("all_selected_routes_live") is True
        ),
    }
