import ast
import json
from pathlib import Path

from halo_swing_mcp import server
from halo_swing_mcp.harness import build_parser
from halo_swing_mcp.tool_registry import TOOL_REGISTRY, call_tool, tool_names
from halo_swing_mcp.tools.health import health_check


ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = ROOT / "src" / "halo_swing_mcp"
MVP_CONTRACT = json.loads(
    (ROOT / "tests" / "golden" / "mvp_tool_contracts.json").read_text(
        encoding="utf-8"
    )
)

FORBIDDEN_DEFAULT_IMPORTS = {
    "httpx",
    "requests",
    "sqlite3",
    "sqlalchemy",
    "ccxt",
}


def test_tool_registry_matches_mvp_contract_and_health_capabilities() -> None:
    names = tool_names()

    assert names == health_check()["capabilities"]
    assert set(MVP_CONTRACT["required_tools"]).issubset(set(names))
    assert set(TOOL_REGISTRY) == set(names)


def test_harness_command_choices_are_registry_backed() -> None:
    parser = build_parser()
    command_action = next(action for action in parser._actions if action.dest == "command")

    assert command_action.choices == tool_names()


def test_server_preserves_public_tool_wrappers_for_registered_tools() -> None:
    for name in tool_names():
        wrapper = getattr(server, name, None)
        assert callable(wrapper), name


def test_registry_calls_registered_payloads() -> None:
    assert call_tool("health_check") == health_check()
    assert call_tool("get_market_snapshot", {"symbols": ["QQQ"]})["snapshots"]


def test_default_source_does_not_import_live_db_or_broker_clients() -> None:
    imported_modules: set[str] = set()

    for path in SRC_ROOT.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported_modules.update(
                    alias.name.split(".", maxsplit=1)[0] for alias in node.names
                )
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported_modules.add(node.module.split(".", maxsplit=1)[0])

    assert imported_modules.isdisjoint(FORBIDDEN_DEFAULT_IMPORTS)
