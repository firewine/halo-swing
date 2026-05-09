"""Shared tool registry for MCP server, CLI harness, and health metadata."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from halo_swing_mcp import MCP_SERVER_NAME, PROJECT_NAME, __version__
from halo_swing_mcp.binance_btc import execute_btc_order, preview_btc_order
from halo_swing_mcp.tools.audit_tools import get_audit_log, get_audit_summary
from halo_swing_mcp.tools.market import (
    calculate_indicators,
    get_event_calendar,
    get_macro_snapshot,
    get_market_snapshot,
    get_news_bundle,
    render_chart,
)
from halo_swing_mcp.tools.recording import (
    evaluate_recorded_score_performance,
    label_signal_outcome,
    record_signal,
)
from halo_swing_mcp.tools.scoring import (
    compare_champion_challenger,
    evaluate_position,
    generate_trade_guide,
    score_leverage_swing,
    suggest_weight_update,
)

ToolCallable = Callable[..., dict[str, Any]]


def _health_check_tool(**_ignored: Any) -> dict[str, Any]:
    return {
        "project": PROJECT_NAME,
        "version": __version__,
        "status": "ok",
        "mcp_server": MCP_SERVER_NAME,
        "capabilities": tool_names(),
        "live_data_required": False,
    }


@dataclass(frozen=True)
class ToolSpec:
    name: str
    function: ToolCallable
    description: str
    audit_enabled: bool = True
    live_data_required: bool = False

    def call(self, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        return self.function(**(payload or {}))


TOOL_SPECS: tuple[ToolSpec, ...] = (
    ToolSpec("health_check", _health_check_tool, "Return deterministic server health."),
    ToolSpec("get_market_snapshot", get_market_snapshot, "Return market snapshots."),
    ToolSpec("get_macro_snapshot", get_macro_snapshot, "Return macro snapshot."),
    ToolSpec("get_event_calendar", get_event_calendar, "Return event calendar."),
    ToolSpec("get_news_bundle", get_news_bundle, "Return evidence cards."),
    ToolSpec("calculate_indicators", calculate_indicators, "Calculate indicators."),
    ToolSpec("render_chart", render_chart, "Render a PNG chart."),
    ToolSpec("score_leverage_swing", score_leverage_swing, "Score swing candidate."),
    ToolSpec("generate_trade_guide", generate_trade_guide, "Generate trade guide."),
    ToolSpec("evaluate_position", evaluate_position, "Evaluate open position."),
    ToolSpec("record_signal", record_signal, "Record signal to ledger."),
    ToolSpec("label_signal_outcome", label_signal_outcome, "Label signal outcome."),
    ToolSpec(
        "evaluate_score_performance",
        evaluate_recorded_score_performance,
        "Evaluate recorded score performance.",
    ),
    ToolSpec(
        "suggest_weight_update",
        suggest_weight_update,
        "Suggest challenger weights.",
    ),
    ToolSpec(
        "compare_champion_challenger",
        compare_champion_challenger,
        "Compare champion and challenger.",
    ),
    ToolSpec("get_audit_log", get_audit_log, "Return recent audit events."),
    ToolSpec("get_audit_summary", get_audit_summary, "Return audit event summary."),
    ToolSpec("preview_btc_order", preview_btc_order, "Preview BTCUSDT Binance order."),
    ToolSpec("execute_btc_order", execute_btc_order, "Submit guarded BTCUSDT order."),
)

TOOL_REGISTRY: dict[str, ToolSpec] = {spec.name: spec for spec in TOOL_SPECS}


def tool_names() -> list[str]:
    """Return canonical tool names in registry order."""

    return [spec.name for spec in TOOL_SPECS]


def get_tool_spec(name: str) -> ToolSpec:
    """Return a tool spec by name."""

    try:
        return TOOL_REGISTRY[name]
    except KeyError as exc:
        raise KeyError(f"unknown tool: {name}") from exc


def call_tool(name: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    """Call a registered tool by name."""

    return get_tool_spec(name).call(payload)
