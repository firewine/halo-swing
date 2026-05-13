import json
import subprocess
import sys
from pathlib import Path

import pytest

from halo_swing_mcp.audit import read_audit_events
from halo_swing_mcp.config import get_settings
from halo_swing_mcp.secret_store import save_binance_credentials
from halo_swing_mcp.tools.readiness import get_integration_readiness


ROOT = Path(__file__).resolve().parents[1]
READINESS_ENV_KEYS = (
    "HALO_SWING_HERMES_CONFIG_PATH",
    "HALO_SWING_TELEGRAM_BOT_TOKEN",
    "HALO_SWING_TELEGRAM_GATEWAY",
    "HALO_SWING_TELEGRAM_GATEWAY_URL",
    "TELEGRAM_BOT_TOKEN",
    "FRED_API_KEY",
    "NEWS_API_KEY",
    "HALO_SWING_FRED_API_KEY",
    "HALO_SWING_NEWS_API_KEY",
    "HALO_SWING_BINANCE_ENABLE_LIVE_TRADING",
    "HALO_SWING_MARKET_DATA_SOURCE",
    "HALO_SWING_MARKET_DATA_API_KEY",
    "HALO_SWING_MACRO_SOURCE",
    "HALO_SWING_NEWS_SOURCE",
    "POLYGON_API_KEY",
    "ALPACA_API_KEY",
    "TIINGO_API_KEY",
)
EXPECTED_READINESS_PAYLOAD_KEYS = [
    "status",
    "gates",
    "next_actions",
    "live_data_required",
]
EXPECTED_READINESS_GATE_NAMES = [
    "hermes",
    "telegram",
    "migration",
    "repository",
    "binance_testnet_read_only",
    "live_order_submission",
    "live_data",
]
EXPECTED_READINESS_GATE_KEYS = ["ready", "status", "missing", "evidence"]
EXPECTED_READINESS_EVIDENCE_KEYS_BY_GATE = {
    "hermes": [
        "schema_version",
        "config_path",
        "config_path_exists",
        "config_path_is_absolute",
        "mcp_config_registered",
        "mcp_server_name",
        "transport",
        "server_module",
        "server_command",
        "runtime_started",
        "network_call",
        "secret_values_returned",
    ],
    "telegram": [
        "schema_version",
        "telegram_configured",
        "bot_token_configured",
        "gateway_configured",
        "delivery_preview_available",
        "telegram_report_format_schema",
        "send_call",
        "network_call",
        "credential_storage_added",
        "secret_values_returned",
    ],
    "migration": [
        "readiness_packet_exists",
        "migration_go_approved",
        "migration_files_allowed",
    ],
    "repository": ["migration_go_approved", "repository_go_approved"],
    "binance_testnet_read_only": [
        "testnet",
        "force_testnet_execution",
        "live_trading_enabled",
        "manual_passphrase_confirmed",
        "credentials",
        "secret_values_returned",
    ],
    "live_order_submission": [
        "live_order_approved",
        "live_trading_enabled",
        "testnet",
        "force_testnet_execution",
        "manual_passphrase_confirmed",
        "trade_only_permission_attested",
        "emergency_kill_switch_enabled",
        "requires_confirmation",
        "order_submission",
        "network_call",
        "credentials",
        "secret_values_returned",
    ],
    "live_data": [
        "schema_version",
        "market_ohlcv_source_configured",
        "macro_source_configured",
        "news_source_configured",
        "live_adapter_added",
        "network_call",
        "secret_values_returned",
    ],
}
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


def clear_readiness_env(monkeypatch) -> None:
    for key in READINESS_ENV_KEYS:
        monkeypatch.delenv(key, raising=False)
    get_settings.cache_clear()


