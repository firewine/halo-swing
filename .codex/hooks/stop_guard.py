#!/usr/bin/env python3
import json
import os
import subprocess
import sys
from pathlib import Path


def emit_block(reason: str) -> None:
    print(json.dumps({"decision": "block", "reason": reason}))
    sys.exit(0)


def run(cmd: str, cwd: Path, timeout: int = 180) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=cwd,
        shell=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=timeout,
    )


def load_payload() -> dict:
    try:
        return json.load(sys.stdin)
    except Exception:
        return {}


def repo_root(start: Path) -> Path:
    result = run("git rev-parse --show-toplevel", start, timeout=30)
    if result.returncode == 0:
        return Path(result.stdout.strip())
    return start


def changed_paths(cwd: Path) -> list[str]:
    result = run("git status --porcelain", cwd, timeout=30)
    if result.returncode != 0:
        emit_block("Unable to inspect git status.\n\n" + result.stdout[-4000:])

    paths: list[str] = []
    for line in result.stdout.splitlines():
        if len(line) < 4:
            continue
        path = line[3:].strip()
        if " -> " in path:
            path = path.split(" -> ", 1)[1].strip()
        if path:
            paths.append(path)
    return sorted(set(paths))


def main() -> None:
    payload = load_payload()

    if payload.get("stop_hook_active"):
        return

    cwd = repo_root(Path(payload.get("cwd") or os.getcwd()))
    task_file = cwd / ".codex" / "tasks" / "current.json"
    if not task_file.exists():
        task_file = cwd / "docs" / "codex-task.json"

    if not task_file.exists():
        return

    task = json.loads(task_file.read_text())
    if task.get("mode") != "implement":
        return

    changed = changed_paths(cwd)
    if not changed:
        return

    allowed = set(task.get("allowed_edit_paths", []))
    blocked_prefixes = tuple(task.get("blocked_path_prefixes", []))
    blocked_exact = set(task.get("blocked_exact_paths", []))

    violations: list[str] = []
    for path in changed:
        if path in blocked_exact:
            violations.append(f"{path} is explicitly blocked")
        elif blocked_prefixes and path.startswith(blocked_prefixes):
            violations.append(f"{path} is under a blocked path prefix")
        elif path not in allowed:
            violations.append(f"{path} is outside allowed_edit_paths")

    if violations:
        emit_block(
            "Scope violation detected. Revert, commit prior work, or update "
            "docs/codex-task.json before finishing.\n\n"
            + "\n".join(f"- {violation}" for violation in violations)
        )

    failures: list[str] = []
    for cmd in task.get("required_commands", []):
        result = run(cmd, cwd)
        if result.returncode != 0:
            failures.append(f"$ {cmd}\n{result.stdout[-6000:]}")

    if failures:
        emit_block(
            "Required verification failed. Fix the errors and rerun "
            "verification before finishing.\n\n"
            + "\n\n".join(failures)
        )


if __name__ == "__main__":
    main()
