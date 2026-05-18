"""Replay-first data provider boundary for market-facing tools."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from urllib import parse, request
from typing import Any, Protocol

from halo_swing_mcp import fixtures
from halo_swing_mcp.config import get_settings
from halo_swing_mcp.env import get_config_value
from halo_swing_mcp.secret_values import (
    is_placeholder_secret_value,
    normalize_secret_value,
)


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


class FredMacroDataProvider:
    """FRED macro provider wrapper selected only by explicit live macro mode."""

    _BASE_URL = "https://api.stlouisfed.org/fred/series/observations"
    _SERIES = {
        "vix": ("VIXCLS", "change_5d"),
        "vxn": ("VXNCLS", "change_5d"),
        "dxy": ("DTWEXBGS", "change_5d"),
        "us_2y": ("DGS2", "change_5d_bps"),
        "us_10y": ("DGS10", "change_5d_bps"),
        "oil_wti": ("DCOILWTICO", "change_5d"),
    }

    def __init__(
        self,
        base_provider: MarketDataProvider,
        *,
        api_key: str,
        http_get: Any | None = None,
    ) -> None:
        self._base_provider = base_provider
        self._api_key = _normalize_secret(api_key, "macro API key")
        self._http_get = http_get or _default_http_get

    @property
    def as_of(self) -> str:
        return self._base_provider.as_of

    @property
    def data_mode(self) -> str:
        return self._base_provider.data_mode

    @property
    def live_data_required(self) -> bool:
        return self._base_provider.live_data_required

    def supported_assets(self) -> list[str]:
        return self._base_provider.supported_assets()

    def supported_timeframes(self) -> list[str]:
        return self._base_provider.supported_timeframes()

    def resolve_asset(self, asset: str) -> tuple[str, int]:
        return self._base_provider.resolve_asset(asset)

    def ohlcv(
        self,
        symbol: str,
        periods: int = 220,
        timeframe: str = "1d",
    ) -> tuple[dict[str, Any], ...]:
        return self._base_provider.ohlcv(symbol, periods, timeframe)

    def macro_snapshot(self) -> dict[str, Any]:
        indicators = {
            name: _fred_indicator(
                self._fetch_series(series_id),
                change_field=change_field,
            )
            for name, (series_id, change_field) in self._SERIES.items()
        }
        risk_score = _macro_risk_score(indicators)
        macro_score = round(max(0.0, min(1.0, 1.0 - risk_score)), 4)
        return {
            "as_of": self.as_of,
            "data_mode": "live",
            "live_data_required": True,
            "macro_score": macro_score,
            "risk_score": risk_score,
            "indicators": indicators,
            "summary": "Live FRED macro snapshot built from configured API-key sources.",
            "source_policy": {
                "schema_version": "fred_macro_source_policy.v1",
                "provider": "fred",
                "network_call": True,
                "secret_values_returned": False,
            },
        }

    def event_calendar(self, days: int = 14) -> list[dict[str, Any]]:
        return self._base_provider.event_calendar(days)

    def news_cards(self, topic: str = "macro") -> list[dict[str, Any]]:
        return self._base_provider.news_cards(topic)

    def _fetch_series(self, series_id: str) -> list[float]:
        query = parse.urlencode(
            {
                "series_id": series_id,
                "api_key": self._api_key,
                "file_type": "json",
                "sort_order": "desc",
                "limit": 10,
            }
        )
        payload = self._http_get(f"{self._BASE_URL}?{query}")
        observations = payload.get("observations")
        if not isinstance(observations, list):
            raise ValueError("FRED response did not include observations")
        values: list[float] = []
        for observation in observations:
            if not isinstance(observation, dict):
                continue
            raw_value = observation.get("value")
            try:
                values.append(float(raw_value))
            except (TypeError, ValueError):
                continue
        if len(values) < 2:
            raise ValueError("FRED response must include at least two numeric observations")
        return values


class NewsApiDataProvider:
    """NewsAPI evidence-card wrapper selected only by explicit live news mode."""

    _BASE_URL = "https://newsapi.org/v2/everything"

    def __init__(
        self,
        base_provider: MarketDataProvider,
        *,
        api_key: str,
        http_get: Any | None = None,
    ) -> None:
        self._base_provider = base_provider
        self._api_key = _normalize_secret(api_key, "news API key")
        self._http_get = http_get or _default_http_get

    @property
    def as_of(self) -> str:
        return self._base_provider.as_of

    @property
    def data_mode(self) -> str:
        return self._base_provider.data_mode

    @property
    def live_data_required(self) -> bool:
        return self._base_provider.live_data_required

    def supported_assets(self) -> list[str]:
        return self._base_provider.supported_assets()

    def supported_timeframes(self) -> list[str]:
        return self._base_provider.supported_timeframes()

    def resolve_asset(self, asset: str) -> tuple[str, int]:
        return self._base_provider.resolve_asset(asset)

    def ohlcv(
        self,
        symbol: str,
        periods: int = 220,
        timeframe: str = "1d",
    ) -> tuple[dict[str, Any], ...]:
        return self._base_provider.ohlcv(symbol, periods, timeframe)

    def macro_snapshot(self) -> dict[str, Any]:
        return self._base_provider.macro_snapshot()

    def event_calendar(self, days: int = 14) -> list[dict[str, Any]]:
        return self._base_provider.event_calendar(days)

    def news_cards(self, topic: str = "macro") -> list[dict[str, Any]]:
        normalized_topic = _normalize_news_topic(topic)
        query = parse.urlencode(
            {
                "q": normalized_topic,
                "language": "en",
                "sortBy": "publishedAt",
                "pageSize": 10,
                "apiKey": self._api_key,
            }
        )
        payload = self._http_get(f"{self._BASE_URL}?{query}")
        articles = payload.get("articles")
        if not isinstance(articles, list) or not articles:
            raise ValueError("NewsAPI response did not include articles")
        return [
            _newsapi_card(article, index=index, topic=normalized_topic)
            for index, article in enumerate(articles[:10], start=1)
            if isinstance(article, dict)
        ]


DEFAULT_MARKET_DATA_PROVIDER = ReplayMarketDataProvider()
MARKET_API_KEY_ENV_KEYS = ("HALO_SWING_MARKET_DATA_API_KEY", "POLYGON_API_KEY")
MACRO_API_KEY_ENV_KEYS = (
    "HALO_SWING_MACRO_API_KEY",
    "HALO_SWING_FRED_API_KEY",
    "FRED_API_KEY",
)
NEWS_API_KEY_ENV_KEYS = ("HALO_SWING_NEWS_API_KEY", "NEWS_API_KEY", "NEWSAPI_KEY")


def get_market_data_provider() -> MarketDataProvider:
    """Return the configured market data provider."""

    settings = get_settings()
    provider: MarketDataProvider = DEFAULT_MARKET_DATA_PROVIDER
    if settings.market_data_mode == "live" or _polygon_api_key_configured(settings):
        if settings.market_data_mode == "live":
            _validate_live_market_data_source(settings.market_data_source)
        provider = PolygonMarketDataProvider(api_key=_resolve_polygon_api_key())
    if settings.macro_data_mode == "live" or _fred_api_key_configured(settings):
        if settings.macro_data_mode == "live":
            _validate_live_macro_source(settings.macro_source)
        provider = FredMacroDataProvider(provider, api_key=_resolve_fred_api_key())
    if settings.news_data_mode == "live" or _news_api_key_configured(settings):
        if settings.news_data_mode == "live":
            _validate_live_news_source(settings.news_source)
        provider = NewsApiDataProvider(provider, api_key=_resolve_news_api_key())

    return provider


def describe_market_data_provider_route() -> dict[str, Any]:
    """Describe provider factory selection without making provider network calls."""

    provider: MarketDataProvider | None
    selection_error: str | None = None
    try:
        provider = get_market_data_provider()
    except ValueError as exc:
        provider = None
        selection_error = str(exc)

    providers = {
        "market": _provider_family_status(
            provider_family="market",
            provider="polygon",
            provider_class="PolygonMarketDataProvider",
            env_keys=MARKET_API_KEY_ENV_KEYS,
            missing_name="market_ohlcv_api_key",
        ),
        "macro": _provider_family_status(
            provider_family="macro",
            provider="fred",
            provider_class="FredMacroDataProvider",
            env_keys=MACRO_API_KEY_ENV_KEYS,
            missing_name="macro_api_key",
        ),
        "news": _provider_family_status(
            provider_family="news",
            provider="newsapi",
            provider_class="NewsApiDataProvider",
            env_keys=NEWS_API_KEY_ENV_KEYS,
            missing_name="news_api_key",
        ),
    }
    route = _provider_route(provider) if provider is not None else []
    selected_provider_classes = [entry["provider_class"] for entry in route]
    missing = [
        missing
        for provider_status in providers.values()
        for missing in provider_status["missing"]
    ]

    for provider_status in providers.values():
        provider_status["selected"] = (
            provider_status["provider_class"] in selected_provider_classes
        )

    return {
        "schema_version": "live_data_provider_route.v1",
        "status": "ready" if not selection_error and not missing else "blocked",
        "provider_factory": "get_market_data_provider",
        "route": route,
        "selected_provider_classes": selected_provider_classes,
        "providers": providers,
        "missing": missing,
        "selection_error": selection_error,
        "network_call": False,
        "secret_values_returned": False,
    }


def _validate_live_market_data_source(source: str) -> None:
    if not isinstance(source, str):
        raise ValueError("HALO_SWING_MARKET_DATA_SOURCE must be polygon")
    normalized = source.strip().lower()
    if normalized != "polygon":
        raise ValueError("HALO_SWING_MARKET_DATA_SOURCE must be polygon")


def _validate_live_macro_source(source: str) -> None:
    if not isinstance(source, str):
        raise ValueError("HALO_SWING_MACRO_SOURCE must be fred")
    normalized = source.strip().lower()
    if normalized != "fred":
        raise ValueError("HALO_SWING_MACRO_SOURCE must be fred")


def _validate_live_news_source(source: str) -> None:
    if not isinstance(source, str):
        raise ValueError("HALO_SWING_NEWS_SOURCE must be newsapi")
    normalized = source.strip().lower()
    if normalized != "newsapi":
        raise ValueError("HALO_SWING_NEWS_SOURCE must be newsapi")


def _resolve_polygon_api_key() -> str:
    settings = get_settings()
    candidates = (
        settings.market_data_api_key,
        get_config_value("HALO_SWING_MARKET_DATA_API_KEY"),
        get_config_value("POLYGON_API_KEY"),
    )
    for candidate in candidates:
        if _secret_candidate_configured(candidate):
            return _normalize_secret(candidate, "market data API key")
    raise ValueError(
        "live market data requires HALO_SWING_MARKET_DATA_API_KEY or POLYGON_API_KEY"
    )


def _polygon_api_key_configured(settings: Any) -> bool:
    return (
        _secret_candidate_configured(settings.market_data_api_key)
        or _secret_candidate_configured(
            get_config_value("HALO_SWING_MARKET_DATA_API_KEY")
        )
        or _secret_candidate_configured(get_config_value("POLYGON_API_KEY"))
    )


def _resolve_fred_api_key() -> str:
    settings = get_settings()
    candidates = (
        settings.macro_api_key,
        get_config_value("HALO_SWING_MACRO_API_KEY"),
        get_config_value("HALO_SWING_FRED_API_KEY"),
        get_config_value("FRED_API_KEY"),
    )
    for candidate in candidates:
        if _secret_candidate_configured(candidate):
            return _normalize_secret(candidate, "macro API key")
    raise ValueError(
        "live macro data requires HALO_SWING_MACRO_API_KEY, "
        "HALO_SWING_FRED_API_KEY, or FRED_API_KEY"
    )


def _fred_api_key_configured(settings: Any) -> bool:
    return (
        _secret_candidate_configured(settings.macro_api_key)
        or _secret_candidate_configured(get_config_value("HALO_SWING_MACRO_API_KEY"))
        or _secret_candidate_configured(get_config_value("HALO_SWING_FRED_API_KEY"))
        or _secret_candidate_configured(get_config_value("FRED_API_KEY"))
    )


def _resolve_news_api_key() -> str:
    settings = get_settings()
    candidates = (
        settings.news_api_key,
        get_config_value("HALO_SWING_NEWS_API_KEY"),
        get_config_value("NEWS_API_KEY"),
        get_config_value("NEWSAPI_KEY"),
    )
    for candidate in candidates:
        if _secret_candidate_configured(candidate):
            return _normalize_secret(candidate, "news API key")
    raise ValueError(
        "live news data requires HALO_SWING_NEWS_API_KEY, NEWS_API_KEY, or NEWSAPI_KEY"
    )


def _news_api_key_configured(settings: Any) -> bool:
    return (
        _secret_candidate_configured(settings.news_api_key)
        or _secret_candidate_configured(get_config_value("HALO_SWING_NEWS_API_KEY"))
        or _secret_candidate_configured(get_config_value("NEWS_API_KEY"))
        or _secret_candidate_configured(get_config_value("NEWSAPI_KEY"))
    )


def _provider_family_status(
    *,
    provider_family: str,
    provider: str,
    provider_class: str,
    env_keys: tuple[str, ...],
    missing_name: str,
) -> dict[str, Any]:
    configured_env_keys = [
        key
        for key in env_keys
        if _secret_candidate_configured(get_config_value(key))
    ]
    configured = bool(configured_env_keys)
    return {
        "provider_family": provider_family,
        "provider": provider,
        "provider_class": provider_class,
        "configured": configured,
        "configured_env_keys": configured_env_keys,
        "accepted_env_keys": list(env_keys),
        "missing": [] if configured else [missing_name],
        "auto_selects_live_provider": configured,
        "selected": False,
        "secret_values_returned": False,
    }


def _provider_route(provider: MarketDataProvider | None) -> list[dict[str, Any]]:
    if provider is None:
        return []
    if isinstance(provider, NewsApiDataProvider):
        return [
            *_provider_route(provider._base_provider),
            _provider_route_entry(
                provider_family="news",
                provider="newsapi",
                provider_class="NewsApiDataProvider",
                data_mode="live",
                live_data_required=True,
            ),
        ]
    if isinstance(provider, FredMacroDataProvider):
        return [
            *_provider_route(provider._base_provider),
            _provider_route_entry(
                provider_family="macro",
                provider="fred",
                provider_class="FredMacroDataProvider",
                data_mode="live",
                live_data_required=True,
            ),
        ]
    if isinstance(provider, PolygonMarketDataProvider):
        return [
            _provider_route_entry(
                provider_family="market",
                provider="polygon",
                provider_class="PolygonMarketDataProvider",
                data_mode=provider.data_mode,
                live_data_required=provider.live_data_required,
            )
        ]
    return [
        _provider_route_entry(
            provider_family="fixture",
            provider="fixture",
            provider_class=provider.__class__.__name__,
            data_mode=provider.data_mode,
            live_data_required=provider.live_data_required,
        )
    ]


def _provider_route_entry(
    *,
    provider_family: str,
    provider: str,
    provider_class: str,
    data_mode: str,
    live_data_required: bool,
) -> dict[str, Any]:
    return {
        "provider_family": provider_family,
        "provider": provider,
        "provider_class": provider_class,
        "data_mode": data_mode,
        "live_data_required": live_data_required,
        "network_call": False,
        "secret_values_returned": False,
    }


def _secret_candidate_configured(value: str | None) -> bool:
    normalized = normalize_secret_value(value) if isinstance(value, str) else ""
    return bool(
        normalized
        and isinstance(value, str)
        and _has_no_control_characters(value)
        and _has_no_control_characters(normalized)
        and not is_placeholder_secret_value(normalized)
    )


def _normalize_news_topic(value: str) -> str:
    if not isinstance(value, str):
        raise ValueError("topic must be a nonempty string")
    if not _has_no_control_characters(value):
        raise ValueError("topic must not contain control characters")
    normalized = value.strip().lower()
    if not normalized:
        raise ValueError("topic must be a nonempty string")
    if normalized in {"all", "*"}:
        return "market OR macro OR policy OR semiconductor"
    return normalized


def _newsapi_card(article: dict[str, Any], *, index: int, topic: str) -> dict[str, Any]:
    title = _safe_article_text(article.get("title"), fallback="Untitled market news")
    description = _safe_article_text(article.get("description"), fallback="")
    source = article.get("source") if isinstance(article.get("source"), dict) else {}
    source_name = _safe_article_text(source.get("name"), fallback="newsapi")
    published_at = _safe_article_text(article.get("publishedAt"), fallback=fixtures.AS_OF)
    url = _safe_article_text(article.get("url"), fallback="https://example.invalid/newsapi")
    summary = f"{title}. {description}".strip()
    return {
        "evidence_id": f"ev_newsapi_{index:03d}",
        "category": _news_category(topic),
        "source": "newsapi",
        "source_group": "newsapi",
        "modality": "news_text",
        "observed_at": published_at,
        "asset_scope": ["QQQ", "SPY", "TQQQ", "QLD", "BTC", "SMH", "SOXX", "SOXL"],
        "bias": "neutral",
        "strength": 0.5,
        "confidence": 0.55,
        "summary": summary[:900],
        "buy_impact": "context_only",
        "sell_impact": "watch_if_headline_conflicts_with_signal",
        "invalidating_condition": "Live headline context changes materially.",
        "artifact_ref": {
            "ref_type": "NEWS",
            "ref": url,
            "metadata": {
                "description": f"NewsAPI article from {source_name}",
                "portable": True,
            },
        },
    }


def _news_category(topic: str) -> str:
    if "semiconductor" in topic or "ai" in topic:
        return "ai_semiconductor"
    if "oil" in topic or "energy" in topic or "geopolitical" in topic:
        return "geopolitical_oil"
    return "macro_policy"


def _safe_article_text(value: Any, *, fallback: str) -> str:
    if not isinstance(value, str):
        return fallback
    if not _has_no_control_characters(value):
        return fallback
    normalized = value.strip()
    return normalized or fallback


def _fred_indicator(values_descending: list[float], *, change_field: str) -> dict[str, Any]:
    latest = values_descending[0]
    comparison = values_descending[min(5, len(values_descending) - 1)]
    change = latest - comparison
    if change_field == "change_5d_bps":
        change *= 100
    return {
        "value": round(latest, 4),
        change_field: round(change, 4),
        "state": _macro_indicator_state(latest, change_field),
    }


def _macro_indicator_state(value: float, change_field: str) -> str:
    if change_field == "change_5d_bps":
        return "easing" if value < 4.5 else "firm"
    if value >= 25:
        return "elevated"
    if value <= 18:
        return "contained"
    return "stable"


def _macro_risk_score(indicators: dict[str, dict[str, Any]]) -> float:
    vix = float(indicators["vix"]["value"])
    vxn = float(indicators["vxn"]["value"])
    us_10y = float(indicators["us_10y"]["value"])
    oil = float(indicators["oil_wti"]["value"])
    raw = (vix / 40 * 0.35) + (vxn / 45 * 0.25) + (us_10y / 6 * 0.25) + (oil / 120 * 0.15)
    return round(max(0.0, min(1.0, raw)), 4)


def _normalize_secret(value: str, field_name: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be a nonempty string")
    if not _has_no_control_characters(value):
        raise ValueError(f"{field_name} must not contain control characters")
    normalized = normalize_secret_value(value)
    if not normalized:
        raise ValueError(f"{field_name} must be a nonempty string")
    if not _has_no_control_characters(normalized):
        raise ValueError(f"{field_name} must not contain control characters")
    if is_placeholder_secret_value(normalized):
        raise ValueError(f"{field_name} must be a real credential, not a placeholder")
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
    with request.urlopen(
        url,
        timeout=get_settings().live_http_timeout_seconds,
    ) as response:
        return json.loads(response.read().decode("utf-8"))


def _has_no_control_characters(value: str) -> bool:
    return all(ord(character) >= 32 and ord(character) != 127 for character in value)
