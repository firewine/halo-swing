"""Summary-only provider-selection top-level field projection."""

from __future__ import annotations

from typing import Any

from .contract_checks import _optional_mapping
from .live_data_setup import _string_list


__all__ = ("_api_key_provider_selection_top_level_fields",)


def _api_key_provider_selection_top_level_fields(
    api_key_provider_selection_summary: dict[str, Any],
) -> dict[str, Any]:
    return {
        "api_key_provider_selection_status": (
            api_key_provider_selection_summary.get("status")
        ),
        "api_key_provider_factory": (
            api_key_provider_selection_summary.get("provider_factory")
        ),
        "api_key_selected_provider_classes": _string_list(
            api_key_provider_selection_summary.get("selected_provider_classes")
        ),
        "api_key_selected_provider_class_count": (
            api_key_provider_selection_summary.get("selected_provider_class_count")
        ),
        "api_key_selected_provider_by_family": _optional_mapping(
            api_key_provider_selection_summary.get("selected_provider_by_family")
        )
        or {},
        "api_key_configured_env_keys_by_provider_family": _optional_mapping(
            api_key_provider_selection_summary.get(
                "configured_env_keys_by_provider_family"
            )
        )
        or {},
        "api_key_provider_env_key_hints_by_family": _optional_mapping(
            api_key_provider_selection_summary.get(
                "provider_env_key_hints_by_family"
            )
        )
        or {},
        "api_key_provider_auto_selects_live_provider_by_family": (
            _optional_mapping(
                api_key_provider_selection_summary.get(
                    "provider_auto_selects_live_provider_by_family"
                )
            )
            or {}
        ),
        "api_key_provider_optional_live_mode_env_by_family": (
            _optional_mapping(
                api_key_provider_selection_summary.get(
                    "provider_optional_live_mode_env_by_family"
                )
            )
            or {}
        ),
        "api_key_provider_live_mode_required_by_family": (
            _optional_mapping(
                api_key_provider_selection_summary.get(
                    "provider_live_mode_required_by_family"
                )
            )
            or {}
        ),
        "api_key_provider_all_configured_auto_select_live_provider": (
            api_key_provider_selection_summary.get(
                "all_configured_auto_select_live_provider"
            )
            is True
        ),
        "api_key_provider_any_live_mode_required": (
            api_key_provider_selection_summary.get("any_live_mode_required")
            is True
        ),
    }
