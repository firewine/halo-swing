"""Halo Swing MCP server entrypoint."""

from typing import Any

from mcp.server.fastmcp import FastMCP

from halo_swing_mcp import MCP_SERVER_NAME
from halo_swing_mcp.audit import append_tool_audit_event
from halo_swing_mcp.tools.audit_tools import (
    get_audit_log as get_audit_log_payload,
    get_audit_summary as get_audit_summary_payload,
)
from halo_swing_mcp.tools.health import health_check as health_check_payload
from halo_swing_mcp.tools.market import (
    calculate_indicators as calculate_indicators_payload,
    get_event_calendar as get_event_calendar_payload,
    get_macro_snapshot as get_macro_snapshot_payload,
    get_market_snapshot as get_market_snapshot_payload,
    get_news_bundle as get_news_bundle_payload,
    render_chart as render_chart_payload,
)
from halo_swing_mcp.tools.recording import (
    evaluate_recorded_score_performance as evaluate_recorded_score_performance_payload,
    label_signal_outcome as label_signal_outcome_payload,
    record_signal as record_signal_payload,
)
from halo_swing_mcp.tools.scoring import (
    compare_champion_challenger as compare_champion_challenger_payload,
    evaluate_position as evaluate_position_payload,
    generate_trade_guide as generate_trade_guide_payload,
    score_leverage_swing as score_leverage_swing_payload,
    suggest_weight_update as suggest_weight_update_payload,
)

mcp = FastMCP(MCP_SERVER_NAME)


def _audited_tool_call(
    command_name: str,
    input_payload: dict[str, Any],
    result: dict[str, Any],
) -> dict[str, Any]:
    audit_log_path = input_payload.get("audit_log_path")
    append_tool_audit_event(
        command_name=command_name,
        input_payload=input_payload,
        result=result,
        outcome="success",
        actor="mcp_server",
        audit_log_path=audit_log_path if isinstance(audit_log_path, str) else None,
    )
    return result


@mcp.tool()
def health_check() -> dict[str, Any]:
    """Return deterministic server health and P0 capability metadata."""

    return _audited_tool_call("health_check", {}, health_check_payload())


@mcp.tool()
def get_audit_log(
    audit_log_path: str | None = None,
    limit: int = 100,
    action: str | None = None,
    resource_type: str | None = None,
    resource_id: str | None = None,
    outcome: str | None = None,
) -> dict[str, Any]:
    """Return recent structured audit events."""

    return _audited_tool_call(
        "get_audit_log",
        {
            "audit_log_path": audit_log_path,
            "limit": limit,
            "action": action,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "outcome": outcome,
        },
        get_audit_log_payload(
            audit_log_path=audit_log_path,
            limit=limit,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            outcome=outcome,
        ),
    )


@mcp.tool()
def get_audit_summary(audit_log_path: str | None = None) -> dict[str, Any]:
    """Return aggregate audit log counts."""

    return _audited_tool_call(
        "get_audit_summary",
        {"audit_log_path": audit_log_path},
        get_audit_summary_payload(audit_log_path=audit_log_path),
    )


@mcp.tool()
def get_market_snapshot(symbols: list[str] | None = None) -> dict[str, Any]:
    """Return fixture-backed market trend snapshots."""

    return _audited_tool_call(
        "get_market_snapshot",
        {"symbols": symbols},
        get_market_snapshot_payload(symbols=symbols),
    )


@mcp.tool()
def get_macro_snapshot() -> dict[str, Any]:
    """Return fixture-backed macro state."""

    return _audited_tool_call("get_macro_snapshot", {}, get_macro_snapshot_payload())


@mcp.tool()
def get_event_calendar(days: int = 14) -> dict[str, Any]:
    """Return fixture-backed event calendar."""

    return _audited_tool_call(
        "get_event_calendar",
        {"days": days},
        get_event_calendar_payload(days=days),
    )


@mcp.tool()
def get_news_bundle(topic: str = "macro") -> dict[str, Any]:
    """Return fixture-backed evidence cards."""

    return _audited_tool_call(
        "get_news_bundle",
        {"topic": topic},
        get_news_bundle_payload(topic=topic),
    )


@mcp.tool()
def calculate_indicators(symbol: str = "QQQ", timeframe: str = "1d") -> dict[str, Any]:
    """Calculate deterministic technical indicators."""

    return _audited_tool_call(
        "calculate_indicators",
        {"symbol": symbol, "timeframe": timeframe},
        calculate_indicators_payload(symbol=symbol, timeframe=timeframe),
    )


