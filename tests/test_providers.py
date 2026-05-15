from typing import Any
from urllib import parse

import pytest

from halo_swing_mcp.config import get_settings
from halo_swing_mcp.providers import (
    MarketDataProvider,
    PolygonMarketDataProvider,
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
    assert provider.supported_timeframes() == ["1d", "4h", "1h"]
    assert provider.resolve_asset("TQQQ") == ("QQQ", 3)
    assert provider.ohlcv("QQQ", 30)[-1]["close"] > 0
    assert provider.ohlcv("QQQ", 30, "4h")[-1]["timeframe"] == "4h"
    assert provider.ohlcv("QQQ", 30, "1h")[-1]["timestamp"].endswith("Z")
    with pytest.raises(ValueError, match="unsupported timeframe"):
        provider.ohlcv("QQQ", 30, "15m")
    assert provider.macro_snapshot()["live_data_required"] is False
    assert provider.event_calendar(14)
    assert provider.news_cards("all")


def test_default_market_data_provider_is_replay_only() -> None:
    provider = get_market_data_provider()

    assert isinstance(provider, ReplayMarketDataProvider)
    assert_market_data_provider(provider)


def test_live_market_data_provider_requires_api_key(monkeypatch) -> None:
    monkeypatch.setenv("HALO_SWING_MARKET_DATA_MODE", "live")
    monkeypatch.delenv("HALO_SWING_MARKET_DATA_API_KEY", raising=False)
    monkeypatch.delenv("POLYGON_API_KEY", raising=False)
    get_settings.cache_clear()

    with pytest.raises(ValueError, match="live market data requires"):
        get_market_data_provider()

    get_settings.cache_clear()


def test_live_market_data_provider_uses_polygon_api_key(monkeypatch) -> None:
    monkeypatch.setenv("HALO_SWING_MARKET_DATA_MODE", "live")
    monkeypatch.setenv("POLYGON_API_KEY", "polygon-secret")
    get_settings.cache_clear()

    provider = get_market_data_provider()

    assert isinstance(provider, PolygonMarketDataProvider)
    assert provider.data_mode == "live"
    assert provider.live_data_required is True

    get_settings.cache_clear()


def test_polygon_market_data_provider_fetches_ohlcv_without_returning_secret() -> None:
    requested_urls: list[str] = []

    def fake_http_get(url: str) -> dict[str, Any]:
        requested_urls.append(url)
        return {
            "results": [
                {
                    "t": 1_700_000_000_000,
                    "o": 100.0,
                    "h": 102.0,
                    "l": 99.5,
                    "c": 101.0,
                    "v": 1000,
                },
                {
                    "t": 1_700_086_400_000,
                    "o": 101.0,
                    "h": 103.0,
                    "l": 100.5,
                    "c": 102.5,
                    "v": 1100,
                },
            ]
        }

    provider = PolygonMarketDataProvider(
        api_key="polygon-secret",
        http_get=fake_http_get,
    )

    bars = provider.ohlcv(" qqq ", periods=2, timeframe="1d")
    query = parse.parse_qs(parse.urlparse(requested_urls[0]).query)
    serialized_bars = repr(bars)

    assert len(bars) == 2
    assert bars[-1]["timeframe"] == "1d"
    assert bars[-1]["close"] == 102.5
    assert query["apiKey"] == ["polygon-secret"]
    assert "polygon-secret" not in serialized_bars


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
    assert news["modality_counts"]["pdf_summary"] >= 1
    assert news["artifact_refs"]
    assert news["multimodal_evidence_guard"]["status"] == "ok"
