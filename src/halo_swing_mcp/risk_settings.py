"""BTC COIN-M futures risk settings and local daily risk state."""

from __future__ import annotations

import json
import math
import os
from dataclasses import asdict, dataclass, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from halo_swing_mcp.config import get_settings


BTC_RISK_SETTINGS_PATH_ENV = "HALO_SWING_BTC_RISK_SETTINGS_PATH"
BTC_RISK_STATE_PATH_ENV = "HALO_SWING_BTC_RISK_STATE_PATH"


@dataclass(frozen=True)
class BtcRiskSettings:
    max_notional_usd_per_order: float = 100.0
    max_daily_order_count: int = 3
    max_daily_loss_usd: float = 50.0
    coinm_contract_size_usd: float = 100.0
    emergency_kill_switch_enabled: bool = False


@dataclass(frozen=True)
class BtcRiskState:
    trade_date: str
    daily_order_count: int = 0
    daily_realized_loss_usd: float = 0.0


def utc_trade_date() -> str:
    return datetime.now(timezone.utc).date().isoformat()


def get_btc_risk_settings(settings_path: str | None = None) -> dict[str, Any]:
    """Return current BTC COIN-M risk settings."""

    normalized_settings_path = _normalize_optional_path(settings_path, "settings_path")
    settings = load_btc_risk_settings(normalized_settings_path)
    return {
        **asdict(settings),
        "settings_path": str(resolve_settings_path(normalized_settings_path)),
        "live_data_required": False,
    }


def update_btc_risk_settings(
    max_notional_usd_per_order: float | None = None,
    max_daily_order_count: int | None = None,
    max_daily_loss_usd: float | None = None,
    coinm_contract_size_usd: float | None = None,
    emergency_kill_switch_enabled: bool | None = None,
    settings_path: str | None = None,
) -> dict[str, Any]:
    """Update BTC COIN-M risk settings and persist them as ignored local state."""

    normalized_settings_path = _normalize_optional_path(settings_path, "settings_path")
    current = load_btc_risk_settings(normalized_settings_path)
    normalized_max_notional = _normalize_optional_positive_finite_number(
        max_notional_usd_per_order,
        "max_notional_usd_per_order",
    )
    normalized_daily_order_count = _normalize_optional_positive_integer(
        max_daily_order_count,
        "max_daily_order_count",
    )
    normalized_daily_loss = _normalize_optional_positive_finite_number(
        max_daily_loss_usd,
        "max_daily_loss_usd",
    )
    normalized_contract_size = _normalize_optional_positive_finite_number(
        coinm_contract_size_usd,
        "coinm_contract_size_usd",
    )
    normalized_kill_switch = _normalize_optional_boolean(
        emergency_kill_switch_enabled,
        "emergency_kill_switch_enabled",
    )
    updated = replace(
        current,
        max_notional_usd_per_order=(
            normalized_max_notional
            if normalized_max_notional is not None
            else current.max_notional_usd_per_order
        ),
        max_daily_order_count=(
            normalized_daily_order_count
            if normalized_daily_order_count is not None
            else current.max_daily_order_count
        ),
        max_daily_loss_usd=(
            normalized_daily_loss
            if normalized_daily_loss is not None
            else current.max_daily_loss_usd
        ),
        coinm_contract_size_usd=(
            normalized_contract_size
            if normalized_contract_size is not None
            else current.coinm_contract_size_usd
        ),
        emergency_kill_switch_enabled=(
            normalized_kill_switch
            if normalized_kill_switch is not None
            else current.emergency_kill_switch_enabled
        ),
    )
    validate_btc_risk_settings(updated)
    path = resolve_settings_path(normalized_settings_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(asdict(updated), indent=2, sort_keys=True), encoding="utf-8")
    return get_btc_risk_settings(str(path))


