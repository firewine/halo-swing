"""Summary-only pipeline route-family top-level field projection."""

from __future__ import annotations

from typing import Any

from .summary_only_provider_route_fields import (
    _route_family_summary_top_level_fields,
)


__all__ = ("_api_key_pipeline_route_top_level_fields",)


def _api_key_pipeline_route_top_level_fields(
    *,
    api_key_pipeline_stage_summary: dict[str, Any],
    api_key_pipeline_check_summary: dict[str, Any],
) -> dict[str, Any]:
    return {
        **_route_family_summary_top_level_fields(
            prefix="api_key_stage",
            source_summary=api_key_pipeline_stage_summary,
        ),
        **_route_family_summary_top_level_fields(
            prefix="api_key_check",
            source_summary=api_key_pipeline_check_summary,
        ),
    }
