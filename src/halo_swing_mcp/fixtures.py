"""Deterministic offline market, macro, event, and evidence fixtures."""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from functools import lru_cache
from typing import Any


AS_OF = "2026-05-08T20:00:00Z"
AS_OF_DATE = date(2026, 5, 8)
SUPPORTED_TIMEFRAMES = ("1d", "4h", "1h")


@dataclass(frozen=True)
class SymbolProfile:
    symbol: str
    base_price: float
    drift: float
    cycle: float
    volume: int
    theme_score: float
    phase: float


UNDERLYING_PROFILES: dict[str, SymbolProfile] = {
    "QQQ": SymbolProfile("QQQ", 406.0, 0.0018, 0.019, 54_000_000, 0.67, 0.0),
    "SPY": SymbolProfile("SPY", 501.0, 0.0011, 0.012, 71_000_000, 0.55, 0.8),
    "SMH": SymbolProfile("SMH", 207.0, 0.0023, 0.025, 12_000_000, 0.73, 1.4),
    "SOXX": SymbolProfile("SOXX", 178.0, 0.0020, 0.024, 6_000_000, 0.71, 1.8),
    "BTC": SymbolProfile("BTC", 92_000.0, 0.0015, 0.030, 0, 0.58, 2.1),
}

ASSET_UNDERLYING: dict[str, tuple[str, int]] = {
    "QLD": ("QQQ", 2),
    "TQQQ": ("QQQ", 3),
    "SSO": ("SPY", 2),
    "UPRO": ("SPY", 3),
    "SOXL": ("SMH", 3),
    "BTC": ("BTC", 1),
    "QQQ": ("QQQ", 1),
    "SPY": ("SPY", 1),
    "SMH": ("SMH", 1),
    "SOXX": ("SOXX", 1),
}

LEVERAGED_BASE_PRICE: dict[str, float] = {
    "QLD": 92.0,
    "TQQQ": 64.0,
    "SSO": 84.0,
    "UPRO": 73.0,
    "SOXL": 38.0,
}

MACRO_FIXTURE: dict[str, Any] = {
    "as_of": AS_OF,
    "data_mode": "fixture",
    "live_data_required": False,
    "macro_score": 0.64,
    "risk_score": 0.28,
    "indicators": {
        "vix": {"value": 17.4, "change_5d": -1.8, "state": "contained"},
        "vxn": {"value": 21.6, "change_5d": -2.1, "state": "falling"},
        "dxy": {"value": 104.2, "change_5d": -0.3, "state": "stable"},
        "us_2y": {"value": 4.76, "change_5d_bps": -5.0, "state": "easing"},
        "us_10y": {"value": 4.48, "change_5d_bps": -3.0, "state": "stable"},
        "oil_wti": {"value": 81.2, "change_5d": 1.1, "state": "firm"},
    },
    "summary": "Volatility is contained and rates are not moving against risk assets.",
}

EVENT_FIXTURES: list[dict[str, Any]] = [
    {
        "event_id": "evt_20260512_cpi",
        "event_type": "CPI",
        "title": "US CPI release",
        "scheduled_at": "2026-05-12T12:30:00Z",
        "risk_level": "high",
        "risk_score": 0.72,
        "blocks_3x_before_hours": 24,
        "blocks_2x_before_hours": 4,
    },
    {
        "event_id": "evt_20260514_nvidia_earnings",
        "event_type": "EARNINGS",
        "title": "Large-cap semiconductor earnings window",
        "scheduled_at": "2026-05-14T20:00:00Z",
        "risk_level": "medium",
        "risk_score": 0.46,
        "blocks_3x_before_hours": 12,
        "blocks_2x_before_hours": 0,
    },
    {
        "event_id": "evt_20260515_nfp",
        "event_type": "NFP",
        "title": "US labor market report window",
        "scheduled_at": "2026-05-15T12:30:00Z",
        "risk_level": "high",
        "risk_score": 0.64,
        "blocks_3x_before_hours": 24,
        "blocks_2x_before_hours": 4,
    },
    {
        "event_id": "evt_20260520_fomc_minutes",
        "event_type": "FOMC",
        "title": "FOMC minutes",
        "scheduled_at": "2026-05-20T18:00:00Z",
        "risk_level": "medium",
        "risk_score": 0.42,
        "blocks_3x_before_hours": 24,
        "blocks_2x_before_hours": 4,
    },
]

