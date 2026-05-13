"""Append-only audit log helpers for Halo Swing tool execution."""

from __future__ import annotations

import hashlib
import json
import os
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from halo_swing_mcp.config import get_settings


SCHEMA_VERSION = "audit.v1"
SENSITIVE_KEY_PARTS = (
    "api_key",
    "apikey",
    "authorization",
    "cookie",
    "credential",
    "password",
    "passphrase",
    "secret",
    "token",
)
MAX_DETAIL_STRING_LENGTH = 500


def utc_now() -> str:
    """Return current UTC time in ISO-8601 Z format."""

    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def resolve_audit_log_path(audit_log_path: str | None = None) -> Path:
    """Resolve audit path from explicit input, environment, then settings."""

    if audit_log_path is not None:
        configured = _normalize_audit_log_path(audit_log_path, "audit_log_path")
    elif "HALO_SWING_AUDIT_LOG_PATH" in os.environ:
        configured = _normalize_audit_log_path(
            os.environ["HALO_SWING_AUDIT_LOG_PATH"],
            "HALO_SWING_AUDIT_LOG_PATH",
        )
    else:
        configured = _normalize_audit_log_path(
            get_settings().audit_log_path,
            "settings.audit_log_path",
        )
    return Path(configured)


def _normalize_audit_log_path(value: str, field_name: str) -> str:
    if not value.strip():
        raise ValueError(f"{field_name} must be a nonempty string")
    if any(ord(character) < 32 or ord(character) == 127 for character in value):
        raise ValueError(f"{field_name} must not contain control characters")
    return value.strip()


def redact_details(value: Any) -> Any:
    """Redact likely secrets and keep event details compact."""

    if isinstance(value, dict):
        redacted: dict[str, Any] = {}
        for key, nested in value.items():
            lowered = str(key).lower()
            if any(part in lowered for part in SENSITIVE_KEY_PARTS):
                redacted[str(key)] = "[REDACTED]"
            else:
                redacted[str(key)] = redact_details(nested)
        return redacted
    if isinstance(value, list):
        return [redact_details(item) for item in value]
    if isinstance(value, str):
        if len(value) > MAX_DETAIL_STRING_LENGTH:
            return f"{value[:MAX_DETAIL_STRING_LENGTH]}...[truncated]"
        return value
    return value


