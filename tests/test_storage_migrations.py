from __future__ import annotations

import json
import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest

from halo_swing_mcp.contracts import StorageHealth
from halo_swing_mcp.storage_migrations import (
    DOMAIN_TABLES,
    apply_migrations,
    get_storage_health,
)
from halo_swing_mcp.tool_registry import call_tool


ROOT = Path(__file__).resolve().parents[1]


def test_initial_replay_schema_migration_is_idempotent(tmp_path: Path) -> None:
    database_path = tmp_path / "halo_swing.sqlite"

    first_result = apply_migrations(database_path)
    second_result = apply_migrations(database_path)

    assert first_result.applied_versions == (
        "202605100001_initial_replay_schema",
    )
    assert first_result.skipped_versions == ()
    assert second_result.applied_versions == ()
    assert second_result.skipped_versions == (
        "202605100001_initial_replay_schema",
    )
    assert second_result.migration_count == 1
    assert second_result.latest_migration == "202605100001_initial_replay_schema"
    assert second_result.domain_tables_present == DOMAIN_TABLES


def test_storage_health_reports_applied_migration_and_domain_tables(
    tmp_path: Path,
) -> None:
    database_path = tmp_path / "halo_swing.sqlite"

    apply_migrations(database_path)
    health = get_storage_health(database_path)

    assert StorageHealth.model_validate(health).model_dump(mode="json") == health
    assert health["status"] == "ok"
    assert health["driver"] == "sqlite"
    assert health["migration_count"] == 1
    assert health["latest_migration"] == "202605100001_initial_replay_schema"
    assert health["domain_tables_present"] == list(DOMAIN_TABLES)
    assert health["live_data_required"] is False


def test_storage_health_tool_reports_missing_database_without_creating_artifact(
    tmp_path: Path,
) -> None:
    database_path = tmp_path / "nested" / "halo_swing.sqlite"

    health = call_tool("get_storage_health", {"database_path": f" {database_path} "})

    assert StorageHealth.model_validate(health).model_dump(mode="json") == health
    assert health["status"] == "ok"
    assert health["migration_count"] == 0
    assert health["latest_migration"] is None
    assert health["domain_tables_present"] == []
    assert health["live_data_required"] is False
    assert not database_path.exists()
    assert list((ROOT / "data").glob("*.sqlite")) == []
    assert list((ROOT / "state").glob("*.sqlite")) == []


def test_apply_storage_migrations_tool_is_idempotent_and_reports_tables(
    tmp_path: Path,
) -> None:
    database_path = tmp_path / "nested" / "halo_swing.sqlite"

    first_result = call_tool(
        "apply_storage_migrations",
        {"database_path": f" {database_path} "},
    )
    second_result = call_tool(
        "apply_storage_migrations",
        {"database_path": str(database_path)},
    )

    assert first_result["status"] == "ok"
    assert first_result["database_path"] == str(database_path)
    assert first_result["applied_versions"] == [
        "202605100001_initial_replay_schema",
    ]
    assert first_result["skipped_versions"] == []
    assert first_result["migration_count"] == 1
    assert first_result["latest_migration"] == "202605100001_initial_replay_schema"
    assert first_result["domain_tables_present"] == list(DOMAIN_TABLES)
    assert first_result["live_data_required"] is False
    assert first_result["secret_values_returned"] is False
    assert second_result["applied_versions"] == []
    assert second_result["skipped_versions"] == [
        "202605100001_initial_replay_schema",
    ]
    assert second_result["domain_tables_present"] == list(DOMAIN_TABLES)
    assert database_path.exists()
    assert database_path.is_relative_to(tmp_path)
    assert list((ROOT / "data").glob("*.sqlite")) == []
    assert list((ROOT / "state").glob("*.sqlite")) == []


