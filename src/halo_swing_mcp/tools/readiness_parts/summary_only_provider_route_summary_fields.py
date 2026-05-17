"""Summary-only provider route summary top-level field projection."""

from __future__ import annotations

from typing import Any

from .live_data_setup import _string_list


__all__ = ("_api_key_provider_route_summary_top_level_fields",)


def _api_key_provider_route_summary_top_level_fields(
    provider_route_summary: dict[str, Any],
) -> dict[str, Any]:
    selected_provider_classes = _string_list(
        provider_route_summary.get("selected_provider_classes")
    )
    missing = _string_list(provider_route_summary.get("missing"))
    return {
        "api_key_provider_route_summary_schema_version": (
            provider_route_summary.get("schema_version")
        ),
        "api_key_provider_route_summary_status": provider_route_summary.get(
            "status"
        ),
        "api_key_provider_route_summary_provider_factory": (
            provider_route_summary.get("provider_factory")
        ),
        "api_key_provider_route_summary_selected_provider_classes": (
            selected_provider_classes
        ),
        "api_key_provider_route_summary_selected_provider_class_count": len(
            selected_provider_classes
        ),
        "api_key_provider_route_summary_missing_keys": missing,
        "api_key_provider_route_summary_missing_key_count": len(missing),
        "api_key_provider_route_summary_network_call": (
            provider_route_summary.get("network_call") is True
        ),
        "api_key_provider_route_summary_secret_values_returned": (
            provider_route_summary.get("secret_values_returned") is True
        ),
    }
