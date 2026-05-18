import json
from typing import Any
from urllib import parse

import pytest

import halo_swing_mcp.env as local_env
from halo_swing_mcp.config import get_settings
from halo_swing_mcp.env import clear_local_env_cache
from halo_swing_mcp.providers import (
    FredMacroDataProvider,
    MarketDataProvider,
    NewsApiDataProvider,
    PolygonMarketDataProvider,
    ReplayMarketDataProvider,
    _default_http_get,
    describe_market_data_provider_route,
    get_market_data_provider,
)
from halo_swing_mcp.secret_values import is_placeholder_secret_value
from halo_swing_mcp.tools.market import (
    calculate_indicators,
    get_event_calendar,
    get_macro_snapshot,
    get_market_snapshot,
    get_news_bundle,
)


@pytest.fixture(autouse=True)
def clear_provider_settings_cache() -> None:
    get_settings.cache_clear()
    clear_local_env_cache()
    yield
    clear_local_env_cache()
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


def clear_live_data_provider_env(monkeypatch) -> None:
    for key in (
        "HALO_SWING_MARKET_DATA_MODE",
        "HALO_SWING_MARKET_DATA_SOURCE",
        "HALO_SWING_MARKET_DATA_API_KEY",
        "POLYGON_API_KEY",
        "HALO_SWING_MACRO_DATA_MODE",
        "HALO_SWING_MACRO_SOURCE",
        "HALO_SWING_MACRO_API_KEY",
        "HALO_SWING_FRED_API_KEY",
        "FRED_API_KEY",
        "HALO_SWING_NEWS_DATA_MODE",
        "HALO_SWING_NEWS_SOURCE",
        "HALO_SWING_NEWS_API_KEY",
        "NEWS_API_KEY",
        "NEWSAPI_KEY",
        "HALO_SWING_LIVE_HTTP_TIMEOUT_SECONDS",
    ):
        monkeypatch.delenv(key, raising=False)
    get_settings.cache_clear()
    clear_local_env_cache()


def test_default_market_data_provider_is_replay_only() -> None:
    provider = get_market_data_provider()

    assert isinstance(provider, ReplayMarketDataProvider)
    assert_market_data_provider(provider)


def test_default_http_get_uses_configured_live_http_timeout(monkeypatch) -> None:
    clear_live_data_provider_env(monkeypatch)
    monkeypatch.setenv("HALO_SWING_LIVE_HTTP_TIMEOUT_SECONDS", "2.5")
    get_settings.cache_clear()
    calls: list[tuple[str, float]] = []

    class FakeResponse:
        def __enter__(self) -> "FakeResponse":
            return self

        def __exit__(self, *args: object) -> None:
            return None

        def read(self) -> bytes:
            return b'{"status":"ok"}'

    def fake_urlopen(url: str, *, timeout: float) -> FakeResponse:
        calls.append((url, timeout))
        return FakeResponse()

    monkeypatch.setattr(
        "halo_swing_mcp.providers.request.urlopen",
        fake_urlopen,
    )

    payload = _default_http_get("https://provider.example/smoke")

    assert payload == {"status": "ok"}
    assert calls == [("https://provider.example/smoke", 2.5)]


def test_live_http_timeout_must_be_positive(monkeypatch) -> None:
    clear_live_data_provider_env(monkeypatch)
    monkeypatch.setenv("HALO_SWING_LIVE_HTTP_TIMEOUT_SECONDS", "0")
    get_settings.cache_clear()

    with pytest.raises(ValueError, match="HALO_SWING_LIVE_HTTP_TIMEOUT_SECONDS"):
        get_settings()


def test_describe_market_data_provider_route_reports_fixture_default(
    monkeypatch,
) -> None:
    clear_live_data_provider_env(monkeypatch)

    payload = describe_market_data_provider_route()

    assert payload["schema_version"] == "live_data_provider_route.v1"
    assert payload["status"] == "blocked"
    assert payload["provider_factory"] == "get_market_data_provider"
    assert payload["missing"] == [
        "market_ohlcv_api_key",
        "macro_api_key",
        "news_api_key",
    ]
    assert payload["route"] == [
        {
            "provider_family": "fixture",
            "provider": "fixture",
            "provider_class": "ReplayMarketDataProvider",
            "data_mode": "fixture",
            "live_data_required": False,
            "network_call": False,
            "secret_values_returned": False,
        }
    ]
    assert payload["selected_provider_classes"] == ["ReplayMarketDataProvider"]
    assert payload["providers"]["market"]["selected"] is False
    assert payload["providers"]["macro"]["selected"] is False
    assert payload["providers"]["news"]["selected"] is False
    assert payload["network_call"] is False
    assert payload["secret_values_returned"] is False


