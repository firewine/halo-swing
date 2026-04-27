"""Halo Swing MCP server entrypoint."""

from typing import Any

from mcp.server.fastmcp import FastMCP

from halo_swing_mcp import MCP_SERVER_NAME
from halo_swing_mcp.tools.health import health_check as health_check_payload

mcp = FastMCP(MCP_SERVER_NAME)


@mcp.tool()
def health_check() -> dict[str, Any]:
    """Return deterministic server health and P0 capability metadata."""

    return health_check_payload()


def main() -> None:
    mcp.run("stdio")


if __name__ == "__main__":
    main()
