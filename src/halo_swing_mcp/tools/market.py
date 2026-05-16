"""Market, macro, event, news, indicator, and chart tools."""

from __future__ import annotations

import struct
import zlib
from datetime import datetime, timezone
from math import isfinite
from pathlib import Path
from typing import Any

from halo_swing_mcp.config import get_settings
from halo_swing_mcp.contracts import DataFreshnessStatus
from halo_swing_mcp.indicators import calculate_indicator_payload
from halo_swing_mcp.providers import get_market_data_provider


ARTIFACT_DIR_ENV = "HALO_SWING_ARTIFACT_DIR"
DOCUMENT_EVIDENCE_SCHEMA_VERSION = "document_evidence_card.v1"
DOCUMENT_SUMMARY_MAX_CHARS = 900
MARKET_SNAPSHOT_CORE_ASSETS = ["QQQ", "SPY", "SMH", "SOXX", "BTC"]
MARKET_SNAPSHOT_FIELDS = [
    "symbol",
    "underlying",
    "leverage",
    "timeframe",
    "last_close",
    "change_pct_1d",
    "judgment_basis",
    "trend_state",
    "rsi_14",
    "ma_20",
    "ma_50",
    "atr_percent",
]
REQUIRED_EVENT_POLICY_TYPES = ["CPI", "FOMC", "NFP", "EARNINGS"]
REQUIRED_NEWS_SOURCE_GROUPS = [
    "fed",
    "treasury",
    "white_house",
    "eia",
    "iran_hormuz",
    "ai_semiconductor",
]
PROVIDER_SMOKE_ERROR_SCHEMA_VERSION = "provider_smoke_error.v1"


def get_market_snapshot(symbols: list[str] | None = None) -> dict[str, Any]:
    """Return deterministic market trend snapshots for supported assets."""

    provider = get_market_data_provider()
    requested = _normalize_symbol_list(symbols)
    snapshots: list[dict[str, Any]] = []
    try:
        for symbol in requested:
            indicators = calculate_indicator_payload(symbol)
            underlying, leverage = provider.resolve_asset(symbol)
            asset_bars = provider.ohlcv(
                symbol,
                220,
                timeframe=indicators["timeframe"],
            )
            latest_asset_close = asset_bars[-1]["close"]
            previous_asset_close = asset_bars[-2]["close"]
            snapshots.append(
                {
                    "symbol": symbol,
                    "underlying": underlying,
                    "leverage": leverage,
                    "timeframe": indicators["timeframe"],
                    "last_close": latest_asset_close,
                    "change_pct_1d": round(
                        (
                            float(latest_asset_close)
                            / float(previous_asset_close)
                            - 1
                        )
                        * 100,
                        4,
                    ),
                    "judgment_basis": indicators["indicator_symbol"],
                    "trend_state": indicators["trend_state"],
                    "rsi_14": indicators["rsi_14"],
                    "ma_20": indicators["ma_20"],
                    "ma_50": indicators["ma_50"],
                    "atr_percent": indicators["atr_percent"],
                }
            )
    except Exception as exc:
        if not _provider_smoke_error_payload_enabled(
            provider,
            "PolygonMarketDataProvider",
        ):
            raise
        return _market_snapshot_provider_exception_payload(provider, requested, exc)

    supported_assets = provider.supported_assets()
    supported_timeframes = provider.supported_timeframes()
    live_data_required = provider.live_data_required
    contract = {
        "schema_version": "market_snapshot.v1",
        "core_assets": MARKET_SNAPSHOT_CORE_ASSETS,
        "required_snapshot_fields": MARKET_SNAPSHOT_FIELDS,
        "data_mode": provider.data_mode,
        "feature_store_persistence": False,
        "feature_store_gate": "MIGRATION_GO_AND_REPOSITORY_GO",
        "network_call": live_data_required,
        "live_data_required": live_data_required,
    }
    guard_checks = [
        {
            "name": "core_assets_supported",
            "passed": all(asset in supported_assets for asset in MARKET_SNAPSHOT_CORE_ASSETS),
        },
        {
            "name": "requested_assets_returned",
            "passed": [snapshot["symbol"] for snapshot in snapshots] == requested,
        },
        {
            "name": "required_fields_present",
            "passed": all(
                all(field in snapshot for field in MARKET_SNAPSHOT_FIELDS)
                for snapshot in snapshots
            ),
        },
        {
            "name": "feature_store_not_persisted",
            "passed": contract["feature_store_persistence"] is False,
        },
        _market_snapshot_live_data_guard_check(live_data_required, contract),
    ]
    return {
        "as_of": provider.as_of,
        "data_mode": provider.data_mode,
        "live_data_required": live_data_required,
        "data_freshness_status": DataFreshnessStatus.FRESH.value,
        "degraded_mode": False,
        "data_warnings": [],
        "supported_assets": supported_assets,
        "supported_timeframes": supported_timeframes,
        "market_snapshot_contract": contract,
        "market_snapshot_guard": {
            "status": "ok" if all(check["passed"] for check in guard_checks) else "conflict",
            "checks": guard_checks,
        },
        "snapshots": snapshots,
    }


