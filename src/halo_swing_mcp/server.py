"""Halo Swing MCP server entrypoint."""

from typing import Any

from mcp.server.fastmcp import FastMCP

from halo_swing_mcp import MCP_SERVER_NAME
from halo_swing_mcp.audit import append_tool_audit_event
from halo_swing_mcp.tool_registry import call_tool

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


def _call_registered_tool(
    command_name: str,
    input_payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload = input_payload or {}
    return _audited_tool_call(command_name, payload, call_tool(command_name, payload))


@mcp.tool()
def health_check() -> dict[str, Any]:
    """Return deterministic server health and P0 capability metadata."""

    return _call_registered_tool("health_check")


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
        call_tool(
            "get_audit_log",
            {
                "audit_log_path": audit_log_path,
                "limit": limit,
                "action": action,
                "resource_type": resource_type,
                "resource_id": resource_id,
                "outcome": outcome,
            },
        ),
    )


@mcp.tool()
def get_audit_summary(audit_log_path: str | None = None) -> dict[str, Any]:
    """Return aggregate audit log counts."""

    return _audited_tool_call(
        "get_audit_summary",
        {"audit_log_path": audit_log_path},
        call_tool("get_audit_summary", {"audit_log_path": audit_log_path}),
    )


@mcp.tool()
def get_runtime_status(
    audit_log_path: str | None = None,
    ledger_path: str | None = None,
    apply_retention: bool = False,
    max_records: int | None = None,
    max_bytes: int | None = None,
    failure_window: int | None = None,
    failure_threshold: int | None = None,
) -> dict[str, Any]:
    """Return local runtime guard status and optional JSONL retention result."""

    payload = {
        "audit_log_path": audit_log_path,
        "ledger_path": ledger_path,
        "apply_retention": apply_retention,
        "max_records": max_records,
        "max_bytes": max_bytes,
        "failure_window": failure_window,
        "failure_threshold": failure_threshold,
    }
    return _audited_tool_call(
        "get_runtime_status",
        payload,
        call_tool("get_runtime_status", payload),
    )


@mcp.tool()
def record_runtime_checkpoint(
    checkpoint_path: str | None = None,
    audit_log_path: str | None = None,
    ledger_path: str | None = None,
    run_id: str | None = None,
    include_readiness: bool = True,
) -> dict[str, Any]:
    """Append a local runtime checkpoint snapshot without scheduling work."""

    payload = {
        "checkpoint_path": checkpoint_path,
        "audit_log_path": audit_log_path,
        "ledger_path": ledger_path,
        "run_id": run_id,
        "include_readiness": include_readiness,
    }
    return _audited_tool_call(
        "record_runtime_checkpoint",
        payload,
        call_tool("record_runtime_checkpoint", payload),
    )


@mcp.tool()
def get_market_snapshot(symbols: list[str] | None = None) -> dict[str, Any]:
    """Return fixture-backed market trend snapshots."""

    return _audited_tool_call(
        "get_market_snapshot",
        {"symbols": symbols},
        call_tool("get_market_snapshot", {"symbols": symbols}),
    )


@mcp.tool()
def get_macro_snapshot() -> dict[str, Any]:
    """Return fixture-backed macro state."""

    return _call_registered_tool("get_macro_snapshot")


@mcp.tool()
def get_event_calendar(days: int = 14) -> dict[str, Any]:
    """Return fixture-backed event calendar."""

    return _audited_tool_call(
        "get_event_calendar",
        {"days": days},
        call_tool("get_event_calendar", {"days": days}),
    )


@mcp.tool()
def get_news_bundle(topic: str = "macro") -> dict[str, Any]:
    """Return fixture-backed evidence cards."""

    return _audited_tool_call(
        "get_news_bundle",
        {"topic": topic},
        call_tool("get_news_bundle", {"topic": topic}),
    )


