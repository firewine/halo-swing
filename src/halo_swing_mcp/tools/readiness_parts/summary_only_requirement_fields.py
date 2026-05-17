"""Summary-only API-key requirements top-level field projection."""

from __future__ import annotations

from typing import Any

from .live_data_setup import _string_list


__all__ = ("_api_key_requirements_top_level_fields",)


def _api_key_requirements_top_level_fields(
    *,
    api_key_requirements_summary: dict[str, Any],
    provider_requirement_rows: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    required_env_keys = _string_list(
        api_key_requirements_summary.get("required_env_keys")
    )
    configured_env_keys = _string_list(
        api_key_requirements_summary.get("configured_env_keys")
    )
    configured_provider_families = _string_list(
        api_key_requirements_summary.get("configured_provider_families")
    )
    missing_provider_families = _string_list(
        api_key_requirements_summary.get("missing_provider_families")
    )
    provider_requirement_families = list(provider_requirement_rows)
    return {
        "api_key_requirement_schema_version": (
            api_key_requirements_summary.get("schema_version")
        ),
        "api_key_requirement_status": api_key_requirements_summary.get("status"),
        "api_key_required_env_keys": required_env_keys,
        "api_key_required_env_key_count": len(required_env_keys),
        "api_key_configured_env_keys": configured_env_keys,
        "api_key_configured_env_key_count": len(configured_env_keys),
        "api_key_requirement_configured_provider_families": (
            configured_provider_families
        ),
        "api_key_requirement_configured_provider_family_count": len(
            configured_provider_families
        ),
        "api_key_requirement_missing_provider_families": (
            missing_provider_families
        ),
        "api_key_requirement_missing_provider_family_count": len(
            missing_provider_families
        ),
        "api_key_requirement_network_call": (
            api_key_requirements_summary.get("network_call") is True
        ),
        "api_key_requirement_mutates_local_state": (
            api_key_requirements_summary.get("mutates_local_state") is True
        ),
        "api_key_requirement_secret_values_returned": (
            api_key_requirements_summary.get("secret_values_returned") is True
        ),
        "api_key_provider_requirement_families": (
            provider_requirement_families
        ),
        "api_key_provider_requirement_count": len(provider_requirement_families),
        "api_key_provider_requirement_providers": {
            family: row.get("provider")
            for family, row in provider_requirement_rows.items()
        },
        "api_key_provider_requirement_required_env_keys": {
            family: _string_list(row.get("required_env_keys"))
            for family, row in provider_requirement_rows.items()
        },
        "api_key_provider_requirement_preferred_env_keys": {
            family: row.get("preferred_env_key")
            for family, row in provider_requirement_rows.items()
        },
        "api_key_provider_requirement_accepted_env_keys": {
            family: _string_list(row.get("accepted_env_keys"))
            for family, row in provider_requirement_rows.items()
        },
        "api_key_provider_requirement_configured_env_keys": {
            family: _string_list(row.get("configured_env_keys"))
            for family, row in provider_requirement_rows.items()
        },
        "api_key_provider_requirement_missing_env_keys": {
            family: _string_list(row.get("missing_env_keys"))
            for family, row in provider_requirement_rows.items()
        },
        "api_key_provider_requirement_setup_statuses": {
            family: row.get("setup_status")
            for family, row in provider_requirement_rows.items()
        },
        "api_key_provider_requirement_configured": {
            family: row.get("configured") is True
            for family, row in provider_requirement_rows.items()
        },
        "api_key_provider_requirement_next_setup_actions": {
            family: row.get("next_setup_action")
            for family, row in provider_requirement_rows.items()
        },
        "api_key_provider_requirement_smoke_command_names": {
            family: row.get("smoke_command_name")
            for family, row in provider_requirement_rows.items()
        },
        "api_key_provider_requirement_network_calls": {
            family: row.get("network_call") is True
            for family, row in provider_requirement_rows.items()
        },
        "api_key_provider_requirement_mutates_local_state": {
            family: row.get("mutates_local_state") is True
            for family, row in provider_requirement_rows.items()
        },
        "api_key_provider_requirement_secret_values_returned": {
            family: row.get("secret_values_returned") is True
            for family, row in provider_requirement_rows.items()
        },
    }
