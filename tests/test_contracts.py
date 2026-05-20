import json
import re
from pathlib import Path

import pytest
from pydantic import ValidationError

from halo_swing_mcp.contracts import (
    LatestSignalReport,
    SignalReplayBundle,
    StorageHealth,
    TradeAction,
)


ROOT = Path(__file__).resolve().parents[1]
GOLDEN_DIR = ROOT / "tests" / "golden"

SUMMARY_FIELDS = (
    "entry_summary",
    "stop_summary",
    "take_profit_summary",
    "invalidation_summary",
    "risk_summary",
)

DTO_FIXTURES = (
    ("latest_signal_report.json", LatestSignalReport),
    ("latest_signal_report_degraded.json", LatestSignalReport),
    ("signal_replay_bundle.json", SignalReplayBundle),
    ("storage_health.json", StorageHealth),
)

REPLAY_REQUIRED_KEYS = {
    "signal",
    "feature_snapshot",
    "evidence_cards",
    "strategy_config",
    "run_journal",
    "label_outcome",
    "missing_links",
}

DRIVE_ROOT_RE = re.compile(r"^[A-Za-z]:[\\/]")


def load_json(name: str) -> dict[str, object]:
    return json.loads((GOLDEN_DIR / name).read_text(encoding="utf-8"))


def assert_round_trip(model: type, payload: dict[str, object]) -> None:
    assert model.model_validate(payload).model_dump(mode="json") == payload


def iter_nested_strings(value: object) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        strings: list[str] = []
        for nested_value in value.values():
            strings.extend(iter_nested_strings(nested_value))
        return strings
    if isinstance(value, list):
        strings = []
        for nested_value in value:
            strings.extend(iter_nested_strings(nested_value))
        return strings
    return []


@pytest.mark.parametrize(("fixture_name", "model"), DTO_FIXTURES)
def test_dto_golden_fixtures_round_trip(
    fixture_name: str,
    model: type,
) -> None:
    assert_round_trip(model, load_json(fixture_name))


def test_latest_signal_report_fixtures_validate_and_contrast() -> None:
    normal = LatestSignalReport.model_validate(load_json("latest_signal_report.json"))
    degraded = LatestSignalReport.model_validate(
        load_json("latest_signal_report_degraded.json")
    )

    assert normal.action == TradeAction.BUY_2X
    assert degraded.action == TradeAction.WAIT
    assert degraded.confidence < normal.confidence
    assert normal.data_warnings == []
    assert degraded.data_warnings

    for report in (normal, degraded):
        for field_name in SUMMARY_FIELDS:
            value = getattr(report, field_name)
            assert isinstance(value, str)
            assert value.strip()


def test_latest_signal_report_accepts_structured_label_status() -> None:
    payload = load_json("latest_signal_report.json")
    payload["label_status"] = {
        "schema_version": "signal_label_outcome.v1",
        "signal_id": payload["signal_id"],
        "outcome": "TAKE_PROFIT_FIRST",
        "realized_r": 2.0,
        "first_barrier_hit": "take_profit",
        "labeled_at": "2026-05-20T00:00:00Z",
        "time_barrier_days": 2,
        "live_data_required": False,
    }

    report = LatestSignalReport.model_validate(payload).model_dump(mode="json")

    assert report["label_status"] == payload["label_status"]


def test_signal_replay_bundle_fixture_validates_and_preserves_links() -> None:
    payload = load_json("signal_replay_bundle.json")
    bundle = SignalReplayBundle.model_validate(payload)

    assert REPLAY_REQUIRED_KEYS.issubset(payload)
    assert bundle.signal["config_hash"] == bundle.strategy_config["config_hash"]
    assert bundle.signal["run_id"] == bundle.run_journal["run_id"]
    assert len(bundle.evidence_cards) >= 2
    assert all(card["modality"] for card in bundle.evidence_cards)
    assert len(bundle.artifact_refs) == len(bundle.evidence_cards)
    assert all(ref["artifact_ref_id"].endswith(":artifact") for ref in bundle.artifact_refs)
    assert all(ref["ref"] and not ref["ref"].startswith("/") for ref in bundle.artifact_refs)


def test_latest_signal_report_rejects_missing_required_field() -> None:
    payload = load_json("latest_signal_report.json")
    payload.pop("signal_id")

    with pytest.raises(ValidationError):
        LatestSignalReport.model_validate(payload)


def test_latest_signal_report_rejects_invalid_action_enum() -> None:
    payload = load_json("latest_signal_report.json")
    payload["action"] = "HOLD"

    with pytest.raises(ValidationError):
        LatestSignalReport.model_validate(payload)


@pytest.mark.parametrize(("fixture_name", "_model"), DTO_FIXTURES)
def test_dto_golden_fixtures_do_not_embed_local_paths(
    fixture_name: str,
    _model: type,
) -> None:
    strings = iter_nested_strings(load_json(fixture_name))

    for value in strings:
        lowered = value.lower()
        assert "/Users/" not in value
        assert "file://" not in value
        assert not value.startswith("~/")
        assert not DRIVE_ROOT_RE.match(value)
        assert ".sqlite" not in lowered
        assert ".sqlite3" not in lowered


def test_no_sqlite_db_artifacts_exist_in_repo() -> None:
    assert list(ROOT.rglob("*.sqlite")) == []
    assert list(ROOT.rglob("*.sqlite3")) == []
