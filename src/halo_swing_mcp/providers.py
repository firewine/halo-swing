"""Replay-first data provider boundary for market-facing tools."""

from __future__ import annotations

from typing import Any, Protocol

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


DEFAULT_MARKET_DATA_PROVIDER = ReplayMarketDataProvider()


def get_market_data_provider() -> MarketDataProvider:
    """Return the default replay provider.

    Live providers must be introduced behind this boundary only after source and
    credential decisions are approved.
    """

    return DEFAULT_MARKET_DATA_PROVIDER