def test_integration_readiness_reports_blocked_defaults(monkeypatch) -> None:
    clear_readiness_env(monkeypatch)

    payload = get_integration_readiness(binance_credentials_path="/missing/credentials.json")

    assert payload["status"] == "blocked"
    assert payload["next_actions"] == [
        "hermes: provide hermes_config_path, hermes_mcp_config_registration",
        "telegram: provide telegram_bot_token_or_gateway",
        "migration: provide explicit_MIGRATION_GO",
        "repository: provide MIGRATION_GO, REPOSITORY_GO",
        (
            "binance_testnet_read_only: provide encrypted_binance_testnet_credentials, "
            "manual_credential_passphrase_at_smoke_time"
        ),
        (
            "live_order_submission: provide explicit_live_order_approval, "
            "HALO_SWING_BINANCE_ENABLE_LIVE_TRADING=true, encrypted_binance_credentials, "
            "manual_credential_passphrase_at_order_time, "
            "binance_console_trade_only_no_withdraw_attestation"
        ),
        (
            "live_data: provide market_ohlcv_source_or_api_key_decision, "
            "macro_source_or_api_key_decision, news_source_or_api_key_decision"
        ),
    ]
    assert payload["gates"]["hermes"]["missing"] == [
        "hermes_config_path",
        "hermes_mcp_config_registration",
    ]
    hermes_gate = payload["gates"]["hermes"]
    assert hermes_gate["evidence"]["schema_version"] == "hermes_mcp_config_readiness.v1"
    assert hermes_gate["evidence"]["mcp_server_name"] == "halo_swing_mcp"
    assert hermes_gate["evidence"]["transport"] == "stdio"
    assert hermes_gate["evidence"]["runtime_started"] is False
    assert hermes_gate["evidence"]["network_call"] is False
    assert payload["gates"]["telegram"]["missing"] == ["telegram_bot_token_or_gateway"]
    telegram_gate = payload["gates"]["telegram"]
    assert telegram_gate["evidence"]["schema_version"] == "telegram_delivery_readiness.v1"
    assert telegram_gate["evidence"]["delivery_preview_available"] is True
    assert telegram_gate["evidence"]["send_call"] is False
    assert telegram_gate["evidence"]["network_call"] is False
    assert telegram_gate["evidence"]["credential_storage_added"] is False
    assert payload["gates"]["migration"]["missing"] == ["explicit_MIGRATION_GO"]
    assert payload["gates"]["repository"]["missing"] == ["MIGRATION_GO", "REPOSITORY_GO"]
    assert "encrypted_binance_testnet_credentials" in payload["gates"]["binance_testnet_read_only"]["missing"]
    assert (
        "manual_credential_passphrase_at_smoke_time"
        in payload["gates"]["binance_testnet_read_only"]["missing"]
    )
    live_order_gate = payload["gates"]["live_order_submission"]
    assert "explicit_live_order_approval" in live_order_gate["missing"]
    assert "HALO_SWING_BINANCE_ENABLE_LIVE_TRADING=true" in live_order_gate["missing"]
    assert "encrypted_binance_credentials" in live_order_gate["missing"]
    assert "manual_credential_passphrase_at_order_time" in live_order_gate["missing"]
    assert "binance_console_trade_only_no_withdraw_attestation" in live_order_gate["missing"]
    assert live_order_gate["evidence"]["order_submission"] is False
    assert live_order_gate["evidence"]["network_call"] is False
    assert payload["gates"]["live_data"]["missing"] == [
        "market_ohlcv_source_or_api_key_decision",
        "macro_source_or_api_key_decision",
        "news_source_or_api_key_decision",
    ]
    assert payload["gates"]["live_data"]["evidence"]["schema_version"] == (
        "live_data_source_readiness.v1"
    )
    assert payload["gates"]["live_data"]["evidence"]["live_adapter_added"] is False
    assert payload["gates"]["live_data"]["evidence"]["network_call"] is False
    assert payload["live_data_required"] is False