def test_describe_market_data_provider_route_reports_full_api_key_route(
    monkeypatch,
) -> None:
    clear_live_data_provider_env(monkeypatch)
    secret_env = {
        "POLYGON_API_KEY": "polygon-secret",
        "HALO_SWING_FRED_API_KEY": "fred-secret",
        "NEWS_API_KEY": "news-secret",
    }
    for key, value in secret_env.items():
        monkeypatch.setenv(key, value)
    get_settings.cache_clear()

    payload = describe_market_data_provider_route()
    serialized = json.dumps(payload, sort_keys=True)

    assert payload["status"] == "ready"
    assert payload["missing"] == []
    assert payload["selected_provider_classes"] == [
        "PolygonMarketDataProvider",
        "FredMacroDataProvider",
        "NewsApiDataProvider",
    ]
    assert [entry["provider"] for entry in payload["route"]] == [
        "polygon",
        "fred",
        "newsapi",
    ]
    assert all(entry["network_call"] is False for entry in payload["route"])
    assert payload["providers"]["market"]["configured_env_keys"] == ["POLYGON_API_KEY"]
    assert payload["providers"]["macro"]["configured_env_keys"] == [
        "HALO_SWING_FRED_API_KEY"
    ]
    assert payload["providers"]["news"]["configured_env_keys"] == ["NEWS_API_KEY"]
    assert payload["providers"]["market"]["selected"] is True
    assert payload["providers"]["macro"]["selected"] is True
    assert payload["providers"]["news"]["selected"] is True
    assert payload["network_call"] is False
    assert payload["secret_values_returned"] is False
    for key, value in secret_env.items():
        assert key in serialized
        assert value not in serialized


def test_placeholder_secret_predicate_covers_documented_examples() -> None:
    placeholders = [
        "your_polygon_key",
        "your_fred_key",
        "your_newsapi_key",
        "your_provider_key",
        "<api_key>",
        '"<api_key>"',
        "'your_polygon_key'",
        "placeholder",
        "CHANGE_ME",
    ]

    assert all(is_placeholder_secret_value(value) for value in placeholders)
    assert not is_placeholder_secret_value("polygon-realistic-test-secret")
    assert not is_placeholder_secret_value('"polygon-realistic-test-secret"')


def test_describe_market_data_provider_route_ignores_documented_placeholder_api_keys(
    monkeypatch,
) -> None:
    clear_live_data_provider_env(monkeypatch)
    placeholder_env = {
        "POLYGON_API_KEY": "your_polygon_key",
        "FRED_API_KEY": "your_fred_key",
        "NEWS_API_KEY": "your_newsapi_key",
    }
    for key, value in placeholder_env.items():
        monkeypatch.setenv(key, value)
    get_settings.cache_clear()

    payload = describe_market_data_provider_route()
    provider = get_market_data_provider()
    serialized = json.dumps(payload, sort_keys=True)

    assert isinstance(provider, ReplayMarketDataProvider)
    assert payload["status"] == "blocked"
    assert payload["missing"] == [
        "market_ohlcv_api_key",
        "macro_api_key",
        "news_api_key",
    ]
    assert payload["selected_provider_classes"] == ["ReplayMarketDataProvider"]
    assert payload["route"] == [
        {
            "provider_family": "fixture",
            "provider": "fixture",
            "provider_class": "ReplayMarketDataProvider",
            "data_mode": "fixture",
            "live_data_required": False,
            "network_call": False,
            "secret_values_returned": False,
        }
    ]
    for family in ("market", "macro", "news"):
        assert payload["providers"][family]["configured"] is False
        assert payload["providers"][family]["configured_env_keys"] == []
        assert payload["providers"][family]["selected"] is False
    assert payload["network_call"] is False
    assert payload["secret_values_returned"] is False
    for value in placeholder_env.values():
        assert value not in serialized


def test_describe_market_data_provider_route_ignores_quoted_placeholder_api_keys(
    monkeypatch,
) -> None:
    clear_live_data_provider_env(monkeypatch)
    placeholder_env = {
        "POLYGON_API_KEY": '"your_polygon_key"',
        "FRED_API_KEY": "'your_fred_key'",
        "NEWS_API_KEY": '"your_newsapi_key"',
    }
    for key, value in placeholder_env.items():
        monkeypatch.setenv(key, value)
    get_settings.cache_clear()

    payload = describe_market_data_provider_route()
    provider = get_market_data_provider()
    serialized = json.dumps(payload, sort_keys=True)

    assert isinstance(provider, ReplayMarketDataProvider)
    assert payload["status"] == "blocked"
    assert payload["missing"] == [
        "market_ohlcv_api_key",
        "macro_api_key",
        "news_api_key",
    ]
    assert payload["selected_provider_classes"] == ["ReplayMarketDataProvider"]
    for family in ("market", "macro", "news"):
        assert payload["providers"][family]["configured"] is False
        assert payload["providers"][family]["configured_env_keys"] == []
        assert payload["providers"][family]["selected"] is False
    assert payload["network_call"] is False
    assert payload["secret_values_returned"] is False
    for value in placeholder_env.values():
        assert value not in serialized
        assert value.strip("\"'") not in serialized


