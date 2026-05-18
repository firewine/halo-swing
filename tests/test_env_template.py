from pathlib import Path

from halo_swing_mcp.providers import (
    MACRO_API_KEY_ENV_KEYS,
    MARKET_API_KEY_ENV_KEYS,
    NEWS_API_KEY_ENV_KEYS,
)
from halo_swing_mcp.tools.readiness import get_live_data_api_key_status


ROOT = Path(__file__).resolve().parents[1]
ENV_TEMPLATE = ROOT / ".env.example"

LIVE_DATA_KEY_NAMES = {
    "HALO_SWING_MARKET_DATA_API_KEY",
    "POLYGON_API_KEY",
    "HALO_SWING_MACRO_API_KEY",
    "HALO_SWING_FRED_API_KEY",
    "FRED_API_KEY",
    "HALO_SWING_NEWS_API_KEY",
    "NEWS_API_KEY",
    "NEWSAPI_KEY",
}
OPTIONAL_LIVE_MODE_LINES = {
    "# HALO_SWING_MARKET_DATA_MODE=live",
    "# HALO_SWING_MACRO_DATA_MODE=live",
    "# HALO_SWING_NEWS_DATA_MODE=live",
}
TELEGRAM_DELIVERY_KEYS = {
    "HALO_SWING_TELEGRAM_BOT_TOKEN",
    "TELEGRAM_BOT_TOKEN",
    "HALO_SWING_TELEGRAM_GATEWAY",
    "HALO_SWING_TELEGRAM_GATEWAY_URL",
}
HERMES_READINESS_KEYS = {
    "HALO_SWING_HERMES_CONFIG_PATH",
    "HALO_SWING_HERMES_MCP_CONFIG_REGISTERED",
}
BINANCE_READINESS_KEYS = {
    "HALO_SWING_BINANCE_LIVE_ORDER_APPROVED",
    "HALO_SWING_BINANCE_PASSPHRASE_CONFIRMED",
    "HALO_SWING_BINANCE_TRADE_ONLY_PERMISSION_ATTESTED",
}
DOTENV_ISOLATION_KEY = "HALO_SWING_DISABLE_DOTENV"


def _env_template_lines() -> list[str]:
    return ENV_TEMPLATE.read_text(encoding="utf-8").splitlines()


def _env_assignments() -> dict[str, str]:
    assignments: dict[str, str] = {}
    for line in _env_template_lines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        assignments[key] = value
    return assignments


def test_env_example_live_data_api_keys_are_blank_placeholders() -> None:
    assignments = _env_assignments()

    for key in LIVE_DATA_KEY_NAMES:
        assert key in assignments
        assert assignments[key] == ""


def test_env_example_live_data_keys_match_readiness_dotenv_template() -> None:
    assignments = _env_assignments()
    payload = get_live_data_api_key_status()
    entries = payload["dotenv_template"]["entries"]
    template_keys = {
        key
        for entry in entries
        for key in [entry["preferred_env_key"], *entry["accepted_env_keys"]]
    }

    assert template_keys == LIVE_DATA_KEY_NAMES
    for key in template_keys:
        assert key in assignments
        assert assignments[key] == ""


def test_readiness_live_data_keys_match_provider_auto_select_keys() -> None:
    payload = get_live_data_api_key_status()
    template_by_family = {
        entry["provider_family"]: entry for entry in payload["dotenv_template"]["entries"]
    }

    assert template_by_family["market"]["accepted_env_keys"] == list(
        MARKET_API_KEY_ENV_KEYS
    )
    assert template_by_family["macro"]["accepted_env_keys"] == list(
        MACRO_API_KEY_ENV_KEYS
    )
    assert template_by_family["news"]["accepted_env_keys"] == list(
        NEWS_API_KEY_ENV_KEYS
    )


def test_readiness_dotenv_template_examples_are_copy_paste_key_value_lines() -> None:
    payload = get_live_data_api_key_status()
    examples = [
        entry["example"] for entry in payload["dotenv_template"]["entries"]
    ]

    assert examples == [
        "POLYGON_API_KEY=your_polygon_key",
        "FRED_API_KEY=your_fred_key",
        "NEWS_API_KEY=your_newsapi_key",
    ]
    assert all(" = " not in example for example in examples)


def test_env_example_telegram_delivery_keys_are_blank_placeholders() -> None:
    assignments = _env_assignments()

    for key in TELEGRAM_DELIVERY_KEYS:
        assert key in assignments
        assert assignments[key] == ""


def test_env_example_hermes_readiness_keys_are_blank_placeholders() -> None:
    assignments = _env_assignments()

    for key in HERMES_READINESS_KEYS:
        assert key in assignments
        assert assignments[key] == ""


def test_env_example_binance_readiness_keys_are_blank_placeholders() -> None:
    assignments = _env_assignments()

    for key in BINANCE_READINESS_KEYS:
        assert key in assignments
        assert assignments[key] == ""


def test_env_example_dotenv_isolation_key_is_blank_placeholder() -> None:
    assignments = _env_assignments()

    assert assignments[DOTENV_ISOLATION_KEY] == ""


def test_env_example_live_modes_are_optional_comments() -> None:
    lines = set(_env_template_lines())
    assignments = _env_assignments()

    assert OPTIONAL_LIVE_MODE_LINES.issubset(lines)
    assert "HALO_SWING_MARKET_DATA_MODE" not in assignments
    assert "HALO_SWING_MACRO_DATA_MODE" not in assignments
    assert "HALO_SWING_NEWS_DATA_MODE" not in assignments


def test_env_example_does_not_include_secret_placeholder_values() -> None:
    assignments = _env_assignments()
    sensitive_fragments = ("secret", "token", "passphrase", "password", "<", ">")

    for key, value in assignments.items():
        if key in LIVE_DATA_KEY_NAMES or key.endswith(("_TOKEN", "_API_KEY")):
            assert value == ""
        normalized = value.lower()
        for fragment in sensitive_fragments:
            assert fragment not in normalized


def test_env_example_database_url_stays_blank_until_storage_gates() -> None:
    assignments = _env_assignments()

    assert assignments["HALO_SWING_DATABASE_URL"] == ""
    assert "data/halo_swing" not in ENV_TEMPLATE.read_text(encoding="utf-8")