def test_integration_readiness_payload_schema_is_stable(monkeypatch) -> None:
    clear_readiness_env(monkeypatch)

    payload = get_integration_readiness(binance_credentials_path="/missing/credentials.json")

    assert list(payload) == EXPECTED_READINESS_PAYLOAD_KEYS
    assert list(payload["gates"]) == EXPECTED_READINESS_GATE_NAMES
    for gate_name in EXPECTED_READINESS_GATE_NAMES:
        gate = payload["gates"][gate_name]
        assert list(gate) == EXPECTED_READINESS_GATE_KEYS
        assert list(gate["evidence"]) == EXPECTED_READINESS_EVIDENCE_KEYS_BY_GATE[
            gate_name
        ]

    for gate_name in ("binance_testnet_read_only", "live_order_submission"):
        credentials = payload["gates"][gate_name]["evidence"]["credentials"]
        assert list(credentials) == EXPECTED_MISSING_CREDENTIAL_STATUS_KEYS
        assert (
            list(credentials["credential_policy"])
            == EXPECTED_BINANCE_CREDENTIAL_POLICY_KEYS
        )
        assert credentials["secret_values_returned"] is False
        assert credentials["passphrase_persisted"] is False
        assert credentials["live_data_required"] is False


def test_integration_readiness_configured_credential_schema_is_stable(
    tmp_path: Path,
    monkeypatch,
) -> None:
    clear_readiness_env(monkeypatch)
    credentials_path = tmp_path / "credentials.enc.json"
    save_binance_credentials(
        api_key="abcde12345key",
        api_secret="super-secret",
        passphrase="local-passphrase",
        credentials_path=str(credentials_path),
    )

    payload = get_integration_readiness(binance_credentials_path=str(credentials_path))

    for gate_name in ("binance_testnet_read_only", "live_order_submission"):
        credentials = payload["gates"][gate_name]["evidence"]["credentials"]
        assert list(credentials) == EXPECTED_CONFIGURED_CREDENTIAL_STATUS_KEYS
        assert list(credentials["kdf"]) == EXPECTED_SAFE_CREDENTIAL_KDF_KEYS
        assert list(credentials["cipher"]) == EXPECTED_SAFE_CREDENTIAL_CIPHER_KEYS
        assert (
            list(credentials["credential_policy"])
            == EXPECTED_BINANCE_CREDENTIAL_POLICY_KEYS
        )
        assert credentials["configured"] is True
        assert credentials["api_key_hint"] == "abcde...5key"
        assert credentials["kdf"]["name"] == "PBKDF2HMAC-SHA256"
        assert credentials["cipher"]["name"] == "Fernet"
        assert credentials["secret_values_returned"] is False
        assert credentials["passphrase_persisted"] is False
        assert credentials["live_data_required"] is False

    serialized = json.dumps(payload)
    assert "super-secret" not in serialized
    assert "local-passphrase" not in serialized
    assert "salt_b64" not in serialized
    assert '"token":' not in serialized


def test_integration_readiness_uses_safe_local_evidence(tmp_path: Path, monkeypatch) -> None:
    hermes_config = tmp_path / "hermes.yaml"
    credentials_path = tmp_path / "credentials.enc.json"
    hermes_config.write_text("mcp_servers: {}\n", encoding="utf-8")
    save_binance_credentials(
        api_key="abcde12345key",
        api_secret="super-secret",
        passphrase="local-passphrase",
        credentials_path=str(credentials_path),
    )
    monkeypatch.setenv("FRED_API_KEY", "configured")
    monkeypatch.setenv("NEWS_API_KEY", "configured")
    monkeypatch.setenv("HALO_SWING_BINANCE_ENABLE_LIVE_TRADING", "true")
    get_settings.cache_clear()

    payload = get_integration_readiness(
        hermes_config_path=str(hermes_config),
        hermes_mcp_config_registered=True,
        telegram_gateway_configured=True,
        migration_go_approved=True,
        repository_go_approved=True,
        binance_credentials_path=str(credentials_path),
        binance_passphrase_confirmed=True,
        binance_trade_only_permission_attested=True,
        live_order_approved=True,
        btc_risk_settings_path=str(tmp_path / "risk_settings.json"),
        market_data_source_configured=True,
    )

    assert payload["status"] == "ready"
    assert payload["next_actions"] == []
    assert all(gate["ready"] for gate in payload["gates"].values())
    assert payload["gates"]["hermes"]["evidence"]["config_path_exists"] is True
    assert payload["gates"]["hermes"]["evidence"]["config_path_is_absolute"] is True
    assert payload["gates"]["hermes"]["evidence"]["mcp_config_registered"] is True
    assert payload["gates"]["telegram"]["evidence"]["gateway_configured"] is True
    assert payload["gates"]["telegram"]["evidence"]["send_call"] is False
    assert payload["gates"]["binance_testnet_read_only"]["evidence"]["credentials"]["configured"] is True
    assert payload["gates"]["binance_testnet_read_only"]["evidence"]["credentials"]["api_key_hint"] == "abcde...5key"
    assert payload["gates"]["live_order_submission"]["ready"] is True
    assert payload["gates"]["live_order_submission"]["evidence"]["order_submission"] is False
    assert (
        payload["gates"]["live_order_submission"]["evidence"]["credentials"]["credential_policy"][
            "withdraw_permission_allowed"
        ]
        is False
    )
    assert "api_secret" not in json.dumps(payload)
    assert "local-passphrase" not in json.dumps(payload)


