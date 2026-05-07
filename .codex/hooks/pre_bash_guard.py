#!/usr/bin/env python3
import json
import re
import sys


DENY_PATTERNS = [
    (
        r"\bgit\s+add\s+(\.|-A)(\s|$)",
        "Use explicit file paths instead of git add . or git add -A.",
    ),
    (r"\bgit\s+push\s+--force\b", "Force push is blocked."),
    (r"\brm\s+-rf\b", "rm -rf is blocked."),
    (
        r"\b(curl|wget)\b.*\|\s*(sh|bash)\b",
        "Piping remote scripts into shell is blocked.",
    ),
    (
        r"\bpython\s+-m\s+pip\s+install\b",
        "Dependency changes require explicit approval and a separate task.",
    ),
    (
        r"\bpip\s+install\b",
        "Dependency changes require explicit approval and a separate task.",
    ),
    (r"\bsqlite3\b", "SQLite shell work is blocked until MIGRATION_GO."),
]


def deny(reason: str) -> None:
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": reason,
                }
            }
        )
    )
    sys.exit(0)


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return

    tool_input = payload.get("tool_input") or {}
    command = (
        tool_input.get("command")
        or tool_input.get("cmd")
        or payload.get("command")
        or payload.get("cmd")
        or ""
    )

    for pattern, reason in DENY_PATTERNS:
        if re.search(pattern, command):
            deny(reason)


if __name__ == "__main__":
    main()
