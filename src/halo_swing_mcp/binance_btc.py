"""BTC-only Binance COIN-M futures preview and guarded execution helpers."""

from __future__ import annotations

import hashlib
import hmac
import json
import time
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Any
from urllib import error, parse, request

from halo_swing_mcp.config import get_settings
from halo_swing_mcp.risk_settings import (
    load_btc_risk_settings,
    record_btc_order_submission,
    validate_btc_order_limits,
)
from halo_swing_mcp.secret_store import (
    binance_credential_policy,
    get_binance_credentials_status,
    load_binance_credentials,
)


ALLOWED_SYMBOL = "BTCUSD_PERP"
ALLOWED_SIDES = {"BUY", "SELL"}
ALLOWED_ORDER_TYPES = {"MARKET", "LIMIT"}
ALLOWED_POSITION_SIDES = {"BOTH", "LONG", "SHORT"}
MAINNET_BASE_URL = "https://dapi.binance.com"
TESTNET_BASE_URL = "https://testnet.binancefuture.com"
ORDER_PATH = "/dapi/v1/order"
BALANCE_PATH = "/dapi/v1/balance"
EXCHANGE_INFO_PATH = "/dapi/v1/exchangeInfo"
POSITION_RISK_PATH = "/dapi/v1/positionRisk"
SERVER_TIME_PATH = "/dapi/v1/time"
LIVE_CONFIRMATION = "CONFIRM_BTC_BINANCE_COINM_ORDER"
PORTFOLIO_SNAPSHOT_SCHEMA_VERSION = "binance_coinm_portfolio_snapshot.v1"
BINANCE_RECV_WINDOW_MS_ENV = "HALO_SWING_BINANCE_RECV_WINDOW_MS"