NEWS_FIXTURES: list[dict[str, Any]] = [
    {
        "evidence_id": "ev_fixture_fed_001",
        "category": "macro_policy",
        "source": "fixture:fed",
        "source_group": "fed",
        "modality": "pdf_summary",
        "observed_at": "2026-05-08T16:10:00Z",
        "asset_scope": ["QQQ", "SPY", "TQQQ", "QLD", "BTC"],
        "bias": "slightly_bullish",
        "strength": 0.58,
        "confidence": 0.74,
        "summary": "Policy tone is not loose, but volatility and rates are not worsening.",
        "buy_impact": "allow_2x",
        "sell_impact": "trim_if_yields_break_higher",
        "invalidating_condition": "DXY and yields rise together for two sessions.",
        "artifact_ref": {
            "ref_type": "PDF",
            "ref": "https://example.invalid/evidence/fed-policy-summary.pdf",
            "metadata": {
                "description": "Fixture macro policy PDF summary",
                "portable": True,
            },
        },
    },
    {
        "evidence_id": "ev_fixture_ai_001",
        "category": "ai_semiconductor",
        "source": "fixture:semiconductor_theme",
        "source_group": "ai_semiconductor",
        "modality": "news_text",
        "observed_at": "2026-05-08T17:25:00Z",
        "asset_scope": ["SMH", "SOXX", "SOXL", "QQQ", "TQQQ"],
        "bias": "bullish",
        "strength": 0.66,
        "confidence": 0.70,
        "summary": "Semiconductor leadership remains constructive, but earnings risk is near.",
        "buy_impact": "support_2x_or_watch_3x",
        "sell_impact": "trim_into_earnings_spike",
        "invalidating_condition": "Semiconductor breadth loses the prior swing low.",
        "artifact_ref": {
            "ref_type": "NEWS",
            "ref": "https://example.invalid/evidence/semiconductor-theme",
            "metadata": {
                "description": "Fixture semiconductor theme evidence",
                "portable": True,
            },
        },
    },
    {
        "evidence_id": "ev_fixture_oil_001",
        "category": "geopolitical_oil",
        "source": "fixture:oil_risk",
        "source_group": "oil_market",
        "modality": "news_text",
        "observed_at": "2026-05-08T18:00:00Z",
        "asset_scope": ["SPY", "QQQ", "BTC"],
        "bias": "neutral_to_bearish",
        "strength": 0.35,
        "confidence": 0.63,
        "summary": "Oil is firm but not yet a broad risk-off shock.",
        "buy_impact": "watch",
        "sell_impact": "trim_if_oil_spikes",
        "invalidating_condition": "WTI breaks higher with VIX expansion.",
        "artifact_ref": {
            "ref_type": "NEWS",
            "ref": "https://example.invalid/evidence/oil-risk",
            "metadata": {
                "description": "Fixture geopolitical oil evidence",
                "portable": True,
            },
        },
    },
    {
        "evidence_id": "ev_fixture_treasury_001",
        "category": "macro_policy",
        "source": "fixture:treasury",
        "source_group": "treasury",
        "modality": "news_text",
        "observed_at": "2026-05-08T18:15:00Z",
        "asset_scope": ["QQQ", "SPY", "TQQQ", "QLD", "BTC"],
        "bias": "neutral",
        "strength": 0.52,
        "confidence": 0.66,
        "summary": "Treasury issuance risk is monitored but not forcing a risk-off block.",
        "buy_impact": "context_only",
        "sell_impact": "watch_if_yields_break_higher",
        "invalidating_condition": "Auction tail pushes yields higher with DXY strength.",
        "artifact_ref": {
            "ref_type": "NEWS",
            "ref": "https://example.invalid/evidence/treasury-issuance",
            "metadata": {
                "description": "Fixture Treasury policy evidence",
                "portable": True,
            },
        },
    },
    {
        "evidence_id": "ev_fixture_white_house_001",
        "category": "macro_policy",
        "source": "fixture:white_house",
        "source_group": "white_house",
        "modality": "news_text",
        "observed_at": "2026-05-08T18:20:00Z",
        "asset_scope": ["QQQ", "SPY", "TQQQ", "QLD"],
        "bias": "neutral",
        "strength": 0.50,
        "confidence": 0.62,
        "summary": "White House policy headlines are monitored for tariff or fiscal shocks.",
        "buy_impact": "context_only",
        "sell_impact": "trim_if_policy_shock",
        "invalidating_condition": "Policy headline raises inflation or margin pressure.",
        "artifact_ref": {
            "ref_type": "NEWS",
            "ref": "https://example.invalid/evidence/white-house-policy",
            "metadata": {
                "description": "Fixture White House policy evidence",
                "portable": True,
            },
        },
    },
    {
        "evidence_id": "ev_fixture_eia_001",
        "category": "energy_policy",
        "source": "fixture:eia",
        "source_group": "eia",
        "modality": "news_text",
        "observed_at": "2026-05-08T18:25:00Z",
        "asset_scope": ["SPY", "QQQ", "BTC"],
        "bias": "neutral_to_bearish",
        "strength": 0.54,
        "confidence": 0.64,
        "summary": "EIA energy context is watched for oil inflation pressure.",
        "buy_impact": "watch",
        "sell_impact": "trim_if_energy_shock",
        "invalidating_condition": "Oil inventory shock combines with VIX expansion.",
        "artifact_ref": {
            "ref_type": "NEWS",
            "ref": "https://example.invalid/evidence/eia-energy-context",
            "metadata": {
                "description": "Fixture EIA energy evidence",
                "portable": True,
            },
        },
    },
    {
        "evidence_id": "ev_fixture_iran_001",
        "category": "geopolitical_oil",
        "source": "fixture:iran_hormuz",
        "source_group": "iran_hormuz",
        "modality": "news_text",
        "observed_at": "2026-05-08T18:30:00Z",
        "asset_scope": ["SPY", "QQQ", "BTC"],
        "bias": "neutral_to_bearish",
        "strength": 0.56,
        "confidence": 0.61,
        "summary": "Iran/Hormuz risk is monitored for oil shock transmission.",
        "buy_impact": "watch",
        "sell_impact": "trim_if_oil_or_vix_spikes",
        "invalidating_condition": "Shipping risk creates a sustained oil volatility spike.",
        "artifact_ref": {
            "ref_type": "NEWS",
            "ref": "https://example.invalid/evidence/iran-hormuz-risk",
            "metadata": {
                "description": "Fixture Iran/Hormuz risk evidence",
                "portable": True,
            },
        },
    },
]


