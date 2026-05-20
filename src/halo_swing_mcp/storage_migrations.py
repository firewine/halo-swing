"""SQLite migration runner for replay schema setup."""

from __future__ import annotations

import hashlib
import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Iterable

from halo_swing_mcp.contracts import StorageHealth


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MIGRATIONS_DIR = REPO_ROOT / "migrations"
DOMAIN_TABLES = (
    "strategy_config",
    "run_journal",
    "feature_store",
    "evidence_card",
    "artifact_ref",
    "signal_ledger",
    "label_store",
)
SCHEMA_MIGRATIONS_TABLE = "schema_migrations"


@dataclass(frozen=True)
class MigrationResult:
    database_path: str
    applied_versions: tuple[str, ...]
    skipped_versions: tuple[str, ...]
    latest_migration: str | None
    migration_count: int
    domain_tables_present: tuple[str, ...]


def apply_migrations(
    database_path: str | Path,
    *,
    migrations_dir: str | Path = DEFAULT_MIGRATIONS_DIR,
) -> MigrationResult:
    """Apply pending SQLite migrations and return deterministic state."""

    normalized_database_path = _normalize_database_path(database_path)
    normalized_database_path.parent.mkdir(parents=True, exist_ok=True)
    migration_files = _list_migration_files(migrations_dir)

    applied_versions: list[str] = []
    skipped_versions: list[str] = []
    with sqlite3.connect(normalized_database_path) as connection:
        connection.execute("PRAGMA foreign_keys = ON")
        _ensure_schema_migrations_table(connection)
        for migration_file in migration_files:
            version = migration_file.stem
            sql = migration_file.read_text(encoding="utf-8")
            checksum = _sha256_text(sql)
            existing_checksum = _existing_checksum(connection, version)
            if existing_checksum is not None:
                if existing_checksum != checksum:
                    raise ValueError(
                        f"migration {version} checksum mismatch; "
                        "refusing to continue"
                    )
                skipped_versions.append(version)
                continue
            _apply_one_migration(connection, version, checksum, sql)
            applied_versions.append(version)

    health = get_storage_health(normalized_database_path)
    return MigrationResult(
        database_path=str(normalized_database_path),
        applied_versions=tuple(applied_versions),
        skipped_versions=tuple(skipped_versions),
        latest_migration=health["latest_migration"],
        migration_count=health["migration_count"],
        domain_tables_present=tuple(health["domain_tables_present"]),
    )


def get_storage_health(database_path: str | Path) -> dict[str, object]:
    """Return the storage health DTO for a SQLite database path."""

    normalized_database_path = _normalize_database_path(database_path)
    if not normalized_database_path.exists():
        return StorageHealth(
            status="ok",
            driver="sqlite",
            database_kind="sqlite",
            migration_count=0,
            latest_migration=None,
            domain_tables_present=[],
            live_data_required=False,
        ).model_dump(mode="json")

    with sqlite3.connect(normalized_database_path) as connection:
        connection.execute("PRAGMA foreign_keys = ON")
        table_names = _table_names(connection)
        if SCHEMA_MIGRATIONS_TABLE in table_names:
            migration_count = connection.execute(
                "SELECT COUNT(*) FROM schema_migrations"
            ).fetchone()[0]
            latest_row = connection.execute(
                "SELECT version FROM schema_migrations ORDER BY version DESC LIMIT 1"
            ).fetchone()
            latest_migration = latest_row[0] if latest_row else None
        else:
            migration_count = 0
            latest_migration = None

    return StorageHealth(
        status="ok",
        driver="sqlite",
        database_kind="sqlite",
        migration_count=migration_count,
        latest_migration=latest_migration,
        domain_tables_present=[
            table_name for table_name in DOMAIN_TABLES if table_name in table_names
        ],
        live_data_required=False,
    ).model_dump(mode="json")


def _apply_one_migration(
    connection: sqlite3.Connection,
    version: str,
    checksum: str,
    sql: str,
) -> None:
    timestamp = datetime.now(UTC).replace(microsecond=0).isoformat()
    try:
        connection.execute("BEGIN")
        for statement in _iter_sql_statements(sql):
            connection.execute(statement)
        connection.execute(
            """
            INSERT INTO schema_migrations (version, checksum, applied_at)
            VALUES (?, ?, ?)
            """,
            (version, checksum, timestamp),
        )
    except Exception:
        connection.rollback()
        raise
    else:
        connection.commit()


def _ensure_schema_migrations_table(connection: sqlite3.Connection) -> None:
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version TEXT PRIMARY KEY,
            checksum TEXT NOT NULL,
            applied_at TEXT NOT NULL
        )
        """
    )


def _existing_checksum(connection: sqlite3.Connection, version: str) -> str | None:
    row = connection.execute(
        "SELECT checksum FROM schema_migrations WHERE version = ?",
        (version,),
    ).fetchone()
    return row[0] if row else None


def _list_migration_files(migrations_dir: str | Path) -> tuple[Path, ...]:
    normalized_migrations_dir = _normalize_migrations_dir(migrations_dir)
    migration_files = tuple(sorted(normalized_migrations_dir.glob("*.sql")))
    if not migration_files:
        raise ValueError("migrations_dir must contain at least one .sql migration")
    return migration_files


def _table_names(connection: sqlite3.Connection) -> set[str]:
    return {
        row[0]
        for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table'"
        ).fetchall()
    }


def _iter_sql_statements(sql: str) -> Iterable[str]:
    statement_parts: list[str] = []
    for line in sql.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        statement_parts.append(line)
        if stripped.endswith(";"):
            statement = "\n".join(statement_parts).strip()
            if statement:
                yield statement
            statement_parts = []
    trailing_statement = "\n".join(statement_parts).strip()
    if trailing_statement:
        yield trailing_statement


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _normalize_database_path(value: str | Path) -> Path:
    normalized = str(value)
    if not normalized.strip():
        raise ValueError("database_path must be a nonempty string")
    if _has_control_characters(normalized):
        raise ValueError("database_path must not contain control characters")
    return Path(normalized).expanduser()


def _normalize_migrations_dir(value: str | Path) -> Path:
    normalized = str(value)
    if not normalized.strip():
        raise ValueError("migrations_dir must be a nonempty string")
    if _has_control_characters(normalized):
        raise ValueError("migrations_dir must not contain control characters")
    path = Path(normalized)
    if not path.is_dir():
        raise ValueError("migrations_dir must be an existing directory")
    return path


def _has_control_characters(value: str) -> bool:
    return any(ord(character) < 32 or ord(character) == 127 for character in value)


__all__ = [
    "DOMAIN_TABLES",
    "MigrationResult",
    "apply_migrations",
    "get_storage_health",
]
