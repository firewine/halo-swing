import ast
import inspect
import json
import subprocess
import sys
from pathlib import Path

import pytest

from halo_swing_mcp.audit import read_audit_events
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


def test_registry_rejects_unexpected_payload_keys_before_dispatch() -> None:
    with pytest.raises(ValueError) as exc_info:
        call_tool(
            "evaluate_score_performance",
            {"signals": [], "extra": True},
        )

    error = str(exc_info.value)
    assert error == "evaluate_score_performance got unexpected input field: extra"
    assert "evaluate_recorded_score_performance" not in error
    assert "unexpected keyword argument" not in error


def test_registry_rejects_missing_required_payload_keys_before_dispatch() -> None:
    with pytest.raises(ValueError) as exc_info:
        call_tool("create_document_evidence_card", {"summary": "Plain PDF summary."})

    error = str(exc_info.value)
    assert error == "create_document_evidence_card missing required input field: artifact_ref"
    assert "create_document_evidence_card()" not in error
    assert "missing 1 required positional argument" not in error


def test_registry_rejects_multiple_missing_required_payload_keys_in_signature_order() -> None:
    with pytest.raises(ValueError) as exc_info:
        call_tool("save_binance_credentials", {})

    assert (
        str(exc_info.value)
        == "save_binance_credentials missing required input fields: "
        "api_key, api_secret, passphrase"
    )


def test_registry_rejects_non_object_payloads_before_dispatch() -> None:
    with pytest.raises(ValueError) as exc_info:
        call_tool("score_leverage_swing", ["bad"])  # type: ignore[arg-type]

    assert str(exc_info.value) == "score_leverage_swing input payload must be an object"


def test_registry_keeps_var_keyword_tools_permissive() -> None:
    assert call_tool("health_check", {"ignored": True}) == health_check()


def test_harness_rejects_unexpected_payload_key_with_failure_audit(
    tmp_path: Path,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    input_payload = {"signals": [], "extra": True}
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "evaluate_score_performance",
            "--input-json",
            json.dumps(input_payload),
            "--audit-log-path",
            str(audit_path),
        ],
        check=False,
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    events = read_audit_events(audit_log_path=str(audit_path))
    event = events[0]
    expected_error = "evaluate_score_performance got unexpected input field: extra"

    assert result.returncode != 0
    assert result.stdout == ""
    assert expected_error in result.stderr
    assert "evaluate_recorded_score_performance" not in result.stderr
    assert "unexpected keyword argument" not in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "evaluate_score_performance"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert expected_error in event["details"]["error"]


def test_harness_rejects_missing_required_payload_key_with_failure_audit(
    tmp_path: Path,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    input_payload = {"summary": "Plain PDF summary."}
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "create_document_evidence_card",
            "--input-json",
            json.dumps(input_payload),
            "--audit-log-path",
            str(audit_path),
        ],
        check=False,
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    events = read_audit_events(audit_log_path=str(audit_path))
    event = events[0]
    expected_error = (
        "create_document_evidence_card missing required input field: artifact_ref"
    )

    assert result.returncode != 0
    assert result.stdout == ""
    assert expected_error in result.stderr
    assert "missing 1 required positional argument" not in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "create_document_evidence_card"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert expected_error in event["details"]["error"]


def test_harness_rejects_non_object_input_json_with_failure_audit(
    tmp_path: Path,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    input_payload = ["bad"]
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "score_leverage_swing",
            "--input-json",
            json.dumps(input_payload),
            "--audit-log-path",
            str(audit_path),
        ],
        check=False,
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    events = read_audit_events(audit_log_path=str(audit_path))
    event = events[0]
    expected_error = "input payload must be a JSON object"

    assert result.returncode != 0
    assert result.stdout == ""
    assert expected_error in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "score_leverage_swing"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert expected_error in event["details"]["error"]


def test_harness_rejects_non_object_input_file_with_failure_audit(
    tmp_path: Path,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    input_file = tmp_path / "input.json"
    input_payload = ["bad"]
    input_file.write_text(json.dumps(input_payload), encoding="utf-8")
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "score_leverage_swing",
            "--input-file",
            str(input_file),
            "--audit-log-path",
            str(audit_path),
        ],
        check=False,
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    events = read_audit_events(audit_log_path=str(audit_path))
    event = events[0]
    expected_error = "input payload must be a JSON object"

    assert result.returncode != 0
    assert result.stdout == ""
    assert expected_error in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "score_leverage_swing"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert expected_error in event["details"]["error"]


def test_harness_rejects_invalid_input_json_with_failure_audit(
    tmp_path: Path,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    malformed_input = '{"asset":'
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "score_leverage_swing",
            "--input-json",
            malformed_input,
            "--audit-log-path",
            str(audit_path),
        ],
        check=False,
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    events = read_audit_events(audit_log_path=str(audit_path))
    event = events[0]
    expected_error = "input payload must be valid JSON"

    assert result.returncode != 0
    assert result.stdout == ""
    assert expected_error in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "score_leverage_swing"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == {"input_source": "input_json"}
    assert malformed_input not in json.dumps(event["details"])
    assert "output_summary" not in event["details"]
    assert expected_error in event["details"]["error"]


