import json
import subprocess
import sys
from io import BytesIO
from pathlib import Path

import pytest

from halo_swing_mcp.audit import (
    append_audit_event,
    audit_summary,
    read_audit_events,
    resolve_audit_log_path,
)
from halo_swing_mcp.audit_web import HTML, create_handler, events_payload, summary_payload
from halo_swing_mcp import server as mcp_server
from halo_swing_mcp import audit_web, binance_btc
from halo_swing_mcp.secret_store import save_binance_credentials
from halo_swing_mcp.tools.audit_tools import get_audit_log, get_audit_summary


ROOT = Path(__file__).resolve().parents[1]
MVP_CONTRACT = json.loads(
    (ROOT / "tests" / "golden" / "mvp_tool_contracts.json").read_text(
        encoding="utf-8"
    )
)
READINESS_ENV_SECRETS = {
    "HALO_SWING_TELEGRAM_BOT_TOKEN": "telegram-secret-token",
    "HALO_SWING_TELEGRAM_GATEWAY_URL": "https://gateway.example/secret",
    "HALO_SWING_MARKET_DATA_API_KEY": "market-secret-key",
    "FRED_API_KEY": "fred-secret-key",
    "NEWS_API_KEY": "news-secret-key",
}


def set_readiness_env_secrets(monkeypatch) -> dict[str, str]:
    for key, value in READINESS_ENV_SECRETS.items():
        monkeypatch.setenv(key, value)
    return READINESS_ENV_SECRETS


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
                "passphrase": "local-passphrase",
                "nested": {"authorization": "Bearer token"},
            }
        },
        occurred_at="2026-05-09T00:00:00Z",
    )
    events = read_audit_events(audit_log_path=str(audit_path))

    assert event["event_id"].startswith("aud_")
    assert events[0]["details"]["input"]["api_key"] == "[REDACTED]"
    assert events[0]["details"]["input"]["passphrase"] == "[REDACTED]"
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

    assert log_payload["schema_version"] == MVP_CONTRACT["audit_fixture"]["log_schema"]
    assert (
        summary_payload["schema_version"]
        == MVP_CONTRACT["audit_fixture"]["summary_schema"]
    )
    assert log_payload["count"] == 1
    assert log_payload["events"][0]["resource_id"] == "generate_trade_guide"
    assert log_payload["filters"]["limit"] == 5
    for field in MVP_CONTRACT["audit_fixture"]["required_payload_fields"]:
        assert field in log_payload
        assert field in summary_payload
    assert log_payload["network_call"] is False
    assert log_payload["secret_values_returned"] is False
    assert summary_payload["network_call"] is False
    assert summary_payload["secret_values_returned"] is False
    assert summary_payload["total_events"] == 1


def test_audit_log_normalizes_public_limit_and_filters(tmp_path: Path) -> None:
    audit_path = tmp_path / "audit.jsonl"
    append_audit_event(
        action="tool_call",
        resource_type="mcp_tool",
        resource_id="score_leverage_swing",
        outcome="failure",
        actor="test",
        audit_log_path=str(audit_path),
    )
    append_audit_event(
        action="tool_call",
        resource_type="mcp_tool",
        resource_id="health_check",
        outcome="success",
        actor="test",
        audit_log_path=str(audit_path),
    )

    filtered = get_audit_log(
        audit_log_path=f" {audit_path} ",
        limit=1001,
        action=" tool_call ",
        resource_type=" mcp_tool ",
        resource_id=" score_leverage_swing ",
        outcome=" failure ",
    )
    unfiltered = get_audit_log(
        audit_log_path=f" {audit_path} ",
        limit=1,
        action="   ",
        outcome="",
    )

    assert filtered["count"] == 1
    assert filtered["events"][0]["resource_id"] == "score_leverage_swing"
    assert filtered["filters"] == {
        "action": "tool_call",
        "resource_type": "mcp_tool",
        "resource_id": "score_leverage_swing",
        "outcome": "failure",
        "limit": 1000,
    }
    assert unfiltered["count"] == 1
    assert unfiltered["events"][0]["resource_id"] == "health_check"
    assert unfiltered["filters"]["action"] is None
    assert unfiltered["filters"]["outcome"] is None
    assert unfiltered["filters"]["limit"] == 1
    assert get_audit_summary(audit_log_path=f" {audit_path} ")["total_events"] == 2


