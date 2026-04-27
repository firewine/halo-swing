"""Direct command harness for MCP tool implementations."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from typing import Any, Callable

from halo_swing_mcp.tools.health import health_check

Command = Callable[[], dict[str, Any]]

COMMANDS: dict[str, Command] = {
    "health_check": health_check,
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Halo Swing MCP tool harness")
    parser.add_argument("command", choices=sorted(COMMANDS))
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    payload = COMMANDS[args.command]()
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
