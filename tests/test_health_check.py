import json
import os
import subprocess
import sys
from pathlib import Path

from halo_swing_mcp.server import mcp
from halo_swing_mcp.tools.health import health_check


ROOT = Path(__file__).resolve().parents[1]
GOLDEN_PATH = ROOT / "tests" / "golden" / "health_check.json"


def load_golden() -> dict[str, object]:
    return json.loads(GOLDEN_PATH.read_text(encoding="utf-8"))


def test_health_check_matches_golden() -> None:
    assert health_check() == load_golden()


def test_mcp_server_imports_with_registered_tool() -> None:
    assert mcp.name == "halo_swing_mcp"


def test_harness_health_check_matches_golden(tmp_path: Path) -> None:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT / "src")

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "health_check",
            "--audit-log-path",
            str(tmp_path / "audit.jsonl"),
        ],
        check=True,
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
    )

    assert json.loads(result.stdout) == load_golden()
