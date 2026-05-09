"""Deterministic health check tool."""

from typing import Any

from halo_swing_mcp import MCP_SERVER_NAME, PROJECT_NAME, __version__

CAPABILITIES = [
    "health_check",
    "get_market_snapshot",
    "get_macro_snapshot",
    "get_event_calendar",
    "get_news_bundle",
    "calculate_indicators",
    "render_chart",
    "score_leverage_swing",
    "generate_trade_guide",
    "evaluate_position",
    "record_signal",
    "label_signal_outcome",
    "evaluate_score_performance",
    "suggest_weight_update",
    "compare_champion_challenger",
    "get_audit_log",
    "get_audit_summary",
]


def health_check() -> dict[str, Any]:
    """Return stable server metadata for MCP and harness smoke tests."""

    return {
        "project": PROJECT_NAME,
        "version": __version__,
        "status": "ok",
        "mcp_server": MCP_SERVER_NAME,
        "capabilities": CAPABILITIES,
        "live_data_required": False,
    }
