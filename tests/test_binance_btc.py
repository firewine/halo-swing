import json
import hashlib
import hmac
import subprocess
import sys
from io import BytesIO
from pathlib import Path
from urllib import parse

import pytest

from halo_swing_mcp.binance_btc import (
    ALLOWED_SYMBOL,
    LIVE_CONFIRMATION,
    BinanceOrderIntent,
    check_binance_coinm_connectivity,
    execute_btc_order,
    get_binance_coinm_account_snapshot,
    normalize_binance_coinm_account_snapshot,
    preview_btc_order,
    signed_read_query,
    signed_order_query,
)
from halo_swing_mcp.audit import read_audit_events
from halo_swing_mcp.config import get_settings
from halo_swing_mcp.risk_settings import update_btc_risk_settings
from halo_swing_mcp.secret_store import (
    binance_credential_policy,
    get_binance_credentials_status,
    load_binance_credentials,
    save_binance_credentials,
)
from halo_swing_mcp.tool_registry import call_tool
from halo_swing_mcp.trading_admin_web import HTML, admin_status_payload, create_handler


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_MISSING_CREDENTIAL_STATUS_KEYS = [
    "configured",
    "provider",
    "credentials_path",
    "credential_policy",
    "secret_values_returned",
    "passphrase_persisted",
    "live_data_required",
]
EXPECTED_CONFIGURED_CREDENTIAL_STATUS_KEYS = [
    "configured",
    "provider",
    "credentials_path",
    "api_key_hint",
    "created_at",
    "updated_at",
    "kdf",
    "cipher",
    "credential_policy",
    "secret_values_returned",
    "passphrase_persisted",
    "live_data_required",
]
EXPECTED_SAFE_CREDENTIAL_KDF_KEYS = ["name", "iterations"]
EXPECTED_SAFE_CREDENTIAL_CIPHER_KEYS = ["name"]
EXPECTED_BINANCE_CREDENTIAL_POLICY_KEYS = [
    "schema_version",
    "provider",
    "testnet_first_required",
    "trade_permission_required",
    "withdraw_permission_allowed",
    "required_permissions",
    "forbidden_permissions",
    "operator_attestation_required",
    "permissions_verified_by_tool",
    "permission_verification",
    "secret_storage",
    "passphrase_handling",
    "passphrase_persistence",
    "secret_values_returned",
]


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
    assert payload["execution_guard"]["schema_version"] == "btc_order_execution_guard.v1"
    assert payload["execution_guard"]["order_submission_default"] is False
    assert payload["execution_guard"]["network_call_before_all_guards_pass"] is False
    assert (
        payload["execution_guard"]["credential_policy"]["schema_version"]
        == "binance_credential_policy.v1"
    )
    assert payload["execution_guard"]["credential_policy"]["withdraw_permission_allowed"] is False


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


def test_preview_btc_order_rejects_noncanonical_testnet_env(monkeypatch) -> None:
    monkeypatch.setenv("HALO_SWING_BINANCE_TESTNET", "yes")
    get_settings.cache_clear()

    try:
        with pytest.raises(
            ValueError,
            match="HALO_SWING_BINANCE_TESTNET must be 'true' or 'false'",
        ):
            preview_btc_order(side="BUY", quantity="1")
    finally:
        get_settings.cache_clear()


def test_execute_btc_order_rejects_noncanonical_live_trading_env_before_credentials(
    tmp_path: Path,
    monkeypatch,
) -> None:
    credentials_path = tmp_path / "missing_credentials.enc.json"

    def fail_load_credentials(*_args: object, **_kwargs: object) -> None:
        raise AssertionError("credentials must not load with invalid live trading env")

    def fail_urlopen(*_args: object, **_kwargs: object) -> None:
        raise AssertionError("network call must not run with invalid live trading env")

    monkeypatch.setenv("HALO_SWING_BINANCE_ENABLE_LIVE_TRADING", "1")
    monkeypatch.setattr(
        "halo_swing_mcp.binance_btc.load_binance_credentials",
        fail_load_credentials,
    )
    monkeypatch.setattr("halo_swing_mcp.binance_btc.request.urlopen", fail_urlopen)
    get_settings.cache_clear()

    try:
        with pytest.raises(
            ValueError,
            match="HALO_SWING_BINANCE_ENABLE_LIVE_TRADING must be 'true' or 'false'",
        ):
            execute_btc_order(
                side="BUY",
                quantity="1",
                confirm=LIVE_CONFIRMATION,
                credential_passphrase="local-passphrase",
                credentials_path=str(credentials_path),
            )
    finally:
        get_settings.cache_clear()

    assert not credentials_path.exists()


def test_check_binance_connectivity_rejects_noncanonical_testnet_env_without_network(
    monkeypatch,
) -> None:
    monkeypatch.setenv("HALO_SWING_BINANCE_TESTNET", "on")
    get_settings.cache_clear()

    def fail_urlopen(*_args: object, **_kwargs: object) -> None:
        raise AssertionError("network call must not run with invalid testnet env")

    monkeypatch.setattr("halo_swing_mcp.binance_btc.request.urlopen", fail_urlopen)

    try:
        with pytest.raises(
            ValueError,
            match="HALO_SWING_BINANCE_TESTNET must be 'true' or 'false'",
        ):
            check_binance_coinm_connectivity()
    finally:
        get_settings.cache_clear()


def test_account_snapshot_rejects_noncanonical_testnet_env_before_credentials(
    tmp_path: Path,
    monkeypatch,
) -> None:
    credentials_path = tmp_path / "missing_credentials.enc.json"

    def fail_load_credentials(*_args: object, **_kwargs: object) -> None:
        raise AssertionError("credentials must not load with invalid testnet env")

    def fail_urlopen(*_args: object, **_kwargs: object) -> None:
        raise AssertionError("network call must not run with invalid testnet env")

    monkeypatch.setenv("HALO_SWING_BINANCE_TESTNET", "1")
    monkeypatch.setattr(
        "halo_swing_mcp.binance_btc.load_binance_credentials",
        fail_load_credentials,
    )
    monkeypatch.setattr("halo_swing_mcp.binance_btc.request.urlopen", fail_urlopen)
    get_settings.cache_clear()

    try:
        with pytest.raises(
            ValueError,
            match="HALO_SWING_BINANCE_TESTNET must be 'true' or 'false'",
        ):
            get_binance_coinm_account_snapshot(
                credential_passphrase="local-passphrase",
                credentials_path=str(credentials_path),
            )
    finally:
        get_settings.cache_clear()

    assert not credentials_path.exists()


def test_account_snapshot_rejects_noncanonical_testnet_env_before_missing_passphrase_status(
    monkeypatch,
) -> None:
    monkeypatch.setenv("HALO_SWING_BINANCE_TESTNET", "yes")
    get_settings.cache_clear()

    def fail_credentials_status(*_args: object, **_kwargs: object) -> None:
        raise AssertionError("credential status must not load with invalid testnet env")

    def fail_urlopen(*_args: object, **_kwargs: object) -> None:
        raise AssertionError("network call must not run with invalid testnet env")

    monkeypatch.setattr(
        "halo_swing_mcp.binance_btc.get_binance_credentials_status",
        fail_credentials_status,
    )
    monkeypatch.setattr("halo_swing_mcp.binance_btc.request.urlopen", fail_urlopen)

    try:
        with pytest.raises(
            ValueError,
            match="HALO_SWING_BINANCE_TESTNET must be 'true' or 'false'",
        ):
            get_binance_coinm_account_snapshot()
    finally:
        get_settings.cache_clear()


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


def test_emergency_kill_switch_blocks_execution(tmp_path: Path) -> None:
    settings_path = tmp_path / "risk_settings.json"
    settings = update_btc_risk_settings(
        emergency_kill_switch_enabled=True,
        settings_path=str(settings_path),
    )
    preview = preview_btc_order(
        side="BUY",
        quantity="1",
        settings_path=str(settings_path),
    )
    blocked = execute_btc_order(
        side="BUY",
        quantity="1",
        confirm=LIVE_CONFIRMATION,
        settings_path=str(settings_path),
    )

    assert settings["emergency_kill_switch_enabled"] is True
    assert preview["risk"]["checks"]["emergency_kill_switch_off"] is False
    assert "emergency_kill_switch_enabled" in preview["risk"]["blocked_reasons"]
    assert blocked["status"] == "blocked"
    assert blocked["blocked_reason"] == "emergency_kill_switch_enabled"


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


def test_preview_btc_order_normalizes_public_order_inputs() -> None:
    payload = preview_btc_order(
        side=" buy ",
        order_type=" limit ",
        quantity=" 1 ",
        price=" 90000 ",
        time_in_force=" gtc ",
        position_side=" both ",
        reduce_only=False,
        client_order_id=" order-1 ",
    )

    assert payload["side"] == "BUY"
    assert payload["order_type"] == "LIMIT"
    assert payload["quantity"] == "1"
    assert payload["price"] == "90000"
    assert payload["time_in_force"] == "GTC"
    assert payload["position_side"] == "BOTH"
    assert payload["reduce_only"] is False
    assert payload["client_order_id"] == "order-1"
    assert payload["status"] == "preview"