def _market_snapshot_live_data_guard_check(
    live_data_required: bool,
    contract: dict[str, Any],
) -> dict[str, Any]:
    if not live_data_required:
        return {
            "name": "no_live_data_required",
            "passed": contract["live_data_required"] is False
            and contract["network_call"] is False,
            "expected": {"live_data_required": False, "network_call": False},
            "actual": {
                "live_data_required": contract["live_data_required"],
                "network_call": contract["network_call"],
            },
        }
    return {
        "name": "live_data_boundary_declared",
        "passed": contract["live_data_required"] is True
        and contract["network_call"] is True,
        "expected": {"live_data_required": True, "network_call": True},
        "actual": {
            "live_data_required": contract["live_data_required"],
            "network_call": contract["network_call"],
        },
    }


def get_macro_snapshot() -> dict[str, Any]:
    """Return deterministic macro state."""

    provider = get_market_data_provider()
    try:
        snapshot = provider.macro_snapshot()
    except Exception as exc:
        if not _provider_smoke_error_payload_enabled(
            provider,
            "FredMacroDataProvider",
        ):
            raise
        return _macro_snapshot_provider_exception_payload(provider, exc)
    indicators = snapshot["indicators"]
    live_data_required = bool(snapshot["live_data_required"])
    contract = {
        "schema_version": "macro_filter.v1",
        "required_indicators": ["vix", "vxn", "dxy", "us_2y", "us_10y", "oil_wti"],
        "change_window": "5d",
        "network_call": live_data_required,
        "live_data_required": live_data_required,
        "policy": (
            "Macro blocks are derived from fixture or configured FRED VIX/VXN, "
            "DXY, rates, and oil change fields."
        ),
    }
    return {
        **snapshot,
        "macro_filter_contract": contract,
        "macro_filter_guard": _macro_filter_guard(contract, indicators),
        "macro_filter_summary": _macro_filter_summary(
            indicators,
            live_data_required=live_data_required,
        ),
    }


def _macro_filter_guard(
    contract: dict[str, Any],
    indicators: dict[str, Any],
) -> dict[str, Any]:
    required_indicators = contract["required_indicators"]
    live_data_required = contract["live_data_required"]
    checks = [
        {
            "name": "required_indicators_present",
            "passed": all(indicator in indicators for indicator in required_indicators),
            "expected": required_indicators,
            "actual": sorted(indicators),
        },
    ]
    if live_data_required:
        checks.extend(
            [
                {
                    "name": "live_data_boundary_declared",
                    "passed": contract["live_data_required"] is True,
                    "expected": True,
                    "actual": contract["live_data_required"],
                },
                {
                    "name": "network_call_declared",
                    "passed": contract["network_call"] is True,
                    "expected": True,
                    "actual": contract["network_call"],
                },
            ]
        )
    else:
        checks.extend(
            [
                {
                    "name": "no_live_data_required",
                    "passed": contract["live_data_required"] is False,
                    "expected": False,
                    "actual": contract["live_data_required"],
                },
                {
                    "name": "no_network_call",
                    "passed": contract["network_call"] is False,
                    "expected": False,
                    "actual": contract["network_call"],
                },
            ]
        )
    return {
        "status": "ok" if all(check["passed"] for check in checks) else "conflict",
        "checks": checks,
    }


def _provider_smoke_error_payload_enabled(
    provider: Any,
    provider_class_name: str,
) -> bool:
    return bool(getattr(provider, "live_data_required", False)) or _provider_chain_has(
        provider,
        provider_class_name,
    )


def _provider_chain_has(provider: Any, provider_class_name: str) -> bool:
    current = provider
    while current is not None:
        if current.__class__.__name__ == provider_class_name:
            return True
        current = getattr(current, "_base_provider", None)
    return False


def _provider_smoke_error_summary(tool: str, exc: Exception) -> dict[str, Any]:
    return {
        "schema_version": PROVIDER_SMOKE_ERROR_SCHEMA_VERSION,
        "tool": tool,
        "exception_type": type(exc).__name__,
        "exception_message_returned": False,
        "url_returned": False,
        "secret_values_returned": False,
    }


def _provider_exception_guard() -> dict[str, Any]:
    checks = [
        {
            "name": "live_data_boundary_declared",
            "passed": True,
            "expected": True,
            "actual": True,
        },
        {
            "name": "network_call_declared",
            "passed": True,
            "expected": True,
            "actual": True,
        },
        {
            "name": "secret_values_not_returned",
            "passed": True,
            "expected": False,
            "actual": False,
        },
        {
            "name": "provider_smoke_completed",
            "passed": False,
            "expected": True,
            "actual": False,
        },
    ]
    return {"status": "conflict", "checks": checks}


def _market_snapshot_provider_exception_payload(
    provider: Any,
    requested: list[str],
    exc: Exception,
) -> dict[str, Any]:
    contract = {
        "schema_version": "market_snapshot.v1",
        "core_assets": MARKET_SNAPSHOT_CORE_ASSETS,
        "required_snapshot_fields": MARKET_SNAPSHOT_FIELDS,
        "data_mode": "live",
        "feature_store_persistence": False,
        "feature_store_gate": "MIGRATION_GO_AND_REPOSITORY_GO",
        "network_call": True,
        "live_data_required": True,
        "secret_values_returned": False,
    }
    return {
        "status": "conflict",
        "as_of": provider.as_of,
        "data_mode": "live",
        "live_data_required": True,
        "data_freshness_status": DataFreshnessStatus.UNKNOWN.value,
        "degraded_mode": True,
        "data_warnings": ["provider_smoke_exception"],
        "supported_assets": provider.supported_assets(),
        "supported_timeframes": provider.supported_timeframes(),
        "requested_symbols": requested,
        "market_snapshot_contract": contract,
        "market_snapshot_guard": _provider_exception_guard(),
        "error_summary": _provider_smoke_error_summary(
            "get_market_snapshot",
            exc,
        ),
        "secret_values_returned": False,
        "snapshots": [],
    }


