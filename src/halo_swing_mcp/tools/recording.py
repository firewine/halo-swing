"""Signal recording, triple-barrier labeling, and ledger-backed evaluation."""

from __future__ import annotations

import math
from typing import Any

from halo_swing_mcp.contracts import (
    LabelOutcome,
    ReplayErrorCode,
    ReplayMissingLinkError,
    SignalReplayBundle,
)
from halo_swing_mcp.fixtures import AS_OF, future_price_path
from halo_swing_mcp.signal_repository import get_signal_ledger_repository
from halo_swing_mcp.tools.market import calculate_indicators, get_news_bundle
from halo_swing_mcp.tools.scoring import evaluate_score_performance, score_leverage_swing


RUN_JOURNAL_SCHEMA_VERSION = "run_journal.v1"
LABEL_OUTCOME_SCHEMA_VERSION = "signal_label_outcome.v1"
LABEL_METRIC_FIELDS = ["mfe", "mae", "realized_r"]
LABEL_BARRIER_FIELDS = [
    "first_barrier_hit",
    "hit_index",
    "entry_price",
    "upper_barrier",
    "lower_barrier",
    "time_barrier_days",
]


def record_signal(
    signal: dict[str, Any] | None = None,
    ledger_path: str | None = None,
    database_path: str | None = None,
) -> dict[str, Any]:
    """Record a signal in a local JSONL ledger with idempotent signal_id handling."""

    normalized_ledger_path = _normalize_optional_path(ledger_path, "ledger_path")
    normalized_database_path = _normalize_optional_path(database_path, "database_path")
    if normalized_ledger_path is not None and normalized_database_path is not None:
        raise ValueError("ledger_path and database_path cannot both be provided")
    payload = _normalize_signal_payload(signal)
    signal_id = str(payload["signal_id"])
    repository = get_signal_ledger_repository(
        normalized_ledger_path,
        database_path=normalized_database_path,
    )
    feature_snapshot = calculate_indicators(str(payload["underlying"]))
    news_bundle = get_news_bundle(topic="all")
    live_data_required = _live_data_required(
        payload,
        feature_snapshot,
        news_bundle,
    )
    network_call = _network_call_required(payload, feature_snapshot, news_bundle)
    run_journal = _run_journal(
        payload,
        live_data_required=live_data_required,
        network_call=network_call,
        db_required=repository.db_required,
    )

    record = {
        "recorded_at": AS_OF,
        "signal": payload,
        "feature_snapshot": feature_snapshot,
        "evidence_cards": news_bundle["evidence_cards"],
        "run_journal": run_journal,
        "strategy_config": _record_strategy_config(payload),
        "config_hash": payload.get("config_hash"),
        "labels": [],
    }
    status, stored_record = repository.append_if_absent(
        signal_id=signal_id,
        record=record,
    )

    return {
        "status": status,
        "signal_id": signal_id,
        "ledger_ref": repository.ledger_ref,
        "run_journal_contract": _run_journal_contract(
            stored_record,
            repository=repository,
        ),
        "record": stored_record,
        "live_data_required": _stored_record_live_data_required(stored_record),
    }