@dataclass(frozen=True)
class BinanceOrderIntent:
    symbol: str
    side: str
    order_type: str
    quantity: str
    price: str | None = None
    time_in_force: str | None = None
    position_side: str | None = None
    reduce_only: bool = False
    client_order_id: str | None = None

    def validate(self) -> None:
        if self.symbol != ALLOWED_SYMBOL:
            raise ValueError("Binance COIN-M auto-trading is restricted to BTCUSD_PERP only.")
        if self.side not in ALLOWED_SIDES:
            raise ValueError("side must be BUY or SELL.")
        if self.order_type not in ALLOWED_ORDER_TYPES:
            raise ValueError("order_type must be MARKET or LIMIT.")
        if _positive_decimal(self.quantity) <= 0:
            raise ValueError("quantity must be positive COIN-M contract count.")
        if self.position_side and self.position_side not in ALLOWED_POSITION_SIDES:
            raise ValueError("position_side must be BOTH, LONG, or SHORT.")
        if self.reduce_only and self.position_side in {"LONG", "SHORT"}:
            raise ValueError("reduce_only cannot be sent with hedge-mode position_side.")
        if self.order_type == "LIMIT":
            if not self.price:
                raise ValueError("LIMIT orders require price.")
            if _positive_decimal(self.price) <= 0:
                raise ValueError("price must be positive.")
            if not self.time_in_force:
                raise ValueError("LIMIT orders require time_in_force.")
        if self.order_type == "MARKET" and (self.price or self.time_in_force):
            raise ValueError("MARKET orders cannot include price or time_in_force.")

    def request_params(self, timestamp_ms: int, recv_window_ms: int) -> dict[str, str]:
        self.validate()
        normalized_recv_window_ms = _normalize_recv_window_ms(
            recv_window_ms,
            "recv_window_ms",
        )
        params = {
            "symbol": self.symbol,
            "side": self.side,
            "type": self.order_type,
            "quantity": self.quantity,
            "timestamp": str(timestamp_ms),
            "recvWindow": str(normalized_recv_window_ms),
        }
        optional = {
            "price": self.price,
            "timeInForce": self.time_in_force,
            "positionSide": self.position_side,
            "newClientOrderId": self.client_order_id,
        }
        params.update({key: value for key, value in optional.items() if value is not None})
        if self.reduce_only:
            params["reduceOnly"] = "true"
        return params


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
    """Return a BTCUSD_PERP Binance COIN-M order preview without submitting it."""

    intent = _build_intent(
        side=side,
        order_type=order_type,
        quantity=quantity,
        price=price,
        time_in_force=time_in_force,
        position_side=position_side,
        reduce_only=reduce_only,
        client_order_id=client_order_id,
    )
    intent.validate()
    settings = get_settings()
    estimated_notional_usd = estimate_notional_usd(intent, settings_path=settings_path)
    risk = validate_btc_order_limits(
        estimated_notional_usd,
        settings_path=settings_path,
        state_path=state_path,
    )
    payload = {
        "status": "preview",
        "exchange": "binance_coin_m_futures",
        "symbol": intent.symbol,
        "side": intent.side,
        "order_type": intent.order_type,
        "quantity": intent.quantity,
        "quantity_unit": "contract",
        "estimated_notional_usd": round(estimated_notional_usd, 4),
        "price": intent.price,
        "time_in_force": intent.time_in_force,
        "position_side": intent.position_side,
        "reduce_only": intent.reduce_only,
        "client_order_id": intent.client_order_id,
        "testnet": settings.binance_testnet,
        "force_testnet_execution": settings.binance_force_testnet_execution,
        "live_trading_enabled": settings.binance_enable_live_trading,
        "live_data_required": False,
        "risk": risk,
        "credentials": get_binance_credentials_status(credentials_path),
        "execution_guard": {
            "schema_version": "btc_order_execution_guard.v1",
            "btc_only": True,
            "coin_m_futures_only": True,
            "order_submission_default": False,
            "network_call_before_all_guards_pass": False,
            "required_for_submission": [
                f"confirm is {LIVE_CONFIRMATION}",
                "HALO_SWING_BINANCE_ENABLE_LIVE_TRADING=true",
                "encrypted Binance credentials are configured locally",
                "credential_passphrase is provided at execution time",
                "BTC risk settings pass",
                "testnet-only policy passes",
            ],
            "requires_env_flag": "HALO_SWING_BINANCE_ENABLE_LIVE_TRADING=true",
            "requires_confirmation": LIVE_CONFIRMATION,
            "passphrase_policy": "manual_input_only",
            "credential_policy": binance_credential_policy(),
        },
    }
    if portfolio_snapshot is not None:
        payload["position_effect"] = _position_effect(intent, portfolio_snapshot)
    return payload


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
    """Submit BTCUSD_PERP COIN-M order only when all live guards pass."""

    intent = _build_intent(
        side=side,
        order_type=order_type,
        quantity=quantity,
        price=price,
        time_in_force=time_in_force,
        position_side=position_side,
        reduce_only=reduce_only,
        client_order_id=client_order_id,
    )
    intent.validate()
    settings = get_settings()
    preview = preview_btc_order(
        side=side,
        order_type=order_type,
        quantity=quantity,
        price=price,
        time_in_force=time_in_force,
        position_side=position_side,
        reduce_only=reduce_only,
        client_order_id=client_order_id,
        settings_path=settings_path,
        state_path=state_path,
        credentials_path=credentials_path,
    )

    if confirm != LIVE_CONFIRMATION:
        return {
            **preview,
            "status": "blocked",
            "blocked_reason": "missing_confirmation",
        }
    if "emergency_kill_switch_enabled" in preview["risk"]["blocked_reasons"]:
        return {
            **preview,
            "status": "blocked",
            "blocked_reason": "emergency_kill_switch_enabled",
        }
    if not preview["risk"]["valid"]:
        return {
            **preview,
            "status": "blocked",
            "blocked_reason": "risk_limit_exceeded",
        }
    if not settings.binance_enable_live_trading:
        return {
            **preview,
            "status": "blocked",
            "blocked_reason": "live_trading_disabled",
        }
    if settings.binance_force_testnet_execution and not settings.binance_testnet:
        return {
            **preview,
            "status": "blocked",
            "blocked_reason": "testnet_only_policy",
        }
    if not credential_passphrase:
        return {
            **preview,
            "status": "blocked",
            "blocked_reason": "missing_credential_passphrase",
        }
    credentials = load_binance_credentials(
        credential_passphrase,
        credentials_path=credentials_path,
    )

    params = intent.request_params(
        timestamp_ms=int(time.time() * 1000),
        recv_window_ms=_normalize_recv_window_ms(
            settings.binance_recv_window_ms,
            BINANCE_RECV_WINDOW_MS_ENV,
        ),
    )
    response_payload = _signed_post(
        base_url=TESTNET_BASE_URL if settings.binance_testnet else MAINNET_BASE_URL,
        path=ORDER_PATH,
        params=params,
        api_key=credentials.api_key,
        api_secret=credentials.api_secret,
    )
    risk_state = record_btc_order_submission(
        float(preview["estimated_notional_usd"]),
        state_path=state_path,
    )
    return {
        **preview,
        "status": "submitted",
        "binance_response": response_payload,
        "risk_state": risk_state,
        "live_data_required": True,
    }