def append_audit_event(
    *,
    action: str,
    resource_type: str,
    resource_id: str | None,
    outcome: str,
    actor: str = "local",
    details: dict[str, Any] | None = None,
    audit_log_path: str | None = None,
    occurred_at: str | None = None,
    correlation_id: str | None = None,
) -> dict[str, Any]:
    """Append one structured audit event and return it."""

    timestamp = occurred_at or utc_now()
    event = {
        "schema_version": SCHEMA_VERSION,
        "event_id": _event_id(
            timestamp=timestamp,
            actor=actor,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            outcome=outcome,
        ),
        "occurred_at": timestamp,
        "actor": actor,
        "action": action,
        "resource_type": resource_type,
        "resource_id": resource_id,
        "outcome": outcome,
        "correlation_id": correlation_id,
        "details": redact_details(details or {}),
    }
    path = resolve_audit_log_path(audit_log_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")
    return event


def read_audit_events(
    *,
    audit_log_path: str | None = None,
    limit: int = 100,
    action: str | None = None,
    resource_type: str | None = None,
    resource_id: str | None = None,
    outcome: str | None = None,
) -> list[dict[str, Any]]:
    """Read newest matching audit events from the JSONL log."""

    path = resolve_audit_log_path(audit_log_path)
    if not path.exists():
        return []

    events: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            stripped = line.strip()
            if not stripped:
                continue
            try:
                event = json.loads(stripped)
            except json.JSONDecodeError:
                continue
            if action and event.get("action") != action:
                continue
            if resource_type and event.get("resource_type") != resource_type:
                continue
            if resource_id and event.get("resource_id") != resource_id:
                continue
            if outcome and event.get("outcome") != outcome:
                continue
            events.append(event)

    bounded_limit = max(1, min(limit, 1000))
    return events[-bounded_limit:][::-1]


def audit_summary(audit_log_path: str | None = None) -> dict[str, Any]:
    """Return aggregate counts for the audit log."""

    events = read_audit_events(audit_log_path=audit_log_path, limit=1000)
    chronological = list(reversed(events))
    by_action = Counter(event.get("action", "unknown") for event in events)
    by_outcome = Counter(event.get("outcome", "unknown") for event in events)
    by_resource_type = Counter(event.get("resource_type", "unknown") for event in events)
    return {
        "audit_log_path": str(resolve_audit_log_path(audit_log_path)),
        "total_events": len(events),
        "by_action": dict(sorted(by_action.items())),
        "by_outcome": dict(sorted(by_outcome.items())),
        "by_resource_type": dict(sorted(by_resource_type.items())),
        "first_event_at": chronological[0]["occurred_at"] if chronological else None,
        "last_event_at": chronological[-1]["occurred_at"] if chronological else None,
    }


def tool_audit_details(
    *,
    command_name: str,
    input_payload: Any,
    result: dict[str, Any] | None = None,
    error: str | None = None,
) -> dict[str, Any]:
    """Build compact audit details for a tool call."""

    details: dict[str, Any] = {
        "command": command_name,
        "input": input_payload,
    }
    if result is not None:
        details["output_summary"] = _result_summary(result)
    if error is not None:
        details["error"] = error
    return details


def append_tool_audit_event(
    *,
    command_name: str,
    input_payload: Any,
    result: dict[str, Any] | None,
    outcome: str,
    actor: str,
    audit_log_path: str | None = None,
    error: str | None = None,
) -> dict[str, Any]:
    """Append an audit event for an MCP or harness tool call."""

    resource_id = command_name
    correlation_id = _correlation_id(result, input_payload)
    return append_audit_event(
        action="tool_call",
        resource_type="mcp_tool",
        resource_id=resource_id,
        outcome=outcome,
        actor=actor,
        audit_log_path=audit_log_path,
        correlation_id=correlation_id,
        details=tool_audit_details(
            command_name=command_name,
            input_payload=input_payload,
            result=result,
            error=error,
        ),
    )


def _result_summary(result: dict[str, Any]) -> dict[str, Any]:
    keys = sorted(result.keys())
    summary: dict[str, Any] = {"keys": keys}
    for key in (
        "signal_id",
        "run_id",
        "asset",
        "underlying",
        "symbol",
        "exchange",
        "action",
        "status",
        "blocked_reason",
        "outcome",
        "estimated_notional_usd",
        "config_hash",
        "ledger_ref",
        "path",
    ):
        if key in result:
            summary[key] = result[key]
    if "signal" in result and isinstance(result["signal"], dict):
        signal = result["signal"]
        for key in ("signal_id", "asset", "underlying", "action", "config_hash"):
            if key in signal:
                summary[f"signal.{key}"] = signal[key]
    return summary


def _correlation_id(
    result: dict[str, Any] | None,
    input_payload: Any,
) -> str | None:
    if result:
        for key in ("signal_id", "run_id", "correlation_id"):
            if key in result and result[key] is not None:
                return str(result[key])
        signal = result.get("signal")
        if isinstance(signal, dict):
            for key in ("signal_id", "run_id"):
                if key in signal and signal[key] is not None:
                    return str(signal[key])
    if isinstance(input_payload, dict):
        for key in ("signal_id", "run_id", "correlation_id"):
            if key in input_payload and input_payload[key] is not None:
                return str(input_payload[key])
    return None


def _event_id(
    *,
    timestamp: str,
    actor: str,
    action: str,
    resource_type: str,
    resource_id: str | None,
    outcome: str,
) -> str:
    raw = "|".join(
        [
            timestamp,
            actor,
            action,
            resource_type,
            resource_id or "",
            outcome,
            os.urandom(8).hex(),
        ]
    )
    return f"aud_{hashlib.sha256(raw.encode('utf-8')).hexdigest()[:24]}"