def test_describe_market_data_provider_route_marks_fred_entry_live_without_market_key(
    monkeypatch,
) -> None:
    clear_live_data_provider_env(monkeypatch)
    monkeypatch.setenv("FRED_API_KEY", "fred-secret")
    get_settings.cache_clear()

    payload = describe_market_data_provider_route()
    serialized = json.dumps(payload, sort_keys=True)

    assert payload["status"] == "blocked"
    assert payload["missing"] == ["market_ohlcv_api_key", "news_api_key"]
    assert payload["selected_provider_classes"] == [
        "ReplayMarketDataProvider",
        "FredMacroDataProvider",
    ]
    assert payload["route"] == [
        {
            "provider_family": "fixture",
            "provider": "fixture",
            "provider_class": "ReplayMarketDataProvider",
            "data_mode": "fixture",
            "live_data_required": False,
            "network_call": False,
            "secret_values_returned": False,
        },
        {
            "provider_family": "macro",
            "provider": "fred",
            "provider_class": "FredMacroDataProvider",
            "data_mode": "live",
            "live_data_required": True,
            "network_call": False,
            "secret_values_returned": False,
        },
    ]
    assert payload["providers"]["macro"]["selected"] is True
    assert payload["providers"]["macro"]["configured_env_keys"] == ["FRED_API_KEY"]
    assert "fred-secret" not in serialized


def test_describe_market_data_provider_route_marks_newsapi_entry_live_without_market_key(
    monkeypatch,
) -> None:
    clear_live_data_provider_env(monkeypatch)
    monkeypatch.setenv("NEWS_API_KEY", "news-secret")
    get_settings.cache_clear()

    payload = describe_market_data_provider_route()
    serialized = json.dumps(payload, sort_keys=True)

    assert payload["status"] == "blocked"
    assert payload["missing"] == ["market_ohlcv_api_key", "macro_api_key"]
    assert payload["selected_provider_classes"] == [
        "ReplayMarketDataProvider",
        "NewsApiDataProvider",
    ]
    assert payload["route"] == [
        {
            "provider_family": "fixture",
            "provider": "fixture",
            "provider_class": "ReplayMarketDataProvider",
            "data_mode": "fixture",
            "live_data_required": False,
            "network_call": False,
            "secret_values_returned": False,
        },
        {
            "provider_family": "news",
            "provider": "newsapi",
            "provider_class": "NewsApiDataProvider",
            "data_mode": "live",
            "live_data_required": True,
            "network_call": False,
            "secret_values_returned": False,
        },
    ]
    assert payload["providers"]["news"]["selected"] is True
    assert payload["providers"]["news"]["configured_env_keys"] == ["NEWS_API_KEY"]
    assert "news-secret" not in serialized


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
    monkeypatch.delenv("NEWSAPI_KEY", raising=False)
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


def test_market_data_provider_auto_uses_newsapi_key_alias(monkeypatch) -> None:
    monkeypatch.delenv("HALO_SWING_NEWS_DATA_MODE", raising=False)
    monkeypatch.setenv("NEWSAPI_KEY", "newsapi-alias-secret")
    get_settings.cache_clear()

    provider = get_market_data_provider()
    payload = describe_market_data_provider_route()
    serialized = json.dumps(payload, sort_keys=True)

    assert isinstance(provider, NewsApiDataProvider)
    assert payload["providers"]["news"]["configured"] is True
    assert payload["providers"]["news"]["configured_env_keys"] == ["NEWSAPI_KEY"]
    assert payload["providers"]["news"]["accepted_env_keys"] == [
        "HALO_SWING_NEWS_API_KEY",
        "NEWS_API_KEY",
        "NEWSAPI_KEY",
    ]
    assert payload["selected_provider_classes"] == [
        "ReplayMarketDataProvider",
        "NewsApiDataProvider",
    ]
    assert "newsapi-alias-secret" not in serialized

    get_settings.cache_clear()


