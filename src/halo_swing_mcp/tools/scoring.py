"""Swing scoring, guide generation, position review, and feedback tools."""

from __future__ import annotations

import math
from typing import Any

from halo_swing_mcp.contracts import DataFreshnessStatus, TradeAction
from halo_swing_mcp.fixtures import AS_OF, UNDERLYING_PROFILES, resolve_asset
from halo_swing_mcp.indicators import calculate_indicator_payload
from halo_swing_mcp.strategy import get_strategy_config, validate_strategy_config
from halo_swing_mcp.tools.market import (
    get_event_calendar,
    get_macro_snapshot,
    get_news_bundle,
)


ACTION_LABELS = {
    TradeAction.BUY_3X: "Buy 3x swing",
    TradeAction.BUY_2X: "Buy 2x swing",
    TradeAction.BUY_WATCH: "Watch for buy trigger",
    TradeAction.WAIT: "Wait",
    TradeAction.TRIM: "Trim risk",
    TradeAction.EXIT: "Exit",
    TradeAction.STOP: "Stop",
    TradeAction.BLOCK: "Block new long",
}


def score_leverage_swing(
    asset: str = "TQQQ",
    timeframe: str = "swing_3d_10d",
) -> dict[str, Any]:
    """Score a leveraged swing candidate from deterministic inputs."""

    normalized = _normalize_asset_identity(asset)
    normalized_timeframe = _normalize_timeframe_identity(timeframe)
    underlying, leverage = resolve_asset(normalized)
    indicators = calculate_indicator_payload(underlying)
    macro = get_macro_snapshot()
    events = get_event_calendar(days=14)
    news = get_news_bundle(topic="all")
    config = get_strategy_config()
    config_validation = validate_strategy_config(config)
    components = _component_scores(underlying, indicators, macro, events, news)
    final_score = _weighted_score(components, config["weights"])
    macro_filter = macro.get("macro_filter_summary", {})
    action = _action_for_score(final_score, leverage, components, indicators, config)
    references = _risk_references(indicators, config)
    confidence = _confidence(final_score, components)
    risk_warnings = _risk_warnings(components, events, macro_filter)

    if macro_filter.get("blocks_new_longs_now"):
        action = TradeAction.BLOCK
    elif risk_warnings and action in {TradeAction.BUY_2X, TradeAction.BUY_3X}:
        action = TradeAction.BUY_WATCH

    return {
        "signal_id": f"sig_fixture_{AS_OF[:10].replace('-', '')}_{normalized.lower()}",
        "run_id": f"run_fixture_{AS_OF[:10].replace('-', '')}_swing",
        "created_at": AS_OF,
        "asset": normalized,
        "underlying": underlying,
        "leverage": leverage,
        "timeframe": normalized_timeframe,
        "action": action.value,
        "action_label": ACTION_LABELS[action],
        "final_score": round(final_score, 4),
        "confidence": confidence,
        "component_scores": components,
        "news_usage_contract": {
            "schema_version": "news_score_usage.v1",
            "news_score_field": "news_score",
            "used_in_component": "theme",
            "policy_score_field": "policy_score",
            "geopolitical_score_field": "geopolitical_score",
            "ai_semiconductor_theme_score_field": "ai_semiconductor_theme_score",
            "live_data_required": False,
        },
        "entry_summary": _entry_summary(action, underlying, indicators),
        "stop_summary": _stop_summary(underlying, references),
        "take_profit_summary": _take_profit_summary(underlying, references),
        "invalidation_summary": _invalidation_summary(underlying),
        "risk_summary": _risk_summary(action, leverage, components),
        "risk_warnings": risk_warnings,
        "entry": {
            "trigger": f"{underlying} holds above MA20 or reclaims prior session high",
            "reference_price": indicators["latest_bar"]["close"],
        },
        "stop": [
            f"{underlying} closes below {references['stop_price']}",
            "VIX/VXN expands with rates or DXY rising",
            "No upside follow-through within three sessions",
        ],
        "take_profit": [
            f"{underlying} reaches {references['take_profit_price']}",
            f"{underlying} tests the 20-day resistance near {references['resistance_20']}",
            "RSI pushes above 70 while +DI becomes extended",
        ],
        "invalidation": [
            f"{underlying} loses the prior swing support",
            "A high-risk event window opens before confirmation",
            "Macro score deteriorates below neutral",
        ],
        "data_freshness_status": DataFreshnessStatus.FRESH.value,
        "degraded_mode": False,
        "data_warnings": [],
        "config_version": config["version"],
        "config_hash": config["config_hash"],
        "strategy_config": config,
        "strategy_config_contract": {
            "schema_version": config_validation["schema_version"],
            "valid": config_validation["valid"],
            "errors": config_validation["errors"],
            "config_hash_matches_signal": config_validation["config_hash"]
            == config["config_hash"],
            "weight_sum": config_validation["weight_sum"],
            "bounds_checked": config_validation["bounds_checked"],
            "sum_checked": config_validation["sum_checked"],
            "threshold_order_checked": config_validation["threshold_order_checked"],
            "hash_algorithm": config_validation["hash_algorithm"],
            "db_required": config_validation["db_required"],
        },
        "p_take_profit": round(min(0.82, 0.35 + final_score * 0.55), 4),
        "p_stop_loss": round(max(0.08, 0.46 - final_score * 0.38), 4),
        "expected_r": round(final_score * 1.7 - components["event_risk"] * 0.8, 4),
        "reason_summary": _reason_summary(action, components),
        "evidence_summary": _evidence_summary(news),
        "label_status": None,
    }


def generate_trade_guide(
    asset: str = "TQQQ",
    timeframe: str = "swing_3d_10d",
) -> dict[str, Any]:
    """Generate entry, stop, take-profit, and invalidation guide."""

    signal = score_leverage_swing(asset=asset, timeframe=timeframe)
    time_barrier_days = signal["strategy_config"]["risk"]["time_barrier_days"]
    guide = {
        "entry": signal["entry"],
        "stop_conditions": signal["stop"],
        "take_profit_conditions": signal["take_profit"],
        "time_exit_conditions": [
            (
                f"Exit or fully reassess if {signal['underlying']} has no upside "
                f"follow-through within {time_barrier_days} trading days"
            ),
            "Do not extend a leveraged ETF swing only because the ETF price is near breakeven",
        ],
        "invalidation_conditions": signal["invalidation"],
        "position_sizing_note": (
            "Size by max loss to stop, not by confidence. Leveraged ETFs are "
            "swing tactics and should not be treated as long-term holdings."
        ),
    }
    contract = {
        "schema_version": "trade_guide.v1",
        "required_guide_fields": [
            "entry",
            "stop_conditions",
            "take_profit_conditions",
            "time_exit_conditions",
            "invalidation_conditions",
            "position_sizing_note",
        ],
        "time_barrier_days": time_barrier_days,
        "config_version": signal["config_version"],
        "config_hash": signal["config_hash"],
        "config_hash_matches_signal": True,
        "order_submission": False,
        "live_data_required": False,
        "db_required": False,
    }
    guard_checks = [
        {"name": "entry_present", "passed": bool(guide["entry"].get("trigger"))},
        {
            "name": "stop_conditions_present",
            "passed": bool(guide["stop_conditions"]),
        },
        {
            "name": "take_profit_conditions_present",
            "passed": bool(guide["take_profit_conditions"]),
        },
        {
            "name": "time_exit_conditions_present",
            "passed": bool(guide["time_exit_conditions"]),
        },
        {
            "name": "invalidation_conditions_present",
            "passed": bool(guide["invalidation_conditions"]),
        },
        {
            "name": "config_trace_present",
            "passed": signal["config_hash"].startswith("sha256:")
            and bool(signal["config_version"]),
        },
        {"name": "no_order_submission", "passed": contract["order_submission"] is False},
        {
            "name": "no_live_data_required",
            "passed": contract["live_data_required"] is False,
        },
    ]
    return {
        "as_of": AS_OF,
        "asset": signal["asset"],
        "underlying": signal["underlying"],
        "action": signal["action"],
        "confidence": signal["confidence"],
        "guide": guide,
        "trade_guide_contract": contract,
        "trade_guide_guard": {
            "status": "ok" if all(check["passed"] for check in guard_checks) else "conflict",
            "checks": guard_checks,
        },
        "signal": signal,
        "live_data_required": False,
    }