def utc_now_fixture() -> str:
    """Return the deterministic fixture clock."""

    return AS_OF


def resolve_asset(asset: str) -> tuple[str, int]:
    """Return the underlying symbol and leverage multiplier for an asset."""

    normalized = asset.upper()
    if normalized not in ASSET_UNDERLYING:
        raise ValueError(f"unsupported asset: {asset}")
    return ASSET_UNDERLYING[normalized]


def supported_assets() -> list[str]:
    return sorted(ASSET_UNDERLYING)


def supported_timeframes() -> list[str]:
    return list(SUPPORTED_TIMEFRAMES)


def validate_timeframe(timeframe: str) -> str:
    normalized = timeframe.lower()
    if normalized not in SUPPORTED_TIMEFRAMES:
        supported = ", ".join(SUPPORTED_TIMEFRAMES)
        raise ValueError(f"unsupported timeframe: {timeframe}; supported: {supported}")
    return normalized


@lru_cache(maxsize=64)
def generate_ohlcv(
    symbol: str,
    periods: int = 220,
    timeframe: str = "1d",
) -> tuple[dict[str, Any], ...]:
    """Generate deterministic OHLCV bars for offline harnesses."""

    normalized = symbol.upper()
    normalized_timeframe = validate_timeframe(timeframe)
    if normalized in UNDERLYING_PROFILES:
        return tuple(
            _generate_underlying_ohlcv(
                UNDERLYING_PROFILES[normalized],
                periods,
                normalized_timeframe,
            )
        )

    underlying, leverage = resolve_asset(normalized)
    base = LEVERAGED_BASE_PRICE.get(normalized)
    if base is None:
        raise ValueError(f"unsupported leveraged asset: {symbol}")
    underlying_bars = generate_ohlcv(underlying, periods, normalized_timeframe)
    return tuple(_generate_leveraged_ohlcv(normalized, base, leverage, underlying_bars))


