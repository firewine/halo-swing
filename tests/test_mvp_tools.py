import json
import subprocess
import sys
from pathlib import Path

import pytest

from halo_swing_mcp.audit import read_audit_events
from halo_swing_mcp.config import get_settings
from halo_swing_mcp.tools import scoring as scoring_tools
from halo_swing_mcp.strategy import get_strategy_config, validate_strategy_config
from halo_swing_mcp.tools.health import health_check
from halo_swing_mcp.tools.market import (
    calculate_indicators,
    create_document_evidence_card,
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
    evaluate_score_performance,
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

    assert set(payload["capabilities"]) == EXPECTED_MVP_TOOLS
    assert payload["live_data_required"] is False


def test_phase6_feedback_tools_are_manifested() -> None:
    assert {
        "evaluate_score_performance",
        "suggest_weight_update",
        "compare_champion_challenger",
    }.issubset(EXPECTED_MVP_TOOLS)


def test_phase7_runtime_tools_are_manifested() -> None:
    assert {
        "get_runtime_status",
        "record_runtime_checkpoint",
    }.issubset(EXPECTED_MVP_TOOLS)


def test_phase9_btc_tools_are_manifested() -> None:
    assert {
        "get_btc_risk_settings",
        "update_btc_risk_settings",
        "get_btc_risk_status",
        "reset_btc_daily_risk_state",
        "save_binance_credentials",
        "get_binance_credentials_status",
        "check_binance_coinm_connectivity",
        "get_binance_coinm_account_snapshot",
        "normalize_binance_coinm_account_snapshot",
        "preview_btc_order",
        "execute_btc_order",
    }.issubset(EXPECTED_MVP_TOOLS)


def test_market_macro_event_and_news_tools_are_offline() -> None:
    market = get_market_snapshot(["QQQ", "SPY", "BTC"])
    default_market = get_market_snapshot()
    macro = get_macro_snapshot()
    events = get_event_calendar(days=14)
    news = get_news_bundle(topic="all")

    assert len(market["snapshots"]) == 3
    assert market["live_data_required"] is False
    assert (
        market["market_snapshot_contract"]["schema_version"]
        == MVP_CONTRACT["market_fixture"]["schema"]
    )
    assert market["market_snapshot_contract"]["feature_store_persistence"] is False
    assert market["market_snapshot_contract"]["live_data_required"] is False
    assert market["data_freshness_status"] == "FRESH"
    assert market["degraded_mode"] is False
    assert market["data_warnings"] == []
    default_symbols = {snapshot["symbol"] for snapshot in default_market["snapshots"]}
    assert set(MVP_CONTRACT["market_fixture"]["core_assets"]).issubset(
        default_symbols
    )
    for field in MVP_CONTRACT["market_fixture"]["required_snapshot_fields"]:
        assert all(field in snapshot for snapshot in market["snapshots"])
    guard_checks = {
        check["name"]: check["passed"]
        for check in default_market["market_snapshot_guard"]["checks"]
    }
    for check_name in MVP_CONTRACT["market_fixture"]["required_guard_checks"]:
        assert guard_checks[check_name] is True
    assert default_market["market_snapshot_guard"]["status"] == "ok"
    assert macro["macro_score"] > 0
    assert macro["macro_filter_contract"]["schema_version"] == "macro_filter.v1"
    assert macro["macro_filter_summary"]["schema_version"] == "macro_filter_summary.v1"
    assert macro["macro_filter_summary"]["live_data_required"] is False
    for key in MVP_CONTRACT["macro_fixture"]["required_indicators"]:
        assert key in macro["indicators"]
        assert key in macro["macro_filter_summary"]["indicator_states"]
    for field in MVP_CONTRACT["macro_fixture"]["required_summary_fields"]:
        assert field in macro["macro_filter_summary"]
    assert events["events"]
    assert news["evidence_cards"]
    assert (
        news["news_score_contract"]["schema_version"]
        == MVP_CONTRACT["news_fixture"]["required_contract_schema"]
    )
    assert (
        news["news_source_policy_contract"]["schema_version"]
        == MVP_CONTRACT["news_fixture"]["required_source_policy_schema"]
    )
    assert set(MVP_CONTRACT["news_fixture"]["required_source_groups"]).issubset(
        news["news_source_policy_contract"]["covered_source_groups"]
    )
    source_policy_checks = {
        check["name"]: check["passed"]
        for check in news["news_source_policy_guard"]["checks"]
    }
    for check_name in MVP_CONTRACT["news_fixture"][
        "required_source_policy_guard_checks"
    ]:
        assert source_policy_checks[check_name] is True
    assert news["news_source_policy_guard"]["status"] == "ok"
    assert all(card["summary"] for card in news["evidence_cards"])
    for key in MVP_CONTRACT["news_fixture"]["required_scores"]:
        assert 0 <= news[key] <= 1
        assert key in news["news_score_contract"]["required_scores"]
    for field in MVP_CONTRACT["news_fixture"]["required_card_fields"]:
        assert all(card[field] for card in news["evidence_cards"])
    for source_group in MVP_CONTRACT["news_fixture"]["required_source_groups"]:
        assert news["source_group_counts"][source_group] >= 1
    for modality in MVP_CONTRACT["news_fixture"]["required_modalities"]:
        assert news["modality_counts"][modality] >= 1
    assert news["artifact_refs"]
    assert news["multimodal_evidence_guard"]["status"] == "ok"
    assert all(
        check["passed"] for check in news["multimodal_evidence_guard"]["checks"]
    )


def test_market_indicator_and_chart_tools_normalize_symbol_timeframe_identity(
    tmp_path: Path,
) -> None:
    market = get_market_snapshot([" qqq ", " tqqq "])
    indicators = calculate_indicators(" tqqq ", timeframe=" 1D ")
    chart_dir = tmp_path / "charts"
    chart = render_chart(" qqq ", timeframe=" 1D ", output_dir=f" {chart_dir} ")

    assert [snapshot["symbol"] for snapshot in market["snapshots"]] == ["QQQ", "TQQQ"]
    assert market["market_snapshot_guard"]["status"] == "ok"
    assert indicators["symbol"] == "TQQQ"
    assert indicators["indicator_symbol"] == "QQQ"
    assert indicators["timeframe"] == "1d"
    assert indicators["latest_bar"]["timeframe"] == "1d"
    assert chart["symbol"] == "QQQ"
    assert chart["timeframe"] == "1d"
    assert Path(chart["path"]) == chart_dir / "QQQ_1d.png"
    assert Path(chart["path"]).exists()
    assert not (chart_dir / "QQQ_ 1D .png").exists()
    assert chart["chart_artifact_guard"]["status"] == "ok"


def test_event_and_news_tools_normalize_public_identity() -> None:
    events = get_event_calendar(days=14)
    news = get_news_bundle(topic=" ALL ")

    assert events["days"] == 14
    assert events["event_policy_guard"]["status"] == "ok"
    assert news["topic"] == "all"
    assert news["news_source_policy_guard"]["status"] == "ok"
    assert news["evidence_cards"]


@pytest.mark.parametrize("days", [0, -1, "14", None, 1.5, True])
def test_event_calendar_rejects_invalid_days_identity(days) -> None:
    with pytest.raises(ValueError, match="days must be a positive integer"):
        get_event_calendar(days=days)


@pytest.mark.parametrize("topic", ["   ", None, 123])
def test_news_bundle_rejects_invalid_topic_identity(topic) -> None:
    with pytest.raises(ValueError, match="topic must be a nonempty string"):
        get_news_bundle(topic=topic)


def test_news_bundle_rejects_topic_control_character() -> None:
    with pytest.raises(ValueError, match="topic must not contain control characters"):
        get_news_bundle(topic="all\n")


@pytest.mark.parametrize("symbol", ["   ", None, 123])
def test_market_indicator_and_chart_tools_reject_invalid_symbol_identity(
    symbol,
    tmp_path: Path,
) -> None:
    chart_dir = tmp_path / "charts"

    with pytest.raises(ValueError, match="symbol must be a nonempty string"):
        get_market_snapshot([symbol])
    with pytest.raises(ValueError, match="symbol must be a nonempty string"):
        calculate_indicators(symbol)
    with pytest.raises(ValueError, match="symbol must be a nonempty string"):
        render_chart(symbol, output_dir=str(chart_dir))

    assert not chart_dir.exists()


@pytest.mark.parametrize("symbols", ["QQQ", ("QQQ",), {"symbol": "QQQ"}, True])
def test_market_snapshot_rejects_invalid_symbols_container(symbols) -> None:
    with pytest.raises(
        ValueError,
        match="symbols must be a list of nonempty strings",
    ):
        get_market_snapshot(symbols)


def test_market_indicator_and_chart_tools_reject_symbol_control_character(
    tmp_path: Path,
) -> None:
    chart_dir = tmp_path / "charts"

    with pytest.raises(ValueError, match="symbol must not contain control characters"):
        get_market_snapshot(["QQQ\n"])
    with pytest.raises(ValueError, match="symbol must not contain control characters"):
        calculate_indicators("QQQ\n")
    with pytest.raises(ValueError, match="symbol must not contain control characters"):
        render_chart("QQQ\n", output_dir=str(chart_dir))

    assert not chart_dir.exists()


@pytest.mark.parametrize("timeframe", ["   ", None, 123])
def test_indicator_and_chart_tools_reject_invalid_timeframe_identity(
    timeframe,
    tmp_path: Path,
) -> None:
    chart_dir = tmp_path / "charts"

    with pytest.raises(ValueError, match="timeframe must be a nonempty string"):
        calculate_indicators("QQQ", timeframe=timeframe)
    with pytest.raises(ValueError, match="timeframe must be a nonempty string"):
        render_chart("QQQ", timeframe=timeframe, output_dir=str(chart_dir))

    assert not chart_dir.exists()


def test_indicator_and_chart_tools_reject_timeframe_control_character(
    tmp_path: Path,
) -> None:
    chart_dir = tmp_path / "charts"

    with pytest.raises(
        ValueError,
        match="timeframe must not contain control characters",
    ):
        calculate_indicators("QQQ", timeframe="1d\n")
    with pytest.raises(
        ValueError,
        match="timeframe must not contain control characters",
    ):
        render_chart("QQQ", timeframe="1d\n", output_dir=str(chart_dir))

    assert not chart_dir.exists()


@pytest.mark.parametrize("output_dir", ["", "   ", 123, False])
def test_render_chart_rejects_invalid_output_dir(output_dir) -> None:
    with pytest.raises(ValueError, match="output_dir must be a nonempty string"):
        render_chart("QQQ", output_dir=output_dir)


def test_render_chart_rejects_output_dir_control_character(
    tmp_path: Path,
) -> None:
    chart_dir = tmp_path / "charts"

    with pytest.raises(
        ValueError,
        match="output_dir must not contain control characters",
    ):
        render_chart("QQQ", output_dir=f"{chart_dir}\n")

    assert not chart_dir.exists()


def test_render_chart_uses_valid_env_artifact_dir(
    tmp_path: Path,
    monkeypatch,
) -> None:
    artifact_dir = tmp_path / "artifacts"
    monkeypatch.setenv("HALO_SWING_ARTIFACT_DIR", f" {artifact_dir} ")
    get_settings.cache_clear()

    try:
        chart = render_chart("QQQ")
    finally:
        get_settings.cache_clear()

    chart_path = artifact_dir / "charts" / "QQQ_1d.png"
    assert Path(chart["path"]) == chart_path
    assert chart["artifact_ref"]["ref"] == str(chart_path)
    assert chart_path.exists()
    assert chart["chart_artifact_guard"]["status"] == "ok"


def test_render_chart_rejects_invalid_env_artifact_dir_without_fallback(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.chdir(tmp_path)
    invalid_cases = [
        (
            "",
            "HALO_SWING_ARTIFACT_DIR must be a nonempty string",
            tmp_path / "artifacts",
        ),
        (
            "   ",
            "HALO_SWING_ARTIFACT_DIR must be a nonempty string",
            tmp_path / "artifacts",
        ),
        (
            f"{tmp_path / 'bad'}\x7fartifacts",
            "HALO_SWING_ARTIFACT_DIR must not contain control characters",
            tmp_path / "bad\x7fartifacts",
        ),
    ]

    for env_value, expected_error, unexpected_path in invalid_cases:
        monkeypatch.setenv("HALO_SWING_ARTIFACT_DIR", env_value)
        get_settings.cache_clear()

        try:
            with pytest.raises(ValueError, match=expected_error):
                render_chart("QQQ")
        finally:
            get_settings.cache_clear()
        assert not unexpected_path.exists()


def test_document_summary_input_creates_guarded_evidence_card() -> None:
    payload = create_document_evidence_card(
        summary=" FOMC minutes summary says policy remains restrictive but stable. ",
        artifact_ref=" artifact://documents/fomc-minutes-summary.pdf ",
        ref_type=" pdf ",
        modality=" pdf_summary ",
        evidence_id=" manual_document_summary ",
        category=" manual_document ",
        source=" manual:document_summary ",
        observed_at=" 2026-05-11T00:00:00Z ",
        asset_scope=[" qqq ", " tqqq "],
        bias=" slightly_bullish ",
        strength=1.57,
        confidence=-0.25,
        buy_impact=" context_only ",
        sell_impact=" context_only ",
        invalidating_condition=" Document summary becomes stale or contradicted. ",
    )
    card = payload["evidence_card"]

    assert payload["schema_version"] == "document_evidence_card.v1"
    assert payload["status"] == "ok"
    assert payload["document_summary_input_contract"]["parser_added"] is False
    assert payload["document_summary_input_contract"]["file_read"] is False
    assert payload["document_summary_input_contract"]["network_call"] is False
    assert payload["document_summary_input_contract"]["raw_document_returned"] is False
    assert payload["document_summary_input_guard"]["status"] == "ok"
    assert payload["multimodal_evidence_guard"]["status"] == "ok"
    assert payload["modality_counts"]["pdf_summary"] == 1
    assert payload["artifact_refs"][0]["artifact_ref"]["ref_type"] == "PDF"
    assert card["modality"] == "pdf_summary"
    assert card["observed_at"] == "2026-05-11T00:00:00Z"
    assert card["artifact_ref"]["metadata"]["parsed_by_mcp"] is False
    assert card["artifact_ref"]["ref"] == "artifact://documents/fomc-minutes-summary.pdf"
    assert card["asset_scope"] == ["QQQ", "TQQQ"]
    assert card["bias"] == "slightly_bullish"
    assert card["strength"] == 1.0
    assert card["confidence"] == 0.0
    assert payload["live_data_required"] is False


@pytest.mark.parametrize(
    ("overrides", "expected_error"),
    [
        ({"summary": "   "}, "summary must be a nonempty string"),
        ({"summary": "line one\nline two"}, "summary must not contain control characters"),
        ({"artifact_ref": ""}, "artifact_ref must be a nonempty string"),
        (
            {"artifact_ref": "artifact://documents/fomc-minutes-summary.pdf\n"},
            "artifact_ref must not contain control characters",
        ),
        ({"ref_type": None}, "ref_type must be a nonempty string"),
        ({"modality": 123}, "modality must be a nonempty string"),
        ({"observed_at": "   "}, "observed_at must be a nonempty string"),
        (
            {"observed_at": "2026-05-11T00:00:00Z\n"},
            "observed_at must not contain control characters",
        ),
        ({"asset_scope": "QQQ,TQQQ"}, "asset_scope must be a list of nonempty strings"),
        ({"asset_scope": ["QQQ", "   "]}, "asset_scope must be a nonempty string"),
        (
            {"asset_scope": ["QQQ", "TQQQ\n"]},
            "asset_scope must not contain control characters",
        ),
        ({"asset_scope": ["QQQ", 123]}, "asset_scope must be a nonempty string"),
        ({"strength": "0.5"}, "strength must be a finite number"),
        ({"confidence": float("nan")}, "confidence must be a finite number"),
    ],
)
def test_document_summary_input_rejects_invalid_public_inputs(
    overrides,
    expected_error,
) -> None:
    payload = {
        "summary": "FOMC minutes summary says policy remains restrictive but stable.",
        "artifact_ref": "artifact://documents/fomc-minutes-summary.pdf",
        "asset_scope": ["QQQ", "TQQQ"],
    }
    payload.update(overrides)

    with pytest.raises(ValueError, match=expected_error):
        create_document_evidence_card(**payload)


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
        "previous_swing_high",
        "previous_swing_low",
    ):
        assert payload[key] is not None
    assert (
        payload["swing_level_contract"]["schema_version"]
        == MVP_CONTRACT["indicator_fixture"]["swing_level_schema"]
    )
    assert payload["swing_level_contract"]["live_data_required"] is False
    for field in MVP_CONTRACT["indicator_fixture"]["required_swing_level_fields"]:
        assert field in payload
    assert payload["previous_swing_high"] > 0
    assert payload["previous_swing_low"] > 0
    assert payload["previous_swing_high_timestamp"]
    assert payload["previous_swing_low_timestamp"]
    assert payload["indicator_symbol"] == "QQQ"
    assert payload["live_data_required"] is False


def test_calculate_indicators_supports_declared_fixture_timeframes() -> None:
    for timeframe in ("1d", "4h", "1h"):
        payload = calculate_indicators("QQQ", timeframe=timeframe)

        assert payload["timeframe"] == timeframe
        assert payload["latest_bar"]["timeframe"] == timeframe
        assert payload["timeframe_contract"]["provider_supports_timeframe"] is True
        assert timeframe in payload["timeframe_contract"]["supported_timeframes"]
        assert payload["rsi_14"] is not None

    with pytest.raises(ValueError, match="unsupported timeframe"):
        calculate_indicators("QQQ", timeframe="15m")


def test_score_and_trade_guide_include_risk_controls() -> None:
    signal = score_leverage_swing("TQQQ")
    guide = generate_trade_guide("TQQQ")

    assert signal["asset"] == "TQQQ"
    assert signal["underlying"] == MVP_CONTRACT["scoring_fixture"]["underlying"]
    assert signal["action"] in MVP_CONTRACT["scoring_fixture"]["allowed_actions"]
    assert (
        signal["news_usage_contract"]["schema_version"]
        == MVP_CONTRACT["news_fixture"]["required_scoring_usage_schema"]
    )
    assert signal["news_usage_contract"]["news_score_field"] == "news_score"
    assert (
        signal["strategy_config_contract"]["schema_version"]
        == MVP_CONTRACT["scoring_fixture"]["strategy_config_schema"]
    )
    assert signal["strategy_config_contract"]["valid"] is True
    assert signal["strategy_config_contract"]["config_hash_matches_signal"] is True
    assert signal["strategy_config_contract"]["weight_sum"] == 1.0
    for field in MVP_CONTRACT["scoring_fixture"][
        "required_strategy_config_contract_fields"
    ]:
        assert field in signal["strategy_config_contract"]
    for component in MVP_CONTRACT["scoring_fixture"]["required_component_scores"]:
        assert component in signal["component_scores"]
        assert 0 <= signal["component_scores"][component] <= 1
    assert signal["config_hash"].startswith("sha256:")
    assert signal["stop"]
    assert signal["take_profit"]
    assert signal["stop_summary"]
    assert signal["take_profit_summary"]
    assert (
        guide["trade_guide_contract"]["schema_version"]
        == MVP_CONTRACT["trade_guide_fixture"]["schema"]
    )
    for field in MVP_CONTRACT["trade_guide_fixture"]["required_guide_fields"]:
        assert field in guide["guide"]
        assert guide["guide"][field]
    assert guide["trade_guide_contract"]["time_barrier_days"] > 0
    assert guide["trade_guide_contract"]["config_hash_matches_signal"] is True
    assert guide["trade_guide_contract"]["order_submission"] is False
    assert guide["trade_guide_contract"]["live_data_required"] is False
    assert guide["trade_guide_contract"]["db_required"] is False
    guard_checks = {
        check["name"]: check["passed"]
        for check in guide["trade_guide_guard"]["checks"]
    }
    for check_name in MVP_CONTRACT["trade_guide_fixture"]["required_guard_checks"]:
        assert guard_checks[check_name] is True
    assert guide["trade_guide_guard"]["status"] == "ok"


def test_scoring_tools_normalize_asset_and_timeframe_identity() -> None:
    signal = score_leverage_swing(" tqqq ", timeframe=" swing_3d_10d ")
    guide = generate_trade_guide(" qld ", timeframe=" swing_3d_10d ")
    position = evaluate_position(
        asset=" tqqq ",
        entry_price=100,
        current_price=114,
        size=3,
    )

    assert signal["asset"] == "TQQQ"
    assert signal["underlying"] == "QQQ"
    assert signal["timeframe"] == "swing_3d_10d"
    assert signal["signal_id"].endswith("_tqqq")
    assert guide["asset"] == "QLD"
    assert guide["signal"]["asset"] == "QLD"
    assert guide["signal"]["timeframe"] == "swing_3d_10d"
    assert guide["trade_guide_guard"]["status"] == "ok"
    assert position["asset"] == "TQQQ"
    assert position["underlying"] == "QQQ"
    assert position["position_management_guard"]["status"] == "ok"


@pytest.mark.parametrize("asset", ["   ", None, 123])
def test_scoring_tools_reject_invalid_asset_identity(asset) -> None:
    for tool in (score_leverage_swing, generate_trade_guide, evaluate_position):
        with pytest.raises(ValueError, match="asset must be a nonempty string"):
            tool(asset=asset)


def test_scoring_tools_reject_asset_control_character() -> None:
    for tool in (score_leverage_swing, generate_trade_guide, evaluate_position):
        with pytest.raises(
            ValueError,
            match="asset must not contain control characters",
        ):
            tool(asset="TQQQ\n")


@pytest.mark.parametrize("timeframe", ["   ", None, 123])
def test_scoring_tools_reject_invalid_timeframe_identity(timeframe) -> None:
    for tool in (score_leverage_swing, generate_trade_guide):
        with pytest.raises(ValueError, match="timeframe must be a nonempty string"):
            tool(asset="TQQQ", timeframe=timeframe)


def test_scoring_tools_reject_timeframe_control_character() -> None:
    for tool in (score_leverage_swing, generate_trade_guide):
        with pytest.raises(
            ValueError,
            match="timeframe must not contain control characters",
        ):
            tool(asset="TQQQ", timeframe="swing_3d_10d\n")


def test_strategy_config_validation_rejects_invalid_weights() -> None:
    config = get_strategy_config()
    config["weights"]["trend"] = 0.99

    validation = validate_strategy_config(config)

    assert validation["schema_version"] == "strategy_config.v1"
    assert validation["valid"] is False
    assert "weights must sum to 1.0" in validation["errors"]
    assert validation["bounds_checked"] is True
    assert validation["sum_checked"] is True
    assert validation["db_required"] is False


def test_trade_guides_cover_target_leveraged_universe() -> None:
    for asset in ("QLD", "TQQQ", "SSO", "UPRO", "SOXL"):
        guide = generate_trade_guide(asset)

        assert guide["asset"] == asset
        assert guide["signal"]["config_hash"].startswith("sha256:")
        assert guide["guide"]["stop_conditions"]
        assert guide["guide"]["take_profit_conditions"]
        assert guide["guide"]["time_exit_conditions"]
        assert guide["signal"]["reason_summary"]


def test_high_event_risk_blocks_new_3x_entries() -> None:
    events = get_event_calendar(days=14)
    signal = score_leverage_swing("TQQQ")

    assert events["highest_event_risk"] > 0.70
    assert (
        events["event_policy_contract"]["schema_version"]
        == MVP_CONTRACT["event_fixture"]["policy_schema"]
    )
    assert set(MVP_CONTRACT["event_fixture"]["required_event_types"]).issubset(
        events["event_policy_contract"]["covered_event_types"]
    )
    policy_guard_checks = {
        check["name"]: check["passed"]
        for check in events["event_policy_guard"]["checks"]
    }
    for check_name in MVP_CONTRACT["event_fixture"][
        "required_policy_guard_checks"
    ]:
        assert policy_guard_checks[check_name] is True
    assert events["event_policy_guard"]["status"] == "ok"
    assert events["event_window_contract"]["schema_version"] == "event_danger_window.v1"
    assert events["event_window_summary"]["next_event_id"] == "evt_20260512_cpi"
    assert events["event_window_summary"]["blocks_new_3x_now"] is False
    assert events["event_window_summary"]["blocks_new_2x_now"] is False
    assert all("danger_window" in event for event in events["events"])
    assert all(
        event["danger_window"]["live_data_required"] is False
        for event in events["events"]
    )
    assert signal["action"] != "BUY_3X"
    assert any("3x entries" in warning for warning in signal["risk_warnings"])


def test_macro_filter_blocks_new_leveraged_longs(monkeypatch: pytest.MonkeyPatch) -> None:
    macro = get_macro_snapshot()
    macro["macro_score"] = 0.25
    macro["macro_filter_summary"] = {
        **macro["macro_filter_summary"],
        "risk_triggers": ["vix_spike", "dxy_rising", "front_end_yield_rising"],
        "blocks_new_longs_now": True,
        "blocks_new_3x_now": True,
        "blocks_new_2x_now": True,
    }

    monkeypatch.setattr(scoring_tools, "get_macro_snapshot", lambda: macro)

    signal = scoring_tools.score_leverage_swing("TQQQ")

    assert signal["action"] == "BLOCK"
    assert any("Macro filter blocks" in warning for warning in signal["risk_warnings"])


def test_scoring_uses_explicit_news_score_field(monkeypatch: pytest.MonkeyPatch) -> None:
    news = get_news_bundle(topic="all")
    news["average_strength"] = 1.0
    news["news_score"] = 0.0

    monkeypatch.setattr(scoring_tools, "get_news_bundle", lambda topic="all": news)

    signal = scoring_tools.score_leverage_swing("TQQQ")

    assert signal["news_usage_contract"]["used_in_component"] == "theme"
    assert signal["component_scores"]["theme"] < 0.4


def test_evaluate_position_returns_management_action() -> None:
    payload = evaluate_position(asset="TQQQ", entry_price=100, current_price=114, size=3)

    assert payload["action"] in MVP_CONTRACT["position_fixture"]["allowed_actions"]
    assert (
        payload["position_state"]
        in MVP_CONTRACT["position_fixture"]["allowed_position_states"]
    )
    assert payload["stop_conditions"]
    assert payload["take_profit_conditions"]
    assert payload["entry_price"] == 100.0
    assert payload["current_price"] == 114.0
    assert payload["size"] == 3.0
    assert (
        payload["position_management_contract"]["schema_version"]
        == MVP_CONTRACT["position_fixture"]["schema"]
    )
    assert payload["position_management_contract"]["numeric_authority"] is True
    assert payload["position_management_contract"]["order_submission"] is False
    assert payload["position_management_contract"]["live_data_required"] is False
    assert payload["position_management_contract"]["db_required"] is False
    guard_checks = {
        check["name"]: check["passed"]
        for check in payload["position_management_guard"]["checks"]
    }
    for check_name in MVP_CONTRACT["position_fixture"]["required_guard_checks"]:
        assert guard_checks[check_name] is True
    assert payload["position_management_guard"]["status"] == "ok"


def test_evaluate_position_rejects_invalid_numeric_inputs() -> None:
    invalid_cases = [
        (
            {"entry_price": 0},
            "entry_price must be a positive finite number",
        ),
        (
            {"entry_price": float("inf")},
            "entry_price must be a positive finite number",
        ),
        (
            {"current_price": False},
            "current_price must be a positive finite number",
        ),
        (
            {"current_price": float("nan")},
            "current_price must be a positive finite number",
        ),
        (
            {"size": "3"},
            "size must be a positive finite number",
        ),
        (
            {"size": -1},
            "size must be a positive finite number",
        ),
    ]

    for overrides, expected_error in invalid_cases:
        with pytest.raises(ValueError, match=expected_error):
            evaluate_position(asset="TQQQ", **overrides)


def test_record_label_and_evaluate_ledger(tmp_path: Path) -> None:
    ledger_path = tmp_path / "signal_ledger.jsonl"
    signal = score_leverage_swing("TQQQ")
    recorded = record_signal(signal=signal, ledger_path=f" {ledger_path} ")
    duplicate = record_signal(signal=signal, ledger_path=f" {ledger_path} ")
    label = label_signal_outcome(
        signal_id=signal["signal_id"],
        ledger_path=f" {ledger_path} ",
    )
    performance = evaluate_recorded_score_performance(ledger_path=f" {ledger_path} ")

    assert recorded["status"] == "recorded"
    assert duplicate["status"] == "duplicate"
    assert recorded["record"]["feature_snapshot"]["indicator_symbol"] == "QQQ"
    assert recorded["record"]["evidence_cards"]
    assert all(card["modality"] for card in recorded["record"]["evidence_cards"])
    assert (
        recorded["run_journal_contract"]["schema_version"]
        == MVP_CONTRACT["recording_fixture"]["run_journal_schema"]
    )
    run_journal = recorded["record"]["run_journal"]
    for field in MVP_CONTRACT["recording_fixture"]["required_run_journal_fields"]:
        assert run_journal[field]
    assert run_journal["schema_version"] == "run_journal.v1"
    assert run_journal["run_id"] == signal["run_id"]
    assert run_journal["signal_id"] == signal["signal_id"]
    assert run_journal["config_hash"] == signal["config_hash"]
    assert run_journal["config_version"] == signal["config_version"]
    assert run_journal["live_data_required"] is False
    assert run_journal["db_required"] is False
    assert signal["signal_id"] in run_journal["idempotency_key"]
    assert ledger_path.exists()
    assert label["outcome"] in MVP_CONTRACT["labeling_fixture"]["allowed_outcomes"]
    assert (
        label["label_contract"]["schema_version"]
        == MVP_CONTRACT["labeling_fixture"]["schema"]
    )
    assert (
        label["label_contract"]["mfe_mae_window"]
        == MVP_CONTRACT["labeling_fixture"]["metric_window"]
    )
    for field in MVP_CONTRACT["labeling_fixture"]["required_metric_fields"]:
        assert field in label
        assert field in label["label_contract"]["metric_fields"]
    for field in MVP_CONTRACT["labeling_fixture"]["required_barrier_fields"]:
        assert field in label
        assert field in label["label_contract"]["barrier_fields"]
    assert performance["sample_size"] == 1
    assert performance["ledger_ref"] == str(ledger_path)


def test_record_signal_normalizes_public_signal_identity(tmp_path: Path) -> None:
    ledger_path = tmp_path / "signal_ledger.jsonl"
    signal = score_leverage_swing("TQQQ")
    supplied_signal = {
        **signal,
        "signal_id": f" {signal['signal_id']} ",
        "run_id": f" {signal['run_id']} ",
        "underlying": " qqq ",
    }

    recorded = record_signal(signal=supplied_signal, ledger_path=str(ledger_path))
    stored_signal = recorded["record"]["signal"]
    run_journal = recorded["record"]["run_journal"]

    assert recorded["signal_id"] == signal["signal_id"]
    assert stored_signal["signal_id"] == signal["signal_id"]
    assert stored_signal["run_id"] == signal["run_id"]
    assert stored_signal["underlying"] == "QQQ"
    assert run_journal["signal_id"] == signal["signal_id"]
    assert run_journal["run_id"] == signal["run_id"]
    assert recorded["record"]["feature_snapshot"]["indicator_symbol"] == "QQQ"


def test_record_signal_rejects_invalid_public_signal_identity() -> None:
    signal = score_leverage_swing("TQQQ")
    invalid_cases = [
        (
            "not-a-signal",
            "signal must be an object",
        ),
        (
            {},
            "signal.signal_id must be a nonempty string",
        ),
        (
            {**signal, "signal_id": "   "},
            "signal.signal_id must be a nonempty string",
        ),
        (
            {**signal, "run_id": 123},
            "signal.run_id must be a nonempty string",
        ),
        (
            {**signal, "created_at": ""},
            "signal.created_at must be a nonempty string",
        ),
        (
            {**signal, "underlying": None},
            "signal.underlying must be a nonempty string",
        ),
        (
            {**signal, "config_version": "   "},
            "signal.config_version must be a nonempty string",
        ),
        (
            {**signal, "config_hash": False},
            "signal.config_hash must be a nonempty string",
        ),
    ]

    for supplied_signal, expected_error in invalid_cases:
        with pytest.raises(ValueError, match=expected_error):
            record_signal(signal=supplied_signal)


def test_record_signal_rejects_signal_identity_control_character_inputs(
    tmp_path: Path,
) -> None:
    ledger_path = tmp_path / "signal_ledger.jsonl"
    signal = score_leverage_swing("TQQQ")
    invalid_cases = [
        (
            {**signal, "signal_id": f"{signal['signal_id']}\n"},
            "signal.signal_id must not contain control characters",
        ),
        (
            {**signal, "run_id": f"{signal['run_id']}\n"},
            "signal.run_id must not contain control characters",
        ),
        (
            {**signal, "created_at": f"{signal['created_at']}\n"},
            "signal.created_at must not contain control characters",
        ),
        (
            {**signal, "underlying": "QQQ\n"},
            "signal.underlying must not contain control characters",
        ),
        (
            {**signal, "config_version": f"{signal['config_version']}\n"},
            "signal.config_version must not contain control characters",
        ),
        (
            {**signal, "config_hash": f"{signal['config_hash']}\n"},
            "signal.config_hash must not contain control characters",
        ),
    ]

    for supplied_signal, expected_error in invalid_cases:
        with pytest.raises(ValueError, match=expected_error):
            record_signal(signal=supplied_signal, ledger_path=str(ledger_path))

        assert not ledger_path.exists()


def test_record_signal_rejects_invalid_ledger_path() -> None:
    invalid_cases = [
        (
            "",
            "ledger_path must be a nonempty string",
        ),
        (
            "   ",
            "ledger_path must be a nonempty string",
        ),
        (
            123,
            "ledger_path must be a nonempty string",
        ),
    ]

    for ledger_path, expected_error in invalid_cases:
        with pytest.raises(ValueError, match=expected_error):
            record_signal(ledger_path=ledger_path)


def test_recording_tools_reject_ledger_path_control_character_inputs(
    tmp_path: Path,
) -> None:
    ledger_path = tmp_path / "signal_ledger.jsonl"

    with pytest.raises(
        ValueError,
        match="ledger_path must not contain control characters",
    ):
        record_signal(ledger_path=f"{ledger_path}\n")

    with pytest.raises(
        ValueError,
        match="ledger_path must not contain control characters",
    ):
        label_signal_outcome(
            signal_id="swing-TQQQ-fixture-001",
            ledger_path=f"{ledger_path}\n",
        )

    with pytest.raises(
        ValueError,
        match="ledger_path must not contain control characters",
    ):
        evaluate_recorded_score_performance(ledger_path=f"{ledger_path}\n")

    assert not ledger_path.exists()


def test_label_signal_outcome_metrics_respect_time_barrier(tmp_path: Path) -> None:
    ledger_path = tmp_path / "signal_ledger.jsonl"
    signal = score_leverage_swing("TQQQ")
    record_signal(signal=signal, ledger_path=str(ledger_path))
    entry_price = float(signal["entry"]["reference_price"])
    price_path = [
        entry_price * 1.01,
        entry_price * 1.02,
        entry_price * 1.25,
    ]

    label = label_signal_outcome(
        signal_id=signal["signal_id"],
        price_path=price_path,
        stop_loss_pct=0.05,
        take_profit_pct=0.10,
        time_barrier_days=2,
        ledger_path=str(ledger_path),
    )

    assert label["outcome"] == "TIME_EXIT"
    assert label["first_barrier_hit"] is None
    assert label["hit_index"] == 1
    assert label["mfe"] == pytest.approx(0.02)
    assert label["mae"] == pytest.approx(0.01)
    assert label["realized_r"] == pytest.approx(0.4)
    assert (
        label["label_contract"]["mfe_mae_window"]
        == MVP_CONTRACT["labeling_fixture"]["metric_window"]
    )


def test_label_signal_outcome_normalizes_public_inputs(tmp_path: Path) -> None:
    ledger_path = tmp_path / "signal_ledger.jsonl"
    signal = score_leverage_swing("TQQQ")
    record_signal(signal=signal, ledger_path=str(ledger_path))
    entry_price = float(signal["entry"]["reference_price"])

    label = label_signal_outcome(
        signal_id=f" {signal['signal_id']} ",
        price_path=[entry_price * 1.01, entry_price * 1.02],
        stop_loss_pct=0.05,
        take_profit_pct=0.10,
        time_barrier_days=2,
        ledger_path=str(ledger_path),
    )
    event_invalidated = label_signal_outcome(
        signal_id=f" {signal['signal_id']} ",
        ledger_path=str(ledger_path),
        invalidated_by_event=True,
        invalidating_event_id=" evt_fixture_cpi ",
    )

    assert label["signal_id"] == signal["signal_id"]
    assert label["time_barrier_days"] == 2
    assert label["hit_index"] == 1
    assert event_invalidated["signal_id"] == signal["signal_id"]
    assert event_invalidated["invalidating_event_id"] == "evt_fixture_cpi"


def test_label_signal_outcome_rejects_invalid_public_inputs(tmp_path: Path) -> None:
    ledger_path = tmp_path / "signal_ledger.jsonl"
    signal = score_leverage_swing("TQQQ")
    record_signal(signal=signal, ledger_path=str(ledger_path))
    entry_price = float(signal["entry"]["reference_price"])

    invalid_cases = [
        (
            {"signal_id": "   "},
            "signal_id must be a nonempty string",
        ),
        (
            {"signal_id": 123},
            "signal_id must be a nonempty string",
        ),
        (
            {"price_path": "not-a-list"},
            "price_path must be a list of positive finite numbers",
        ),
        (
            {"price_path": [entry_price, 0]},
            "price_path must be a list of positive finite numbers",
        ),
        (
            {"price_path": [entry_price, float("nan")]},
            "price_path must be a list of positive finite numbers",
        ),
        (
            {"stop_loss_pct": 0},
            "stop_loss_pct must be a positive finite number",
        ),
        (
            {"stop_loss_pct": "0.05"},
            "stop_loss_pct must be a positive finite number",
        ),
        (
            {"stop_loss_pct": float("inf")},
            "stop_loss_pct must be a positive finite number",
        ),
        (
            {"take_profit_pct": "0.10"},
            "take_profit_pct must be a positive finite number",
        ),
        (
            {"take_profit_pct": 0},
            "take_profit_pct must be a positive finite number",
        ),
        (
            {"take_profit_pct": float("inf")},
            "take_profit_pct must be a positive finite number",
        ),
        (
            {"time_barrier_days": True},
            "time_barrier_days must be a positive integer",
        ),
        (
            {"time_barrier_days": 0},
            "time_barrier_days must be a positive integer",
        ),
        (
            {"time_barrier_days": "2"},
            "time_barrier_days must be a positive integer",
        ),
        (
            {"invalidated_by_event": "true"},
            "invalidated_by_event must be a boolean",
        ),
        (
            {"invalidated_by_event": True, "invalidating_event_id": "   "},
            "invalidating_event_id must be a nonempty string",
        ),
        (
            {"invalidated_by_event": True, "invalidating_event_id": 123},
            "invalidating_event_id must be a nonempty string",
        ),
        (
            {"ledger_path": ""},
            "ledger_path must be a nonempty string",
        ),
        (
            {"ledger_path": False},
            "ledger_path must be a nonempty string",
        ),
    ]

    for overrides, expected_error in invalid_cases:
        payload = {
            "signal_id": signal["signal_id"],
            "ledger_path": str(ledger_path),
        }
        payload.update(overrides)
        with pytest.raises(ValueError, match=expected_error):
            label_signal_outcome(**payload)


def test_label_signal_outcome_rejects_identity_control_character_inputs(
    tmp_path: Path,
) -> None:
    ledger_path = tmp_path / "signal_ledger.jsonl"
    signal = score_leverage_swing("TQQQ")
    record_signal(signal=signal, ledger_path=str(ledger_path))
    invalid_cases = [
        (
            {"signal_id": f"{signal['signal_id']}\n"},
            "signal_id must not contain control characters",
        ),
        (
            {
                "signal_id": signal["signal_id"],
                "invalidated_by_event": True,
                "invalidating_event_id": "event_cpi\n",
            },
            "invalidating_event_id must not contain control characters",
        ),
        (
            {
                "signal_id": signal["signal_id"],
                "invalidated_by_event": False,
                "invalidating_event_id": "event_cpi\n",
            },
            "invalidating_event_id must not contain control characters",
        ),
    ]

    for overrides, expected_error in invalid_cases:
        payload = {
            "signal_id": signal["signal_id"],
            "ledger_path": str(ledger_path),
        }
        payload.update(overrides)
        with pytest.raises(ValueError, match=expected_error):
            label_signal_outcome(**payload)


def test_evaluate_recorded_score_performance_rejects_invalid_days() -> None:
    with pytest.raises(ValueError, match="days must be a positive integer"):
        evaluate_recorded_score_performance(days=False)

    with pytest.raises(ValueError, match="days must be a positive integer"):
        evaluate_recorded_score_performance(days=0)

    with pytest.raises(ValueError, match="days must be a positive integer"):
        evaluate_recorded_score_performance(days=-1)

    with pytest.raises(ValueError, match="days must be a positive integer"):
        evaluate_recorded_score_performance(days="90")  # type: ignore[arg-type]


def test_evaluate_recorded_score_performance_rejects_invalid_ledger_path() -> None:
    with pytest.raises(ValueError, match="ledger_path must be a nonempty string"):
        evaluate_recorded_score_performance(ledger_path="")

    with pytest.raises(ValueError, match="ledger_path must be a nonempty string"):
        evaluate_recorded_score_performance(ledger_path=[])


def test_label_signal_outcome_supports_no_data_and_event_invalidation(
    tmp_path: Path,
) -> None:
    ledger_path = tmp_path / "signal_ledger.jsonl"
    signal = score_leverage_swing("TQQQ")
    record_signal(signal=signal, ledger_path=str(ledger_path))

    no_data = label_signal_outcome(
        signal_id=signal["signal_id"],
        price_path=[],
        ledger_path=str(ledger_path),
    )
    event_invalidated = label_signal_outcome(
        signal_id=signal["signal_id"],
        ledger_path=str(ledger_path),
        invalidated_by_event=True,
        invalidating_event_id="evt_fixture_cpi",
    )

    assert no_data["outcome"] == "NO_DATA"
    assert no_data["label_reason"] == "empty_price_path"
    assert no_data["label_contract"]["network_call"] is False
    assert event_invalidated["outcome"] == "INVALIDATED_BY_EVENT"
    assert event_invalidated["first_barrier_hit"] == "event_invalidation"
    assert event_invalidated["invalidating_event_id"] == "evt_fixture_cpi"
    assert set(MVP_CONTRACT["labeling_fixture"]["allowed_outcomes"]).issubset(
        event_invalidated["label_contract"]["supported_outcomes"]
    )


def test_render_chart_writes_png(tmp_path: Path) -> None:
    payload = render_chart("QQQ", output_dir=str(tmp_path))
    chart_path = Path(payload["path"])

    assert chart_path.exists()
    assert chart_path.read_bytes().startswith(b"\x89PNG\r\n\x1a\n")
    assert (
        payload["chart_artifact_contract"]["schema_version"]
        == MVP_CONTRACT["chart_fixture"]["artifact_schema"]
    )
    assert payload["chart_artifact_contract"]["network_call"] is False
    assert payload["chart_artifact_guard"]["status"] == "ok"
    guard_checks = {
        check["name"]: check["passed"]
        for check in payload["chart_artifact_guard"]["checks"]
    }
    for check_name in MVP_CONTRACT["chart_fixture"]["required_guard_checks"]:
        assert guard_checks[check_name] is True
    assert payload["artifact_ref"]["ref_type"] == "CHART"


def test_feedback_keeps_champion_unchanged() -> None:
    suggestion = suggest_weight_update()
    comparison = compare_champion_challenger()

    assert suggestion["challenger"]["status"] == "challenger"
    assert suggestion["validation"]["valid"] is True
    assert suggestion["validation"]["config_hash_matches"] is True
    assert (
        suggestion["challenger_contract"]["schema_version"]
        == MVP_CONTRACT["performance_fixture"]["challenger_contract_schema"]
    )
    for field in MVP_CONTRACT["performance_fixture"][
        "required_challenger_contract_fields"
    ]:
        assert field in suggestion["challenger_contract"]
    assert suggestion["challenger_contract"]["candidate_status"] == "challenger"
    assert suggestion["challenger_contract"]["champion_unchanged"] is True
    assert suggestion["challenger_contract"]["approval_required"] is True
    assert suggestion["challenger_contract"]["shadow_validation_required"] is True
    assert suggestion["challenger_contract"]["out_of_sample_required"] is True
    assert suggestion["challenger_contract"]["auto_promotion_allowed"] is False
    assert suggestion["challenger_contract"]["config_hash_matches_challenger"] is True
    assert comparison["decision"] == "keep_champion_shadow_challenger"
    assert MVP_CONTRACT["performance_fixture"]["requires_promotion_report"] is True
    assert comparison["promotion_report"]["approval_required"] is True
    assert comparison["promotion_report"]["out_of_sample_required"] is True
    assert comparison["promotion_report"]["champion_out_of_sample_ready"] is True
    assert comparison["promotion_report"]["challenger_out_of_sample_ready"] is True
    assert comparison["promotion_report"]["promote"] is False


def test_score_performance_includes_attribution_and_ablation() -> None:
    payload = evaluate_score_performance(
        days=MVP_CONTRACT["performance_fixture"]["default_window_days"]
    )

    for section in MVP_CONTRACT["performance_fixture"]["required_sections"]:
        assert section in payload
    assert payload["evaluation_window"]["requested_days"] == 90
    assert payload["evaluation_window"]["sample_source"] == "fixture_replay"
    assert (
        payload["evaluation_window"]["schema_version"]
        == MVP_CONTRACT["performance_fixture"]["evaluation_window_schema"]
    )
    for field in MVP_CONTRACT["performance_fixture"][
        "required_evaluation_window_fields"
    ]:
        assert field in payload["evaluation_window"]
    assert payload["sample_size"] >= 18
    assert payload["score_calibration"]["available"] is True
    assert payload["score_calibration"]["bins"]
    assert payload["score_calibration"]["largest_abs_calibration_error"] is not None
    assert (
        payload["score_calibration"]["score_bin_order_check"]
        == "higher_scores_outperform"
    )
    assert (
        payload["score_calibration"]["take_profit_rate_order_check"]
        == "higher_scores_higher_take_profit_rate"
    )
    assert payload["component_attribution"]["available"] is True
    assert payload["component_attribution"]["components"]
    assert payload["ablation_report"]["available"] is True
    assert payload["ablation_report"]["ablations"]
    assert payload["ablation_report"]["baseline_avg_score"] is not None
    assert payload["out_of_sample_report"]["ready"] is True
    assert payload["out_of_sample_report"]["out_of_sample_count"] >= 3
    assert (
        payload["out_of_sample_report"]["score_bin_order_check"]
        == "higher_scores_outperform"
    )
    assert payload["out_of_sample_report"]["asset_breakdown"]
    assert payload["out_of_sample_report"]["regime_breakdown"]
    assert payload["walk_forward_report"]["ready"] is True
    assert payload["walk_forward_report"]["fold_count"] >= 3
    assert payload["walk_forward_report"]["positive_fold_rate"] >= 0.67
    assert payload["walk_forward_report"]["coverage"]["asset_count"] >= 3
    assert payload["walk_forward_report"]["coverage"]["market_regime_count"] >= 3
    assert payload["overfit_guard"]["status"] == "ok"
    overfit_checks = {
        check["name"]: check["passed"]
        for check in payload["overfit_guard"]["checks"]
    }
    for check_name in MVP_CONTRACT["performance_fixture"][
        "required_overfit_guard_checks"
    ]:
        assert overfit_checks[check_name] is True
    assert (
        payload["overfit_guard"]["deflated_sharpe_proxy"]["schema_version"]
        == MVP_CONTRACT["performance_fixture"]["deflated_sharpe_proxy_schema"]
    )
    assert payload["overfit_guard"]["deflated_sharpe_proxy"]["status"] == "ok"
    assert (
        payload["overfit_guard"]["deflated_sharpe_proxy"][
            "exact_deflated_sharpe_ratio"
        ]
        is False
    )
    assert (
        payload["overfit_guard"]["deflated_sharpe_proxy"]["deflated_sharpe_proxy"]
        > 0
    )
    assert (
        payload["overfit_guard"]["deflated_sharpe_proxy"]["promotion_allowed"]
        is False
    )
    assert payload["overfit_guard"]["auto_promotion_allowed"] is False
    assert payload["overfit_guard"]["approval_required"] is True


def test_score_performance_supports_extended_fixture_window() -> None:
    payload = evaluate_score_performance(
        days=MVP_CONTRACT["performance_fixture"]["extended_window_days"]
    )

    assert (
        payload["sample_size"]
        >= MVP_CONTRACT["performance_fixture"]["minimum_extended_sample_size"]
    )
    assert payload["evaluation_window"]["requested_days"] == 180
    assert payload["evaluation_window"]["sample_source"] == "fixture_replay"
    assert payload["evaluation_window"]["requested_window_supported"] is True
    assert payload["evaluation_window"]["live_data_required"] is False
    assert payload["evaluation_window"]["repository_required"] is False
    assert payload["evaluation_window"]["network_call"] is False
    assert (
        180
        in payload["evaluation_window"]["supported_fixture_windows_days"]
    )
    assert payload["out_of_sample_report"]["ready"] is True
    assert payload["walk_forward_report"]["ready"] is True
    assert payload["walk_forward_report"]["fold_count"] >= 5
    assert payload["overfit_guard"]["status"] == "ok"
    assert (
        payload["overfit_guard"]["deflated_sharpe_proxy"]["sample_size"]
        == payload["sample_size"]
    )


def test_score_performance_marks_unsupported_long_fixture_window() -> None:
    payload = evaluate_score_performance(
        days=MVP_CONTRACT["performance_fixture"]["unsupported_window_days"]
    )
    window = payload["evaluation_window"]

    assert window["requested_days"] == 365
    assert window["sample_source"] == "fixture_replay"
    assert window["requested_window_supported"] is False
    assert window["coverage_status"] == "unsupported_requested_window"
    assert window["unsupported_reason"] == "requested_days_exceed_fixture_coverage"
    assert window["requested_window_coverage_ratio"] < window[
        "minimum_supported_coverage_ratio"
    ]
    assert window["requested_window_gap_days"] > 0
    assert (
        window["available_fixture_window_days"]
        == window["sample_age_range_days_ago"]["oldest"]
    )
    assert 365 not in window["supported_fixture_windows_days"]
    assert window["live_data_required"] is False
    assert window["repository_required"] is False
    assert window["network_call"] is False


def test_score_performance_treats_empty_provided_signals_as_empty_sample() -> None:
    payload = evaluate_score_performance(signals=[], days=90)
    window = payload["evaluation_window"]

    assert payload["sample_size"] == 0
    assert payload["avg_realized_r"] == 0.0
    assert window["sample_source"] == "provided_signals"
    assert window["fixture_replay_default"] is False
    assert window["coverage_status"] == "provided_signals_not_fixture_windowed"
    assert window["requested_window_supported"] is None
    assert payload["score_calibration"]["available"] is False
    assert payload["component_attribution"]["available"] is False
    assert payload["ablation_report"]["available"] is False
    assert payload["out_of_sample_report"]["ready"] is False
    assert payload["walk_forward_report"]["ready"] is False
    assert payload["overfit_guard"]["status"] == "watch"


@pytest.mark.parametrize(
    ("signals", "message"),
    [
        ("bad", "signals must be a list of objects"),
        ([1], "signals items must be objects"),
        (
            [{"outcome": "TAKE_PROFIT_FIRST", "realized_r": 0.5}],
            "signals.final_score must be a finite number",
        ),
        (
            [
                {
                    "final_score": True,
                    "outcome": "TAKE_PROFIT_FIRST",
                    "realized_r": 0.5,
                }
            ],
            "signals.final_score must be a finite number",
        ),
        (
            [
                {
                    "final_score": 1.5,
                    "outcome": "TAKE_PROFIT_FIRST",
                    "realized_r": 0.5,
                }
            ],
            "signals.final_score must be between 0 and 1",
        ),
        (
            [{"final_score": 0.6, "outcome": "", "realized_r": 0.5}],
            "signals.outcome must be a nonempty string",
        ),
        (
            [
                {
                    "final_score": 0.6,
                    "outcome": "TAKE_PROFIT_FIRST",
                    "realized_r": float("nan"),
                }
            ],
            "signals.realized_r must be a finite number",
        ),
        (
            [
                {
                    "final_score": 0.6,
                    "outcome": "TAKE_PROFIT_FIRST",
                    "realized_r": 0.5,
                    "age_days_ago": -1,
                }
            ],
            "signals.age_days_ago must be a nonnegative integer",
        ),
        (
            [
                {
                    "final_score": 0.6,
                    "outcome": "TAKE_PROFIT_FIRST",
                    "realized_r": 0.5,
                    "component_scores": [],
                }
            ],
            "signals.component_scores must be an object",
        ),
        (
            [
                {
                    "final_score": 0.6,
                    "outcome": "TAKE_PROFIT_FIRST",
                    "realized_r": 0.5,
                    "component_scores": {"trend": "high"},
                }
            ],
            "signals.component_scores values must be a finite number",
        ),
    ],
)
def test_score_performance_rejects_invalid_provided_signals(signals, message) -> None:
    with pytest.raises(ValueError, match=message):
        evaluate_score_performance(signals=signals)


@pytest.mark.parametrize(
    ("signals", "expected_error"),
    [
        ("bad", "signals must be a list of objects"),
        ([1], "signals items must be objects"),
        (
            [{"outcome": "TAKE_PROFIT_FIRST", "realized_r": 0.5}],
            "signals.final_score must be a finite number",
        ),
        (
            [{"final_score": 1.5, "outcome": "TAKE_PROFIT_FIRST", "realized_r": 0.5}],
            "signals.final_score must be between 0 and 1",
        ),
        (
            [{"final_score": 0.6, "outcome": "", "realized_r": 0.5}],
            "signals.outcome must be a nonempty string",
        ),
        (
            [
                {
                    "final_score": 0.6,
                    "outcome": "TAKE_PROFIT_FIRST",
                    "realized_r": 0.5,
                    "component_scores": [],
                }
            ],
            "signals.component_scores must be an object",
        ),
    ],
)
def test_harness_rejects_invalid_score_performance_signals_with_failure_audit(
    tmp_path: Path,
    signals: object,
    expected_error: str,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    input_payload = {"signals": signals}
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

    assert result.returncode != 0
    assert result.stdout == ""
    assert expected_error in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "evaluate_score_performance"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert expected_error in event["details"]["error"]


@pytest.mark.parametrize(
    ("signals", "expected_error"),
    [
        (
            [
                {
                    "final_score": True,
                    "outcome": "TAKE_PROFIT_FIRST",
                    "realized_r": 0.5,
                }
            ],
            "signals.final_score must be a finite number",
        ),
        (
            [
                {
                    "final_score": 0.6,
                    "outcome": "TAKE_PROFIT_FIRST",
                    "realized_r": float("inf"),
                }
            ],
            "signals.realized_r must be a finite number",
        ),
        (
            [
                {
                    "final_score": 0.6,
                    "outcome": "TAKE_PROFIT_FIRST",
                    "realized_r": 0.5,
                    "age_days_ago": -1,
                }
            ],
            "signals.age_days_ago must be a nonnegative integer",
        ),
        (
            [
                {
                    "final_score": 0.6,
                    "outcome": "TAKE_PROFIT_FIRST",
                    "realized_r": 0.5,
                    "component_scores": {"trend": "high"},
                }
            ],
            "signals.component_scores values must be a finite number",
        ),
    ],
)
def test_harness_rejects_remaining_score_performance_signals_with_failure_audit(
    tmp_path: Path,
    signals: object,
    expected_error: str,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    input_payload = {"signals": signals}
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

    assert result.returncode != 0
    assert result.stdout == ""
    assert expected_error in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "evaluate_score_performance"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert expected_error in event["details"]["error"]


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


def test_harness_rejects_blank_indicator_symbol_with_failure_audit(
    tmp_path: Path,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    input_payload = {"symbol": "   "}
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "calculate_indicators",
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

    assert result.returncode != 0
    assert result.stdout == ""
    assert "symbol must be a nonempty string" in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "calculate_indicators"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "symbol must be a nonempty string" in event["details"]["error"]


def test_harness_rejects_invalid_market_symbols_container_with_failure_audit(
    tmp_path: Path,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    input_payload = {"symbols": "QQQ"}
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "get_market_snapshot",
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

    assert result.returncode != 0
    assert result.stdout == ""
    assert "symbols must be a list of nonempty strings" in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "get_market_snapshot"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "symbols must be a list of nonempty strings" in event["details"]["error"]


def test_harness_rejects_indicator_symbol_control_character_with_failure_audit(
    tmp_path: Path,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    input_payload = {"symbol": "QQQ\n"}
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "calculate_indicators",
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

    assert result.returncode != 0
    assert result.stdout == ""
    assert "symbol must not contain control characters" in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "calculate_indicators"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "symbol must not contain control characters" in event["details"]["error"]


def test_harness_rejects_invalid_render_chart_output_dir_with_failure_audit(
    tmp_path: Path,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    input_payload = {"symbol": "QQQ", "output_dir": "   "}
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "render_chart",
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

    assert result.returncode != 0
    assert result.stdout == ""
    assert "output_dir must be a nonempty string" in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "render_chart"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "output_dir must be a nonempty string" in event["details"]["error"]


def test_harness_rejects_render_chart_output_dir_control_character_with_failure_audit(
    tmp_path: Path,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    chart_dir = tmp_path / "charts"
    input_payload = {"symbol": "QQQ", "output_dir": f"{chart_dir}\n"}
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "render_chart",
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

    assert result.returncode != 0
    assert result.stdout == ""
    assert "output_dir must not contain control characters" in result.stderr
    assert not chart_dir.exists()
    assert event["actor"] == "harness"
    assert event["resource_id"] == "render_chart"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "output_dir must not contain control characters" in event["details"]["error"]


def test_harness_rejects_invalid_document_summary_input_with_failure_audit(
    tmp_path: Path,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    input_payload = {
        "summary": "   ",
        "artifact_ref": "artifact://documents/fomc-minutes-summary.pdf",
    }
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

    assert result.returncode != 0
    assert result.stdout == ""
    assert "summary must be a nonempty string" in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "create_document_evidence_card"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "summary must be a nonempty string" in event["details"]["error"]


def test_harness_rejects_document_summary_control_character_with_failure_audit(
    tmp_path: Path,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    input_payload = {
        "summary": "FOMC minutes summary\ncontains injected control text.",
        "artifact_ref": "artifact://documents/fomc-minutes-summary.pdf",
    }
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

    assert result.returncode != 0
    assert result.stdout == ""
    assert "summary must not contain control characters" in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "create_document_evidence_card"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "summary must not contain control characters" in event["details"]["error"]


def test_harness_rejects_invalid_event_calendar_days_with_failure_audit(
    tmp_path: Path,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    input_payload = {"days": 0}
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "get_event_calendar",
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

    assert result.returncode != 0
    assert result.stdout == ""
    assert "days must be a positive integer" in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "get_event_calendar"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "days must be a positive integer" in event["details"]["error"]


def test_harness_rejects_blank_news_topic_with_failure_audit(
    tmp_path: Path,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    input_payload = {"topic": "   "}
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "get_news_bundle",
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

    assert result.returncode != 0
    assert result.stdout == ""
    assert "topic must be a nonempty string" in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "get_news_bundle"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "topic must be a nonempty string" in event["details"]["error"]


def test_harness_rejects_news_topic_control_character_with_failure_audit(
    tmp_path: Path,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    input_payload = {"topic": "all\n"}
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "get_news_bundle",
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

    assert result.returncode != 0
    assert result.stdout == ""
    assert "topic must not contain control characters" in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "get_news_bundle"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "topic must not contain control characters" in event["details"]["error"]


def test_harness_rejects_invalid_label_price_path_with_failure_audit(
    tmp_path: Path,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    input_payload = {"price_path": ["not-a-price"]}
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "label_signal_outcome",
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

    assert result.returncode != 0
    assert result.stdout == ""
    assert "price_path must be a list of positive finite numbers" in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "label_signal_outcome"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert (
        "price_path must be a list of positive finite numbers"
        in event["details"]["error"]
    )


def test_harness_rejects_label_price_path_type_with_failure_audit(
    tmp_path: Path,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    input_payload = {"price_path": "not-a-list"}
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "label_signal_outcome",
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

    assert result.returncode != 0
    assert result.stdout == ""
    assert "price_path must be a list of positive finite numbers" in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "label_signal_outcome"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert (
        "price_path must be a list of positive finite numbers"
        in event["details"]["error"]
    )


def test_harness_rejects_label_price_path_nonpositive_with_failure_audit(
    tmp_path: Path,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    input_payload = {"price_path": [100, 0]}
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "label_signal_outcome",
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

    assert result.returncode != 0
    assert result.stdout == ""
    assert "price_path must be a list of positive finite numbers" in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "label_signal_outcome"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert (
        "price_path must be a list of positive finite numbers"
        in event["details"]["error"]
    )


def test_harness_rejects_label_price_path_nonfinite_with_failure_audit(
    tmp_path: Path,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    input_json = '{"price_path":[100,1e999]}'
    expected_input_payload = {"price_path": [100, float("inf")]}
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "label_signal_outcome",
            "--input-json",
            input_json,
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

    assert result.returncode != 0
    assert result.stdout == ""
    assert "price_path must be a list of positive finite numbers" in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "label_signal_outcome"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == expected_input_payload
    assert "output_summary" not in event["details"]
    assert (
        "price_path must be a list of positive finite numbers"
        in event["details"]["error"]
    )


def test_harness_rejects_invalid_label_stop_loss_with_failure_audit(
    tmp_path: Path,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    input_payload = {"stop_loss_pct": 0}
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "label_signal_outcome",
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

    assert result.returncode != 0
    assert result.stdout == ""
    assert "stop_loss_pct must be a positive finite number" in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "label_signal_outcome"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "stop_loss_pct must be a positive finite number" in event["details"][
        "error"
    ]


def test_harness_rejects_label_stop_loss_type_with_failure_audit(
    tmp_path: Path,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    input_payload = {"stop_loss_pct": "0.05"}
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "label_signal_outcome",
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

    assert result.returncode != 0
    assert result.stdout == ""
    assert "stop_loss_pct must be a positive finite number" in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "label_signal_outcome"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "stop_loss_pct must be a positive finite number" in event["details"][
        "error"
    ]


def test_harness_rejects_label_stop_loss_nonfinite_with_failure_audit(
    tmp_path: Path,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    input_json = '{"stop_loss_pct":1e999}'
    expected_input_payload = {"stop_loss_pct": float("inf")}
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "label_signal_outcome",
            "--input-json",
            input_json,
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

    assert result.returncode != 0
    assert result.stdout == ""
    assert "stop_loss_pct must be a positive finite number" in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "label_signal_outcome"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == expected_input_payload
    assert "output_summary" not in event["details"]
    assert "stop_loss_pct must be a positive finite number" in event["details"][
        "error"
    ]


def test_harness_rejects_invalid_label_take_profit_with_failure_audit(
    tmp_path: Path,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    input_payload = {"take_profit_pct": "0.10"}
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "label_signal_outcome",
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

    assert result.returncode != 0
    assert result.stdout == ""
    assert "take_profit_pct must be a positive finite number" in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "label_signal_outcome"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "take_profit_pct must be a positive finite number" in event["details"][
        "error"
    ]


def test_harness_rejects_label_take_profit_nonpositive_with_failure_audit(
    tmp_path: Path,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    input_payload = {"take_profit_pct": 0}
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "label_signal_outcome",
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

    assert result.returncode != 0
    assert result.stdout == ""
    assert "take_profit_pct must be a positive finite number" in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "label_signal_outcome"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "take_profit_pct must be a positive finite number" in event["details"][
        "error"
    ]


def test_harness_rejects_label_take_profit_nonfinite_with_failure_audit(
    tmp_path: Path,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    input_json = '{"take_profit_pct":1e999}'
    expected_input_payload = {"take_profit_pct": float("inf")}
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "label_signal_outcome",
            "--input-json",
            input_json,
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

    assert result.returncode != 0
    assert result.stdout == ""
    assert "take_profit_pct must be a positive finite number" in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "label_signal_outcome"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == expected_input_payload
    assert "output_summary" not in event["details"]
    assert "take_profit_pct must be a positive finite number" in event["details"][
        "error"
    ]


def test_harness_rejects_invalid_label_time_barrier_with_failure_audit(
    tmp_path: Path,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    input_payload = {"time_barrier_days": True}
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "label_signal_outcome",
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

    assert result.returncode != 0
    assert result.stdout == ""
    assert "time_barrier_days must be a positive integer" in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "label_signal_outcome"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "time_barrier_days must be a positive integer" in event["details"]["error"]


def test_harness_rejects_label_time_barrier_nonpositive_with_failure_audit(
    tmp_path: Path,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    input_payload = {"time_barrier_days": 0}
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "label_signal_outcome",
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

    assert result.returncode != 0
    assert result.stdout == ""
    assert "time_barrier_days must be a positive integer" in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "label_signal_outcome"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "time_barrier_days must be a positive integer" in event["details"]["error"]


def test_harness_rejects_label_time_barrier_type_with_failure_audit(
    tmp_path: Path,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    input_payload = {"time_barrier_days": "2"}
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "label_signal_outcome",
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

    assert result.returncode != 0
    assert result.stdout == ""
    assert "time_barrier_days must be a positive integer" in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "label_signal_outcome"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "time_barrier_days must be a positive integer" in event["details"]["error"]


def test_harness_rejects_invalid_label_signal_id_with_failure_audit(
    tmp_path: Path,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    input_payload = {"signal_id": "   "}
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "label_signal_outcome",
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

    assert result.returncode != 0
    assert result.stdout == ""
    assert "signal_id must be a nonempty string" in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "label_signal_outcome"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "signal_id must be a nonempty string" in event["details"]["error"]


def test_harness_rejects_label_signal_id_type_with_failure_audit(
    tmp_path: Path,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    input_payload = {"signal_id": 123}
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "label_signal_outcome",
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

    assert result.returncode != 0
    assert result.stdout == ""
    assert "signal_id must be a nonempty string" in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "label_signal_outcome"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "signal_id must be a nonempty string" in event["details"]["error"]


def test_harness_rejects_invalid_record_signal_with_failure_audit(
    tmp_path: Path,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    input_payload = {"signal": {"signal_id": "   "}}
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "record_signal",
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

    assert result.returncode != 0
    assert result.stdout == ""
    assert "signal.signal_id must be a nonempty string" in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "record_signal"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "signal.signal_id must be a nonempty string" in event["details"]["error"]


def test_harness_rejects_record_signal_run_id_type_with_failure_audit(
    tmp_path: Path,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    signal = score_leverage_swing("TQQQ")
    input_payload = {"signal": {**signal, "run_id": 123}}
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "record_signal",
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

    assert result.returncode != 0
    assert result.stdout == ""
    assert "signal.run_id must be a nonempty string" in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "record_signal"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "signal.run_id must be a nonempty string" in event["details"]["error"]


def test_harness_rejects_record_signal_created_at_blank_with_failure_audit(
    tmp_path: Path,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    signal = score_leverage_swing("TQQQ")
    input_payload = {"signal": {**signal, "created_at": ""}}
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "record_signal",
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

    assert result.returncode != 0
    assert result.stdout == ""
    assert "signal.created_at must be a nonempty string" in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "record_signal"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "signal.created_at must be a nonempty string" in event["details"]["error"]


def test_harness_rejects_record_signal_underlying_null_with_failure_audit(
    tmp_path: Path,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    signal = score_leverage_swing("TQQQ")
    input_payload = {"signal": {**signal, "underlying": None}}
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "record_signal",
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

    assert result.returncode != 0
    assert result.stdout == ""
    assert "signal.underlying must be a nonempty string" in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "record_signal"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "signal.underlying must be a nonempty string" in event["details"]["error"]


def test_harness_rejects_record_signal_config_version_blank_with_failure_audit(
    tmp_path: Path,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    signal = score_leverage_swing("TQQQ")
    input_payload = {"signal": {**signal, "config_version": "   "}}
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "record_signal",
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

    assert result.returncode != 0
    assert result.stdout == ""
    assert "signal.config_version must be a nonempty string" in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "record_signal"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "signal.config_version must be a nonempty string" in event["details"][
        "error"
    ]


def test_harness_rejects_record_signal_config_version_control_character_with_failure_audit(
    tmp_path: Path,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    signal = score_leverage_swing("TQQQ")
    input_payload = {
        "signal": {**signal, "config_version": f"{signal['config_version']}\n"}
    }
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "record_signal",
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

    assert result.returncode != 0
    assert result.stdout == ""
    assert "signal.config_version must not contain control characters" in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "record_signal"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "signal.config_version must not contain control characters" in event[
        "details"
    ]["error"]


def test_harness_rejects_record_signal_config_hash_type_with_failure_audit(
    tmp_path: Path,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    signal = score_leverage_swing("TQQQ")
    input_payload = {"signal": {**signal, "config_hash": False}}
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "record_signal",
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

    assert result.returncode != 0
    assert result.stdout == ""
    assert "signal.config_hash must be a nonempty string" in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "record_signal"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "signal.config_hash must be a nonempty string" in event["details"]["error"]


def test_harness_rejects_record_signal_config_hash_control_character_with_failure_audit(
    tmp_path: Path,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    signal = score_leverage_swing("TQQQ")
    input_payload = {"signal": {**signal, "config_hash": f"{signal['config_hash']}\n"}}
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "record_signal",
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

    assert result.returncode != 0
    assert result.stdout == ""
    assert "signal.config_hash must not contain control characters" in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "record_signal"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "signal.config_hash must not contain control characters" in event["details"][
        "error"
    ]


@pytest.mark.parametrize(
    ("field_name", "invalid_value", "expected_error"),
    [
        (
            "run_id",
            "run_fixture\n",
            "signal.run_id must not contain control characters",
        ),
        (
            "created_at",
            "2026-05-10T00:00:00Z\n",
            "signal.created_at must not contain control characters",
        ),
        (
            "underlying",
            "QQQ\n",
            "signal.underlying must not contain control characters",
        ),
    ],
)
def test_harness_rejects_record_signal_remaining_identity_control_characters_with_failure_audit(
    field_name: str,
    invalid_value: str,
    expected_error: str,
    tmp_path: Path,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    signal = score_leverage_swing("TQQQ")
    input_payload = {"signal": {**signal, field_name: invalid_value}}
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "record_signal",
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

    assert result.returncode != 0
    assert result.stdout == ""
    assert expected_error in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "record_signal"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert expected_error in event["details"]["error"]


def test_harness_rejects_record_signal_object_type_with_failure_audit(
    tmp_path: Path,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    input_payload = {"signal": "not-a-signal"}
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "record_signal",
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

    assert result.returncode != 0
    assert result.stdout == ""
    assert "signal must be an object" in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "record_signal"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "signal must be an object" in event["details"]["error"]


def test_harness_rejects_record_signal_identity_control_character_with_failure_audit(
    tmp_path: Path,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    ledger_path = tmp_path / "signal_ledger.jsonl"
    input_payload = {"signal": {"signal_id": "sig_fixture\n"}}
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "record_signal",
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

    assert result.returncode != 0
    assert result.stdout == ""
    assert "signal.signal_id must not contain control characters" in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "record_signal"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "signal.signal_id must not contain control characters" in event["details"][
        "error"
    ]
    assert not ledger_path.exists()


def test_harness_rejects_invalid_record_signal_ledger_path_with_failure_audit(
    tmp_path: Path,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    input_payload = {"ledger_path": "   "}
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "record_signal",
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

    assert result.returncode != 0
    assert result.stdout == ""
    assert "ledger_path must be a nonempty string" in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "record_signal"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "ledger_path must be a nonempty string" in event["details"]["error"]


def test_harness_rejects_record_signal_ledger_path_type_with_failure_audit(
    tmp_path: Path,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    input_payload = {"ledger_path": False}
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "record_signal",
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

    assert result.returncode != 0
    assert result.stdout == ""
    assert "ledger_path must be a nonempty string" in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "record_signal"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "ledger_path must be a nonempty string" in event["details"]["error"]


def test_harness_rejects_record_signal_ledger_path_control_character_with_failure_audit(
    tmp_path: Path,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    ledger_path = tmp_path / "signal_ledger.jsonl"
    input_payload = {"ledger_path": f"{ledger_path}\n"}
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "record_signal",
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

    assert result.returncode != 0
    assert result.stdout == ""
    assert "ledger_path must not contain control characters" in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "record_signal"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "ledger_path must not contain control characters" in event["details"][
        "error"
    ]
    assert not ledger_path.exists()


def test_harness_rejects_invalid_label_signal_ledger_path_with_failure_audit(
    tmp_path: Path,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    input_payload = {"ledger_path": "   "}
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "label_signal_outcome",
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

    assert result.returncode != 0
    assert result.stdout == ""
    assert "ledger_path must be a nonempty string" in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "label_signal_outcome"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "ledger_path must be a nonempty string" in event["details"]["error"]


def test_harness_rejects_label_signal_ledger_path_type_with_failure_audit(
    tmp_path: Path,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    input_payload = {"ledger_path": False}
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "label_signal_outcome",
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

    assert result.returncode != 0
    assert result.stdout == ""
    assert "ledger_path must be a nonempty string" in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "label_signal_outcome"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "ledger_path must be a nonempty string" in event["details"]["error"]


def test_harness_rejects_label_signal_ledger_path_control_character_with_failure_audit(
    tmp_path: Path,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    ledger_path = tmp_path / "signal_ledger.jsonl"
    input_payload = {"ledger_path": f"{ledger_path}\n"}
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "label_signal_outcome",
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

    assert result.returncode != 0
    assert result.stdout == ""
    assert "ledger_path must not contain control characters" in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "label_signal_outcome"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "ledger_path must not contain control characters" in event["details"][
        "error"
    ]
    assert not ledger_path.exists()


def test_harness_rejects_label_signal_identity_control_character_with_failure_audit(
    tmp_path: Path,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    input_payload = {"signal_id": "sig_fixture\n"}
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "label_signal_outcome",
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

    assert result.returncode != 0
    assert result.stdout == ""
    assert "signal_id must not contain control characters" in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "label_signal_outcome"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "signal_id must not contain control characters" in event["details"]["error"]


def test_harness_rejects_invalid_label_event_boolean_with_failure_audit(
    tmp_path: Path,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    input_payload = {"invalidated_by_event": "true"}
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "label_signal_outcome",
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

    assert result.returncode != 0
    assert result.stdout == ""
    assert "invalidated_by_event must be a boolean" in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "label_signal_outcome"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "invalidated_by_event must be a boolean" in event["details"]["error"]


def test_harness_rejects_blank_label_invalidating_event_id_with_failure_audit(
    tmp_path: Path,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    input_payload = {
        "invalidated_by_event": True,
        "invalidating_event_id": "   ",
    }
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "label_signal_outcome",
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

    assert result.returncode != 0
    assert result.stdout == ""
    assert "invalidating_event_id must be a nonempty string" in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "label_signal_outcome"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "invalidating_event_id must be a nonempty string" in event["details"][
        "error"
    ]


def test_harness_rejects_label_invalidating_event_id_type_with_failure_audit(
    tmp_path: Path,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    input_payload = {
        "invalidated_by_event": True,
        "invalidating_event_id": 123,
    }
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "label_signal_outcome",
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

    assert result.returncode != 0
    assert result.stdout == ""
    assert "invalidating_event_id must be a nonempty string" in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "label_signal_outcome"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "invalidating_event_id must be a nonempty string" in event["details"][
        "error"
    ]


def test_harness_rejects_label_invalidating_event_id_control_character_with_failure_audit(
    tmp_path: Path,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    input_payload = {
        "invalidated_by_event": True,
        "invalidating_event_id": "event_cpi\n",
    }
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "label_signal_outcome",
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

    assert result.returncode != 0
    assert result.stdout == ""
    assert "invalidating_event_id must not contain control characters" in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "label_signal_outcome"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "invalidating_event_id must not contain control characters" in event[
        "details"
    ]["error"]


def test_harness_rejects_label_unused_invalidating_event_id_control_character_with_failure_audit(
    tmp_path: Path,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    input_payload = {
        "invalidated_by_event": False,
        "invalidating_event_id": "event_cpi\n",
    }
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "label_signal_outcome",
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

    assert result.returncode != 0
    assert result.stdout == ""
    assert "invalidating_event_id must not contain control characters" in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "label_signal_outcome"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "invalidating_event_id must not contain control characters" in event[
        "details"
    ]["error"]


def test_harness_rejects_invalid_score_performance_days_with_failure_audit(
    tmp_path: Path,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    input_payload = {"days": 0}
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

    assert result.returncode != 0
    assert result.stdout == ""
    assert "days must be a positive integer" in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "evaluate_score_performance"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "days must be a positive integer" in event["details"]["error"]


@pytest.mark.parametrize("days", [True, -1, "90"])
def test_harness_rejects_score_performance_remaining_days_values_with_failure_audit(
    tmp_path: Path,
    days: object,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    input_payload = {"days": days}
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

    assert result.returncode != 0
    assert result.stdout == ""
    assert "days must be a positive integer" in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "evaluate_score_performance"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "days must be a positive integer" in event["details"]["error"]


def test_harness_rejects_invalid_score_performance_ledger_path_with_failure_audit(
    tmp_path: Path,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    input_payload = {"ledger_path": "   "}
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

    assert result.returncode != 0
    assert result.stdout == ""
    assert "ledger_path must be a nonempty string" in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "evaluate_score_performance"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "ledger_path must be a nonempty string" in event["details"]["error"]


def test_harness_rejects_score_performance_ledger_path_type_with_failure_audit(
    tmp_path: Path,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    input_payload = {"ledger_path": []}
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

    assert result.returncode != 0
    assert result.stdout == ""
    assert "ledger_path must be a nonempty string" in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "evaluate_score_performance"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "ledger_path must be a nonempty string" in event["details"]["error"]


def test_harness_rejects_score_performance_ledger_path_control_character_with_failure_audit(
    tmp_path: Path,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    ledger_path = tmp_path / "signal_ledger.jsonl"
    input_payload = {"ledger_path": f"{ledger_path}\n"}
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

    assert result.returncode != 0
    assert result.stdout == ""
    assert "ledger_path must not contain control characters" in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "evaluate_score_performance"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "ledger_path must not contain control characters" in event["details"][
        "error"
    ]
    assert not ledger_path.exists()


def test_harness_rejects_invalid_position_numeric_input_with_failure_audit(
    tmp_path: Path,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    input_payload = {"asset": "TQQQ", "entry_price": 100, "current_price": 0}
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "evaluate_position",
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

    assert result.returncode != 0
    assert result.stdout == ""
    assert "current_price must be a positive finite number" in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "evaluate_position"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert (
        "current_price must be a positive finite number"
        in event["details"]["error"]
    )


@pytest.mark.parametrize(
    ("input_payload", "expected_error"),
    [
        (
            {"asset": "TQQQ", "entry_price": 0},
            "entry_price must be a positive finite number",
        ),
        (
            {"asset": "TQQQ", "entry_price": False},
            "entry_price must be a positive finite number",
        ),
        (
            {"asset": "TQQQ", "current_price": False},
            "current_price must be a positive finite number",
        ),
        (
            {"asset": "TQQQ", "size": "3"},
            "size must be a positive finite number",
        ),
        (
            {"asset": "TQQQ", "size": -1},
            "size must be a positive finite number",
        ),
    ],
)
def test_harness_rejects_remaining_position_numeric_inputs_with_failure_audit(
    tmp_path: Path,
    input_payload: dict[str, object],
    expected_error: str,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "evaluate_position",
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

    assert result.returncode != 0
    assert result.stdout == ""
    assert expected_error in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "evaluate_position"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert expected_error in event["details"]["error"]


def test_harness_rejects_blank_scoring_asset_with_failure_audit(
    tmp_path: Path,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    input_payload = {"asset": "   "}
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

    assert result.returncode != 0
    assert result.stdout == ""
    assert "asset must be a nonempty string" in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "score_leverage_swing"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "asset must be a nonempty string" in event["details"]["error"]


@pytest.mark.parametrize(
    ("tool_name", "input_payload", "expected_error"),
    [
        (
            "score_leverage_swing",
            {"asset": 123},
            "asset must be a nonempty string",
        ),
        (
            "score_leverage_swing",
            {"asset": "TQQQ", "timeframe": None},
            "timeframe must be a nonempty string",
        ),
        (
            "generate_trade_guide",
            {"asset": "TQQQ", "timeframe": []},
            "timeframe must be a nonempty string",
        ),
        (
            "generate_trade_guide",
            {"asset": None},
            "asset must be a nonempty string",
        ),
        (
            "evaluate_position",
            {"asset": False},
            "asset must be a nonempty string",
        ),
    ],
)
def test_harness_rejects_scoring_tool_identity_types_with_failure_audit(
    tmp_path: Path,
    tool_name: str,
    input_payload: dict[str, object],
    expected_error: str,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            tool_name,
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

    assert result.returncode != 0
    assert result.stdout == ""
    assert expected_error in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == tool_name
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert expected_error in event["details"]["error"]


def test_harness_rejects_scoring_asset_control_character_with_failure_audit(
    tmp_path: Path,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    input_payload = {"asset": "TQQQ\n"}
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

    assert result.returncode != 0
    assert result.stdout == ""
    assert "asset must not contain control characters" in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "score_leverage_swing"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "asset must not contain control characters" in event["details"]["error"]


@pytest.mark.parametrize(
    ("tool_name", "input_payload", "expected_error"),
    [
        (
            "score_leverage_swing",
            {"asset": "TQQQ", "timeframe": "swing_3d_10d\n"},
            "timeframe must not contain control characters",
        ),
        (
            "generate_trade_guide",
            {"asset": "TQQQ\n"},
            "asset must not contain control characters",
        ),
        (
            "evaluate_position",
            {"asset": "TQQQ\n"},
            "asset must not contain control characters",
        ),
    ],
)
def test_harness_rejects_remaining_scoring_identity_control_characters_with_failure_audit(
    tmp_path: Path,
    tool_name: str,
    input_payload: dict[str, object],
    expected_error: str,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            tool_name,
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

    assert result.returncode != 0
    assert result.stdout == ""
    assert expected_error in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == tool_name
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert expected_error in event["details"]["error"]


def test_harness_rejects_trade_guide_timeframe_control_character_with_failure_audit(
    tmp_path: Path,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    input_payload = {"asset": "TQQQ", "timeframe": "swing_3d_10d\n"}
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "generate_trade_guide",
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

    assert result.returncode != 0
    assert result.stdout == ""
    assert "timeframe must not contain control characters" in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "generate_trade_guide"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "timeframe must not contain control characters" in event["details"]["error"]


def test_server_tool_wrappers_execute(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("HALO_SWING_AUDIT_LOG_PATH", str(tmp_path / "audit.jsonl"))
    from halo_swing_mcp import server

    assert server.get_market_snapshot()["snapshots"]
    assert server.calculate_indicators("QQQ")["indicator_symbol"] == "QQQ"
    assert server.score_leverage_swing("TQQQ")["asset"] == "TQQQ"
    assert server.generate_trade_guide("TQQQ")["guide"]["stop_conditions"]
    assert server.evaluate_score_performance(days=90)["out_of_sample_report"]["ready"]
