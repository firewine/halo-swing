"""Audit log read tools."""

from __future__ import annotations

from typing import Any

from halo_swing_mcp.audit import audit_summary, read_audit_events


AUDIT_LOG_SCHEMA_VERSION = "audit_log.v1"
AUDIT_SUMMARY_SCHEMA_VERSION = "audit_summary.v1"


def get_audit_log(
    audit_log_path: str | None = None,
    limit: int = 100,
    action: str | None = None,
    resource_type: str | None = None,
    resource_id: str | None = None,
    outcome: str | None = None,
) -> dict[str, Any]:
    """Return recent structured audit events."""

    normalized_audit_log_path = _normalize_optional_audit_path(
        audit_log_path,
        "audit_log_path",
    )
    normalized_limit = _normalize_audit_limit(limit)
    normalized_action = _normalize_optional_audit_filter(action, "action")
    normalized_resource_type = _normalize_optional_audit_filter(
        resource_type,
        "resource_type",
    )
    normalized_resource_id = _normalize_optional_audit_filter(
        resource_id,
        "resource_id",
    )
    normalized_outcome = _normalize_optional_audit_filter(outcome, "outcome")
    events = read_audit_events(
        audit_log_path=normalized_audit_log_path,
        limit=normalized_limit,
        action=normalized_action,
        resource_type=normalized_resource_type,
        resource_id=normalized_resource_id,
        outcome=normalized_outcome,
    )
    return {
        "schema_version": AUDIT_LOG_SCHEMA_VERSION,
        "events": events,
        "count": len(events),
        "filters": {
            "action": normalized_action,
            "resource_type": normalized_resource_type,
            "resource_id": normalized_resource_id,
            "outcome": normalized_outcome,
            "limit": normalized_limit,
        },
        "network_call": False,
        "secret_values_returned": False,
        "live_data_required": False,
    }


def get_audit_summary(audit_log_path: str | None = None) -> dict[str, Any]:
    """Return aggregate audit log counts."""

    normalized_audit_log_path = _normalize_optional_audit_path(
        audit_log_path,
        "audit_log_path",
    )
    summary = audit_summary(audit_log_path=normalized_audit_log_path)
    summary["schema_version"] = AUDIT_SUMMARY_SCHEMA_VERSION
    summary["network_call"] = False
    summary["secret_values_returned"] = False
    summary["live_data_required"] = False
    return summary


def _normalize_audit_limit(limit: int) -> int:
    if not isinstance(limit, int) or isinstance(limit, bool):
        raise ValueError("limit must be a positive integer")
    if limit <= 0:
        raise ValueError("limit must be a positive integer")
    return min(limit, 1000)


def _normalize_optional_audit_filter(value: str | None, field_name: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be a string when provided")
    if not _has_no_control_characters(value):
        raise ValueError(f"{field_name} must not contain control characters")
    normalized = value.strip()
    return normalized or None


def _normalize_optional_audit_path(value: str | None, field_name: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be a nonempty string")
    if not _has_no_control_characters(value):
        raise ValueError(f"{field_name} must not contain control characters")
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{field_name} must be a nonempty string")
    return normalized


def _has_no_control_characters(value: str) -> bool:
    return all(ord(character) >= 32 and ord(character) != 127 for character in value)