def label_signal_outcome(
    signal_id: str | None = None,
    price_path: list[float] | None = None,
    stop_loss_pct: float = 0.05,
    take_profit_pct: float = 0.10,
    time_barrier_days: int = 10,
    ledger_path: str | None = None,
    database_path: str | None = None,
    invalidated_by_event: bool = False,
    invalidating_event_id: str | None = None,
) -> dict[str, Any]:
    """Label a signal with triple-barrier outcome, MFE, MAE, and realized R."""

    normalized_signal_id = _normalize_signal_id(signal_id)
    normalized_price_path = _normalize_price_path(price_path)
    normalized_stop_loss_pct = _normalize_positive_finite_number(
        stop_loss_pct,
        "stop_loss_pct",
    )
    normalized_take_profit_pct = _normalize_positive_finite_number(
        take_profit_pct,
        "take_profit_pct",
    )
    normalized_time_barrier_days = _normalize_positive_integer(
        time_barrier_days,
        "time_barrier_days",
    )
    normalized_invalidated_by_event = _normalize_boolean(
        invalidated_by_event,
        "invalidated_by_event",
    )
    normalized_invalidating_event_id = _normalize_optional_string_identity(
        invalidating_event_id,
        "invalidating_event_id",
    )
    normalized_ledger_path = _normalize_optional_path(ledger_path, "ledger_path")
    normalized_database_path = _normalize_optional_path(database_path, "database_path")
    if normalized_ledger_path is not None and normalized_database_path is not None:
        raise ValueError("ledger_path and database_path cannot both be provided")

    repository = get_signal_ledger_repository(
        normalized_ledger_path,
        database_path=normalized_database_path,
    )
    records = repository.list_records()
    record = _select_record(records, normalized_signal_id)
    signal = record["signal"] if record else score_leverage_swing()
    selected_signal_id = normalized_signal_id or str(signal["signal_id"])
    entry_reference = float(signal.get("entry", {}).get("reference_price") or 0.0)

    if normalized_invalidated_by_event:
        label = _non_price_barrier_label(
            signal_id=selected_signal_id,
            outcome=LabelOutcome.INVALIDATED_BY_EVENT.value,
            entry_price=entry_reference,
            stop_loss_pct=normalized_stop_loss_pct,
            take_profit_pct=normalized_take_profit_pct,
            time_barrier_days=normalized_time_barrier_days,
            first_barrier_hit="event_invalidation",
            label_reason="invalidated_by_event",
            invalidating_event_id=normalized_invalidating_event_id,
            db_required=repository.db_required,
        )
        _append_label_if_recorded(repository, record, selected_signal_id, label)
        return label

    if normalized_price_path is not None and not normalized_price_path:
        label = _non_price_barrier_label(
            signal_id=selected_signal_id,
            outcome=LabelOutcome.NO_DATA.value,
            entry_price=entry_reference,
            stop_loss_pct=normalized_stop_loss_pct,
            take_profit_pct=normalized_take_profit_pct,
            time_barrier_days=normalized_time_barrier_days,
            first_barrier_hit=None,
            label_reason="empty_price_path",
            invalidating_event_id=None,
            db_required=repository.db_required,
        )
        _append_label_if_recorded(repository, record, selected_signal_id, label)
        return label

    prices = (
        normalized_price_path
        if normalized_price_path is not None
        else future_price_path(str(signal["underlying"]), normalized_time_barrier_days)
    )
    if not prices:
        label = _non_price_barrier_label(
            signal_id=selected_signal_id,
            outcome=LabelOutcome.NO_DATA.value,
            entry_price=entry_reference,
            stop_loss_pct=normalized_stop_loss_pct,
            take_profit_pct=normalized_take_profit_pct,
            time_barrier_days=normalized_time_barrier_days,
            first_barrier_hit=None,
            label_reason="missing_future_price_path",
            invalidating_event_id=None,
            db_required=repository.db_required,
        )
        _append_label_if_recorded(repository, record, selected_signal_id, label)
        return label

    evaluation_prices = prices[:normalized_time_barrier_days]
    entry_price = float(signal.get("entry", {}).get("reference_price") or prices[0])
    upper_barrier = entry_price * (1 + normalized_take_profit_pct)
    lower_barrier = entry_price * (1 - normalized_stop_loss_pct)
    outcome = LabelOutcome.TIME_EXIT.value
    first_barrier_hit = None
    hit_index = len(evaluation_prices) - 1

    for index, price in enumerate(evaluation_prices):
        if price >= upper_barrier:
            outcome = LabelOutcome.TAKE_PROFIT_FIRST.value
            first_barrier_hit = "take_profit"
            hit_index = index
            break
        if price <= lower_barrier:
            outcome = LabelOutcome.STOP_LOSS_FIRST.value
            first_barrier_hit = "stop_loss"
            hit_index = index
            break

    mfe = max((price - entry_price) / entry_price for price in evaluation_prices)
    mae = min((price - entry_price) / entry_price for price in evaluation_prices)
    if outcome == LabelOutcome.TAKE_PROFIT_FIRST.value:
        realized_r = normalized_take_profit_pct / normalized_stop_loss_pct
    elif outcome == LabelOutcome.STOP_LOSS_FIRST.value:
        realized_r = -1.0
    else:
        realized_r = (
            evaluation_prices[hit_index] - entry_price
        ) / (entry_price * normalized_stop_loss_pct)

    label = {
        "signal_id": selected_signal_id,
        "labeled_at": AS_OF,
        "outcome": outcome,
        "first_barrier_hit": first_barrier_hit,
        "hit_index": hit_index,
        "entry_price": round(entry_price, 4),
        "upper_barrier": round(upper_barrier, 4),
        "lower_barrier": round(lower_barrier, 4),
        "time_barrier_days": normalized_time_barrier_days,
        "mfe": round(mfe, 6),
        "mae": round(mae, 6),
        "realized_r": round(realized_r, 4),
        "label_contract": _label_contract(
            "triple_barrier",
            db_required=repository.db_required,
        ),
        "live_data_required": False,
    }

    _append_label_if_recorded(repository, record, selected_signal_id, label)

    return label


