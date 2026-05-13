"""Repository contract and JSONL adapter for signal ledger records."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Protocol

from halo_swing_mcp.config import get_settings


class SignalLedgerRepository(Protocol):
    """Minimal repository boundary for signal replay and labeling."""

    @property
    def ledger_ref(self) -> str:
        """Portable reference to the backing ledger."""

    def list_records(self) -> list[dict[str, Any]]:
        """Return all ledger records in insertion order."""

    def find_by_signal_id(self, signal_id: str) -> dict[str, Any] | None:
        """Return one signal record if present."""

    def latest_record(self) -> dict[str, Any] | None:
        """Return the newest ledger record if present."""

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


def get_signal_ledger_repository(
    ledger_path: str | os.PathLike[str] | None = None,
) -> SignalLedgerRepository:
    """Return the default replay-safe signal ledger repository."""

    return JsonlSignalLedgerRepository(ledger_path)


def _normalize_ledger_path(value: str | os.PathLike[str], field_name: str) -> str:
    normalized = str(value)
    if not normalized.strip():
        raise ValueError(f"{field_name} must be a nonempty string")
    if any(ord(character) < 32 or ord(character) == 127 for character in normalized):
        raise ValueError(f"{field_name} must not contain control characters")
    return normalized.strip()


__all__ = [
    "JsonlSignalLedgerRepository",
    "SignalLedgerRepository",
    "get_signal_ledger_repository",
]
