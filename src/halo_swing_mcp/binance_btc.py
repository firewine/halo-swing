"""BTC-only Binance Spot order preview and guarded execution helpers."""

from __future__ import annotations

import hashlib
import hmac
import json
import time
from dataclasses import dataclass
from typing import Any
from urllib import error, parse, request

from halo_swing_mcp.config import get_settings


ALLOWED_SYMBOL = "BTCUSDT"
ALLOWED_SIDES = {"BUY", "SELL"}
ALLOWED_ORDER_TYPES = {"MARKET", "LIMIT"}
MAINNET_BASE_URL = "https://api.binance.com"
TESTNET_BASE_URL = "https://testnet.binance.vision"
LIVE_CONFIRMATION = "CONFIRM_BTC_BINANCE_ORDER"


@dataclass(frozen=True)
class BinanceOrderIntent:
    symbol: str
    side: str
    order_type: str
    quantity: str | None = None
    quote_order_qty: str | None = None
    price: str | None = None
    time_in_force: str | None = None
    client_order_id: str | None = None

    def validate(self) -> None:
        if self.symbol != ALLOWED_SYMBOL:
            raise ValueError("Binance auto-trading is restricted to BTCUSDT only.")
        if self.side not in ALLOWED_SIDES:
            raise ValueError("side must be BUY or SELL.")
        if self.order_type not in ALLOWED_ORDER_TYPES:
            raise ValueError("order_type must be MARKET or LIMIT.")
        if bool(self.quantity) == bool(self.quote_order_qty):
            raise ValueError("Provide exactly one of quantity or quote_order_qty.")
        if self.order_type == "LIMIT":
            if not self.price:
                raise ValueError("LIMIT orders require price.")
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
            "timestamp": str(timestamp_ms),
            "recvWindow": str(recv_window_ms),
        }
        optional = {
            "quantity": self.quantity,
            "quoteOrderQty": self.quote_order_qty,
            "price": self.price,
            "timeInForce": self.time_in_force,
            "newClientOrderId": self.client_order_id,
        }
        params.update({key: value for key, value in optional.items() if value is not None})
        return params


def preview_btc_order(
    side: str = "BUY",
    order_type: str = "MARKET",
    quantity: str | None = None,
    quote_order_qty: str | None = None,
    price: str | None = None,
    time_in_force: str | None = None,
    client_order_id: str | None = None,
) -> dict[str, Any]:
    """Return a BTCUSDT Binance order preview without submitting it."""

    intent = _build_intent(
        side=side,
        order_type=order_type,
        quantity=quantity,
        quote_order_qty=quote_order_qty,
        price=price,
        time_in_force=time_in_force,
        client_order_id=client_order_id,
    )
    intent.validate()
    settings = get_settings()
    return {
        "status": "preview",
        "exchange": "binance_spot",
        "symbol": intent.symbol,
        "side": intent.side,
        "order_type": intent.order_type,
        "quantity": intent.quantity,
        "quote_order_qty": intent.quote_order_qty,
        "price": intent.price,
        "time_in_force": intent.time_in_force,
        "client_order_id": intent.client_order_id,
        "testnet": settings.binance_testnet,
        "live_trading_enabled": settings.binance_enable_live_trading,
        "live_data_required": False,
        "execution_guard": {
            "btc_only": True,
            "requires_env_flag": "HALO_SWING_BINANCE_ENABLE_LIVE_TRADING=true",
            "requires_confirmation": LIVE_CONFIRMATION,
        },
    }


def execute_btc_order(
    side: str = "BUY",
    order_type: str = "MARKET",
    quantity: str | None = None,
    quote_order_qty: str | None = None,
    price: str | None = None,
    time_in_force: str | None = None,
    client_order_id: str | None = None,
    confirm: str | None = None,
) -> dict[str, Any]:
    """Submit a BTCUSDT Binance Spot order only when all live guards pass."""

    intent = _build_intent(
        side=side,
        order_type=order_type,
        quantity=quantity,
        quote_order_qty=quote_order_qty,
        price=price,
        time_in_force=time_in_force,
        client_order_id=client_order_id,
    )
    intent.validate()
    settings = get_settings()
    preview = preview_btc_order(
        side=side,
        order_type=order_type,
        quantity=quantity,
        quote_order_qty=quote_order_qty,
        price=price,
        time_in_force=time_in_force,
        client_order_id=client_order_id,
    )

    if confirm != LIVE_CONFIRMATION:
        return {
            **preview,
            "status": "blocked",
            "blocked_reason": "missing_confirmation",
        }
    if not settings.binance_enable_live_trading:
        return {
            **preview,
            "status": "blocked",
            "blocked_reason": "live_trading_disabled",
        }
    if not settings.binance_api_key or not settings.binance_api_secret:
        return {
            **preview,
            "status": "blocked",
            "blocked_reason": "missing_binance_credentials",
        }

    params = intent.request_params(
        timestamp_ms=int(time.time() * 1000),
        recv_window_ms=settings.binance_recv_window_ms,
    )
    response_payload = _signed_post(
        base_url=TESTNET_BASE_URL if settings.binance_testnet else MAINNET_BASE_URL,
        path="/api/v3/order",
        params=params,
        api_key=settings.binance_api_key,
        api_secret=settings.binance_api_secret,
    )
    return {
        **preview,
        "status": "submitted",
        "binance_response": response_payload,
        "live_data_required": True,
    }


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
    quantity: str | None,
    quote_order_qty: str | None,
    price: str | None,
    time_in_force: str | None,
    client_order_id: str | None,
) -> BinanceOrderIntent:
    return BinanceOrderIntent(
        symbol=ALLOWED_SYMBOL,
        side=side.upper(),
        order_type=order_type.upper(),
        quantity=quantity,
        quote_order_qty=quote_order_qty,
        price=price,
        time_in_force=time_in_force,
        client_order_id=client_order_id,
    )


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
        raise RuntimeError(f"Binance order request failed: {exc.code} {payload}") from exc
