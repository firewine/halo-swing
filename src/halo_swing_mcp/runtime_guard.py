"""Runtime retention and watchdog helpers for local JSONL artifacts."""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from halo_swing_mcp.audit import utc_now
from halo_swing_mcp.config import get_settings


WATCHDOG_SCHEMA_VERSION = "watchdog.v1"
RUNTIME_RETENTION_MAX_RECORDS_ENV = "HALO_SWING_RUNTIME_RETENTION_MAX_RECORDS"
RUNTIME_RETENTION_MAX_BYTES_ENV = "HALO_SWING_RUNTIME_RETENTION_MAX_BYTES"
RUNTIME_FAILURE_WINDOW_ENV = "HALO_SWING_RUNTIME_FAILURE_WINDOW"
RUNTIME_FAILURE_THRESHOLD_ENV = "HALO_SWING_RUNTIME_FAILURE_THRESHOLD"


@dataclass(frozen=True)
class RetentionPolicy:
    max_records: int
    max_bytes: int


def default_retention_policy(
    max_records: int | None = None,
    max_bytes: int | None = None,
) -> RetentionPolicy:
    """Return bounded JSONL retention defaults from inputs or settings."""

    settings = get_settings()
    return RetentionPolicy(
        max_records=_select_positive_integer(
            max_records,
            settings.runtime_retention_max_records,
            "max_records",
            "runtime_retention_max_records",
            RUNTIME_RETENTION_MAX_RECORDS_ENV,
        ),
        max_bytes=_select_positive_integer(
            max_bytes,
            settings.runtime_retention_max_bytes,
            "max_bytes",
            "runtime_retention_max_bytes",
            RUNTIME_RETENTION_MAX_BYTES_ENV,
        ),
    )


def inspect_jsonl_retention(
    path: str | Path,
    policy: RetentionPolicy,
) -> dict[str, Any]:
    """Inspect whether a JSONL file exceeds retention limits without mutating it."""

    jsonl_path = Path(path)
    lines = _read_jsonl_lines(jsonl_path)
    selected = _select_retained_lines(lines, policy)
    original_bytes = _line_bytes(lines)
    retained_bytes = _line_bytes(selected)
    dropped_records = max(0, len(lines) - len(selected))

    return {
        "path": str(jsonl_path),
        "status": "missing" if not jsonl_path.exists() else "ok",
        "max_records": policy.max_records,
        "max_bytes": policy.max_bytes,
        "original_records": len(lines),
        "retained_records": len(selected),
        "dropped_records": dropped_records,
        "original_bytes": original_bytes,
        "retained_bytes": retained_bytes,
        "over_limit": dropped_records > 0 or original_bytes > policy.max_bytes,
        "live_data_required": False,
    }


def apply_jsonl_retention(
    path: str | Path,
    policy: RetentionPolicy,
) -> dict[str, Any]:
    """Keep only the newest JSONL records allowed by a retention policy."""

    jsonl_path = Path(path)
    before = inspect_jsonl_retention(jsonl_path, policy)
    if before["status"] == "missing":
        return {**before, "retention_applied": False}

    lines = _read_jsonl_lines(jsonl_path)
    retained = _select_retained_lines(lines, policy)
    if retained != lines:
        _write_jsonl_lines(jsonl_path, retained)

    after = inspect_jsonl_retention(jsonl_path, policy)
    return {
        **after,
        "status": "retained" if retained != lines else "unchanged",
        "retention_applied": retained != lines,
        "dropped_records": before["dropped_records"],
        "original_records": before["original_records"],
        "original_bytes": before["original_bytes"],
    }


