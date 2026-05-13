"""Runtime status, retention, checkpoint, and watchdog tools."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from halo_swing_mcp.audit import utc_now
from halo_swing_mcp.audit import read_audit_events, resolve_audit_log_path
from halo_swing_mcp.config import get_settings
from halo_swing_mcp.runtime_guard import (
    apply_jsonl_retention,
    default_retention_policy,
    evaluate_failure_degraded_mode,
    inspect_jsonl_retention,
    retention_policy_payload,
    validate_jsonl,
)
from halo_swing_mcp.signal_repository import get_signal_ledger_repository
from halo_swing_mcp.tools.readiness import get_integration_readiness


CHECKPOINT_SCHEMA_VERSION = "runtime_checkpoint.v1"
RUNTIME_CHECKPOINT_PATH_ENV = "HALO_SWING_RUNTIME_CHECKPOINT_PATH"


def get_runtime_status(
    audit_log_path: str | None = None,
    ledger_path: str | None = None,
    apply_retention: bool = False,
    max_records: int | None = None,
    max_bytes: int | None = None,
    failure_window: int | None = None,
    failure_threshold: int | None = None,
) -> dict[str, Any]:
    """Return local runtime guard status for JSONL artifacts and audit failures."""

    normalized_audit_log_path = _normalize_optional_path(
        audit_log_path,
        "audit_log_path",
    )
    normalized_ledger_path = _normalize_optional_path(
        ledger_path,
        "ledger_path",
    )
    normalized_apply_retention = _normalize_boolean(
        apply_retention,
        "apply_retention",
    )
    normalized_max_records = _normalize_optional_positive_integer(
        max_records,
        "max_records",
    )
    normalized_max_bytes = _normalize_optional_positive_integer(
        max_bytes,
        "max_bytes",
    )
    normalized_failure_window = _normalize_optional_positive_integer(
        failure_window,
        "failure_window",
    )
    normalized_failure_threshold = _normalize_optional_positive_integer(
        failure_threshold,
        "failure_threshold",
    )
    policy = default_retention_policy(
        max_records=normalized_max_records,
        max_bytes=normalized_max_bytes,
    )
    audit_path = resolve_audit_log_path(normalized_audit_log_path)
    ledger_ref = get_signal_ledger_repository(normalized_ledger_path).ledger_ref
    retention_fn = (
        apply_jsonl_retention
        if normalized_apply_retention
        else inspect_jsonl_retention
    )
    audit_events = read_audit_events(
        audit_log_path=str(audit_path),
        limit=normalized_failure_window or 100,
    )
    watchdog = evaluate_failure_degraded_mode(
        audit_events,
        failure_window=normalized_failure_window,
        failure_threshold=normalized_failure_threshold,
    )

    return {
        "status": "degraded" if watchdog["degraded_mode"] else "ok",
        "degraded_mode": watchdog["degraded_mode"],
        "retention_applied": normalized_apply_retention,
        "retention_policy": retention_policy_payload(policy),
        "resources": {
            "audit_log": {
                **retention_fn(audit_path, policy),
                "jsonl_validation": validate_jsonl(audit_path),
            },
            "signal_ledger": {
                **retention_fn(ledger_ref, policy),
                "jsonl_validation": validate_jsonl(ledger_ref),
            },
        },
        "watchdog": watchdog,
        "live_data_required": False,
    }


def record_runtime_checkpoint(
    checkpoint_path: str | None = None,
    audit_log_path: str | None = None,
    ledger_path: str | None = None,
    run_id: str | None = None,
    include_readiness: bool = True,
) -> dict[str, Any]:
    """Append a local runtime checkpoint snapshot without scheduling work."""

    normalized_include_readiness = _normalize_boolean(
        include_readiness,
        "include_readiness",
    )
    normalized_checkpoint_path = _normalize_optional_path(
        checkpoint_path,
        "checkpoint_path",
    )
    normalized_run_id = _normalize_optional_run_id(run_id)
    path = _resolve_checkpoint_path(normalized_checkpoint_path)
    runtime_status = get_runtime_status(
        audit_log_path=audit_log_path,
        ledger_path=ledger_path,
        apply_retention=False,
    )
    readiness = get_integration_readiness() if normalized_include_readiness else None
    checkpoint = {
        "schema_version": CHECKPOINT_SCHEMA_VERSION,
        "checkpoint_id": _checkpoint_id(normalized_run_id),
        "created_at": utc_now(),
        "run_id": normalized_run_id,
        "runtime_status": runtime_status["status"],
        "degraded_mode": runtime_status["degraded_mode"],
        "watchdog": runtime_status["watchdog"],
        "resources": runtime_status["resources"],
        "readiness_status": readiness["status"] if readiness else None,
        "readiness_next_actions": readiness["next_actions"] if readiness else [],
        "checkpoint_contract": {
            "append_only_jsonl": True,
            "scheduler_added": False,
            "network_call": False,
            "secret_values_returned": False,
        },
        "live_data_required": False,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(checkpoint, ensure_ascii=False, sort_keys=True) + "\n")

    return {
        "status": "recorded",
        "checkpoint_path": str(path),
        "checkpoint": checkpoint,
        "live_data_required": False,
    }


def _checkpoint_id(run_id: str | None) -> str:
    timestamp = utc_now().replace(":", "").replace("-", "")
    suffix = run_id or "manual"
    return f"checkpoint_{timestamp}_{suffix}"


def _resolve_checkpoint_path(checkpoint_path: str | None = None) -> Path:
    if checkpoint_path is not None:
        return Path(_normalize_path(checkpoint_path, "checkpoint_path"))
    if RUNTIME_CHECKPOINT_PATH_ENV in os.environ:
        return Path(
            _normalize_path(
                os.environ[RUNTIME_CHECKPOINT_PATH_ENV],
                RUNTIME_CHECKPOINT_PATH_ENV,
            )
        )
    return Path(
        _normalize_path(
            get_settings().runtime_checkpoint_path,
            "settings.runtime_checkpoint_path",
        )
    )


def _normalize_boolean(value: bool, field_name: str) -> bool:
    if not isinstance(value, bool):
        raise ValueError(f"{field_name} must be a boolean")
    return value


def _normalize_optional_positive_integer(
    value: int | None,
    field_name: str,
) -> int | None:
    if value is None:
        return None
    if not isinstance(value, int) or isinstance(value, bool):
        raise ValueError(f"{field_name} must be a positive integer")
    if value <= 0:
        raise ValueError(f"{field_name} must be a positive integer")
    return value


def _normalize_optional_run_id(run_id: str | None) -> str | None:
    if run_id is None:
        return None
    if not isinstance(run_id, str):
        raise ValueError("run_id must be a nonempty string")
    if not _has_no_control_characters(run_id):
        raise ValueError("run_id must not contain control characters")
    normalized = run_id.strip()
    if not normalized:
        raise ValueError("run_id must be a nonempty string")
    return normalized


def _normalize_optional_path(value: str | None, field_name: str) -> str | None:
    if value is None:
        return None
    return _normalize_path(value, field_name)


def _normalize_path(value: Any, field_name: str) -> str:
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
