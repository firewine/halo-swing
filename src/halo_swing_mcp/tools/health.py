"""Deterministic health check tool."""

from typing import Any

from halo_swing_mcp.tool_registry import call_tool


def health_check() -> dict[str, Any]:
    """Return stable server metadata for MCP and harness smoke tests."""

    return call_tool("health_check")
