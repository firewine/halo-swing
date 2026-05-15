import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from halo_swing_mcp.audit import append_audit_event
from halo_swing_mcp.audit import read_audit_events
from halo_swing_mcp.config import get_settings
from halo_swing_mcp.runtime_guard import (
    RetentionPolicy,
    apply_jsonl_retention,
    build_watchdog_event,
)
from halo_swing_mcp.tools.runtime import get_runtime_status, record_runtime_checkpoint


def write_jsonl(path: Path, records: list[dict[str, object]]) -> None:
    path.write_text(
        "".join(json.dumps(record, sort_keys=True) + "\n" for record in records),
        encoding="utf-8",
    )


def read_jsonl(path: Path) -> list[dict[str, object]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def test_apply_jsonl_retention_keeps_newest_records(tmp_path: Path) -> None:
    path = tmp_path / "signal_ledger.jsonl"
    write_jsonl(path, [{"sequence": index} for index in range(5)])

    result = apply_jsonl_retention(
        path,
        RetentionPolicy(max_records=2, max_bytes=10_000),
    )

    assert result["status"] == "retained"
    assert result["original_records"] == 5
    assert result["retained_records"] == 2
    assert result["dropped_records"] == 3
    assert read_jsonl(path) == [{"sequence": 3}, {"sequence": 4}]


def test_apply_jsonl_retention_honors_byte_limit(tmp_path: Path) -> None:
    path = tmp_path / "audit.jsonl"
    write_jsonl(
        path,
        [
            {"sequence": 1, "message": "short"},
            {"sequence": 2, "message": "x" * 200},
            {"sequence": 3, "message": "short"},
        ],
    )

    result = apply_jsonl_retention(
        path,
        RetentionPolicy(max_records=10, max_bytes=80),
    )

    assert result["status"] == "retained"
    assert result["retained_bytes"] <= 80
    assert read_jsonl(path) == [{"message": "short", "sequence": 3}]


def test_watchdog_event_contract_is_structured() -> None:
    event = build_watchdog_event(
        severity="warning",
        metric_name="tool_failure_count",
        metric_value=3,
        threshold_value=3,
        action_taken="degraded_mode",
        details={"window_size": 5},
        run_id="run_test",
        occurred_at="2026-05-10T00:00:00Z",
    )

    assert event == {
        "schema_version": "watchdog.v1",
        "run_id": "run_test",
        "timestamp": "2026-05-10T00:00:00Z",
        "severity": "warning",
        "metric_name": "tool_failure_count",
        "metric_value": 3,
        "threshold_value": 3,
        "action_taken": "degraded_mode",
        "details": {"window_size": 5},
    }


def test_runtime_status_applies_retention_and_degraded_mode(tmp_path: Path) -> None:
    audit_path = tmp_path / "audit.jsonl"
    ledger_path = tmp_path / "signal_ledger.jsonl"
    write_jsonl(ledger_path, [{"sequence": index} for index in range(4)])
    append_audit_event(
        action="tool_call",
        resource_type="mcp_tool",
        resource_id="health_check",
        outcome="success",
        actor="test",
        audit_log_path=str(audit_path),
        occurred_at="2026-05-10T00:00:00Z",
    )
    for index in range(3):
        append_audit_event(
            action="tool_call",
            resource_type="mcp_tool",
            resource_id=f"tool_{index}",
            outcome="failure",
            actor="test",
            audit_log_path=str(audit_path),
            occurred_at=f"2026-05-10T00:0{index + 1}:00Z",
        )

    payload = get_runtime_status(
        audit_log_path=f" {audit_path} ",
        ledger_path=f" {ledger_path} ",
        apply_retention=True,
        max_records=2,
        max_bytes=10_000,
        failure_window=4,
        failure_threshold=3,
    )

    assert payload["status"] == "degraded"
    assert payload["degraded_mode"] is True
    assert payload["retention_applied"] is True
    assert payload["resources"]["audit_log"]["retained_records"] == 2
    assert payload["resources"]["signal_ledger"]["retained_records"] == 2
    assert payload["watchdog"]["watchdog_event"]["action_taken"] == "degraded_mode"
    assert payload["live_data_required"] is False
    assert len(read_jsonl(audit_path)) == 2
    assert read_jsonl(ledger_path) == [{"sequence": 2}, {"sequence": 3}]


def test_runtime_status_rejects_invalid_public_inputs(
    tmp_path: Path,
    monkeypatch,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    ledger_path = tmp_path / "signal_ledger.jsonl"
    monkeypatch.chdir(tmp_path)
    invalid_cases = [
        (
            {"apply_retention": "false"},
            "apply_retention must be a boolean",
        ),
        (
            {"max_records": 0},
            "max_records must be a positive integer",
        ),
        (
            {"max_bytes": False},
            "max_bytes must be a positive integer",
        ),
        (
            {"failure_window": "5"},
            "failure_window must be a positive integer",
        ),
        (
            {"failure_threshold": -1},
            "failure_threshold must be a positive integer",
        ),
        (
            {"audit_log_path": ""},
            "audit_log_path must be a nonempty string",
        ),
        (
            {"audit_log_path": "   "},
            "audit_log_path must be a nonempty string",
        ),
        (
            {"audit_log_path": 123},
            "audit_log_path must be a nonempty string",
        ),
        (
            {"ledger_path": ""},
            "ledger_path must be a nonempty string",
        ),
        (
            {"ledger_path": False},
            "ledger_path must be a nonempty string",
        ),
    ]

    for overrides, expected_error in invalid_cases:
        payload = {
            "audit_log_path": str(audit_path),
            "ledger_path": str(ledger_path),
        }
        payload.update(overrides)
        with pytest.raises(ValueError, match=expected_error):
            get_runtime_status(**payload)

        assert not audit_path.exists()
        assert not ledger_path.exists()
        assert not (tmp_path / "state").exists()


def test_runtime_status_uses_valid_env_runtime_limits(
    tmp_path: Path,
    monkeypatch,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    ledger_path = tmp_path / "signal_ledger.jsonl"
    write_jsonl(ledger_path, [{"sequence": 1}])
    monkeypatch.setenv("HALO_SWING_RUNTIME_RETENTION_MAX_RECORDS", "2")
    monkeypatch.setenv("HALO_SWING_RUNTIME_RETENTION_MAX_BYTES", "10000")
    monkeypatch.setenv("HALO_SWING_RUNTIME_FAILURE_WINDOW", "4")
    monkeypatch.setenv("HALO_SWING_RUNTIME_FAILURE_THRESHOLD", "3")
    get_settings.cache_clear()

    try:
        payload = get_runtime_status(
            audit_log_path=str(audit_path),
            ledger_path=str(ledger_path),
        )

        assert payload["retention_policy"] == {"max_records": 2, "max_bytes": 10000}
        assert payload["watchdog"]["failure_window"] == 4
        assert payload["watchdog"]["failure_threshold"] == 3
    finally:
        get_settings.cache_clear()


def test_runtime_status_rejects_invalid_env_runtime_limits_without_fallback(
    tmp_path: Path,
    monkeypatch,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    ledger_path = tmp_path / "signal_ledger.jsonl"
    monkeypatch.chdir(tmp_path)
    invalid_cases = [
        (
            "HALO_SWING_RUNTIME_RETENTION_MAX_RECORDS",
            "0",
            "HALO_SWING_RUNTIME_RETENTION_MAX_RECORDS must be a positive integer",
        ),
        (
            "HALO_SWING_RUNTIME_RETENTION_MAX_BYTES",
            "-1",
            "HALO_SWING_RUNTIME_RETENTION_MAX_BYTES must be a positive integer",
        ),
        (
            "HALO_SWING_RUNTIME_FAILURE_WINDOW",
            "0",
            "HALO_SWING_RUNTIME_FAILURE_WINDOW must be a positive integer",
        ),
        (
            "HALO_SWING_RUNTIME_FAILURE_THRESHOLD",
            "-1",
            "HALO_SWING_RUNTIME_FAILURE_THRESHOLD must be a positive integer",
        ),
    ]
    runtime_env_keys = [env_key for env_key, _, _ in invalid_cases]

    try:
        for env_key, env_value, expected_error in invalid_cases:
            for key in runtime_env_keys:
                monkeypatch.delenv(key, raising=False)
            monkeypatch.setenv(env_key, env_value)
            get_settings.cache_clear()

            with pytest.raises(ValueError, match=expected_error):
                get_runtime_status(
                    audit_log_path=str(audit_path),
                    ledger_path=str(ledger_path),
            )
            assert not audit_path.exists()
            assert not ledger_path.exists()
            assert not (tmp_path / "state").exists()
    finally:
        for key in runtime_env_keys:
            monkeypatch.delenv(key, raising=False)
        get_settings.cache_clear()


def test_runtime_status_rejects_path_control_character_inputs(
    tmp_path: Path,
    monkeypatch,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    ledger_path = tmp_path / "signal_ledger.jsonl"
    monkeypatch.chdir(tmp_path)
    invalid_cases = [
        (
            {"audit_log_path": f"{audit_path}\n"},
            "audit_log_path must not contain control characters",
        ),
        (
            {"ledger_path": f"{ledger_path}\n"},
            "ledger_path must not contain control characters",
        ),
    ]

    for overrides, expected_error in invalid_cases:
        payload = {
            "audit_log_path": str(audit_path),
            "ledger_path": str(ledger_path),
        }
        payload.update(overrides)
        with pytest.raises(ValueError, match=expected_error):
            get_runtime_status(**payload)

        assert not audit_path.exists()
        assert not ledger_path.exists()
        assert not (tmp_path / "state").exists()


def test_harness_rejects_invalid_runtime_status_input_with_failure_audit(
    tmp_path: Path,
) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    audit_path = tmp_path / "audit.jsonl"
    ledger_path = tmp_path / "signal_ledger.jsonl"
    input_payload = {
        "audit_log_path": str(audit_path),
        "ledger_path": str(ledger_path),
        "apply_retention": "false",
    }
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "get_runtime_status",
            "--input-json",
            json.dumps(input_payload),
            "--audit-log-path",
            str(audit_path),
        ],
        check=False,
        cwd=tmp_path,
        env={**os.environ, "PYTHONPATH": str(repo_root / "src")},
        text=True,
        capture_output=True,
    )
    events = read_audit_events(audit_log_path=str(audit_path))
    event = events[0]

    assert result.returncode != 0
    assert result.stdout == ""
    assert "apply_retention must be a boolean" in result.stderr
    assert str(audit_path) not in result.stderr
    assert str(ledger_path) not in result.stderr
    assert "audit.jsonl" not in result.stderr
    assert "signal_ledger.jsonl" not in result.stderr
    assert "false" not in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "get_runtime_status"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "apply_retention must be a boolean" in event["details"]["error"]
    assert not ledger_path.exists()
    assert not (tmp_path / "state").exists()


def test_harness_rejects_runtime_status_apply_retention_type_without_fallback(
    tmp_path: Path,
) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    audit_path = tmp_path / "audit.jsonl"
    ledger_path = tmp_path / "signal_ledger.jsonl"
    input_payload = {
        "audit_log_path": str(audit_path),
        "ledger_path": str(ledger_path),
        "apply_retention": "false",
    }
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "get_runtime_status",
            "--input-json",
            json.dumps(input_payload),
            "--audit-log-path",
            str(audit_path),
        ],
        check=False,
        cwd=tmp_path,
        env={**os.environ, "PYTHONPATH": str(repo_root / "src")},
        text=True,
        capture_output=True,
    )
    events = read_audit_events(audit_log_path=str(audit_path))
    event = events[0]

    assert result.returncode != 0
    assert result.stdout == ""
    assert "apply_retention must be a boolean" in result.stderr
    assert str(audit_path) not in result.stderr
    assert str(ledger_path) not in result.stderr
    assert "audit.jsonl" not in result.stderr
    assert "signal_ledger.jsonl" not in result.stderr
    assert "false" not in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "get_runtime_status"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "apply_retention must be a boolean" in event["details"]["error"]
    assert not ledger_path.exists()
    assert not (tmp_path / "state").exists()


def test_harness_rejects_runtime_status_apply_retention_numeric_without_fallback(
    tmp_path: Path,
) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    audit_path = tmp_path / "audit.jsonl"
    ledger_path = tmp_path / "signal_ledger.jsonl"
    input_payload = {
        "audit_log_path": str(audit_path),
        "ledger_path": str(ledger_path),
        "apply_retention": 1,
    }
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "get_runtime_status",
            "--input-json",
            json.dumps(input_payload),
            "--audit-log-path",
            str(audit_path),
        ],
        check=False,
        cwd=tmp_path,
        env={**os.environ, "PYTHONPATH": str(repo_root / "src")},
        text=True,
        capture_output=True,
    )
    events = read_audit_events(audit_log_path=str(audit_path))
    event = events[0]

    assert result.returncode != 0
    assert result.stdout == ""
    assert "apply_retention must be a boolean" in result.stderr
    assert str(audit_path) not in result.stderr
    assert str(ledger_path) not in result.stderr
    assert "audit.jsonl" not in result.stderr
    assert "signal_ledger.jsonl" not in result.stderr
    assert '"apply_retention": 1' not in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "get_runtime_status"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "apply_retention must be a boolean" in event["details"]["error"]
    assert not ledger_path.exists()
    assert not (tmp_path / "state").exists()


