import hmac
import hashlib
from urllib import parse

import pytest

from halo_swing_mcp.binance_btc import (
    ALLOWED_SYMBOL,
    LIVE_CONFIRMATION,
    BinanceOrderIntent,
    execute_btc_order,
    preview_btc_order,
    signed_order_query,
)
from halo_swing_mcp.config import get_settings
from halo_swing_mcp.tool_registry import call_tool


def test_preview_btc_order_is_btc_only_and_dry_run_by_default() -> None:
    payload = preview_btc_order(side="BUY", quote_order_qty="25")

    assert payload["status"] == "preview"
    assert payload["exchange"] == "binance_spot"
    assert payload["symbol"] == ALLOWED_SYMBOL
    assert payload["live_trading_enabled"] is False
    assert payload["execution_guard"]["btc_only"] is True


def test_execute_btc_order_blocks_without_confirmation() -> None:
    payload = execute_btc_order(side="BUY", quote_order_qty="25")

    assert payload["status"] == "blocked"
    assert payload["blocked_reason"] == "missing_confirmation"


def test_execute_btc_order_blocks_when_live_flag_is_disabled() -> None:
    get_settings.cache_clear()
    payload = execute_btc_order(
        side="BUY",
        quote_order_qty="25",
        confirm=LIVE_CONFIRMATION,
    )

    assert payload["status"] == "blocked"
    assert payload["blocked_reason"] == "live_trading_disabled"


def test_order_intent_rejects_non_btc_symbol() -> None:
    intent = BinanceOrderIntent(symbol="ETHUSDT", side="BUY", order_type="MARKET", quote_order_qty="25")

    with pytest.raises(ValueError, match="BTCUSDT only"):
        intent.validate()


def test_order_intent_rejects_ambiguous_quantity() -> None:
    intent = BinanceOrderIntent(
        symbol=ALLOWED_SYMBOL,
        side="BUY",
        order_type="MARKET",
        quantity="0.001",
        quote_order_qty="25",
    )

    with pytest.raises(ValueError, match="exactly one"):
        intent.validate()


def test_signed_order_query_uses_hmac_sha256_signature() -> None:
    intent = BinanceOrderIntent(
        symbol=ALLOWED_SYMBOL,
        side="BUY",
        order_type="MARKET",
        quote_order_qty="25",
    )
    query = signed_order_query(intent, api_secret="secret", timestamp_ms=1234567890)
    unsigned = query.rsplit("&signature=", maxsplit=1)[0]
    expected_signature = hmac.new(
        b"secret",
        unsigned.encode(),
        hashlib.sha256,
    ).hexdigest()

    assert parse.parse_qs(query)["signature"] == [expected_signature]


def test_binance_btc_tools_are_registry_backed() -> None:
    preview = call_tool("preview_btc_order", {"side": "BUY", "quote_order_qty": "25"})
    blocked = call_tool("execute_btc_order", {"side": "BUY", "quote_order_qty": "25"})

    assert preview["status"] == "preview"
    assert blocked["status"] == "blocked"