def test_preview_btc_order_rejects_invalid_public_order_inputs() -> None:
    invalid_cases = [
        (
            {"side": "   "},
            "side must be a nonempty string",
        ),
        (
            {"side": 123},
            "side must be a nonempty string",
        ),
        (
            {"side": "HOLD"},
            "side must be BUY or SELL",
        ),
        (
            {"order_type": ""},
            "order_type must be a nonempty string",
        ),
        (
            {"order_type": "STOP"},
            "order_type must be MARKET or LIMIT",
        ),
        (
            {"quantity": 1},
            "quantity must be a nonempty string",
        ),
        (
            {"quantity": "NaN"},
            "invalid decimal value",
        ),
        (
            {"quantity": "0"},
            "quantity must be positive",
        ),
        (
            {"price": 90000, "order_type": "LIMIT"},
            "price must be a nonempty string",
        ),
        (
            {"price": "NaN", "order_type": "LIMIT"},
            "invalid decimal value",
        ),
        (
            {"time_in_force": "   ", "order_type": "LIMIT", "price": "90000"},
            "time_in_force must be a nonempty string",
        ),
        (
            {"position_side": []},
            "position_side must be a nonempty string",
        ),
        (
            {"position_side": "invalid"},
            "position_side must be BOTH, LONG, or SHORT",
        ),
        (
            {"reduce_only": "false"},
            "reduce_only must be a boolean",
        ),
        (
            {"client_order_id": ""},
            "client_order_id must be a nonempty string",
        ),
    ]

    for overrides, expected_error in invalid_cases:
        payload = {"side": "BUY", "quantity": "1"}
        payload.update(overrides)
        with pytest.raises(ValueError, match=expected_error):
            preview_btc_order(**payload)


def test_btc_order_tools_reject_order_text_control_character_inputs() -> None:
    invalid_cases = [
        (
            {"side": "BUY\n"},
            "side must not contain control characters",
        ),
        (
            {"order_type": "MARKET\n"},
            "order_type must not contain control characters",
        ),
        (
            {"quantity": "1\n"},
            "quantity must not contain control characters",
        ),
        (
            {"order_type": "LIMIT", "price": "90000\n"},
            "price must not contain control characters",
        ),
        (
            {"order_type": "LIMIT", "price": "90000", "time_in_force": "GTC\n"},
            "time_in_force must not contain control characters",
        ),
        (
            {"position_side": "BOTH\n"},
            "position_side must not contain control characters",
        ),
        (
            {"client_order_id": "order-1\n"},
            "client_order_id must not contain control characters",
        ),
    ]

    for overrides, expected_error in invalid_cases:
        payload = {"side": "BUY", "quantity": "1"}
        payload.update(overrides)
        with pytest.raises(ValueError, match=expected_error):
            preview_btc_order(**payload)

    with pytest.raises(ValueError, match="side must not contain control characters"):
        execute_btc_order(side="BUY\n", quantity="1")


def test_harness_rejects_invalid_btc_order_input_with_failure_audit(
    tmp_path: Path,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    input_payload = {"side": "BUY", "quantity": "1", "reduce_only": "false"}
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "preview_btc_order",
            "--input-json",
            json.dumps(input_payload),
            "--audit-log-path",
            str(audit_path),
        ],
        check=False,
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    events = read_audit_events(audit_log_path=str(audit_path))
    event = events[0]

    assert result.returncode != 0
    assert result.stdout == ""
    assert "reduce_only must be a boolean" in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "preview_btc_order"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "reduce_only must be a boolean" in event["details"]["error"]


def test_harness_rejects_btc_order_text_control_character_with_failure_audit(
    tmp_path: Path,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    input_payload = {"side": "BUY\n", "quantity": "1"}
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "preview_btc_order",
            "--input-json",
            json.dumps(input_payload),
            "--audit-log-path",
            str(audit_path),
        ],
        check=False,
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    events = read_audit_events(audit_log_path=str(audit_path))
    event = events[0]

    assert result.returncode != 0
    assert result.stdout == ""
    assert "side must not contain control characters" in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "preview_btc_order"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "side must not contain control characters" in event["details"]["error"]


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


def test_signed_queries_reject_invalid_recv_window_ms() -> None:
    intent = BinanceOrderIntent(
        symbol=ALLOWED_SYMBOL,
        side="BUY",
        order_type="MARKET",
        quantity="1",
    )

    with pytest.raises(ValueError, match="recv_window_ms must be a positive integer"):
        signed_order_query(
            intent,
            api_secret="secret",
            timestamp_ms=1234567890,
            recv_window_ms=0,
        )
    with pytest.raises(ValueError, match="recv_window_ms must be a positive integer"):
        signed_read_query(
            {"pair": "BTCUSD"},
            api_secret="secret",
            timestamp_ms=1234567890,
            recv_window_ms=-1,
        )


def test_execute_btc_order_uses_valid_env_recv_window_in_signed_request(
    tmp_path: Path,
    monkeypatch,
) -> None:
    credentials_path = tmp_path / "binance_credentials.enc.json"
    state_path = tmp_path / "risk_state.json"
    requests = []
    save_binance_credentials(
        api_key="abcde12345key",
        api_secret="super-secret",
        passphrase="local-passphrase",
        credentials_path=str(credentials_path),
    )
    monkeypatch.setenv("HALO_SWING_BINANCE_ENABLE_LIVE_TRADING", "true")
    monkeypatch.setenv("HALO_SWING_BINANCE_RECV_WINDOW_MS", "6000")
    get_settings.cache_clear()

    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, *_args: object) -> bool:
            return False

        def read(self) -> bytes:
            return json.dumps({"orderId": 123, "symbol": ALLOWED_SYMBOL}).encode()

    def fake_urlopen(http_request, timeout: int):
        requests.append((http_request, timeout))
        return FakeResponse()

    monkeypatch.setattr("halo_swing_mcp.binance_btc.request.urlopen", fake_urlopen)

    try:
        payload = execute_btc_order(
            side="BUY",
            quantity="1",
            confirm=LIVE_CONFIRMATION,
            credential_passphrase="local-passphrase",
            credentials_path=str(credentials_path),
            state_path=str(state_path),
        )
    finally:
        get_settings.cache_clear()

    body = requests[0][0].data.decode()
    assert payload["status"] == "submitted"
    assert parse.parse_qs(body)["recvWindow"] == ["6000"]


def test_execute_btc_order_rejects_invalid_env_recv_window_without_network(
    tmp_path: Path,
    monkeypatch,
) -> None:
    credentials_path = tmp_path / "binance_credentials.enc.json"
    state_path = tmp_path / "risk_state.json"
    save_binance_credentials(
        api_key="abcde12345key",
        api_secret="super-secret",
        passphrase="local-passphrase",
        credentials_path=str(credentials_path),
    )
    monkeypatch.setenv("HALO_SWING_BINANCE_ENABLE_LIVE_TRADING", "true")
    monkeypatch.setenv("HALO_SWING_BINANCE_RECV_WINDOW_MS", "0")
    get_settings.cache_clear()

    def fail_urlopen(*_args: object, **_kwargs: object) -> None:
        raise AssertionError("network call must not run with invalid recvWindow")

    monkeypatch.setattr("halo_swing_mcp.binance_btc.request.urlopen", fail_urlopen)

    try:
        with pytest.raises(
            ValueError,
            match="HALO_SWING_BINANCE_RECV_WINDOW_MS must be a positive integer",
        ):
            execute_btc_order(
                side="BUY",
                quantity="1",
                confirm=LIVE_CONFIRMATION,
                credential_passphrase="local-passphrase",
                credentials_path=str(credentials_path),
                state_path=str(state_path),
            )
    finally:
        get_settings.cache_clear()


def test_account_snapshot_rejects_invalid_env_recv_window_without_network(
    tmp_path: Path,
    monkeypatch,
) -> None:
    credentials_path = tmp_path / "binance_credentials.enc.json"
    save_binance_credentials(
        api_key="abcde12345key",
        api_secret="super-secret",
        passphrase="local-passphrase",
        credentials_path=str(credentials_path),
    )
    monkeypatch.setenv("HALO_SWING_BINANCE_RECV_WINDOW_MS", "-1")
    get_settings.cache_clear()

    def fail_urlopen(*_args: object, **_kwargs: object) -> None:
        raise AssertionError("network call must not run with invalid recvWindow")

    monkeypatch.setattr("halo_swing_mcp.binance_btc.request.urlopen", fail_urlopen)

    try:
        with pytest.raises(
            ValueError,
            match="HALO_SWING_BINANCE_RECV_WINDOW_MS must be a positive integer",
        ):
            get_binance_coinm_account_snapshot(
                credential_passphrase="local-passphrase",
                credentials_path=str(credentials_path),
            )
    finally:
        get_settings.cache_clear()


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