def test_harness_rejects_runtime_status_apply_retention_zero_without_fallback(
    tmp_path: Path,
) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    audit_path = tmp_path / "audit.jsonl"
    ledger_path = tmp_path / "signal_ledger.jsonl"
    input_payload = {
        "audit_log_path": str(audit_path),
        "ledger_path": str(ledger_path),
        "apply_retention": 0,
    }
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "get_runtime_status",
            "--input-json",
            json.dumps(input_payload),
            "--audit-log-path",
            str(audit_path),
        ],
        check=False,
        cwd=tmp_path,
        env={**os.environ, "PYTHONPATH": str(repo_root / "src")},
        text=True,
        capture_output=True,
    )
    events = read_audit_events(audit_log_path=str(audit_path))
    event = events[0]

    assert result.returncode != 0
    assert result.stdout == ""
    assert "apply_retention must be a boolean" in result.stderr
    assert str(audit_path) not in result.stderr
    assert str(ledger_path) not in result.stderr
    assert "audit.jsonl" not in result.stderr
    assert "signal_ledger.jsonl" not in result.stderr
    assert '"apply_retention": 0' not in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "get_runtime_status"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "apply_retention must be a boolean" in event["details"]["error"]
    assert not ledger_path.exists()
    assert not (tmp_path / "state").exists()


def test_harness_rejects_runtime_status_apply_retention_null_without_fallback(
    tmp_path: Path,
) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    audit_path = tmp_path / "audit.jsonl"
    ledger_path = tmp_path / "signal_ledger.jsonl"
    input_payload = {
        "audit_log_path": str(audit_path),
        "ledger_path": str(ledger_path),
        "apply_retention": None,
    }
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "get_runtime_status",
            "--input-json",
            json.dumps(input_payload),
            "--audit-log-path",
            str(audit_path),
        ],
        check=False,
        cwd=tmp_path,
        env={**os.environ, "PYTHONPATH": str(repo_root / "src")},
        text=True,
        capture_output=True,
    )
    events = read_audit_events(audit_log_path=str(audit_path))
    event = events[0]

    assert result.returncode != 0
    assert result.stdout == ""
    assert "apply_retention must be a boolean" in result.stderr
    assert str(audit_path) not in result.stderr
    assert str(ledger_path) not in result.stderr
    assert "audit.jsonl" not in result.stderr
    assert "signal_ledger.jsonl" not in result.stderr
    assert '"apply_retention": null' not in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "get_runtime_status"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "apply_retention must be a boolean" in event["details"]["error"]
    assert not ledger_path.exists()
    assert not (tmp_path / "state").exists()


def test_harness_rejects_runtime_status_max_records_without_fallback(
    tmp_path: Path,
) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    audit_path = tmp_path / "audit.jsonl"
    ledger_path = tmp_path / "signal_ledger.jsonl"
    input_payload = {
        "audit_log_path": str(audit_path),
        "ledger_path": str(ledger_path),
        "max_records": 0,
    }
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "get_runtime_status",
            "--input-json",
            json.dumps(input_payload),
            "--audit-log-path",
            str(audit_path),
        ],
        check=False,
        cwd=tmp_path,
        env={**os.environ, "PYTHONPATH": str(repo_root / "src")},
        text=True,
        capture_output=True,
    )
    events = read_audit_events(audit_log_path=str(audit_path))
    event = events[0]

    assert result.returncode != 0
    assert result.stdout == ""
    assert "max_records must be a positive integer" in result.stderr
    assert str(audit_path) not in result.stderr
    assert str(ledger_path) not in result.stderr
    assert "audit.jsonl" not in result.stderr
    assert "signal_ledger.jsonl" not in result.stderr
    assert '"max_records": 0' not in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "get_runtime_status"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "max_records must be a positive integer" in event["details"]["error"]
    assert not ledger_path.exists()
    assert not (tmp_path / "state").exists()


def test_harness_rejects_runtime_status_max_records_type_without_fallback(
    tmp_path: Path,
) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    audit_path = tmp_path / "audit.jsonl"
    ledger_path = tmp_path / "signal_ledger.jsonl"
    input_payload = {
        "audit_log_path": str(audit_path),
        "ledger_path": str(ledger_path),
        "max_records": "2",
    }
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "get_runtime_status",
            "--input-json",
            json.dumps(input_payload),
            "--audit-log-path",
            str(audit_path),
        ],
        check=False,
        cwd=tmp_path,
        env={**os.environ, "PYTHONPATH": str(repo_root / "src")},
        text=True,
        capture_output=True,
    )
    events = read_audit_events(audit_log_path=str(audit_path))
    event = events[0]

    assert result.returncode != 0
    assert result.stdout == ""
    assert "max_records must be a positive integer" in result.stderr
    assert str(audit_path) not in result.stderr
    assert str(ledger_path) not in result.stderr
    assert "audit.jsonl" not in result.stderr
    assert "signal_ledger.jsonl" not in result.stderr
    assert '"max_records": "2"' not in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "get_runtime_status"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "max_records must be a positive integer" in event["details"]["error"]
    assert not ledger_path.exists()
    assert not (tmp_path / "state").exists()


def test_harness_rejects_runtime_status_max_records_boolean_without_fallback(
    tmp_path: Path,
) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    audit_path = tmp_path / "audit.jsonl"
    ledger_path = tmp_path / "signal_ledger.jsonl"
    input_payload = {
        "audit_log_path": str(audit_path),
        "ledger_path": str(ledger_path),
        "max_records": True,
    }
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "get_runtime_status",
            "--input-json",
            json.dumps(input_payload),
            "--audit-log-path",
            str(audit_path),
        ],
        check=False,
        cwd=tmp_path,
        env={**os.environ, "PYTHONPATH": str(repo_root / "src")},
        text=True,
        capture_output=True,
    )
    events = read_audit_events(audit_log_path=str(audit_path))
    event = events[0]

    assert result.returncode != 0
    assert result.stdout == ""
    assert "max_records must be a positive integer" in result.stderr
    assert str(audit_path) not in result.stderr
    assert str(ledger_path) not in result.stderr
    assert "audit.jsonl" not in result.stderr
    assert "signal_ledger.jsonl" not in result.stderr
    assert '"max_records": true' not in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "get_runtime_status"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "max_records must be a positive integer" in event["details"]["error"]
    assert not ledger_path.exists()
    assert not (tmp_path / "state").exists()


def test_harness_rejects_runtime_status_max_bytes_without_fallback(
    tmp_path: Path,
) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    audit_path = tmp_path / "audit.jsonl"
    ledger_path = tmp_path / "signal_ledger.jsonl"
    input_payload = {
        "audit_log_path": str(audit_path),
        "ledger_path": str(ledger_path),
        "max_bytes": False,
    }
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "get_runtime_status",
            "--input-json",
            json.dumps(input_payload),
            "--audit-log-path",
            str(audit_path),
        ],
        check=False,
        cwd=tmp_path,
        env={**os.environ, "PYTHONPATH": str(repo_root / "src")},
        text=True,
        capture_output=True,
    )
    events = read_audit_events(audit_log_path=str(audit_path))
    event = events[0]

    assert result.returncode != 0
    assert result.stdout == ""
    assert "max_bytes must be a positive integer" in result.stderr
    assert str(audit_path) not in result.stderr
    assert str(ledger_path) not in result.stderr
    assert "audit.jsonl" not in result.stderr
    assert "signal_ledger.jsonl" not in result.stderr
    assert '"max_bytes": false' not in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "get_runtime_status"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "max_bytes must be a positive integer" in event["details"]["error"]
    assert not ledger_path.exists()
    assert not (tmp_path / "state").exists()


