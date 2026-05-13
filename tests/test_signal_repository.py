from pathlib import Path

import pytest

from halo_swing_mcp.signal_repository import JsonlSignalLedgerRepository


def test_jsonl_signal_repository_appends_and_deduplicates(tmp_path: Path) -> None:
    ledger_path = tmp_path / "signal_ledger.jsonl"
    repository = JsonlSignalLedgerRepository(ledger_path)
    record = {
        "signal": {"signal_id": "sig_test_001", "config_hash": "sha256:test"},
        "labels": [],
    }

    status, stored = repository.append_if_absent(
        signal_id="sig_test_001",
        record=record,
    )
    duplicate_status, duplicate = repository.append_if_absent(
        signal_id="sig_test_001",
        record={"signal": {"signal_id": "sig_test_001"}, "labels": []},
    )

    assert status == "recorded"
    assert stored == record
    assert duplicate_status == "duplicate"
    assert duplicate == record
    assert repository.ledger_ref == str(ledger_path)
    assert repository.find_by_signal_id("sig_test_001") == record
    assert repository.latest_record() == record


def test_jsonl_signal_repository_appends_label_persistently(tmp_path: Path) -> None:
    ledger_path = tmp_path / "signal_ledger.jsonl"
    repository = JsonlSignalLedgerRepository(ledger_path)
    repository.append_if_absent(
        signal_id="sig_test_001",
        record={
            "signal": {"signal_id": "sig_test_001", "config_hash": "sha256:test"},
            "labels": [],
        },
    )
    label = {
        "signal_id": "sig_test_001",
        "outcome": "TAKE_PROFIT_FIRST",
        "realized_r": 2.0,
    }

    updated = repository.append_label(signal_id="sig_test_001", label=label)
    missing_updated = repository.append_label(signal_id="missing", label=label)
    reloaded = JsonlSignalLedgerRepository(ledger_path)

    assert updated is True
    assert missing_updated is False
    assert reloaded.find_by_signal_id("sig_test_001")["labels"] == [label]


def test_jsonl_signal_repository_normalizes_env_ledger_path(
    tmp_path: Path,
    monkeypatch,
) -> None:
    ledger_path = tmp_path / "signal_ledger.jsonl"
    monkeypatch.setenv("HALO_SWING_LEDGER_PATH", f" {ledger_path} ")
    repository = JsonlSignalLedgerRepository()

    assert repository.ledger_ref == str(ledger_path)


def test_jsonl_signal_repository_rejects_invalid_env_ledger_path(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.chdir(tmp_path)
    invalid_cases = [
        ("", "HALO_SWING_LEDGER_PATH must be a nonempty string", tmp_path / "state"),
        ("   ", "HALO_SWING_LEDGER_PATH must be a nonempty string", tmp_path / "   "),
        (
            f"{tmp_path / 'bad'}\x7fledger.jsonl",
            "HALO_SWING_LEDGER_PATH must not contain control characters",
            tmp_path / "bad\x7fledger.jsonl",
        ),
    ]

    for env_value, expected_error, unexpected_path in invalid_cases:
        monkeypatch.setenv("HALO_SWING_LEDGER_PATH", env_value)
        with pytest.raises(ValueError, match=expected_error):
            JsonlSignalLedgerRepository()

        assert not unexpected_path.exists()
