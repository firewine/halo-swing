from typing import Any
from urllib import parse

import pytest

from halo_swing_mcp.config import get_settings
from halo_swing_mcp.providers import (
    FredMacroDataProvider,
    MarketDataProvider,
    NewsApiDataProvider,
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


@pytest.fixture(autouse=True)
def clear_provider_settings_cache() -> None:
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


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


def test_market_data_provider_auto_uses_polygon_api_key(monkeypatch) -> None:
    monkeypatch.delenv("HALO_SWING_MARKET_DATA_MODE", raising=False)
    monkeypatch.setenv("POLYGON_API_KEY", "polygon-secret")
    get_settings.cache_clear()

    provider = get_market_data_provider()

    assert isinstance(provider, PolygonMarketDataProvider)
    assert provider.data_mode == "live"
    assert provider.live_data_required is True

    get_settings.cache_clear()


def test_market_data_provider_auto_key_ignores_source_without_live_mode(
    monkeypatch,
) -> None:
    monkeypatch.delenv("HALO_SWING_MARKET_DATA_MODE", raising=False)
    monkeypatch.setenv("HALO_SWING_MARKET_DATA_SOURCE", "unsupported-source")
    monkeypatch.setenv("POLYGON_API_KEY", "polygon-secret")
    get_settings.cache_clear()

    provider = get_market_data_provider()

    assert isinstance(provider, PolygonMarketDataProvider)
    assert provider.data_mode == "live"

    get_settings.cache_clear()


def test_live_macro_provider_requires_api_key(monkeypatch) -> None:
    monkeypatch.setenv("HALO_SWING_MACRO_DATA_MODE", "live")
    monkeypatch.delenv("HALO_SWING_MACRO_API_KEY", raising=False)
    monkeypatch.delenv("HALO_SWING_FRED_API_KEY", raising=False)
    monkeypatch.delenv("FRED_API_KEY", raising=False)
    get_settings.cache_clear()

    with pytest.raises(ValueError, match="live macro data requires"):
        get_market_data_provider()

    get_settings.cache_clear()


def test_live_macro_provider_uses_fred_api_key(monkeypatch) -> None:
    monkeypatch.setenv("HALO_SWING_MACRO_DATA_MODE", "live")
    monkeypatch.setenv("FRED_API_KEY", "fred-secret")
    get_settings.cache_clear()

    provider = get_market_data_provider()

    assert isinstance(provider, FredMacroDataProvider)
    assert provider.data_mode == "fixture"
    assert provider.live_data_required is False

    get_settings.cache_clear()


def test_market_data_provider_auto_uses_fred_api_key(monkeypatch) -> None:
    monkeypatch.delenv("HALO_SWING_MACRO_DATA_MODE", raising=False)
    monkeypatch.setenv("FRED_API_KEY", "fred-secret")
    get_settings.cache_clear()

    provider = get_market_data_provider()

    assert isinstance(provider, FredMacroDataProvider)
    assert provider.data_mode == "fixture"
    assert provider.live_data_required is False

    get_settings.cache_clear()


def test_live_news_provider_requires_api_key(monkeypatch) -> None:
    monkeypatch.setenv("HALO_SWING_NEWS_DATA_MODE", "live")
    monkeypatch.delenv("HALO_SWING_NEWS_API_KEY", raising=False)
    monkeypatch.delenv("NEWS_API_KEY", raising=False)
    get_settings.cache_clear()

    with pytest.raises(ValueError, match="live news data requires"):
        get_market_data_provider()

    get_settings.cache_clear()


def test_live_news_provider_uses_newsapi_key(monkeypatch) -> None:
    monkeypatch.setenv("HALO_SWING_NEWS_DATA_MODE", "live")
    monkeypatch.setenv("NEWS_API_KEY", "news-secret")
    get_settings.cache_clear()

    provider = get_market_data_provider()

    assert isinstance(provider, NewsApiDataProvider)
    assert provider.data_mode == "fixture"
    assert provider.live_data_required is False

    get_settings.cache_clear()


def test_market_data_provider_auto_uses_newsapi_key(monkeypatch) -> None:
    monkeypatch.delenv("HALO_SWING_NEWS_DATA_MODE", raising=False)
    monkeypatch.setenv("NEWS_API_KEY", "news-secret")
    get_settings.cache_clear()

    provider = get_market_data_provider()

    assert isinstance(provider, NewsApiDataProvider)
    assert provider.data_mode == "fixture"
    assert provider.live_data_required is False

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


def test_fred_macro_provider_fetches_macro_snapshot_without_returning_secret() -> None:
    requested_urls: list[str] = []

    def fake_http_get(url: str) -> dict[str, Any]:
        requested_urls.append(url)
        return {
            "observations": [
                {"value": "20.0"},
                {"value": "19.5"},
                {"value": "19.0"},
                {"value": "18.5"},
                {"value": "18.0"},
                {"value": "17.5"},
            ]
        }

    provider = FredMacroDataProvider(
        ReplayMarketDataProvider(),
        api_key="fred-secret",
        http_get=fake_http_get,
    )

    snapshot = provider.macro_snapshot()
    serialized = repr(snapshot)
    query = parse.parse_qs(parse.urlparse(requested_urls[0]).query)

    assert snapshot["data_mode"] == "live"
    assert snapshot["live_data_required"] is True
    assert snapshot["source_policy"]["provider"] == "fred"
    assert snapshot["source_policy"]["network_call"] is True
    assert snapshot["source_policy"]["secret_values_returned"] is False
    assert set(snapshot["indicators"]) == {"vix", "vxn", "dxy", "us_2y", "us_10y", "oil_wti"}
    assert query["api_key"] == ["fred-secret"]
    assert "fred-secret" not in serialized


def test_newsapi_provider_fetches_news_cards_without_returning_secret() -> None:
    requested_urls: list[str] = []

    def fake_http_get(url: str) -> dict[str, Any]:
        requested_urls.append(url)
        return {
            "articles": [
                {
                    "title": "Semiconductor shares extend AI rally",
                    "description": "Chip leadership remains constructive.",
                    "publishedAt": "2026-05-16T12:00:00Z",
                    "url": "https://example.invalid/news/ai-rally",
                    "source": {"name": "Example Markets"},
                }
            ]
        }

    provider = NewsApiDataProvider(
        ReplayMarketDataProvider(),
        api_key="news-secret",
        http_get=fake_http_get,
    )

    cards = provider.news_cards("ai semiconductor")
    serialized = repr(cards)
    query = parse.parse_qs(parse.urlparse(requested_urls[0]).query)

    assert len(cards) == 1
    assert cards[0]["source"] == "newsapi"
    assert cards[0]["source_group"] == "newsapi"
    assert cards[0]["category"] == "ai_semiconductor"
    assert cards[0]["artifact_ref"]["ref_type"] == "NEWS"
    assert query["apiKey"] == ["news-secret"]
    assert "news-secret" not in serialized


def test_news_bundle_marks_newsapi_cards_as_live(monkeypatch) -> None:
    def fake_http_get(_url: str) -> dict[str, Any]:
        return {
            "articles": [
                {
                    "title": "Policy headline",
                    "description": "Market policy context changed.",
                    "publishedAt": "2026-05-16T13:00:00Z",
                    "url": "https://example.invalid/news/policy",
                    "source": {"name": "Example Policy"},
                }
            ]
        }

    provider = NewsApiDataProvider(
        ReplayMarketDataProvider(),
        api_key="news-secret",
        http_get=fake_http_get,
    )
    monkeypatch.setattr(
        "halo_swing_mcp.tools.market.get_market_data_provider",
        lambda: provider,
    )

    bundle = get_news_bundle("macro")

    assert bundle["data_mode"] == "live"
    assert bundle["live_data_required"] is True
    assert bundle["news_source_policy_contract"]["collection_mode"] == "live"
    assert bundle["news_source_policy_contract"]["required_source_groups"] == [
        "newsapi"
    ]
    assert bundle["news_source_policy_contract"]["live_collection_enabled"] is True
    assert bundle["news_source_policy_contract"]["network_call"] is True
    assert bundle["news_source_policy_guard"]["status"] == "ok"
    source_policy_checks = {
        check["name"]: check["passed"]
        for check in bundle["news_source_policy_guard"]["checks"]
    }
    assert source_policy_checks["live_collection_explicit"] is True
    assert source_policy_checks["network_call_declared"] is True
    assert bundle["news_score_contract"]["network_call"] is True
    assert bundle["evidence_cards"][0]["source"] == "newsapi"


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
