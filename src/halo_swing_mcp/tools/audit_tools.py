"""Audit log read tools."""

from __future__ import annotations

from typing import Any

from halo_swing_mcp.audit import audit_summary, read_audit_events


def get_audit_log(
    audit_log_path: str | None = None,
    limit: int = 100,
    action: str | None = None,
    resource_type: str | None = None,
    resource_id: str | None = None,
    outcome: str | None = None,
) -> dict[str, Any]:
    """Return recent structured audit events."""

    events = read_audit_events(
        audit_log_path=audit_log_path,
        limit=limit,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        outcome=outcome,
    )
    return {
        "events": events,
        "count": len(events),
        "live_data_required": False,
    }


def get_audit_summary(audit_log_path: str | None = None) -> dict[str, Any]:
    """Return aggregate audit log counts."""

    summary = audit_summary(audit_log_path=audit_log_path)
    summary["live_data_required"] = False
    return summary