def test_integration_readiness_normalizes_public_path_inputs(
    tmp_path: Path,
    monkeypatch,
) -> None:
    clear_readiness_env(monkeypatch)
    hermes_config = tmp_path / "hermes.yaml"
    credentials_path = tmp_path / "credentials.enc.json"
    risk_settings_path = tmp_path / "risk_settings.json"
    hermes_config.write_text("mcp_servers: {}\n", encoding="utf-8")
    save_binance_credentials(
        api_key="abcde12345key",
        api_secret="super-secret",
        passphrase="local-passphrase",
        credentials_path=str(credentials_path),
    )
    monkeypatch.setenv("HALO_SWING_BINANCE_ENABLE_LIVE_TRADING", "true")
    get_settings.cache_clear()

    payload = get_integration_readiness(
        hermes_config_path=f" {hermes_config} ",
        hermes_mcp_config_registered=True,
        telegram_configured=True,
        migration_go_approved=True,
        repository_go_approved=True,
        binance_credentials_path=f" {credentials_path} ",
        binance_passphrase_confirmed=True,
        binance_trade_only_permission_attested=True,
        live_order_approved=True,
        btc_risk_settings_path=f" {risk_settings_path} ",
        market_data_source_configured=True,
        macro_source_configured=True,
        news_source_configured=True,
    )

    assert payload["status"] == "ready"
    assert payload["next_actions"] == []
    assert payload["gates"]["hermes"]["evidence"]["config_path"] == str(hermes_config)
    assert payload["gates"]["telegram"]["evidence"]["telegram_configured"] is True
    assert (
        payload["gates"]["binance_testnet_read_only"]["evidence"]["credentials"][
            "credentials_path"
        ]
        == str(credentials_path)
    )
    assert (
        payload["gates"]["live_order_submission"]["evidence"]["credentials"][
            "configured"
        ]
        is True
    )


def test_integration_readiness_normalizes_env_hermes_config_path(
    tmp_path: Path,
    monkeypatch,
) -> None:
    clear_readiness_env(monkeypatch)
    hermes_config = tmp_path / "hermes.yaml"
    missing_credentials = tmp_path / "missing.enc.json"
    hermes_config.write_text("mcp_servers: {}\n", encoding="utf-8")
    monkeypatch.setenv("HALO_SWING_HERMES_CONFIG_PATH", f" {hermes_config} ")
    get_settings.cache_clear()

    payload = get_integration_readiness(
        hermes_mcp_config_registered=True,
        binance_credentials_path=str(missing_credentials),
    )
    hermes_gate = payload["gates"]["hermes"]

    assert hermes_gate["status"] == "ready"
    assert hermes_gate["missing"] == []
    assert hermes_gate["evidence"]["config_path"] == str(hermes_config)
    assert hermes_gate["evidence"]["config_path_exists"] is True
    assert hermes_gate["evidence"]["config_path_is_absolute"] is True