def _macro_snapshot_provider_exception_payload(
    provider: Any,
    exc: Exception,
) -> dict[str, Any]:
    contract = {
        "schema_version": "macro_filter.v1",
        "required_indicators": ["vix", "vxn", "dxy", "us_2y", "us_10y", "oil_wti"],
        "change_window": "5d",
        "network_call": True,
        "live_data_required": True,
        "secret_values_returned": False,
        "policy": (
            "Macro blocks are derived from configured FRED VIX/VXN, DXY, "
            "rates, and oil change fields."
        ),
    }
    return {
        "status": "conflict",
        "as_of": provider.as_of,
        "data_mode": "live",
        "live_data_required": True,
        "macro_score": None,
        "risk_score": None,
        "indicators": {},
        "summary": "Live macro provider smoke did not complete.",
        "source_policy": {
            "schema_version": "fred_macro_source_policy.v1",
            "provider": "fred",
            "network_call": True,
            "secret_values_returned": False,
        },
        "macro_filter_contract": contract,
        "macro_filter_guard": _provider_exception_guard(),
        "macro_filter_summary": {
            "schema_version": "macro_filter_summary.v1",
            "status": "conflict",
            "risk_triggers": [],
            "blocks_new_longs_now": False,
            "blocks_new_3x_now": False,
            "blocks_new_2x_now": False,
            "indicator_states": {},
            "change_window": "5d",
            "live_data_required": True,
        },
        "error_summary": _provider_smoke_error_summary(
            "get_macro_snapshot",
            exc,
        ),
        "secret_values_returned": False,
    }


def _news_bundle_provider_exception_payload(
    provider: Any,
    normalized_topic: str,
    exc: Exception,
) -> dict[str, Any]:
    return {
        "status": "conflict",
        "as_of": provider.as_of,
        "topic": normalized_topic,
        "data_mode": "live",
        "live_data_required": True,
        "news_source_policy_contract": {
            "schema_version": "news_source_policy.v1",
            "required_source_groups": ["newsapi"],
            "covered_source_groups": [],
            "collection_mode": "live",
            "live_collection_enabled": True,
            "network_call": True,
            "live_data_required": True,
            "secret_values_returned": False,
        },
        "news_source_policy_guard": _provider_exception_guard(),
        "news_score_contract": {
            "schema_version": "news_score.v1",
            "required_scores": [
                "news_score",
                "policy_score",
                "geopolitical_score",
                "ai_semiconductor_theme_score",
            ],
            "required_card_fields": ["bias", "strength", "confidence"],
            "scoring_usage": "score_leverage_swing.component_scores.theme",
            "network_call": True,
            "live_data_required": True,
            "secret_values_returned": False,
        },
        "average_strength": 0.0,
        "news_score": 0.0,
        "policy_score": 0.0,
        "geopolitical_score": 0.0,
        "ai_semiconductor_theme_score": 0.0,
        "modality_counts": {},
        "source_group_counts": {},
        "artifact_refs": [],
        "multimodal_evidence_guard": {
            "status": "conflict",
            "checks": [
                {
                    "name": "provider_smoke_completed",
                    "passed": False,
                    "expected": True,
                    "actual": False,
                }
            ],
        },
        "error_summary": _provider_smoke_error_summary("get_news_bundle", exc),
        "secret_values_returned": False,
        "evidence_cards": [],
    }


def get_event_calendar(days: int = 14) -> dict[str, Any]:
    """Return deterministic event risk calendar."""

    normalized_days = _normalize_positive_days(days)
    provider = get_market_data_provider()
    events = [
        {
            **event,
            "danger_window": _event_danger_window(event, provider.as_of),
        }
        for event in provider.event_calendar(normalized_days)
    ]
    highest_risk = max((event["risk_score"] for event in events), default=0.0)
    covered_event_types = sorted({str(event["event_type"]) for event in events})
    event_policy_contract = {
        "schema_version": "event_policy.v1",
        "required_event_types": REQUIRED_EVENT_POLICY_TYPES,
        "covered_event_types": covered_event_types,
        "buy_restriction_policy": {
            "new_3x_uses": "blocks_3x_before_hours",
            "new_2x_uses": "blocks_2x_before_hours",
            "post_event_watch_minutes": "30-60",
        },
        "network_call": False,
        "live_data_required": False,
    }
    policy_guard_checks = [
        {
            "name": "required_event_types_covered",
            "passed": all(
                event_type in covered_event_types
                for event_type in REQUIRED_EVENT_POLICY_TYPES
            ),
        },
        {
            "name": "danger_window_present",
            "passed": all("danger_window" in event for event in events),
        },
        {
            "name": "pre_event_block_fields_present",
            "passed": all(
                "blocks_3x_before_hours" in event and "blocks_2x_before_hours" in event
                for event in events
            ),
        },
        {
            "name": "no_live_data_required",
            "passed": event_policy_contract["live_data_required"] is False,
        },
        {
            "name": "no_network_call",
            "passed": event_policy_contract["network_call"] is False,
        },
    ]
    return {
        "as_of": provider.as_of,
        "days": normalized_days,
        "data_mode": provider.data_mode,
        "live_data_required": provider.live_data_required,
        "event_policy_contract": event_policy_contract,
        "event_policy_guard": {
            "status": "ok" if all(check["passed"] for check in policy_guard_checks) else "conflict",
            "checks": policy_guard_checks,
        },
        "event_window_contract": {
            "schema_version": "event_danger_window.v1",
            "network_call": False,
            "live_data_required": False,
            "policy": (
                "Pre-event blocks use fixture blocks_3x_before_hours and "
                "blocks_2x_before_hours fields."
            ),
        },
        "event_window_summary": _event_window_summary(events),
        "highest_event_risk": round(highest_risk, 4),
        "events": events,
    }


