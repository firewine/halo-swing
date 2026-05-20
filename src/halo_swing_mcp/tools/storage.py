"""Storage tool surface for explicit SQLite repository checks."""

from __future__ import annotations

from halo_swing_mcp.storage_migrations import (
    apply_migrations,
    get_storage_health as _get_storage_health,
)


def apply_storage_migrations(database_path: str) -> dict[str, object]:
    """Apply SQLite storage migrations for an explicit database path."""

    normalized_database_path = _normalize_database_path(database_path)
    result = apply_migrations(normalized_database_path)
    return {
        "status": "ok",
        "database_path": result.database_path,
        "applied_versions": list(result.applied_versions),
        "skipped_versions": list(result.skipped_versions),
        "latest_migration": result.latest_migration,
        "migration_count": result.migration_count,
        "domain_tables_present": list(result.domain_tables_present),
        "live_data_required": False,
        "secret_values_returned": False,
    }


def get_storage_health(database_path: str) -> dict[str, object]:
    """Return SQLite storage health for an explicit database path."""

    normalized_database_path = _normalize_database_path(database_path)
    return _get_storage_health(normalized_database_path)


def _normalize_database_path(value: str) -> str:
    if not isinstance(value, str):
        raise ValueError("database_path must be a nonempty string")
    if not _has_no_control_characters(value):
        raise ValueError("database_path must not contain control characters")
    normalized = value.strip()
    if not normalized:
        raise ValueError("database_path must be a nonempty string")
    return normalized


def _has_no_control_characters(value: str) -> bool:
    return all(ord(character) >= 32 and ord(character) != 127 for character in value)