@mcp.tool()
def create_document_evidence_card(
    summary: str,
    artifact_ref: str,
    ref_type: str = "PDF",
    modality: str = "pdf_summary",
    evidence_id: str = "manual_document_summary",
    category: str = "manual_document",
    source: str = "manual:document_summary",
    observed_at: str | None = None,
    asset_scope: list[str] | None = None,
    bias: str = "neutral",
    strength: float = 0.5,
    confidence: float = 0.5,
    buy_impact: str = "context_only",
    sell_impact: str = "context_only",
    invalidating_condition: str = "Document summary becomes stale or contradicted.",
) -> dict[str, Any]:
    """Normalize a caller-supplied document summary into an evidence card."""

    payload = {
        "summary": summary,
        "artifact_ref": artifact_ref,
        "ref_type": ref_type,
        "modality": modality,
        "evidence_id": evidence_id,
        "category": category,
        "source": source,
        "observed_at": observed_at,
        "asset_scope": asset_scope,
        "bias": bias,
        "strength": strength,
        "confidence": confidence,
        "buy_impact": buy_impact,
        "sell_impact": sell_impact,
        "invalidating_condition": invalidating_condition,
    }
    return _audited_tool_call(
        "create_document_evidence_card",
        payload,
        call_tool("create_document_evidence_card", payload),
    )


@mcp.tool()
def calculate_indicators(symbol: str = "QQQ", timeframe: str = "1d") -> dict[str, Any]:
    """Calculate deterministic technical indicators."""

    return _audited_tool_call(
        "calculate_indicators",
        {"symbol": symbol, "timeframe": timeframe},
        call_tool("calculate_indicators", {"symbol": symbol, "timeframe": timeframe}),
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
        call_tool(
            "render_chart",
            {"symbol": symbol, "timeframe": timeframe, "output_dir": output_dir},
        ),
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
        call_tool("score_leverage_swing", {"asset": asset, "timeframe": timeframe}),
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
        call_tool("generate_trade_guide", {"asset": asset, "timeframe": timeframe}),
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
        call_tool(
            "evaluate_position",
            {
                "asset": asset,
                "entry_price": entry_price,
                "current_price": current_price,
                "size": size,
            },
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
        call_tool("record_signal", {"signal": signal, "ledger_path": ledger_path}),
    )


@mcp.tool()
def label_signal_outcome(
    signal_id: str | None = None,
    price_path: list[float] | None = None,
    stop_loss_pct: float = 0.05,
    take_profit_pct: float = 0.10,
    time_barrier_days: int = 10,
    ledger_path: str | None = None,
    invalidated_by_event: bool = False,
    invalidating_event_id: str | None = None,
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
            "invalidated_by_event": invalidated_by_event,
            "invalidating_event_id": invalidating_event_id,
        },
        call_tool(
            "label_signal_outcome",
            {
                "signal_id": signal_id,
                "price_path": price_path,
                "stop_loss_pct": stop_loss_pct,
                "take_profit_pct": take_profit_pct,
                "time_barrier_days": time_barrier_days,
                "ledger_path": ledger_path,
                "invalidated_by_event": invalidated_by_event,
                "invalidating_event_id": invalidating_event_id,
            },
        ),
    )