def get_news_bundle(topic: str = "macro") -> dict[str, Any]:
    """Return deterministic evidence cards for a report topic."""

    normalized_topic = _normalize_topic_identity(topic)
    provider = get_market_data_provider()
    try:
        cards = provider.news_cards(normalized_topic)
    except Exception as exc:
        if not _provider_smoke_error_payload_enabled(
            provider,
            "NewsApiDataProvider",
        ):
            raise
        return _news_bundle_provider_exception_payload(
            provider,
            normalized_topic,
            exc,
        )
    live_collection_enabled = any(card.get("source") == "newsapi" for card in cards)
    collection_mode = "live" if live_collection_enabled else provider.data_mode
    average_strength = _average_strength(cards)
    covered_source_groups = sorted(
        {str(card.get("source_group")) for card in cards if card.get("source_group")}
    )
    required_source_groups = (
        ["newsapi"] if live_collection_enabled else REQUIRED_NEWS_SOURCE_GROUPS
    )
    source_policy_contract = {
        "schema_version": "news_source_policy.v1",
        "required_source_groups": required_source_groups,
        "covered_source_groups": covered_source_groups,
        "collection_mode": collection_mode,
        "live_collection_enabled": live_collection_enabled,
        "network_call": live_collection_enabled,
        "live_data_required": live_collection_enabled,
        "secret_values_returned": False,
    }
    source_policy_guard_checks = [
        {
            "name": "required_source_groups_covered",
            "passed": all(
                source_group in covered_source_groups
                for source_group in required_source_groups
            ),
        },
        {
            "name": "source_group_present_on_cards",
            "passed": all(card.get("source_group") for card in cards),
        },
    ]
    if live_collection_enabled:
        source_policy_guard_checks.extend(
            [
                {
                    "name": "live_collection_explicit",
                    "passed": source_policy_contract["collection_mode"] == "live",
                },
                {
                    "name": "network_call_declared",
                    "passed": source_policy_contract["network_call"] is True,
                },
                {
                    "name": "live_data_boundary_declared",
                    "passed": source_policy_contract["live_data_required"] is True,
                },
                {
                    "name": "secret_values_not_returned",
                    "passed": source_policy_contract["secret_values_returned"]
                    is False,
                },
            ]
        )
    else:
        source_policy_guard_checks.extend(
            [
                {
                    "name": "no_live_collection",
                    "passed": source_policy_contract["live_collection_enabled"]
                    is False,
                },
                {
                    "name": "no_network_call",
                    "passed": source_policy_contract["network_call"] is False,
                },
                {
                    "name": "secret_values_not_returned",
                    "passed": source_policy_contract["secret_values_returned"]
                    is False,
                },
            ]
        )
    return {
        "as_of": provider.as_of,
        "topic": normalized_topic,
        "data_mode": collection_mode,
        "live_data_required": live_collection_enabled or provider.live_data_required,
        "news_source_policy_contract": source_policy_contract,
        "news_source_policy_guard": {
            "status": "ok"
            if all(check["passed"] for check in source_policy_guard_checks)
            else "conflict",
            "checks": source_policy_guard_checks,
        },
        "news_score_contract": {
            "schema_version": "news_score.v1",
            "required_scores": [
                "news_score",
                "policy_score",
                "geopolitical_score",
                "ai_semiconductor_theme_score",
            ],
            "required_card_fields": ["bias", "strength", "confidence"],
            "scoring_usage": "score_leverage_swing.component_scores.theme",
            "network_call": live_collection_enabled,
            "live_data_required": live_collection_enabled,
            "secret_values_returned": False,
        },
        "average_strength": round(average_strength, 4),
        "news_score": round(average_strength, 4),
        "policy_score": _category_strength(cards, {"macro_policy"}),
        "geopolitical_score": _category_strength(
            cards,
            {"energy_policy", "geopolitical_oil"},
        ),
        "ai_semiconductor_theme_score": _category_strength(cards, {"ai_semiconductor"}),
        "modality_counts": _modality_counts(cards),
        "source_group_counts": _source_group_counts(cards),
        "artifact_refs": _evidence_artifact_refs(cards),
        "multimodal_evidence_guard": _multimodal_evidence_guard(cards),
        "evidence_cards": cards,
    }


