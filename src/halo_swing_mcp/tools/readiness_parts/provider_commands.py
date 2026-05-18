# ruff: noqa: F403,F405,F821
"""Provider Commands readiness implementation."""

from __future__ import annotations

from .context import *


__all__ = ('_guard_check_passed', '_setup_live_data_smoke_commands', '_live_data_api_key_provider_status', '_configured_env_keys', '_live_data_smoke_command')


def _guard_check_passed(guard: dict[str, Any] | None, check_name: str) -> bool | None:
    checks = _mapping_value(guard, "checks")
    if not isinstance(checks, list):
        return None
    for check in checks:
        if not isinstance(check, dict):
            continue
        if check.get("name") == check_name:
            return check.get("passed") is True
    return None


def _setup_live_data_smoke_commands() -> list[dict[str, Any]]:
    return [
        {
            "name": "get_market_snapshot_live_smoke",
            "provider": "polygon",
            "required_env_key_groups": [
                ["HALO_SWING_MARKET_DATA_API_KEY", "POLYGON_API_KEY"]
            ],
            "command": (
                "PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness "
                "get_market_snapshot --input-json '{\"symbols\":[\"QQQ\"]}' --no-audit"
            ),
            "expected_live_contract": "market_snapshot_contract",
            "expected_live_checks": ["live_data_boundary_declared"],
            "network_call_policy": "only_when_matching_api_key_selects_live_provider",
            "mutates_local_state": False,
            "hermes_runtime_started": False,
            "telegram_send_call": False,
            "order_submission": False,
            "secret_values_returned": False,
        },
        {
            "name": "get_macro_snapshot_live_smoke",
            "provider": "fred",
            "required_env_key_groups": [
                [
                    "HALO_SWING_MACRO_API_KEY",
                    "HALO_SWING_FRED_API_KEY",
                    "FRED_API_KEY",
                ]
            ],
            "command": (
                "PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness "
                "get_macro_snapshot --no-audit"
            ),
            "expected_live_contract": "macro_filter_contract",
            "expected_live_checks": [
                "live_data_boundary_declared",
                "network_call_declared",
            ],
            "network_call_policy": "only_when_matching_api_key_selects_live_provider",
            "mutates_local_state": False,
            "hermes_runtime_started": False,
            "telegram_send_call": False,
            "order_submission": False,
            "secret_values_returned": False,
        },
        {
            "name": "get_news_bundle_live_smoke",
            "provider": "newsapi",
            "required_env_key_groups": [
                ["NEWSAPI_KEY", "HALO_SWING_NEWS_API_KEY", "NEWS_API_KEY"]
            ],
            "command": (
                "PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness "
                "get_news_bundle --input-json '{\"topic\":\"macro\"}' --no-audit"
            ),
            "expected_live_contract": "news_source_policy_contract",
            "expected_live_checks": [
                "live_data_boundary_declared",
                "network_call_declared",
                "secret_values_not_returned",
            ],
            "network_call_policy": "only_when_matching_api_key_selects_live_provider",
            "mutates_local_state": False,
            "hermes_runtime_started": False,
            "telegram_send_call": False,
            "order_submission": False,
            "secret_values_returned": False,
        },
    ]


def _live_data_api_key_provider_status(
    *,
    provider_family: str,
    provider: str,
    preferred_env_key: str,
    accepted_env_keys: list[str],
    missing_name: str,
    smoke_command_name: str,
    optional_live_mode_env: str,
) -> dict[str, Any]:
    configured_env_keys = _configured_env_keys(accepted_env_keys)
    configured = bool(configured_env_keys)
    setup_status = "ready" if configured else "pending"
    return {
        "provider_family": provider_family,
        "provider": provider,
        "configured": configured,
        "configured_env_keys": configured_env_keys,
        "preferred_env_key": preferred_env_key,
        "accepted_env_keys": accepted_env_keys,
        "missing": [] if configured else [missing_name],
        "setup_status": setup_status,
        "next_setup_action": (
            "run_provider_smoke" if configured else "fill_preferred_env_key"
        ),
        "dotenv_target_path": ".env",
        "example": f"{preferred_env_key}=your_{provider}_key",
        "auto_selects_live_provider": configured,
        "live_mode_required": False,
        "optional_live_mode_env": optional_live_mode_env,
        "smoke_command": _live_data_smoke_command(smoke_command_name),
        "network_call": False,
        "mutates_local_state": False,
        "secret_values_returned": False,
    }


def _configured_env_keys(keys: list[str]) -> list[str]:
    return [
        key
        for key in keys
        if _is_env_value_configured(get_config_value(key))
    ]


def _live_data_smoke_command(name: str) -> dict[str, Any]:
    for command in _setup_live_data_smoke_commands():
        if command["name"] == name:
            return command
    raise ValueError(f"unknown live data smoke command: {name}")
