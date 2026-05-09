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
LIVE_CONFIRMATION = "CONFIRM_BTC_BINANCE_COINM_ORDER"


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
        params = {
            "symbol": self.symbol,
            "side": self.side,
            "type": self.order_type,
            "quantity": self.quantity,
            "timestamp": str(timestamp_ms),
            "recvWindow": str(recv_window_ms),
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
    return {
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
        "live_trading_enabled": settings.binance_enable_live_trading,
        "live_data_required": False,
        "risk": risk,
        "credentials": get_binance_credentials_status(credentials_path),
        "execution_guard": {
            "btc_only": True,
            "coin_m_futures_only": True,
            "requires_env_flag": "HALO_SWING_BINANCE_ENABLE_LIVE_TRADING=true",
            "requires_confirmation": LIVE_CONFIRMATION,
        },
    }


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
        recv_window_ms=settings.binance_recv_window_ms,
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
    return BinanceOrderIntent(
        symbol=ALLOWED_SYMBOL,
        side=side.upper(),
        order_type=order_type.upper(),
        quantity=str(quantity),
        price=price,
        time_in_force=time_in_force,
        position_side=position_side.upper() if position_side else None,
        reduce_only=bool(reduce_only),
        client_order_id=client_order_id,
    )


def _positive_decimal(value: str) -> Decimal:
    try:
        return Decimal(str(value))
    except InvalidOperation as exc:
        raise ValueError(f"invalid decimal value: {value}") from exc


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