def _macro_filter_summary(
    indicators: dict[str, Any],
    *,
    live_data_required: bool = False,
) -> dict[str, Any]:
    vix_value = _indicator_value(indicators, "vix")
    vxn_value = _indicator_value(indicators, "vxn")
    dxy_change = _indicator_change(indicators, "dxy")
    oil_change = _indicator_change(indicators, "oil_wti")
    us_2y_change_bps = _indicator_change(indicators, "us_2y", "change_5d_bps")
    us_10y_change_bps = _indicator_change(indicators, "us_10y", "change_5d_bps")

    trigger_checks = {
        "vix_spike": vix_value >= 25 or _indicator_change(indicators, "vix") >= 4,
        "vxn_spike": vxn_value >= 30 or _indicator_change(indicators, "vxn") >= 5,
        "dxy_rising": dxy_change >= 1,
        "front_end_yield_rising": us_2y_change_bps >= 15,
        "long_yield_rising": us_10y_change_bps >= 15,
        "oil_shock_watch": oil_change >= 6,
    }
    risk_triggers = [name for name, triggered in trigger_checks.items() if triggered]
    volatility_shock = trigger_checks["vix_spike"] or trigger_checks["vxn_spike"]
    rate_dollar_shock = (
        trigger_checks["dxy_rising"]
        and (trigger_checks["front_end_yield_rising"] or trigger_checks["long_yield_rising"])
    )
    blocks_longs = volatility_shock and (
        rate_dollar_shock or trigger_checks["oil_shock_watch"]
    )
    blocks_3x = bool(risk_triggers)
    blocks_2x = blocks_longs

    return {
        "schema_version": "macro_filter_summary.v1",
        "risk_triggers": risk_triggers,
        "blocks_new_longs_now": blocks_longs,
        "blocks_new_3x_now": blocks_3x,
        "blocks_new_2x_now": blocks_2x,
        "indicator_states": {
            name: indicators[name]["state"]
            for name in ("vix", "vxn", "dxy", "us_2y", "us_10y", "oil_wti")
        },
        "change_window": "5d",
        "live_data_required": live_data_required,
    }


def _indicator_value(indicators: dict[str, Any], name: str) -> float:
    return float(indicators[name]["value"])


def _indicator_change(
    indicators: dict[str, Any],
    name: str,
    field: str = "change_5d",
) -> float:
    return float(indicators[name].get(field, 0))


def _event_danger_window(event: dict[str, Any], as_of: str) -> dict[str, Any]:
    as_of_dt = datetime.fromisoformat(as_of.replace("Z", "+00:00"))
    scheduled_at = datetime.fromisoformat(str(event["scheduled_at"]).replace("Z", "+00:00"))
    if as_of_dt.tzinfo is None:
        as_of_dt = as_of_dt.replace(tzinfo=timezone.utc)
    if scheduled_at.tzinfo is None:
        scheduled_at = scheduled_at.replace(tzinfo=timezone.utc)
    hours_until_event = (scheduled_at - as_of_dt).total_seconds() / 3600
    blocks_3x_before = float(event.get("blocks_3x_before_hours") or 0)
    blocks_2x_before = float(event.get("blocks_2x_before_hours") or 0)
    blocks_3x_now = 0 <= hours_until_event <= blocks_3x_before
    blocks_2x_now = 0 <= hours_until_event <= blocks_2x_before
    state = "upcoming"
    if blocks_2x_now:
        state = "pre_event_2x_block_window"
    elif blocks_3x_now:
        state = "pre_event_3x_block_window"
    elif hours_until_event < 0:
        state = "past"

    return {
        "schema_version": "event_danger_window.v1",
        "as_of": as_of,
        "hours_until_event": round(hours_until_event, 2),
        "blocks_new_3x_now": blocks_3x_now,
        "blocks_new_2x_now": blocks_2x_now,
        "blocks_3x_before_hours": int(blocks_3x_before),
        "blocks_2x_before_hours": int(blocks_2x_before),
        "state": state,
        "live_data_required": False,
    }


def _event_window_summary(events: list[dict[str, Any]]) -> dict[str, Any]:
    future_events = [
        event
        for event in events
        if float(event["danger_window"]["hours_until_event"]) >= 0
    ]
    next_event = min(
        future_events,
        key=lambda event: float(event["danger_window"]["hours_until_event"]),
        default=None,
    )
    blocked_3x = [
        event["event_id"]
        for event in events
        if event["danger_window"]["blocks_new_3x_now"]
    ]
    blocked_2x = [
        event["event_id"]
        for event in events
        if event["danger_window"]["blocks_new_2x_now"]
    ]
    return {
        "schema_version": "event_danger_window_summary.v1",
        "next_event_id": next_event["event_id"] if next_event else None,
        "next_event_hours_until": (
            next_event["danger_window"]["hours_until_event"] if next_event else None
        ),
        "blocks_new_3x_now": bool(blocked_3x),
        "blocks_new_2x_now": bool(blocked_2x),
        "blocking_3x_event_ids": blocked_3x,
        "blocking_2x_event_ids": blocked_2x,
        "live_data_required": False,
    }