def check_binance_coinm_connectivity() -> dict[str, Any]:
    """Read Binance COIN-M server time and BTCUSD_PERP symbol metadata."""

    settings = get_settings()
    base_url = _base_url()
    server_time = _public_get(base_url, SERVER_TIME_PATH)
    exchange_info = _public_get(base_url, EXCHANGE_INFO_PATH)
    symbol_info = _symbol_info(exchange_info, ALLOWED_SYMBOL)
    return {
        "status": "ok",
        "exchange": "binance_coin_m_futures",
        "testnet": settings.binance_testnet,
        "base_url": base_url,
        "server_time": server_time,
        "symbol": ALLOWED_SYMBOL,
        "symbol_info": symbol_info,
        "live_data_required": True,
    }


def get_binance_coinm_account_snapshot(
    credential_passphrase: str | None = None,
    credentials_path: str | None = None,
) -> dict[str, Any]:
    """Read BTC COIN-M account balance and position without placing orders."""

    if not credential_passphrase:
        return {
            "status": "blocked",
            "blocked_reason": "missing_credential_passphrase",
            "credentials": get_binance_credentials_status(credentials_path),
            "live_data_required": False,
        }

    settings = get_settings()
    credentials = load_binance_credentials(
        credential_passphrase,
        credentials_path=credentials_path,
    )
    base_url = _base_url()
    recv_window_ms = _normalize_recv_window_ms(
        settings.binance_recv_window_ms,
        BINANCE_RECV_WINDOW_MS_ENV,
    )
    balance = _signed_get(
        base_url=base_url,
        path=BALANCE_PATH,
        params={},
        api_key=credentials.api_key,
        api_secret=credentials.api_secret,
        recv_window_ms=recv_window_ms,
    )
    positions = _signed_get(
        base_url=base_url,
        path=POSITION_RISK_PATH,
        params={"pair": "BTCUSD"},
        api_key=credentials.api_key,
        api_secret=credentials.api_secret,
        recv_window_ms=recv_window_ms,
    )
    btc_positions = [
        position
        for position in positions
        if isinstance(position, dict) and position.get("symbol") == ALLOWED_SYMBOL
    ]
    portfolio_snapshot = normalize_binance_coinm_account_snapshot(
        balance=balance if isinstance(balance, list) else [],
        positions=btc_positions,
    )
    return {
        "status": "ok",
        "exchange": "binance_coin_m_futures",
        "testnet": settings.binance_testnet,
        "base_url": base_url,
        "credentials": get_binance_credentials_status(credentials_path),
        "balance": balance,
        "positions": btc_positions,
        "portfolio_snapshot": portfolio_snapshot,
        "live_data_required": True,
    }


