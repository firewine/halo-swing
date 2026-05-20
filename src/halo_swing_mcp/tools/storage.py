"""Storage health tool surface for explicit SQLite repository checks."""

from __future__ import annotations

from halo_swing_mcp.storage_migrations import get_storage_health as _get_storage_health


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
