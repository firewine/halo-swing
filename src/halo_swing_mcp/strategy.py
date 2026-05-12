"""Strategy configuration and hashing helpers."""

from __future__ import annotations

import copy
import hashlib
import json
from typing import Any


DEFAULT_STRATEGY_CONFIG: dict[str, Any] = {
    "config_id": "leverage_swing_default",
    "version": "0.1.0",
    "status": "champion",
    "target_universe": ["TQQQ", "QLD", "UPRO", "SSO", "SOXL", "BTC"],
    "weights": {
        "trend": 0.25,
        "momentum": 0.20,
        "volatility": 0.20,
        "macro": 0.15,
        "event_safety": 0.10,
        "theme": 0.10,
    },
    "thresholds": {
        "buy_3x": 0.68,
        "buy_2x": 0.52,
        "buy_watch": 0.35,
        "block": 0.20,
    },
    "risk": {
        "max_3x_event_risk": 0.35,
        "time_barrier_days": 10,
        "stop_atr_multiple": 1.6,
        "take_profit_atr_multiple": 2.4,
    },
}

STRATEGY_CONFIG_SCHEMA_VERSION = "strategy_config.v1"


def canonical_json(payload: dict[str, Any]) -> str:
    """Return stable JSON for hashing and fixture comparisons."""

    return json.dumps(payload, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def config_hash(config: dict[str, Any]) -> str:
    """Hash a strategy config without its derived config_hash field."""

    hashable = copy.deepcopy(config)
    hashable.pop("config_hash", None)
    digest = hashlib.sha256(canonical_json(hashable).encode("utf-8")).hexdigest()
    return f"sha256:{digest}"


def get_strategy_config() -> dict[str, Any]:
    """Return the active deterministic champion config."""

    config = copy.deepcopy(DEFAULT_STRATEGY_CONFIG)
    config["config_hash"] = config_hash(config)
    return config


def validate_strategy_config(config: dict[str, Any]) -> dict[str, Any]:
    """Validate basic bounds without adding a schema dependency."""

    weights = config.get("weights", {})
    thresholds = config.get("thresholds", {})
    risk = config.get("risk", {})
    errors: list[str] = []

    for field in ("config_id", "version", "status", "target_universe", "weights", "thresholds", "risk"):
        if field not in config:
            errors.append(f"{field} is required")

    if not weights:
        errors.append("weights are required")
    else:
        total_weight = sum(float(value) for value in weights.values())
        if abs(total_weight - 1.0) > 0.000001:
            errors.append("weights must sum to 1.0")
        for name, value in weights.items():
            if not 0 <= float(value) <= 1:
                errors.append(f"weight {name} is out of bounds")

    ordered_thresholds = [
        thresholds.get("buy_3x"),
        thresholds.get("buy_2x"),
        thresholds.get("buy_watch"),
        thresholds.get("block"),
    ]
    if any(value is None for value in ordered_thresholds):
        errors.append("all thresholds are required")
    elif not (
        thresholds["buy_3x"]
        > thresholds["buy_2x"]
        > thresholds["buy_watch"]
        > thresholds["block"]
    ):
        errors.append("thresholds must be strictly descending")

    for field in (
        "max_3x_event_risk",
        "time_barrier_days",
        "stop_atr_multiple",
        "take_profit_atr_multiple",
    ):
        if field not in risk:
            errors.append(f"risk.{field} is required")

    if "max_3x_event_risk" in risk and not 0 <= float(risk["max_3x_event_risk"]) <= 1:
        errors.append("risk.max_3x_event_risk is out of bounds")
    if "time_barrier_days" in risk and int(risk["time_barrier_days"]) <= 0:
        errors.append("risk.time_barrier_days must be positive")
    if "stop_atr_multiple" in risk and float(risk["stop_atr_multiple"]) <= 0:
        errors.append("risk.stop_atr_multiple must be positive")
    if "take_profit_atr_multiple" in risk and float(risk["take_profit_atr_multiple"]) <= 0:
        errors.append("risk.take_profit_atr_multiple must be positive")

    expected_hash = config_hash(config)
    provided_hash = config.get("config_hash")
    return {
        "schema_version": STRATEGY_CONFIG_SCHEMA_VERSION,
        "valid": not errors,
        "errors": errors,
        "config_hash": expected_hash,
        "provided_config_hash": provided_hash,
        "config_hash_matches": provided_hash in {None, expected_hash},
        "weight_sum": round(sum(float(value) for value in weights.values()), 8)
        if weights
        else 0.0,
        "required_sections": [
            "config_id",
            "version",
            "status",
            "target_universe",
            "weights",
            "thresholds",
            "risk",
        ],
        "bounds_checked": True,
        "sum_checked": True,
        "threshold_order_checked": True,
        "hash_algorithm": "sha256:canonical_json_without_config_hash",
        "db_required": False,
    }
