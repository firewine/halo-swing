from typing import Any

from halo_swing_mcp.providers import (
    MarketDataProvider,
    ReplayMarketDataProvider,
    get_market_data_provider,
)
from halo_swing_mcp.tools.market import (
    get_event_calendar,
    get_macro_snapshot,
    get_market_snapshot,
    get_news_bundle,
)


def assert_market_data_provider(provider: MarketDataProvider) -> None:
    assert provider.as_of
    assert provider.data_mode == "fixture"
    assert provider.live_data_required is False
    assert "TQQQ" in provider.supported_assets()
    assert provider.resolve_asset("TQQQ") == ("QQQ", 3)
    assert provider.ohlcv("QQQ", 30)[-1]["close"] > 0
    assert provider.macro_snapshot()["live_data_required"] is False
    assert provider.event_calendar(14)
    assert provider.news_cards("all")


def test_default_market_data_provider_is_replay_only() -> None:
    provider = get_market_data_provider()

    assert isinstance(provider, ReplayMarketDataProvider)
    assert_market_data_provider(provider)


def test_market_tools_keep_replay_payload_contract() -> None:
    market = get_market_snapshot(["QQQ"])
    macro = get_macro_snapshot()
    events = get_event_calendar(14)
    news = get_news_bundle("all")

    payloads: list[dict[str, Any]] = [market, macro, events, news]
    for payload in payloads:
        assert payload["data_mode"] == "fixture"
        assert payload["live_data_required"] is False

    assert market["snapshots"][0]["symbol"] == "QQQ"
    assert events["events"]
    assert news["evidence_cards"]