def test_market_data_provider_auto_uses_newsapi_key_alias_with_legacy_placeholder_sibling(
    monkeypatch,
) -> None:
    monkeypatch.delenv("HALO_SWING_NEWS_DATA_MODE", raising=False)
    monkeypatch.setenv("NEWS_API_KEY", "your_newsapi_key")
    monkeypatch.setenv("NEWSAPI_KEY", "newsapi-alias-secret")
    get_settings.cache_clear()

    provider = get_market_data_provider()
    payload = describe_market_data_provider_route()
    serialized = json.dumps(payload, sort_keys=True)

    assert isinstance(provider, NewsApiDataProvider)
    assert payload["providers"]["news"]["configured"] is True
    assert payload["providers"]["news"]["configured_env_keys"] == ["NEWSAPI_KEY"]
    assert payload["providers"]["news"]["accepted_env_keys"] == [
        "HALO_SWING_NEWS_API_KEY",
        "NEWS_API_KEY",
        "NEWSAPI_KEY",
    ]
    assert "newsapi-alias-secret" not in serialized

    get_settings.cache_clear()


def test_market_data_provider_auto_uses_local_env_api_key_aliases(
    tmp_path,
    monkeypatch,
) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("HALO_SWING_DISABLE_DOTENV", raising=False)
    for key in (
        "HALO_SWING_MARKET_DATA_API_KEY",
        "POLYGON_API_KEY",
        "HALO_SWING_MACRO_API_KEY",
        "HALO_SWING_FRED_API_KEY",
        "FRED_API_KEY",
        "HALO_SWING_NEWS_API_KEY",
        "NEWS_API_KEY",
    ):
        monkeypatch.delenv(key, raising=False)
    (tmp_path / ".env").write_text(
        "\n".join(
            [
                "POLYGON_API_KEY=polygon-local-secret",
                "HALO_SWING_FRED_API_KEY=fred-local-secret",
                "NEWS_API_KEY=news-local-secret",
            ]
        ),
        encoding="utf-8",
    )
    get_settings.cache_clear()
    clear_local_env_cache()

    provider = get_market_data_provider()

    assert isinstance(provider, NewsApiDataProvider)
    assert provider.data_mode == "live"
    assert provider.live_data_required is True


def test_market_data_provider_auto_uses_repo_root_env_from_other_cwd(
    tmp_path,
    monkeypatch,
) -> None:
    repo_dir = tmp_path / "repo"
    run_dir = tmp_path / "runner"
    repo_dir.mkdir()
    run_dir.mkdir()
    repo_env = repo_dir / ".env"
    monkeypatch.setattr(local_env, "REPO_ROOT_ENV_PATH", repo_env)
    monkeypatch.chdir(run_dir)
    monkeypatch.delenv("HALO_SWING_DISABLE_DOTENV", raising=False)
    for key in (
        "HALO_SWING_MARKET_DATA_API_KEY",
        "POLYGON_API_KEY",
        "HALO_SWING_MACRO_API_KEY",
        "HALO_SWING_FRED_API_KEY",
        "FRED_API_KEY",
        "HALO_SWING_NEWS_API_KEY",
        "NEWS_API_KEY",
    ):
        monkeypatch.delenv(key, raising=False)
    repo_env.write_text(
        "\n".join(
            [
                "HALO_SWING_MARKET_DATA_API_KEY=market-repo-secret",
                "HALO_SWING_MACRO_API_KEY=macro-repo-secret",
                "HALO_SWING_NEWS_API_KEY=news-repo-secret",
            ]
        ),
        encoding="utf-8",
    )
    get_settings.cache_clear()
    clear_local_env_cache()

    provider = get_market_data_provider()

    assert isinstance(provider, NewsApiDataProvider)
    assert provider.data_mode == "live"
    assert provider.live_data_required is True


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