def test_harness_rejects_runtime_status_max_bytes_nonpositive_without_fallback(
    tmp_path: Path,
) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    audit_path = tmp_path / "audit.jsonl"
    ledger_path = tmp_path / "signal_ledger.jsonl"
    input_payload = {
        "audit_log_path": str(audit_path),
        "ledger_path": str(ledger_path),
        "max_bytes": 0,
    }
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "get_runtime_status",
            "--input-json",
            json.dumps(input_payload),
            "--audit-log-path",
            str(audit_path),
        ],
        check=False,
        cwd=tmp_path,
        env={**os.environ, "PYTHONPATH": str(repo_root / "src")},
        text=True,
        capture_output=True,
    )
    events = read_audit_events(audit_log_path=str(audit_path))
    event = events[0]

    assert result.returncode != 0
    assert result.stdout == ""
    assert "max_bytes must be a positive integer" in result.stderr
    assert str(audit_path) not in result.stderr
    assert str(ledger_path) not in result.stderr
    assert "audit.jsonl" not in result.stderr
    assert "signal_ledger.jsonl" not in result.stderr
    assert '"max_bytes": 0' not in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "get_runtime_status"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "max_bytes must be a positive integer" in event["details"]["error"]
    assert not ledger_path.exists()
    assert not (tmp_path / "state").exists()


def test_harness_rejects_runtime_status_max_bytes_type_without_fallback(
    tmp_path: Path,
) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    audit_path = tmp_path / "audit.jsonl"
    ledger_path = tmp_path / "signal_ledger.jsonl"
    input_payload = {
        "audit_log_path": str(audit_path),
        "ledger_path": str(ledger_path),
        "max_bytes": "10000",
    }
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "get_runtime_status",
            "--input-json",
            json.dumps(input_payload),
            "--audit-log-path",
            str(audit_path),
        ],
        check=False,
        cwd=tmp_path,
        env={**os.environ, "PYTHONPATH": str(repo_root / "src")},
        text=True,
        capture_output=True,
    )
    events = read_audit_events(audit_log_path=str(audit_path))
    event = events[0]

    assert result.returncode != 0
    assert result.stdout == ""
    assert "max_bytes must be a positive integer" in result.stderr
    assert str(audit_path) not in result.stderr
    assert str(ledger_path) not in result.stderr
    assert "audit.jsonl" not in result.stderr
    assert "signal_ledger.jsonl" not in result.stderr
    assert '"max_bytes": "10000"' not in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "get_runtime_status"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "max_bytes must be a positive integer" in event["details"]["error"]
    assert not ledger_path.exists()
    assert not (tmp_path / "state").exists()


def test_harness_rejects_runtime_status_max_bytes_boolean_without_fallback(
    tmp_path: Path,
) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    audit_path = tmp_path / "audit.jsonl"
    ledger_path = tmp_path / "signal_ledger.jsonl"
    input_payload = {
        "audit_log_path": str(audit_path),
        "ledger_path": str(ledger_path),
        "max_bytes": True,
    }
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "get_runtime_status",
            "--input-json",
            json.dumps(input_payload),
            "--audit-log-path",
            str(audit_path),
        ],
        check=False,
        cwd=tmp_path,
        env={**os.environ, "PYTHONPATH": str(repo_root / "src")},
        text=True,
        capture_output=True,
    )
    events = read_audit_events(audit_log_path=str(audit_path))
    event = events[0]

    assert result.returncode != 0
    assert result.stdout == ""
    assert "max_bytes must be a positive integer" in result.stderr
    assert str(audit_path) not in result.stderr
    assert str(ledger_path) not in result.stderr
    assert "audit.jsonl" not in result.stderr
    assert "signal_ledger.jsonl" not in result.stderr
    assert '"max_bytes": true' not in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "get_runtime_status"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "max_bytes must be a positive integer" in event["details"]["error"]
    assert not ledger_path.exists()
    assert not (tmp_path / "state").exists()


def test_harness_rejects_runtime_status_failure_window_without_fallback(
    tmp_path: Path,
) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    audit_path = tmp_path / "audit.jsonl"
    ledger_path = tmp_path / "signal_ledger.jsonl"
    input_payload = {
        "audit_log_path": str(audit_path),
        "ledger_path": str(ledger_path),
        "failure_window": "5",
    }
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "get_runtime_status",
            "--input-json",
            json.dumps(input_payload),
            "--audit-log-path",
            str(audit_path),
        ],
        check=False,
        cwd=tmp_path,
        env={**os.environ, "PYTHONPATH": str(repo_root / "src")},
        text=True,
        capture_output=True,
    )
    events = read_audit_events(audit_log_path=str(audit_path))
    event = events[0]

    assert result.returncode != 0
    assert result.stdout == ""
    assert "failure_window must be a positive integer" in result.stderr
    assert str(audit_path) not in result.stderr
    assert str(ledger_path) not in result.stderr
    assert "audit.jsonl" not in result.stderr
    assert "signal_ledger.jsonl" not in result.stderr
    assert '"failure_window": "5"' not in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "get_runtime_status"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "failure_window must be a positive integer" in event["details"]["error"]
    assert not ledger_path.exists()
    assert not (tmp_path / "state").exists()


def test_harness_rejects_runtime_status_failure_window_nonpositive_without_fallback(
    tmp_path: Path,
) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    audit_path = tmp_path / "audit.jsonl"
    ledger_path = tmp_path / "signal_ledger.jsonl"
    input_payload = {
        "audit_log_path": str(audit_path),
        "ledger_path": str(ledger_path),
        "failure_window": 0,
    }
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "get_runtime_status",
            "--input-json",
            json.dumps(input_payload),
            "--audit-log-path",
            str(audit_path),
        ],
        check=False,
        cwd=tmp_path,
        env={**os.environ, "PYTHONPATH": str(repo_root / "src")},
        text=True,
        capture_output=True,
    )
    events = read_audit_events(audit_log_path=str(audit_path))
    event = events[0]

    assert result.returncode != 0
    assert result.stdout == ""
    assert "failure_window must be a positive integer" in result.stderr
    assert str(audit_path) not in result.stderr
    assert str(ledger_path) not in result.stderr
    assert "audit.jsonl" not in result.stderr
    assert "signal_ledger.jsonl" not in result.stderr
    assert '"failure_window": 0' not in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "get_runtime_status"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "failure_window must be a positive integer" in event["details"]["error"]
    assert not ledger_path.exists()
    assert not (tmp_path / "state").exists()


def test_harness_rejects_runtime_status_failure_window_boolean_without_fallback(
    tmp_path: Path,
) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    audit_path = tmp_path / "audit.jsonl"
    ledger_path = tmp_path / "signal_ledger.jsonl"
    input_payload = {
        "audit_log_path": str(audit_path),
        "ledger_path": str(ledger_path),
        "failure_window": True,
    }
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "get_runtime_status",
            "--input-json",
            json.dumps(input_payload),
            "--audit-log-path",
            str(audit_path),
        ],
        check=False,
        cwd=tmp_path,
        env={**os.environ, "PYTHONPATH": str(repo_root / "src")},
        text=True,
        capture_output=True,
    )
    events = read_audit_events(audit_log_path=str(audit_path))
    event = events[0]

    assert result.returncode != 0
    assert result.stdout == ""
    assert "failure_window must be a positive integer" in result.stderr
    assert str(audit_path) not in result.stderr
    assert str(ledger_path) not in result.stderr
    assert "audit.jsonl" not in result.stderr
    assert "signal_ledger.jsonl" not in result.stderr
    assert '"failure_window": true' not in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "get_runtime_status"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "failure_window must be a positive integer" in event["details"]["error"]
    assert not ledger_path.exists()
    assert not (tmp_path / "state").exists()


def test_harness_rejects_runtime_status_failure_threshold_without_fallback(
    tmp_path: Path,
) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    audit_path = tmp_path / "audit.jsonl"
    ledger_path = tmp_path / "signal_ledger.jsonl"
    input_payload = {
        "audit_log_path": str(audit_path),
        "ledger_path": str(ledger_path),
        "failure_threshold": -1,
    }
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "get_runtime_status",
            "--input-json",
            json.dumps(input_payload),
            "--audit-log-path",
            str(audit_path),
        ],
        check=False,
        cwd=tmp_path,
        env={**os.environ, "PYTHONPATH": str(repo_root / "src")},
        text=True,
        capture_output=True,
    )
    events = read_audit_events(audit_log_path=str(audit_path))
    event = events[0]

    assert result.returncode != 0
    assert result.stdout == ""
    assert "failure_threshold must be a positive integer" in result.stderr
    assert str(audit_path) not in result.stderr
    assert str(ledger_path) not in result.stderr
    assert "audit.jsonl" not in result.stderr
    assert "signal_ledger.jsonl" not in result.stderr
    assert '"failure_threshold": -1' not in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "get_runtime_status"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "failure_threshold must be a positive integer" in event["details"]["error"]
    assert not ledger_path.exists()
    assert not (tmp_path / "state").exists()


def test_harness_rejects_runtime_status_failure_threshold_type_without_fallback(
    tmp_path: Path,
) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    audit_path = tmp_path / "audit.jsonl"
    ledger_path = tmp_path / "signal_ledger.jsonl"
    input_payload = {
        "audit_log_path": str(audit_path),
        "ledger_path": str(ledger_path),
        "failure_threshold": "3",
    }
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "get_runtime_status",
            "--input-json",
            json.dumps(input_payload),
            "--audit-log-path",
            str(audit_path),
        ],
        check=False,
        cwd=tmp_path,
        env={**os.environ, "PYTHONPATH": str(repo_root / "src")},
        text=True,
        capture_output=True,
    )
    events = read_audit_events(audit_log_path=str(audit_path))
    event = events[0]

    assert result.returncode != 0
    assert result.stdout == ""
    assert "failure_threshold must be a positive integer" in result.stderr
    assert str(audit_path) not in result.stderr
    assert str(ledger_path) not in result.stderr
    assert "audit.jsonl" not in result.stderr
    assert "signal_ledger.jsonl" not in result.stderr
    assert '"failure_threshold": "3"' not in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "get_runtime_status"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "failure_threshold must be a positive integer" in event["details"]["error"]
    assert not ledger_path.exists()
    assert not (tmp_path / "state").exists()