def create_document_evidence_card(
    summary: str,
    artifact_ref: str,
    ref_type: str = "PDF",
    modality: str = "pdf_summary",
    evidence_id: str = "manual_document_summary",
    category: str = "manual_document",
    source: str = "manual:document_summary",
    observed_at: str | None = None,
    asset_scope: list[str] | None = None,
    bias: str = "neutral",
    strength: float = 0.5,
    confidence: float = 0.5,
    buy_impact: str = "context_only",
    sell_impact: str = "context_only",
    invalidating_condition: str = "Document summary becomes stale or contradicted.",
) -> dict[str, Any]:
    """Normalize a caller-supplied document summary into one evidence card."""

    provider = get_market_data_provider()
    normalized_summary = _normalize_required_text(summary, "summary")
    normalized_ref_type = _normalize_required_text(ref_type, "ref_type").upper()
    normalized_artifact_ref = _normalize_required_text(artifact_ref, "artifact_ref")
    normalized_modality = _normalize_required_text(modality, "modality")
    normalized_evidence_id = _normalize_required_text(evidence_id, "evidence_id")
    normalized_category = _normalize_required_text(category, "category")
    normalized_source = _normalize_required_text(source, "source")
    normalized_observed_at = _normalize_optional_text(observed_at, "observed_at")
    normalized_asset_scope = _normalize_asset_scope(asset_scope)
    normalized_bias = _normalize_required_text(bias, "bias")
    normalized_buy_impact = _normalize_required_text(buy_impact, "buy_impact")
    normalized_sell_impact = _normalize_required_text(sell_impact, "sell_impact")
    normalized_invalidating_condition = _normalize_required_text(
        invalidating_condition,
        "invalidating_condition",
    )
    normalized_ref = _document_artifact_ref(
        ref_type=normalized_ref_type,
        ref=normalized_artifact_ref,
    )
    bounded_summary = _bounded_text(normalized_summary, DOCUMENT_SUMMARY_MAX_CHARS)
    evidence_card = {
        "evidence_id": normalized_evidence_id,
        "category": normalized_category,
        "source": normalized_source,
        "modality": normalized_modality,
        "observed_at": normalized_observed_at or provider.as_of,
        "asset_scope": normalized_asset_scope,
        "bias": normalized_bias,
        "strength": _clamped_score(strength, "strength"),
        "confidence": _clamped_score(confidence, "confidence"),
        "summary": bounded_summary,
        "summary_truncated": len(normalized_summary) > DOCUMENT_SUMMARY_MAX_CHARS,
        "buy_impact": normalized_buy_impact,
        "sell_impact": normalized_sell_impact,
        "invalidating_condition": normalized_invalidating_condition,
        "artifact_ref": normalized_ref,
    }
    guard = _multimodal_evidence_guard([evidence_card])
    input_guard = _document_summary_input_guard(evidence_card)
    status = "ok" if guard["status"] == "ok" and input_guard["status"] == "ok" else "conflict"
    return {
        "schema_version": DOCUMENT_EVIDENCE_SCHEMA_VERSION,
        "status": status,
        "as_of": provider.as_of,
        "document_summary_input_contract": {
            "summary_max_chars": DOCUMENT_SUMMARY_MAX_CHARS,
            "parser_added": False,
            "file_read": False,
            "network_call": False,
            "raw_document_returned": False,
            "secret_values_returned": False,
        },
        "document_summary_input_guard": input_guard,
        "modality_counts": _modality_counts([evidence_card]),
        "artifact_refs": _evidence_artifact_refs([evidence_card]),
        "multimodal_evidence_guard": guard,
        "evidence_card": evidence_card,
        "live_data_required": False,
    }


def calculate_indicators(symbol: str = "QQQ", timeframe: str = "1d") -> dict[str, Any]:
    """Return RSI, DMI/ADX, moving averages, ATR, gaps, and levels."""

    return calculate_indicator_payload(symbol, timeframe=timeframe)


def render_chart(
    symbol: str = "QQQ",
    timeframe: str = "1d",
    output_dir: str | None = None,
) -> dict[str, Any]:
    """Render a dependency-free PNG line chart for offline reports."""

    normalized = _normalize_symbol_identity(symbol)
    normalized_timeframe = _normalize_timeframe_identity(timeframe)
    normalized_output_dir = _normalize_optional_path(output_dir, "output_dir")
    directory = (
        Path(normalized_output_dir)
        if normalized_output_dir is not None
        else _default_chart_output_dir()
    )
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{normalized}_{normalized_timeframe}.png"
    provider = get_market_data_provider()
    bars = list(provider.ohlcv(normalized, 90, timeframe=normalized_timeframe))
    closes = [float(bar["close"]) for bar in bars[-60:]]
    _write_line_chart_png(path, closes)
    artifact_ref = str(path)
    artifact = {
        "ref_type": "CHART",
        "ref": artifact_ref,
        "metadata": {
            "bars": len(closes),
            "renderer": "stdlib_png",
            "timeframe_supported": normalized_timeframe in provider.supported_timeframes(),
        },
    }
    guard = _chart_artifact_guard(path, artifact, provider.live_data_required)

    return {
        "as_of": provider.as_of,
        "symbol": normalized,
        "timeframe": normalized_timeframe,
        "format": "png",
        "path": str(path),
        "chart_artifact_contract": {
            "schema_version": "chart_artifact.v1",
            "format": "png",
            "renderer": "stdlib_png",
            "artifact_ref_type": "CHART",
            "network_call": False,
            "live_data_required": False,
            "committed_artifact_required": False,
        },
        "chart_artifact_guard": guard,
        "artifact_ref": artifact,
        "live_data_required": provider.live_data_required,
    }