def test_save_binance_credentials_normalizes_public_inputs(tmp_path: Path) -> None:
    credentials_path = tmp_path / "binance_credentials.enc.json"
    status = save_binance_credentials(
        api_key=" abcde12345key ",
        api_secret=" super-secret ",
        passphrase="local-passphrase",
        credentials_path=f" {credentials_path} ",
    )
    credentials = load_binance_credentials(
        "local-passphrase",
        credentials_path=f" {credentials_path} ",
    )

    assert status["configured"] is True
    assert status["credentials_path"] == str(credentials_path)
    assert status["api_key_hint"] == "abcde...5key"
    assert credentials.api_key == "abcde12345key"
    assert credentials.api_secret == "super-secret"
    assert credentials_path.exists()


def test_binance_credentials_normalizes_env_credentials_path(
    tmp_path: Path,
    monkeypatch,
) -> None:
    credentials_path = tmp_path / "binance_credentials.enc.json"
    monkeypatch.setenv(
        "HALO_SWING_BINANCE_CREDENTIALS_PATH",
        f" {credentials_path} ",
    )
    get_settings.cache_clear()

    status = get_binance_credentials_status()

    assert status["configured"] is False
    assert status["credentials_path"] == str(credentials_path)
    assert not credentials_path.exists()


def test_binance_credentials_reject_env_credentials_path_without_fallback(
    tmp_path: Path,
    monkeypatch,
) -> None:
    invalid_cases = [
        (
            "",
            "HALO_SWING_BINANCE_CREDENTIALS_PATH must be a nonempty string",
            tmp_path / "state",
        ),
        (
            "   ",
            "HALO_SWING_BINANCE_CREDENTIALS_PATH must be a nonempty string",
            tmp_path / "   ",
        ),
        (
            f"{tmp_path / 'bad'}\x7fcredentials.enc.json",
            "HALO_SWING_BINANCE_CREDENTIALS_PATH must not contain control characters",
            tmp_path / "bad\x7fcredentials.enc.json",
        ),
    ]

    for env_value, expected_error, unexpected_path in invalid_cases:
        monkeypatch.setenv("HALO_SWING_BINANCE_CREDENTIALS_PATH", env_value)
        get_settings.cache_clear()

        with pytest.raises(ValueError, match=expected_error):
            get_binance_credentials_status()
        with pytest.raises(ValueError, match=expected_error):
            save_binance_credentials(
                api_key="abcde12345key",
                api_secret="super-secret",
                passphrase="local-passphrase",
            )
        assert not unexpected_path.exists()


def test_save_binance_credentials_rejects_invalid_public_inputs(
    tmp_path: Path,
) -> None:
    credentials_path = tmp_path / "binance_credentials.enc.json"
    invalid_cases = [
        (
            {"api_key": 123},
            "api_key must be a nonempty string",
        ),
        (
            {"api_key": "   "},
            "api_key must be a nonempty string",
        ),
        (
            {"api_secret": []},
            "api_secret must be a nonempty string",
        ),
        (
            {"api_secret": ""},
            "api_secret must be a nonempty string",
        ),
        (
            {"passphrase": "        "},
            "passphrase must be a nonempty string",
        ),
        (
            {"passphrase": "short"},
            "passphrase must be at least 8 characters",
        ),
        (
            {"credentials_path": ""},
            "credentials_path must be a nonempty string",
        ),
        (
            {"credentials_path": 123},
            "credentials_path must be a nonempty string",
        ),
    ]

    for overrides, expected_error in invalid_cases:
        payload = {
            "api_key": "abcde12345key",
            "api_secret": "super-secret",
            "passphrase": "local-passphrase",
            "credentials_path": str(credentials_path),
        }
        payload.update(overrides)
        with pytest.raises(ValueError, match=expected_error):
            save_binance_credentials(**payload)
        assert not credentials_path.exists()


def test_binance_credentials_reject_credentials_path_control_character_inputs(
    tmp_path: Path,
) -> None:
    credentials_path = tmp_path / "binance_credentials.enc.json"

    with pytest.raises(
        ValueError,
        match="credentials_path must not contain control characters",
    ):
        save_binance_credentials(
            api_key="abcde12345key",
            api_secret="super-secret",
            passphrase="local-passphrase",
            credentials_path=f"{credentials_path}\n",
        )

    with pytest.raises(
        ValueError,
        match="credentials_path must not contain control characters",
    ):
        get_binance_credentials_status(f"{credentials_path}\n")

    with pytest.raises(
        ValueError,
        match="credentials_path must not contain control characters",
    ):
        load_binance_credentials(
            "local-passphrase",
            credentials_path=f"{credentials_path}\n",
        )

    assert not credentials_path.exists()


def test_binance_credentials_reject_secret_control_character_inputs(
    tmp_path: Path,
) -> None:
    credentials_path = tmp_path / "binance_credentials.enc.json"
    invalid_save_cases = [
        (
            {"api_key": "abcde12345key\n"},
            "api_key must not contain control characters",
        ),
        (
            {"api_secret": "super-secret\n"},
            "api_secret must not contain control characters",
        ),
        (
            {"passphrase": "local-passphrase\n"},
            "passphrase must not contain control characters",
        ),
    ]

    for overrides, expected_error in invalid_save_cases:
        payload = {
            "api_key": "abcde12345key",
            "api_secret": "super-secret",
            "passphrase": "local-passphrase",
            "credentials_path": str(credentials_path),
        }
        payload.update(overrides)
        with pytest.raises(ValueError, match=expected_error):
            save_binance_credentials(**payload)
        assert not credentials_path.exists()

    save_binance_credentials(
        api_key="abcde12345key",
        api_secret="super-secret",
        passphrase="local-passphrase",
        credentials_path=str(credentials_path),
    )

    with pytest.raises(
        ValueError,
        match="passphrase must not contain control characters",
    ):
        load_binance_credentials(
            "local-passphrase\n",
            credentials_path=str(credentials_path),
        )


def test_harness_rejects_invalid_save_credentials_input_with_failure_audit(
    tmp_path: Path,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    credentials_path = tmp_path / "binance_credentials.enc.json"
    input_payload = {
        "api_key": "   ",
        "api_secret": "super-secret",
        "passphrase": "local-passphrase",
        "credentials_path": str(credentials_path),
    }
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "save_binance_credentials",
            "--input-json",
            json.dumps(input_payload),
            "--audit-log-path",
            str(audit_path),
        ],
        check=False,
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    events = read_audit_events(audit_log_path=str(audit_path))
    event = events[0]
    serialized_event = json.dumps(event)

    assert result.returncode != 0
    assert result.stdout == ""
    assert "api_key must be a nonempty string" in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "save_binance_credentials"
    assert event["outcome"] == "failure"
    assert event["details"]["input"]["api_key"] == "[REDACTED]"
    assert event["details"]["input"]["api_secret"] == "[REDACTED]"
    assert event["details"]["input"]["passphrase"] == "[REDACTED]"
    assert event["details"]["input"]["credentials_path"] == "[REDACTED]"
    assert "output_summary" not in event["details"]
    assert "api_key must be a nonempty string" in event["details"]["error"]
    assert "super-secret" not in serialized_event
    assert "local-passphrase" not in serialized_event
    assert str(credentials_path) not in serialized_event
    assert not credentials_path.exists()


def test_harness_rejects_secret_control_character_with_failure_audit(
    tmp_path: Path,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    credentials_path = tmp_path / "binance_credentials.enc.json"
    input_payload = {
        "api_key": "abcde12345key\n",
        "api_secret": "super-secret",
        "passphrase": "local-passphrase",
        "credentials_path": str(credentials_path),
    }
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "save_binance_credentials",
            "--input-json",
            json.dumps(input_payload),
            "--audit-log-path",
            str(audit_path),
        ],
        check=False,
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    events = read_audit_events(audit_log_path=str(audit_path))
    event = events[0]
    serialized_event = json.dumps(event)

    assert result.returncode != 0
    assert result.stdout == ""
    assert "api_key must not contain control characters" in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "save_binance_credentials"
    assert event["outcome"] == "failure"
    assert event["details"]["input"]["api_key"] == "[REDACTED]"
    assert event["details"]["input"]["api_secret"] == "[REDACTED]"
    assert event["details"]["input"]["passphrase"] == "[REDACTED]"
    assert event["details"]["input"]["credentials_path"] == "[REDACTED]"
    assert "output_summary" not in event["details"]
    assert "api_key must not contain control characters" in event["details"]["error"]
    assert "abcde12345key" not in serialized_event
    assert "super-secret" not in serialized_event
    assert "local-passphrase" not in serialized_event
    assert str(credentials_path) not in serialized_event
    assert not credentials_path.exists()


