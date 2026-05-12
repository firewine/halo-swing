"""Shared tool registry for MCP server, CLI harness, and health metadata."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from halo_swing_mcp import MCP_SERVER_NAME, PROJECT_NAME, __version__
from halo_swing_mcp.binance_btc import (
    check_binance_coinm_connectivity,
    execute_btc_order,
    get_binance_coinm_account_snapshot,
    normalize_binance_coinm_account_snapshot,
    preview_btc_order,
)
from halo_swing_mcp.risk_settings import (
    get_btc_risk_settings,
    get_btc_risk_status,
    reset_btc_daily_risk_state,
    update_btc_risk_settings,
)
from halo_swing_mcp.secret_store import (
    get_binance_credentials_status,
    save_binance_credentials,
)
from halo_swing_mcp.tools.audit_tools import get_audit_log, get_audit_summary
from halo_swing_mcp.tools.market import (
    calculate_indicators,
    create_document_evidence_card,
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
from halo_swing_mcp.tools.readiness import get_integration_readiness
from halo_swing_mcp.tools.reporting import (
    generate_cron_prompt_pack,
    generate_latest_signal_report,
    generate_position_review_report,
)
from halo_swing_mcp.tools.runtime import get_runtime_status, record_runtime_checkpoint
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
    ToolSpec(
        "create_document_evidence_card",
        create_document_evidence_card,
        "Normalize a document summary into an evidence card.",
    ),
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
    ToolSpec(
        "generate_latest_signal_report",
        generate_latest_signal_report,
        "Generate a Hermes-facing latest signal report.",
    ),
    ToolSpec(
        "generate_position_review_report",
        generate_position_review_report,
        "Generate a Hermes-facing open-position review report.",
    ),
    ToolSpec(
        "generate_cron_prompt_pack",
        generate_cron_prompt_pack,
        "Generate offline Hermes cron prompt templates.",
    ),
    ToolSpec(
        "get_integration_readiness",
        get_integration_readiness,
        "Return offline readiness for blocked integration gates.",
    ),
    ToolSpec("get_audit_log", get_audit_log, "Return recent audit events."),
    ToolSpec("get_audit_summary", get_audit_summary, "Return audit event summary."),
    ToolSpec("get_runtime_status", get_runtime_status, "Return runtime guard status."),
    ToolSpec(
        "record_runtime_checkpoint",
        record_runtime_checkpoint,
        "Append a local runtime checkpoint snapshot.",
    ),
    ToolSpec("get_btc_risk_settings", get_btc_risk_settings, "Return BTC risk settings."),
    ToolSpec(
        "update_btc_risk_settings",
        update_btc_risk_settings,
        "Update BTC risk settings.",
    ),
    ToolSpec("get_btc_risk_status", get_btc_risk_status, "Return BTC risk status."),
    ToolSpec(
        "reset_btc_daily_risk_state",
        reset_btc_daily_risk_state,
        "Reset BTC daily risk counters.",
    ),
    ToolSpec(
        "save_binance_credentials",
        save_binance_credentials,
        "Encrypt and save Binance API credentials.",
    ),
    ToolSpec(
        "get_binance_credentials_status",
        get_binance_credentials_status,
        "Return encrypted Binance credential status.",
    ),
    ToolSpec(
        "check_binance_coinm_connectivity",
        check_binance_coinm_connectivity,
        "Read Binance COIN-M server time and BTCUSD_PERP metadata.",
    ),
    ToolSpec(
        "get_binance_coinm_account_snapshot",
        get_binance_coinm_account_snapshot,
        "Read Binance COIN-M balance and BTC position.",
    ),
    ToolSpec(
        "normalize_binance_coinm_account_snapshot",
        normalize_binance_coinm_account_snapshot,
        "Normalize caller-supplied Binance COIN-M account payloads.",
    ),
    ToolSpec("preview_btc_order", preview_btc_order, "Preview BTCUSD_PERP COIN-M order."),
    ToolSpec("execute_btc_order", execute_btc_order, "Submit guarded BTCUSD_PERP order."),
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
