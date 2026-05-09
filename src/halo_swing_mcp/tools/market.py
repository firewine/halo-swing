"""Market, macro, event, news, indicator, and chart tools."""

from __future__ import annotations

import struct
import zlib
from pathlib import Path
from typing import Any

from halo_swing_mcp.fixtures import (
    AS_OF,
    MACRO_FIXTURE,
    NEWS_FIXTURES,
    events_within_days,
    generate_ohlcv,
    resolve_asset,
    supported_assets,
)
from halo_swing_mcp.indicators import calculate_indicator_payload


def get_market_snapshot(symbols: list[str] | None = None) -> dict[str, Any]:
    """Return deterministic market trend snapshots for supported assets."""

    requested = [symbol.upper() for symbol in (symbols or ["QQQ", "SPY", "SMH", "BTC"])]
    snapshots: list[dict[str, Any]] = []
    for symbol in requested:
        indicators = calculate_indicator_payload(symbol)
        underlying, leverage = resolve_asset(symbol)
        asset_bars = generate_ohlcv(symbol, 220)
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
                    (float(latest_asset_close) / float(previous_asset_close) - 1) * 100,
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

    return {
        "as_of": AS_OF,
        "data_mode": "fixture",
        "live_data_required": False,
        "supported_assets": supported_assets(),
        "snapshots": snapshots,
    }


def get_macro_snapshot() -> dict[str, Any]:
    """Return deterministic macro state."""

    return dict(MACRO_FIXTURE)


def get_event_calendar(days: int = 14) -> dict[str, Any]:
    """Return deterministic event risk calendar."""

    events = events_within_days(days)
    highest_risk = max((event["risk_score"] for event in events), default=0.0)
    return {
        "as_of": AS_OF,
        "days": days,
        "data_mode": "fixture",
        "live_data_required": False,
        "highest_event_risk": round(highest_risk, 4),
        "events": events,
    }


def get_news_bundle(topic: str = "macro") -> dict[str, Any]:
    """Return deterministic evidence cards for a report topic."""

    normalized = topic.lower()
    if normalized in {"all", "*"}:
        cards = [dict(card) for card in NEWS_FIXTURES]
    else:
        cards = [
            dict(card)
            for card in NEWS_FIXTURES
            if normalized in card["category"] or normalized in card["source"]
        ]
        if not cards:
            cards = [dict(card) for card in NEWS_FIXTURES]

    average_strength = (
        sum(float(card["strength"]) for card in cards) / len(cards) if cards else 0.0
    )
    return {
        "as_of": AS_OF,
        "topic": topic,
        "data_mode": "fixture",
        "live_data_required": False,
        "average_strength": round(average_strength, 4),
        "evidence_cards": cards,
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

    normalized = symbol.upper()
    directory = Path(output_dir) if output_dir else Path("artifacts") / "charts"
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{normalized}_{timeframe}.png"
    bars = list(generate_ohlcv(normalized, 90))
    closes = [float(bar["close"]) for bar in bars[-60:]]
    _write_line_chart_png(path, closes)
    artifact_ref = str(path) if output_dir else str(Path("artifacts") / "charts" / path.name)

    return {
        "as_of": AS_OF,
        "symbol": normalized,
        "timeframe": timeframe,
        "format": "png",
        "path": str(path),
        "artifact_ref": {
            "ref_type": "CHART",
            "ref": artifact_ref,
            "metadata": {
                "bars": len(closes),
                "renderer": "stdlib_png",
            },
        },
        "live_data_required": False,
    }


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
