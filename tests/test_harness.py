import json

import pytest

from halo_swing_mcp import harness


def test_harness_summary_only_flag_maps_api_key_pipeline(capsys) -> None:
    exit_code = harness.main(
        [
            "run_api_key_pipeline_smoke",
            "--input-json",
            (
                '{"asset":"TQQQ","timeframe":"swing_3d_10d",'
                '"symbols":["QQQ"],"topic":"macro"}'
            ),
            "--summary-only",
            "--no-audit",
        ]
    )

    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["schema_version"] == "api_key_pipeline_smoke_summary_only.v1"
    assert payload["summary_only"] is True
    assert payload["secret_values_returned"] is False
    assert "live_data_smoke_summary" not in payload


def test_harness_summary_only_flag_uses_api_key_pipeline_defaults(capsys) -> None:
    exit_code = harness.main(
        [
            "run_api_key_pipeline_smoke",
            "--summary-only",
            "--no-audit",
        ]
    )

    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["schema_version"] == "api_key_pipeline_smoke_summary_only.v1"
    assert payload["input"] == {
        "asset": "TQQQ",
        "timeframe": "swing_3d_10d",
        "symbols": ["QQQ"],
        "topic": "macro",
        "summary_only": True,
    }
    assert payload["summary_only"] is True
    assert payload["secret_values_returned"] is False


def test_harness_summary_only_flag_rejects_other_commands() -> None:
    with pytest.raises(
        ValueError,
        match="summary-only is only supported for run_api_key_pipeline_smoke",
    ):
        harness.main(["health_check", "--summary-only", "--no-audit"])
