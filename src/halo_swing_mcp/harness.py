"""Direct command harness for MCP tool implementations."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence

from halo_swing_mcp.audit import append_tool_audit_event
from halo_swing_mcp.tool_registry import call_tool, tool_names


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Halo Swing MCP tool harness")
    parser.add_argument("command", choices=tool_names())
    parser.add_argument(
        "--input-json",
        help="JSON object passed as keyword arguments to the selected command.",
    )
    parser.add_argument(
        "--input-file",
        help="Path to a JSON object passed as keyword arguments to the command.",
    )
    parser.add_argument(
        "--audit-log-path",
        help="Override the JSONL audit log path for this harness invocation.",
    )
    parser.add_argument(
        "--no-audit",
        action="store_true",
        help="Disable audit logging for this harness invocation.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.input_file and args.input_json is not None:
        error = ValueError("input-json and input-file are mutually exclusive")
        if not args.no_audit:
            append_tool_audit_event(
                command_name=args.command,
                input_payload={
                    "input_source": "input_conflict",
                    "input_file": args.input_file,
                    "input_json_provided": True,
                },
                result=None,
                outcome="failure",
                actor="harness",
                audit_log_path=args.audit_log_path,
                error=repr(error),
            )
        raise error

    try:
        if args.input_file:
            with open(args.input_file, encoding="utf-8") as handle:
                input_payload = json.load(handle)
        else:
            input_json = args.input_json if args.input_json is not None else "{}"
            input_payload = json.loads(input_json)
    except json.JSONDecodeError as exc:
        error = ValueError("input payload must be valid JSON")
        if not args.no_audit:
            input_payload = (
                {"input_source": "input_file", "input_file": args.input_file}
                if args.input_file
                else {"input_source": "input_json"}
            )
            append_tool_audit_event(
                command_name=args.command,
                input_payload=input_payload,
                result=None,
                outcome="failure",
                actor="harness",
                audit_log_path=args.audit_log_path,
                error=repr(error),
            )
        raise error from exc
    except (OSError, UnicodeDecodeError) as exc:
        error = ValueError("input file must be readable")
        if not args.no_audit:
            append_tool_audit_event(
                command_name=args.command,
                input_payload={
                    "input_source": "input_file",
                    "input_file": args.input_file,
                },
                result=None,
                outcome="failure",
                actor="harness",
                audit_log_path=args.audit_log_path,
                error=repr(error),
            )
        raise error from exc

    if not isinstance(input_payload, dict):
        error = ValueError("input payload must be a JSON object")
        if not args.no_audit:
            append_tool_audit_event(
                command_name=args.command,
                input_payload=input_payload,
                result=None,
                outcome="failure",
                actor="harness",
                audit_log_path=args.audit_log_path,
                error=repr(error),
            )
        raise error

    try:
        payload = call_tool(args.command, input_payload)
    except Exception as exc:
        if not args.no_audit:
            append_tool_audit_event(
                command_name=args.command,
                input_payload=input_payload,
                result=None,
                outcome="failure",
                actor="harness",
                audit_log_path=args.audit_log_path,
                error=repr(exc),
            )
        raise

    if not args.no_audit:
        append_tool_audit_event(
            command_name=args.command,
            input_payload=input_payload,
            result=payload,
            outcome="success",
            actor="harness",
            audit_log_path=args.audit_log_path,
        )

    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