def normalize_binance_coinm_account_snapshot(
    balance: list[dict[str, Any]] | None = None,
    positions: list[dict[str, Any]] | None = None,
    as_of: str | None = None,
    coinm_contract_size_usd: float | None = None,
) -> dict[str, Any]:
    """Normalize caller-supplied COIN-M balances and positions without network calls."""

    normalized_balance_rows = _normalize_snapshot_rows(balance, "balance")
    normalized_position_rows = _normalize_snapshot_rows(positions, "positions")
    normalized_as_of = _normalize_optional_snapshot_text(as_of, "as_of")
    normalized_contract_size = _normalize_optional_snapshot_positive_finite_number(
        coinm_contract_size_usd,
        "coinm_contract_size_usd",
    )
    normalized_balances = [_normalize_balance(row) for row in normalized_balance_rows]
    btc_position = _normalize_btc_position(
        normalized_position_rows,
        coinm_contract_size_usd=normalized_contract_size,
    )
    guard = _portfolio_snapshot_guard(normalized_balances, btc_position)
    return {
        "schema_version": PORTFOLIO_SNAPSHOT_SCHEMA_VERSION,
        "status": guard["status"],
        "exchange": "binance_coin_m_futures",
        "symbol": ALLOWED_SYMBOL,
        "as_of": normalized_as_of,
        "snapshot_source": "caller_supplied",
        "portfolio_sync_contract": {
            "read_only": True,
            "order_submission": False,
            "network_call": False,
            "credential_required": False,
            "secret_values_returned": False,
            "raw_snapshot_returned": False,
        },
        "balances": normalized_balances,
        "btc_position": btc_position,
        "position_detected": btc_position["position_state"] != "flat",
        "guard": guard,
        "live_data_required": False,
    }


def estimate_notional_usd(
    intent: BinanceOrderIntent,
    settings_path: str | None = None,
) -> float:
    settings = load_btc_risk_settings(settings_path)
    return float(_positive_decimal(intent.quantity) * Decimal(str(settings.coinm_contract_size_usd)))


def signed_order_query(
    intent: BinanceOrderIntent,
    api_secret: str,
    timestamp_ms: int,
    recv_window_ms: int = 5000,
) -> str:
    """Return Binance signed query string for tests and diagnostics."""

    params = intent.request_params(timestamp_ms, recv_window_ms)
    query = parse.urlencode(params)
    signature = hmac.new(api_secret.encode(), query.encode(), hashlib.sha256).hexdigest()
    return f"{query}&signature={signature}"


def signed_read_query(
    params: dict[str, str],
    api_secret: str,
    timestamp_ms: int,
    recv_window_ms: int = 5000,
) -> str:
    """Return a signed USER_DATA query string for read-only requests."""

    request_params = {
        **params,
        "timestamp": str(timestamp_ms),
        "recvWindow": str(_normalize_recv_window_ms(recv_window_ms, "recv_window_ms")),
    }
    query = parse.urlencode(request_params)
    signature = hmac.new(api_secret.encode(), query.encode(), hashlib.sha256).hexdigest()
    return f"{query}&signature={signature}"


def _build_intent(
    *,
    side: str,
    order_type: str,
    quantity: str,
    price: str | None,
    time_in_force: str | None,
    position_side: str | None,
    reduce_only: bool,
    client_order_id: str | None,
) -> BinanceOrderIntent:
    normalized_position_side = _normalize_optional_order_text(
        position_side,
        "position_side",
    )
    normalized_time_in_force = _normalize_optional_order_text(
        time_in_force,
        "time_in_force",
    )
    return BinanceOrderIntent(
        symbol=ALLOWED_SYMBOL,
        side=_normalize_required_order_text(side, "side").upper(),
        order_type=_normalize_required_order_text(order_type, "order_type").upper(),
        quantity=_normalize_required_order_decimal_text(quantity, "quantity"),
        price=_normalize_optional_order_decimal_text(price, "price"),
        time_in_force=(
            normalized_time_in_force.upper()
            if normalized_time_in_force is not None
            else None
        ),
        position_side=(
            normalized_position_side.upper()
            if normalized_position_side is not None
            else None
        ),
        reduce_only=_normalize_order_boolean(reduce_only, "reduce_only"),
        client_order_id=_normalize_optional_order_text(
            client_order_id,
            "client_order_id",
        ),
    )


def _positive_decimal(value: str) -> Decimal:
    try:
        decimal = Decimal(str(value))
    except InvalidOperation as exc:
        raise ValueError(f"invalid decimal value: {value}") from exc
    if not decimal.is_finite():
        raise ValueError(f"invalid decimal value: {value}")
    return decimal


