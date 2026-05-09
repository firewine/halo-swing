"""BTC COIN-M futures risk settings and local daily risk state."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from halo_swing_mcp.config import get_settings


@dataclass(frozen=True)
class BtcRiskSettings:
    max_notional_usd_per_order: float = 100.0
    max_daily_order_count: int = 3
    max_daily_loss_usd: float = 50.0
    coinm_contract_size_usd: float = 100.0


@dataclass(frozen=True)
class BtcRiskState:
    trade_date: str
    daily_order_count: int = 0
    daily_realized_loss_usd: float = 0.0


def utc_trade_date() -> str:
    return datetime.now(timezone.utc).date().isoformat()


def get_btc_risk_settings(settings_path: str | None = None) -> dict[str, Any]:
    """Return current BTC COIN-M risk settings."""

    settings = load_btc_risk_settings(settings_path)
    return {
        **asdict(settings),
        "settings_path": str(resolve_settings_path(settings_path)),
        "live_data_required": False,
    }


def update_btc_risk_settings(
    max_notional_usd_per_order: float | None = None,
    max_daily_order_count: int | None = None,
    max_daily_loss_usd: float | None = None,
    coinm_contract_size_usd: float | None = None,
    settings_path: str | None = None,
) -> dict[str, Any]:
    """Update BTC COIN-M risk settings and persist them as ignored local state."""

    current = load_btc_risk_settings(settings_path)
    updated = replace(
        current,
        max_notional_usd_per_order=(
            float(max_notional_usd_per_order)
            if max_notional_usd_per_order is not None
            else current.max_notional_usd_per_order
        ),
        max_daily_order_count=(
            int(max_daily_order_count)
            if max_daily_order_count is not None
            else current.max_daily_order_count
        ),
        max_daily_loss_usd=(
            float(max_daily_loss_usd)
            if max_daily_loss_usd is not None
            else current.max_daily_loss_usd
        ),
        coinm_contract_size_usd=(
            float(coinm_contract_size_usd)
            if coinm_contract_size_usd is not None
            else current.coinm_contract_size_usd
        ),
    )
    validate_btc_risk_settings(updated)
    path = resolve_settings_path(settings_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(asdict(updated), indent=2, sort_keys=True), encoding="utf-8")
    return get_btc_risk_settings(str(path))


def get_btc_risk_status(
    settings_path: str | None = None,
    state_path: str | None = None,
) -> dict[str, Any]:
    """Return current settings and daily state."""

    settings = load_btc_risk_settings(settings_path)
    state = load_btc_risk_state(state_path)
    return {
        "settings": get_btc_risk_settings(settings_path),
        "state": {
            **asdict(state),
            "state_path": str(resolve_state_path(state_path)),
        },
        "remaining_daily_order_count": max(
            settings.max_daily_order_count - state.daily_order_count,
            0,
        ),
        "remaining_daily_loss_usd": max(
            settings.max_daily_loss_usd - state.daily_realized_loss_usd,
            0.0,
        ),
        "live_data_required": False,
    }


def reset_btc_daily_risk_state(
    daily_realized_loss_usd: float = 0.0,
    daily_order_count: int = 0,
    state_path: str | None = None,
) -> dict[str, Any]:
    """Reset local daily order/loss counters."""

    state = BtcRiskState(
        trade_date=utc_trade_date(),
        daily_order_count=int(daily_order_count),
        daily_realized_loss_usd=float(daily_realized_loss_usd),
    )
    if state.daily_order_count < 0:
        raise ValueError("daily_order_count must be non-negative.")
    if state.daily_realized_loss_usd < 0:
        raise ValueError("daily_realized_loss_usd must be non-negative.")
    path = resolve_state_path(state_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(asdict(state), indent=2, sort_keys=True), encoding="utf-8")
    return {
        **asdict(state),
        "state_path": str(path),
        "live_data_required": False,
    }


def load_btc_risk_settings(settings_path: str | None = None) -> BtcRiskSettings:
    path = resolve_settings_path(settings_path)
    if not path.exists():
        return BtcRiskSettings()
    payload = json.loads(path.read_text(encoding="utf-8"))
    settings = BtcRiskSettings(
        max_notional_usd_per_order=float(payload["max_notional_usd_per_order"]),
        max_daily_order_count=int(payload["max_daily_order_count"]),
        max_daily_loss_usd=float(payload["max_daily_loss_usd"]),
        coinm_contract_size_usd=float(payload["coinm_contract_size_usd"]),
    )
    validate_btc_risk_settings(settings)
    return settings


def validate_btc_risk_settings(settings: BtcRiskSettings) -> None:
    if settings.max_notional_usd_per_order <= 0:
        raise ValueError("max_notional_usd_per_order must be positive.")
    if settings.max_daily_order_count < 1:
        raise ValueError("max_daily_order_count must be at least 1.")
    if settings.max_daily_loss_usd <= 0:
        raise ValueError("max_daily_loss_usd must be positive.")
    if settings.coinm_contract_size_usd <= 0:
        raise ValueError("coinm_contract_size_usd must be positive.")


def load_btc_risk_state(state_path: str | None = None) -> BtcRiskState:
    path = resolve_state_path(state_path)
    today = utc_trade_date()
    if not path.exists():
        return BtcRiskState(trade_date=today)
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("trade_date") != today:
        return BtcRiskState(trade_date=today)
    return BtcRiskState(
        trade_date=str(payload["trade_date"]),
        daily_order_count=int(payload.get("daily_order_count", 0)),
        daily_realized_loss_usd=float(payload.get("daily_realized_loss_usd", 0.0)),
    )


def validate_btc_order_limits(
    estimated_notional_usd: float,
    settings_path: str | None = None,
    state_path: str | None = None,
) -> dict[str, Any]:
    """Return risk gate result for one proposed BTC COIN-M order."""

    settings = load_btc_risk_settings(settings_path)
    state = load_btc_risk_state(state_path)
    checks = {
        "per_order_notional_ok": estimated_notional_usd
        <= settings.max_notional_usd_per_order,
        "daily_order_count_ok": state.daily_order_count
        < settings.max_daily_order_count,
        "daily_loss_ok": state.daily_realized_loss_usd < settings.max_daily_loss_usd,
    }
    blocked_reasons = [name for name, valid in checks.items() if not valid]
    return {
        "valid": not blocked_reasons,
        "blocked_reasons": blocked_reasons,
        "estimated_notional_usd": round(estimated_notional_usd, 4),
        "settings": asdict(settings),
        "state": asdict(state),
        "checks": checks,
    }


def record_btc_order_submission(
    estimated_notional_usd: float,
    state_path: str | None = None,
) -> dict[str, Any]:
    """Increment local daily order count after a submitted order."""

    state = load_btc_risk_state(state_path)
    updated = replace(state, daily_order_count=state.daily_order_count + 1)
    path = resolve_state_path(state_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(asdict(updated), indent=2, sort_keys=True), encoding="utf-8")
    return {
        **asdict(updated),
        "last_order_estimated_notional_usd": round(estimated_notional_usd, 4),
        "state_path": str(path),
    }


def resolve_settings_path(settings_path: str | None = None) -> Path:
    return Path(settings_path or get_settings().btc_risk_settings_path)


def resolve_state_path(state_path: str | None = None) -> Path:
    return Path(state_path or get_settings().btc_risk_state_path)
