import hashlib
import hmac
from pathlib import Path
from urllib import parse

import pytest

from halo_swing_mcp.binance_btc import (
    ALLOWED_SYMBOL,
    LIVE_CONFIRMATION,
    BinanceOrderIntent,
    execute_btc_order,
    preview_btc_order,
    signed_read_query,
    signed_order_query,
)
from halo_swing_mcp.config import get_settings
from halo_swing_mcp.risk_settings import update_btc_risk_settings
from halo_swing_mcp.secret_store import (
    get_binance_credentials_status,
    load_binance_credentials,
    save_binance_credentials,
)
from halo_swing_mcp.tool_registry import call_tool
from halo_swing_mcp.trading_admin_web import HTML, admin_status_payload


def test_preview_btc_order_is_coin_m_and_dry_run_by_default() -> None:
    payload = preview_btc_order(side="BUY", quantity="1")

    assert payload["status"] == "preview"
    assert payload["exchange"] == "binance_coin_m_futures"
    assert payload["symbol"] == ALLOWED_SYMBOL
    assert payload["quantity_unit"] == "contract"
    assert payload["estimated_notional_usd"] == 100.0
    assert payload["live_trading_enabled"] is False
    assert payload["execution_guard"]["btc_only"] is True
    assert payload["execution_guard"]["coin_m_futures_only"] is True


def test_execute_btc_order_blocks_without_confirmation() -> None:
    payload = execute_btc_order(side="BUY", quantity="1")

    assert payload["status"] == "blocked"
    assert payload["blocked_reason"] == "missing_confirmation"


def test_execute_btc_order_blocks_when_live_flag_is_disabled() -> None:
    get_settings.cache_clear()
    payload = execute_btc_order(
        side="BUY",
        quantity="1",
        confirm=LIVE_CONFIRMATION,
    )

    assert payload["status"] == "blocked"
    assert payload["blocked_reason"] == "live_trading_disabled"


def test_execute_btc_order_blocks_when_risk_limit_is_exceeded(tmp_path: Path) -> None:
    settings_path = tmp_path / "risk_settings.json"
    update_btc_risk_settings(
        max_notional_usd_per_order=100,
        settings_path=str(settings_path),
    )
    payload = execute_btc_order(
        side="BUY",
        quantity="2",
        confirm=LIVE_CONFIRMATION,
        settings_path=str(settings_path),
    )

    assert payload["status"] == "blocked"
    assert payload["blocked_reason"] == "risk_limit_exceeded"
    assert "per_order_notional_ok" in payload["risk"]["blocked_reasons"]


def test_order_intent_rejects_non_btc_coin_m_symbol() -> None:
    intent = BinanceOrderIntent(symbol="ETHUSD_PERP", side="BUY", order_type="MARKET", quantity="1")

    with pytest.raises(ValueError, match="BTCUSD_PERP only"):
        intent.validate()


def test_order_intent_rejects_invalid_quantity() -> None:
    intent = BinanceOrderIntent(
        symbol=ALLOWED_SYMBOL,
        side="BUY",
        order_type="MARKET",
        quantity="0",
    )

    with pytest.raises(ValueError, match="quantity must be positive"):
        intent.validate()


def test_order_intent_rejects_reduce_only_with_hedge_position_side() -> None:
    intent = BinanceOrderIntent(
        symbol=ALLOWED_SYMBOL,
        side="SELL",
        order_type="MARKET",
        quantity="1",
        position_side="LONG",
        reduce_only=True,
    )

    with pytest.raises(ValueError, match="reduce_only cannot be sent"):
        intent.validate()


def test_signed_order_query_uses_coin_m_hmac_sha256_signature() -> None:
    intent = BinanceOrderIntent(
        symbol=ALLOWED_SYMBOL,
        side="BUY",
        order_type="MARKET",
        quantity="1",
    )
    query = signed_order_query(intent, api_secret="secret", timestamp_ms=1234567890)
    unsigned = query.rsplit("&signature=", maxsplit=1)[0]
    expected_signature = hmac.new(
        b"secret",
        unsigned.encode(),
        hashlib.sha256,
    ).hexdigest()

    assert parse.parse_qs(query)["signature"] == [expected_signature]


def test_signed_read_query_uses_hmac_sha256_signature() -> None:
    query = signed_read_query(
        {"pair": "BTCUSD"},
        api_secret="secret",
        timestamp_ms=1234567890,
    )
    unsigned = query.rsplit("&signature=", maxsplit=1)[0]
    expected_signature = hmac.new(
        b"secret",
        unsigned.encode(),
        hashlib.sha256,
    ).hexdigest()

    assert parse.parse_qs(query)["signature"] == [expected_signature]


def test_encrypted_binance_credentials_round_trip(tmp_path: Path) -> None:
    credentials_path = tmp_path / "binance_credentials.enc.json"
    status = save_binance_credentials(
        api_key="abcde12345key",
        api_secret="super-secret",
        passphrase="local-passphrase",
        credentials_path=str(credentials_path),
    )
    credentials = load_binance_credentials(
        "local-passphrase",
        credentials_path=str(credentials_path),
    )

    assert status["configured"] is True
    assert status["api_key_hint"] == "abcde...5key"
    assert "super-secret" not in credentials_path.read_text(encoding="utf-8")
    assert credentials.api_key == "abcde12345key"
    assert credentials.api_secret == "super-secret"


def test_encrypted_binance_credentials_reject_wrong_passphrase(tmp_path: Path) -> None:
    credentials_path = tmp_path / "binance_credentials.enc.json"
    save_binance_credentials(
        api_key="abcde12345key",
        api_secret="super-secret",
        passphrase="local-passphrase",
        credentials_path=str(credentials_path),
    )

    with pytest.raises(ValueError, match="invalid Binance credential passphrase"):
        load_binance_credentials("wrong-passphrase", credentials_path=str(credentials_path))


def test_binance_btc_tools_are_registry_backed(tmp_path: Path) -> None:
    credentials_path = tmp_path / "binance_credentials.enc.json"
    preview = call_tool(
        "preview_btc_order",
        {"side": "BUY", "quantity": "1", "credentials_path": str(credentials_path)},
    )
    blocked = call_tool("execute_btc_order", {"side": "BUY", "quantity": "1"})
    status = call_tool(
        "save_binance_credentials",
        {
            "api_key": "abcde12345key",
            "api_secret": "super-secret",
            "passphrase": "local-passphrase",
            "credentials_path": str(credentials_path),
        },
    )
    account = call_tool("get_binance_coinm_account_snapshot")

    assert preview["status"] == "preview"
    assert blocked["status"] == "blocked"
    assert status["configured"] is True
    assert account["blocked_reason"] == "missing_credential_passphrase"


def test_trading_admin_status_is_secret_safe(tmp_path: Path, monkeypatch) -> None:
    credentials_path = tmp_path / "credentials.enc.json"
    monkeypatch.setenv("HALO_SWING_BINANCE_CREDENTIALS_PATH", str(credentials_path))
    get_settings.cache_clear()
    save_binance_credentials(
        api_key="abcde12345key",
        api_secret="super-secret",
        passphrase="local-passphrase",
        credentials_path=str(credentials_path),
    )
    payload = admin_status_payload()

    assert "Halo Swing Trading Admin" in HTML
    assert payload["credentials"]["configured"] is True
    assert get_binance_credentials_status(str(credentials_path))["api_key_hint"] == "abcde...5key"
    assert "api_secret" not in payload["credentials"]
