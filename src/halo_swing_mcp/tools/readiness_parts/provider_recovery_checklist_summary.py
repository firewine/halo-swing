"""API-key provider recovery checklist summary projection."""

from __future__ import annotations

from typing import Any

from .api_key_route_family_fields import _api_key_route_family_fields
from .contract_checks import _optional_mapping


__all__ = ("_api_key_provider_recovery_checklist_summary",)


def _api_key_provider_recovery_checklist_summary(
    api_key_provider_recovery_checklist: dict[str, Any],
) -> dict[str, Any]:
    items = api_key_provider_recovery_checklist.get("items")
    item_rows = (
        [row for row in items if isinstance(row, dict)]
        if isinstance(items, list)
        else []
    )
    next_recovery_action = item_rows[0] if item_rows else {}
    recovery_smoke = _optional_mapping(next_recovery_action.get("recovery_smoke")) or {}
    return {
        "schema_version": "api_key_provider_recovery_checklist_summary.v1",
        "status": api_key_provider_recovery_checklist.get("status"),
        "provider_recovery_required": bool(item_rows),
        "provider_error_count": api_key_provider_recovery_checklist.get(
            "provider_error_count"
        ),
        "provider_recovery_smoke_count": (
            api_key_provider_recovery_checklist.get(
                "provider_recovery_smoke_count"
            )
        ),
        "item_count": api_key_provider_recovery_checklist.get("item_count"),
        "next_recovery_provider_family": next_recovery_action.get(
            "provider_family"
        ),
        "next_recovery_provider": next_recovery_action.get("provider"),
        "next_recovery_smoke_command_name": next_recovery_action.get(
            "smoke_command_name"
        ),
        "next_recovery_smoke_available": (
            next_recovery_action.get("recovery_smoke_available") is True
        ),
        "next_recovery_network_call": recovery_smoke.get("network_call") is True,
        **_api_key_route_family_fields(api_key_provider_recovery_checklist),
        "network_call": False,
        "mutates_local_state": False,
        "secret_values_returned": False,
    }
