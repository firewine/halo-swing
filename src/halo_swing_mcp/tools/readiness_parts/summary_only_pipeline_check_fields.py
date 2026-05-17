"""Summary-only pipeline check top-level field projection."""

from __future__ import annotations

from typing import Any

from .contract_checks import _optional_mapping
from .live_data_setup import _string_list


__all__ = ("_api_key_pipeline_check_top_level_fields",)


def _api_key_pipeline_check_top_level_fields(
    api_key_pipeline_check_summary: dict[str, Any],
) -> dict[str, Any]:
    first_failed_check = (
        _optional_mapping(
            api_key_pipeline_check_summary.get("first_failed_check")
        )
        or {}
    )
    return {
        "api_key_check_status": api_key_pipeline_check_summary.get("status"),
        "api_key_check_count": api_key_pipeline_check_summary.get("check_count"),
        "api_key_check_passed_count": api_key_pipeline_check_summary.get(
            "passed_check_count"
        ),
        "api_key_check_failed_count": api_key_pipeline_check_summary.get(
            "failed_check_count"
        ),
        "api_key_check_failed_keys": _string_list(
            api_key_pipeline_check_summary.get("failed_check_keys")
        ),
        "api_key_check_tools_with_failures": _string_list(
            api_key_pipeline_check_summary.get("tools_with_failures")
        ),
        "api_key_check_tool_failure_counts": (
            _optional_mapping(
                api_key_pipeline_check_summary.get("tool_failure_counts")
            )
            or {}
        ),
        "api_key_check_first_failed_tool": first_failed_check.get("tool"),
        "api_key_check_first_failed_name": first_failed_check.get("name"),
        "api_key_check_first_failed_key": first_failed_check.get("key"),
        "api_key_check_first_failed_expected": first_failed_check.get(
            "expected"
        ),
        "api_key_check_first_failed_actual": first_failed_check.get("actual"),
        "api_key_check_first_failed_provider_family": (
            first_failed_check.get("provider_family")
        ),
        "api_key_check_first_failed_provider": first_failed_check.get(
            "provider"
        ),
        "api_key_check_first_failed_smoke_command_name": (
            first_failed_check.get("smoke_command_name")
        ),
        "api_key_check_first_failed_preferred_env_key": (
            first_failed_check.get("preferred_env_key")
        ),
        "api_key_check_first_failed_accepted_env_keys": _string_list(
            first_failed_check.get("accepted_env_keys")
        ),
        "api_key_check_first_failed_secret_values_returned": (
            first_failed_check.get("secret_values_returned") is True
        ),
        "api_key_check_network_call": (
            api_key_pipeline_check_summary.get("network_call") is True
        ),
        "api_key_check_mutates_local_state": (
            api_key_pipeline_check_summary.get("mutates_local_state") is True
        ),
        "api_key_check_secret_values_returned": (
            api_key_pipeline_check_summary.get("secret_values_returned") is True
        ),
    }