def test_resolve_audit_log_path_normalizes_env_path(
    tmp_path: Path,
    monkeypatch,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    monkeypatch.setenv("HALO_SWING_AUDIT_LOG_PATH", f" {audit_path} ")

    assert resolve_audit_log_path() == audit_path


def test_append_audit_event_rejects_invalid_env_audit_path_without_fallback(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.chdir(tmp_path)
    invalid_cases = [
        ("", "HALO_SWING_AUDIT_LOG_PATH must be a nonempty string", tmp_path / "state"),
        ("   ", "HALO_SWING_AUDIT_LOG_PATH must be a nonempty string", tmp_path / "   "),
        (
            f"{tmp_path / 'bad'}\x7faudit.jsonl",
            "HALO_SWING_AUDIT_LOG_PATH must not contain control characters",
            tmp_path / "bad\x7faudit.jsonl",
        ),
    ]

    for env_value, expected_error, unexpected_path in invalid_cases:
        monkeypatch.setenv("HALO_SWING_AUDIT_LOG_PATH", env_value)
        with pytest.raises(ValueError, match=expected_error):
            append_audit_event(
                action="tool_call",
                resource_type="mcp_tool",
                resource_id="health_check",
                outcome="success",
                actor="test",
            )

        assert not unexpected_path.exists()


def test_audit_log_rejects_invalid_public_inputs(tmp_path: Path) -> None:
    audit_path = tmp_path / "audit.jsonl"
    invalid_cases = [
        (
            {"limit": 0},
            "limit must be a positive integer",
        ),
        (
            {"limit": False},
            "limit must be a positive integer",
        ),
        (
            {"limit": "5"},
            "limit must be a positive integer",
        ),
        (
            {"action": 123},
            "action must be a string when provided",
        ),
        (
            {"resource_type": []},
            "resource_type must be a string when provided",
        ),
        (
            {"resource_id": 123},
            "resource_id must be a string when provided",
        ),
        (
            {"outcome": False},
            "outcome must be a string when provided",
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
    ]

    for overrides, expected_error in invalid_cases:
        payload = {"audit_log_path": str(audit_path)}
        payload.update(overrides)
        with pytest.raises(ValueError, match=expected_error):
            get_audit_log(**payload)

    for invalid_path in ("", "   ", 123):
        with pytest.raises(ValueError, match="audit_log_path must be a nonempty string"):
            get_audit_summary(audit_log_path=invalid_path)


def test_audit_log_rejects_control_character_public_inputs(tmp_path: Path) -> None:
    audit_path = tmp_path / "audit.jsonl"
    invalid_cases = [
        (
            {"action": "tool_call\n"},
            "action must not contain control characters",
        ),
        (
            {"resource_type": "mcp_tool\n"},
            "resource_type must not contain control characters",
        ),
        (
            {"resource_id": "health_check\n"},
            "resource_id must not contain control characters",
        ),
        (
            {"outcome": "success\n"},
            "outcome must not contain control characters",
        ),
        (
            {"audit_log_path": f"{audit_path}\n"},
            "audit_log_path must not contain control characters",
        ),
    ]

    for overrides, expected_error in invalid_cases:
        payload = {"audit_log_path": str(audit_path)}
        payload.update(overrides)
        with pytest.raises(ValueError, match=expected_error):
            get_audit_log(**payload)

    with pytest.raises(
        ValueError,
        match="audit_log_path must not contain control characters",
    ):
        get_audit_summary(audit_log_path=f"{audit_path}\n")


def test_harness_rejects_invalid_audit_log_limit_with_failure_audit(
    tmp_path: Path,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    input_payload = {"audit_log_path": str(audit_path), "limit": 0}
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "get_audit_log",
            "--input-json",
            json.dumps(input_payload),
            "--audit-log-path",
            str(audit_path),
        ],
        check=False,
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    events = read_audit_events(audit_log_path=str(audit_path))
    event = events[0]

    assert result.returncode != 0
    assert result.stdout == ""
    assert "limit must be a positive integer" in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "get_audit_log"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "limit must be a positive integer" in event["details"]["error"]


def test_harness_rejects_invalid_audit_log_path_with_failure_audit(
    tmp_path: Path,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    input_payload = {"audit_log_path": "   ", "limit": 5}
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "get_audit_log",
            "--input-json",
            json.dumps(input_payload),
            "--audit-log-path",
            str(audit_path),
        ],
        check=False,
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    events = read_audit_events(audit_log_path=str(audit_path))
    event = events[0]

    assert result.returncode != 0
    assert result.stdout == ""
    assert "audit_log_path must be a nonempty string" in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "get_audit_log"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "audit_log_path must be a nonempty string" in event["details"]["error"]


def test_harness_rejects_audit_log_path_control_character_with_failure_audit(
    tmp_path: Path,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    input_payload = {"audit_log_path": f"{tmp_path / 'events.jsonl'}\n", "limit": 5}
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "get_audit_log",
            "--input-json",
            json.dumps(input_payload),
            "--audit-log-path",
            str(audit_path),
        ],
        check=False,
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    events = read_audit_events(audit_log_path=str(audit_path))
    event = events[0]

    assert result.returncode != 0
    assert result.stdout == ""
    assert "audit_log_path must not contain control characters" in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "get_audit_log"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "audit_log_path must not contain control characters" in event["details"][
        "error"
    ]


def test_harness_rejects_audit_log_filter_control_character_with_failure_audit(
    tmp_path: Path,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    input_payload = {
        "audit_log_path": str(tmp_path / "events.jsonl"),
        "limit": 5,
        "resource_id": "health_check\n",
    }
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "get_audit_log",
            "--input-json",
            json.dumps(input_payload),
            "--audit-log-path",
            str(audit_path),
        ],
        check=False,
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    events = read_audit_events(audit_log_path=str(audit_path))
    event = events[0]

    assert result.returncode != 0
    assert result.stdout == ""
    assert "resource_id must not contain control characters" in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "get_audit_log"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "resource_id must not contain control characters" in event["details"][
        "error"
    ]


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


def test_harness_integration_readiness_audit_redacts_env_secrets(
    tmp_path: Path,
    monkeypatch,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    env_secrets = set_readiness_env_secrets(monkeypatch)

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "get_integration_readiness",
            "--input-json",
            json.dumps(
                {"binance_credentials_path": str(tmp_path / "missing.enc.json")}
            ),
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
    event = events[0]
    raw_log = audit_path.read_text(encoding="utf-8")
    serialized_event = json.dumps(event, sort_keys=True)

    assert payload["status"] == "blocked"
    assert payload["gates"]["telegram"]["status"] == "ready"
    assert payload["gates"]["live_data"]["status"] == "ready"
    assert event["actor"] == "harness"
    assert event["resource_id"] == "get_integration_readiness"
    assert event["details"]["output_summary"]["status"] == "blocked"
    assert event["details"]["output_summary"]["keys"] == sorted(payload)
    for serialized in (result.stdout, raw_log, serialized_event):
        for key, value in env_secrets.items():
            assert key not in serialized
            assert value not in serialized


def test_mcp_server_integration_readiness_audit_redacts_env_secrets(
    tmp_path: Path,
    monkeypatch,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    monkeypatch.setenv("HALO_SWING_AUDIT_LOG_PATH", str(audit_path))
    env_secrets = set_readiness_env_secrets(monkeypatch)

    payload = mcp_server.get_integration_readiness(
        binance_credentials_path=str(tmp_path / "missing.enc.json")
    )
    events = read_audit_events(audit_log_path=str(audit_path))
    event = events[0]
    raw_log = audit_path.read_text(encoding="utf-8")
    serialized_event = json.dumps(event, sort_keys=True)

    assert payload["status"] == "blocked"
    assert payload["gates"]["telegram"]["status"] == "ready"
    assert payload["gates"]["live_data"]["status"] == "ready"
    assert event["actor"] == "mcp_server"
    assert event["resource_id"] == "get_integration_readiness"
    assert event["details"]["input"]["binance_credentials_path"] == "[REDACTED]"
    assert event["details"]["output_summary"]["status"] == "blocked"
    assert event["details"]["output_summary"]["keys"] == sorted(payload)
    for serialized in (
        json.dumps(payload, sort_keys=True),
        raw_log,
        serialized_event,
    ):
        for key, value in env_secrets.items():
            assert key not in serialized
            assert value not in serialized


def test_audit_read_surfaces_preserve_readiness_env_secret_boundary(
    tmp_path: Path,
    monkeypatch,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    monkeypatch.setenv("HALO_SWING_AUDIT_LOG_PATH", str(audit_path))
    env_secrets = set_readiness_env_secrets(monkeypatch)
    payload = mcp_server.get_integration_readiness(
        binance_credentials_path=str(tmp_path / "missing.enc.json")
    )

    tool_payload = get_audit_log(
        audit_log_path=str(audit_path),
        resource_id="get_integration_readiness",
        outcome="success",
        limit=5,
    )
    web_payload = events_payload(
        str(audit_path),
        {
            "resource_id": ["get_integration_readiness"],
            "outcome": ["success"],
            "limit": ["5"],
        },
    )
    tool_event = tool_payload["events"][0]
    web_event = web_payload["events"][0]

    assert payload["gates"]["telegram"]["status"] == "ready"
    assert payload["gates"]["live_data"]["status"] == "ready"
    assert tool_payload["count"] == 1
    assert tool_payload["secret_values_returned"] is False
    assert tool_event == web_event
    assert tool_event["actor"] == "mcp_server"
    assert tool_event["resource_id"] == "get_integration_readiness"
    assert tool_event["details"]["input"]["binance_credentials_path"] == "[REDACTED]"
    assert tool_event["details"]["output_summary"]["status"] == "blocked"
    for serialized in (
        json.dumps(tool_payload, sort_keys=True),
        json.dumps(web_payload, sort_keys=True),
    ):
        for key, value in env_secrets.items():
            assert key not in serialized
            assert value not in serialized


def test_audit_summary_surfaces_preserve_readiness_env_secret_boundary(
    tmp_path: Path,
    monkeypatch,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    monkeypatch.setenv("HALO_SWING_AUDIT_LOG_PATH", str(audit_path))
    env_secrets = set_readiness_env_secrets(monkeypatch)
    payload = mcp_server.get_integration_readiness(
        binance_credentials_path=str(tmp_path / "missing.enc.json")
    )

    tool_summary = get_audit_summary(audit_log_path=str(audit_path))
    web_summary = summary_payload(str(audit_path))

    assert payload["gates"]["telegram"]["status"] == "ready"
    assert payload["gates"]["live_data"]["status"] == "ready"
    assert tool_summary["total_events"] == 1
    assert tool_summary["by_outcome"] == {"success": 1}
    assert tool_summary["by_resource_type"] == {"mcp_tool": 1}
    assert tool_summary["secret_values_returned"] is False
    assert web_summary["total_events"] == 1
    assert web_summary["by_action"] == {"tool_call": 1}
    assert web_summary["by_outcome"] == {"success": 1}
    for serialized in (
        json.dumps(tool_summary, sort_keys=True),
        json.dumps(web_summary, sort_keys=True),
    ):
        for key, value in env_secrets.items():
            assert key not in serialized
            assert value not in serialized


def test_harness_save_binance_credentials_audit_redacts_secret_inputs(
    tmp_path: Path,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    credentials_path = tmp_path / "binance_credentials.enc.json"
    input_payload = {
        "api_key": "abcde12345key",
        "api_secret": "super-secret",
        "passphrase": "local-passphrase",
        "credentials_path": str(credentials_path),
    }
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "save_binance_credentials",
            "--input-json",
            json.dumps(input_payload),
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
    event = events[0]
    serialized_event = json.dumps(event, sort_keys=True)
    raw_log = audit_path.read_text(encoding="utf-8")

    assert payload["configured"] is True
    assert payload["api_key_hint"] == "abcde...5key"
    assert payload["secret_values_returned"] is False
    assert payload["passphrase_persisted"] is False
    assert event["actor"] == "harness"
    assert event["resource_id"] == "save_binance_credentials"
    assert event["details"]["input"]["api_key"] == "[REDACTED]"
    assert event["details"]["input"]["api_secret"] == "[REDACTED]"
    assert event["details"]["input"]["passphrase"] == "[REDACTED]"
    assert event["details"]["input"]["credentials_path"] == "[REDACTED]"
    assert event["details"]["output_summary"]["keys"] == sorted(payload)
    for serialized in (result.stdout, raw_log, serialized_event):
        assert "abcde12345key" not in serialized
        assert "super-secret" not in serialized
        assert "local-passphrase" not in serialized
        assert "salt_b64" not in serialized
        assert '"token":' not in serialized


def test_harness_account_snapshot_failure_audit_redacts_passphrase(
    tmp_path: Path,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    credentials_path = tmp_path / "binance_credentials.enc.json"
    save_binance_credentials(
        api_key="abcde12345key",
        api_secret="super-secret",
        passphrase="local-passphrase",
        credentials_path=str(credentials_path),
    )
    input_payload = {
        "credential_passphrase": "wrong-passphrase",
        "credentials_path": str(credentials_path),
    }
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "get_binance_coinm_account_snapshot",
            "--input-json",
            json.dumps(input_payload),
            "--audit-log-path",
            str(audit_path),
        ],
        check=False,
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    events = read_audit_events(audit_log_path=str(audit_path))
    event = events[0]
    raw_log = audit_path.read_text(encoding="utf-8")
    serialized_event = json.dumps(event, sort_keys=True)

    assert result.returncode != 0
    assert "invalid Binance credential passphrase" in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "get_binance_coinm_account_snapshot"
    assert event["outcome"] == "failure"
    assert event["details"]["input"]["credential_passphrase"] == "[REDACTED]"
    assert event["details"]["input"]["credentials_path"] == "[REDACTED]"
    assert "invalid Binance credential passphrase" in event["details"]["error"]
    for serialized in (raw_log, serialized_event):
        assert "abcde12345key" not in serialized
        assert "super-secret" not in serialized
        assert "local-passphrase" not in serialized
        assert "wrong-passphrase" not in serialized
        assert "salt_b64" not in serialized
        assert '"token":' not in serialized
        assert "credential_passphrase" in serialized


def test_audit_read_surfaces_preserve_redacted_failure_event(
    tmp_path: Path,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    credentials_path = tmp_path / "binance_credentials.enc.json"
    save_binance_credentials(
        api_key="abcde12345key",
        api_secret="super-secret",
        passphrase="local-passphrase",
        credentials_path=str(credentials_path),
    )
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "get_binance_coinm_account_snapshot",
            "--input-json",
            json.dumps(
                {
                    "credential_passphrase": "wrong-passphrase",
                    "credentials_path": str(credentials_path),
                }
            ),
            "--audit-log-path",
            str(audit_path),
        ],
        check=False,
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    tool_payload = get_audit_log(
        audit_log_path=str(audit_path),
        resource_id="get_binance_coinm_account_snapshot",
        outcome="failure",
        limit=5,
    )
    web_payload = events_payload(
        str(audit_path),
        {
            "resource_id": ["get_binance_coinm_account_snapshot"],
            "outcome": ["failure"],
            "limit": ["5"],
        },
    )
    tool_event = tool_payload["events"][0]
    web_event = web_payload["events"][0]

    assert result.returncode != 0
    assert tool_payload["count"] == 1
    assert tool_payload["secret_values_returned"] is False
    assert tool_event == web_event
    assert tool_event["outcome"] == "failure"
    assert tool_event["details"]["input"]["credential_passphrase"] == "[REDACTED]"
    assert tool_event["details"]["input"]["credentials_path"] == "[REDACTED]"
    for serialized in (
        json.dumps(tool_payload, sort_keys=True),
        json.dumps(web_payload, sort_keys=True),
    ):
        assert "abcde12345key" not in serialized
        assert "super-secret" not in serialized
        assert "local-passphrase" not in serialized
        assert "wrong-passphrase" not in serialized
        assert "salt_b64" not in serialized
        assert '"token":' not in serialized
        assert "credential_passphrase" in serialized


def test_mcp_server_execute_order_audit_redacts_credential_passphrase(
    tmp_path: Path,
    monkeypatch,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    monkeypatch.setenv("HALO_SWING_AUDIT_LOG_PATH", str(audit_path))
    payload = mcp_server.execute_btc_order(
        side="BUY",
        quantity="1",
        credential_passphrase="local-passphrase",
    )
    events = read_audit_events(audit_log_path=str(audit_path))
    event = events[0]
    raw_log = audit_path.read_text(encoding="utf-8")
    serialized_event = json.dumps(event, sort_keys=True)

    assert payload["status"] == "blocked"
    assert payload["blocked_reason"] == "missing_confirmation"
    assert event["actor"] == "mcp_server"
    assert event["resource_id"] == "execute_btc_order"
    assert event["details"]["input"]["credential_passphrase"] == "[REDACTED]"
    assert event["details"]["output_summary"]["blocked_reason"] == "missing_confirmation"
    for serialized in (raw_log, serialized_event):
        assert "local-passphrase" not in serialized
        assert "credential_passphrase" in serialized


def test_mcp_server_account_snapshot_audit_redacts_credential_passphrase(
    tmp_path: Path,
    monkeypatch,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    credentials_path = tmp_path / "binance_credentials.enc.json"
    monkeypatch.setenv("HALO_SWING_AUDIT_LOG_PATH", str(audit_path))
    save_binance_credentials(
        api_key="abcde12345key",
        api_secret="super-secret",
        passphrase="local-passphrase",
        credentials_path=str(credentials_path),
    )
    signed_calls: list[dict[str, object]] = []

    def fake_signed_get(**kwargs: object) -> list[dict[str, str]]:
        signed_calls.append(kwargs)
        if len(signed_calls) == 1:
            return [{"asset": "BTC", "balance": "0.01000000"}]
        return [{"symbol": "BTCUSD_PERP", "positionAmt": "0"}]

    monkeypatch.setattr(binance_btc, "_signed_get", fake_signed_get)
    payload = mcp_server.get_binance_coinm_account_snapshot(
        credential_passphrase="local-passphrase",
        credentials_path=str(credentials_path),
    )
    events = read_audit_events(audit_log_path=str(audit_path))
    event = events[0]
    raw_log = audit_path.read_text(encoding="utf-8")
    serialized_event = json.dumps(event, sort_keys=True)

    assert payload["status"] == "ok"
    assert payload["credentials"]["api_key_hint"] == "abcde...5key"
    assert len(signed_calls) == 2
    assert event["actor"] == "mcp_server"
    assert event["resource_id"] == "get_binance_coinm_account_snapshot"
    assert event["details"]["input"]["credential_passphrase"] == "[REDACTED]"
    assert event["details"]["input"]["credentials_path"] == "[REDACTED]"
    assert event["details"]["output_summary"]["status"] == "ok"
    for serialized in (raw_log, serialized_event):
        assert "abcde12345key" not in serialized
        assert "super-secret" not in serialized
        assert "local-passphrase" not in serialized
        assert "salt_b64" not in serialized
        assert '"token":' not in serialized
        assert "credential_passphrase" in serialized


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


def test_audit_web_main_rejects_non_localhost_bind(capsys) -> None:
    result = audit_web.main(["--host", "0.0.0.0", "--port", "8765"])
    captured = capsys.readouterr()

    assert result == 2
    assert "Audit web must bind to localhost only." in captured.err


def test_audit_web_main_rejects_invalid_port_without_server(
    monkeypatch,
    capsys,
) -> None:
    def fail_resolve_path(*_args: object, **_kwargs: object) -> None:
        raise AssertionError("audit path must not resolve with an invalid port")

    def fail_server(*_args: object, **_kwargs: object) -> None:
        raise AssertionError("server must not bind with an invalid port")

    monkeypatch.setattr(
        "halo_swing_mcp.audit_web.resolve_audit_log_path",
        fail_resolve_path,
    )
    monkeypatch.setattr(
        "halo_swing_mcp.audit_web.ThreadingHTTPServer",
        fail_server,
    )

    for port in ("-1", "65536"):
        result = audit_web.main(["--host", "127.0.0.1", "--port", port])
        captured = capsys.readouterr()

        assert result == 2
        assert "Audit web port must be between 0 and 65535." in captured.err


def test_audit_web_main_allows_localhost_ephemeral_port(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    server_events: list[tuple[str, object]] = []

    class FakeServer:
        server_address = ("127.0.0.1", 8765)

        def __init__(self, server_address: tuple[str, int], _handler: object) -> None:
            server_events.append(("init", server_address))

        def serve_forever(self) -> None:
            server_events.append(("serve_forever", None))
            raise KeyboardInterrupt

        def server_close(self) -> None:
            server_events.append(("server_close", None))

    monkeypatch.setattr(
        "halo_swing_mcp.audit_web.ThreadingHTTPServer",
        FakeServer,
    )

    result = audit_web.main(
        [
            "--host",
            "127.0.0.1",
            "--port",
            "0",
            "--audit-log-path",
            str(audit_path),
        ]
    )
    captured = capsys.readouterr()

    assert result == 0
    assert server_events == [
        ("init", ("127.0.0.1", 0)),
        ("serve_forever", None),
        ("server_close", None),
    ]
    assert "Serving Halo Swing audit log at http://127.0.0.1:8765" in captured.out
    assert f"Audit log: {audit_path}" in captured.out


def test_audit_web_main_rejects_invalid_audit_log_path_without_server(
    monkeypatch,
    capsys,
) -> None:
    def fail_server(*_args: object, **_kwargs: object) -> None:
        raise AssertionError("server must not bind with an invalid audit log path")

    monkeypatch.setattr(
        "halo_swing_mcp.audit_web.ThreadingHTTPServer",
        fail_server,
    )

    for audit_log_path, expected_error in (
        ("", "audit_log_path must be a nonempty string"),
        ("   ", "audit_log_path must be a nonempty string"),
        ("bad\x7faudit.jsonl", "audit_log_path must not contain control characters"),
    ):
        result = audit_web.main(
            [
                "--host",
                "127.0.0.1",
                "--port",
                "8765",
                "--audit-log-path",
                audit_log_path,
            ]
        )
        captured = capsys.readouterr()

        assert result == 2
        assert expected_error in captured.err


def test_audit_web_main_rejects_invalid_env_audit_log_path_without_server(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("HALO_SWING_AUDIT_LOG_PATH", "   ")

    def fail_server(*_args: object, **_kwargs: object) -> None:
        raise AssertionError("server must not bind with an invalid audit log path")

    monkeypatch.setattr(
        "halo_swing_mcp.audit_web.ThreadingHTTPServer",
        fail_server,
    )

    result = audit_web.main(["--host", "127.0.0.1", "--port", "8765"])
    captured = capsys.readouterr()

    assert result == 2
    assert "HALO_SWING_AUDIT_LOG_PATH must be a nonempty string" in captured.err
    assert not (tmp_path / "state").exists()
    assert not (tmp_path / "   ").exists()


def test_audit_web_events_payload_normalizes_query_inputs(tmp_path: Path) -> None:
    audit_path = tmp_path / "audit.jsonl"
    append_audit_event(
        action="tool_call",
        resource_type="mcp_tool",
        resource_id="health_check",
        outcome="success",
        actor="test",
        audit_log_path=str(audit_path),
    )
    append_audit_event(
        action="tool_call",
        resource_type="mcp_tool",
        resource_id="score_leverage_swing",
        outcome="failure",
        actor="test",
        audit_log_path=str(audit_path),
    )

    filtered = events_payload(
        str(audit_path),
        {
            "limit": [" 1001 "],
            "action": [" tool_call "],
            "resource_type": [" mcp_tool "],
            "resource_id": [" health_check "],
            "outcome": [" success "],
        },
    )
    unfiltered = events_payload(
        str(audit_path),
        {"limit": [""], "resource_id": ["   "]},
    )

    assert len(filtered["events"]) == 1
    assert filtered["events"][0]["resource_id"] == "health_check"
    assert len(unfiltered["events"]) == 2


def test_audit_web_events_payload_rejects_invalid_query_inputs(
    tmp_path: Path,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    invalid_cases = [
        (
            {"limit": ["0"]},
            "limit must be a positive integer",
        ),
        (
            {"limit": ["1.5"]},
            "limit must be a positive integer",
        ),
        (
            {"limit": [False]},
            "limit must be a positive integer",
        ),
        (
            {"resource_id": [123]},
            "resource_id must be a string when provided",
        ),
    ]

    for query, expected_error in invalid_cases:
        with pytest.raises(ValueError, match=expected_error):
            events_payload(str(audit_path), query)


def test_audit_web_events_payload_rejects_control_character_query_inputs(
    tmp_path: Path,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    invalid_cases = [
        (
            {"limit": ["10\n"]},
            "limit must not contain control characters",
        ),
        (
            {"action": ["tool_call\n"]},
            "action must not contain control characters",
        ),
        (
            {"resource_type": ["mcp_tool\n"]},
            "resource_type must not contain control characters",
        ),
        (
            {"resource_id": ["health_check\n"]},
            "resource_id must not contain control characters",
        ),
        (
            {"outcome": ["success\n"]},
            "outcome must not contain control characters",
        ),
    ]

    for query, expected_error in invalid_cases:
        with pytest.raises(ValueError, match=expected_error):
            events_payload(str(audit_path), query)


def test_audit_web_events_endpoint_returns_bad_request_for_invalid_query(
    tmp_path: Path,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    response_payload = _audit_web_get(
        str(audit_path),
        "/api/events?limit=0",
        expected_status="HTTP/1.0 400 Bad Request",
    )

    assert response_payload == {"error": "limit must be a positive integer"}


def test_audit_web_events_endpoint_returns_bad_request_for_control_character_query(
    tmp_path: Path,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    response_payload = _audit_web_get(
        str(audit_path),
        "/api/events?resource_id=health_check%0A",
        expected_status="HTTP/1.0 400 Bad Request",
    )

    assert response_payload == {
        "error": "resource_id must not contain control characters"
    }


def _audit_web_get(
    audit_log_path: str,
    path: str,
    expected_status: str = "HTTP/1.0 200 OK",
) -> dict[str, object]:
    raw_request = (
        f"GET {path} HTTP/1.1\r\n"
        "Host: 127.0.0.1\r\n"
        "\r\n"
    ).encode("utf-8")
    socket = _MemorySocket(raw_request)
    create_handler(audit_log_path)(socket, ("127.0.0.1", 0), object())
    response = socket.output.getvalue()
    headers, _, response_body = response.partition(b"\r\n\r\n")
    status_line = headers.splitlines()[0].decode("ascii")

    assert status_line == expected_status
    parsed = json.loads(response_body.decode("utf-8"))
    assert isinstance(parsed, dict)
    return parsed


class _MemorySocket:
    def __init__(self, raw_request: bytes) -> None:
        self.input = BytesIO(raw_request)
        self.output = BytesIO()

    def makefile(
        self,
        mode: str,
        buffering: int | None = None,
    ) -> BytesIO:
        if "r" in mode:
            return self.input
        return self.output

    def sendall(self, data: bytes) -> None:
        self.output.write(data)

    def close(self) -> None:
        self.input.close()
        self.output.close()