def test_harness_rejects_invalid_input_file_json_with_failure_audit(
    tmp_path: Path,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    input_file = tmp_path / "input.json"
    malformed_input = '{"asset":'
    input_file.write_text(malformed_input, encoding="utf-8")
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "score_leverage_swing",
            "--input-file",
            str(input_file),
            "--audit-log-path",
            str(audit_path),
        ],
        check=False,
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    events = read_audit_events(audit_log_path=str(audit_path))
    event = events[0]
    expected_error = "input payload must be valid JSON"

    assert result.returncode != 0
    assert result.stdout == ""
    assert expected_error in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "score_leverage_swing"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == {
        "input_source": "input_file",
        "input_file": str(input_file),
    }
    assert malformed_input not in json.dumps(event["details"])
    assert "output_summary" not in event["details"]
    assert expected_error in event["details"]["error"]


def test_harness_rejects_unreadable_input_file_with_failure_audit(
    tmp_path: Path,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    input_file = tmp_path / "missing.json"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "score_leverage_swing",
            "--input-file",
            str(input_file),
            "--audit-log-path",
            str(audit_path),
        ],
        check=False,
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    events = read_audit_events(audit_log_path=str(audit_path))
    event = events[0]
    expected_error = "input file must be readable"

    assert result.returncode != 0
    assert result.stdout == ""
    assert expected_error in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "score_leverage_swing"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == {
        "input_source": "input_file",
        "input_file": str(input_file),
    }
    assert "output_summary" not in event["details"]
    assert expected_error in event["details"]["error"]


def test_harness_rejects_invalid_utf8_input_file_with_failure_audit(
    tmp_path: Path,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    input_file = tmp_path / "input.json"
    input_file.write_bytes(b"\xff")
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "score_leverage_swing",
            "--input-file",
            str(input_file),
            "--audit-log-path",
            str(audit_path),
        ],
        check=False,
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    events = read_audit_events(audit_log_path=str(audit_path))
    event = events[0]
    expected_error = "input file must be readable"

    assert result.returncode != 0
    assert result.stdout == ""
    assert expected_error in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "score_leverage_swing"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == {
        "input_source": "input_file",
        "input_file": str(input_file),
    }
    assert "output_summary" not in event["details"]
    assert expected_error in event["details"]["error"]


def test_harness_rejects_input_source_conflict_with_failure_audit(
    tmp_path: Path,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    input_file = tmp_path / "missing.json"
    input_json = {"api_key": "secret-value"}
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "score_leverage_swing",
            "--input-file",
            str(input_file),
            "--input-json",
            json.dumps(input_json),
            "--audit-log-path",
            str(audit_path),
        ],
        check=False,
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    events = read_audit_events(audit_log_path=str(audit_path))
    event = events[0]
    expected_error = "input-json and input-file are mutually exclusive"
    event_details = json.dumps(event["details"])

    assert result.returncode != 0
    assert result.stdout == ""
    assert expected_error in result.stderr
    assert "input file must be readable" not in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "score_leverage_swing"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == {
        "input_source": "input_conflict",
        "input_file": str(input_file),
        "input_json_provided": True,
    }
    assert "secret-value" not in event_details
    assert "output_summary" not in event["details"]
    assert expected_error in event["details"]["error"]


def test_harness_rejects_blank_input_file_with_failure_audit(
    tmp_path: Path,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "score_leverage_swing",
            "--input-file",
            "   ",
            "--audit-log-path",
            str(audit_path),
        ],
        check=False,
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    events = read_audit_events(audit_log_path=str(audit_path))
    event = events[0]
    expected_error = "input-file must be a nonempty string"

    assert result.returncode != 0
    assert result.stdout == ""
    assert expected_error in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "score_leverage_swing"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == {
        "input_source": "input_file",
        "input_file_provided": True,
    }
    assert "output_summary" not in event["details"]
    assert expected_error in event["details"]["error"]


def test_harness_rejects_input_file_control_character_with_failure_audit(
    tmp_path: Path,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    input_file = f"{tmp_path / 'bad'}\nfile.json"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "score_leverage_swing",
            "--input-file",
            input_file,
            "--audit-log-path",
            str(audit_path),
        ],
        check=False,
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    events = read_audit_events(audit_log_path=str(audit_path))
    event = events[0]
    expected_error = "input-file must not contain control characters"
    event_details = json.dumps(event["details"])

    assert result.returncode != 0
    assert result.stdout == ""
    assert expected_error in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "score_leverage_swing"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == {
        "input_source": "input_file",
        "input_file_provided": True,
    }
    assert "bad" not in event_details
    assert "\\n" not in event_details
    assert "output_summary" not in event["details"]
    assert expected_error in event["details"]["error"]


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