def test_harness_rejects_runtime_status_failure_threshold_boolean_without_fallback(
    tmp_path: Path,
) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    audit_path = tmp_path / "audit.jsonl"
    ledger_path = tmp_path / "signal_ledger.jsonl"
    input_payload = {
        "audit_log_path": str(audit_path),
        "ledger_path": str(ledger_path),
        "failure_threshold": True,
    }
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "get_runtime_status",
            "--input-json",
            json.dumps(input_payload),
            "--audit-log-path",
            str(audit_path),
        ],
        check=False,
        cwd=tmp_path,
        env={**os.environ, "PYTHONPATH": str(repo_root / "src")},
        text=True,
        capture_output=True,
    )
    events = read_audit_events(audit_log_path=str(audit_path))
    event = events[0]

    assert result.returncode != 0
    assert result.stdout == ""
    assert "failure_threshold must be a positive integer" in result.stderr
    assert str(audit_path) not in result.stderr
    assert str(ledger_path) not in result.stderr
    assert "audit.jsonl" not in result.stderr
    assert "signal_ledger.jsonl" not in result.stderr
    assert '"failure_threshold": true' not in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "get_runtime_status"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "failure_threshold must be a positive integer" in event["details"]["error"]
    assert not ledger_path.exists()
    assert not (tmp_path / "state").exists()


def test_harness_rejects_invalid_runtime_path_input_with_failure_audit(
    tmp_path: Path,
) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    audit_path = tmp_path / "audit.jsonl"
    ledger_path = tmp_path / "signal_ledger.jsonl"
    input_payload = {
        "audit_log_path": "   ",
        "ledger_path": str(ledger_path),
    }
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "get_runtime_status",
            "--input-json",
            json.dumps(input_payload),
            "--audit-log-path",
            str(audit_path),
        ],
        check=False,
        cwd=tmp_path,
        env={**os.environ, "PYTHONPATH": str(repo_root / "src")},
        text=True,
        capture_output=True,
    )
    events = read_audit_events(audit_log_path=str(audit_path))
    event = events[0]

    assert result.returncode != 0
    assert result.stdout == ""
    assert "audit_log_path must be a nonempty string" in result.stderr
    assert str(audit_path) not in result.stderr
    assert str(ledger_path) not in result.stderr
    assert "audit.jsonl" not in result.stderr
    assert "signal_ledger.jsonl" not in result.stderr
    assert '"audit_log_path": "   "' not in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "get_runtime_status"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "audit_log_path must be a nonempty string" in event["details"]["error"]
    assert not ledger_path.exists()
    assert not (tmp_path / "state").exists()


def test_harness_rejects_invalid_runtime_status_audit_path_without_fallback(
    tmp_path: Path,
) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    audit_path = tmp_path / "audit.jsonl"
    ledger_path = tmp_path / "signal_ledger.jsonl"
    input_payload = {
        "audit_log_path": "   ",
        "ledger_path": str(ledger_path),
    }
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "get_runtime_status",
            "--input-json",
            json.dumps(input_payload),
            "--audit-log-path",
            str(audit_path),
        ],
        check=False,
        cwd=tmp_path,
        env={**os.environ, "PYTHONPATH": str(repo_root / "src")},
        text=True,
        capture_output=True,
    )
    events = read_audit_events(audit_log_path=str(audit_path))
    event = events[0]

    assert result.returncode != 0
    assert result.stdout == ""
    assert "audit_log_path must be a nonempty string" in result.stderr
    assert str(audit_path) not in result.stderr
    assert str(ledger_path) not in result.stderr
    assert "audit.jsonl" not in result.stderr
    assert "signal_ledger.jsonl" not in result.stderr
    assert '"audit_log_path": 123' not in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "get_runtime_status"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "audit_log_path must be a nonempty string" in event["details"]["error"]
    assert not ledger_path.exists()
    assert not (tmp_path / "state").exists()
    assert not (tmp_path / "state").exists()
    assert not (tmp_path / "   ").exists()


def test_harness_rejects_runtime_status_audit_path_type_with_failure_audit(
    tmp_path: Path,
) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    audit_path = tmp_path / "audit.jsonl"
    ledger_path = tmp_path / "signal_ledger.jsonl"
    input_payload = {
        "audit_log_path": 123,
        "ledger_path": str(ledger_path),
    }
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "get_runtime_status",
            "--input-json",
            json.dumps(input_payload),
            "--audit-log-path",
            str(audit_path),
        ],
        check=False,
        cwd=tmp_path,
        env={**os.environ, "PYTHONPATH": str(repo_root / "src")},
        text=True,
        capture_output=True,
    )
    events = read_audit_events(audit_log_path=str(audit_path))
    event = events[0]

    assert result.returncode != 0
    assert result.stdout == ""
    assert "audit_log_path must be a nonempty string" in result.stderr
    assert str(audit_path) not in result.stderr
    assert str(ledger_path) not in result.stderr
    assert "audit.jsonl" not in result.stderr
    assert "signal_ledger.jsonl" not in result.stderr
    assert '"audit_log_path": 123' not in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "get_runtime_status"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "audit_log_path must be a nonempty string" in event["details"]["error"]
    assert not ledger_path.exists()
    assert not (tmp_path / "state").exists()


def test_harness_rejects_runtime_status_ledger_path_type_with_failure_audit(
    tmp_path: Path,
) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    audit_path = tmp_path / "audit.jsonl"
    input_payload = {
        "audit_log_path": str(audit_path),
        "ledger_path": 123,
    }
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "get_runtime_status",
            "--input-json",
            json.dumps(input_payload),
            "--audit-log-path",
            str(audit_path),
        ],
        check=False,
        cwd=tmp_path,
        env={**os.environ, "PYTHONPATH": str(repo_root / "src")},
        text=True,
        capture_output=True,
    )
    events = read_audit_events(audit_log_path=str(audit_path))
    event = events[0]

    assert result.returncode != 0
    assert result.stdout == ""
    assert "ledger_path must be a nonempty string" in result.stderr
    assert str(audit_path) not in result.stderr
    assert "audit.jsonl" not in result.stderr
    assert '"ledger_path": 123' not in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "get_runtime_status"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "ledger_path must be a nonempty string" in event["details"]["error"]
    assert not (tmp_path / "state").exists()


def test_harness_rejects_invalid_runtime_status_ledger_path_with_failure_audit(
    tmp_path: Path,
) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    audit_path = tmp_path / "audit.jsonl"
    input_payload = {
        "audit_log_path": str(audit_path),
        "ledger_path": "   ",
    }
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "get_runtime_status",
            "--input-json",
            json.dumps(input_payload),
            "--audit-log-path",
            str(audit_path),
        ],
        check=False,
        cwd=tmp_path,
        env={**os.environ, "PYTHONPATH": str(repo_root / "src")},
        text=True,
        capture_output=True,
    )
    events = read_audit_events(audit_log_path=str(audit_path))
    event = events[0]

    assert result.returncode != 0
    assert result.stdout == ""
    assert "ledger_path must be a nonempty string" in result.stderr
    assert str(audit_path) not in result.stderr
    assert "audit.jsonl" not in result.stderr
    assert '"ledger_path": "   "' not in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "get_runtime_status"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "ledger_path must be a nonempty string" in event["details"]["error"]
    assert not (tmp_path / "state").exists()
    assert not (tmp_path / "   ").exists()


def test_harness_rejects_runtime_path_control_character_with_failure_audit(
    tmp_path: Path,
) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    audit_path = tmp_path / "audit.jsonl"
    ledger_path = tmp_path / "signal_ledger.jsonl"
    invalid_audit_path = f"{audit_path}\n"
    input_payload = {
        "audit_log_path": invalid_audit_path,
        "ledger_path": str(ledger_path),
    }
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "get_runtime_status",
            "--input-json",
            json.dumps(input_payload),
            "--audit-log-path",
            str(audit_path),
        ],
        check=False,
        cwd=tmp_path,
        env={**os.environ, "PYTHONPATH": str(repo_root / "src")},
        text=True,
        capture_output=True,
    )
    events = read_audit_events(audit_log_path=str(audit_path))
    event = events[0]

    assert result.returncode != 0
    assert result.stdout == ""
    assert "audit_log_path must not contain control characters" in result.stderr
    assert str(audit_path) not in result.stderr
    assert str(ledger_path) not in result.stderr
    assert invalid_audit_path not in result.stderr
    assert "audit.jsonl" not in result.stderr
    assert "signal_ledger.jsonl" not in result.stderr
    assert "\\n" not in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "get_runtime_status"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "audit_log_path must not contain control characters" in event["details"][
        "error"
    ]
    assert not ledger_path.exists()
    assert not (tmp_path / "state").exists()


def test_harness_rejects_runtime_status_audit_path_control_character_without_fallback(
    tmp_path: Path,
) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    audit_path = tmp_path / "audit.jsonl"
    malformed_audit_path = tmp_path / "bad\naudit.jsonl"
    ledger_path = tmp_path / "signal_ledger.jsonl"
    input_payload = {
        "audit_log_path": str(malformed_audit_path),
        "ledger_path": str(ledger_path),
    }
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "get_runtime_status",
            "--input-json",
            json.dumps(input_payload),
            "--audit-log-path",
            str(audit_path),
        ],
        check=False,
        cwd=tmp_path,
        env={**os.environ, "PYTHONPATH": str(repo_root / "src")},
        text=True,
        capture_output=True,
    )
    events = read_audit_events(audit_log_path=str(audit_path))
    event = events[0]

    assert result.returncode != 0
    assert result.stdout == ""
    assert "audit_log_path must not contain control characters" in result.stderr
    assert str(malformed_audit_path) not in result.stderr
    assert str(ledger_path) not in result.stderr
    assert "bad" not in result.stderr
    assert "signal_ledger.jsonl" not in result.stderr
    assert "\\n" not in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "get_runtime_status"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "audit_log_path must not contain control characters" in event["details"][
        "error"
    ]
    assert not malformed_audit_path.exists()
    assert not ledger_path.exists()
    assert not (tmp_path / "state").exists()


