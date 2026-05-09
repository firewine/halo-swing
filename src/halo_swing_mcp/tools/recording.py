"""Signal recording, triple-barrier labeling, and ledger-backed evaluation."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from halo_swing_mcp.fixtures import AS_OF, future_price_path
from halo_swing_mcp.tools.market import calculate_indicators, get_news_bundle
from halo_swing_mcp.tools.scoring import evaluate_score_performance, score_leverage_swing


DEFAULT_LEDGER_PATH = Path("state") / "signal_ledger.jsonl"


def record_signal(
    signal: dict[str, Any] | None = None,
    ledger_path: str | None = None,
) -> dict[str, Any]:
    """Record a signal in a local JSONL ledger with idempotent signal_id handling."""

    payload = signal or score_leverage_swing()
    signal_id = str(payload["signal_id"])
    path = _ledger_path(ledger_path)
    records = _read_records(path)
    duplicate = next(
        (
            record
            for record in records
            if record.get("signal", {}).get("signal_id") == signal_id
        ),
        None,
    )
    if duplicate is not None:
        return {
            "status": "duplicate",
            "signal_id": signal_id,
            "ledger_ref": str(path),
            "record": duplicate,
            "live_data_required": False,
        }

    record = {
        "recorded_at": AS_OF,
        "signal": payload,
        "feature_snapshot": calculate_indicators(str(payload["underlying"])),
        "evidence_cards": get_news_bundle(topic="all")["evidence_cards"],
        "run_journal": {
            "run_id": payload.get("run_id"),
            "started_at": payload.get("created_at"),
            "finished_at": AS_OF,
            "status": "completed",
            "trigger": "mcp_tool_record_signal",
            "config_hash": payload.get("config_hash"),
        },
        "config_hash": payload.get("config_hash"),
        "labels": [],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")

    return {
        "status": "recorded",
        "signal_id": signal_id,
        "ledger_ref": str(path),
        "record": record,
        "live_data_required": False,
    }


def label_signal_outcome(
    signal_id: str | None = None,
    price_path: list[float] | None = None,
    stop_loss_pct: float = 0.05,
    take_profit_pct: float = 0.10,
    time_barrier_days: int = 10,
    ledger_path: str | None = None,
) -> dict[str, Any]:
    """Label a signal with triple-barrier outcome, MFE, MAE, and realized R."""

    path = _ledger_path(ledger_path)
    records = _read_records(path)
    record = _select_record(records, signal_id)
    signal = record["signal"] if record else score_leverage_swing()
    selected_signal_id = signal_id or str(signal["signal_id"])
    prices = price_path or future_price_path(str(signal["underlying"]), time_barrier_days)
    entry_price = float(signal.get("entry", {}).get("reference_price") or prices[0])
    upper_barrier = entry_price * (1 + take_profit_pct)
    lower_barrier = entry_price * (1 - stop_loss_pct)
    outcome = "TIME_EXIT"
    first_barrier_hit = None
    hit_index = len(prices) - 1

    for index, price in enumerate(prices[:time_barrier_days]):
        if price >= upper_barrier:
            outcome = "TAKE_PROFIT_FIRST"
            first_barrier_hit = "take_profit"
            hit_index = index
            break
        if price <= lower_barrier:
            outcome = "STOP_LOSS_FIRST"
            first_barrier_hit = "stop_loss"
            hit_index = index
            break

    mfe = max((price - entry_price) / entry_price for price in prices)
    mae = min((price - entry_price) / entry_price for price in prices)
    if outcome == "TAKE_PROFIT_FIRST":
        realized_r = take_profit_pct / stop_loss_pct
    elif outcome == "STOP_LOSS_FIRST":
        realized_r = -1.0
    else:
        realized_r = (prices[hit_index] - entry_price) / (entry_price * stop_loss_pct)

    label = {
        "signal_id": selected_signal_id,
        "labeled_at": AS_OF,
        "outcome": outcome,
        "first_barrier_hit": first_barrier_hit,
        "hit_index": hit_index,
        "entry_price": round(entry_price, 4),
        "upper_barrier": round(upper_barrier, 4),
        "lower_barrier": round(lower_barrier, 4),
        "time_barrier_days": time_barrier_days,
        "mfe": round(mfe, 6),
        "mae": round(mae, 6),
        "realized_r": round(realized_r, 4),
        "live_data_required": False,
    }

    if record is not None:
        record.setdefault("labels", []).append(label)
        _write_records(path, records)

    return label


def evaluate_recorded_score_performance(
    ledger_path: str | None = None,
) -> dict[str, Any]:
    """Evaluate recorded ledger signals, falling back to fixture samples."""

    path = _ledger_path(ledger_path)
    records = _read_records(path)
    if not records:
        return evaluate_score_performance()

    outcomes: list[dict[str, Any]] = []
    for record in records:
        signal = record["signal"]
        labels = record.get("labels") or []
        if labels:
            label = labels[-1]
        else:
            label = label_signal_outcome(
                signal_id=signal["signal_id"],
                ledger_path=str(path),
            )
        outcomes.append(
            {
                "signal_id": signal["signal_id"],
                "final_score": signal["final_score"],
                "outcome": label["outcome"],
                "realized_r": label["realized_r"],
            }
        )

    performance = evaluate_score_performance(outcomes)
    performance["ledger_ref"] = str(path)
    return performance


def _ledger_path(ledger_path: str | None) -> Path:
    configured = ledger_path or os.environ.get("HALO_SWING_LEDGER_PATH")
    return Path(configured) if configured else DEFAULT_LEDGER_PATH


def _read_records(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    records: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            stripped = line.strip()
            if stripped:
                records.append(json.loads(stripped))
    return records


def _write_records(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")


def _select_record(
    records: list[dict[str, Any]],
    signal_id: str | None,
) -> dict[str, Any] | None:
    if not records:
        return None
    if signal_id is None:
        return records[-1]
    for record in records:
        if record.get("signal", {}).get("signal_id") == signal_id:
            return record
    return None