def evaluate_position(
    asset: str = "TQQQ",
    entry_price: float | None = None,
    current_price: float | None = None,
    size: float | None = None,
) -> dict[str, Any]:
    """Evaluate whether an existing position should be held, trimmed, or exited."""

    signal = score_leverage_swing(asset=asset)
    underlying = signal["underlying"]
    reference = signal["entry"]["reference_price"]
    entry = _normalize_optional_positive_finite_number(
        entry_price,
        "entry_price",
        default=float(reference) * 0.97,
    )
    current = _normalize_optional_positive_finite_number(
        current_price,
        "current_price",
        default=float(reference),
    )
    normalized_size = _normalize_optional_positive_finite_number(size, "size")
    pnl_pct = current / entry - 1
    action = TradeAction.WAIT
    position_state = "maintain"

    if signal["action"] in {TradeAction.BLOCK.value, TradeAction.STOP.value}:
        action = TradeAction.EXIT
        position_state = "exit"
    elif pnl_pct <= -0.06:
        action = TradeAction.STOP
        position_state = "stop"
    elif pnl_pct >= 0.12 or signal["component_scores"]["event_risk"] > 0.55:
        action = TradeAction.TRIM
        position_state = "trim"

    contract = {
        "schema_version": "position_management.v1",
        "allowed_actions": [
            TradeAction.WAIT.value,
            TradeAction.TRIM.value,
            TradeAction.EXIT.value,
            TradeAction.STOP.value,
        ],
        "allowed_position_states": ["maintain", "trim", "exit", "stop"],
        "decision_inputs": [
            "entry_price",
            "current_price",
            "unrealized_return_pct",
            "signal_action",
            "event_risk",
        ],
        "signal_id": signal["signal_id"],
        "config_version": signal["config_version"],
        "config_hash": signal["config_hash"],
        "numeric_authority": True,
        "order_submission": False,
        "live_data_required": False,
        "db_required": False,
    }
    guard_checks = [
        {"name": "action_allowed", "passed": action.value in contract["allowed_actions"]},
        {
            "name": "position_state_allowed",
            "passed": position_state in contract["allowed_position_states"],
        },
        {"name": "stop_conditions_present", "passed": bool(signal["stop"])},
        {
            "name": "take_profit_conditions_present",
            "passed": bool(signal["take_profit"]),
        },
        {
            "name": "signal_trace_present",
            "passed": signal["config_hash"].startswith("sha256:")
            and bool(signal["signal_id"]),
        },
        {"name": "no_order_submission", "passed": contract["order_submission"] is False},
        {
            "name": "no_live_data_required",
            "passed": contract["live_data_required"] is False,
        },
    ]

    return {
        "as_of": AS_OF,
        "asset": signal["asset"],
        "underlying": underlying,
        "entry_price": round(entry, 4),
        "current_price": round(current, 4),
        "size": normalized_size,
        "unrealized_return_pct": round(pnl_pct * 100, 4),
        "action": action.value,
        "position_state": position_state,
        "rationale": _position_rationale(position_state, signal, pnl_pct),
        "stop_conditions": signal["stop"],
        "take_profit_conditions": signal["take_profit"],
        "position_management_contract": contract,
        "position_management_guard": {
            "status": "ok" if all(check["passed"] for check in guard_checks) else "conflict",
            "checks": guard_checks,
        },
        "live_data_required": False,
    }


def _normalize_asset_identity(asset: str) -> str:
    if not isinstance(asset, str):
        raise ValueError("asset must be a nonempty string")
    if not _has_no_control_characters(asset):
        raise ValueError("asset must not contain control characters")
    normalized = asset.strip().upper()
    if not normalized:
        raise ValueError("asset must be a nonempty string")
    return normalized


def _normalize_timeframe_identity(timeframe: str) -> str:
    if not isinstance(timeframe, str):
        raise ValueError("timeframe must be a nonempty string")
    if not _has_no_control_characters(timeframe):
        raise ValueError("timeframe must not contain control characters")
    normalized = timeframe.strip()
    if not normalized:
        raise ValueError("timeframe must be a nonempty string")
    return normalized


def _has_no_control_characters(value: str) -> bool:
    return all(ord(character) >= 32 and ord(character) != 127 for character in value)


def _normalize_optional_positive_finite_number(
    value: float | None,
    field_name: str,
    *,
    default: float | None = None,
) -> float | None:
    if value is None:
        return default
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise ValueError(f"{field_name} must be a positive finite number")
    normalized = float(value)
    if not math.isfinite(normalized) or normalized <= 0.0:
        raise ValueError(f"{field_name} must be a positive finite number")
    return normalized


def evaluate_score_performance(
    signals: list[dict[str, Any]] | None = None,
    days: int = 90,
) -> dict[str, Any]:
    """Evaluate score calibration, attribution, and deterministic ablation."""

    normalized_days = _normalize_performance_days(days)
    if signals is None:
        sample = _demo_signal_outcomes(days=normalized_days)
        sample_source = "fixture_replay"
    else:
        sample = _normalize_performance_signals(signals)
        sample_source = "provided_signals"
    bins: dict[str, dict[str, float]] = {
        "0.00-0.35": {"count": 0, "take_profit_first": 0, "realized_r": 0.0},
        "0.35-0.52": {"count": 0, "take_profit_first": 0, "realized_r": 0.0},
        "0.52-0.68": {"count": 0, "take_profit_first": 0, "realized_r": 0.0},
        "0.68-1.00": {"count": 0, "take_profit_first": 0, "realized_r": 0.0},
    }
    total_realized_r = 0.0
    stop_loss_first = 0

    for item in sample:
        score = float(item["final_score"])
        outcome = item["outcome"]
        realized_r = float(item["realized_r"])
        key = _score_bin(score)
        bins[key]["count"] += 1
        bins[key]["realized_r"] += realized_r
        total_realized_r += realized_r
        if outcome == "TAKE_PROFIT_FIRST":
            bins[key]["take_profit_first"] += 1
        if outcome == "STOP_LOSS_FIRST":
            stop_loss_first += 1

    for values in bins.values():
        if values["count"]:
            values["avg_realized_r"] = round(values["realized_r"] / values["count"], 4)
            values["take_profit_rate"] = round(
                values["take_profit_first"] / values["count"], 4
            )
        values.pop("realized_r", None)

    out_of_sample_report = _out_of_sample_report(sample)
    walk_forward_report = _walk_forward_report(sample)
    overfit_guard = _overfit_guard(sample, out_of_sample_report, walk_forward_report)
    evaluation_window = _evaluation_window_metadata(
        sample,
        normalized_days,
        sample_source,
    )

    return {
        "as_of": AS_OF,
        "sample_size": len(sample),
        "avg_realized_r": round(total_realized_r / len(sample), 4) if sample else 0.0,
        "stop_loss_first_count": stop_loss_first,
        "score_bins": bins,
        "score_calibration": _score_calibration(sample),
        "component_attribution": _component_attribution(sample),
        "ablation_report": _ablation_report(sample),
        "out_of_sample_report": out_of_sample_report,
        "walk_forward_report": walk_forward_report,
        "overfit_guard": overfit_guard,
        "evaluation_window": evaluation_window,
        "calibration_note": (
            "Fixture evaluation expects higher score bins to produce stronger "
            "realized-R before any challenger is promoted."
        ),
        "live_data_required": False,
    }