@mcp.tool()
def evaluate_score_performance(
    ledger_path: str | None = None,
    days: int = 90,
    signals: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Evaluate score calibration and realized-R performance."""

    return _audited_tool_call(
        "evaluate_score_performance",
        {"ledger_path": ledger_path, "days": days, "signals": signals},
        call_tool(
            "evaluate_score_performance",
            {"ledger_path": ledger_path, "days": days, "signals": signals},
        ),
    )


@mcp.tool()
def suggest_weight_update() -> dict[str, Any]:
    """Return a challenger config proposal without promotion."""

    return _call_registered_tool("suggest_weight_update")


@mcp.tool()
def compare_champion_challenger() -> dict[str, Any]:
    """Compare champion and challenger configs on fixture outcomes."""

    return _audited_tool_call(
        "compare_champion_challenger",
        {},
        call_tool("compare_champion_challenger"),
    )


@mcp.tool()
def generate_latest_signal_report(
    asset: str = "TQQQ",
    timeframe: str = "swing_3d_10d",
    report_intent: str = "pre_market_swing_report",
    include_chart: bool = False,
    chart_timeframe: str = "1d",
    chart_output_dir: str | None = None,
    extra_evidence_cards: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Generate a deterministic Hermes-facing latest signal report."""

    payload = {
        "asset": asset,
        "timeframe": timeframe,
        "report_intent": report_intent,
        "include_chart": include_chart,
        "chart_timeframe": chart_timeframe,
        "chart_output_dir": chart_output_dir,
        "extra_evidence_cards": extra_evidence_cards,
    }
    return _audited_tool_call(
        "generate_latest_signal_report",
        payload,
        call_tool("generate_latest_signal_report", payload),
    )


@mcp.tool()
def generate_position_review_report(
    asset: str = "TQQQ",
    entry_price: float | None = None,
    current_price: float | None = None,
    size: float | None = None,
) -> dict[str, Any]:
    """Generate a deterministic Hermes-facing open-position review report."""

    payload = {
        "asset": asset,
        "entry_price": entry_price,
        "current_price": current_price,
        "size": size,
    }
    return _audited_tool_call(
        "generate_position_review_report",
        payload,
        call_tool("generate_position_review_report", payload),
    )


@mcp.tool()
def generate_cron_prompt_pack(
    asset: str = "TQQQ",
    timeframe: str = "swing_3d_10d",
    include_position_review: bool = True,
) -> dict[str, Any]:
    """Generate offline Hermes cron prompt templates without scheduling work."""

    payload = {
        "asset": asset,
        "timeframe": timeframe,
        "include_position_review": include_position_review,
    }
    return _audited_tool_call(
        "generate_cron_prompt_pack",
        payload,
        call_tool("generate_cron_prompt_pack", payload),
    )


@mcp.tool()
def get_integration_readiness(
    hermes_config_path: str | None = None,
    hermes_mcp_config_registered: bool | None = None,
    telegram_configured: bool | None = None,
    telegram_bot_token_configured: bool | None = None,
    telegram_gateway_configured: bool | None = None,
    migration_go_approved: bool = False,
    repository_go_approved: bool = False,
    binance_credentials_path: str | None = None,
    binance_passphrase_confirmed: bool | None = None,
    binance_trade_only_permission_attested: bool | None = None,
    live_order_approved: bool | None = None,
    btc_risk_settings_path: str | None = None,
    market_data_source_configured: bool | None = None,
    macro_source_configured: bool | None = None,
    news_source_configured: bool | None = None,
) -> dict[str, Any]:
    """Return offline readiness for deployment, data, and live-order gates."""

    payload = {
        "hermes_config_path": hermes_config_path,
        "hermes_mcp_config_registered": hermes_mcp_config_registered,
        "telegram_configured": telegram_configured,
        "telegram_bot_token_configured": telegram_bot_token_configured,
        "telegram_gateway_configured": telegram_gateway_configured,
        "migration_go_approved": migration_go_approved,
        "repository_go_approved": repository_go_approved,
        "binance_credentials_path": binance_credentials_path,
        "binance_passphrase_confirmed": binance_passphrase_confirmed,
        "binance_trade_only_permission_attested": binance_trade_only_permission_attested,
        "live_order_approved": live_order_approved,
        "btc_risk_settings_path": btc_risk_settings_path,
        "market_data_source_configured": market_data_source_configured,
        "macro_source_configured": macro_source_configured,
        "news_source_configured": news_source_configured,
    }
    return _audited_tool_call(
        "get_integration_readiness",
        payload,
        call_tool("get_integration_readiness", payload),
    )


@mcp.tool()
def get_integration_setup_checklist() -> dict[str, Any]:
    """Return local setup requirements for integration readiness."""

    return _call_registered_tool("get_integration_setup_checklist")


@mcp.tool()
def get_live_data_api_key_status() -> dict[str, Any]:
    """Return live data API-key readiness without network calls."""

    return _call_registered_tool("get_live_data_api_key_status")


@mcp.tool()
def validate_live_data_smoke_result(
    market_snapshot: dict[str, Any] | None = None,
    macro_snapshot: dict[str, Any] | None = None,
    news_bundle: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Validate live data smoke outputs without calling networks."""

    payload = {
        "market_snapshot": market_snapshot,
        "macro_snapshot": macro_snapshot,
        "news_bundle": news_bundle,
    }
    return _audited_tool_call(
        "validate_live_data_smoke_result",
        payload,
        call_tool("validate_live_data_smoke_result", payload),
    )


@mcp.tool()
def run_live_data_smoke(
    symbols: list[str] | None = None,
    topic: str = "macro",
) -> dict[str, Any]:
    """Run and validate live data smoke paths."""

    payload = {"symbols": symbols, "topic": topic}
    return _audited_tool_call(
        "run_live_data_smoke",
        payload,
        call_tool("run_live_data_smoke", payload),
    )


@mcp.tool()
def run_integration_smoke(
    symbols: list[str] | None = None,
    topic: str = "macro",
) -> dict[str, Any]:
    """Run readiness and live data smoke checks."""

    payload = {"symbols": symbols, "topic": topic}
    return _audited_tool_call(
        "run_integration_smoke",
        payload,
        call_tool("run_integration_smoke", payload),
    )


@mcp.tool()
def run_live_signal_workflow_smoke(
    asset: str = "TQQQ",
    timeframe: str = "swing_3d_10d",
) -> dict[str, Any]:
    """Run live scoring/report workflow smoke checks."""

    payload = {"asset": asset, "timeframe": timeframe}
    return _audited_tool_call(
        "run_live_signal_workflow_smoke",
        payload,
        call_tool("run_live_signal_workflow_smoke", payload),
    )


@mcp.tool()
def run_live_recording_smoke(
    asset: str = "TQQQ",
    timeframe: str = "swing_3d_10d",
    ledger_path: str | None = None,
) -> dict[str, Any]:
    """Run live signal recording smoke checks."""

    payload = {
        "asset": asset,
        "timeframe": timeframe,
        "ledger_path": ledger_path,
    }
    return _audited_tool_call(
        "run_live_recording_smoke",
        payload,
        call_tool("run_live_recording_smoke", payload),
    )


@mcp.tool()
def run_api_key_pipeline_smoke(
    asset: str = "TQQQ",
    timeframe: str = "swing_3d_10d",
    symbols: list[str] | None = None,
    topic: str = "macro",
) -> dict[str, Any]:
    """Run API-key pipeline smoke checks."""

    payload = {
        "asset": asset,
        "timeframe": timeframe,
        "symbols": symbols,
        "topic": topic,
    }
    return _audited_tool_call(
        "run_api_key_pipeline_smoke",
        payload,
        call_tool("run_api_key_pipeline_smoke", payload),
    )


@mcp.tool()
def get_btc_risk_settings(settings_path: str | None = None) -> dict[str, Any]:
    """Return BTC COIN-M risk settings."""

    return _audited_tool_call(
        "get_btc_risk_settings",
        {"settings_path": settings_path},
        call_tool("get_btc_risk_settings", {"settings_path": settings_path}),
    )


@mcp.tool()
def update_btc_risk_settings(
    max_notional_usd_per_order: float | None = None,
    max_daily_order_count: int | None = None,
    max_daily_loss_usd: float | None = None,
    coinm_contract_size_usd: float | None = None,
    emergency_kill_switch_enabled: bool | None = None,
    settings_path: str | None = None,
) -> dict[str, Any]:
    """Update BTC COIN-M risk settings."""

    payload = {
        "max_notional_usd_per_order": max_notional_usd_per_order,
        "max_daily_order_count": max_daily_order_count,
        "max_daily_loss_usd": max_daily_loss_usd,
        "coinm_contract_size_usd": coinm_contract_size_usd,
        "emergency_kill_switch_enabled": emergency_kill_switch_enabled,
        "settings_path": settings_path,
    }
    return _audited_tool_call(
        "update_btc_risk_settings",
        payload,
        call_tool("update_btc_risk_settings", payload),
    )


@mcp.tool()
def get_btc_risk_status(
    settings_path: str | None = None,
    state_path: str | None = None,
) -> dict[str, Any]:
    """Return BTC COIN-M risk settings and daily counters."""

    payload = {"settings_path": settings_path, "state_path": state_path}
    return _audited_tool_call(
        "get_btc_risk_status",
        payload,
        call_tool("get_btc_risk_status", payload),
    )


@mcp.tool()
def reset_btc_daily_risk_state(
    daily_realized_loss_usd: float = 0.0,
    daily_order_count: int = 0,
    state_path: str | None = None,
) -> dict[str, Any]:
    """Reset BTC COIN-M daily risk counters."""

    payload = {
        "daily_realized_loss_usd": daily_realized_loss_usd,
        "daily_order_count": daily_order_count,
        "state_path": state_path,
    }
    return _audited_tool_call(
        "reset_btc_daily_risk_state",
        payload,
        call_tool("reset_btc_daily_risk_state", payload),
    )


@mcp.tool()
def save_binance_credentials(
    api_key: str,
    api_secret: str,
    passphrase: str,
    credentials_path: str | None = None,
) -> dict[str, Any]:
    """Encrypt and save Binance COIN-M API credentials locally."""

    payload = {
        "api_key": api_key,
        "api_secret": api_secret,
        "passphrase": passphrase,
        "credentials_path": credentials_path,
    }
    return _audited_tool_call(
        "save_binance_credentials",
        payload,
        call_tool("save_binance_credentials", payload),
    )


@mcp.tool()
def get_binance_credentials_status(
    credentials_path: str | None = None,
) -> dict[str, Any]:
    """Return encrypted Binance credential status without exposing secrets."""

    payload = {"credentials_path": credentials_path}
    return _audited_tool_call(
        "get_binance_credentials_status",
        payload,
        call_tool("get_binance_credentials_status", payload),
    )


@mcp.tool()
def check_binance_coinm_connectivity() -> dict[str, Any]:
    """Read Binance COIN-M server time and BTCUSD_PERP metadata."""

    return _call_registered_tool("check_binance_coinm_connectivity")


@mcp.tool()
def get_binance_coinm_account_snapshot(
    credential_passphrase: str | None = None,
    credentials_path: str | None = None,
) -> dict[str, Any]:
    """Read Binance COIN-M balance and BTC position without placing orders."""

    payload = {
        "credential_passphrase": credential_passphrase,
        "credentials_path": credentials_path,
    }
    return _audited_tool_call(
        "get_binance_coinm_account_snapshot",
        payload,
        call_tool("get_binance_coinm_account_snapshot", payload),
    )


@mcp.tool()
def normalize_binance_coinm_account_snapshot(
    balance: list[dict[str, Any]] | None = None,
    positions: list[dict[str, Any]] | None = None,
    as_of: str | None = None,
    coinm_contract_size_usd: float | None = None,
) -> dict[str, Any]:
    """Normalize caller-supplied Binance COIN-M account payloads."""

    payload = {
        "balance": balance,
        "positions": positions,
        "as_of": as_of,
        "coinm_contract_size_usd": coinm_contract_size_usd,
    }
    return _audited_tool_call(
        "normalize_binance_coinm_account_snapshot",
        payload,
        call_tool("normalize_binance_coinm_account_snapshot", payload),
    )


@mcp.tool()
def preview_btc_order(
    side: str = "BUY",
    order_type: str = "MARKET",
    quantity: str = "1",
    price: str | None = None,
    time_in_force: str | None = None,
    position_side: str | None = None,
    reduce_only: bool = False,
    client_order_id: str | None = None,
    settings_path: str | None = None,
    state_path: str | None = None,
    credentials_path: str | None = None,
    portfolio_snapshot: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Preview a BTCUSD_PERP Binance COIN-M order without submitting it."""

    payload = {
        "side": side,
        "order_type": order_type,
        "quantity": quantity,
        "price": price,
        "time_in_force": time_in_force,
        "position_side": position_side,
        "reduce_only": reduce_only,
        "client_order_id": client_order_id,
        "settings_path": settings_path,
        "state_path": state_path,
        "credentials_path": credentials_path,
        "portfolio_snapshot": portfolio_snapshot,
    }

    return _audited_tool_call(
        "preview_btc_order",
        payload,
        call_tool("preview_btc_order", payload),
    )


@mcp.tool()
def execute_btc_order(
    side: str = "BUY",
    order_type: str = "MARKET",
    quantity: str = "1",
    price: str | None = None,
    time_in_force: str | None = None,
    position_side: str | None = None,
    reduce_only: bool = False,
    client_order_id: str | None = None,
    confirm: str | None = None,
    credential_passphrase: str | None = None,
    credentials_path: str | None = None,
    settings_path: str | None = None,
    state_path: str | None = None,
) -> dict[str, Any]:
    """Submit a BTCUSD_PERP Binance COIN-M order only when live guards pass."""

    payload = {
        "side": side,
        "order_type": order_type,
        "quantity": quantity,
        "price": price,
        "time_in_force": time_in_force,
        "position_side": position_side,
        "reduce_only": reduce_only,
        "client_order_id": client_order_id,
        "confirm": confirm,
        "credential_passphrase": credential_passphrase,
        "credentials_path": credentials_path,
        "settings_path": settings_path,
        "state_path": state_path,
    }

    return _audited_tool_call(
        "execute_btc_order",
        payload,
        call_tool("execute_btc_order", payload),
    )


def main() -> None:
    mcp.run("stdio")


if __name__ == "__main__":
    main()