def get_btc_risk_status(
    settings_path: str | None = None,
    state_path: str | None = None,
) -> dict[str, Any]:
    """Return current settings and daily state."""

    normalized_settings_path = _normalize_optional_path(settings_path, "settings_path")
    normalized_state_path = _normalize_optional_path(state_path, "state_path")
    settings = load_btc_risk_settings(normalized_settings_path)
    state = load_btc_risk_state(normalized_state_path)
    return {
        "settings": get_btc_risk_settings(normalized_settings_path),
        "state": {
            **asdict(state),
            "state_path": str(resolve_state_path(normalized_state_path)),
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

    normalized_loss = _normalize_non_negative_finite_number(
        daily_realized_loss_usd,
        "daily_realized_loss_usd",
    )
    normalized_order_count = _normalize_non_negative_integer(
        daily_order_count,
        "daily_order_count",
    )
    normalized_state_path = _normalize_optional_path(state_path, "state_path")
    state = BtcRiskState(
        trade_date=utc_trade_date(),
        daily_order_count=normalized_order_count,
        daily_realized_loss_usd=normalized_loss,
    )
    path = resolve_state_path(normalized_state_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(asdict(state), indent=2, sort_keys=True), encoding="utf-8")
    return {
        **asdict(state),
        "state_path": str(path),
        "live_data_required": False,
    }


def load_btc_risk_settings(settings_path: str | None = None) -> BtcRiskSettings:
    normalized_settings_path = _normalize_optional_path(settings_path, "settings_path")
    path = resolve_settings_path(normalized_settings_path)
    if not path.exists():
        return BtcRiskSettings()
    payload = json.loads(path.read_text(encoding="utf-8"))
    settings = BtcRiskSettings(
        max_notional_usd_per_order=_normalize_positive_finite_number(
            payload["max_notional_usd_per_order"],
            "max_notional_usd_per_order",
        ),
        max_daily_order_count=_normalize_positive_integer(
            payload["max_daily_order_count"],
            "max_daily_order_count",
        ),
        max_daily_loss_usd=_normalize_positive_finite_number(
            payload["max_daily_loss_usd"],
            "max_daily_loss_usd",
        ),
        coinm_contract_size_usd=_normalize_positive_finite_number(
            payload["coinm_contract_size_usd"],
            "coinm_contract_size_usd",
        ),
        emergency_kill_switch_enabled=_normalize_boolean(
            payload.get("emergency_kill_switch_enabled", False),
            "emergency_kill_switch_enabled",
        ),
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
    normalized_state_path = _normalize_optional_path(state_path, "state_path")
    path = resolve_state_path(normalized_state_path)
    today = utc_trade_date()
    if not path.exists():
        return BtcRiskState(trade_date=today)
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("trade_date") != today:
        return BtcRiskState(trade_date=today)
    return BtcRiskState(
        trade_date=str(payload["trade_date"]),
        daily_order_count=_normalize_non_negative_integer(
            payload.get("daily_order_count", 0),
            "daily_order_count",
        ),
        daily_realized_loss_usd=_normalize_non_negative_finite_number(
            payload.get("daily_realized_loss_usd", 0.0),
            "daily_realized_loss_usd",
        ),
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
        "emergency_kill_switch_off": not settings.emergency_kill_switch_enabled,
    }
    blocked_reasons = [name for name, valid in checks.items() if not valid]
    if "emergency_kill_switch_off" in blocked_reasons:
        blocked_reasons.remove("emergency_kill_switch_off")
        blocked_reasons.append("emergency_kill_switch_enabled")
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
    if settings_path is not None:
        return Path(_normalize_path(settings_path, "settings_path"))
    if BTC_RISK_SETTINGS_PATH_ENV in os.environ:
        return Path(
            _normalize_path(
                os.environ[BTC_RISK_SETTINGS_PATH_ENV],
                BTC_RISK_SETTINGS_PATH_ENV,
            )
        )
    return Path(
        _normalize_path(
            get_settings().btc_risk_settings_path,
            "settings.btc_risk_settings_path",
        )
    )


def resolve_state_path(state_path: str | None = None) -> Path:
    if state_path is not None:
        return Path(_normalize_path(state_path, "state_path"))
    if BTC_RISK_STATE_PATH_ENV in os.environ:
        return Path(
            _normalize_path(
                os.environ[BTC_RISK_STATE_PATH_ENV],
                BTC_RISK_STATE_PATH_ENV,
            )
        )
    return Path(
        _normalize_path(
            get_settings().btc_risk_state_path,
            "settings.btc_risk_state_path",
        )
    )


def _normalize_optional_path(value: str | None, field_name: str) -> str | None:
    if value is None:
        return None
    return _normalize_path(value, field_name)


def _normalize_path(value: Any, field_name: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be a nonempty string")
    if not _has_no_control_characters(value):
        raise ValueError(f"{field_name} must not contain control characters")
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{field_name} must be a nonempty string")
    return normalized


def _has_no_control_characters(value: str) -> bool:
    return all(ord(character) >= 32 and ord(character) != 127 for character in value)


def _normalize_boolean(value: bool, field_name: str) -> bool:
    if type(value) is not bool:
        raise ValueError(f"{field_name} must be a boolean")
    return value


def _normalize_optional_boolean(value: bool | None, field_name: str) -> bool | None:
    if value is None:
        return None
    return _normalize_boolean(value, field_name)


def _normalize_optional_positive_finite_number(
    value: float | int | None,
    field_name: str,
) -> float | None:
    if value is None:
        return None
    return _normalize_positive_finite_number(value, field_name)


def _normalize_positive_finite_number(value: float | int, field_name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{field_name} must be a positive finite number")
    normalized = float(value)
    if not math.isfinite(normalized) or normalized <= 0.0:
        raise ValueError(f"{field_name} must be a positive finite number")
    return normalized


def _normalize_non_negative_finite_number(value: float | int, field_name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{field_name} must be a non-negative finite number")
    normalized = float(value)
    if not math.isfinite(normalized) or normalized < 0.0:
        raise ValueError(f"{field_name} must be a non-negative finite number")
    return normalized


def _normalize_optional_positive_integer(
    value: int | None,
    field_name: str,
) -> int | None:
    if value is None:
        return None
    return _normalize_positive_integer(value, field_name)


def _normalize_positive_integer(value: int, field_name: str) -> int:
    if type(value) is not int or value < 1:
        raise ValueError(f"{field_name} must be a positive integer")
    return value


def _normalize_non_negative_integer(value: int, field_name: str) -> int:
    if type(value) is not int or value < 0:
        raise ValueError(f"{field_name} must be a non-negative integer")
    return value
