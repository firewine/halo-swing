from pathlib import Path


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


def test_env_example_telegram_delivery_keys_are_blank_placeholders() -> None:
    assignments = _env_assignments()

    for key in TELEGRAM_DELIVERY_KEYS:
        assert key in assignments
        assert assignments[key] == ""


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
