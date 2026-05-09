"""Pure Python technical indicator calculations."""

from __future__ import annotations

from typing import Any

from halo_swing_mcp.providers import get_market_data_provider


def _round(value: float | None, digits: int = 4) -> float | None:
    if value is None:
        return None
    return round(value, digits)


def simple_moving_average(values: list[float], period: int) -> float | None:
    if len(values) < period:
        return None
    return sum(values[-period:]) / period


def rsi(values: list[float], period: int = 14) -> float | None:
    if len(values) <= period:
        return None

    gains: list[float] = []
    losses: list[float] = []
    for previous, current in zip(values[-period - 1 : -1], values[-period:]):
        change = current - previous
        gains.append(max(change, 0))
        losses.append(abs(min(change, 0)))

    average_gain = sum(gains) / period
    average_loss = sum(losses) / period
    if average_loss == 0:
        return 100.0
    rs = average_gain / average_loss
    return 100 - 100 / (1 + rs)


def true_ranges(bars: list[dict[str, Any]]) -> list[float]:
    ranges: list[float] = []
    previous_close = float(bars[0]["close"])
    for bar in bars[1:]:
        high = float(bar["high"])
        low = float(bar["low"])
        ranges.append(
            max(
                high - low,
                abs(high - previous_close),
                abs(low - previous_close),
            )
        )
        previous_close = float(bar["close"])
    return ranges


def atr(bars: list[dict[str, Any]], period: int = 14) -> float | None:
    ranges = true_ranges(bars)
    if len(ranges) < period:
        return None
    return sum(ranges[-period:]) / period


def dmi_adx(bars: list[dict[str, Any]], period: int = 14) -> dict[str, float | None]:
    if len(bars) <= period + 1:
        return {"plus_di": None, "minus_di": None, "adx": None}

    plus_dm: list[float] = []
    minus_dm: list[float] = []
    tr_values: list[float] = []
    dx_values: list[float] = []

    for previous, current in zip(bars[:-1], bars[1:]):
        up_move = float(current["high"]) - float(previous["high"])
        down_move = float(previous["low"]) - float(current["low"])
        plus_dm.append(up_move if up_move > down_move and up_move > 0 else 0.0)
        minus_dm.append(down_move if down_move > up_move and down_move > 0 else 0.0)
        tr_values.append(
            max(
                float(current["high"]) - float(current["low"]),
                abs(float(current["high"]) - float(previous["close"])),
                abs(float(current["low"]) - float(previous["close"])),
            )
        )

    for index in range(period, len(tr_values) + 1):
        tr_sum = sum(tr_values[index - period : index])
        plus_di = 100 * sum(plus_dm[index - period : index]) / tr_sum if tr_sum else 0
        minus_di = 100 * sum(minus_dm[index - period : index]) / tr_sum if tr_sum else 0
        denominator = plus_di + minus_di
        dx = 100 * abs(plus_di - minus_di) / denominator if denominator else 0
        dx_values.append(dx)

    latest_tr = sum(tr_values[-period:])
    latest_plus_di = 100 * sum(plus_dm[-period:]) / latest_tr if latest_tr else 0
    latest_minus_di = 100 * sum(minus_dm[-period:]) / latest_tr if latest_tr else 0
    latest_adx = sum(dx_values[-period:]) / period if len(dx_values) >= period else None

    return {
        "plus_di": latest_plus_di,
        "minus_di": latest_minus_di,
        "adx": latest_adx,
    }


def detect_recent_gaps(bars: list[dict[str, Any]], lookback: int = 20) -> list[dict[str, Any]]:
    gaps: list[dict[str, Any]] = []
    recent = bars[-lookback:]
    for previous, current in zip(recent[:-1], recent[1:]):
        previous_high = float(previous["high"])
        previous_low = float(previous["low"])
        current_high = float(current["high"])
        current_low = float(current["low"])
        if previous_high < current_low:
            gaps.append(
                {
                    "type": "gap_up",
                    "timestamp": current["timestamp"],
                    "lower": round(previous_high, 4),
                    "upper": round(current_low, 4),
                }
            )
        elif previous_low > current_high:
            gaps.append(
                {
                    "type": "gap_down",
                    "timestamp": current["timestamp"],
                    "lower": round(current_high, 4),
                    "upper": round(previous_low, 4),
                }
            )
    return gaps[-3:]


def calculate_indicator_payload(
    symbol: str,
    timeframe: str = "1d",
    periods: int = 220,
) -> dict[str, Any]:
    """Calculate deterministic indicators from OHLCV bars."""

    provider = get_market_data_provider()
    normalized = symbol.upper()
    underlying, leverage = provider.resolve_asset(normalized)
    indicator_symbol = underlying if leverage > 1 else normalized
    bars = list(provider.ohlcv(indicator_symbol, periods))
    closes = [float(bar["close"]) for bar in bars]
    latest_close = closes[-1]
    previous_close = closes[-2]
    atr_14 = atr(bars, 14)
    dmi = dmi_adx(bars, 14)
    ma_10 = simple_moving_average(closes, 10)
    ma_20 = simple_moving_average(closes, 20)
    ma_50 = simple_moving_average(closes, 50)
    ma_200 = simple_moving_average(closes, 200)
    support = min(closes[-20:])
    resistance = max(closes[-20:])
    ma_20_previous = simple_moving_average(closes[:-5], 20)
    ma_20_slope = None
    if ma_20 is not None and ma_20_previous is not None:
        ma_20_slope = (ma_20 - ma_20_previous) / ma_20_previous

    trend_state = "uptrend"
    if ma_50 is not None and latest_close < ma_50:
        trend_state = "pullback"
    if ma_200 is not None and latest_close < ma_200:
        trend_state = "risk_off"

    return {
        "symbol": normalized,
        "indicator_symbol": indicator_symbol,
        "timeframe": timeframe,
        "data_mode": provider.data_mode,
        "live_data_required": provider.live_data_required,
        "latest_bar": bars[-1],
        "change_pct_1d": _round((latest_close / previous_close - 1) * 100),
        "rsi_14": _round(rsi(closes, 14)),
        "plus_di_14": _round(dmi["plus_di"]),
        "minus_di_14": _round(dmi["minus_di"]),
        "adx_14": _round(dmi["adx"]),
        "atr_14": _round(atr_14),
        "atr_percent": _round(100 * atr_14 / latest_close if atr_14 else None),
        "ma_10": _round(ma_10),
        "ma_20": _round(ma_20),
        "ma_50": _round(ma_50),
        "ma_200": _round(ma_200),
        "ma_20_slope": _round(ma_20_slope, 6),
        "support_20": _round(support),
        "resistance_20": _round(resistance),
        "recent_gaps": detect_recent_gaps(bars),
        "trend_state": trend_state,
    }
