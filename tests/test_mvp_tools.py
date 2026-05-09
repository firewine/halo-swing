import json
import subprocess
import sys
from pathlib import Path

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


ROOT = Path(__file__).resolve().parents[1]
MVP_CONTRACT = json.loads(
    (ROOT / "tests" / "golden" / "mvp_tool_contracts.json").read_text(
        encoding="utf-8"
    )
)

EXPECTED_MVP_TOOLS = set(MVP_CONTRACT["required_tools"])


def test_health_check_advertises_mvp_tools() -> None:
    payload = health_check()

    assert EXPECTED_MVP_TOOLS.issubset(set(payload["capabilities"]))
    assert payload["live_data_required"] is False


def test_market_macro_event_and_news_tools_are_offline() -> None:
    market = get_market_snapshot(["QQQ", "SPY", "BTC"])
    macro = get_macro_snapshot()
    events = get_event_calendar(days=14)
    news = get_news_bundle(topic="all")

    assert len(market["snapshots"]) == 3
    assert market["live_data_required"] is False
    assert macro["macro_score"] > 0
    assert events["events"]
    assert news["evidence_cards"]
    assert all(card["summary"] for card in news["evidence_cards"])


def test_calculate_indicators_returns_required_swing_values() -> None:
    payload = calculate_indicators("QQQ")

    for key in (
        "rsi_14",
        "plus_di_14",
        "minus_di_14",
        "adx_14",
        "atr_14",
        "ma_20",
        "ma_50",
        "ma_200",
        "support_20",
        "resistance_20",
    ):
        assert payload[key] is not None
    assert payload["indicator_symbol"] == "QQQ"
    assert payload["live_data_required"] is False


def test_score_and_trade_guide_include_risk_controls() -> None:
    signal = score_leverage_swing("TQQQ")
    guide = generate_trade_guide("TQQQ")

    assert signal["asset"] == "TQQQ"
    assert signal["underlying"] == MVP_CONTRACT["scoring_fixture"]["underlying"]
    assert signal["action"] in MVP_CONTRACT["scoring_fixture"]["allowed_actions"]
    assert signal["config_hash"].startswith("sha256:")
    assert signal["stop"]
    assert signal["take_profit"]
    assert signal["stop_summary"]
    assert signal["take_profit_summary"]
    assert guide["guide"]["stop_conditions"]
    assert guide["guide"]["take_profit_conditions"]


def test_evaluate_position_returns_management_action() -> None:
    payload = evaluate_position(asset="TQQQ", entry_price=100, current_price=114)

    assert payload["action"] in {"WAIT", "TRIM", "EXIT", "STOP"}
    assert payload["position_state"] in {"maintain", "trim", "exit", "stop"}
    assert payload["stop_conditions"]


def test_record_label_and_evaluate_ledger(tmp_path: Path) -> None:
    ledger_path = tmp_path / "signal_ledger.jsonl"
    signal = score_leverage_swing("TQQQ")
    recorded = record_signal(signal=signal, ledger_path=str(ledger_path))
    duplicate = record_signal(signal=signal, ledger_path=str(ledger_path))
    label = label_signal_outcome(
        signal_id=signal["signal_id"],
        ledger_path=str(ledger_path),
    )
    performance = evaluate_recorded_score_performance(ledger_path=str(ledger_path))

    assert recorded["status"] == "recorded"
    assert duplicate["status"] == "duplicate"
    assert recorded["record"]["feature_snapshot"]["indicator_symbol"] == "QQQ"
    assert recorded["record"]["evidence_cards"]
    assert recorded["record"]["run_journal"]["config_hash"] == signal["config_hash"]
    assert ledger_path.exists()
    assert label["outcome"] in MVP_CONTRACT["labeling_fixture"]["allowed_outcomes"]
    assert performance["sample_size"] == 1
    assert performance["ledger_ref"] == str(ledger_path)


def test_render_chart_writes_png(tmp_path: Path) -> None:
    payload = render_chart("QQQ", output_dir=str(tmp_path))
    chart_path = Path(payload["path"])

    assert chart_path.exists()
    assert chart_path.read_bytes().startswith(b"\x89PNG\r\n\x1a\n")
    assert payload["artifact_ref"]["ref_type"] == "CHART"


def test_feedback_keeps_champion_unchanged() -> None:
    suggestion = suggest_weight_update()
    comparison = compare_champion_challenger()

    assert suggestion["challenger"]["status"] == "challenger"
    assert suggestion["validation"]["valid"] is True
    assert comparison["decision"] == "keep_champion_shadow_challenger"


def test_harness_executes_parameterized_tool(tmp_path: Path) -> None:
    audit_path = tmp_path / "audit.jsonl"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "score_leverage_swing",
            "--input-json",
            '{"asset": "TQQQ"}',
            "--audit-log-path",
            str(audit_path),
        ],
        check=True,
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    payload = json.loads(result.stdout)
    assert payload["asset"] == "TQQQ"
    assert payload["stop"]
    assert audit_path.exists()


def test_server_tool_wrappers_execute(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("HALO_SWING_AUDIT_LOG_PATH", str(tmp_path / "audit.jsonl"))
    from halo_swing_mcp import server

    assert server.get_market_snapshot()["snapshots"]
    assert server.calculate_indicators("QQQ")["indicator_symbol"] == "QQQ"
    assert server.score_leverage_swing("TQQQ")["asset"] == "TQQQ"
    assert server.generate_trade_guide("TQQQ")["guide"]["stop_conditions"]