def test_provider_api_keys_strip_accidental_surrounding_quotes_before_requests() -> None:
    requested_urls: list[str] = []

    def fake_http_get(url: str) -> dict[str, Any]:
        requested_urls.append(url)
        if "polygon.io" in url:
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
        if "stlouisfed.org" in url:
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
        return {
            "articles": [
                {
                    "title": "Market headline",
                    "description": "Policy context changed.",
                    "publishedAt": "2026-05-16T13:00:00Z",
                    "url": "https://example.invalid/news/policy",
                    "source": {"name": "Example Policy"},
                }
            ]
        }

    market_provider = PolygonMarketDataProvider(
        api_key='"polygon-quoted-secret"',
        http_get=fake_http_get,
    )
    macro_provider = FredMacroDataProvider(
        ReplayMarketDataProvider(),
        api_key="'fred-quoted-secret'",
        http_get=fake_http_get,
    )
    news_provider = NewsApiDataProvider(
        ReplayMarketDataProvider(),
        api_key='  "news-quoted-secret"  ',
        http_get=fake_http_get,
    )

    market_provider.ohlcv("QQQ", periods=2)
    macro_provider.macro_snapshot()
    news_provider.news_cards("macro")

    polygon_query = parse.parse_qs(parse.urlparse(requested_urls[0]).query)
    fred_query = parse.parse_qs(parse.urlparse(requested_urls[1]).query)
    news_query = parse.parse_qs(parse.urlparse(requested_urls[-1]).query)
    serialized_urls = repr(requested_urls)

    assert polygon_query["apiKey"] == ["polygon-quoted-secret"]
    assert fred_query["api_key"] == ["fred-quoted-secret"]
    assert news_query["apiKey"] == ["news-quoted-secret"]
    assert "%22" not in serialized_urls
    assert "%27" not in serialized_urls
    assert '"polygon-quoted-secret"' not in serialized_urls
    assert "'fred-quoted-secret'" not in serialized_urls
    assert '"news-quoted-secret"' not in serialized_urls


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


def test_macro_snapshot_declares_live_fred_boundary_without_secret(
    monkeypatch,
) -> None:
    def fake_http_get(_url: str) -> dict[str, Any]:
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
    monkeypatch.setattr(
        "halo_swing_mcp.tools.market.get_market_data_provider",
        lambda: provider,
    )

    payload = get_macro_snapshot()
    guard_checks = {
        check["name"]: check
        for check in payload["macro_filter_guard"]["checks"]
    }
    serialized = repr(payload)

    assert payload["data_mode"] == "live"
    assert payload["live_data_required"] is True
    assert payload["macro_filter_contract"]["network_call"] is True
    assert payload["macro_filter_contract"]["live_data_required"] is True
    assert payload["macro_filter_guard"]["status"] == "ok"
    assert payload["provider_smoke_summary"] == {
        "schema_version": "provider_smoke_summary.v1",
        "status": "ok",
        "passed": True,
        "tool": "get_macro_snapshot",
        "provider_family": "macro",
        "provider": "fred",
        "smoke_command_name": "get_macro_snapshot_live_smoke",
        "preferred_env_key": "FRED_API_KEY",
        "accepted_env_keys": [
            "HALO_SWING_MACRO_API_KEY",
            "HALO_SWING_FRED_API_KEY",
            "FRED_API_KEY",
        ],
        "expected_live_contract": "macro_filter_contract",
        "expected_live_checks": [
            "live_data_boundary_declared",
            "network_call_declared",
        ],
        "network_call": True,
        "network_call_policy": "only_when_matching_provider_selects_live_route",
        "mutates_local_state": False,
        "secret_values_returned": False,
    }
    assert guard_checks["required_indicators_present"]["passed"] is True
    assert guard_checks["live_data_boundary_declared"]["passed"] is True
    assert guard_checks["network_call_declared"]["passed"] is True
    assert "no_live_data_required" not in guard_checks
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
    assert bundle["news_source_policy_contract"]["live_data_required"] is True
    assert bundle["news_source_policy_contract"]["secret_values_returned"] is False
    assert bundle["news_source_policy_guard"]["status"] == "ok"
    assert bundle["provider_smoke_summary"] == {
        "schema_version": "provider_smoke_summary.v1",
        "status": "ok",
        "passed": True,
        "tool": "get_news_bundle",
        "provider_family": "news",
        "provider": "newsapi",
        "smoke_command_name": "get_news_bundle_live_smoke",
        "preferred_env_key": "NEWSAPI_KEY",
        "accepted_env_keys": [
            "HALO_SWING_NEWS_API_KEY",
            "NEWS_API_KEY",
            "NEWSAPI_KEY",
        ],
        "expected_live_contract": "news_source_policy_contract",
        "expected_live_checks": [
            "live_data_boundary_declared",
            "network_call_declared",
            "secret_values_not_returned",
        ],
        "network_call": True,
        "network_call_policy": "only_when_matching_provider_selects_live_route",
        "mutates_local_state": False,
        "secret_values_returned": False,
    }
    source_policy_checks = {
        check["name"]: check["passed"]
        for check in bundle["news_source_policy_guard"]["checks"]
    }
    assert source_policy_checks["live_collection_explicit"] is True
    assert source_policy_checks["network_call_declared"] is True
    assert source_policy_checks["live_data_boundary_declared"] is True
    assert source_policy_checks["secret_values_not_returned"] is True
    assert bundle["news_score_contract"]["network_call"] is True
    assert bundle["news_score_contract"]["live_data_required"] is True
    assert bundle["news_score_contract"]["secret_values_returned"] is False
    assert bundle["evidence_cards"][0]["source"] == "newsapi"
    assert "news-secret" not in json.dumps(bundle, sort_keys=True)


