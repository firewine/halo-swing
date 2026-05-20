"""Repository contract plus JSONL and SQLite adapters for signal ledger records."""

from __future__ import annotations

import json
import os
import sqlite3
from pathlib import Path
from typing import Any, Protocol

from halo_swing_mcp.config import get_settings
from halo_swing_mcp.storage_migrations import apply_migrations


class SignalLedgerRepository(Protocol):
    """Minimal repository boundary for signal replay and labeling."""

    @property
    def ledger_ref(self) -> str:
        """Portable reference to the backing ledger."""

    @property
    def storage_name(self) -> str:
        """Stable storage contract name for run journal metadata."""

    @property
    def db_required(self) -> bool:
        """Return whether this repository persists through a database."""

    def list_records(self) -> list[dict[str, Any]]:
        """Return all ledger records in insertion order."""

    def find_by_signal_id(self, signal_id: str) -> dict[str, Any] | None:
        """Return one signal record if present."""

    def latest_record(self) -> dict[str, Any] | None:
        """Return the newest ledger record if present."""

    def latest_matching_record(
        self,
        *,
        asset: str | None = None,
        underlying: str | None = None,
        timeframe: str | None = None,
    ) -> dict[str, Any] | None:
        """Return the newest ledger record matching searchable signal fields."""

    def append_if_absent(
        self,
        *,
        signal_id: str,
        record: dict[str, Any],
    ) -> tuple[str, dict[str, Any]]:
        """Append a record unless the signal_id already exists."""

    def append_label(self, *, signal_id: str, label: dict[str, Any]) -> bool:
        """Append a label to an existing signal record."""