def _normalize_recv_window_ms(value: int, field_name: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        raise ValueError(f"{field_name} must be a positive integer")
    if value <= 0:
        raise ValueError(f"{field_name} must be a positive integer")
    return value


def _normalize_order_boolean(value: bool, field_name: str) -> bool:
    if type(value) is not bool:
        raise ValueError(f"{field_name} must be a boolean")
    return value


def _normalize_required_order_text(value: str, field_name: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be a nonempty string")
    if not _has_no_control_characters(value):
        raise ValueError(f"{field_name} must not contain control characters")
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{field_name} must be a nonempty string")
    return normalized


def _normalize_optional_order_text(value: str | None, field_name: str) -> str | None:
    if value is None:
        return None
    return _normalize_required_order_text(value, field_name)


def _normalize_required_order_decimal_text(value: str, field_name: str) -> str:
    normalized = _normalize_required_order_text(value, field_name)
    _positive_decimal(normalized)
    return normalized


def _normalize_optional_order_decimal_text(
    value: str | None,
    field_name: str,
) -> str | None:
    if value is None:
        return None
    normalized = _normalize_required_order_text(value, field_name)
    _positive_decimal(normalized)
    return normalized


def _has_no_control_characters(value: str) -> bool:
    return all(ord(character) >= 32 and ord(character) != 127 for character in value)


def _normalize_snapshot_rows(
    rows: list[dict[str, Any]] | None,
    field_name: str,
) -> list[dict[str, Any]]:
    if rows is None:
        return []
    if not isinstance(rows, list):
        raise ValueError(f"{field_name} must be a list of objects")
    normalized_rows: list[dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError(f"{field_name} must be a list of objects")
        normalized_rows.append(row)
    return normalized_rows


def _normalize_snapshot_required_text(value: Any, field_name: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be a nonempty string")
    if not _has_no_control_characters(value):
        raise ValueError(f"{field_name} must not contain control characters")
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{field_name} must be a nonempty string")
    return normalized


def _normalize_optional_snapshot_text(value: Any, field_name: str) -> str | None:
    if value is None:
        return None
    return _normalize_snapshot_required_text(value, field_name)


def _normalize_optional_snapshot_positive_finite_number(
    value: float | int | None,
    field_name: str,
) -> float | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{field_name} must be a positive finite number")
    normalized = Decimal(str(value))
    if not normalized.is_finite() or normalized <= 0:
        raise ValueError(f"{field_name} must be a positive finite number")
    return float(normalized)


def _validated_decimal(value: Any, field_name: str) -> Decimal:
    if isinstance(value, bool):
        raise ValueError(f"{field_name} must be a finite decimal value")
    try:
        decimal = Decimal(str(value))
    except InvalidOperation as exc:
        raise ValueError(f"{field_name} must be a finite decimal value") from exc
    if not decimal.is_finite():
        raise ValueError(f"{field_name} must be a finite decimal value")
    return decimal


def _validated_decimal_string(value: Any, field_name: str) -> str:
    return _decimal_string(_validated_decimal(value, field_name))


def _normalize_balance(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "asset": _normalize_snapshot_required_text(row.get("asset"), "balance.asset"),
        "balance": _validated_decimal_string(
            row.get("balance", row.get("walletBalance", "0")),
            "balance.balance",
        ),
        "available_balance": _validated_decimal_string(
            row.get("availableBalance", "0"),
            "balance.availableBalance",
        ),
        "cross_wallet_balance": _validated_decimal_string(
            row.get("crossWalletBalance", "0"),
            "balance.crossWalletBalance",
        ),
        "cross_unrealized_pnl": _validated_decimal_string(
            row.get("crossUnPnl", "0"),
            "balance.crossUnPnl",
        ),
    }


def _normalize_btc_position(
    positions: list[dict[str, Any]],
    coinm_contract_size_usd: float | None = None,
) -> dict[str, Any]:
    contract_size = (
        Decimal(str(coinm_contract_size_usd))
        if coinm_contract_size_usd is not None
        else Decimal(str(load_btc_risk_settings().coinm_contract_size_usd))
    )
    btc_position = next(
        (
            position
            for position in positions
            if isinstance(position, dict) and position.get("symbol") == ALLOWED_SYMBOL
        ),
        {},
    )
    amount = _validated_decimal(
        btc_position.get("positionAmt", "0"),
        "positions.positionAmt",
    )
    mark_price = _validated_decimal(
        btc_position.get("markPrice", "0"),
        "positions.markPrice",
    )
    entry_price = _validated_decimal(
        btc_position.get("entryPrice", "0"),
        "positions.entryPrice",
    )
    state = "flat"
    if amount > 0:
        state = "long"
    elif amount < 0:
        state = "short"
    return {
        "symbol": ALLOWED_SYMBOL,
        "position_side": _normalize_optional_snapshot_text(
            btc_position.get("positionSide"),
            "positions.positionSide",
        )
        or "BOTH",
        "position_state": state,
        "position_amt_contracts": _decimal_string(amount),
        "contract_size_usd": _decimal_string(contract_size),
        "estimated_notional_usd": _decimal_string(abs(amount) * contract_size),
        "entry_price": _decimal_string(entry_price),
        "mark_price": _decimal_string(mark_price),
        "unrealized_pnl": _validated_decimal_string(
            btc_position.get("unRealizedProfit", "0"),
            "positions.unRealizedProfit",
        ),
        "liquidation_price": _validated_decimal_string(
            btc_position.get("liquidationPrice", "0"),
            "positions.liquidationPrice",
        ),
        "leverage": _normalize_optional_snapshot_text(
            btc_position.get("leverage"),
            "positions.leverage",
        )
        or "",
        "margin_type": _normalize_optional_snapshot_text(
            btc_position.get("marginType"),
            "positions.marginType",
        )
        or "",
    }


def _portfolio_snapshot_guard(
    balances: list[dict[str, Any]],
    btc_position: dict[str, Any],
) -> dict[str, Any]:
    checks = [
        {
            "name": "btc_only_position_scope",
            "passed": btc_position["symbol"] == ALLOWED_SYMBOL,
            "expected": ALLOWED_SYMBOL,
            "actual": btc_position["symbol"],
        },
        {
            "name": "read_only_no_order_submission",
            "passed": True,
            "expected": False,
            "actual": False,
        },
        {
            "name": "no_network_call",
            "passed": True,
            "expected": False,
            "actual": False,
        },
        {
            "name": "secret_values_not_returned",
            "passed": True,
            "expected": False,
            "actual": False,
        },
        {
            "name": "balances_are_normalized",
            "passed": all("asset" in balance and "balance" in balance for balance in balances),
            "expected": "normalized_balance_rows",
            "actual": len(balances),
        },
    ]
    return {
        "status": "ok" if all(check["passed"] for check in checks) else "conflict",
        "checks": checks,
    }


def _position_effect(
    intent: BinanceOrderIntent,
    portfolio_snapshot: dict[str, Any],
) -> dict[str, Any]:
    btc_position = dict(portfolio_snapshot.get("btc_position") or {})
    current_contracts = _safe_decimal(btc_position.get("position_amt_contracts", "0"))
    order_contracts = _positive_decimal(intent.quantity)
    signed_order_contracts = order_contracts if intent.side == "BUY" else -order_contracts
    projected_contracts = current_contracts + signed_order_contracts
    effect = _classify_position_effect(current_contracts, projected_contracts)
    reduce_only_effect_valid = not intent.reduce_only or effect in {
        "reduces_long",
        "closes_long",
        "reduces_short",
        "closes_short",
    }
    checks = [
        {
            "name": "portfolio_snapshot_symbol_matches",
            "passed": btc_position.get("symbol", ALLOWED_SYMBOL) == ALLOWED_SYMBOL,
            "expected": ALLOWED_SYMBOL,
            "actual": btc_position.get("symbol", ALLOWED_SYMBOL),
        },
        {
            "name": "no_order_submission",
            "passed": True,
            "expected": False,
            "actual": False,
        },
        {
            "name": "reduce_only_does_not_increase_or_flip",
            "passed": reduce_only_effect_valid,
            "expected": True,
            "actual": reduce_only_effect_valid,
        },
    ]
    return {
        "schema_version": "btc_order_position_effect.v1",
        "source": "portfolio_snapshot",
        "current_position_state": btc_position.get("position_state", "flat"),
        "current_contracts": _decimal_string(current_contracts),
        "order_contracts": _decimal_string(order_contracts),
        "signed_order_contracts": _decimal_string(signed_order_contracts),
        "projected_contracts": _decimal_string(projected_contracts),
        "effect": effect,
        "reduce_only_requested": intent.reduce_only,
        "guard": {
            "status": "ok" if all(check["passed"] for check in checks) else "conflict",
            "checks": checks,
        },
        "live_data_required": False,
    }


def _classify_position_effect(
    current_contracts: Decimal,
    projected_contracts: Decimal,
) -> str:
    if current_contracts == 0:
        if projected_contracts > 0:
            return "opens_long"
        if projected_contracts < 0:
            return "opens_short"
        return "stays_flat"
    if current_contracts > 0:
        if projected_contracts > current_contracts:
            return "increases_long"
        if projected_contracts > 0:
            return "reduces_long"
        if projected_contracts == 0:
            return "closes_long"
        return "flips_long_to_short"
    if projected_contracts < current_contracts:
        return "increases_short"
    if projected_contracts < 0:
        return "reduces_short"
    if projected_contracts == 0:
        return "closes_short"
    return "flips_short_to_long"


def _safe_decimal(value: Any) -> Decimal:
    try:
        return Decimal(str(value or "0"))
    except InvalidOperation:
        return Decimal("0")


def _decimal_string(value: Any) -> str:
    decimal = _safe_decimal(value)
    normalized = decimal.normalize()
    if normalized == normalized.to_integral():
        return format(normalized, "f")
    return format(normalized, "f")


def _base_url() -> str:
    return TESTNET_BASE_URL if get_settings().binance_testnet else MAINNET_BASE_URL


def _public_get(base_url: str, path: str) -> dict[str, Any]:
    http_request = request.Request(f"{base_url}{path}", method="GET")
    with request.urlopen(http_request, timeout=10) as response:
        return json.loads(response.read().decode("utf-8"))


def _symbol_info(exchange_info: dict[str, Any], symbol: str) -> dict[str, Any]:
    for item in exchange_info.get("symbols", []):
        if isinstance(item, dict) and item.get("symbol") == symbol:
            return {
                "symbol": item.get("symbol"),
                "pair": item.get("pair"),
                "contractType": item.get("contractType"),
                "contractStatus": item.get("contractStatus"),
                "contractSize": item.get("contractSize"),
                "baseAsset": item.get("baseAsset"),
                "quoteAsset": item.get("quoteAsset"),
                "marginAsset": item.get("marginAsset"),
                "orderTypes": item.get("orderTypes"),
                "timeInForce": item.get("timeInForce"),
                "filters": item.get("filters"),
            }
    raise RuntimeError(f"Binance COIN-M symbol not found: {symbol}")


def _signed_get(
    *,
    base_url: str,
    path: str,
    params: dict[str, str],
    api_key: str,
    api_secret: str,
    recv_window_ms: int,
) -> Any:
    query = signed_read_query(
        params=params,
        api_secret=api_secret,
        timestamp_ms=int(time.time() * 1000),
        recv_window_ms=recv_window_ms,
    )
    http_request = request.Request(
        f"{base_url}{path}?{query}",
        headers={"X-MBX-APIKEY": api_key},
        method="GET",
    )
    try:
        with request.urlopen(http_request, timeout=10) as response:
            return json.loads(response.read().decode("utf-8"))
    except error.HTTPError as exc:
        payload = exc.read().decode("utf-8")
        raise RuntimeError(f"Binance COIN-M read request failed: {exc.code} {payload}") from exc


def _signed_post(
    *,
    base_url: str,
    path: str,
    params: dict[str, str],
    api_key: str,
    api_secret: str,
) -> dict[str, Any]:
    query = parse.urlencode(params)
    signature = hmac.new(api_secret.encode(), query.encode(), hashlib.sha256).hexdigest()
    body = f"{query}&signature={signature}".encode()
    http_request = request.Request(
        f"{base_url}{path}",
        data=body,
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "X-MBX-APIKEY": api_key,
        },
        method="POST",
    )
    try:
        with request.urlopen(http_request, timeout=10) as response:
            return json.loads(response.read().decode("utf-8"))
    except error.HTTPError as exc:
        payload = exc.read().decode("utf-8")
        raise RuntimeError(f"Binance COIN-M order request failed: {exc.code} {payload}") from exc