def test_harness_rejects_credentials_path_control_character_with_failure_audit(
    tmp_path: Path,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    credentials_path = tmp_path / "binance_credentials.enc.json"
    input_payload = {
        "api_key": "abcde12345key",
        "api_secret": "super-secret",
        "passphrase": "local-passphrase",
        "credentials_path": f"{credentials_path}\n",
    }
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "save_binance_credentials",
            "--input-json",
            json.dumps(input_payload),
            "--audit-log-path",
            str(audit_path),
        ],
        check=False,
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    events = read_audit_events(audit_log_path=str(audit_path))
    event = events[0]
    serialized_event = json.dumps(event)

    assert result.returncode != 0
    assert result.stdout == ""
    assert "credentials_path must not contain control characters" in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "save_binance_credentials"
    assert event["outcome"] == "failure"
    assert event["details"]["input"]["api_key"] == "[REDACTED]"
    assert event["details"]["input"]["api_secret"] == "[REDACTED]"
    assert event["details"]["input"]["passphrase"] == "[REDACTED]"
    assert event["details"]["input"]["credentials_path"] == "[REDACTED]"
    assert "output_summary" not in event["details"]
    assert "credentials_path must not contain control characters" in event["details"][
        "error"
    ]
    assert "super-secret" not in serialized_event
    assert "local-passphrase" not in serialized_event
    assert str(credentials_path) not in serialized_event
    assert not credentials_path.exists()


def test_binance_credential_status_exposes_trade_only_policy_without_secrets(
    tmp_path: Path,
) -> None:
    credentials_path = tmp_path / "binance_credentials.enc.json"
    missing_status = get_binance_credentials_status(str(credentials_path))
    policy = binance_credential_policy()
    status = save_binance_credentials(
        api_key="abcde12345key",
        api_secret="super-secret",
        passphrase="local-passphrase",
        credentials_path=str(credentials_path),
    )
    registry_status = call_tool(
        "get_binance_credentials_status",
        {"credentials_path": str(credentials_path)},
    )

    assert missing_status["configured"] is False
    assert list(missing_status) == EXPECTED_MISSING_CREDENTIAL_STATUS_KEYS
    assert missing_status["credential_policy"] == policy
    assert status["credential_policy"] == policy
    assert registry_status == status
    assert list(status) == EXPECTED_CONFIGURED_CREDENTIAL_STATUS_KEYS
    assert list(status["kdf"]) == EXPECTED_SAFE_CREDENTIAL_KDF_KEYS
    assert list(status["cipher"]) == EXPECTED_SAFE_CREDENTIAL_CIPHER_KEYS
    assert list(status["credential_policy"]) == EXPECTED_BINANCE_CREDENTIAL_POLICY_KEYS
    assert policy["schema_version"] == "binance_credential_policy.v1"
    assert policy["trade_permission_required"] is True
    assert policy["withdraw_permission_allowed"] is False
    assert "withdraw" in policy["forbidden_permissions"]
    assert policy["passphrase_handling"] == "manual_input_only"
    assert policy["passphrase_persistence"] == "forbidden"
    assert status["api_key_hint"] == "abcde...5key"
    assert status["kdf"]["name"] == "PBKDF2HMAC-SHA256"
    assert status["cipher"]["name"] == "Fernet"
    assert status["secret_values_returned"] is False
    assert status["passphrase_persisted"] is False
    serialized_status = json.dumps(status)
    assert '"api_secret":' not in serialized_status
    assert '"api_key":' not in serialized_status
    assert "super-secret" not in serialized_status
    assert "local-passphrase" not in serialized_status
    assert "salt_b64" not in serialized_status
    assert '"token":' not in serialized_status


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


def test_normalize_binance_coinm_account_snapshot_is_offline_read_only() -> None:
    payload = normalize_binance_coinm_account_snapshot(
        balance=[
            {
                "asset": "BTC",
                "balance": "0.25000000",
                "availableBalance": "0.20000000",
                "crossWalletBalance": "0.24000000",
                "crossUnPnl": "0.01000000",
            }
        ],
        positions=[
            {
                "symbol": ALLOWED_SYMBOL,
                "positionAmt": "3",
                "entryPrice": "90000",
                "markPrice": "92000",
                "unRealizedProfit": "0.0065",
                "liquidationPrice": "65000",
                "leverage": "2",
                "marginType": "cross",
                "positionSide": "BOTH",
            }
        ],
        as_of="2026-05-10T00:00:00Z",
        coinm_contract_size_usd=100,
    )

    assert payload["schema_version"] == "binance_coinm_portfolio_snapshot.v1"
    assert payload["status"] == "ok"
    assert payload["snapshot_source"] == "caller_supplied"
    assert payload["portfolio_sync_contract"]["read_only"] is True
    assert payload["portfolio_sync_contract"]["order_submission"] is False
    assert payload["portfolio_sync_contract"]["network_call"] is False
    assert payload["portfolio_sync_contract"]["credential_required"] is False
    assert payload["portfolio_sync_contract"]["secret_values_returned"] is False
    assert payload["portfolio_sync_contract"]["raw_snapshot_returned"] is False
    assert payload["balances"][0]["asset"] == "BTC"
    assert payload["btc_position"]["position_state"] == "long"
    assert payload["btc_position"]["position_amt_contracts"] == "3"
    assert payload["btc_position"]["estimated_notional_usd"] == "300"
    assert payload["position_detected"] is True
    assert payload["guard"]["status"] == "ok"
    assert payload["live_data_required"] is False


def test_normalize_binance_coinm_account_snapshot_normalizes_public_inputs() -> None:
    payload = normalize_binance_coinm_account_snapshot(
        balance=[
            {
                "asset": " BTC ",
                "balance": " 0.25000000 ",
                "availableBalance": " 0.20000000 ",
                "crossWalletBalance": " 0.24000000 ",
                "crossUnPnl": " 0.01000000 ",
            }
        ],
        positions=[
            {
                "symbol": ALLOWED_SYMBOL,
                "positionAmt": " 3 ",
                "entryPrice": " 90000 ",
                "markPrice": " 92000 ",
                "unRealizedProfit": " 0.0065 ",
                "liquidationPrice": " 65000 ",
                "leverage": " 2 ",
                "marginType": " cross ",
                "positionSide": " BOTH ",
            }
        ],
        as_of=" 2026-05-10T00:00:00Z ",
        coinm_contract_size_usd=100,
    )

    assert payload["as_of"] == "2026-05-10T00:00:00Z"
    assert payload["balances"][0]["asset"] == "BTC"
    assert payload["balances"][0]["balance"] == "0.25"
    assert payload["balances"][0]["available_balance"] == "0.2"
    assert payload["btc_position"]["position_side"] == "BOTH"
    assert payload["btc_position"]["position_amt_contracts"] == "3"
    assert payload["btc_position"]["contract_size_usd"] == "100"
    assert payload["btc_position"]["margin_type"] == "cross"
    assert payload["guard"]["status"] == "ok"


def test_normalize_binance_coinm_account_snapshot_rejects_invalid_public_inputs() -> None:
    invalid_cases = [
        (
            {"balance": {"asset": "BTC"}},
            "balance must be a list of objects",
        ),
        (
            {"balance": ["bad-row"]},
            "balance must be a list of objects",
        ),
        (
            {"positions": {"symbol": ALLOWED_SYMBOL}},
            "positions must be a list of objects",
        ),
        (
            {"positions": ["bad-row"]},
            "positions must be a list of objects",
        ),
        (
            {"as_of": "   "},
            "as_of must be a nonempty string",
        ),
        (
            {"coinm_contract_size_usd": "100"},
            "coinm_contract_size_usd must be a positive finite number",
        ),
        (
            {"coinm_contract_size_usd": False},
            "coinm_contract_size_usd must be a positive finite number",
        ),
        (
            {"coinm_contract_size_usd": 0},
            "coinm_contract_size_usd must be a positive finite number",
        ),
        (
            {"balance": [{"asset": "BTC", "balance": "not-a-number"}]},
            "balance.balance must be a finite decimal value",
        ),
        (
            {"balance": [{"asset": "   "}]},
            "balance.asset must be a nonempty string",
        ),
        (
            {"positions": [{"symbol": ALLOWED_SYMBOL, "positionAmt": "not-a-number"}]},
            "positions.positionAmt must be a finite decimal value",
        ),
        (
            {"positions": [{"symbol": ALLOWED_SYMBOL, "positionSide": 123}]},
            "positions.positionSide must be a nonempty string",
        ),
    ]

    for overrides, expected_error in invalid_cases:
        with pytest.raises(ValueError, match=expected_error):
            normalize_binance_coinm_account_snapshot(**overrides)


