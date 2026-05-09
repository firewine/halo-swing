import json
import subprocess
import sys
from pathlib import Path

from halo_swing_mcp.audit import (
    append_audit_event,
    audit_summary,
    read_audit_events,
)
from halo_swing_mcp.audit_web import HTML, events_payload, summary_payload
from halo_swing_mcp.tools.audit_tools import get_audit_log, get_audit_summary


ROOT = Path(__file__).resolve().parents[1]


def test_audit_event_redacts_sensitive_details(tmp_path: Path) -> None:
    audit_path = tmp_path / "audit.jsonl"

    event = append_audit_event(
        action="tool_call",
        resource_type="mcp_tool",
        resource_id="score_leverage_swing",
        outcome="success",
        actor="test",
        audit_log_path=str(audit_path),
        details={
            "input": {
                "asset": "TQQQ",
                "api_key": "secret-value",
                "nested": {"authorization": "Bearer token"},
            }
        },
        occurred_at="2026-05-09T00:00:00Z",
    )
    events = read_audit_events(audit_log_path=str(audit_path))

    assert event["event_id"].startswith("aud_")
    assert events[0]["details"]["input"]["api_key"] == "[REDACTED]"
    assert events[0]["details"]["input"]["nested"]["authorization"] == "[REDACTED]"


def test_audit_log_filters_and_summary(tmp_path: Path) -> None:
    audit_path = tmp_path / "audit.jsonl"
    append_audit_event(
        action="tool_call",
        resource_type="mcp_tool",
        resource_id="health_check",
        outcome="success",
        actor="test",
        audit_log_path=str(audit_path),
        occurred_at="2026-05-09T00:00:00Z",
    )
    append_audit_event(
        action="tool_call",
        resource_type="mcp_tool",
        resource_id="score_leverage_swing",
        outcome="failure",
        actor="test",
        audit_log_path=str(audit_path),
        occurred_at="2026-05-09T00:01:00Z",
    )

    failures = read_audit_events(audit_log_path=str(audit_path), outcome="failure")
    summary = audit_summary(audit_log_path=str(audit_path))

    assert len(failures) == 1
    assert failures[0]["resource_id"] == "score_leverage_swing"
    assert summary["total_events"] == 2
    assert summary["by_outcome"] == {"failure": 1, "success": 1}


def test_audit_tools_return_events_and_summary(tmp_path: Path) -> None:
    audit_path = tmp_path / "audit.jsonl"
    append_audit_event(
        action="tool_call",
        resource_type="mcp_tool",
        resource_id="generate_trade_guide",
        outcome="success",
        actor="test",
        audit_log_path=str(audit_path),
    )

    log_payload = get_audit_log(audit_log_path=str(audit_path), limit=5)
    summary_payload = get_audit_summary(audit_log_path=str(audit_path))

    assert log_payload["count"] == 1
    assert log_payload["events"][0]["resource_id"] == "generate_trade_guide"
    assert summary_payload["total_events"] == 1


def test_harness_writes_audit_event(tmp_path: Path) -> None:
    audit_path = tmp_path / "audit.jsonl"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "health_check",
            "--input-json",
            '{"asset": "TQQQ", "api_key": "should-redact"}',
            "--audit-log-path",
            str(audit_path),
        ],
        check=True,
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    payload = json.loads(result.stdout)
    events = read_audit_events(audit_log_path=str(audit_path))

    assert payload["status"] == "ok"
    assert events[0]["actor"] == "harness"
    assert events[0]["resource_id"] == "health_check"
    assert events[0]["details"]["input"]["api_key"] == "[REDACTED]"


def test_audit_web_builds_html_and_json_payloads(tmp_path: Path) -> None:
    audit_path = tmp_path / "audit.jsonl"
    append_audit_event(
        action="tool_call",
        resource_type="mcp_tool",
        resource_id="health_check",
        outcome="success",
        actor="test",
        audit_log_path=str(audit_path),
    )

    events = events_payload(
        str(audit_path),
        {"limit": ["10"], "resource_id": ["health_check"]},
    )
    summary = summary_payload(str(audit_path))

    assert "Halo Swing Audit Log" in HTML
    assert "fetch(\"/api/summary\")" in HTML
    assert events["events"][0]["resource_id"] == "health_check"
    assert summary["total_events"] == 1