class JsonlSignalLedgerRepository:
    """Append-oriented JSONL implementation for local offline harnesses."""

    def __init__(self, ledger_path: str | os.PathLike[str] | None = None) -> None:
        if ledger_path is not None:
            configured = _normalize_ledger_path(ledger_path, "ledger_path")
        elif "HALO_SWING_LEDGER_PATH" in os.environ:
            configured = _normalize_ledger_path(
                os.environ["HALO_SWING_LEDGER_PATH"],
                "HALO_SWING_LEDGER_PATH",
            )
        else:
            configured = _normalize_ledger_path(
                get_settings().ledger_path,
                "settings.ledger_path",
            )
        self.path = Path(configured)

    @property
    def ledger_ref(self) -> str:
        return str(self.path)

    @property
    def storage_name(self) -> str:
        return "jsonl_signal_ledger_record"

    @property
    def db_required(self) -> bool:
        return False

    def list_records(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []

        records: list[dict[str, Any]] = []
        with self.path.open(encoding="utf-8") as handle:
            for line in handle:
                stripped = line.strip()
                if stripped:
                    records.append(json.loads(stripped))
        return records

    def find_by_signal_id(self, signal_id: str) -> dict[str, Any] | None:
        for record in self.list_records():
            if record.get("signal", {}).get("signal_id") == signal_id:
                return record
        return None

    def latest_record(self) -> dict[str, Any] | None:
        records = self.list_records()
        return records[-1] if records else None

    def latest_matching_record(
        self,
        *,
        asset: str | None = None,
        underlying: str | None = None,
        timeframe: str | None = None,
    ) -> dict[str, Any] | None:
        for record in reversed(self.list_records()):
            if _record_matches_signal_filters(
                record,
                asset=asset,
                underlying=underlying,
                timeframe=timeframe,
            ):
                return record
        return None

    def append_if_absent(
        self,
        *,
        signal_id: str,
        record: dict[str, Any],
    ) -> tuple[str, dict[str, Any]]:
        existing = self.find_by_signal_id(signal_id)
        if existing is not None:
            return "duplicate", existing

        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
        return "recorded", record

    def append_label(self, *, signal_id: str, label: dict[str, Any]) -> bool:
        records = self.list_records()
        updated = False
        for record in records:
            if record.get("signal", {}).get("signal_id") == signal_id:
                record.setdefault("labels", []).append(label)
                updated = True
                break

        if updated:
            self._write_records(records)
        return updated

    def _write_records(self, records: list[dict[str, Any]]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path = self.path.with_suffix(f"{self.path.suffix}.tmp")
        with temporary_path.open("w", encoding="utf-8") as handle:
            for record in records:
                handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
        temporary_path.replace(self.path)


class SQLiteSignalLedgerRepository:
    """SQLite implementation for replay-safe repository persistence."""

    def __init__(self, database_path: str | os.PathLike[str]) -> None:
        configured = _normalize_ledger_path(database_path, "database_path")
        self.path = Path(configured)
        apply_migrations(self.path)

    @property
    def ledger_ref(self) -> str:
        return f"sqlite:{self.path}"

    @property
    def storage_name(self) -> str:
        return "sqlite_signal_repository"

    @property
    def db_required(self) -> bool:
        return True

    def list_records(self) -> list[dict[str, Any]]:
        with self._connect() as connection:
            signal_rows = connection.execute(
                """
                SELECT
                    signal_id,
                    signal_json,
                    feature_snapshot_id,
                    evidence_card_ids_json,
                    artifact_ref_ids_json,
                    run_id,
                    config_hash
                FROM signal_ledger
                ORDER BY created_at, signal_id
                """
            ).fetchall()
            return [self._record_from_row(connection, row) for row in signal_rows]

    def find_by_signal_id(self, signal_id: str) -> dict[str, Any] | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT
                    signal_id,
                    signal_json,
                    feature_snapshot_id,
                    evidence_card_ids_json,
                    artifact_ref_ids_json,
                    run_id,
                    config_hash
                FROM signal_ledger
                WHERE signal_id = ?
                """,
                (signal_id,),
            ).fetchone()
            return self._record_from_row(connection, row) if row else None

    def latest_record(self) -> dict[str, Any] | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT
                    signal_id,
                    signal_json,
                    feature_snapshot_id,
                    evidence_card_ids_json,
                    artifact_ref_ids_json,
                    run_id,
                    config_hash
                FROM signal_ledger
                ORDER BY created_at DESC, signal_id DESC
                LIMIT 1
                """
            ).fetchone()
            return self._record_from_row(connection, row) if row else None

    def latest_matching_record(
        self,
        *,
        asset: str | None = None,
        underlying: str | None = None,
        timeframe: str | None = None,
    ) -> dict[str, Any] | None:
        where_clauses: list[str] = []
        parameters: list[str] = []
        if asset is not None:
            where_clauses.append("asset = ?")
            parameters.append(asset)
        if underlying is not None:
            where_clauses.append("underlying = ?")
            parameters.append(underlying)
        if timeframe is not None:
            where_clauses.append("timeframe = ?")
            parameters.append(timeframe)

        where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""
        query = f"""
            SELECT
                signal_id,
                signal_json,
                feature_snapshot_id,
                evidence_card_ids_json,
                artifact_ref_ids_json,
                run_id,
                config_hash
            FROM signal_ledger
            {where_sql}
            ORDER BY created_at DESC, signal_id DESC
            LIMIT 1
            """
        with self._connect() as connection:
            row = connection.execute(query, parameters).fetchone()
            return self._record_from_row(connection, row) if row else None

    def append_if_absent(
        self,
        *,
        signal_id: str,
        record: dict[str, Any],
    ) -> tuple[str, dict[str, Any]]:
        existing = self.find_by_signal_id(signal_id)
        if existing is not None:
            return "duplicate", existing

        with self._connect() as connection:
            try:
                connection.execute("BEGIN")
                self._insert_record(connection, signal_id, record)
            except Exception:
                connection.rollback()
                raise
            else:
                connection.commit()

        stored = self.find_by_signal_id(signal_id)
        return "recorded", stored if stored is not None else record

    def append_label(self, *, signal_id: str, label: dict[str, Any]) -> bool:
        if self.find_by_signal_id(signal_id) is None:
            return False

        with self._connect() as connection:
            label_count = connection.execute(
                "SELECT COUNT(*) FROM label_store WHERE signal_id = ?",
                (signal_id,),
            ).fetchone()[0]
            label_id = f"{signal_id}:label:{label_count + 1}"
            connection.execute(
                """
                INSERT INTO label_store (
                    label_id,
                    signal_id,
                    outcome,
                    labeled_at,
                    horizon_days,
                    label_json
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    label_id,
                    signal_id,
                    str(label.get("outcome", "UNKNOWN")),
                    str(label.get("labeled_at", "")),
                    label.get("time_barrier_days"),
                    _json_dumps(label),
                ),
            )
        return True

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def _insert_record(
        self,
        connection: sqlite3.Connection,
        signal_id: str,
        record: dict[str, Any],
    ) -> None:
        signal = _expect_mapping(record.get("signal"), "record.signal")
        feature_snapshot = _expect_mapping(
            record.get("feature_snapshot"),
            "record.feature_snapshot",
        )
        run_journal = _expect_mapping(record.get("run_journal"), "record.run_journal")
        strategy_config = _expect_mapping(
            record.get("strategy_config"),
            "record.strategy_config",
        )
        evidence_cards = _expect_list(record.get("evidence_cards"), "record.evidence_cards")

        run_id = str(run_journal["run_id"])
        config_hash = str(signal["config_hash"])
        created_at = str(signal["created_at"])
        feature_snapshot_id = f"{signal_id}:feature_snapshot"
        evidence_ids = [str(card["evidence_id"]) for card in evidence_cards]
        artifact_ids: list[str] = []

        connection.execute(
            """
            INSERT OR IGNORE INTO strategy_config (
                config_hash,
                schema_version,
                config_json,
                created_at
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                config_hash,
                "strategy_config.v1",
                _json_dumps(
                    {
                        **strategy_config,
                        "schema_version": strategy_config.get(
                            "schema_version",
                            "strategy_config.v1",
                        ),
                        "config_hash": config_hash,
                        "config_version": strategy_config.get(
                            "config_version",
                            signal.get("config_version"),
                        ),
                    }
                ),
                created_at,
            ),
        )
        connection.execute(
            """
            INSERT INTO run_journal (
                run_id,
                idempotency_key,
                run_type,
                status,
                started_at,
                completed_at,
                metadata_json
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                run_id,
                run_journal.get("idempotency_key"),
                str(run_journal.get("trigger", "record_signal")),
                str(run_journal.get("status", "completed")),
                str(run_journal.get("started_at", created_at)),
                run_journal.get("finished_at"),
                _json_dumps(run_journal),
            ),
        )
        connection.execute(
            """
            INSERT INTO feature_store (
                feature_snapshot_id,
                asset,
                underlying,
                timeframe,
                created_at,
                features_json
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                feature_snapshot_id,
                str(signal.get("asset", "")),
                str(signal["underlying"]),
                str(signal.get("timeframe", "swing_3d_10d")),
                created_at,
                _json_dumps(feature_snapshot),
            ),
        )

        for card in evidence_cards:
            self._insert_evidence_card(connection, card, created_at, artifact_ids)

        connection.execute(
            """
            INSERT INTO signal_ledger (
                signal_id,
                created_at,
                asset,
                underlying,
                timeframe,
                action,
                final_score,
                confidence,
                data_freshness_status,
                run_id,
                feature_snapshot_id,
                config_hash,
                evidence_card_ids_json,
                artifact_ref_ids_json,
                signal_json
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                signal_id,
                created_at,
                str(signal.get("asset", "")),
                str(signal["underlying"]),
                str(signal.get("timeframe", "swing_3d_10d")),
                str(signal.get("action", "")),
                float(signal.get("final_score", 0.0)),
                float(signal.get("confidence", 0.0)),
                str(signal.get("data_freshness_status", "UNKNOWN")),
                run_id,
                feature_snapshot_id,
                config_hash,
                _json_dumps(evidence_ids),
                _json_dumps(artifact_ids),
                _json_dumps(signal),
            ),
        )

    def _insert_evidence_card(
        self,
        connection: sqlite3.Connection,
        card: dict[str, Any],
        created_at: str,
        artifact_ids: list[str],
    ) -> None:
        evidence_id = str(card["evidence_id"])
        artifact_ref = card.get("artifact_ref")
        if isinstance(artifact_ref, dict):
            artifact_ref_id = f"{evidence_id}:artifact"
            artifact_ids.append(artifact_ref_id)
            connection.execute(
                """
                INSERT OR IGNORE INTO artifact_ref (
                    artifact_ref_id,
                    ref_type,
                    ref,
                    metadata_json,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    artifact_ref_id,
                    str(artifact_ref.get("ref_type", "OTHER")),
                    str(artifact_ref.get("ref", "")),
                    _json_dumps(artifact_ref.get("metadata", {})),
                    created_at,
                ),
            )
        connection.execute(
            """
            INSERT OR IGNORE INTO evidence_card (
                evidence_id,
                modality,
                summary,
                source_ref,
                created_at,
                payload_json
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                evidence_id,
                str(card.get("modality", "unknown")),
                str(card.get("summary", "")),
                str(card.get("source") or card.get("source_group") or ""),
                created_at,
                _json_dumps(card),
            ),
        )

    def _record_from_row(
        self,
        connection: sqlite3.Connection,
        row: sqlite3.Row | tuple[Any, ...],
    ) -> dict[str, Any]:
        (
            signal_id,
            signal_json,
            feature_snapshot_id,
            evidence_ids_json,
            artifact_ids_json,
            run_id,
            config_hash,
        ) = row
        signal = _json_loads(str(signal_json))
        feature_row = connection.execute(
            "SELECT features_json FROM feature_store WHERE feature_snapshot_id = ?",
            (feature_snapshot_id,),
        ).fetchone()
        run_row = connection.execute(
            "SELECT metadata_json FROM run_journal WHERE run_id = ?",
            (run_id,),
        ).fetchone()
        config_row = connection.execute(
            "SELECT config_json FROM strategy_config WHERE config_hash = ?",
            (config_hash,),
        ).fetchone()
        evidence_cards = []
        for evidence_id in _json_loads(str(evidence_ids_json)):
            evidence_row = connection.execute(
                "SELECT payload_json FROM evidence_card WHERE evidence_id = ?",
                (str(evidence_id),),
            ).fetchone()
            if evidence_row:
                evidence_cards.append(_json_loads(evidence_row[0]))
        artifact_refs = []
        for artifact_ref_id in _json_loads(str(artifact_ids_json)):
            artifact_row = connection.execute(
                """
                SELECT artifact_ref_id, ref_type, ref, metadata_json
                FROM artifact_ref
                WHERE artifact_ref_id = ?
                """,
                (str(artifact_ref_id),),
            ).fetchone()
            if artifact_row:
                artifact_refs.append(
                    {
                        "artifact_ref_id": artifact_row[0],
                        "ref_type": artifact_row[1],
                        "ref": artifact_row[2],
                        "metadata": _json_loads(artifact_row[3]),
                    }
                )
        labels = [
            _json_loads(row[0])
            for row in connection.execute(
                """
                SELECT label_json
                FROM label_store
                WHERE signal_id = ?
                ORDER BY rowid
                """,
                (signal_id,),
            ).fetchall()
        ]
        return {
            "recorded_at": signal.get("created_at"),
            "signal": signal,
            "feature_snapshot": _json_loads(feature_row[0]) if feature_row else {},
            "evidence_cards": evidence_cards,
            "artifact_refs": artifact_refs,
            "run_journal": _json_loads(run_row[0]) if run_row else {},
            "strategy_config": _json_loads(config_row[0]) if config_row else {},
            "config_hash": config_hash,
            "labels": labels,
        }


def get_signal_ledger_repository(
    ledger_path: str | os.PathLike[str] | None = None,
    *,
    database_path: str | os.PathLike[str] | None = None,
) -> SignalLedgerRepository:
    """Return the default replay-safe signal ledger repository."""

    if ledger_path is not None and database_path is not None:
        raise ValueError("ledger_path and database_path cannot both be provided")
    if database_path is not None:
        return SQLiteSignalLedgerRepository(database_path)
    return JsonlSignalLedgerRepository(ledger_path)


def _normalize_ledger_path(value: str | os.PathLike[str], field_name: str) -> str:
    normalized = str(value)
    if not normalized.strip():
        raise ValueError(f"{field_name} must be a nonempty string")
    if any(ord(character) < 32 or ord(character) == 127 for character in normalized):
        raise ValueError(f"{field_name} must not contain control characters")
    return normalized.strip()


def _record_matches_signal_filters(
    record: dict[str, Any],
    *,
    asset: str | None,
    underlying: str | None,
    timeframe: str | None,
) -> bool:
    signal = record.get("signal")
    if not isinstance(signal, dict):
        return False
    if asset is not None and str(signal.get("asset", "")).upper() != asset:
        return False
    if underlying is not None and str(signal.get("underlying", "")).upper() != underlying:
        return False
    return timeframe is None or str(signal.get("timeframe", "")) == timeframe


def _json_dumps(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def _json_loads(value: str) -> Any:
    return json.loads(value)


def _expect_mapping(value: Any, field_name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{field_name} must be an object")
    return value


def _expect_list(value: Any, field_name: str) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        raise ValueError(f"{field_name} must be a list")
    if not all(isinstance(item, dict) for item in value):
        raise ValueError(f"{field_name} must be a list of objects")
    return value


__all__ = [
    "JsonlSignalLedgerRepository",
    "SQLiteSignalLedgerRepository",
    "SignalLedgerRepository",
    "get_signal_ledger_repository",
]