def test_normalize_binance_coinm_account_snapshot_rejects_text_control_characters() -> None:
    invalid_cases = [
        (
            {"as_of": "2026-05-10T00:00:00Z\n"},
            "as_of must not contain control characters",
        ),
        (
            {"balance": [{"asset": "BTC\n"}]},
            "balance.asset must not contain control characters",
        ),
        (
            {"positions": [{"symbol": ALLOWED_SYMBOL, "positionSide": "BOTH\n"}]},
            "positions.positionSide must not contain control characters",
        ),
        (
            {"positions": [{"symbol": ALLOWED_SYMBOL, "leverage": "2\n"}]},
            "positions.leverage must not contain control characters",
        ),
        (
            {"positions": [{"symbol": ALLOWED_SYMBOL, "marginType": "cross\n"}]},
            "positions.marginType must not contain control characters",
        ),
    ]

    for overrides, expected_error in invalid_cases:
        with pytest.raises(ValueError, match=expected_error):
            normalize_binance_coinm_account_snapshot(**overrides)


def test_harness_rejects_invalid_portfolio_snapshot_input_with_failure_audit(
    tmp_path: Path,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    input_payload = {"balance": {"asset": "BTC"}}
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "normalize_binance_coinm_account_snapshot",
            "--input-json",
            json.dumps(input_payload),
            "--audit-log-path",
            str(audit_path),
        ],
        check=False,
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    events = read_audit_events(audit_log_path=str(audit_path))
    event = events[0]

    assert result.returncode != 0
    assert result.stdout == ""
    assert "balance must be a list of objects" in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "normalize_binance_coinm_account_snapshot"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "balance must be a list of objects" in event["details"]["error"]


def test_harness_rejects_portfolio_snapshot_text_control_character_with_failure_audit(
    tmp_path: Path,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    input_payload = {"balance": [{"asset": "BTC\n"}]}
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "normalize_binance_coinm_account_snapshot",
            "--input-json",
            json.dumps(input_payload),
            "--audit-log-path",
            str(audit_path),
        ],
        check=False,
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    events = read_audit_events(audit_log_path=str(audit_path))
    event = events[0]

    assert result.returncode != 0
    assert result.stdout == ""
    assert "balance.asset must not contain control characters" in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "normalize_binance_coinm_account_snapshot"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "balance.asset must not contain control characters" in event["details"][
        "error"
    ]


def test_preview_btc_order_reports_position_effect_from_snapshot() -> None:
    snapshot = normalize_binance_coinm_account_snapshot(
        positions=[
            {
                "symbol": ALLOWED_SYMBOL,
                "positionAmt": "3",
                "entryPrice": "90000",
                "markPrice": "92000",
            }
        ],
        coinm_contract_size_usd=100,
    )
    preview = preview_btc_order(
        side="SELL",
        quantity="1",
        portfolio_snapshot=snapshot,
    )
    effect = preview["position_effect"]

    assert effect["schema_version"] == "btc_order_position_effect.v1"
    assert effect["current_position_state"] == "long"
    assert effect["current_contracts"] == "3"
    assert effect["signed_order_contracts"] == "-1"
    assert effect["projected_contracts"] == "2"
    assert effect["effect"] == "reduces_long"
    assert effect["guard"]["status"] == "ok"
    assert effect["live_data_required"] is False


def test_preview_btc_order_flags_invalid_reduce_only_position_effect() -> None:
    snapshot = normalize_binance_coinm_account_snapshot(
        positions=[{"symbol": ALLOWED_SYMBOL, "positionAmt": "3"}],
    )
    preview = preview_btc_order(
        side="BUY",
        quantity="1",
        reduce_only=True,
        portfolio_snapshot=snapshot,
    )

    assert preview["position_effect"]["effect"] == "increases_long"
    assert preview["position_effect"]["guard"]["status"] == "conflict"
    assert any(
        check["name"] == "reduce_only_does_not_increase_or_flip"
        and check["passed"] is False
        for check in preview["position_effect"]["guard"]["checks"]
    )


def test_update_risk_settings_registry_supports_kill_switch(tmp_path: Path) -> None:
    settings_path = tmp_path / "risk_settings.json"
    payload = call_tool(
        "update_btc_risk_settings",
        {
            "emergency_kill_switch_enabled": True,
            "settings_path": str(settings_path),
        },
    )
    preview = call_tool(
        "preview_btc_order",
        {"settings_path": str(settings_path)},
    )

    assert payload["emergency_kill_switch_enabled"] is True
    assert preview["risk"]["valid"] is False
    assert "emergency_kill_switch_enabled" in preview["risk"]["blocked_reasons"]


def test_update_btc_risk_settings_normalizes_public_inputs(tmp_path: Path) -> None:
    settings_path = tmp_path / "risk_settings.json"
    payload = call_tool(
        "update_btc_risk_settings",
        {
            "max_notional_usd_per_order": 150,
            "max_daily_order_count": 4,
            "max_daily_loss_usd": 75,
            "coinm_contract_size_usd": 100,
            "emergency_kill_switch_enabled": False,
            "settings_path": f" {settings_path} ",
        },
    )

    assert payload["max_notional_usd_per_order"] == 150.0
    assert payload["max_daily_order_count"] == 4
    assert payload["max_daily_loss_usd"] == 75.0
    assert payload["coinm_contract_size_usd"] == 100.0
    assert payload["emergency_kill_switch_enabled"] is False
    assert payload["settings_path"] == str(settings_path)
    assert settings_path.exists()


def test_update_btc_risk_settings_rejects_invalid_public_inputs(
    tmp_path: Path,
) -> None:
    settings_path = tmp_path / "risk_settings.json"
    invalid_cases = [
        (
            {"max_notional_usd_per_order": "100"},
            "max_notional_usd_per_order must be a positive finite number",
        ),
        (
            {"max_notional_usd_per_order": 0},
            "max_notional_usd_per_order must be a positive finite number",
        ),
        (
            {"max_daily_order_count": 1.5},
            "max_daily_order_count must be a positive integer",
        ),
        (
            {"max_daily_order_count": False},
            "max_daily_order_count must be a positive integer",
        ),
        (
            {"max_daily_loss_usd": "50"},
            "max_daily_loss_usd must be a positive finite number",
        ),
        (
            {"coinm_contract_size_usd": False},
            "coinm_contract_size_usd must be a positive finite number",
        ),
        (
            {"emergency_kill_switch_enabled": "false"},
            "emergency_kill_switch_enabled must be a boolean",
        ),
        (
            {"settings_path": "   "},
            "settings_path must be a nonempty string",
        ),
    ]

    for overrides, expected_error in invalid_cases:
        payload = {"settings_path": str(settings_path)}
        payload.update(overrides)
        with pytest.raises(ValueError, match=expected_error):
            call_tool("update_btc_risk_settings", payload)


def test_btc_risk_tools_reject_path_control_character_inputs(
    tmp_path: Path,
) -> None:
    settings_path = tmp_path / "risk_settings.json"
    state_path = tmp_path / "risk_state.json"

    with pytest.raises(
        ValueError,
        match="settings_path must not contain control characters",
    ):
        call_tool("get_btc_risk_settings", {"settings_path": f"{settings_path}\n"})
    with pytest.raises(
        ValueError,
        match="settings_path must not contain control characters",
    ):
        call_tool(
            "update_btc_risk_settings",
            {
                "settings_path": f"{settings_path}\n",
                "max_notional_usd_per_order": 150,
            },
        )
    with pytest.raises(
        ValueError,
        match="state_path must not contain control characters",
    ):
        call_tool(
            "get_btc_risk_status",
            {
                "settings_path": str(settings_path),
                "state_path": f"{state_path}\n",
            },
        )
    with pytest.raises(
        ValueError,
        match="state_path must not contain control characters",
    ):
        call_tool(
            "reset_btc_daily_risk_state",
            {
                "daily_realized_loss_usd": 0,
                "daily_order_count": 0,
                "state_path": f"{state_path}\n",
            },
        )

    assert not settings_path.exists()
    assert not state_path.exists()


def test_btc_risk_tools_normalize_env_paths(
    tmp_path: Path,
    monkeypatch,
) -> None:
    settings_path = tmp_path / "risk_settings.json"
    state_path = tmp_path / "risk_state.json"
    monkeypatch.setenv("HALO_SWING_BTC_RISK_SETTINGS_PATH", f" {settings_path} ")
    monkeypatch.setenv("HALO_SWING_BTC_RISK_STATE_PATH", f" {state_path} ")
    get_settings.cache_clear()

    settings = call_tool(
        "update_btc_risk_settings",
        {"max_notional_usd_per_order": 150},
    )
    state = call_tool(
        "reset_btc_daily_risk_state",
        {"daily_realized_loss_usd": 0, "daily_order_count": 1},
    )
    status = call_tool("get_btc_risk_status", {})

    assert settings["settings_path"] == str(settings_path)
    assert state["state_path"] == str(state_path)
    assert status["settings"]["settings_path"] == str(settings_path)
    assert status["state"]["state_path"] == str(state_path)
    assert settings_path.exists()
    assert state_path.exists()


