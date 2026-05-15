"""Replay-first data provider boundary for market-facing tools."""

from __future__ import annotations

import json
import os
from datetime import datetime, timedelta, timezone
from urllib import parse, request
from typing import Any, Protocol

from halo_swing_mcp.config import get_settings
from halo_swing_mcp import fixtures


class MarketDataProvider(Protocol):
    """Read-only data boundary used by deterministic and future live providers."""

    @property
    def as_of(self) -> str:
        """Return provider clock in ISO-8601 format."""

    @property
    def data_mode(self) -> str:
        """Return provider mode such as fixture, replay, or live."""

    @property
    def live_data_required(self) -> bool:
        """Return whether the provider needs live external data."""

    def supported_assets(self) -> list[str]:
        """Return supported asset symbols."""

    def supported_timeframes(self) -> list[str]:
        """Return supported OHLCV timeframes."""

    def resolve_asset(self, asset: str) -> tuple[str, int]:
        """Return underlying symbol and leverage multiplier."""

    def ohlcv(
        self,
        symbol: str,
        periods: int = 220,
        timeframe: str = "1d",
    ) -> tuple[dict[str, Any], ...]:
        """Return OHLCV bars."""

    def macro_snapshot(self) -> dict[str, Any]:
        """Return macro snapshot payload."""

    def event_calendar(self, days: int = 14) -> list[dict[str, Any]]:
        """Return events inside the requested window."""

    def news_cards(self, topic: str = "macro") -> list[dict[str, Any]]:
        """Return evidence cards for a report topic."""


class ReplayMarketDataProvider:
    """Fixture-backed replay provider used by default in tests and local runs."""

    @property
    def as_of(self) -> str:
        return fixtures.AS_OF

    @property
    def data_mode(self) -> str:
        return "fixture"

    @property
    def live_data_required(self) -> bool:
        return False

    def supported_assets(self) -> list[str]:
        return fixtures.supported_assets()

    def supported_timeframes(self) -> list[str]:
        return fixtures.supported_timeframes()

    def resolve_asset(self, asset: str) -> tuple[str, int]:
        return fixtures.resolve_asset(asset)

    def ohlcv(
        self,
        symbol: str,
        periods: int = 220,
        timeframe: str = "1d",
    ) -> tuple[dict[str, Any], ...]:
        return fixtures.generate_ohlcv(symbol, periods, timeframe)

    def macro_snapshot(self) -> dict[str, Any]:
        return dict(fixtures.MACRO_FIXTURE)

    def event_calendar(self, days: int = 14) -> list[dict[str, Any]]:
        return fixtures.events_within_days(days)

    def news_cards(self, topic: str = "macro") -> list[dict[str, Any]]:
        normalized = topic.lower()
        if normalized in {"all", "*"}:
            return [dict(card) for card in fixtures.NEWS_FIXTURES]

        cards = [
            dict(card)
            for card in fixtures.NEWS_FIXTURES
            if normalized in card["category"] or normalized in card["source"]
        ]
        if not cards:
            cards = [dict(card) for card in fixtures.NEWS_FIXTURES]
        return cards


class PolygonMarketDataProvider:
    """Polygon OHLCV provider selected only by explicit live market-data mode."""

    _BASE_URL = "https://api.polygon.io/v2/aggs/ticker"

    def __init__(self, *, api_key: str, http_get: Any | None = None) -> None:
        self._api_key = _normalize_secret(api_key, "market data API key")
        self._http_get = http_get or _default_http_get
        self._replay = ReplayMarketDataProvider()

    @property
    def as_of(self) -> str:
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace(
            "+00:00",
            "Z",
        )

    @property
    def data_mode(self) -> str:
        return "live"

    @property
    def live_data_required(self) -> bool:
        return True

    def supported_assets(self) -> list[str]:
        return self._replay.supported_assets()

    def supported_timeframes(self) -> list[str]:
        return self._replay.supported_timeframes()

    def resolve_asset(self, asset: str) -> tuple[str, int]:
        return self._replay.resolve_asset(asset)

    def ohlcv(
        self,
        symbol: str,
        periods: int = 220,
        timeframe: str = "1d",
    ) -> tuple[dict[str, Any], ...]:
        normalized_symbol = _normalize_symbol(symbol)
        multiplier, timespan = _polygon_timeframe(timeframe)
        to_date = datetime.now(timezone.utc).date()
        lookback_days = max(periods * (2 if timespan == "day" else 1), 14)
        from_date = to_date - timedelta(days=lookback_days)
        query = parse.urlencode(
            {
                "adjusted": "true",
                "sort": "asc",
                "limit": max(periods, 1) * 3,
                "apiKey": self._api_key,
            }
        )
        url = (
            f"{self._BASE_URL}/{parse.quote(normalized_symbol)}/range/"
            f"{multiplier}/{timespan}/{from_date.isoformat()}/{to_date.isoformat()}"
            f"?{query}"
        )
        payload = self._http_get(url)
        results = payload.get("results")
        if not isinstance(results, list) or not results:
            raise ValueError("Polygon OHLCV response did not include bars")
        bars = tuple(_polygon_bar(result, timeframe) for result in results[-periods:])
        if len(bars) < 2:
            raise ValueError("Polygon OHLCV response must include at least two bars")
        return bars

    def macro_snapshot(self) -> dict[str, Any]:
        snapshot = self._replay.macro_snapshot()
        snapshot["data_mode"] = "fixture_fallback"
        snapshot["live_data_required"] = True
        snapshot["data_warnings"] = ["macro_live_adapter_not_enabled"]
        return snapshot

    def event_calendar(self, days: int = 14) -> list[dict[str, Any]]:
        return self._replay.event_calendar(days)

    def news_cards(self, topic: str = "macro") -> list[dict[str, Any]]:
        return self._replay.news_cards(topic)