def test_integration_readiness_rejects_env_hermes_config_path_without_fallback(
    tmp_path: Path,
    monkeypatch,
) -> None:
    clear_readiness_env(monkeypatch)
    invalid_cases = [
        (
            "",
            "HALO_SWING_HERMES_CONFIG_PATH must be a nonempty string",
        ),
        (
            "   ",
            "HALO_SWING_HERMES_CONFIG_PATH must be a nonempty string",
        ),
        (
            f"{tmp_path / 'hermes'}\x7f.yaml",
            "HALO_SWING_HERMES_CONFIG_PATH must not contain control characters",
        ),
    ]

    for env_value, expected_error in invalid_cases:
        monkeypatch.setenv("HALO_SWING_HERMES_CONFIG_PATH", env_value)
        get_settings.cache_clear()

        with pytest.raises(ValueError, match=expected_error):
            get_integration_readiness(
                binance_credentials_path=f"{tmp_path / 'credentials.enc.json'}\n",
            )


def test_integration_readiness_rejects_invalid_public_inputs(tmp_path: Path) -> None:
    missing_credentials = tmp_path / "missing.enc.json"
    invalid_cases = [
        (
            {"hermes_mcp_config_registered": "false"},
            "hermes_mcp_config_registered must be a boolean",
        ),
        (
            {"telegram_configured": "false"},
            "telegram_configured must be a boolean when provided",
        ),
        (
            {"telegram_bot_token_configured": 1},
            "telegram_bot_token_configured must be a boolean when provided",
        ),
        (
            {"telegram_gateway_configured": []},
            "telegram_gateway_configured must be a boolean when provided",
        ),
        (
            {"migration_go_approved": "true"},
            "migration_go_approved must be a boolean",
        ),
        (
            {"repository_go_approved": 1},
            "repository_go_approved must be a boolean",
        ),
        (
            {"binance_passphrase_confirmed": "false"},
            "binance_passphrase_confirmed must be a boolean",
        ),
        (
            {"binance_trade_only_permission_attested": "true"},
            "binance_trade_only_permission_attested must be a boolean",
        ),
        (
            {"live_order_approved": "false"},
            "live_order_approved must be a boolean",
        ),
        (
            {"market_data_source_configured": "true"},
            "market_data_source_configured must be a boolean when provided",
        ),
        (
            {"macro_source_configured": 0},
            "macro_source_configured must be a boolean when provided",
        ),
        (
            {"news_source_configured": "false"},
            "news_source_configured must be a boolean when provided",
        ),
        (
            {"hermes_config_path": "   "},
            "hermes_config_path must be a nonempty string",
        ),
        (
            {"binance_credentials_path": 123},
            "binance_credentials_path must be a nonempty string",
        ),
        (
            {"btc_risk_settings_path": ""},
            "btc_risk_settings_path must be a nonempty string",
        ),
    ]

    for overrides, expected_error in invalid_cases:
        payload = {"binance_credentials_path": str(missing_credentials)}
        payload.update(overrides)
        with pytest.raises(ValueError, match=expected_error):
            get_integration_readiness(**payload)


def test_integration_readiness_rejects_path_control_character_inputs(
    tmp_path: Path,
) -> None:
    missing_credentials = tmp_path / "missing.enc.json"
    invalid_cases = [
        (
            {"hermes_config_path": f"{tmp_path / 'hermes.yaml'}\n"},
            "hermes_config_path must not contain control characters",
        ),
        (
            {"binance_credentials_path": f"{missing_credentials}\n"},
            "binance_credentials_path must not contain control characters",
        ),
        (
            {"btc_risk_settings_path": f"{tmp_path / 'risk_settings.json'}\n"},
            "btc_risk_settings_path must not contain control characters",
        ),
    ]

    for overrides, expected_error in invalid_cases:
        payload = {"binance_credentials_path": str(missing_credentials)}
        payload.update(overrides)
        with pytest.raises(ValueError, match=expected_error):
            get_integration_readiness(**payload)


