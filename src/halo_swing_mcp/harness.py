"""Direct command harness for MCP tool implementations."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from typing import Any, Callable

from halo_swing_mcp.audit import append_tool_audit_event
from halo_swing_mcp.tools.audit_tools import get_audit_log, get_audit_summary
from halo_swing_mcp.tools.health import health_check
from halo_swing_mcp.tools.market import (
    calculate_indicators,
    get_event_calendar,
    get_macro_snapshot,
    get_market_snapshot,
    get_news_bundle,
    render_chart,
)
from halo_swing_mcp.tools.recording import (
    evaluate_recorded_score_performance,
    label_signal_outcome,
    record_signal,
)
from halo_swing_mcp.tools.scoring import (
    compare_champion_challenger,
    evaluate_position,
    generate_trade_guide,
    score_leverage_swing,
    suggest_weight_update,
)

Command = Callable[[dict[str, Any]], dict[str, Any]]


def _with_kwargs(function: Callable[..., dict[str, Any]]) -> Command:
    return lambda payload: function(**payload)


COMMANDS: dict[str, Command] = {
    "health_check": lambda _payload: health_check(),
    "get_audit_log": _with_kwargs(get_audit_log),
    "get_audit_summary": _with_kwargs(get_audit_summary),
    "get_market_snapshot": _with_kwargs(get_market_snapshot),
    "get_macro_snapshot": _with_kwargs(get_macro_snapshot),
    "get_event_calendar": _with_kwargs(get_event_calendar),
    "get_news_bundle": _with_kwargs(get_news_bundle),
    "calculate_indicators": _with_kwargs(calculate_indicators),
    "render_chart": _with_kwargs(render_chart),
    "score_leverage_swing": _with_kwargs(score_leverage_swing),
    "generate_trade_guide": _with_kwargs(generate_trade_guide),
    "evaluate_position": _with_kwargs(evaluate_position),
    "record_signal": _with_kwargs(record_signal),
    "label_signal_outcome": _with_kwargs(label_signal_outcome),
    "evaluate_score_performance": _with_kwargs(evaluate_recorded_score_performance),
    "suggest_weight_update": lambda _payload: suggest_weight_update(),
    "compare_champion_challenger": lambda _payload: compare_champion_challenger(),
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Halo Swing MCP tool harness")
    parser.add_argument("command", choices=sorted(COMMANDS))
    parser.add_argument(
        "--input-json",
        default="{}",
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

    if args.input_file:
        with open(args.input_file, encoding="utf-8") as handle:
            input_payload = json.load(handle)
    else:
        input_payload = json.loads(args.input_json)

    if not isinstance(input_payload, dict):
        parser.error("input payload must be a JSON object")

    try:
        payload = COMMANDS[args.command](input_payload)
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
