"""Shared no-secret value helpers."""

from __future__ import annotations


PLACEHOLDER_SECRET_VALUES = {
    "your_polygon_key",
    "your_fred_key",
    "your_newsapi_key",
    "your_news_key",
    "your_api_key",
    "placeholder",
    "changeme",
    "change_me",
    "replace_me",
}


def normalize_secret_value(value: str) -> str:
    """Return a configured secret with accidental wrapping quotes removed."""

    normalized = value.strip()
    if (
        len(normalized) >= 2
        and normalized[0] == normalized[-1]
        and normalized[0] in {"'", '"'}
    ):
        normalized = normalized[1:-1].strip()
    return normalized


def is_placeholder_secret_value(value: str) -> bool:
    """Return whether a value is a documented or generic secret placeholder."""

    normalized = normalize_secret_value(value).lower()
    return (
        normalized in PLACEHOLDER_SECRET_VALUES
        or (normalized.startswith("your_") and normalized.endswith("_key"))
        or (normalized.startswith("<") and normalized.endswith(">"))
    )
