"""Swing scoring, guide generation, position review, and feedback tools."""

from __future__ import annotations

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

    normalized = asset.upper()
    underlying, leverage = resolve_asset(normalized)
    indicators = calculate_indicator_payload(underlying)
    macro = get_macro_snapshot()
    events = get_event_calendar(days=14)
    news = get_news_bundle(topic="all")
    config = get_strategy_config()
    components = _component_scores(underlying, indicators, macro, events, news)
    final_score = _weighted_score(components, config["weights"])
    action = _action_for_score(final_score, leverage, components, indicators, config)
    references = _risk_references(indicators, config)
    confidence = _confidence(final_score, components)
    risk_warnings = _risk_warnings(components, events)

    if risk_warnings and action in {TradeAction.BUY_2X, TradeAction.BUY_3X}:
        action = TradeAction.BUY_WATCH

    return {
        "signal_id": f"sig_fixture_{AS_OF[:10].replace('-', '')}_{normalized.lower()}",
        "run_id": f"run_fixture_{AS_OF[:10].replace('-', '')}_swing",
        "created_at": AS_OF,
        "asset": normalized,
        "underlying": underlying,
        "leverage": leverage,
        "timeframe": timeframe,
        "action": action.value,
        "action_label": ACTION_LABELS[action],
        "final_score": round(final_score, 4),
        "confidence": confidence,
        "component_scores": components,
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
    return {
        "as_of": AS_OF,
        "asset": signal["asset"],
        "underlying": signal["underlying"],
        "action": signal["action"],
        "confidence": signal["confidence"],
        "guide": {
            "entry": signal["entry"],
            "stop_conditions": signal["stop"],
            "take_profit_conditions": signal["take_profit"],
            "invalidation_conditions": signal["invalidation"],
            "position_sizing_note": (
                "Size by max loss to stop, not by confidence. Leveraged ETFs are "
                "swing tactics and should not be treated as long-term holdings."
            ),
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
    entry = float(entry_price) if entry_price is not None else float(reference) * 0.97
    current = float(current_price) if current_price is not None else float(reference)
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

    return {
        "as_of": AS_OF,
        "asset": asset.upper(),
        "underlying": underlying,
        "entry_price": round(entry, 4),
        "current_price": round(current, 4),
        "size": size,
        "unrealized_return_pct": round(pnl_pct * 100, 4),
        "action": action.value,
        "position_state": position_state,
        "rationale": _position_rationale(position_state, signal, pnl_pct),
        "stop_conditions": signal["stop"],
        "take_profit_conditions": signal["take_profit"],
        "live_data_required": False,
    }


def evaluate_score_performance(
    signals: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Evaluate score calibration and rough realized-R summary."""

    sample = signals or _demo_signal_outcomes()
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

    return {
        "as_of": AS_OF,
        "sample_size": len(sample),
        "avg_realized_r": round(total_realized_r / len(sample), 4) if sample else 0.0,
        "stop_loss_first_count": stop_loss_first,
        "score_bins": bins,
        "calibration_note": (
            "Fixture evaluation expects higher score bins to produce stronger "
            "realized-R before any challenger is promoted."
        ),
        "live_data_required": False,
    }


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
    validation = validate_strategy_config(challenger)
    challenger["config_hash"] = validation["config_hash"]
    return {
        "as_of": AS_OF,
        "champion_config_hash": champion["config_hash"],
        "challenger": challenger,
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
    for item in _demo_signal_outcomes():
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
    news_strength = float(news["average_strength"])
    theme = min(1.0, (theme_score + news_strength) / 2)

    return {
        "trend": round(max(0.0, min(1.0, trend)), 4),
        "momentum": round(momentum, 4),
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
) -> list[str]:
    warnings: list[str] = []
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


def _demo_signal_outcomes() -> list[dict[str, Any]]:
    return [
        {
            "signal_id": "demo_low_wait",
            "final_score": 0.31,
            "outcome": "TIME_EXIT",
            "realized_r": 0.02,
        },
        {
            "signal_id": "demo_watch",
            "final_score": 0.46,
            "outcome": "STOP_LOSS_FIRST",
            "realized_r": -1.0,
        },
        {
            "signal_id": "demo_buy_2x",
            "final_score": 0.59,
            "outcome": "TAKE_PROFIT_FIRST",
            "realized_r": 1.28,
        },
        {
            "signal_id": "demo_buy_3x",
            "final_score": 0.72,
            "outcome": "TAKE_PROFIT_FIRST",
            "realized_r": 1.55,
        },
    ]