def test_market_snapshot_declares_live_provider_boundary_without_secret(
    monkeypatch,
) -> None:
    def fake_http_get(_url: str) -> dict[str, Any]:
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
    monkeypatch.setattr(
        "halo_swing_mcp.tools.market.get_market_data_provider",
        lambda: provider,
    )

    payload = get_market_snapshot(["QQQ"])
    guard_checks = {
        check["name"]: check
        for check in payload["market_snapshot_guard"]["checks"]
    }
    serialized = repr(payload)

    assert payload["data_mode"] == "live"
    assert payload["live_data_required"] is True
    assert payload["market_snapshot_contract"]["network_call"] is True
    assert payload["market_snapshot_contract"]["live_data_required"] is True
    assert payload["market_snapshot_guard"]["status"] == "ok"
    assert payload["provider_smoke_summary"] == {
        "schema_version": "provider_smoke_summary.v1",
        "status": "ok",
        "passed": True,
        "tool": "get_market_snapshot",
        "provider_family": "market",
        "provider": "polygon",
        "smoke_command_name": "get_market_snapshot_live_smoke",
        "preferred_env_key": "POLYGON_API_KEY",
        "accepted_env_keys": [
            "HALO_SWING_MARKET_DATA_API_KEY",
            "POLYGON_API_KEY",
        ],
        "expected_live_contract": "market_snapshot_contract",
        "expected_live_checks": ["live_data_boundary_declared"],
        "network_call": True,
        "network_call_policy": "only_when_matching_provider_selects_live_route",
        "mutates_local_state": False,
        "secret_values_returned": False,
    }
    assert "no_live_data_required" not in guard_checks
    assert guard_checks["live_data_boundary_declared"]["passed"] is True
    assert guard_checks["feature_store_not_persisted"]["passed"] is True
    assert payload["snapshots"][0]["last_close"] == 102.5
    assert "polygon-secret" not in serialized


def test_market_snapshot_live_provider_exception_returns_recovery_metadata(
    monkeypatch,
) -> None:
    def fake_http_get(_url: str) -> dict[str, Any]:
        raise RuntimeError(
            "provider failed at https://provider.example/?apiKey=polygon-secret"
        )

    provider = PolygonMarketDataProvider(
        api_key="polygon-secret",
        http_get=fake_http_get,
    )
    monkeypatch.setattr(
        "halo_swing_mcp.tools.market.get_market_data_provider",
        lambda: provider,
    )

    payload = get_market_snapshot(["QQQ"])
    serialized = json.dumps(payload, sort_keys=True)
    error_summary = payload["error_summary"]
    guard_checks = {
        check["name"]: check
        for check in payload["market_snapshot_guard"]["checks"]
    }

    assert payload["status"] == "conflict"
    assert payload["data_mode"] == "live"
    assert payload["live_data_required"] is True
    assert payload["market_snapshot_contract"]["network_call"] is True
    assert payload["market_snapshot_contract"]["live_data_required"] is True
    assert payload["market_snapshot_contract"]["secret_values_returned"] is False
    assert payload["market_snapshot_guard"]["status"] == "conflict"
    assert guard_checks["live_data_boundary_declared"]["passed"] is True
    assert guard_checks["network_call_declared"]["passed"] is True
    assert guard_checks["secret_values_not_returned"]["passed"] is True
    assert guard_checks["provider_smoke_completed"]["passed"] is False
    assert error_summary == {
        "schema_version": "provider_smoke_error.v1",
        "tool": "get_market_snapshot",
        "provider_family": "market",
        "provider": "polygon",
        "smoke_command_name": "get_market_snapshot_live_smoke",
        "preferred_env_key": "POLYGON_API_KEY",
        "accepted_env_keys": [
            "HALO_SWING_MARKET_DATA_API_KEY",
            "POLYGON_API_KEY",
        ],
        "next_setup_action": "verify_provider_credentials_or_network",
        "expected_live_contract": "market_snapshot_contract",
        "expected_live_checks": ["live_data_boundary_declared"],
        "network_call_policy": "only_when_matching_provider_selects_live_route",
        "exception_type": "RuntimeError",
        "exception_message_returned": False,
        "url_returned": False,
        "secret_values_returned": False,
    }
    assert "provider.example" not in serialized
    assert "apiKey" not in serialized
    assert "polygon-secret" not in serialized