def test_harness_rejects_invalid_readiness_input_with_failure_audit(
    tmp_path: Path,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    input_payload = {"migration_go_approved": "false"}
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "get_integration_readiness",
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
    assert "migration_go_approved must be a boolean" in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "get_integration_readiness"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "migration_go_approved must be a boolean" in event["details"]["error"]


def test_harness_rejects_readiness_path_control_character_with_failure_audit(
    tmp_path: Path,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    input_payload = {"binance_credentials_path": f"{tmp_path / 'credentials.enc.json'}\n"}
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "get_integration_readiness",
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
    assert "binance_credentials_path must not contain control characters" in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "get_integration_readiness"
    assert event["outcome"] == "failure"
    assert event["details"]["input"]["binance_credentials_path"] == "[REDACTED]"
    assert "output_summary" not in event["details"]
    assert "binance_credentials_path must not contain control characters" in event[
        "details"
    ]["error"]


def test_hermes_readiness_requires_config_path_and_registration(tmp_path: Path) -> None:
    hermes_config = tmp_path / "hermes.yaml"
    hermes_config.write_text("mcp_servers: {}\n", encoding="utf-8")

    payload = get_integration_readiness(hermes_config_path=str(hermes_config))
    hermes_gate = payload["gates"]["hermes"]

    assert payload["status"] == "blocked"
    assert hermes_gate["status"] == "blocked"
    assert hermes_gate["missing"] == ["hermes_mcp_config_registration"]
    assert hermes_gate["evidence"]["schema_version"] == "hermes_mcp_config_readiness.v1"
    assert hermes_gate["evidence"]["config_path_exists"] is True
    assert hermes_gate["evidence"]["config_path_is_absolute"] is True
    assert hermes_gate["evidence"]["mcp_config_registered"] is False
    assert hermes_gate["evidence"]["server_command"] == (
        "PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.server"
    )
    assert hermes_gate["evidence"]["runtime_started"] is False
    assert hermes_gate["evidence"]["network_call"] is False


def test_telegram_readiness_accepts_gateway_without_returning_secrets() -> None:
    payload = get_integration_readiness(
        telegram_gateway_configured=True,
        telegram_bot_token_configured=False,
    )
    telegram_gate = payload["gates"]["telegram"]

    assert payload["status"] == "blocked"
    assert telegram_gate["status"] == "ready"
    assert telegram_gate["missing"] == []
    assert telegram_gate["evidence"]["schema_version"] == "telegram_delivery_readiness.v1"
    assert telegram_gate["evidence"]["gateway_configured"] is True
    assert telegram_gate["evidence"]["bot_token_configured"] is False
    assert telegram_gate["evidence"]["delivery_preview_available"] is True
    assert telegram_gate["evidence"]["telegram_report_format_schema"] == (
        "telegram_report_format.v1"
    )
    assert telegram_gate["evidence"]["send_call"] is False
    assert telegram_gate["evidence"]["network_call"] is False
    assert telegram_gate["evidence"]["secret_values_returned"] is False


def test_live_data_readiness_requires_market_macro_and_news_sources() -> None:
    payload = get_integration_readiness(
        market_data_source_configured=True,
        macro_source_configured=False,
        news_source_configured=True,
    )
    live_data_gate = payload["gates"]["live_data"]

    assert payload["status"] == "blocked"
    assert live_data_gate["status"] == "blocked"
    assert live_data_gate["missing"] == ["macro_source_or_api_key_decision"]
    assert live_data_gate["evidence"]["schema_version"] == "live_data_source_readiness.v1"
    assert live_data_gate["evidence"]["market_ohlcv_source_configured"] is True
    assert live_data_gate["evidence"]["macro_source_configured"] is False
    assert live_data_gate["evidence"]["news_source_configured"] is True
    assert live_data_gate["evidence"]["live_adapter_added"] is False
    assert live_data_gate["evidence"]["network_call"] is False
    assert live_data_gate["evidence"]["secret_values_returned"] is False


def test_integration_readiness_env_secrets_are_boolean_only(
    monkeypatch,
) -> None:
    clear_readiness_env(monkeypatch)
    monkeypatch.setenv("HALO_SWING_TELEGRAM_BOT_TOKEN", "telegram-secret-token")
    monkeypatch.setenv("HALO_SWING_TELEGRAM_GATEWAY_URL", "https://gateway.example/secret")
    monkeypatch.setenv("HALO_SWING_MARKET_DATA_API_KEY", "market-secret-key")
    monkeypatch.setenv("FRED_API_KEY", "fred-secret-key")
    monkeypatch.setenv("NEWS_API_KEY", "news-secret-key")

    payload = get_integration_readiness(binance_credentials_path="/missing/credentials.json")
    telegram_gate = payload["gates"]["telegram"]
    live_data_gate = payload["gates"]["live_data"]
    serialized = json.dumps(payload, sort_keys=True)

    assert payload["status"] == "blocked"
    assert telegram_gate["status"] == "ready"
    assert telegram_gate["missing"] == []
    assert telegram_gate["evidence"]["bot_token_configured"] is True
    assert telegram_gate["evidence"]["gateway_configured"] is True
    assert telegram_gate["evidence"]["secret_values_returned"] is False
    assert live_data_gate["status"] == "ready"
    assert live_data_gate["missing"] == []
    assert live_data_gate["evidence"]["market_ohlcv_source_configured"] is True
    assert live_data_gate["evidence"]["macro_source_configured"] is True
    assert live_data_gate["evidence"]["news_source_configured"] is True
    assert live_data_gate["evidence"]["secret_values_returned"] is False
    assert "telegram: provide" not in payload["next_actions"]
    assert "live_data: provide" not in payload["next_actions"]
    assert "telegram-secret-token" not in serialized
    assert "gateway.example/secret" not in serialized
    assert "market-secret-key" not in serialized
    assert "fred-secret-key" not in serialized
    assert "news-secret-key" not in serialized
    assert "HALO_SWING_TELEGRAM_BOT_TOKEN" not in serialized
    assert "HALO_SWING_MARKET_DATA_API_KEY" not in serialized
    assert "FRED_API_KEY" not in serialized
    assert "NEWS_API_KEY" not in serialized


def test_integration_readiness_env_secret_aliases_are_boolean_only(
    monkeypatch,
) -> None:
    clear_readiness_env(monkeypatch)
    env_aliases = {
        "TELEGRAM_BOT_TOKEN": "telegram-alias-secret-token",
        "HALO_SWING_TELEGRAM_GATEWAY": "https://gateway.example/alias-secret",
        "POLYGON_API_KEY": "polygon-secret-key",
        "ALPACA_API_KEY": "alpaca-secret-key",
        "TIINGO_API_KEY": "tiingo-secret-key",
        "HALO_SWING_FRED_API_KEY": "fred-alias-secret-key",
        "HALO_SWING_NEWS_API_KEY": "news-alias-secret-key",
    }
    for key, value in env_aliases.items():
        monkeypatch.setenv(key, value)

    payload = get_integration_readiness(binance_credentials_path="/missing/credentials.json")
    telegram_gate = payload["gates"]["telegram"]
    live_data_gate = payload["gates"]["live_data"]
    serialized = json.dumps(payload, sort_keys=True)

    assert payload["status"] == "blocked"
    assert telegram_gate["status"] == "ready"
    assert telegram_gate["missing"] == []
    assert telegram_gate["evidence"]["bot_token_configured"] is True
    assert telegram_gate["evidence"]["gateway_configured"] is True
    assert telegram_gate["evidence"]["secret_values_returned"] is False
    assert live_data_gate["status"] == "ready"
    assert live_data_gate["missing"] == []
    assert live_data_gate["evidence"]["market_ohlcv_source_configured"] is True
    assert live_data_gate["evidence"]["macro_source_configured"] is True
    assert live_data_gate["evidence"]["news_source_configured"] is True
    assert live_data_gate["evidence"]["secret_values_returned"] is False
    assert "telegram: provide" not in payload["next_actions"]
    assert "live_data: provide" not in payload["next_actions"]
    for key, value in env_aliases.items():
        assert key not in serialized
        assert value not in serialized


def test_integration_readiness_live_data_source_env_values_are_boolean_only(
    monkeypatch,
) -> None:
    clear_readiness_env(monkeypatch)
    source_env = {
        "HALO_SWING_MARKET_DATA_SOURCE": "polygon-live-source",
        "HALO_SWING_MACRO_SOURCE": "fred-live-source",
        "HALO_SWING_NEWS_SOURCE": "newsapi-live-source",
    }
    for key, value in source_env.items():
        monkeypatch.setenv(key, value)

    payload = get_integration_readiness(binance_credentials_path="/missing/credentials.json")
    live_data_gate = payload["gates"]["live_data"]
    serialized = json.dumps(payload, sort_keys=True)

    assert payload["status"] == "blocked"
    assert live_data_gate["status"] == "ready"
    assert live_data_gate["missing"] == []
    assert live_data_gate["evidence"]["market_ohlcv_source_configured"] is True
    assert live_data_gate["evidence"]["macro_source_configured"] is True
    assert live_data_gate["evidence"]["news_source_configured"] is True
    assert live_data_gate["evidence"]["live_adapter_added"] is False
    assert live_data_gate["evidence"]["network_call"] is False
    assert live_data_gate["evidence"]["secret_values_returned"] is False
    assert "live_data: provide" not in payload["next_actions"]
    for key, value in source_env.items():
        assert key not in serialized
        assert value not in serialized


def test_binance_readiness_requires_passphrase_confirmation(tmp_path: Path) -> None:
    credentials_path = tmp_path / "credentials.enc.json"
    save_binance_credentials(
        api_key="abcde12345key",
        api_secret="super-secret",
        passphrase="local-passphrase",
        credentials_path=str(credentials_path),
    )
    get_settings.cache_clear()

    payload = get_integration_readiness(binance_credentials_path=str(credentials_path))
    binance_gate = payload["gates"]["binance_testnet_read_only"]

    assert payload["status"] == "blocked"
    assert binance_gate["status"] == "blocked"
    assert binance_gate["evidence"]["credentials"]["configured"] is True
    assert binance_gate["evidence"]["manual_passphrase_confirmed"] is False
    assert binance_gate["missing"] == ["manual_credential_passphrase_at_smoke_time"]
    assert "super-secret" not in json.dumps(payload)
    assert "local-passphrase" not in json.dumps(payload)


def test_live_order_submission_requires_explicit_approval(
    tmp_path: Path,
    monkeypatch,
) -> None:
    credentials_path = tmp_path / "credentials.enc.json"
    save_binance_credentials(
        api_key="abcde12345key",
        api_secret="super-secret",
        passphrase="local-passphrase",
        credentials_path=str(credentials_path),
    )
    monkeypatch.setenv("HALO_SWING_BINANCE_ENABLE_LIVE_TRADING", "true")
    get_settings.cache_clear()

    payload = get_integration_readiness(
        binance_credentials_path=str(credentials_path),
        binance_passphrase_confirmed=True,
        binance_trade_only_permission_attested=True,
        btc_risk_settings_path=str(tmp_path / "risk_settings.json"),
    )
    live_order_gate = payload["gates"]["live_order_submission"]

    assert payload["status"] == "blocked"
    assert live_order_gate["status"] == "blocked"
    assert live_order_gate["missing"] == ["explicit_live_order_approval"]
    assert live_order_gate["evidence"]["live_trading_enabled"] is True
    assert live_order_gate["evidence"]["trade_only_permission_attested"] is True
    assert live_order_gate["evidence"]["credentials"]["configured"] is True
    assert live_order_gate["evidence"]["order_submission"] is False
    assert live_order_gate["evidence"]["network_call"] is False
    assert "super-secret" not in json.dumps(payload)
    assert "local-passphrase" not in json.dumps(payload)


def test_harness_returns_integration_readiness(tmp_path: Path) -> None:
    audit_path = tmp_path / "audit.jsonl"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "get_integration_readiness",
            "--input-json",
            json.dumps({"binance_credentials_path": str(tmp_path / "missing.enc.json")}),
            "--audit-log-path",
            str(audit_path),
        ],
        check=True,
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    payload = json.loads(result.stdout)

    assert payload["status"] == "blocked"
    assert payload["gates"]["migration"]["status"] == "blocked"
    assert audit_path.exists()
