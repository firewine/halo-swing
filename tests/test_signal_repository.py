from pathlib import Path

import pytest

from halo_swing_mcp.signal_repository import (
    JsonlSignalLedgerRepository,
    SQLiteSignalLedgerRepository,
)


def repository_record(
    *,
    signal_id: str,
    asset: str,
    underlying: str,
    timeframe: str,
    created_at: str,
) -> dict[str, object]:
    config_hash = f"sha256:{signal_id:0<64}"[:71]
    run_id = f"run_{signal_id}"
    return {
        "recorded_at": created_at,
        "signal": {
            "signal_id": signal_id,
            "run_id": run_id,
            "created_at": created_at,
            "asset": asset,
            "underlying": underlying,
            "timeframe": timeframe,
            "action": "WAIT",
            "final_score": 0.5,
            "confidence": 0.6,
            "data_freshness_status": "FRESH",
            "config_hash": config_hash,
            "config_version": "test",
        },
        "feature_snapshot": {
            "symbol": underlying,
            "timeframe": timeframe,
        },
        "evidence_cards": [],
        "artifact_refs": [],
        "run_journal": {
            "run_id": run_id,
            "idempotency_key": f"idempotency:{signal_id}",
            "trigger": "record_signal",
            "status": "completed",
            "started_at": created_at,
            "finished_at": created_at,
        },
        "strategy_config": {
            "schema_version": "strategy_config.v1",
            "config_hash": config_hash,
            "config_version": "test",
        },
        "config_hash": config_hash,
        "labels": [],
    }


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


def test_jsonl_signal_repository_latest_matching_record_matches_existing_reverse_scan(
    tmp_path: Path,
) -> None:
    ledger_path = tmp_path / "signal_ledger.jsonl"
    repository = JsonlSignalLedgerRepository(ledger_path)
    first_record = repository_record(
        signal_id="sig_test_tqqq_swing",
        asset="TQQQ",
        underlying="QQQ",
        timeframe="swing_3d_10d",
        created_at="2026-05-20T10:00:00Z",
    )
    second_record = repository_record(
        signal_id="sig_test_tqqq_alt",
        asset="TQQQ",
        underlying="QQQ",
        timeframe="swing_5d_20d",
        created_at="2026-05-20T11:00:00Z",
    )
    repository.append_if_absent(
        signal_id="sig_test_tqqq_swing",
        record=first_record,
    )
    repository.append_if_absent(
        signal_id="sig_test_tqqq_alt",
        record=second_record,
    )

    assert repository.latest_matching_record(asset="TQQQ") == second_record
    assert (
        repository.latest_matching_record(asset="TQQQ", timeframe="swing_3d_10d")
        == first_record
    )
    assert repository.latest_matching_record(asset="SSO") is None


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


def test_sqlite_signal_repository_initializes_migrated_database(
    tmp_path: Path,
) -> None:
    database_path = tmp_path / "halo_swing.sqlite"
    repository = SQLiteSignalLedgerRepository(database_path)

    assert repository.ledger_ref == f"sqlite:{database_path}"
    assert repository.storage_name == "sqlite_signal_repository"
    assert repository.db_required is True
    assert database_path.exists()


def test_sqlite_signal_repository_latest_matching_record_uses_searchable_core_fields(
    tmp_path: Path,
) -> None:
    database_path = tmp_path / "halo_swing.sqlite"
    repository = SQLiteSignalLedgerRepository(database_path)
    tqqq_record = repository_record(
        signal_id="sig_test_tqqq_swing",
        asset="TQQQ",
        underlying="QQQ",
        timeframe="swing_3d_10d",
        created_at="2026-05-20T10:00:00Z",
    )
    sso_record = repository_record(
        signal_id="sig_test_sso_swing",
        asset="SSO",
        underlying="SPY",
        timeframe="swing_3d_10d",
        created_at="2026-05-20T11:00:00Z",
    )
    later_tqqq_record = repository_record(
        signal_id="sig_test_tqqq_alt",
        asset="TQQQ",
        underlying="QQQ",
        timeframe="swing_5d_20d",
        created_at="2026-05-20T12:00:00Z",
    )
    for record in (tqqq_record, sso_record, later_tqqq_record):
        repository.append_if_absent(
            signal_id=str(record["signal"]["signal_id"]),
            record=record,
        )

    assert repository.latest_matching_record()["signal"]["signal_id"] == (
        "sig_test_tqqq_alt"
    )
    assert repository.latest_matching_record(asset="SSO")["signal"]["signal_id"] == (
        "sig_test_sso_swing"
    )
    assert repository.latest_matching_record(underlying="SPY")["signal"][
        "signal_id"
    ] == "sig_test_sso_swing"
    assert repository.latest_matching_record(
        asset="TQQQ",
        timeframe="swing_3d_10d",
    )["signal"]["signal_id"] == "sig_test_tqqq_swing"
    assert repository.latest_matching_record(asset="SOXL") is None