def _normalize_symbol_identity(symbol: str) -> str:
    if not isinstance(symbol, str):
        raise ValueError("symbol must be a nonempty string")
    if not _has_no_control_characters(symbol):
        raise ValueError("symbol must not contain control characters")
    normalized = symbol.strip().upper()
    if not normalized:
        raise ValueError("symbol must be a nonempty string")
    return normalized


def _normalize_timeframe_identity(timeframe: str) -> str:
    if not isinstance(timeframe, str):
        raise ValueError("timeframe must be a nonempty string")
    if not _has_no_control_characters(timeframe):
        raise ValueError("timeframe must not contain control characters")
    normalized = timeframe.strip().lower()
    if not normalized:
        raise ValueError("timeframe must be a nonempty string")
    return normalized


def _normalize_required_text(value: str, field_name: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be a nonempty string")
    if not _has_no_control_characters(value):
        raise ValueError(f"{field_name} must not contain control characters")
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{field_name} must be a nonempty string")
    return normalized


def _normalize_optional_text(value: str | None, field_name: str) -> str | None:
    if value is None:
        return None
    return _normalize_required_text(value, field_name)


def _normalize_asset_scope(asset_scope: list[str] | None) -> list[str]:
    if asset_scope is None:
        return []
    if not isinstance(asset_scope, list):
        raise ValueError("asset_scope must be a list of nonempty strings")
    return [
        _normalize_required_text(asset, "asset_scope").upper()
        for asset in asset_scope
    ]


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


def _default_chart_output_dir() -> Path:
    return Path(
        _normalize_optional_path(
            get_settings().artifact_dir,
            ARTIFACT_DIR_ENV,
        )
    ) / "charts"


def _normalize_symbol_list(symbols: list[str] | None) -> list[str]:
    if symbols is None or symbols == []:
        return MARKET_SNAPSHOT_CORE_ASSETS.copy()
    if not isinstance(symbols, list):
        raise ValueError("symbols must be a list of nonempty strings")
    return [_normalize_symbol_identity(symbol) for symbol in symbols]


def _normalize_positive_days(days: int) -> int:
    if not isinstance(days, int) or isinstance(days, bool):
        raise ValueError("days must be a positive integer")
    if days <= 0:
        raise ValueError("days must be a positive integer")
    return days


def _normalize_topic_identity(topic: str) -> str:
    if not isinstance(topic, str):
        raise ValueError("topic must be a nonempty string")
    if not _has_no_control_characters(topic):
        raise ValueError("topic must not contain control characters")
    normalized = topic.strip().lower()
    if not normalized:
        raise ValueError("topic must be a nonempty string")
    return normalized


def _write_line_chart_png(path: Path, values: list[float]) -> None:
    width = 640
    height = 360
    margin = 32
    pixels = bytearray([255] * width * height * 3)
    _draw_line(pixels, width, height, margin, height - margin, width - margin, height - margin)
    _draw_line(pixels, width, height, margin, margin, margin, height - margin)

    min_value = min(values)
    max_value = max(values)
    value_range = max(max_value - min_value, 0.0001)
    points: list[tuple[int, int]] = []
    for index, value in enumerate(values):
        x = margin + int(index * (width - 2 * margin) / max(len(values) - 1, 1))
        y = height - margin - int((value - min_value) * (height - 2 * margin) / value_range)
        points.append((x, y))

    for start, end in zip(points[:-1], points[1:]):
        _draw_line(pixels, width, height, start[0], start[1], end[0], end[1], (31, 91, 180))

    path.write_bytes(_encode_png(width, height, pixels))


def _chart_artifact_guard(
    path: Path,
    artifact_ref: dict[str, Any],
    live_data_required: bool,
) -> dict[str, Any]:
    png_signature = b"\x89PNG\r\n\x1a\n"
    exists = path.exists()
    starts_with_png_signature = (
        path.read_bytes().startswith(png_signature) if exists else False
    )
    checks = [
        {
            "name": "artifact_written",
            "passed": exists,
            "expected": True,
            "actual": exists,
        },
        {
            "name": "png_signature",
            "passed": starts_with_png_signature,
            "expected": "png_signature",
            "actual": starts_with_png_signature,
        },
        {
            "name": "artifact_ref_type_declared",
            "passed": artifact_ref.get("ref_type") == "CHART",
            "expected": "CHART",
            "actual": artifact_ref.get("ref_type"),
        },
        {
            "name": "renderer_is_offline_stdlib",
            "passed": artifact_ref.get("metadata", {}).get("renderer") == "stdlib_png",
            "expected": "stdlib_png",
            "actual": artifact_ref.get("metadata", {}).get("renderer"),
        },
        {
            "name": "no_live_data_required",
            "passed": live_data_required is False,
            "expected": False,
            "actual": live_data_required,
        },
    ]
    return {
        "status": "ok" if all(check["passed"] for check in checks) else "conflict",
        "checks": checks,
    }


def _average_strength(cards: list[dict[str, Any]]) -> float:
    return sum(float(card["strength"]) for card in cards) / len(cards) if cards else 0.0


def _category_strength(cards: list[dict[str, Any]], categories: set[str]) -> float:
    selected = [card for card in cards if card.get("category") in categories]
    return round(_average_strength(selected), 4)


def _modality_counts(cards: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for card in cards:
        modality = str(card.get("modality", "unknown"))
        counts[modality] = counts.get(modality, 0) + 1
    return counts


def _source_group_counts(cards: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for card in cards:
        source_group = str(card.get("source_group", "unknown"))
        counts[source_group] = counts.get(source_group, 0) + 1
    return counts


def _evidence_artifact_refs(cards: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "evidence_id": str(card["evidence_id"]),
            "artifact_ref": card["artifact_ref"],
        }
        for card in cards
        if card.get("artifact_ref")
    ]


def _document_artifact_ref(ref_type: str, ref: str) -> dict[str, Any]:
    return {
        "ref_type": ref_type.upper(),
        "ref": ref,
        "metadata": {
            "description": "Caller-supplied document summary reference",
            "portable": _is_portable_ref(ref),
            "parsed_by_mcp": False,
        },
    }


def _document_summary_input_guard(evidence_card: dict[str, Any]) -> dict[str, Any]:
    summary = str(evidence_card.get("summary") or "")
    artifact_ref = evidence_card.get("artifact_ref") or {}
    checks = [
        {
            "name": "summary_present",
            "passed": bool(summary.strip()),
            "expected": "non_empty_summary",
            "actual": bool(summary.strip()),
        },
        {
            "name": "summary_within_limit",
            "passed": len(summary) <= DOCUMENT_SUMMARY_MAX_CHARS,
            "expected": DOCUMENT_SUMMARY_MAX_CHARS,
            "actual": len(summary),
        },
        {
            "name": "document_not_parsed_by_mcp",
            "passed": artifact_ref.get("metadata", {}).get("parsed_by_mcp") is False,
            "expected": False,
            "actual": artifact_ref.get("metadata", {}).get("parsed_by_mcp"),
        },
        {
            "name": "artifact_ref_portable",
            "passed": _is_portable_ref(str(artifact_ref.get("ref", ""))),
            "expected": "portable_ref",
            "actual": artifact_ref.get("ref"),
        },
    ]
    return {
        "status": "ok" if all(check["passed"] for check in checks) else "conflict",
        "checks": checks,
    }


def _multimodal_evidence_guard(cards: list[dict[str, Any]]) -> dict[str, Any]:
    refs = [card["artifact_ref"] for card in cards if card.get("artifact_ref")]
    checks = [
        {
            "name": "all_cards_have_modality",
            "passed": all(card.get("modality") for card in cards),
            "expected": "modality",
            "actual": [card.get("modality") for card in cards],
        },
        {
            "name": "artifact_refs_are_portable",
            "passed": all(_is_portable_ref(str(ref["ref"])) for ref in refs),
            "expected": "portable_ref",
            "actual": [ref["ref"] for ref in refs],
        },
        {
            "name": "artifact_ref_types_are_declared",
            "passed": all(ref.get("ref_type") for ref in refs),
            "expected": "ref_type",
            "actual": [ref.get("ref_type") for ref in refs],
        },
    ]
    return {
        "status": "ok" if all(check["passed"] for check in checks) else "conflict",
        "checks": checks,
    }


def _is_portable_ref(ref: str) -> bool:
    lowered = ref.lower()
    return (
        ref.startswith("https://")
        or ref.startswith("artifact://")
        or (
            not ref.startswith("/")
            and not ref.startswith("~")
            and not lowered.startswith("file://")
        )
    )


def _has_no_control_characters(value: str) -> bool:
    return all(ord(character) >= 32 and ord(character) != 127 for character in value)


def _bounded_text(value: str, max_chars: int) -> str:
    text = value.strip()
    if len(text) <= max_chars:
        return text
    return f"{text[: max_chars - 15].rstrip()}...[truncated]"


def _clamped_score(value: float, field_name: str) -> float:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise ValueError(f"{field_name} must be a finite number")
    number = float(value)
    if not isfinite(number):
        raise ValueError(f"{field_name} must be a finite number")
    return round(max(0.0, min(1.0, number)), 4)


def _draw_line(
    pixels: bytearray,
    width: int,
    height: int,
    x0: int,
    y0: int,
    x1: int,
    y1: int,
    color: tuple[int, int, int] = (90, 90, 90),
) -> None:
    dx = abs(x1 - x0)
    sx = 1 if x0 < x1 else -1
    dy = -abs(y1 - y0)
    sy = 1 if y0 < y1 else -1
    error = dx + dy

    while True:
        if 0 <= x0 < width and 0 <= y0 < height:
            offset = (y0 * width + x0) * 3
            pixels[offset : offset + 3] = bytes(color)
        if x0 == x1 and y0 == y1:
            break
        doubled_error = 2 * error
        if doubled_error >= dy:
            error += dy
            x0 += sx
        if doubled_error <= dx:
            error += dx
            y0 += sy


def _encode_png(width: int, height: int, pixels: bytearray) -> bytes:
    rows = []
    stride = width * 3
    for y in range(height):
        rows.append(b"\x00" + bytes(pixels[y * stride : (y + 1) * stride]))
    raw = b"".join(rows)
    return (
        b"\x89PNG\r\n\x1a\n"
        + _png_chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
        + _png_chunk(b"IDAT", zlib.compress(raw))
        + _png_chunk(b"IEND", b"")
    )


def _png_chunk(chunk_type: bytes, data: bytes) -> bytes:
    checksum = zlib.crc32(chunk_type)
    checksum = zlib.crc32(data, checksum)
    return (
        struct.pack(">I", len(data))
        + chunk_type
        + data
        + struct.pack(">I", checksum & 0xFFFFFFFF)
    )
