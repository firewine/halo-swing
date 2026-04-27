"""Deterministic health check tool."""

from typing import Any

from halo_swing_mcp import MCP_SERVER_NAME, PROJECT_NAME, __version__

CAPABILITIES = ["health_check"]


def health_check() -> dict[str, Any]:
    """Return stable server metadata for MCP and harness smoke tests."""

    return {
        "project": PROJECT_NAME,
        "version": __version__,
        "status": "ok",
        "mcp_server": MCP_SERVER_NAME,
        "capabilities": CAPABILITIES,
        "live_data_required": False,
    }