def test_macro_snapshot_live_provider_exception_returns_recovery_metadata(
    monkeypatch,
) -> None:
    def fake_http_get(_url: str) -> dict[str, Any]:
        raise RuntimeError(
            "provider failed at https://provider.example/?api_key=fred-secret"
        )

    provider = FredMacroDataProvider(
        ReplayMarketDataProvider(),
        api_key="fred-secret",
        http_get=fake_http_get,
    )
    monkeypatch.setattr(
        "halo_swing_mcp.tools.market.get_market_data_provider",
        lambda: provider,
    )

    payload = get_macro_snapshot()
    serialized = json.dumps(payload, sort_keys=True)
    error_summary = payload["error_summary"]
    guard_checks = {
        check["name"]: check
        for check in payload["macro_filter_guard"]["checks"]
    }

    assert payload["status"] == "conflict"
    assert payload["data_mode"] == "live"
    assert payload["live_data_required"] is True
    assert payload["macro_filter_contract"]["network_call"] is True
    assert payload["macro_filter_contract"]["live_data_required"] is True
    assert payload["macro_filter_contract"]["secret_values_returned"] is False
    assert payload["source_policy"]["secret_values_returned"] is False
    assert payload["macro_filter_guard"]["status"] == "conflict"
    assert guard_checks["live_data_boundary_declared"]["passed"] is True
    assert guard_checks["network_call_declared"]["passed"] is True
    assert guard_checks["secret_values_not_returned"]["passed"] is True
    assert guard_checks["provider_smoke_completed"]["passed"] is False
    assert error_summary == {
        "schema_version": "provider_smoke_error.v1",
        "tool": "get_macro_snapshot",
        "provider_family": "macro",
        "provider": "fred",
        "smoke_command_name": "get_macro_snapshot_live_smoke",
        "preferred_env_key": "FRED_API_KEY",
        "accepted_env_keys": [
            "HALO_SWING_MACRO_API_KEY",
            "HALO_SWING_FRED_API_KEY",
            "FRED_API_KEY",
        ],
        "next_setup_action": "verify_provider_credentials_or_network",
        "expected_live_contract": "macro_filter_contract",
        "expected_live_checks": [
            "live_data_boundary_declared",
            "network_call_declared",
        ],
        "network_call_policy": "only_when_matching_provider_selects_live_route",
        "exception_type": "RuntimeError",
        "exception_message_returned": False,
        "url_returned": False,
        "secret_values_returned": False,
    }
    assert "provider.example" not in serialized
    assert "api_key" not in serialized
    assert "fred-secret" not in serialized


def test_news_bundle_live_provider_exception_returns_recovery_metadata(
    monkeypatch,
) -> None:
    def fake_http_get(_url: str) -> dict[str, Any]:
        raise RuntimeError(
            "provider failed at https://provider.example/?apiKey=news-secret"
        )

    provider = NewsApiDataProvider(
        ReplayMarketDataProvider(),
        api_key="news-secret",
        http_get=fake_http_get,
    )
    monkeypatch.setattr(
        "halo_swing_mcp.tools.market.get_market_data_provider",
        lambda: provider,
    )

    payload = get_news_bundle("macro")
    serialized = json.dumps(payload, sort_keys=True)
    error_summary = payload["error_summary"]
    guard_checks = {
        check["name"]: check
        for check in payload["news_source_policy_guard"]["checks"]
    }

    assert payload["status"] == "conflict"
    assert payload["data_mode"] == "live"
    assert payload["live_data_required"] is True
    assert payload["news_source_policy_contract"]["network_call"] is True
    assert payload["news_source_policy_contract"]["live_data_required"] is True
    assert payload["news_source_policy_contract"]["secret_values_returned"] is False
    assert payload["news_score_contract"]["network_call"] is True
    assert payload["news_score_contract"]["live_data_required"] is True
    assert payload["news_score_contract"]["secret_values_returned"] is False
    assert payload["news_source_policy_guard"]["status"] == "conflict"
    assert guard_checks["live_data_boundary_declared"]["passed"] is True
    assert guard_checks["network_call_declared"]["passed"] is True
    assert guard_checks["secret_values_not_returned"]["passed"] is True
    assert guard_checks["provider_smoke_completed"]["passed"] is False
    assert error_summary == {
        "schema_version": "provider_smoke_error.v1",
        "tool": "get_news_bundle",
        "provider_family": "news",
        "provider": "newsapi",
        "smoke_command_name": "get_news_bundle_live_smoke",
        "preferred_env_key": "NEWSAPI_KEY",
        "accepted_env_keys": [
            "HALO_SWING_NEWS_API_KEY",
            "NEWS_API_KEY",
            "NEWSAPI_KEY",
        ],
        "next_setup_action": "verify_provider_credentials_or_network",
        "expected_live_contract": "news_source_policy_contract",
        "expected_live_checks": [
            "live_data_boundary_declared",
            "network_call_declared",
            "secret_values_not_returned",
        ],
        "network_call_policy": "only_when_matching_provider_selects_live_route",
        "exception_type": "RuntimeError",
        "exception_message_returned": False,
        "url_returned": False,
        "secret_values_returned": False,
    }
    assert "provider.example" not in serialized
    assert "apiKey" not in serialized
    assert "news-secret" not in serialized