def test_harness_rejects_runtime_status_ledger_path_control_character_without_fallback(
    tmp_path: Path,
) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    audit_path = tmp_path / "audit.jsonl"
    ledger_path = tmp_path / "bad\nsignal_ledger.jsonl"
    input_payload = {
        "audit_log_path": str(audit_path),
        "ledger_path": str(ledger_path),
    }
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "get_runtime_status",
            "--input-json",
            json.dumps(input_payload),
            "--audit-log-path",
            str(audit_path),
        ],
        check=False,
        cwd=tmp_path,
        env={**os.environ, "PYTHONPATH": str(repo_root / "src")},
        text=True,
        capture_output=True,
    )
    events = read_audit_events(audit_log_path=str(audit_path))
    event = events[0]

    assert result.returncode != 0
    assert result.stdout == ""
    assert "ledger_path must not contain control characters" in result.stderr
    assert str(audit_path) not in result.stderr
    assert str(ledger_path) not in result.stderr
    assert "audit.jsonl" not in result.stderr
    assert "bad" not in result.stderr
    assert "signal_ledger.jsonl" not in result.stderr
    assert "\\n" not in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "get_runtime_status"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "ledger_path must not contain control characters" in event["details"][
        "error"
    ]
    assert not ledger_path.exists()
    assert not (tmp_path / "state").exists()


def test_runtime_status_watchdog_does_not_return_audit_event_details_or_secrets(
    tmp_path: Path,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    ledger_path = tmp_path / "signal_ledger.jsonl"
    write_jsonl(ledger_path, [{"sequence": 1}])
    append_audit_event(
        action="tool_call",
        resource_type="mcp_tool",
        resource_id="get_binance_coinm_account_snapshot",
        outcome="failure",
        actor="harness",
        audit_log_path=str(audit_path),
        details={
            "input": {
                "api_key": "abcde12345key",
                "api_secret": "super-secret",
                "credential_passphrase": "wrong-passphrase",
                "credentials_path": str(tmp_path / "credentials.enc.json"),
            },
            "error": "invalid Binance credential passphrase.",
        },
        occurred_at="2026-05-10T00:01:00Z",
    )

    payload = get_runtime_status(
        audit_log_path=str(audit_path),
        ledger_path=str(ledger_path),
        failure_window=1,
        failure_threshold=1,
    )
    serialized_payload = json.dumps(payload, sort_keys=True)

    assert payload["status"] == "degraded"
    assert payload["watchdog"]["failure_count"] == 1
    assert payload["watchdog"]["watchdog_event"]["metric_name"] == "tool_failure_count"
    assert "get_binance_coinm_account_snapshot" not in serialized_payload
    assert "credential_passphrase" not in serialized_payload
    assert "credentials_path" not in serialized_payload
    assert "abcde12345key" not in serialized_payload
    assert "super-secret" not in serialized_payload
    assert "wrong-passphrase" not in serialized_payload
    assert "invalid Binance credential passphrase" not in serialized_payload
    assert "salt_b64" not in serialized_payload
    assert '"token":' not in serialized_payload
    assert payload["live_data_required"] is False


def test_runtime_checkpoint_does_not_persist_audit_event_details_or_secrets(
    tmp_path: Path,
) -> None:
    checkpoint_path = tmp_path / "runtime_checkpoints.jsonl"
    audit_path = tmp_path / "audit.jsonl"
    ledger_path = tmp_path / "signal_ledger.jsonl"
    write_jsonl(ledger_path, [{"sequence": 1}])
    for index in range(3):
        append_audit_event(
            action="tool_call",
            resource_type="mcp_tool",
            resource_id="get_binance_coinm_account_snapshot",
            outcome="failure",
            actor="harness",
            audit_log_path=str(audit_path),
            details={
                "input": {
                    "api_key": "abcde12345key",
                    "api_secret": "super-secret",
                    "credential_passphrase": f"wrong-passphrase-{index}",
                    "credentials_path": str(tmp_path / "credentials.enc.json"),
                },
                "error": "invalid Binance credential passphrase.",
            },
            occurred_at=f"2026-05-10T00:0{index + 1}:00Z",
        )

    payload = record_runtime_checkpoint(
        checkpoint_path=str(checkpoint_path),
        audit_log_path=str(audit_path),
        ledger_path=str(ledger_path),
        run_id="run_secret_boundary",
        include_readiness=False,
    )
    checkpoint = read_jsonl(checkpoint_path)[0]
    serialized_payload = json.dumps(payload, sort_keys=True)
    serialized_checkpoint = json.dumps(checkpoint, sort_keys=True)

    assert payload["status"] == "recorded"
    assert checkpoint["runtime_status"] == "degraded"
    assert checkpoint["degraded_mode"] is True
    assert checkpoint["watchdog"]["failure_count"] == 3
    assert checkpoint["checkpoint_contract"]["secret_values_returned"] is False
    assert checkpoint["readiness_status"] is None
    for serialized in (serialized_payload, serialized_checkpoint):
        assert "get_binance_coinm_account_snapshot" not in serialized
        assert "credential_passphrase" not in serialized
        assert "credentials_path" not in serialized
        assert "abcde12345key" not in serialized
        assert "super-secret" not in serialized
        assert "wrong-passphrase" not in serialized
        assert "invalid Binance credential passphrase" not in serialized
        assert "salt_b64" not in serialized
        assert '"token":' not in serialized


def test_runtime_checkpoint_normalizes_public_run_id(tmp_path: Path) -> None:
    checkpoint_path = tmp_path / "runtime_checkpoints.jsonl"
    audit_path = tmp_path / "audit.jsonl"
    ledger_path = tmp_path / "signal_ledger.jsonl"
    write_jsonl(ledger_path, [{"sequence": 1}])

    payload = record_runtime_checkpoint(
        checkpoint_path=f" {checkpoint_path} ",
        audit_log_path=f" {audit_path} ",
        ledger_path=f" {ledger_path} ",
        run_id=" run_runtime ",
        include_readiness=False,
    )
    checkpoint = read_jsonl(checkpoint_path)[0]

    assert payload["checkpoint"]["run_id"] == "run_runtime"
    assert checkpoint["run_id"] == "run_runtime"
    assert checkpoint["checkpoint_id"].endswith("_run_runtime")
    assert checkpoint["readiness_status"] is None


def test_runtime_checkpoint_rejects_invalid_public_inputs(
    tmp_path: Path,
    monkeypatch,
) -> None:
    checkpoint_path = tmp_path / "runtime_checkpoints.jsonl"
    audit_path = tmp_path / "audit.jsonl"
    ledger_path = tmp_path / "signal_ledger.jsonl"
    monkeypatch.chdir(tmp_path)
    invalid_cases = [
        (
            {"include_readiness": "false"},
            "include_readiness must be a boolean",
        ),
        (
            {"run_id": "   "},
            "run_id must be a nonempty string",
        ),
        (
            {"run_id": 123},
            "run_id must be a nonempty string",
        ),
        (
            {"checkpoint_path": ""},
            "checkpoint_path must be a nonempty string",
        ),
        (
            {"audit_log_path": "   "},
            "audit_log_path must be a nonempty string",
        ),
        (
            {"ledger_path": 123},
            "ledger_path must be a nonempty string",
        ),
    ]

    for overrides, expected_error in invalid_cases:
        payload = {
            "checkpoint_path": str(checkpoint_path),
            "audit_log_path": str(audit_path),
            "ledger_path": str(ledger_path),
        }
        payload.update(overrides)
        with pytest.raises(ValueError, match=expected_error):
            record_runtime_checkpoint(**payload)

        assert not checkpoint_path.exists()
        assert not audit_path.exists()
        assert not ledger_path.exists()
        assert not (tmp_path / "state").exists()


def test_runtime_checkpoint_rejects_control_character_inputs(
    tmp_path: Path,
    monkeypatch,
) -> None:
    checkpoint_path = tmp_path / "runtime_checkpoints.jsonl"
    audit_path = tmp_path / "audit.jsonl"
    ledger_path = tmp_path / "signal_ledger.jsonl"
    monkeypatch.chdir(tmp_path)
    invalid_cases = [
        (
            {"run_id": "run_runtime\n"},
            "run_id must not contain control characters",
        ),
        (
            {"checkpoint_path": f"{checkpoint_path}\n"},
            "checkpoint_path must not contain control characters",
        ),
        (
            {"audit_log_path": f"{audit_path}\n"},
            "audit_log_path must not contain control characters",
        ),
        (
            {"ledger_path": f"{ledger_path}\n"},
            "ledger_path must not contain control characters",
        ),
    ]

    for overrides, expected_error in invalid_cases:
        payload = {
            "checkpoint_path": str(checkpoint_path),
            "audit_log_path": str(audit_path),
            "ledger_path": str(ledger_path),
            "include_readiness": False,
        }
        payload.update(overrides)
        with pytest.raises(ValueError, match=expected_error):
            record_runtime_checkpoint(**payload)

        assert not checkpoint_path.exists()
        assert not audit_path.exists()
        assert not ledger_path.exists()
        assert not (tmp_path / "state").exists()


def test_runtime_checkpoint_normalizes_env_checkpoint_path(
    tmp_path: Path,
    monkeypatch,
) -> None:
    checkpoint_path = tmp_path / "runtime_checkpoints.jsonl"
    audit_path = tmp_path / "audit.jsonl"
    ledger_path = tmp_path / "signal_ledger.jsonl"
    write_jsonl(ledger_path, [{"sequence": 1}])
    monkeypatch.setenv("HALO_SWING_RUNTIME_CHECKPOINT_PATH", f" {checkpoint_path} ")
    get_settings.cache_clear()

    payload = record_runtime_checkpoint(
        audit_log_path=str(audit_path),
        ledger_path=str(ledger_path),
        include_readiness=False,
    )

    assert payload["checkpoint_path"] == str(checkpoint_path)
    assert read_jsonl(checkpoint_path)[0]["readiness_status"] is None


def test_runtime_checkpoint_rejects_env_checkpoint_path_without_fallback(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.chdir(tmp_path)
    audit_path = tmp_path / "audit.jsonl"
    ledger_path = tmp_path / "signal_ledger.jsonl"
    invalid_cases = [
        (
            "",
            "HALO_SWING_RUNTIME_CHECKPOINT_PATH must be a nonempty string",
            tmp_path / "state",
        ),
        (
            "   ",
            "HALO_SWING_RUNTIME_CHECKPOINT_PATH must be a nonempty string",
            tmp_path / "   ",
        ),
        (
            f"{tmp_path / 'bad'}\x7fruntime_checkpoints.jsonl",
            "HALO_SWING_RUNTIME_CHECKPOINT_PATH must not contain control characters",
            tmp_path / "bad\x7fruntime_checkpoints.jsonl",
        ),
    ]

    for env_value, expected_error, unexpected_path in invalid_cases:
        monkeypatch.setenv("HALO_SWING_RUNTIME_CHECKPOINT_PATH", env_value)
        get_settings.cache_clear()

        with pytest.raises(ValueError, match=expected_error):
            record_runtime_checkpoint(
                audit_log_path=f"{audit_path}\n",
                ledger_path=f"{ledger_path}\n",
                include_readiness=False,
            )
        assert not unexpected_path.exists()
        assert not audit_path.exists()
        assert not ledger_path.exists()
        assert not (tmp_path / "state").exists()


def test_harness_rejects_invalid_runtime_checkpoint_input_with_failure_audit(
    tmp_path: Path,
) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    checkpoint_path = tmp_path / "runtime_checkpoints.jsonl"
    audit_path = tmp_path / "audit.jsonl"
    ledger_path = tmp_path / "signal_ledger.jsonl"
    input_payload = {
        "checkpoint_path": str(checkpoint_path),
        "audit_log_path": str(audit_path),
        "ledger_path": str(ledger_path),
        "include_readiness": "false",
    }
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "record_runtime_checkpoint",
            "--input-json",
            json.dumps(input_payload),
            "--audit-log-path",
            str(audit_path),
        ],
        check=False,
        cwd=tmp_path,
        env={**os.environ, "PYTHONPATH": str(repo_root / "src")},
        text=True,
        capture_output=True,
    )
    events = read_audit_events(audit_log_path=str(audit_path))
    event = events[0]

    assert result.returncode != 0
    assert result.stdout == ""
    assert "include_readiness must be a boolean" in result.stderr
    assert str(checkpoint_path) not in result.stderr
    assert str(audit_path) not in result.stderr
    assert str(ledger_path) not in result.stderr
    assert "runtime_checkpoints.jsonl" not in result.stderr
    assert "signal_ledger.jsonl" not in result.stderr
    assert "false" not in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "record_runtime_checkpoint"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "include_readiness must be a boolean" in event["details"]["error"]
    assert not checkpoint_path.exists()
    assert not ledger_path.exists()
    assert not (tmp_path / "state").exists()


