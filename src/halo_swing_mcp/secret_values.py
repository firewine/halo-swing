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


def is_placeholder_secret_value(value: str) -> bool:
    """Return whether a value is a documented or generic secret placeholder."""

    normalized = value.strip().lower()
    return (
        normalized in PLACEHOLDER_SECRET_VALUES
        or (normalized.startswith("your_") and normalized.endswith("_key"))
        or (normalized.startswith("<") and normalized.endswith(">"))
    )
