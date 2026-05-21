import json
import subprocess
import sys
from pathlib import Path

import pytest
from pydantic import ValidationError

from halo_swing_mcp.audit import read_audit_events
from halo_swing_mcp.contracts import LatestSignalReport
from halo_swing_mcp.tools.market import (
    DOCUMENT_SUMMARY_MAX_CHARS,
    create_document_evidence_card,
)
from halo_swing_mcp.tools import reporting
from halo_swing_mcp.tools.recording import label_signal_outcome, record_signal
from halo_swing_mcp.tools.reporting import (
    generate_cron_prompt_pack,
    generate_latest_signal_report,
    generate_position_review_report,
)


ROOT = Path(__file__).resolve().parents[1]
GOLDEN_PATH = ROOT / "tests" / "golden" / "hermes_latest_signal_report.json"
DEGRADED_REPORT_PATH = ROOT / "tests" / "golden" / "latest_signal_report_degraded.json"
EXPECTED_DOCUMENT_EVIDENCE_CARD_KEYS = [
    "evidence_id",
    "category",
    "source",
    "modality",
    "observed_at",
    "asset_scope",
    "bias",
    "strength",
    "confidence",
    "summary",
    "summary_truncated",
    "buy_impact",
    "sell_impact",
    "invalidating_condition",
    "artifact_ref",
]
EXPECTED_MULTIMODAL_CONTEXT_IDENTITY_VALUES = {
    "schema_version": "multimodal_context.v1",
    "numeric_authority": "latest_signal_report",
    "hermes_multimodal_call": False,
    "network_call": False,
    "raw_artifacts_embedded": False,
}
EXPECTED_MULTIMODAL_ARTIFACT_REF_TYPES = ["CHART", "PDF"]


def expected_document_evidence_card_values(card: dict[str, object]) -> dict[str, object]:
    return {
        "evidence_id": card["evidence_id"],
        "modality_nonempty": True,
        "observed_at_nonempty": True,
        "asset_scope_uppercase": True,
        "strength_in_range": True,
        "confidence_in_range": True,
        "summary_nonempty": True,
        "summary_truncated_is_bool": True,
        "impacts_nonempty": True,
        "invalidating_condition_nonempty": True,
        "artifact_ref_portable": True,
    }


def expected_document_evidence_card_string_field_types(
    card: dict[str, object],
) -> dict[str, object]:
    return {
        "evidence_id": card["evidence_id"],
        "string_fields": [
            "category",
            "source",
            "modality",
            "observed_at",
            "bias",
            "summary",
            "buy_impact",
            "sell_impact",
            "invalidating_condition",
        ],
        "string_fields_are_strings": True,
    }


def expected_document_evidence_card_structural_field_types(
    card: dict[str, object],
) -> dict[str, object]:
    return {
        "evidence_id": card["evidence_id"],
        "asset_scope_is_list": True,
        "artifact_ref_is_dict": True,
    }


def expected_document_evidence_card_text_safety(
    card: dict[str, object],
) -> dict[str, object]:
    return {
        "evidence_id": card["evidence_id"],
        "text_fields": ["summary", "invalidating_condition"],
        "text_values_have_no_surrounding_whitespace": True,
        "text_values_have_no_control_characters": True,
    }


def expected_document_evidence_card_scalar_safety(
    card: dict[str, object],
) -> dict[str, object]:
    return {
        "evidence_id": card["evidence_id"],
        "scalar_fields": ["modality", "observed_at"],
        "scalar_values_have_no_surrounding_whitespace": True,
        "scalar_values_have_no_control_characters": True,
    }


def expected_document_evidence_card_modality(
    card: dict[str, object],
) -> dict[str, object]:
    return {
        "evidence_id": card["evidence_id"],
        "modality": "pdf_summary",
        "modality_supported": True,
    }


def expected_safe_evidence_id(evidence_id: object) -> dict[str, object]:
    return {
        "evidence_id": evidence_id,
        "pattern": "lowercase_ascii_underscore_identifier",
        "min_chars": 3,
        "max_chars": 64,
        "matches_safe_contract": True,
    }


def expected_document_evidence_card_safe_id(
    card: dict[str, object],
) -> dict[str, object]:
    return expected_safe_evidence_id(card["evidence_id"])


def expected_multimodal_evidence_id_types(
    evidence_card_ids: list[object],
    artifact_ref_evidence_ids: list[object],
) -> dict[str, object]:
    return {
        "evidence_card_ids": evidence_card_ids,
        "artifact_ref_evidence_ids": artifact_ref_evidence_ids,
        "evidence_card_ids_are_strings": True,
        "artifact_ref_evidence_ids_are_strings": True,
    }


def expected_document_evidence_card_artifact_uri(
    card: dict[str, object],
) -> dict[str, object]:
    return {
        "evidence_id": card["evidence_id"],
        "allowed_ref_prefixes": [
            "artifact://",
            "https://",
            "memory://",
            "urn:",
            "sha256:",
        ],
        "artifact_ref_uses_explicit_uri": True,
    }


def expected_document_pdf_artifact_ref_contract(
    card: dict[str, object],
) -> dict[str, object]:
    return {
        "evidence_id": card["evidence_id"],
        "ref_type": "PDF",
        "allowed_ref_suffixes": [".pdf"],
        "content_addressed_prefix": "sha256:",
        "ref_matches_pdf_contract": True,
    }


def expected_artifact_ref_type_canonical(
    evidence_id: str,
    ref_type: str,
) -> dict[str, object]:
    return {
        "evidence_id": evidence_id,
        "allowed_ref_types": EXPECTED_MULTIMODAL_ARTIFACT_REF_TYPES,
        "ref_type": ref_type,
        "ref_type_is_canonical_uppercase": True,
    }


def expected_chart_artifact_ref_metadata_value_types(
    evidence_id: str = "latest_signal_chart",
) -> dict[str, object]:
    return {
        "evidence_id": evidence_id,
        "ref_type": "CHART",
        "renderer_is_string": True,
        "bars_is_positive_int": True,
        "timeframe_supported_is_bool_true": True,
    }


def expected_document_pdf_artifact_ref_metadata_value_types(
    card: dict[str, object],
) -> dict[str, object]:
    return {
        "evidence_id": card["evidence_id"],
        "ref_type": "PDF",
        "description_is_string": True,
        "portable_is_bool_true": True,
        "parsed_by_mcp_is_bool_false": True,
    }


def expected_pdf_artifact_ref_metadata_text_safety(
    card: dict[str, object],
) -> dict[str, object]:
    return {
        "evidence_id": card["evidence_id"],
        "ref_type": "PDF",
        "metadata_text_fields": ["description"],
        "metadata_text_values_have_no_surrounding_whitespace": True,
        "metadata_text_values_have_no_control_characters": True,
    }


def expected_chart_artifact_ref_metadata_text_safety(
    evidence_id: str = "latest_signal_chart",
) -> dict[str, object]:
    return {
        "evidence_id": evidence_id,
        "ref_type": "CHART",
        "metadata_text_fields": ["renderer"],
        "metadata_text_values_have_no_surrounding_whitespace": True,
        "metadata_text_values_have_no_control_characters": True,
    }


def expected_chart_png_artifact_ref_contract(
    evidence_id: str = "latest_signal_chart",
) -> dict[str, object]:
    return {
        "evidence_id": evidence_id,
        "ref_type": "CHART",
        "allowed_ref_suffixes": [".png"],
        "content_addressed_prefix": "sha256:",
        "ref_matches_chart_contract": True,
    }


def expected_chart_offline_artifact_ref_location(
    evidence_id: str = "latest_signal_chart",
) -> dict[str, object]:
    return {
        "evidence_id": evidence_id,
        "ref_type": "CHART",
        "allowed_ref_locations": [
            "local_path",
            "artifact://",
            "sha256:",
        ],
        "network_ref_allowed": False,
        "ref_uses_offline_location": True,
    }


def expected_chart_artifact_ref_reserved_evidence_id(
    evidence_id: str = "latest_signal_chart",
) -> dict[str, object]:
    return {
        "evidence_id": evidence_id,
        "ref_type": "CHART",
        "uses_reserved_chart_evidence_id": True,
    }


def expected_artifact_ref_string_safety(
    evidence_id: str = "latest_signal_chart",
) -> dict[str, object]:
    return {
        "evidence_id": evidence_id,
        "ref_has_no_surrounding_whitespace": True,
        "ref_has_no_control_characters": True,
    }


def expected_artifact_ref_string_field_types(
    evidence_id: str = "latest_signal_chart",
) -> dict[str, object]:
    return {
        "evidence_id": evidence_id,
        "string_fields": ["ref_type", "ref"],
        "ref_type_is_string": True,
        "ref_is_string": True,
    }


def expected_document_evidence_card_observed_at(
    card: dict[str, object],
) -> dict[str, object]:
    return {
        "evidence_id": card["evidence_id"],
        "observed_at_format": "iso8601_utc",
        "observed_at_is_utc_iso": True,
    }


def expected_document_evidence_card_observed_at_not_future(
    card: dict[str, object],
    report_created_at: str,
) -> dict[str, object]:
    return {
        "evidence_id": card["evidence_id"],
        "report_created_at": report_created_at,
        "observed_at_not_after_report_created_at": True,
    }


def expected_document_evidence_card_asset_scope(
    card: dict[str, object],
) -> dict[str, object]:
    return {
        "evidence_id": card["evidence_id"],
        "report_asset": "TQQQ",
        "report_underlying": "QQQ",
        "includes_report_asset": True,
        "includes_report_underlying": True,
    }


def expected_document_evidence_card_asset_scope_string_safety(
    card: dict[str, object],
) -> dict[str, object]:
    return {
        "evidence_id": card["evidence_id"],
        "asset_scope_values_have_no_surrounding_whitespace": True,
        "asset_scope_values_have_no_control_characters": True,
    }


def expected_document_evidence_card_categorical_values(
    card: dict[str, object],
) -> dict[str, object]:
    return {
        "evidence_id": card["evidence_id"],
        "category": "manual_document",
        "source": "manual:document_summary",
        "bias_in_allowed_set": True,
    }


def expected_document_evidence_card_impact_values(
    card: dict[str, object],
) -> dict[str, object]:
    return {
        "evidence_id": card["evidence_id"],
        "buy_impact": "context_only",
        "sell_impact": "context_only",
    }


def expected_document_evidence_card_summary_bounds(
    card: dict[str, object],
) -> dict[str, object]:
    return {
        "evidence_id": card["evidence_id"],
        "summary_max_chars": DOCUMENT_SUMMARY_MAX_CHARS,
        "summary_within_limit": True,
    }


def expected_document_evidence_card_summary_truncation(
    card: dict[str, object],
) -> dict[str, object]:
    return {
        "evidence_id": card["evidence_id"],
        "summary_truncated": card["summary_truncated"],
        "summary_truncated_requires_max_length": True,
    }


def expected_document_evidence_card_invalidating_condition(
    card: dict[str, object],
) -> dict[str, object]:
    return {
        "evidence_id": card["evidence_id"],
        "invalidating_condition_words_min": 4,
        "invalidating_condition_has_min_words": True,
        "invalidating_condition_nonplaceholder": True,
    }


def load_golden() -> dict[str, object]:
    return json.loads(GOLDEN_PATH.read_text(encoding="utf-8"))


def load_degraded_report_fixture() -> dict[str, object]:
    return json.loads(DEGRADED_REPORT_PATH.read_text(encoding="utf-8"))


def iter_nested_strings(value: object) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        strings: list[str] = []
        for nested in value.values():
            strings.extend(iter_nested_strings(nested))
        return strings
    if isinstance(value, list):
        strings = []
        for nested in value:
            strings.extend(iter_nested_strings(nested))
        return strings
    return []


def test_latest_signal_report_snapshot_matches_golden() -> None:
    payload = generate_latest_signal_report("TQQQ")

    assert payload == load_golden()
    LatestSignalReport.model_validate(payload["latest_signal_report"])


def test_latest_signal_report_can_use_jsonl_repository_source(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    ledger_path = tmp_path / "signal_ledger.jsonl"
    stored_signal = {
        **reporting.score_leverage_swing("SSO"),
        "signal_id": "sig_report_repo_sso",
        "run_id": "run_report_repo_sso",
        "created_at": "2026-05-20T12:00:00Z",
    }
    record_signal(signal=stored_signal, ledger_path=str(ledger_path))

    def unexpected_score_call(*_args: object, **_kwargs: object) -> dict[str, object]:
        raise AssertionError("repository-backed report must not rescore the signal")

    monkeypatch.setattr(reporting, "score_leverage_swing", unexpected_score_call)
    payload = generate_latest_signal_report(asset="SSO", ledger_path=f" {ledger_path} ")

    assert payload["latest_signal_report"]["signal_id"] == stored_signal["signal_id"]
    assert payload["latest_signal_report"]["asset"] == "SSO"
    assert payload["latest_signal_report"]["created_at"] == stored_signal["created_at"]
    assert payload["source_signal_ref"] == {
        "signal_id": stored_signal["signal_id"],
        "run_id": stored_signal["run_id"],
        "config_hash": stored_signal["config_hash"],
    }
    assert payload["sections"][0]["items"] == ["SSO / SPY"]
    assert payload["report_contract_guard"]["status"] == "ok"


def test_latest_signal_report_can_use_sqlite_repository_source(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    database_path = tmp_path / "halo_swing.sqlite"
    stored_signal = {
        **reporting.score_leverage_swing("QLD"),
        "signal_id": "sig_report_repo_qld",
        "run_id": "run_report_repo_qld",
        "created_at": "2026-05-20T13:00:00Z",
    }
    record_signal(signal=stored_signal, database_path=str(database_path))

    def unexpected_score_call(*_args: object, **_kwargs: object) -> dict[str, object]:
        raise AssertionError("repository-backed report must not rescore the signal")

    monkeypatch.setattr(reporting, "score_leverage_swing", unexpected_score_call)
    payload = generate_latest_signal_report(
        asset="QLD",
        database_path=f" {database_path} ",
    )
    report_payload_guard_checks = {
        check["name"]: check for check in payload["report_payload_guard"]["checks"]
    }

    assert payload["latest_signal_report"]["signal_id"] == stored_signal["signal_id"]
    assert payload["latest_signal_report"]["asset"] == "QLD"
    assert payload["source_signal_ref"] == {
        "signal_id": stored_signal["signal_id"],
        "run_id": stored_signal["run_id"],
        "config_hash": stored_signal["config_hash"],
    }
    assert str(database_path) not in iter_nested_strings(payload["source_signal_ref"])
    assert all(
        ".sqlite" not in value.lower()
        for value in iter_nested_strings(payload["source_signal_ref"])
    )
    assert report_payload_guard_checks[
        "report_payload_source_signal_ref_keys_match_expected_schema"
    ]["actual"] == ["signal_id", "run_id", "config_hash"]
    assert report_payload_guard_checks[
        "report_payload_source_signal_ref_matches_report_identity"
    ]["actual"] == {
        "signal_id": stored_signal["signal_id"],
        "config_hash": stored_signal["config_hash"],
        "run_id_nonempty": True,
    }
    assert report_payload_guard_checks[
        "report_payload_source_signal_ref_values_have_traceable_format"
    ]["actual"] == {
        "signal_id_nonempty": True,
        "run_id_nonempty": True,
        "config_hash_sha256_prefix": True,
    }
    assert report_payload_guard_checks[
        "report_payload_source_signal_ref_config_hash_digest_is_sha256"
    ]["actual"] == {
        "config_hash_digest_length": 64,
        "config_hash_digest_hex": True,
    }
    assert str(database_path) not in iter_nested_strings(report_payload_guard_checks)
    assert all(
        ".sqlite" not in value.lower()
        for value in iter_nested_strings(report_payload_guard_checks)
    )
    assert payload["report_payload_guard"]["status"] == "ok"
    assert payload["live_data_required"] is False


def test_latest_signal_report_repository_source_includes_jsonl_source_metadata(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    ledger_path = tmp_path / "signal_ledger.jsonl"
    stored_signal = {
        **reporting.score_leverage_swing("SSO"),
        "signal_id": "sig_report_repo_meta_jsonl",
        "run_id": "run_report_repo_meta_jsonl",
        "created_at": "2026-05-20T13:30:00Z",
    }
    record_signal(signal=stored_signal, ledger_path=str(ledger_path))

    def unexpected_score_call(*_args: object, **_kwargs: object) -> dict[str, object]:
        raise AssertionError("repository-backed report must not rescore the signal")

    monkeypatch.setattr(reporting, "score_leverage_swing", unexpected_score_call)
    payload = generate_latest_signal_report(asset="sso", ledger_path=f" {ledger_path} ")
    source_repository_ref = payload["source_repository_ref"]

    assert source_repository_ref == {
        "storage": "jsonl_signal_ledger_record",
        "db_required": False,
        "filters": {
            "asset": "SSO",
            "underlying": None,
            "timeframe": "swing_3d_10d",
        },
    }
    assert "ledger_ref" not in source_repository_ref
    assert "ledger_path" not in source_repository_ref
    assert "database_path" not in source_repository_ref
    assert str(ledger_path) not in iter_nested_strings(source_repository_ref)
    assert payload["report_payload_guard"]["status"] == "ok"
    guard_checks = {
        check["name"]: check for check in payload["report_payload_guard"]["checks"]
    }
    assert guard_checks[
        "report_payload_source_repository_ref_keys_match_expected_schema"
    ]["passed"] is True
    assert guard_checks[
        "report_payload_source_repository_ref_is_path_free"
    ]["passed"] is True


def test_latest_signal_report_reuses_latest_record_source_repository_ref(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    ledger_path = tmp_path / "signal_ledger.jsonl"
    stored_signal = {
        **reporting.score_leverage_swing("SSO"),
        "signal_id": "sig_report_repo_source_ref_reuse",
        "run_id": "run_report_repo_source_ref_reuse",
        "created_at": "2026-05-20T13:40:00Z",
    }
    source_repository_ref = {
        "storage": "latest_signal_record_boundary",
        "db_required": False,
        "filters": {
            "asset": "SSO",
            "underlying": None,
            "timeframe": "swing_3d_10d",
        },
    }

    def fake_get_latest_signal_record(**kwargs: object) -> dict[str, object]:
        assert kwargs == {
            "ledger_path": str(ledger_path),
            "database_path": None,
            "asset": "SSO",
            "underlying": None,
            "timeframe": "swing_3d_10d",
        }
        return {
            "status": "found",
            "signal_id": stored_signal["signal_id"],
            "ledger_ref": str(ledger_path),
            "storage": "legacy_reconstructed_storage",
            "db_required": False,
            "filters": {
                "asset": "SSO",
                "underlying": None,
                "timeframe": "swing_3d_10d",
            },
            "source_repository_ref": source_repository_ref,
            "record": {"signal": stored_signal},
            "label_outcome": None,
            "missing_links": [],
            "live_data_required": False,
        }

    monkeypatch.setattr(
        reporting,
        "get_latest_signal_record",
        fake_get_latest_signal_record,
    )
    payload = generate_latest_signal_report(asset="sso", ledger_path=f" {ledger_path} ")

    assert payload["source_repository_ref"] == source_repository_ref
    assert payload["evidence_context"]["source_repository_ref"] == source_repository_ref
    assert "legacy_reconstructed_storage" not in iter_nested_strings(
        payload["source_repository_ref"]
    )
    assert str(ledger_path) not in iter_nested_strings(payload["source_repository_ref"])
    assert payload["report_payload_guard"]["status"] == "ok"


def test_latest_signal_report_reuses_latest_record_guard(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    ledger_path = tmp_path / "signal_ledger.jsonl"
    stored_signal = {
        **reporting.score_leverage_swing("SSO"),
        "signal_id": "sig_report_repo_record_guard",
        "run_id": "run_report_repo_record_guard",
        "created_at": "2026-05-20T13:45:00Z",
    }
    source_repository_ref = {
        "storage": "latest_signal_record_boundary",
        "db_required": False,
        "filters": {
            "asset": "SSO",
            "underlying": None,
            "timeframe": "swing_3d_10d",
        },
    }
    latest_record_guard = {
        "status": "ok",
        "checks": [
            {
                "name": (
                    "latest_record_source_repository_ref_keys_match_expected_schema"
                ),
                "passed": True,
                "expected": ["storage", "db_required", "filters"],
                "actual": ["storage", "db_required", "filters"],
            },
            {
                "name": "latest_record_source_repository_ref_is_path_free",
                "passed": True,
                "expected": {
                    "omits_ledger_ref": True,
                    "omits_ledger_path": True,
                    "omits_database_path": True,
                    "omits_absolute_or_sqlite_paths": True,
                },
                "actual": {
                    "omits_ledger_ref": True,
                    "omits_ledger_path": True,
                    "omits_database_path": True,
                    "omits_absolute_or_sqlite_paths": True,
                },
            },
            {
                "name": (
                    "latest_record_source_repository_ref_matches_top_level_source"
                ),
                "passed": True,
                "expected": source_repository_ref,
                "actual": source_repository_ref,
            },
        ],
    }

    def fake_get_latest_signal_record(**kwargs: object) -> dict[str, object]:
        assert kwargs == {
            "ledger_path": str(ledger_path),
            "database_path": None,
            "asset": "SSO",
            "underlying": None,
            "timeframe": "swing_3d_10d",
        }
        return {
            "status": "found",
            "signal_id": stored_signal["signal_id"],
            "ledger_ref": str(ledger_path),
            "storage": "legacy_reconstructed_storage",
            "db_required": False,
            "filters": {
                "asset": "SSO",
                "underlying": None,
                "timeframe": "swing_3d_10d",
            },
            "source_repository_ref": source_repository_ref,
            "latest_record_guard": latest_record_guard,
            "record": {"signal": stored_signal},
            "label_outcome": None,
            "missing_links": [],
            "live_data_required": False,
        }

    monkeypatch.setattr(
        reporting,
        "get_latest_signal_record",
        fake_get_latest_signal_record,
    )
    payload = generate_latest_signal_report(asset="sso", ledger_path=f" {ledger_path} ")
    guard_checks = {
        check["name"]: check for check in payload["report_payload_guard"]["checks"]
    }

    assert payload["latest_record_guard"] == latest_record_guard
    assert str(ledger_path) not in iter_nested_strings(payload["latest_record_guard"])
    assert "legacy_reconstructed_storage" not in iter_nested_strings(
        payload["latest_record_guard"]
    )
    assert guard_checks["report_payload_nested_guard_statuses_are_ok"][
        "expected"
    ] == {
        "delivery_preview.guard": "ok",
        "evidence_guard": "ok",
        "report_contract_guard": "ok",
        "latest_record_guard": "ok",
    }
    assert guard_checks["report_payload_nested_guard_statuses_are_ok"][
        "actual"
    ] == {
        "delivery_preview.guard": "ok",
        "evidence_guard": "ok",
        "report_contract_guard": "ok",
        "latest_record_guard": "ok",
    }
    assert guard_checks["report_payload_keys_match_expected_schema"]["actual"][
        guard_checks["report_payload_keys_match_expected_schema"]["actual"].index(
            "source_repository_ref"
        )
        + 1
    ] == "latest_record_guard"
    assert payload["report_payload_guard"]["status"] == "ok"


def test_latest_signal_report_reuses_latest_record_guard_in_evidence_context(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    ledger_path = tmp_path / "signal_ledger.jsonl"
    stored_signal = {
        **reporting.score_leverage_swing("SSO"),
        "signal_id": "sig_report_repo_record_guard_evidence",
        "run_id": "run_report_repo_record_guard_evidence",
        "created_at": "2026-05-20T13:50:00Z",
    }
    record_signal(signal=stored_signal, ledger_path=str(ledger_path))

    def unexpected_score_call(*_args: object, **_kwargs: object) -> dict[str, object]:
        raise AssertionError("repository-backed report must not rescore the signal")

    monkeypatch.setattr(reporting, "score_leverage_swing", unexpected_score_call)
    payload = generate_latest_signal_report(asset="sso", ledger_path=f" {ledger_path} ")
    evidence_guard_checks = {
        check["name"]: check for check in payload["evidence_guard"]["checks"]
    }

    assert payload["evidence_context"]["latest_record_guard"] == payload[
        "latest_record_guard"
    ]
    assert payload["evidence_context"]["latest_record_guard"]["status"] == "ok"
    assert str(ledger_path) not in iter_nested_strings(
        payload["evidence_context"]["latest_record_guard"]
    )
    assert evidence_guard_checks[
        "evidence_latest_record_guard_keys_match_expected_schema"
    ] == {
        "name": "evidence_latest_record_guard_keys_match_expected_schema",
        "passed": True,
        "expected": ["status", "checks"],
        "actual": ["status", "checks"],
    }
    assert evidence_guard_checks["evidence_latest_record_guard_status_is_ok"] == {
        "name": "evidence_latest_record_guard_status_is_ok",
        "passed": True,
        "expected": "ok",
        "actual": "ok",
    }
    assert "evidence_latest_record_guard_keys_match_expected_schema" in (
        evidence_guard_checks["evidence_guard_check_names_match_expected_schema"][
            "actual"
        ]
    )
    assert "evidence_latest_record_guard_status_is_ok" in (
        evidence_guard_checks["evidence_guard_check_names_match_expected_schema"][
            "actual"
        ]
    )
    assert payload["evidence_guard"]["status"] == "ok"


def test_latest_signal_report_evidence_guard_validates_latest_record_guard_checks(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    ledger_path = tmp_path / "signal_ledger.jsonl"
    stored_signal = {
        **reporting.score_leverage_swing("SSO"),
        "signal_id": "sig_report_repo_record_guard_checks",
        "run_id": "run_report_repo_record_guard_checks",
        "created_at": "2026-05-20T13:55:00Z",
    }
    record_signal(signal=stored_signal, ledger_path=str(ledger_path))

    def unexpected_score_call(*_args: object, **_kwargs: object) -> dict[str, object]:
        raise AssertionError("repository-backed report must not rescore the signal")

    monkeypatch.setattr(reporting, "score_leverage_swing", unexpected_score_call)
    payload = generate_latest_signal_report(asset="sso", ledger_path=f" {ledger_path} ")
    evidence_guard_checks = {
        check["name"]: check for check in payload["evidence_guard"]["checks"]
    }
    expected_latest_record_guard_check_names = [
        "latest_record_source_repository_ref_keys_match_expected_schema",
        "latest_record_source_repository_ref_is_path_free",
        "latest_record_source_repository_ref_matches_top_level_source",
    ]

    assert evidence_guard_checks[
        "evidence_latest_record_guard_check_names_match_expected_schema"
    ] == {
        "name": "evidence_latest_record_guard_check_names_match_expected_schema",
        "passed": True,
        "expected": expected_latest_record_guard_check_names,
        "actual": expected_latest_record_guard_check_names,
    }
    assert evidence_guard_checks[
        "evidence_latest_record_guard_checks_all_passed"
    ] == {
        "name": "evidence_latest_record_guard_checks_all_passed",
        "passed": True,
        "expected": True,
        "actual": [True, True, True],
    }
    assert "evidence_latest_record_guard_check_names_match_expected_schema" in (
        evidence_guard_checks["evidence_guard_check_names_match_expected_schema"][
            "actual"
        ]
    )
    assert "evidence_latest_record_guard_checks_all_passed" in (
        evidence_guard_checks["evidence_guard_check_names_match_expected_schema"][
            "actual"
        ]
    )
    assert payload["evidence_guard"]["status"] == "ok"


def test_latest_signal_report_repository_source_includes_jsonl_evidence_source_metadata(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    ledger_path = tmp_path / "signal_ledger.jsonl"
    stored_signal = {
        **reporting.score_leverage_swing("SSO"),
        "signal_id": "sig_report_repo_evidence_meta_jsonl",
        "run_id": "run_report_repo_evidence_meta_jsonl",
        "created_at": "2026-05-20T13:35:00Z",
    }
    record_signal(signal=stored_signal, ledger_path=str(ledger_path))

    def unexpected_score_call(*_args: object, **_kwargs: object) -> dict[str, object]:
        raise AssertionError("repository-backed report must not rescore the signal")

    monkeypatch.setattr(reporting, "score_leverage_swing", unexpected_score_call)
    payload = generate_latest_signal_report(asset="SSO", ledger_path=str(ledger_path))
    evidence_source_ref = payload["evidence_context"]["source_repository_ref"]

    assert evidence_source_ref == payload["source_repository_ref"]
    assert evidence_source_ref["storage"] == "jsonl_signal_ledger_record"
    assert evidence_source_ref["filters"] == {
        "asset": "SSO",
        "underlying": None,
        "timeframe": "swing_3d_10d",
    }
    assert str(ledger_path) not in iter_nested_strings(evidence_source_ref)
    assert all(
        ".sqlite" not in value.lower()
        for value in iter_nested_strings(evidence_source_ref)
    )


def test_latest_signal_report_repository_source_evidence_guard_validates_source_metadata(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    ledger_path = tmp_path / "signal_ledger.jsonl"
    stored_signal = {
        **reporting.score_leverage_swing("SSO"),
        "signal_id": "sig_report_repo_evidence_meta_guard_jsonl",
        "run_id": "run_report_repo_evidence_meta_guard_jsonl",
        "created_at": "2026-05-20T13:37:00Z",
    }
    record_signal(signal=stored_signal, ledger_path=str(ledger_path))

    def unexpected_score_call(*_args: object, **_kwargs: object) -> dict[str, object]:
        raise AssertionError("repository-backed report must not rescore the signal")

    monkeypatch.setattr(reporting, "score_leverage_swing", unexpected_score_call)
    payload = generate_latest_signal_report(asset="SSO", ledger_path=str(ledger_path))
    guard_checks = {
        check["name"]: check for check in payload["evidence_guard"]["checks"]
    }

    assert payload["evidence_guard"]["status"] == "ok"
    assert guard_checks[
        "evidence_source_repository_ref_keys_match_expected_schema"
    ] == {
        "name": "evidence_source_repository_ref_keys_match_expected_schema",
        "passed": True,
        "expected": ["storage", "db_required", "filters"],
        "actual": ["storage", "db_required", "filters"],
    }
    assert guard_checks["evidence_source_repository_ref_is_path_free"] == {
        "name": "evidence_source_repository_ref_is_path_free",
        "passed": True,
        "expected": {
            "omits_ledger_ref": True,
            "omits_ledger_path": True,
            "omits_database_path": True,
            "omits_absolute_or_sqlite_paths": True,
        },
        "actual": {
            "omits_ledger_ref": True,
            "omits_ledger_path": True,
            "omits_database_path": True,
            "omits_absolute_or_sqlite_paths": True,
        },
    }
    assert "evidence_source_repository_ref_is_path_free" in guard_checks[
        "evidence_guard_check_names_match_expected_schema"
    ]["expected"]
    assert str(ledger_path) not in iter_nested_strings(guard_checks)
    assert all(
        ".sqlite" not in value.lower()
        for value in iter_nested_strings(guard_checks)
    )


def test_latest_signal_report_repository_source_summary_appears_in_sections_and_text(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    ledger_path = tmp_path / "signal_ledger.jsonl"
    stored_signal = {
        **reporting.score_leverage_swing("SSO"),
        "signal_id": "sig_report_repo_source_summary_jsonl",
        "run_id": "run_report_repo_source_summary_jsonl",
        "created_at": "2026-05-20T13:38:00Z",
    }
    record_signal(signal=stored_signal, ledger_path=str(ledger_path))

    def unexpected_score_call(*_args: object, **_kwargs: object) -> dict[str, object]:
        raise AssertionError("repository-backed report must not rescore the signal")

    monkeypatch.setattr(reporting, "score_leverage_swing", unexpected_score_call)
    payload = generate_latest_signal_report(asset="SSO", ledger_path=str(ledger_path))
    reasons = next(
        section for section in payload["sections"] if section["title"] == "Reasons"
    )
    source_summary = (
        "Repository source: jsonl_signal_ledger_record; "
        "db_required=false; "
        "filters asset=SSO underlying=<any> timeframe=swing_3d_10d"
    )

    assert source_summary in reasons["items"]
    assert f"- {source_summary}" in payload["text"]
    assert str(ledger_path) not in iter_nested_strings(reasons)
    assert str(ledger_path) not in payload["text"]
    assert all(
        ".sqlite" not in value.lower()
        for value in iter_nested_strings(reasons)
    )


def test_latest_signal_report_repository_source_includes_sqlite_source_metadata(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    database_path = tmp_path / "halo_swing.sqlite"
    stored_signal = {
        **reporting.score_leverage_swing("QLD", timeframe="swing_5d_20d"),
        "signal_id": "sig_report_repo_meta_sqlite",
        "run_id": "run_report_repo_meta_sqlite",
        "created_at": "2026-05-20T13:45:00Z",
    }
    record_signal(signal=stored_signal, database_path=str(database_path))

    def unexpected_score_call(*_args: object, **_kwargs: object) -> dict[str, object]:
        raise AssertionError("repository-backed report must not rescore the signal")

    monkeypatch.setattr(reporting, "score_leverage_swing", unexpected_score_call)
    payload = generate_latest_signal_report(
        asset="QLD",
        timeframe=" swing_5d_20d ",
        database_path=f" {database_path} ",
    )
    source_repository_ref = payload["source_repository_ref"]

    assert source_repository_ref == {
        "storage": "sqlite_signal_repository",
        "db_required": True,
        "filters": {
            "asset": "QLD",
            "underlying": None,
            "timeframe": "swing_5d_20d",
        },
    }
    strings = iter_nested_strings(source_repository_ref)
    assert str(database_path) not in strings
    assert all(".sqlite" not in value.lower() for value in strings)
    assert payload["report_payload_guard"]["status"] == "ok"
    guard_checks = {
        check["name"]: check for check in payload["report_payload_guard"]["checks"]
    }
    assert guard_checks[
        "report_payload_source_repository_ref_keys_match_expected_schema"
    ]["actual"] == ["storage", "db_required", "filters"]
    assert guard_checks[
        "report_payload_source_repository_ref_is_path_free"
    ]["actual"] == {
        "omits_ledger_ref": True,
        "omits_ledger_path": True,
        "omits_database_path": True,
        "omits_absolute_or_sqlite_paths": True,
    }


def test_latest_signal_report_sqlite_repository_source_summary_appears_in_sections_and_text(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    database_path = tmp_path / "halo_swing.sqlite"
    stored_signal = {
        **reporting.score_leverage_swing("QLD", timeframe="swing_5d_20d"),
        "signal_id": "sig_report_repo_source_summary_sqlite",
        "run_id": "run_report_repo_source_summary_sqlite",
        "created_at": "2026-05-20T13:47:00Z",
    }
    record_signal(signal=stored_signal, database_path=str(database_path))

    def unexpected_score_call(*_args: object, **_kwargs: object) -> dict[str, object]:
        raise AssertionError("repository-backed report must not rescore the signal")

    monkeypatch.setattr(reporting, "score_leverage_swing", unexpected_score_call)
    payload = generate_latest_signal_report(
        asset="QLD",
        timeframe=" swing_5d_20d ",
        database_path=f" {database_path} ",
    )
    reasons = next(
        section for section in payload["sections"] if section["title"] == "Reasons"
    )
    source_summary = (
        "Repository source: sqlite_signal_repository; "
        "db_required=true; "
        "filters asset=QLD underlying=<any> timeframe=swing_5d_20d"
    )

    assert source_summary in reasons["items"]
    assert f"- {source_summary}" in payload["text"]
    assert payload["source_repository_ref"] == {
        "storage": "sqlite_signal_repository",
        "db_required": True,
        "filters": {
            "asset": "QLD",
            "underlying": None,
            "timeframe": "swing_5d_20d",
        },
    }
    assert payload["report_payload_guard"]["status"] == "ok"
    assert str(database_path) not in iter_nested_strings(reasons)
    assert str(database_path) not in payload["text"]
    assert all(
        ".sqlite" not in value.lower()
        for value in iter_nested_strings(reasons)
    )


def test_latest_signal_report_sqlite_repository_source_evidence_guard_validates_source_metadata(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    database_path = tmp_path / "halo_swing.sqlite"
    stored_signal = {
        **reporting.score_leverage_swing("QLD", timeframe="swing_5d_20d"),
        "signal_id": "sig_report_repo_evidence_meta_guard_sqlite",
        "run_id": "run_report_repo_evidence_meta_guard_sqlite",
        "created_at": "2026-05-20T13:48:00Z",
    }
    record_signal(signal=stored_signal, database_path=str(database_path))

    def unexpected_score_call(*_args: object, **_kwargs: object) -> dict[str, object]:
        raise AssertionError("repository-backed report must not rescore the signal")

    monkeypatch.setattr(reporting, "score_leverage_swing", unexpected_score_call)
    payload = generate_latest_signal_report(
        asset="QLD",
        timeframe=" swing_5d_20d ",
        database_path=f" {database_path} ",
    )
    guard_checks = {
        check["name"]: check for check in payload["evidence_guard"]["checks"]
    }

    assert payload["evidence_guard"]["status"] == "ok"
    assert guard_checks[
        "evidence_source_repository_ref_keys_match_expected_schema"
    ] == {
        "name": "evidence_source_repository_ref_keys_match_expected_schema",
        "passed": True,
        "expected": ["storage", "db_required", "filters"],
        "actual": ["storage", "db_required", "filters"],
    }
    assert guard_checks["evidence_source_repository_ref_is_path_free"] == {
        "name": "evidence_source_repository_ref_is_path_free",
        "passed": True,
        "expected": {
            "omits_ledger_ref": True,
            "omits_ledger_path": True,
            "omits_database_path": True,
            "omits_absolute_or_sqlite_paths": True,
        },
        "actual": {
            "omits_ledger_ref": True,
            "omits_ledger_path": True,
            "omits_database_path": True,
            "omits_absolute_or_sqlite_paths": True,
        },
    }
    assert "evidence_source_repository_ref_is_path_free" in guard_checks[
        "evidence_guard_check_names_match_expected_schema"
    ]["expected"]
    assert payload["evidence_context"]["source_repository_ref"] == {
        "storage": "sqlite_signal_repository",
        "db_required": True,
        "filters": {
            "asset": "QLD",
            "underlying": None,
            "timeframe": "swing_5d_20d",
        },
    }
    assert str(database_path) not in iter_nested_strings(guard_checks)
    assert all(
        ".sqlite" not in value.lower()
        for value in iter_nested_strings(guard_checks)
    )


def test_latest_signal_report_sqlite_repository_includes_path_free_latest_record_guard(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    database_path = tmp_path / "halo_swing.sqlite"
    stored_signal = {
        **reporting.score_leverage_swing("QLD", timeframe="swing_5d_20d"),
        "signal_id": "sig_report_repo_guard_sqlite",
        "run_id": "run_report_repo_guard_sqlite",
        "created_at": "2026-05-20T13:46:00Z",
    }
    record_signal(signal=stored_signal, database_path=str(database_path))

    def unexpected_score_call(*_args: object, **_kwargs: object) -> dict[str, object]:
        raise AssertionError("repository-backed report must not rescore the signal")

    monkeypatch.setattr(reporting, "score_leverage_swing", unexpected_score_call)
    payload = generate_latest_signal_report(
        asset="QLD",
        timeframe=" swing_5d_20d ",
        database_path=f" {database_path} ",
    )
    latest_record_guard = payload["latest_record_guard"]
    latest_record_guard_checks = {
        check["name"]: check for check in latest_record_guard["checks"]
    }
    evidence_guard_checks = {
        check["name"]: check for check in payload["evidence_guard"]["checks"]
    }
    expected_latest_record_guard_check_names = [
        "latest_record_source_repository_ref_keys_match_expected_schema",
        "latest_record_source_repository_ref_is_path_free",
        "latest_record_source_repository_ref_matches_top_level_source",
    ]
    evidence_guard_checks = {
        check["name"]: check for check in payload["evidence_guard"]["checks"]
    }
    expected_latest_record_guard_check_names = [
        "latest_record_source_repository_ref_keys_match_expected_schema",
        "latest_record_source_repository_ref_is_path_free",
        "latest_record_source_repository_ref_matches_top_level_source",
    ]

    assert payload["evidence_context"]["latest_record_guard"] == latest_record_guard
    assert latest_record_guard["status"] == "ok"
    assert latest_record_guard_checks[
        "latest_record_source_repository_ref_matches_top_level_source"
    ]["expected"] == {
        "storage": "sqlite_signal_repository",
        "db_required": True,
        "filters": {
            "asset": "QLD",
            "underlying": None,
            "timeframe": "swing_5d_20d",
        },
    }
    assert latest_record_guard_checks[
        "latest_record_source_repository_ref_is_path_free"
    ]["actual"] == {
        "omits_ledger_ref": True,
        "omits_ledger_path": True,
        "omits_database_path": True,
        "omits_absolute_or_sqlite_paths": True,
    }
    assert str(database_path) not in iter_nested_strings(latest_record_guard)
    assert all(
        ".sqlite" not in value.lower()
        for value in iter_nested_strings(latest_record_guard)
    )
    assert evidence_guard_checks[
        "evidence_latest_record_guard_check_names_match_expected_schema"
    ] == {
        "name": "evidence_latest_record_guard_check_names_match_expected_schema",
        "passed": True,
        "expected": expected_latest_record_guard_check_names,
        "actual": expected_latest_record_guard_check_names,
    }
    assert evidence_guard_checks[
        "evidence_latest_record_guard_checks_all_passed"
    ] == {
        "name": "evidence_latest_record_guard_checks_all_passed",
        "passed": True,
        "expected": True,
        "actual": [True, True, True],
    }
    assert str(database_path) not in iter_nested_strings(evidence_guard_checks)
    assert all(
        ".sqlite" not in value.lower()
        for value in iter_nested_strings(evidence_guard_checks)
    )
    assert payload["report_payload_guard"]["status"] == "ok"
    assert payload["evidence_guard"]["status"] == "ok"


def test_latest_signal_report_repository_source_filters_by_timeframe(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    database_path = tmp_path / "halo_swing.sqlite"
    swing_signal = {
        **reporting.score_leverage_swing("TQQQ", timeframe="swing_3d_10d"),
        "signal_id": "sig_report_repo_tqqq_swing",
        "run_id": "run_report_repo_tqqq_swing",
        "created_at": "2026-05-20T12:00:00Z",
    }
    alternate_signal = {
        **reporting.score_leverage_swing("TQQQ", timeframe="swing_5d_20d"),
        "signal_id": "sig_report_repo_tqqq_alt",
        "run_id": "run_report_repo_tqqq_alt",
        "created_at": "2026-05-20T13:00:00Z",
    }
    record_signal(signal=swing_signal, database_path=str(database_path))
    record_signal(signal=alternate_signal, database_path=str(database_path))
    selected_label = label_signal_outcome(
        signal_id=swing_signal["signal_id"],
        database_path=str(database_path),
        price_path=[500.0, 560.0],
        time_barrier_days=2,
    )
    label_signal_outcome(
        signal_id=alternate_signal["signal_id"],
        database_path=str(database_path),
        price_path=[500.0, 450.0],
        time_barrier_days=3,
    )

    def unexpected_score_call(*_args: object, **_kwargs: object) -> dict[str, object]:
        raise AssertionError("repository-backed report must not rescore the signal")

    monkeypatch.setattr(reporting, "score_leverage_swing", unexpected_score_call)
    payload = generate_latest_signal_report(
        asset="TQQQ",
        timeframe=" swing_3d_10d ",
        database_path=f" {database_path} ",
    )
    reasons = next(
        section for section in payload["sections"] if section["title"] == "Reasons"
    )
    cautions = next(
        section["items"]
        for section in payload["sections"]
        if section["title"] == "Cautions"
    )
    report_payload_guard_checks = {
        check["name"]: check for check in payload["report_payload_guard"]["checks"]
    }
    actual_payload_check_names = [
        check["name"] for check in payload["report_payload_guard"]["checks"]
    ]
    actual_payload_check_keys = {
        check["name"]: list(check)
        for check in payload["report_payload_guard"]["checks"]
    }
    report_contract_guard_checks = {
        check["name"]: check for check in payload["report_contract_guard"]["checks"]
    }
    latest_record_guard = payload["latest_record_guard"]
    latest_record_guard_checks = {
        check["name"]: check for check in latest_record_guard["checks"]
    }
    evidence_guard_checks = {
        check["name"]: check for check in payload["evidence_guard"]["checks"]
    }
    delivery_preview = payload["delivery_preview"]
    telegram_preview = delivery_preview["channels"]["telegram"]
    delivery_preview_guard_checks = {
        check["name"]: check for check in delivery_preview["guard"]["checks"]
    }
    delivery_contract = payload["delivery_contract"]
    delivery_channels = delivery_contract["channels"]
    telegram_contract = delivery_channels["telegram"]
    prompt_contract = payload["prompt_contract"]
    report_intent_contract = payload["report_intent_contract"]
    evidence_contract = payload["evidence_contract"]
    evidence_context = payload["evidence_context"]
    expected_latest_record_guard_check_names = [
        "latest_record_source_repository_ref_keys_match_expected_schema",
        "latest_record_source_repository_ref_is_path_free",
        "latest_record_source_repository_ref_matches_top_level_source",
    ]
    source_summary = (
        "Repository source: sqlite_signal_repository; "
        "db_required=true; "
        "filters asset=TQQQ underlying=<any> timeframe=swing_3d_10d"
    )
    source_repository_ref = {
        "storage": "sqlite_signal_repository",
        "db_required": True,
        "filters": {
            "asset": "TQQQ",
            "underlying": None,
            "timeframe": "swing_3d_10d",
        },
    }
    expected_source_repository_ref_path_free = {
        "omits_ledger_ref": True,
        "omits_ledger_path": True,
        "omits_database_path": True,
        "omits_absolute_or_sqlite_paths": True,
    }
    expected_source_signal_ref_identity = {
        "signal_id": swing_signal["signal_id"],
        "config_hash": swing_signal["config_hash"],
        "run_id_nonempty": True,
    }
    expected_source_signal_ref_traceable_format = {
        "signal_id_nonempty": True,
        "run_id_nonempty": True,
        "config_hash_sha256_prefix": True,
    }
    expected_source_signal_ref_config_hash_digest = {
        "config_hash_digest_length": 64,
        "config_hash_digest_hex": True,
    }
    selected_label_summary = (
        f"Stored label: outcome={selected_label['outcome']}; "
        f"realized_r={selected_label['realized_r']}; "
        f"first_barrier_hit={selected_label['first_barrier_hit']}; "
        "time_barrier_days=2"
    )
    expected_nested_guard_statuses = {
        "delivery_preview.guard": "ok",
        "evidence_guard": "ok",
        "report_contract_guard": "ok",
        "latest_record_guard": "ok",
    }
    actual_nested_guard_statuses = {
        "delivery_preview.guard": delivery_preview["guard"]["status"],
        "evidence_guard": payload["evidence_guard"]["status"],
        "report_contract_guard": payload["report_contract_guard"]["status"],
        "latest_record_guard": latest_record_guard["status"],
    }
    expected_top_level_identity = {
        "as_of": swing_signal["created_at"],
        "asset": "TQQQ",
        "underlying": swing_signal["underlying"],
        "timeframe": "swing_3d_10d",
        "action": swing_signal["action"],
        "confidence_label": payload["confidence_label"],
    }
    expected_payload_keys = [
        "schema_version",
        "as_of",
        "asset",
        "underlying",
        "timeframe",
        "action",
        "confidence_label",
        "report_intent",
        "latest_signal_report",
        "sections",
        "text",
        "prompt_contract",
        "delivery_contract",
        "delivery_preview",
        "evidence_contract",
        "evidence_context",
        "evidence_guard",
        "report_intent_contract",
        "report_contract_guard",
        "source_signal_ref",
        "source_repository_ref",
        "latest_record_guard",
        "live_data_required",
        "report_payload_guard",
    ]
    expected_payload_check_names = [
        "report_payload_schema_version_matches_expected",
        "report_payload_live_data_required_matches_expected",
        "report_payload_keys_match_expected_schema",
        "report_payload_source_signal_ref_keys_match_expected_schema",
        "report_payload_source_signal_ref_matches_report_identity",
        "report_payload_source_signal_ref_values_have_traceable_format",
        "report_payload_source_signal_ref_config_hash_digest_is_sha256",
        "report_payload_source_repository_ref_keys_match_expected_schema",
        "report_payload_source_repository_ref_is_path_free",
        "report_payload_intent_matches_contract",
        "report_payload_top_level_identity_matches_latest_signal_report",
        "report_payload_nested_guard_statuses_are_ok",
        "report_payload_optional_context_statuses_are_ok",
        "report_payload_optional_context_guards_are_ok",
        "report_payload_guard_check_names_match_expected_schema",
        "report_payload_guard_keys_match_expected_schema",
        "report_payload_guard_check_keys_match_expected_schema",
    ]
    expected_delivery_contract_schema = {
        "contract_keys": ["channels", "cron_intents"],
        "channel_names": ["hermes", "telegram"],
        "hermes_channel_keys": ["format", "network_call", "numeric_authority"],
        "telegram_channel_keys": [
            "schema_version",
            "format",
            "network_call",
            "max_chars",
            "required_sections",
            "overflow_policy",
            "section_separator",
            "chunk_indexing",
            "send_call",
        ],
    }
    expected_delivery_channel_formats = {
        "hermes": "structured_json_plus_text",
        "telegram": "plain_text",
    }
    expected_telegram_chunking_contract = {
        "overflow_policy": "split_on_section_boundary",
        "section_separator": "\n\n",
        "chunk_indexing": "1_based",
    }
    expected_report_sections = [
        "Target",
        "Decision",
        "Reasons",
        "Entry",
        "Stop",
        "Take Profit",
        "Cautions",
    ]
    expected_prompt_terms = [
        "action",
        "confidence",
        "entry",
        "stop",
        "take_profit",
        "risk",
        "data_warnings",
    ]
    expected_prompt_identity = {
        "numeric_authority": "Use MCP numeric fields as source of truth.",
        "llm_role": "Summarize conflicts, caveats, and final wording only.",
    }
    expected_evidence_contract = {
        "max_reason_summary_chars": 260,
        "max_evidence_summary_chars": 700,
        "max_conflict_flags": 8,
        "required_conflict_fields": ["name", "severity", "status", "details"],
    }
    expected_evidence_special_check_keys = {
        "reason_summary_within_limit": [
            "name",
            "passed",
            "expected_max_chars",
            "actual_chars",
        ],
        "evidence_summary_within_limit": [
            "name",
            "passed",
            "expected_max_chars",
            "actual_chars",
        ],
        "conflict_flags_within_limit": [
            "name",
            "passed",
            "expected_max",
            "actual_count",
        ],
    }
    expected_report_intent_contract = {
        "name": "pre_market_swing_report",
        "schedule_hint": "weekday_pre_market",
        "decision_focus": "new_swing_entry_and_watchlist",
        "required_sections": expected_report_sections,
    }
    section_titles = [section["title"] for section in payload["sections"]]
    expected_text_section_positions = {
        title: payload["text"].find(f"{title}:")
        for title in expected_report_sections
    }
    expected_text_order_actual = {
        "found_sections": expected_report_sections,
        "positions_ascending": True,
        "positions": expected_text_section_positions,
    }
    latest_report = payload["latest_signal_report"]
    expected_numeric_field_presence = {
        "decision_line_present": True,
        "confidence_line_present": True,
        "score_line_present": True,
    }
    selected_component_scores = {
        key: float(value)
        for key, value in swing_signal["component_scores"].items()
        if key != "event_risk"
    }
    strongest_component = max(
        selected_component_scores,
        key=selected_component_scores.get,
    )
    weakest_component = min(
        selected_component_scores,
        key=selected_component_scores.get,
    )
    expected_component_extremes = {
        "strongest": {
            "name": strongest_component,
            "score": round(selected_component_scores[strongest_component], 4),
        },
        "weakest": {
            "name": weakest_component,
            "score": round(selected_component_scores[weakest_component], 4),
        },
        "spread": round(
            selected_component_scores[strongest_component]
            - selected_component_scores[weakest_component],
            4,
        ),
    }

    assert evidence_contract == expected_evidence_contract
    assert evidence_context["source_repository_ref"] == source_repository_ref
    assert evidence_context["component_extremes"] == expected_component_extremes
    assert evidence_context["component_extremes"]["spread"] > 0
    assert evidence_context["component_extremes"]["strongest"]["name"] in (
        selected_component_scores
    )
    assert evidence_context["component_extremes"]["weakest"]["name"] in (
        selected_component_scores
    )
    assert evidence_context["component_extremes"]["strongest"]["name"] != "event_risk"
    assert evidence_context["component_extremes"]["weakest"]["name"] != "event_risk"
    assert (
        len(evidence_context["reason_summary"])
        <= evidence_contract["max_reason_summary_chars"]
    )
    assert (
        len(evidence_context["evidence_summary"])
        <= evidence_contract["max_evidence_summary_chars"]
    )
    assert (
        len(evidence_context["conflict_flags"])
        <= evidence_contract["max_conflict_flags"]
    )
    assert all(
        all(
            field in flag
            for field in evidence_contract["required_conflict_fields"]
        )
        for flag in evidence_context["conflict_flags"]
    )
    assert evidence_guard_checks["reason_summary_within_limit"] == {
        "name": "reason_summary_within_limit",
        "passed": True,
        "expected_max_chars": evidence_contract["max_reason_summary_chars"],
        "actual_chars": len(latest_report["reason_summary"]),
    }
    assert evidence_guard_checks["evidence_summary_within_limit"] == {
        "name": "evidence_summary_within_limit",
        "passed": True,
        "expected_max_chars": evidence_contract["max_evidence_summary_chars"],
        "actual_chars": len(latest_report["evidence_summary"]),
    }
    assert evidence_guard_checks["conflict_flags_within_limit"] == {
        "name": "conflict_flags_within_limit",
        "passed": True,
        "expected_max": evidence_contract["max_conflict_flags"],
        "actual_count": len(evidence_context["conflict_flags"]),
    }
    assert evidence_guard_checks["conflict_flags_have_required_fields"] == {
        "name": "conflict_flags_have_required_fields",
        "passed": True,
        "expected": evidence_contract["required_conflict_fields"],
        "actual": [
            sorted(flag)
            for flag in evidence_context["conflict_flags"]
        ],
    }
    assert evidence_context["risk_warnings"]
    assert set(evidence_context["risk_warnings"]).issubset(cautions)
    assert all(
        flag["status"] == "acknowledged"
        for flag in evidence_context["conflict_flags"]
    )
    assert evidence_guard_checks["risk_warnings_reflected_in_cautions"] == {
        "name": "risk_warnings_reflected_in_cautions",
        "passed": True,
        "expected": evidence_context["risk_warnings"],
        "actual": cautions,
    }
    assert evidence_guard_checks["flagged_conflicts_are_acknowledged"] == {
        "name": "flagged_conflicts_are_acknowledged",
        "passed": True,
        "expected": "acknowledged",
        "actual": [
            flag["status"]
            for flag in evidence_context["conflict_flags"]
        ],
    }
    assert evidence_guard_checks[
        "evidence_source_repository_ref_keys_match_expected_schema"
    ] == {
        "name": "evidence_source_repository_ref_keys_match_expected_schema",
        "passed": True,
        "expected": ["storage", "db_required", "filters"],
        "actual": ["storage", "db_required", "filters"],
    }
    assert evidence_guard_checks["evidence_source_repository_ref_is_path_free"] == {
        "name": "evidence_source_repository_ref_is_path_free",
        "passed": True,
        "expected": {
            "omits_ledger_ref": True,
            "omits_ledger_path": True,
            "omits_database_path": True,
            "omits_absolute_or_sqlite_paths": True,
        },
        "actual": {
            "omits_ledger_ref": True,
            "omits_ledger_path": True,
            "omits_database_path": True,
            "omits_absolute_or_sqlite_paths": True,
        },
    }
    assert evidence_guard_checks[
        "evidence_guard_check_keys_match_expected_schema"
    ]["actual"]["special_check_keys"] == expected_evidence_special_check_keys
    assert "evidence_source_repository_ref_is_path_free" in evidence_guard_checks[
        "evidence_guard_check_names_match_expected_schema"
    ]["expected"]
    assert "conflict_flags_have_required_fields" in evidence_guard_checks[
        "evidence_guard_check_keys_match_expected_schema"
    ]["expected"]["default_check_names"]
    assert "risk_warnings_reflected_in_cautions" in evidence_guard_checks[
        "evidence_guard_check_names_match_expected_schema"
    ]["expected"]
    assert "flagged_conflicts_are_acknowledged" in evidence_guard_checks[
        "evidence_guard_check_keys_match_expected_schema"
    ]["expected"]["default_check_names"]
    assert payload["latest_signal_report"]["signal_id"] == swing_signal["signal_id"]
    assert payload["latest_signal_report"]["timeframe"] == "swing_3d_10d"
    label_status = payload["latest_signal_report"]["label_status"]
    assert label_status["schema_version"] == "signal_label_outcome.v1"
    assert label_status["signal_id"] == swing_signal["signal_id"]
    assert label_status["outcome"] == selected_label["outcome"]
    assert label_status["realized_r"] == selected_label["realized_r"]
    assert label_status["first_barrier_hit"] == selected_label["first_barrier_hit"]
    assert label_status["labeled_at"] == selected_label["labeled_at"]
    assert label_status["time_barrier_days"] == selected_label["time_barrier_days"]
    assert label_status["live_data_required"] is False
    evidence_label_status = payload["evidence_context"]["label_status"]
    assert evidence_label_status == label_status
    assert evidence_guard_checks["label_status_reflected_in_evidence_context"] == {
        "name": "label_status_reflected_in_evidence_context",
        "passed": True,
        "expected": label_status,
        "actual": evidence_label_status,
    }
    assert "label_status_reflected_in_evidence_context" in evidence_guard_checks[
        "evidence_guard_check_names_match_expected_schema"
    ]["expected"]
    assert "label_status_reflected_in_evidence_context" in evidence_guard_checks[
        "evidence_guard_check_keys_match_expected_schema"
    ]["expected"]["default_check_names"]
    assert payload["source_signal_ref"] == {
        "signal_id": swing_signal["signal_id"],
        "run_id": swing_signal["run_id"],
        "config_hash": swing_signal["config_hash"],
    }
    assert payload["source_repository_ref"] == source_repository_ref
    assert payload["evidence_context"]["latest_record_guard"] == latest_record_guard
    assert list(latest_record_guard) == ["status", "checks"]
    assert latest_record_guard["status"] == "ok"
    assert [check["name"] for check in latest_record_guard["checks"]] == (
        expected_latest_record_guard_check_names
    )
    expected_latest_record_guard_passes = [True, True, True]
    latest_record_guard_passes = [
        check["passed"] for check in latest_record_guard["checks"]
    ]
    assert latest_record_guard_passes == expected_latest_record_guard_passes
    assert latest_record_guard_checks[
        "latest_record_source_repository_ref_keys_match_expected_schema"
    ] == {
        "name": "latest_record_source_repository_ref_keys_match_expected_schema",
        "passed": True,
        "expected": ["storage", "db_required", "filters"],
        "actual": ["storage", "db_required", "filters"],
    }
    assert latest_record_guard_checks[
        "latest_record_source_repository_ref_matches_top_level_source"
    ] == {
        "name": "latest_record_source_repository_ref_matches_top_level_source",
        "passed": True,
        "expected": source_repository_ref,
        "actual": source_repository_ref,
    }
    assert latest_record_guard_checks[
        "latest_record_source_repository_ref_is_path_free"
    ] == {
        "name": "latest_record_source_repository_ref_is_path_free",
        "passed": True,
        "expected": expected_source_repository_ref_path_free,
        "actual": expected_source_repository_ref_path_free,
    }
    assert payload["evidence_guard"]["status"] == "ok"
    assert evidence_guard_checks[
        "evidence_latest_record_guard_keys_match_expected_schema"
    ] == {
        "name": "evidence_latest_record_guard_keys_match_expected_schema",
        "passed": True,
        "expected": ["status", "checks"],
        "actual": ["status", "checks"],
    }
    assert evidence_guard_checks[
        "evidence_latest_record_guard_keys_match_expected_schema"
    ]["actual"] == list(payload["evidence_context"]["latest_record_guard"])
    assert evidence_guard_checks["evidence_latest_record_guard_status_is_ok"] == {
        "name": "evidence_latest_record_guard_status_is_ok",
        "passed": True,
        "expected": "ok",
        "actual": "ok",
    }
    assert evidence_guard_checks["evidence_latest_record_guard_status_is_ok"][
        "actual"
    ] == payload["evidence_context"]["latest_record_guard"]["status"]
    assert evidence_guard_checks[
        "evidence_latest_record_guard_check_names_match_expected_schema"
    ] == {
        "name": "evidence_latest_record_guard_check_names_match_expected_schema",
        "passed": True,
        "expected": expected_latest_record_guard_check_names,
        "actual": expected_latest_record_guard_check_names,
    }
    assert evidence_guard_checks[
        "evidence_latest_record_guard_checks_all_passed"
    ] == {
        "name": "evidence_latest_record_guard_checks_all_passed",
        "passed": True,
        "expected": True,
        "actual": expected_latest_record_guard_passes,
    }
    assert evidence_guard_checks[
        "evidence_latest_record_guard_checks_all_passed"
    ]["actual"] == latest_record_guard_passes
    assert source_summary in reasons["items"]
    assert f"- {source_summary}" in payload["text"]
    assert selected_label_summary in reasons["items"]
    assert f"- {selected_label_summary}" in payload["text"]
    assert prompt_contract == {
        "numeric_authority": expected_prompt_identity["numeric_authority"],
        "llm_role": expected_prompt_identity["llm_role"],
        "must_include": expected_prompt_terms,
    }
    assert payload["report_intent"] == "pre_market_swing_report"
    assert payload["report_intent"] == report_intent_contract["name"]
    assert report_intent_contract == expected_report_intent_contract
    assert section_titles == expected_report_sections
    assert report_contract_guard_checks["required_sections_present"] == {
        "name": "required_sections_present",
        "passed": True,
        "expected": expected_report_sections,
        "actual": expected_report_sections,
    }
    assert report_contract_guard_checks["intent_required_sections_present"] == {
        "name": "intent_required_sections_present",
        "passed": True,
        "expected": expected_report_sections,
        "actual": expected_report_sections,
    }
    assert report_contract_guard_checks["report_sections_match_intent_order"] == {
        "name": "report_sections_match_intent_order",
        "passed": True,
        "expected": expected_report_sections,
        "actual": expected_report_sections,
    }
    assert report_contract_guard_checks["report_text_sections_match_intent_order"] == {
        "name": "report_text_sections_match_intent_order",
        "passed": True,
        "expected": expected_report_sections,
        "actual": expected_text_order_actual,
    }
    assert all(
        position >= 0 for position in expected_text_section_positions.values()
    )
    assert report_contract_guard_checks["telegram_required_sections_match_intent"] == {
        "name": "telegram_required_sections_match_intent",
        "passed": True,
        "expected": expected_report_sections,
        "actual": expected_report_sections,
    }
    assert "report_text_sections_match_intent_order" in (
        report_contract_guard_checks[
            "report_contract_guard_check_names_match_expected_schema"
        ]["expected"]
    )
    assert "telegram_required_sections_match_intent" in (
        report_contract_guard_checks[
            "report_contract_guard_check_keys_match_expected_schema"
        ]["expected"]["default_check_names"]
    )
    assert f"Decision: {latest_report['action']}" in payload["text"]
    assert (
        f"Confidence: {payload['confidence_label']} ({latest_report['confidence']})"
        in payload["text"]
    )
    assert f"Score: {latest_report['final_score']}" in payload["text"]
    assert report_contract_guard_checks[
        "delivery_numeric_authority_is_latest_signal_report"
    ] == {
        "name": "delivery_numeric_authority_is_latest_signal_report",
        "passed": True,
        "expected": "latest_signal_report",
        "actual": "latest_signal_report",
    }
    assert report_contract_guard_checks["telegram_text_fits_single_message"] == {
        "name": "telegram_text_fits_single_message",
        "passed": True,
        "expected_max_chars": 3900,
        "actual_chars": len(payload["text"]),
    }
    assert report_contract_guard_checks[
        "report_telegram_max_chars_matches_expected"
    ] == {
        "name": "report_telegram_max_chars_matches_expected",
        "passed": True,
        "expected": 3900,
        "actual": 3900,
    }
    assert report_contract_guard_checks[
        "report_text_reflects_latest_signal_numeric_fields"
    ] == {
        "name": "report_text_reflects_latest_signal_numeric_fields",
        "passed": True,
        "expected": {
            "action": latest_report["action"],
            "confidence": latest_report["confidence"],
            "final_score": latest_report["final_score"],
        },
        "actual": expected_numeric_field_presence,
    }
    assert "delivery_numeric_authority_is_latest_signal_report" in (
        report_contract_guard_checks[
            "report_contract_guard_check_names_match_expected_schema"
        ]["expected"]
    )
    assert "telegram_text_fits_single_message" in (
        report_contract_guard_checks[
            "report_contract_guard_check_keys_match_expected_schema"
        ]["expected"]["special_check_keys"]
    )
    assert report_contract_guard_checks["report_intent_is_supported"] == {
        "name": "report_intent_is_supported",
        "passed": True,
        "expected": delivery_contract["cron_intents"],
        "actual": "pre_market_swing_report",
    }
    assert report_contract_guard_checks[
        "report_intent_contract_keys_match_expected_schema"
    ] == {
        "name": "report_intent_contract_keys_match_expected_schema",
        "passed": True,
        "expected": ["name", "schedule_hint", "decision_focus", "required_sections"],
        "actual": ["name", "schedule_hint", "decision_focus", "required_sections"],
    }
    assert report_contract_guard_checks[
        "report_intent_contract_matches_registry"
    ] == {
        "name": "report_intent_contract_matches_registry",
        "passed": True,
        "expected": expected_report_intent_contract,
        "actual": expected_report_intent_contract,
    }
    assert report_contract_guard_checks["prompt_must_include_is_covered"] == {
        "name": "prompt_must_include_is_covered",
        "passed": True,
        "expected": expected_prompt_terms,
        "actual": expected_prompt_terms,
    }
    assert report_contract_guard_checks[
        "report_prompt_must_include_matches_intent_terms"
    ] == {
        "name": "report_prompt_must_include_matches_intent_terms",
        "passed": True,
        "expected": expected_prompt_terms,
        "actual": expected_prompt_terms,
    }
    assert report_contract_guard_checks[
        "report_prompt_contract_keys_match_expected_schema"
    ] == {
        "name": "report_prompt_contract_keys_match_expected_schema",
        "passed": True,
        "expected": ["numeric_authority", "llm_role", "must_include"],
        "actual": ["numeric_authority", "llm_role", "must_include"],
    }
    assert report_contract_guard_checks[
        "report_prompt_contract_identity_matches_expected"
    ] == {
        "name": "report_prompt_contract_identity_matches_expected",
        "passed": True,
        "expected": expected_prompt_identity,
        "actual": expected_prompt_identity,
    }
    assert "report_prompt_contract_identity_matches_expected" in (
        report_contract_guard_checks[
            "report_contract_guard_check_names_match_expected_schema"
        ]["expected"]
    )
    assert "report_intent_contract_matches_registry" in (
        report_contract_guard_checks[
            "report_contract_guard_check_keys_match_expected_schema"
        ]["expected"]["default_check_names"]
    )
    assert delivery_preview["guard"]["status"] == "ok"
    assert telegram_preview["schema_version"] == "telegram_report_format.v1"
    assert telegram_preview["network_call"] is False
    assert telegram_preview["send_call"] is False
    assert telegram_preview["message_count"] == len(telegram_preview["chunks"])
    assert (
        telegram_preview["section_separator"].join(
            chunk["text"] for chunk in telegram_preview["chunks"]
        )
        == payload["text"]
    )
    assert delivery_preview_guard_checks[
        "delivery_preview_has_no_network_side_effect"
    ] == {
        "name": "delivery_preview_has_no_network_side_effect",
        "passed": True,
        "expected": False,
        "actual": {"hermes": False, "telegram": False},
    }
    assert delivery_preview_guard_checks[
        "delivery_preview_has_no_send_side_effect"
    ] == {
        "name": "delivery_preview_has_no_send_side_effect",
        "passed": True,
        "expected": False,
        "actual": {"hermes": False, "telegram": False},
    }
    assert (
        delivery_preview_guard_checks[
            "delivery_preview_guard_check_names_match_expected_schema"
        ]["passed"]
        is True
    )
    assert (
        "delivery_preview_has_no_network_side_effect"
        in delivery_preview_guard_checks[
            "delivery_preview_guard_check_names_match_expected_schema"
        ]["expected"]
    )
    assert (
        "delivery_preview_has_no_send_side_effect"
        in delivery_preview_guard_checks[
            "delivery_preview_guard_check_keys_match_expected_schema"
        ]["expected"]["default_check_names"]
    )
    assert delivery_preview_guard_checks[
        "delivery_preview_payload_keys_match_expected_schema"
    ]["actual"]["telegram_chunk_keys"] == [
        ["index", "chars", "text"] for _chunk in telegram_preview["chunks"]
    ]
    assert delivery_contract["cron_intents"] == [
        "pre_market_swing_report",
        "intraday_risk_watch",
        "post_market_review",
    ]
    assert delivery_channels["hermes"]["network_call"] is False
    assert delivery_channels["hermes"]["numeric_authority"] == "latest_signal_report"
    assert telegram_contract["schema_version"] == "telegram_report_format.v1"
    assert telegram_contract["network_call"] is False
    assert telegram_contract["send_call"] is False
    assert (
        telegram_contract["required_sections"]
        == payload["report_intent_contract"]["required_sections"]
    )
    assert report_contract_guard_checks[
        "delivery_contract_has_no_network_side_effect"
    ] == {
        "name": "delivery_contract_has_no_network_side_effect",
        "passed": True,
        "expected": False,
        "actual": {"hermes": False, "telegram": False},
    }
    assert report_contract_guard_checks[
        "delivery_contract_has_no_send_side_effect"
    ] == {
        "name": "delivery_contract_has_no_send_side_effect",
        "passed": True,
        "expected": False,
        "actual": {"hermes": False, "telegram": False},
    }
    assert report_contract_guard_checks[
        "delivery_contract_keys_match_expected_schema"
    ] == {
        "name": "delivery_contract_keys_match_expected_schema",
        "passed": True,
        "expected": expected_delivery_contract_schema,
        "actual": expected_delivery_contract_schema,
    }
    assert report_contract_guard_checks[
        "delivery_channel_formats_match_expected"
    ] == {
        "name": "delivery_channel_formats_match_expected",
        "passed": True,
        "expected": expected_delivery_channel_formats,
        "actual": expected_delivery_channel_formats,
    }
    assert report_contract_guard_checks[
        "report_telegram_schema_version_matches_expected"
    ] == {
        "name": "report_telegram_schema_version_matches_expected",
        "passed": True,
        "expected": "telegram_report_format.v1",
        "actual": "telegram_report_format.v1",
    }
    assert report_contract_guard_checks[
        "report_telegram_chunking_contract_matches_expected"
    ] == {
        "name": "report_telegram_chunking_contract_matches_expected",
        "passed": True,
        "expected": expected_telegram_chunking_contract,
        "actual": expected_telegram_chunking_contract,
    }
    assert "delivery_contract_has_no_network_side_effect" in (
        report_contract_guard_checks[
            "report_contract_guard_check_names_match_expected_schema"
        ]["expected"]
    )
    assert "delivery_contract_keys_match_expected_schema" in (
        report_contract_guard_checks[
            "report_contract_guard_check_keys_match_expected_schema"
        ]["expected"]["default_check_names"]
    )
    assert payload["report_contract_guard"]["status"] == "ok"
    assert report_contract_guard_checks[
        "report_text_reflects_source_repository_summary"
    ] == {
        "name": "report_text_reflects_source_repository_summary",
        "passed": True,
        "expected": source_summary,
        "actual": source_summary,
    }
    assert report_contract_guard_checks[
        "report_text_reflects_label_status_summary"
    ] == {
        "name": "report_text_reflects_label_status_summary",
        "passed": True,
        "expected": selected_label_summary,
        "actual": selected_label_summary,
    }
    assert "report_text_reflects_source_repository_summary" in report_contract_guard_checks[
        "report_contract_guard_check_names_match_expected_schema"
    ]["expected"]
    assert "report_text_reflects_label_status_summary" in report_contract_guard_checks[
        "report_contract_guard_check_keys_match_expected_schema"
    ]["expected"]["default_check_names"]
    assert report_payload_guard_checks[
        "report_payload_source_repository_ref_keys_match_expected_schema"
    ] == {
        "name": "report_payload_source_repository_ref_keys_match_expected_schema",
        "passed": True,
        "expected": ["storage", "db_required", "filters"],
        "actual": ["storage", "db_required", "filters"],
    }
    assert report_payload_guard_checks[
        "report_payload_source_repository_ref_is_path_free"
    ] == {
        "name": "report_payload_source_repository_ref_is_path_free",
        "passed": True,
        "expected": expected_source_repository_ref_path_free,
        "actual": expected_source_repository_ref_path_free,
    }
    assert report_payload_guard_checks[
        "report_payload_source_signal_ref_keys_match_expected_schema"
    ] == {
        "name": "report_payload_source_signal_ref_keys_match_expected_schema",
        "passed": True,
        "expected": ["signal_id", "run_id", "config_hash"],
        "actual": ["signal_id", "run_id", "config_hash"],
    }
    assert report_payload_guard_checks[
        "report_payload_source_signal_ref_matches_report_identity"
    ] == {
        "name": "report_payload_source_signal_ref_matches_report_identity",
        "passed": True,
        "expected": expected_source_signal_ref_identity,
        "actual": expected_source_signal_ref_identity,
    }
    assert report_payload_guard_checks[
        "report_payload_source_signal_ref_values_have_traceable_format"
    ] == {
        "name": "report_payload_source_signal_ref_values_have_traceable_format",
        "passed": True,
        "expected": expected_source_signal_ref_traceable_format,
        "actual": expected_source_signal_ref_traceable_format,
    }
    assert report_payload_guard_checks[
        "report_payload_source_signal_ref_config_hash_digest_is_sha256"
    ] == {
        "name": "report_payload_source_signal_ref_config_hash_digest_is_sha256",
        "passed": True,
        "expected": expected_source_signal_ref_config_hash_digest,
        "actual": expected_source_signal_ref_config_hash_digest,
    }
    assert report_payload_guard_checks["report_payload_intent_matches_contract"] == {
        "name": "report_payload_intent_matches_contract",
        "passed": True,
        "expected": expected_report_intent_contract["name"],
        "actual": "pre_market_swing_report",
    }
    assert "report_payload_intent_matches_contract" in (
        report_payload_guard_checks[
            "report_payload_guard_check_names_match_expected_schema"
        ]["expected"]
    )
    assert report_payload_guard_checks[
        "report_payload_guard_check_keys_match_expected_schema"
    ]["actual"]["report_payload_intent_matches_contract"] == [
        "name",
        "passed",
        "expected",
        "actual",
    ]
    assert report_payload_guard_checks[
        "report_payload_top_level_identity_matches_latest_signal_report"
    ] == {
        "name": "report_payload_top_level_identity_matches_latest_signal_report",
        "passed": True,
        "expected": expected_top_level_identity,
        "actual": expected_top_level_identity,
    }
    assert "report_payload_top_level_identity_matches_latest_signal_report" in (
        report_payload_guard_checks[
            "report_payload_guard_check_names_match_expected_schema"
        ]["expected"]
    )
    assert payload["schema_version"] == "hermes_report.v1"
    assert report_payload_guard_checks[
        "report_payload_schema_version_matches_expected"
    ] == {
        "name": "report_payload_schema_version_matches_expected",
        "passed": True,
        "expected": "hermes_report.v1",
        "actual": "hermes_report.v1",
    }
    assert "report_payload_schema_version_matches_expected" in (
        report_payload_guard_checks[
            "report_payload_guard_check_names_match_expected_schema"
        ]["expected"]
    )
    assert report_payload_guard_checks[
        "report_payload_guard_check_keys_match_expected_schema"
    ]["actual"]["report_payload_schema_version_matches_expected"] == [
        "name",
        "passed",
        "expected",
        "actual",
    ]
    assert payload["live_data_required"] is False
    assert report_payload_guard_checks[
        "report_payload_live_data_required_matches_expected"
    ] == {
        "name": "report_payload_live_data_required_matches_expected",
        "passed": True,
        "expected": False,
        "actual": False,
    }
    assert "report_payload_live_data_required_matches_expected" in (
        report_payload_guard_checks[
            "report_payload_guard_check_names_match_expected_schema"
        ]["expected"]
    )
    assert report_payload_guard_checks[
        "report_payload_guard_check_keys_match_expected_schema"
    ]["actual"]["report_payload_live_data_required_matches_expected"] == [
        "name",
        "passed",
        "expected",
        "actual",
    ]
    assert report_payload_guard_checks["report_payload_keys_match_expected_schema"] == {
        "name": "report_payload_keys_match_expected_schema",
        "passed": True,
        "expected": expected_payload_keys,
        "actual": expected_payload_keys,
    }
    assert list(payload["report_payload_guard"]) == ["status", "checks"]
    assert report_payload_guard_checks[
        "report_payload_guard_keys_match_expected_schema"
    ] == {
        "name": "report_payload_guard_keys_match_expected_schema",
        "passed": True,
        "expected": ["status", "checks"],
        "actual": ["status", "checks"],
    }
    assert report_payload_guard_checks[
        "report_payload_guard_keys_match_expected_schema"
    ]["actual"] == list(payload["report_payload_guard"])
    assert "report_payload_guard_keys_match_expected_schema" in (
        report_payload_guard_checks[
            "report_payload_guard_check_names_match_expected_schema"
        ]["expected"]
    )
    payload_check_names = report_payload_guard_checks[
        "report_payload_guard_check_names_match_expected_schema"
    ]
    assert payload_check_names == {
        "name": "report_payload_guard_check_names_match_expected_schema",
        "passed": True,
        "expected": expected_payload_check_names,
        "actual": expected_payload_check_names,
    }
    assert payload_check_names["actual"] == actual_payload_check_names
    assert "report_payload_source_repository_ref_keys_match_expected_schema" in (
        payload_check_names["expected"]
    )
    assert "report_payload_source_repository_ref_is_path_free" in (
        payload_check_names["expected"]
    )
    assert payload["source_repository_ref"] == source_repository_ref
    assert "source_repository_ref" in report_payload_guard_checks[
        "report_payload_keys_match_expected_schema"
    ]["actual"]
    assert "latest_record_guard" in report_payload_guard_checks[
        "report_payload_keys_match_expected_schema"
    ]["actual"]
    expected_default_check_keys = ["name", "passed", "expected", "actual"]
    expected_payload_check_keys = {
        check_name: expected_default_check_keys
        for check_name in expected_payload_check_names
    }
    payload_check_keys = report_payload_guard_checks[
        "report_payload_guard_check_keys_match_expected_schema"
    ]["actual"]
    assert payload_check_keys == actual_payload_check_keys
    assert payload_check_keys[
        "report_payload_source_repository_ref_keys_match_expected_schema"
    ] == expected_default_check_keys
    assert payload_check_keys[
        "report_payload_source_repository_ref_is_path_free"
    ] == expected_default_check_keys
    assert report_payload_guard_checks[
        "report_payload_guard_check_keys_match_expected_schema"
    ] == {
        "name": "report_payload_guard_check_keys_match_expected_schema",
        "passed": True,
        "expected": expected_default_check_keys,
        "actual": expected_payload_check_keys,
    }
    assert all(
        check_keys == expected_default_check_keys
        for check_keys in payload_check_keys.values()
    )
    assert payload_check_keys[
        "report_payload_keys_match_expected_schema"
    ] == expected_default_check_keys
    assert payload_check_keys[
        "report_payload_guard_check_keys_match_expected_schema"
    ] == expected_default_check_keys
    assert report_payload_guard_checks[
        "report_payload_optional_context_statuses_are_ok"
    ] == {
        "name": "report_payload_optional_context_statuses_are_ok",
        "passed": True,
        "expected": {},
        "actual": {},
    }
    assert report_payload_guard_checks[
        "report_payload_optional_context_guards_are_ok"
    ] == {
        "name": "report_payload_optional_context_guards_are_ok",
        "passed": True,
        "expected": {},
        "actual": {},
    }
    assert report_payload_guard_checks[
        "report_payload_nested_guard_statuses_are_ok"
    ] == {
        "name": "report_payload_nested_guard_statuses_are_ok",
        "passed": True,
        "expected": expected_nested_guard_statuses,
        "actual": expected_nested_guard_statuses,
    }
    assert report_payload_guard_checks[
        "report_payload_nested_guard_statuses_are_ok"
    ]["expected"] == actual_nested_guard_statuses
    assert report_payload_guard_checks[
        "report_payload_nested_guard_statuses_are_ok"
    ]["actual"] == actual_nested_guard_statuses
    assert "report_payload_nested_guard_statuses_are_ok" in report_payload_guard_checks[
        "report_payload_guard_check_names_match_expected_schema"
    ]["expected"]
    assert "latest_record_guard" in report_payload_guard_checks[
        "report_payload_nested_guard_statuses_are_ok"
    ]["actual"]
    assert payload["report_payload_guard"]["status"] == "ok"
    assert str(database_path) not in iter_nested_strings(label_status)
    assert str(database_path) not in iter_nested_strings(evidence_contract)
    assert str(database_path) not in iter_nested_strings(evidence_context)
    assert str(database_path) not in iter_nested_strings(evidence_label_status)
    assert str(database_path) not in iter_nested_strings(payload["source_signal_ref"])
    assert str(database_path) not in iter_nested_strings(payload["source_repository_ref"])
    assert str(database_path) not in iter_nested_strings(latest_record_guard)
    assert str(database_path) not in iter_nested_strings(evidence_guard_checks)
    assert str(database_path) not in iter_nested_strings(prompt_contract)
    assert str(database_path) not in iter_nested_strings(report_intent_contract)
    assert str(database_path) not in iter_nested_strings(delivery_contract)
    assert str(database_path) not in iter_nested_strings(delivery_preview)
    assert str(database_path) not in iter_nested_strings(report_contract_guard_checks)
    assert str(database_path) not in iter_nested_strings(report_payload_guard_checks)
    assert str(database_path) not in iter_nested_strings(reasons)
    assert str(database_path) not in payload["text"]
    assert all(
        ".sqlite" not in value.lower()
        for value in iter_nested_strings(label_status)
    )
    assert all(
        ".sqlite" not in value.lower()
        for value in iter_nested_strings(evidence_contract)
    )
    assert all(
        ".sqlite" not in value.lower()
        for value in iter_nested_strings(evidence_context)
    )
    assert all(
        ".sqlite" not in value.lower()
        for value in iter_nested_strings(evidence_label_status)
    )
    assert all(
        ".sqlite" not in value.lower()
        for value in iter_nested_strings(payload["source_signal_ref"])
    )
    assert all(
        ".sqlite" not in value.lower()
        for value in iter_nested_strings(payload["source_repository_ref"])
    )
    assert all(
        ".sqlite" not in value.lower()
        for value in iter_nested_strings(latest_record_guard)
    )
    assert all(
        ".sqlite" not in value.lower()
        for value in iter_nested_strings(evidence_guard_checks)
    )
    assert all(
        ".sqlite" not in value.lower()
        for value in iter_nested_strings(prompt_contract)
    )
    assert all(
        ".sqlite" not in value.lower()
        for value in iter_nested_strings(report_intent_contract)
    )
    assert all(
        ".sqlite" not in value.lower()
        for value in iter_nested_strings(delivery_contract)
    )
    assert all(
        ".sqlite" not in value.lower()
        for value in iter_nested_strings(delivery_preview)
    )
    assert all(
        ".sqlite" not in value.lower()
        for value in iter_nested_strings(report_contract_guard_checks)
    )
    assert all(
        ".sqlite" not in value.lower()
        for value in iter_nested_strings(report_payload_guard_checks)
    )
    assert all(
        ".sqlite" not in value.lower()
        for value in iter_nested_strings(reasons)
    )


def test_latest_signal_report_repository_source_filters_by_underlying(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    database_path = tmp_path / "halo_swing.sqlite"
    qqq_signal = {
        **reporting.score_leverage_swing("TQQQ"),
        "signal_id": "sig_report_repo_tqqq_qqq",
        "run_id": "run_report_repo_tqqq_qqq",
        "created_at": "2026-05-20T12:00:00Z",
    }
    ndx_signal = {
        **reporting.score_leverage_swing("TQQQ"),
        "signal_id": "sig_report_repo_tqqq_soxx",
        "run_id": "run_report_repo_tqqq_soxx",
        "created_at": "2026-05-20T13:00:00Z",
        "underlying": "SOXX",
    }
    record_signal(signal=qqq_signal, database_path=str(database_path))
    record_signal(signal=ndx_signal, database_path=str(database_path))
    selected_label = label_signal_outcome(
        signal_id=qqq_signal["signal_id"],
        database_path=str(database_path),
        price_path=[500.0, 560.0],
        time_barrier_days=2,
    )
    label_signal_outcome(
        signal_id=ndx_signal["signal_id"],
        database_path=str(database_path),
        price_path=[500.0, 450.0],
        time_barrier_days=3,
    )

    def unexpected_score_call(*_args: object, **_kwargs: object) -> dict[str, object]:
        raise AssertionError("repository-backed report must not rescore the signal")

    monkeypatch.setattr(reporting, "score_leverage_swing", unexpected_score_call)
    payload = generate_latest_signal_report(
        asset="TQQQ",
        underlying=" qqq ",
        database_path=str(database_path),
    )
    reasons = next(
        section for section in payload["sections"] if section["title"] == "Reasons"
    )
    cautions = next(
        section["items"]
        for section in payload["sections"]
        if section["title"] == "Cautions"
    )
    report_payload_guard_checks = {
        check["name"]: check for check in payload["report_payload_guard"]["checks"]
    }
    actual_payload_check_names = [
        check["name"] for check in payload["report_payload_guard"]["checks"]
    ]
    actual_payload_check_keys = {
        check["name"]: list(check)
        for check in payload["report_payload_guard"]["checks"]
    }
    report_contract_guard_checks = {
        check["name"]: check for check in payload["report_contract_guard"]["checks"]
    }
    latest_record_guard = payload["latest_record_guard"]
    latest_record_guard_checks = {
        check["name"]: check for check in latest_record_guard["checks"]
    }
    evidence_guard_checks = {
        check["name"]: check for check in payload["evidence_guard"]["checks"]
    }
    delivery_preview = payload["delivery_preview"]
    telegram_preview = delivery_preview["channels"]["telegram"]
    delivery_preview_guard_checks = {
        check["name"]: check for check in delivery_preview["guard"]["checks"]
    }
    delivery_contract = payload["delivery_contract"]
    delivery_channels = delivery_contract["channels"]
    telegram_contract = delivery_channels["telegram"]
    prompt_contract = payload["prompt_contract"]
    report_intent_contract = payload["report_intent_contract"]
    evidence_contract = payload["evidence_contract"]
    evidence_context = payload["evidence_context"]
    expected_latest_record_guard_check_names = [
        "latest_record_source_repository_ref_keys_match_expected_schema",
        "latest_record_source_repository_ref_is_path_free",
        "latest_record_source_repository_ref_matches_top_level_source",
    ]
    source_summary = (
        "Repository source: sqlite_signal_repository; "
        "db_required=true; "
        "filters asset=TQQQ underlying=QQQ timeframe=swing_3d_10d"
    )
    source_repository_ref = {
        "storage": "sqlite_signal_repository",
        "db_required": True,
        "filters": {
            "asset": "TQQQ",
            "underlying": "QQQ",
            "timeframe": "swing_3d_10d",
        },
    }
    expected_source_repository_ref_path_free = {
        "omits_ledger_ref": True,
        "omits_ledger_path": True,
        "omits_database_path": True,
        "omits_absolute_or_sqlite_paths": True,
    }
    expected_source_signal_ref_identity = {
        "signal_id": qqq_signal["signal_id"],
        "config_hash": qqq_signal["config_hash"],
        "run_id_nonempty": True,
    }
    expected_source_signal_ref_traceable_format = {
        "signal_id_nonempty": True,
        "run_id_nonempty": True,
        "config_hash_sha256_prefix": True,
    }
    expected_source_signal_ref_config_hash_digest = {
        "config_hash_digest_length": 64,
        "config_hash_digest_hex": True,
    }
    selected_label_summary = (
        f"Stored label: outcome={selected_label['outcome']}; "
        f"realized_r={selected_label['realized_r']}; "
        f"first_barrier_hit={selected_label['first_barrier_hit']}; "
        "time_barrier_days=2"
    )
    expected_nested_guard_statuses = {
        "delivery_preview.guard": "ok",
        "evidence_guard": "ok",
        "report_contract_guard": "ok",
        "latest_record_guard": "ok",
    }
    actual_nested_guard_statuses = {
        "delivery_preview.guard": delivery_preview["guard"]["status"],
        "evidence_guard": payload["evidence_guard"]["status"],
        "report_contract_guard": payload["report_contract_guard"]["status"],
        "latest_record_guard": latest_record_guard["status"],
    }
    expected_top_level_identity = {
        "as_of": qqq_signal["created_at"],
        "asset": "TQQQ",
        "underlying": "QQQ",
        "timeframe": qqq_signal["timeframe"],
        "action": qqq_signal["action"],
        "confidence_label": payload["confidence_label"],
    }
    expected_payload_keys = [
        "schema_version",
        "as_of",
        "asset",
        "underlying",
        "timeframe",
        "action",
        "confidence_label",
        "report_intent",
        "latest_signal_report",
        "sections",
        "text",
        "prompt_contract",
        "delivery_contract",
        "delivery_preview",
        "evidence_contract",
        "evidence_context",
        "evidence_guard",
        "report_intent_contract",
        "report_contract_guard",
        "source_signal_ref",
        "source_repository_ref",
        "latest_record_guard",
        "live_data_required",
        "report_payload_guard",
    ]
    expected_payload_check_names = [
        "report_payload_schema_version_matches_expected",
        "report_payload_live_data_required_matches_expected",
        "report_payload_keys_match_expected_schema",
        "report_payload_source_signal_ref_keys_match_expected_schema",
        "report_payload_source_signal_ref_matches_report_identity",
        "report_payload_source_signal_ref_values_have_traceable_format",
        "report_payload_source_signal_ref_config_hash_digest_is_sha256",
        "report_payload_source_repository_ref_keys_match_expected_schema",
        "report_payload_source_repository_ref_is_path_free",
        "report_payload_intent_matches_contract",
        "report_payload_top_level_identity_matches_latest_signal_report",
        "report_payload_nested_guard_statuses_are_ok",
        "report_payload_optional_context_statuses_are_ok",
        "report_payload_optional_context_guards_are_ok",
        "report_payload_guard_check_names_match_expected_schema",
        "report_payload_guard_keys_match_expected_schema",
        "report_payload_guard_check_keys_match_expected_schema",
    ]
    expected_delivery_contract_schema = {
        "contract_keys": ["channels", "cron_intents"],
        "channel_names": ["hermes", "telegram"],
        "hermes_channel_keys": ["format", "network_call", "numeric_authority"],
        "telegram_channel_keys": [
            "schema_version",
            "format",
            "network_call",
            "max_chars",
            "required_sections",
            "overflow_policy",
            "section_separator",
            "chunk_indexing",
            "send_call",
        ],
    }
    expected_delivery_channel_formats = {
        "hermes": "structured_json_plus_text",
        "telegram": "plain_text",
    }
    expected_telegram_chunking_contract = {
        "overflow_policy": "split_on_section_boundary",
        "section_separator": "\n\n",
        "chunk_indexing": "1_based",
    }
    expected_report_sections = [
        "Target",
        "Decision",
        "Reasons",
        "Entry",
        "Stop",
        "Take Profit",
        "Cautions",
    ]
    expected_prompt_terms = [
        "action",
        "confidence",
        "entry",
        "stop",
        "take_profit",
        "risk",
        "data_warnings",
    ]
    expected_prompt_identity = {
        "numeric_authority": "Use MCP numeric fields as source of truth.",
        "llm_role": "Summarize conflicts, caveats, and final wording only.",
    }
    expected_evidence_contract = {
        "max_reason_summary_chars": 260,
        "max_evidence_summary_chars": 700,
        "max_conflict_flags": 8,
        "required_conflict_fields": ["name", "severity", "status", "details"],
    }
    expected_evidence_special_check_keys = {
        "reason_summary_within_limit": [
            "name",
            "passed",
            "expected_max_chars",
            "actual_chars",
        ],
        "evidence_summary_within_limit": [
            "name",
            "passed",
            "expected_max_chars",
            "actual_chars",
        ],
        "conflict_flags_within_limit": [
            "name",
            "passed",
            "expected_max",
            "actual_count",
        ],
    }
    expected_report_intent_contract = {
        "name": "pre_market_swing_report",
        "schedule_hint": "weekday_pre_market",
        "decision_focus": "new_swing_entry_and_watchlist",
        "required_sections": expected_report_sections,
    }
    section_titles = [section["title"] for section in payload["sections"]]
    expected_text_section_positions = {
        title: payload["text"].find(f"{title}:")
        for title in expected_report_sections
    }
    expected_text_order_actual = {
        "found_sections": expected_report_sections,
        "positions_ascending": True,
        "positions": expected_text_section_positions,
    }
    latest_report = payload["latest_signal_report"]
    expected_numeric_field_presence = {
        "decision_line_present": True,
        "confidence_line_present": True,
        "score_line_present": True,
    }
    selected_component_scores = {
        key: float(value)
        for key, value in qqq_signal["component_scores"].items()
        if key != "event_risk"
    }
    strongest_component = max(
        selected_component_scores,
        key=selected_component_scores.get,
    )
    weakest_component = min(
        selected_component_scores,
        key=selected_component_scores.get,
    )
    expected_component_extremes = {
        "strongest": {
            "name": strongest_component,
            "score": round(selected_component_scores[strongest_component], 4),
        },
        "weakest": {
            "name": weakest_component,
            "score": round(selected_component_scores[weakest_component], 4),
        },
        "spread": round(
            selected_component_scores[strongest_component]
            - selected_component_scores[weakest_component],
            4,
        ),
    }

    assert evidence_contract == expected_evidence_contract
    assert evidence_context["source_repository_ref"] == source_repository_ref
    assert evidence_context["component_extremes"] == expected_component_extremes
    assert evidence_context["component_extremes"]["spread"] > 0
    assert evidence_context["component_extremes"]["strongest"]["name"] in (
        selected_component_scores
    )
    assert evidence_context["component_extremes"]["weakest"]["name"] in (
        selected_component_scores
    )
    assert evidence_context["component_extremes"]["strongest"]["name"] != "event_risk"
    assert evidence_context["component_extremes"]["weakest"]["name"] != "event_risk"
    assert (
        len(evidence_context["reason_summary"])
        <= evidence_contract["max_reason_summary_chars"]
    )
    assert (
        len(evidence_context["evidence_summary"])
        <= evidence_contract["max_evidence_summary_chars"]
    )
    assert (
        len(evidence_context["conflict_flags"])
        <= evidence_contract["max_conflict_flags"]
    )
    assert all(
        all(
            field in flag
            for field in evidence_contract["required_conflict_fields"]
        )
        for flag in evidence_context["conflict_flags"]
    )
    assert evidence_guard_checks["reason_summary_within_limit"] == {
        "name": "reason_summary_within_limit",
        "passed": True,
        "expected_max_chars": evidence_contract["max_reason_summary_chars"],
        "actual_chars": len(latest_report["reason_summary"]),
    }
    assert evidence_guard_checks["evidence_summary_within_limit"] == {
        "name": "evidence_summary_within_limit",
        "passed": True,
        "expected_max_chars": evidence_contract["max_evidence_summary_chars"],
        "actual_chars": len(latest_report["evidence_summary"]),
    }
    assert evidence_guard_checks["conflict_flags_within_limit"] == {
        "name": "conflict_flags_within_limit",
        "passed": True,
        "expected_max": evidence_contract["max_conflict_flags"],
        "actual_count": len(evidence_context["conflict_flags"]),
    }
    assert evidence_guard_checks["conflict_flags_have_required_fields"] == {
        "name": "conflict_flags_have_required_fields",
        "passed": True,
        "expected": evidence_contract["required_conflict_fields"],
        "actual": [
            sorted(flag)
            for flag in evidence_context["conflict_flags"]
        ],
    }
    assert evidence_context["risk_warnings"]
    assert set(evidence_context["risk_warnings"]).issubset(cautions)
    assert all(
        flag["status"] == "acknowledged"
        for flag in evidence_context["conflict_flags"]
    )
    assert evidence_guard_checks["risk_warnings_reflected_in_cautions"] == {
        "name": "risk_warnings_reflected_in_cautions",
        "passed": True,
        "expected": evidence_context["risk_warnings"],
        "actual": cautions,
    }
    assert evidence_guard_checks["flagged_conflicts_are_acknowledged"] == {
        "name": "flagged_conflicts_are_acknowledged",
        "passed": True,
        "expected": "acknowledged",
        "actual": [
            flag["status"]
            for flag in evidence_context["conflict_flags"]
        ],
    }
    assert evidence_guard_checks[
        "evidence_source_repository_ref_keys_match_expected_schema"
    ] == {
        "name": "evidence_source_repository_ref_keys_match_expected_schema",
        "passed": True,
        "expected": ["storage", "db_required", "filters"],
        "actual": ["storage", "db_required", "filters"],
    }
    assert evidence_guard_checks["evidence_source_repository_ref_is_path_free"] == {
        "name": "evidence_source_repository_ref_is_path_free",
        "passed": True,
        "expected": {
            "omits_ledger_ref": True,
            "omits_ledger_path": True,
            "omits_database_path": True,
            "omits_absolute_or_sqlite_paths": True,
        },
        "actual": {
            "omits_ledger_ref": True,
            "omits_ledger_path": True,
            "omits_database_path": True,
            "omits_absolute_or_sqlite_paths": True,
        },
    }
    assert evidence_guard_checks[
        "evidence_guard_check_keys_match_expected_schema"
    ]["actual"]["special_check_keys"] == expected_evidence_special_check_keys
    assert "evidence_source_repository_ref_is_path_free" in evidence_guard_checks[
        "evidence_guard_check_names_match_expected_schema"
    ]["expected"]
    assert "conflict_flags_have_required_fields" in evidence_guard_checks[
        "evidence_guard_check_keys_match_expected_schema"
    ]["expected"]["default_check_names"]
    assert "risk_warnings_reflected_in_cautions" in evidence_guard_checks[
        "evidence_guard_check_names_match_expected_schema"
    ]["expected"]
    assert "flagged_conflicts_are_acknowledged" in evidence_guard_checks[
        "evidence_guard_check_keys_match_expected_schema"
    ]["expected"]["default_check_names"]
    assert payload["latest_signal_report"]["signal_id"] == qqq_signal["signal_id"]
    assert payload["latest_signal_report"]["underlying"] == "QQQ"
    label_status = payload["latest_signal_report"]["label_status"]
    assert label_status["schema_version"] == "signal_label_outcome.v1"
    assert label_status["signal_id"] == qqq_signal["signal_id"]
    assert label_status["outcome"] == selected_label["outcome"]
    assert label_status["realized_r"] == selected_label["realized_r"]
    assert label_status["first_barrier_hit"] == selected_label["first_barrier_hit"]
    assert label_status["labeled_at"] == selected_label["labeled_at"]
    assert label_status["time_barrier_days"] == selected_label["time_barrier_days"]
    assert label_status["live_data_required"] is False
    evidence_label_status = payload["evidence_context"]["label_status"]
    assert evidence_label_status == label_status
    assert evidence_guard_checks["label_status_reflected_in_evidence_context"] == {
        "name": "label_status_reflected_in_evidence_context",
        "passed": True,
        "expected": label_status,
        "actual": evidence_label_status,
    }
    assert "label_status_reflected_in_evidence_context" in evidence_guard_checks[
        "evidence_guard_check_names_match_expected_schema"
    ]["expected"]
    assert "label_status_reflected_in_evidence_context" in evidence_guard_checks[
        "evidence_guard_check_keys_match_expected_schema"
    ]["expected"]["default_check_names"]
    assert payload["source_signal_ref"] == {
        "signal_id": qqq_signal["signal_id"],
        "run_id": qqq_signal["run_id"],
        "config_hash": qqq_signal["config_hash"],
    }
    assert payload["source_repository_ref"] == source_repository_ref
    assert payload["evidence_context"]["latest_record_guard"] == latest_record_guard
    assert list(latest_record_guard) == ["status", "checks"]
    assert latest_record_guard["status"] == "ok"
    assert [check["name"] for check in latest_record_guard["checks"]] == (
        expected_latest_record_guard_check_names
    )
    expected_latest_record_guard_passes = [True, True, True]
    latest_record_guard_passes = [
        check["passed"] for check in latest_record_guard["checks"]
    ]
    assert latest_record_guard_passes == expected_latest_record_guard_passes
    assert latest_record_guard_checks[
        "latest_record_source_repository_ref_keys_match_expected_schema"
    ] == {
        "name": "latest_record_source_repository_ref_keys_match_expected_schema",
        "passed": True,
        "expected": ["storage", "db_required", "filters"],
        "actual": ["storage", "db_required", "filters"],
    }
    assert latest_record_guard_checks[
        "latest_record_source_repository_ref_matches_top_level_source"
    ] == {
        "name": "latest_record_source_repository_ref_matches_top_level_source",
        "passed": True,
        "expected": source_repository_ref,
        "actual": source_repository_ref,
    }
    assert latest_record_guard_checks[
        "latest_record_source_repository_ref_is_path_free"
    ] == {
        "name": "latest_record_source_repository_ref_is_path_free",
        "passed": True,
        "expected": expected_source_repository_ref_path_free,
        "actual": expected_source_repository_ref_path_free,
    }
    assert payload["evidence_guard"]["status"] == "ok"
    assert evidence_guard_checks[
        "evidence_latest_record_guard_keys_match_expected_schema"
    ] == {
        "name": "evidence_latest_record_guard_keys_match_expected_schema",
        "passed": True,
        "expected": ["status", "checks"],
        "actual": ["status", "checks"],
    }
    assert evidence_guard_checks[
        "evidence_latest_record_guard_keys_match_expected_schema"
    ]["actual"] == list(payload["evidence_context"]["latest_record_guard"])
    assert evidence_guard_checks["evidence_latest_record_guard_status_is_ok"] == {
        "name": "evidence_latest_record_guard_status_is_ok",
        "passed": True,
        "expected": "ok",
        "actual": "ok",
    }
    assert evidence_guard_checks["evidence_latest_record_guard_status_is_ok"][
        "actual"
    ] == payload["evidence_context"]["latest_record_guard"]["status"]
    assert evidence_guard_checks[
        "evidence_latest_record_guard_check_names_match_expected_schema"
    ] == {
        "name": "evidence_latest_record_guard_check_names_match_expected_schema",
        "passed": True,
        "expected": expected_latest_record_guard_check_names,
        "actual": expected_latest_record_guard_check_names,
    }
    assert evidence_guard_checks[
        "evidence_latest_record_guard_checks_all_passed"
    ] == {
        "name": "evidence_latest_record_guard_checks_all_passed",
        "passed": True,
        "expected": True,
        "actual": expected_latest_record_guard_passes,
    }
    assert evidence_guard_checks[
        "evidence_latest_record_guard_checks_all_passed"
    ]["actual"] == latest_record_guard_passes
    assert source_summary in reasons["items"]
    assert f"- {source_summary}" in payload["text"]
    assert selected_label_summary in reasons["items"]
    assert f"- {selected_label_summary}" in payload["text"]
    assert prompt_contract == {
        "numeric_authority": expected_prompt_identity["numeric_authority"],
        "llm_role": expected_prompt_identity["llm_role"],
        "must_include": expected_prompt_terms,
    }
    assert payload["report_intent"] == "pre_market_swing_report"
    assert payload["report_intent"] == report_intent_contract["name"]
    assert report_intent_contract == expected_report_intent_contract
    assert section_titles == expected_report_sections
    assert report_contract_guard_checks["required_sections_present"] == {
        "name": "required_sections_present",
        "passed": True,
        "expected": expected_report_sections,
        "actual": expected_report_sections,
    }
    assert report_contract_guard_checks["intent_required_sections_present"] == {
        "name": "intent_required_sections_present",
        "passed": True,
        "expected": expected_report_sections,
        "actual": expected_report_sections,
    }
    assert report_contract_guard_checks["report_sections_match_intent_order"] == {
        "name": "report_sections_match_intent_order",
        "passed": True,
        "expected": expected_report_sections,
        "actual": expected_report_sections,
    }
    assert report_contract_guard_checks["report_text_sections_match_intent_order"] == {
        "name": "report_text_sections_match_intent_order",
        "passed": True,
        "expected": expected_report_sections,
        "actual": expected_text_order_actual,
    }
    assert all(
        position >= 0 for position in expected_text_section_positions.values()
    )
    assert report_contract_guard_checks["telegram_required_sections_match_intent"] == {
        "name": "telegram_required_sections_match_intent",
        "passed": True,
        "expected": expected_report_sections,
        "actual": expected_report_sections,
    }
    assert "report_text_sections_match_intent_order" in (
        report_contract_guard_checks[
            "report_contract_guard_check_names_match_expected_schema"
        ]["expected"]
    )
    assert "telegram_required_sections_match_intent" in (
        report_contract_guard_checks[
            "report_contract_guard_check_keys_match_expected_schema"
        ]["expected"]["default_check_names"]
    )
    assert f"Decision: {latest_report['action']}" in payload["text"]
    assert (
        f"Confidence: {payload['confidence_label']} ({latest_report['confidence']})"
        in payload["text"]
    )
    assert f"Score: {latest_report['final_score']}" in payload["text"]
    assert report_contract_guard_checks[
        "delivery_numeric_authority_is_latest_signal_report"
    ] == {
        "name": "delivery_numeric_authority_is_latest_signal_report",
        "passed": True,
        "expected": "latest_signal_report",
        "actual": "latest_signal_report",
    }
    assert report_contract_guard_checks["telegram_text_fits_single_message"] == {
        "name": "telegram_text_fits_single_message",
        "passed": True,
        "expected_max_chars": 3900,
        "actual_chars": len(payload["text"]),
    }
    assert report_contract_guard_checks[
        "report_telegram_max_chars_matches_expected"
    ] == {
        "name": "report_telegram_max_chars_matches_expected",
        "passed": True,
        "expected": 3900,
        "actual": 3900,
    }
    assert report_contract_guard_checks[
        "report_text_reflects_latest_signal_numeric_fields"
    ] == {
        "name": "report_text_reflects_latest_signal_numeric_fields",
        "passed": True,
        "expected": {
            "action": latest_report["action"],
            "confidence": latest_report["confidence"],
            "final_score": latest_report["final_score"],
        },
        "actual": expected_numeric_field_presence,
    }
    assert "delivery_numeric_authority_is_latest_signal_report" in (
        report_contract_guard_checks[
            "report_contract_guard_check_names_match_expected_schema"
        ]["expected"]
    )
    assert "telegram_text_fits_single_message" in (
        report_contract_guard_checks[
            "report_contract_guard_check_keys_match_expected_schema"
        ]["expected"]["special_check_keys"]
    )
    assert report_contract_guard_checks["report_intent_is_supported"] == {
        "name": "report_intent_is_supported",
        "passed": True,
        "expected": delivery_contract["cron_intents"],
        "actual": "pre_market_swing_report",
    }
    assert report_contract_guard_checks[
        "report_intent_contract_keys_match_expected_schema"
    ] == {
        "name": "report_intent_contract_keys_match_expected_schema",
        "passed": True,
        "expected": ["name", "schedule_hint", "decision_focus", "required_sections"],
        "actual": ["name", "schedule_hint", "decision_focus", "required_sections"],
    }
    assert report_contract_guard_checks[
        "report_intent_contract_matches_registry"
    ] == {
        "name": "report_intent_contract_matches_registry",
        "passed": True,
        "expected": expected_report_intent_contract,
        "actual": expected_report_intent_contract,
    }
    assert report_contract_guard_checks["prompt_must_include_is_covered"] == {
        "name": "prompt_must_include_is_covered",
        "passed": True,
        "expected": expected_prompt_terms,
        "actual": expected_prompt_terms,
    }
    assert report_contract_guard_checks[
        "report_prompt_must_include_matches_intent_terms"
    ] == {
        "name": "report_prompt_must_include_matches_intent_terms",
        "passed": True,
        "expected": expected_prompt_terms,
        "actual": expected_prompt_terms,
    }
    assert report_contract_guard_checks[
        "report_prompt_contract_keys_match_expected_schema"
    ] == {
        "name": "report_prompt_contract_keys_match_expected_schema",
        "passed": True,
        "expected": ["numeric_authority", "llm_role", "must_include"],
        "actual": ["numeric_authority", "llm_role", "must_include"],
    }
    assert report_contract_guard_checks[
        "report_prompt_contract_identity_matches_expected"
    ] == {
        "name": "report_prompt_contract_identity_matches_expected",
        "passed": True,
        "expected": expected_prompt_identity,
        "actual": expected_prompt_identity,
    }
    assert "report_prompt_contract_identity_matches_expected" in (
        report_contract_guard_checks[
            "report_contract_guard_check_names_match_expected_schema"
        ]["expected"]
    )
    assert "report_intent_contract_matches_registry" in (
        report_contract_guard_checks[
            "report_contract_guard_check_keys_match_expected_schema"
        ]["expected"]["default_check_names"]
    )
    assert delivery_preview["guard"]["status"] == "ok"
    assert telegram_preview["schema_version"] == "telegram_report_format.v1"
    assert telegram_preview["network_call"] is False
    assert telegram_preview["send_call"] is False
    assert telegram_preview["message_count"] == len(telegram_preview["chunks"])
    assert (
        telegram_preview["section_separator"].join(
            chunk["text"] for chunk in telegram_preview["chunks"]
        )
        == payload["text"]
    )
    assert delivery_preview_guard_checks[
        "delivery_preview_has_no_network_side_effect"
    ] == {
        "name": "delivery_preview_has_no_network_side_effect",
        "passed": True,
        "expected": False,
        "actual": {"hermes": False, "telegram": False},
    }
    assert delivery_preview_guard_checks[
        "delivery_preview_has_no_send_side_effect"
    ] == {
        "name": "delivery_preview_has_no_send_side_effect",
        "passed": True,
        "expected": False,
        "actual": {"hermes": False, "telegram": False},
    }
    assert (
        delivery_preview_guard_checks[
            "delivery_preview_guard_check_names_match_expected_schema"
        ]["passed"]
        is True
    )
    assert (
        "delivery_preview_has_no_network_side_effect"
        in delivery_preview_guard_checks[
            "delivery_preview_guard_check_names_match_expected_schema"
        ]["expected"]
    )
    assert (
        "delivery_preview_has_no_send_side_effect"
        in delivery_preview_guard_checks[
            "delivery_preview_guard_check_keys_match_expected_schema"
        ]["expected"]["default_check_names"]
    )
    assert delivery_preview_guard_checks[
        "delivery_preview_payload_keys_match_expected_schema"
    ]["actual"]["telegram_chunk_keys"] == [
        ["index", "chars", "text"] for _chunk in telegram_preview["chunks"]
    ]
    assert delivery_contract["cron_intents"] == [
        "pre_market_swing_report",
        "intraday_risk_watch",
        "post_market_review",
    ]
    assert delivery_channels["hermes"]["network_call"] is False
    assert delivery_channels["hermes"]["numeric_authority"] == "latest_signal_report"
    assert telegram_contract["schema_version"] == "telegram_report_format.v1"
    assert telegram_contract["network_call"] is False
    assert telegram_contract["send_call"] is False
    assert (
        telegram_contract["required_sections"]
        == payload["report_intent_contract"]["required_sections"]
    )
    assert report_contract_guard_checks[
        "delivery_contract_has_no_network_side_effect"
    ] == {
        "name": "delivery_contract_has_no_network_side_effect",
        "passed": True,
        "expected": False,
        "actual": {"hermes": False, "telegram": False},
    }
    assert report_contract_guard_checks[
        "delivery_contract_has_no_send_side_effect"
    ] == {
        "name": "delivery_contract_has_no_send_side_effect",
        "passed": True,
        "expected": False,
        "actual": {"hermes": False, "telegram": False},
    }
    assert report_contract_guard_checks[
        "delivery_contract_keys_match_expected_schema"
    ] == {
        "name": "delivery_contract_keys_match_expected_schema",
        "passed": True,
        "expected": expected_delivery_contract_schema,
        "actual": expected_delivery_contract_schema,
    }
    assert report_contract_guard_checks[
        "delivery_channel_formats_match_expected"
    ] == {
        "name": "delivery_channel_formats_match_expected",
        "passed": True,
        "expected": expected_delivery_channel_formats,
        "actual": expected_delivery_channel_formats,
    }
    assert report_contract_guard_checks[
        "report_telegram_schema_version_matches_expected"
    ] == {
        "name": "report_telegram_schema_version_matches_expected",
        "passed": True,
        "expected": "telegram_report_format.v1",
        "actual": "telegram_report_format.v1",
    }
    assert report_contract_guard_checks[
        "report_telegram_chunking_contract_matches_expected"
    ] == {
        "name": "report_telegram_chunking_contract_matches_expected",
        "passed": True,
        "expected": expected_telegram_chunking_contract,
        "actual": expected_telegram_chunking_contract,
    }
    assert "delivery_contract_has_no_network_side_effect" in (
        report_contract_guard_checks[
            "report_contract_guard_check_names_match_expected_schema"
        ]["expected"]
    )
    assert "delivery_contract_keys_match_expected_schema" in (
        report_contract_guard_checks[
            "report_contract_guard_check_keys_match_expected_schema"
        ]["expected"]["default_check_names"]
    )
    assert payload["report_contract_guard"]["status"] == "ok"
    assert report_contract_guard_checks[
        "report_text_reflects_source_repository_summary"
    ] == {
        "name": "report_text_reflects_source_repository_summary",
        "passed": True,
        "expected": source_summary,
        "actual": source_summary,
    }
    assert report_contract_guard_checks[
        "report_text_reflects_label_status_summary"
    ] == {
        "name": "report_text_reflects_label_status_summary",
        "passed": True,
        "expected": selected_label_summary,
        "actual": selected_label_summary,
    }
    assert "report_text_reflects_source_repository_summary" in report_contract_guard_checks[
        "report_contract_guard_check_names_match_expected_schema"
    ]["expected"]
    assert "report_text_reflects_label_status_summary" in report_contract_guard_checks[
        "report_contract_guard_check_keys_match_expected_schema"
    ]["expected"]["default_check_names"]
    assert report_payload_guard_checks[
        "report_payload_source_repository_ref_keys_match_expected_schema"
    ] == {
        "name": "report_payload_source_repository_ref_keys_match_expected_schema",
        "passed": True,
        "expected": ["storage", "db_required", "filters"],
        "actual": ["storage", "db_required", "filters"],
    }
    assert report_payload_guard_checks[
        "report_payload_source_repository_ref_is_path_free"
    ] == {
        "name": "report_payload_source_repository_ref_is_path_free",
        "passed": True,
        "expected": expected_source_repository_ref_path_free,
        "actual": expected_source_repository_ref_path_free,
    }
    assert report_payload_guard_checks[
        "report_payload_source_signal_ref_keys_match_expected_schema"
    ] == {
        "name": "report_payload_source_signal_ref_keys_match_expected_schema",
        "passed": True,
        "expected": ["signal_id", "run_id", "config_hash"],
        "actual": ["signal_id", "run_id", "config_hash"],
    }
    assert report_payload_guard_checks[
        "report_payload_source_signal_ref_matches_report_identity"
    ] == {
        "name": "report_payload_source_signal_ref_matches_report_identity",
        "passed": True,
        "expected": expected_source_signal_ref_identity,
        "actual": expected_source_signal_ref_identity,
    }
    assert report_payload_guard_checks[
        "report_payload_source_signal_ref_values_have_traceable_format"
    ] == {
        "name": "report_payload_source_signal_ref_values_have_traceable_format",
        "passed": True,
        "expected": expected_source_signal_ref_traceable_format,
        "actual": expected_source_signal_ref_traceable_format,
    }
    assert report_payload_guard_checks[
        "report_payload_source_signal_ref_config_hash_digest_is_sha256"
    ] == {
        "name": "report_payload_source_signal_ref_config_hash_digest_is_sha256",
        "passed": True,
        "expected": expected_source_signal_ref_config_hash_digest,
        "actual": expected_source_signal_ref_config_hash_digest,
    }
    assert report_payload_guard_checks["report_payload_intent_matches_contract"] == {
        "name": "report_payload_intent_matches_contract",
        "passed": True,
        "expected": expected_report_intent_contract["name"],
        "actual": "pre_market_swing_report",
    }
    assert "report_payload_intent_matches_contract" in (
        report_payload_guard_checks[
            "report_payload_guard_check_names_match_expected_schema"
        ]["expected"]
    )
    assert report_payload_guard_checks[
        "report_payload_guard_check_keys_match_expected_schema"
    ]["actual"]["report_payload_intent_matches_contract"] == [
        "name",
        "passed",
        "expected",
        "actual",
    ]
    assert report_payload_guard_checks[
        "report_payload_top_level_identity_matches_latest_signal_report"
    ] == {
        "name": "report_payload_top_level_identity_matches_latest_signal_report",
        "passed": True,
        "expected": expected_top_level_identity,
        "actual": expected_top_level_identity,
    }
    assert "report_payload_top_level_identity_matches_latest_signal_report" in (
        report_payload_guard_checks[
            "report_payload_guard_check_names_match_expected_schema"
        ]["expected"]
    )
    assert payload["schema_version"] == "hermes_report.v1"
    assert report_payload_guard_checks[
        "report_payload_schema_version_matches_expected"
    ] == {
        "name": "report_payload_schema_version_matches_expected",
        "passed": True,
        "expected": "hermes_report.v1",
        "actual": "hermes_report.v1",
    }
    assert "report_payload_schema_version_matches_expected" in (
        report_payload_guard_checks[
            "report_payload_guard_check_names_match_expected_schema"
        ]["expected"]
    )
    assert report_payload_guard_checks[
        "report_payload_guard_check_keys_match_expected_schema"
    ]["actual"]["report_payload_schema_version_matches_expected"] == [
        "name",
        "passed",
        "expected",
        "actual",
    ]
    assert payload["live_data_required"] is False
    assert report_payload_guard_checks[
        "report_payload_live_data_required_matches_expected"
    ] == {
        "name": "report_payload_live_data_required_matches_expected",
        "passed": True,
        "expected": False,
        "actual": False,
    }
    assert "report_payload_live_data_required_matches_expected" in (
        report_payload_guard_checks[
            "report_payload_guard_check_names_match_expected_schema"
        ]["expected"]
    )
    assert report_payload_guard_checks[
        "report_payload_guard_check_keys_match_expected_schema"
    ]["actual"]["report_payload_live_data_required_matches_expected"] == [
        "name",
        "passed",
        "expected",
        "actual",
    ]
    assert report_payload_guard_checks["report_payload_keys_match_expected_schema"] == {
        "name": "report_payload_keys_match_expected_schema",
        "passed": True,
        "expected": expected_payload_keys,
        "actual": expected_payload_keys,
    }
    assert list(payload["report_payload_guard"]) == ["status", "checks"]
    assert report_payload_guard_checks[
        "report_payload_guard_keys_match_expected_schema"
    ] == {
        "name": "report_payload_guard_keys_match_expected_schema",
        "passed": True,
        "expected": ["status", "checks"],
        "actual": ["status", "checks"],
    }
    assert report_payload_guard_checks[
        "report_payload_guard_keys_match_expected_schema"
    ]["actual"] == list(payload["report_payload_guard"])
    assert "report_payload_guard_keys_match_expected_schema" in (
        report_payload_guard_checks[
            "report_payload_guard_check_names_match_expected_schema"
        ]["expected"]
    )
    payload_check_names = report_payload_guard_checks[
        "report_payload_guard_check_names_match_expected_schema"
    ]
    assert payload_check_names == {
        "name": "report_payload_guard_check_names_match_expected_schema",
        "passed": True,
        "expected": expected_payload_check_names,
        "actual": expected_payload_check_names,
    }
    assert payload_check_names["actual"] == actual_payload_check_names
    assert "report_payload_source_repository_ref_keys_match_expected_schema" in (
        payload_check_names["expected"]
    )
    assert "report_payload_source_repository_ref_is_path_free" in (
        payload_check_names["expected"]
    )
    assert payload["source_repository_ref"] == source_repository_ref
    assert "source_repository_ref" in report_payload_guard_checks[
        "report_payload_keys_match_expected_schema"
    ]["actual"]
    assert "latest_record_guard" in report_payload_guard_checks[
        "report_payload_keys_match_expected_schema"
    ]["actual"]
    expected_default_check_keys = ["name", "passed", "expected", "actual"]
    expected_payload_check_keys = {
        check_name: expected_default_check_keys
        for check_name in expected_payload_check_names
    }
    payload_check_keys = report_payload_guard_checks[
        "report_payload_guard_check_keys_match_expected_schema"
    ]["actual"]
    assert payload_check_keys == actual_payload_check_keys
    assert payload_check_keys[
        "report_payload_source_repository_ref_keys_match_expected_schema"
    ] == expected_default_check_keys
    assert payload_check_keys[
        "report_payload_source_repository_ref_is_path_free"
    ] == expected_default_check_keys
    assert report_payload_guard_checks[
        "report_payload_guard_check_keys_match_expected_schema"
    ] == {
        "name": "report_payload_guard_check_keys_match_expected_schema",
        "passed": True,
        "expected": expected_default_check_keys,
        "actual": expected_payload_check_keys,
    }
    assert all(
        check_keys == expected_default_check_keys
        for check_keys in payload_check_keys.values()
    )
    assert payload_check_keys[
        "report_payload_keys_match_expected_schema"
    ] == expected_default_check_keys
    assert payload_check_keys[
        "report_payload_guard_check_keys_match_expected_schema"
    ] == expected_default_check_keys
    assert report_payload_guard_checks[
        "report_payload_optional_context_statuses_are_ok"
    ] == {
        "name": "report_payload_optional_context_statuses_are_ok",
        "passed": True,
        "expected": {},
        "actual": {},
    }
    assert report_payload_guard_checks[
        "report_payload_optional_context_guards_are_ok"
    ] == {
        "name": "report_payload_optional_context_guards_are_ok",
        "passed": True,
        "expected": {},
        "actual": {},
    }
    assert report_payload_guard_checks[
        "report_payload_nested_guard_statuses_are_ok"
    ] == {
        "name": "report_payload_nested_guard_statuses_are_ok",
        "passed": True,
        "expected": expected_nested_guard_statuses,
        "actual": expected_nested_guard_statuses,
    }
    assert report_payload_guard_checks[
        "report_payload_nested_guard_statuses_are_ok"
    ]["expected"] == actual_nested_guard_statuses
    assert report_payload_guard_checks[
        "report_payload_nested_guard_statuses_are_ok"
    ]["actual"] == actual_nested_guard_statuses
    assert "report_payload_nested_guard_statuses_are_ok" in report_payload_guard_checks[
        "report_payload_guard_check_names_match_expected_schema"
    ]["expected"]
    assert "latest_record_guard" in report_payload_guard_checks[
        "report_payload_nested_guard_statuses_are_ok"
    ]["actual"]
    assert payload["report_payload_guard"]["status"] == "ok"
    assert str(database_path) not in iter_nested_strings(label_status)
    assert str(database_path) not in iter_nested_strings(evidence_contract)
    assert str(database_path) not in iter_nested_strings(evidence_context)
    assert str(database_path) not in iter_nested_strings(evidence_label_status)
    assert str(database_path) not in iter_nested_strings(payload["source_signal_ref"])
    assert str(database_path) not in iter_nested_strings(payload["source_repository_ref"])
    assert str(database_path) not in iter_nested_strings(latest_record_guard)
    assert str(database_path) not in iter_nested_strings(evidence_guard_checks)
    assert str(database_path) not in iter_nested_strings(prompt_contract)
    assert str(database_path) not in iter_nested_strings(report_intent_contract)
    assert str(database_path) not in iter_nested_strings(delivery_contract)
    assert str(database_path) not in iter_nested_strings(delivery_preview)
    assert str(database_path) not in iter_nested_strings(report_contract_guard_checks)
    assert str(database_path) not in iter_nested_strings(report_payload_guard_checks)
    assert str(database_path) not in iter_nested_strings(reasons)
    assert str(database_path) not in payload["text"]
    assert all(
        ".sqlite" not in value.lower()
        for value in iter_nested_strings(label_status)
    )
    assert all(
        ".sqlite" not in value.lower()
        for value in iter_nested_strings(evidence_contract)
    )
    assert all(
        ".sqlite" not in value.lower()
        for value in iter_nested_strings(evidence_context)
    )
    assert all(
        ".sqlite" not in value.lower()
        for value in iter_nested_strings(evidence_label_status)
    )
    assert all(
        ".sqlite" not in value.lower()
        for value in iter_nested_strings(payload["source_signal_ref"])
    )
    assert all(
        ".sqlite" not in value.lower()
        for value in iter_nested_strings(payload["source_repository_ref"])
    )
    assert all(
        ".sqlite" not in value.lower()
        for value in iter_nested_strings(latest_record_guard)
    )
    assert all(
        ".sqlite" not in value.lower()
        for value in iter_nested_strings(evidence_guard_checks)
    )
    assert all(
        ".sqlite" not in value.lower()
        for value in iter_nested_strings(prompt_contract)
    )
    assert all(
        ".sqlite" not in value.lower()
        for value in iter_nested_strings(report_intent_contract)
    )
    assert all(
        ".sqlite" not in value.lower()
        for value in iter_nested_strings(delivery_contract)
    )
    assert all(
        ".sqlite" not in value.lower()
        for value in iter_nested_strings(delivery_preview)
    )
    assert all(
        ".sqlite" not in value.lower()
        for value in iter_nested_strings(report_contract_guard_checks)
    )
    assert all(
        ".sqlite" not in value.lower()
        for value in iter_nested_strings(report_payload_guard_checks)
    )
    assert all(
        ".sqlite" not in value.lower()
        for value in iter_nested_strings(reasons)
    )


def test_latest_signal_report_repository_source_includes_jsonl_label_status(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    ledger_path = tmp_path / "signal_ledger.jsonl"
    stored_signal = {
        **reporting.score_leverage_swing("SSO"),
        "signal_id": "sig_report_label_jsonl",
        "run_id": "run_report_label_jsonl",
        "created_at": "2026-05-20T14:00:00Z",
    }
    record_signal(signal=stored_signal, ledger_path=str(ledger_path))
    label = label_signal_outcome(
        signal_id=stored_signal["signal_id"],
        ledger_path=str(ledger_path),
        price_path=[500.0, 560.0],
        time_barrier_days=2,
    )

    def unexpected_score_call(*_args: object, **_kwargs: object) -> dict[str, object]:
        raise AssertionError("repository-backed report must not rescore the signal")

    monkeypatch.setattr(reporting, "score_leverage_swing", unexpected_score_call)
    payload = generate_latest_signal_report(asset="SSO", ledger_path=str(ledger_path))
    label_status = payload["latest_signal_report"]["label_status"]

    assert label_status == {
        "schema_version": "signal_label_outcome.v1",
        "signal_id": stored_signal["signal_id"],
        "outcome": label["outcome"],
        "realized_r": label["realized_r"],
        "first_barrier_hit": label["first_barrier_hit"],
        "labeled_at": label["labeled_at"],
        "time_barrier_days": label["time_barrier_days"],
        "live_data_required": False,
    }


def test_latest_signal_report_repository_source_includes_jsonl_evidence_label_status(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    ledger_path = tmp_path / "signal_ledger.jsonl"
    stored_signal = {
        **reporting.score_leverage_swing("SSO"),
        "signal_id": "sig_report_evidence_label_jsonl",
        "run_id": "run_report_evidence_label_jsonl",
        "created_at": "2026-05-20T14:05:00Z",
    }
    record_signal(signal=stored_signal, ledger_path=str(ledger_path))
    label = label_signal_outcome(
        signal_id=stored_signal["signal_id"],
        ledger_path=str(ledger_path),
        price_path=[500.0, 560.0],
        time_barrier_days=2,
    )

    def unexpected_score_call(*_args: object, **_kwargs: object) -> dict[str, object]:
        raise AssertionError("repository-backed report must not rescore the signal")

    monkeypatch.setattr(reporting, "score_leverage_swing", unexpected_score_call)
    payload = generate_latest_signal_report(asset="SSO", ledger_path=str(ledger_path))
    evidence_label_status = payload["evidence_context"]["label_status"]

    assert evidence_label_status == payload["latest_signal_report"]["label_status"]
    assert evidence_label_status["schema_version"] == "signal_label_outcome.v1"
    assert evidence_label_status["signal_id"] == stored_signal["signal_id"]
    assert evidence_label_status["outcome"] == label["outcome"]
    assert evidence_label_status["realized_r"] == label["realized_r"]
    assert str(ledger_path) not in iter_nested_strings(evidence_label_status)
    assert all(
        ".sqlite" not in value.lower()
        for value in iter_nested_strings(evidence_label_status)
    )


def test_latest_signal_report_repository_label_summary_appears_in_sections_and_text(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    ledger_path = tmp_path / "signal_ledger.jsonl"
    stored_signal = {
        **reporting.score_leverage_swing("SSO"),
        "signal_id": "sig_report_label_summary_jsonl",
        "run_id": "run_report_label_summary_jsonl",
        "created_at": "2026-05-20T14:06:00Z",
    }
    record_signal(signal=stored_signal, ledger_path=str(ledger_path))
    label = label_signal_outcome(
        signal_id=stored_signal["signal_id"],
        ledger_path=str(ledger_path),
        price_path=[500.0, 560.0],
        time_barrier_days=2,
    )

    def unexpected_score_call(*_args: object, **_kwargs: object) -> dict[str, object]:
        raise AssertionError("repository-backed report must not rescore the signal")

    monkeypatch.setattr(reporting, "score_leverage_swing", unexpected_score_call)
    payload = generate_latest_signal_report(asset="SSO", ledger_path=str(ledger_path))
    reasons = next(
        section for section in payload["sections"] if section["title"] == "Reasons"
    )
    label_summary = (
        f"Stored label: outcome={label['outcome']}; "
        f"realized_r={label['realized_r']}; "
        f"first_barrier_hit={label['first_barrier_hit']}; "
        "time_barrier_days=2"
    )

    assert label_summary in reasons["items"]
    assert f"- {label_summary}" in payload["text"]
    assert str(ledger_path) not in iter_nested_strings(reasons)
    assert str(ledger_path) not in payload["text"]
    assert all(
        ".sqlite" not in value.lower()
        for value in iter_nested_strings(reasons)
    )


def test_latest_signal_report_repository_context_summaries_survive_intraday_intent_without_reasons(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    ledger_path = tmp_path / "signal_ledger.jsonl"
    stored_signal = {
        **reporting.score_leverage_swing("SSO"),
        "signal_id": "sig_report_intraday_context_jsonl",
        "run_id": "run_report_intraday_context_jsonl",
        "created_at": "2026-05-20T14:08:00Z",
    }
    record_signal(signal=stored_signal, ledger_path=str(ledger_path))
    label = label_signal_outcome(
        signal_id=stored_signal["signal_id"],
        ledger_path=str(ledger_path),
        price_path=[500.0, 560.0],
        time_barrier_days=2,
    )

    def unexpected_score_call(*_args: object, **_kwargs: object) -> dict[str, object]:
        raise AssertionError("repository-backed report must not rescore the signal")

    monkeypatch.setattr(reporting, "score_leverage_swing", unexpected_score_call)
    payload = generate_latest_signal_report(
        asset="SSO",
        ledger_path=str(ledger_path),
        report_intent="intraday_risk_watch",
    )
    section_titles = [section["title"] for section in payload["sections"]]
    cautions = next(
        section for section in payload["sections"] if section["title"] == "Cautions"
    )
    source_summary = (
        "Repository source: jsonl_signal_ledger_record; "
        "db_required=false; "
        "filters asset=SSO underlying=<any> timeframe=swing_3d_10d"
    )
    label_summary = (
        f"Stored label: outcome={label['outcome']}; "
        f"realized_r={label['realized_r']}; "
        f"first_barrier_hit={label['first_barrier_hit']}; "
        "time_barrier_days=2"
    )

    assert section_titles == ["Target", "Decision", "Stop", "Cautions"]
    assert "Reasons:" not in payload["text"]
    assert source_summary in cautions["items"]
    assert label_summary in cautions["items"]
    assert f"- {source_summary}" in payload["text"]
    assert f"- {label_summary}" in payload["text"]
    assert payload["report_contract_guard"]["status"] == "ok"
    assert str(ledger_path) not in iter_nested_strings(cautions)
    assert str(ledger_path) not in payload["text"]
    assert all(
        ".sqlite" not in value.lower()
        for value in iter_nested_strings(cautions)
    )


def test_latest_signal_report_repository_context_summary_text_guard_validates_intraday_fallback(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    ledger_path = tmp_path / "signal_ledger.jsonl"
    stored_signal = {
        **reporting.score_leverage_swing("SSO"),
        "signal_id": "sig_report_intraday_context_guard_jsonl",
        "run_id": "run_report_intraday_context_guard_jsonl",
        "created_at": "2026-05-20T14:09:00Z",
    }
    record_signal(signal=stored_signal, ledger_path=str(ledger_path))
    label = label_signal_outcome(
        signal_id=stored_signal["signal_id"],
        ledger_path=str(ledger_path),
        price_path=[500.0, 560.0],
        time_barrier_days=2,
    )

    def unexpected_score_call(*_args: object, **_kwargs: object) -> dict[str, object]:
        raise AssertionError("repository-backed report must not rescore the signal")

    monkeypatch.setattr(reporting, "score_leverage_swing", unexpected_score_call)
    payload = generate_latest_signal_report(
        asset="SSO",
        ledger_path=str(ledger_path),
        report_intent="intraday_risk_watch",
    )
    guard_checks = {
        check["name"]: check for check in payload["report_contract_guard"]["checks"]
    }
    source_summary = (
        "Repository source: jsonl_signal_ledger_record; "
        "db_required=false; "
        "filters asset=SSO underlying=<any> timeframe=swing_3d_10d"
    )
    label_summary = (
        f"Stored label: outcome={label['outcome']}; "
        f"realized_r={label['realized_r']}; "
        f"first_barrier_hit={label['first_barrier_hit']}; "
        "time_barrier_days=2"
    )

    assert payload["report_contract_guard"]["status"] == "ok"
    assert guard_checks["report_text_reflects_source_repository_summary"] == {
        "name": "report_text_reflects_source_repository_summary",
        "passed": True,
        "expected": source_summary,
        "actual": source_summary,
    }
    assert guard_checks["report_text_reflects_label_status_summary"] == {
        "name": "report_text_reflects_label_status_summary",
        "passed": True,
        "expected": label_summary,
        "actual": label_summary,
    }
    assert "report_text_reflects_source_repository_summary" in guard_checks[
        "report_contract_guard_check_names_match_expected_schema"
    ]["expected"]
    assert "report_text_reflects_label_status_summary" in guard_checks[
        "report_contract_guard_check_keys_match_expected_schema"
    ]["expected"]["default_check_names"]
    assert str(ledger_path) not in iter_nested_strings(guard_checks)
    assert all(
        ".sqlite" not in value.lower()
        for value in iter_nested_strings(guard_checks)
    )


def test_latest_signal_report_repository_source_evidence_guard_validates_label_status(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    ledger_path = tmp_path / "signal_ledger.jsonl"
    stored_signal = {
        **reporting.score_leverage_swing("SSO"),
        "signal_id": "sig_report_evidence_label_guard_jsonl",
        "run_id": "run_report_evidence_label_guard_jsonl",
        "created_at": "2026-05-20T14:07:00Z",
    }
    record_signal(signal=stored_signal, ledger_path=str(ledger_path))
    label_signal_outcome(
        signal_id=stored_signal["signal_id"],
        ledger_path=str(ledger_path),
        price_path=[500.0, 560.0],
        time_barrier_days=2,
    )

    def unexpected_score_call(*_args: object, **_kwargs: object) -> dict[str, object]:
        raise AssertionError("repository-backed report must not rescore the signal")

    monkeypatch.setattr(reporting, "score_leverage_swing", unexpected_score_call)
    payload = generate_latest_signal_report(asset="SSO", ledger_path=str(ledger_path))
    guard_checks = {
        check["name"]: check for check in payload["evidence_guard"]["checks"]
    }

    assert payload["evidence_guard"]["status"] == "ok"
    assert guard_checks["label_status_reflected_in_evidence_context"] == {
        "name": "label_status_reflected_in_evidence_context",
        "passed": True,
        "expected": payload["latest_signal_report"]["label_status"],
        "actual": payload["evidence_context"]["label_status"],
    }
    assert "label_status_reflected_in_evidence_context" in guard_checks[
        "evidence_guard_check_names_match_expected_schema"
    ]["expected"]
    assert "label_status_reflected_in_evidence_context" in guard_checks[
        "evidence_guard_check_keys_match_expected_schema"
    ]["expected"]["default_check_names"]


def test_latest_signal_report_repository_source_includes_sqlite_label_status(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    database_path = tmp_path / "halo_swing.sqlite"
    stored_signal = {
        **reporting.score_leverage_swing("QLD"),
        "signal_id": "sig_report_label_sqlite",
        "run_id": "run_report_label_sqlite",
        "created_at": "2026-05-20T15:00:00Z",
    }
    record_signal(signal=stored_signal, database_path=str(database_path))
    label = label_signal_outcome(
        signal_id=stored_signal["signal_id"],
        database_path=str(database_path),
        price_path=[500.0, 560.0],
        time_barrier_days=2,
    )

    def unexpected_score_call(*_args: object, **_kwargs: object) -> dict[str, object]:
        raise AssertionError("repository-backed report must not rescore the signal")

    monkeypatch.setattr(reporting, "score_leverage_swing", unexpected_score_call)
    payload = generate_latest_signal_report(
        asset="QLD",
        database_path=str(database_path),
    )
    label_status = payload["latest_signal_report"]["label_status"]

    assert label_status["schema_version"] == "signal_label_outcome.v1"
    assert label_status["signal_id"] == stored_signal["signal_id"]
    assert label_status["outcome"] == label["outcome"]
    assert label_status["realized_r"] == label["realized_r"]
    assert label_status["first_barrier_hit"] == label["first_barrier_hit"]
    assert label_status["labeled_at"] == label["labeled_at"]
    assert label_status["time_barrier_days"] == label["time_barrier_days"]
    assert label_status["live_data_required"] is False
    assert str(database_path) not in iter_nested_strings(label_status)
    assert all(
        ".sqlite" not in value.lower()
        for value in iter_nested_strings(label_status)
    )


def test_latest_signal_report_sqlite_repository_label_status_is_reflected_in_evidence_context(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    database_path = tmp_path / "halo_swing.sqlite"
    stored_signal = {
        **reporting.score_leverage_swing("QLD"),
        "signal_id": "sig_report_evidence_label_sqlite",
        "run_id": "run_report_evidence_label_sqlite",
        "created_at": "2026-05-20T15:05:00Z",
    }
    record_signal(signal=stored_signal, database_path=str(database_path))
    label = label_signal_outcome(
        signal_id=stored_signal["signal_id"],
        database_path=str(database_path),
        price_path=[500.0, 560.0],
        time_barrier_days=2,
    )

    def unexpected_score_call(*_args: object, **_kwargs: object) -> dict[str, object]:
        raise AssertionError("repository-backed report must not rescore the signal")

    monkeypatch.setattr(reporting, "score_leverage_swing", unexpected_score_call)
    payload = generate_latest_signal_report(
        asset="QLD",
        database_path=f" {database_path} ",
    )
    evidence_label_status = payload["evidence_context"]["label_status"]
    evidence_guard_checks = {
        check["name"]: check for check in payload["evidence_guard"]["checks"]
    }

    assert evidence_label_status == payload["latest_signal_report"]["label_status"]
    assert evidence_label_status["schema_version"] == "signal_label_outcome.v1"
    assert evidence_label_status["signal_id"] == stored_signal["signal_id"]
    assert evidence_label_status["outcome"] == label["outcome"]
    assert evidence_label_status["realized_r"] == label["realized_r"]
    assert str(database_path) not in iter_nested_strings(evidence_label_status)
    assert all(
        ".sqlite" not in value.lower()
        for value in iter_nested_strings(evidence_label_status)
    )
    assert evidence_guard_checks["label_status_reflected_in_evidence_context"] == {
        "name": "label_status_reflected_in_evidence_context",
        "passed": True,
        "expected": payload["latest_signal_report"]["label_status"],
        "actual": evidence_label_status,
    }
    assert "label_status_reflected_in_evidence_context" in evidence_guard_checks[
        "evidence_guard_check_names_match_expected_schema"
    ]["expected"]
    assert "label_status_reflected_in_evidence_context" in evidence_guard_checks[
        "evidence_guard_check_keys_match_expected_schema"
    ]["expected"]["default_check_names"]
    assert str(database_path) not in iter_nested_strings(evidence_guard_checks)
    assert all(
        ".sqlite" not in value.lower()
        for value in iter_nested_strings(evidence_guard_checks)
    )
    assert payload["evidence_guard"]["status"] == "ok"


def test_latest_signal_report_sqlite_repository_label_summary_appears_in_sections_and_text(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    database_path = tmp_path / "halo_swing.sqlite"
    stored_signal = {
        **reporting.score_leverage_swing("QLD"),
        "signal_id": "sig_report_label_summary_sqlite",
        "run_id": "run_report_label_summary_sqlite",
        "created_at": "2026-05-20T15:06:00Z",
    }
    record_signal(signal=stored_signal, database_path=str(database_path))
    label = label_signal_outcome(
        signal_id=stored_signal["signal_id"],
        database_path=str(database_path),
        price_path=[500.0, 560.0],
        time_barrier_days=2,
    )

    def unexpected_score_call(*_args: object, **_kwargs: object) -> dict[str, object]:
        raise AssertionError("repository-backed report must not rescore the signal")

    monkeypatch.setattr(reporting, "score_leverage_swing", unexpected_score_call)
    payload = generate_latest_signal_report(
        asset="QLD",
        database_path=f" {database_path} ",
    )
    reasons = next(
        section for section in payload["sections"] if section["title"] == "Reasons"
    )
    label_summary = (
        f"Stored label: outcome={label['outcome']}; "
        f"realized_r={label['realized_r']}; "
        f"first_barrier_hit={label['first_barrier_hit']}; "
        "time_barrier_days=2"
    )

    assert label_summary in reasons["items"]
    assert f"- {label_summary}" in payload["text"]
    assert str(database_path) not in iter_nested_strings(reasons)
    assert str(database_path) not in payload["text"]
    assert all(
        ".sqlite" not in value.lower()
        for value in iter_nested_strings(reasons)
    )


def test_latest_signal_report_sqlite_repository_context_summaries_survive_intraday_intent_without_reasons(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    database_path = tmp_path / "halo_swing.sqlite"
    stored_signal = {
        **reporting.score_leverage_swing("QLD"),
        "signal_id": "sig_report_intraday_context_sqlite",
        "run_id": "run_report_intraday_context_sqlite",
        "created_at": "2026-05-20T15:08:00Z",
    }
    record_signal(signal=stored_signal, database_path=str(database_path))
    label = label_signal_outcome(
        signal_id=stored_signal["signal_id"],
        database_path=str(database_path),
        price_path=[500.0, 560.0],
        time_barrier_days=2,
    )

    def unexpected_score_call(*_args: object, **_kwargs: object) -> dict[str, object]:
        raise AssertionError("repository-backed report must not rescore the signal")

    monkeypatch.setattr(reporting, "score_leverage_swing", unexpected_score_call)
    payload = generate_latest_signal_report(
        asset="QLD",
        database_path=f" {database_path} ",
        report_intent="intraday_risk_watch",
    )
    section_titles = [section["title"] for section in payload["sections"]]
    cautions = next(
        section for section in payload["sections"] if section["title"] == "Cautions"
    )
    source_summary = (
        "Repository source: sqlite_signal_repository; "
        "db_required=true; "
        "filters asset=QLD underlying=<any> timeframe=swing_3d_10d"
    )
    label_summary = (
        f"Stored label: outcome={label['outcome']}; "
        f"realized_r={label['realized_r']}; "
        f"first_barrier_hit={label['first_barrier_hit']}; "
        "time_barrier_days=2"
    )

    assert section_titles == ["Target", "Decision", "Stop", "Cautions"]
    assert "Reasons:" not in payload["text"]
    assert source_summary in cautions["items"]
    assert label_summary in cautions["items"]
    assert f"- {source_summary}" in payload["text"]
    assert f"- {label_summary}" in payload["text"]
    assert payload["report_contract_guard"]["status"] == "ok"
    assert payload["report_payload_guard"]["status"] == "ok"
    assert payload["evidence_guard"]["status"] == "ok"
    assert str(database_path) not in iter_nested_strings(cautions)
    assert str(database_path) not in payload["text"]
    assert all(
        ".sqlite" not in value.lower()
        for value in iter_nested_strings(cautions)
    )


def test_latest_signal_report_sqlite_repository_context_summary_text_guard_validates_intraday_fallback(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    database_path = tmp_path / "halo_swing.sqlite"
    stored_signal = {
        **reporting.score_leverage_swing("QLD"),
        "signal_id": "sig_report_intraday_context_guard_sqlite",
        "run_id": "run_report_intraday_context_guard_sqlite",
        "created_at": "2026-05-20T15:09:00Z",
    }
    record_signal(signal=stored_signal, database_path=str(database_path))
    label = label_signal_outcome(
        signal_id=stored_signal["signal_id"],
        database_path=str(database_path),
        price_path=[500.0, 560.0],
        time_barrier_days=2,
    )

    def unexpected_score_call(*_args: object, **_kwargs: object) -> dict[str, object]:
        raise AssertionError("repository-backed report must not rescore the signal")

    monkeypatch.setattr(reporting, "score_leverage_swing", unexpected_score_call)
    payload = generate_latest_signal_report(
        asset="QLD",
        database_path=f" {database_path} ",
        report_intent="intraday_risk_watch",
    )
    guard_checks = {
        check["name"]: check for check in payload["report_contract_guard"]["checks"]
    }
    source_summary = (
        "Repository source: sqlite_signal_repository; "
        "db_required=true; "
        "filters asset=QLD underlying=<any> timeframe=swing_3d_10d"
    )
    label_summary = (
        f"Stored label: outcome={label['outcome']}; "
        f"realized_r={label['realized_r']}; "
        f"first_barrier_hit={label['first_barrier_hit']}; "
        "time_barrier_days=2"
    )

    assert payload["report_contract_guard"]["status"] == "ok"
    assert guard_checks["report_text_reflects_source_repository_summary"] == {
        "name": "report_text_reflects_source_repository_summary",
        "passed": True,
        "expected": source_summary,
        "actual": source_summary,
    }
    assert guard_checks["report_text_reflects_label_status_summary"] == {
        "name": "report_text_reflects_label_status_summary",
        "passed": True,
        "expected": label_summary,
        "actual": label_summary,
    }
    assert "report_text_reflects_source_repository_summary" in guard_checks[
        "report_contract_guard_check_names_match_expected_schema"
    ]["expected"]
    assert "report_text_reflects_label_status_summary" in guard_checks[
        "report_contract_guard_check_keys_match_expected_schema"
    ]["expected"]["default_check_names"]
    assert str(database_path) not in iter_nested_strings(guard_checks)
    assert all(
        ".sqlite" not in value.lower()
        for value in iter_nested_strings(guard_checks)
    )


def test_latest_signal_report_rejects_missing_repository_source(
    tmp_path: Path,
) -> None:
    ledger_path = tmp_path / "missing_signal_ledger.jsonl"

    with pytest.raises(
        ValueError,
        match="latest signal report source was not found",
    ):
        generate_latest_signal_report(asset="SOXL", ledger_path=str(ledger_path))

    with pytest.raises(
        ValueError,
        match="ledger_path and database_path cannot both be provided",
    ):
        generate_latest_signal_report(
            ledger_path=str(ledger_path),
            database_path=str(tmp_path / "halo_swing.sqlite"),
        )

    assert not ledger_path.exists()


def test_latest_signal_report_missing_repository_source_error_includes_path_free_filters(
    tmp_path: Path,
) -> None:
    database_path = tmp_path / "halo_swing.sqlite"
    stored_signal = {
        **reporting.score_leverage_swing("TQQQ"),
        "signal_id": "sig_report_missing_filter_source",
        "run_id": "run_report_missing_filter_source",
        "created_at": "2026-05-20T16:00:00Z",
    }
    record_signal(signal=stored_signal, database_path=str(database_path))

    with pytest.raises(ValueError) as exc_info:
        generate_latest_signal_report(
            asset=" tqqq ",
            underlying=" soxx ",
            timeframe=" swing_3d_10d ",
            database_path=str(database_path),
        )

    message = str(exc_info.value)
    assert "latest signal report source was not found" in message
    assert "filters asset=TQQQ underlying=SOXX timeframe=swing_3d_10d" in message
    assert "database_path" not in message
    assert "ledger_path" not in message
    assert str(database_path) not in message
    assert ".sqlite" not in message.lower()
    assert "/Users/" not in message


def test_latest_signal_report_contains_required_report_sections() -> None:
    payload = generate_latest_signal_report("TQQQ")
    sections = {section["title"]: section["items"] for section in payload["sections"]}

    assert payload["schema_version"] == "hermes_report.v1"
    assert payload["report_intent"] == "pre_market_swing_report"
    report_payload_guard_checks = {
        check["name"]: check for check in payload["report_payload_guard"]["checks"]
    }
    assert payload["report_payload_guard"]["status"] == "ok"
    assert (
        report_payload_guard_checks["report_payload_schema_version_matches_expected"][
            "passed"
        ]
        is True
    )
    assert report_payload_guard_checks[
        "report_payload_schema_version_matches_expected"
    ]["actual"] == "hermes_report.v1"
    assert (
        report_payload_guard_checks[
            "report_payload_live_data_required_matches_expected"
        ]["passed"]
        is True
    )
    assert report_payload_guard_checks[
        "report_payload_live_data_required_matches_expected"
    ]["actual"] is False
    assert (
        report_payload_guard_checks[
            "report_payload_guard_check_names_match_expected_schema"
        ]["passed"]
        is True
    )
    assert report_payload_guard_checks[
        "report_payload_guard_check_names_match_expected_schema"
    ]["actual"] == report_payload_guard_checks[
        "report_payload_guard_check_names_match_expected_schema"
    ]["expected"]
    assert report_payload_guard_checks[
        "report_payload_guard_check_names_match_expected_schema"
    ]["actual"] == [
        "report_payload_schema_version_matches_expected",
        "report_payload_live_data_required_matches_expected",
        "report_payload_keys_match_expected_schema",
        "report_payload_source_signal_ref_keys_match_expected_schema",
        "report_payload_source_signal_ref_matches_report_identity",
        "report_payload_source_signal_ref_values_have_traceable_format",
        "report_payload_source_signal_ref_config_hash_digest_is_sha256",
        "report_payload_intent_matches_contract",
        "report_payload_top_level_identity_matches_latest_signal_report",
        "report_payload_nested_guard_statuses_are_ok",
        "report_payload_optional_context_statuses_are_ok",
        "report_payload_optional_context_guards_are_ok",
        "report_payload_guard_check_names_match_expected_schema",
        "report_payload_guard_keys_match_expected_schema",
        "report_payload_guard_check_keys_match_expected_schema",
    ]
    assert (
        report_payload_guard_checks[
            "report_payload_source_signal_ref_keys_match_expected_schema"
        ]["passed"]
        is True
    )
    assert report_payload_guard_checks[
        "report_payload_source_signal_ref_keys_match_expected_schema"
    ]["actual"] == ["signal_id", "run_id", "config_hash"]
    assert (
        report_payload_guard_checks[
            "report_payload_source_signal_ref_matches_report_identity"
        ]["passed"]
        is True
    )
    assert report_payload_guard_checks[
        "report_payload_source_signal_ref_matches_report_identity"
    ]["actual"] == {
        "signal_id": payload["latest_signal_report"]["signal_id"],
        "config_hash": payload["latest_signal_report"]["config_hash"],
        "run_id_nonempty": True,
    }
    assert (
        report_payload_guard_checks[
            "report_payload_source_signal_ref_values_have_traceable_format"
        ]["passed"]
        is True
    )
    assert report_payload_guard_checks[
        "report_payload_source_signal_ref_values_have_traceable_format"
    ]["actual"] == {
        "signal_id_nonempty": True,
        "run_id_nonempty": True,
        "config_hash_sha256_prefix": True,
    }
    assert (
        report_payload_guard_checks[
            "report_payload_source_signal_ref_config_hash_digest_is_sha256"
        ]["passed"]
        is True
    )
    assert report_payload_guard_checks[
        "report_payload_source_signal_ref_config_hash_digest_is_sha256"
    ]["actual"] == {
        "config_hash_digest_length": 64,
        "config_hash_digest_hex": True,
    }
    assert report_payload_guard_checks["report_payload_intent_matches_contract"][
        "passed"
    ] is True
    assert report_payload_guard_checks["report_payload_intent_matches_contract"][
        "actual"
    ] == "pre_market_swing_report"
    expected_top_level_identity = {
        "as_of": payload["latest_signal_report"]["created_at"],
        "asset": payload["latest_signal_report"]["asset"],
        "underlying": payload["latest_signal_report"]["underlying"],
        "timeframe": payload["latest_signal_report"]["timeframe"],
        "action": payload["latest_signal_report"]["action"],
        "confidence_label": payload["confidence_label"],
    }
    assert (
        report_payload_guard_checks[
            "report_payload_top_level_identity_matches_latest_signal_report"
        ]["passed"]
        is True
    )
    assert report_payload_guard_checks[
        "report_payload_top_level_identity_matches_latest_signal_report"
    ]["actual"] == expected_top_level_identity
    assert report_payload_guard_checks[
        "report_payload_top_level_identity_matches_latest_signal_report"
    ]["expected"] == expected_top_level_identity
    expected_nested_guard_statuses = {
        "delivery_preview.guard": "ok",
        "evidence_guard": "ok",
        "report_contract_guard": "ok",
    }
    assert report_payload_guard_checks["report_payload_nested_guard_statuses_are_ok"][
        "passed"
    ] is True
    assert report_payload_guard_checks["report_payload_nested_guard_statuses_are_ok"][
        "actual"
    ] == expected_nested_guard_statuses
    assert report_payload_guard_checks["report_payload_nested_guard_statuses_are_ok"][
        "expected"
    ] == expected_nested_guard_statuses
    assert (
        report_payload_guard_checks[
            "report_payload_optional_context_statuses_are_ok"
        ]["passed"]
        is True
    )
    assert report_payload_guard_checks[
        "report_payload_optional_context_statuses_are_ok"
    ]["actual"] == {}
    assert report_payload_guard_checks[
        "report_payload_optional_context_statuses_are_ok"
    ]["expected"] == {}
    assert (
        report_payload_guard_checks[
            "report_payload_optional_context_guards_are_ok"
        ]["passed"]
        is True
    )
    assert report_payload_guard_checks[
        "report_payload_optional_context_guards_are_ok"
    ]["actual"] == {}
    assert report_payload_guard_checks[
        "report_payload_optional_context_guards_are_ok"
    ]["expected"] == {}
    assert (
        report_payload_guard_checks[
            "report_payload_guard_keys_match_expected_schema"
        ]["passed"]
        is True
    )
    assert report_payload_guard_checks[
        "report_payload_guard_keys_match_expected_schema"
    ]["actual"] == ["status", "checks"]
    assert (
        report_payload_guard_checks[
            "report_payload_guard_check_keys_match_expected_schema"
        ]["passed"]
        is True
    )
    assert all(
        check_keys == ["name", "passed", "expected", "actual"]
        for check_keys in report_payload_guard_checks[
            "report_payload_guard_check_keys_match_expected_schema"
        ]["actual"].values()
    )
    assert report_payload_guard_checks[
        "report_payload_guard_check_keys_match_expected_schema"
    ]["actual"]["report_payload_keys_match_expected_schema"] == [
        "name",
        "passed",
        "expected",
        "actual",
    ]
    assert report_payload_guard_checks[
        "report_payload_guard_check_keys_match_expected_schema"
    ]["actual"]["report_payload_guard_keys_match_expected_schema"] == [
        "name",
        "passed",
        "expected",
        "actual",
    ]
    assert report_payload_guard_checks[
        "report_payload_guard_check_keys_match_expected_schema"
    ]["actual"][
        "report_payload_source_signal_ref_keys_match_expected_schema"
    ] == [
        "name",
        "passed",
        "expected",
        "actual",
    ]
    assert report_payload_guard_checks[
        "report_payload_guard_check_keys_match_expected_schema"
    ]["actual"][
        "report_payload_source_signal_ref_matches_report_identity"
    ] == [
        "name",
        "passed",
        "expected",
        "actual",
    ]
    assert report_payload_guard_checks[
        "report_payload_guard_check_keys_match_expected_schema"
    ]["actual"][
        "report_payload_source_signal_ref_values_have_traceable_format"
    ] == [
        "name",
        "passed",
        "expected",
        "actual",
    ]
    assert report_payload_guard_checks[
        "report_payload_guard_check_keys_match_expected_schema"
    ]["actual"][
        "report_payload_source_signal_ref_config_hash_digest_is_sha256"
    ] == [
        "name",
        "passed",
        "expected",
        "actual",
    ]
    assert report_payload_guard_checks[
        "report_payload_guard_check_keys_match_expected_schema"
    ]["actual"]["report_payload_intent_matches_contract"] == [
        "name",
        "passed",
        "expected",
        "actual",
    ]
    assert report_payload_guard_checks[
        "report_payload_guard_check_keys_match_expected_schema"
    ]["actual"][
        "report_payload_top_level_identity_matches_latest_signal_report"
    ] == [
        "name",
        "passed",
        "expected",
        "actual",
    ]
    assert report_payload_guard_checks[
        "report_payload_guard_check_keys_match_expected_schema"
    ]["actual"]["report_payload_nested_guard_statuses_are_ok"] == [
        "name",
        "passed",
        "expected",
        "actual",
    ]
    assert report_payload_guard_checks[
        "report_payload_guard_check_keys_match_expected_schema"
    ]["actual"]["report_payload_optional_context_statuses_are_ok"] == [
        "name",
        "passed",
        "expected",
        "actual",
    ]
    assert report_payload_guard_checks[
        "report_payload_guard_check_keys_match_expected_schema"
    ]["actual"]["report_payload_optional_context_guards_are_ok"] == [
        "name",
        "passed",
        "expected",
        "actual",
    ]
    assert (
        report_payload_guard_checks["report_payload_keys_match_expected_schema"][
            "passed"
        ]
        is True
    )
    assert report_payload_guard_checks[
        "report_payload_keys_match_expected_schema"
    ]["actual"] == report_payload_guard_checks[
        "report_payload_keys_match_expected_schema"
    ]["expected"]
    assert report_payload_guard_checks[
        "report_payload_keys_match_expected_schema"
    ]["actual"][-4:] == [
        "report_contract_guard",
        "source_signal_ref",
        "live_data_required",
        "report_payload_guard",
    ]
    assert payload["report_intent_contract"]["decision_focus"]
    assert payload["prompt_contract"]["numeric_authority"]
    assert (
        payload["delivery_contract"]["channels"]["telegram"]["schema_version"]
        == "telegram_report_format.v1"
    )
    assert payload["delivery_contract"]["channels"]["telegram"]["network_call"] is False
    assert payload["delivery_contract"]["channels"]["telegram"]["send_call"] is False
    assert payload["delivery_preview"]["guard"]["status"] == "ok"
    assert (
        payload["delivery_preview"]["channels"]["telegram"]["schema_version"]
        == "telegram_report_format.v1"
    )
    assert (
        payload["delivery_preview"]["channels"]["telegram"]["section_separator"]
        == "\n\n"
    )
    assert payload["delivery_preview"]["channels"]["telegram"]["message_count"] == 1
    assert (
        payload["delivery_preview"]["channels"]["telegram"]["chunks"][0]["text"]
        == payload["text"]
    )
    preview_guard_checks = {
        check["name"]: check for check in payload["delivery_preview"]["guard"]["checks"]
    }
    assert (
        preview_guard_checks["hermes_payload_ref_matches_structured_payload"]["passed"]
        is True
    )
    assert preview_guard_checks["hermes_payload_ref_matches_structured_payload"][
        "expected"
    ] == "latest_signal_report"
    assert (
        preview_guard_checks["hermes_numeric_authority_matches_payload_ref"]["passed"]
        is True
    )
    assert preview_guard_checks["telegram_format_schema_declared"]["passed"] is True
    assert (
        preview_guard_checks["telegram_format_schema_declared"]["actual"]
        == "telegram_report_format.v1"
    )
    assert (
        preview_guard_checks["telegram_required_sections_present_in_preview"]["passed"]
        is True
    )
    assert (
        preview_guard_checks["telegram_unrequested_sections_absent_from_preview"][
            "passed"
        ]
        is True
    )
    assert preview_guard_checks["telegram_chunks_are_1_based_sequential"]["passed"] is True
    assert preview_guard_checks["telegram_message_count_matches_chunks"]["passed"] is True
    assert (
        preview_guard_checks["telegram_single_message_flag_matches_chunk_count"][
            "passed"
        ]
        is True
    )
    assert preview_guard_checks["telegram_chunk_char_counts_match_text"]["passed"] is True
    assert preview_guard_checks["telegram_chunks_are_nonempty"]["passed"] is True
    assert (
        preview_guard_checks["telegram_section_separator_preserves_preview_text"][
            "passed"
        ]
        is True
    )
    assert (
        preview_guard_checks["telegram_overflow_policy_splits_on_section_boundary"][
            "passed"
        ]
        is True
    )
    assert preview_guard_checks["telegram_chunks_fit_max_chars"]["passed"] is True
    assert preview_guard_checks["telegram_chunks_preserve_text"]["passed"] is True
    assert (
        preview_guard_checks["delivery_preview_has_no_network_side_effect"]["passed"]
        is True
    )
    assert preview_guard_checks["delivery_preview_has_no_network_side_effect"][
        "actual"
    ] == {"hermes": False, "telegram": False}
    assert preview_guard_checks["delivery_preview_has_no_send_side_effect"]["passed"] is True
    assert (
        preview_guard_checks[
            "delivery_preview_guard_check_names_match_expected_schema"
        ]["passed"]
        is True
    )
    assert preview_guard_checks[
        "delivery_preview_guard_check_names_match_expected_schema"
    ]["actual"] == preview_guard_checks[
        "delivery_preview_guard_check_names_match_expected_schema"
    ]["expected"]
    assert preview_guard_checks[
        "delivery_preview_guard_check_names_match_expected_schema"
    ]["actual"][:3] == [
        "hermes_payload_ref_matches_structured_payload",
        "hermes_numeric_authority_matches_payload_ref",
        "telegram_format_schema_declared",
    ]
    assert preview_guard_checks[
        "delivery_preview_guard_check_names_match_expected_schema"
    ]["actual"][-3:] == [
        "delivery_preview_guard_check_names_match_expected_schema",
        "delivery_preview_guard_check_keys_match_expected_schema",
        "delivery_preview_payload_keys_match_expected_schema",
    ]
    assert (
        preview_guard_checks[
            "delivery_preview_guard_check_keys_match_expected_schema"
        ]["passed"]
        is True
    )
    assert preview_guard_checks[
        "delivery_preview_guard_check_keys_match_expected_schema"
    ]["actual"] == preview_guard_checks[
        "delivery_preview_guard_check_keys_match_expected_schema"
    ]["expected"]
    assert preview_guard_checks[
        "delivery_preview_guard_check_keys_match_expected_schema"
    ]["actual"]["special_check_keys"][
        "telegram_unrequested_sections_absent_from_preview"
    ] == [
        "name",
        "passed",
        "expected_absent",
        "actual_present",
    ]
    assert preview_guard_checks[
        "delivery_preview_guard_check_keys_match_expected_schema"
    ]["actual"]["special_check_keys"]["telegram_chunks_fit_max_chars"] == [
        "name",
        "passed",
        "expected_max_chars",
        "actual_chars",
    ]
    assert (
        preview_guard_checks[
            "delivery_preview_payload_keys_match_expected_schema"
        ]["passed"]
        is True
    )
    assert preview_guard_checks[
        "delivery_preview_payload_keys_match_expected_schema"
    ]["actual"] == preview_guard_checks[
        "delivery_preview_payload_keys_match_expected_schema"
    ]["expected"]
    assert preview_guard_checks[
        "delivery_preview_payload_keys_match_expected_schema"
    ]["actual"]["preview_keys"] == ["channels", "guard"]
    assert preview_guard_checks[
        "delivery_preview_payload_keys_match_expected_schema"
    ]["actual"]["channel_names"] == ["hermes", "telegram"]
    assert preview_guard_checks[
        "delivery_preview_payload_keys_match_expected_schema"
    ]["actual"]["telegram_chunk_keys"] == [["index", "chars", "text"]]
    report_guard_checks = {
        check["name"]: check for check in payload["report_contract_guard"]["checks"]
    }
    assert payload["report_contract_guard"]["status"] == "ok"
    assert all(check["passed"] for check in payload["report_contract_guard"]["checks"])
    assert (
        report_guard_checks["delivery_cron_intents_match_report_intent_registry"][
            "passed"
        ]
        is True
    )
    assert report_guard_checks[
        "delivery_cron_intents_match_report_intent_registry"
    ]["actual"] == [
        "pre_market_swing_report",
        "intraday_risk_watch",
        "post_market_review",
    ]
    assert (
        report_guard_checks["delivery_contract_has_no_network_side_effect"]["passed"]
        is True
    )
    assert report_guard_checks["delivery_contract_has_no_network_side_effect"][
        "expected"
    ] is False
    assert report_guard_checks["delivery_contract_has_no_network_side_effect"][
        "actual"
    ] == {"hermes": False, "telegram": False}
    assert (
        report_guard_checks["delivery_contract_has_no_send_side_effect"]["passed"]
        is True
    )
    assert report_guard_checks["delivery_contract_has_no_send_side_effect"][
        "expected"
    ] is False
    assert report_guard_checks["delivery_contract_has_no_send_side_effect"][
        "actual"
    ] == {"hermes": False, "telegram": False}
    assert (
        report_guard_checks["delivery_contract_keys_match_expected_schema"]["passed"]
        is True
    )
    assert report_guard_checks["delivery_contract_keys_match_expected_schema"][
        "actual"
    ] == report_guard_checks["delivery_contract_keys_match_expected_schema"][
        "expected"
    ]
    assert report_guard_checks["delivery_contract_keys_match_expected_schema"][
        "actual"
    ]["contract_keys"] == ["channels", "cron_intents"]
    assert report_guard_checks["delivery_contract_keys_match_expected_schema"][
        "actual"
    ]["telegram_channel_keys"] == [
        "schema_version",
        "format",
        "network_call",
        "max_chars",
        "required_sections",
        "overflow_policy",
        "section_separator",
        "chunk_indexing",
        "send_call",
    ]
    assert report_guard_checks["delivery_channel_formats_match_expected"]["passed"] is True
    assert report_guard_checks["delivery_channel_formats_match_expected"]["actual"] == {
        "hermes": "structured_json_plus_text",
        "telegram": "plain_text",
    }
    assert report_guard_checks["report_telegram_max_chars_matches_expected"][
        "passed"
    ] is True
    assert report_guard_checks["report_telegram_max_chars_matches_expected"][
        "actual"
    ] == 3900
    assert report_guard_checks["report_telegram_schema_version_matches_expected"][
        "passed"
    ] is True
    assert report_guard_checks["report_telegram_schema_version_matches_expected"][
        "actual"
    ] == "telegram_report_format.v1"
    assert report_guard_checks[
        "report_telegram_chunking_contract_matches_expected"
    ]["passed"] is True
    assert report_guard_checks[
        "report_telegram_chunking_contract_matches_expected"
    ]["actual"] == {
        "overflow_policy": "split_on_section_boundary",
        "section_separator": "\n\n",
        "chunk_indexing": "1_based",
    }
    assert (
        report_guard_checks[
            "report_contract_guard_check_names_match_expected_schema"
        ]["passed"]
        is True
    )
    assert report_guard_checks[
        "report_contract_guard_check_names_match_expected_schema"
    ]["actual"] == report_guard_checks[
        "report_contract_guard_check_names_match_expected_schema"
    ]["expected"]
    assert report_guard_checks[
        "report_contract_guard_check_names_match_expected_schema"
    ]["actual"][-4:] == [
        "report_text_reflects_latest_signal_numeric_fields",
        "report_contract_guard_check_names_match_expected_schema",
        "report_contract_guard_check_keys_match_expected_schema",
        "report_contract_guard_keys_match_expected_schema",
    ]
    assert (
        report_guard_checks[
            "report_contract_guard_check_keys_match_expected_schema"
        ]["passed"]
        is True
    )
    assert report_guard_checks[
        "report_contract_guard_check_keys_match_expected_schema"
    ]["actual"] == report_guard_checks[
        "report_contract_guard_check_keys_match_expected_schema"
    ]["expected"]
    assert report_guard_checks[
        "report_contract_guard_check_keys_match_expected_schema"
    ]["actual"]["special_check_keys"]["telegram_text_fits_single_message"] == [
        "name",
        "passed",
        "expected_max_chars",
        "actual_chars",
    ]
    assert (
        report_guard_checks["report_contract_guard_keys_match_expected_schema"][
            "passed"
        ]
        is True
    )
    assert report_guard_checks["report_contract_guard_keys_match_expected_schema"][
        "actual"
    ] == ["status", "checks"]
    assert (
        report_guard_checks["delivery_numeric_authority_is_latest_signal_report"][
            "passed"
        ]
        is True
    )
    assert report_guard_checks["delivery_numeric_authority_is_latest_signal_report"][
        "expected"
    ] == "latest_signal_report"
    assert report_guard_checks["delivery_numeric_authority_is_latest_signal_report"][
        "actual"
    ] == payload["delivery_contract"]["channels"]["hermes"]["numeric_authority"]
    assert (
        report_guard_checks["report_text_reflects_latest_signal_numeric_fields"][
            "passed"
        ]
        is True
    )
    assert report_guard_checks["report_text_reflects_latest_signal_numeric_fields"][
        "expected"
    ] == {
        "action": payload["latest_signal_report"]["action"],
        "confidence": payload["latest_signal_report"]["confidence"],
        "final_score": payload["latest_signal_report"]["final_score"],
    }
    assert report_guard_checks["report_text_reflects_latest_signal_numeric_fields"][
        "actual"
    ] == {
        "decision_line_present": True,
        "confidence_line_present": True,
        "score_line_present": True,
    }
    assert payload["evidence_guard"]["status"] == "ok"
    assert all(check["passed"] for check in payload["evidence_guard"]["checks"])
    evidence_guard_checks = {
        check["name"]: check for check in payload["evidence_guard"]["checks"]
    }
    assert (
        evidence_guard_checks["evidence_guard_check_names_match_expected_schema"][
            "passed"
        ]
        is True
    )
    assert evidence_guard_checks[
        "evidence_guard_check_names_match_expected_schema"
    ]["actual"] == evidence_guard_checks[
        "evidence_guard_check_names_match_expected_schema"
    ]["expected"]
    assert evidence_guard_checks[
        "evidence_guard_check_names_match_expected_schema"
    ]["actual"][-5:] == [
        "risk_warnings_reflected_in_cautions",
        "flagged_conflicts_are_acknowledged",
        "evidence_guard_check_names_match_expected_schema",
        "evidence_guard_check_keys_match_expected_schema",
        "evidence_guard_keys_match_expected_schema",
    ]
    assert (
        evidence_guard_checks["evidence_guard_check_keys_match_expected_schema"][
            "passed"
        ]
        is True
    )
    assert evidence_guard_checks[
        "evidence_guard_check_keys_match_expected_schema"
    ]["actual"] == evidence_guard_checks[
        "evidence_guard_check_keys_match_expected_schema"
    ]["expected"]
    assert evidence_guard_checks[
        "evidence_guard_check_keys_match_expected_schema"
    ]["actual"]["special_check_keys"] == {
        "reason_summary_within_limit": [
            "name",
            "passed",
            "expected_max_chars",
            "actual_chars",
        ],
        "evidence_summary_within_limit": [
            "name",
            "passed",
            "expected_max_chars",
            "actual_chars",
        ],
        "conflict_flags_within_limit": [
            "name",
            "passed",
            "expected_max",
            "actual_count",
        ],
    }
    assert (
        evidence_guard_checks["evidence_guard_keys_match_expected_schema"]["passed"]
        is True
    )
    assert evidence_guard_checks["evidence_guard_keys_match_expected_schema"][
        "actual"
    ] == ["status", "checks"]
    assert sections["Entry"]
    assert sections["Stop"]
    assert sections["Take Profit"]
    assert sections["Cautions"]
    assert payload["text"].startswith("Target: TQQQ / QQQ")
    assert "Decision: BUY_WATCH" in payload["text"]
    assert payload["live_data_required"] is False


def test_latest_signal_report_propagates_live_signal_boundary(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    signal = reporting.score_leverage_swing("TQQQ")
    live_signal = {**signal, "live_data_required": True}
    monkeypatch.setattr(
        reporting,
        "score_leverage_swing",
        lambda asset="TQQQ", timeframe="swing_3d_10d": live_signal,
    )

    payload = generate_latest_signal_report("TQQQ")
    guard_checks = {
        check["name"]: check for check in payload["report_payload_guard"]["checks"]
    }

    assert payload["live_data_required"] is True
    assert guard_checks["report_payload_live_data_required_matches_expected"][
        "passed"
    ] is True
    assert guard_checks["report_payload_live_data_required_matches_expected"][
        "expected"
    ] is True
    assert guard_checks["report_payload_live_data_required_matches_expected"][
        "actual"
    ] is True
    assert payload["report_payload_guard"]["status"] == "ok"


def test_latest_signal_report_limits_evidence_and_flags_conflicts() -> None:
    payload = generate_latest_signal_report("TQQQ")
    contract = payload["evidence_contract"]
    context = payload["evidence_context"]
    cautions = {
        item
        for section in payload["sections"]
        if section["title"] == "Cautions"
        for item in section["items"]
    }

    assert len(context["reason_summary"]) <= contract["max_reason_summary_chars"]
    assert len(context["evidence_summary"]) <= contract["max_evidence_summary_chars"]
    assert len(context["conflict_flags"]) <= contract["max_conflict_flags"]
    assert {flag["name"] for flag in context["conflict_flags"]} == {
        "event_risk_vs_long_bias",
        "mixed_component_signal",
    }
    assert all(flag["status"] == "acknowledged" for flag in context["conflict_flags"])
    assert set(context["risk_warnings"]).issubset(cautions)
    assert context["component_extremes"]["spread"] > 0


def test_degraded_report_reflects_data_warnings_in_cautions() -> None:
    signal = {
        **load_degraded_report_fixture(),
        "run_id": "run_degraded_fixture",
        "entry": {"trigger": "Wait for fresh macro and news evidence before entry."},
        "stop": ["No active stop until a fresh entry setup appears."],
        "take_profit": ["No active take-profit until a fresh entry setup appears."],
        "risk_warnings": ["Freshness warnings reduce confidence in the current read."],
        "component_scores": {
            "trend": 0.34,
            "momentum": 0.42,
            "volatility": 0.46,
            "macro": 0.22,
            "event_safety": 0.28,
            "theme": 0.31,
            "event_risk": 0.72,
        },
    }
    report = reporting._latest_signal_report_from_signal(signal)
    sections = reporting._report_sections(
        signal,
        report,
        reporting._report_intent_contract("pre_market_swing_report"),
    )
    evidence_context = reporting._evidence_context(signal, report)
    evidence_guard = reporting._evidence_guard(
        report,
        sections,
        evidence_context,
        reporting.EVIDENCE_SUMMARY_CONTRACT,
    )
    cautions = {
        item
        for section in sections
        if section["title"] == "Cautions"
        for item in section["items"]
    }
    guard_checks = {check["name"]: check for check in evidence_guard["checks"]}

    assert report["degraded_mode"] is True
    assert report["data_warnings"]
    assert set(report["data_warnings"]).issubset(cautions)
    assert "data_quality_caveat" in {
        flag["name"] for flag in evidence_context["conflict_flags"]
    }
    assert guard_checks["data_warnings_reflected_in_cautions"]["passed"] is True
    assert guard_checks["evidence_guard_check_names_match_expected_schema"][
        "passed"
    ] is True
    assert guard_checks["evidence_guard_check_names_match_expected_schema"][
        "actual"
    ] == guard_checks["evidence_guard_check_names_match_expected_schema"][
        "expected"
    ]
    assert guard_checks["evidence_guard_check_names_match_expected_schema"][
        "actual"
    ][-4:] == [
        "data_warnings_reflected_in_cautions",
        "evidence_guard_check_names_match_expected_schema",
        "evidence_guard_check_keys_match_expected_schema",
        "evidence_guard_keys_match_expected_schema",
    ]
    assert guard_checks["evidence_guard_check_keys_match_expected_schema"][
        "passed"
    ] is True
    assert guard_checks["evidence_guard_check_keys_match_expected_schema"][
        "actual"
    ] == guard_checks["evidence_guard_check_keys_match_expected_schema"][
        "expected"
    ]
    assert "data_warnings_reflected_in_cautions" in guard_checks[
        "evidence_guard_check_keys_match_expected_schema"
    ]["actual"]["default_check_names"]
    assert guard_checks["evidence_guard_keys_match_expected_schema"][
        "passed"
    ] is True
    assert guard_checks["evidence_guard_keys_match_expected_schema"][
        "actual"
    ] == ["status", "checks"]
    assert evidence_guard["status"] == "ok"


def test_latest_signal_report_supports_cron_intents() -> None:
    expected_sections = {
        "pre_market_swing_report": [
            "Target",
            "Decision",
            "Reasons",
            "Entry",
            "Stop",
            "Take Profit",
            "Cautions",
        ],
        "intraday_risk_watch": ["Target", "Decision", "Stop", "Cautions"],
        "post_market_review": [
            "Target",
            "Decision",
            "Reasons",
            "Take Profit",
            "Cautions",
        ],
    }
    expected_prompt_terms = {
        "pre_market_swing_report": [
            "action",
            "confidence",
            "entry",
            "stop",
            "take_profit",
            "risk",
            "data_warnings",
        ],
        "intraday_risk_watch": [
            "action",
            "confidence",
            "stop",
            "risk",
            "data_warnings",
        ],
        "post_market_review": [
            "action",
            "confidence",
            "take_profit",
            "risk",
            "data_warnings",
        ],
    }
    expected_schedule_hints = {
        "pre_market_swing_report": "weekday_pre_market",
        "intraday_risk_watch": "market_hours",
        "post_market_review": "post_market",
    }
    expected_decision_focus = {
        "pre_market_swing_report": "new_swing_entry_and_watchlist",
        "intraday_risk_watch": "risk_monitoring_trim_or_exit_checks",
        "post_market_review": "end_of_day_review_and_next_session_plan",
    }
    for intent, sections in expected_sections.items():
        payload = generate_latest_signal_report("TQQQ", report_intent=intent)
        section_titles = [section["title"] for section in payload["sections"]]
        guard_checks = {
            check["name"]: check for check in payload["report_contract_guard"]["checks"]
        }
        preview_guard_checks = {
            check["name"]: check
            for check in payload["delivery_preview"]["guard"]["checks"]
        }
        telegram_chunks = payload["delivery_preview"]["channels"]["telegram"]["chunks"]

        assert payload["report_intent"] == intent
        assert payload["report_intent_contract"]["name"] == intent
        assert payload["report_intent_contract"]["required_sections"] == sections
        assert guard_checks["report_sections_match_intent_order"]["passed"] is True
        assert guard_checks["report_sections_match_intent_order"]["actual"] == sections
        assert guard_checks["report_text_sections_match_intent_order"][
            "passed"
        ] is True
        assert guard_checks["report_text_sections_match_intent_order"][
            "actual"
        ]["found_sections"] == sections
        assert guard_checks["report_text_sections_match_intent_order"][
            "actual"
        ]["positions_ascending"] is True
        assert guard_checks["report_intent_contract_keys_match_expected_schema"][
            "passed"
        ] is True
        assert guard_checks["report_intent_contract_keys_match_expected_schema"][
            "actual"
        ] == [
            "name",
            "schedule_hint",
            "decision_focus",
            "required_sections",
        ]
        assert guard_checks["report_intent_contract_matches_registry"][
            "passed"
        ] is True
        assert guard_checks["report_intent_contract_matches_registry"][
            "actual"
        ] == {
            "name": intent,
            "schedule_hint": expected_schedule_hints[intent],
            "decision_focus": expected_decision_focus[intent],
            "required_sections": sections,
        }
        assert payload["prompt_contract"]["must_include"] == expected_prompt_terms[intent]
        assert (
            guard_checks["report_prompt_must_include_matches_intent_terms"][
                "passed"
            ]
            is True
        )
        assert guard_checks["report_prompt_must_include_matches_intent_terms"][
            "actual"
        ] == expected_prompt_terms[intent]
        assert guard_checks["report_prompt_contract_keys_match_expected_schema"][
            "passed"
        ] is True
        assert guard_checks["report_prompt_contract_keys_match_expected_schema"][
            "actual"
        ] == [
            "numeric_authority",
            "llm_role",
            "must_include",
        ]
        assert guard_checks["report_prompt_contract_identity_matches_expected"][
            "passed"
        ] is True
        assert guard_checks["report_prompt_contract_identity_matches_expected"][
            "actual"
        ] == {
            "numeric_authority": "Use MCP numeric fields as source of truth.",
            "llm_role": "Summarize conflicts, caveats, and final wording only.",
        }
        assert payload["delivery_contract"]["channels"]["telegram"][
            "required_sections"
        ] == sections
        assert guard_checks["telegram_required_sections_match_intent"]["passed"] is True
        assert guard_checks["telegram_required_sections_match_intent"]["expected"] == sections
        assert guard_checks["telegram_required_sections_match_intent"]["actual"] == sections
        assert (
            preview_guard_checks["telegram_required_sections_present_in_preview"][
                "passed"
            ]
            is True
        )
        assert preview_guard_checks["telegram_format_schema_declared"]["passed"] is True
        assert (
            preview_guard_checks["telegram_format_schema_declared"]["actual"]
            == "telegram_report_format.v1"
        )
        assert preview_guard_checks["telegram_required_sections_present_in_preview"][
            "expected"
        ] == [f"{section}:" for section in sections]
        assert (
            preview_guard_checks["telegram_unrequested_sections_absent_from_preview"][
                "passed"
            ]
            is True
        )
        assert preview_guard_checks["telegram_unrequested_sections_absent_from_preview"][
            "actual_present"
        ] == []
        assert preview_guard_checks["telegram_unrequested_sections_absent_from_preview"][
            "expected_absent"
        ] == [
            f"{section}:"
            for section in reporting.TELEGRAM_KNOWN_SECTIONS
            if section not in sections
        ]
        assert (
            preview_guard_checks["telegram_chunks_are_1_based_sequential"]["passed"]
            is True
        )
        assert preview_guard_checks["telegram_chunks_are_1_based_sequential"][
            "actual"
        ]["indexes"] == list(range(1, len(telegram_chunks) + 1))
        assert preview_guard_checks["telegram_message_count_matches_chunks"][
            "actual"
        ] == len(telegram_chunks)
        assert (
            preview_guard_checks["telegram_single_message_flag_matches_chunk_count"][
                "actual"
            ]
            == (len(telegram_chunks) == 1)
        )
        assert (
            preview_guard_checks["telegram_chunk_char_counts_match_text"]["passed"]
            is True
        )
        assert preview_guard_checks["telegram_chunks_are_nonempty"]["passed"] is True
        assert (
            preview_guard_checks["telegram_section_separator_preserves_preview_text"][
                "passed"
            ]
            is True
        )
        assert (
            preview_guard_checks["telegram_overflow_policy_splits_on_section_boundary"][
                "passed"
            ]
            is True
        )
        assert preview_guard_checks["telegram_chunks_fit_max_chars"]["passed"] is True
        assert preview_guard_checks["telegram_chunks_preserve_text"]["passed"] is True
        assert (
            preview_guard_checks["delivery_preview_has_no_network_side_effect"][
                "passed"
            ]
            is True
        )
        assert preview_guard_checks["delivery_preview_has_no_network_side_effect"][
            "actual"
        ] == {"hermes": False, "telegram": False}
        assert (
            preview_guard_checks[
                "delivery_preview_guard_check_names_match_expected_schema"
            ]["passed"]
            is True
        )
        assert preview_guard_checks[
            "delivery_preview_guard_check_names_match_expected_schema"
        ]["actual"] == preview_guard_checks[
            "delivery_preview_guard_check_names_match_expected_schema"
        ]["expected"]
        assert (
            preview_guard_checks[
                "delivery_preview_guard_check_keys_match_expected_schema"
            ]["passed"]
            is True
        )
        assert preview_guard_checks[
            "delivery_preview_guard_check_keys_match_expected_schema"
        ]["actual"] == preview_guard_checks[
            "delivery_preview_guard_check_keys_match_expected_schema"
        ]["expected"]
        assert (
            preview_guard_checks[
                "delivery_preview_payload_keys_match_expected_schema"
            ]["passed"]
            is True
        )
        assert preview_guard_checks[
            "delivery_preview_payload_keys_match_expected_schema"
        ]["actual"] == preview_guard_checks[
            "delivery_preview_payload_keys_match_expected_schema"
        ]["expected"]
        assert section_titles == sections
        assert all(section["items"] for section in payload["sections"])
        assert "\n\n".join(chunk["text"] for chunk in telegram_chunks) == payload["text"]
        assert [chunk["index"] for chunk in telegram_chunks] == list(
            range(1, len(telegram_chunks) + 1)
        )
        assert payload["report_contract_guard"]["status"] == "ok"
        assert (
            guard_checks["delivery_cron_intents_match_report_intent_registry"][
                "passed"
            ]
            is True
        )
        assert guard_checks[
            "delivery_cron_intents_match_report_intent_registry"
        ]["actual"] == [
            "pre_market_swing_report",
            "intraday_risk_watch",
            "post_market_review",
        ]
        assert (
            guard_checks["delivery_contract_has_no_network_side_effect"]["passed"]
            is True
        )
        assert guard_checks["delivery_contract_has_no_network_side_effect"][
            "actual"
        ] == {"hermes": False, "telegram": False}
        assert (
            guard_checks["delivery_contract_has_no_send_side_effect"]["passed"]
            is True
        )
        assert guard_checks["delivery_contract_has_no_send_side_effect"][
            "expected"
        ] is False
        assert guard_checks["delivery_contract_has_no_send_side_effect"][
            "actual"
        ] == {"hermes": False, "telegram": False}
        assert (
            guard_checks["delivery_contract_keys_match_expected_schema"]["passed"]
            is True
        )
        assert guard_checks["delivery_contract_keys_match_expected_schema"][
            "actual"
        ] == guard_checks["delivery_contract_keys_match_expected_schema"][
            "expected"
        ]
        assert (
            guard_checks["delivery_channel_formats_match_expected"]["passed"]
            is True
        )
        assert guard_checks["delivery_channel_formats_match_expected"]["actual"] == {
            "hermes": "structured_json_plus_text",
            "telegram": "plain_text",
        }
        assert guard_checks["report_telegram_max_chars_matches_expected"][
            "passed"
        ] is True
        assert guard_checks["report_telegram_max_chars_matches_expected"][
            "actual"
        ] == 3900
        assert guard_checks["report_telegram_schema_version_matches_expected"][
            "passed"
        ] is True
        assert guard_checks["report_telegram_schema_version_matches_expected"][
            "actual"
        ] == "telegram_report_format.v1"
        assert guard_checks[
            "report_telegram_chunking_contract_matches_expected"
        ]["passed"] is True
        assert guard_checks[
            "report_telegram_chunking_contract_matches_expected"
        ]["actual"] == {
            "overflow_policy": "split_on_section_boundary",
            "section_separator": "\n\n",
            "chunk_indexing": "1_based",
        }
        assert (
            guard_checks[
                "report_contract_guard_check_names_match_expected_schema"
            ]["passed"]
            is True
        )
        assert guard_checks[
            "report_contract_guard_check_names_match_expected_schema"
        ]["actual"] == guard_checks[
            "report_contract_guard_check_names_match_expected_schema"
        ]["expected"]
        assert (
            guard_checks[
                "report_contract_guard_check_keys_match_expected_schema"
            ]["passed"]
            is True
        )
        assert guard_checks[
            "report_contract_guard_check_keys_match_expected_schema"
        ]["actual"] == guard_checks[
            "report_contract_guard_check_keys_match_expected_schema"
        ]["expected"]
        assert (
            guard_checks["report_contract_guard_keys_match_expected_schema"]["passed"]
            is True
        )
        assert guard_checks["report_contract_guard_keys_match_expected_schema"][
            "actual"
        ] == ["status", "checks"]
        assert (
            guard_checks["delivery_numeric_authority_is_latest_signal_report"][
                "passed"
            ]
            is True
        )
        assert guard_checks["delivery_numeric_authority_is_latest_signal_report"][
            "expected"
        ] == "latest_signal_report"
        assert guard_checks["delivery_numeric_authority_is_latest_signal_report"][
            "actual"
        ] == payload["delivery_contract"]["channels"]["hermes"][
            "numeric_authority"
        ]
        assert (
            guard_checks["report_text_reflects_latest_signal_numeric_fields"]["passed"]
            is True
        )
        assert guard_checks["report_text_reflects_latest_signal_numeric_fields"][
            "actual"
        ] == {
            "decision_line_present": True,
            "confidence_line_present": True,
            "score_line_present": True,
        }
        assert guard_checks["prompt_must_include_is_covered"][
            "expected"
        ] == expected_prompt_terms[intent]
        assert guard_checks["report_prompt_must_include_matches_intent_terms"][
            "expected"
        ] == expected_prompt_terms[intent]
        assert payload["live_data_required"] is False

    intraday_text = generate_latest_signal_report(
        "TQQQ", report_intent="intraday_risk_watch"
    )["text"]
    post_market_text = generate_latest_signal_report(
        "TQQQ", report_intent="post_market_review"
    )["text"]

    assert "Stop:" in intraday_text
    assert "Entry:" not in intraday_text
    assert "Take Profit:" not in intraday_text
    assert "Take Profit:" in post_market_text
    assert "Entry:" not in post_market_text
    assert "Stop:" not in post_market_text


def test_latest_signal_report_rejects_unsupported_report_intent_at_boundary() -> None:
    unsupported_intent = "opening_gap_scalp"
    expected_allowed = ", ".join(sorted(reporting.REPORT_INTENTS))

    with pytest.raises(ValueError) as exc_info:
        generate_latest_signal_report("TQQQ", report_intent=unsupported_intent)

    message = str(exc_info.value)
    assert unsupported_intent not in reporting.REPORT_INTENTS
    assert f"unsupported report_intent: {unsupported_intent}" in message
    assert f"allowed: {expected_allowed}" in message


def test_latest_signal_report_trims_and_lowercases_report_intent() -> None:
    payload = generate_latest_signal_report(
        "TQQQ",
        report_intent=" INTRADAY_RISK_WATCH ",
    )

    assert payload["report_intent"] == "intraday_risk_watch"
    assert payload["report_intent_contract"]["name"] == "intraday_risk_watch"
    assert payload["report_payload_guard"]["status"] == "ok"
    assert [section["title"] for section in payload["sections"]] == [
        "Target",
        "Decision",
        "Stop",
        "Cautions",
    ]


@pytest.mark.parametrize("report_intent", ["   ", None, 123])
def test_latest_signal_report_rejects_invalid_report_intent_identity(
    report_intent,
) -> None:
    with pytest.raises(ValueError, match="report_intent must be a nonempty string"):
        generate_latest_signal_report("TQQQ", report_intent=report_intent)


def test_latest_signal_report_rejects_report_intent_control_character() -> None:
    with pytest.raises(
        ValueError,
        match="report_intent must not contain control characters",
    ):
        generate_latest_signal_report(
            "TQQQ",
            report_intent="intraday_risk_watch\n",
        )


def test_latest_signal_report_trims_and_uppercases_asset_identity() -> None:
    payload = generate_latest_signal_report(" tqqq ")
    report = payload["latest_signal_report"]

    assert payload["asset"] == "TQQQ"
    assert report["asset"] == "TQQQ"
    assert payload["underlying"] == "QQQ"
    assert payload["source_signal_ref"]["signal_id"].endswith("_tqqq")
    assert " tqqq " not in payload["text"]
    assert payload["report_payload_guard"]["status"] == "ok"


@pytest.mark.parametrize("asset", ["   ", None, 123])
def test_latest_signal_report_rejects_invalid_asset_identity(
    asset,
    tmp_path: Path,
) -> None:
    with pytest.raises(ValueError, match="asset must be a nonempty string"):
        generate_latest_signal_report(
            asset,
            include_chart=True,
            chart_output_dir=str(tmp_path),
        )

    assert not any(tmp_path.iterdir())


def test_latest_signal_report_rejects_asset_control_character(
    tmp_path: Path,
) -> None:
    with pytest.raises(
        ValueError,
        match="asset must not contain control characters",
    ):
        generate_latest_signal_report(
            "TQQQ\n",
            include_chart=True,
            chart_output_dir=str(tmp_path),
        )

    assert not any(tmp_path.iterdir())


def test_latest_signal_report_trims_timeframe_identity() -> None:
    payload = generate_latest_signal_report("TQQQ", timeframe=" swing_3d_10d ")
    report = payload["latest_signal_report"]
    guard_checks = {
        check["name"]: check for check in payload["report_payload_guard"]["checks"]
    }

    assert payload["timeframe"] == "swing_3d_10d"
    assert report["timeframe"] == "swing_3d_10d"
    assert payload["report_payload_guard"]["status"] == "ok"
    assert guard_checks["report_payload_top_level_identity_matches_latest_signal_report"][
        "actual"
    ]["timeframe"] == "swing_3d_10d"


@pytest.mark.parametrize("timeframe", ["   ", None, 123])
def test_latest_signal_report_rejects_invalid_timeframe_identity(
    timeframe,
    tmp_path: Path,
) -> None:
    with pytest.raises(ValueError, match="timeframe must be a nonempty string"):
        generate_latest_signal_report(
            "TQQQ",
            timeframe=timeframe,
            include_chart=True,
            chart_output_dir=str(tmp_path),
        )

    assert not any(tmp_path.iterdir())


def test_latest_signal_report_rejects_timeframe_control_character(
    tmp_path: Path,
) -> None:
    with pytest.raises(
        ValueError,
        match="timeframe must not contain control characters",
    ):
        generate_latest_signal_report(
            "TQQQ",
            timeframe="swing_3d_10d\n",
            include_chart=True,
            chart_output_dir=str(tmp_path),
        )

    assert not any(tmp_path.iterdir())


@pytest.mark.parametrize("include_chart", ["false", "true", 0, 1, None])
def test_latest_signal_report_rejects_non_bool_include_chart(
    include_chart,
    tmp_path: Path,
) -> None:
    with pytest.raises(ValueError, match="include_chart must be a boolean"):
        generate_latest_signal_report(
            "TQQQ",
            include_chart=include_chart,
            chart_output_dir=str(tmp_path),
        )

    assert not any(tmp_path.iterdir())


def test_latest_signal_report_trims_and_lowercases_chart_timeframe(
    tmp_path: Path,
) -> None:
    payload = generate_latest_signal_report(
        "TQQQ",
        include_chart=True,
        chart_timeframe=" 1D ",
        chart_output_dir=f" {tmp_path} ",
    )
    chart_ref = payload["latest_signal_report"]["chart_ref"]
    chart_path = tmp_path / "QQQ_1d.png"

    assert chart_path.exists()
    assert not (tmp_path / "QQQ_ 1D .png").exists()
    assert chart_ref["ref"] == str(chart_path)
    assert chart_ref["metadata"]["timeframe_supported"] is True
    assert payload["chart_code_guard"]["status"] == "ok"


@pytest.mark.parametrize("chart_timeframe", ["   ", None, 123])
def test_latest_signal_report_rejects_invalid_chart_timeframe(
    chart_timeframe,
    tmp_path: Path,
) -> None:
    with pytest.raises(ValueError, match="chart_timeframe must be a nonempty string"):
        generate_latest_signal_report(
            "TQQQ",
            include_chart=True,
            chart_timeframe=chart_timeframe,
            chart_output_dir=str(tmp_path),
        )

    assert not any(tmp_path.iterdir())


def test_latest_signal_report_rejects_chart_timeframe_control_character(
    tmp_path: Path,
) -> None:
    with pytest.raises(
        ValueError,
        match="chart_timeframe must not contain control characters",
    ):
        generate_latest_signal_report(
            "TQQQ",
            include_chart=True,
            chart_timeframe="1d\n",
            chart_output_dir=str(tmp_path),
        )

    assert not any(tmp_path.iterdir())


@pytest.mark.parametrize("chart_output_dir", ["", "   ", [], False])
def test_latest_signal_report_rejects_invalid_chart_output_dir(
    chart_output_dir,
    tmp_path: Path,
) -> None:
    with pytest.raises(ValueError, match="chart_output_dir must be a nonempty string"):
        generate_latest_signal_report(
            "TQQQ",
            include_chart=True,
            chart_output_dir=chart_output_dir,
        )

    assert not any(tmp_path.iterdir())


def test_latest_signal_report_rejects_chart_output_dir_control_character(
    tmp_path: Path,
    monkeypatch,
) -> None:
    chart_dir = tmp_path / "charts"

    def unexpected_score_call(*args, **kwargs):
        del args, kwargs
        raise AssertionError("score should not run for invalid chart_output_dir")

    monkeypatch.setattr(reporting, "score_leverage_swing", unexpected_score_call)

    with pytest.raises(
        ValueError,
        match="chart_output_dir must not contain control characters",
    ):
        generate_latest_signal_report(
            "TQQQ",
            include_chart=True,
            chart_output_dir=f"{chart_dir}\n",
        )

    assert not chart_dir.exists()


@pytest.mark.parametrize(
    "extra_evidence_cards",
    ["not-a-list", {"evidence_id": "manual_document_summary"}, False],
)
def test_latest_signal_report_rejects_invalid_extra_evidence_cards_container(
    extra_evidence_cards,
    tmp_path: Path,
    monkeypatch,
) -> None:
    chart_dir = tmp_path / "charts"

    def unexpected_score_call(*args, **kwargs):
        del args, kwargs
        raise AssertionError("score should not run for invalid extra_evidence_cards")

    monkeypatch.setattr(reporting, "score_leverage_swing", unexpected_score_call)

    with pytest.raises(
        ValueError,
        match="extra_evidence_cards must be a list of objects",
    ):
        generate_latest_signal_report(
            "TQQQ",
            include_chart=True,
            chart_output_dir=str(chart_dir),
            extra_evidence_cards=extra_evidence_cards,
        )

    assert not chart_dir.exists()


def test_latest_signal_report_rejects_extra_evidence_card_non_object(
    tmp_path: Path,
    monkeypatch,
) -> None:
    chart_dir = tmp_path / "charts"

    def unexpected_score_call(*args, **kwargs):
        del args, kwargs
        raise AssertionError("score should not run for invalid extra_evidence_cards")

    monkeypatch.setattr(reporting, "score_leverage_swing", unexpected_score_call)

    with pytest.raises(
        ValueError,
        match="extra_evidence_cards items must be objects",
    ):
        generate_latest_signal_report(
            "TQQQ",
            include_chart=True,
            chart_output_dir=str(chart_dir),
            extra_evidence_cards=["not-an-object"],
        )

    assert not chart_dir.exists()


def test_cron_prompt_pack_covers_hermes_report_schedules_without_side_effects() -> None:
    payload = generate_cron_prompt_pack("TQQQ")
    prompts = {prompt["name"]: prompt for prompt in payload["prompts"]}
    contract = payload["cron_prompt_contract"]
    guard_checks = {
        check["name"]: check for check in payload["cron_prompt_guard"]["checks"]
    }

    assert payload["schema_version"] == "hermes_cron_prompt_pack.v1"
    assert (
        guard_checks["cron_prompt_pack_schema_version_matches_expected"]["passed"]
        is True
    )
    assert guard_checks["cron_prompt_pack_schema_version_matches_expected"][
        "actual"
    ] == "hermes_cron_prompt_pack.v1"
    expected_pack_keys = [
        "schema_version",
        "asset",
        "timeframe",
        "prompts",
        "cron_prompt_contract",
        "cron_prompt_guard",
        "live_data_required",
    ]
    assert (
        guard_checks["cron_prompt_pack_keys_match_expected_schema"]["passed"]
        is True
    )
    assert guard_checks["cron_prompt_pack_keys_match_expected_schema"][
        "actual"
    ] == expected_pack_keys
    assert guard_checks["pack_live_data_required_matches_contract"]["passed"] is True
    assert guard_checks["pack_live_data_required_matches_contract"]["actual"] is False
    assert payload["asset"] == "TQQQ"
    assert payload["timeframe"] == "swing_3d_10d"
    assert guard_checks["cron_prompt_contract_name_matches_schema"]["passed"] is True
    assert guard_checks["cron_prompt_contract_name_matches_schema"][
        "actual"
    ] == "hermes_cron_prompt_pack"
    expected_contract_keys = [
        "name",
        "supported_report_intents",
        "include_position_review",
        "scheduler_added",
        "cron_runner_added",
        "network_call",
        "telegram_send",
        "telegram_credentials_required",
        "order_submission",
        "secret_values_returned",
        "live_data_required",
        "manual_setup_required_before_unattended_run",
    ]
    expected_prompt_keys = [
        "name",
        "schedule_hint",
        "decision_focus",
        "tool_name",
        "input_json",
        "expected_output_schema",
        "live_data_required",
        "idempotency_key_template",
        "expected_sections",
        "telegram_format_schema",
        "numeric_authority",
        "prompt",
        "delivery_preview_path",
    ]
    expected_guard_check_keys = [
        "name",
        "passed",
        "expected",
        "actual",
    ]
    expected_guard_keys = [
        "status",
        "checks",
    ]
    assert (
        guard_checks["cron_prompt_contract_keys_match_expected_schema"]["passed"]
        is True
    )
    assert guard_checks["cron_prompt_contract_keys_match_expected_schema"][
        "actual"
    ] == expected_contract_keys
    assert (
        guard_checks["cron_prompt_prompt_keys_match_expected_schema"]["passed"]
        is True
    )
    assert guard_checks["cron_prompt_prompt_keys_match_expected_schema"][
        "actual"
    ] == {
        name: expected_prompt_keys
        for name in prompts
    }
    assert (
        guard_checks["cron_prompt_guard_keys_match_expected_schema"]["passed"]
        is True
    )
    assert guard_checks["cron_prompt_guard_keys_match_expected_schema"][
        "actual"
    ] == expected_guard_keys
    assert (
        guard_checks["cron_prompt_guard_check_names_match_expected_schema"]["passed"]
        is True
    )
    assert guard_checks["cron_prompt_guard_check_names_match_expected_schema"][
        "actual"
    ] == guard_checks["cron_prompt_guard_check_names_match_expected_schema"][
        "expected"
    ]
    assert guard_checks["cron_prompt_guard_check_names_match_expected_schema"][
        "actual"
    ][:3] == [
        "cron_prompt_pack_schema_version_matches_expected",
        "cron_prompt_pack_keys_match_expected_schema",
        "cron_prompt_contract_name_matches_schema",
    ]
    assert guard_checks["cron_prompt_guard_check_names_match_expected_schema"][
        "actual"
    ][-3:] == [
        "cron_prompt_guard_keys_match_expected_schema",
        "cron_prompt_guard_check_names_match_expected_schema",
        "cron_prompt_guard_check_keys_match_expected_schema",
    ]
    assert len(
        guard_checks["cron_prompt_guard_check_names_match_expected_schema"]["actual"]
    ) == len(payload["cron_prompt_guard"]["checks"])
    assert (
        guard_checks["cron_prompt_guard_check_keys_match_expected_schema"]["passed"]
        is True
    )
    assert all(
        check_keys == expected_guard_check_keys
        for check_keys in guard_checks[
            "cron_prompt_guard_check_keys_match_expected_schema"
        ]["actual"].values()
    )
    assert (
        guard_checks["cron_prompt_guard_check_keys_match_expected_schema"]["actual"][
            "cron_prompt_pack_keys_match_expected_schema"
        ]
        == expected_guard_check_keys
    )
    assert guard_checks["prompt_assets_match_pack_asset"]["passed"] is True
    assert guard_checks["prompt_assets_match_pack_asset"]["actual"] == {
        name: "TQQQ"
        for name in prompts
    }
    assert guard_checks["report_prompt_timeframes_match_pack_timeframe"][
        "passed"
    ] is True
    assert guard_checks["report_prompt_timeframes_match_pack_timeframe"][
        "actual"
    ] == {
        "pre_market_swing_report": "swing_3d_10d",
        "intraday_risk_watch": "swing_3d_10d",
        "post_market_review": "swing_3d_10d",
    }
    assert (
        guard_checks["include_position_review_contract_matches_request"]["passed"]
        is True
    )
    assert guard_checks["include_position_review_contract_matches_request"][
        "actual"
    ] is True
    assert set(contract["supported_report_intents"]).issubset(prompts)
    assert guard_checks["supported_report_intents_match_registry"]["passed"] is True
    assert guard_checks["supported_report_intents_match_registry"]["actual"] == [
        "pre_market_swing_report",
        "intraday_risk_watch",
        "post_market_review",
    ]
    assert "position_review" in prompts
    assert prompts["pre_market_swing_report"]["tool_name"] == (
        "generate_latest_signal_report"
    )
    assert prompts["intraday_risk_watch"]["schedule_hint"] == "market_hours"
    assert prompts["post_market_review"]["input_json"]["report_intent"] == (
        "post_market_review"
    )
    for intent in contract["supported_report_intents"]:
        report = generate_latest_signal_report(
            **prompts[intent]["input_json"],
        )
        assert prompts[intent]["expected_sections"] == report[
            "report_intent_contract"
        ]["required_sections"]
        assert prompts[intent]["input_json"]["report_intent"] == intent
    assert (
        guard_checks["position_review_prompt_expected_sections_match_contract"][
            "passed"
        ]
        is True
    )
    assert guard_checks["position_review_prompt_expected_sections_match_contract"][
        "actual"
    ] == {
        "position_review": [
            "Position",
            "Decision",
            "Rationale",
            "Stop",
            "Take Profit",
            "Risk",
        ]
    }
    assert prompts["position_review"]["tool_name"] == "generate_position_review_report"
    assert all(
        prompt["delivery_preview_path"] == "delivery_preview.channels.telegram.chunks"
        for prompt in payload["prompts"]
    )
    assert contract["scheduler_added"] is False
    assert contract["cron_runner_added"] is False
    assert contract["network_call"] is False
    assert contract["telegram_send"] is False
    assert contract["order_submission"] is False
    assert contract["live_data_required"] is False
    assert all(prompt["live_data_required"] is False for prompt in payload["prompts"])
    assert payload["cron_prompt_guard"]["status"] == "ok"
    assert all(check["passed"] for check in payload["cron_prompt_guard"]["checks"])
    assert guard_checks["prompt_names_match_contract_and_position_option"][
        "passed"
    ] is True
    assert guard_checks["prompt_names_match_contract_and_position_option"][
        "actual"
    ] == [
        "intraday_risk_watch",
        "position_review",
        "post_market_review",
        "pre_market_swing_report",
    ]
    assert guard_checks["prompt_names_match_contract_order_and_are_unique"][
        "passed"
    ] is True
    assert guard_checks["prompt_names_match_contract_order_and_are_unique"][
        "expected"
    ] == [
        "pre_market_swing_report",
        "intraday_risk_watch",
        "post_market_review",
        "position_review",
    ]
    assert guard_checks["prompt_names_match_contract_order_and_are_unique"][
        "actual"
    ] == [
        "pre_market_swing_report",
        "intraday_risk_watch",
        "post_market_review",
        "position_review",
    ]
    assert guard_checks["prompt_text_references_prompt_name"]["passed"] is True
    assert guard_checks["prompt_text_references_prompt_name"]["actual"] == {
        name: True
        for name in prompts
    }
    assert guard_checks["prompt_text_references_prompt_name"]["expected"] == {
        "pre_market_swing_report": "Prompt name: pre_market_swing_report.",
        "intraday_risk_watch": "Prompt name: intraday_risk_watch.",
        "post_market_review": "Prompt name: post_market_review.",
        "position_review": "Prompt name: position_review.",
    }
    assert guard_checks["prompt_schedule_hints_match_contract"]["passed"] is True
    assert guard_checks["prompt_schedule_hints_match_contract"]["actual"] == {
        "pre_market_swing_report": "weekday_pre_market",
        "intraday_risk_watch": "market_hours",
        "post_market_review": "post_market",
        "position_review": "manual_or_scheduled_position_check",
    }
    assert guard_checks["prompt_decision_focus_matches_contract"]["passed"] is True
    assert guard_checks["prompt_decision_focus_matches_contract"]["actual"] == {
        "pre_market_swing_report": "new_swing_entry_and_watchlist",
        "intraday_risk_watch": "risk_monitoring_trim_or_exit_checks",
        "post_market_review": "end_of_day_review_and_next_session_plan",
        "position_review": "hold_trim_exit_or_stop_review",
    }
    assert (
        guard_checks["idempotency_key_templates_match_prompt_identity"]["passed"]
        is True
    )
    assert guard_checks["idempotency_key_templates_match_prompt_identity"][
        "actual"
    ] == {
        name: f"halo_swing:{name}:TQQQ:{{yyyy_mm_dd}}"
        for name in prompts
    }
    assert (
        guard_checks["prompt_text_references_idempotency_key_template"]["passed"]
        is True
    )
    assert guard_checks["prompt_text_references_idempotency_key_template"][
        "actual"
    ] == {
        name: True
        for name in prompts
    }
    assert (
        guard_checks[
            "manual_setup_requirements_declared_before_unattended_run"
        ]["passed"]
        is True
    )
    assert guard_checks[
        "manual_setup_requirements_declared_before_unattended_run"
    ]["actual"] == [
        "hermes_config_path",
        "telegram_bot_token_or_gateway",
        "duplicate_run_lock_policy",
        "runtime_checkpoint_path",
        "watchdog_alert_destination",
    ]
    assert guard_checks["manual_setup_requirements_match_registry"]["passed"] is True
    assert guard_checks["manual_setup_requirements_match_registry"]["actual"] == [
        "hermes_config_path",
        "telegram_bot_token_or_gateway",
        "duplicate_run_lock_policy",
        "runtime_checkpoint_path",
        "watchdog_alert_destination",
    ]
    assert (
        guard_checks["prompt_text_references_manual_setup_requirements"]["passed"]
        is True
    )
    assert guard_checks["prompt_text_references_manual_setup_requirements"][
        "actual"
    ] == {
        name: True
        for name in prompts
    }
    assert guard_checks["prompt_text_references_manual_setup_requirements"][
        "expected"
    ] == (
        "Manual setup required before unattended run: hermes_config_path, "
        "telegram_bot_token_or_gateway, duplicate_run_lock_policy, "
        "runtime_checkpoint_path, watchdog_alert_destination."
    )
    expected_scheduler_setup_block_text = (
        "Do not configure a scheduler or cron runner until manual setup is "
        "complete: hermes_config_path, telegram_bot_token_or_gateway, "
        "duplicate_run_lock_policy, runtime_checkpoint_path, "
        "watchdog_alert_destination."
    )
    assert (
        guard_checks[
            "prompt_text_declares_manual_setup_before_scheduler_setup"
        ]["passed"]
        is True
    )
    assert guard_checks[
        "prompt_text_declares_manual_setup_before_scheduler_setup"
    ]["expected"] == {
        "manual_setup_text": (
            "Manual setup required before unattended run: hermes_config_path, "
            "telegram_bot_token_or_gateway, duplicate_run_lock_policy, "
            "runtime_checkpoint_path, watchdog_alert_destination."
        ),
        "scheduler_setup_block_text": expected_scheduler_setup_block_text,
        "order": "manual_setup_before_scheduler_setup",
    }
    assert all(
        positions["manual_setup_index"] != -1
        and positions["scheduler_setup_block_index"] > positions["manual_setup_index"]
        for positions in guard_checks[
            "prompt_text_declares_manual_setup_before_scheduler_setup"
        ]["actual"].values()
    )
    assert (
        guard_checks["cron_prompt_contract_requires_no_credentials_or_secrets"][
            "passed"
        ]
        is True
    )
    assert guard_checks["cron_prompt_contract_requires_no_credentials_or_secrets"][
        "actual"
    ] == {
        "telegram_credentials_required": False,
        "secret_values_returned": False,
    }
    assert (
        guard_checks["prompt_text_references_no_secret_instruction"]["passed"]
        is True
    )
    assert guard_checks["prompt_text_references_no_secret_instruction"][
        "expected"
    ] == "Do not include credentials or secret values."
    assert guard_checks["prompt_text_references_no_secret_instruction"][
        "actual"
    ] == {
        name: True
        for name in prompts
    }
    assert guard_checks["report_prompt_tool_and_input_schema_match"]["passed"] is True
    assert guard_checks["report_prompt_tool_and_input_schema_match"][
        "actual"
    ] == {
        intent: {
            "tool_name": "generate_latest_signal_report",
            "input_keys": ["asset", "report_intent", "timeframe"],
        }
        for intent in contract["supported_report_intents"]
    }
    assert (
        guard_checks["position_review_prompt_tool_and_input_schema_match"]["passed"]
        is True
    )
    assert guard_checks["position_review_prompt_tool_and_input_schema_match"][
        "actual"
    ] == [
        {
            "tool_name": "generate_position_review_report",
            "input_keys": ["asset"],
        }
    ]
    assert guard_checks["report_prompt_intents_match_input_json"]["passed"] is True
    assert (
        guard_checks["report_prompt_expected_sections_match_contract"]["passed"] is True
    )
    assert guard_checks["prompt_output_schema_matches_tool_contract"]["passed"] is True
    assert guard_checks["prompt_output_schema_matches_tool_contract"][
        "expected"
    ] == {
        "pre_market_swing_report": "hermes_report.v1",
        "intraday_risk_watch": "hermes_report.v1",
        "post_market_review": "hermes_report.v1",
        "position_review": "hermes_position_review.v1",
    }
    assert guard_checks["prompt_output_schema_matches_tool_contract"][
        "actual"
    ] == {
        "pre_market_swing_report": "hermes_report.v1",
        "intraday_risk_watch": "hermes_report.v1",
        "post_market_review": "hermes_report.v1",
        "position_review": "hermes_position_review.v1",
    }
    assert guard_checks["prompt_live_data_required_matches_contract"]["passed"] is True
    assert guard_checks["prompt_live_data_required_matches_contract"][
        "expected"
    ] == {
        name: False
        for name in prompts
    }
    assert guard_checks["prompt_live_data_required_matches_contract"]["actual"] == {
        name: False
        for name in prompts
    }
    assert guard_checks["prompt_text_references_output_schema"]["passed"] is True
    assert guard_checks["prompt_text_references_output_schema"]["expected"] == {
        "pre_market_swing_report": "Expected tool output schema: hermes_report.v1.",
        "intraday_risk_watch": "Expected tool output schema: hermes_report.v1.",
        "post_market_review": "Expected tool output schema: hermes_report.v1.",
        "position_review": (
            "Expected tool output schema: hermes_position_review.v1."
        ),
    }
    assert guard_checks["prompt_text_references_output_schema"]["actual"] == {
        name: True
        for name in prompts
    }
    assert guard_checks["prompt_text_references_no_live_data_boundary"]["passed"] is True
    assert guard_checks["prompt_text_references_no_live_data_boundary"][
        "expected"
    ] == "Do not call live market, macro, news, broker, or exchange data sources."
    assert guard_checks["prompt_text_references_no_live_data_boundary"]["actual"] == {
        name: True
        for name in prompts
    }
    assert (
        guard_checks["prompt_telegram_format_schema_matches_contract"]["passed"]
        is True
    )
    assert guard_checks["prompt_telegram_format_schema_matches_contract"][
        "expected"
    ] == {
        name: "telegram_report_format.v1"
        for name in prompts
    }
    assert guard_checks["prompt_telegram_format_schema_matches_contract"][
        "actual"
    ] == {
        name: "telegram_report_format.v1"
        for name in prompts
    }
    assert (
        guard_checks["prompt_text_references_telegram_format_schema"]["passed"]
        is True
    )
    assert guard_checks["prompt_text_references_telegram_format_schema"][
        "expected"
    ] == {
        name: "Telegram format schema: telegram_report_format.v1."
        for name in prompts
    }
    assert guard_checks["prompt_text_references_telegram_format_schema"][
        "actual"
    ] == {
        name: True
        for name in prompts
    }
    assert guard_checks["prompt_numeric_authority_matches_contract"]["passed"] is True
    assert guard_checks["prompt_numeric_authority_matches_contract"]["expected"] == {
        "pre_market_swing_report": "latest_signal_report",
        "intraday_risk_watch": "latest_signal_report",
        "post_market_review": "latest_signal_report",
        "position_review": "position_review",
    }
    assert guard_checks["prompt_numeric_authority_matches_contract"]["actual"] == {
        "pre_market_swing_report": "latest_signal_report",
        "intraday_risk_watch": "latest_signal_report",
        "post_market_review": "latest_signal_report",
        "position_review": "position_review",
    }
    assert guard_checks["prompt_text_references_numeric_authority"]["passed"] is True
    assert guard_checks["prompt_text_references_numeric_authority"]["expected"] == {
        "pre_market_swing_report": "Numeric authority: latest_signal_report.",
        "intraday_risk_watch": "Numeric authority: latest_signal_report.",
        "post_market_review": "Numeric authority: latest_signal_report.",
        "position_review": "Numeric authority: position_review.",
    }
    assert guard_checks["prompt_text_references_numeric_authority"]["actual"] == {
        name: True
        for name in prompts
    }
    assert (
        guard_checks["prompt_text_references_delivery_preview_chunks"]["passed"]
        is True
    )
    assert guard_checks["prompt_text_references_delivery_preview_chunks"][
        "actual"
    ] == {
        name: True
        for name in prompts
    }
    assert (
        guard_checks["prompt_text_matches_declared_delivery_preview_path"]["passed"]
        is True
    )
    assert guard_checks["prompt_text_matches_declared_delivery_preview_path"][
        "expected"
    ] == {
        name: prompt["delivery_preview_path"]
        for name, prompt in prompts.items()
    }
    assert guard_checks["prompt_text_matches_declared_delivery_preview_path"][
        "actual"
    ] == {
        name: True
        for name in prompts
    }
    assert guard_checks["prompt_text_references_expected_sections"]["passed"] is True
    assert guard_checks["prompt_text_references_expected_sections"]["actual"] == {
        name: True
        for name in prompts
    }
    assert guard_checks["prompt_text_references_expected_sections"]["expected"] == {
        "pre_market_swing_report": (
            "Expected Telegram sections: Target, Decision, Reasons, Entry, "
            "Stop, Take Profit, Cautions."
        ),
        "intraday_risk_watch": (
            "Expected Telegram sections: Target, Decision, Stop, Cautions."
        ),
        "post_market_review": (
            "Expected Telegram sections: Target, Decision, Reasons, "
            "Take Profit, Cautions."
        ),
        "position_review": (
            "Expected Telegram sections: Position, Decision, Rationale, Stop, "
            "Take Profit, Risk."
        ),
    }
    assert guard_checks["prompt_text_references_schedule_hint"]["passed"] is True
    assert guard_checks["prompt_text_references_schedule_hint"]["actual"] == {
        name: True
        for name in prompts
    }
    assert guard_checks["prompt_text_references_schedule_hint"]["expected"] == {
        "pre_market_swing_report": "Schedule hint: weekday_pre_market.",
        "intraday_risk_watch": "Schedule hint: market_hours.",
        "post_market_review": "Schedule hint: post_market.",
        "position_review": (
            "Schedule hint: manual_or_scheduled_position_check."
        ),
    }
    assert guard_checks["prompt_text_references_decision_focus"]["passed"] is True
    assert guard_checks["prompt_text_references_decision_focus"]["expected"] == {
        "pre_market_swing_report": (
            "Decision focus: new_swing_entry_and_watchlist."
        ),
        "intraday_risk_watch": (
            "Decision focus: risk_monitoring_trim_or_exit_checks."
        ),
        "post_market_review": (
            "Decision focus: end_of_day_review_and_next_session_plan."
        ),
        "position_review": "Decision focus: hold_trim_exit_or_stop_review.",
    }
    assert guard_checks["prompt_text_references_decision_focus"]["actual"] == {
        name: True
        for name in prompts
    }
    assert guard_checks["prompt_text_requires_configured_gateway"]["passed"] is True
    assert guard_checks["prompt_text_requires_configured_gateway"]["actual"] == {
        name: True
        for name in prompts
    }
    assert (
        guard_checks["prompt_text_matches_declared_tool_and_inputs"]["passed"]
        is True
    )
    assert guard_checks["prompt_text_matches_declared_tool_and_inputs"][
        "expected"
    ] == {
        "pre_market_swing_report": (
            "Use the market_swing MCP tool generate_latest_signal_report with "
            "asset=TQQQ, timeframe=swing_3d_10d, "
            "report_intent=pre_market_swing_report."
        ),
        "intraday_risk_watch": (
            "Use the market_swing MCP tool generate_latest_signal_report with "
            "asset=TQQQ, timeframe=swing_3d_10d, "
            "report_intent=intraday_risk_watch."
        ),
        "post_market_review": (
            "Use the market_swing MCP tool generate_latest_signal_report with "
            "asset=TQQQ, timeframe=swing_3d_10d, "
            "report_intent=post_market_review."
        ),
        "position_review": (
            "Use the market_swing MCP tool generate_position_review_report "
            "with asset=TQQQ."
        ),
    }
    assert guard_checks["prompt_text_matches_declared_tool_and_inputs"][
        "actual"
    ] == {
        name: True
        for name in prompts
    }
    assert guard_checks["prompt_text_preserves_numeric_authority"]["passed"] is True
    assert guard_checks["prompt_text_preserves_numeric_authority"]["expected"] == {
        "pre_market_swing_report": "Use MCP numeric fields as source of truth.",
        "intraday_risk_watch": "Use MCP numeric fields as source of truth.",
        "post_market_review": "Use MCP numeric fields as source of truth.",
        "position_review": (
            "Use position_review numeric fields as source of truth."
        ),
    }
    assert guard_checks["prompt_text_preserves_numeric_authority"]["actual"] == {
        name: True
        for name in prompts
    }
    assert guard_checks["prompt_text_preserves_order_block"]["passed"] is True
    assert guard_checks["prompt_text_preserves_order_block"]["actual"] == {
        name: True
        for name in prompts
    }
    assert payload["live_data_required"] is False


def test_cron_prompt_pack_trims_and_uppercases_asset_identity() -> None:
    payload = generate_cron_prompt_pack(" tqqq ")
    prompts = {prompt["name"]: prompt for prompt in payload["prompts"]}
    guard_checks = {
        check["name"]: check for check in payload["cron_prompt_guard"]["checks"]
    }

    assert payload["asset"] == "TQQQ"
    assert guard_checks["prompt_assets_match_pack_asset"]["passed"] is True
    assert guard_checks["prompt_assets_match_pack_asset"]["actual"] == {
        name: "TQQQ"
        for name in prompts
    }
    assert all(
        prompt["input_json"]["asset"] == "TQQQ"
        for prompt in payload["prompts"]
    )
    assert all(
        f"halo_swing:{name}:TQQQ:{{yyyy_mm_dd}}"
        == prompt["idempotency_key_template"]
        for name, prompt in prompts.items()
    )
    assert all(" tqqq " not in prompt["prompt"] for prompt in payload["prompts"])
    assert all(
        "asset=TQQQ" in prompt["prompt"] or "with asset=TQQQ." in prompt["prompt"]
        for prompt in payload["prompts"]
    )
    assert payload["cron_prompt_guard"]["status"] == "ok"


def test_cron_prompt_pack_rejects_blank_asset_identity() -> None:
    with pytest.raises(ValueError, match="asset must be a nonempty string"):
        generate_cron_prompt_pack("   ")


def test_cron_prompt_pack_rejects_asset_control_character() -> None:
    with pytest.raises(ValueError, match="asset must not contain control characters"):
        generate_cron_prompt_pack("TQQQ\n")


def test_cron_prompt_pack_trims_timeframe_identity() -> None:
    payload = generate_cron_prompt_pack("TQQQ", timeframe=" swing_3d_10d ")
    prompts = {prompt["name"]: prompt for prompt in payload["prompts"]}
    report_prompts = {
        name: prompt
        for name, prompt in prompts.items()
        if prompt["tool_name"] == "generate_latest_signal_report"
    }
    guard_checks = {
        check["name"]: check for check in payload["cron_prompt_guard"]["checks"]
    }

    assert payload["timeframe"] == "swing_3d_10d"
    assert guard_checks["report_prompt_timeframes_match_pack_timeframe"][
        "passed"
    ] is True
    assert guard_checks["report_prompt_timeframes_match_pack_timeframe"][
        "actual"
    ] == {
        name: "swing_3d_10d"
        for name in report_prompts
    }
    assert all(
        prompt["input_json"]["timeframe"] == "swing_3d_10d"
        for prompt in report_prompts.values()
    )
    assert all(
        "timeframe=swing_3d_10d" in prompt["prompt"]
        for prompt in report_prompts.values()
    )
    assert all(
        " swing_3d_10d " not in prompt["prompt"]
        for prompt in report_prompts.values()
    )
    assert payload["cron_prompt_guard"]["status"] == "ok"


@pytest.mark.parametrize("timeframe", ["   ", None, 123])
def test_cron_prompt_pack_rejects_invalid_timeframe_identity(timeframe) -> None:
    with pytest.raises(ValueError, match="timeframe must be a nonempty string"):
        generate_cron_prompt_pack("TQQQ", timeframe=timeframe)


def test_cron_prompt_pack_rejects_timeframe_control_character() -> None:
    with pytest.raises(
        ValueError,
        match="timeframe must not contain control characters",
    ):
        generate_cron_prompt_pack("TQQQ", timeframe="swing_3d_10d\n")


@pytest.mark.parametrize(
    "include_position_review",
    ["false", "true", 1, 0, None],
)
def test_cron_prompt_pack_rejects_non_bool_include_position_review(
    include_position_review,
) -> None:
    with pytest.raises(
        ValueError,
        match="include_position_review must be a boolean",
    ):
        generate_cron_prompt_pack(
            "TQQQ",
            include_position_review=include_position_review,
        )


def test_cron_prompt_pack_can_exclude_position_review_without_side_effects() -> None:
    payload = generate_cron_prompt_pack("TQQQ", include_position_review=False)
    prompts = {prompt["name"]: prompt for prompt in payload["prompts"]}
    guard_checks = {
        check["name"]: check for check in payload["cron_prompt_guard"]["checks"]
    }

    assert "position_review" not in prompts
    assert (
        guard_checks["cron_prompt_pack_schema_version_matches_expected"]["passed"]
        is True
    )
    assert guard_checks["cron_prompt_pack_schema_version_matches_expected"][
        "actual"
    ] == "hermes_cron_prompt_pack.v1"
    assert (
        guard_checks["cron_prompt_pack_keys_match_expected_schema"]["passed"]
        is True
    )
    assert guard_checks["cron_prompt_pack_keys_match_expected_schema"][
        "actual"
    ] == [
        "schema_version",
        "asset",
        "timeframe",
        "prompts",
        "cron_prompt_contract",
        "cron_prompt_guard",
        "live_data_required",
    ]
    assert guard_checks["pack_live_data_required_matches_contract"]["passed"] is True
    assert guard_checks["pack_live_data_required_matches_contract"]["actual"] is False
    assert payload["asset"] == "TQQQ"
    assert payload["timeframe"] == "swing_3d_10d"
    assert guard_checks["cron_prompt_contract_name_matches_schema"]["passed"] is True
    assert (
        guard_checks["cron_prompt_contract_keys_match_expected_schema"]["passed"]
        is True
    )
    assert guard_checks["cron_prompt_contract_keys_match_expected_schema"][
        "actual"
    ] == [
        "name",
        "supported_report_intents",
        "include_position_review",
        "scheduler_added",
        "cron_runner_added",
        "network_call",
        "telegram_send",
        "telegram_credentials_required",
        "order_submission",
        "secret_values_returned",
        "live_data_required",
        "manual_setup_required_before_unattended_run",
    ]
    assert (
        guard_checks["cron_prompt_prompt_keys_match_expected_schema"]["passed"]
        is True
    )
    assert guard_checks["cron_prompt_prompt_keys_match_expected_schema"][
        "actual"
    ] == {
        name: [
            "name",
            "schedule_hint",
            "decision_focus",
            "tool_name",
            "input_json",
            "expected_output_schema",
            "live_data_required",
            "idempotency_key_template",
            "expected_sections",
            "telegram_format_schema",
            "numeric_authority",
            "prompt",
            "delivery_preview_path",
        ]
        for name in prompts
    }
    assert (
        guard_checks["cron_prompt_guard_keys_match_expected_schema"]["passed"]
        is True
    )
    assert guard_checks["cron_prompt_guard_keys_match_expected_schema"][
        "actual"
    ] == [
        "status",
        "checks",
    ]
    assert (
        guard_checks["cron_prompt_guard_check_names_match_expected_schema"]["passed"]
        is True
    )
    assert guard_checks["cron_prompt_guard_check_names_match_expected_schema"][
        "actual"
    ] == guard_checks["cron_prompt_guard_check_names_match_expected_schema"][
        "expected"
    ]
    assert guard_checks["cron_prompt_guard_check_names_match_expected_schema"][
        "actual"
    ][-3:] == [
        "cron_prompt_guard_keys_match_expected_schema",
        "cron_prompt_guard_check_names_match_expected_schema",
        "cron_prompt_guard_check_keys_match_expected_schema",
    ]
    assert (
        guard_checks["cron_prompt_guard_check_keys_match_expected_schema"]["passed"]
        is True
    )
    assert all(
        check_keys == [
            "name",
            "passed",
            "expected",
            "actual",
        ]
        for check_keys in guard_checks[
            "cron_prompt_guard_check_keys_match_expected_schema"
        ]["actual"].values()
    )
    assert guard_checks["prompt_assets_match_pack_asset"]["passed"] is True
    assert guard_checks["prompt_assets_match_pack_asset"]["actual"] == {
        name: "TQQQ"
        for name in prompts
    }
    assert guard_checks["report_prompt_timeframes_match_pack_timeframe"][
        "passed"
    ] is True
    assert guard_checks["report_prompt_timeframes_match_pack_timeframe"][
        "actual"
    ] == {
        "pre_market_swing_report": "swing_3d_10d",
        "intraday_risk_watch": "swing_3d_10d",
        "post_market_review": "swing_3d_10d",
    }
    assert (
        guard_checks["include_position_review_contract_matches_request"]["passed"]
        is True
    )
    assert guard_checks["include_position_review_contract_matches_request"][
        "actual"
    ] is False
    assert set(payload["cron_prompt_contract"]["supported_report_intents"]) == set(prompts)
    assert guard_checks["supported_report_intents_match_registry"]["passed"] is True
    assert guard_checks["supported_report_intents_match_registry"]["actual"] == [
        "pre_market_swing_report",
        "intraday_risk_watch",
        "post_market_review",
    ]
    assert (
        guard_checks["position_review_prompt_expected_sections_match_contract"][
            "passed"
        ]
        is True
    )
    assert guard_checks["position_review_prompt_expected_sections_match_contract"][
        "actual"
    ] == {}
    assert guard_checks["position_review_prompt_expected_sections_match_contract"][
        "expected"
    ] == {}
    assert payload["cron_prompt_contract"]["include_position_review"] is False
    assert payload["cron_prompt_contract"]["live_data_required"] is False
    assert all(prompt["live_data_required"] is False for prompt in payload["prompts"])
    assert payload["cron_prompt_guard"]["status"] == "ok"
    assert all(check["passed"] for check in payload["cron_prompt_guard"]["checks"])
    assert guard_checks["prompt_names_match_contract_and_position_option"][
        "passed"
    ] is True
    assert guard_checks["prompt_names_match_contract_and_position_option"][
        "actual"
    ] == [
        "intraday_risk_watch",
        "post_market_review",
        "pre_market_swing_report",
    ]
    assert guard_checks["prompt_names_match_contract_order_and_are_unique"][
        "passed"
    ] is True
    assert guard_checks["prompt_names_match_contract_order_and_are_unique"][
        "expected"
    ] == [
        "pre_market_swing_report",
        "intraday_risk_watch",
        "post_market_review",
    ]
    assert guard_checks["prompt_names_match_contract_order_and_are_unique"][
        "actual"
    ] == [
        "pre_market_swing_report",
        "intraday_risk_watch",
        "post_market_review",
    ]
    assert guard_checks["prompt_text_references_prompt_name"]["passed"] is True
    assert guard_checks["prompt_text_references_prompt_name"]["actual"] == {
        name: True
        for name in prompts
    }
    assert guard_checks["prompt_text_references_prompt_name"]["expected"] == {
        "pre_market_swing_report": "Prompt name: pre_market_swing_report.",
        "intraday_risk_watch": "Prompt name: intraday_risk_watch.",
        "post_market_review": "Prompt name: post_market_review.",
    }
    assert guard_checks["prompt_schedule_hints_match_contract"]["passed"] is True
    assert guard_checks["prompt_schedule_hints_match_contract"]["actual"] == {
        "pre_market_swing_report": "weekday_pre_market",
        "intraday_risk_watch": "market_hours",
        "post_market_review": "post_market",
    }
    assert guard_checks["prompt_decision_focus_matches_contract"]["passed"] is True
    assert guard_checks["prompt_decision_focus_matches_contract"]["actual"] == {
        "pre_market_swing_report": "new_swing_entry_and_watchlist",
        "intraday_risk_watch": "risk_monitoring_trim_or_exit_checks",
        "post_market_review": "end_of_day_review_and_next_session_plan",
    }
    assert (
        guard_checks["idempotency_key_templates_match_prompt_identity"]["passed"]
        is True
    )
    assert guard_checks["idempotency_key_templates_match_prompt_identity"][
        "actual"
    ] == {
        name: f"halo_swing:{name}:TQQQ:{{yyyy_mm_dd}}"
        for name in prompts
    }
    assert (
        guard_checks["prompt_text_references_idempotency_key_template"]["passed"]
        is True
    )
    assert guard_checks["prompt_text_references_idempotency_key_template"][
        "actual"
    ] == {
        name: True
        for name in prompts
    }
    assert (
        guard_checks[
            "manual_setup_requirements_declared_before_unattended_run"
        ]["passed"]
        is True
    )
    assert guard_checks["manual_setup_requirements_match_registry"]["passed"] is True
    assert guard_checks["manual_setup_requirements_match_registry"]["actual"] == [
        "hermes_config_path",
        "telegram_bot_token_or_gateway",
        "duplicate_run_lock_policy",
        "runtime_checkpoint_path",
        "watchdog_alert_destination",
    ]
    assert (
        guard_checks["prompt_text_references_manual_setup_requirements"]["passed"]
        is True
    )
    assert guard_checks["prompt_text_references_manual_setup_requirements"][
        "actual"
    ] == {
        name: True
        for name in prompts
    }
    assert guard_checks["prompt_text_references_manual_setup_requirements"][
        "expected"
    ] == (
        "Manual setup required before unattended run: hermes_config_path, "
        "telegram_bot_token_or_gateway, duplicate_run_lock_policy, "
        "runtime_checkpoint_path, watchdog_alert_destination."
    )
    expected_scheduler_setup_block_text = (
        "Do not configure a scheduler or cron runner until manual setup is "
        "complete: hermes_config_path, telegram_bot_token_or_gateway, "
        "duplicate_run_lock_policy, runtime_checkpoint_path, "
        "watchdog_alert_destination."
    )
    assert (
        guard_checks[
            "prompt_text_declares_manual_setup_before_scheduler_setup"
        ]["passed"]
        is True
    )
    assert guard_checks[
        "prompt_text_declares_manual_setup_before_scheduler_setup"
    ]["expected"] == {
        "manual_setup_text": (
            "Manual setup required before unattended run: hermes_config_path, "
            "telegram_bot_token_or_gateway, duplicate_run_lock_policy, "
            "runtime_checkpoint_path, watchdog_alert_destination."
        ),
        "scheduler_setup_block_text": expected_scheduler_setup_block_text,
        "order": "manual_setup_before_scheduler_setup",
    }
    assert all(
        positions["manual_setup_index"] != -1
        and positions["scheduler_setup_block_index"] > positions["manual_setup_index"]
        for positions in guard_checks[
            "prompt_text_declares_manual_setup_before_scheduler_setup"
        ]["actual"].values()
    )
    assert (
        guard_checks["cron_prompt_contract_requires_no_credentials_or_secrets"][
            "passed"
        ]
        is True
    )
    assert guard_checks["cron_prompt_contract_requires_no_credentials_or_secrets"][
        "actual"
    ] == {
        "telegram_credentials_required": False,
        "secret_values_returned": False,
    }
    assert (
        guard_checks["prompt_text_references_no_secret_instruction"]["passed"]
        is True
    )
    assert guard_checks["prompt_text_references_no_secret_instruction"][
        "expected"
    ] == "Do not include credentials or secret values."
    assert guard_checks["prompt_text_references_no_secret_instruction"][
        "actual"
    ] == {
        name: True
        for name in prompts
    }
    assert guard_checks["report_prompt_tool_and_input_schema_match"]["passed"] is True
    assert (
        guard_checks["position_review_prompt_tool_and_input_schema_match"]["passed"]
        is True
    )
    assert guard_checks["position_review_prompt_tool_and_input_schema_match"][
        "actual"
    ] == []
    assert guard_checks["prompt_output_schema_matches_tool_contract"]["passed"] is True
    assert guard_checks["prompt_output_schema_matches_tool_contract"][
        "expected"
    ] == {
        "pre_market_swing_report": "hermes_report.v1",
        "intraday_risk_watch": "hermes_report.v1",
        "post_market_review": "hermes_report.v1",
    }
    assert guard_checks["prompt_output_schema_matches_tool_contract"][
        "actual"
    ] == {
        "pre_market_swing_report": "hermes_report.v1",
        "intraday_risk_watch": "hermes_report.v1",
        "post_market_review": "hermes_report.v1",
    }
    assert guard_checks["prompt_live_data_required_matches_contract"]["passed"] is True
    assert guard_checks["prompt_live_data_required_matches_contract"][
        "expected"
    ] == {
        name: False
        for name in prompts
    }
    assert guard_checks["prompt_live_data_required_matches_contract"]["actual"] == {
        name: False
        for name in prompts
    }
    assert guard_checks["prompt_text_references_output_schema"]["passed"] is True
    assert guard_checks["prompt_text_references_output_schema"]["expected"] == {
        "pre_market_swing_report": "Expected tool output schema: hermes_report.v1.",
        "intraday_risk_watch": "Expected tool output schema: hermes_report.v1.",
        "post_market_review": "Expected tool output schema: hermes_report.v1.",
    }
    assert guard_checks["prompt_text_references_output_schema"]["actual"] == {
        name: True
        for name in prompts
    }
    assert guard_checks["prompt_text_references_no_live_data_boundary"]["passed"] is True
    assert guard_checks["prompt_text_references_no_live_data_boundary"][
        "expected"
    ] == "Do not call live market, macro, news, broker, or exchange data sources."
    assert guard_checks["prompt_text_references_no_live_data_boundary"]["actual"] == {
        name: True
        for name in prompts
    }
    assert (
        guard_checks["prompt_telegram_format_schema_matches_contract"]["passed"]
        is True
    )
    assert guard_checks["prompt_telegram_format_schema_matches_contract"][
        "expected"
    ] == {
        name: "telegram_report_format.v1"
        for name in prompts
    }
    assert guard_checks["prompt_telegram_format_schema_matches_contract"][
        "actual"
    ] == {
        name: "telegram_report_format.v1"
        for name in prompts
    }
    assert (
        guard_checks["prompt_text_references_telegram_format_schema"]["passed"]
        is True
    )
    assert guard_checks["prompt_text_references_telegram_format_schema"][
        "expected"
    ] == {
        name: "Telegram format schema: telegram_report_format.v1."
        for name in prompts
    }
    assert guard_checks["prompt_text_references_telegram_format_schema"][
        "actual"
    ] == {
        name: True
        for name in prompts
    }
    assert guard_checks["prompt_numeric_authority_matches_contract"]["passed"] is True
    assert guard_checks["prompt_numeric_authority_matches_contract"]["expected"] == {
        "pre_market_swing_report": "latest_signal_report",
        "intraday_risk_watch": "latest_signal_report",
        "post_market_review": "latest_signal_report",
    }
    assert guard_checks["prompt_numeric_authority_matches_contract"]["actual"] == {
        "pre_market_swing_report": "latest_signal_report",
        "intraday_risk_watch": "latest_signal_report",
        "post_market_review": "latest_signal_report",
    }
    assert guard_checks["prompt_text_references_numeric_authority"]["passed"] is True
    assert guard_checks["prompt_text_references_numeric_authority"]["expected"] == {
        "pre_market_swing_report": "Numeric authority: latest_signal_report.",
        "intraday_risk_watch": "Numeric authority: latest_signal_report.",
        "post_market_review": "Numeric authority: latest_signal_report.",
    }
    assert guard_checks["prompt_text_references_numeric_authority"]["actual"] == {
        name: True
        for name in prompts
    }
    assert (
        guard_checks["prompt_text_references_delivery_preview_chunks"]["passed"]
        is True
    )
    assert guard_checks["prompt_text_references_delivery_preview_chunks"][
        "actual"
    ] == {
        name: True
        for name in prompts
    }
    assert (
        guard_checks["prompt_text_matches_declared_delivery_preview_path"]["passed"]
        is True
    )
    assert guard_checks["prompt_text_matches_declared_delivery_preview_path"][
        "expected"
    ] == {
        name: prompt["delivery_preview_path"]
        for name, prompt in prompts.items()
    }
    assert guard_checks["prompt_text_matches_declared_delivery_preview_path"][
        "actual"
    ] == {
        name: True
        for name in prompts
    }
    assert guard_checks["prompt_text_references_expected_sections"]["passed"] is True
    assert guard_checks["prompt_text_references_expected_sections"]["actual"] == {
        name: True
        for name in prompts
    }
    assert guard_checks["prompt_text_references_expected_sections"]["expected"] == {
        "pre_market_swing_report": (
            "Expected Telegram sections: Target, Decision, Reasons, Entry, "
            "Stop, Take Profit, Cautions."
        ),
        "intraday_risk_watch": (
            "Expected Telegram sections: Target, Decision, Stop, Cautions."
        ),
        "post_market_review": (
            "Expected Telegram sections: Target, Decision, Reasons, "
            "Take Profit, Cautions."
        ),
    }
    assert guard_checks["prompt_text_references_schedule_hint"]["passed"] is True
    assert guard_checks["prompt_text_references_schedule_hint"]["actual"] == {
        name: True
        for name in prompts
    }
    assert guard_checks["prompt_text_references_schedule_hint"]["expected"] == {
        "pre_market_swing_report": "Schedule hint: weekday_pre_market.",
        "intraday_risk_watch": "Schedule hint: market_hours.",
        "post_market_review": "Schedule hint: post_market.",
    }
    assert guard_checks["prompt_text_references_decision_focus"]["passed"] is True
    assert guard_checks["prompt_text_references_decision_focus"]["expected"] == {
        "pre_market_swing_report": (
            "Decision focus: new_swing_entry_and_watchlist."
        ),
        "intraday_risk_watch": (
            "Decision focus: risk_monitoring_trim_or_exit_checks."
        ),
        "post_market_review": (
            "Decision focus: end_of_day_review_and_next_session_plan."
        ),
    }
    assert guard_checks["prompt_text_references_decision_focus"]["actual"] == {
        name: True
        for name in prompts
    }
    assert guard_checks["prompt_text_requires_configured_gateway"]["passed"] is True
    assert guard_checks["prompt_text_requires_configured_gateway"]["actual"] == {
        name: True
        for name in prompts
    }
    assert (
        guard_checks["prompt_text_matches_declared_tool_and_inputs"]["passed"]
        is True
    )
    assert guard_checks["prompt_text_matches_declared_tool_and_inputs"][
        "expected"
    ] == {
        "pre_market_swing_report": (
            "Use the market_swing MCP tool generate_latest_signal_report with "
            "asset=TQQQ, timeframe=swing_3d_10d, "
            "report_intent=pre_market_swing_report."
        ),
        "intraday_risk_watch": (
            "Use the market_swing MCP tool generate_latest_signal_report with "
            "asset=TQQQ, timeframe=swing_3d_10d, "
            "report_intent=intraday_risk_watch."
        ),
        "post_market_review": (
            "Use the market_swing MCP tool generate_latest_signal_report with "
            "asset=TQQQ, timeframe=swing_3d_10d, "
            "report_intent=post_market_review."
        ),
    }
    assert guard_checks["prompt_text_matches_declared_tool_and_inputs"][
        "actual"
    ] == {
        name: True
        for name in prompts
    }
    assert guard_checks["prompt_text_preserves_numeric_authority"]["passed"] is True
    assert guard_checks["prompt_text_preserves_numeric_authority"]["expected"] == {
        "pre_market_swing_report": "Use MCP numeric fields as source of truth.",
        "intraday_risk_watch": "Use MCP numeric fields as source of truth.",
        "post_market_review": "Use MCP numeric fields as source of truth.",
    }
    assert guard_checks["prompt_text_preserves_numeric_authority"]["actual"] == {
        name: True
        for name in prompts
    }
    assert guard_checks["prompt_text_preserves_order_block"]["passed"] is True
    assert guard_checks["prompt_text_preserves_order_block"]["actual"] == {
        name: True
        for name in prompts
    }
    assert guard_checks["position_review_prompt_absent_when_excluded"]["passed"] is True
    assert payload["cron_prompt_contract"]["scheduler_added"] is False
    assert payload["cron_prompt_contract"]["telegram_send"] is False
    assert payload["live_data_required"] is False


def test_latest_signal_report_can_include_chart_ref_and_guard(tmp_path: Path) -> None:
    payload = generate_latest_signal_report(
        "TQQQ",
        include_chart=True,
        chart_output_dir=str(tmp_path),
    )
    report = payload["latest_signal_report"]
    chart_ref = report["chart_ref"]
    chart_path = tmp_path / "QQQ_1d.png"
    context = payload["multimodal_context"]
    context_guard_checks = {
        check["name"]: check for check in context["guard"]["checks"]
    }

    assert chart_path.exists()
    assert chart_path.read_bytes().startswith(b"\x89PNG\r\n\x1a\n")
    assert chart_ref["ref_type"] == "CHART"
    assert chart_ref["ref"] == str(chart_path)
    assert chart_ref["metadata"]["renderer"] == "stdlib_png"
    assert payload["chart_code_guard"]["status"] == "ok"
    assert all(check["passed"] for check in payload["chart_code_guard"]["checks"])
    payload_guard_checks = {
        check["name"]: check for check in payload["report_payload_guard"]["checks"]
    }
    assert payload_guard_checks["report_payload_keys_match_expected_schema"][
        "passed"
    ] is True
    assert payload_guard_checks["report_payload_keys_match_expected_schema"][
        "actual"
    ][-3:] == [
        "chart_code_guard",
        "multimodal_context",
        "report_payload_guard",
    ]
    assert (
        payload_guard_checks[
            "report_payload_optional_context_statuses_are_ok"
        ]["passed"]
        is True
    )
    assert payload_guard_checks[
        "report_payload_optional_context_statuses_are_ok"
    ]["actual"] == {
        "chart_code_guard": "ok",
        "multimodal_context": "ok",
    }
    assert payload_guard_checks[
        "report_payload_optional_context_statuses_are_ok"
    ]["expected"] == {
        "chart_code_guard": "ok",
        "multimodal_context": "ok",
    }
    assert (
        payload_guard_checks[
            "report_payload_optional_context_guards_are_ok"
        ]["passed"]
        is True
    )
    assert payload_guard_checks[
        "report_payload_optional_context_guards_are_ok"
    ]["actual"] == {
        "chart_code_guard": "ok",
        "multimodal_context.guard": "ok",
    }
    assert payload_guard_checks[
        "report_payload_optional_context_guards_are_ok"
    ]["expected"] == {
        "chart_code_guard": "ok",
        "multimodal_context.guard": "ok",
    }
    assert (
        context_guard_checks[
            "multimodal_context_guard_check_names_match_expected_schema"
        ]["passed"]
        is True
    )
    assert (
        context_guard_checks[
            "multimodal_context_guard_check_keys_match_expected_schema"
        ]["passed"]
        is True
    )
    assert (
        context_guard_checks["multimodal_context_guard_keys_match_expected_schema"][
            "passed"
        ]
        is True
    )
    assert (
        context_guard_checks["multimodal_context_keys_match_expected_schema"]["passed"]
        is True
    )
    assert context_guard_checks["multimodal_context_keys_match_expected_schema"][
        "actual"
    ] == [
        "status",
        "schema_version",
        "numeric_authority",
        "hermes_multimodal_call",
        "network_call",
        "raw_artifacts_embedded",
        "modality_counts",
        "artifact_refs",
        "evidence_cards",
        "guard",
    ]
    assert (
        context_guard_checks[
            "multimodal_context_artifact_refs_match_expected_schema"
        ]["passed"]
        is True
    )
    assert context_guard_checks[
        "multimodal_context_artifact_refs_match_expected_schema"
    ]["actual"] == {
        "artifact_ref_entry_keys": [["evidence_id", "artifact_ref"]],
        "artifact_ref_keys": [["ref_type", "ref", "metadata"]],
    }
    assert context_guard_checks["chart_ref_slot_uses_chart_artifact_ref_type"][
        "actual"
    ] == {
        "chart_ref_present": True,
        "ref_type": "CHART",
        "slot_uses_chart_artifact_ref_type": True,
    }
    assert context_guard_checks["chart_artifact_refs_use_reserved_evidence_id"][
        "actual"
    ] == [
        expected_chart_artifact_ref_reserved_evidence_id(),
    ]
    assert context_guard_checks[
        "multimodal_context_evidence_ids_are_string_typed"
    ]["actual"] == expected_multimodal_evidence_id_types(
        [],
        ["latest_signal_chart"],
    )
    assert context_guard_checks[
        "multimodal_context_artifact_ref_string_field_types_are_strict"
    ]["actual"] == [
        expected_artifact_ref_string_field_types(),
    ]
    assert context_guard_checks[
        "multimodal_context_artifact_ref_types_match_expected_contract"
    ]["expected"] == EXPECTED_MULTIMODAL_ARTIFACT_REF_TYPES
    assert context_guard_checks[
        "multimodal_context_artifact_ref_types_match_expected_contract"
    ]["actual"] == ["CHART"]
    assert context_guard_checks[
        "multimodal_context_artifact_ref_types_are_canonical_uppercase"
    ]["actual"] == [
        expected_artifact_ref_type_canonical("latest_signal_chart", "CHART"),
    ]
    assert context_guard_checks[
        "multimodal_context_chart_artifact_refs_match_png_contract"
    ]["actual"] == [
        expected_chart_png_artifact_ref_contract(),
    ]
    assert context_guard_checks[
        "multimodal_context_chart_artifact_refs_use_offline_locations"
    ]["actual"] == [
        expected_chart_offline_artifact_ref_location(),
    ]
    assert context_guard_checks[
        "multimodal_context_artifact_ref_values_are_trimmed_and_control_free"
    ]["actual"] == [
        expected_artifact_ref_string_safety(),
    ]
    assert context_guard_checks[
        "multimodal_context_artifact_ref_metadata_entries_match_expected_schema"
    ]["actual"] == [
        {
            "evidence_id": "latest_signal_chart",
            "ref_type": "CHART",
            "metadata_is_dict": True,
            "metadata_keys": ["bars", "renderer", "timeframe_supported"],
        },
    ]
    assert (
        context_guard_checks[
            "multimodal_context_artifact_ref_metadata_matches_expected_schema"
        ]["passed"]
        is True
    )
    assert context_guard_checks[
        "multimodal_context_artifact_ref_metadata_matches_expected_schema"
    ]["actual"] == {
        "metadata_is_dict": [True],
        "metadata_keys_by_ref_type": {
            "CHART": ["bars", "renderer", "timeframe_supported"],
        },
    }
    assert context_guard_checks[
        "multimodal_context_artifact_ref_metadata_values_are_safe"
    ]["actual"] == [
        {
            "evidence_id": "latest_signal_chart",
            "ref_type": "CHART",
            "renderer": "stdlib_png",
            "bars_positive": True,
            "timeframe_supported": True,
        },
    ]
    assert context_guard_checks[
        "multimodal_context_artifact_ref_metadata_value_types_are_strict"
    ]["actual"] == [
        expected_chart_artifact_ref_metadata_value_types(),
    ]
    assert context_guard_checks[
        "multimodal_context_artifact_ref_metadata_text_values_are_trimmed_and_control_free"
    ]["actual"] == [
        expected_chart_artifact_ref_metadata_text_safety(),
    ]
    assert (
        context_guard_checks[
            "multimodal_context_modality_counts_match_expected_context"
        ]["passed"]
        is True
    )
    assert context_guard_checks[
        "multimodal_context_modality_counts_match_expected_context"
    ]["actual"] == {
        "chart_image": 1,
    }
    assert (
        context_guard_checks[
            "multimodal_context_identity_values_match_expected_contract"
        ]["passed"]
        is True
    )
    assert context_guard_checks[
        "multimodal_context_identity_values_match_expected_contract"
    ]["actual"] == EXPECTED_MULTIMODAL_CONTEXT_IDENTITY_VALUES
    assert (
        context_guard_checks[
            "multimodal_context_evidence_cards_match_expected_schema"
        ]["passed"]
        is True
    )
    assert context_guard_checks[
        "multimodal_context_evidence_cards_match_expected_schema"
    ]["actual"] == []
    assert (
        context_guard_checks[
            "multimodal_context_evidence_card_values_are_safe"
        ]["passed"]
        is True
    )
    assert context_guard_checks[
        "multimodal_context_evidence_card_values_are_safe"
    ]["actual"] == []
    assert (
        context_guard_checks[
            "multimodal_context_artifact_refs_match_expected_context"
        ]["passed"]
        is True
    )
    assert context_guard_checks[
        "multimodal_context_artifact_refs_match_expected_context"
    ]["actual"] == [
        {
            "evidence_id": "latest_signal_chart",
            "artifact_ref": chart_ref,
        }
    ]


def test_latest_signal_report_rejects_non_png_chart_artifact_ref(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_render_chart(
        symbol: str = "QQQ",
        timeframe: str = "1d",
        output_dir: str | None = None,
    ) -> dict[str, object]:
        del output_dir
        return {
            "as_of": "2026-05-08T20:00:00Z",
            "symbol": symbol.upper(),
            "timeframe": timeframe,
            "format": "svg",
            "path": "artifact://charts/QQQ_1d.svg",
            "chart_artifact_contract": {
                "schema_version": "chart_artifact.v1",
                "format": "png",
                "renderer": "stdlib_png",
                "artifact_ref_type": "CHART",
                "network_call": False,
                "live_data_required": False,
                "committed_artifact_required": False,
            },
            "chart_artifact_guard": {"status": "ok", "checks": []},
            "artifact_ref": {
                "ref_type": "CHART",
                "ref": "artifact://charts/QQQ_1d.svg",
                "metadata": {
                    "bars": 60,
                    "renderer": "stdlib_png",
                    "timeframe_supported": True,
                },
            },
            "live_data_required": False,
        }

    monkeypatch.setattr(reporting, "render_chart", fake_render_chart)
    payload = generate_latest_signal_report("TQQQ", include_chart=True)
    context = payload["multimodal_context"]
    context_guard_checks = {
        check["name"]: check for check in context["guard"]["checks"]
    }
    payload_guard_checks = {
        check["name"]: check for check in payload["report_payload_guard"]["checks"]
    }

    assert payload["chart_code_guard"]["status"] == "ok"
    assert context["status"] == "conflict"
    assert context_guard_checks[
        "multimodal_context_artifact_ref_types_match_expected_contract"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_artifact_ref_metadata_values_are_safe"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_chart_artifact_refs_match_png_contract"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_chart_artifact_refs_match_png_contract"
    ]["actual"] == [
        {
            "evidence_id": "latest_signal_chart",
            "ref_type": "CHART",
            "allowed_ref_suffixes": [".png"],
            "content_addressed_prefix": "sha256:",
            "ref_matches_chart_contract": False,
        },
    ]
    assert payload_guard_checks[
        "report_payload_optional_context_statuses_are_ok"
    ]["actual"] == {
        "chart_code_guard": "ok",
        "multimodal_context": "conflict",
    }


def test_latest_signal_report_rejects_empty_chart_artifact_ref_value(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_render_chart(
        symbol: str = "QQQ",
        timeframe: str = "1d",
        output_dir: str | None = None,
    ) -> dict[str, object]:
        del output_dir
        return {
            "as_of": "2026-05-08T20:00:00Z",
            "symbol": symbol.upper(),
            "timeframe": timeframe,
            "format": "png",
            "path": "",
            "chart_artifact_contract": {
                "schema_version": "chart_artifact.v1",
                "format": "png",
                "renderer": "stdlib_png",
                "artifact_ref_type": "CHART",
                "network_call": False,
                "live_data_required": False,
                "committed_artifact_required": False,
            },
            "chart_artifact_guard": {"status": "ok", "checks": []},
            "artifact_ref": {
                "ref_type": "CHART",
                "ref": "",
                "metadata": {
                    "bars": 60,
                    "renderer": "stdlib_png",
                    "timeframe_supported": True,
                },
            },
            "live_data_required": False,
        }

    monkeypatch.setattr(reporting, "render_chart", fake_render_chart)
    payload = generate_latest_signal_report("TQQQ", include_chart=True)
    context = payload["multimodal_context"]
    context_guard_checks = {
        check["name"]: check for check in context["guard"]["checks"]
    }
    payload_guard_checks = {
        check["name"]: check for check in payload["report_payload_guard"]["checks"]
    }

    assert payload["chart_code_guard"]["status"] == "ok"
    assert context["status"] == "conflict"
    assert context_guard_checks[
        "chart_ref_slot_uses_chart_artifact_ref_type"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_artifact_ref_types_match_expected_contract"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_artifact_ref_metadata_values_are_safe"
    ]["passed"] is True
    assert context_guard_checks["chart_refs_are_declared"]["passed"] is False
    assert context_guard_checks["chart_refs_are_declared"]["expected"] == (
        "declared_chart_ref"
    )
    assert context_guard_checks["chart_refs_are_declared"]["actual"] == [""]
    assert context_guard_checks[
        "multimodal_context_chart_artifact_refs_match_png_contract"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_chart_artifact_refs_use_offline_locations"
    ]["passed"] is False
    assert payload_guard_checks[
        "report_payload_optional_context_statuses_are_ok"
    ]["actual"] == {
        "chart_code_guard": "ok",
        "multimodal_context": "conflict",
    }


def test_latest_signal_report_rejects_chart_metadata_loose_bool_numeric_types(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_render_chart(
        symbol: str = "QQQ",
        timeframe: str = "1d",
        output_dir: str | None = None,
    ) -> dict[str, object]:
        del output_dir
        return {
            "as_of": "2026-05-08T20:00:00Z",
            "symbol": symbol.upper(),
            "timeframe": timeframe,
            "format": "png",
            "path": "artifact://charts/QQQ_1d.png",
            "chart_artifact_contract": {
                "schema_version": "chart_artifact.v1",
                "format": "png",
                "renderer": "stdlib_png",
                "artifact_ref_type": "CHART",
                "network_call": False,
                "live_data_required": False,
                "committed_artifact_required": False,
            },
            "chart_artifact_guard": {"status": "ok", "checks": []},
            "artifact_ref": {
                "ref_type": "CHART",
                "ref": "artifact://charts/QQQ_1d.png",
                "metadata": {
                    "bars": True,
                    "renderer": "stdlib_png",
                    "timeframe_supported": 1,
                },
            },
            "live_data_required": False,
        }

    monkeypatch.setattr(reporting, "render_chart", fake_render_chart)
    payload = generate_latest_signal_report("TQQQ", include_chart=True)
    context = payload["multimodal_context"]
    context_guard_checks = {
        check["name"]: check for check in context["guard"]["checks"]
    }
    payload_guard_checks = {
        check["name"]: check for check in payload["report_payload_guard"]["checks"]
    }

    assert payload["chart_code_guard"]["status"] == "ok"
    assert context["status"] == "conflict"
    assert context_guard_checks[
        "multimodal_context_chart_artifact_refs_match_png_contract"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_artifact_ref_metadata_values_are_safe"
    ]["passed"] is True
    metadata_values_actual = context_guard_checks[
        "multimodal_context_artifact_ref_metadata_values_are_safe"
    ]["actual"][0]
    assert metadata_values_actual["bars_positive"] is True
    assert metadata_values_actual["timeframe_supported"] is not True
    assert context_guard_checks[
        "multimodal_context_artifact_ref_metadata_value_types_are_strict"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_artifact_ref_metadata_value_types_are_strict"
    ]["actual"] == [
        {
            "evidence_id": "latest_signal_chart",
            "ref_type": "CHART",
            "renderer_is_string": True,
            "bars_is_positive_int": False,
            "timeframe_supported_is_bool_true": False,
        },
    ]
    assert payload_guard_checks[
        "report_payload_optional_context_statuses_are_ok"
    ]["actual"] == {
        "chart_code_guard": "ok",
        "multimodal_context": "conflict",
    }


def test_latest_signal_report_rejects_missing_chart_metadata_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_render_chart(
        symbol: str = "QQQ",
        timeframe: str = "1d",
        output_dir: str | None = None,
    ) -> dict[str, object]:
        del output_dir
        return {
            "as_of": "2026-05-08T20:00:00Z",
            "symbol": symbol.upper(),
            "timeframe": timeframe,
            "format": "png",
            "path": "artifact://charts/QQQ_1d.png",
            "chart_artifact_contract": {
                "schema_version": "chart_artifact.v1",
                "format": "png",
                "renderer": "stdlib_png",
                "artifact_ref_type": "CHART",
                "network_call": False,
                "live_data_required": False,
                "committed_artifact_required": False,
            },
            "chart_artifact_guard": {"status": "ok", "checks": []},
            "artifact_ref": {
                "ref_type": "CHART",
                "ref": "artifact://charts/QQQ_1d.png",
                "metadata": {
                    "bars": 60,
                    "renderer": "stdlib_png",
                },
            },
            "live_data_required": False,
        }

    monkeypatch.setattr(reporting, "render_chart", fake_render_chart)
    payload = generate_latest_signal_report("TQQQ", include_chart=True)
    context = payload["multimodal_context"]
    context_guard_checks = {
        check["name"]: check for check in context["guard"]["checks"]
    }
    payload_guard_checks = {
        check["name"]: check for check in payload["report_payload_guard"]["checks"]
    }

    assert payload["chart_code_guard"]["status"] == "ok"
    assert context["status"] == "conflict"
    assert context_guard_checks[
        "multimodal_context_chart_artifact_refs_match_png_contract"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_artifact_ref_metadata_matches_expected_schema"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_artifact_ref_metadata_matches_expected_schema"
    ]["actual"] == {
        "metadata_is_dict": [True],
        "metadata_keys_by_ref_type": {
            "CHART": ["bars", "renderer"],
        },
    }
    assert context_guard_checks[
        "multimodal_context_artifact_ref_metadata_entries_match_expected_schema"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_artifact_ref_metadata_entries_match_expected_schema"
    ]["actual"] == [
        {
            "evidence_id": "latest_signal_chart",
            "ref_type": "CHART",
            "metadata_is_dict": True,
            "metadata_keys": ["bars", "renderer"],
        },
    ]
    assert context_guard_checks[
        "multimodal_context_artifact_ref_metadata_values_are_safe"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_artifact_ref_metadata_values_are_safe"
    ]["actual"] == [
        {
            "evidence_id": "latest_signal_chart",
            "ref_type": "CHART",
            "renderer": "stdlib_png",
            "bars_positive": True,
            "timeframe_supported": None,
        },
    ]
    assert context_guard_checks[
        "multimodal_context_artifact_ref_metadata_value_types_are_strict"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_artifact_ref_metadata_text_values_are_trimmed_and_control_free"
    ]["passed"] is True
    assert payload_guard_checks[
        "report_payload_optional_context_statuses_are_ok"
    ]["actual"] == {
        "chart_code_guard": "ok",
        "multimodal_context": "conflict",
    }


def test_latest_signal_report_rejects_unexpected_chart_metadata_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_render_chart(
        symbol: str = "QQQ",
        timeframe: str = "1d",
        output_dir: str | None = None,
    ) -> dict[str, object]:
        del output_dir
        return {
            "as_of": "2026-05-08T20:00:00Z",
            "symbol": symbol.upper(),
            "timeframe": timeframe,
            "format": "png",
            "path": "artifact://charts/QQQ_1d.png",
            "chart_artifact_contract": {
                "schema_version": "chart_artifact.v1",
                "format": "png",
                "renderer": "stdlib_png",
                "artifact_ref_type": "CHART",
                "network_call": False,
                "live_data_required": False,
                "committed_artifact_required": False,
            },
            "chart_artifact_guard": {"status": "ok", "checks": []},
            "artifact_ref": {
                "ref_type": "CHART",
                "ref": "artifact://charts/QQQ_1d.png",
                "metadata": {
                    "bars": 60,
                    "renderer": "stdlib_png",
                    "timeframe_supported": True,
                    "source": "chart_renderer",
                },
            },
            "live_data_required": False,
        }

    monkeypatch.setattr(reporting, "render_chart", fake_render_chart)
    payload = generate_latest_signal_report("TQQQ", include_chart=True)
    context = payload["multimodal_context"]
    context_guard_checks = {
        check["name"]: check for check in context["guard"]["checks"]
    }
    payload_guard_checks = {
        check["name"]: check for check in payload["report_payload_guard"]["checks"]
    }

    assert payload["chart_code_guard"]["status"] == "ok"
    assert context["status"] == "conflict"
    assert context_guard_checks[
        "multimodal_context_chart_artifact_refs_match_png_contract"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_artifact_ref_metadata_matches_expected_schema"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_artifact_ref_metadata_matches_expected_schema"
    ]["actual"] == {
        "metadata_is_dict": [True],
        "metadata_keys_by_ref_type": {
            "CHART": ["bars", "renderer", "timeframe_supported", "source"],
        },
    }
    assert context_guard_checks[
        "multimodal_context_artifact_ref_metadata_entries_match_expected_schema"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_artifact_ref_metadata_entries_match_expected_schema"
    ]["actual"] == [
        {
            "evidence_id": "latest_signal_chart",
            "ref_type": "CHART",
            "metadata_is_dict": True,
            "metadata_keys": ["bars", "renderer", "timeframe_supported", "source"],
        },
    ]
    assert context_guard_checks[
        "multimodal_context_artifact_ref_metadata_values_are_safe"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_artifact_ref_metadata_value_types_are_strict"
    ]["passed"] is True
    assert payload_guard_checks[
        "report_payload_optional_context_statuses_are_ok"
    ]["actual"] == {
        "chart_code_guard": "ok",
        "multimodal_context": "conflict",
    }


def test_latest_signal_report_rejects_unsafe_chart_metadata_values(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_render_chart(
        symbol: str = "QQQ",
        timeframe: str = "1d",
        output_dir: str | None = None,
    ) -> dict[str, object]:
        del output_dir
        return {
            "as_of": "2026-05-08T20:00:00Z",
            "symbol": symbol.upper(),
            "timeframe": timeframe,
            "format": "png",
            "path": "artifact://charts/QQQ_1d.png",
            "chart_artifact_contract": {
                "schema_version": "chart_artifact.v1",
                "format": "png",
                "renderer": "stdlib_png",
                "artifact_ref_type": "CHART",
                "network_call": False,
                "live_data_required": False,
                "committed_artifact_required": False,
            },
            "chart_artifact_guard": {"status": "ok", "checks": []},
            "artifact_ref": {
                "ref_type": "CHART",
                "ref": "artifact://charts/QQQ_1d.png",
                "metadata": {
                    "bars": 0,
                    "renderer": "stdlib_png",
                    "timeframe_supported": False,
                },
            },
            "live_data_required": False,
        }

    monkeypatch.setattr(reporting, "render_chart", fake_render_chart)
    payload = generate_latest_signal_report("TQQQ", include_chart=True)
    context = payload["multimodal_context"]
    context_guard_checks = {
        check["name"]: check for check in context["guard"]["checks"]
    }
    payload_guard_checks = {
        check["name"]: check for check in payload["report_payload_guard"]["checks"]
    }

    assert payload["chart_code_guard"]["status"] == "ok"
    assert context["status"] == "conflict"
    assert context_guard_checks[
        "multimodal_context_chart_artifact_refs_match_png_contract"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_artifact_ref_metadata_matches_expected_schema"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_artifact_ref_metadata_values_are_safe"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_artifact_ref_metadata_values_are_safe"
    ]["actual"] == [
        {
            "evidence_id": "latest_signal_chart",
            "ref_type": "CHART",
            "renderer": "stdlib_png",
            "bars_positive": False,
            "timeframe_supported": False,
        },
    ]
    assert context_guard_checks[
        "multimodal_context_artifact_ref_metadata_value_types_are_strict"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_artifact_ref_metadata_text_values_are_trimmed_and_control_free"
    ]["passed"] is True
    assert payload_guard_checks[
        "report_payload_optional_context_statuses_are_ok"
    ]["actual"] == {
        "chart_code_guard": "ok",
        "multimodal_context": "conflict",
    }


def test_latest_signal_report_rejects_chart_metadata_non_string_renderer(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_render_chart(
        symbol: str = "QQQ",
        timeframe: str = "1d",
        output_dir: str | None = None,
    ) -> dict[str, object]:
        del output_dir
        return {
            "as_of": "2026-05-08T20:00:00Z",
            "symbol": symbol.upper(),
            "timeframe": timeframe,
            "format": "png",
            "path": "artifact://charts/QQQ_1d.png",
            "chart_artifact_contract": {
                "schema_version": "chart_artifact.v1",
                "format": "png",
                "renderer": "stdlib_png",
                "artifact_ref_type": "CHART",
                "network_call": False,
                "live_data_required": False,
                "committed_artifact_required": False,
            },
            "chart_artifact_guard": {"status": "ok", "checks": []},
            "artifact_ref": {
                "ref_type": "CHART",
                "ref": "artifact://charts/QQQ_1d.png",
                "metadata": {
                    "bars": 60,
                    "renderer": ["stdlib_png"],
                    "timeframe_supported": True,
                },
            },
            "live_data_required": False,
        }

    monkeypatch.setattr(reporting, "render_chart", fake_render_chart)
    payload = generate_latest_signal_report("TQQQ", include_chart=True)
    context = payload["multimodal_context"]
    context_guard_checks = {
        check["name"]: check for check in context["guard"]["checks"]
    }
    payload_guard_checks = {
        check["name"]: check for check in payload["report_payload_guard"]["checks"]
    }

    assert payload["chart_code_guard"]["status"] == "ok"
    assert context["status"] == "conflict"
    assert context_guard_checks[
        "multimodal_context_chart_artifact_refs_match_png_contract"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_artifact_ref_metadata_matches_expected_schema"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_artifact_ref_metadata_value_types_are_strict"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_artifact_ref_metadata_value_types_are_strict"
    ]["actual"] == [
        {
            "evidence_id": "latest_signal_chart",
            "ref_type": "CHART",
            "renderer_is_string": False,
            "bars_is_positive_int": True,
            "timeframe_supported_is_bool_true": True,
        },
    ]
    assert payload_guard_checks[
        "report_payload_optional_context_statuses_are_ok"
    ]["actual"] == {
        "chart_code_guard": "ok",
        "multimodal_context": "conflict",
    }


def test_latest_signal_report_rejects_chart_metadata_unknown_renderer(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_render_chart(
        symbol: str = "QQQ",
        timeframe: str = "1d",
        output_dir: str | None = None,
    ) -> dict[str, object]:
        del output_dir
        return {
            "as_of": "2026-05-08T20:00:00Z",
            "symbol": symbol.upper(),
            "timeframe": timeframe,
            "format": "png",
            "path": "artifact://charts/QQQ_1d.png",
            "chart_artifact_contract": {
                "schema_version": "chart_artifact.v1",
                "format": "png",
                "renderer": "stdlib_png",
                "artifact_ref_type": "CHART",
                "network_call": False,
                "live_data_required": False,
                "committed_artifact_required": False,
            },
            "chart_artifact_guard": {"status": "ok", "checks": []},
            "artifact_ref": {
                "ref_type": "CHART",
                "ref": "artifact://charts/QQQ_1d.png",
                "metadata": {
                    "bars": 60,
                    "renderer": "matplotlib",
                    "timeframe_supported": True,
                },
            },
            "live_data_required": False,
        }

    monkeypatch.setattr(reporting, "render_chart", fake_render_chart)
    payload = generate_latest_signal_report("TQQQ", include_chart=True)
    context = payload["multimodal_context"]
    context_guard_checks = {
        check["name"]: check for check in context["guard"]["checks"]
    }
    payload_guard_checks = {
        check["name"]: check for check in payload["report_payload_guard"]["checks"]
    }

    assert payload["chart_code_guard"]["status"] == "ok"
    assert context["status"] == "conflict"
    assert context_guard_checks[
        "multimodal_context_chart_artifact_refs_match_png_contract"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_artifact_ref_metadata_matches_expected_schema"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_artifact_ref_metadata_value_types_are_strict"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_artifact_ref_metadata_value_types_are_strict"
    ]["actual"] == [
        expected_chart_artifact_ref_metadata_value_types(),
    ]
    assert context_guard_checks[
        "multimodal_context_artifact_ref_metadata_values_are_safe"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_artifact_ref_metadata_values_are_safe"
    ]["actual"] == [
        {
            "evidence_id": "latest_signal_chart",
            "ref_type": "CHART",
            "renderer": "matplotlib",
            "bars_positive": True,
            "timeframe_supported": True,
        },
    ]
    assert payload_guard_checks[
        "report_payload_optional_context_statuses_are_ok"
    ]["actual"] == {
        "chart_code_guard": "ok",
        "multimodal_context": "conflict",
    }


def test_latest_signal_report_rejects_chart_metadata_renderer_control_character(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_render_chart(
        symbol: str = "QQQ",
        timeframe: str = "1d",
        output_dir: str | None = None,
    ) -> dict[str, object]:
        del output_dir
        return {
            "as_of": "2026-05-08T20:00:00Z",
            "symbol": symbol.upper(),
            "timeframe": timeframe,
            "format": "png",
            "path": "artifact://charts/QQQ_1d.png",
            "chart_artifact_contract": {
                "schema_version": "chart_artifact.v1",
                "format": "png",
                "renderer": "stdlib_png",
                "artifact_ref_type": "CHART",
                "network_call": False,
                "live_data_required": False,
                "committed_artifact_required": False,
            },
            "chart_artifact_guard": {"status": "ok", "checks": []},
            "artifact_ref": {
                "ref_type": "CHART",
                "ref": "artifact://charts/QQQ_1d.png",
                "metadata": {
                    "bars": 60,
                    "renderer": "stdlib_png\n",
                    "timeframe_supported": True,
                },
            },
            "live_data_required": False,
        }

    monkeypatch.setattr(reporting, "render_chart", fake_render_chart)
    payload = generate_latest_signal_report("TQQQ", include_chart=True)
    context = payload["multimodal_context"]
    context_guard_checks = {
        check["name"]: check for check in context["guard"]["checks"]
    }
    payload_guard_checks = {
        check["name"]: check for check in payload["report_payload_guard"]["checks"]
    }

    assert payload["chart_code_guard"]["status"] == "ok"
    assert context["status"] == "conflict"
    assert context_guard_checks[
        "multimodal_context_chart_artifact_refs_match_png_contract"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_artifact_ref_metadata_matches_expected_schema"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_artifact_ref_metadata_value_types_are_strict"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_artifact_ref_metadata_values_are_safe"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_artifact_ref_metadata_text_values_are_trimmed_and_control_free"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_artifact_ref_metadata_text_values_are_trimmed_and_control_free"
    ]["actual"] == [
        {
            "evidence_id": "latest_signal_chart",
            "ref_type": "CHART",
            "metadata_text_fields": ["renderer"],
            "metadata_text_values_have_no_surrounding_whitespace": False,
            "metadata_text_values_have_no_control_characters": False,
        },
    ]
    assert payload_guard_checks[
        "report_payload_optional_context_statuses_are_ok"
    ]["actual"] == {
        "chart_code_guard": "ok",
        "multimodal_context": "conflict",
    }


def test_latest_signal_report_rejects_non_dict_chart_artifact_ref_metadata(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_render_chart(
        symbol: str = "QQQ",
        timeframe: str = "1d",
        output_dir: str | None = None,
    ) -> dict[str, object]:
        del output_dir
        return {
            "as_of": "2026-05-08T20:00:00Z",
            "symbol": symbol.upper(),
            "timeframe": timeframe,
            "format": "png",
            "path": "artifact://charts/QQQ_1d.png",
            "chart_artifact_contract": {
                "schema_version": "chart_artifact.v1",
                "format": "png",
                "renderer": "stdlib_png",
                "artifact_ref_type": "CHART",
                "network_call": False,
                "live_data_required": False,
                "committed_artifact_required": False,
            },
            "chart_artifact_guard": {"status": "ok", "checks": []},
            "artifact_ref": {
                "ref_type": "CHART",
                "ref": "artifact://charts/QQQ_1d.png",
                "metadata": [],
            },
            "live_data_required": False,
    }

    monkeypatch.setattr(reporting, "render_chart", fake_render_chart)
    with pytest.raises(ValidationError, match="chart_ref.metadata"):
        generate_latest_signal_report("TQQQ", include_chart=True)


def test_latest_signal_report_rejects_missing_chart_artifact_ref_metadata_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_render_chart(
        symbol: str = "QQQ",
        timeframe: str = "1d",
        output_dir: str | None = None,
    ) -> dict[str, object]:
        del output_dir
        return {
            "as_of": "2026-05-08T20:00:00Z",
            "symbol": symbol.upper(),
            "timeframe": timeframe,
            "format": "png",
            "path": "artifact://charts/QQQ_1d.png",
            "chart_artifact_contract": {
                "schema_version": "chart_artifact.v1",
                "format": "png",
                "renderer": "stdlib_png",
                "artifact_ref_type": "CHART",
                "network_call": False,
                "live_data_required": False,
                "committed_artifact_required": False,
            },
            "chart_artifact_guard": {"status": "ok", "checks": []},
            "artifact_ref": {
                "ref_type": "CHART",
                "ref": "artifact://charts/QQQ_1d.png",
            },
            "live_data_required": False,
        }

    monkeypatch.setattr(reporting, "render_chart", fake_render_chart)
    payload = generate_latest_signal_report("TQQQ", include_chart=True)
    context = payload["multimodal_context"]
    context_guard_checks = {
        check["name"]: check for check in context["guard"]["checks"]
    }
    payload_guard_checks = {
        check["name"]: check for check in payload["report_payload_guard"]["checks"]
    }

    assert payload["chart_code_guard"]["status"] == "ok"
    assert context["status"] == "conflict"
    assert context_guard_checks[
        "multimodal_context_artifact_refs_match_expected_schema"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_chart_artifact_refs_match_png_contract"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_artifact_ref_metadata_matches_expected_schema"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_artifact_ref_metadata_matches_expected_schema"
    ]["actual"] == {
        "metadata_is_dict": [True],
        "metadata_keys_by_ref_type": {"CHART": []},
    }
    assert context_guard_checks[
        "multimodal_context_artifact_ref_metadata_entries_match_expected_schema"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_artifact_ref_metadata_entries_match_expected_schema"
    ]["actual"] == [
        {
            "evidence_id": "latest_signal_chart",
            "ref_type": "CHART",
            "metadata_is_dict": True,
            "metadata_keys": [],
        },
    ]
    assert context_guard_checks[
        "multimodal_context_artifact_ref_metadata_values_are_safe"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_artifact_ref_metadata_values_are_safe"
    ]["actual"] == [
        {
            "evidence_id": "latest_signal_chart",
            "ref_type": "CHART",
            "renderer": None,
            "bars_positive": False,
            "timeframe_supported": None,
        },
    ]
    assert context_guard_checks[
        "multimodal_context_artifact_ref_metadata_value_types_are_strict"
    ]["passed"] is False
    assert payload_guard_checks[
        "report_payload_optional_context_statuses_are_ok"
    ]["actual"] == {
        "chart_code_guard": "ok",
        "multimodal_context": "conflict",
    }


def test_latest_signal_report_rejects_missing_chart_artifact_ref_value_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_render_chart(
        symbol: str = "QQQ",
        timeframe: str = "1d",
        output_dir: str | None = None,
    ) -> dict[str, object]:
        del output_dir
        return {
            "as_of": "2026-05-08T20:00:00Z",
            "symbol": symbol.upper(),
            "timeframe": timeframe,
            "format": "png",
            "path": "artifact://charts/QQQ_1d.png",
            "chart_artifact_contract": {
                "schema_version": "chart_artifact.v1",
                "format": "png",
                "renderer": "stdlib_png",
                "artifact_ref_type": "CHART",
                "network_call": False,
                "live_data_required": False,
                "committed_artifact_required": False,
            },
            "chart_artifact_guard": {"status": "ok", "checks": []},
            "artifact_ref": {
                "ref_type": "CHART",
                "metadata": {
                    "bars": 60,
                    "renderer": "stdlib_png",
                    "timeframe_supported": True,
                },
            },
            "live_data_required": False,
        }

    monkeypatch.setattr(reporting, "render_chart", fake_render_chart)
    with pytest.raises(ValidationError, match="chart_ref.ref"):
        generate_latest_signal_report("TQQQ", include_chart=True)


def test_latest_signal_report_rejects_non_string_chart_artifact_ref_value(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_render_chart(
        symbol: str = "QQQ",
        timeframe: str = "1d",
        output_dir: str | None = None,
    ) -> dict[str, object]:
        del output_dir
        return {
            "as_of": "2026-05-08T20:00:00Z",
            "symbol": symbol.upper(),
            "timeframe": timeframe,
            "format": "png",
            "path": "artifact://charts/QQQ_1d.png",
            "chart_artifact_contract": {
                "schema_version": "chart_artifact.v1",
                "format": "png",
                "renderer": "stdlib_png",
                "artifact_ref_type": "CHART",
                "network_call": False,
                "live_data_required": False,
                "committed_artifact_required": False,
            },
            "chart_artifact_guard": {"status": "ok", "checks": []},
            "artifact_ref": {
                "ref_type": "CHART",
                "ref": 123,
                "metadata": {
                    "bars": 60,
                    "renderer": "stdlib_png",
                    "timeframe_supported": True,
                },
            },
            "live_data_required": False,
        }

    monkeypatch.setattr(reporting, "render_chart", fake_render_chart)
    with pytest.raises(ValidationError, match="chart_ref.ref"):
        generate_latest_signal_report("TQQQ", include_chart=True)


def test_latest_signal_report_rejects_missing_chart_artifact_ref_type_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_render_chart(
        symbol: str = "QQQ",
        timeframe: str = "1d",
        output_dir: str | None = None,
    ) -> dict[str, object]:
        del output_dir
        return {
            "as_of": "2026-05-08T20:00:00Z",
            "symbol": symbol.upper(),
            "timeframe": timeframe,
            "format": "png",
            "path": "artifact://charts/QQQ_1d.png",
            "chart_artifact_contract": {
                "schema_version": "chart_artifact.v1",
                "format": "png",
                "renderer": "stdlib_png",
                "artifact_ref_type": "CHART",
                "network_call": False,
                "live_data_required": False,
                "committed_artifact_required": False,
            },
            "chart_artifact_guard": {"status": "ok", "checks": []},
            "artifact_ref": {
                "ref": "artifact://charts/QQQ_1d.png",
                "metadata": {
                    "bars": 60,
                    "renderer": "stdlib_png",
                    "timeframe_supported": True,
                },
            },
            "live_data_required": False,
        }

    monkeypatch.setattr(reporting, "render_chart", fake_render_chart)
    with pytest.raises(ValidationError, match="chart_ref.ref_type"):
        generate_latest_signal_report("TQQQ", include_chart=True)


def test_latest_signal_report_rejects_unexpected_chart_artifact_ref_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_render_chart(
        symbol: str = "QQQ",
        timeframe: str = "1d",
        output_dir: str | None = None,
    ) -> dict[str, object]:
        del output_dir
        return {
            "as_of": "2026-05-08T20:00:00Z",
            "symbol": symbol.upper(),
            "timeframe": timeframe,
            "format": "png",
            "path": "artifact://charts/QQQ_1d.png",
            "chart_artifact_contract": {
                "schema_version": "chart_artifact.v1",
                "format": "png",
                "renderer": "stdlib_png",
                "artifact_ref_type": "CHART",
                "network_call": False,
                "live_data_required": False,
                "committed_artifact_required": False,
            },
            "chart_artifact_guard": {"status": "ok", "checks": []},
            "artifact_ref": {
                "ref_type": "CHART",
                "ref": "artifact://charts/QQQ_1d.png",
                "metadata": {
                    "bars": 60,
                    "renderer": "stdlib_png",
                    "timeframe_supported": True,
                },
                "mime_type": "image/png",
            },
            "live_data_required": False,
        }

    monkeypatch.setattr(reporting, "render_chart", fake_render_chart)
    with pytest.raises(ValidationError, match="chart_ref.mime_type"):
        generate_latest_signal_report("TQQQ", include_chart=True)


def test_latest_signal_report_rejects_non_string_chart_artifact_ref_type(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_render_chart(
        symbol: str = "QQQ",
        timeframe: str = "1d",
        output_dir: str | None = None,
    ) -> dict[str, object]:
        del output_dir
        return {
            "as_of": "2026-05-08T20:00:00Z",
            "symbol": symbol.upper(),
            "timeframe": timeframe,
            "format": "png",
            "path": "artifact://charts/QQQ_1d.png",
            "chart_artifact_contract": {
                "schema_version": "chart_artifact.v1",
                "format": "png",
                "renderer": "stdlib_png",
                "artifact_ref_type": "CHART",
                "network_call": False,
                "live_data_required": False,
                "committed_artifact_required": False,
            },
            "chart_artifact_guard": {"status": "ok", "checks": []},
            "artifact_ref": {
                "ref_type": 123,
                "ref": "artifact://charts/QQQ_1d.png",
                "metadata": {
                    "bars": 60,
                    "renderer": "stdlib_png",
                    "timeframe_supported": True,
                },
            },
            "live_data_required": False,
        }

    monkeypatch.setattr(reporting, "render_chart", fake_render_chart)
    with pytest.raises(ValidationError, match="chart_ref.ref_type"):
        generate_latest_signal_report("TQQQ", include_chart=True)


def test_latest_signal_report_rejects_empty_chart_artifact_ref_type(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_render_chart(
        symbol: str = "QQQ",
        timeframe: str = "1d",
        output_dir: str | None = None,
    ) -> dict[str, object]:
        del output_dir
        return {
            "as_of": "2026-05-08T20:00:00Z",
            "symbol": symbol.upper(),
            "timeframe": timeframe,
            "format": "png",
            "path": "artifact://charts/QQQ_1d.png",
            "chart_artifact_contract": {
                "schema_version": "chart_artifact.v1",
                "format": "png",
                "renderer": "stdlib_png",
                "artifact_ref_type": "CHART",
                "network_call": False,
                "live_data_required": False,
                "committed_artifact_required": False,
            },
            "chart_artifact_guard": {"status": "ok", "checks": []},
            "artifact_ref": {
                "ref_type": "",
                "ref": "artifact://charts/QQQ_1d.png",
                "metadata": {
                    "bars": 60,
                    "renderer": "stdlib_png",
                    "timeframe_supported": True,
                },
            },
            "live_data_required": False,
        }

    monkeypatch.setattr(reporting, "render_chart", fake_render_chart)
    with pytest.raises(ValidationError, match="chart_ref.ref_type"):
        generate_latest_signal_report("TQQQ", include_chart=True)


def test_latest_signal_report_rejects_lowercase_chart_artifact_ref_type(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_render_chart(
        symbol: str = "QQQ",
        timeframe: str = "1d",
        output_dir: str | None = None,
    ) -> dict[str, object]:
        del output_dir
        return {
            "as_of": "2026-05-08T20:00:00Z",
            "symbol": symbol.upper(),
            "timeframe": timeframe,
            "format": "png",
            "path": "artifact://charts/QQQ_1d.png",
            "chart_artifact_contract": {
                "schema_version": "chart_artifact.v1",
                "format": "png",
                "renderer": "stdlib_png",
                "artifact_ref_type": "CHART",
                "network_call": False,
                "live_data_required": False,
                "committed_artifact_required": False,
            },
            "chart_artifact_guard": {"status": "ok", "checks": []},
            "artifact_ref": {
                "ref_type": "chart",
                "ref": "artifact://charts/QQQ_1d.png",
                "metadata": {
                    "bars": 60,
                    "renderer": "stdlib_png",
                    "timeframe_supported": True,
                },
            },
            "live_data_required": False,
        }

    monkeypatch.setattr(reporting, "render_chart", fake_render_chart)
    with pytest.raises(ValidationError, match="chart_ref.ref_type"):
        generate_latest_signal_report("TQQQ", include_chart=True)


def test_latest_signal_report_rejects_chart_ref_slot_with_pdf_artifact_ref_type(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_render_chart(
        symbol: str = "QQQ",
        timeframe: str = "1d",
        output_dir: str | None = None,
    ) -> dict[str, object]:
        del output_dir
        return {
            "as_of": "2026-05-08T20:00:00Z",
            "symbol": symbol.upper(),
            "timeframe": timeframe,
            "format": "png",
            "path": "artifact://charts/QQQ_1d.pdf",
            "chart_artifact_contract": {
                "schema_version": "chart_artifact.v1",
                "format": "png",
                "renderer": "stdlib_png",
                "artifact_ref_type": "CHART",
                "network_call": False,
                "live_data_required": False,
                "committed_artifact_required": False,
            },
            "chart_artifact_guard": {"status": "ok", "checks": []},
            "artifact_ref": {
                "ref_type": "PDF",
                "ref": "artifact://charts/QQQ_1d.pdf",
                "metadata": {
                    "description": "Caller-supplied chart artifact reference",
                    "portable": True,
                    "parsed_by_mcp": False,
                },
            },
            "live_data_required": False,
        }

    monkeypatch.setattr(reporting, "render_chart", fake_render_chart)
    payload = generate_latest_signal_report("TQQQ", include_chart=True)
    context = payload["multimodal_context"]
    context_guard_checks = {
        check["name"]: check for check in context["guard"]["checks"]
    }
    payload_guard_checks = {
        check["name"]: check for check in payload["report_payload_guard"]["checks"]
    }

    assert payload["chart_code_guard"]["status"] == "ok"
    assert context["status"] == "conflict"
    assert context_guard_checks["chart_refs_are_declared"]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_artifact_ref_types_match_expected_contract"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_pdf_artifact_refs_match_pdf_contract"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_artifact_ref_metadata_matches_expected_schema"
    ]["passed"] is True
    assert context_guard_checks["chart_ref_slot_uses_chart_artifact_ref_type"][
        "passed"
    ] is False
    assert context_guard_checks["chart_ref_slot_uses_chart_artifact_ref_type"][
        "expected"
    ] == {
        "chart_ref_present": True,
        "ref_type": "CHART",
        "slot_uses_chart_artifact_ref_type": True,
    }
    assert context_guard_checks["chart_ref_slot_uses_chart_artifact_ref_type"][
        "actual"
    ] == {
        "chart_ref_present": True,
        "ref_type": "PDF",
        "slot_uses_chart_artifact_ref_type": False,
    }
    assert payload_guard_checks[
        "report_payload_optional_context_statuses_are_ok"
    ]["actual"] == {
        "chart_code_guard": "ok",
        "multimodal_context": "conflict",
    }


def test_latest_signal_report_rejects_extra_card_chart_artifact_ref_id() -> None:
    document = create_document_evidence_card(
        summary="FOMC minutes summary says policy remains restrictive but stable.",
        artifact_ref="artifact://documents/fomc-minutes-summary.pdf",
        asset_scope=["QQQ", "TQQQ"],
    )
    document["evidence_card"]["artifact_ref"] = {
        "ref_type": "CHART",
        "ref": "artifact://charts/manual-document-context.png",
        "metadata": {
            "bars": 60,
            "renderer": "stdlib_png",
            "timeframe_supported": True,
        },
    }
    payload = generate_latest_signal_report(
        "TQQQ",
        extra_evidence_cards=[document["evidence_card"]],
    )
    context = payload["multimodal_context"]
    context_guard_checks = {
        check["name"]: check for check in context["guard"]["checks"]
    }
    payload_guard_checks = {
        check["name"]: check for check in payload["report_payload_guard"]["checks"]
    }

    assert context["status"] == "conflict"
    assert context_guard_checks["chart_refs_are_declared"]["passed"] is True
    assert context_guard_checks[
        "chart_ref_slot_uses_chart_artifact_ref_type"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_artifact_ref_types_match_expected_contract"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_chart_artifact_refs_match_png_contract"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_artifact_ref_metadata_matches_expected_schema"
    ]["passed"] is True
    assert context_guard_checks["chart_artifact_refs_use_reserved_evidence_id"][
        "passed"
    ] is False
    assert context_guard_checks["chart_artifact_refs_use_reserved_evidence_id"][
        "expected"
    ] == [
        expected_chart_artifact_ref_reserved_evidence_id(),
    ]
    assert context_guard_checks["chart_artifact_refs_use_reserved_evidence_id"][
        "actual"
    ] == [
        {
            "evidence_id": "manual_document_summary",
            "ref_type": "CHART",
            "uses_reserved_chart_evidence_id": False,
        },
    ]
    assert payload_guard_checks[
        "report_payload_optional_context_statuses_are_ok"
    ]["actual"] == {
        "multimodal_context": "conflict",
    }


def test_latest_signal_report_rejects_duplicate_chart_artifact_ref_values(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    duplicate_ref = "artifact://charts/QQQ_1d.png"

    def fake_render_chart(
        symbol: str = "QQQ",
        timeframe: str = "1d",
        output_dir: str | None = None,
    ) -> dict[str, object]:
        del output_dir
        return {
            "as_of": "2026-05-08T20:00:00Z",
            "symbol": symbol.upper(),
            "timeframe": timeframe,
            "format": "png",
            "path": duplicate_ref,
            "chart_artifact_contract": {
                "schema_version": "chart_artifact.v1",
                "format": "png",
                "renderer": "stdlib_png",
                "artifact_ref_type": "CHART",
                "network_call": False,
                "live_data_required": False,
                "committed_artifact_required": False,
            },
            "chart_artifact_guard": {"status": "ok", "checks": []},
            "artifact_ref": {
                "ref_type": "CHART",
                "ref": duplicate_ref,
                "metadata": {
                    "bars": 60,
                    "renderer": "stdlib_png",
                    "timeframe_supported": True,
                },
            },
            "live_data_required": False,
        }

    document = create_document_evidence_card(
        summary="FOMC minutes summary says policy remains restrictive but stable.",
        artifact_ref="artifact://documents/fomc-minutes-summary.pdf",
        asset_scope=["QQQ", "TQQQ"],
    )
    document["evidence_card"]["artifact_ref"] = {
        "ref_type": "CHART",
        "ref": duplicate_ref,
        "metadata": {
            "bars": 60,
            "renderer": "stdlib_png",
            "timeframe_supported": True,
        },
    }

    monkeypatch.setattr(reporting, "render_chart", fake_render_chart)
    payload = generate_latest_signal_report(
        "TQQQ",
        include_chart=True,
        extra_evidence_cards=[document["evidence_card"]],
    )
    context = payload["multimodal_context"]
    context_guard_checks = {
        check["name"]: check for check in context["guard"]["checks"]
    }
    payload_guard_checks = {
        check["name"]: check for check in payload["report_payload_guard"]["checks"]
    }

    assert payload["chart_code_guard"]["status"] == "ok"
    assert context["status"] == "conflict"
    assert context_guard_checks[
        "multimodal_context_artifact_ref_evidence_ids_are_unique"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_artifact_ref_values_are_unique"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_artifact_ref_values_are_unique"
    ]["actual"] == {
        "refs": [duplicate_ref, duplicate_ref],
        "nonempty": True,
        "unique": False,
    }
    assert context_guard_checks[
        "multimodal_context_chart_artifact_refs_match_png_contract"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_chart_artifact_refs_use_offline_locations"
    ]["passed"] is True
    assert payload_guard_checks[
        "report_payload_optional_context_statuses_are_ok"
    ]["actual"] == {
        "chart_code_guard": "ok",
        "multimodal_context": "conflict",
    }


def test_latest_signal_report_rejects_remote_chart_artifact_ref(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_render_chart(
        symbol: str = "QQQ",
        timeframe: str = "1d",
        output_dir: str | None = None,
    ) -> dict[str, object]:
        del output_dir
        remote_ref = f"https://charts.example.test/{symbol.upper()}_{timeframe}.png"
        return {
            "as_of": "2026-05-08T20:00:00Z",
            "symbol": symbol.upper(),
            "timeframe": timeframe,
            "format": "png",
            "path": remote_ref,
            "chart_artifact_contract": {
                "schema_version": "chart_artifact.v1",
                "format": "png",
                "renderer": "stdlib_png",
                "artifact_ref_type": "CHART",
                "network_call": False,
                "live_data_required": False,
                "committed_artifact_required": False,
            },
            "chart_artifact_guard": {"status": "ok", "checks": []},
            "artifact_ref": {
                "ref_type": "CHART",
                "ref": remote_ref,
                "metadata": {
                    "bars": 60,
                    "renderer": "stdlib_png",
                    "timeframe_supported": True,
                },
            },
            "live_data_required": False,
        }

    monkeypatch.setattr(reporting, "render_chart", fake_render_chart)
    payload = generate_latest_signal_report("TQQQ", include_chart=True)
    context = payload["multimodal_context"]
    context_guard_checks = {
        check["name"]: check for check in context["guard"]["checks"]
    }
    payload_guard_checks = {
        check["name"]: check for check in payload["report_payload_guard"]["checks"]
    }

    assert payload["chart_code_guard"]["status"] == "ok"
    assert context["status"] == "conflict"
    assert context_guard_checks[
        "multimodal_context_chart_artifact_refs_match_png_contract"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_artifact_ref_metadata_values_are_safe"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_chart_artifact_refs_use_offline_locations"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_chart_artifact_refs_use_offline_locations"
    ]["actual"] == [
        {
            "evidence_id": "latest_signal_chart",
            "ref_type": "CHART",
            "allowed_ref_locations": [
                "local_path",
                "artifact://",
                "sha256:",
            ],
            "network_ref_allowed": False,
            "ref_uses_offline_location": False,
        },
    ]
    assert payload_guard_checks[
        "report_payload_optional_context_statuses_are_ok"
    ]["actual"] == {
        "chart_code_guard": "ok",
        "multimodal_context": "conflict",
    }


def test_latest_signal_report_rejects_file_uri_chart_artifact_ref(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_render_chart(
        symbol: str = "QQQ",
        timeframe: str = "1d",
        output_dir: str | None = None,
    ) -> dict[str, object]:
        del output_dir
        file_uri_ref = f"file:///tmp/{symbol.upper()}_{timeframe}.png"
        return {
            "as_of": "2026-05-08T20:00:00Z",
            "symbol": symbol.upper(),
            "timeframe": timeframe,
            "format": "png",
            "path": file_uri_ref,
            "chart_artifact_contract": {
                "schema_version": "chart_artifact.v1",
                "format": "png",
                "renderer": "stdlib_png",
                "artifact_ref_type": "CHART",
                "network_call": False,
                "live_data_required": False,
                "committed_artifact_required": False,
            },
            "chart_artifact_guard": {"status": "ok", "checks": []},
            "artifact_ref": {
                "ref_type": "CHART",
                "ref": file_uri_ref,
                "metadata": {
                    "bars": 60,
                    "renderer": "stdlib_png",
                    "timeframe_supported": True,
                },
            },
            "live_data_required": False,
        }

    monkeypatch.setattr(reporting, "render_chart", fake_render_chart)
    payload = generate_latest_signal_report("TQQQ", include_chart=True)
    context = payload["multimodal_context"]
    context_guard_checks = {
        check["name"]: check for check in context["guard"]["checks"]
    }
    payload_guard_checks = {
        check["name"]: check for check in payload["report_payload_guard"]["checks"]
    }

    assert payload["chart_code_guard"]["status"] == "ok"
    assert context["status"] == "conflict"
    assert context_guard_checks[
        "multimodal_context_chart_artifact_refs_match_png_contract"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_artifact_ref_metadata_values_are_safe"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_chart_artifact_refs_use_offline_locations"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_chart_artifact_refs_use_offline_locations"
    ]["actual"] == [
        {
            "evidence_id": "latest_signal_chart",
            "ref_type": "CHART",
            "allowed_ref_locations": [
                "local_path",
                "artifact://",
                "sha256:",
            ],
            "network_ref_allowed": False,
            "ref_uses_offline_location": False,
        },
    ]
    assert payload_guard_checks[
        "report_payload_optional_context_statuses_are_ok"
    ]["actual"] == {
        "chart_code_guard": "ok",
        "multimodal_context": "conflict",
    }


def test_latest_signal_report_rejects_tilde_chart_artifact_ref(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_render_chart(
        symbol: str = "QQQ",
        timeframe: str = "1d",
        output_dir: str | None = None,
    ) -> dict[str, object]:
        del output_dir
        tilde_ref = f"~/charts/{symbol.upper()}_{timeframe}.png"
        return {
            "as_of": "2026-05-08T20:00:00Z",
            "symbol": symbol.upper(),
            "timeframe": timeframe,
            "format": "png",
            "path": tilde_ref,
            "chart_artifact_contract": {
                "schema_version": "chart_artifact.v1",
                "format": "png",
                "renderer": "stdlib_png",
                "artifact_ref_type": "CHART",
                "network_call": False,
                "live_data_required": False,
                "committed_artifact_required": False,
            },
            "chart_artifact_guard": {"status": "ok", "checks": []},
            "artifact_ref": {
                "ref_type": "CHART",
                "ref": tilde_ref,
                "metadata": {
                    "bars": 60,
                    "renderer": "stdlib_png",
                    "timeframe_supported": True,
                },
            },
            "live_data_required": False,
        }

    monkeypatch.setattr(reporting, "render_chart", fake_render_chart)
    payload = generate_latest_signal_report("TQQQ", include_chart=True)
    context = payload["multimodal_context"]
    context_guard_checks = {
        check["name"]: check for check in context["guard"]["checks"]
    }
    payload_guard_checks = {
        check["name"]: check for check in payload["report_payload_guard"]["checks"]
    }

    assert payload["chart_code_guard"]["status"] == "ok"
    assert context["status"] == "conflict"
    assert context_guard_checks[
        "multimodal_context_chart_artifact_refs_match_png_contract"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_artifact_ref_metadata_values_are_safe"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_chart_artifact_refs_use_offline_locations"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_chart_artifact_refs_use_offline_locations"
    ]["actual"] == [
        {
            "evidence_id": "latest_signal_chart",
            "ref_type": "CHART",
            "allowed_ref_locations": [
                "local_path",
                "artifact://",
                "sha256:",
            ],
            "network_ref_allowed": False,
            "ref_uses_offline_location": False,
        },
    ]
    assert payload_guard_checks[
        "report_payload_optional_context_statuses_are_ok"
    ]["actual"] == {
        "chart_code_guard": "ok",
        "multimodal_context": "conflict",
    }


def test_latest_signal_report_rejects_user_home_absolute_chart_artifact_ref(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_render_chart(
        symbol: str = "QQQ",
        timeframe: str = "1d",
        output_dir: str | None = None,
    ) -> dict[str, object]:
        del output_dir
        user_path_ref = f"/Users/june/charts/{symbol.upper()}_{timeframe}.png"
        return {
            "as_of": "2026-05-08T20:00:00Z",
            "symbol": symbol.upper(),
            "timeframe": timeframe,
            "format": "png",
            "path": user_path_ref,
            "chart_artifact_contract": {
                "schema_version": "chart_artifact.v1",
                "format": "png",
                "renderer": "stdlib_png",
                "artifact_ref_type": "CHART",
                "network_call": False,
                "live_data_required": False,
                "committed_artifact_required": False,
            },
            "chart_artifact_guard": {"status": "ok", "checks": []},
            "artifact_ref": {
                "ref_type": "CHART",
                "ref": user_path_ref,
                "metadata": {
                    "bars": 60,
                    "renderer": "stdlib_png",
                    "timeframe_supported": True,
                },
            },
            "live_data_required": False,
        }

    monkeypatch.setattr(reporting, "render_chart", fake_render_chart)
    payload = generate_latest_signal_report("TQQQ", include_chart=True)
    context = payload["multimodal_context"]
    context_guard_checks = {
        check["name"]: check for check in context["guard"]["checks"]
    }
    payload_guard_checks = {
        check["name"]: check for check in payload["report_payload_guard"]["checks"]
    }

    assert payload["chart_code_guard"]["status"] == "ok"
    assert context["status"] == "conflict"
    assert context_guard_checks[
        "multimodal_context_chart_artifact_refs_match_png_contract"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_artifact_ref_metadata_values_are_safe"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_chart_artifact_refs_use_offline_locations"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_chart_artifact_refs_use_offline_locations"
    ]["actual"] == [
        {
            "evidence_id": "latest_signal_chart",
            "ref_type": "CHART",
            "allowed_ref_locations": [
                "local_path",
                "artifact://",
                "sha256:",
            ],
            "network_ref_allowed": False,
            "ref_uses_offline_location": False,
        },
    ]
    assert payload_guard_checks[
        "report_payload_optional_context_statuses_are_ok"
    ]["actual"] == {
        "chart_code_guard": "ok",
        "multimodal_context": "conflict",
    }


def test_latest_signal_report_rejects_drive_root_chart_artifact_ref(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_render_chart(
        symbol: str = "QQQ",
        timeframe: str = "1d",
        output_dir: str | None = None,
    ) -> dict[str, object]:
        del output_dir
        drive_root_ref = f"C:/Users/june/charts/{symbol.upper()}_{timeframe}.png"
        return {
            "as_of": "2026-05-08T20:00:00Z",
            "symbol": symbol.upper(),
            "timeframe": timeframe,
            "format": "png",
            "path": drive_root_ref,
            "chart_artifact_contract": {
                "schema_version": "chart_artifact.v1",
                "format": "png",
                "renderer": "stdlib_png",
                "artifact_ref_type": "CHART",
                "network_call": False,
                "live_data_required": False,
                "committed_artifact_required": False,
            },
            "chart_artifact_guard": {"status": "ok", "checks": []},
            "artifact_ref": {
                "ref_type": "CHART",
                "ref": drive_root_ref,
                "metadata": {
                    "bars": 60,
                    "renderer": "stdlib_png",
                    "timeframe_supported": True,
                },
            },
            "live_data_required": False,
        }

    monkeypatch.setattr(reporting, "render_chart", fake_render_chart)
    payload = generate_latest_signal_report("TQQQ", include_chart=True)
    context = payload["multimodal_context"]
    context_guard_checks = {
        check["name"]: check for check in context["guard"]["checks"]
    }
    payload_guard_checks = {
        check["name"]: check for check in payload["report_payload_guard"]["checks"]
    }

    assert payload["chart_code_guard"]["status"] == "ok"
    assert context["status"] == "conflict"
    assert context_guard_checks[
        "multimodal_context_chart_artifact_refs_match_png_contract"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_artifact_ref_metadata_values_are_safe"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_chart_artifact_refs_use_offline_locations"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_chart_artifact_refs_use_offline_locations"
    ]["actual"] == [
        {
            "evidence_id": "latest_signal_chart",
            "ref_type": "CHART",
            "allowed_ref_locations": [
                "local_path",
                "artifact://",
                "sha256:",
            ],
            "network_ref_allowed": False,
            "ref_uses_offline_location": False,
        },
    ]
    assert payload_guard_checks[
        "report_payload_optional_context_statuses_are_ok"
    ]["actual"] == {
        "chart_code_guard": "ok",
        "multimodal_context": "conflict",
    }


def test_latest_signal_report_rejects_chart_artifact_ref_with_embedded_local_path(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_render_chart(
        symbol: str = "QQQ",
        timeframe: str = "1d",
        output_dir: str | None = None,
    ) -> dict[str, object]:
        del output_dir
        embedded_path_ref = f"artifact://charts//Users/june/{symbol.upper()}_{timeframe}.png"
        return {
            "as_of": "2026-05-08T20:00:00Z",
            "symbol": symbol.upper(),
            "timeframe": timeframe,
            "format": "png",
            "path": embedded_path_ref,
            "chart_artifact_contract": {
                "schema_version": "chart_artifact.v1",
                "format": "png",
                "renderer": "stdlib_png",
                "artifact_ref_type": "CHART",
                "network_call": False,
                "live_data_required": False,
                "committed_artifact_required": False,
            },
            "chart_artifact_guard": {"status": "ok", "checks": []},
            "artifact_ref": {
                "ref_type": "CHART",
                "ref": embedded_path_ref,
                "metadata": {
                    "bars": 60,
                    "renderer": "stdlib_png",
                    "timeframe_supported": True,
                },
            },
            "live_data_required": False,
        }

    monkeypatch.setattr(reporting, "render_chart", fake_render_chart)
    payload = generate_latest_signal_report("TQQQ", include_chart=True)
    context = payload["multimodal_context"]
    context_guard_checks = {
        check["name"]: check for check in context["guard"]["checks"]
    }
    payload_guard_checks = {
        check["name"]: check for check in payload["report_payload_guard"]["checks"]
    }

    assert payload["chart_code_guard"]["status"] == "ok"
    assert context["status"] == "conflict"
    assert context_guard_checks[
        "multimodal_context_chart_artifact_refs_match_png_contract"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_chart_artifact_refs_use_offline_locations"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_artifact_ref_values_do_not_embed_local_path_markers"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_artifact_ref_values_do_not_embed_local_path_markers"
    ]["actual"] == [
        {
            "evidence_id": "latest_signal_chart",
            "forbidden_ref_fragments": [
                "/Users/",
                "file://",
                "~/",
            ],
            "forbidden_drive_root": True,
            "ref_has_no_local_path_marker": False,
        },
    ]
    assert payload_guard_checks[
        "report_payload_optional_context_statuses_are_ok"
    ]["actual"] == {
        "chart_code_guard": "ok",
        "multimodal_context": "conflict",
    }


def test_latest_signal_report_rejects_chart_artifact_ref_with_surrounding_whitespace(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_render_chart(
        symbol: str = "QQQ",
        timeframe: str = "1d",
        output_dir: str | None = None,
    ) -> dict[str, object]:
        del output_dir
        whitespace_ref = f"artifact://charts/{symbol.upper()}_{timeframe}.png "
        return {
            "as_of": "2026-05-08T20:00:00Z",
            "symbol": symbol.upper(),
            "timeframe": timeframe,
            "format": "png",
            "path": whitespace_ref,
            "chart_artifact_contract": {
                "schema_version": "chart_artifact.v1",
                "format": "png",
                "renderer": "stdlib_png",
                "artifact_ref_type": "CHART",
                "network_call": False,
                "live_data_required": False,
                "committed_artifact_required": False,
            },
            "chart_artifact_guard": {"status": "ok", "checks": []},
            "artifact_ref": {
                "ref_type": "CHART",
                "ref": whitespace_ref,
                "metadata": {
                    "bars": 60,
                    "renderer": "stdlib_png",
                    "timeframe_supported": True,
                },
            },
            "live_data_required": False,
        }

    monkeypatch.setattr(reporting, "render_chart", fake_render_chart)
    payload = generate_latest_signal_report("TQQQ", include_chart=True)
    context = payload["multimodal_context"]
    context_guard_checks = {
        check["name"]: check for check in context["guard"]["checks"]
    }
    payload_guard_checks = {
        check["name"]: check for check in payload["report_payload_guard"]["checks"]
    }

    assert payload["chart_code_guard"]["status"] == "ok"
    assert context["status"] == "conflict"
    assert context_guard_checks[
        "multimodal_context_chart_artifact_refs_match_png_contract"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_chart_artifact_refs_use_offline_locations"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_artifact_ref_values_are_trimmed_and_control_free"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_artifact_ref_values_are_trimmed_and_control_free"
    ]["actual"] == [
        {
            "evidence_id": "latest_signal_chart",
            "ref_has_no_surrounding_whitespace": False,
            "ref_has_no_control_characters": True,
        },
    ]
    assert payload_guard_checks[
        "report_payload_optional_context_statuses_are_ok"
    ]["actual"] == {
        "chart_code_guard": "ok",
        "multimodal_context": "conflict",
    }


def test_latest_signal_report_rejects_chart_artifact_ref_with_control_character(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_render_chart(
        symbol: str = "QQQ",
        timeframe: str = "1d",
        output_dir: str | None = None,
    ) -> dict[str, object]:
        del output_dir
        control_ref = f"artifact://charts/{symbol.upper()}_{timeframe}.png\n"
        return {
            "as_of": "2026-05-08T20:00:00Z",
            "symbol": symbol.upper(),
            "timeframe": timeframe,
            "format": "png",
            "path": control_ref,
            "chart_artifact_contract": {
                "schema_version": "chart_artifact.v1",
                "format": "png",
                "renderer": "stdlib_png",
                "artifact_ref_type": "CHART",
                "network_call": False,
                "live_data_required": False,
                "committed_artifact_required": False,
            },
            "chart_artifact_guard": {"status": "ok", "checks": []},
            "artifact_ref": {
                "ref_type": "CHART",
                "ref": control_ref,
                "metadata": {
                    "bars": 60,
                    "renderer": "stdlib_png",
                    "timeframe_supported": True,
                },
            },
            "live_data_required": False,
        }

    monkeypatch.setattr(reporting, "render_chart", fake_render_chart)
    payload = generate_latest_signal_report("TQQQ", include_chart=True)
    context = payload["multimodal_context"]
    context_guard_checks = {
        check["name"]: check for check in context["guard"]["checks"]
    }
    payload_guard_checks = {
        check["name"]: check for check in payload["report_payload_guard"]["checks"]
    }

    assert payload["chart_code_guard"]["status"] == "ok"
    assert context["status"] == "conflict"
    assert context_guard_checks[
        "multimodal_context_chart_artifact_refs_match_png_contract"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_chart_artifact_refs_use_offline_locations"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_artifact_ref_values_are_trimmed_and_control_free"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_artifact_ref_values_are_trimmed_and_control_free"
    ]["actual"] == [
        {
            "evidence_id": "latest_signal_chart",
            "ref_has_no_surrounding_whitespace": False,
            "ref_has_no_control_characters": False,
        },
    ]
    assert payload_guard_checks[
        "report_payload_optional_context_statuses_are_ok"
    ]["actual"] == {
        "chart_code_guard": "ok",
        "multimodal_context": "conflict",
    }


def test_latest_signal_report_rejects_malformed_sha256_chart_artifact_ref(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_render_chart(
        symbol: str = "QQQ",
        timeframe: str = "1d",
        output_dir: str | None = None,
    ) -> dict[str, object]:
        del symbol, timeframe, output_dir
        malformed_ref = "sha256:not-a-real-digest"
        return {
            "as_of": "2026-05-08T20:00:00Z",
            "symbol": "QQQ",
            "timeframe": "1d",
            "format": "png",
            "path": malformed_ref,
            "chart_artifact_contract": {
                "schema_version": "chart_artifact.v1",
                "format": "png",
                "renderer": "stdlib_png",
                "artifact_ref_type": "CHART",
                "network_call": False,
                "live_data_required": False,
                "committed_artifact_required": False,
            },
            "chart_artifact_guard": {"status": "ok", "checks": []},
            "artifact_ref": {
                "ref_type": "CHART",
                "ref": malformed_ref,
                "metadata": {
                    "bars": 60,
                    "renderer": "stdlib_png",
                    "timeframe_supported": True,
                },
            },
            "live_data_required": False,
        }

    monkeypatch.setattr(reporting, "render_chart", fake_render_chart)
    payload = generate_latest_signal_report("TQQQ", include_chart=True)
    context = payload["multimodal_context"]
    context_guard_checks = {
        check["name"]: check for check in context["guard"]["checks"]
    }
    payload_guard_checks = {
        check["name"]: check for check in payload["report_payload_guard"]["checks"]
    }

    assert payload["chart_code_guard"]["status"] == "ok"
    assert context["status"] == "conflict"
    assert context_guard_checks[
        "multimodal_context_artifact_ref_metadata_values_are_safe"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_chart_artifact_refs_match_png_contract"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_chart_artifact_refs_match_png_contract"
    ]["actual"] == [
        {
            "evidence_id": "latest_signal_chart",
            "ref_type": "CHART",
            "allowed_ref_suffixes": [".png"],
            "content_addressed_prefix": "sha256:",
            "ref_matches_chart_contract": False,
        },
    ]
    assert context_guard_checks[
        "multimodal_context_chart_artifact_refs_use_offline_locations"
    ]["passed"] is False
    assert payload_guard_checks[
        "report_payload_optional_context_statuses_are_ok"
    ]["actual"] == {
        "chart_code_guard": "ok",
        "multimodal_context": "conflict",
    }


def test_latest_signal_report_accepts_valid_sha256_chart_artifact_ref(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_render_chart(
        symbol: str = "QQQ",
        timeframe: str = "1d",
        output_dir: str | None = None,
    ) -> dict[str, object]:
        del symbol, timeframe, output_dir
        content_ref = f"sha256:{'a' * 64}"
        return {
            "as_of": "2026-05-08T20:00:00Z",
            "symbol": "QQQ",
            "timeframe": "1d",
            "format": "png",
            "path": content_ref,
            "chart_artifact_contract": {
                "schema_version": "chart_artifact.v1",
                "format": "png",
                "renderer": "stdlib_png",
                "artifact_ref_type": "CHART",
                "network_call": False,
                "live_data_required": False,
                "committed_artifact_required": False,
            },
            "chart_artifact_guard": {"status": "ok", "checks": []},
            "artifact_ref": {
                "ref_type": "CHART",
                "ref": content_ref,
                "metadata": {
                    "bars": 60,
                    "renderer": "stdlib_png",
                    "timeframe_supported": True,
                },
            },
            "live_data_required": False,
        }

    monkeypatch.setattr(reporting, "render_chart", fake_render_chart)
    payload = generate_latest_signal_report("TQQQ", include_chart=True)
    context = payload["multimodal_context"]
    context_guard_checks = {
        check["name"]: check for check in context["guard"]["checks"]
    }
    payload_guard_checks = {
        check["name"]: check for check in payload["report_payload_guard"]["checks"]
    }

    assert payload["chart_code_guard"]["status"] == "ok"
    assert context["status"] == "ok"
    assert context_guard_checks[
        "multimodal_context_chart_artifact_refs_match_png_contract"
    ]["actual"] == [
        expected_chart_png_artifact_ref_contract(),
    ]
    assert context_guard_checks[
        "multimodal_context_chart_artifact_refs_use_offline_locations"
    ]["actual"] == [
        expected_chart_offline_artifact_ref_location(),
    ]
    assert payload_guard_checks[
        "report_payload_optional_context_statuses_are_ok"
    ]["actual"] == {
        "chart_code_guard": "ok",
        "multimodal_context": "ok",
    }


def test_latest_signal_report_accepts_multimodal_document_context(tmp_path: Path) -> None:
    document = create_document_evidence_card(
        summary="FOMC minutes summary says policy remains restrictive but stable.",
        artifact_ref="artifact://documents/fomc-minutes-summary.pdf",
        asset_scope=["QQQ", "TQQQ"],
    )
    payload = generate_latest_signal_report(
        "TQQQ",
        include_chart=True,
        chart_output_dir=str(tmp_path),
        extra_evidence_cards=[document["evidence_card"]],
    )
    context = payload["multimodal_context"]
    context_guard_checks = {
        check["name"]: check for check in context["guard"]["checks"]
    }

    assert context["status"] == "ok"
    assert context["schema_version"] == "multimodal_context.v1"
    assert context["numeric_authority"] == "latest_signal_report"
    assert context["hermes_multimodal_call"] is False
    assert context["network_call"] is False
    assert context["raw_artifacts_embedded"] is False
    assert context["modality_counts"]["chart_image"] == 1
    assert context["modality_counts"]["pdf_summary"] == 1
    assert {ref["artifact_ref"]["ref_type"] for ref in context["artifact_refs"]} == {
        "CHART",
        "PDF",
    }
    assert context["guard"]["status"] == "ok"
    assert all(check["passed"] for check in context["guard"]["checks"])
    assert context_guard_checks["chart_artifact_refs_use_reserved_evidence_id"][
        "actual"
    ] == [
        expected_chart_artifact_ref_reserved_evidence_id(),
    ]
    payload_guard_checks = {
        check["name"]: check for check in payload["report_payload_guard"]["checks"]
    }
    assert payload_guard_checks["report_payload_keys_match_expected_schema"][
        "passed"
    ] is True
    assert "multimodal_context" in payload_guard_checks[
        "report_payload_keys_match_expected_schema"
    ]["actual"]
    assert (
        payload_guard_checks[
            "report_payload_optional_context_statuses_are_ok"
        ]["passed"]
        is True
    )
    assert payload_guard_checks[
        "report_payload_optional_context_statuses_are_ok"
    ]["actual"] == {
        "chart_code_guard": "ok",
        "multimodal_context": "ok",
    }
    assert payload_guard_checks[
        "report_payload_optional_context_statuses_are_ok"
    ]["expected"] == {
        "chart_code_guard": "ok",
        "multimodal_context": "ok",
    }
    assert (
        payload_guard_checks[
            "report_payload_optional_context_guards_are_ok"
        ]["passed"]
        is True
    )
    assert payload_guard_checks[
        "report_payload_optional_context_guards_are_ok"
    ]["actual"] == {
        "chart_code_guard": "ok",
        "multimodal_context.guard": "ok",
    }
    assert payload_guard_checks[
        "report_payload_optional_context_guards_are_ok"
    ]["expected"] == {
        "chart_code_guard": "ok",
        "multimodal_context.guard": "ok",
    }
    assert context_guard_checks[
        "multimodal_context_guard_check_names_match_expected_schema"
    ]["actual"] == context_guard_checks[
        "multimodal_context_guard_check_names_match_expected_schema"
    ]["expected"]
    assert all(
        check_keys == ["name", "passed", "expected", "actual"]
        for check_keys in context_guard_checks[
            "multimodal_context_guard_check_keys_match_expected_schema"
        ]["actual"].values()
    )
    assert context_guard_checks["multimodal_context_guard_keys_match_expected_schema"][
        "actual"
    ] == ["status", "checks"]
    assert (
        context_guard_checks["multimodal_context_keys_match_expected_schema"]["actual"]
        == context_guard_checks["multimodal_context_keys_match_expected_schema"][
            "expected"
        ]
    )
    assert context_guard_checks[
        "multimodal_context_artifact_refs_match_expected_schema"
    ]["actual"] == {
        "artifact_ref_entry_keys": [
            ["evidence_id", "artifact_ref"],
            ["evidence_id", "artifact_ref"],
        ],
        "artifact_ref_keys": [
            ["ref_type", "ref", "metadata"],
            ["ref_type", "ref", "metadata"],
        ],
    }
    assert context_guard_checks[
        "multimodal_context_evidence_card_ids_are_unique"
    ]["actual"] == {
        "ids": ["manual_document_summary"],
        "nonempty": True,
        "unique": True,
    }
    assert context_guard_checks[
        "multimodal_context_evidence_card_ids_do_not_use_reserved_ids"
    ]["actual"] == {
        "reserved_ids": ["latest_signal_chart"],
        "uses_reserved_id": False,
    }
    assert context_guard_checks[
        "multimodal_context_evidence_card_ids_match_safe_contract"
    ]["actual"] == [
        expected_document_evidence_card_safe_id(document["evidence_card"]),
    ]
    assert context_guard_checks[
        "multimodal_context_artifact_ref_evidence_ids_are_unique"
    ]["actual"] == {
        "ids": ["latest_signal_chart", "manual_document_summary"],
        "nonempty": True,
        "unique": True,
    }
    assert context_guard_checks[
        "multimodal_context_artifact_ref_evidence_ids_match_safe_contract"
    ]["actual"] == [
        expected_safe_evidence_id("latest_signal_chart"),
        expected_safe_evidence_id("manual_document_summary"),
    ]
    assert context_guard_checks[
        "multimodal_context_evidence_ids_are_string_typed"
    ]["actual"] == expected_multimodal_evidence_id_types(
        ["manual_document_summary"],
        ["latest_signal_chart", "manual_document_summary"],
    )
    assert context_guard_checks[
        "multimodal_context_artifact_ref_string_field_types_are_strict"
    ]["actual"] == [
        expected_artifact_ref_string_field_types(),
        expected_artifact_ref_string_field_types("manual_document_summary"),
    ]
    assert context_guard_checks[
        "multimodal_context_artifact_ref_values_are_unique"
    ]["actual"] == {
        "refs": [
            payload["latest_signal_report"]["chart_ref"]["ref"],
            document["evidence_card"]["artifact_ref"]["ref"],
        ],
        "nonempty": True,
        "unique": True,
    }
    assert context_guard_checks[
        "multimodal_context_artifact_ref_values_are_trimmed_and_control_free"
    ]["actual"] == [
        expected_artifact_ref_string_safety(),
        expected_artifact_ref_string_safety("manual_document_summary"),
    ]
    assert context_guard_checks[
        "multimodal_context_chart_artifact_refs_match_png_contract"
    ]["actual"] == [
        expected_chart_png_artifact_ref_contract(),
    ]
    assert context_guard_checks[
        "multimodal_context_chart_artifact_refs_use_offline_locations"
    ]["actual"] == [
        expected_chart_offline_artifact_ref_location(),
    ]
    assert context_guard_checks[
        "multimodal_context_artifact_ref_types_match_expected_contract"
    ]["expected"] == EXPECTED_MULTIMODAL_ARTIFACT_REF_TYPES
    assert context_guard_checks[
        "multimodal_context_artifact_ref_types_match_expected_contract"
    ]["actual"] == ["CHART", "PDF"]
    assert context_guard_checks[
        "multimodal_context_artifact_ref_types_are_canonical_uppercase"
    ]["actual"] == [
        expected_artifact_ref_type_canonical("latest_signal_chart", "CHART"),
        expected_artifact_ref_type_canonical("manual_document_summary", "PDF"),
    ]
    assert context_guard_checks[
        "multimodal_context_artifact_ref_metadata_entries_match_expected_schema"
    ]["actual"] == [
        {
            "evidence_id": "latest_signal_chart",
            "ref_type": "CHART",
            "metadata_is_dict": True,
            "metadata_keys": ["bars", "renderer", "timeframe_supported"],
        },
        {
            "evidence_id": "manual_document_summary",
            "ref_type": "PDF",
            "metadata_is_dict": True,
            "metadata_keys": ["description", "portable", "parsed_by_mcp"],
        },
    ]
    assert context_guard_checks[
        "multimodal_context_artifact_ref_metadata_matches_expected_schema"
    ]["actual"] == {
        "metadata_is_dict": [True, True],
        "metadata_keys_by_ref_type": {
            "CHART": ["bars", "renderer", "timeframe_supported"],
            "PDF": ["description", "portable", "parsed_by_mcp"],
        },
    }
    assert context_guard_checks[
        "multimodal_context_artifact_ref_metadata_values_are_safe"
    ]["actual"] == [
        {
            "evidence_id": "latest_signal_chart",
            "ref_type": "CHART",
            "renderer": "stdlib_png",
            "bars_positive": True,
            "timeframe_supported": True,
        },
        {
            "evidence_id": "manual_document_summary",
            "ref_type": "PDF",
            "portable": True,
            "parsed_by_mcp": False,
            "description_nonempty": True,
        },
    ]
    assert context_guard_checks[
        "multimodal_context_artifact_ref_metadata_value_types_are_strict"
    ]["actual"] == [
        expected_chart_artifact_ref_metadata_value_types(),
        expected_document_pdf_artifact_ref_metadata_value_types(
            document["evidence_card"]
        ),
    ]
    assert context_guard_checks[
        "multimodal_context_artifact_ref_metadata_text_values_are_trimmed_and_control_free"
    ]["actual"] == [
        expected_chart_artifact_ref_metadata_text_safety(),
        expected_pdf_artifact_ref_metadata_text_safety(document["evidence_card"]),
    ]
    assert context_guard_checks[
        "multimodal_context_modality_counts_match_expected_context"
    ]["actual"] == {
        "chart_image": 1,
        "pdf_summary": 1,
    }
    assert context_guard_checks[
        "multimodal_context_identity_values_match_expected_contract"
    ]["actual"] == EXPECTED_MULTIMODAL_CONTEXT_IDENTITY_VALUES
    assert context_guard_checks[
        "multimodal_context_evidence_cards_match_expected_schema"
    ]["actual"] == [
        EXPECTED_DOCUMENT_EVIDENCE_CARD_KEYS,
    ]
    assert context_guard_checks[
        "multimodal_context_evidence_card_values_are_safe"
    ]["actual"] == [
        expected_document_evidence_card_values(document["evidence_card"]),
    ]
    assert context_guard_checks[
        "multimodal_context_evidence_card_string_field_types_are_strict"
    ]["actual"] == [
        expected_document_evidence_card_string_field_types(
            document["evidence_card"]
        ),
    ]
    assert context_guard_checks[
        "multimodal_context_evidence_card_structural_field_types_are_strict"
    ]["actual"] == [
        expected_document_evidence_card_structural_field_types(
            document["evidence_card"]
        ),
    ]
    assert context_guard_checks[
        "multimodal_context_evidence_card_asset_scope_values_are_trimmed_and_control_free"
    ]["actual"] == [
        expected_document_evidence_card_asset_scope_string_safety(
            document["evidence_card"]
        ),
    ]
    assert context_guard_checks[
        "multimodal_context_evidence_card_text_values_are_trimmed_and_control_free"
    ]["actual"] == [
        expected_document_evidence_card_text_safety(document["evidence_card"]),
    ]
    assert context_guard_checks[
        "multimodal_context_evidence_card_scalar_values_are_trimmed_and_control_free"
    ]["actual"] == [
        expected_document_evidence_card_scalar_safety(document["evidence_card"]),
    ]
    assert context_guard_checks[
        "multimodal_context_evidence_card_modality_values_are_supported"
    ]["actual"] == [
        expected_document_evidence_card_modality(document["evidence_card"]),
    ]
    assert context_guard_checks[
        "multimodal_context_evidence_card_artifact_refs_use_explicit_uris"
    ]["actual"] == [
        expected_document_evidence_card_artifact_uri(document["evidence_card"]),
    ]
    assert context_guard_checks[
        "multimodal_context_pdf_artifact_refs_match_pdf_contract"
    ]["actual"] == [
        expected_document_pdf_artifact_ref_contract(document["evidence_card"]),
    ]
    assert context_guard_checks[
        "multimodal_context_evidence_card_observed_at_values_are_utc_iso"
    ]["actual"] == [
        expected_document_evidence_card_observed_at(document["evidence_card"]),
    ]
    assert context_guard_checks[
        "multimodal_context_evidence_card_observed_at_not_after_report"
    ]["actual"] == [
        expected_document_evidence_card_observed_at_not_future(
            document["evidence_card"],
            payload["latest_signal_report"]["created_at"],
        ),
    ]
    assert context_guard_checks[
        "multimodal_context_evidence_card_asset_scope_matches_report"
    ]["actual"] == [
        expected_document_evidence_card_asset_scope(document["evidence_card"]),
    ]
    assert context_guard_checks[
        "multimodal_context_evidence_card_asset_scope_values_are_trimmed_and_control_free"
    ]["actual"] == [
        expected_document_evidence_card_asset_scope_string_safety(
            document["evidence_card"]
        ),
    ]
    assert context_guard_checks[
        "multimodal_context_evidence_card_summary_bounds_are_safe"
    ]["actual"] == [
        expected_document_evidence_card_summary_bounds(document["evidence_card"]),
    ]
    assert context_guard_checks[
        "multimodal_context_evidence_card_summary_truncation_flags_are_consistent"
    ]["actual"] == [
        expected_document_evidence_card_summary_truncation(document["evidence_card"]),
    ]
    assert context_guard_checks[
        "multimodal_context_evidence_card_invalidating_conditions_are_actionable"
    ]["actual"] == [
        expected_document_evidence_card_invalidating_condition(
            document["evidence_card"]
        ),
    ]
    assert context_guard_checks[
        "multimodal_context_evidence_card_categorical_values_are_safe"
    ]["actual"] == [
        expected_document_evidence_card_categorical_values(document["evidence_card"]),
    ]
    assert context_guard_checks[
        "multimodal_context_evidence_card_impacts_are_context_only"
    ]["actual"] == [
        expected_document_evidence_card_impact_values(document["evidence_card"]),
    ]
    assert context_guard_checks[
        "multimodal_context_artifact_refs_match_expected_context"
    ]["actual"] == [
        {
            "evidence_id": "latest_signal_chart",
            "artifact_ref": payload["latest_signal_report"]["chart_ref"],
        },
        {
            "evidence_id": "manual_document_summary",
            "artifact_ref": document["evidence_card"]["artifact_ref"],
        },
    ]
    assert payload["live_data_required"] is False


def test_latest_signal_report_accepts_multimodal_document_context_without_chart() -> None:
    document = create_document_evidence_card(
        summary="FOMC minutes summary says policy remains restrictive but stable.",
        artifact_ref="artifact://documents/fomc-minutes-summary.pdf",
        asset_scope=["QQQ", "TQQQ"],
    )
    payload = generate_latest_signal_report(
        "TQQQ",
        extra_evidence_cards=[document["evidence_card"]],
    )
    context = payload["multimodal_context"]
    context_guard_checks = {
        check["name"]: check for check in context["guard"]["checks"]
    }
    payload_guard_checks = {
        check["name"]: check for check in payload["report_payload_guard"]["checks"]
    }

    assert "chart_code_guard" not in payload
    assert context["status"] == "ok"
    assert context["guard"]["status"] == "ok"
    assert context["modality_counts"] == {"pdf_summary": 1}
    assert {ref["artifact_ref"]["ref_type"] for ref in context["artifact_refs"]} == {
        "PDF"
    }
    assert (
        payload_guard_checks["report_payload_keys_match_expected_schema"]["actual"][
            -2:
        ]
        == [
            "multimodal_context",
            "report_payload_guard",
        ]
    )
    assert (
        payload_guard_checks[
            "report_payload_optional_context_statuses_are_ok"
        ]["passed"]
        is True
    )
    assert payload_guard_checks[
        "report_payload_optional_context_statuses_are_ok"
    ]["actual"] == {
        "multimodal_context": "ok",
    }
    assert (
        payload_guard_checks[
            "report_payload_optional_context_guards_are_ok"
        ]["passed"]
        is True
    )
    assert payload_guard_checks[
        "report_payload_optional_context_guards_are_ok"
    ]["actual"] == {
        "multimodal_context.guard": "ok",
    }
    assert (
        context_guard_checks[
            "multimodal_context_guard_check_names_match_expected_schema"
        ]["passed"]
        is True
    )
    assert (
        context_guard_checks[
            "multimodal_context_guard_check_keys_match_expected_schema"
        ]["passed"]
        is True
    )
    assert (
        context_guard_checks["multimodal_context_guard_keys_match_expected_schema"][
            "passed"
        ]
        is True
    )
    assert (
        context_guard_checks["multimodal_context_keys_match_expected_schema"]["passed"]
        is True
    )
    assert context_guard_checks[
        "multimodal_context_artifact_refs_match_expected_schema"
    ]["actual"] == {
        "artifact_ref_entry_keys": [["evidence_id", "artifact_ref"]],
        "artifact_ref_keys": [["ref_type", "ref", "metadata"]],
    }
    assert context_guard_checks[
        "multimodal_context_evidence_card_ids_do_not_use_reserved_ids"
    ]["actual"] == {
        "reserved_ids": ["latest_signal_chart"],
        "uses_reserved_id": False,
    }
    assert context_guard_checks[
        "multimodal_context_evidence_card_ids_match_safe_contract"
    ]["actual"] == [
        expected_document_evidence_card_safe_id(document["evidence_card"]),
    ]
    assert context_guard_checks[
        "multimodal_context_artifact_ref_types_match_expected_contract"
    ]["expected"] == EXPECTED_MULTIMODAL_ARTIFACT_REF_TYPES
    assert context_guard_checks[
        "multimodal_context_artifact_ref_evidence_ids_match_safe_contract"
    ]["actual"] == [
        expected_safe_evidence_id("manual_document_summary"),
    ]
    assert context_guard_checks[
        "multimodal_context_evidence_ids_are_string_typed"
    ]["actual"] == expected_multimodal_evidence_id_types(
        ["manual_document_summary"],
        ["manual_document_summary"],
    )
    assert context_guard_checks[
        "multimodal_context_artifact_ref_string_field_types_are_strict"
    ]["actual"] == [
        expected_artifact_ref_string_field_types("manual_document_summary"),
    ]
    assert context_guard_checks[
        "multimodal_context_artifact_ref_values_are_unique"
    ]["actual"] == {
        "refs": [document["evidence_card"]["artifact_ref"]["ref"]],
        "nonempty": True,
        "unique": True,
    }
    assert context_guard_checks[
        "multimodal_context_artifact_ref_types_match_expected_contract"
    ]["actual"] == ["PDF"]
    assert context_guard_checks[
        "multimodal_context_artifact_ref_types_are_canonical_uppercase"
    ]["actual"] == [
        expected_artifact_ref_type_canonical("manual_document_summary", "PDF"),
    ]
    assert context_guard_checks[
        "multimodal_context_artifact_ref_metadata_entries_match_expected_schema"
    ]["actual"] == [
        {
            "evidence_id": "manual_document_summary",
            "ref_type": "PDF",
            "metadata_is_dict": True,
            "metadata_keys": ["description", "portable", "parsed_by_mcp"],
        },
    ]
    assert context_guard_checks[
        "multimodal_context_artifact_ref_metadata_matches_expected_schema"
    ]["actual"] == {
        "metadata_is_dict": [True],
        "metadata_keys_by_ref_type": {
            "PDF": ["description", "portable", "parsed_by_mcp"],
        },
    }
    assert context_guard_checks[
        "multimodal_context_artifact_ref_metadata_values_are_safe"
    ]["actual"] == [
        {
            "evidence_id": "manual_document_summary",
            "ref_type": "PDF",
            "portable": True,
            "parsed_by_mcp": False,
            "description_nonempty": True,
        },
    ]
    assert context_guard_checks[
        "multimodal_context_artifact_ref_metadata_value_types_are_strict"
    ]["actual"] == [
        expected_document_pdf_artifact_ref_metadata_value_types(
            document["evidence_card"]
        ),
    ]
    assert context_guard_checks[
        "multimodal_context_artifact_ref_metadata_text_values_are_trimmed_and_control_free"
    ]["actual"] == [
        expected_pdf_artifact_ref_metadata_text_safety(document["evidence_card"]),
    ]
    assert context_guard_checks[
        "multimodal_context_modality_counts_match_expected_context"
    ]["actual"] == {
        "pdf_summary": 1,
    }
    assert context_guard_checks[
        "multimodal_context_identity_values_match_expected_contract"
    ]["actual"] == EXPECTED_MULTIMODAL_CONTEXT_IDENTITY_VALUES
    assert context_guard_checks[
        "multimodal_context_evidence_cards_match_expected_schema"
    ]["actual"] == [
        EXPECTED_DOCUMENT_EVIDENCE_CARD_KEYS,
    ]
    assert context_guard_checks[
        "multimodal_context_evidence_card_values_are_safe"
    ]["actual"] == [
        expected_document_evidence_card_values(document["evidence_card"]),
    ]
    assert context_guard_checks[
        "multimodal_context_evidence_card_string_field_types_are_strict"
    ]["actual"] == [
        expected_document_evidence_card_string_field_types(
            document["evidence_card"]
        ),
    ]
    assert context_guard_checks[
        "multimodal_context_evidence_card_structural_field_types_are_strict"
    ]["actual"] == [
        expected_document_evidence_card_structural_field_types(
            document["evidence_card"]
        ),
    ]
    assert context_guard_checks[
        "multimodal_context_evidence_card_asset_scope_values_are_trimmed_and_control_free"
    ]["actual"] == [
        expected_document_evidence_card_asset_scope_string_safety(
            document["evidence_card"]
        ),
    ]
    assert context_guard_checks[
        "multimodal_context_evidence_card_text_values_are_trimmed_and_control_free"
    ]["actual"] == [
        expected_document_evidence_card_text_safety(document["evidence_card"]),
    ]
    assert context_guard_checks[
        "multimodal_context_evidence_card_scalar_values_are_trimmed_and_control_free"
    ]["actual"] == [
        expected_document_evidence_card_scalar_safety(document["evidence_card"]),
    ]
    assert context_guard_checks[
        "multimodal_context_artifact_refs_match_expected_context"
    ]["actual"] == [
        {
            "evidence_id": "manual_document_summary",
            "artifact_ref": document["evidence_card"]["artifact_ref"],
        },
    ]
    assert payload["live_data_required"] is False


def test_latest_signal_report_rejects_unknown_multimodal_artifact_ref_type() -> None:
    document = create_document_evidence_card(
        summary="FOMC minutes summary says policy remains restrictive but stable.",
        artifact_ref="artifact://documents/fomc-minutes-summary.docx",
        ref_type="DOCX",
        asset_scope=["QQQ", "TQQQ"],
    )
    payload = generate_latest_signal_report(
        "TQQQ",
        extra_evidence_cards=[document["evidence_card"]],
    )
    context = payload["multimodal_context"]
    context_guard_checks = {
        check["name"]: check for check in context["guard"]["checks"]
    }
    payload_guard_checks = {
        check["name"]: check for check in payload["report_payload_guard"]["checks"]
    }

    assert "chart_code_guard" not in payload
    assert context["status"] == "conflict"
    assert context["guard"]["status"] == "conflict"
    assert context_guard_checks[
        "multimodal_context_artifact_ref_types_match_expected_contract"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_artifact_ref_types_match_expected_contract"
    ]["expected"] == EXPECTED_MULTIMODAL_ARTIFACT_REF_TYPES
    assert context_guard_checks[
        "multimodal_context_artifact_ref_types_match_expected_contract"
    ]["actual"] == ["DOCX"]
    assert payload_guard_checks[
        "report_payload_optional_context_statuses_are_ok"
    ]["passed"] is False
    assert payload_guard_checks[
        "report_payload_optional_context_statuses_are_ok"
    ]["actual"] == {
        "multimodal_context": "conflict",
    }


def test_latest_signal_report_rejects_unexpected_pdf_artifact_ref_key() -> None:
    document = create_document_evidence_card(
        summary="FOMC minutes summary says policy remains restrictive but stable.",
        artifact_ref="artifact://documents/fomc-minutes-summary.pdf",
        asset_scope=["QQQ", "TQQQ"],
    )
    document["evidence_card"]["artifact_ref"]["mime_type"] = "application/pdf"
    payload = generate_latest_signal_report(
        "TQQQ",
        extra_evidence_cards=[document["evidence_card"]],
    )
    context = payload["multimodal_context"]
    context_guard_checks = {
        check["name"]: check for check in context["guard"]["checks"]
    }
    payload_guard_checks = {
        check["name"]: check for check in payload["report_payload_guard"]["checks"]
    }

    assert context["status"] == "conflict"
    assert context_guard_checks[
        "multimodal_context_artifact_refs_match_expected_schema"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_artifact_refs_match_expected_schema"
    ]["expected"] == {
        "artifact_ref_entry_keys": ["evidence_id", "artifact_ref"],
        "artifact_ref_keys": ["ref_type", "ref", "metadata"],
    }
    assert context_guard_checks[
        "multimodal_context_artifact_refs_match_expected_schema"
    ]["actual"] == {
        "artifact_ref_entry_keys": [["evidence_id", "artifact_ref"]],
        "artifact_ref_keys": [["ref_type", "ref", "metadata", "mime_type"]],
    }
    assert context_guard_checks[
        "multimodal_context_artifact_refs_match_expected_context"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_artifact_ref_string_field_types_are_strict"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_artifact_ref_types_match_expected_contract"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_pdf_artifact_refs_match_pdf_contract"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_artifact_ref_metadata_matches_expected_schema"
    ]["passed"] is True
    assert payload_guard_checks[
        "report_payload_optional_context_statuses_are_ok"
    ]["actual"] == {
        "multimodal_context": "conflict",
    }


def test_latest_signal_report_rejects_missing_pdf_artifact_ref_value_key() -> None:
    document = create_document_evidence_card(
        summary="FOMC minutes summary says policy remains restrictive but stable.",
        artifact_ref="artifact://documents/fomc-minutes-summary.pdf",
        asset_scope=["QQQ", "TQQQ"],
    )
    document["evidence_card"]["artifact_ref"].pop("ref")
    payload = generate_latest_signal_report(
        "TQQQ",
        extra_evidence_cards=[document["evidence_card"]],
    )
    context = payload["multimodal_context"]
    context_guard_checks = {
        check["name"]: check for check in context["guard"]["checks"]
    }
    payload_guard_checks = {
        check["name"]: check for check in payload["report_payload_guard"]["checks"]
    }

    assert context["status"] == "conflict"
    assert context_guard_checks[
        "multimodal_context_artifact_refs_match_expected_schema"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_artifact_refs_match_expected_schema"
    ]["actual"] == {
        "artifact_ref_entry_keys": [["evidence_id", "artifact_ref"]],
        "artifact_ref_keys": [["ref_type", "metadata"]],
    }
    assert context_guard_checks[
        "multimodal_context_artifact_refs_match_expected_context"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_artifact_ref_string_field_types_are_strict"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_artifact_ref_string_field_types_are_strict"
    ]["actual"] == [
        {
            "evidence_id": "manual_document_summary",
            "string_fields": ["ref_type", "ref"],
            "ref_type_is_string": True,
            "ref_is_string": False,
        },
    ]
    assert context_guard_checks[
        "multimodal_context_artifact_ref_values_are_unique"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_artifact_ref_values_are_unique"
    ]["actual"] == {
        "refs": [""],
        "nonempty": False,
        "unique": True,
    }
    assert context_guard_checks[
        "multimodal_context_evidence_card_artifact_refs_use_explicit_uris"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_pdf_artifact_refs_match_pdf_contract"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_artifact_ref_metadata_matches_expected_schema"
    ]["passed"] is True
    assert payload_guard_checks[
        "report_payload_optional_context_statuses_are_ok"
    ]["actual"] == {
        "multimodal_context": "conflict",
    }


def test_latest_signal_report_rejects_missing_pdf_artifact_ref_type_key() -> None:
    document = create_document_evidence_card(
        summary="FOMC minutes summary says policy remains restrictive but stable.",
        artifact_ref="artifact://documents/fomc-minutes-summary.pdf",
        asset_scope=["QQQ", "TQQQ"],
    )
    document["evidence_card"]["artifact_ref"].pop("ref_type")
    payload = generate_latest_signal_report(
        "TQQQ",
        extra_evidence_cards=[document["evidence_card"]],
    )
    context = payload["multimodal_context"]
    context_guard_checks = {
        check["name"]: check for check in context["guard"]["checks"]
    }
    payload_guard_checks = {
        check["name"]: check for check in payload["report_payload_guard"]["checks"]
    }

    assert context["status"] == "conflict"
    assert context_guard_checks[
        "multimodal_context_artifact_refs_match_expected_schema"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_artifact_refs_match_expected_schema"
    ]["actual"] == {
        "artifact_ref_entry_keys": [["evidence_id", "artifact_ref"]],
        "artifact_ref_keys": [["ref", "metadata"]],
    }
    assert context_guard_checks[
        "multimodal_context_artifact_refs_match_expected_context"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_artifact_ref_string_field_types_are_strict"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_artifact_ref_string_field_types_are_strict"
    ]["actual"] == [
        {
            "evidence_id": "manual_document_summary",
            "string_fields": ["ref_type", "ref"],
            "ref_type_is_string": False,
            "ref_is_string": True,
        },
    ]
    assert context_guard_checks[
        "multimodal_context_artifact_ref_types_match_expected_contract"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_artifact_ref_types_match_expected_contract"
    ]["actual"] == [""]
    assert context_guard_checks[
        "multimodal_context_artifact_ref_types_are_canonical_uppercase"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_evidence_card_artifact_refs_use_explicit_uris"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_artifact_ref_metadata_matches_expected_schema"
    ]["passed"] is True
    assert payload_guard_checks[
        "report_payload_optional_context_statuses_are_ok"
    ]["actual"] == {
        "multimodal_context": "conflict",
    }


def test_latest_signal_report_rejects_missing_pdf_artifact_ref_metadata_key() -> None:
    document = create_document_evidence_card(
        summary="FOMC minutes summary says policy remains restrictive but stable.",
        artifact_ref="artifact://documents/fomc-minutes-summary.pdf",
        asset_scope=["QQQ", "TQQQ"],
    )
    document["evidence_card"]["artifact_ref"].pop("metadata")
    payload = generate_latest_signal_report(
        "TQQQ",
        extra_evidence_cards=[document["evidence_card"]],
    )
    context = payload["multimodal_context"]
    context_guard_checks = {
        check["name"]: check for check in context["guard"]["checks"]
    }
    payload_guard_checks = {
        check["name"]: check for check in payload["report_payload_guard"]["checks"]
    }

    assert context["status"] == "conflict"
    assert context_guard_checks[
        "multimodal_context_artifact_refs_match_expected_schema"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_artifact_refs_match_expected_schema"
    ]["actual"] == {
        "artifact_ref_entry_keys": [["evidence_id", "artifact_ref"]],
        "artifact_ref_keys": [["ref_type", "ref"]],
    }
    assert context_guard_checks[
        "multimodal_context_artifact_refs_match_expected_context"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_artifact_ref_string_field_types_are_strict"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_pdf_artifact_refs_match_pdf_contract"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_artifact_ref_metadata_matches_expected_schema"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_artifact_ref_metadata_matches_expected_schema"
    ]["actual"] == {
        "metadata_is_dict": [False],
        "metadata_keys_by_ref_type": {"PDF": []},
    }
    assert context_guard_checks[
        "multimodal_context_artifact_ref_metadata_entries_match_expected_schema"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_artifact_ref_metadata_values_are_safe"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_artifact_ref_metadata_value_types_are_strict"
    ]["passed"] is False
    assert payload_guard_checks[
        "report_payload_optional_context_statuses_are_ok"
    ]["actual"] == {
        "multimodal_context": "conflict",
    }


def test_latest_signal_report_rejects_lowercase_artifact_ref_type() -> None:
    document = create_document_evidence_card(
        summary="FOMC minutes summary says policy remains restrictive but stable.",
        artifact_ref="artifact://documents/fomc-minutes-summary.pdf",
        asset_scope=["QQQ", "TQQQ"],
    )
    document["evidence_card"]["artifact_ref"]["ref_type"] = "pdf"
    payload = generate_latest_signal_report(
        "TQQQ",
        extra_evidence_cards=[document["evidence_card"]],
    )
    context = payload["multimodal_context"]
    context_guard_checks = {
        check["name"]: check for check in context["guard"]["checks"]
    }
    payload_guard_checks = {
        check["name"]: check for check in payload["report_payload_guard"]["checks"]
    }

    assert context["status"] == "conflict"
    assert context_guard_checks[
        "multimodal_context_artifact_ref_types_match_expected_contract"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_pdf_artifact_refs_match_pdf_contract"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_artifact_ref_types_are_canonical_uppercase"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_artifact_ref_types_are_canonical_uppercase"
    ]["expected"] == [
        expected_artifact_ref_type_canonical("manual_document_summary", "PDF"),
    ]
    assert context_guard_checks[
        "multimodal_context_artifact_ref_types_are_canonical_uppercase"
    ]["actual"] == [
        {
            "evidence_id": "manual_document_summary",
            "allowed_ref_types": EXPECTED_MULTIMODAL_ARTIFACT_REF_TYPES,
            "ref_type": "pdf",
            "ref_type_is_canonical_uppercase": False,
        },
    ]
    assert payload_guard_checks[
        "report_payload_optional_context_statuses_are_ok"
    ]["actual"] == {
        "multimodal_context": "conflict",
    }


def test_latest_signal_report_rejects_pdf_ref_type_with_non_pdf_artifact_ref() -> None:
    document = create_document_evidence_card(
        summary="FOMC minutes summary says policy remains restrictive but stable.",
        artifact_ref="artifact://documents/fomc-minutes-summary.docx",
        asset_scope=["QQQ", "TQQQ"],
    )
    payload = generate_latest_signal_report(
        "TQQQ",
        extra_evidence_cards=[document["evidence_card"]],
    )
    context = payload["multimodal_context"]
    context_guard_checks = {
        check["name"]: check for check in context["guard"]["checks"]
    }
    payload_guard_checks = {
        check["name"]: check for check in payload["report_payload_guard"]["checks"]
    }

    assert context["status"] == "conflict"
    assert context_guard_checks[
        "multimodal_context_artifact_ref_types_match_expected_contract"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_evidence_card_artifact_refs_use_explicit_uris"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_pdf_artifact_refs_match_pdf_contract"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_pdf_artifact_refs_match_pdf_contract"
    ]["actual"] == [
        {
            "evidence_id": "manual_document_summary",
            "ref_type": "PDF",
            "allowed_ref_suffixes": [".pdf"],
            "content_addressed_prefix": "sha256:",
            "ref_matches_pdf_contract": False,
        },
    ]
    assert payload_guard_checks[
        "report_payload_optional_context_statuses_are_ok"
    ]["actual"] == {
        "multimodal_context": "conflict",
    }


def test_latest_signal_report_rejects_non_string_pdf_artifact_ref_value() -> None:
    document = create_document_evidence_card(
        summary="FOMC minutes summary says policy remains restrictive but stable.",
        artifact_ref="artifact://documents/fomc-minutes-summary.pdf",
        asset_scope=["QQQ", "TQQQ"],
    )
    document["evidence_card"]["artifact_ref"]["ref"] = 123
    payload = generate_latest_signal_report(
        "TQQQ",
        extra_evidence_cards=[document["evidence_card"]],
    )
    context = payload["multimodal_context"]
    context_guard_checks = {
        check["name"]: check for check in context["guard"]["checks"]
    }
    payload_guard_checks = {
        check["name"]: check for check in payload["report_payload_guard"]["checks"]
    }

    assert context["status"] == "conflict"
    assert context_guard_checks[
        "multimodal_context_artifact_ref_values_are_trimmed_and_control_free"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_artifact_ref_string_field_types_are_strict"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_artifact_ref_string_field_types_are_strict"
    ]["expected"] == [
        expected_artifact_ref_string_field_types("manual_document_summary"),
    ]
    assert context_guard_checks[
        "multimodal_context_artifact_ref_string_field_types_are_strict"
    ]["actual"] == [
        {
            "evidence_id": "manual_document_summary",
            "string_fields": ["ref_type", "ref"],
            "ref_type_is_string": True,
            "ref_is_string": False,
        },
    ]
    assert context_guard_checks[
        "multimodal_context_pdf_artifact_refs_match_pdf_contract"
    ]["passed"] is False
    assert payload_guard_checks[
        "report_payload_optional_context_statuses_are_ok"
    ]["actual"] == {
        "multimodal_context": "conflict",
    }


def test_latest_signal_report_rejects_empty_pdf_artifact_ref_value() -> None:
    document = create_document_evidence_card(
        summary="FOMC minutes summary says policy remains restrictive but stable.",
        artifact_ref="artifact://documents/fomc-minutes-summary.pdf",
        asset_scope=["QQQ", "TQQQ"],
    )
    document["evidence_card"]["artifact_ref"]["ref"] = ""
    payload = generate_latest_signal_report(
        "TQQQ",
        extra_evidence_cards=[document["evidence_card"]],
    )
    context = payload["multimodal_context"]
    context_guard_checks = {
        check["name"]: check for check in context["guard"]["checks"]
    }
    payload_guard_checks = {
        check["name"]: check for check in payload["report_payload_guard"]["checks"]
    }

    assert context["status"] == "conflict"
    assert context_guard_checks[
        "multimodal_context_artifact_ref_values_are_trimmed_and_control_free"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_artifact_ref_string_field_types_are_strict"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_artifact_ref_values_are_unique"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_artifact_ref_values_are_unique"
    ]["actual"] == {
        "refs": [""],
        "nonempty": False,
        "unique": True,
    }
    assert context_guard_checks[
        "multimodal_context_evidence_card_values_are_safe"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_evidence_card_values_are_safe"
    ]["actual"] == [
        {
            **expected_document_evidence_card_values(document["evidence_card"]),
            "artifact_ref_portable": False,
        },
    ]
    assert context_guard_checks[
        "multimodal_context_evidence_card_artifact_refs_use_explicit_uris"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_evidence_card_artifact_refs_use_explicit_uris"
    ]["actual"] == [
        {
            "evidence_id": "manual_document_summary",
            "allowed_ref_prefixes": [
                "artifact://",
                "https://",
                "memory://",
                "urn:",
                "sha256:",
            ],
            "artifact_ref_uses_explicit_uri": False,
        },
    ]
    assert context_guard_checks[
        "multimodal_context_pdf_artifact_refs_match_pdf_contract"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_pdf_artifact_refs_match_pdf_contract"
    ]["actual"] == [
        {
            "evidence_id": "manual_document_summary",
            "ref_type": "PDF",
            "allowed_ref_suffixes": [".pdf"],
            "content_addressed_prefix": "sha256:",
            "ref_matches_pdf_contract": False,
        },
    ]
    assert payload_guard_checks[
        "report_payload_optional_context_statuses_are_ok"
    ]["actual"] == {
        "multimodal_context": "conflict",
    }


def test_latest_signal_report_rejects_non_string_pdf_artifact_ref_type() -> None:
    document = create_document_evidence_card(
        summary="FOMC minutes summary says policy remains restrictive but stable.",
        artifact_ref="artifact://documents/fomc-minutes-summary.pdf",
        asset_scope=["QQQ", "TQQQ"],
    )
    document["evidence_card"]["artifact_ref"]["ref_type"] = 123
    payload = generate_latest_signal_report(
        "TQQQ",
        extra_evidence_cards=[document["evidence_card"]],
    )
    context = payload["multimodal_context"]
    context_guard_checks = {
        check["name"]: check for check in context["guard"]["checks"]
    }
    payload_guard_checks = {
        check["name"]: check for check in payload["report_payload_guard"]["checks"]
    }

    assert context["status"] == "conflict"
    assert context_guard_checks[
        "multimodal_context_evidence_card_artifact_refs_use_explicit_uris"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_artifact_ref_metadata_matches_expected_schema"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_artifact_ref_string_field_types_are_strict"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_artifact_ref_string_field_types_are_strict"
    ]["actual"] == [
        {
            "evidence_id": "manual_document_summary",
            "string_fields": ["ref_type", "ref"],
            "ref_type_is_string": False,
            "ref_is_string": True,
        },
    ]
    assert context_guard_checks[
        "multimodal_context_artifact_ref_types_match_expected_contract"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_artifact_ref_types_match_expected_contract"
    ]["actual"] == ["123"]
    assert payload_guard_checks[
        "report_payload_optional_context_statuses_are_ok"
    ]["actual"] == {
        "multimodal_context": "conflict",
    }


def test_latest_signal_report_rejects_empty_pdf_artifact_ref_type() -> None:
    document = create_document_evidence_card(
        summary="FOMC minutes summary says policy remains restrictive but stable.",
        artifact_ref="artifact://documents/fomc-minutes-summary.pdf",
        asset_scope=["QQQ", "TQQQ"],
    )
    document["evidence_card"]["artifact_ref"]["ref_type"] = ""
    payload = generate_latest_signal_report(
        "TQQQ",
        extra_evidence_cards=[document["evidence_card"]],
    )
    context = payload["multimodal_context"]
    context_guard_checks = {
        check["name"]: check for check in context["guard"]["checks"]
    }
    payload_guard_checks = {
        check["name"]: check for check in payload["report_payload_guard"]["checks"]
    }

    assert context["status"] == "conflict"
    assert context_guard_checks[
        "multimodal_context_evidence_card_artifact_refs_use_explicit_uris"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_artifact_ref_string_field_types_are_strict"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_artifact_ref_types_match_expected_contract"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_artifact_ref_types_match_expected_contract"
    ]["actual"] == [""]
    assert context_guard_checks[
        "multimodal_context_artifact_ref_types_are_canonical_uppercase"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_artifact_ref_types_are_canonical_uppercase"
    ]["actual"] == [
        {
            "evidence_id": "manual_document_summary",
            "allowed_ref_types": EXPECTED_MULTIMODAL_ARTIFACT_REF_TYPES,
            "ref_type": "",
            "ref_type_is_canonical_uppercase": False,
        },
    ]
    assert payload_guard_checks[
        "report_payload_optional_context_statuses_are_ok"
    ]["actual"] == {
        "multimodal_context": "conflict",
    }


def test_latest_signal_report_rejects_malformed_sha256_pdf_artifact_ref() -> None:
    document = create_document_evidence_card(
        summary="FOMC minutes summary says policy remains restrictive but stable.",
        artifact_ref="sha256:not-a-real-digest",
        asset_scope=["QQQ", "TQQQ"],
    )
    payload = generate_latest_signal_report(
        "TQQQ",
        extra_evidence_cards=[document["evidence_card"]],
    )
    context = payload["multimodal_context"]
    context_guard_checks = {
        check["name"]: check for check in context["guard"]["checks"]
    }
    payload_guard_checks = {
        check["name"]: check for check in payload["report_payload_guard"]["checks"]
    }

    assert context["status"] == "conflict"
    assert context_guard_checks[
        "multimodal_context_evidence_card_artifact_refs_use_explicit_uris"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_artifact_ref_metadata_values_are_safe"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_pdf_artifact_refs_match_pdf_contract"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_pdf_artifact_refs_match_pdf_contract"
    ]["actual"] == [
        {
            "evidence_id": "manual_document_summary",
            "ref_type": "PDF",
            "allowed_ref_suffixes": [".pdf"],
            "content_addressed_prefix": "sha256:",
            "ref_matches_pdf_contract": False,
        },
    ]
    assert payload_guard_checks[
        "report_payload_optional_context_statuses_are_ok"
    ]["actual"] == {
        "multimodal_context": "conflict",
    }


def test_latest_signal_report_accepts_valid_sha256_pdf_artifact_ref() -> None:
    document = create_document_evidence_card(
        summary="FOMC minutes summary says policy remains restrictive but stable.",
        artifact_ref=f"sha256:{'b' * 64}",
        asset_scope=["QQQ", "TQQQ"],
    )
    payload = generate_latest_signal_report(
        "TQQQ",
        extra_evidence_cards=[document["evidence_card"]],
    )
    context = payload["multimodal_context"]
    context_guard_checks = {
        check["name"]: check for check in context["guard"]["checks"]
    }
    payload_guard_checks = {
        check["name"]: check for check in payload["report_payload_guard"]["checks"]
    }

    assert context["status"] == "ok"
    assert context_guard_checks[
        "multimodal_context_evidence_card_artifact_refs_use_explicit_uris"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_artifact_ref_metadata_values_are_safe"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_pdf_artifact_refs_match_pdf_contract"
    ]["actual"] == [
        expected_document_pdf_artifact_ref_contract(document["evidence_card"]),
    ]
    assert payload_guard_checks[
        "report_payload_optional_context_statuses_are_ok"
    ]["actual"] == {
        "multimodal_context": "ok",
    }


def test_latest_signal_report_rejects_pdf_artifact_ref_with_embedded_local_path() -> None:
    document = create_document_evidence_card(
        summary="FOMC minutes summary says policy remains restrictive but stable.",
        artifact_ref="artifact://documents//Users/june/fomc-minutes-summary.pdf",
        asset_scope=["QQQ", "TQQQ"],
    )
    payload = generate_latest_signal_report(
        "TQQQ",
        extra_evidence_cards=[document["evidence_card"]],
    )
    context = payload["multimodal_context"]
    context_guard_checks = {
        check["name"]: check for check in context["guard"]["checks"]
    }
    payload_guard_checks = {
        check["name"]: check for check in payload["report_payload_guard"]["checks"]
    }

    assert context["status"] == "conflict"
    assert context_guard_checks[
        "multimodal_context_evidence_card_artifact_refs_use_explicit_uris"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_pdf_artifact_refs_match_pdf_contract"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_artifact_ref_values_do_not_embed_local_path_markers"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_artifact_ref_values_do_not_embed_local_path_markers"
    ]["actual"] == [
        {
            "evidence_id": "manual_document_summary",
            "forbidden_ref_fragments": [
                "/Users/",
                "file://",
                "~/",
            ],
            "forbidden_drive_root": True,
            "ref_has_no_local_path_marker": False,
        },
    ]
    assert payload_guard_checks[
        "report_payload_optional_context_statuses_are_ok"
    ]["actual"] == {
        "multimodal_context": "conflict",
    }


def test_latest_signal_report_rejects_pdf_artifact_ref_with_control_character() -> None:
    document = create_document_evidence_card(
        summary="FOMC minutes summary says policy remains restrictive but stable.",
        artifact_ref="artifact://documents/fomc-minutes-summary.pdf",
        asset_scope=["QQQ", "TQQQ"],
    )
    document["evidence_card"]["artifact_ref"]["ref"] = (
        "artifact://documents/fomc-minutes-summary.pdf\n"
    )
    payload = generate_latest_signal_report(
        "TQQQ",
        extra_evidence_cards=[document["evidence_card"]],
    )
    context = payload["multimodal_context"]
    context_guard_checks = {
        check["name"]: check for check in context["guard"]["checks"]
    }
    payload_guard_checks = {
        check["name"]: check for check in payload["report_payload_guard"]["checks"]
    }

    assert context["status"] == "conflict"
    assert context_guard_checks[
        "multimodal_context_evidence_card_artifact_refs_use_explicit_uris"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_pdf_artifact_refs_match_pdf_contract"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_artifact_ref_values_are_trimmed_and_control_free"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_artifact_ref_values_are_trimmed_and_control_free"
    ]["actual"] == [
        {
            "evidence_id": "manual_document_summary",
            "ref_has_no_surrounding_whitespace": False,
            "ref_has_no_control_characters": False,
        },
    ]
    assert payload_guard_checks[
        "report_payload_optional_context_statuses_are_ok"
    ]["actual"] == {
        "multimodal_context": "conflict",
    }


def test_latest_signal_report_rejects_duplicate_document_metadata_key_drift() -> None:
    bad_document = create_document_evidence_card(
        summary="FOMC minutes summary says policy remains restrictive but stable.",
        artifact_ref="artifact://documents/fomc-minutes-summary.pdf",
        evidence_id="manual_document_bad_metadata",
        asset_scope=["QQQ", "TQQQ"],
    )
    good_document = create_document_evidence_card(
        summary="Treasury refunding summary says duration supply is stable.",
        artifact_ref="artifact://documents/treasury-refunding-summary.pdf",
        evidence_id="manual_document_good_metadata",
        asset_scope=["QQQ", "TQQQ"],
    )
    bad_document["evidence_card"]["artifact_ref"]["metadata"]["raw_text"] = (
        "raw file contents must not be embedded"
    )
    payload = generate_latest_signal_report(
        "TQQQ",
        extra_evidence_cards=[
            bad_document["evidence_card"],
            good_document["evidence_card"],
        ],
    )
    context = payload["multimodal_context"]
    context_guard_checks = {
        check["name"]: check for check in context["guard"]["checks"]
    }
    payload_guard_checks = {
        check["name"]: check for check in payload["report_payload_guard"]["checks"]
    }

    assert context["status"] == "conflict"
    assert context_guard_checks[
        "multimodal_context_artifact_ref_metadata_matches_expected_schema"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_artifact_ref_metadata_entries_match_expected_schema"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_artifact_ref_metadata_entries_match_expected_schema"
    ]["actual"] == [
        {
            "evidence_id": "manual_document_bad_metadata",
            "ref_type": "PDF",
            "metadata_is_dict": True,
            "metadata_keys": [
                "description",
                "portable",
                "parsed_by_mcp",
                "raw_text",
            ],
        },
        {
            "evidence_id": "manual_document_good_metadata",
            "ref_type": "PDF",
            "metadata_is_dict": True,
            "metadata_keys": ["description", "portable", "parsed_by_mcp"],
        },
    ]
    assert payload_guard_checks[
        "report_payload_optional_context_statuses_are_ok"
    ]["actual"] == {
        "multimodal_context": "conflict",
    }


def test_latest_signal_report_rejects_unexpected_pdf_metadata_key() -> None:
    document = create_document_evidence_card(
        summary="FOMC minutes summary says policy remains restrictive but stable.",
        artifact_ref="artifact://documents/fomc-minutes-summary.pdf",
        asset_scope=["QQQ", "TQQQ"],
    )
    document["evidence_card"]["artifact_ref"]["metadata"]["raw_text"] = (
        "raw file contents must not be embedded"
    )
    payload = generate_latest_signal_report(
        "TQQQ",
        extra_evidence_cards=[document["evidence_card"]],
    )
    context = payload["multimodal_context"]
    context_guard_checks = {
        check["name"]: check for check in context["guard"]["checks"]
    }
    payload_guard_checks = {
        check["name"]: check for check in payload["report_payload_guard"]["checks"]
    }

    assert context["status"] == "conflict"
    assert context_guard_checks[
        "multimodal_context_pdf_artifact_refs_match_pdf_contract"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_artifact_ref_metadata_matches_expected_schema"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_artifact_ref_metadata_matches_expected_schema"
    ]["actual"] == {
        "metadata_is_dict": [True],
        "metadata_keys_by_ref_type": {
            "PDF": ["description", "portable", "parsed_by_mcp", "raw_text"],
        },
    }
    assert context_guard_checks[
        "multimodal_context_artifact_ref_metadata_entries_match_expected_schema"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_artifact_ref_metadata_entries_match_expected_schema"
    ]["actual"] == [
        {
            "evidence_id": "manual_document_summary",
            "ref_type": "PDF",
            "metadata_is_dict": True,
            "metadata_keys": [
                "description",
                "portable",
                "parsed_by_mcp",
                "raw_text",
            ],
        },
    ]
    assert context_guard_checks[
        "multimodal_context_artifact_ref_metadata_values_are_safe"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_artifact_ref_metadata_value_types_are_strict"
    ]["passed"] is True
    assert payload_guard_checks[
        "report_payload_optional_context_statuses_are_ok"
    ]["actual"] == {
        "multimodal_context": "conflict",
    }


def test_latest_signal_report_rejects_missing_pdf_metadata_key() -> None:
    document = create_document_evidence_card(
        summary="FOMC minutes summary says policy remains restrictive but stable.",
        artifact_ref="artifact://documents/fomc-minutes-summary.pdf",
        asset_scope=["QQQ", "TQQQ"],
    )
    document["evidence_card"]["artifact_ref"]["metadata"].pop("parsed_by_mcp")
    payload = generate_latest_signal_report(
        "TQQQ",
        extra_evidence_cards=[document["evidence_card"]],
    )
    context = payload["multimodal_context"]
    context_guard_checks = {
        check["name"]: check for check in context["guard"]["checks"]
    }
    payload_guard_checks = {
        check["name"]: check for check in payload["report_payload_guard"]["checks"]
    }

    assert context["status"] == "conflict"
    assert context_guard_checks[
        "multimodal_context_artifact_ref_metadata_matches_expected_schema"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_artifact_ref_metadata_matches_expected_schema"
    ]["actual"] == {
        "metadata_is_dict": [True],
        "metadata_keys_by_ref_type": {
            "PDF": ["description", "portable"],
        },
    }
    assert context_guard_checks[
        "multimodal_context_artifact_ref_metadata_entries_match_expected_schema"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_artifact_ref_metadata_entries_match_expected_schema"
    ]["actual"] == [
        {
            "evidence_id": "manual_document_summary",
            "ref_type": "PDF",
            "metadata_is_dict": True,
            "metadata_keys": ["description", "portable"],
        },
    ]
    assert context_guard_checks[
        "multimodal_context_artifact_ref_metadata_values_are_safe"
    ]["actual"] == [
        {
            "evidence_id": "manual_document_summary",
            "ref_type": "PDF",
            "portable": True,
            "parsed_by_mcp": None,
            "description_nonempty": True,
        },
    ]
    assert context_guard_checks[
        "multimodal_context_artifact_ref_metadata_values_are_safe"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_artifact_ref_metadata_value_types_are_strict"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_artifact_ref_metadata_text_values_are_trimmed_and_control_free"
    ]["passed"] is True
    assert payload_guard_checks[
        "report_payload_optional_context_statuses_are_ok"
    ]["actual"] == {
        "multimodal_context": "conflict",
    }


def test_latest_signal_report_rejects_non_dict_pdf_artifact_ref_metadata() -> None:
    document = create_document_evidence_card(
        summary="FOMC minutes summary says policy remains restrictive but stable.",
        artifact_ref="artifact://documents/fomc-minutes-summary.pdf",
        asset_scope=["QQQ", "TQQQ"],
    )
    document["evidence_card"]["artifact_ref"]["metadata"] = []
    payload = generate_latest_signal_report(
        "TQQQ",
        extra_evidence_cards=[document["evidence_card"]],
    )
    context = payload["multimodal_context"]
    context_guard_checks = {
        check["name"]: check for check in context["guard"]["checks"]
    }
    payload_guard_checks = {
        check["name"]: check for check in payload["report_payload_guard"]["checks"]
    }

    assert context["status"] == "conflict"
    assert context_guard_checks[
        "multimodal_context_artifact_ref_metadata_matches_expected_schema"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_artifact_ref_metadata_matches_expected_schema"
    ]["expected"] == {
        "metadata_is_dict": True,
        "metadata_keys_by_ref_type": {
            "PDF": ["description", "portable", "parsed_by_mcp"],
        },
    }
    assert context_guard_checks[
        "multimodal_context_artifact_ref_metadata_matches_expected_schema"
    ]["actual"] == {
        "metadata_is_dict": [False],
        "metadata_keys_by_ref_type": {
            "PDF": [],
        },
    }
    assert context_guard_checks[
        "multimodal_context_artifact_ref_metadata_entries_match_expected_schema"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_artifact_ref_metadata_entries_match_expected_schema"
    ]["actual"] == [
        {
            "evidence_id": "manual_document_summary",
            "ref_type": "PDF",
            "metadata_is_dict": False,
            "metadata_keys": [],
        },
    ]
    assert context_guard_checks[
        "multimodal_context_artifact_ref_metadata_values_are_safe"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_artifact_ref_metadata_values_are_safe"
    ]["actual"] == [
        {
            "evidence_id": "manual_document_summary",
            "ref_type": "PDF",
            "portable": None,
            "parsed_by_mcp": None,
            "description_nonempty": False,
        },
    ]
    assert context_guard_checks[
        "multimodal_context_artifact_ref_metadata_value_types_are_strict"
    ]["passed"] is False
    assert payload_guard_checks[
        "report_payload_optional_context_statuses_are_ok"
    ]["actual"] == {
        "multimodal_context": "conflict",
    }


def test_latest_signal_report_rejects_pdf_metadata_description_with_control_character() -> None:
    document = create_document_evidence_card(
        summary="FOMC minutes summary says policy remains restrictive but stable.",
        artifact_ref="artifact://documents/fomc-minutes-summary.pdf",
        asset_scope=["QQQ", "TQQQ"],
    )
    document["evidence_card"]["artifact_ref"]["metadata"]["description"] = (
        "Caller-supplied document summary reference\n"
    )
    payload = generate_latest_signal_report(
        "TQQQ",
        extra_evidence_cards=[document["evidence_card"]],
    )
    context = payload["multimodal_context"]
    context_guard_checks = {
        check["name"]: check for check in context["guard"]["checks"]
    }
    payload_guard_checks = {
        check["name"]: check for check in payload["report_payload_guard"]["checks"]
    }

    assert context["status"] == "conflict"
    assert context_guard_checks[
        "multimodal_context_artifact_ref_metadata_matches_expected_schema"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_artifact_ref_metadata_entries_match_expected_schema"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_artifact_ref_metadata_values_are_safe"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_artifact_ref_metadata_text_values_are_trimmed_and_control_free"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_artifact_ref_metadata_text_values_are_trimmed_and_control_free"
    ]["actual"] == [
        {
            "evidence_id": "manual_document_summary",
            "ref_type": "PDF",
            "metadata_text_fields": ["description"],
            "metadata_text_values_have_no_surrounding_whitespace": False,
            "metadata_text_values_have_no_control_characters": False,
        },
    ]
    assert payload_guard_checks[
        "report_payload_optional_context_statuses_are_ok"
    ]["actual"] == {
        "multimodal_context": "conflict",
    }


def test_latest_signal_report_rejects_empty_pdf_metadata_description() -> None:
    document = create_document_evidence_card(
        summary="FOMC minutes summary says policy remains restrictive but stable.",
        artifact_ref="artifact://documents/fomc-minutes-summary.pdf",
        asset_scope=["QQQ", "TQQQ"],
    )
    document["evidence_card"]["artifact_ref"]["metadata"]["description"] = ""
    payload = generate_latest_signal_report(
        "TQQQ",
        extra_evidence_cards=[document["evidence_card"]],
    )
    context = payload["multimodal_context"]
    context_guard_checks = {
        check["name"]: check for check in context["guard"]["checks"]
    }
    payload_guard_checks = {
        check["name"]: check for check in payload["report_payload_guard"]["checks"]
    }
    metadata_values_actual = context_guard_checks[
        "multimodal_context_artifact_ref_metadata_values_are_safe"
    ]["actual"][0]

    assert context["status"] == "conflict"
    assert context_guard_checks[
        "multimodal_context_artifact_ref_metadata_matches_expected_schema"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_artifact_ref_metadata_entries_match_expected_schema"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_artifact_ref_metadata_values_are_safe"
    ]["passed"] is False
    assert metadata_values_actual == {
        "evidence_id": "manual_document_summary",
        "ref_type": "PDF",
        "portable": True,
        "parsed_by_mcp": False,
        "description_nonempty": False,
    }
    assert context_guard_checks[
        "multimodal_context_artifact_ref_metadata_value_types_are_strict"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_artifact_ref_metadata_text_values_are_trimmed_and_control_free"
    ]["passed"] is True
    assert payload_guard_checks[
        "report_payload_optional_context_statuses_are_ok"
    ]["actual"] == {
        "multimodal_context": "conflict",
    }


def test_latest_signal_report_rejects_unsafe_pdf_metadata_bool_values() -> None:
    document = create_document_evidence_card(
        summary="FOMC minutes summary says policy remains restrictive but stable.",
        artifact_ref="artifact://documents/fomc-minutes-summary.pdf",
        asset_scope=["QQQ", "TQQQ"],
    )
    metadata = document["evidence_card"]["artifact_ref"]["metadata"]
    metadata["portable"] = False
    metadata["parsed_by_mcp"] = True
    payload = generate_latest_signal_report(
        "TQQQ",
        extra_evidence_cards=[document["evidence_card"]],
    )
    context = payload["multimodal_context"]
    context_guard_checks = {
        check["name"]: check for check in context["guard"]["checks"]
    }
    payload_guard_checks = {
        check["name"]: check for check in payload["report_payload_guard"]["checks"]
    }
    metadata_values_actual = context_guard_checks[
        "multimodal_context_artifact_ref_metadata_values_are_safe"
    ]["actual"][0]

    assert context["status"] == "conflict"
    assert context_guard_checks[
        "multimodal_context_artifact_ref_metadata_matches_expected_schema"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_artifact_ref_metadata_entries_match_expected_schema"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_artifact_ref_metadata_values_are_safe"
    ]["passed"] is False
    assert metadata_values_actual == {
        "evidence_id": "manual_document_summary",
        "ref_type": "PDF",
        "portable": False,
        "parsed_by_mcp": True,
        "description_nonempty": True,
    }
    assert context_guard_checks[
        "multimodal_context_artifact_ref_metadata_value_types_are_strict"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_artifact_ref_metadata_text_values_are_trimmed_and_control_free"
    ]["passed"] is True
    assert payload_guard_checks[
        "report_payload_optional_context_statuses_are_ok"
    ]["actual"] == {
        "multimodal_context": "conflict",
    }


def test_latest_signal_report_rejects_pdf_metadata_non_bool_flags() -> None:
    document = create_document_evidence_card(
        summary="FOMC minutes summary says policy remains restrictive but stable.",
        artifact_ref="artifact://documents/fomc-minutes-summary.pdf",
        asset_scope=["QQQ", "TQQQ"],
    )
    metadata = document["evidence_card"]["artifact_ref"]["metadata"]
    metadata["portable"] = 1
    metadata["parsed_by_mcp"] = 0
    payload = generate_latest_signal_report(
        "TQQQ",
        extra_evidence_cards=[document["evidence_card"]],
    )
    context = payload["multimodal_context"]
    context_guard_checks = {
        check["name"]: check for check in context["guard"]["checks"]
    }
    payload_guard_checks = {
        check["name"]: check for check in payload["report_payload_guard"]["checks"]
    }

    assert context["status"] == "conflict"
    assert context_guard_checks[
        "multimodal_context_artifact_ref_metadata_values_are_safe"
    ]["passed"] is True
    metadata_values_actual = context_guard_checks[
        "multimodal_context_artifact_ref_metadata_values_are_safe"
    ]["actual"][0]
    assert metadata_values_actual["portable"] is not True
    assert metadata_values_actual["parsed_by_mcp"] is not False
    assert context_guard_checks[
        "multimodal_context_artifact_ref_metadata_value_types_are_strict"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_artifact_ref_metadata_value_types_are_strict"
    ]["expected"] == [
        expected_document_pdf_artifact_ref_metadata_value_types(
            document["evidence_card"]
        ),
    ]
    assert context_guard_checks[
        "multimodal_context_artifact_ref_metadata_value_types_are_strict"
    ]["actual"] == [
        {
            "evidence_id": "manual_document_summary",
            "ref_type": "PDF",
            "description_is_string": True,
            "portable_is_bool_true": False,
            "parsed_by_mcp_is_bool_false": False,
        },
    ]
    assert context_guard_checks[
        "multimodal_context_artifact_ref_metadata_text_values_are_trimmed_and_control_free"
    ]["passed"] is True
    assert payload_guard_checks[
        "report_payload_optional_context_statuses_are_ok"
    ]["actual"] == {
        "multimodal_context": "conflict",
    }


def test_latest_signal_report_rejects_duplicate_document_artifact_ref_values() -> None:
    first_document = create_document_evidence_card(
        summary="FOMC minutes summary says policy remains restrictive but stable.",
        artifact_ref="artifact://documents/fomc-minutes-summary.pdf",
        evidence_id="manual_document_primary",
        asset_scope=["QQQ", "TQQQ"],
    )
    second_document = create_document_evidence_card(
        summary="FOMC minutes summary says policy remains restrictive and stable.",
        artifact_ref="artifact://documents/fomc-minutes-summary.pdf",
        evidence_id="manual_document_secondary",
        asset_scope=["QQQ", "TQQQ"],
    )
    payload = generate_latest_signal_report(
        "TQQQ",
        extra_evidence_cards=[
            first_document["evidence_card"],
            second_document["evidence_card"],
        ],
    )
    context = payload["multimodal_context"]
    context_guard_checks = {
        check["name"]: check for check in context["guard"]["checks"]
    }
    payload_guard_checks = {
        check["name"]: check for check in payload["report_payload_guard"]["checks"]
    }

    assert context["status"] == "conflict"
    assert context_guard_checks[
        "multimodal_context_evidence_card_ids_are_unique"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_artifact_ref_evidence_ids_are_unique"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_artifact_ref_evidence_ids_match_safe_contract"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_artifact_refs_match_expected_context"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_artifact_ref_values_are_unique"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_artifact_ref_values_are_unique"
    ]["actual"] == {
        "refs": [
            "artifact://documents/fomc-minutes-summary.pdf",
            "artifact://documents/fomc-minutes-summary.pdf",
        ],
        "nonempty": True,
        "unique": False,
    }
    assert payload_guard_checks[
        "report_payload_optional_context_statuses_are_ok"
    ]["actual"] == {
        "multimodal_context": "conflict",
    }


def test_latest_signal_report_rejects_duplicate_document_evidence_ids() -> None:
    first_document = create_document_evidence_card(
        summary="FOMC minutes summary says policy remains restrictive but stable.",
        artifact_ref="artifact://documents/fomc-minutes-summary.pdf",
        evidence_id="manual_document_summary",
        asset_scope=["QQQ", "TQQQ"],
    )
    second_document = create_document_evidence_card(
        summary="Treasury refunding summary says duration supply is stable.",
        artifact_ref="artifact://documents/treasury-refunding-summary.pdf",
        evidence_id="manual_document_summary",
        asset_scope=["QQQ", "TQQQ"],
    )
    payload = generate_latest_signal_report(
        "TQQQ",
        extra_evidence_cards=[
            first_document["evidence_card"],
            second_document["evidence_card"],
        ],
    )
    context = payload["multimodal_context"]
    context_guard_checks = {
        check["name"]: check for check in context["guard"]["checks"]
    }
    payload_guard_checks = {
        check["name"]: check for check in payload["report_payload_guard"]["checks"]
    }

    assert context["status"] == "conflict"
    assert context_guard_checks[
        "multimodal_context_evidence_card_ids_are_unique"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_evidence_card_ids_are_unique"
    ]["actual"] == {
        "ids": ["manual_document_summary", "manual_document_summary"],
        "nonempty": True,
        "unique": False,
    }
    assert context_guard_checks[
        "multimodal_context_artifact_ref_evidence_ids_are_unique"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_artifact_ref_evidence_ids_are_unique"
    ]["actual"] == {
        "ids": ["manual_document_summary", "manual_document_summary"],
        "nonempty": True,
        "unique": False,
    }
    assert context_guard_checks[
        "multimodal_context_evidence_card_ids_do_not_use_reserved_ids"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_artifact_ref_values_are_unique"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_artifact_refs_match_expected_context"
    ]["passed"] is True
    assert payload_guard_checks[
        "report_payload_optional_context_statuses_are_ok"
    ]["actual"] == {
        "multimodal_context": "conflict",
    }


def test_latest_signal_report_rejects_reserved_chart_evidence_id_collision(
    tmp_path: Path,
) -> None:
    document = create_document_evidence_card(
        summary="FOMC minutes summary says policy remains restrictive but stable.",
        artifact_ref="artifact://documents/fomc-minutes-summary.pdf",
        evidence_id="latest_signal_chart",
        asset_scope=["QQQ", "TQQQ"],
    )
    payload = generate_latest_signal_report(
        "TQQQ",
        include_chart=True,
        chart_output_dir=str(tmp_path),
        extra_evidence_cards=[document["evidence_card"]],
    )
    context = payload["multimodal_context"]
    context_guard_checks = {
        check["name"]: check for check in context["guard"]["checks"]
    }
    payload_guard_checks = {
        check["name"]: check for check in payload["report_payload_guard"]["checks"]
    }

    assert payload["chart_code_guard"]["status"] == "ok"
    assert context["status"] == "conflict"
    assert context_guard_checks[
        "multimodal_context_evidence_card_ids_are_unique"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_evidence_card_ids_do_not_use_reserved_ids"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_evidence_card_ids_do_not_use_reserved_ids"
    ]["actual"] == {
        "reserved_ids": ["latest_signal_chart"],
        "uses_reserved_id": True,
    }
    assert context_guard_checks[
        "multimodal_context_artifact_ref_evidence_ids_are_unique"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_artifact_ref_evidence_ids_are_unique"
    ]["actual"] == {
        "ids": ["latest_signal_chart", "latest_signal_chart"],
        "nonempty": True,
        "unique": False,
    }
    assert payload_guard_checks[
        "report_payload_optional_context_statuses_are_ok"
    ]["actual"] == {
        "chart_code_guard": "ok",
        "multimodal_context": "conflict",
    }
    assert payload_guard_checks[
        "report_payload_optional_context_guards_are_ok"
    ]["actual"] == {
        "chart_code_guard": "ok",
        "multimodal_context.guard": "conflict",
    }


def test_latest_signal_report_rejects_reserved_document_evidence_id_without_chart() -> None:
    document = create_document_evidence_card(
        summary="FOMC minutes summary says policy remains restrictive but stable.",
        artifact_ref="artifact://documents/fomc-minutes-summary.pdf",
        evidence_id="latest_signal_chart",
        asset_scope=["QQQ", "TQQQ"],
    )
    payload = generate_latest_signal_report(
        "TQQQ",
        extra_evidence_cards=[document["evidence_card"]],
    )
    context = payload["multimodal_context"]
    context_guard_checks = {
        check["name"]: check for check in context["guard"]["checks"]
    }
    payload_guard_checks = {
        check["name"]: check for check in payload["report_payload_guard"]["checks"]
    }

    assert "chart_code_guard" not in payload
    assert context["status"] == "conflict"
    assert context_guard_checks[
        "multimodal_context_evidence_card_ids_are_unique"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_evidence_card_ids_do_not_use_reserved_ids"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_evidence_card_ids_do_not_use_reserved_ids"
    ]["actual"] == {
        "reserved_ids": ["latest_signal_chart"],
        "uses_reserved_id": True,
    }
    assert context_guard_checks[
        "multimodal_context_artifact_ref_evidence_ids_are_unique"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_artifact_ref_evidence_ids_are_unique"
    ]["actual"] == {
        "ids": ["latest_signal_chart"],
        "nonempty": True,
        "unique": True,
    }
    assert payload_guard_checks[
        "report_payload_optional_context_statuses_are_ok"
    ]["actual"] == {
        "multimodal_context": "conflict",
    }
    assert payload_guard_checks[
        "report_payload_optional_context_guards_are_ok"
    ]["actual"] == {
        "multimodal_context.guard": "conflict",
    }


def test_latest_signal_report_rejects_unsafe_document_evidence_id() -> None:
    document = create_document_evidence_card(
        summary="FOMC minutes summary says policy remains restrictive but stable.",
        artifact_ref="artifact://documents/fomc-minutes-summary.pdf",
        evidence_id="manual document summary",
        asset_scope=["QQQ", "TQQQ"],
    )
    payload = generate_latest_signal_report(
        "TQQQ",
        extra_evidence_cards=[document["evidence_card"]],
    )
    context = payload["multimodal_context"]
    context_guard_checks = {
        check["name"]: check for check in context["guard"]["checks"]
    }
    payload_guard_checks = {
        check["name"]: check for check in payload["report_payload_guard"]["checks"]
    }

    assert context["status"] == "conflict"
    assert context_guard_checks[
        "multimodal_context_evidence_card_ids_are_unique"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_evidence_card_ids_do_not_use_reserved_ids"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_artifact_ref_evidence_ids_are_unique"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_evidence_card_ids_match_safe_contract"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_artifact_ref_evidence_ids_match_safe_contract"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_evidence_card_ids_match_safe_contract"
    ]["actual"] == [
        {
            "evidence_id": "manual document summary",
            "pattern": "lowercase_ascii_underscore_identifier",
            "min_chars": 3,
            "max_chars": 64,
            "matches_safe_contract": False,
        },
    ]
    assert context_guard_checks[
        "multimodal_context_artifact_ref_evidence_ids_match_safe_contract"
    ]["actual"] == [
        {
            "evidence_id": "manual document summary",
            "pattern": "lowercase_ascii_underscore_identifier",
            "min_chars": 3,
            "max_chars": 64,
            "matches_safe_contract": False,
        },
    ]
    assert payload_guard_checks[
        "report_payload_optional_context_statuses_are_ok"
    ]["actual"] == {
        "multimodal_context": "conflict",
    }


def test_latest_signal_report_rejects_non_string_document_evidence_id() -> None:
    document = create_document_evidence_card(
        summary="FOMC minutes summary says policy remains restrictive but stable.",
        artifact_ref="artifact://documents/fomc-minutes-summary.pdf",
        evidence_id="manual_document_summary",
        asset_scope=["QQQ", "TQQQ"],
    )
    document["evidence_card"]["evidence_id"] = 123
    payload = generate_latest_signal_report(
        "TQQQ",
        extra_evidence_cards=[document["evidence_card"]],
    )
    context = payload["multimodal_context"]
    context_guard_checks = {
        check["name"]: check for check in context["guard"]["checks"]
    }
    payload_guard_checks = {
        check["name"]: check for check in payload["report_payload_guard"]["checks"]
    }

    assert context["status"] == "conflict"
    assert context_guard_checks[
        "multimodal_context_evidence_card_ids_are_unique"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_evidence_card_ids_do_not_use_reserved_ids"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_evidence_ids_are_string_typed"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_evidence_card_ids_match_safe_contract"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_artifact_ref_evidence_ids_match_safe_contract"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_evidence_ids_are_string_typed"
    ]["expected"] == expected_multimodal_evidence_id_types(
        ["123"],
        ["123"],
    )
    assert context_guard_checks[
        "multimodal_context_evidence_ids_are_string_typed"
    ]["actual"] == {
        "evidence_card_ids": [123],
        "artifact_ref_evidence_ids": ["123"],
        "evidence_card_ids_are_strings": False,
        "artifact_ref_evidence_ids_are_strings": True,
    }
    assert context_guard_checks[
        "multimodal_context_evidence_card_ids_match_safe_contract"
    ]["actual"] == [
        {
            "evidence_id": "123",
            "pattern": "lowercase_ascii_underscore_identifier",
            "min_chars": 3,
            "max_chars": 64,
            "matches_safe_contract": False,
        },
    ]
    assert context_guard_checks[
        "multimodal_context_artifact_ref_evidence_ids_match_safe_contract"
    ]["actual"] == [
        {
            "evidence_id": "123",
            "pattern": "lowercase_ascii_underscore_identifier",
            "min_chars": 3,
            "max_chars": 64,
            "matches_safe_contract": False,
        },
    ]
    assert payload_guard_checks[
        "report_payload_optional_context_statuses_are_ok"
    ]["actual"] == {
        "multimodal_context": "conflict",
    }


def test_latest_signal_report_rejects_unknown_document_evidence_bias() -> None:
    document = create_document_evidence_card(
        summary="FOMC minutes summary says policy remains restrictive but stable.",
        artifact_ref="artifact://documents/fomc-minutes-summary.pdf",
        bias="moonshot",
        asset_scope=["QQQ", "TQQQ"],
    )
    payload = generate_latest_signal_report(
        "TQQQ",
        extra_evidence_cards=[document["evidence_card"]],
    )
    context = payload["multimodal_context"]
    context_guard_checks = {
        check["name"]: check for check in context["guard"]["checks"]
    }
    payload_guard_checks = {
        check["name"]: check for check in payload["report_payload_guard"]["checks"]
    }

    assert context["status"] == "conflict"
    assert context_guard_checks[
        "multimodal_context_evidence_card_categorical_values_are_safe"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_evidence_card_categorical_values_are_safe"
    ]["actual"] == [
        {
            "evidence_id": "manual_document_summary",
            "category": "manual_document",
            "source": "manual:document_summary",
            "bias_in_allowed_set": False,
        },
    ]
    assert payload_guard_checks[
        "report_payload_optional_context_statuses_are_ok"
    ]["actual"] == {
        "multimodal_context": "conflict",
    }


def test_latest_signal_report_rejects_non_string_document_evidence_bias() -> None:
    document = create_document_evidence_card(
        summary="FOMC minutes summary says policy remains restrictive but stable.",
        artifact_ref="artifact://documents/fomc-minutes-summary.pdf",
        asset_scope=["QQQ", "TQQQ"],
    )
    document["evidence_card"]["bias"] = 123
    payload = generate_latest_signal_report(
        "TQQQ",
        extra_evidence_cards=[document["evidence_card"]],
    )
    context = payload["multimodal_context"]
    context_guard_checks = {
        check["name"]: check for check in context["guard"]["checks"]
    }
    payload_guard_checks = {
        check["name"]: check for check in payload["report_payload_guard"]["checks"]
    }

    assert context["status"] == "conflict"
    assert context_guard_checks[
        "multimodal_context_evidence_card_values_are_safe"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_evidence_card_string_field_types_are_strict"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_evidence_card_string_field_types_are_strict"
    ]["actual"] == [
        {
            **expected_document_evidence_card_string_field_types(
                document["evidence_card"]
            ),
            "string_fields_are_strings": False,
        },
    ]
    assert context_guard_checks[
        "multimodal_context_evidence_card_categorical_values_are_safe"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_evidence_card_categorical_values_are_safe"
    ]["actual"] == [
        {
            "evidence_id": "manual_document_summary",
            "category": "manual_document",
            "source": "manual:document_summary",
            "bias_in_allowed_set": False,
        },
    ]
    assert payload_guard_checks[
        "report_payload_optional_context_statuses_are_ok"
    ]["actual"] == {
        "multimodal_context": "conflict",
    }


def test_latest_signal_report_rejects_empty_document_evidence_bias() -> None:
    document = create_document_evidence_card(
        summary="FOMC minutes summary says policy remains restrictive but stable.",
        artifact_ref="artifact://documents/fomc-minutes-summary.pdf",
        asset_scope=["QQQ", "TQQQ"],
    )
    document["evidence_card"]["bias"] = ""
    payload = generate_latest_signal_report(
        "TQQQ",
        extra_evidence_cards=[document["evidence_card"]],
    )
    context = payload["multimodal_context"]
    context_guard_checks = {
        check["name"]: check for check in context["guard"]["checks"]
    }
    payload_guard_checks = {
        check["name"]: check for check in payload["report_payload_guard"]["checks"]
    }

    assert context["status"] == "conflict"
    assert context_guard_checks[
        "multimodal_context_evidence_card_values_are_safe"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_evidence_card_string_field_types_are_strict"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_evidence_card_categorical_values_are_safe"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_evidence_card_categorical_values_are_safe"
    ]["actual"] == [
        {
            "evidence_id": "manual_document_summary",
            "category": "manual_document",
            "source": "manual:document_summary",
            "bias_in_allowed_set": False,
        },
    ]
    assert payload_guard_checks[
        "report_payload_optional_context_statuses_are_ok"
    ]["actual"] == {
        "multimodal_context": "conflict",
    }


def test_latest_signal_report_rejects_non_string_document_category_source() -> None:
    document = create_document_evidence_card(
        summary="FOMC minutes summary says policy remains restrictive but stable.",
        artifact_ref="artifact://documents/fomc-minutes-summary.pdf",
        asset_scope=["QQQ", "TQQQ"],
    )
    document["evidence_card"]["category"] = 123
    document["evidence_card"]["source"] = 456
    payload = generate_latest_signal_report(
        "TQQQ",
        extra_evidence_cards=[document["evidence_card"]],
    )
    context = payload["multimodal_context"]
    context_guard_checks = {
        check["name"]: check for check in context["guard"]["checks"]
    }
    payload_guard_checks = {
        check["name"]: check for check in payload["report_payload_guard"]["checks"]
    }

    assert context["status"] == "conflict"
    assert context_guard_checks[
        "multimodal_context_evidence_card_values_are_safe"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_evidence_card_string_field_types_are_strict"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_evidence_card_string_field_types_are_strict"
    ]["actual"] == [
        {
            **expected_document_evidence_card_string_field_types(
                document["evidence_card"]
            ),
            "string_fields_are_strings": False,
        },
    ]
    assert context_guard_checks[
        "multimodal_context_evidence_card_categorical_values_are_safe"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_evidence_card_categorical_values_are_safe"
    ]["actual"] == [
        {
            **expected_document_evidence_card_categorical_values(
                document["evidence_card"]
            ),
            "category": 123,
            "source": 456,
        },
    ]
    assert payload_guard_checks[
        "report_payload_optional_context_statuses_are_ok"
    ]["actual"] == {
        "multimodal_context": "conflict",
    }


def test_latest_signal_report_rejects_empty_document_category_source() -> None:
    document = create_document_evidence_card(
        summary="FOMC minutes summary says policy remains restrictive but stable.",
        artifact_ref="artifact://documents/fomc-minutes-summary.pdf",
        asset_scope=["QQQ", "TQQQ"],
    )
    document["evidence_card"]["category"] = ""
    document["evidence_card"]["source"] = ""
    payload = generate_latest_signal_report(
        "TQQQ",
        extra_evidence_cards=[document["evidence_card"]],
    )
    context = payload["multimodal_context"]
    context_guard_checks = {
        check["name"]: check for check in context["guard"]["checks"]
    }
    payload_guard_checks = {
        check["name"]: check for check in payload["report_payload_guard"]["checks"]
    }

    assert context["status"] == "conflict"
    assert context_guard_checks[
        "multimodal_context_evidence_card_values_are_safe"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_evidence_card_string_field_types_are_strict"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_evidence_card_categorical_values_are_safe"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_evidence_card_categorical_values_are_safe"
    ]["actual"] == [
        {
            **expected_document_evidence_card_categorical_values(
                document["evidence_card"]
            ),
            "category": "",
            "source": "",
        },
    ]
    assert payload_guard_checks[
        "report_payload_optional_context_statuses_are_ok"
    ]["actual"] == {
        "multimodal_context": "conflict",
    }


def test_latest_signal_report_rejects_missing_document_source_key() -> None:
    document = create_document_evidence_card(
        summary="FOMC minutes summary says policy remains restrictive but stable.",
        artifact_ref="artifact://documents/fomc-minutes-summary.pdf",
        asset_scope=["QQQ", "TQQQ"],
    )
    document["evidence_card"].pop("source")
    payload = generate_latest_signal_report(
        "TQQQ",
        extra_evidence_cards=[document["evidence_card"]],
    )
    context = payload["multimodal_context"]
    context_guard_checks = {
        check["name"]: check for check in context["guard"]["checks"]
    }
    payload_guard_checks = {
        check["name"]: check for check in payload["report_payload_guard"]["checks"]
    }
    actual_card_keys = [
        key for key in EXPECTED_DOCUMENT_EVIDENCE_CARD_KEYS if key != "source"
    ]

    assert context["status"] == "conflict"
    assert context_guard_checks[
        "multimodal_context_evidence_cards_match_expected_schema"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_evidence_cards_match_expected_schema"
    ]["expected"] == EXPECTED_DOCUMENT_EVIDENCE_CARD_KEYS
    assert context_guard_checks[
        "multimodal_context_evidence_cards_match_expected_schema"
    ]["actual"] == [actual_card_keys]
    assert context_guard_checks[
        "multimodal_context_evidence_card_string_field_types_are_strict"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_evidence_card_string_field_types_are_strict"
    ]["actual"] == [
        {
            **expected_document_evidence_card_string_field_types(
                document["evidence_card"]
            ),
            "string_fields_are_strings": False,
        },
    ]
    assert context_guard_checks[
        "multimodal_context_evidence_card_categorical_values_are_safe"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_evidence_card_categorical_values_are_safe"
    ]["actual"] == [
        {
            **expected_document_evidence_card_categorical_values(
                document["evidence_card"]
            ),
            "source": None,
        },
    ]
    assert payload_guard_checks[
        "report_payload_optional_context_statuses_are_ok"
    ]["actual"] == {
        "multimodal_context": "conflict",
    }


def test_latest_signal_report_rejects_unexpected_document_card_key() -> None:
    document = create_document_evidence_card(
        summary="FOMC minutes summary says policy remains restrictive but stable.",
        artifact_ref="artifact://documents/fomc-minutes-summary.pdf",
        asset_scope=["QQQ", "TQQQ"],
    )
    document["evidence_card"]["raw_text"] = "Unbounded source text must not leak."
    payload = generate_latest_signal_report(
        "TQQQ",
        extra_evidence_cards=[document["evidence_card"]],
    )
    context = payload["multimodal_context"]
    context_guard_checks = {
        check["name"]: check for check in context["guard"]["checks"]
    }
    payload_guard_checks = {
        check["name"]: check for check in payload["report_payload_guard"]["checks"]
    }
    actual_card_keys = [*EXPECTED_DOCUMENT_EVIDENCE_CARD_KEYS, "raw_text"]

    assert context["status"] == "conflict"
    assert context_guard_checks[
        "multimodal_context_evidence_cards_match_expected_schema"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_evidence_cards_match_expected_schema"
    ]["expected"] == EXPECTED_DOCUMENT_EVIDENCE_CARD_KEYS
    assert context_guard_checks[
        "multimodal_context_evidence_cards_match_expected_schema"
    ]["actual"] == [actual_card_keys]
    assert context_guard_checks[
        "multimodal_context_evidence_card_values_are_safe"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_evidence_card_string_field_types_are_strict"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_evidence_card_structural_field_types_are_strict"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_evidence_card_categorical_values_are_safe"
    ]["passed"] is True
    assert payload_guard_checks[
        "report_payload_optional_context_statuses_are_ok"
    ]["actual"] == {
        "multimodal_context": "conflict",
    }


def test_latest_signal_report_rejects_unsupported_document_evidence_modality() -> None:
    document = create_document_evidence_card(
        summary="FOMC minutes summary says policy remains restrictive but stable.",
        artifact_ref="artifact://documents/fomc-minutes-summary.pdf",
        modality="raw_pdf",
        asset_scope=["QQQ", "TQQQ"],
    )
    payload = generate_latest_signal_report(
        "TQQQ",
        extra_evidence_cards=[document["evidence_card"]],
    )
    context = payload["multimodal_context"]
    context_guard_checks = {
        check["name"]: check for check in context["guard"]["checks"]
    }
    payload_guard_checks = {
        check["name"]: check for check in payload["report_payload_guard"]["checks"]
    }

    assert context["status"] == "conflict"
    assert context_guard_checks[
        "multimodal_context_modality_counts_match_expected_context"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_evidence_card_values_are_safe"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_evidence_card_modality_values_are_supported"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_evidence_card_modality_values_are_supported"
    ]["actual"] == [
        {
            "evidence_id": "manual_document_summary",
            "modality": "raw_pdf",
            "modality_supported": False,
        },
    ]
    assert payload_guard_checks[
        "report_payload_optional_context_statuses_are_ok"
    ]["actual"] == {
        "multimodal_context": "conflict",
    }


def test_latest_signal_report_rejects_non_string_document_modality() -> None:
    document = create_document_evidence_card(
        summary="FOMC minutes summary says policy remains restrictive but stable.",
        artifact_ref="artifact://documents/fomc-minutes-summary.pdf",
        asset_scope=["QQQ", "TQQQ"],
    )
    document["evidence_card"]["modality"] = 123
    payload = generate_latest_signal_report(
        "TQQQ",
        extra_evidence_cards=[document["evidence_card"]],
    )
    context = payload["multimodal_context"]
    context_guard_checks = {
        check["name"]: check for check in context["guard"]["checks"]
    }
    payload_guard_checks = {
        check["name"]: check for check in payload["report_payload_guard"]["checks"]
    }

    assert context["status"] == "conflict"
    assert context_guard_checks[
        "multimodal_context_evidence_card_values_are_safe"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_evidence_card_scalar_values_are_trimmed_and_control_free"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_evidence_card_string_field_types_are_strict"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_evidence_card_string_field_types_are_strict"
    ]["actual"] == [
        {
            **expected_document_evidence_card_string_field_types(
                document["evidence_card"]
            ),
            "string_fields_are_strings": False,
        },
    ]
    assert context_guard_checks[
        "multimodal_context_evidence_card_modality_values_are_supported"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_evidence_card_modality_values_are_supported"
    ]["actual"] == [
        {
            "evidence_id": "manual_document_summary",
            "modality": "123",
            "modality_supported": False,
        },
    ]
    assert payload_guard_checks[
        "report_payload_optional_context_statuses_are_ok"
    ]["actual"] == {
        "multimodal_context": "conflict",
    }


def test_latest_signal_report_rejects_empty_document_modality() -> None:
    document = create_document_evidence_card(
        summary="FOMC minutes summary says policy remains restrictive but stable.",
        artifact_ref="artifact://documents/fomc-minutes-summary.pdf",
        asset_scope=["QQQ", "TQQQ"],
    )
    document["evidence_card"]["modality"] = ""
    payload = generate_latest_signal_report(
        "TQQQ",
        extra_evidence_cards=[document["evidence_card"]],
    )
    context = payload["multimodal_context"]
    context_guard_checks = {
        check["name"]: check for check in context["guard"]["checks"]
    }
    payload_guard_checks = {
        check["name"]: check for check in payload["report_payload_guard"]["checks"]
    }

    assert context["status"] == "conflict"
    assert context_guard_checks["extra_cards_have_modality"]["passed"] is False
    assert context_guard_checks["extra_cards_have_modality"]["actual"] == [""]
    assert context_guard_checks[
        "multimodal_context_modality_counts_match_expected_context"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_evidence_card_string_field_types_are_strict"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_evidence_card_scalar_values_are_trimmed_and_control_free"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_evidence_card_values_are_safe"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_evidence_card_values_are_safe"
    ]["actual"] == [
        {
            **expected_document_evidence_card_values(document["evidence_card"]),
            "modality_nonempty": False,
        },
    ]
    assert context_guard_checks[
        "multimodal_context_evidence_card_modality_values_are_supported"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_evidence_card_modality_values_are_supported"
    ]["actual"] == [
        {
            "evidence_id": "manual_document_summary",
            "modality": "",
            "modality_supported": False,
        },
    ]
    assert payload_guard_checks[
        "report_payload_optional_context_statuses_are_ok"
    ]["actual"] == {
        "multimodal_context": "conflict",
    }


def test_latest_signal_report_rejects_document_modality_with_surrounding_whitespace() -> None:
    document = create_document_evidence_card(
        summary="FOMC minutes summary says policy remains restrictive but stable.",
        artifact_ref="artifact://documents/fomc-minutes-summary.pdf",
        asset_scope=["QQQ", "TQQQ"],
    )
    document["evidence_card"]["modality"] = "pdf_summary "
    payload = generate_latest_signal_report(
        "TQQQ",
        extra_evidence_cards=[document["evidence_card"]],
    )
    context = payload["multimodal_context"]
    context_guard_checks = {
        check["name"]: check for check in context["guard"]["checks"]
    }
    payload_guard_checks = {
        check["name"]: check for check in payload["report_payload_guard"]["checks"]
    }

    assert context["status"] == "conflict"
    assert context_guard_checks[
        "multimodal_context_modality_counts_match_expected_context"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_evidence_card_values_are_safe"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_evidence_card_modality_values_are_supported"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_evidence_card_scalar_values_are_trimmed_and_control_free"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_evidence_card_scalar_values_are_trimmed_and_control_free"
    ]["actual"] == [
        {
            "evidence_id": "manual_document_summary",
            "scalar_fields": ["modality", "observed_at"],
            "scalar_values_have_no_surrounding_whitespace": False,
            "scalar_values_have_no_control_characters": True,
        },
    ]
    assert payload_guard_checks[
        "report_payload_optional_context_statuses_are_ok"
    ]["actual"] == {
        "multimodal_context": "conflict",
    }


def test_latest_signal_report_rejects_relative_document_artifact_ref() -> None:
    document = create_document_evidence_card(
        summary="FOMC minutes summary says policy remains restrictive but stable.",
        artifact_ref="documents/fomc-minutes-summary.pdf",
        asset_scope=["QQQ", "TQQQ"],
    )
    payload = generate_latest_signal_report(
        "TQQQ",
        extra_evidence_cards=[document["evidence_card"]],
    )
    context = payload["multimodal_context"]
    context_guard_checks = {
        check["name"]: check for check in context["guard"]["checks"]
    }
    payload_guard_checks = {
        check["name"]: check for check in payload["report_payload_guard"]["checks"]
    }

    assert context["status"] == "conflict"
    assert context_guard_checks[
        "multimodal_context_evidence_card_values_are_safe"
    ]["passed"] is True
    assert context_guard_checks["non_chart_artifact_refs_are_portable"][
        "passed"
    ] is True
    assert context_guard_checks[
        "multimodal_context_evidence_card_artifact_refs_use_explicit_uris"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_evidence_card_artifact_refs_use_explicit_uris"
    ]["actual"] == [
        {
            "evidence_id": "manual_document_summary",
            "allowed_ref_prefixes": [
                "artifact://",
                "https://",
                "memory://",
                "urn:",
                "sha256:",
            ],
            "artifact_ref_uses_explicit_uri": False,
        },
    ]
    assert payload_guard_checks[
        "report_payload_optional_context_statuses_are_ok"
    ]["actual"] == {
        "multimodal_context": "conflict",
    }


def test_latest_signal_report_rejects_raw_length_document_summary() -> None:
    document = create_document_evidence_card(
        summary="FOMC minutes summary says policy remains restrictive but stable.",
        artifact_ref="artifact://documents/fomc-minutes-summary.pdf",
        asset_scope=["QQQ", "TQQQ"],
    )
    document["evidence_card"]["summary"] = "x" * (DOCUMENT_SUMMARY_MAX_CHARS + 1)
    document["evidence_card"]["summary_truncated"] = False
    payload = generate_latest_signal_report(
        "TQQQ",
        extra_evidence_cards=[document["evidence_card"]],
    )
    context = payload["multimodal_context"]
    context_guard_checks = {
        check["name"]: check for check in context["guard"]["checks"]
    }
    payload_guard_checks = {
        check["name"]: check for check in payload["report_payload_guard"]["checks"]
    }

    assert context["status"] == "conflict"
    assert context_guard_checks[
        "multimodal_context_evidence_card_summary_bounds_are_safe"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_evidence_card_summary_bounds_are_safe"
    ]["actual"] == [
        {
            "evidence_id": "manual_document_summary",
            "summary_max_chars": DOCUMENT_SUMMARY_MAX_CHARS,
            "summary_within_limit": False,
        },
    ]
    assert payload_guard_checks[
        "report_payload_optional_context_statuses_are_ok"
    ]["actual"] == {
        "multimodal_context": "conflict",
    }


def test_latest_signal_report_rejects_empty_document_summary() -> None:
    document = create_document_evidence_card(
        summary="FOMC minutes summary says policy remains restrictive but stable.",
        artifact_ref="artifact://documents/fomc-minutes-summary.pdf",
        asset_scope=["QQQ", "TQQQ"],
    )
    document["evidence_card"]["summary"] = ""
    document["evidence_card"]["summary_truncated"] = False
    payload = generate_latest_signal_report(
        "TQQQ",
        extra_evidence_cards=[document["evidence_card"]],
    )
    context = payload["multimodal_context"]
    context_guard_checks = {
        check["name"]: check for check in context["guard"]["checks"]
    }
    payload_guard_checks = {
        check["name"]: check for check in payload["report_payload_guard"]["checks"]
    }

    assert context["status"] == "conflict"
    assert context_guard_checks["extra_cards_have_summary"]["passed"] is False
    assert context_guard_checks["extra_cards_have_summary"]["actual"] == [False]
    assert context_guard_checks[
        "multimodal_context_evidence_card_string_field_types_are_strict"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_evidence_card_text_values_are_trimmed_and_control_free"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_evidence_card_summary_bounds_are_safe"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_evidence_card_summary_truncation_flags_are_consistent"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_evidence_card_values_are_safe"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_evidence_card_values_are_safe"
    ]["actual"] == [
        {
            **expected_document_evidence_card_values(document["evidence_card"]),
            "summary_nonempty": False,
        },
    ]
    assert payload_guard_checks[
        "report_payload_optional_context_statuses_are_ok"
    ]["actual"] == {
        "multimodal_context": "conflict",
    }


def test_latest_signal_report_rejects_document_summary_with_control_character() -> None:
    document = create_document_evidence_card(
        summary="FOMC minutes summary says policy remains restrictive but stable.",
        artifact_ref="artifact://documents/fomc-minutes-summary.pdf",
        asset_scope=["QQQ", "TQQQ"],
    )
    document["evidence_card"]["summary"] = (
        "FOMC minutes summary says policy remains restrictive but stable.\n"
        "Injected line must not pass text safety."
    )
    document["evidence_card"]["summary_truncated"] = False
    payload = generate_latest_signal_report(
        "TQQQ",
        extra_evidence_cards=[document["evidence_card"]],
    )
    context = payload["multimodal_context"]
    context_guard_checks = {
        check["name"]: check for check in context["guard"]["checks"]
    }
    payload_guard_checks = {
        check["name"]: check for check in payload["report_payload_guard"]["checks"]
    }

    assert context["status"] == "conflict"
    assert context_guard_checks[
        "multimodal_context_evidence_card_values_are_safe"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_evidence_card_summary_bounds_are_safe"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_evidence_card_text_values_are_trimmed_and_control_free"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_evidence_card_text_values_are_trimmed_and_control_free"
    ]["actual"] == [
        {
            "evidence_id": "manual_document_summary",
            "text_fields": ["summary", "invalidating_condition"],
            "text_values_have_no_surrounding_whitespace": True,
            "text_values_have_no_control_characters": False,
        },
    ]
    assert payload_guard_checks[
        "report_payload_optional_context_statuses_are_ok"
    ]["actual"] == {
        "multimodal_context": "conflict",
    }


def test_latest_signal_report_rejects_non_string_document_summary() -> None:
    document = create_document_evidence_card(
        summary="FOMC minutes summary says policy remains restrictive but stable.",
        artifact_ref="artifact://documents/fomc-minutes-summary.pdf",
        asset_scope=["QQQ", "TQQQ"],
    )
    document["evidence_card"]["summary"] = 123
    document["evidence_card"]["summary_truncated"] = False
    payload = generate_latest_signal_report(
        "TQQQ",
        extra_evidence_cards=[document["evidence_card"]],
    )
    context = payload["multimodal_context"]
    context_guard_checks = {
        check["name"]: check for check in context["guard"]["checks"]
    }
    payload_guard_checks = {
        check["name"]: check for check in payload["report_payload_guard"]["checks"]
    }

    assert context["status"] == "conflict"
    assert context_guard_checks[
        "multimodal_context_evidence_card_values_are_safe"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_evidence_card_text_values_are_trimmed_and_control_free"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_evidence_card_summary_bounds_are_safe"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_evidence_card_string_field_types_are_strict"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_evidence_card_string_field_types_are_strict"
    ]["actual"] == [
        {
            **expected_document_evidence_card_string_field_types(
                document["evidence_card"]
            ),
            "string_fields_are_strings": False,
        },
    ]
    assert payload_guard_checks[
        "report_payload_optional_context_statuses_are_ok"
    ]["actual"] == {
        "multimodal_context": "conflict",
    }


def test_latest_signal_report_rejects_bool_document_strength_confidence() -> None:
    document = create_document_evidence_card(
        summary="FOMC minutes summary says policy remains restrictive but stable.",
        artifact_ref="artifact://documents/fomc-minutes-summary.pdf",
        asset_scope=["QQQ", "TQQQ"],
    )
    document["evidence_card"]["strength"] = True
    document["evidence_card"]["confidence"] = False
    payload = generate_latest_signal_report(
        "TQQQ",
        extra_evidence_cards=[document["evidence_card"]],
    )
    context = payload["multimodal_context"]
    context_guard_checks = {
        check["name"]: check for check in context["guard"]["checks"]
    }
    payload_guard_checks = {
        check["name"]: check for check in payload["report_payload_guard"]["checks"]
    }

    assert context["status"] == "conflict"
    assert context_guard_checks[
        "multimodal_context_evidence_card_string_field_types_are_strict"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_evidence_card_structural_field_types_are_strict"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_evidence_card_values_are_safe"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_evidence_card_values_are_safe"
    ]["actual"] == [
        {
            **expected_document_evidence_card_values(document["evidence_card"]),
            "strength_in_range": False,
            "confidence_in_range": False,
        },
    ]
    assert payload_guard_checks[
        "report_payload_optional_context_statuses_are_ok"
    ]["actual"] == {
        "multimodal_context": "conflict",
    }


def test_latest_signal_report_rejects_non_numeric_document_strength_confidence() -> None:
    document = create_document_evidence_card(
        summary="FOMC minutes summary says policy remains restrictive but stable.",
        artifact_ref="artifact://documents/fomc-minutes-summary.pdf",
        asset_scope=["QQQ", "TQQQ"],
    )
    document["evidence_card"]["strength"] = "0.57"
    document["evidence_card"]["confidence"] = None
    payload = generate_latest_signal_report(
        "TQQQ",
        extra_evidence_cards=[document["evidence_card"]],
    )
    context = payload["multimodal_context"]
    context_guard_checks = {
        check["name"]: check for check in context["guard"]["checks"]
    }
    payload_guard_checks = {
        check["name"]: check for check in payload["report_payload_guard"]["checks"]
    }

    assert context["status"] == "conflict"
    assert context_guard_checks[
        "multimodal_context_evidence_card_string_field_types_are_strict"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_evidence_card_structural_field_types_are_strict"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_evidence_card_values_are_safe"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_evidence_card_values_are_safe"
    ]["actual"] == [
        {
            **expected_document_evidence_card_values(document["evidence_card"]),
            "strength_in_range": False,
            "confidence_in_range": False,
        },
    ]
    assert payload_guard_checks[
        "report_payload_optional_context_statuses_are_ok"
    ]["actual"] == {
        "multimodal_context": "conflict",
    }


def test_latest_signal_report_rejects_out_of_range_document_strength_confidence() -> None:
    document = create_document_evidence_card(
        summary="FOMC minutes summary says policy remains restrictive but stable.",
        artifact_ref="artifact://documents/fomc-minutes-summary.pdf",
        asset_scope=["QQQ", "TQQQ"],
    )
    document["evidence_card"]["strength"] = 1.01
    document["evidence_card"]["confidence"] = -0.01
    payload = generate_latest_signal_report(
        "TQQQ",
        extra_evidence_cards=[document["evidence_card"]],
    )
    context = payload["multimodal_context"]
    context_guard_checks = {
        check["name"]: check for check in context["guard"]["checks"]
    }
    payload_guard_checks = {
        check["name"]: check for check in payload["report_payload_guard"]["checks"]
    }

    assert context["status"] == "conflict"
    assert context_guard_checks[
        "multimodal_context_evidence_card_string_field_types_are_strict"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_evidence_card_structural_field_types_are_strict"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_evidence_card_values_are_safe"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_evidence_card_values_are_safe"
    ]["actual"] == [
        {
            **expected_document_evidence_card_values(document["evidence_card"]),
            "strength_in_range": False,
            "confidence_in_range": False,
        },
    ]
    assert payload_guard_checks[
        "report_payload_optional_context_statuses_are_ok"
    ]["actual"] == {
        "multimodal_context": "conflict",
    }


def test_latest_signal_report_rejects_non_bool_summary_truncation_flag() -> None:
    document = create_document_evidence_card(
        summary="FOMC minutes summary says policy remains restrictive but stable.",
        artifact_ref="artifact://documents/fomc-minutes-summary.pdf",
        asset_scope=["QQQ", "TQQQ"],
    )
    document["evidence_card"]["summary_truncated"] = "false"
    payload = generate_latest_signal_report(
        "TQQQ",
        extra_evidence_cards=[document["evidence_card"]],
    )
    context = payload["multimodal_context"]
    context_guard_checks = {
        check["name"]: check for check in context["guard"]["checks"]
    }
    payload_guard_checks = {
        check["name"]: check for check in payload["report_payload_guard"]["checks"]
    }

    assert context["status"] == "conflict"
    assert context_guard_checks[
        "multimodal_context_evidence_card_summary_bounds_are_safe"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_evidence_card_summary_truncation_flags_are_consistent"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_evidence_card_values_are_safe"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_evidence_card_values_are_safe"
    ]["actual"] == [
        {
            **expected_document_evidence_card_values(document["evidence_card"]),
            "summary_truncated_is_bool": False,
        },
    ]
    assert payload_guard_checks[
        "report_payload_optional_context_statuses_are_ok"
    ]["actual"] == {
        "multimodal_context": "conflict",
    }


def test_latest_signal_report_rejects_inconsistent_summary_truncation_flag() -> None:
    document = create_document_evidence_card(
        summary="FOMC minutes summary says policy remains restrictive but stable.",
        artifact_ref="artifact://documents/fomc-minutes-summary.pdf",
        asset_scope=["QQQ", "TQQQ"],
    )
    document["evidence_card"]["summary_truncated"] = True
    payload = generate_latest_signal_report(
        "TQQQ",
        extra_evidence_cards=[document["evidence_card"]],
    )
    context = payload["multimodal_context"]
    context_guard_checks = {
        check["name"]: check for check in context["guard"]["checks"]
    }
    payload_guard_checks = {
        check["name"]: check for check in payload["report_payload_guard"]["checks"]
    }

    assert context["status"] == "conflict"
    assert context_guard_checks[
        "multimodal_context_evidence_card_summary_bounds_are_safe"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_evidence_card_summary_truncation_flags_are_consistent"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_evidence_card_summary_truncation_flags_are_consistent"
    ]["actual"] == [
        {
            "evidence_id": "manual_document_summary",
            "summary_truncated": True,
            "summary_truncated_requires_max_length": False,
        },
    ]
    assert payload_guard_checks[
        "report_payload_optional_context_statuses_are_ok"
    ]["actual"] == {
        "multimodal_context": "conflict",
    }


def test_latest_signal_report_rejects_actionable_document_evidence_impact() -> None:
    document = create_document_evidence_card(
        summary="FOMC minutes summary says policy remains restrictive but stable.",
        artifact_ref="artifact://documents/fomc-minutes-summary.pdf",
        buy_impact="buy_now",
        asset_scope=["QQQ", "TQQQ"],
    )
    payload = generate_latest_signal_report(
        "TQQQ",
        extra_evidence_cards=[document["evidence_card"]],
    )
    context = payload["multimodal_context"]
    context_guard_checks = {
        check["name"]: check for check in context["guard"]["checks"]
    }
    payload_guard_checks = {
        check["name"]: check for check in payload["report_payload_guard"]["checks"]
    }

    assert context["status"] == "conflict"
    assert context_guard_checks[
        "multimodal_context_evidence_card_impacts_are_context_only"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_evidence_card_impacts_are_context_only"
    ]["actual"] == [
        {
            "evidence_id": "manual_document_summary",
            "buy_impact": "buy_now",
            "sell_impact": "context_only",
        },
    ]
    assert payload_guard_checks[
        "report_payload_optional_context_statuses_are_ok"
    ]["actual"] == {
        "multimodal_context": "conflict",
    }


def test_latest_signal_report_rejects_empty_document_evidence_impact() -> None:
    document = create_document_evidence_card(
        summary="FOMC minutes summary says policy remains restrictive but stable.",
        artifact_ref="artifact://documents/fomc-minutes-summary.pdf",
        asset_scope=["QQQ", "TQQQ"],
    )
    document["evidence_card"]["buy_impact"] = ""
    payload = generate_latest_signal_report(
        "TQQQ",
        extra_evidence_cards=[document["evidence_card"]],
    )
    context = payload["multimodal_context"]
    context_guard_checks = {
        check["name"]: check for check in context["guard"]["checks"]
    }
    payload_guard_checks = {
        check["name"]: check for check in payload["report_payload_guard"]["checks"]
    }

    assert context["status"] == "conflict"
    assert context_guard_checks[
        "multimodal_context_evidence_card_string_field_types_are_strict"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_evidence_card_values_are_safe"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_evidence_card_values_are_safe"
    ]["actual"] == [
        {
            **expected_document_evidence_card_values(document["evidence_card"]),
            "impacts_nonempty": False,
        },
    ]
    assert context_guard_checks[
        "multimodal_context_evidence_card_impacts_are_context_only"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_evidence_card_impacts_are_context_only"
    ]["actual"] == [
        {
            "evidence_id": "manual_document_summary",
            "buy_impact": "",
            "sell_impact": "context_only",
        },
    ]
    assert payload_guard_checks[
        "report_payload_optional_context_statuses_are_ok"
    ]["actual"] == {
        "multimodal_context": "conflict",
    }


def test_latest_signal_report_rejects_non_string_document_evidence_impact() -> None:
    document = create_document_evidence_card(
        summary="FOMC minutes summary says policy remains restrictive but stable.",
        artifact_ref="artifact://documents/fomc-minutes-summary.pdf",
        asset_scope=["QQQ", "TQQQ"],
    )
    document["evidence_card"]["buy_impact"] = 123
    payload = generate_latest_signal_report(
        "TQQQ",
        extra_evidence_cards=[document["evidence_card"]],
    )
    context = payload["multimodal_context"]
    context_guard_checks = {
        check["name"]: check for check in context["guard"]["checks"]
    }
    payload_guard_checks = {
        check["name"]: check for check in payload["report_payload_guard"]["checks"]
    }

    assert context["status"] == "conflict"
    assert context_guard_checks[
        "multimodal_context_evidence_card_values_are_safe"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_evidence_card_string_field_types_are_strict"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_evidence_card_string_field_types_are_strict"
    ]["actual"] == [
        {
            **expected_document_evidence_card_string_field_types(
                document["evidence_card"]
            ),
            "string_fields_are_strings": False,
        },
    ]
    assert context_guard_checks[
        "multimodal_context_evidence_card_impacts_are_context_only"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_evidence_card_impacts_are_context_only"
    ]["actual"] == [
        {
            **expected_document_evidence_card_impact_values(
                document["evidence_card"]
            ),
            "buy_impact": 123,
        },
    ]
    assert payload_guard_checks[
        "report_payload_optional_context_statuses_are_ok"
    ]["actual"] == {
        "multimodal_context": "conflict",
    }


def test_latest_signal_report_rejects_empty_invalidating_condition() -> None:
    document = create_document_evidence_card(
        summary="FOMC minutes summary says policy remains restrictive but stable.",
        artifact_ref="artifact://documents/fomc-minutes-summary.pdf",
        asset_scope=["QQQ", "TQQQ"],
    )
    document["evidence_card"]["invalidating_condition"] = ""
    payload = generate_latest_signal_report(
        "TQQQ",
        extra_evidence_cards=[document["evidence_card"]],
    )
    context = payload["multimodal_context"]
    context_guard_checks = {
        check["name"]: check for check in context["guard"]["checks"]
    }
    payload_guard_checks = {
        check["name"]: check for check in payload["report_payload_guard"]["checks"]
    }

    assert context["status"] == "conflict"
    assert context_guard_checks[
        "multimodal_context_evidence_card_string_field_types_are_strict"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_evidence_card_text_values_are_trimmed_and_control_free"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_evidence_card_values_are_safe"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_evidence_card_values_are_safe"
    ]["actual"] == [
        {
            **expected_document_evidence_card_values(document["evidence_card"]),
            "invalidating_condition_nonempty": False,
        },
    ]
    assert context_guard_checks[
        "multimodal_context_evidence_card_invalidating_conditions_are_actionable"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_evidence_card_invalidating_conditions_are_actionable"
    ]["actual"] == [
        {
            "evidence_id": "manual_document_summary",
            "invalidating_condition_words_min": 4,
            "invalidating_condition_has_min_words": False,
            "invalidating_condition_nonplaceholder": False,
        },
    ]
    assert payload_guard_checks[
        "report_payload_optional_context_statuses_are_ok"
    ]["actual"] == {
        "multimodal_context": "conflict",
    }


def test_latest_signal_report_rejects_placeholder_invalidating_condition() -> None:
    document = create_document_evidence_card(
        summary="FOMC minutes summary says policy remains restrictive but stable.",
        artifact_ref="artifact://documents/fomc-minutes-summary.pdf",
        asset_scope=["QQQ", "TQQQ"],
        invalidating_condition="TBD",
    )
    payload = generate_latest_signal_report(
        "TQQQ",
        extra_evidence_cards=[document["evidence_card"]],
    )
    context = payload["multimodal_context"]
    context_guard_checks = {
        check["name"]: check for check in context["guard"]["checks"]
    }
    payload_guard_checks = {
        check["name"]: check for check in payload["report_payload_guard"]["checks"]
    }

    assert context["status"] == "conflict"
    assert context_guard_checks[
        "multimodal_context_evidence_card_invalidating_conditions_are_actionable"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_evidence_card_invalidating_conditions_are_actionable"
    ]["actual"] == [
        {
            "evidence_id": "manual_document_summary",
            "invalidating_condition_words_min": 4,
            "invalidating_condition_has_min_words": False,
            "invalidating_condition_nonplaceholder": False,
        },
    ]
    assert payload_guard_checks[
        "report_payload_optional_context_statuses_are_ok"
    ]["actual"] == {
        "multimodal_context": "conflict",
    }


def test_latest_signal_report_rejects_non_string_invalidating_condition() -> None:
    document = create_document_evidence_card(
        summary="FOMC minutes summary says policy remains restrictive but stable.",
        artifact_ref="artifact://documents/fomc-minutes-summary.pdf",
        asset_scope=["QQQ", "TQQQ"],
    )
    document["evidence_card"]["invalidating_condition"] = 123
    payload = generate_latest_signal_report(
        "TQQQ",
        extra_evidence_cards=[document["evidence_card"]],
    )
    context = payload["multimodal_context"]
    context_guard_checks = {
        check["name"]: check for check in context["guard"]["checks"]
    }
    payload_guard_checks = {
        check["name"]: check for check in payload["report_payload_guard"]["checks"]
    }

    assert context["status"] == "conflict"
    assert context_guard_checks[
        "multimodal_context_evidence_card_values_are_safe"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_evidence_card_text_values_are_trimmed_and_control_free"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_evidence_card_string_field_types_are_strict"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_evidence_card_string_field_types_are_strict"
    ]["actual"] == [
        {
            **expected_document_evidence_card_string_field_types(
                document["evidence_card"]
            ),
            "string_fields_are_strings": False,
        },
    ]
    assert context_guard_checks[
        "multimodal_context_evidence_card_invalidating_conditions_are_actionable"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_evidence_card_invalidating_conditions_are_actionable"
    ]["actual"] == [
        {
            "evidence_id": "manual_document_summary",
            "invalidating_condition_words_min": 4,
            "invalidating_condition_has_min_words": False,
            "invalidating_condition_nonplaceholder": True,
        },
    ]
    assert payload_guard_checks[
        "report_payload_optional_context_statuses_are_ok"
    ]["actual"] == {
        "multimodal_context": "conflict",
    }


def test_latest_signal_report_rejects_invalidating_condition_with_surrounding_whitespace() -> None:
    document = create_document_evidence_card(
        summary="FOMC minutes summary says policy remains restrictive but stable.",
        artifact_ref="artifact://documents/fomc-minutes-summary.pdf",
        asset_scope=["QQQ", "TQQQ"],
    )
    document["evidence_card"]["invalidating_condition"] = (
        "Document summary becomes stale or contradicted. "
    )
    payload = generate_latest_signal_report(
        "TQQQ",
        extra_evidence_cards=[document["evidence_card"]],
    )
    context = payload["multimodal_context"]
    context_guard_checks = {
        check["name"]: check for check in context["guard"]["checks"]
    }
    payload_guard_checks = {
        check["name"]: check for check in payload["report_payload_guard"]["checks"]
    }

    assert context["status"] == "conflict"
    assert context_guard_checks[
        "multimodal_context_evidence_card_values_are_safe"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_evidence_card_invalidating_conditions_are_actionable"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_evidence_card_text_values_are_trimmed_and_control_free"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_evidence_card_text_values_are_trimmed_and_control_free"
    ]["actual"] == [
        {
            "evidence_id": "manual_document_summary",
            "text_fields": ["summary", "invalidating_condition"],
            "text_values_have_no_surrounding_whitespace": False,
            "text_values_have_no_control_characters": True,
        },
    ]
    assert payload_guard_checks[
        "report_payload_optional_context_statuses_are_ok"
    ]["actual"] == {
        "multimodal_context": "conflict",
    }


def test_latest_signal_report_rejects_non_iso_document_evidence_observed_at() -> None:
    document = create_document_evidence_card(
        summary="FOMC minutes summary says policy remains restrictive but stable.",
        artifact_ref="artifact://documents/fomc-minutes-summary.pdf",
        observed_at="yesterday",
        asset_scope=["QQQ", "TQQQ"],
    )
    payload = generate_latest_signal_report(
        "TQQQ",
        extra_evidence_cards=[document["evidence_card"]],
    )
    context = payload["multimodal_context"]
    context_guard_checks = {
        check["name"]: check for check in context["guard"]["checks"]
    }
    payload_guard_checks = {
        check["name"]: check for check in payload["report_payload_guard"]["checks"]
    }

    assert context["status"] == "conflict"
    assert context_guard_checks[
        "multimodal_context_evidence_card_values_are_safe"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_evidence_card_observed_at_values_are_utc_iso"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_evidence_card_observed_at_values_are_utc_iso"
    ]["actual"] == [
        {
            "evidence_id": "manual_document_summary",
            "observed_at_format": "iso8601_utc",
            "observed_at_is_utc_iso": False,
        },
    ]
    assert payload_guard_checks[
        "report_payload_optional_context_statuses_are_ok"
    ]["actual"] == {
        "multimodal_context": "conflict",
    }


def test_latest_signal_report_rejects_empty_document_observed_at() -> None:
    document = create_document_evidence_card(
        summary="FOMC minutes summary says policy remains restrictive but stable.",
        artifact_ref="artifact://documents/fomc-minutes-summary.pdf",
        asset_scope=["QQQ", "TQQQ"],
    )
    document["evidence_card"]["observed_at"] = ""
    payload = generate_latest_signal_report(
        "TQQQ",
        extra_evidence_cards=[document["evidence_card"]],
    )
    context = payload["multimodal_context"]
    context_guard_checks = {
        check["name"]: check for check in context["guard"]["checks"]
    }
    payload_guard_checks = {
        check["name"]: check for check in payload["report_payload_guard"]["checks"]
    }

    assert context["status"] == "conflict"
    assert context_guard_checks[
        "multimodal_context_evidence_card_string_field_types_are_strict"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_evidence_card_scalar_values_are_trimmed_and_control_free"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_evidence_card_values_are_safe"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_evidence_card_values_are_safe"
    ]["actual"] == [
        {
            **expected_document_evidence_card_values(document["evidence_card"]),
            "observed_at_nonempty": False,
        },
    ]
    assert context_guard_checks[
        "multimodal_context_evidence_card_observed_at_values_are_utc_iso"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_evidence_card_observed_at_values_are_utc_iso"
    ]["actual"] == [
        {
            "evidence_id": "manual_document_summary",
            "observed_at_format": "iso8601_utc",
            "observed_at_is_utc_iso": False,
        },
    ]
    assert context_guard_checks[
        "multimodal_context_evidence_card_observed_at_not_after_report"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_evidence_card_observed_at_not_after_report"
    ]["actual"] == [
        {
            "evidence_id": "manual_document_summary",
            "report_created_at": payload["latest_signal_report"]["created_at"],
            "observed_at_not_after_report_created_at": False,
        },
    ]
    assert payload_guard_checks[
        "report_payload_optional_context_statuses_are_ok"
    ]["actual"] == {
        "multimodal_context": "conflict",
    }


def test_latest_signal_report_rejects_non_string_document_observed_at() -> None:
    document = create_document_evidence_card(
        summary="FOMC minutes summary says policy remains restrictive but stable.",
        artifact_ref="artifact://documents/fomc-minutes-summary.pdf",
        asset_scope=["QQQ", "TQQQ"],
    )
    document["evidence_card"]["observed_at"] = 123
    payload = generate_latest_signal_report(
        "TQQQ",
        extra_evidence_cards=[document["evidence_card"]],
    )
    context = payload["multimodal_context"]
    context_guard_checks = {
        check["name"]: check for check in context["guard"]["checks"]
    }
    payload_guard_checks = {
        check["name"]: check for check in payload["report_payload_guard"]["checks"]
    }

    assert context["status"] == "conflict"
    assert context_guard_checks[
        "multimodal_context_evidence_card_values_are_safe"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_evidence_card_scalar_values_are_trimmed_and_control_free"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_evidence_card_string_field_types_are_strict"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_evidence_card_string_field_types_are_strict"
    ]["actual"] == [
        {
            **expected_document_evidence_card_string_field_types(
                document["evidence_card"]
            ),
            "string_fields_are_strings": False,
        },
    ]
    assert context_guard_checks[
        "multimodal_context_evidence_card_observed_at_values_are_utc_iso"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_evidence_card_observed_at_not_after_report"
    ]["passed"] is False
    assert payload_guard_checks[
        "report_payload_optional_context_statuses_are_ok"
    ]["actual"] == {
        "multimodal_context": "conflict",
    }


def test_latest_signal_report_rejects_document_observed_at_with_control_character() -> None:
    document = create_document_evidence_card(
        summary="FOMC minutes summary says policy remains restrictive but stable.",
        artifact_ref="artifact://documents/fomc-minutes-summary.pdf",
        observed_at="2026-05-08T20:00:00Z",
        asset_scope=["QQQ", "TQQQ"],
    )
    document["evidence_card"]["observed_at"] = "2026-05-08T20:00:00Z\n"
    payload = generate_latest_signal_report(
        "TQQQ",
        extra_evidence_cards=[document["evidence_card"]],
    )
    context = payload["multimodal_context"]
    context_guard_checks = {
        check["name"]: check for check in context["guard"]["checks"]
    }
    payload_guard_checks = {
        check["name"]: check for check in payload["report_payload_guard"]["checks"]
    }

    assert context["status"] == "conflict"
    assert context_guard_checks[
        "multimodal_context_evidence_card_values_are_safe"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_evidence_card_observed_at_values_are_utc_iso"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_evidence_card_observed_at_not_after_report"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_evidence_card_scalar_values_are_trimmed_and_control_free"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_evidence_card_scalar_values_are_trimmed_and_control_free"
    ]["actual"] == [
        {
            "evidence_id": "manual_document_summary",
            "scalar_fields": ["modality", "observed_at"],
            "scalar_values_have_no_surrounding_whitespace": False,
            "scalar_values_have_no_control_characters": False,
        },
    ]
    assert payload_guard_checks[
        "report_payload_optional_context_statuses_are_ok"
    ]["actual"] == {
        "multimodal_context": "conflict",
    }


def test_latest_signal_report_rejects_future_document_evidence_observed_at() -> None:
    document = create_document_evidence_card(
        summary="FOMC minutes summary says policy remains restrictive but stable.",
        artifact_ref="artifact://documents/fomc-minutes-summary.pdf",
        observed_at="2099-01-01T00:00:00Z",
        asset_scope=["QQQ", "TQQQ"],
    )
    payload = generate_latest_signal_report(
        "TQQQ",
        extra_evidence_cards=[document["evidence_card"]],
    )
    context = payload["multimodal_context"]
    context_guard_checks = {
        check["name"]: check for check in context["guard"]["checks"]
    }
    payload_guard_checks = {
        check["name"]: check for check in payload["report_payload_guard"]["checks"]
    }

    assert context["status"] == "conflict"
    assert context_guard_checks[
        "multimodal_context_evidence_card_values_are_safe"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_evidence_card_observed_at_values_are_utc_iso"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_evidence_card_observed_at_not_after_report"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_evidence_card_observed_at_not_after_report"
    ]["actual"] == [
        {
            "evidence_id": "manual_document_summary",
            "report_created_at": payload["latest_signal_report"]["created_at"],
            "observed_at_not_after_report_created_at": False,
        },
    ]
    assert payload_guard_checks[
        "report_payload_optional_context_statuses_are_ok"
    ]["actual"] == {
        "multimodal_context": "conflict",
    }


def test_latest_signal_report_rejects_empty_document_asset_scope() -> None:
    document = create_document_evidence_card(
        summary="FOMC minutes summary says policy remains restrictive but stable.",
        artifact_ref="artifact://documents/fomc-minutes-summary.pdf",
        asset_scope=["QQQ", "TQQQ"],
    )
    document["evidence_card"]["asset_scope"] = []
    payload = generate_latest_signal_report(
        "TQQQ",
        extra_evidence_cards=[document["evidence_card"]],
    )
    context = payload["multimodal_context"]
    context_guard_checks = {
        check["name"]: check for check in context["guard"]["checks"]
    }
    payload_guard_checks = {
        check["name"]: check for check in payload["report_payload_guard"]["checks"]
    }

    assert context["status"] == "conflict"
    assert context_guard_checks[
        "multimodal_context_evidence_card_structural_field_types_are_strict"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_evidence_card_values_are_safe"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_evidence_card_asset_scope_values_are_trimmed_and_control_free"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_evidence_card_asset_scope_matches_report"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_evidence_card_asset_scope_matches_report"
    ]["actual"] == [
        {
            "evidence_id": "manual_document_summary",
            "report_asset": "TQQQ",
            "report_underlying": "QQQ",
            "includes_report_asset": False,
            "includes_report_underlying": False,
        },
    ]
    assert payload_guard_checks[
        "report_payload_optional_context_statuses_are_ok"
    ]["actual"] == {
        "multimodal_context": "conflict",
    }


def test_latest_signal_report_rejects_document_evidence_outside_asset_scope() -> None:
    document = create_document_evidence_card(
        summary="FOMC minutes summary says policy remains restrictive but stable.",
        artifact_ref="artifact://documents/fomc-minutes-summary.pdf",
        asset_scope=["SPY"],
    )
    payload = generate_latest_signal_report(
        "TQQQ",
        extra_evidence_cards=[document["evidence_card"]],
    )
    context = payload["multimodal_context"]
    context_guard_checks = {
        check["name"]: check for check in context["guard"]["checks"]
    }
    payload_guard_checks = {
        check["name"]: check for check in payload["report_payload_guard"]["checks"]
    }

    assert context["status"] == "conflict"
    assert context_guard_checks[
        "multimodal_context_evidence_card_asset_scope_matches_report"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_evidence_card_asset_scope_matches_report"
    ]["actual"] == [
        {
            "evidence_id": "manual_document_summary",
            "report_asset": "TQQQ",
            "report_underlying": "QQQ",
            "includes_report_asset": False,
            "includes_report_underlying": False,
        },
    ]
    assert payload_guard_checks[
        "report_payload_optional_context_statuses_are_ok"
    ]["actual"] == {
        "multimodal_context": "conflict",
    }


def test_latest_signal_report_rejects_lowercase_document_asset_scope() -> None:
    document = create_document_evidence_card(
        summary="FOMC minutes summary says policy remains restrictive but stable.",
        artifact_ref="artifact://documents/fomc-minutes-summary.pdf",
        asset_scope=["QQQ", "TQQQ"],
    )
    document["evidence_card"]["asset_scope"] = ["qqq", "tqqq"]
    payload = generate_latest_signal_report(
        "TQQQ",
        extra_evidence_cards=[document["evidence_card"]],
    )
    context = payload["multimodal_context"]
    context_guard_checks = {
        check["name"]: check for check in context["guard"]["checks"]
    }
    payload_guard_checks = {
        check["name"]: check for check in payload["report_payload_guard"]["checks"]
    }

    assert context["status"] == "conflict"
    assert context_guard_checks[
        "multimodal_context_evidence_card_structural_field_types_are_strict"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_evidence_card_asset_scope_matches_report"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_evidence_card_asset_scope_values_are_trimmed_and_control_free"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_evidence_card_values_are_safe"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_evidence_card_values_are_safe"
    ]["actual"] == [
        {
            **expected_document_evidence_card_values(document["evidence_card"]),
            "asset_scope_uppercase": False,
        },
    ]
    assert payload_guard_checks[
        "report_payload_optional_context_statuses_are_ok"
    ]["actual"] == {
        "multimodal_context": "conflict",
    }


def test_latest_signal_report_rejects_document_asset_scope_with_control_character() -> None:
    document = create_document_evidence_card(
        summary="FOMC minutes summary says policy remains restrictive but stable.",
        artifact_ref="artifact://documents/fomc-minutes-summary.pdf",
        asset_scope=["QQQ", "TQQQ"],
    )
    document["evidence_card"]["asset_scope"] = ["QQQ", "TQQQ", "SPY\n"]
    payload = generate_latest_signal_report(
        "TQQQ",
        extra_evidence_cards=[document["evidence_card"]],
    )
    context = payload["multimodal_context"]
    context_guard_checks = {
        check["name"]: check for check in context["guard"]["checks"]
    }
    payload_guard_checks = {
        check["name"]: check for check in payload["report_payload_guard"]["checks"]
    }

    assert context["status"] == "conflict"
    assert context_guard_checks[
        "multimodal_context_evidence_card_values_are_safe"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_evidence_card_asset_scope_matches_report"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_evidence_card_asset_scope_values_are_trimmed_and_control_free"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_evidence_card_asset_scope_values_are_trimmed_and_control_free"
    ]["actual"] == [
        {
            "evidence_id": "manual_document_summary",
            "asset_scope_values_have_no_surrounding_whitespace": False,
            "asset_scope_values_have_no_control_characters": False,
        },
    ]
    assert payload_guard_checks[
        "report_payload_optional_context_statuses_are_ok"
    ]["actual"] == {
        "multimodal_context": "conflict",
    }


def test_latest_signal_report_rejects_non_string_document_asset_scope_value() -> None:
    document = create_document_evidence_card(
        summary="FOMC minutes summary says policy remains restrictive but stable.",
        artifact_ref="artifact://documents/fomc-minutes-summary.pdf",
        asset_scope=["QQQ", "TQQQ"],
    )
    document["evidence_card"]["asset_scope"] = ["QQQ", "TQQQ", 123]
    payload = generate_latest_signal_report(
        "TQQQ",
        extra_evidence_cards=[document["evidence_card"]],
    )
    context = payload["multimodal_context"]
    context_guard_checks = {
        check["name"]: check for check in context["guard"]["checks"]
    }
    payload_guard_checks = {
        check["name"]: check for check in payload["report_payload_guard"]["checks"]
    }

    assert context["status"] == "conflict"
    assert context_guard_checks[
        "multimodal_context_evidence_card_asset_scope_matches_report"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_evidence_card_structural_field_types_are_strict"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_evidence_card_values_are_safe"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_evidence_card_values_are_safe"
    ]["actual"] == [
        {
            **expected_document_evidence_card_values(document["evidence_card"]),
            "asset_scope_uppercase": False,
        },
    ]
    assert context_guard_checks[
        "multimodal_context_evidence_card_asset_scope_values_are_trimmed_and_control_free"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_evidence_card_asset_scope_values_are_trimmed_and_control_free"
    ]["actual"] == [
        {
            "evidence_id": "manual_document_summary",
            "asset_scope_values_have_no_surrounding_whitespace": False,
            "asset_scope_values_have_no_control_characters": False,
        },
    ]
    assert payload_guard_checks[
        "report_payload_optional_context_statuses_are_ok"
    ]["actual"] == {
        "multimodal_context": "conflict",
    }


def test_latest_signal_report_rejects_non_list_document_asset_scope() -> None:
    document = create_document_evidence_card(
        summary="FOMC minutes summary says policy remains restrictive but stable.",
        artifact_ref="artifact://documents/fomc-minutes-summary.pdf",
        asset_scope=["QQQ", "TQQQ"],
    )
    document["evidence_card"]["asset_scope"] = "QQQ,TQQQ"
    payload = generate_latest_signal_report(
        "TQQQ",
        extra_evidence_cards=[document["evidence_card"]],
    )
    context = payload["multimodal_context"]
    context_guard_checks = {
        check["name"]: check for check in context["guard"]["checks"]
    }
    payload_guard_checks = {
        check["name"]: check for check in payload["report_payload_guard"]["checks"]
    }

    assert context["status"] == "conflict"
    assert context_guard_checks[
        "multimodal_context_evidence_card_values_are_safe"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_evidence_card_asset_scope_values_are_trimmed_and_control_free"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_evidence_card_asset_scope_matches_report"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_evidence_card_structural_field_types_are_strict"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_evidence_card_structural_field_types_are_strict"
    ]["actual"] == [
        {
            **expected_document_evidence_card_structural_field_types(
                document["evidence_card"]
            ),
            "asset_scope_is_list": False,
        },
    ]
    assert payload_guard_checks[
        "report_payload_optional_context_statuses_are_ok"
    ]["actual"] == {
        "multimodal_context": "conflict",
    }


def test_latest_signal_report_rejects_non_dict_document_artifact_ref() -> None:
    document = create_document_evidence_card(
        summary="FOMC minutes summary says policy remains restrictive but stable.",
        artifact_ref="artifact://documents/fomc-minutes-summary.pdf",
        asset_scope=["QQQ", "TQQQ"],
    )
    document["evidence_card"]["artifact_ref"] = (
        "artifact://documents/fomc-minutes-summary.pdf"
    )
    payload = generate_latest_signal_report(
        "TQQQ",
        extra_evidence_cards=[document["evidence_card"]],
    )
    context = payload["multimodal_context"]
    context_guard_checks = {
        check["name"]: check for check in context["guard"]["checks"]
    }
    payload_guard_checks = {
        check["name"]: check for check in payload["report_payload_guard"]["checks"]
    }

    assert context["status"] == "conflict"
    assert context_guard_checks[
        "multimodal_context_artifact_ref_types_match_expected_contract"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_artifact_ref_metadata_matches_expected_schema"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_artifact_refs_match_expected_schema"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_evidence_card_artifact_refs_use_explicit_uris"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_evidence_card_structural_field_types_are_strict"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_evidence_card_structural_field_types_are_strict"
    ]["actual"] == [
        {
            **expected_document_evidence_card_structural_field_types(
                document["evidence_card"]
            ),
            "artifact_ref_is_dict": False,
        },
    ]
    assert payload_guard_checks[
        "report_payload_optional_context_statuses_are_ok"
    ]["actual"] == {
        "multimodal_context": "conflict",
    }


def test_latest_signal_report_rejects_empty_document_artifact_ref_dict() -> None:
    document = create_document_evidence_card(
        summary="FOMC minutes summary says policy remains restrictive but stable.",
        artifact_ref="artifact://documents/fomc-minutes-summary.pdf",
        asset_scope=["QQQ", "TQQQ"],
    )
    document["evidence_card"]["artifact_ref"] = {}
    payload = generate_latest_signal_report(
        "TQQQ",
        extra_evidence_cards=[document["evidence_card"]],
    )
    context = payload["multimodal_context"]
    context_guard_checks = {
        check["name"]: check for check in context["guard"]["checks"]
    }
    payload_guard_checks = {
        check["name"]: check for check in payload["report_payload_guard"]["checks"]
    }

    assert context["status"] == "conflict"
    assert context["artifact_refs"] == [
        {
            "evidence_id": "manual_document_summary",
            "artifact_ref": {},
        },
    ]
    assert context_guard_checks[
        "multimodal_context_artifact_refs_match_expected_context"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_artifact_refs_cover_evidence_cards_with_artifact_ref"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_artifact_refs_cover_evidence_cards_with_artifact_ref"
    ]["actual"] == ["manual_document_summary"]
    assert context_guard_checks[
        "multimodal_context_artifact_refs_match_expected_schema"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_artifact_refs_match_expected_schema"
    ]["actual"] == {
        "artifact_ref_entry_keys": [["evidence_id", "artifact_ref"]],
        "artifact_ref_keys": [[]],
    }
    assert context_guard_checks[
        "multimodal_context_artifact_ref_string_field_types_are_strict"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_artifact_ref_string_field_types_are_strict"
    ]["actual"] == [
        {
            "evidence_id": "manual_document_summary",
            "string_fields": ["ref_type", "ref"],
            "ref_type_is_string": False,
            "ref_is_string": False,
        },
    ]
    assert context_guard_checks[
        "multimodal_context_artifact_ref_types_match_expected_contract"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_artifact_ref_values_are_unique"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_evidence_card_values_are_safe"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_evidence_card_artifact_refs_use_explicit_uris"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_evidence_card_structural_field_types_are_strict"
    ]["passed"] is True
    assert payload_guard_checks[
        "report_payload_optional_context_statuses_are_ok"
    ]["actual"] == {
        "multimodal_context": "conflict",
    }


def test_latest_signal_report_rejects_null_document_artifact_ref() -> None:
    document = create_document_evidence_card(
        summary="FOMC minutes summary says policy remains restrictive but stable.",
        artifact_ref="artifact://documents/fomc-minutes-summary.pdf",
        asset_scope=["QQQ", "TQQQ"],
    )
    document["evidence_card"]["artifact_ref"] = None
    payload = generate_latest_signal_report(
        "TQQQ",
        extra_evidence_cards=[document["evidence_card"]],
    )
    context = payload["multimodal_context"]
    context_guard_checks = {
        check["name"]: check for check in context["guard"]["checks"]
    }
    payload_guard_checks = {
        check["name"]: check for check in payload["report_payload_guard"]["checks"]
    }

    assert context["status"] == "conflict"
    assert context["artifact_refs"] == [
        {
            "evidence_id": "manual_document_summary",
            "artifact_ref": None,
        },
    ]
    assert context_guard_checks[
        "multimodal_context_artifact_refs_match_expected_context"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_artifact_refs_cover_evidence_cards_with_artifact_ref"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_artifact_refs_cover_evidence_cards_with_artifact_ref"
    ]["actual"] == ["manual_document_summary"]
    assert context_guard_checks[
        "multimodal_context_artifact_refs_match_expected_schema"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_artifact_refs_match_expected_schema"
    ]["actual"] == {
        "artifact_ref_entry_keys": [["evidence_id", "artifact_ref"]],
        "artifact_ref_keys": [[]],
    }
    assert context_guard_checks[
        "multimodal_context_evidence_card_values_are_safe"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_evidence_card_values_are_safe"
    ]["actual"] == [
        {
            **expected_document_evidence_card_values(document["evidence_card"]),
            "artifact_ref_portable": False,
        },
    ]
    assert context_guard_checks[
        "multimodal_context_evidence_card_artifact_refs_use_explicit_uris"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_evidence_card_structural_field_types_are_strict"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_evidence_card_structural_field_types_are_strict"
    ]["actual"] == [
        {
            **expected_document_evidence_card_structural_field_types(
                document["evidence_card"]
            ),
            "artifact_ref_is_dict": False,
        },
    ]
    assert payload_guard_checks[
        "report_payload_optional_context_statuses_are_ok"
    ]["actual"] == {
        "multimodal_context": "conflict",
    }


def test_latest_signal_report_rejects_missing_document_artifact_ref_key() -> None:
    document = create_document_evidence_card(
        summary="FOMC minutes summary says policy remains restrictive but stable.",
        artifact_ref="artifact://documents/fomc-minutes-summary.pdf",
        asset_scope=["QQQ", "TQQQ"],
    )
    document["evidence_card"].pop("artifact_ref")
    payload = generate_latest_signal_report(
        "TQQQ",
        extra_evidence_cards=[document["evidence_card"]],
    )
    context = payload["multimodal_context"]
    context_guard_checks = {
        check["name"]: check for check in context["guard"]["checks"]
    }
    payload_guard_checks = {
        check["name"]: check for check in payload["report_payload_guard"]["checks"]
    }

    assert context["status"] == "conflict"
    assert context["artifact_refs"] == []
    assert context_guard_checks[
        "multimodal_context_artifact_refs_match_expected_context"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_artifact_refs_cover_evidence_cards_with_artifact_ref"
    ]["passed"] is True
    assert context_guard_checks[
        "multimodal_context_artifact_refs_cover_evidence_cards_with_artifact_ref"
    ]["actual"] == []
    assert context_guard_checks[
        "multimodal_context_evidence_cards_match_expected_schema"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_evidence_cards_match_expected_schema"
    ]["actual"] == [
        [
            "evidence_id",
            "category",
            "source",
            "modality",
            "observed_at",
            "asset_scope",
            "bias",
            "strength",
            "confidence",
            "summary",
            "summary_truncated",
            "buy_impact",
            "sell_impact",
            "invalidating_condition",
        ],
    ]
    assert context_guard_checks[
        "multimodal_context_evidence_card_values_are_safe"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_evidence_card_values_are_safe"
    ]["actual"] == [
        {
            **expected_document_evidence_card_values(document["evidence_card"]),
            "artifact_ref_portable": False,
        },
    ]
    assert context_guard_checks[
        "multimodal_context_evidence_card_artifact_refs_use_explicit_uris"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_evidence_card_structural_field_types_are_strict"
    ]["passed"] is False
    assert context_guard_checks[
        "multimodal_context_evidence_card_structural_field_types_are_strict"
    ]["actual"] == [
        {
            **expected_document_evidence_card_structural_field_types(
                document["evidence_card"]
            ),
            "artifact_ref_is_dict": False,
        },
    ]
    assert payload_guard_checks[
        "report_payload_optional_context_statuses_are_ok"
    ]["actual"] == {
        "multimodal_context": "conflict",
    }


def test_latest_signal_report_multimodal_context_survives_report_intent_variants(
    tmp_path: Path,
) -> None:
    document = create_document_evidence_card(
        summary="FOMC minutes summary says policy remains restrictive but stable.",
        artifact_ref="artifact://documents/fomc-minutes-summary.pdf",
        asset_scope=["QQQ", "TQQQ"],
    )
    expected_sections_by_intent = {
        "intraday_risk_watch": ["Target", "Decision", "Stop", "Cautions"],
        "post_market_review": [
            "Target",
            "Decision",
            "Reasons",
            "Take Profit",
            "Cautions",
        ],
    }

    for intent, expected_sections in expected_sections_by_intent.items():
        payload = generate_latest_signal_report(
            "TQQQ",
            report_intent=intent,
            include_chart=True,
            chart_output_dir=str(tmp_path / intent),
            extra_evidence_cards=[document["evidence_card"]],
        )
        context = payload["multimodal_context"]
        payload_guard_checks = {
            check["name"]: check for check in payload["report_payload_guard"]["checks"]
        }
        context_guard_checks = {
            check["name"]: check for check in context["guard"]["checks"]
        }

        assert payload["report_intent"] == intent
        assert [
            section["title"] for section in payload["sections"]
        ] == expected_sections
        assert payload["report_intent_contract"]["required_sections"] == expected_sections
        assert context["status"] == "ok"
        assert context["guard"]["status"] == "ok"
        assert context["modality_counts"] == {
            "chart_image": 1,
            "pdf_summary": 1,
        }
        assert {ref["artifact_ref"]["ref_type"] for ref in context["artifact_refs"]} == {
            "CHART",
            "PDF",
        }
        assert payload_guard_checks["report_payload_optional_context_statuses_are_ok"][
            "actual"
        ] == {
            "chart_code_guard": "ok",
            "multimodal_context": "ok",
        }
        assert payload_guard_checks["report_payload_optional_context_guards_are_ok"][
            "actual"
        ] == {
            "chart_code_guard": "ok",
            "multimodal_context.guard": "ok",
        }
        assert context_guard_checks[
            "multimodal_context_identity_values_match_expected_contract"
        ]["actual"] == EXPECTED_MULTIMODAL_CONTEXT_IDENTITY_VALUES
        assert context_guard_checks[
            "multimodal_context_evidence_card_values_are_safe"
        ]["actual"] == [
            expected_document_evidence_card_values(document["evidence_card"]),
        ]
        assert context_guard_checks[
            "multimodal_context_artifact_refs_match_expected_context"
        ]["actual"][1] == {
            "evidence_id": "manual_document_summary",
            "artifact_ref": document["evidence_card"]["artifact_ref"],
        }
        assert payload["live_data_required"] is False


def test_latest_signal_report_document_only_multimodal_context_survives_report_intent_variants() -> None:
    document = create_document_evidence_card(
        summary="FOMC minutes summary says policy remains restrictive but stable.",
        artifact_ref="artifact://documents/fomc-minutes-summary.pdf",
        asset_scope=["QQQ", "TQQQ"],
    )
    expected_sections_by_intent = {
        "intraday_risk_watch": ["Target", "Decision", "Stop", "Cautions"],
        "post_market_review": [
            "Target",
            "Decision",
            "Reasons",
            "Take Profit",
            "Cautions",
        ],
    }

    for intent, expected_sections in expected_sections_by_intent.items():
        payload = generate_latest_signal_report(
            "TQQQ",
            report_intent=intent,
            extra_evidence_cards=[document["evidence_card"]],
        )
        context = payload["multimodal_context"]
        payload_guard_checks = {
            check["name"]: check for check in payload["report_payload_guard"]["checks"]
        }
        context_guard_checks = {
            check["name"]: check for check in context["guard"]["checks"]
        }

        assert "chart_code_guard" not in payload
        assert payload["report_intent"] == intent
        assert [
            section["title"] for section in payload["sections"]
        ] == expected_sections
        assert payload["report_intent_contract"]["required_sections"] == expected_sections
        assert context["status"] == "ok"
        assert context["guard"]["status"] == "ok"
        assert context["modality_counts"] == {"pdf_summary": 1}
        assert {ref["artifact_ref"]["ref_type"] for ref in context["artifact_refs"]} == {
            "PDF"
        }
        assert payload_guard_checks["report_payload_keys_match_expected_schema"][
            "actual"
        ][-2:] == [
            "multimodal_context",
            "report_payload_guard",
        ]
        assert payload_guard_checks["report_payload_optional_context_statuses_are_ok"][
            "actual"
        ] == {
            "multimodal_context": "ok",
        }
        assert payload_guard_checks["report_payload_optional_context_guards_are_ok"][
            "actual"
        ] == {
            "multimodal_context.guard": "ok",
        }
        assert context_guard_checks[
            "multimodal_context_identity_values_match_expected_contract"
        ]["actual"] == EXPECTED_MULTIMODAL_CONTEXT_IDENTITY_VALUES
        assert context_guard_checks[
            "multimodal_context_evidence_card_values_are_safe"
        ]["actual"] == [
            expected_document_evidence_card_values(document["evidence_card"]),
        ]
        assert context_guard_checks[
            "multimodal_context_artifact_refs_match_expected_context"
        ]["actual"] == [
            {
                "evidence_id": "manual_document_summary",
                "artifact_ref": document["evidence_card"]["artifact_ref"],
            },
        ]
        assert payload["live_data_required"] is False


def test_position_review_report_contains_guarded_decision() -> None:
    payload = generate_position_review_report(
        "TQQQ",
        entry_price=100,
        current_price=114,
        size=3,
    )
    sections = {section["title"]: section["items"] for section in payload["sections"]}

    assert payload["schema_version"] == "hermes_position_review.v1"
    payload_guard_checks = {
        check["name"]: check for check in payload["position_payload_guard"]["checks"]
    }
    assert payload["position_payload_guard"]["status"] == "ok"
    assert payload_guard_checks[
        "position_payload_schema_version_matches_expected"
    ]["passed"] is True
    assert payload_guard_checks[
        "position_payload_schema_version_matches_expected"
    ]["actual"] == "hermes_position_review.v1"
    assert payload_guard_checks[
        "position_payload_live_data_required_matches_expected"
    ]["passed"] is True
    assert payload_guard_checks[
        "position_payload_live_data_required_matches_expected"
    ]["actual"] is False
    assert payload_guard_checks[
        "position_payload_guard_check_names_match_expected_schema"
    ]["passed"] is True
    assert payload_guard_checks[
        "position_payload_guard_check_names_match_expected_schema"
    ]["actual"] == payload_guard_checks[
        "position_payload_guard_check_names_match_expected_schema"
    ]["expected"]
    assert payload_guard_checks[
        "position_payload_guard_check_names_match_expected_schema"
    ]["actual"] == [
        "position_payload_schema_version_matches_expected",
        "position_payload_live_data_required_matches_expected",
        "position_payload_keys_match_expected_schema",
        "position_payload_top_level_identity_matches_position_review",
        "position_payload_nested_guard_statuses_are_ok",
        "position_payload_guard_check_names_match_expected_schema",
        "position_payload_guard_keys_match_expected_schema",
        "position_payload_guard_check_keys_match_expected_schema",
    ]
    expected_position_payload_identity = {
        "as_of": payload["position_review"]["as_of"],
        "asset": payload["position_review"]["asset"],
        "underlying": payload["position_review"]["underlying"],
        "action": payload["position_review"]["action"],
        "position_state": payload["position_review"]["position_state"],
    }
    assert payload_guard_checks[
        "position_payload_top_level_identity_matches_position_review"
    ]["passed"] is True
    assert payload_guard_checks[
        "position_payload_top_level_identity_matches_position_review"
    ]["actual"] == expected_position_payload_identity
    assert payload_guard_checks[
        "position_payload_top_level_identity_matches_position_review"
    ]["expected"] == expected_position_payload_identity
    expected_position_nested_guard_statuses = {
        "delivery_preview.guard": "ok",
        "position_review_guard": "ok",
    }
    assert payload_guard_checks["position_payload_nested_guard_statuses_are_ok"][
        "passed"
    ] is True
    assert payload_guard_checks["position_payload_nested_guard_statuses_are_ok"][
        "actual"
    ] == expected_position_nested_guard_statuses
    assert payload_guard_checks["position_payload_nested_guard_statuses_are_ok"][
        "expected"
    ] == expected_position_nested_guard_statuses
    assert payload_guard_checks[
        "position_payload_guard_keys_match_expected_schema"
    ]["passed"] is True

    assert payload_guard_checks[
        "position_payload_guard_keys_match_expected_schema"
    ]["actual"] == ["status", "checks"]
    assert payload_guard_checks[
        "position_payload_guard_check_keys_match_expected_schema"
    ]["passed"] is True
    assert all(
        check_keys == ["name", "passed", "expected", "actual"]
        for check_keys in payload_guard_checks[
            "position_payload_guard_check_keys_match_expected_schema"
        ]["actual"].values()
    )
    assert payload_guard_checks[
        "position_payload_guard_check_keys_match_expected_schema"
    ]["actual"]["position_payload_keys_match_expected_schema"] == [
        "name",
        "passed",
        "expected",
        "actual",
    ]
    assert payload_guard_checks[
        "position_payload_guard_check_keys_match_expected_schema"
    ]["actual"]["position_payload_guard_keys_match_expected_schema"] == [
        "name",
        "passed",
        "expected",
        "actual",
    ]
    assert payload_guard_checks[
        "position_payload_guard_check_keys_match_expected_schema"
    ]["actual"]["position_payload_top_level_identity_matches_position_review"] == [
        "name",
        "passed",
        "expected",
        "actual",
    ]
    assert payload_guard_checks[
        "position_payload_guard_check_keys_match_expected_schema"
    ]["actual"]["position_payload_nested_guard_statuses_are_ok"] == [
        "name",
        "passed",
        "expected",
        "actual",
    ]
    assert payload_guard_checks["position_payload_keys_match_expected_schema"][
        "passed"
    ] is True
    assert payload_guard_checks["position_payload_keys_match_expected_schema"][
        "actual"
    ] == payload_guard_checks["position_payload_keys_match_expected_schema"][
        "expected"
    ]
    assert payload_guard_checks["position_payload_keys_match_expected_schema"][
        "actual"
    ][-4:] == [
        "position_review_contract",
        "position_review_guard",
        "live_data_required",
        "position_payload_guard",
    ]
    assert payload["action"] == "TRIM"
    assert payload["position_state"] == "trim"
    assert payload["position_review"]["unrealized_return_pct"] == 14.0
    assert (
        payload["delivery_contract"]["channels"]["hermes"]["numeric_authority"]
        == "position_review"
    )
    assert payload["delivery_contract"]["channels"]["telegram"]["network_call"] is False
    assert payload["delivery_preview"]["guard"]["status"] == "ok"
    assert (
        payload["delivery_preview"]["channels"]["hermes"]["payload_ref"]
        == "position_review"
    )
    assert (
        payload["delivery_preview"]["channels"]["telegram"]["chunks"][0]["text"]
        == payload["text"]
    )
    preview_guard_checks = {
        check["name"]: check for check in payload["delivery_preview"]["guard"]["checks"]
    }
    assert (
        preview_guard_checks["hermes_payload_ref_matches_structured_payload"]["passed"]
        is True
    )
    assert preview_guard_checks["hermes_payload_ref_matches_structured_payload"][
        "expected"
    ] == "position_review"
    assert (
        preview_guard_checks["hermes_numeric_authority_matches_payload_ref"]["passed"]
        is True
    )
    assert preview_guard_checks["telegram_format_schema_declared"]["passed"] is True
    assert (
        preview_guard_checks["telegram_format_schema_declared"]["actual"]
        == "telegram_report_format.v1"
    )
    assert (
        preview_guard_checks["telegram_required_sections_present_in_preview"]["passed"]
        is True
    )
    assert (
        preview_guard_checks["telegram_unrequested_sections_absent_from_preview"][
            "passed"
        ]
        is True
    )
    assert preview_guard_checks["telegram_chunks_are_1_based_sequential"]["passed"] is True
    assert preview_guard_checks["telegram_message_count_matches_chunks"]["passed"] is True
    assert (
        preview_guard_checks["telegram_single_message_flag_matches_chunk_count"][
            "passed"
        ]
        is True
    )
    assert preview_guard_checks["telegram_chunk_char_counts_match_text"]["passed"] is True
    assert preview_guard_checks["telegram_chunks_are_nonempty"]["passed"] is True
    assert (
        preview_guard_checks["telegram_section_separator_preserves_preview_text"][
            "passed"
        ]
        is True
    )
    assert (
        preview_guard_checks["telegram_overflow_policy_splits_on_section_boundary"][
            "passed"
        ]
        is True
    )
    assert preview_guard_checks["telegram_chunks_fit_max_chars"]["passed"] is True
    assert preview_guard_checks["telegram_chunks_preserve_text"]["passed"] is True
    assert (
        preview_guard_checks["delivery_preview_has_no_network_side_effect"]["passed"]
        is True
    )
    assert preview_guard_checks["delivery_preview_has_no_network_side_effect"][
        "actual"
    ] == {"hermes": False, "telegram": False}
    assert preview_guard_checks["delivery_preview_has_no_send_side_effect"]["passed"] is True
    assert (
        preview_guard_checks[
            "delivery_preview_guard_check_names_match_expected_schema"
        ]["passed"]
        is True
    )
    assert preview_guard_checks[
        "delivery_preview_guard_check_names_match_expected_schema"
    ]["actual"] == preview_guard_checks[
        "delivery_preview_guard_check_names_match_expected_schema"
    ]["expected"]
    assert (
        preview_guard_checks[
            "delivery_preview_guard_check_keys_match_expected_schema"
        ]["passed"]
        is True
    )
    assert preview_guard_checks[
        "delivery_preview_guard_check_keys_match_expected_schema"
    ]["actual"] == preview_guard_checks[
        "delivery_preview_guard_check_keys_match_expected_schema"
    ]["expected"]
    assert (
        preview_guard_checks[
            "delivery_preview_payload_keys_match_expected_schema"
        ]["passed"]
        is True
    )
    assert preview_guard_checks[
        "delivery_preview_payload_keys_match_expected_schema"
    ]["actual"] == preview_guard_checks[
        "delivery_preview_payload_keys_match_expected_schema"
    ]["expected"]
    guard_checks = {
        check["name"]: check for check in payload["position_review_guard"]["checks"]
    }
    assert payload["position_review_guard"]["status"] == "ok"
    assert all(check["passed"] for check in payload["position_review_guard"]["checks"])
    assert (
        payload["delivery_contract"]["channels"]["telegram"]["required_sections"]
        == payload["position_review_contract"]["required_sections"]
    )
    assert (
        guard_checks["telegram_required_sections_match_position_review"]["passed"]
        is True
    )
    assert (
        guard_checks["position_review_sections_match_contract_order"]["passed"]
        is True
    )
    assert guard_checks["position_review_sections_match_contract_order"][
        "actual"
    ] == payload["position_review_contract"]["required_sections"]
    assert (
        guard_checks[
            "position_review_prompt_must_include_matches_expected_terms"
        ]["passed"]
        is True
    )
    assert guard_checks[
        "position_review_prompt_must_include_matches_expected_terms"
    ]["actual"] == [
        "action",
        "position_state",
        "unrealized_return_pct",
        "stop",
        "take_profit",
        "risk",
    ]
    assert (
        guard_checks[
            "position_review_prompt_contract_keys_match_expected_schema"
        ]["passed"]
        is True
    )
    assert guard_checks[
        "position_review_prompt_contract_keys_match_expected_schema"
    ]["actual"] == [
        "numeric_authority",
        "llm_role",
        "must_include",
    ]
    assert (
        guard_checks[
            "position_review_prompt_contract_identity_matches_expected"
        ]["passed"]
        is True
    )
    assert guard_checks[
        "position_review_prompt_contract_identity_matches_expected"
    ]["actual"] == {
        "numeric_authority": "Use position_review numeric fields as source of truth.",
        "llm_role": "Summarize hold, trim, exit, or stop rationale only.",
    }
    assert (
        guard_checks["delivery_contract_has_no_network_side_effect"]["passed"]
        is True
    )
    assert guard_checks["delivery_contract_has_no_network_side_effect"][
        "actual"
    ] == {"hermes": False, "telegram": False}
    assert (
        guard_checks["delivery_contract_has_no_send_side_effect"]["passed"]
        is True
    )
    assert guard_checks["delivery_contract_has_no_send_side_effect"][
        "expected"
    ] is False
    assert guard_checks["delivery_contract_has_no_send_side_effect"][
        "actual"
    ] == {"hermes": False, "telegram": False}
    assert (
        guard_checks["delivery_contract_keys_match_expected_schema"]["passed"]
        is True
    )
    assert guard_checks["delivery_contract_keys_match_expected_schema"][
        "actual"
    ] == guard_checks["delivery_contract_keys_match_expected_schema"][
        "expected"
    ]
    assert guard_checks["delivery_channel_formats_match_expected"]["passed"] is True
    assert guard_checks["delivery_channel_formats_match_expected"]["actual"] == {
        "hermes": "structured_json_plus_text",
        "telegram": "plain_text",
    }
    assert (
        guard_checks["delivery_cron_intents_match_report_intent_registry"][
            "passed"
        ]
        is True
    )
    assert guard_checks[
        "delivery_cron_intents_match_report_intent_registry"
    ]["actual"] == [
        "pre_market_swing_report",
        "intraday_risk_watch",
        "post_market_review",
    ]
    assert (
        guard_checks["position_review_telegram_max_chars_matches_expected"][
            "passed"
        ]
        is True
    )
    assert guard_checks["position_review_telegram_max_chars_matches_expected"][
        "actual"
    ] == 3900
    assert (
        guard_checks[
            "position_review_telegram_schema_version_matches_expected"
        ]["passed"]
        is True
    )
    assert guard_checks[
        "position_review_telegram_schema_version_matches_expected"
    ]["actual"] == "telegram_report_format.v1"
    assert (
        guard_checks[
            "position_review_telegram_chunking_contract_matches_expected"
        ]["passed"]
        is True
    )
    assert guard_checks[
        "position_review_telegram_chunking_contract_matches_expected"
    ]["actual"] == {
        "overflow_policy": "split_on_section_boundary",
        "section_separator": "\n\n",
        "chunk_indexing": "1_based",
    }
    assert (
        guard_checks[
            "position_review_guard_check_names_match_expected_schema"
        ]["passed"]
        is True
    )
    assert guard_checks[
        "position_review_guard_check_names_match_expected_schema"
    ]["actual"] == guard_checks[
        "position_review_guard_check_names_match_expected_schema"
    ]["expected"]
    assert (
        guard_checks[
            "position_review_guard_check_keys_match_expected_schema"
        ]["passed"]
        is True
    )
    assert guard_checks[
        "position_review_guard_check_keys_match_expected_schema"
    ]["actual"] == guard_checks[
        "position_review_guard_check_keys_match_expected_schema"
    ]["expected"]
    assert guard_checks[
        "position_review_guard_check_keys_match_expected_schema"
    ]["actual"]["special_check_keys"]["telegram_text_fits_single_message"] == [
        "name",
        "passed",
        "expected_max_chars",
        "actual_chars",
    ]
    assert (
        guard_checks["position_review_guard_keys_match_expected_schema"]["passed"]
        is True
    )
    assert guard_checks["position_review_guard_keys_match_expected_schema"][
        "actual"
    ] == ["status", "checks"]
    assert (
        guard_checks["position_review_text_reflects_review_numeric_fields"]["passed"]
        is True
    )
    assert guard_checks["position_review_text_reflects_review_numeric_fields"][
        "expected"
    ] == {
        "action": payload["position_review"]["action"],
        "position_state": payload["position_review"]["position_state"],
        "unrealized_return_pct": payload["position_review"][
            "unrealized_return_pct"
        ],
    }
    assert guard_checks["position_review_text_reflects_review_numeric_fields"][
        "actual"
    ] == {
        "decision_line_present": True,
        "unrealized_return_line_present": True,
    }
    assert guard_checks["telegram_required_sections_match_position_review"][
        "expected"
    ] == payload["position_review_contract"]["required_sections"]
    assert guard_checks["telegram_required_sections_match_position_review"][
        "actual"
    ] == payload["delivery_contract"]["channels"]["telegram"]["required_sections"]
    assert (
        guard_checks["position_review_contract_keys_match_expected_schema"][
            "passed"
        ]
        is True
    )
    assert guard_checks["position_review_contract_keys_match_expected_schema"][
        "actual"
    ] == [
        "name",
        "trigger",
        "decision_focus",
        "required_sections",
        "network_call",
        "order_submission",
    ]
    assert (
        guard_checks["position_review_contract_has_no_network_side_effect"][
            "passed"
        ]
        is True
    )
    assert guard_checks["position_review_contract_has_no_network_side_effect"][
        "actual"
    ] is False
    assert (
        guard_checks["position_review_contract_identity_matches_expected"][
            "passed"
        ]
        is True
    )
    assert guard_checks["position_review_contract_identity_matches_expected"][
        "actual"
    ] == {
        "name": "position_review",
        "trigger": "manual_or_scheduled_position_check",
        "decision_focus": "hold_trim_exit_or_stop_review",
    }
    assert (
        guard_checks[
            "position_review_contract_required_sections_match_expected"
        ]["passed"]
        is True
    )
    assert guard_checks[
        "position_review_contract_required_sections_match_expected"
    ]["actual"] == [
        "Position",
        "Decision",
        "Rationale",
        "Stop",
        "Take Profit",
        "Risk",
    ]
    assert (
        guard_checks[
            "position_review_contract_has_no_order_submission_side_effect"
        ]["passed"]
        is True
    )
    assert guard_checks[
        "position_review_contract_has_no_order_submission_side_effect"
    ]["actual"] is False
    assert guard_checks["telegram_text_fits_single_message"]["passed"] is True
    assert guard_checks["telegram_text_fits_single_message"][
        "expected_max_chars"
    ] == payload["delivery_contract"]["channels"]["telegram"]["max_chars"]
    assert guard_checks["telegram_text_fits_single_message"]["actual_chars"] == len(
        payload["text"]
    )
    assert sections["Stop"]
    assert sections["Take Profit"]
    assert payload["live_data_required"] is False


def test_position_review_report_propagates_live_review_boundary(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    review = reporting.evaluate_position(
        asset="TQQQ",
        entry_price=100,
        current_price=114,
        size=3,
    )
    live_review = {
        **review,
        "live_data_required": True,
        "position_management_contract": {
            **review["position_management_contract"],
            "live_data_required": True,
        },
    }
    monkeypatch.setattr(
        reporting,
        "evaluate_position",
        lambda asset="TQQQ", entry_price=None, current_price=None, size=None: live_review,
    )

    payload = generate_position_review_report(
        "TQQQ",
        entry_price=100,
        current_price=114,
        size=3,
    )
    guard_checks = {
        check["name"]: check for check in payload["position_payload_guard"]["checks"]
    }

    assert payload["live_data_required"] is True
    assert payload["position_review"]["live_data_required"] is True
    assert guard_checks["position_payload_live_data_required_matches_expected"][
        "passed"
    ] is True
    assert guard_checks["position_payload_live_data_required_matches_expected"][
        "expected"
    ] is True
    assert guard_checks["position_payload_live_data_required_matches_expected"][
        "actual"
    ] is True
    assert payload["position_payload_guard"]["status"] == "ok"


def test_delivery_preview_splits_telegram_text_on_section_boundaries() -> None:
    text = "Header\n\n" + "\n\n".join(
        f"Section {index}:\n- {'x' * 70}" for index in range(1, 5)
    )
    contract = reporting._delivery_contract(
        telegram_required_sections=[f"Section {index}" for index in range(1, 5)],
        telegram_max_chars=95,
    )
    preview = reporting._delivery_preview(
        text=text,
        delivery_contract=contract,
        structured_payload_key="latest_signal_report",
    )
    chunks = preview["channels"]["telegram"]["chunks"]

    assert preview["guard"]["status"] == "ok"
    assert preview["channels"]["telegram"]["message_count"] > 1
    assert preview["channels"]["telegram"]["schema_version"] == "telegram_report_format.v1"
    assert preview["channels"]["telegram"]["chunk_indexing"] == "1_based"
    preview_guard_checks = {
        check["name"]: check for check in preview["guard"]["checks"]
    }
    assert (
        preview_guard_checks["hermes_payload_ref_matches_structured_payload"]["passed"]
        is True
    )
    assert (
        preview_guard_checks["hermes_numeric_authority_matches_payload_ref"]["passed"]
        is True
    )
    assert preview_guard_checks["telegram_format_schema_declared"]["passed"] is True
    assert (
        preview_guard_checks["telegram_format_schema_declared"]["actual"]
        == "telegram_report_format.v1"
    )
    assert (
        preview_guard_checks["telegram_required_sections_present_in_preview"]["passed"]
        is True
    )
    assert (
        preview_guard_checks["telegram_unrequested_sections_absent_from_preview"][
            "passed"
        ]
        is True
    )
    assert preview_guard_checks["telegram_chunks_are_1_based_sequential"]["passed"] is True
    assert preview_guard_checks["telegram_message_count_matches_chunks"]["passed"] is True
    assert (
        preview_guard_checks["telegram_single_message_flag_matches_chunk_count"][
            "actual"
        ]
        is False
    )
    assert preview_guard_checks["telegram_chunk_char_counts_match_text"]["passed"] is True
    assert all(
        item["chars"] == item["text_len"]
        for item in preview_guard_checks["telegram_chunk_char_counts_match_text"][
            "actual"
        ]
    )
    assert preview_guard_checks["telegram_chunks_are_nonempty"]["passed"] is True
    assert all(
        item["text_empty"] is False and item["chars"] > 0
        for item in preview_guard_checks["telegram_chunks_are_nonempty"]["actual"]
    )
    assert (
        preview_guard_checks["telegram_section_separator_preserves_preview_text"][
            "passed"
        ]
        is True
    )
    assert (
        preview_guard_checks["telegram_overflow_policy_splits_on_section_boundary"][
            "passed"
        ]
        is True
    )
    assert preview_guard_checks["telegram_overflow_policy_splits_on_section_boundary"][
        "actual"
    ]["continuation_chunk_starts"] == [
        chunk["text"].splitlines()[0]
        for chunk in chunks[1:]
    ]
    assert preview_guard_checks["telegram_chunks_fit_max_chars"]["passed"] is True
    assert preview_guard_checks["telegram_chunks_preserve_text"]["passed"] is True
    assert (
        preview_guard_checks["delivery_preview_has_no_network_side_effect"]["passed"]
        is True
    )
    assert preview_guard_checks["delivery_preview_has_no_network_side_effect"][
        "actual"
    ] == {"hermes": False, "telegram": False}
    assert preview_guard_checks["delivery_preview_has_no_send_side_effect"]["passed"] is True
    assert (
        preview_guard_checks[
            "delivery_preview_guard_check_names_match_expected_schema"
        ]["passed"]
        is True
    )
    assert preview_guard_checks[
        "delivery_preview_guard_check_names_match_expected_schema"
    ]["actual"] == preview_guard_checks[
        "delivery_preview_guard_check_names_match_expected_schema"
    ]["expected"]
    assert (
        preview_guard_checks[
            "delivery_preview_guard_check_keys_match_expected_schema"
        ]["passed"]
        is True
    )
    assert preview_guard_checks[
        "delivery_preview_guard_check_keys_match_expected_schema"
    ]["actual"] == preview_guard_checks[
        "delivery_preview_guard_check_keys_match_expected_schema"
    ]["expected"]
    assert (
        preview_guard_checks[
            "delivery_preview_payload_keys_match_expected_schema"
        ]["passed"]
        is True
    )
    assert preview_guard_checks[
        "delivery_preview_payload_keys_match_expected_schema"
    ]["actual"] == preview_guard_checks[
        "delivery_preview_payload_keys_match_expected_schema"
    ]["expected"]
    assert all(chunk["chars"] <= 95 for chunk in chunks)
    assert "\n\n".join(chunk["text"] for chunk in chunks) == text


def test_position_review_report_trims_and_uppercases_asset_identity() -> None:
    payload = generate_position_review_report(
        " tqqq ",
        entry_price=100,
        current_price=114,
        size=3,
    )

    assert payload["asset"] == "TQQQ"
    assert payload["position_review"]["asset"] == "TQQQ"
    assert payload["underlying"] == "QQQ"
    assert " tqqq " not in payload["text"]
    assert payload["position_payload_guard"]["status"] == "ok"


@pytest.mark.parametrize("asset", ["   ", None, 123])
def test_position_review_report_rejects_invalid_asset_identity(asset) -> None:
    with pytest.raises(ValueError, match="asset must be a nonempty string"):
        generate_position_review_report(
            asset,
            entry_price=100,
            current_price=114,
            size=3,
        )


def test_position_review_report_rejects_asset_control_character() -> None:
    with pytest.raises(ValueError, match="asset must not contain control characters"):
        generate_position_review_report(
            "TQQQ\n",
            entry_price=100,
            current_price=114,
            size=3,
        )


@pytest.mark.parametrize(
    ("overrides", "expected_error"),
    [
        ({"entry_price": 0}, "entry_price must be a positive finite number"),
        ({"entry_price": float("inf")}, "entry_price must be a positive finite number"),
        ({"current_price": False}, "current_price must be a positive finite number"),
        ({"current_price": float("nan")}, "current_price must be a positive finite number"),
        ({"size": "3"}, "size must be a positive finite number"),
        ({"size": -1}, "size must be a positive finite number"),
    ],
)
def test_position_review_report_rejects_invalid_numeric_inputs_before_position_evaluation(
    overrides,
    expected_error,
    monkeypatch,
) -> None:
    def unexpected_position_call(*args, **kwargs):
        del args, kwargs
        raise AssertionError("position evaluation should not run for invalid inputs")

    monkeypatch.setattr(reporting, "evaluate_position", unexpected_position_call)
    payload = {
        "asset": "TQQQ",
        "entry_price": 100,
        "current_price": 114,
        "size": 3,
    }
    payload.update(overrides)

    with pytest.raises(ValueError, match=expected_error):
        generate_position_review_report(**payload)


def test_latest_signal_report_snapshot_has_no_local_artifact_paths() -> None:
    for value in iter_nested_strings(load_golden()):
        lowered = value.lower()
        assert "/Users/" not in value
        assert "file://" not in value
        assert not value.startswith("~/")
        assert ".sqlite" not in lowered
        assert ".sqlite3" not in lowered


def test_harness_generates_latest_signal_report(tmp_path: Path) -> None:
    audit_path = tmp_path / "audit.jsonl"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "generate_latest_signal_report",
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

    assert json.loads(result.stdout) == load_golden()
    assert audit_path.exists()


def test_harness_generates_report_with_chart_ref(tmp_path: Path) -> None:
    audit_path = tmp_path / "audit.jsonl"
    chart_dir = tmp_path / "charts"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "generate_latest_signal_report",
            "--input-json",
            json.dumps(
                {
                    "asset": "TQQQ",
                    "include_chart": True,
                    "chart_output_dir": str(chart_dir),
                }
            ),
            "--audit-log-path",
            str(audit_path),
        ],
        check=True,
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    payload = json.loads(result.stdout)

    assert payload["latest_signal_report"]["chart_ref"]["ref_type"] == "CHART"
    assert payload["chart_code_guard"]["status"] == "ok"
    assert (chart_dir / "QQQ_1d.png").exists()


def test_harness_generates_position_review_report(tmp_path: Path) -> None:
    audit_path = tmp_path / "audit.jsonl"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "generate_position_review_report",
            "--input-json",
            json.dumps(
                {
                    "asset": "TQQQ",
                    "entry_price": 100,
                    "current_price": 114,
                    "size": 3,
                }
            ),
            "--audit-log-path",
            str(audit_path),
        ],
        check=True,
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    payload = json.loads(result.stdout)

    assert payload["position_review_guard"]["status"] == "ok"
    assert payload["position_state"] == "trim"
    assert audit_path.exists()


def test_harness_rejects_blank_position_review_asset_with_failure_audit(
    tmp_path: Path,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    input_payload = {
        "asset": "   ",
        "entry_price": 100,
        "current_price": 114,
        "size": 3,
    }
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "generate_position_review_report",
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
    assert event["resource_id"] == "generate_position_review_report"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "asset must be a nonempty string" in event["details"]["error"]


@pytest.mark.parametrize("asset", [None, 123])
def test_harness_rejects_position_review_asset_type_with_failure_audit(
    tmp_path: Path,
    asset,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    input_payload = {
        "asset": asset,
        "entry_price": 100,
        "current_price": 114,
        "size": 3,
    }
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "generate_position_review_report",
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
    assert event["resource_id"] == "generate_position_review_report"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "asset must be a nonempty string" in event["details"]["error"]


def test_harness_rejects_position_review_asset_control_character_with_failure_audit(
    tmp_path: Path,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    input_payload = {
        "asset": "TQQQ\n",
        "entry_price": 100,
        "current_price": 114,
        "size": 3,
    }
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "generate_position_review_report",
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
    assert event["resource_id"] == "generate_position_review_report"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "asset must not contain control characters" in event["details"]["error"]


@pytest.mark.parametrize(
    ("input_payload", "expected_error"),
    [
        (
            {"asset": "TQQQ", "entry_price": 0, "current_price": 114, "size": 3},
            "entry_price must be a positive finite number",
        ),
        (
            {"asset": "TQQQ", "entry_price": 100, "current_price": False, "size": 3},
            "current_price must be a positive finite number",
        ),
        (
            {"asset": "TQQQ", "entry_price": 100, "current_price": 114, "size": "3"},
            "size must be a positive finite number",
        ),
    ],
)
def test_harness_rejects_position_review_numeric_inputs_with_failure_audit(
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
            "generate_position_review_report",
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
    assert event["resource_id"] == "generate_position_review_report"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert expected_error in event["details"]["error"]


def test_harness_generates_cron_prompt_pack(tmp_path: Path) -> None:
    audit_path = tmp_path / "audit.jsonl"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "generate_cron_prompt_pack",
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

    assert payload["cron_prompt_guard"]["status"] == "ok"
    assert payload["cron_prompt_contract"]["scheduler_added"] is False
    assert audit_path.exists()


def test_harness_rejects_unsupported_report_intent_with_failure_audit(
    tmp_path: Path,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    unsupported_intent = "opening_gap_scalp"
    expected_allowed = ", ".join(sorted(reporting.REPORT_INTENTS))
    input_payload = {"asset": "TQQQ", "report_intent": unsupported_intent}
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "generate_latest_signal_report",
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
    assert f"unsupported report_intent: {unsupported_intent}" in result.stderr
    assert f"allowed: {expected_allowed}" in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "generate_latest_signal_report"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert f"unsupported report_intent: {unsupported_intent}" in event["details"][
        "error"
    ]
    assert f"allowed: {expected_allowed}" in event["details"]["error"]


def test_harness_rejects_invalid_report_intent_with_failure_audit(
    tmp_path: Path,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    input_payload = {"asset": "TQQQ", "report_intent": "   "}
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "generate_latest_signal_report",
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
    assert "report_intent must be a nonempty string" in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "generate_latest_signal_report"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "report_intent must be a nonempty string" in event["details"]["error"]


def test_harness_rejects_report_intent_type_with_failure_audit(
    tmp_path: Path,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    input_payload = {"asset": "TQQQ", "report_intent": 123}
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "generate_latest_signal_report",
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
    assert "report_intent must be a nonempty string" in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "generate_latest_signal_report"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "report_intent must be a nonempty string" in event["details"]["error"]


def test_harness_rejects_report_intent_control_character_with_failure_audit(
    tmp_path: Path,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    input_payload = {"asset": "TQQQ", "report_intent": "intraday_risk_watch\n"}
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "generate_latest_signal_report",
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
    assert "report_intent must not contain control characters" in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "generate_latest_signal_report"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "report_intent must not contain control characters" in event["details"][
        "error"
    ]


def test_harness_rejects_blank_latest_report_asset_with_failure_audit(
    tmp_path: Path,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    chart_dir = tmp_path / "chart"
    input_payload = {
        "asset": "   ",
        "include_chart": True,
        "chart_output_dir": str(chart_dir),
    }
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "generate_latest_signal_report",
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
    assert not chart_dir.exists()
    assert event["actor"] == "harness"
    assert event["resource_id"] == "generate_latest_signal_report"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "asset must be a nonempty string" in event["details"]["error"]


def test_harness_rejects_latest_report_asset_type_with_failure_audit(
    tmp_path: Path,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    chart_dir = tmp_path / "chart"
    input_payload = {
        "asset": 123,
        "include_chart": True,
        "chart_output_dir": str(chart_dir),
    }
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "generate_latest_signal_report",
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
    assert not chart_dir.exists()
    assert event["actor"] == "harness"
    assert event["resource_id"] == "generate_latest_signal_report"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "asset must be a nonempty string" in event["details"]["error"]


def test_harness_rejects_latest_report_asset_control_character_with_failure_audit(
    tmp_path: Path,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    chart_dir = tmp_path / "chart"
    input_payload = {
        "asset": "TQQQ\n",
        "include_chart": True,
        "chart_output_dir": str(chart_dir),
    }
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "generate_latest_signal_report",
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
    assert not chart_dir.exists()
    assert event["actor"] == "harness"
    assert event["resource_id"] == "generate_latest_signal_report"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "asset must not contain control characters" in event["details"]["error"]


def test_harness_rejects_blank_latest_report_timeframe_with_failure_audit(
    tmp_path: Path,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    chart_dir = tmp_path / "chart"
    input_payload = {
        "asset": "TQQQ",
        "timeframe": "   ",
        "include_chart": True,
        "chart_output_dir": str(chart_dir),
    }
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "generate_latest_signal_report",
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
    assert "timeframe must be a nonempty string" in result.stderr
    assert not chart_dir.exists()
    assert event["actor"] == "harness"
    assert event["resource_id"] == "generate_latest_signal_report"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "timeframe must be a nonempty string" in event["details"]["error"]


def test_harness_rejects_latest_report_timeframe_type_with_failure_audit(
    tmp_path: Path,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    chart_dir = tmp_path / "chart"
    input_payload = {
        "asset": "TQQQ",
        "timeframe": 123,
        "include_chart": True,
        "chart_output_dir": str(chart_dir),
    }
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "generate_latest_signal_report",
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
    assert "timeframe must be a nonempty string" in result.stderr
    assert not chart_dir.exists()
    assert event["actor"] == "harness"
    assert event["resource_id"] == "generate_latest_signal_report"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "timeframe must be a nonempty string" in event["details"]["error"]


def test_harness_rejects_latest_report_timeframe_control_character_with_failure_audit(
    tmp_path: Path,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    chart_dir = tmp_path / "chart"
    input_payload = {
        "asset": "TQQQ",
        "timeframe": "swing_3d_10d\n",
        "include_chart": True,
        "chart_output_dir": str(chart_dir),
    }
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "generate_latest_signal_report",
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
    assert not chart_dir.exists()
    assert event["actor"] == "harness"
    assert event["resource_id"] == "generate_latest_signal_report"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "timeframe must not contain control characters" in event["details"]["error"]


def test_harness_rejects_blank_cron_prompt_asset_with_failure_audit(
    tmp_path: Path,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    input_payload = {"asset": "   "}
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "generate_cron_prompt_pack",
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
    assert event["resource_id"] == "generate_cron_prompt_pack"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "asset must be a nonempty string" in event["details"]["error"]


def test_harness_rejects_cron_prompt_asset_type_with_failure_audit(
    tmp_path: Path,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    input_payload = {"asset": 123}
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "generate_cron_prompt_pack",
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
    assert event["resource_id"] == "generate_cron_prompt_pack"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "asset must be a nonempty string" in event["details"]["error"]


def test_harness_rejects_cron_prompt_asset_control_character_with_failure_audit(
    tmp_path: Path,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    input_payload = {"asset": "TQQQ\n"}
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "generate_cron_prompt_pack",
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
    assert event["resource_id"] == "generate_cron_prompt_pack"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "asset must not contain control characters" in event["details"]["error"]


def test_harness_rejects_blank_cron_prompt_timeframe_with_failure_audit(
    tmp_path: Path,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    input_payload = {"asset": "TQQQ", "timeframe": "   "}
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "generate_cron_prompt_pack",
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
    assert "timeframe must be a nonempty string" in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "generate_cron_prompt_pack"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "timeframe must be a nonempty string" in event["details"]["error"]


def test_harness_rejects_cron_prompt_timeframe_type_with_failure_audit(
    tmp_path: Path,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    input_payload = {"asset": "TQQQ", "timeframe": 123}
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "generate_cron_prompt_pack",
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
    assert "timeframe must be a nonempty string" in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "generate_cron_prompt_pack"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "timeframe must be a nonempty string" in event["details"]["error"]


def test_harness_rejects_cron_prompt_timeframe_control_character_with_failure_audit(
    tmp_path: Path,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    input_payload = {"asset": "TQQQ", "timeframe": "swing_3d_10d\n"}
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "generate_cron_prompt_pack",
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
    assert event["resource_id"] == "generate_cron_prompt_pack"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "timeframe must not contain control characters" in event["details"]["error"]


def test_harness_rejects_non_bool_include_position_review_with_failure_audit(
    tmp_path: Path,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    input_payload = {"asset": "TQQQ", "include_position_review": "false"}
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "generate_cron_prompt_pack",
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
    assert "include_position_review must be a boolean" in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "generate_cron_prompt_pack"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "include_position_review must be a boolean" in event["details"]["error"]


@pytest.mark.parametrize("include_position_review", [0, None])
def test_harness_rejects_remaining_non_bool_include_position_review_with_failure_audit(
    tmp_path: Path,
    include_position_review: object,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    input_payload = {
        "asset": "TQQQ",
        "include_position_review": include_position_review,
    }
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "generate_cron_prompt_pack",
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
    assert "include_position_review must be a boolean" in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "generate_cron_prompt_pack"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "include_position_review must be a boolean" in event["details"]["error"]


def test_harness_rejects_non_bool_include_chart_with_failure_audit(
    tmp_path: Path,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    chart_dir = tmp_path / "charts"
    input_payload = {
        "asset": "TQQQ",
        "include_chart": "false",
        "chart_output_dir": str(chart_dir),
    }
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "generate_latest_signal_report",
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
    assert "include_chart must be a boolean" in result.stderr
    assert not chart_dir.exists()
    assert event["actor"] == "harness"
    assert event["resource_id"] == "generate_latest_signal_report"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "include_chart must be a boolean" in event["details"]["error"]


@pytest.mark.parametrize("include_chart", [0, 1, None])
def test_harness_rejects_remaining_non_bool_include_chart_with_failure_audit(
    tmp_path: Path,
    include_chart,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    chart_dir = tmp_path / "charts"
    input_payload = {
        "asset": "TQQQ",
        "include_chart": include_chart,
        "chart_output_dir": str(chart_dir),
    }
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "generate_latest_signal_report",
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
    assert "include_chart must be a boolean" in result.stderr
    assert not chart_dir.exists()
    assert event["actor"] == "harness"
    assert event["resource_id"] == "generate_latest_signal_report"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "include_chart must be a boolean" in event["details"]["error"]


def test_harness_rejects_invalid_extra_evidence_cards_container_with_failure_audit(
    tmp_path: Path,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    chart_dir = tmp_path / "charts"
    input_payload = {
        "asset": "TQQQ",
        "include_chart": True,
        "chart_output_dir": str(chart_dir),
        "extra_evidence_cards": "not-a-list",
    }
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "generate_latest_signal_report",
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
    assert "extra_evidence_cards must be a list of objects" in result.stderr
    assert not chart_dir.exists()
    assert event["actor"] == "harness"
    assert event["resource_id"] == "generate_latest_signal_report"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "extra_evidence_cards must be a list of objects" in event["details"][
        "error"
    ]


def test_harness_rejects_extra_evidence_card_non_object_with_failure_audit(
    tmp_path: Path,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    chart_dir = tmp_path / "charts"
    input_payload = {
        "asset": "TQQQ",
        "include_chart": True,
        "chart_output_dir": str(chart_dir),
        "extra_evidence_cards": ["not-an-object"],
    }
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "generate_latest_signal_report",
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
    assert "extra_evidence_cards items must be objects" in result.stderr
    assert not chart_dir.exists()
    assert event["actor"] == "harness"
    assert event["resource_id"] == "generate_latest_signal_report"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "extra_evidence_cards items must be objects" in event["details"]["error"]


def test_harness_rejects_blank_chart_timeframe_with_failure_audit(
    tmp_path: Path,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    chart_dir = tmp_path / "charts"
    input_payload = {
        "asset": "TQQQ",
        "include_chart": True,
        "chart_timeframe": "   ",
        "chart_output_dir": str(chart_dir),
    }
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "generate_latest_signal_report",
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
    assert "chart_timeframe must be a nonempty string" in result.stderr
    assert not chart_dir.exists()
    assert event["actor"] == "harness"
    assert event["resource_id"] == "generate_latest_signal_report"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "chart_timeframe must be a nonempty string" in event["details"]["error"]


def test_harness_rejects_chart_timeframe_control_character_with_failure_audit(
    tmp_path: Path,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    chart_dir = tmp_path / "charts"
    input_payload = {
        "asset": "TQQQ",
        "include_chart": True,
        "chart_timeframe": "1d\n",
        "chart_output_dir": str(chart_dir),
    }
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "generate_latest_signal_report",
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
    assert "chart_timeframe must not contain control characters" in result.stderr
    assert not chart_dir.exists()
    assert event["actor"] == "harness"
    assert event["resource_id"] == "generate_latest_signal_report"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "chart_timeframe must not contain control characters" in event["details"][
        "error"
    ]


def test_harness_rejects_chart_timeframe_type_with_failure_audit(
    tmp_path: Path,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    chart_dir = tmp_path / "charts"
    input_payload = {
        "asset": "TQQQ",
        "include_chart": True,
        "chart_timeframe": 123,
        "chart_output_dir": str(chart_dir),
    }
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "generate_latest_signal_report",
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
    assert "chart_timeframe must be a nonempty string" in result.stderr
    assert not chart_dir.exists()
    assert event["actor"] == "harness"
    assert event["resource_id"] == "generate_latest_signal_report"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "chart_timeframe must be a nonempty string" in event["details"]["error"]


def test_harness_rejects_blank_chart_output_dir_with_failure_audit(
    tmp_path: Path,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    input_payload = {
        "asset": "TQQQ",
        "include_chart": True,
        "chart_output_dir": "   ",
    }
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "generate_latest_signal_report",
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
    assert "chart_output_dir must be a nonempty string" in result.stderr
    assert event["actor"] == "harness"
    assert event["resource_id"] == "generate_latest_signal_report"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "chart_output_dir must be a nonempty string" in event["details"]["error"]


@pytest.mark.parametrize("chart_output_dir", [[], False])
def test_harness_rejects_chart_output_dir_type_with_failure_audit(
    tmp_path: Path,
    chart_output_dir,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    chart_dir = tmp_path / "charts"
    input_payload = {
        "asset": "TQQQ",
        "include_chart": True,
        "chart_output_dir": chart_output_dir,
    }
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "generate_latest_signal_report",
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
    assert "chart_output_dir must be a nonempty string" in result.stderr
    assert not chart_dir.exists()
    assert event["actor"] == "harness"
    assert event["resource_id"] == "generate_latest_signal_report"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "chart_output_dir must be a nonempty string" in event["details"]["error"]


def test_harness_rejects_chart_output_dir_control_character_with_failure_audit(
    tmp_path: Path,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    chart_dir = tmp_path / "charts"
    input_payload = {
        "asset": "TQQQ",
        "include_chart": True,
        "chart_output_dir": f"{chart_dir}\n",
    }
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "halo_swing_mcp.harness",
            "generate_latest_signal_report",
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
    assert "chart_output_dir must not contain control characters" in result.stderr
    assert not chart_dir.exists()
    assert event["actor"] == "harness"
    assert event["resource_id"] == "generate_latest_signal_report"
    assert event["outcome"] == "failure"
    assert event["details"]["input"] == input_payload
    assert "output_summary" not in event["details"]
    assert "chart_output_dir must not contain control characters" in event["details"][
        "error"
    ]