def test_harness_rejects_runtime_checkpoint_include_readiness_numeric_without_checkpoint(
    tmp_path: Path,
) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    checkpoint_path = tmp_path / "runtime_checkpoints.jsonl"
    audit_path = tmp_path / "audit.jsonl"
    ledger_path = tmp_path / "signal_ledger.jsonl"
    input_payload = {
        "checkpoint_path": str(checkpoint_path),
        "audit_log_path": str(audit_path),
        "ledger_path": str(ledger_path),
        "include_readiness": 1,
    }
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "record_runtime_checkpoint",
            "--input-json",
            json.dumps(input_payload),
            "--audit-log-path",
            str(audit_path),
        ],
        check=False,
        cwd=tmp_path,
        env={**os.environ, "PYTHONPATH": str(repo_root / "src")},
        text=True,
        capture_output=True,
    )
    events = read_audit_events(audit_log_path=str(audit_path))
    event = events[0]

    assert result.returncode != 0
    assert result.stdout == ""
    assert "include_readiness must be a boolean" in result.stderr
    assert str(checkpoint_path) not in result.stderr
    assert str(audit_path) not in result.stderr
    assert str(ledger_path) not in result.stderr
    assert "runtime_checkpoints.jsonl" not in result.stderr
    assert "audit.jsonl" not in result.stderr
    assert "signal_ledger.jsonl" not in result.stderr
    assert '"include_readiness": 1' not in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "record_runtime_checkpoint"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "include_readiness must be a boolean" in event["details"]["error"]
    assert not checkpoint_path.exists()
    assert not ledger_path.exists()
    assert not (tmp_path / "state").exists()


def test_harness_rejects_runtime_checkpoint_include_readiness_zero_without_checkpoint(
    tmp_path: Path,
) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    checkpoint_path = tmp_path / "runtime_checkpoints.jsonl"
    audit_path = tmp_path / "audit.jsonl"
    ledger_path = tmp_path / "signal_ledger.jsonl"
    input_payload = {
        "checkpoint_path": str(checkpoint_path),
        "audit_log_path": str(audit_path),
        "ledger_path": str(ledger_path),
        "include_readiness": 0,
    }
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "record_runtime_checkpoint",
            "--input-json",
            json.dumps(input_payload),
            "--audit-log-path",
            str(audit_path),
        ],
        check=False,
        cwd=tmp_path,
        env={**os.environ, "PYTHONPATH": str(repo_root / "src")},
        text=True,
        capture_output=True,
    )
    events = read_audit_events(audit_log_path=str(audit_path))
    event = events[0]

    assert result.returncode != 0
    assert result.stdout == ""
    assert "include_readiness must be a boolean" in result.stderr
    assert str(checkpoint_path) not in result.stderr
    assert str(audit_path) not in result.stderr
    assert str(ledger_path) not in result.stderr
    assert "runtime_checkpoints.jsonl" not in result.stderr
    assert "audit.jsonl" not in result.stderr
    assert "signal_ledger.jsonl" not in result.stderr
    assert '"include_readiness": 0' not in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "record_runtime_checkpoint"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "include_readiness must be a boolean" in event["details"]["error"]
    assert not checkpoint_path.exists()
    assert not ledger_path.exists()
    assert not (tmp_path / "state").exists()


def test_harness_rejects_runtime_checkpoint_include_readiness_null_without_checkpoint(
    tmp_path: Path,
) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    checkpoint_path = tmp_path / "runtime_checkpoints.jsonl"
    audit_path = tmp_path / "audit.jsonl"
    ledger_path = tmp_path / "signal_ledger.jsonl"
    input_payload = {
        "checkpoint_path": str(checkpoint_path),
        "audit_log_path": str(audit_path),
        "ledger_path": str(ledger_path),
        "include_readiness": None,
    }
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "record_runtime_checkpoint",
            "--input-json",
            json.dumps(input_payload),
            "--audit-log-path",
            str(audit_path),
        ],
        check=False,
        cwd=tmp_path,
        env={**os.environ, "PYTHONPATH": str(repo_root / "src")},
        text=True,
        capture_output=True,
    )
    events = read_audit_events(audit_log_path=str(audit_path))
    event = events[0]

    assert result.returncode != 0
    assert result.stdout == ""
    assert "include_readiness must be a boolean" in result.stderr
    assert str(checkpoint_path) not in result.stderr
    assert str(audit_path) not in result.stderr
    assert str(ledger_path) not in result.stderr
    assert "runtime_checkpoints.jsonl" not in result.stderr
    assert "audit.jsonl" not in result.stderr
    assert "signal_ledger.jsonl" not in result.stderr
    assert '"include_readiness": null' not in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "record_runtime_checkpoint"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "include_readiness must be a boolean" in event["details"]["error"]
    assert not checkpoint_path.exists()
    assert not ledger_path.exists()
    assert not (tmp_path / "state").exists()


def test_harness_rejects_invalid_runtime_checkpoint_run_id_without_checkpoint(
    tmp_path: Path,
) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    checkpoint_path = tmp_path / "runtime_checkpoints.jsonl"
    audit_path = tmp_path / "audit.jsonl"
    ledger_path = tmp_path / "signal_ledger.jsonl"
    input_payload = {
        "checkpoint_path": str(checkpoint_path),
        "audit_log_path": str(audit_path),
        "ledger_path": str(ledger_path),
        "run_id": "   ",
        "include_readiness": False,
    }
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "record_runtime_checkpoint",
            "--input-json",
            json.dumps(input_payload),
            "--audit-log-path",
            str(audit_path),
        ],
        check=False,
        cwd=tmp_path,
        env={**os.environ, "PYTHONPATH": str(repo_root / "src")},
        text=True,
        capture_output=True,
    )
    events = read_audit_events(audit_log_path=str(audit_path))
    event = events[0]

    assert result.returncode != 0
    assert result.stdout == ""
    assert "run_id must be a nonempty string" in result.stderr
    assert str(checkpoint_path) not in result.stderr
    assert str(audit_path) not in result.stderr
    assert str(ledger_path) not in result.stderr
    assert "runtime_checkpoints.jsonl" not in result.stderr
    assert "audit.jsonl" not in result.stderr
    assert "signal_ledger.jsonl" not in result.stderr
    assert '"run_id": "   "' not in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "record_runtime_checkpoint"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "run_id must be a nonempty string" in event["details"]["error"]
    assert not checkpoint_path.exists()
    assert not ledger_path.exists()
    assert not (tmp_path / "state").exists()


def test_harness_rejects_runtime_checkpoint_run_id_type_without_checkpoint(
    tmp_path: Path,
) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    checkpoint_path = tmp_path / "runtime_checkpoints.jsonl"
    audit_path = tmp_path / "audit.jsonl"
    ledger_path = tmp_path / "signal_ledger.jsonl"
    input_payload = {
        "checkpoint_path": str(checkpoint_path),
        "audit_log_path": str(audit_path),
        "ledger_path": str(ledger_path),
        "run_id": 123,
        "include_readiness": False,
    }
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "record_runtime_checkpoint",
            "--input-json",
            json.dumps(input_payload),
            "--audit-log-path",
            str(audit_path),
        ],
        check=False,
        cwd=tmp_path,
        env={**os.environ, "PYTHONPATH": str(repo_root / "src")},
        text=True,
        capture_output=True,
    )
    events = read_audit_events(audit_log_path=str(audit_path))
    event = events[0]

    assert result.returncode != 0
    assert result.stdout == ""
    assert "run_id must be a nonempty string" in result.stderr
    assert str(checkpoint_path) not in result.stderr
    assert str(audit_path) not in result.stderr
    assert str(ledger_path) not in result.stderr
    assert "runtime_checkpoints.jsonl" not in result.stderr
    assert "audit.jsonl" not in result.stderr
    assert "signal_ledger.jsonl" not in result.stderr
    assert '"run_id": 123' not in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "record_runtime_checkpoint"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "run_id must be a nonempty string" in event["details"]["error"]
    assert not checkpoint_path.exists()
    assert not ledger_path.exists()
    assert not (tmp_path / "state").exists()