def test_storage_health_harness_reports_migrated_database(
    tmp_path: Path,
) -> None:
    database_path = tmp_path / "halo_swing.sqlite"
    apply_migrations(database_path)

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "get_storage_health",
            "--input-json",
            json.dumps({"database_path": str(database_path)}),
            "--no-audit",
        ],
        check=True,
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    health = json.loads(result.stdout)

    assert StorageHealth.model_validate(health).model_dump(mode="json") == health
    assert health["migration_count"] == 1
    assert health["latest_migration"] == "202605100001_initial_replay_schema"
    assert health["domain_tables_present"] == list(DOMAIN_TABLES)


def test_apply_storage_migrations_harness_reports_idempotent_result(
    tmp_path: Path,
) -> None:
    database_path = tmp_path / "halo_swing.sqlite"

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "apply_storage_migrations",
            "--input-json",
            json.dumps({"database_path": str(database_path)}),
            "--no-audit",
        ],
        check=True,
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    payload = json.loads(result.stdout)

    assert payload["status"] == "ok"
    assert payload["database_path"] == str(database_path)
    assert payload["applied_versions"] == ["202605100001_initial_replay_schema"]
    assert payload["skipped_versions"] == []
    assert payload["migration_count"] == 1
    assert payload["domain_tables_present"] == list(DOMAIN_TABLES)
    assert payload["secret_values_returned"] is False


def test_initial_replay_schema_contains_required_indexes_and_foreign_keys(
    tmp_path: Path,
) -> None:
    database_path = tmp_path / "halo_swing.sqlite"
    apply_migrations(database_path)

    with sqlite3.connect(database_path) as connection:
        indexes = {
            row[1]
            for row in connection.execute(
                "SELECT type, name FROM sqlite_master WHERE type = 'index'"
            ).fetchall()
        }
        signal_foreign_keys = {
            (row[2], row[3], row[4])
            for row in connection.execute("PRAGMA foreign_key_list(signal_ledger)")
        }
        label_foreign_keys = {
            (row[2], row[3], row[4])
            for row in connection.execute("PRAGMA foreign_key_list(label_store)")
        }

    assert {
        "idx_signal_ledger_created_at",
        "idx_signal_ledger_asset",
        "idx_signal_ledger_underlying",
        "idx_signal_ledger_timeframe",
        "idx_signal_ledger_action",
        "idx_signal_ledger_config_hash",
        "idx_signal_ledger_data_freshness_status",
        "idx_feature_store_asset",
        "idx_feature_store_underlying",
        "idx_feature_store_timeframe",
        "idx_run_journal_status",
        "idx_label_store_signal_id",
        "idx_label_store_outcome",
    }.issubset(indexes)
    assert (
        "run_journal",
        "run_id",
        "run_id",
    ) in signal_foreign_keys
    assert (
        "feature_store",
        "feature_snapshot_id",
        "feature_snapshot_id",
    ) in signal_foreign_keys
    assert (
        "strategy_config",
        "config_hash",
        "config_hash",
    ) in signal_foreign_keys
    assert ("signal_ledger", "signal_id", "signal_id") in label_foreign_keys


def test_migration_runner_rejects_checksum_mismatch(
    tmp_path: Path,
) -> None:
    database_path = tmp_path / "halo_swing.sqlite"
    apply_migrations(database_path)

    with sqlite3.connect(database_path) as connection:
        connection.execute(
            "UPDATE schema_migrations SET checksum = ? WHERE version = ?",
            ("tampered", "202605100001_initial_replay_schema"),
        )

    with pytest.raises(ValueError, match="checksum mismatch"):
        apply_migrations(database_path)


def test_migration_creates_database_only_under_requested_tmp_path(
    tmp_path: Path,
) -> None:
    database_path = tmp_path / "nested" / "halo_swing.sqlite"

    apply_migrations(database_path)

    assert database_path.exists()
    assert database_path.is_relative_to(tmp_path)
    assert list((ROOT / "data").glob("*.sqlite")) == []
    assert list((ROOT / "data").glob("*.sqlite3")) == []
    assert list((ROOT / "state").glob("*.sqlite")) == []
    assert list((ROOT / "state").glob("*.sqlite3")) == []