def test_btc_risk_tools_reject_env_settings_path_without_fallback(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.chdir(tmp_path)
    invalid_cases = [
        (
            "",
            "HALO_SWING_BTC_RISK_SETTINGS_PATH must be a nonempty string",
            tmp_path / "state",
        ),
        (
            "   ",
            "HALO_SWING_BTC_RISK_SETTINGS_PATH must be a nonempty string",
            tmp_path / "   ",
        ),
        (
            f"{tmp_path / 'bad'}\x7frisk_settings.json",
            "HALO_SWING_BTC_RISK_SETTINGS_PATH must not contain control characters",
            tmp_path / "bad\x7frisk_settings.json",
        ),
    ]

    for env_value, expected_error, unexpected_path in invalid_cases:
        monkeypatch.setenv("HALO_SWING_BTC_RISK_SETTINGS_PATH", env_value)
        get_settings.cache_clear()

        with pytest.raises(ValueError, match=expected_error):
            call_tool("get_btc_risk_settings", {})
        with pytest.raises(ValueError, match=expected_error):
            call_tool(
                "update_btc_risk_settings",
                {"max_notional_usd_per_order": 150},
            )
        assert not unexpected_path.exists()


def test_btc_risk_tools_reject_env_state_path_without_fallback(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.chdir(tmp_path)
    settings_path = tmp_path / "risk_settings.json"
    monkeypatch.setenv("HALO_SWING_BTC_RISK_SETTINGS_PATH", str(settings_path))
    invalid_cases = [
        (
            "",
            "HALO_SWING_BTC_RISK_STATE_PATH must be a nonempty string",
            tmp_path / "state",
        ),
        (
            "   ",
            "HALO_SWING_BTC_RISK_STATE_PATH must be a nonempty string",
            tmp_path / "   ",
        ),
        (
            f"{tmp_path / 'bad'}\x7frisk_state.json",
            "HALO_SWING_BTC_RISK_STATE_PATH must not contain control characters",
            tmp_path / "bad\x7frisk_state.json",
        ),
    ]

    for env_value, expected_error, unexpected_path in invalid_cases:
        monkeypatch.setenv("HALO_SWING_BTC_RISK_STATE_PATH", env_value)
        get_settings.cache_clear()

        with pytest.raises(ValueError, match=expected_error):
            call_tool("get_btc_risk_status", {})
        with pytest.raises(ValueError, match=expected_error):
            call_tool(
                "reset_btc_daily_risk_state",
                {"daily_realized_loss_usd": 0, "daily_order_count": 0},
            )
        assert not unexpected_path.exists()
    assert not settings_path.exists()


def test_reset_btc_daily_risk_state_normalizes_public_inputs(tmp_path: Path) -> None:
    state_path = tmp_path / "risk_state.json"
    payload = call_tool(
        "reset_btc_daily_risk_state",
        {
            "daily_realized_loss_usd": 12,
            "daily_order_count": 2,
            "state_path": f" {state_path} ",
        },
    )

    assert payload["daily_realized_loss_usd"] == 12.0
    assert payload["daily_order_count"] == 2
    assert payload["state_path"] == str(state_path)
    assert state_path.exists()


def test_reset_btc_daily_risk_state_rejects_invalid_public_inputs(
    tmp_path: Path,
) -> None:
    state_path = tmp_path / "risk_state.json"
    invalid_cases = [
        (
            {"daily_realized_loss_usd": "0"},
            "daily_realized_loss_usd must be a non-negative finite number",
        ),
        (
            {"daily_realized_loss_usd": -0.01},
            "daily_realized_loss_usd must be a non-negative finite number",
        ),
        (
            {"daily_order_count": "2"},
            "daily_order_count must be a non-negative integer",
        ),
        (
            {"daily_order_count": 1.5},
            "daily_order_count must be a non-negative integer",
        ),
        (
            {"daily_order_count": -1},
            "daily_order_count must be a non-negative integer",
        ),
        (
            {"daily_order_count": False},
            "daily_order_count must be a non-negative integer",
        ),
        (
            {"state_path": ""},
            "state_path must be a nonempty string",
        ),
    ]

    for overrides, expected_error in invalid_cases:
        payload = {"state_path": str(state_path)}
        payload.update(overrides)
        with pytest.raises(ValueError, match=expected_error):
            call_tool("reset_btc_daily_risk_state", payload)


def test_harness_rejects_invalid_risk_settings_input_with_failure_audit(
    tmp_path: Path,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    settings_path = tmp_path / "risk_settings.json"
    input_payload = {
        "settings_path": str(settings_path),
        "emergency_kill_switch_enabled": "false",
    }
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "update_btc_risk_settings",
            "--input-json",
            json.dumps(input_payload),
            "--audit-log-path",
            str(audit_path),
        ],
        check=False,
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    events = read_audit_events(audit_log_path=str(audit_path))
    event = events[0]

    assert result.returncode != 0
    assert result.stdout == ""
    assert "emergency_kill_switch_enabled must be a boolean" in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "update_btc_risk_settings"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert (
        "emergency_kill_switch_enabled must be a boolean"
        in event["details"]["error"]
    )
    assert not settings_path.exists()


def test_harness_rejects_risk_settings_path_control_character_with_failure_audit(
    tmp_path: Path,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    settings_path = tmp_path / "risk_settings.json"
    input_payload = {
        "settings_path": f"{settings_path}\n",
        "max_notional_usd_per_order": 150,
    }
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "update_btc_risk_settings",
            "--input-json",
            json.dumps(input_payload),
            "--audit-log-path",
            str(audit_path),
        ],
        check=False,
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    events = read_audit_events(audit_log_path=str(audit_path))
    event = events[0]

    assert result.returncode != 0
    assert result.stdout == ""
    assert "settings_path must not contain control characters" in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "update_btc_risk_settings"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "settings_path must not contain control characters" in event["details"][
        "error"
    ]
    assert not settings_path.exists()


def test_trading_admin_risk_settings_endpoint_normalizes_form_inputs(
    tmp_path: Path,
    monkeypatch,
) -> None:
    settings_path = tmp_path / "risk_settings.json"
    monkeypatch.setenv("HALO_SWING_BTC_RISK_SETTINGS_PATH", str(settings_path))
    get_settings.cache_clear()

    payload = _admin_json_request(
        "/api/risk-settings",
        {
            "max_notional_usd_per_order": " 150.5 ",
            "max_daily_order_count": "4",
            "max_daily_loss_usd": "75.25",
            "coinm_contract_size_usd": "100",
            "emergency_kill_switch_enabled": True,
        },
    )

    assert payload["max_notional_usd_per_order"] == 150.5
    assert payload["max_daily_order_count"] == 4
    assert payload["max_daily_loss_usd"] == 75.25
    assert payload["coinm_contract_size_usd"] == 100.0
    assert payload["emergency_kill_switch_enabled"] is True
    assert payload["settings_path"] == str(settings_path)
    assert settings_path.exists()


def test_trading_admin_risk_settings_endpoint_rejects_invalid_inputs(
    tmp_path: Path,
    monkeypatch,
) -> None:
    settings_path = tmp_path / "risk_settings.json"
    monkeypatch.setenv("HALO_SWING_BTC_RISK_SETTINGS_PATH", str(settings_path))
    get_settings.cache_clear()
    invalid_cases = [
        (
            {"max_notional_usd_per_order": "NaN"},
            "max_notional_usd_per_order must be a positive finite number",
        ),
        (
            {"max_daily_order_count": "1.5"},
            "max_daily_order_count must be a positive integer",
        ),
        (
            {"emergency_kill_switch_enabled": "false"},
            "emergency_kill_switch_enabled must be a boolean",
        ),
    ]

    for input_payload, expected_error in invalid_cases:
        response_payload = _admin_json_request(
            "/api/risk-settings",
            input_payload,
            expected_status="HTTP/1.0 400 Bad Request",
        )

        assert expected_error in response_payload["error"]
        assert not settings_path.exists()


def test_trading_admin_risk_settings_endpoint_rejects_control_characters(
    tmp_path: Path,
    monkeypatch,
) -> None:
    settings_path = tmp_path / "risk_settings.json"
    monkeypatch.setenv("HALO_SWING_BTC_RISK_SETTINGS_PATH", str(settings_path))
    get_settings.cache_clear()
    invalid_cases = [
        (
            {"max_notional_usd_per_order": "150\n"},
            "max_notional_usd_per_order must not contain control characters",
        ),
        (
            {"max_daily_order_count": "4\n"},
            "max_daily_order_count must not contain control characters",
        ),
        (
            {"max_daily_loss_usd": "75\n"},
            "max_daily_loss_usd must not contain control characters",
        ),
        (
            {"coinm_contract_size_usd": "100\n"},
            "coinm_contract_size_usd must not contain control characters",
        ),
    ]

    for input_payload, expected_error in invalid_cases:
        response_payload = _admin_json_request(
            "/api/risk-settings",
            input_payload,
            expected_status="HTTP/1.0 400 Bad Request",
        )

        assert response_payload == {"error": expected_error}
        assert not settings_path.exists()


def test_trading_admin_risk_settings_endpoint_rejects_invalid_env_path_without_write(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("HALO_SWING_BTC_RISK_SETTINGS_PATH", "   ")
    get_settings.cache_clear()

    try:
        response_payload = _admin_json_request(
            "/api/risk-settings",
            {"max_notional_usd_per_order": "150"},
            expected_status="HTTP/1.0 400 Bad Request",
        )
    finally:
        get_settings.cache_clear()

    assert response_payload == {
        "error": "HALO_SWING_BTC_RISK_SETTINGS_PATH must be a nonempty string"
    }
    assert not (tmp_path / "state").exists()
    assert not (tmp_path / "   ").exists()


def test_trading_admin_credentials_endpoint_rejects_invalid_input_without_write(
    tmp_path: Path,
    monkeypatch,
) -> None:
    credentials_path = tmp_path / "credentials.enc.json"
    monkeypatch.setenv("HALO_SWING_BINANCE_CREDENTIALS_PATH", str(credentials_path))
    get_settings.cache_clear()
    response_payload = _admin_json_request(
        "/api/credentials",
        {
            "api_key": 123,
            "api_secret": "super-secret",
            "passphrase": "local-passphrase",
        },
        expected_status="HTTP/1.0 400 Bad Request",
    )
    serialized_response = json.dumps(response_payload)

    assert response_payload == {"error": "api_key must be a nonempty string"}
    assert not credentials_path.exists()
    assert "super-secret" not in serialized_response
    assert "local-passphrase" not in serialized_response


def test_trading_admin_credentials_endpoint_rejects_control_characters_without_write(
    tmp_path: Path,
    monkeypatch,
) -> None:
    credentials_path = tmp_path / "credentials.enc.json"
    monkeypatch.setenv("HALO_SWING_BINANCE_CREDENTIALS_PATH", str(credentials_path))
    get_settings.cache_clear()
    invalid_cases = [
        (
            {
                "api_key": "abcde12345key\n",
                "api_secret": "super-secret",
                "passphrase": "local-passphrase",
            },
            "api_key must not contain control characters",
        ),
        (
            {
                "api_key": "abcde12345key",
                "api_secret": "super-secret\n",
                "passphrase": "local-passphrase",
            },
            "api_secret must not contain control characters",
        ),
        (
            {
                "api_key": "abcde12345key",
                "api_secret": "super-secret",
                "passphrase": "local-passphrase\n",
            },
            "passphrase must not contain control characters",
        ),
    ]

    for input_payload, expected_error in invalid_cases:
        response_payload = _admin_json_request(
            "/api/credentials",
            input_payload,
            expected_status="HTTP/1.0 400 Bad Request",
        )
        serialized_response = json.dumps(response_payload)

        assert response_payload == {"error": expected_error}
        assert not credentials_path.exists()
        assert "abcde12345key" not in serialized_response
        assert "super-secret" not in serialized_response
        assert "local-passphrase" not in serialized_response


def test_trading_admin_credentials_endpoint_rejects_invalid_env_path_without_secret_leak(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("HALO_SWING_BINANCE_CREDENTIALS_PATH", "   ")
    get_settings.cache_clear()

    try:
        response_payload = _admin_json_request(
            "/api/credentials",
            {
                "api_key": "abcde12345key",
                "api_secret": "super-secret",
                "passphrase": "local-passphrase",
            },
            expected_status="HTTP/1.0 400 Bad Request",
        )
    finally:
        get_settings.cache_clear()

    serialized_response = json.dumps(response_payload)
    assert response_payload == {
        "error": "HALO_SWING_BINANCE_CREDENTIALS_PATH must be a nonempty string."
    }
    assert not (tmp_path / "state").exists()
    assert not (tmp_path / "   ").exists()
    assert "abcde12345key" not in serialized_response
    assert "super-secret" not in serialized_response
    assert "local-passphrase" not in serialized_response


def test_trading_admin_order_preview_endpoint_rejects_invalid_text_inputs() -> None:
    response_payload = _admin_json_request(
        "/api/order-preview",
        {"side": 123, "quantity": "1"},
        expected_status="HTTP/1.0 400 Bad Request",
    )

    assert response_payload == {"error": "side must be a nonempty string"}


def test_trading_admin_order_preview_endpoint_rejects_control_characters() -> None:
    invalid_cases = [
        (
            {"side": "BUY\n", "quantity": "1"},
            "side must not contain control characters",
        ),
        (
            {"side": "BUY", "quantity": "1\n"},
            "quantity must not contain control characters",
        ),
        (
            {"side": "BUY", "quantity": "1", "position_side": "BOTH\n"},
            "position_side must not contain control characters",
        ),
    ]

    for input_payload, expected_error in invalid_cases:
        response_payload = _admin_json_request(
            "/api/order-preview",
            input_payload,
            expected_status="HTTP/1.0 400 Bad Request",
        )

        assert response_payload == {"error": expected_error}


def test_trading_admin_account_snapshot_endpoint_rejects_invalid_passphrase_type() -> None:
    response_payload = _admin_json_request(
        "/api/account-snapshot",
        {"credential_passphrase": 123},
        expected_status="HTTP/1.0 400 Bad Request",
    )

    assert response_payload == {
        "error": "credential_passphrase must be a string when provided"
    }


def test_trading_admin_account_snapshot_endpoint_rejects_passphrase_control_character() -> None:
    response_payload = _admin_json_request(
        "/api/account-snapshot",
        {"credential_passphrase": "local-passphrase\n"},
        expected_status="HTTP/1.0 400 Bad Request",
    )

    assert response_payload == {
        "error": "credential_passphrase must not contain control characters"
    }


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
    expected_credentials = get_binance_credentials_status(str(credentials_path))
    serialized_payload = json.dumps(payload)

    assert "Halo Swing Trading Admin" in HTML
    assert payload["credentials"] == expected_credentials
    assert payload["credentials"]["configured"] is True
    assert payload["credentials"]["api_key_hint"] == "abcde...5key"
    assert list(payload["credentials"]) == EXPECTED_CONFIGURED_CREDENTIAL_STATUS_KEYS
    assert list(payload["credentials"]["kdf"]) == EXPECTED_SAFE_CREDENTIAL_KDF_KEYS
    assert list(payload["credentials"]["cipher"]) == EXPECTED_SAFE_CREDENTIAL_CIPHER_KEYS
    assert (
        list(payload["credentials"]["credential_policy"])
        == EXPECTED_BINANCE_CREDENTIAL_POLICY_KEYS
    )
    assert payload["credentials"]["secret_values_returned"] is False
    assert payload["credentials"]["passphrase_persisted"] is False
    assert '"api_secret":' not in serialized_payload
    assert '"api_key":' not in serialized_payload
    assert "abcde12345key" not in serialized_payload
    assert "super-secret" not in serialized_payload
    assert "local-passphrase" not in serialized_payload
    assert "salt_b64" not in serialized_payload
    assert '"token":' not in serialized_payload
    assert payload["risk"]["settings"]["emergency_kill_switch_enabled"] is False


def test_trading_admin_status_prevalidates_binance_env_before_local_reads(
    monkeypatch,
) -> None:
    monkeypatch.setenv("HALO_SWING_BINANCE_TESTNET", "yes")
    get_settings.cache_clear()

    def fail_credentials_status(*_args: object, **_kwargs: object) -> None:
        raise AssertionError("credential status must not load with invalid testnet env")

    def fail_risk_status(*_args: object, **_kwargs: object) -> None:
        raise AssertionError("risk status must not load with invalid testnet env")

    monkeypatch.setattr(
        "halo_swing_mcp.trading_admin_web.get_binance_credentials_status",
        fail_credentials_status,
    )
    monkeypatch.setattr(
        "halo_swing_mcp.trading_admin_web.get_btc_risk_status",
        fail_risk_status,
    )

    try:
        with pytest.raises(
            ValueError,
            match="HALO_SWING_BINANCE_TESTNET must be 'true' or 'false'",
        ):
            admin_status_payload()
    finally:
        get_settings.cache_clear()


def test_trading_admin_status_endpoint_returns_json_error_for_invalid_binance_env(
    monkeypatch,
) -> None:
    monkeypatch.setenv("HALO_SWING_BINANCE_TESTNET", "yes")
    get_settings.cache_clear()

    def fail_credentials_status(*_args: object, **_kwargs: object) -> None:
        raise AssertionError("credential status must not load with invalid testnet env")

    def fail_risk_status(*_args: object, **_kwargs: object) -> None:
        raise AssertionError("risk status must not load with invalid testnet env")

    monkeypatch.setattr(
        "halo_swing_mcp.trading_admin_web.get_binance_credentials_status",
        fail_credentials_status,
    )
    monkeypatch.setattr(
        "halo_swing_mcp.trading_admin_web.get_btc_risk_status",
        fail_risk_status,
    )

    try:
        response_payload = _admin_json_request(
            "/api/status",
            expected_status="HTTP/1.0 400 Bad Request",
        )
    finally:
        get_settings.cache_clear()

    assert "HALO_SWING_BINANCE_TESTNET must be 'true' or 'false'" in str(
        response_payload["error"]
    )


def test_trading_admin_connectivity_endpoint_rejects_invalid_env_without_network(
    monkeypatch,
) -> None:
    monkeypatch.setenv("HALO_SWING_BINANCE_TESTNET", "on")
    get_settings.cache_clear()

    def fail_urlopen(*_args: object, **_kwargs: object) -> None:
        raise AssertionError("network call must not run with invalid testnet env")

    monkeypatch.setattr("halo_swing_mcp.binance_btc.request.urlopen", fail_urlopen)

    try:
        response_payload = _admin_json_request(
            "/api/connectivity",
            {},
            expected_status="HTTP/1.0 400 Bad Request",
        )
    finally:
        get_settings.cache_clear()

    assert "HALO_SWING_BINANCE_TESTNET must be 'true' or 'false'" in str(
        response_payload["error"]
    )


def test_trading_admin_account_snapshot_endpoint_rejects_invalid_env_before_status(
    monkeypatch,
) -> None:
    monkeypatch.setenv("HALO_SWING_BINANCE_TESTNET", "yes")
    get_settings.cache_clear()

    def fail_credentials_status(*_args: object, **_kwargs: object) -> None:
        raise AssertionError("credential status must not load with invalid testnet env")

    def fail_urlopen(*_args: object, **_kwargs: object) -> None:
        raise AssertionError("network call must not run with invalid testnet env")

    monkeypatch.setattr(
        "halo_swing_mcp.binance_btc.get_binance_credentials_status",
        fail_credentials_status,
    )
    monkeypatch.setattr("halo_swing_mcp.binance_btc.request.urlopen", fail_urlopen)

    try:
        response_payload = _admin_json_request(
            "/api/account-snapshot",
            {},
            expected_status="HTTP/1.0 400 Bad Request",
        )
    finally:
        get_settings.cache_clear()

    assert "HALO_SWING_BINANCE_TESTNET must be 'true' or 'false'" in str(
        response_payload["error"]
    )


def test_trading_admin_order_preview_endpoint_rejects_invalid_env_before_risk(
    monkeypatch,
) -> None:
    monkeypatch.setenv("HALO_SWING_BINANCE_TESTNET", "yes")
    get_settings.cache_clear()

    def fail_estimate_notional(*_args: object, **_kwargs: object) -> None:
        raise AssertionError("notional estimate must not run with invalid testnet env")

    def fail_validate_risk(*_args: object, **_kwargs: object) -> None:
        raise AssertionError("risk validation must not run with invalid testnet env")

    monkeypatch.setattr(
        "halo_swing_mcp.binance_btc.estimate_notional_usd",
        fail_estimate_notional,
    )
    monkeypatch.setattr(
        "halo_swing_mcp.binance_btc.validate_btc_order_limits",
        fail_validate_risk,
    )

    try:
        response_payload = _admin_json_request(
            "/api/order-preview",
            {"side": "BUY", "quantity": "1"},
            expected_status="HTTP/1.0 400 Bad Request",
        )
    finally:
        get_settings.cache_clear()

    assert "HALO_SWING_BINANCE_TESTNET must be 'true' or 'false'" in str(
        response_payload["error"]
    )


def test_trading_admin_risk_state_reset_endpoint_rejects_invalid_env_path_without_write(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("HALO_SWING_BTC_RISK_STATE_PATH", "   ")
    get_settings.cache_clear()

    try:
        response_payload = _admin_json_request(
            "/api/risk-state/reset",
            {},
            expected_status="HTTP/1.0 400 Bad Request",
        )
    finally:
        get_settings.cache_clear()

    assert response_payload == {
        "error": "HALO_SWING_BTC_RISK_STATE_PATH must be a nonempty string"
    }
    assert not (tmp_path / "state").exists()
    assert not (tmp_path / "   ").exists()


def test_trading_admin_credentials_endpoint_returns_secret_safe_status(
    tmp_path: Path,
    monkeypatch,
) -> None:
    credentials_path = tmp_path / "credentials.enc.json"
    monkeypatch.setenv("HALO_SWING_BINANCE_CREDENTIALS_PATH", str(credentials_path))
    get_settings.cache_clear()
    input_payload = {
        "api_key": "abcde12345key",
        "api_secret": "super-secret",
        "passphrase": "local-passphrase",
    }

    response_payload = _admin_json_request("/api/credentials", input_payload)
    status_payload = _admin_json_request("/api/status")

    expected_credentials = get_binance_credentials_status(str(credentials_path))
    serialized_response = json.dumps(response_payload)
    serialized_status = json.dumps(status_payload)

    assert response_payload == expected_credentials
    assert status_payload["credentials"] == expected_credentials
    assert response_payload["configured"] is True
    assert response_payload["api_key_hint"] == "abcde...5key"
    assert response_payload["secret_values_returned"] is False
    assert response_payload["passphrase_persisted"] is False
    assert credentials_path.exists()
    for serialized in (serialized_response, serialized_status):
        assert '"api_secret":' not in serialized
        assert '"api_key":' not in serialized
        assert "abcde12345key" not in serialized
        assert "super-secret" not in serialized
        assert "local-passphrase" not in serialized
        assert "salt_b64" not in serialized
        assert '"token":' not in serialized


def test_trading_admin_account_snapshot_endpoint_blocks_secret_safely(
    tmp_path: Path,
    monkeypatch,
) -> None:
    credentials_path = tmp_path / "credentials.enc.json"
    monkeypatch.setenv("HALO_SWING_BINANCE_CREDENTIALS_PATH", str(credentials_path))
    get_settings.cache_clear()
    save_binance_credentials(
        api_key="abcde12345key",
        api_secret="super-secret",
        passphrase="local-passphrase",
        credentials_path=str(credentials_path),
    )

    blocked_payload = _admin_json_request("/api/account-snapshot", {})
    error_payload = _admin_json_request(
        "/api/account-snapshot",
        {"credential_passphrase": "wrong-passphrase"},
        expected_status="HTTP/1.0 400 Bad Request",
    )
    expected_credentials = get_binance_credentials_status(str(credentials_path))
    serialized_blocked = json.dumps(blocked_payload)
    serialized_error = json.dumps(error_payload)

    assert blocked_payload["status"] == "blocked"
    assert blocked_payload["blocked_reason"] == "missing_credential_passphrase"
    assert blocked_payload["credentials"] == expected_credentials
    assert blocked_payload["live_data_required"] is False
    assert error_payload == {"error": "invalid Binance credential passphrase."}
    for serialized in (serialized_blocked, serialized_error):
        assert '"api_secret":' not in serialized
        assert '"api_key":' not in serialized
        assert "abcde12345key" not in serialized
        assert "super-secret" not in serialized
        assert "local-passphrase" not in serialized
        assert "wrong-passphrase" not in serialized
        assert "salt_b64" not in serialized
        assert '"token":' not in serialized


def _admin_json_request(
    path: str,
    payload: dict[str, object] | None = None,
    expected_status: str = "HTTP/1.0 200 OK",
) -> dict[str, object]:
    body = json.dumps(payload).encode("utf-8") if payload is not None else b""
    method = "POST" if payload is not None else "GET"
    raw_request = (
        f"{method} {path} HTTP/1.1\r\n"
        "Host: 127.0.0.1\r\n"
        "Content-Type: application/json\r\n"
        f"Content-Length: {len(body)}\r\n"
        "\r\n"
    ).encode("utf-8") + body
    socket = _MemorySocket(raw_request)
    create_handler()(socket, ("127.0.0.1", 0), object())
    response = socket.output.getvalue()
    headers, _, response_body = response.partition(b"\r\n\r\n")
    status_line = headers.splitlines()[0].decode("ascii")

    assert status_line == expected_status
    parsed = json.loads(response_body.decode("utf-8"))
    assert isinstance(parsed, dict)
    return parsed


class _MemorySocket:
    def __init__(self, raw_request: bytes) -> None:
        self.input = BytesIO(raw_request)
        self.output = BytesIO()

    def makefile(
        self,
        mode: str,
        buffering: int | None = None,
    ) -> BytesIO:
        if "r" in mode:
            return self.input
        return self.output

    def sendall(self, data: bytes) -> None:
        self.output.write(data)

    def close(self) -> None:
        self.input.close()
        self.output.close()