def test_harness_rejects_runtime_checkpoint_run_id_control_without_checkpoint(
    tmp_path: Path,
) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    checkpoint_path = tmp_path / "runtime_checkpoints.jsonl"
    audit_path = tmp_path / "audit.jsonl"
    ledger_path = tmp_path / "signal_ledger.jsonl"
    input_payload = {
        "checkpoint_path": str(checkpoint_path),
        "audit_log_path": str(audit_path),
        "ledger_path": str(ledger_path),
        "run_id": "run\x7fruntime",
        "include_readiness": False,
    }
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "record_runtime_checkpoint",
            "--input-json",
            json.dumps(input_payload),
            "--audit-log-path",
            str(audit_path),
        ],
        check=False,
        cwd=tmp_path,
        env={**os.environ, "PYTHONPATH": str(repo_root / "src")},
        text=True,
        capture_output=True,
    )
    events = read_audit_events(audit_log_path=str(audit_path))
    event = events[0]

    assert result.returncode != 0
    assert result.stdout == ""
    assert "run_id must not contain control characters" in result.stderr
    assert str(checkpoint_path) not in result.stderr
    assert str(audit_path) not in result.stderr
    assert str(ledger_path) not in result.stderr
    assert "runtime_checkpoints.jsonl" not in result.stderr
    assert "audit.jsonl" not in result.stderr
    assert "signal_ledger.jsonl" not in result.stderr
    assert "run\x7fruntime" not in result.stderr
    assert "\x7f" not in result.stderr
    assert "\\x7f" not in result.stderr
    assert "run\\u007fruntime" not in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "record_runtime_checkpoint"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "run_id must not contain control characters" in event["details"]["error"]
    assert not checkpoint_path.exists()
    assert not ledger_path.exists()
    assert not (tmp_path / "state").exists()


def test_harness_rejects_invalid_runtime_checkpoint_path_without_fallback(
    tmp_path: Path,
) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    audit_path = tmp_path / "audit.jsonl"
    ledger_path = tmp_path / "signal_ledger.jsonl"
    input_payload = {
        "checkpoint_path": "",
        "audit_log_path": str(audit_path),
        "ledger_path": str(ledger_path),
        "include_readiness": False,
    }
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "record_runtime_checkpoint",
            "--input-json",
            json.dumps(input_payload),
            "--audit-log-path",
            str(audit_path),
        ],
        check=False,
        cwd=tmp_path,
        env={**os.environ, "PYTHONPATH": str(repo_root / "src")},
        text=True,
        capture_output=True,
    )
    events = read_audit_events(audit_log_path=str(audit_path))
    event = events[0]

    assert result.returncode != 0
    assert result.stdout == ""
    assert "checkpoint_path must be a nonempty string" in result.stderr
    assert str(audit_path) not in result.stderr
    assert str(ledger_path) not in result.stderr
    assert "audit.jsonl" not in result.stderr
    assert "signal_ledger.jsonl" not in result.stderr
    assert '"checkpoint_path": ""' not in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "record_runtime_checkpoint"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "checkpoint_path must be a nonempty string" in event["details"]["error"]
    assert not (tmp_path / "state").exists()
    assert not ledger_path.exists()


def test_harness_rejects_runtime_checkpoint_path_type_without_fallback(
    tmp_path: Path,
) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    audit_path = tmp_path / "audit.jsonl"
    ledger_path = tmp_path / "signal_ledger.jsonl"
    input_payload = {
        "checkpoint_path": 123,
        "audit_log_path": str(audit_path),
        "ledger_path": str(ledger_path),
        "include_readiness": False,
    }
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "record_runtime_checkpoint",
            "--input-json",
            json.dumps(input_payload),
            "--audit-log-path",
            str(audit_path),
        ],
        check=False,
        cwd=tmp_path,
        env={**os.environ, "PYTHONPATH": str(repo_root / "src")},
        text=True,
        capture_output=True,
    )
    events = read_audit_events(audit_log_path=str(audit_path))
    event = events[0]

    assert result.returncode != 0
    assert result.stdout == ""
    assert "checkpoint_path must be a nonempty string" in result.stderr
    assert str(audit_path) not in result.stderr
    assert str(ledger_path) not in result.stderr
    assert "audit.jsonl" not in result.stderr
    assert "signal_ledger.jsonl" not in result.stderr
    assert '"checkpoint_path": 123' not in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "record_runtime_checkpoint"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "checkpoint_path must be a nonempty string" in event["details"]["error"]
    assert not (tmp_path / "state").exists()
    assert not ledger_path.exists()


def test_harness_rejects_runtime_checkpoint_path_control_character_without_fallback(
    tmp_path: Path,
) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    checkpoint_path = tmp_path / "bad\x7fruntime_checkpoints.jsonl"
    audit_path = tmp_path / "audit.jsonl"
    ledger_path = tmp_path / "signal_ledger.jsonl"
    input_payload = {
        "checkpoint_path": str(checkpoint_path),
        "audit_log_path": str(audit_path),
        "ledger_path": str(ledger_path),
        "include_readiness": False,
    }
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "record_runtime_checkpoint",
            "--input-json",
            json.dumps(input_payload),
            "--audit-log-path",
            str(audit_path),
        ],
        check=False,
        cwd=tmp_path,
        env={**os.environ, "PYTHONPATH": str(repo_root / "src")},
        text=True,
        capture_output=True,
    )
    events = read_audit_events(audit_log_path=str(audit_path))
    event = events[0]

    assert result.returncode != 0
    assert result.stdout == ""
    assert "checkpoint_path must not contain control characters" in result.stderr
    assert str(checkpoint_path) not in result.stderr
    assert str(audit_path) not in result.stderr
    assert str(ledger_path) not in result.stderr
    assert "bad" not in result.stderr
    assert "runtime_checkpoints.jsonl" not in result.stderr
    assert "audit.jsonl" not in result.stderr
    assert "signal_ledger.jsonl" not in result.stderr
    assert "\\x7f" not in result.stderr
    assert "bad\\u007fruntime_checkpoints.jsonl" not in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "record_runtime_checkpoint"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "checkpoint_path must not contain control characters" in event["details"][
        "error"
    ]
    assert not checkpoint_path.exists()
    assert not (tmp_path / "state").exists()
    assert not ledger_path.exists()


def test_harness_rejects_invalid_runtime_checkpoint_audit_path_without_checkpoint(
    tmp_path: Path,
) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    checkpoint_path = tmp_path / "runtime_checkpoints.jsonl"
    audit_path = tmp_path / "audit.jsonl"
    ledger_path = tmp_path / "signal_ledger.jsonl"
    input_payload = {
        "checkpoint_path": str(checkpoint_path),
        "audit_log_path": "   ",
        "ledger_path": str(ledger_path),
        "include_readiness": False,
    }
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "record_runtime_checkpoint",
            "--input-json",
            json.dumps(input_payload),
            "--audit-log-path",
            str(audit_path),
        ],
        check=False,
        cwd=tmp_path,
        env={**os.environ, "PYTHONPATH": str(repo_root / "src")},
        text=True,
        capture_output=True,
    )
    events = read_audit_events(audit_log_path=str(audit_path))
    event = events[0]

    assert result.returncode != 0
    assert result.stdout == ""
    assert "audit_log_path must be a nonempty string" in result.stderr
    assert str(checkpoint_path) not in result.stderr
    assert str(audit_path) not in result.stderr
    assert str(ledger_path) not in result.stderr
    assert "runtime_checkpoints.jsonl" not in result.stderr
    assert "audit.jsonl" not in result.stderr
    assert "signal_ledger.jsonl" not in result.stderr
    assert '"audit_log_path": "   "' not in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "record_runtime_checkpoint"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "audit_log_path must be a nonempty string" in event["details"]["error"]
    assert not checkpoint_path.exists()
    assert not ledger_path.exists()
    assert not (tmp_path / "state").exists()


def test_harness_rejects_runtime_checkpoint_audit_path_type_without_checkpoint(
    tmp_path: Path,
) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    checkpoint_path = tmp_path / "runtime_checkpoints.jsonl"
    audit_path = tmp_path / "audit.jsonl"
    ledger_path = tmp_path / "signal_ledger.jsonl"
    input_payload = {
        "checkpoint_path": str(checkpoint_path),
        "audit_log_path": 123,
        "ledger_path": str(ledger_path),
        "include_readiness": False,
    }
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "record_runtime_checkpoint",
            "--input-json",
            json.dumps(input_payload),
            "--audit-log-path",
            str(audit_path),
        ],
        check=False,
        cwd=tmp_path,
        env={**os.environ, "PYTHONPATH": str(repo_root / "src")},
        text=True,
        capture_output=True,
    )
    events = read_audit_events(audit_log_path=str(audit_path))
    event = events[0]

    assert result.returncode != 0
    assert result.stdout == ""
    assert "audit_log_path must be a nonempty string" in result.stderr
    assert str(checkpoint_path) not in result.stderr
    assert str(audit_path) not in result.stderr
    assert str(ledger_path) not in result.stderr
    assert "runtime_checkpoints.jsonl" not in result.stderr
    assert "audit.jsonl" not in result.stderr
    assert "signal_ledger.jsonl" not in result.stderr
    assert '"audit_log_path": 123' not in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "record_runtime_checkpoint"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "audit_log_path must be a nonempty string" in event["details"]["error"]
    assert not checkpoint_path.exists()
    assert not ledger_path.exists()
    assert not (tmp_path / "state").exists()


def test_harness_rejects_runtime_checkpoint_audit_path_control_character_without_checkpoint(
    tmp_path: Path,
) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    checkpoint_path = tmp_path / "runtime_checkpoints.jsonl"
    failure_audit_path = tmp_path / "audit.jsonl"
    runtime_audit_path = tmp_path / "bad\x7faudit.jsonl"
    ledger_path = tmp_path / "signal_ledger.jsonl"
    input_payload = {
        "checkpoint_path": str(checkpoint_path),
        "audit_log_path": str(runtime_audit_path),
        "ledger_path": str(ledger_path),
        "include_readiness": False,
    }
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "record_runtime_checkpoint",
            "--input-json",
            json.dumps(input_payload),
            "--audit-log-path",
            str(failure_audit_path),
        ],
        check=False,
        cwd=tmp_path,
        env={**os.environ, "PYTHONPATH": str(repo_root / "src")},
        text=True,
        capture_output=True,
    )
    events = read_audit_events(audit_log_path=str(failure_audit_path))
    event = events[0]

    assert result.returncode != 0
    assert result.stdout == ""
    assert "audit_log_path must not contain control characters" in result.stderr
    assert str(checkpoint_path) not in result.stderr
    assert str(failure_audit_path) not in result.stderr
    assert str(runtime_audit_path) not in result.stderr
    assert str(ledger_path) not in result.stderr
    assert "runtime_checkpoints.jsonl" not in result.stderr
    assert "audit.jsonl" not in result.stderr
    assert "signal_ledger.jsonl" not in result.stderr
    assert "bad" not in result.stderr
    assert "\\x7f" not in result.stderr
    assert "\\u007f" not in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "record_runtime_checkpoint"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "audit_log_path must not contain control characters" in event["details"][
        "error"
    ]
    assert not checkpoint_path.exists()
    assert not runtime_audit_path.exists()
    assert not ledger_path.exists()
    assert not (tmp_path / "state").exists()


