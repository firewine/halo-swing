import ast
import inspect
import json
from pathlib import Path

from halo_swing_mcp import server
from halo_swing_mcp.harness import build_parser
from halo_swing_mcp.tool_registry import TOOL_REGISTRY, TOOL_SPECS, call_tool, tool_names
from halo_swing_mcp.tools.health import health_check


ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = ROOT / "src" / "halo_swing_mcp"
SERVER_PATH = SRC_ROOT / "server.py"
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


def _is_mcp_tool_decorator(decorator: ast.expr) -> bool:
    return (
        isinstance(decorator, ast.Call)
        and isinstance(decorator.func, ast.Attribute)
        and decorator.func.attr == "tool"
        and isinstance(decorator.func.value, ast.Name)
        and decorator.func.value.id == "mcp"
    )


def _mcp_tool_functions() -> dict[str, ast.FunctionDef | ast.AsyncFunctionDef]:
    tree = ast.parse(SERVER_PATH.read_text(encoding="utf-8"))
    return {
        node.name: node
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and any(_is_mcp_tool_decorator(decorator) for decorator in node.decorator_list)
    }


def _registry_dispatch_names(
    node: ast.FunctionDef | ast.AsyncFunctionDef,
) -> set[str]:
    dispatch_helpers = {"_audited_tool_call", "_call_registered_tool", "call_tool"}
    names: set[str] = set()

    for child in ast.walk(node):
        if (
            isinstance(child, ast.Call)
            and isinstance(child.func, ast.Name)
            and child.func.id in dispatch_helpers
            and child.args
            and isinstance(child.args[0], ast.Constant)
            and isinstance(child.args[0].value, str)
        ):
            names.add(child.args[0].value)

    return names


def _wrapper_parameter_names(node: ast.FunctionDef | ast.AsyncFunctionDef) -> set[str]:
    return {
        arg.arg
        for arg in [*node.args.posonlyargs, *node.args.args, *node.args.kwonlyargs]
    }


def _literal_payload_bindings(
    node: ast.FunctionDef | ast.AsyncFunctionDef,
) -> dict[str, set[str]]:
    bindings: dict[str, set[str]] = {}

    for child in ast.walk(node):
        if not isinstance(child, ast.Dict):
            continue
        for key, value in zip(child.keys, child.values, strict=True):
            if not (
                isinstance(key, ast.Constant)
                and isinstance(key.value, str)
                and isinstance(value, ast.Name)
            ):
                continue
            bindings.setdefault(key.value, set()).add(value.id)

    return bindings


def _callable_parameter_names(function: object) -> set[str]:
    accepted_kinds = {
        inspect.Parameter.POSITIONAL_ONLY,
        inspect.Parameter.POSITIONAL_OR_KEYWORD,
        inspect.Parameter.KEYWORD_ONLY,
    }
    return {
        name
        for name, parameter in inspect.signature(function).parameters.items()
        if parameter.kind in accepted_kinds
    }


def test_tool_registry_matches_mvp_contract_and_health_capabilities() -> None:
    names = tool_names()

    assert names == health_check()["capabilities"]
    assert MVP_CONTRACT["required_tools"] == names
    assert set(TOOL_REGISTRY) == set(names)


def test_tool_specs_are_unique_ordered_and_complete() -> None:
    spec_names = [spec.name for spec in TOOL_SPECS]

    assert len(spec_names) == len(set(spec_names))
    assert spec_names == tool_names()
    assert list(TOOL_REGISTRY) == spec_names
    for spec in TOOL_SPECS:
        assert TOOL_REGISTRY[spec.name] is spec
        assert callable(spec.function)
        assert spec.description.strip()
        assert isinstance(spec.audit_enabled, bool)
        assert isinstance(spec.live_data_required, bool)


def test_harness_command_choices_are_registry_backed() -> None:
    parser = build_parser()
    command_action = next(action for action in parser._actions if action.dest == "command")

    assert command_action.choices == tool_names()


def test_server_mcp_tool_wrappers_match_registered_tools() -> None:
    wrapper_names = set(_mcp_tool_functions())

    assert wrapper_names == set(tool_names())
    for name in wrapper_names:
        wrapper = getattr(server, name, None)
        assert callable(wrapper), name


def test_server_mcp_tool_wrappers_dispatch_to_matching_registry_tool() -> None:
    for name, wrapper_node in _mcp_tool_functions().items():
        assert _registry_dispatch_names(wrapper_node) == {name}


def test_server_mcp_tool_wrapper_payload_keys_match_parameters() -> None:
    for name, wrapper_node in _mcp_tool_functions().items():
        parameter_names = _wrapper_parameter_names(wrapper_node)
        payload_bindings = _literal_payload_bindings(wrapper_node)

        assert set(payload_bindings) == parameter_names, name
        assert all(bound_names == {key} for key, bound_names in payload_bindings.items())


def test_server_mcp_tool_wrapper_parameters_match_registered_functions() -> None:
    for name, wrapper_node in _mcp_tool_functions().items():
        assert _wrapper_parameter_names(wrapper_node) == _callable_parameter_names(
            TOOL_REGISTRY[name].function
        ), name


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