def test_fixture_provider_exception_is_not_swallowed(monkeypatch) -> None:
    class BrokenReplayProvider(ReplayMarketDataProvider):
        def macro_snapshot(self) -> dict[str, Any]:
            raise RuntimeError("fixture provider failure")

    monkeypatch.setattr(
        "halo_swing_mcp.tools.market.get_market_data_provider",
        BrokenReplayProvider,
    )

    with pytest.raises(RuntimeError, match="fixture provider failure"):
        get_macro_snapshot()


def test_calculate_indicators_declares_live_provider_boundaries(monkeypatch) -> None:
    def fake_http_get(url: str) -> dict[str, Any]:
        assert "polygon-secret" in parse.parse_qs(parse.urlparse(url).query)["apiKey"]
        base_timestamp = 1_700_000_000_000
        return {
            "results": [
                {
                    "t": base_timestamp + index * 86_400_000,
                    "o": 100.0 + index,
                    "h": 101.5 + index,
                    "l": 99.5 + index,
                    "c": 100.75 + index,
                    "v": 1000 + index,
                }
                for index in range(220)
            ]
        }

    provider = PolygonMarketDataProvider(
        api_key="polygon-secret",
        http_get=fake_http_get,
    )
    monkeypatch.setattr(
        "halo_swing_mcp.indicators.get_market_data_provider",
        lambda: provider,
    )

    payload = calculate_indicators("QQQ")
    serialized = repr(payload)

    assert payload["data_mode"] == "live"
    assert payload["live_data_required"] is True
    assert payload["timeframe_contract"]["network_call"] is True
    assert payload["timeframe_contract"]["live_data_required"] is True
    assert payload["timeframe_contract"]["fixture_replay_default"] is False
    assert payload["swing_level_contract"]["network_call"] is True
    assert payload["swing_level_contract"]["live_data_required"] is True
    assert payload["rsi_14"] is not None
    assert payload["latest_bar"]["close"] == 319.75
    assert "polygon-secret" not in serialized


def test_market_tools_keep_replay_payload_contract() -> None:
    market = get_market_snapshot(["QQQ"])
    macro = get_macro_snapshot()
    events = get_event_calendar(14)
    news = get_news_bundle("all")

    payloads: list[dict[str, Any]] = [market, macro, events, news]
    for payload in payloads:
        assert payload["data_mode"] == "fixture"
        assert payload["live_data_required"] is False

    macro_guard_checks = {
        check["name"]: check
        for check in macro["macro_filter_guard"]["checks"]
    }
    assert macro["macro_filter_contract"]["network_call"] is False
    assert macro_guard_checks["required_indicators_present"]["passed"] is True
    assert macro_guard_checks["no_live_data_required"]["passed"] is True
    assert macro_guard_checks["no_network_call"]["passed"] is True
    assert "live_data_boundary_declared" not in macro_guard_checks
    market_guard_checks = {
        check["name"]: check
        for check in market["market_snapshot_guard"]["checks"]
    }
    assert market["market_snapshot_contract"]["network_call"] is False
    assert market_guard_checks["no_live_data_required"]["passed"] is True
    assert "live_data_boundary_declared" not in market_guard_checks
    assert market["snapshots"][0]["symbol"] == "QQQ"
    assert events["events"]
    news_guard_checks = {
        check["name"]: check
        for check in news["news_source_policy_guard"]["checks"]
    }
    assert news["news_source_policy_contract"]["network_call"] is False
    assert news["news_source_policy_contract"]["live_data_required"] is False
    assert news["news_source_policy_contract"]["secret_values_returned"] is False
    assert news_guard_checks["no_live_collection"]["passed"] is True
    assert news_guard_checks["no_network_call"]["passed"] is True
    assert news_guard_checks["secret_values_not_returned"]["passed"] is True
    assert "live_data_boundary_declared" not in news_guard_checks
    assert news["news_score_contract"]["secret_values_returned"] is False
    assert news["evidence_cards"]
    assert news["modality_counts"]["pdf_summary"] >= 1
    assert news["artifact_refs"]
    assert news["multimodal_evidence_guard"]["status"] == "ok"