def test_harness_rejects_invalid_runtime_checkpoint_ledger_path_without_checkpoint(
    tmp_path: Path,
) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    checkpoint_path = tmp_path / "runtime_checkpoints.jsonl"
    audit_path = tmp_path / "audit.jsonl"
    input_payload = {
        "checkpoint_path": str(checkpoint_path),
        "audit_log_path": str(audit_path),
        "ledger_path": "   ",
        "include_readiness": False,
    }
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "record_runtime_checkpoint",
            "--input-json",
            json.dumps(input_payload),
            "--audit-log-path",
            str(audit_path),
        ],
        check=False,
        cwd=tmp_path,
        env={**os.environ, "PYTHONPATH": str(repo_root / "src")},
        text=True,
        capture_output=True,
    )
    events = read_audit_events(audit_log_path=str(audit_path))
    event = events[0]

    assert result.returncode != 0
    assert result.stdout == ""
    assert "ledger_path must be a nonempty string" in result.stderr
    assert str(checkpoint_path) not in result.stderr
    assert str(audit_path) not in result.stderr
    assert "runtime_checkpoints.jsonl" not in result.stderr
    assert "audit.jsonl" not in result.stderr
    assert '"ledger_path": "   "' not in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "record_runtime_checkpoint"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "ledger_path must be a nonempty string" in event["details"]["error"]
    assert not checkpoint_path.exists()
    assert not (tmp_path / "state").exists()
    assert not (tmp_path / "   ").exists()


def test_harness_rejects_runtime_checkpoint_ledger_path_type_without_checkpoint(
    tmp_path: Path,
) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    checkpoint_path = tmp_path / "runtime_checkpoints.jsonl"
    audit_path = tmp_path / "audit.jsonl"
    input_payload = {
        "checkpoint_path": str(checkpoint_path),
        "audit_log_path": str(audit_path),
        "ledger_path": 123,
        "include_readiness": False,
    }
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "record_runtime_checkpoint",
            "--input-json",
            json.dumps(input_payload),
            "--audit-log-path",
            str(audit_path),
        ],
        check=False,
        cwd=tmp_path,
        env={**os.environ, "PYTHONPATH": str(repo_root / "src")},
        text=True,
        capture_output=True,
    )
    events = read_audit_events(audit_log_path=str(audit_path))
    event = events[0]

    assert result.returncode != 0
    assert result.stdout == ""
    assert "ledger_path must be a nonempty string" in result.stderr
    assert str(checkpoint_path) not in result.stderr
    assert str(audit_path) not in result.stderr
    assert "runtime_checkpoints.jsonl" not in result.stderr
    assert "audit.jsonl" not in result.stderr
    assert '"ledger_path": 123' not in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "record_runtime_checkpoint"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "ledger_path must be a nonempty string" in event["details"]["error"]
    assert not checkpoint_path.exists()
    assert not (tmp_path / "state").exists()


def test_harness_rejects_runtime_checkpoint_ledger_path_control_character_without_checkpoint(
    tmp_path: Path,
) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    checkpoint_path = tmp_path / "runtime_checkpoints.jsonl"
    audit_path = tmp_path / "audit.jsonl"
    ledger_path = tmp_path / "bad\x7fledger.jsonl"
    input_payload = {
        "checkpoint_path": str(checkpoint_path),
        "audit_log_path": str(audit_path),
        "ledger_path": str(ledger_path),
        "include_readiness": False,
    }
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "record_runtime_checkpoint",
            "--input-json",
            json.dumps(input_payload),
            "--audit-log-path",
            str(audit_path),
        ],
        check=False,
        cwd=tmp_path,
        env={**os.environ, "PYTHONPATH": str(repo_root / "src")},
        text=True,
        capture_output=True,
    )
    events = read_audit_events(audit_log_path=str(audit_path))
    event = events[0]

    assert result.returncode != 0
    assert result.stdout == ""
    assert "ledger_path must not contain control characters" in result.stderr
    assert str(checkpoint_path) not in result.stderr
    assert str(audit_path) not in result.stderr
    assert str(ledger_path) not in result.stderr
    assert "runtime_checkpoints.jsonl" not in result.stderr
    assert "audit.jsonl" not in result.stderr
    assert "ledger.jsonl" not in result.stderr
    assert "bad" not in result.stderr
    assert "\\x7f" not in result.stderr
    assert "\\u007f" not in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "record_runtime_checkpoint"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "ledger_path must not contain control characters" in event["details"][
        "error"
    ]
    assert not checkpoint_path.exists()
    assert not ledger_path.exists()
    assert not (tmp_path / "state").exists()


def test_harness_rejects_runtime_checkpoint_control_character_with_failure_audit(
    tmp_path: Path,
) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    checkpoint_path = tmp_path / "runtime_checkpoints.jsonl"
    audit_path = tmp_path / "audit.jsonl"
    ledger_path = tmp_path / "signal_ledger.jsonl"
    input_payload = {
        "checkpoint_path": str(checkpoint_path),
        "audit_log_path": str(audit_path),
        "ledger_path": str(ledger_path),
        "run_id": "run_runtime\n",
        "include_readiness": False,
    }
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "record_runtime_checkpoint",
            "--input-json",
            json.dumps(input_payload),
            "--audit-log-path",
            str(audit_path),
        ],
        check=False,
        cwd=tmp_path,
        env={**os.environ, "PYTHONPATH": str(repo_root / "src")},
        text=True,
        capture_output=True,
    )
    events = read_audit_events(audit_log_path=str(audit_path))
    event = events[0]

    assert result.returncode != 0
    assert result.stdout == ""
    assert "run_id must not contain control characters" in result.stderr
    assert str(checkpoint_path) not in result.stderr
    assert str(audit_path) not in result.stderr
    assert str(ledger_path) not in result.stderr
    assert "runtime_checkpoints.jsonl" not in result.stderr
    assert "audit.jsonl" not in result.stderr
    assert "signal_ledger.jsonl" not in result.stderr
    assert "run_runtime" not in result.stderr
    assert "\\n" not in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "record_runtime_checkpoint"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "run_id must not contain control characters" in event["details"]["error"]
    assert not checkpoint_path.exists()
    assert not ledger_path.exists()
    assert not (tmp_path / "state").exists()


def test_runtime_checkpoint_readiness_snapshot_does_not_persist_env_secrets(
    tmp_path: Path,
    monkeypatch,
) -> None:
    checkpoint_path = tmp_path / "runtime_checkpoints.jsonl"
    audit_path = tmp_path / "audit.jsonl"
    ledger_path = tmp_path / "signal_ledger.jsonl"
    write_jsonl(ledger_path, [{"sequence": 1}])
    secret_env_values = {
        "HALO_SWING_TELEGRAM_BOT_TOKEN": "telegram-secret-token",
        "TELEGRAM_BOT_TOKEN": "telegram-alias-secret-token",
        "HALO_SWING_TELEGRAM_GATEWAY": "https://gateway.example/secret",
        "HALO_SWING_TELEGRAM_GATEWAY_URL": "https://gateway-url.example/secret",
        "HALO_SWING_MARKET_DATA_SOURCE": "market-secret-source",
        "HALO_SWING_MARKET_DATA_API_KEY": "market-secret-key",
        "POLYGON_API_KEY": "polygon-secret-key",
        "ALPACA_API_KEY": "alpaca-secret-key",
        "TIINGO_API_KEY": "tiingo-secret-key",
        "HALO_SWING_MACRO_SOURCE": "macro-secret-source",
        "HALO_SWING_MACRO_API_KEY": "halo-macro-secret-key",
        "FRED_API_KEY": "fred-secret-key",
        "HALO_SWING_FRED_API_KEY": "halo-fred-secret-key",
        "HALO_SWING_NEWS_SOURCE": "news-secret-source",
        "NEWS_API_KEY": "news-secret-key",
        "HALO_SWING_NEWS_API_KEY": "halo-news-secret-key",
    }
    for env_key, env_value in secret_env_values.items():
        monkeypatch.setenv(env_key, env_value)

    payload = record_runtime_checkpoint(
        checkpoint_path=str(checkpoint_path),
        audit_log_path=str(audit_path),
        ledger_path=str(ledger_path),
        run_id="run_readiness_secret_boundary",
    )
    checkpoint = read_jsonl(checkpoint_path)[0]
    serialized_payload = json.dumps(payload, sort_keys=True)
    serialized_checkpoint = json.dumps(checkpoint, sort_keys=True)

    assert checkpoint["readiness_status"] == "blocked"
    assert checkpoint["readiness_next_actions"]
    assert checkpoint["checkpoint_contract"]["secret_values_returned"] is False
    assert "telegram: provide" not in checkpoint["readiness_next_actions"]
    assert "live_data: provide" not in checkpoint["readiness_next_actions"]
    for serialized in (serialized_payload, serialized_checkpoint):
        for env_key, env_value in secret_env_values.items():
            assert env_key not in serialized
            assert env_value not in serialized


def test_record_runtime_checkpoint_appends_snapshot(tmp_path: Path) -> None:
    checkpoint_path = tmp_path / "runtime_checkpoints.jsonl"
    audit_path = tmp_path / "audit.jsonl"
    ledger_path = tmp_path / "signal_ledger.jsonl"
    write_jsonl(ledger_path, [{"sequence": 1}])

    payload = record_runtime_checkpoint(
        checkpoint_path=str(checkpoint_path),
        audit_log_path=str(audit_path),
        ledger_path=str(ledger_path),
        run_id="run_test",
    )
    records = read_jsonl(checkpoint_path)
    checkpoint = records[0]

    assert payload["status"] == "recorded"
    assert payload["checkpoint_path"] == str(checkpoint_path)
    assert len(records) == 1
    assert checkpoint["schema_version"] == "runtime_checkpoint.v1"
    assert checkpoint["run_id"] == "run_test"
    assert checkpoint["runtime_status"] == "ok"
    assert checkpoint["readiness_status"] == "blocked"
    assert checkpoint["checkpoint_contract"]["append_only_jsonl"] is True
    assert checkpoint["checkpoint_contract"]["scheduler_added"] is False
    assert checkpoint["checkpoint_contract"]["network_call"] is False
    assert checkpoint["live_data_required"] is False
