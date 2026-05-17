"""Shared imports and constants for readiness implementation modules."""

from __future__ import annotations

import tempfile
from collections.abc import Callable
from pathlib import Path
from typing import Any

from halo_swing_mcp import MCP_SERVER_NAME
import halo_swing_mcp.env as local_env
from halo_swing_mcp.binance_btc import LIVE_CONFIRMATION
from halo_swing_mcp.config import (
    LIVE_HTTP_TIMEOUT_SECONDS_ENV_NAME,
    get_settings,
)
from halo_swing_mcp.env import get_config_value
from halo_swing_mcp.providers import describe_market_data_provider_route
from halo_swing_mcp.risk_settings import load_btc_risk_settings, resolve_settings_path
from halo_swing_mcp.secret_store import get_binance_credentials_status

HERMES_SERVER_COMMAND = "PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.server"
HERMES_CONFIG_PATH_ENV = "HALO_SWING_HERMES_CONFIG_PATH"
HERMES_MCP_CONFIG_REGISTERED_ENV = "HALO_SWING_HERMES_MCP_CONFIG_REGISTERED"
BINANCE_PASSPHRASE_CONFIRMED_ENV = "HALO_SWING_BINANCE_PASSPHRASE_CONFIRMED"
BINANCE_TRADE_ONLY_PERMISSION_ATTESTED_ENV = (
    "HALO_SWING_BINANCE_TRADE_ONLY_PERMISSION_ATTESTED"
)
BINANCE_LIVE_ORDER_APPROVED_ENV = "HALO_SWING_BINANCE_LIVE_ORDER_APPROVED"

__all__ = (
    "Any",
    "Callable",
    "Path",
    "tempfile",
    "MCP_SERVER_NAME",
    "local_env",
    "LIVE_CONFIRMATION",
    "LIVE_HTTP_TIMEOUT_SECONDS_ENV_NAME",
    "get_settings",
    "get_config_value",
    "describe_market_data_provider_route",
    "load_btc_risk_settings",
    "resolve_settings_path",
    "get_binance_credentials_status",
    "HERMES_SERVER_COMMAND",
    "HERMES_CONFIG_PATH_ENV",
    "HERMES_MCP_CONFIG_REGISTERED_ENV",
    "BINANCE_PASSPHRASE_CONFIRMED_ENV",
    "BINANCE_TRADE_ONLY_PERMISSION_ATTESTED_ENV",
    "BINANCE_LIVE_ORDER_APPROVED_ENV",
)