@mcp.tool()
def render_chart(
    symbol: str = "QQQ",
    timeframe: str = "1d",
    output_dir: str | None = None,
) -> dict[str, Any]:
    """Render a dependency-free PNG chart."""

    return _audited_tool_call(
        "render_chart",
        {"symbol": symbol, "timeframe": timeframe, "output_dir": output_dir},
        render_chart_payload(symbol=symbol, timeframe=timeframe, output_dir=output_dir),
    )


@mcp.tool()
def score_leverage_swing(
    asset: str = "TQQQ",
    timeframe: str = "swing_3d_10d",
) -> dict[str, Any]:
    """Score a leveraged ETF or BTC swing candidate."""

    return _audited_tool_call(
        "score_leverage_swing",
        {"asset": asset, "timeframe": timeframe},
        score_leverage_swing_payload(asset=asset, timeframe=timeframe),
    )


@mcp.tool()
def generate_trade_guide(
    asset: str = "TQQQ",
    timeframe: str = "swing_3d_10d",
) -> dict[str, Any]:
    """Generate entry, stop, take-profit, and invalidation guidance."""

    return _audited_tool_call(
        "generate_trade_guide",
        {"asset": asset, "timeframe": timeframe},
        generate_trade_guide_payload(asset=asset, timeframe=timeframe),
    )


@mcp.tool()
def evaluate_position(
    asset: str = "TQQQ",
    entry_price: float | None = None,
    current_price: float | None = None,
    size: float | None = None,
) -> dict[str, Any]:
    """Evaluate hold, trim, exit, or stop guidance for an open position."""

    return _audited_tool_call(
        "evaluate_position",
        {
            "asset": asset,
            "entry_price": entry_price,
            "current_price": current_price,
            "size": size,
        },
        evaluate_position_payload(
            asset=asset,
            entry_price=entry_price,
            current_price=current_price,
            size=size,
        ),
    )


@mcp.tool()
def record_signal(
    signal: dict[str, Any] | None = None,
    ledger_path: str | None = None,
) -> dict[str, Any]:
    """Record a signal in the local runtime ledger."""

    return _audited_tool_call(
        "record_signal",
        {"signal": signal, "ledger_path": ledger_path},
        record_signal_payload(signal=signal, ledger_path=ledger_path),
    )


@mcp.tool()
def label_signal_outcome(
    signal_id: str | None = None,
    price_path: list[float] | None = None,
    stop_loss_pct: float = 0.05,
    take_profit_pct: float = 0.10,
    time_barrier_days: int = 10,
    ledger_path: str | None = None,
) -> dict[str, Any]:
    """Label a signal outcome with triple-barrier logic."""

    return _audited_tool_call(
        "label_signal_outcome",
        {
            "signal_id": signal_id,
            "price_path": price_path,
            "stop_loss_pct": stop_loss_pct,
            "take_profit_pct": take_profit_pct,
            "time_barrier_days": time_barrier_days,
            "ledger_path": ledger_path,
        },
        label_signal_outcome_payload(
            signal_id=signal_id,
            price_path=price_path,
            stop_loss_pct=stop_loss_pct,
            take_profit_pct=take_profit_pct,
            time_barrier_days=time_barrier_days,
            ledger_path=ledger_path,
        ),
    )


@mcp.tool()
def evaluate_score_performance(ledger_path: str | None = None) -> dict[str, Any]:
    """Evaluate score calibration and realized-R performance."""

    return _audited_tool_call(
        "evaluate_score_performance",
        {"ledger_path": ledger_path},
        evaluate_recorded_score_performance_payload(ledger_path=ledger_path),
    )


@mcp.tool()
def suggest_weight_update() -> dict[str, Any]:
    """Return a challenger config proposal without promotion."""

    return _audited_tool_call("suggest_weight_update", {}, suggest_weight_update_payload())


@mcp.tool()
def compare_champion_challenger() -> dict[str, Any]:
    """Compare champion and challenger configs on fixture outcomes."""

    return _audited_tool_call(
        "compare_champion_challenger",
        {},
        compare_champion_challenger_payload(),
    )


def main() -> None:
    mcp.run("stdio")


if __name__ == "__main__":
    main()