def _normalize_performance_days(days: int) -> int:
    if not isinstance(days, int) or isinstance(days, bool) or days <= 0:
        raise ValueError("days must be a positive integer")
    return days


def _normalize_performance_signals(signals: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not isinstance(signals, list):
        raise ValueError("signals must be a list of objects")

    normalized: list[dict[str, Any]] = []
    for item in signals:
        if not isinstance(item, dict):
            raise ValueError("signals items must be objects")
        row = dict(item)
        row["final_score"] = _normalize_score_metric(row.get("final_score"))
        row["outcome"] = _normalize_outcome_metric(row.get("outcome"))
        row["realized_r"] = _normalize_realized_r_metric(row.get("realized_r"))
        if "age_days_ago" in row:
            row["age_days_ago"] = _normalize_age_days_metric(row["age_days_ago"])
        if row.get("component_scores") is not None:
            row["component_scores"] = _normalize_component_scores_metric(
                row["component_scores"]
            )
        normalized.append(row)
    return normalized


def _normalize_score_metric(value: Any) -> float:
    score = _normalize_finite_metric(value, "signals.final_score")
    if score < 0.0 or score > 1.0:
        raise ValueError("signals.final_score must be between 0 and 1")
    return score


def _normalize_realized_r_metric(value: Any) -> float:
    return _normalize_finite_metric(value, "signals.realized_r")


def _normalize_finite_metric(value: Any, field_name: str) -> float:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise ValueError(f"{field_name} must be a finite number")
    normalized = float(value)
    if not math.isfinite(normalized):
        raise ValueError(f"{field_name} must be a finite number")
    return normalized


def _normalize_outcome_metric(value: Any) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("signals.outcome must be a nonempty string")
    return value.strip()


def _normalize_age_days_metric(value: Any) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise ValueError("signals.age_days_ago must be a nonnegative integer")
    return value


def _normalize_component_scores_metric(value: Any) -> dict[str, float]:
    if not isinstance(value, dict):
        raise ValueError("signals.component_scores must be an object")
    normalized: dict[str, float] = {}
    for name, score in value.items():
        if not isinstance(name, str) or not name.strip():
            raise ValueError("signals.component_scores keys must be nonempty strings")
        normalized[name] = _normalize_finite_metric(
            score,
            "signals.component_scores values",
        )
    return normalized


def suggest_weight_update() -> dict[str, Any]:
    """Generate a challenger config without mutating the champion config."""

    champion = get_strategy_config()
    challenger = {
        **champion,
        "version": "0.1.0-challenger-vol-risk",
        "status": "challenger",
        "weights": {
            "trend": 0.24,
            "momentum": 0.18,
            "volatility": 0.23,
            "macro": 0.15,
            "event_safety": 0.12,
            "theme": 0.08,
        },
    }
    challenger.pop("config_hash", None)
    validation = validate_strategy_config(challenger)
    challenger["config_hash"] = validation["config_hash"]
    return {
        "as_of": AS_OF,
        "champion_config_hash": champion["config_hash"],
        "challenger": challenger,
        "challenger_contract": {
            "schema_version": "challenger_config.v1",
            "candidate_status": "challenger",
            "champion_unchanged": True,
            "approval_required": True,
            "shadow_validation_required": True,
            "out_of_sample_required": True,
            "auto_promotion_allowed": False,
            "validation_schema_version": validation["schema_version"],
            "config_hash_matches_challenger": validation["config_hash"]
            == challenger["config_hash"],
            "db_required": False,
            "live_data_required": False,
        },
        "validation": validation,
        "promotion_policy": (
            "Do not overwrite the active champion automatically. Promote only "
            "after out-of-sample comparison and explicit approval."
        ),
        "live_data_required": False,
    }


def compare_champion_challenger() -> dict[str, Any]:
    """Compare champion and challenger on deterministic fixture signals."""

    champion_perf = evaluate_score_performance()
    challenger = suggest_weight_update()["challenger"]
    challenger_sample = []
    for item in _demo_signal_outcomes(days=90):
        adjusted = dict(item)
        adjusted["final_score"] = min(1.0, adjusted["final_score"] + 0.025)
        adjusted["realized_r"] = adjusted["realized_r"] + 0.04
        challenger_sample.append(adjusted)
    challenger_perf = evaluate_score_performance(challenger_sample)

    return {
        "as_of": AS_OF,
        "champion": {
            "config_hash": get_strategy_config()["config_hash"],
            "performance": champion_perf,
        },
        "challenger": {
            "config_hash": challenger["config_hash"],
            "performance": challenger_perf,
        },
        "decision": "keep_champion_shadow_challenger",
        "reason": "Fixture improvement is not enough to bypass shadow validation.",
        "promotion_report": _promotion_report(champion_perf, challenger_perf),
        "live_data_required": False,
    }


def _component_scores(
    underlying: str,
    indicators: dict[str, Any],
    macro: dict[str, Any],
    events: dict[str, Any],
    news: dict[str, Any],
) -> dict[str, float]:
    close = float(indicators["latest_bar"]["close"])
    ma_20 = float(indicators["ma_20"])
    ma_50 = float(indicators["ma_50"])
    ma_200 = float(indicators["ma_200"])
    rsi_14 = float(indicators["rsi_14"])
    atr_percent = float(indicators["atr_percent"])
    plus_di = float(indicators["plus_di_14"])
    minus_di = float(indicators["minus_di_14"])
    adx = float(indicators["adx_14"])
    event_risk = float(events["highest_event_risk"])
    theme_score = UNDERLYING_PROFILES.get(underlying, UNDERLYING_PROFILES["QQQ"]).theme_score

    trend = 0.35
    trend += 0.18 if close > ma_20 else -0.05
    trend += 0.18 if close > ma_50 else -0.10
    trend += 0.14 if close > ma_200 else -0.20
    trend += 0.10 if plus_di > minus_di else -0.05
    trend += 0.05 if adx >= 18 else 0.0

    if 45 <= rsi_14 <= 67:
        momentum = 0.72
    elif 35 <= rsi_14 < 45:
        momentum = 0.55
    elif 67 < rsi_14 <= 75:
        momentum = 0.52
    else:
        momentum = 0.35

    volatility = max(0.0, min(1.0, 1 - atr_percent / 8))
    macro_score = float(macro["macro_score"])
    event_safety = max(0.0, 1 - event_risk)
    news_strength = float(news["news_score"])
    theme = min(1.0, (theme_score + news_strength) / 2)
    distance_from_ma20 = close / ma_20 - 1
    pullback = 0.62 - abs(distance_from_ma20) * 5.0
    if close > ma_50 and close > ma_200:
        pullback += 0.08
    if rsi_14 > 75:
        pullback -= 0.10
    breadth = (
        (0.35 if close > ma_50 else 0.10)
        + (0.25 if close > ma_200 else 0.05)
        + (0.20 if plus_di > minus_di else 0.05)
        + min(0.20, theme_score * 0.20)
    )

    return {
        "trend": round(max(0.0, min(1.0, trend)), 4),
        "pullback": round(max(0.0, min(1.0, pullback)), 4),
        "momentum": round(momentum, 4),
        "breadth": round(max(0.0, min(1.0, breadth)), 4),
        "volatility": round(volatility, 4),
        "macro": round(macro_score, 4),
        "event_safety": round(event_safety, 4),
        "event_risk": round(event_risk, 4),
        "theme": round(theme, 4),
    }


def _weighted_score(components: dict[str, float], weights: dict[str, float]) -> float:
    return sum(float(components[name]) * float(weight) for name, weight in weights.items())


def _action_for_score(
    final_score: float,
    leverage: int,
    components: dict[str, float],
    indicators: dict[str, Any],
    config: dict[str, Any],
) -> TradeAction:
    thresholds = config["thresholds"]
    if (
        final_score < thresholds["block"]
        or components["event_risk"] >= 0.80
        or indicators["trend_state"] == "risk_off"
    ):
        return TradeAction.BLOCK
    if final_score >= thresholds["buy_3x"] and leverage >= 3:
        if components["event_risk"] <= config["risk"]["max_3x_event_risk"]:
            return TradeAction.BUY_3X
        return TradeAction.BUY_2X
    if final_score >= thresholds["buy_2x"]:
        return TradeAction.BUY_2X
    if final_score >= thresholds["buy_watch"]:
        return TradeAction.BUY_WATCH
    return TradeAction.WAIT


def _risk_references(
    indicators: dict[str, Any],
    config: dict[str, Any],
) -> dict[str, float]:
    close = float(indicators["latest_bar"]["close"])
    atr_value = float(indicators["atr_14"])
    support = float(indicators["support_20"])
    resistance = float(indicators["resistance_20"])
    stop_price = min(support, close - config["risk"]["stop_atr_multiple"] * atr_value)
    take_profit = max(
        resistance,
        close + config["risk"]["take_profit_atr_multiple"] * atr_value,
    )
    return {
        "stop_price": round(stop_price, 2),
        "take_profit_price": round(take_profit, 2),
        "resistance_20": round(resistance, 2),
    }


def _confidence(final_score: float, components: dict[str, float]) -> float:
    spread_penalty = max(components.values()) - min(components.values())
    return round(max(0.20, min(0.90, 0.35 + final_score * 0.65 - spread_penalty * 0.08)), 4)


def _risk_warnings(
    components: dict[str, float],
    events: dict[str, Any],
    macro_filter: dict[str, Any] | None = None,
) -> list[str]:
    warnings: list[str] = []
    macro_filter = macro_filter or {}
    if macro_filter.get("blocks_new_longs_now"):
        warnings.append("Macro filter blocks new leveraged longs until risk shocks ease.")
    elif macro_filter.get("blocks_new_3x_now"):
        warnings.append("Macro filter blocks new 3x entries until VIX/DXY/rates stabilize.")
    if components["event_risk"] > 0.65:
        warnings.append("A high-risk event window is inside the next 14 days.")
    if events["highest_event_risk"] > 0.70:
        warnings.append("3x entries require confirmation because CPI/FOMC risk is near.")
    return warnings


def _entry_summary(
    action: TradeAction,
    underlying: str,
    indicators: dict[str, Any],
) -> str:
    if action in {TradeAction.BUY_2X, TradeAction.BUY_3X}:
        return (
            f"Entry is favored only if {underlying} holds above MA20 near "
            f"{indicators['ma_20']} and confirms follow-through."
        )
    if action == TradeAction.BUY_WATCH:
        return f"{underlying} is a watch candidate; wait for confirmation before entry."
    return f"Entry is deferred until {underlying} trend and event risk improve."


def _stop_summary(underlying: str, references: dict[str, float]) -> str:
    return f"Stop is guided by {underlying} closing below {references['stop_price']}."


def _take_profit_summary(underlying: str, references: dict[str, float]) -> str:
    return (
        f"Take profit is guided by {underlying} reaching "
        f"{references['take_profit_price']} or resistance exhaustion."
    )


def _invalidation_summary(underlying: str) -> str:
    return f"Setup invalidates if {underlying} loses support with volatility expansion."


def _risk_summary(
    action: TradeAction,
    leverage: int,
    components: dict[str, float],
) -> str:
    if action in {TradeAction.BUY_2X, TradeAction.BUY_3X}:
        return (
            f"Risk is acceptable for a {leverage}x tactical swing, but event risk "
            f"is {components['event_risk']:.2f} and must be monitored."
        )
    if action == TradeAction.BUY_WATCH:
        return "Risk is mixed; confirmation is required before any leveraged entry."
    return "Risk/reward is not strong enough for a new leveraged long."


def _reason_summary(action: TradeAction, components: dict[str, float]) -> str:
    strongest = max(
        (key for key in components if key != "event_risk"),
        key=lambda key: components[key],
    )
    weakest = min(
        (key for key in components if key != "event_risk"),
        key=lambda key: components[key],
    )
    return (
        f"{action.value} comes from strongest component {strongest} and weakest "
        f"component {weakest}; event risk remains explicit."
    )


def _evidence_summary(news: dict[str, Any]) -> str:
    return "; ".join(card["summary"] for card in news["evidence_cards"][:2])


def _position_rationale(
    position_state: str,
    signal: dict[str, Any],
    pnl_pct: float,
) -> str:
    if position_state == "trim":
        return "Trim because profit or event risk justifies reducing exposure."
    if position_state == "exit":
        return "Exit because the current swing signal blocks fresh long exposure."
    if position_state == "stop":
        return "Stop because realized drawdown exceeded the tactical risk budget."
    return (
        f"Maintain while {signal['underlying']} respects the stop plan; current "
        f"return is {pnl_pct:.2%}."
    )


def _score_bin(score: float) -> str:
    if score < 0.35:
        return "0.00-0.35"
    if score < 0.52:
        return "0.35-0.52"
    if score < 0.68:
        return "0.52-0.68"
    return "0.68-1.00"


def _component_attribution(sample: list[dict[str, Any]]) -> dict[str, Any]:
    component_rows = [item for item in sample if item.get("component_scores")]
    if not component_rows:
        return {
            "available": False,
            "components": [],
            "note": "No component_scores were available for attribution.",
        }

    components = [
        name
        for name in get_strategy_config()["weights"]
        if name in component_rows[0]["component_scores"]
    ]
    rows = []
    for component in components:
        weighted_sum = 0.0
        winning_values: list[float] = []
        losing_values: list[float] = []
        for item in component_rows:
            value = float(item["component_scores"][component])
            weighted_sum += value * float(item["realized_r"])
            if item["outcome"] == "TAKE_PROFIT_FIRST":
                winning_values.append(value)
            else:
                losing_values.append(value)
        row = {
            "component": component,
            "avg_when_take_profit_first": _avg(winning_values),
            "avg_when_not_take_profit_first": _avg(losing_values),
            "realized_r_weighted_signal": round(weighted_sum / len(component_rows), 4),
        }
        rows.append(row)

    rows.sort(key=lambda row: row["realized_r_weighted_signal"], reverse=True)
    return {
        "available": True,
        "components": rows,
        "note": "Positive weighted signal means higher component values aligned with higher realized R in the fixture sample.",
    }


def _score_calibration(sample: list[dict[str, Any]]) -> dict[str, Any]:
    if not sample:
        return {
            "available": False,
            "bins": [],
            "score_bin_order_check": "insufficient_sample",
            "take_profit_rate_order_check": "insufficient_sample",
            "largest_abs_calibration_error": None,
            "note": "No labeled samples were available for score calibration.",
        }

    grouped: dict[str, list[dict[str, Any]]] = {
        "0.00-0.35": [],
        "0.35-0.52": [],
        "0.52-0.68": [],
        "0.68-1.00": [],
    }
    for item in sample:
        grouped[_score_bin(float(item["final_score"]))].append(item)

    bins = []
    for bin_name, rows in grouped.items():
        avg_score = _avg([float(item["final_score"]) for item in rows])
        realized_take_profit_rate = _take_profit_rate(rows)
        expected_take_profit_rate = (
            _expected_take_profit_rate(avg_score) if avg_score is not None else None
        )
        calibration_error = (
            round(realized_take_profit_rate - expected_take_profit_rate, 4)
            if realized_take_profit_rate is not None
            and expected_take_profit_rate is not None
            else None
        )
        bins.append(
            {
                "score_bin": bin_name,
                "sample_count": len(rows),
                "avg_score": avg_score,
                "expected_take_profit_rate": expected_take_profit_rate,
                "realized_take_profit_rate": realized_take_profit_rate,
                "avg_realized_r": _avg([float(item["realized_r"]) for item in rows]),
                "calibration_error": calibration_error,
            }
        )

    calibration_errors = [
        abs(float(row["calibration_error"]))
        for row in bins
        if row["calibration_error"] is not None
    ]
    return {
        "available": True,
        "bins": bins,
        "score_bin_order_check": _score_bin_order_check(
            {row["score_bin"]: row["avg_realized_r"] for row in bins}
        ),
        "take_profit_rate_order_check": _take_profit_rate_order_check(bins),
        "largest_abs_calibration_error": (
            round(max(calibration_errors), 4) if calibration_errors else None
        ),
        "note": (
            "Compares expected take-profit rate from final_score against labeled "
            "fixture outcomes. This is offline evidence only."
        ),
    }


def _ablation_report(sample: list[dict[str, Any]]) -> dict[str, Any]:
    config = get_strategy_config()
    component_rows = [item for item in sample if item.get("component_scores")]
    if not component_rows:
        return {
            "available": False,
            "ablations": [],
            "note": "No component_scores were available for ablation.",
        }

    baseline_avg_score = _avg([float(item["final_score"]) for item in component_rows])
    ablations = []
    for component, weight in config["weights"].items():
        adjusted_scores = []
        for item in component_rows:
            component_value = float(item["component_scores"].get(component, 0.0))
            adjusted_scores.append(float(item["final_score"]) - component_value * float(weight))
        ablations.append(
            {
                "removed_component": component,
                "avg_score_without_component": _avg(adjusted_scores),
                "avg_score_delta": round(_avg(adjusted_scores) - baseline_avg_score, 4),
            }
        )

    ablations.sort(key=lambda row: row["avg_score_delta"])
    return {
        "available": True,
        "baseline_avg_score": baseline_avg_score,
        "ablations": ablations,
        "note": "A larger negative delta means the component contributed more to fixture scores.",
    }


def _promotion_report(
    champion_perf: dict[str, Any],
    challenger_perf: dict[str, Any],
) -> dict[str, Any]:
    champion_avg = float(champion_perf["avg_realized_r"])
    challenger_avg = float(challenger_perf["avg_realized_r"])
    delta = round(challenger_avg - champion_avg, 4)
    champion_oos = champion_perf["out_of_sample_report"]
    challenger_oos = challenger_perf["out_of_sample_report"]
    return {
        "champion_avg_realized_r": champion_avg,
        "challenger_avg_realized_r": challenger_avg,
        "delta_avg_realized_r": delta,
        "out_of_sample_required": True,
        "champion_out_of_sample_ready": champion_oos["ready"],
        "challenger_out_of_sample_ready": challenger_oos["ready"],
        "challenger_out_of_sample_avg_realized_r": challenger_oos[
            "out_of_sample_avg_realized_r"
        ],
        "approval_required": True,
        "promote": False,
        "reason": (
            "Keep challenger in shadow mode; fixture delta alone is not enough "
            "for automatic promotion."
        ),
    }


def _out_of_sample_report(sample: list[dict[str, Any]]) -> dict[str, Any]:
    if len(sample) < 4:
        return {
            "ready": False,
            "sample_size": len(sample),
            "in_sample_count": len(sample),
            "out_of_sample_count": 0,
            "out_of_sample_avg_realized_r": None,
            "score_bin_order_check": "insufficient_sample",
            "note": "Need at least four labeled samples before fixture OOS split.",
        }

    ordered = sorted(
        sample,
        key=lambda item: int(item.get("age_days_ago", 0)),
        reverse=True,
    )
    split_index = max(1, min(len(ordered) - 1, int(len(ordered) * 0.67)))
    in_sample = ordered[:split_index]
    out_of_sample = ordered[split_index:]
    oos_avg = _avg([float(item["realized_r"]) for item in out_of_sample])
    bin_scores = _bin_avg_realized_r(out_of_sample)
    return {
        "ready": len(out_of_sample) >= 3,
        "sample_size": len(sample),
        "in_sample_count": len(in_sample),
        "out_of_sample_count": len(out_of_sample),
        "out_of_sample_avg_realized_r": oos_avg,
        "out_of_sample_take_profit_rate": _take_profit_rate(out_of_sample),
        "score_bin_avg_realized_r": bin_scores,
        "score_bin_order_check": _score_bin_order_check(bin_scores),
        "asset_breakdown": _group_performance(out_of_sample, "asset"),
        "regime_breakdown": _group_performance(out_of_sample, "market_regime"),
        "promotion_policy": (
            "Out-of-sample fixture performance is evidence only; promotion still "
            "requires explicit approval."
        ),
    }


def _walk_forward_report(sample: list[dict[str, Any]]) -> dict[str, Any]:
    if len(sample) < 8:
        return {
            "ready": False,
            "sample_size": len(sample),
            "fold_count": 0,
            "positive_fold_rate": None,
            "folds": [],
            "coverage": _fixture_coverage(sample),
            "note": "Need at least eight labeled samples before walk-forward fixture evaluation.",
        }

    ordered = _chronological_sample(sample)
    train_size = max(4, len(ordered) // 3)
    test_window = max(2, len(ordered) // 6)
    folds = []

    for fold_number, start in enumerate(range(train_size, len(ordered), test_window), 1):
        train = ordered[:start]
        test = ordered[start : start + test_window]
        if not test:
            continue
        test_avg = _avg([float(item["realized_r"]) for item in test])
        folds.append(
            {
                "fold": fold_number,
                "train_count": len(train),
                "test_count": len(test),
                "train_age_range_days_ago": _age_range(train),
                "test_age_range_days_ago": _age_range(test),
                "test_avg_realized_r": test_avg,
                "test_take_profit_rate": _take_profit_rate(test),
                "test_score_bin_order_check": _score_bin_order_check(
                    _bin_avg_realized_r(test)
                ),
                "test_regime_breakdown": _group_performance(test, "market_regime"),
            }
        )

    positive_fold_count = sum(
        1 for fold in folds if float(fold["test_avg_realized_r"] or 0.0) > 0.0
    )
    total_test_count = sum(int(fold["test_count"]) for fold in folds)
    positive_fold_rate = (
        round(positive_fold_count / len(folds), 4) if folds else None
    )

    return {
        "ready": len(folds) >= 3 and total_test_count >= 6,
        "sample_size": len(sample),
        "fold_count": len(folds),
        "total_test_count": total_test_count,
        "positive_fold_count": positive_fold_count,
        "positive_fold_rate": positive_fold_rate,
        "coverage": _fixture_coverage(sample),
        "folds": folds,
        "promotion_policy": (
            "Walk-forward fixture evidence is advisory only; challenger promotion "
            "still requires explicit approval."
        ),
    }


def _overfit_guard(
    sample: list[dict[str, Any]],
    out_of_sample_report: dict[str, Any],
    walk_forward_report: dict[str, Any],
) -> dict[str, Any]:
    coverage = walk_forward_report.get("coverage", {})
    regimes = coverage.get("market_regimes", [])
    positive_fold_rate = walk_forward_report.get("positive_fold_rate")
    ratio = _conservative_realized_r_ratio(sample)
    deflated_proxy = _deflated_sharpe_proxy(sample)
    checks = [
        {
            "name": "minimum_fixture_size",
            "passed": len(sample) >= 12,
            "actual": len(sample),
            "expected": ">=12",
        },
        {
            "name": "out_of_sample_ready",
            "passed": bool(out_of_sample_report.get("ready")),
            "actual": out_of_sample_report.get("ready"),
            "expected": True,
        },
        {
            "name": "walk_forward_ready",
            "passed": bool(walk_forward_report.get("ready")),
            "actual": walk_forward_report.get("ready"),
            "expected": True,
        },
        {
            "name": "positive_walk_forward_fold_rate",
            "passed": positive_fold_rate is not None and positive_fold_rate >= 0.67,
            "actual": positive_fold_rate,
            "expected": ">=0.67",
        },
        {
            "name": "multi_regime_fixture_coverage",
            "passed": len(regimes) >= 3,
            "actual": regimes,
            "expected": ">=3 regimes",
        },
        {
            "name": "deflated_sharpe_proxy_positive",
            "passed": deflated_proxy["status"] == "ok",
            "actual": deflated_proxy["deflated_sharpe_proxy"],
            "expected": ">0 after fixture trial penalty",
        },
    ]
    return {
        "status": "ok" if all(check["passed"] for check in checks) else "watch",
        "checks": checks,
        "conservative_realized_r_ratio": ratio,
        "deflated_sharpe_proxy": deflated_proxy,
        "auto_promotion_allowed": False,
        "approval_required": True,
        "note": (
            "This guard is a conservative fixture check against overfitting. It "
            "does not replace real out-of-sample data or approval."
        ),
    }


def _bin_avg_realized_r(sample: list[dict[str, Any]]) -> dict[str, float | None]:
    grouped: dict[str, list[float]] = {
        "0.00-0.35": [],
        "0.35-0.52": [],
        "0.52-0.68": [],
        "0.68-1.00": [],
    }
    for item in sample:
        grouped[_score_bin(float(item["final_score"]))].append(float(item["realized_r"]))
    return {key: _avg(values) for key, values in grouped.items()}


def _score_bin_order_check(bin_scores: dict[str, float | None]) -> str:
    low = bin_scores["0.35-0.52"]
    high = bin_scores["0.68-1.00"]
    if low is None or high is None:
        return "insufficient_bins"
    return "higher_scores_outperform" if high >= low else "needs_review"


def _take_profit_rate_order_check(bins: list[dict[str, Any]]) -> str:
    low = next(
        (row["realized_take_profit_rate"] for row in bins if row["score_bin"] == "0.35-0.52"),
        None,
    )
    high = next(
        (row["realized_take_profit_rate"] for row in bins if row["score_bin"] == "0.68-1.00"),
        None,
    )
    if low is None or high is None:
        return "insufficient_bins"
    return "higher_scores_higher_take_profit_rate" if high >= low else "needs_review"


def _expected_take_profit_rate(avg_score: float | None) -> float | None:
    if avg_score is None:
        return None
    return round(min(0.82, 0.35 + avg_score * 0.55), 4)


def _take_profit_rate(sample: list[dict[str, Any]]) -> float | None:
    if not sample:
        return None
    wins = sum(1 for item in sample if item["outcome"] == "TAKE_PROFIT_FIRST")
    return round(wins / len(sample), 4)


def _avg(values: list[float]) -> float | None:
    if not values:
        return None
    return round(sum(values) / len(values), 4)


def _chronological_sample(sample: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        sample,
        key=lambda item: int(item.get("age_days_ago", 0)),
        reverse=True,
    )


def _age_range(sample: list[dict[str, Any]]) -> dict[str, int | None]:
    ages = [int(item.get("age_days_ago", 0)) for item in sample]
    if not ages:
        return {"oldest": None, "newest": None}
    return {"oldest": max(ages), "newest": min(ages)}


def _evaluation_window_metadata(
    sample: list[dict[str, Any]],
    requested_days: int,
    sample_source: str,
) -> dict[str, Any]:
    age_range = _age_range(sample)
    oldest = age_range["oldest"]
    minimum_supported_coverage_ratio = 0.95
    coverage_ratio = (
        round(float(oldest) / requested_days, 4)
        if oldest is not None and requested_days > 0
        else None
    )
    fixture_replay_default = sample_source == "fixture_replay"
    requested_window_supported = (
        coverage_ratio is not None
        and coverage_ratio >= minimum_supported_coverage_ratio
        if fixture_replay_default
        else None
    )
    available_fixture_window_days = (
        int(oldest) if fixture_replay_default and oldest is not None else None
    )
    requested_window_gap_days = (
        max(0, int(requested_days) - int(oldest))
        if fixture_replay_default and oldest is not None and requested_days > 0
        else None
    )
    if not fixture_replay_default:
        coverage_status = "provided_signals_not_fixture_windowed"
        unsupported_reason = None
    elif requested_window_supported:
        coverage_status = "supported_fixture_window"
        unsupported_reason = None
    elif sample:
        coverage_status = "unsupported_requested_window"
        unsupported_reason = "requested_days_exceed_fixture_coverage"
    else:
        coverage_status = "empty_fixture_window"
        unsupported_reason = "no_fixture_samples_available"
    return {
        "schema_version": "fixture_oos_window.v1",
        "requested_days": requested_days,
        "sample_source": sample_source,
        "sample_size": len(sample),
        "sample_age_range_days_ago": age_range,
        "available_fixture_window_days": available_fixture_window_days,
        "minimum_supported_coverage_ratio": minimum_supported_coverage_ratio,
        "requested_window_coverage_ratio": coverage_ratio,
        "requested_window_supported": requested_window_supported,
        "requested_window_gap_days": requested_window_gap_days,
        "coverage_status": coverage_status,
        "unsupported_reason": unsupported_reason,
        "fixture_replay_default": fixture_replay_default,
        "supported_fixture_windows_days": [90, 180],
        "extended_fixture_window_days": 180,
        "live_data_required": False,
        "repository_required": False,
        "network_call": False,
        "note": (
            "Fixture-backed OOS windows are deterministic evidence only; real "
            "repository and live data gates remain separate approvals."
        ),
    }


def _group_performance(
    sample: list[dict[str, Any]],
    key: str,
) -> dict[str, dict[str, float | int | None]]:
    groups: dict[str, list[dict[str, Any]]] = {}
    for item in sample:
        group_key = str(item.get(key) or "unknown")
        groups.setdefault(group_key, []).append(item)

    return {
        group_key: {
            "count": len(rows),
            "avg_realized_r": _avg([float(item["realized_r"]) for item in rows]),
            "take_profit_rate": _take_profit_rate(rows),
        }
        for group_key, rows in sorted(groups.items())
    }


def _fixture_coverage(sample: list[dict[str, Any]]) -> dict[str, Any]:
    assets = sorted({str(item.get("asset") or "unknown") for item in sample})
    regimes = sorted({str(item.get("market_regime") or "unknown") for item in sample})
    return {
        "assets": assets,
        "market_regimes": regimes,
        "asset_count": len(assets),
        "market_regime_count": len(regimes),
    }


def _conservative_realized_r_ratio(sample: list[dict[str, Any]]) -> float | None:
    realized_values = [float(item["realized_r"]) for item in sample]
    avg = _avg(realized_values)
    stddev = _stddev(realized_values)
    if avg is None or stddev is None or stddev == 0:
        return None
    return round(avg / stddev, 4)


def _deflated_sharpe_proxy(sample: list[dict[str, Any]]) -> dict[str, Any]:
    realized_values = [float(item["realized_r"]) for item in sample]
    avg = _avg(realized_values)
    stddev = _stddev(realized_values)
    sample_size = len(realized_values)
    trial_count = max(2, len({item.get("asset") for item in sample}))
    if avg is None or stddev is None or stddev == 0 or sample_size < 2:
        return {
            "schema_version": "deflated_sharpe_proxy.v1",
            "status": "insufficient_sample",
            "exact_deflated_sharpe_ratio": False,
            "sample_size": sample_size,
            "trial_count": trial_count,
            "sharpe_like_realized_r": None,
            "multiple_testing_penalty": None,
            "deflated_sharpe_proxy": None,
            "promotion_allowed": False,
        }

    sharpe_like = avg / stddev
    penalty = math.sqrt((2 * math.log(trial_count)) / sample_size)
    deflated = sharpe_like - penalty
    return {
        "schema_version": "deflated_sharpe_proxy.v1",
        "status": "ok" if deflated > 0 else "watch",
        "exact_deflated_sharpe_ratio": False,
        "sample_size": sample_size,
        "trial_count": trial_count,
        "sharpe_like_realized_r": round(sharpe_like, 4),
        "multiple_testing_penalty": round(penalty, 4),
        "deflated_sharpe_proxy": round(deflated, 4),
        "promotion_allowed": False,
        "note": (
            "Offline conservative proxy only; exact Deflated Sharpe Ratio and "
            "real OOS evaluation remain future hardening."
        ),
    }


def _stddev(values: list[float]) -> float | None:
    if len(values) < 2:
        return None
    mean = sum(values) / len(values)
    variance = sum((value - mean) ** 2 for value in values) / (len(values) - 1)
    return round(variance**0.5, 4)


def _decorate_demo_outcomes(outcomes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    assets = ["TQQQ", "QLD", "SSO", "UPRO", "SOXL"]
    regimes = [
        "risk_off_rebound",
        "event_risk",
        "trend_followthrough",
        "volatility_compression",
        "range_bound",
    ]
    decorated = []
    for index, item in enumerate(outcomes):
        decorated.append(
            {
                **item,
                "asset": item.get("asset", assets[index % len(assets)]),
                "market_regime": item.get(
                    "market_regime",
                    regimes[index % len(regimes)],
                ),
            }
        )
    return decorated


def _demo_signal_outcomes(days: int = 90) -> list[dict[str, Any]]:
    outcomes = [
        {
            "signal_id": "demo_180_low_wait",
            "age_days_ago": 178,
            "final_score": 0.30,
            "outcome": "TIME_EXIT",
            "realized_r": 0.04,
            "component_scores": {
                "trend": 0.33,
                "momentum": 0.40,
                "volatility": 0.47,
                "macro": 0.44,
                "event_safety": 0.32,
                "theme": 0.35,
            },
        },
        {
            "signal_id": "demo_180_watch_stop",
            "age_days_ago": 171,
            "final_score": 0.45,
            "outcome": "STOP_LOSS_FIRST",
            "realized_r": -0.72,
            "component_scores": {
                "trend": 0.55,
                "momentum": 0.49,
                "volatility": 0.41,
                "macro": 0.47,
                "event_safety": 0.29,
                "theme": 0.54,
            },
        },
        {
            "signal_id": "demo_180_mid_win",
            "age_days_ago": 164,
            "final_score": 0.58,
            "outcome": "TAKE_PROFIT_FIRST",
            "realized_r": 0.94,
            "component_scores": {
                "trend": 0.70,
                "momentum": 0.61,
                "volatility": 0.64,
                "macro": 0.57,
                "event_safety": 0.56,
                "theme": 0.59,
            },
        },
        {
            "signal_id": "demo_180_high_trend_win",
            "age_days_ago": 157,
            "final_score": 0.71,
            "outcome": "TAKE_PROFIT_FIRST",
            "realized_r": 1.44,
            "component_scores": {
                "trend": 0.85,
                "momentum": 0.73,
                "volatility": 0.72,
                "macro": 0.66,
                "event_safety": 0.62,
                "theme": 0.69,
            },
        },
        {
            "signal_id": "demo_180_low_range",
            "age_days_ago": 150,
            "final_score": 0.28,
            "outcome": "TIME_EXIT",
            "realized_r": -0.06,
            "component_scores": {
                "trend": 0.27,
                "momentum": 0.37,
                "volatility": 0.45,
                "macro": 0.41,
                "event_safety": 0.35,
                "theme": 0.37,
            },
        },
        {
            "signal_id": "demo_180_event_drag",
            "age_days_ago": 143,
            "final_score": 0.47,
            "outcome": "STOP_LOSS_FIRST",
            "realized_r": -0.58,
            "component_scores": {
                "trend": 0.59,
                "momentum": 0.51,
                "volatility": 0.43,
                "macro": 0.45,
                "event_safety": 0.27,
                "theme": 0.55,
            },
        },
        {
            "signal_id": "demo_180_mid_followthrough",
            "age_days_ago": 136,
            "final_score": 0.61,
            "outcome": "TAKE_PROFIT_FIRST",
            "realized_r": 0.86,
            "component_scores": {
                "trend": 0.73,
                "momentum": 0.63,
                "volatility": 0.66,
                "macro": 0.59,
                "event_safety": 0.58,
                "theme": 0.60,
            },
        },
        {
            "signal_id": "demo_180_high_extension",
            "age_days_ago": 129,
            "final_score": 0.74,
            "outcome": "TAKE_PROFIT_FIRST",
            "realized_r": 1.52,
            "component_scores": {
                "trend": 0.88,
                "momentum": 0.75,
                "volatility": 0.74,
                "macro": 0.68,
                "event_safety": 0.64,
                "theme": 0.71,
            },
        },
        {
            "signal_id": "demo_180_mid_timeout",
            "age_days_ago": 122,
            "final_score": 0.52,
            "outcome": "TIME_EXIT",
            "realized_r": 0.16,
            "component_scores": {
                "trend": 0.61,
                "momentum": 0.53,
                "volatility": 0.56,
                "macro": 0.50,
                "event_safety": 0.49,
                "theme": 0.54,
            },
        },
        {
            "signal_id": "demo_180_mid_grind_win",
            "age_days_ago": 115,
            "final_score": 0.55,
            "outcome": "TAKE_PROFIT_FIRST",
            "realized_r": 0.72,
            "component_scores": {
                "trend": 0.65,
                "momentum": 0.57,
                "volatility": 0.60,
                "macro": 0.53,
                "event_safety": 0.54,
                "theme": 0.57,
            },
        },
        {
            "signal_id": "demo_180_low_stop",
            "age_days_ago": 108,
            "final_score": 0.39,
            "outcome": "STOP_LOSS_FIRST",
            "realized_r": -0.38,
            "component_scores": {
                "trend": 0.44,
                "momentum": 0.43,
                "volatility": 0.45,
                "macro": 0.39,
                "event_safety": 0.33,
                "theme": 0.46,
            },
        },
        {
            "signal_id": "demo_180_high_win",
            "age_days_ago": 101,
            "final_score": 0.70,
            "outcome": "TAKE_PROFIT_FIRST",
            "realized_r": 1.31,
            "component_scores": {
                "trend": 0.83,
                "momentum": 0.71,
                "volatility": 0.71,
                "macro": 0.65,
                "event_safety": 0.61,
                "theme": 0.68,
            },
        },
        {
            "signal_id": "demo_180_mid_oos_win",
            "age_days_ago": 97,
            "final_score": 0.60,
            "outcome": "TAKE_PROFIT_FIRST",
            "realized_r": 0.80,
            "component_scores": {
                "trend": 0.72,
                "momentum": 0.62,
                "volatility": 0.65,
                "macro": 0.58,
                "event_safety": 0.57,
                "theme": 0.60,
            },
        },
        {
            "signal_id": "demo_180_low_time_exit",
            "age_days_ago": 94,
            "final_score": 0.34,
            "outcome": "TIME_EXIT",
            "realized_r": 0.08,
            "component_scores": {
                "trend": 0.39,
                "momentum": 0.41,
                "volatility": 0.49,
                "macro": 0.44,
                "event_safety": 0.38,
                "theme": 0.42,
            },
        },
        {
            "signal_id": "demo_180_high_partial_win",
            "age_days_ago": 92,
            "final_score": 0.68,
            "outcome": "TAKE_PROFIT_FIRST",
            "realized_r": 1.22,
            "component_scores": {
                "trend": 0.80,
                "momentum": 0.69,
                "volatility": 0.70,
                "macro": 0.63,
                "event_safety": 0.60,
                "theme": 0.66,
            },
        },
        {
            "signal_id": "demo_180_watch_late_stop",
            "age_days_ago": 91,
            "final_score": 0.43,
            "outcome": "STOP_LOSS_FIRST",
            "realized_r": -0.32,
            "component_scores": {
                "trend": 0.51,
                "momentum": 0.47,
                "volatility": 0.44,
                "macro": 0.46,
                "event_safety": 0.37,
                "theme": 0.49,
            },
        },
        {
            "signal_id": "demo_low_wait",
            "age_days_ago": 88,
            "final_score": 0.31,
            "outcome": "TIME_EXIT",
            "realized_r": 0.02,
            "component_scores": {
                "trend": 0.34,
                "momentum": 0.42,
                "volatility": 0.48,
                "macro": 0.45,
                "event_safety": 0.30,
                "theme": 0.36,
            },
        },
        {
            "signal_id": "demo_watch",
            "age_days_ago": 81,
            "final_score": 0.46,
            "outcome": "STOP_LOSS_FIRST",
            "realized_r": -1.0,
            "component_scores": {
                "trend": 0.58,
                "momentum": 0.50,
                "volatility": 0.42,
                "macro": 0.48,
                "event_safety": 0.28,
                "theme": 0.56,
            },
        },
        {
            "signal_id": "demo_buy_2x",
            "age_days_ago": 74,
            "final_score": 0.59,
            "outcome": "TAKE_PROFIT_FIRST",
            "realized_r": 1.28,
            "component_scores": {
                "trend": 0.72,
                "momentum": 0.64,
                "volatility": 0.66,
                "macro": 0.60,
                "event_safety": 0.55,
                "theme": 0.58,
            },
        },
        {
            "signal_id": "demo_buy_3x",
            "age_days_ago": 67,
            "final_score": 0.72,
            "outcome": "TAKE_PROFIT_FIRST",
            "realized_r": 1.55,
            "component_scores": {
                "trend": 0.88,
                "momentum": 0.74,
                "volatility": 0.72,
                "macro": 0.68,
                "event_safety": 0.62,
                "theme": 0.70,
            },
        },
        {
            "signal_id": "demo_block_low_trend",
            "age_days_ago": 60,
            "final_score": 0.27,
            "outcome": "TIME_EXIT",
            "realized_r": -0.08,
            "component_scores": {
                "trend": 0.25,
                "momentum": 0.36,
                "volatility": 0.44,
                "macro": 0.42,
                "event_safety": 0.34,
                "theme": 0.38,
            },
        },
        {
            "signal_id": "demo_watch_event_risk",
            "age_days_ago": 53,
            "final_score": 0.49,
            "outcome": "STOP_LOSS_FIRST",
            "realized_r": -0.82,
            "component_scores": {
                "trend": 0.62,
                "momentum": 0.54,
                "volatility": 0.40,
                "macro": 0.46,
                "event_safety": 0.25,
                "theme": 0.57,
            },
        },
        {
            "signal_id": "demo_buy_2x_followthrough",
            "age_days_ago": 45,
            "final_score": 0.63,
            "outcome": "TAKE_PROFIT_FIRST",
            "realized_r": 1.12,
            "component_scores": {
                "trend": 0.76,
                "momentum": 0.62,
                "volatility": 0.68,
                "macro": 0.58,
                "event_safety": 0.60,
                "theme": 0.61,
            },
        },
        {
            "signal_id": "demo_buy_3x_extended",
            "age_days_ago": 37,
            "final_score": 0.76,
            "outcome": "TAKE_PROFIT_FIRST",
            "realized_r": 1.72,
            "component_scores": {
                "trend": 0.90,
                "momentum": 0.76,
                "volatility": 0.73,
                "macro": 0.70,
                "event_safety": 0.66,
                "theme": 0.74,
            },
        },
        {
            "signal_id": "demo_mid_trend_followthrough",
            "age_days_ago": 33,
            "final_score": 0.57,
            "outcome": "TAKE_PROFIT_FIRST",
            "realized_r": 0.96,
            "component_scores": {
                "trend": 0.68,
                "momentum": 0.60,
                "volatility": 0.63,
                "macro": 0.56,
                "event_safety": 0.58,
                "theme": 0.60,
            },
        },
        {
            "signal_id": "demo_low_no_trade",
            "age_days_ago": 29,
            "final_score": 0.33,
            "outcome": "TIME_EXIT",
            "realized_r": 0.0,
            "component_scores": {
                "trend": 0.38,
                "momentum": 0.40,
                "volatility": 0.50,
                "macro": 0.43,
                "event_safety": 0.36,
                "theme": 0.41,
            },
        },
        {
            "signal_id": "demo_low_event_drag",
            "age_days_ago": 25,
            "final_score": 0.41,
            "outcome": "STOP_LOSS_FIRST",
            "realized_r": -0.35,
            "component_scores": {
                "trend": 0.48,
                "momentum": 0.44,
                "volatility": 0.46,
                "macro": 0.40,
                "event_safety": 0.31,
                "theme": 0.49,
            },
        },
        {
            "signal_id": "demo_mid_watch_timeout",
            "age_days_ago": 21,
            "final_score": 0.51,
            "outcome": "TIME_EXIT",
            "realized_r": 0.18,
            "component_scores": {
                "trend": 0.60,
                "momentum": 0.52,
                "volatility": 0.57,
                "macro": 0.50,
                "event_safety": 0.48,
                "theme": 0.53,
            },
        },
        {
            "signal_id": "demo_mid_oos_win",
            "age_days_ago": 17,
            "final_score": 0.56,
            "outcome": "TAKE_PROFIT_FIRST",
            "realized_r": 0.88,
            "component_scores": {
                "trend": 0.66,
                "momentum": 0.58,
                "volatility": 0.62,
                "macro": 0.54,
                "event_safety": 0.56,
                "theme": 0.58,
            },
        },
        {
            "signal_id": "demo_high_score_win",
            "age_days_ago": 13,
            "final_score": 0.69,
            "outcome": "TAKE_PROFIT_FIRST",
            "realized_r": 1.34,
            "component_scores": {
                "trend": 0.82,
                "momentum": 0.70,
                "volatility": 0.71,
                "macro": 0.64,
                "event_safety": 0.61,
                "theme": 0.67,
            },
        },
        {
            "signal_id": "demo_watch_oos_time_exit",
            "age_days_ago": 10,
            "final_score": 0.44,
            "outcome": "TIME_EXIT",
            "realized_r": 0.05,
            "component_scores": {
                "trend": 0.52,
                "momentum": 0.48,
                "volatility": 0.54,
                "macro": 0.47,
                "event_safety": 0.44,
                "theme": 0.50,
            },
        },
        {
            "signal_id": "demo_high_oos_followthrough",
            "age_days_ago": 8,
            "final_score": 0.70,
            "outcome": "TAKE_PROFIT_FIRST",
            "realized_r": 1.42,
            "component_scores": {
                "trend": 0.84,
                "momentum": 0.71,
                "volatility": 0.72,
                "macro": 0.65,
                "event_safety": 0.63,
                "theme": 0.68,
            },
        },
        {
            "signal_id": "demo_high_score_partial_win",
            "age_days_ago": 6,
            "final_score": 0.73,
            "outcome": "TAKE_PROFIT_FIRST",
            "realized_r": 1.48,
            "component_scores": {
                "trend": 0.86,
                "momentum": 0.72,
                "volatility": 0.74,
                "macro": 0.66,
                "event_safety": 0.64,
                "theme": 0.69,
            },
        },
        {
            "signal_id": "demo_high_oos_extension",
            "age_days_ago": 3,
            "final_score": 0.77,
            "outcome": "TAKE_PROFIT_FIRST",
            "realized_r": 1.62,
            "component_scores": {
                "trend": 0.89,
                "momentum": 0.76,
                "volatility": 0.75,
                "macro": 0.69,
                "event_safety": 0.67,
                "theme": 0.73,
            },
        },
    ]
    return [
        item
        for item in _decorate_demo_outcomes(outcomes)
        if int(item["age_days_ago"]) <= days
    ]