def evaluate_failure_degraded_mode(
    events: list[dict[str, Any]],
    *,
    failure_threshold: int | None = None,
    failure_window: int | None = None,
) -> dict[str, Any]:
    """Evaluate whether recent audit failures should put runtime in degraded mode."""

    settings = get_settings()
    bounded_window = _select_positive_integer(
        failure_window,
        settings.runtime_failure_window,
        "failure_window",
        "runtime_failure_window",
        RUNTIME_FAILURE_WINDOW_ENV,
    )
    threshold = _select_positive_integer(
        failure_threshold,
        settings.runtime_failure_threshold,
        "failure_threshold",
        "runtime_failure_threshold",
        RUNTIME_FAILURE_THRESHOLD_ENV,
    )
    recent_events = events[:bounded_window]
    failure_count = sum(1 for event in recent_events if event.get("outcome") == "failure")
    degraded = failure_count >= threshold
    event = None
    if degraded:
        event = build_watchdog_event(
            severity="warning",
            metric_name="tool_failure_count",
            metric_value=failure_count,
            threshold_value=threshold,
            action_taken="degraded_mode",
            details={"window_size": bounded_window},
        )

    return {
        "schema_version": WATCHDOG_SCHEMA_VERSION,
        "status": "degraded" if degraded else "ok",
        "degraded_mode": degraded,
        "failure_count": failure_count,
        "failure_threshold": threshold,
        "failure_window": bounded_window,
        "events_considered": len(recent_events),
        "watchdog_event": event,
        "live_data_required": False,
    }


def build_watchdog_event(
    *,
    severity: str,
    metric_name: str,
    metric_value: int | float,
    threshold_value: int | float,
    action_taken: str,
    details: dict[str, Any] | None = None,
    run_id: str | None = None,
    occurred_at: str | None = None,
) -> dict[str, Any]:
    """Build a structured watchdog event payload without persisting it."""

    return {
        "schema_version": WATCHDOG_SCHEMA_VERSION,
        "run_id": run_id,
        "timestamp": occurred_at or utc_now(),
        "severity": severity,
        "metric_name": metric_name,
        "metric_value": metric_value,
        "threshold_value": threshold_value,
        "action_taken": action_taken,
        "details": details or {},
    }


def retention_policy_payload(policy: RetentionPolicy) -> dict[str, int]:
    return asdict(policy)


def _select_positive_integer(
    provided_value: int | None,
    settings_value: int,
    provided_field_name: str,
    settings_field_name: str,
    env_key: str,
) -> int:
    if provided_value is not None:
        return _normalize_positive_integer(provided_value, provided_field_name)
    field_name = env_key if env_key in os.environ else f"settings.{settings_field_name}"
    return _normalize_positive_integer(settings_value, field_name)


def _normalize_positive_integer(value: Any, field_name: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        raise ValueError(f"{field_name} must be a positive integer")
    if value <= 0:
        raise ValueError(f"{field_name} must be a positive integer")
    return value


def _read_jsonl_lines(path: Path) -> list[str]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8") as handle:
        return handle.readlines()


def _write_jsonl_lines(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = path.with_suffix(f"{path.suffix}.tmp")
    with temporary_path.open("w", encoding="utf-8") as handle:
        handle.writelines(lines)
    temporary_path.replace(path)


def _select_retained_lines(lines: list[str], policy: RetentionPolicy) -> list[str]:
    retained_reversed: list[str] = []
    retained_bytes = 0
    for line in reversed(lines[-policy.max_records :]):
        encoded_size = len(line.encode("utf-8"))
        if encoded_size > policy.max_bytes:
            if retained_reversed:
                break
            continue
        if retained_bytes + encoded_size > policy.max_bytes:
            break
        retained_reversed.append(line)
        retained_bytes += encoded_size
    return list(reversed(retained_reversed))


def _line_bytes(lines: list[str]) -> int:
    return sum(len(line.encode("utf-8")) for line in lines)


def validate_jsonl(path: str | Path) -> dict[str, Any]:
    """Return parse status for a JSONL file used by runtime retention checks."""

    jsonl_path = Path(path)
    errors: list[dict[str, Any]] = []
    for index, line in enumerate(_read_jsonl_lines(jsonl_path), start=1):
        if not line.strip():
            continue
        try:
            json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append({"line": index, "error": str(exc)})
    return {
        "path": str(jsonl_path),
        "valid": not errors,
        "errors": errors,
        "live_data_required": False,
    }


__all__ = [
    "RetentionPolicy",
    "WATCHDOG_SCHEMA_VERSION",
    "apply_jsonl_retention",
    "build_watchdog_event",
    "default_retention_policy",
    "evaluate_failure_degraded_mode",
    "inspect_jsonl_retention",
    "retention_policy_payload",
    "validate_jsonl",
]
