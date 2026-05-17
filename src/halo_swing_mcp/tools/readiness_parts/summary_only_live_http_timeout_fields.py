"""Summary-only live HTTP timeout top-level field projection."""

from __future__ import annotations

from typing import Any

from .live_data_setup import _string_list


__all__ = ("_api_key_live_http_timeout_top_level_fields",)


def _api_key_live_http_timeout_top_level_fields(
    api_key_live_http_timeout_summary: dict[str, Any],
) -> dict[str, Any]:
    applies_to = _string_list(api_key_live_http_timeout_summary.get("applies_to"))
    return {
        "api_key_live_http_timeout_seconds": (
            api_key_live_http_timeout_summary.get("timeout_seconds")
        ),
        "api_key_live_http_timeout_env_key": (
            api_key_live_http_timeout_summary.get("env_key")
        ),
        "api_key_live_http_timeout_default_seconds": (
            api_key_live_http_timeout_summary.get("default_timeout_seconds")
        ),
        "api_key_live_http_timeout_applies_to": applies_to,
        "api_key_live_http_timeout_applies_to_count": len(applies_to),
        "api_key_live_http_timeout_network_call": (
            api_key_live_http_timeout_summary.get("network_call") is True
        ),
        "api_key_live_http_timeout_mutates_local_state": (
            api_key_live_http_timeout_summary.get("mutates_local_state") is True
        ),
        "api_key_live_http_timeout_secret_values_returned": (
            api_key_live_http_timeout_summary.get("secret_values_returned")
            is True
        ),
    }