def evaluate_recorded_score_performance(
    ledger_path: str | None = None,
    database_path: str | None = None,
    days: int = 90,
    signals: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Evaluate recorded ledger signals, falling back to fixture samples."""

    normalized_days = _normalize_positive_integer(days, "days")
    normalized_ledger_path = _normalize_optional_path(ledger_path, "ledger_path")
    normalized_database_path = _normalize_optional_path(database_path, "database_path")
    if normalized_ledger_path is not None and normalized_database_path is not None:
        raise ValueError("ledger_path and database_path cannot both be provided")
    if signals is not None:
        return evaluate_score_performance(signals=signals, days=normalized_days)

    repository = get_signal_ledger_repository(
        normalized_ledger_path,
        database_path=normalized_database_path,
    )
    records = repository.list_records()
    if not records:
        return evaluate_score_performance(days=normalized_days)

    outcomes: list[dict[str, Any]] = []
    for record in records:
        signal = record["signal"]
        labels = record.get("labels") or []
        if labels:
            label = labels[-1]
        else:
            label = label_signal_outcome(
                signal_id=signal["signal_id"],
                database_path=normalized_database_path,
                ledger_path=normalized_ledger_path,
            )
        outcomes.append(
            {
                "signal_id": signal["signal_id"],
                "final_score": signal["final_score"],
                "outcome": label["outcome"],
                "realized_r": label["realized_r"],
                "component_scores": signal.get("component_scores"),
            }
        )

    performance = evaluate_score_performance(outcomes, days=normalized_days)
    performance["ledger_ref"] = repository.ledger_ref
    return performance


def get_signal_replay_bundle(
    signal_id: str,
    ledger_path: str | None = None,
    database_path: str | None = None,
) -> dict[str, Any]:
    """Return the replay bundle for one recorded signal."""

    normalized_signal_id = _normalize_optional_string_identity(signal_id, "signal_id")
    normalized_ledger_path = _normalize_optional_path(ledger_path, "ledger_path")
    normalized_database_path = _normalize_optional_path(database_path, "database_path")
    if normalized_ledger_path is not None and normalized_database_path is not None:
        raise ValueError("ledger_path and database_path cannot both be provided")

    repository = get_signal_ledger_repository(
        normalized_ledger_path,
        database_path=normalized_database_path,
    )
    record = repository.find_by_signal_id(str(normalized_signal_id))
    if record is None:
        return SignalReplayBundle(
            signal={},
            feature_snapshot={},
            evidence_cards=[],
            artifact_refs=[],
            strategy_config={},
            run_journal={},
            label_outcome=None,
            missing_links=[
                ReplayMissingLinkError(
                    code=ReplayErrorCode.MISSING_REQUIRED_LINK,
                    message="signal_id was not found in the selected repository",
                    missing_ref_type="signal_ledger",
                    missing_ref_id=str(normalized_signal_id),
                )
            ],
        ).model_dump(mode="json")

    missing_links = _replay_missing_links(record)
    labels = record.get("labels") if isinstance(record.get("labels"), list) else []
    label_outcome = labels[-1] if labels else None
    evidence_cards = _expect_list(record.get("evidence_cards"), "record.evidence_cards")
    return SignalReplayBundle(
        signal=_expect_mapping(record.get("signal"), "record.signal"),
        feature_snapshot=_expect_mapping(
            record.get("feature_snapshot"),
            "record.feature_snapshot",
        ),
        evidence_cards=evidence_cards,
        artifact_refs=_record_artifact_refs(record, evidence_cards),
        strategy_config=_expect_mapping(
            record.get("strategy_config"),
            "record.strategy_config",
        ),
        run_journal=_expect_mapping(record.get("run_journal"), "record.run_journal"),
        label_outcome=label_outcome,
        missing_links=missing_links,
    ).model_dump(mode="json")


def get_latest_signal_record(
    ledger_path: str | None = None,
    database_path: str | None = None,
    asset: str | None = None,
    underlying: str | None = None,
) -> dict[str, Any]:
    """Return the latest recorded signal, optionally constrained by asset keys."""

    normalized_ledger_path = _normalize_optional_path(ledger_path, "ledger_path")
    normalized_database_path = _normalize_optional_path(database_path, "database_path")
    if normalized_ledger_path is not None and normalized_database_path is not None:
        raise ValueError("ledger_path and database_path cannot both be provided")
    normalized_asset = _normalize_optional_asset_filter(asset, "asset")
    normalized_underlying = _normalize_optional_asset_filter(underlying, "underlying")

    repository = get_signal_ledger_repository(
        normalized_ledger_path,
        database_path=normalized_database_path,
    )
    record = _select_latest_matching_record(
        repository.list_records(),
        asset=normalized_asset,
        underlying=normalized_underlying,
    )
    filters = {
        "asset": normalized_asset,
        "underlying": normalized_underlying,
    }

    if record is None:
        return {
            "status": "not_found",
            "signal_id": None,
            "ledger_ref": repository.ledger_ref,
            "storage": repository.storage_name,
            "db_required": repository.db_required,
            "filters": filters,
            "record": {},
            "label_outcome": None,
            "missing_links": [
                ReplayMissingLinkError(
                    code=ReplayErrorCode.MISSING_REQUIRED_LINK,
                    message=(
                        "no signal record matched the selected repository and filters"
                    ),
                    missing_ref_type="signal_ledger",
                    missing_ref_id=_latest_signal_missing_ref_id(
                        asset=normalized_asset,
                        underlying=normalized_underlying,
                    ),
                ).model_dump(mode="json")
            ],
            "live_data_required": False,
        }

    signal = _expect_mapping(record.get("signal"), "record.signal")
    labels = record.get("labels") if isinstance(record.get("labels"), list) else []
    return {
        "status": "found",
        "signal_id": signal.get("signal_id"),
        "ledger_ref": repository.ledger_ref,
        "storage": repository.storage_name,
        "db_required": repository.db_required,
        "filters": filters,
        "record": record,
        "label_outcome": labels[-1] if labels else None,
        "missing_links": [],
        "live_data_required": _stored_record_live_data_required(record),
    }


def _normalize_signal_payload(signal: dict[str, Any] | None) -> dict[str, Any]:
    if signal is None:
        return score_leverage_swing()
    if not isinstance(signal, dict):
        raise ValueError("signal must be an object")

    payload = dict(signal)
    for field_name in (
        "signal_id",
        "run_id",
        "created_at",
        "underlying",
        "config_version",
        "config_hash",
    ):
        payload[field_name] = _normalize_required_signal_field(payload, field_name)
    payload["underlying"] = str(payload["underlying"]).upper()
    return payload


def _record_strategy_config(signal: dict[str, Any]) -> dict[str, Any]:
    fallback = {
        "schema_version": "strategy_config.v1",
        "config_hash": signal.get("config_hash"),
        "config_version": signal.get("config_version"),
    }
    source_config = signal.get("strategy_config")
    if not isinstance(source_config, dict):
        return fallback

    config = dict(source_config)
    config["schema_version"] = "strategy_config.v1"
    config["config_hash"] = signal.get("config_hash")
    config.setdefault("config_version", signal.get("config_version"))
    if signal.get("config_version") is not None:
        config.setdefault("version", signal.get("config_version"))
    return config


def _normalize_required_signal_field(
    signal: dict[str, Any],
    field_name: str,
) -> str:
    if field_name not in signal:
        raise ValueError(f"signal.{field_name} must be a nonempty string")
    if signal[field_name] is None:
        raise ValueError(f"signal.{field_name} must be a nonempty string")
    return _normalize_optional_string_identity(
        signal[field_name],
        f"signal.{field_name}",
    )


def _normalize_signal_id(signal_id: str | None) -> str | None:
    if signal_id is None:
        return None
    return _normalize_optional_string_identity(signal_id, "signal_id")


def _normalize_optional_string_identity(value: str | None, field_name: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be a nonempty string")
    if not _has_no_control_characters(value):
        raise ValueError(f"{field_name} must not contain control characters")
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{field_name} must be a nonempty string")
    return normalized


def _normalize_optional_asset_filter(value: str | None, field_name: str) -> str | None:
    normalized = _normalize_optional_string_identity(value, field_name)
    return normalized.upper() if normalized is not None else None


def _normalize_optional_path(value: str | None, field_name: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be a nonempty string")
    if not _has_no_control_characters(value):
        raise ValueError(f"{field_name} must not contain control characters")
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{field_name} must be a nonempty string")
    return normalized


def _has_no_control_characters(value: str) -> bool:
    return all(ord(character) >= 32 and ord(character) != 127 for character in value)


def _normalize_price_path(price_path: list[float] | None) -> list[float] | None:
    if price_path is None:
        return None
    if not isinstance(price_path, list):
        raise ValueError("price_path must be a list of positive finite numbers")
    normalized_prices: list[float] = []
    for price in price_path:
        normalized_prices.append(
            _normalize_positive_finite_number(
                price,
                "price_path",
                message="price_path must be a list of positive finite numbers",
            )
        )
    return normalized_prices


def _normalize_positive_finite_number(
    value: float,
    field_name: str,
    *,
    message: str | None = None,
) -> float:
    error_message = message or f"{field_name} must be a positive finite number"
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise ValueError(error_message)
    normalized = float(value)
    if not math.isfinite(normalized) or normalized <= 0.0:
        raise ValueError(error_message)
    return normalized


def _normalize_positive_integer(value: int, field_name: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        raise ValueError(f"{field_name} must be a positive integer")
    if value <= 0:
        raise ValueError(f"{field_name} must be a positive integer")
    return value


def _normalize_boolean(value: bool, field_name: str) -> bool:
    if not isinstance(value, bool):
        raise ValueError(f"{field_name} must be a boolean")
    return value


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


def _select_latest_matching_record(
    records: list[dict[str, Any]],
    *,
    asset: str | None,
    underlying: str | None,
) -> dict[str, Any] | None:
    for record in reversed(records):
        signal = record.get("signal")
        if not isinstance(signal, dict):
            continue
        if asset is not None and str(signal.get("asset", "")).upper() != asset:
            continue
        if (
            underlying is not None
            and str(signal.get("underlying", "")).upper() != underlying
        ):
            continue
        return record
    return None


def _latest_signal_missing_ref_id(
    *,
    asset: str | None,
    underlying: str | None,
) -> str:
    filters = []
    if asset is not None:
        filters.append(f"asset={asset}")
    if underlying is not None:
        filters.append(f"underlying={underlying}")
    return "latest" if not filters else f"latest:{','.join(filters)}"


def _run_journal(
    signal: dict[str, Any],
    *,
    live_data_required: bool | None = None,
    network_call: bool | None = None,
    db_required: bool = False,
) -> dict[str, Any]:
    run_id = str(signal.get("run_id"))
    signal_id = str(signal.get("signal_id"))
    return {
        "schema_version": RUN_JOURNAL_SCHEMA_VERSION,
        "run_id": run_id,
        "signal_id": signal_id,
        "started_at": signal.get("created_at"),
        "finished_at": AS_OF,
        "status": "completed",
        "trigger": "mcp_tool_record_signal",
        "config_version": signal.get("config_version"),
        "config_hash": signal.get("config_hash"),
        "idempotency_key": f"{run_id}:{signal_id}:record_signal",
        "network_call": _payload_network_call(signal)
        if network_call is None
        else network_call,
        "db_required": db_required,
        "secret_values_returned": False,
        "live_data_required": bool(signal.get("live_data_required"))
        if live_data_required is None
        else live_data_required,
    }


def _live_data_required(*payloads: dict[str, Any]) -> bool:
    return any(bool(payload.get("live_data_required")) for payload in payloads)


def _network_call_required(*payloads: dict[str, Any]) -> bool:
    return any(_payload_network_call(payload) for payload in payloads)


def _payload_network_call(payload: dict[str, Any]) -> bool:
    for contract_key in (
        "source_data_contract",
        "timeframe_contract",
        "swing_level_contract",
        "news_source_policy_contract",
        "news_score_contract",
    ):
        contract = payload.get(contract_key)
        if isinstance(contract, dict) and contract.get("network_call") is True:
            return True
    return bool(payload.get("network_call"))


def _stored_record_live_data_required(record: dict[str, Any]) -> bool:
    run_journal = record.get("run_journal", {})
    if isinstance(run_journal, dict):
        return bool(run_journal.get("live_data_required"))
    return False


def _stored_record_network_call(record: dict[str, Any] | None) -> bool:
    if record is None:
        return False
    run_journal = record.get("run_journal", {})
    if isinstance(run_journal, dict):
        return bool(run_journal.get("network_call"))
    return False


def _run_journal_contract(
    record: dict[str, Any] | None = None,
    *,
    repository: Any | None = None,
) -> dict[str, Any]:
    return {
        "schema_version": RUN_JOURNAL_SCHEMA_VERSION,
        "storage": getattr(repository, "storage_name", "jsonl_signal_ledger_record"),
        "idempotency_key_field": "idempotency_key",
        "network_call": _stored_record_network_call(record),
        "db_required": bool(getattr(repository, "db_required", False)),
        "secret_values_returned": False,
    }


def _non_price_barrier_label(
    *,
    signal_id: str,
    outcome: str,
    entry_price: float,
    stop_loss_pct: float,
    take_profit_pct: float,
    time_barrier_days: int,
    first_barrier_hit: str | None,
    label_reason: str,
    invalidating_event_id: str | None,
    db_required: bool,
) -> dict[str, Any]:
    upper_barrier = entry_price * (1 + take_profit_pct)
    lower_barrier = entry_price * (1 - stop_loss_pct)
    return {
        "signal_id": signal_id,
        "labeled_at": AS_OF,
        "outcome": outcome,
        "first_barrier_hit": first_barrier_hit,
        "hit_index": None,
        "entry_price": round(entry_price, 4),
        "upper_barrier": round(upper_barrier, 4),
        "lower_barrier": round(lower_barrier, 4),
        "time_barrier_days": time_barrier_days,
        "mfe": 0.0,
        "mae": 0.0,
        "realized_r": 0.0,
        "label_reason": label_reason,
        "invalidating_event_id": invalidating_event_id,
        "label_contract": _label_contract(label_reason, db_required=db_required),
        "live_data_required": False,
    }


def _label_contract(label_reason: str, *, db_required: bool = False) -> dict[str, Any]:
    return {
        "schema_version": LABEL_OUTCOME_SCHEMA_VERSION,
        "label_reason": label_reason,
        "metric_fields": LABEL_METRIC_FIELDS,
        "barrier_fields": LABEL_BARRIER_FIELDS,
        "mfe_mae_window": "price_path[:time_barrier_days]",
        "realized_r_unit": "stop_loss_risk",
        "network_call": False,
        "db_required": db_required,
        "secret_values_returned": False,
        "supported_outcomes": [outcome.value for outcome in LabelOutcome],
    }


def _append_label_if_recorded(
    repository: Any,
    record: dict[str, Any] | None,
    signal_id: str,
    label: dict[str, Any],
) -> None:
    if record is not None:
        repository.append_label(signal_id=signal_id, label=label)


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


def _record_artifact_refs(
    record: dict[str, Any],
    evidence_cards: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    artifact_refs = record.get("artifact_refs")
    if artifact_refs is not None:
        return _expect_list(artifact_refs, "record.artifact_refs")

    refs: list[dict[str, Any]] = []
    for card in evidence_cards:
        artifact_ref = card.get("artifact_ref")
        if isinstance(artifact_ref, dict):
            evidence_id = str(card.get("evidence_id", "unknown_evidence"))
            refs.append(
                {
                    "artifact_ref_id": f"{evidence_id}:artifact",
                    "ref_type": artifact_ref.get("ref_type", "OTHER"),
                    "ref": artifact_ref.get("ref", ""),
                    "metadata": artifact_ref.get("metadata", {}),
                }
            )
    return refs


def _replay_missing_links(record: dict[str, Any]) -> list[ReplayMissingLinkError]:
    required_sections = {
        "signal": "signal_ledger",
        "feature_snapshot": "feature_store",
        "evidence_cards": "evidence_card",
        "strategy_config": "strategy_config",
        "run_journal": "run_journal",
    }
    missing_links: list[ReplayMissingLinkError] = []
    for section_name, ref_type in required_sections.items():
        value = record.get(section_name)
        missing = not value if section_name != "evidence_cards" else not isinstance(
            value,
            list,
        )
        if missing:
            missing_links.append(
                ReplayMissingLinkError(
                    code=ReplayErrorCode.MISSING_REQUIRED_LINK,
                    message=f"{section_name} is missing from replay bundle",
                    missing_ref_type=ref_type,
                    missing_ref_id=None,
                )
            )
    return missing_links