DEFAULT_MARKET_DATA_PROVIDER = ReplayMarketDataProvider()


def get_market_data_provider() -> MarketDataProvider:
    """Return the configured market data provider."""

    settings = get_settings()
    if settings.market_data_mode == "live":
        _validate_live_market_data_source(settings.market_data_source)
        return PolygonMarketDataProvider(api_key=_resolve_polygon_api_key())

    return DEFAULT_MARKET_DATA_PROVIDER


def _validate_live_market_data_source(source: str) -> None:
    if not isinstance(source, str):
        raise ValueError("HALO_SWING_MARKET_DATA_SOURCE must be polygon")
    normalized = source.strip().lower()
    if normalized != "polygon":
        raise ValueError("HALO_SWING_MARKET_DATA_SOURCE must be polygon")


def _resolve_polygon_api_key() -> str:
    settings = get_settings()
    candidates = (
        settings.market_data_api_key,
        os.environ.get("POLYGON_API_KEY"),
    )
    for candidate in candidates:
        if isinstance(candidate, str) and candidate.strip():
            return _normalize_secret(candidate, "market data API key")
    raise ValueError(
        "live market data requires HALO_SWING_MARKET_DATA_API_KEY or POLYGON_API_KEY"
    )


def _normalize_secret(value: str, field_name: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be a nonempty string")
    if not _has_no_control_characters(value):
        raise ValueError(f"{field_name} must not contain control characters")
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{field_name} must be a nonempty string")
    return normalized


def _normalize_symbol(value: str) -> str:
    if not isinstance(value, str):
        raise ValueError("symbol must be a nonempty string")
    if not _has_no_control_characters(value):
        raise ValueError("symbol must not contain control characters")
    normalized = value.strip().upper()
    if not normalized:
        raise ValueError("symbol must be a nonempty string")
    return normalized


def _polygon_timeframe(timeframe: str) -> tuple[int, str]:
    normalized = timeframe.strip().lower() if isinstance(timeframe, str) else ""
    if normalized == "1d":
        return 1, "day"
    if normalized == "4h":
        return 4, "hour"
    if normalized == "1h":
        return 1, "hour"
    raise ValueError("unsupported timeframe")


def _polygon_bar(result: Any, timeframe: str) -> dict[str, Any]:
    if not isinstance(result, dict):
        raise ValueError("Polygon OHLCV bar must be an object")
    try:
        timestamp_ms = int(result["t"])
        open_price = float(result["o"])
        high_price = float(result["h"])
        low_price = float(result["l"])
        close_price = float(result["c"])
        volume = float(result.get("v", 0))
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError("Polygon OHLCV bar is missing numeric fields") from exc
    timestamp = datetime.fromtimestamp(timestamp_ms / 1000, tz=timezone.utc)
    return {
        "timestamp": timestamp.isoformat().replace("+00:00", "Z"),
        "timeframe": timeframe.strip().lower(),
        "open": round(open_price, 4),
        "high": round(high_price, 4),
        "low": round(low_price, 4),
        "close": round(close_price, 4),
        "volume": volume,
    }


def _default_http_get(url: str) -> dict[str, Any]:
    with request.urlopen(url, timeout=10) as response:
        return json.loads(response.read().decode("utf-8"))


def _has_no_control_characters(value: str) -> bool:
    return all(ord(character) >= 32 and ord(character) != 127 for character in value)