def _generate_underlying_ohlcv(
    profile: SymbolProfile,
    periods: int,
    timeframe: str,
) -> list[dict[str, Any]]:
    start = AS_OF_DATE - timedelta(days=periods - 1)
    bars: list[dict[str, Any]] = []
    previous_close = profile.base_price
    timeframe_scale = {"1d": 1.0, "4h": 0.45, "1h": 0.22}[timeframe]
    volume_scale = {"1d": 1.0, "4h": 0.18, "1h": 0.055}[timeframe]

    for index in range(periods):
        current_date = start + timedelta(days=index)
        trend = 1 + profile.drift * index * timeframe_scale
        cycle = profile.cycle * math.sin(index / 6 + profile.phase)
        slower_cycle = profile.cycle * 0.55 * math.sin(index / 17 + profile.phase / 2)
        pullback = -0.035 * math.exp(-((periods - index - 19) / 8) ** 2)
        rebound = 0.020 * math.exp(-((periods - index - 6) / 7) ** 2)
        close = profile.base_price * (trend + cycle + slower_cycle + pullback + rebound)
        open_price = previous_close * (1 + 0.002 * math.sin(index / 3 + profile.phase))
        high = max(open_price, close) * (1 + 0.005 + abs(math.sin(index)) * 0.003)
        low = min(open_price, close) * (1 - 0.005 - abs(math.cos(index)) * 0.003)
        volume = int(
            profile.volume
            * volume_scale
            * (1 + 0.08 * math.sin(index / 5 + profile.phase))
        )
        bars.append(
            {
                "timestamp": _bar_timestamp(current_date, index, periods, timeframe),
                "timeframe": timeframe,
                "open": round(open_price, 4),
                "high": round(high, 4),
                "low": round(low, 4),
                "close": round(close, 4),
                "volume": max(volume, 0),
            }
        )
        previous_close = close

    return bars


def _bar_timestamp(
    current_date: date,
    index: int,
    periods: int,
    timeframe: str,
) -> str:
    if timeframe == "1d":
        return current_date.isoformat()

    as_of_dt = datetime.fromisoformat(AS_OF.replace("Z", "+00:00"))
    hours = {"4h": 4, "1h": 1}[timeframe]
    timestamp = as_of_dt - timedelta(hours=hours * (periods - index - 1))
    return timestamp.isoformat().replace("+00:00", "Z")


def _generate_leveraged_ohlcv(
    symbol: str,
    base_price: float,
    leverage: int,
    underlying_bars: tuple[dict[str, Any], ...],
) -> list[dict[str, Any]]:
    bars: list[dict[str, Any]] = []
    previous_underlying_close = float(underlying_bars[0]["close"])
    previous_close = base_price

    for bar in underlying_bars:
        underlying_close = float(bar["close"])
        underlying_return = underlying_close / previous_underlying_close - 1
        volatility_drag = 0.00025 * max(leverage - 1, 0)
        close = max(previous_close * (1 + leverage * underlying_return - volatility_drag), 1)
        open_price = previous_close
        intraday_range = abs(leverage * underlying_return) + 0.012
        high = max(open_price, close) * (1 + intraday_range / 2)
        low = min(open_price, close) * (1 - intraday_range / 2)
        bars.append(
            {
                "timestamp": bar["timestamp"],
                "timeframe": bar["timeframe"],
                "open": round(open_price, 4),
                "high": round(high, 4),
                "low": round(low, 4),
                "close": round(close, 4),
                "volume": 0,
            }
        )
        previous_underlying_close = underlying_close
        previous_close = close

    return bars


def future_price_path(symbol: str, days: int = 10) -> list[float]:
    """Return a deterministic future path for labeler harnesses."""

    bars = generate_ohlcv(symbol, 240)
    last_close = float(bars[-1]["close"])
    path: list[float] = []
    for offset in range(1, days + 1):
        move = 0.008 * offset + 0.006 * math.sin(offset / 2)
        path.append(round(last_close * (1 + move), 4))
    return path


def events_within_days(days: int) -> list[dict[str, Any]]:
    cutoff = datetime.combine(AS_OF_DATE + timedelta(days=days), datetime.min.time())
    cutoff = cutoff.replace(tzinfo=timezone.utc)
    events = []
    for event in EVENT_FIXTURES:
        scheduled_at = datetime.fromisoformat(
            event["scheduled_at"].replace("Z", "+00:00")
        )
        if scheduled_at <= cutoff:
            events.append(dict(event))
    return events
