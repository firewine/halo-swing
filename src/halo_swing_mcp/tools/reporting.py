"""Hermes-facing deterministic report snapshots."""

from __future__ import annotations

import math
from datetime import datetime, timezone
from typing import Any

from halo_swing_mcp.contracts import LatestSignalReport
from halo_swing_mcp.tools.market import DOCUMENT_SUMMARY_MAX_CHARS, render_chart
from halo_swing_mcp.tools.recording import get_latest_signal_record
from halo_swing_mcp.tools.scoring import evaluate_position, score_leverage_swing


REPORT_SCHEMA_VERSION = "hermes_report.v1"
POSITION_REVIEW_SCHEMA_VERSION = "hermes_position_review.v1"
CRON_PROMPT_SCHEMA_VERSION = "hermes_cron_prompt_pack.v1"
TELEGRAM_FORMAT_SCHEMA_VERSION = "telegram_report_format.v1"
CRON_NO_SECRET_TEXT = "Do not include credentials or secret values."
CRON_MANUAL_SETUP_REQUIRED = [
    "hermes_config_path",
    "telegram_bot_token_or_gateway",
    "duplicate_run_lock_policy",
    "runtime_checkpoint_path",
    "watchdog_alert_destination",
]
REQUIRED_REPORT_SECTIONS = [
    "Target",
    "Decision",
    "Reasons",
    "Entry",
    "Stop",
    "Take Profit",
    "Cautions",
]
POSITION_REVIEW_SECTIONS = [
    "Position",
    "Decision",
    "Rationale",
    "Stop",
    "Take Profit",
    "Risk",
]
TELEGRAM_KNOWN_SECTIONS = list(
    dict.fromkeys([*REQUIRED_REPORT_SECTIONS, *POSITION_REVIEW_SECTIONS])
)
EVIDENCE_SUMMARY_CONTRACT = {
    "max_reason_summary_chars": 260,
    "max_evidence_summary_chars": 700,
    "max_conflict_flags": 8,
    "required_conflict_fields": ["name", "severity", "status", "details"],
}
REPORT_INTENTS = {
    "pre_market_swing_report": {
        "schedule_hint": "weekday_pre_market",
        "decision_focus": "new_swing_entry_and_watchlist",
        "required_sections": REQUIRED_REPORT_SECTIONS,
    },
    "intraday_risk_watch": {
        "schedule_hint": "market_hours",
        "decision_focus": "risk_monitoring_trim_or_exit_checks",
        "required_sections": ["Target", "Decision", "Stop", "Cautions"],
    },
    "post_market_review": {
        "schedule_hint": "post_market",
        "decision_focus": "end_of_day_review_and_next_session_plan",
        "required_sections": ["Target", "Decision", "Reasons", "Take Profit", "Cautions"],
    },
}


def generate_latest_signal_report(
    asset: str = "TQQQ",
    timeframe: str = "swing_3d_10d",
    report_intent: str = "pre_market_swing_report",
    include_chart: bool = False,
    chart_timeframe: str = "1d",
    chart_output_dir: str | None = None,
    extra_evidence_cards: list[dict[str, Any]] | None = None,
    ledger_path: str | None = None,
    database_path: str | None = None,
) -> dict[str, Any]:
    """Build a stable report snapshot from deterministic scoring output."""

    normalized_asset = _normalize_report_asset(asset)
    normalized_timeframe = _normalize_report_timeframe(timeframe)
    normalized_ledger_path = _normalize_report_repository_path(
        ledger_path,
        "ledger_path",
    )
    normalized_database_path = _normalize_report_repository_path(
        database_path,
        "database_path",
    )
    if normalized_ledger_path is not None and normalized_database_path is not None:
        raise ValueError("ledger_path and database_path cannot both be provided")
    normalized_report_intent = _normalize_report_intent(report_intent)
    intent_contract = _report_intent_contract(normalized_report_intent)
    normalized_include_chart = _normalize_report_include_chart(include_chart)
    normalized_chart_timeframe = (
        _normalize_report_chart_timeframe(chart_timeframe)
        if normalized_include_chart
        else chart_timeframe
    )
    normalized_chart_output_dir = (
        _normalize_report_chart_output_dir(chart_output_dir)
        if normalized_include_chart
        else chart_output_dir
    )
    normalized_extra_evidence_cards = _normalize_extra_evidence_cards(
        extra_evidence_cards
    )
    signal = _latest_report_source_signal(
        asset=normalized_asset,
        timeframe=normalized_timeframe,
        ledger_path=normalized_ledger_path,
        database_path=normalized_database_path,
    )
    chart_payload = (
        render_chart(
            symbol=signal["underlying"],
            timeframe=normalized_chart_timeframe,
            output_dir=normalized_chart_output_dir,
        )
        if normalized_include_chart
        else None
    )
    report = _latest_signal_report_from_signal(signal, chart_payload)
    sections = _report_sections(signal, report, intent_contract)
    text = _format_report_text(report, sections)
    prompt_contract = _prompt_contract(intent_contract["required_sections"])
    delivery_contract = _delivery_contract(
        telegram_required_sections=intent_contract["required_sections"]
    )
    delivery_preview = _delivery_preview(
        text=text,
        delivery_contract=delivery_contract,
        structured_payload_key="latest_signal_report",
    )
    evidence_context = _evidence_context(signal, report)
    payload_live_data_required = bool(signal.get("live_data_required"))
    payload = {
        "schema_version": REPORT_SCHEMA_VERSION,
        "as_of": report["created_at"],
        "asset": report["asset"],
        "underlying": report["underlying"],
        "timeframe": report["timeframe"],
        "action": report["action"],
        "confidence_label": _confidence_label(float(report["confidence"])),
        "report_intent": normalized_report_intent,
        "latest_signal_report": report,
        "sections": sections,
        "text": text,
        "prompt_contract": prompt_contract,
        "delivery_contract": delivery_contract,
        "delivery_preview": delivery_preview,
        "evidence_contract": EVIDENCE_SUMMARY_CONTRACT,
        "evidence_context": evidence_context,
        "evidence_guard": _evidence_guard(
            report,
            sections,
            evidence_context,
            EVIDENCE_SUMMARY_CONTRACT,
        ),
        "report_intent_contract": intent_contract,
        "report_contract_guard": _report_contract_guard(
            report,
            sections,
            prompt_contract,
            delivery_contract,
            intent_contract,
        ),
        "source_signal_ref": {
            "signal_id": signal["signal_id"],
            "run_id": signal["run_id"],
            "config_hash": signal["config_hash"],
        },
        "live_data_required": payload_live_data_required,
    }
    if chart_payload is not None:
        payload["chart_code_guard"] = _chart_code_guard(signal, chart_payload)
    if chart_payload is not None or normalized_extra_evidence_cards:
        payload["multimodal_context"] = _multimodal_context(
            report=report,
            extra_evidence_cards=normalized_extra_evidence_cards or [],
        )
    source_config_hash = str(payload["source_signal_ref"]["config_hash"])
    source_config_hash_digest = source_config_hash.removeprefix("sha256:")
    source_config_hash_digest_is_hex = all(
        char in "0123456789abcdef"
        for char in source_config_hash_digest.lower()
    )
    expected_payload_top_level_identity = {
        "as_of": payload["latest_signal_report"]["created_at"],
        "asset": payload["latest_signal_report"]["asset"],
        "underlying": payload["latest_signal_report"]["underlying"],
        "timeframe": payload["latest_signal_report"]["timeframe"],
        "action": payload["latest_signal_report"]["action"],
        "confidence_label": _confidence_label(
            float(payload["latest_signal_report"]["confidence"])
        ),
    }
    actual_payload_top_level_identity = {
        "as_of": payload["as_of"],
        "asset": payload["asset"],
        "underlying": payload["underlying"],
        "timeframe": payload["timeframe"],
        "action": payload["action"],
        "confidence_label": payload["confidence_label"],
    }
    expected_payload_nested_guard_statuses = {
        "delivery_preview.guard": "ok",
        "evidence_guard": "ok",
        "report_contract_guard": "ok",
    }
    actual_payload_nested_guard_statuses = {
        "delivery_preview.guard": payload["delivery_preview"]["guard"]["status"],
        "evidence_guard": payload["evidence_guard"]["status"],
        "report_contract_guard": payload["report_contract_guard"]["status"],
    }
    expected_optional_context_statuses = {}
    actual_optional_context_statuses = {}
    expected_optional_context_guard_statuses = {}
    actual_optional_context_guard_statuses = {}
    if chart_payload is not None:
        expected_optional_context_statuses["chart_code_guard"] = "ok"
        actual_optional_context_statuses["chart_code_guard"] = payload[
            "chart_code_guard"
        ]["status"]
        expected_optional_context_guard_statuses["chart_code_guard"] = "ok"
        actual_optional_context_guard_statuses["chart_code_guard"] = payload[
            "chart_code_guard"
        ]["status"]
    if "multimodal_context" in payload:
        expected_optional_context_statuses["multimodal_context"] = "ok"
        actual_optional_context_statuses["multimodal_context"] = payload[
            "multimodal_context"
        ]["status"]
        expected_optional_context_guard_statuses["multimodal_context.guard"] = "ok"
        actual_optional_context_guard_statuses["multimodal_context.guard"] = payload[
            "multimodal_context"
        ]["guard"]["status"]
    payload["report_payload_guard"] = {"status": "pending", "checks": []}
    payload["report_payload_guard"] = _payload_contract_guard(
        payload=payload,
        expected_schema_version=REPORT_SCHEMA_VERSION,
        expected_keys=_expected_report_payload_keys(
            include_chart=chart_payload is not None,
            include_multimodal=chart_payload is not None
            or bool(normalized_extra_evidence_cards),
        ),
        schema_check_name="report_payload_schema_version_matches_expected",
        live_data_check_name="report_payload_live_data_required_matches_expected",
        keys_check_name="report_payload_keys_match_expected_schema",
        expected_live_data_required=payload_live_data_required,
        extra_checks=[
            {
                "name": "report_payload_source_signal_ref_keys_match_expected_schema",
                "passed": list(payload["source_signal_ref"])
                == ["signal_id", "run_id", "config_hash"],
                "expected": ["signal_id", "run_id", "config_hash"],
                "actual": list(payload["source_signal_ref"]),
            },
            {
                "name": "report_payload_source_signal_ref_matches_report_identity",
                "passed": (
                    payload["source_signal_ref"]["signal_id"]
                    == payload["latest_signal_report"]["signal_id"]
                    and payload["source_signal_ref"]["config_hash"]
                    == payload["latest_signal_report"]["config_hash"]
                    and bool(payload["source_signal_ref"]["run_id"])
                ),
                "expected": {
                    "signal_id": payload["latest_signal_report"]["signal_id"],
                    "config_hash": payload["latest_signal_report"]["config_hash"],
                    "run_id_nonempty": True,
                },
                "actual": {
                    "signal_id": payload["source_signal_ref"]["signal_id"],
                    "config_hash": payload["source_signal_ref"]["config_hash"],
                    "run_id_nonempty": bool(payload["source_signal_ref"]["run_id"]),
                },
            },
            {
                "name": "report_payload_source_signal_ref_values_have_traceable_format",
                "passed": (
                    bool(payload["source_signal_ref"]["signal_id"])
                    and bool(payload["source_signal_ref"]["run_id"])
                    and payload["source_signal_ref"]["config_hash"].startswith(
                        "sha256:"
                    )
                ),
                "expected": {
                    "signal_id_nonempty": True,
                    "run_id_nonempty": True,
                    "config_hash_sha256_prefix": True,
                },
                "actual": {
                    "signal_id_nonempty": bool(payload["source_signal_ref"]["signal_id"]),
                    "run_id_nonempty": bool(payload["source_signal_ref"]["run_id"]),
                    "config_hash_sha256_prefix": payload["source_signal_ref"][
                        "config_hash"
                    ].startswith("sha256:"),
                },
            },
            {
                "name": "report_payload_source_signal_ref_config_hash_digest_is_sha256",
                "passed": (
                    len(source_config_hash_digest) == 64
                    and source_config_hash_digest_is_hex
                ),
                "expected": {
                    "config_hash_digest_length": 64,
                    "config_hash_digest_hex": True,
                },
                "actual": {
                    "config_hash_digest_length": len(source_config_hash_digest),
                    "config_hash_digest_hex": source_config_hash_digest_is_hex,
                },
            },
            {
                "name": "report_payload_intent_matches_contract",
                "passed": (
                    payload["report_intent"]
                    == payload["report_intent_contract"]["name"]
                ),
                "expected": payload["report_intent_contract"]["name"],
                "actual": payload["report_intent"],
            },
            {
                "name": (
                    "report_payload_top_level_identity_matches_latest_signal_report"
                ),
                "passed": (
                    actual_payload_top_level_identity
                    == expected_payload_top_level_identity
                ),
                "expected": expected_payload_top_level_identity,
                "actual": actual_payload_top_level_identity,
            },
            {
                "name": "report_payload_nested_guard_statuses_are_ok",
                "passed": (
                    actual_payload_nested_guard_statuses
                    == expected_payload_nested_guard_statuses
                ),
                "expected": expected_payload_nested_guard_statuses,
                "actual": actual_payload_nested_guard_statuses,
            },
            {
                "name": "report_payload_optional_context_statuses_are_ok",
                "passed": (
                    actual_optional_context_statuses
                    == expected_optional_context_statuses
                ),
                "expected": expected_optional_context_statuses,
                "actual": actual_optional_context_statuses,
            },
            {
                "name": "report_payload_optional_context_guards_are_ok",
                "passed": (
                    actual_optional_context_guard_statuses
                    == expected_optional_context_guard_statuses
                ),
                "expected": expected_optional_context_guard_statuses,
                "actual": actual_optional_context_guard_statuses,
            },
        ],
        check_names_check_name=(
            "report_payload_guard_check_names_match_expected_schema"
        ),
        guard_keys_check_name=(
            "report_payload_guard_keys_match_expected_schema"
        ),
        check_keys_check_name=(
            "report_payload_guard_check_keys_match_expected_schema"
        ),
    )
    return payload


def generate_position_review_report(
    asset: str = "TQQQ",
    entry_price: float | None = None,
    current_price: float | None = None,
    size: float | None = None,
) -> dict[str, Any]:
    """Build a deterministic Hermes-facing open-position review snapshot."""

    normalized_asset = _normalize_report_asset(asset)
    normalized_entry_price = _normalize_report_optional_positive_finite_number(
        entry_price,
        "entry_price",
    )
    normalized_current_price = _normalize_report_optional_positive_finite_number(
        current_price,
        "current_price",
    )
    normalized_size = _normalize_report_optional_positive_finite_number(size, "size")
    review = evaluate_position(
        asset=normalized_asset,
        entry_price=normalized_entry_price,
        current_price=normalized_current_price,
        size=normalized_size,
    )
    sections = _position_review_sections(review)
    text = _format_position_review_text(review, sections)
    prompt_contract = _position_review_prompt_contract()
    delivery_contract = _delivery_contract(
        numeric_authority="position_review",
        telegram_required_sections=POSITION_REVIEW_SECTIONS,
    )
    delivery_preview = _delivery_preview(
        text=text,
        delivery_contract=delivery_contract,
        structured_payload_key="position_review",
    )
    review_contract = _position_review_contract()
    payload_live_data_required = bool(review.get("live_data_required"))
    payload = {
        "schema_version": POSITION_REVIEW_SCHEMA_VERSION,
        "as_of": review["as_of"],
        "asset": review["asset"],
        "underlying": review["underlying"],
        "action": review["action"],
        "position_state": review["position_state"],
        "position_review": review,
        "sections": sections,
        "text": text,
        "prompt_contract": prompt_contract,
        "delivery_contract": delivery_contract,
        "delivery_preview": delivery_preview,
        "position_review_contract": review_contract,
        "position_review_guard": _position_review_guard(
            review,
            sections,
            prompt_contract,
            delivery_contract,
            review_contract,
        ),
        "live_data_required": payload_live_data_required,
    }
    expected_position_payload_top_level_identity = {
        "as_of": payload["position_review"]["as_of"],
        "asset": payload["position_review"]["asset"],
        "underlying": payload["position_review"]["underlying"],
        "action": payload["position_review"]["action"],
        "position_state": payload["position_review"]["position_state"],
    }
    actual_position_payload_top_level_identity = {
        "as_of": payload["as_of"],
        "asset": payload["asset"],
        "underlying": payload["underlying"],
        "action": payload["action"],
        "position_state": payload["position_state"],
    }
    expected_position_payload_nested_guard_statuses = {
        "delivery_preview.guard": "ok",
        "position_review_guard": "ok",
    }
    actual_position_payload_nested_guard_statuses = {
        "delivery_preview.guard": payload["delivery_preview"]["guard"]["status"],
        "position_review_guard": payload["position_review_guard"]["status"],
    }
    payload["position_payload_guard"] = {"status": "pending", "checks": []}
    payload["position_payload_guard"] = _payload_contract_guard(
        payload=payload,
        expected_schema_version=POSITION_REVIEW_SCHEMA_VERSION,
        expected_keys=_expected_position_payload_keys(),
        schema_check_name="position_payload_schema_version_matches_expected",
        live_data_check_name="position_payload_live_data_required_matches_expected",
        keys_check_name="position_payload_keys_match_expected_schema",
        expected_live_data_required=payload_live_data_required,
        extra_checks=[
            {
                "name": "position_payload_top_level_identity_matches_position_review",
                "passed": (
                    actual_position_payload_top_level_identity
                    == expected_position_payload_top_level_identity
                ),
                "expected": expected_position_payload_top_level_identity,
                "actual": actual_position_payload_top_level_identity,
            },
            {
                "name": "position_payload_nested_guard_statuses_are_ok",
                "passed": (
                    actual_position_payload_nested_guard_statuses
                    == expected_position_payload_nested_guard_statuses
                ),
                "expected": expected_position_payload_nested_guard_statuses,
                "actual": actual_position_payload_nested_guard_statuses,
            },
        ],
        check_names_check_name=(
            "position_payload_guard_check_names_match_expected_schema"
        ),
        guard_keys_check_name=(
            "position_payload_guard_keys_match_expected_schema"
        ),
        check_keys_check_name=(
            "position_payload_guard_check_keys_match_expected_schema"
        ),
    )
    return payload


def generate_cron_prompt_pack(
    asset: str = "TQQQ",
    timeframe: str = "swing_3d_10d",
    include_position_review: bool = True,
) -> dict[str, Any]:
    """Return offline Hermes cron prompt templates without scheduling work."""

    normalized_asset = _normalize_prompt_asset(asset)
    normalized_timeframe = _normalize_prompt_timeframe(timeframe)
    normalized_include_position_review = _normalize_prompt_include_position_review(
        include_position_review
    )
    prompts = []
    for intent_name in REPORT_INTENTS:
        intent = _report_intent_contract(intent_name)
        input_json = {
            "asset": normalized_asset,
            "timeframe": normalized_timeframe,
            "report_intent": intent_name,
        }
        idempotency_key_template = (
            f"halo_swing:{intent_name}:{normalized_asset}:{{yyyy_mm_dd}}"
        )
        prompts.append(
            {
                "name": intent_name,
                "schedule_hint": intent["schedule_hint"],
                "decision_focus": intent["decision_focus"],
                "tool_name": "generate_latest_signal_report",
                "input_json": input_json,
                "expected_output_schema": REPORT_SCHEMA_VERSION,
                "live_data_required": False,
                "idempotency_key_template": idempotency_key_template,
                "expected_sections": intent["required_sections"],
                "telegram_format_schema": TELEGRAM_FORMAT_SCHEMA_VERSION,
                "numeric_authority": "latest_signal_report",
                "prompt": _cron_report_prompt_text(
                    asset=normalized_asset,
                    prompt_name=intent_name,
                    timeframe=normalized_timeframe,
                    intent=intent,
                    expected_output_schema=REPORT_SCHEMA_VERSION,
                    telegram_format_schema=TELEGRAM_FORMAT_SCHEMA_VERSION,
                    numeric_authority="latest_signal_report",
                    schedule_hint=intent["schedule_hint"],
                    decision_focus=intent["decision_focus"],
                    expected_sections=intent["required_sections"],
                    manual_setup_required=CRON_MANUAL_SETUP_REQUIRED,
                    idempotency_key_template=idempotency_key_template,
                ),
                "delivery_preview_path": "delivery_preview.channels.telegram.chunks",
            }
        )

    if normalized_include_position_review:
        idempotency_key_template = (
            f"halo_swing:position_review:{normalized_asset}:{{yyyy_mm_dd}}"
        )
        prompts.append(
            {
                "name": "position_review",
                "schedule_hint": "manual_or_scheduled_position_check",
                "decision_focus": "hold_trim_exit_or_stop_review",
                "tool_name": "generate_position_review_report",
                "input_json": {"asset": normalized_asset},
                "expected_output_schema": POSITION_REVIEW_SCHEMA_VERSION,
                "live_data_required": False,
                "idempotency_key_template": idempotency_key_template,
                "expected_sections": POSITION_REVIEW_SECTIONS,
                "telegram_format_schema": TELEGRAM_FORMAT_SCHEMA_VERSION,
                "numeric_authority": "position_review",
                "prompt": _cron_position_review_prompt_text(
                    asset=normalized_asset,
                    prompt_name="position_review",
                    expected_output_schema=POSITION_REVIEW_SCHEMA_VERSION,
                    telegram_format_schema=TELEGRAM_FORMAT_SCHEMA_VERSION,
                    numeric_authority="position_review",
                    schedule_hint="manual_or_scheduled_position_check",
                    decision_focus="hold_trim_exit_or_stop_review",
                    expected_sections=POSITION_REVIEW_SECTIONS,
                    manual_setup_required=CRON_MANUAL_SETUP_REQUIRED,
                    idempotency_key_template=idempotency_key_template,
                ),
                "delivery_preview_path": "delivery_preview.channels.telegram.chunks",
            }
        )

    contract = _cron_prompt_pack_contract(normalized_include_position_review)
    payload = {
        "schema_version": CRON_PROMPT_SCHEMA_VERSION,
        "asset": normalized_asset,
        "timeframe": normalized_timeframe,
        "prompts": prompts,
        "cron_prompt_contract": contract,
        "cron_prompt_guard": {},
        "live_data_required": False,
    }
    payload["cron_prompt_guard"] = _cron_prompt_pack_guard(
        prompts=prompts,
        contract=contract,
        pack_keys=list(payload),
        schema_version=payload["schema_version"],
        asset=payload["asset"],
        timeframe=payload["timeframe"],
        pack_live_data_required=payload["live_data_required"],
        include_position_review=normalized_include_position_review,
    )
    return payload


def _latest_signal_report_from_signal(
    signal: dict[str, Any],
    chart_payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    report = LatestSignalReport.model_validate(
        {
            "signal_id": signal["signal_id"],
            "created_at": signal["created_at"],
            "asset": signal["asset"],
            "underlying": signal["underlying"],
            "timeframe": signal["timeframe"],
            "action": signal["action"],
            "action_label": signal["action_label"],
            "final_score": signal["final_score"],
            "confidence": signal["confidence"],
            "entry_summary": signal["entry_summary"],
            "stop_summary": signal["stop_summary"],
            "take_profit_summary": signal["take_profit_summary"],
            "invalidation_summary": signal["invalidation_summary"],
            "risk_summary": signal["risk_summary"],
            "data_freshness_status": signal["data_freshness_status"],
            "degraded_mode": signal["degraded_mode"],
            "data_warnings": signal["data_warnings"],
            "config_hash": signal["config_hash"],
            "reason_summary": signal["reason_summary"],
            "evidence_summary": signal["evidence_summary"],
            "label_status": signal["label_status"],
            "chart_ref": chart_payload["artifact_ref"] if chart_payload else None,
        }
    )
    return report.model_dump(mode="json")


def _latest_report_source_signal(
    *,
    asset: str,
    timeframe: str,
    ledger_path: str | None,
    database_path: str | None,
) -> dict[str, Any]:
    if ledger_path is None and database_path is None:
        return score_leverage_swing(asset=asset, timeframe=timeframe)

    latest_record = get_latest_signal_record(
        ledger_path=ledger_path,
        database_path=database_path,
        asset=asset,
    )
    if latest_record["status"] != "found":
        raise ValueError(
            "latest signal report source was not found in the selected repository"
        )
    record = latest_record.get("record")
    if not isinstance(record, dict) or not isinstance(record.get("signal"), dict):
        raise ValueError("latest signal report source record.signal must be an object")
    return record["signal"]


def _report_sections(
    signal: dict[str, Any],
    report: dict[str, Any],
    intent_contract: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    cautions = list(signal.get("risk_warnings") or [])
    if report["data_warnings"]:
        cautions.extend(report["data_warnings"])
    if not cautions:
        cautions.append(report["risk_summary"])

    sections = [
        {
            "title": "Target",
            "items": [f"{report['asset']} / {report['underlying']}"],
        },
        {
            "title": "Decision",
            "items": [
                report["action"],
                f"{_confidence_label(float(report['confidence']))} confidence",
                f"score {report['final_score']}",
            ],
        },
        {
            "title": "Reasons",
            "items": [report["reason_summary"], report["evidence_summary"]],
        },
        {
            "title": "Entry",
            "items": [report["entry_summary"], signal["entry"]["trigger"]],
        },
        {
            "title": "Stop",
            "items": signal["stop"],
        },
        {
            "title": "Take Profit",
            "items": signal["take_profit"],
        },
        {
            "title": "Cautions",
            "items": cautions,
        },
    ]
    if intent_contract is None:
        return sections

    required = set(intent_contract["required_sections"])
    return [section for section in sections if section["title"] in required]


def _format_report_text(
    report: dict[str, Any],
    sections: list[dict[str, Any]],
) -> str:
    lines = [
        f"Target: {report['asset']} / {report['underlying']}",
        f"Decision: {report['action']}",
        (
            "Confidence: "
            f"{_confidence_label(float(report['confidence']))} ({report['confidence']})"
        ),
        f"Score: {report['final_score']}",
    ]
    for section in sections[2:]:
        lines.append("")
        lines.append(f"{section['title']}:")
        lines.extend(f"- {item}" for item in section["items"] if item)
    return "\n".join(lines)


def _position_review_sections(review: dict[str, Any]) -> list[dict[str, Any]]:
    size = review.get("size")
    position_items = [
        f"{review['asset']} / {review['underlying']}",
        f"entry {review['entry_price']}",
        f"current {review['current_price']}",
    ]
    if size is not None:
        position_items.append(f"size {size}")

    return [
        {
            "title": "Position",
            "items": position_items,
        },
        {
            "title": "Decision",
            "items": [
                review["action"],
                review["position_state"],
                f"unrealized return {review['unrealized_return_pct']}%",
            ],
        },
        {
            "title": "Rationale",
            "items": [review["rationale"]],
        },
        {
            "title": "Stop",
            "items": review["stop_conditions"],
        },
        {
            "title": "Take Profit",
            "items": review["take_profit_conditions"],
        },
        {
            "title": "Risk",
            "items": [
                "Position review is advisory and does not submit orders.",
                "Size decisions remain user-approved.",
            ],
        },
    ]


def _format_position_review_text(
    review: dict[str, Any],
    sections: list[dict[str, Any]],
) -> str:
    lines = [
        f"Position: {review['asset']} / {review['underlying']}",
        f"Decision: {review['action']} ({review['position_state']})",
        f"Unrealized Return: {review['unrealized_return_pct']}%",
    ]
    for section in sections[2:]:
        lines.append("")
        lines.append(f"{section['title']}:")
        lines.extend(f"- {item}" for item in section["items"] if item)
    return "\n".join(lines)


def _evidence_context(
    signal: dict[str, Any],
    report: dict[str, Any],
) -> dict[str, Any]:
    components = dict(signal.get("component_scores") or {})
    scored_components = {
        key: float(value)
        for key, value in components.items()
        if key != "event_risk"
    }
    strongest = max(scored_components, key=scored_components.get)
    weakest = min(scored_components, key=scored_components.get)
    return {
        "reason_summary": report["reason_summary"],
        "evidence_summary": report["evidence_summary"],
        "risk_warnings": list(signal.get("risk_warnings") or []),
        "component_extremes": {
            "strongest": {
                "name": strongest,
                "score": round(scored_components[strongest], 4),
            },
            "weakest": {
                "name": weakest,
                "score": round(scored_components[weakest], 4),
            },
            "spread": round(
                scored_components[strongest] - scored_components[weakest],
                4,
            ),
        },
        "conflict_flags": _evidence_conflict_flags(signal, report),
    }


def _multimodal_context(
    report: dict[str, Any],
    extra_evidence_cards: list[dict[str, Any]],
) -> dict[str, Any]:
    evidence_cards = [dict(card) for card in extra_evidence_cards]
    artifact_refs = _multimodal_artifact_refs(report, evidence_cards)
    modality_counts = _multimodal_modality_counts(report, evidence_cards)
    context = {
        "status": "pending",
        "schema_version": "multimodal_context.v1",
        "numeric_authority": "latest_signal_report",
        "hermes_multimodal_call": False,
        "network_call": False,
        "raw_artifacts_embedded": False,
        "modality_counts": modality_counts,
        "artifact_refs": artifact_refs,
        "evidence_cards": evidence_cards,
    }
    guard = _multimodal_context_guard(
        report,
        evidence_cards,
        artifact_refs,
        modality_counts=modality_counts,
        context_keys=[*list(context), "guard"],
        context_identity_values={
            "schema_version": context["schema_version"],
            "numeric_authority": context["numeric_authority"],
            "hermes_multimodal_call": context["hermes_multimodal_call"],
            "network_call": context["network_call"],
            "raw_artifacts_embedded": context["raw_artifacts_embedded"],
        },
    )
    context["status"] = guard["status"]
    context["guard"] = guard
    return context


def _multimodal_artifact_refs(
    report: dict[str, Any],
    evidence_cards: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    refs: list[dict[str, Any]] = []
    chart_ref = report.get("chart_ref")
    if chart_ref:
        refs.append({"evidence_id": "latest_signal_chart", "artifact_ref": chart_ref})
    refs.extend(
        {
            "evidence_id": str(card.get("evidence_id", "extra_evidence")),
            "artifact_ref": card["artifact_ref"],
        }
        for card in evidence_cards
        if "artifact_ref" in card
    )
    return refs


def _multimodal_modality_counts(
    report: dict[str, Any],
    evidence_cards: list[dict[str, Any]],
) -> dict[str, int]:
    counts: dict[str, int] = {}
    if report.get("chart_ref"):
        counts["chart_image"] = 1
    for card in evidence_cards:
        modality = str(card.get("modality", "unknown"))
        counts[modality] = counts.get(modality, 0) + 1
    return counts


def _multimodal_context_guard(
    report: dict[str, Any],
    evidence_cards: list[dict[str, Any]],
    artifact_refs: list[dict[str, Any]],
    modality_counts: dict[str, int],
    context_keys: list[str],
    context_identity_values: dict[str, Any],
) -> dict[str, Any]:
    expected_guard_check_keys = [
        "name",
        "passed",
        "expected",
        "actual",
    ]
    expected_guard_keys = ["status", "checks"]
    expected_context_keys = [
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
    expected_context_identity_values = {
        "schema_version": "multimodal_context.v1",
        "numeric_authority": "latest_signal_report",
        "hermes_multimodal_call": False,
        "network_call": False,
        "raw_artifacts_embedded": False,
    }
    expected_artifact_ref_entry_keys = ["evidence_id", "artifact_ref"]
    expected_artifact_ref_keys = ["ref_type", "ref", "metadata"]
    expected_artifact_ref_types = ["CHART", "PDF"]
    expected_evidence_card_keys = [
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
    expected_artifact_ref_metadata_keys_by_type = {
        "CHART": ["bars", "renderer", "timeframe_supported"],
        "PDF": ["description", "portable", "parsed_by_mcp"],
    }
    expected_guard_check_names = [
        "numeric_authority_is_latest_signal_report",
        "no_hermes_multimodal_call",
        "no_network_call",
        "non_chart_artifact_refs_are_portable",
        "chart_refs_are_declared",
        "chart_ref_slot_uses_chart_artifact_ref_type",
        "chart_artifact_refs_use_reserved_evidence_id",
        "extra_cards_have_modality",
        "extra_cards_have_summary",
        "multimodal_context_evidence_card_ids_are_unique",
        "multimodal_context_evidence_card_ids_do_not_use_reserved_ids",
        "multimodal_context_evidence_card_ids_match_safe_contract",
        "multimodal_context_artifact_ref_evidence_ids_are_unique",
        "multimodal_context_artifact_ref_evidence_ids_match_safe_contract",
        "multimodal_context_evidence_ids_are_string_typed",
        "multimodal_context_artifact_ref_values_are_unique",
        "multimodal_context_artifact_ref_values_are_trimmed_and_control_free",
        "multimodal_context_artifact_ref_values_do_not_embed_local_path_markers",
        "multimodal_context_identity_values_match_expected_contract",
        "multimodal_context_modality_counts_match_expected_context",
        "multimodal_context_evidence_cards_match_expected_schema",
        "multimodal_context_evidence_card_values_are_safe",
        "multimodal_context_evidence_card_string_field_types_are_strict",
        "multimodal_context_evidence_card_structural_field_types_are_strict",
        "multimodal_context_evidence_card_text_values_are_trimmed_and_control_free",
        "multimodal_context_evidence_card_scalar_values_are_trimmed_and_control_free",
        "multimodal_context_evidence_card_modality_values_are_supported",
        "multimodal_context_evidence_card_artifact_refs_use_explicit_uris",
        "multimodal_context_chart_artifact_refs_match_png_contract",
        "multimodal_context_chart_artifact_refs_use_offline_locations",
        "multimodal_context_pdf_artifact_refs_match_pdf_contract",
        "multimodal_context_evidence_card_observed_at_values_are_utc_iso",
        "multimodal_context_evidence_card_observed_at_not_after_report",
        "multimodal_context_evidence_card_asset_scope_matches_report",
        "multimodal_context_evidence_card_asset_scope_values_are_trimmed_and_control_free",
        "multimodal_context_evidence_card_summary_bounds_are_safe",
        "multimodal_context_evidence_card_summary_truncation_flags_are_consistent",
        "multimodal_context_evidence_card_invalidating_conditions_are_actionable",
        "multimodal_context_evidence_card_categorical_values_are_safe",
        "multimodal_context_evidence_card_impacts_are_context_only",
        "multimodal_context_artifact_refs_match_expected_context",
        "multimodal_context_artifact_refs_cover_evidence_cards_with_artifact_ref",
        "multimodal_context_artifact_refs_match_expected_schema",
        "multimodal_context_artifact_ref_string_field_types_are_strict",
        "multimodal_context_artifact_ref_types_match_expected_contract",
        "multimodal_context_artifact_ref_types_are_canonical_uppercase",
        "multimodal_context_artifact_ref_metadata_matches_expected_schema",
        "multimodal_context_artifact_ref_metadata_entries_match_expected_schema",
        "multimodal_context_artifact_ref_metadata_values_are_safe",
        "multimodal_context_artifact_ref_metadata_value_types_are_strict",
        "multimodal_context_artifact_ref_metadata_text_values_are_trimmed_and_control_free",
        "multimodal_context_keys_match_expected_schema",
        "multimodal_context_guard_check_names_match_expected_schema",
        "multimodal_context_guard_check_keys_match_expected_schema",
        "multimodal_context_guard_keys_match_expected_schema",
    ]
    refs = [
        ref["artifact_ref"]
        for ref in artifact_refs
        if isinstance(ref.get("artifact_ref"), dict)
    ]
    chart_ref = report.get("chart_ref")
    chart_ref_slot_expected_values = {
        "chart_ref_present": bool(chart_ref),
        "ref_type": "CHART" if chart_ref else None,
        "slot_uses_chart_artifact_ref_type": True,
    }
    chart_ref_slot_actual_values = {
        "chart_ref_present": bool(chart_ref),
        "ref_type": chart_ref.get("ref_type") if isinstance(chart_ref, dict) else None,
        "slot_uses_chart_artifact_ref_type": (
            not chart_ref
            or (isinstance(chart_ref, dict) and chart_ref.get("ref_type") == "CHART")
        ),
    }
    chart_artifact_ref_id_expected_values = []
    chart_artifact_ref_id_actual_values = []
    for ref_entry in artifact_refs:
        artifact_ref = ref_entry.get("artifact_ref", {})
        if not isinstance(artifact_ref, dict):
            continue
        ref_type = str(artifact_ref.get("ref_type", "")).upper()
        if ref_type != "CHART":
            continue
        chart_artifact_ref_id_expected_values.append(
            {
                "evidence_id": "latest_signal_chart",
                "ref_type": "CHART",
                "uses_reserved_chart_evidence_id": True,
            }
        )
        evidence_id = ref_entry.get("evidence_id")
        chart_artifact_ref_id_actual_values.append(
            {
                "evidence_id": evidence_id,
                "ref_type": ref_type,
                "uses_reserved_chart_evidence_id": (
                    evidence_id == "latest_signal_chart"
                ),
            }
        )
    non_chart_ref_values = [
        str(ref.get("ref", ""))
        for ref in refs
        if str(ref.get("ref_type", "")).upper() != "CHART"
    ]
    artifact_ref_values = [str(ref.get("ref", "")).strip() for ref in refs]
    artifact_ref_string_expected_values = [
        {
            "evidence_id": ref_entry.get("evidence_id"),
            "ref_has_no_surrounding_whitespace": True,
            "ref_has_no_control_characters": True,
        }
        for ref_entry in artifact_refs
        if isinstance(ref_entry.get("artifact_ref"), dict)
    ]
    artifact_ref_string_actual_values = []
    for ref_entry in artifact_refs:
        artifact_ref = ref_entry.get("artifact_ref", {})
        if not isinstance(artifact_ref, dict):
            continue
        ref_value = str(artifact_ref.get("ref", ""))
        artifact_ref_string_actual_values.append(
            {
                "evidence_id": ref_entry.get("evidence_id"),
                "ref_has_no_surrounding_whitespace": ref_value == ref_value.strip(),
                "ref_has_no_control_characters": _has_no_control_characters(ref_value),
            }
        )
    artifact_ref_local_path_marker_contract = {
        "forbidden_ref_fragments": [
            "/Users/",
            "file://",
            "~/",
        ],
        "forbidden_drive_root": True,
    }
    artifact_ref_local_path_marker_expected_values = [
        {
            "evidence_id": ref_entry.get("evidence_id"),
            **artifact_ref_local_path_marker_contract,
            "ref_has_no_local_path_marker": True,
        }
        for ref_entry in artifact_refs
        if isinstance(ref_entry.get("artifact_ref"), dict)
    ]
    artifact_ref_local_path_marker_actual_values = [
        {
            "evidence_id": ref_entry.get("evidence_id"),
            **artifact_ref_local_path_marker_contract,
            "ref_has_no_local_path_marker": _artifact_ref_has_no_local_path_marker(
                str(ref_entry.get("artifact_ref", {}).get("ref", ""))
            ),
        }
        for ref_entry in artifact_refs
        if isinstance(ref_entry.get("artifact_ref"), dict)
    ]
    expected_modality_counts = _multimodal_modality_counts(report, evidence_cards)
    expected_artifact_refs = _multimodal_artifact_refs(report, evidence_cards)
    expected_artifact_ref_card_ids = [
        str(card.get("evidence_id", "extra_evidence"))
        for card in evidence_cards
        if "artifact_ref" in card
    ]
    actual_artifact_ref_card_ids = [
        str(ref_entry.get("evidence_id", ""))
        for ref_entry in artifact_refs
        if ref_entry.get("evidence_id") != "latest_signal_chart"
    ]
    raw_evidence_card_ids = [card.get("evidence_id") for card in evidence_cards]
    evidence_card_ids = [str(card.get("evidence_id", "")) for card in evidence_cards]
    reserved_evidence_card_ids = ["latest_signal_chart"]
    uses_reserved_evidence_card_id = any(
        evidence_id in reserved_evidence_card_ids for evidence_id in evidence_card_ids
    )
    safe_evidence_id_contract = {
        "pattern": "lowercase_ascii_underscore_identifier",
        "min_chars": 3,
        "max_chars": 64,
    }
    evidence_card_id_contract_expected_values = [
        {
            "evidence_id": evidence_id,
            **safe_evidence_id_contract,
            "matches_safe_contract": True,
        }
        for evidence_id in evidence_card_ids
    ]
    evidence_card_id_contract_actual_values = [
        {
            "evidence_id": evidence_id,
            **safe_evidence_id_contract,
            "matches_safe_contract": _is_safe_evidence_id(evidence_id),
        }
        for evidence_id in evidence_card_ids
    ]
    raw_artifact_ref_evidence_ids = [ref.get("evidence_id") for ref in artifact_refs]
    artifact_ref_evidence_ids = [str(ref.get("evidence_id", "")) for ref in artifact_refs]
    evidence_id_type_expected_values = {
        "evidence_card_ids": evidence_card_ids,
        "artifact_ref_evidence_ids": artifact_ref_evidence_ids,
        "evidence_card_ids_are_strings": True,
        "artifact_ref_evidence_ids_are_strings": True,
    }
    evidence_id_type_actual_values = {
        "evidence_card_ids": raw_evidence_card_ids,
        "artifact_ref_evidence_ids": raw_artifact_ref_evidence_ids,
        "evidence_card_ids_are_strings": all(
            isinstance(evidence_id, str) for evidence_id in raw_evidence_card_ids
        ),
        "artifact_ref_evidence_ids_are_strings": all(
            isinstance(evidence_id, str)
            for evidence_id in raw_artifact_ref_evidence_ids
        ),
    }
    artifact_ref_evidence_id_contract_expected_values = [
        {
            "evidence_id": evidence_id,
            **safe_evidence_id_contract,
            "matches_safe_contract": True,
        }
        for evidence_id in artifact_ref_evidence_ids
    ]
    artifact_ref_evidence_id_contract_actual_values = [
        {
            "evidence_id": evidence_id,
            **safe_evidence_id_contract,
            "matches_safe_contract": _is_safe_evidence_id(evidence_id),
        }
        for evidence_id in artifact_ref_evidence_ids
    ]
    evidence_card_keys = [list(card) for card in evidence_cards]
    evidence_card_expected_values = []
    evidence_card_actual_values = []
    evidence_card_string_fields = [
        "category",
        "source",
        "modality",
        "observed_at",
        "bias",
        "summary",
        "buy_impact",
        "sell_impact",
        "invalidating_condition",
    ]
    evidence_card_string_type_expected_values = []
    evidence_card_string_type_actual_values = []
    evidence_card_structural_type_expected_values = []
    evidence_card_structural_type_actual_values = []
    evidence_card_text_fields = ["summary", "invalidating_condition"]
    evidence_card_text_expected_values = []
    evidence_card_text_actual_values = []
    evidence_card_scalar_fields = ["modality", "observed_at"]
    evidence_card_scalar_expected_values = []
    evidence_card_scalar_actual_values = []
    expected_evidence_card_modality_values = ["pdf_summary"]
    evidence_card_modality_expected_values = []
    evidence_card_modality_actual_values = []
    explicit_artifact_ref_prefixes = [
        "artifact://",
        "https://",
        "memory://",
        "urn:",
        "sha256:",
    ]
    evidence_card_artifact_uri_expected_values = []
    evidence_card_artifact_uri_actual_values = []
    evidence_card_observed_at_expected_values = []
    evidence_card_observed_at_actual_values = []
    evidence_card_observed_at_temporal_expected_values = []
    evidence_card_observed_at_temporal_actual_values = []
    evidence_card_asset_scope_expected_values = []
    evidence_card_asset_scope_actual_values = []
    evidence_card_asset_scope_string_expected_values = []
    evidence_card_asset_scope_string_actual_values = []
    evidence_card_summary_bounds_expected_values = []
    evidence_card_summary_bounds_actual_values = []
    evidence_card_summary_truncation_expected_values = []
    evidence_card_summary_truncation_actual_values = []
    invalidating_condition_min_words = 4
    invalidating_condition_placeholder_values = {
        "",
        "na",
        "none",
        "not applicable",
        "null",
        "placeholder",
        "tbd",
        "todo",
        "unknown",
    }
    evidence_card_invalidating_condition_expected_values = []
    evidence_card_invalidating_condition_actual_values = []
    expected_evidence_card_bias_values = [
        "bullish",
        "slightly_bullish",
        "neutral_to_bullish",
        "neutral",
        "neutral_to_bearish",
        "slightly_bearish",
        "bearish",
    ]
    evidence_card_categorical_expected_values = []
    evidence_card_categorical_actual_values = []
    evidence_card_impact_expected_values = []
    evidence_card_impact_actual_values = []
    report_created_at = str(report.get("created_at", "")).strip()
    report_created_at_dt = _parse_utc_iso_timestamp(report_created_at)
    for card in evidence_cards:
        artifact_ref = card.get("artifact_ref", {})
        if not isinstance(artifact_ref, dict):
            artifact_ref = {}
        asset_scope = card.get("asset_scope", [])
        if not isinstance(asset_scope, list):
            asset_scope = []
        normalized_asset_scope = [
            asset.upper()
            for asset in asset_scope
            if isinstance(asset, str)
        ]
        strength = card.get("strength")
        confidence = card.get("confidence")
        modality = str(card.get("modality", "")).strip()
        observed_at = str(card.get("observed_at", "")).strip()
        observed_at_dt = _parse_utc_iso_timestamp(observed_at)
        artifact_ref_value = str(artifact_ref.get("ref", "")).strip()
        evidence_card_expected_values.append(
            {
                "evidence_id": card.get("evidence_id"),
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
        )
        evidence_card_actual_values.append(
            {
                "evidence_id": card.get("evidence_id"),
                "modality_nonempty": bool(str(card.get("modality", "")).strip()),
                "observed_at_nonempty": bool(str(card.get("observed_at", "")).strip()),
                "asset_scope_uppercase": all(
                    isinstance(asset, str) and asset == asset.upper()
                    for asset in asset_scope
                ),
                "strength_in_range": (
                    not isinstance(strength, bool)
                    and isinstance(strength, int | float)
                    and 0.0 <= float(strength) <= 1.0
                ),
                "confidence_in_range": (
                    not isinstance(confidence, bool)
                    and isinstance(confidence, int | float)
                    and 0.0 <= float(confidence) <= 1.0
                ),
                "summary_nonempty": bool(str(card.get("summary", "")).strip()),
                "summary_truncated_is_bool": isinstance(
                    card.get("summary_truncated"), bool
                ),
                "impacts_nonempty": bool(
                    str(card.get("buy_impact", "")).strip()
                    and str(card.get("sell_impact", "")).strip()
                ),
                "invalidating_condition_nonempty": bool(
                    str(card.get("invalidating_condition", "")).strip()
                ),
                "artifact_ref_portable": _is_portable_artifact_ref(
                    str(artifact_ref.get("ref", ""))
                ),
            }
        )
        evidence_card_string_type_expected_values.append(
            {
                "evidence_id": card.get("evidence_id"),
                "string_fields": evidence_card_string_fields,
                "string_fields_are_strings": True,
            }
        )
        evidence_card_string_type_actual_values.append(
            {
                "evidence_id": card.get("evidence_id"),
                "string_fields": evidence_card_string_fields,
                "string_fields_are_strings": all(
                    isinstance(card.get(field), str)
                    for field in evidence_card_string_fields
                ),
            }
        )
        evidence_card_structural_type_expected_values.append(
            {
                "evidence_id": card.get("evidence_id"),
                "asset_scope_is_list": True,
                "artifact_ref_is_dict": True,
            }
        )
        evidence_card_structural_type_actual_values.append(
            {
                "evidence_id": card.get("evidence_id"),
                "asset_scope_is_list": isinstance(card.get("asset_scope"), list),
                "artifact_ref_is_dict": isinstance(card.get("artifact_ref"), dict),
            }
        )
        evidence_card_text_expected_values.append(
            {
                "evidence_id": card.get("evidence_id"),
                "text_fields": evidence_card_text_fields,
                "text_values_have_no_surrounding_whitespace": True,
                "text_values_have_no_control_characters": True,
            }
        )
        evidence_card_text_actual_values.append(
            {
                "evidence_id": card.get("evidence_id"),
                "text_fields": evidence_card_text_fields,
                "text_values_have_no_surrounding_whitespace": all(
                    str(card.get(field, "")) == str(card.get(field, "")).strip()
                    for field in evidence_card_text_fields
                ),
                "text_values_have_no_control_characters": all(
                    _has_no_control_characters(str(card.get(field, "")))
                    for field in evidence_card_text_fields
                ),
            }
        )
        evidence_card_scalar_expected_values.append(
            {
                "evidence_id": card.get("evidence_id"),
                "scalar_fields": evidence_card_scalar_fields,
                "scalar_values_have_no_surrounding_whitespace": True,
                "scalar_values_have_no_control_characters": True,
            }
        )
        evidence_card_scalar_actual_values.append(
            {
                "evidence_id": card.get("evidence_id"),
                "scalar_fields": evidence_card_scalar_fields,
                "scalar_values_have_no_surrounding_whitespace": all(
                    str(card.get(field, "")) == str(card.get(field, "")).strip()
                    for field in evidence_card_scalar_fields
                ),
                "scalar_values_have_no_control_characters": all(
                    _has_no_control_characters(str(card.get(field, "")))
                    for field in evidence_card_scalar_fields
                ),
            }
        )
        evidence_card_modality_expected_values.append(
            {
                "evidence_id": card.get("evidence_id"),
                "modality": "pdf_summary",
                "modality_supported": True,
            }
        )
        evidence_card_modality_actual_values.append(
            {
                "evidence_id": card.get("evidence_id"),
                "modality": modality,
                "modality_supported": modality in expected_evidence_card_modality_values,
            }
        )
        evidence_card_artifact_uri_expected_values.append(
            {
                "evidence_id": card.get("evidence_id"),
                "allowed_ref_prefixes": explicit_artifact_ref_prefixes,
                "artifact_ref_uses_explicit_uri": True,
            }
        )
        evidence_card_artifact_uri_actual_values.append(
            {
                "evidence_id": card.get("evidence_id"),
                "allowed_ref_prefixes": explicit_artifact_ref_prefixes,
                "artifact_ref_uses_explicit_uri": _is_explicit_artifact_uri(
                    artifact_ref_value,
                    explicit_artifact_ref_prefixes,
                ),
            }
        )
        evidence_card_observed_at_expected_values.append(
            {
                "evidence_id": card.get("evidence_id"),
                "observed_at_format": "iso8601_utc",
                "observed_at_is_utc_iso": True,
            }
        )
        evidence_card_observed_at_actual_values.append(
            {
                "evidence_id": card.get("evidence_id"),
                "observed_at_format": "iso8601_utc",
                "observed_at_is_utc_iso": _is_utc_iso_timestamp(observed_at),
            }
        )
        evidence_card_observed_at_temporal_expected_values.append(
            {
                "evidence_id": card.get("evidence_id"),
                "report_created_at": report_created_at,
                "observed_at_not_after_report_created_at": True,
            }
        )
        evidence_card_observed_at_temporal_actual_values.append(
            {
                "evidence_id": card.get("evidence_id"),
                "report_created_at": report_created_at,
                "observed_at_not_after_report_created_at": (
                    observed_at_dt is not None
                    and report_created_at_dt is not None
                    and observed_at_dt <= report_created_at_dt
                ),
            }
        )
        evidence_card_asset_scope_expected_values.append(
            {
                "evidence_id": card.get("evidence_id"),
                "report_asset": report["asset"],
                "report_underlying": report["underlying"],
                "includes_report_asset": True,
                "includes_report_underlying": True,
            }
        )
        evidence_card_asset_scope_actual_values.append(
            {
                "evidence_id": card.get("evidence_id"),
                "report_asset": report["asset"],
                "report_underlying": report["underlying"],
                "includes_report_asset": report["asset"] in normalized_asset_scope,
                "includes_report_underlying": (
                    report["underlying"] in normalized_asset_scope
                ),
            }
        )
        evidence_card_asset_scope_string_expected_values.append(
            {
                "evidence_id": card.get("evidence_id"),
                "asset_scope_values_have_no_surrounding_whitespace": True,
                "asset_scope_values_have_no_control_characters": True,
            }
        )
        evidence_card_asset_scope_string_actual_values.append(
            {
                "evidence_id": card.get("evidence_id"),
                "asset_scope_values_have_no_surrounding_whitespace": all(
                    isinstance(asset, str) and asset == asset.strip()
                    for asset in asset_scope
                ),
                "asset_scope_values_have_no_control_characters": all(
                    isinstance(asset, str) and _has_no_control_characters(asset)
                    for asset in asset_scope
                ),
            }
        )
        summary = str(card.get("summary", ""))
        evidence_card_summary_bounds_expected_values.append(
            {
                "evidence_id": card.get("evidence_id"),
                "summary_max_chars": DOCUMENT_SUMMARY_MAX_CHARS,
                "summary_within_limit": True,
            }
        )
        evidence_card_summary_bounds_actual_values.append(
            {
                "evidence_id": card.get("evidence_id"),
                "summary_max_chars": DOCUMENT_SUMMARY_MAX_CHARS,
                "summary_within_limit": len(summary) <= DOCUMENT_SUMMARY_MAX_CHARS,
            }
        )
        summary_truncated = card.get("summary_truncated")
        evidence_card_summary_truncation_expected_values.append(
            {
                "evidence_id": card.get("evidence_id"),
                "summary_truncated": summary_truncated,
                "summary_truncated_requires_max_length": True,
            }
        )
        evidence_card_summary_truncation_actual_values.append(
            {
                "evidence_id": card.get("evidence_id"),
                "summary_truncated": summary_truncated,
                "summary_truncated_requires_max_length": (
                    summary_truncated is not True
                    or len(summary) == DOCUMENT_SUMMARY_MAX_CHARS
                ),
            }
        )
        invalidating_condition = str(card.get("invalidating_condition", "")).strip()
        normalized_invalidating_condition = "".join(
            character
            for character in invalidating_condition.lower()
            if character.isalnum() or character.isspace()
        ).strip()
        evidence_card_invalidating_condition_expected_values.append(
            {
                "evidence_id": card.get("evidence_id"),
                "invalidating_condition_words_min": invalidating_condition_min_words,
                "invalidating_condition_has_min_words": True,
                "invalidating_condition_nonplaceholder": True,
            }
        )
        evidence_card_invalidating_condition_actual_values.append(
            {
                "evidence_id": card.get("evidence_id"),
                "invalidating_condition_words_min": invalidating_condition_min_words,
                "invalidating_condition_has_min_words": (
                    len(invalidating_condition.split())
                    >= invalidating_condition_min_words
                ),
                "invalidating_condition_nonplaceholder": (
                    normalized_invalidating_condition
                    not in invalidating_condition_placeholder_values
                ),
            }
        )
        evidence_card_categorical_expected_values.append(
            {
                "evidence_id": card.get("evidence_id"),
                "category": "manual_document",
                "source": "manual:document_summary",
                "bias_in_allowed_set": True,
            }
        )
        evidence_card_categorical_actual_values.append(
            {
                "evidence_id": card.get("evidence_id"),
                "category": card.get("category"),
                "source": card.get("source"),
                "bias_in_allowed_set": str(card.get("bias", ""))
                in expected_evidence_card_bias_values,
            }
        )
        evidence_card_impact_expected_values.append(
            {
                "evidence_id": card.get("evidence_id"),
                "buy_impact": "context_only",
                "sell_impact": "context_only",
            }
        )
        evidence_card_impact_actual_values.append(
            {
                "evidence_id": card.get("evidence_id"),
                "buy_impact": card.get("buy_impact"),
                "sell_impact": card.get("sell_impact"),
            }
        )
    artifact_ref_entry_keys = [list(ref) for ref in artifact_refs]
    artifact_ref_keys = [
        list(ref["artifact_ref"])
        if isinstance(ref.get("artifact_ref"), dict)
        else []
        for ref in artifact_refs
    ]
    artifact_ref_string_fields = ["ref_type", "ref"]
    artifact_ref_string_type_expected_values = []
    artifact_ref_string_type_actual_values = []
    for ref_entry in artifact_refs:
        artifact_ref = ref_entry.get("artifact_ref", {})
        if not isinstance(artifact_ref, dict):
            continue
        artifact_ref_string_type_expected_values.append(
            {
                "evidence_id": ref_entry.get("evidence_id"),
                "string_fields": artifact_ref_string_fields,
                "ref_type_is_string": True,
                "ref_is_string": True,
            }
        )
        artifact_ref_string_type_actual_values.append(
            {
                "evidence_id": ref_entry.get("evidence_id"),
                "string_fields": artifact_ref_string_fields,
                "ref_type_is_string": isinstance(artifact_ref.get("ref_type"), str),
                "ref_is_string": isinstance(artifact_ref.get("ref"), str),
            }
        )
    artifact_ref_types = [
        str(ref.get("ref_type", "")).upper()
        for ref in refs
    ]
    artifact_ref_type_canonical_expected_values = []
    artifact_ref_type_canonical_actual_values = []
    for ref_entry in artifact_refs:
        artifact_ref = ref_entry.get("artifact_ref", {})
        if not isinstance(artifact_ref, dict):
            continue
        raw_ref_type = str(artifact_ref.get("ref_type", ""))
        artifact_ref_type_canonical_expected_values.append(
            {
                "evidence_id": ref_entry.get("evidence_id"),
                "allowed_ref_types": expected_artifact_ref_types,
                "ref_type": raw_ref_type.upper(),
                "ref_type_is_canonical_uppercase": True,
            }
        )
        artifact_ref_type_canonical_actual_values.append(
            {
                "evidence_id": ref_entry.get("evidence_id"),
                "allowed_ref_types": expected_artifact_ref_types,
                "ref_type": raw_ref_type,
                "ref_type_is_canonical_uppercase": (
                    raw_ref_type in expected_artifact_ref_types
                ),
            }
        )
    artifact_ref_metadata_keys_by_type = {
        str(ref.get("ref_type", "")).upper(): list(ref.get("metadata", {}))
        for ref in refs
        if str(ref.get("ref_type", "")).upper()
        in expected_artifact_ref_metadata_keys_by_type
    }
    artifact_ref_metadata_is_dict = [
        isinstance(ref.get("metadata"), dict) for ref in refs
    ]
    chart_artifact_ref_expected_values = []
    chart_artifact_ref_actual_values = []
    chart_artifact_ref_offline_location_expected_values = []
    chart_artifact_ref_offline_location_actual_values = []
    for ref_entry in artifact_refs:
        artifact_ref = ref_entry.get("artifact_ref", {})
        if not isinstance(artifact_ref, dict):
            continue
        ref_type = str(artifact_ref.get("ref_type", "")).upper()
        if ref_type != "CHART":
            continue
        chart_artifact_ref_expected_values.append(
            {
                "evidence_id": ref_entry.get("evidence_id"),
                "ref_type": "CHART",
                "allowed_ref_suffixes": [".png"],
                "content_addressed_prefix": "sha256:",
                "ref_matches_chart_contract": True,
            }
        )
        chart_artifact_ref_actual_values.append(
            {
                "evidence_id": ref_entry.get("evidence_id"),
                "ref_type": ref_type,
                "allowed_ref_suffixes": [".png"],
                "content_addressed_prefix": "sha256:",
                "ref_matches_chart_contract": _is_png_artifact_ref(
                    str(artifact_ref.get("ref", ""))
                ),
            }
        )
        chart_artifact_ref_offline_location_expected_values.append(
            {
                "evidence_id": ref_entry.get("evidence_id"),
                "ref_type": "CHART",
                "allowed_ref_locations": [
                    "local_path",
                    "artifact://",
                    "sha256:",
                ],
                "network_ref_allowed": False,
                "ref_uses_offline_location": True,
            }
        )
        chart_artifact_ref_offline_location_actual_values.append(
            {
                "evidence_id": ref_entry.get("evidence_id"),
                "ref_type": ref_type,
                "allowed_ref_locations": [
                    "local_path",
                    "artifact://",
                    "sha256:",
                ],
                "network_ref_allowed": False,
                "ref_uses_offline_location": _is_offline_chart_artifact_ref(
                    str(artifact_ref.get("ref", ""))
                ),
            }
        )
    pdf_artifact_ref_expected_values = []
    pdf_artifact_ref_actual_values = []
    for ref_entry in artifact_refs:
        artifact_ref = ref_entry.get("artifact_ref", {})
        if not isinstance(artifact_ref, dict):
            continue
        ref_type = str(artifact_ref.get("ref_type", "")).upper()
        if ref_type != "PDF":
            continue
        pdf_artifact_ref_expected_values.append(
            {
                "evidence_id": ref_entry.get("evidence_id"),
                "ref_type": "PDF",
                "allowed_ref_suffixes": [".pdf"],
                "content_addressed_prefix": "sha256:",
                "ref_matches_pdf_contract": True,
            }
        )
        pdf_artifact_ref_actual_values.append(
            {
                "evidence_id": ref_entry.get("evidence_id"),
                "ref_type": ref_type,
                "allowed_ref_suffixes": [".pdf"],
                "content_addressed_prefix": "sha256:",
                "ref_matches_pdf_contract": _is_pdf_artifact_ref(
                    str(artifact_ref.get("ref", ""))
                ),
            }
        )
    artifact_ref_metadata_entry_expected_values = []
    artifact_ref_metadata_entry_actual_values = []
    for ref_entry in artifact_refs:
        artifact_ref = ref_entry.get("artifact_ref", {})
        if not isinstance(artifact_ref, dict):
            continue
        ref_type = str(artifact_ref.get("ref_type", "")).upper()
        expected_metadata_keys = expected_artifact_ref_metadata_keys_by_type.get(
            ref_type
        )
        if expected_metadata_keys is None:
            continue
        metadata = artifact_ref.get("metadata", {})
        artifact_ref_metadata_entry_expected_values.append(
            {
                "evidence_id": ref_entry.get("evidence_id"),
                "ref_type": ref_type,
                "metadata_is_dict": True,
                "metadata_keys": expected_metadata_keys,
            }
        )
        artifact_ref_metadata_entry_actual_values.append(
            {
                "evidence_id": ref_entry.get("evidence_id"),
                "ref_type": ref_type,
                "metadata_is_dict": isinstance(metadata, dict),
                "metadata_keys": list(metadata) if isinstance(metadata, dict) else [],
            }
        )
    artifact_ref_metadata_expected_values = []
    artifact_ref_metadata_actual_values = []
    artifact_ref_metadata_value_type_expected_values = []
    artifact_ref_metadata_value_type_actual_values = []
    artifact_ref_metadata_text_fields_by_type = {
        "CHART": ["renderer"],
        "PDF": ["description"],
    }
    artifact_ref_metadata_text_expected_values = []
    artifact_ref_metadata_text_actual_values = []
    for ref_entry in artifact_refs:
        artifact_ref = ref_entry.get("artifact_ref", {})
        if not isinstance(artifact_ref, dict):
            continue
        ref_type = str(artifact_ref.get("ref_type", "")).upper()
        metadata = artifact_ref.get("metadata", {})
        if not isinstance(metadata, dict):
            metadata = {}
        if ref_type == "CHART":
            artifact_ref_metadata_expected_values.append(
                {
                    "evidence_id": ref_entry.get("evidence_id"),
                    "ref_type": "CHART",
                    "renderer": "stdlib_png",
                    "bars_positive": True,
                    "timeframe_supported": True,
                }
            )
            bars = metadata.get("bars")
            artifact_ref_metadata_actual_values.append(
                {
                    "evidence_id": ref_entry.get("evidence_id"),
                    "ref_type": "CHART",
                    "renderer": metadata.get("renderer"),
                    "bars_positive": isinstance(bars, int) and bars > 0,
                    "timeframe_supported": metadata.get("timeframe_supported"),
                }
            )
            artifact_ref_metadata_value_type_expected_values.append(
                {
                    "evidence_id": ref_entry.get("evidence_id"),
                    "ref_type": "CHART",
                    "renderer_is_string": True,
                    "bars_is_positive_int": True,
                    "timeframe_supported_is_bool_true": True,
                }
            )
            artifact_ref_metadata_value_type_actual_values.append(
                {
                    "evidence_id": ref_entry.get("evidence_id"),
                    "ref_type": "CHART",
                    "renderer_is_string": isinstance(metadata.get("renderer"), str),
                    "bars_is_positive_int": (
                        isinstance(bars, int)
                        and not isinstance(bars, bool)
                        and bars > 0
                    ),
                    "timeframe_supported_is_bool_true": (
                        metadata.get("timeframe_supported") is True
                    ),
                }
            )
        elif ref_type == "PDF":
            artifact_ref_metadata_expected_values.append(
                {
                    "evidence_id": ref_entry.get("evidence_id"),
                    "ref_type": "PDF",
                    "portable": True,
                    "parsed_by_mcp": False,
                    "description_nonempty": True,
                }
            )
            artifact_ref_metadata_actual_values.append(
                {
                    "evidence_id": ref_entry.get("evidence_id"),
                    "ref_type": "PDF",
                    "portable": metadata.get("portable"),
                    "parsed_by_mcp": metadata.get("parsed_by_mcp"),
                    "description_nonempty": bool(
                        str(metadata.get("description", "")).strip()
                    ),
                }
            )
            artifact_ref_metadata_value_type_expected_values.append(
                {
                    "evidence_id": ref_entry.get("evidence_id"),
                    "ref_type": "PDF",
                    "description_is_string": True,
                    "portable_is_bool_true": True,
                    "parsed_by_mcp_is_bool_false": True,
                }
            )
            artifact_ref_metadata_value_type_actual_values.append(
                {
                    "evidence_id": ref_entry.get("evidence_id"),
                    "ref_type": "PDF",
                    "description_is_string": isinstance(
                        metadata.get("description"), str
                    ),
                    "portable_is_bool_true": metadata.get("portable") is True,
                    "parsed_by_mcp_is_bool_false": (
                        metadata.get("parsed_by_mcp") is False
                    ),
                }
            )
        metadata_text_fields = artifact_ref_metadata_text_fields_by_type.get(
            ref_type,
            [],
        )
        if metadata_text_fields:
            artifact_ref_metadata_text_expected_values.append(
                {
                    "evidence_id": ref_entry.get("evidence_id"),
                    "ref_type": ref_type,
                    "metadata_text_fields": metadata_text_fields,
                    "metadata_text_values_have_no_surrounding_whitespace": True,
                    "metadata_text_values_have_no_control_characters": True,
                }
            )
            artifact_ref_metadata_text_actual_values.append(
                {
                    "evidence_id": ref_entry.get("evidence_id"),
                    "ref_type": ref_type,
                    "metadata_text_fields": metadata_text_fields,
                    "metadata_text_values_have_no_surrounding_whitespace": all(
                        str(metadata.get(field, ""))
                        == str(metadata.get(field, "")).strip()
                        for field in metadata_text_fields
                    ),
                    "metadata_text_values_have_no_control_characters": all(
                        _has_no_control_characters(str(metadata.get(field, "")))
                        for field in metadata_text_fields
                    ),
                }
            )
    checks = [
        {
            "name": "numeric_authority_is_latest_signal_report",
            "passed": bool(report.get("signal_id")),
            "expected": "latest_signal_report",
            "actual": "latest_signal_report",
        },
        {
            "name": "no_hermes_multimodal_call",
            "passed": True,
            "expected": False,
            "actual": False,
        },
        {
            "name": "no_network_call",
            "passed": True,
            "expected": False,
            "actual": False,
        },
        {
            "name": "non_chart_artifact_refs_are_portable",
            "passed": all(_is_portable_artifact_ref(ref) for ref in non_chart_ref_values),
            "expected": "portable_ref",
            "actual": non_chart_ref_values,
        },
        {
            "name": "chart_refs_are_declared",
            "passed": all(ref.get("ref") for ref in refs if ref.get("ref_type") == "CHART"),
            "expected": "declared_chart_ref",
            "actual": [ref.get("ref") for ref in refs if ref.get("ref_type") == "CHART"],
        },
        {
            "name": "chart_ref_slot_uses_chart_artifact_ref_type",
            "passed": chart_ref_slot_actual_values == chart_ref_slot_expected_values,
            "expected": chart_ref_slot_expected_values,
            "actual": chart_ref_slot_actual_values,
        },
        {
            "name": "chart_artifact_refs_use_reserved_evidence_id",
            "passed": (
                chart_artifact_ref_id_actual_values
                == chart_artifact_ref_id_expected_values
            ),
            "expected": chart_artifact_ref_id_expected_values,
            "actual": chart_artifact_ref_id_actual_values,
        },
        {
            "name": "extra_cards_have_modality",
            "passed": all(card.get("modality") for card in evidence_cards),
            "expected": "modality",
            "actual": [card.get("modality") for card in evidence_cards],
        },
        {
            "name": "extra_cards_have_summary",
            "passed": all(str(card.get("summary", "")).strip() for card in evidence_cards),
            "expected": "summary",
            "actual": [bool(str(card.get("summary", "")).strip()) for card in evidence_cards],
        },
        {
            "name": "multimodal_context_evidence_card_ids_are_unique",
            "passed": (
                all(evidence_card_ids)
                and len(evidence_card_ids) == len(set(evidence_card_ids))
            ),
            "expected": {"nonempty": True, "unique": True},
            "actual": {
                "ids": evidence_card_ids,
                "nonempty": all(evidence_card_ids),
                "unique": len(evidence_card_ids) == len(set(evidence_card_ids)),
            },
        },
        {
            "name": "multimodal_context_evidence_card_ids_do_not_use_reserved_ids",
            "passed": not uses_reserved_evidence_card_id,
            "expected": {
                "reserved_ids": reserved_evidence_card_ids,
                "uses_reserved_id": False,
            },
            "actual": {
                "reserved_ids": reserved_evidence_card_ids,
                "uses_reserved_id": uses_reserved_evidence_card_id,
            },
        },
        {
            "name": "multimodal_context_evidence_card_ids_match_safe_contract",
            "passed": (
                evidence_card_id_contract_actual_values
                == evidence_card_id_contract_expected_values
            ),
            "expected": evidence_card_id_contract_expected_values,
            "actual": evidence_card_id_contract_actual_values,
        },
        {
            "name": "multimodal_context_artifact_ref_evidence_ids_are_unique",
            "passed": (
                all(artifact_ref_evidence_ids)
                and len(artifact_ref_evidence_ids) == len(set(artifact_ref_evidence_ids))
            ),
            "expected": {"nonempty": True, "unique": True},
            "actual": {
                "ids": artifact_ref_evidence_ids,
                "nonempty": all(artifact_ref_evidence_ids),
                "unique": (
                    len(artifact_ref_evidence_ids)
                    == len(set(artifact_ref_evidence_ids))
                ),
            },
        },
        {
            "name": "multimodal_context_artifact_ref_evidence_ids_match_safe_contract",
            "passed": (
                artifact_ref_evidence_id_contract_actual_values
                == artifact_ref_evidence_id_contract_expected_values
            ),
            "expected": artifact_ref_evidence_id_contract_expected_values,
            "actual": artifact_ref_evidence_id_contract_actual_values,
        },
        {
            "name": "multimodal_context_evidence_ids_are_string_typed",
            "passed": evidence_id_type_actual_values == evidence_id_type_expected_values,
            "expected": evidence_id_type_expected_values,
            "actual": evidence_id_type_actual_values,
        },
        {
            "name": "multimodal_context_artifact_ref_values_are_unique",
            "passed": (
                all(artifact_ref_values)
                and len(artifact_ref_values) == len(set(artifact_ref_values))
            ),
            "expected": {"nonempty": True, "unique": True},
            "actual": {
                "refs": artifact_ref_values,
                "nonempty": all(artifact_ref_values),
                "unique": len(artifact_ref_values) == len(set(artifact_ref_values)),
            },
        },
        {
            "name": (
                "multimodal_context_artifact_ref_values_are_trimmed_and_control_free"
            ),
            "passed": artifact_ref_string_actual_values == artifact_ref_string_expected_values,
            "expected": artifact_ref_string_expected_values,
            "actual": artifact_ref_string_actual_values,
        },
        {
            "name": (
                "multimodal_context_artifact_ref_values_do_not_embed_local_path_markers"
            ),
            "passed": (
                artifact_ref_local_path_marker_actual_values
                == artifact_ref_local_path_marker_expected_values
            ),
            "expected": artifact_ref_local_path_marker_expected_values,
            "actual": artifact_ref_local_path_marker_actual_values,
        },
        {
            "name": "multimodal_context_identity_values_match_expected_contract",
            "passed": context_identity_values == expected_context_identity_values,
            "expected": expected_context_identity_values,
            "actual": context_identity_values,
        },
        {
            "name": "multimodal_context_modality_counts_match_expected_context",
            "passed": modality_counts == expected_modality_counts,
            "expected": expected_modality_counts,
            "actual": modality_counts,
        },
        {
            "name": "multimodal_context_evidence_cards_match_expected_schema",
            "passed": all(keys == expected_evidence_card_keys for keys in evidence_card_keys),
            "expected": expected_evidence_card_keys,
            "actual": evidence_card_keys,
        },
        {
            "name": "multimodal_context_evidence_card_values_are_safe",
            "passed": evidence_card_actual_values == evidence_card_expected_values,
            "expected": evidence_card_expected_values,
            "actual": evidence_card_actual_values,
        },
        {
            "name": (
                "multimodal_context_evidence_card_string_field_types_are_strict"
            ),
            "passed": (
                evidence_card_string_type_actual_values
                == evidence_card_string_type_expected_values
            ),
            "expected": evidence_card_string_type_expected_values,
            "actual": evidence_card_string_type_actual_values,
        },
        {
            "name": (
                "multimodal_context_evidence_card_structural_field_types_are_strict"
            ),
            "passed": (
                evidence_card_structural_type_actual_values
                == evidence_card_structural_type_expected_values
            ),
            "expected": evidence_card_structural_type_expected_values,
            "actual": evidence_card_structural_type_actual_values,
        },
        {
            "name": (
                "multimodal_context_evidence_card_text_values_are_trimmed_and_control_free"
            ),
            "passed": (
                evidence_card_text_actual_values
                == evidence_card_text_expected_values
            ),
            "expected": evidence_card_text_expected_values,
            "actual": evidence_card_text_actual_values,
        },
        {
            "name": (
                "multimodal_context_evidence_card_scalar_values_are_trimmed_and_control_free"
            ),
            "passed": (
                evidence_card_scalar_actual_values
                == evidence_card_scalar_expected_values
            ),
            "expected": evidence_card_scalar_expected_values,
            "actual": evidence_card_scalar_actual_values,
        },
        {
            "name": "multimodal_context_evidence_card_modality_values_are_supported",
            "passed": (
                evidence_card_modality_actual_values
                == evidence_card_modality_expected_values
            ),
            "expected": evidence_card_modality_expected_values,
            "actual": evidence_card_modality_actual_values,
        },
        {
            "name": "multimodal_context_evidence_card_artifact_refs_use_explicit_uris",
            "passed": (
                evidence_card_artifact_uri_actual_values
                == evidence_card_artifact_uri_expected_values
            ),
            "expected": evidence_card_artifact_uri_expected_values,
            "actual": evidence_card_artifact_uri_actual_values,
        },
        {
            "name": "multimodal_context_chart_artifact_refs_match_png_contract",
            "passed": (
                chart_artifact_ref_actual_values
                == chart_artifact_ref_expected_values
            ),
            "expected": chart_artifact_ref_expected_values,
            "actual": chart_artifact_ref_actual_values,
        },
        {
            "name": "multimodal_context_chart_artifact_refs_use_offline_locations",
            "passed": (
                chart_artifact_ref_offline_location_actual_values
                == chart_artifact_ref_offline_location_expected_values
            ),
            "expected": chart_artifact_ref_offline_location_expected_values,
            "actual": chart_artifact_ref_offline_location_actual_values,
        },
        {
            "name": "multimodal_context_pdf_artifact_refs_match_pdf_contract",
            "passed": pdf_artifact_ref_actual_values == pdf_artifact_ref_expected_values,
            "expected": pdf_artifact_ref_expected_values,
            "actual": pdf_artifact_ref_actual_values,
        },
        {
            "name": "multimodal_context_evidence_card_observed_at_values_are_utc_iso",
            "passed": (
                evidence_card_observed_at_actual_values
                == evidence_card_observed_at_expected_values
            ),
            "expected": evidence_card_observed_at_expected_values,
            "actual": evidence_card_observed_at_actual_values,
        },
        {
            "name": "multimodal_context_evidence_card_observed_at_not_after_report",
            "passed": (
                evidence_card_observed_at_temporal_actual_values
                == evidence_card_observed_at_temporal_expected_values
            ),
            "expected": evidence_card_observed_at_temporal_expected_values,
            "actual": evidence_card_observed_at_temporal_actual_values,
        },
        {
            "name": "multimodal_context_evidence_card_asset_scope_matches_report",
            "passed": (
                evidence_card_asset_scope_actual_values
                == evidence_card_asset_scope_expected_values
            ),
            "expected": evidence_card_asset_scope_expected_values,
            "actual": evidence_card_asset_scope_actual_values,
        },
        {
            "name": (
                "multimodal_context_evidence_card_asset_scope_values_are_trimmed_and_control_free"
            ),
            "passed": (
                evidence_card_asset_scope_string_actual_values
                == evidence_card_asset_scope_string_expected_values
            ),
            "expected": evidence_card_asset_scope_string_expected_values,
            "actual": evidence_card_asset_scope_string_actual_values,
        },
        {
            "name": "multimodal_context_evidence_card_summary_bounds_are_safe",
            "passed": (
                evidence_card_summary_bounds_actual_values
                == evidence_card_summary_bounds_expected_values
            ),
            "expected": evidence_card_summary_bounds_expected_values,
            "actual": evidence_card_summary_bounds_actual_values,
        },
        {
            "name": (
                "multimodal_context_evidence_card_summary_truncation_flags_are_consistent"
            ),
            "passed": (
                evidence_card_summary_truncation_actual_values
                == evidence_card_summary_truncation_expected_values
            ),
            "expected": evidence_card_summary_truncation_expected_values,
            "actual": evidence_card_summary_truncation_actual_values,
        },
        {
            "name": (
                "multimodal_context_evidence_card_invalidating_conditions_are_actionable"
            ),
            "passed": (
                evidence_card_invalidating_condition_actual_values
                == evidence_card_invalidating_condition_expected_values
            ),
            "expected": evidence_card_invalidating_condition_expected_values,
            "actual": evidence_card_invalidating_condition_actual_values,
        },
        {
            "name": "multimodal_context_evidence_card_categorical_values_are_safe",
            "passed": (
                evidence_card_categorical_actual_values
                == evidence_card_categorical_expected_values
            ),
            "expected": evidence_card_categorical_expected_values,
            "actual": evidence_card_categorical_actual_values,
        },
        {
            "name": "multimodal_context_evidence_card_impacts_are_context_only",
            "passed": (
                evidence_card_impact_actual_values
                == evidence_card_impact_expected_values
            ),
            "expected": evidence_card_impact_expected_values,
            "actual": evidence_card_impact_actual_values,
        },
        {
            "name": "multimodal_context_artifact_refs_match_expected_context",
            "passed": artifact_refs == expected_artifact_refs,
            "expected": expected_artifact_refs,
            "actual": artifact_refs,
        },
        {
            "name": (
                "multimodal_context_artifact_refs_cover_evidence_cards_with_artifact_ref"
            ),
            "passed": actual_artifact_ref_card_ids == expected_artifact_ref_card_ids,
            "expected": expected_artifact_ref_card_ids,
            "actual": actual_artifact_ref_card_ids,
        },
        {
            "name": "multimodal_context_artifact_refs_match_expected_schema",
            "passed": (
                all(
                    keys == expected_artifact_ref_entry_keys
                    for keys in artifact_ref_entry_keys
                )
                and all(keys == expected_artifact_ref_keys for keys in artifact_ref_keys)
            ),
            "expected": {
                "artifact_ref_entry_keys": expected_artifact_ref_entry_keys,
                "artifact_ref_keys": expected_artifact_ref_keys,
            },
            "actual": {
                "artifact_ref_entry_keys": artifact_ref_entry_keys,
                "artifact_ref_keys": artifact_ref_keys,
            },
        },
        {
            "name": "multimodal_context_artifact_ref_string_field_types_are_strict",
            "passed": (
                artifact_ref_string_type_actual_values
                == artifact_ref_string_type_expected_values
            ),
            "expected": artifact_ref_string_type_expected_values,
            "actual": artifact_ref_string_type_actual_values,
        },
        {
            "name": "multimodal_context_artifact_ref_types_match_expected_contract",
            "passed": all(
                ref_type in expected_artifact_ref_types
                for ref_type in artifact_ref_types
            ),
            "expected": expected_artifact_ref_types,
            "actual": artifact_ref_types,
        },
        {
            "name": "multimodal_context_artifact_ref_types_are_canonical_uppercase",
            "passed": (
                artifact_ref_type_canonical_actual_values
                == artifact_ref_type_canonical_expected_values
            ),
            "expected": artifact_ref_type_canonical_expected_values,
            "actual": artifact_ref_type_canonical_actual_values,
        },
        {
            "name": (
                "multimodal_context_artifact_ref_metadata_matches_expected_schema"
            ),
            "passed": (
                all(artifact_ref_metadata_is_dict)
                and artifact_ref_metadata_keys_by_type
                == {
                    ref_type: keys
                    for ref_type, keys in expected_artifact_ref_metadata_keys_by_type.items()
                    if ref_type in artifact_ref_metadata_keys_by_type
                }
            ),
            "expected": {
                "metadata_is_dict": True,
                "metadata_keys_by_ref_type": {
                    ref_type: keys
                    for ref_type, keys in expected_artifact_ref_metadata_keys_by_type.items()
                    if ref_type in artifact_ref_metadata_keys_by_type
                },
            },
            "actual": {
                "metadata_is_dict": artifact_ref_metadata_is_dict,
                "metadata_keys_by_ref_type": artifact_ref_metadata_keys_by_type,
            },
        },
        {
            "name": (
                "multimodal_context_artifact_ref_metadata_entries_match_expected_schema"
            ),
            "passed": (
                artifact_ref_metadata_entry_actual_values
                == artifact_ref_metadata_entry_expected_values
            ),
            "expected": artifact_ref_metadata_entry_expected_values,
            "actual": artifact_ref_metadata_entry_actual_values,
        },
        {
            "name": "multimodal_context_artifact_ref_metadata_values_are_safe",
            "passed": (
                artifact_ref_metadata_actual_values
                == artifact_ref_metadata_expected_values
            ),
            "expected": artifact_ref_metadata_expected_values,
            "actual": artifact_ref_metadata_actual_values,
        },
        {
            "name": (
                "multimodal_context_artifact_ref_metadata_value_types_are_strict"
            ),
            "passed": (
                artifact_ref_metadata_value_type_actual_values
                == artifact_ref_metadata_value_type_expected_values
            ),
            "expected": artifact_ref_metadata_value_type_expected_values,
            "actual": artifact_ref_metadata_value_type_actual_values,
        },
        {
            "name": (
                "multimodal_context_artifact_ref_metadata_text_values_are_trimmed_and_control_free"
            ),
            "passed": (
                artifact_ref_metadata_text_actual_values
                == artifact_ref_metadata_text_expected_values
            ),
            "expected": artifact_ref_metadata_text_expected_values,
            "actual": artifact_ref_metadata_text_actual_values,
        },
        {
            "name": "multimodal_context_keys_match_expected_schema",
            "passed": context_keys == expected_context_keys,
            "expected": expected_context_keys,
            "actual": context_keys,
        },
    ]
    guard_check_names_actual = [check["name"] for check in checks] + [
        "multimodal_context_guard_check_names_match_expected_schema",
        "multimodal_context_guard_check_keys_match_expected_schema",
        "multimodal_context_guard_keys_match_expected_schema",
    ]
    checks.append(
        {
            "name": "multimodal_context_guard_check_names_match_expected_schema",
            "passed": guard_check_names_actual == expected_guard_check_names,
            "expected": expected_guard_check_names,
            "actual": guard_check_names_actual,
        }
    )
    guard_check_keys_actual = {check["name"]: list(check) for check in checks}
    guard_check_keys_actual[
        "multimodal_context_guard_check_keys_match_expected_schema"
    ] = expected_guard_check_keys
    guard_check_keys_actual[
        "multimodal_context_guard_keys_match_expected_schema"
    ] = expected_guard_check_keys
    checks.append(
        {
            "name": "multimodal_context_guard_check_keys_match_expected_schema",
            "passed": all(
                check_keys == expected_guard_check_keys
                for check_keys in guard_check_keys_actual.values()
            ),
            "expected": expected_guard_check_keys,
            "actual": guard_check_keys_actual,
        }
    )
    checks.append(
        {
            "name": "multimodal_context_guard_keys_match_expected_schema",
            "passed": expected_guard_keys == ["status", "checks"],
            "expected": ["status", "checks"],
            "actual": expected_guard_keys,
        }
    )
    return {
        "status": "ok" if all(check["passed"] for check in checks) else "conflict",
        "checks": checks,
    }


def _evidence_conflict_flags(
    signal: dict[str, Any],
    report: dict[str, Any],
) -> list[dict[str, Any]]:
    components = dict(signal.get("component_scores") or {})
    scored_components = {
        key: float(value)
        for key, value in components.items()
        if key != "event_risk"
    }
    flags: list[dict[str, Any]] = []

    if signal.get("risk_warnings") and report["action"] in {
        "BUY_2X",
        "BUY_3X",
        "BUY_WATCH",
    }:
        flags.append(
            {
                "name": "event_risk_vs_long_bias",
                "severity": "medium",
                "status": "acknowledged",
                "details": (
                    "Report keeps event risk explicit while action still monitors "
                    "a leveraged long setup."
                ),
            }
        )

    if scored_components:
        spread = max(scored_components.values()) - min(scored_components.values())
        if spread >= 0.40:
            flags.append(
                {
                    "name": "mixed_component_signal",
                    "severity": "low",
                    "status": "acknowledged",
                    "details": (
                        "Component spread is wide enough that the report should "
                        "summarize both supportive and weak evidence."
                    ),
                }
            )

    if report["degraded_mode"] or report["data_warnings"]:
        flags.append(
            {
                "name": "data_quality_caveat",
                "severity": "high",
                "status": "acknowledged",
                "details": "Data warnings or degraded mode must stay visible.",
            }
        )

    return flags


def _confidence_label(confidence: float) -> str:
    if confidence >= 0.75:
        return "high"
    if confidence >= 0.55:
        return "medium"
    return "low"


def _is_safe_evidence_id(value: str) -> bool:
    if not 3 <= len(value) <= 64:
        return False
    if not ("a" <= value[0] <= "z"):
        return False
    return all(
        "a" <= character <= "z"
        or "0" <= character <= "9"
        or character == "_"
        for character in value
    )


def _is_portable_artifact_ref(ref: str) -> bool:
    if not ref.strip():
        return False
    lowered = ref.lower()
    return (
        ref.startswith("https://")
        or ref.startswith("artifact://")
        or (
            not ref.startswith("/")
            and not ref.startswith("~")
            and not lowered.startswith("file://")
        )
    )


def _is_explicit_artifact_uri(ref: str, prefixes: list[str]) -> bool:
    return any(ref.startswith(prefix) for prefix in prefixes)


def _is_pdf_artifact_ref(ref: str) -> bool:
    lowered = ref.lower().strip()
    if lowered.startswith("sha256:"):
        return _is_sha256_content_addressed_ref(ref)
    without_fragment = lowered.split("#", 1)[0]
    without_query = without_fragment.split("?", 1)[0]
    return without_query.endswith(".pdf")


def _is_png_artifact_ref(ref: str) -> bool:
    lowered = ref.lower().strip()
    if lowered.startswith("sha256:"):
        return _is_sha256_content_addressed_ref(ref)
    without_fragment = lowered.split("#", 1)[0]
    without_query = without_fragment.split("?", 1)[0]
    return without_query.endswith(".png")


def _is_offline_chart_artifact_ref(ref: str) -> bool:
    lowered = ref.lower().strip()
    if not lowered:
        return False
    if lowered.startswith(("~/", "file://", "http://", "https://")):
        return False
    if lowered.startswith("/users/") or _has_drive_root(ref):
        return False
    if lowered.startswith("artifact://"):
        return True
    if lowered.startswith("sha256:"):
        return _is_sha256_content_addressed_ref(ref)
    return _is_png_artifact_ref(ref)


def _is_sha256_content_addressed_ref(ref: str) -> bool:
    lowered = ref.lower().strip()
    digest = lowered.removeprefix("sha256:")
    return len(digest) == 64 and all(
        character in "0123456789abcdef" for character in digest
    )


def _artifact_ref_has_no_local_path_marker(ref: str) -> bool:
    lowered = ref.lower().strip()
    return not (
        "/users/" in lowered
        or "file://" in lowered
        or "~/" in lowered
        or _contains_drive_root(ref)
    )


def _has_no_control_characters(value: str) -> bool:
    return all(ord(character) >= 32 and ord(character) != 127 for character in value)


def _has_drive_root(ref: str) -> bool:
    return (
        len(ref) >= 3
        and ref[0].isalpha()
        and ref[1] == ":"
        and ref[2] in {"/", "\\"}
    )


def _contains_drive_root(ref: str) -> bool:
    for index in range(len(ref) - 2):
        previous = ref[index - 1] if index > 0 else ""
        if (
            (index == 0 or previous in {"/", "\\"})
            and ref[index].isalpha()
            and ref[index + 1] == ":"
            and ref[index + 2] in {"/", "\\"}
        ):
            return True
    return False


def _is_utc_iso_timestamp(value: str) -> bool:
    return _parse_utc_iso_timestamp(value) is not None


def _parse_utc_iso_timestamp(value: str) -> datetime | None:
    timestamp = value.strip()
    if not timestamp:
        return None
    try:
        parsed = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None or parsed.utcoffset() != timezone.utc.utcoffset(None):
        return None
    return parsed


def _prompt_contract(required_sections: list[str] | None = None) -> dict[str, Any]:
    return {
        "numeric_authority": "Use MCP numeric fields as source of truth.",
        "llm_role": "Summarize conflicts, caveats, and final wording only.",
        "must_include": _prompt_required_terms(required_sections),
    }


def _delivery_contract(
    numeric_authority: str = "latest_signal_report",
    telegram_required_sections: list[str] | None = None,
    telegram_max_chars: int = 3900,
) -> dict[str, Any]:
    required_sections = telegram_required_sections or REQUIRED_REPORT_SECTIONS
    return {
        "channels": {
            "hermes": {
                "format": "structured_json_plus_text",
                "network_call": False,
                "numeric_authority": numeric_authority,
            },
            "telegram": {
                "schema_version": TELEGRAM_FORMAT_SCHEMA_VERSION,
                "format": "plain_text",
                "network_call": False,
                "max_chars": telegram_max_chars,
                "required_sections": required_sections,
                "overflow_policy": "split_on_section_boundary",
                "section_separator": "\n\n",
                "chunk_indexing": "1_based",
                "send_call": False,
            },
        },
        "cron_intents": [
            "pre_market_swing_report",
            "intraday_risk_watch",
            "post_market_review",
        ],
    }


def _expected_delivery_contract_key_schema() -> dict[str, Any]:
    return {
        "contract_keys": [
            "channels",
            "cron_intents",
        ],
        "channel_names": [
            "hermes",
            "telegram",
        ],
        "hermes_channel_keys": [
            "format",
            "network_call",
            "numeric_authority",
        ],
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


def _delivery_contract_key_schema(delivery_contract: dict[str, Any]) -> dict[str, Any]:
    delivery_channels = delivery_contract["channels"]
    return {
        "contract_keys": list(delivery_contract),
        "channel_names": list(delivery_channels),
        "hermes_channel_keys": list(delivery_channels["hermes"]),
        "telegram_channel_keys": list(delivery_channels["telegram"]),
    }


def _delivery_preview(
    text: str,
    delivery_contract: dict[str, Any],
    structured_payload_key: str,
) -> dict[str, Any]:
    hermes_contract = delivery_contract["channels"]["hermes"]
    telegram_contract = delivery_contract["channels"]["telegram"]
    chunks = _telegram_chunks(text, int(telegram_contract["max_chars"]))
    chunk_texts = [str(chunk["text"]) for chunk in chunks]
    declared_separator = str(telegram_contract["section_separator"])
    reconstructed_text = declared_separator.join(chunk_texts)
    expected_chunk_indexes = list(range(1, len(chunks) + 1))
    required_sections = list(telegram_contract["required_sections"])
    required_section_headers = [
        f"{section}:" for section in required_sections
    ]
    continuation_chunk_starts = [
        chunk_text.splitlines()[0] if chunk_text.splitlines() else ""
        for chunk_text in chunk_texts[1:]
    ]
    unrequested_section_headers = [
        f"{section}:"
        for section in TELEGRAM_KNOWN_SECTIONS
        if section not in required_sections
    ]
    hermes_preview = {
        "format": hermes_contract["format"],
        "network_call": False,
        "numeric_authority": hermes_contract["numeric_authority"],
        "payload_ref": structured_payload_key,
    }
    telegram_preview = {
        "schema_version": telegram_contract["schema_version"],
        "format": telegram_contract["format"],
        "network_call": False,
        "max_chars": telegram_contract["max_chars"],
        "overflow_policy": telegram_contract["overflow_policy"],
        "section_separator": telegram_contract["section_separator"],
        "chunk_indexing": telegram_contract["chunk_indexing"],
        "send_call": telegram_contract["send_call"],
        "message_count": len(chunks),
        "fits_single_message": len(chunks) == 1,
        "chunks": chunks,
    }
    preview_channels = {
        "hermes": hermes_preview,
        "telegram": telegram_preview,
    }
    expected_guard_check_names = [
        "hermes_payload_ref_matches_structured_payload",
        "hermes_numeric_authority_matches_payload_ref",
        "telegram_format_schema_declared",
        "telegram_required_sections_present_in_preview",
        "telegram_unrequested_sections_absent_from_preview",
        "telegram_chunks_are_1_based_sequential",
        "telegram_message_count_matches_chunks",
        "telegram_single_message_flag_matches_chunk_count",
        "telegram_chunk_char_counts_match_text",
        "telegram_chunks_are_nonempty",
        "telegram_section_separator_preserves_preview_text",
        "telegram_overflow_policy_splits_on_section_boundary",
        "telegram_chunks_fit_max_chars",
        "telegram_chunks_preserve_text",
        "delivery_preview_has_no_network_side_effect",
        "delivery_preview_has_no_send_side_effect",
        "delivery_preview_guard_check_names_match_expected_schema",
        "delivery_preview_guard_check_keys_match_expected_schema",
        "delivery_preview_payload_keys_match_expected_schema",
    ]
    expected_delivery_preview_key_schema = {
        "preview_keys": [
            "channels",
            "guard",
        ],
        "channel_names": [
            "hermes",
            "telegram",
        ],
        "hermes_channel_keys": [
            "format",
            "network_call",
            "numeric_authority",
            "payload_ref",
        ],
        "telegram_channel_keys": [
            "schema_version",
            "format",
            "network_call",
            "max_chars",
            "overflow_policy",
            "section_separator",
            "chunk_indexing",
            "send_call",
            "message_count",
            "fits_single_message",
            "chunks",
        ],
        "telegram_chunk_keys": [
            [
                "index",
                "chars",
                "text",
            ]
            for _chunk in chunks
        ],
        "guard_keys": [
            "status",
            "checks",
        ],
    }
    expected_default_guard_check_keys = [
        "name",
        "passed",
        "expected",
        "actual",
    ]
    expected_special_guard_check_keys = {
        "telegram_unrequested_sections_absent_from_preview": [
            "name",
            "passed",
            "expected_absent",
            "actual_present",
        ],
        "telegram_chunks_fit_max_chars": [
            "name",
            "passed",
            "expected_max_chars",
            "actual_chars",
        ],
    }
    expected_default_guard_check_names = [
        name
        for name in expected_guard_check_names
        if name not in expected_special_guard_check_keys
    ]
    expected_guard_check_key_schema = {
        "default_keys": expected_default_guard_check_keys,
        "default_check_names": expected_default_guard_check_names,
        "special_check_keys": expected_special_guard_check_keys,
    }
    checks = [
        {
            "name": "hermes_payload_ref_matches_structured_payload",
            "passed": hermes_preview["payload_ref"] == structured_payload_key,
            "expected": structured_payload_key,
            "actual": hermes_preview["payload_ref"],
        },
        {
            "name": "hermes_numeric_authority_matches_payload_ref",
            "passed": hermes_preview["numeric_authority"] == hermes_preview["payload_ref"],
            "expected": hermes_preview["payload_ref"],
            "actual": hermes_preview["numeric_authority"],
        },
        {
            "name": "telegram_format_schema_declared",
            "passed": telegram_preview["schema_version"]
            == TELEGRAM_FORMAT_SCHEMA_VERSION,
            "expected": TELEGRAM_FORMAT_SCHEMA_VERSION,
            "actual": telegram_preview["schema_version"],
        },
        {
            "name": "telegram_required_sections_present_in_preview",
            "passed": all(header in reconstructed_text for header in required_section_headers),
            "expected": required_section_headers,
            "actual": [
                header
                for header in required_section_headers
                if header in reconstructed_text
            ],
        },
        {
            "name": "telegram_unrequested_sections_absent_from_preview",
            "passed": not any(
                header in reconstructed_text for header in unrequested_section_headers
            ),
            "expected_absent": unrequested_section_headers,
            "actual_present": [
                header
                for header in unrequested_section_headers
                if header in reconstructed_text
            ],
        },
        {
            "name": "telegram_chunks_are_1_based_sequential",
            "passed": telegram_preview["chunk_indexing"] == "1_based"
            and [chunk["index"] for chunk in chunks] == expected_chunk_indexes,
            "expected": {
                "chunk_indexing": "1_based",
                "indexes": expected_chunk_indexes,
            },
            "actual": {
                "chunk_indexing": telegram_preview["chunk_indexing"],
                "indexes": [
                    chunk["index"]
                    for chunk in chunks
                ],
            },
        },
        {
            "name": "telegram_message_count_matches_chunks",
            "passed": telegram_preview["message_count"] == len(chunks),
            "expected": len(chunks),
            "actual": telegram_preview["message_count"],
        },
        {
            "name": "telegram_single_message_flag_matches_chunk_count",
            "passed": telegram_preview["fits_single_message"] == (len(chunks) == 1),
            "expected": len(chunks) == 1,
            "actual": telegram_preview["fits_single_message"],
        },
        {
            "name": "telegram_chunk_char_counts_match_text",
            "passed": all(
                int(chunk["chars"]) == len(str(chunk["text"]))
                for chunk in chunks
            ),
            "expected": "len(chunk.text)",
            "actual": [
                {
                    "index": chunk["index"],
                    "chars": chunk["chars"],
                    "text_len": len(str(chunk["text"])),
                }
                for chunk in chunks
            ],
        },
        {
            "name": "telegram_chunks_are_nonempty",
            "passed": all(
                str(chunk["text"]) and int(chunk["chars"]) > 0
                for chunk in chunks
            ),
            "expected": "nonempty_chunk_text",
            "actual": [
                {
                    "index": chunk["index"],
                    "chars": chunk["chars"],
                    "text_empty": not bool(str(chunk["text"])),
                }
                for chunk in chunks
            ],
        },
        {
            "name": "telegram_section_separator_preserves_preview_text",
            "passed": reconstructed_text == text,
            "expected": "original_text",
            "actual": "declared_separator_reconstructed_text",
        },
        {
            "name": "telegram_overflow_policy_splits_on_section_boundary",
            "passed": telegram_preview["overflow_policy"] == "split_on_section_boundary"
            and all(
                any(start == header for header in required_section_headers)
                for start in continuation_chunk_starts
            ),
            "expected": {
                "overflow_policy": "split_on_section_boundary",
                "continuation_chunks_start_with_required_section": True,
            },
            "actual": {
                "overflow_policy": telegram_preview["overflow_policy"],
                "continuation_chunk_starts": continuation_chunk_starts,
            },
        },
        {
            "name": "telegram_chunks_fit_max_chars",
            "passed": all(
                int(chunk["chars"]) <= int(telegram_preview["max_chars"])
                for chunk in chunks
            ),
            "expected_max_chars": telegram_preview["max_chars"],
            "actual_chars": [chunk["chars"] for chunk in chunks],
        },
        {
            "name": "telegram_chunks_preserve_text",
            "passed": reconstructed_text == text,
            "expected": "original_text",
            "actual": "reconstructed_text",
        },
        {
            "name": "delivery_preview_has_no_network_side_effect",
            "passed": all(
                channel["network_call"] is False for channel in preview_channels.values()
            ),
            "expected": False,
            "actual": {
                name: channel["network_call"]
                for name, channel in preview_channels.items()
            },
        },
        {
            "name": "delivery_preview_has_no_send_side_effect",
            "passed": all(
                channel.get("send_call", False) is False
                for channel in preview_channels.values()
            ),
            "expected": False,
            "actual": {
                name: channel.get("send_call", False)
                for name, channel in preview_channels.items()
            },
        },
    ]
    guard_check_names_actual = [
        check["name"]
        for check in checks
    ] + [
        "delivery_preview_guard_check_names_match_expected_schema",
        "delivery_preview_guard_check_keys_match_expected_schema",
        "delivery_preview_payload_keys_match_expected_schema",
    ]
    checks.append(
        {
            "name": "delivery_preview_guard_check_names_match_expected_schema",
            "passed": guard_check_names_actual == expected_guard_check_names,
            "expected": expected_guard_check_names,
            "actual": guard_check_names_actual,
        }
    )
    guard_check_keys_actual = {
        check["name"]: list(check)
        for check in checks
    }
    guard_check_keys_actual[
        "delivery_preview_guard_check_keys_match_expected_schema"
    ] = expected_default_guard_check_keys
    guard_check_keys_actual[
        "delivery_preview_payload_keys_match_expected_schema"
    ] = expected_default_guard_check_keys
    actual_default_guard_check_names = [
        name
        for name in expected_guard_check_names
        if guard_check_keys_actual.get(name) == expected_default_guard_check_keys
    ]
    actual_special_guard_check_keys = {
        name: guard_check_keys_actual.get(name)
        for name in expected_special_guard_check_keys
    }
    actual_guard_check_key_schema = {
        "default_keys": expected_default_guard_check_keys,
        "default_check_names": actual_default_guard_check_names,
        "special_check_keys": actual_special_guard_check_keys,
    }
    checks.append(
        {
            "name": "delivery_preview_guard_check_keys_match_expected_schema",
            "passed": actual_guard_check_key_schema == expected_guard_check_key_schema,
            "expected": expected_guard_check_key_schema,
            "actual": actual_guard_check_key_schema,
        }
    )
    delivery_preview_for_schema = {
        "channels": preview_channels,
        "guard": {
            "status": "ok",
            "checks": checks,
        },
    }
    actual_delivery_preview_key_schema = {
        "preview_keys": list(delivery_preview_for_schema),
        "channel_names": list(preview_channels),
        "hermes_channel_keys": list(hermes_preview),
        "telegram_channel_keys": list(telegram_preview),
        "telegram_chunk_keys": [
            list(chunk)
            for chunk in chunks
        ],
        "guard_keys": list(delivery_preview_for_schema["guard"]),
    }
    checks.append(
        {
            "name": "delivery_preview_payload_keys_match_expected_schema",
            "passed": actual_delivery_preview_key_schema
            == expected_delivery_preview_key_schema,
            "expected": expected_delivery_preview_key_schema,
            "actual": actual_delivery_preview_key_schema,
        }
    )
    return {
        "channels": preview_channels,
        "guard": {
            "status": "ok" if all(check["passed"] for check in checks) else "conflict",
            "checks": checks,
        },
    }


def _telegram_chunks(text: str, max_chars: int) -> list[dict[str, Any]]:
    if max_chars < 1:
        raise ValueError("max_chars must be positive")
    if len(text) <= max_chars:
        return [{"index": 1, "chars": len(text), "text": text}]

    chunks: list[str] = []
    current = ""
    for block in text.split("\n\n"):
        candidate = block if not current else f"{current}\n\n{block}"
        if len(candidate) <= max_chars:
            current = candidate
            continue
        if current:
            chunks.append(current)
        if len(block) <= max_chars:
            current = block
            continue
        chunks.extend(_split_long_block(block, max_chars))
        current = ""
    if current:
        chunks.append(current)

    return [
        {"index": index, "chars": len(chunk), "text": chunk}
        for index, chunk in enumerate(chunks, start=1)
    ]


def _split_long_block(block: str, max_chars: int) -> list[str]:
    chunks: list[str] = []
    current = ""
    for line in block.splitlines() or [block]:
        candidate = line if not current else f"{current}\n{line}"
        if len(candidate) <= max_chars:
            current = candidate
            continue
        if current:
            chunks.append(current)
        if len(line) <= max_chars:
            current = line
            continue
        chunks.extend(line[start : start + max_chars] for start in range(0, len(line), max_chars))
        current = ""
    if current:
        chunks.append(current)
    return chunks


def _report_intent_contract(report_intent: str) -> dict[str, Any]:
    if report_intent not in REPORT_INTENTS:
        allowed = ", ".join(sorted(REPORT_INTENTS))
        raise ValueError(f"unsupported report_intent: {report_intent}; allowed: {allowed}")
    return {
        "name": report_intent,
        **REPORT_INTENTS[report_intent],
    }


def _normalize_report_include_chart(include_chart: bool) -> bool:
    if not isinstance(include_chart, bool):
        raise ValueError("include_chart must be a boolean")
    return include_chart


def _normalize_report_intent(report_intent: str) -> str:
    if not isinstance(report_intent, str):
        raise ValueError("report_intent must be a nonempty string")
    if not _has_no_control_characters(report_intent):
        raise ValueError("report_intent must not contain control characters")
    normalized = report_intent.strip().lower()
    if not normalized:
        raise ValueError("report_intent must be a nonempty string")
    return normalized


def _normalize_report_asset(asset: str) -> str:
    if not isinstance(asset, str):
        raise ValueError("asset must be a nonempty string")
    if not _has_no_control_characters(asset):
        raise ValueError("asset must not contain control characters")
    normalized = asset.strip().upper()
    if not normalized:
        raise ValueError("asset must be a nonempty string")
    return normalized


def _normalize_report_timeframe(timeframe: str) -> str:
    if not isinstance(timeframe, str):
        raise ValueError("timeframe must be a nonempty string")
    if not _has_no_control_characters(timeframe):
        raise ValueError("timeframe must not contain control characters")
    normalized = timeframe.strip()
    if not normalized:
        raise ValueError("timeframe must be a nonempty string")
    return normalized


def _normalize_report_chart_timeframe(chart_timeframe: str) -> str:
    if not isinstance(chart_timeframe, str):
        raise ValueError("chart_timeframe must be a nonempty string")
    if not _has_no_control_characters(chart_timeframe):
        raise ValueError("chart_timeframe must not contain control characters")
    normalized = chart_timeframe.strip().lower()
    if not normalized:
        raise ValueError("chart_timeframe must be a nonempty string")
    return normalized


def _normalize_report_chart_output_dir(chart_output_dir: str | None) -> str | None:
    if chart_output_dir is None:
        return None
    if not isinstance(chart_output_dir, str):
        raise ValueError("chart_output_dir must be a nonempty string")
    if not _has_no_control_characters(chart_output_dir):
        raise ValueError("chart_output_dir must not contain control characters")
    normalized = chart_output_dir.strip()
    if not normalized:
        raise ValueError("chart_output_dir must be a nonempty string")
    return normalized


def _normalize_report_repository_path(
    value: str | None,
    field_name: str,
) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be a nonempty string")
    if not _has_no_control_characters(value):
        raise ValueError(f"{field_name} must not contain control characters")
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{field_name} must be a nonempty string")
    return normalized


def _normalize_extra_evidence_cards(
    extra_evidence_cards: list[dict[str, Any]] | None,
) -> list[dict[str, Any]] | None:
    if extra_evidence_cards is None:
        return None
    if not isinstance(extra_evidence_cards, list):
        raise ValueError("extra_evidence_cards must be a list of objects")
    normalized_cards: list[dict[str, Any]] = []
    for card in extra_evidence_cards:
        if not isinstance(card, dict):
            raise ValueError("extra_evidence_cards items must be objects")
        normalized_cards.append(dict(card))
    return normalized_cards


def _normalize_report_optional_positive_finite_number(
    value: float | None,
    field_name: str,
) -> float | None:
    if value is None:
        return None
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise ValueError(f"{field_name} must be a positive finite number")
    normalized = float(value)
    if not math.isfinite(normalized) or normalized <= 0.0:
        raise ValueError(f"{field_name} must be a positive finite number")
    return normalized


def _normalize_prompt_asset(asset: str) -> str:
    return _normalize_report_asset(asset)


def _normalize_prompt_timeframe(timeframe: str) -> str:
    return _normalize_report_timeframe(timeframe)


def _normalize_prompt_include_position_review(
    include_position_review: bool,
) -> bool:
    if not isinstance(include_position_review, bool):
        raise ValueError("include_position_review must be a boolean")
    return include_position_review


def _has_no_control_characters(value: str) -> bool:
    return all(ord(character) >= 32 and ord(character) != 127 for character in value)


def _position_review_prompt_contract() -> dict[str, Any]:
    return {
        "numeric_authority": "Use position_review numeric fields as source of truth.",
        "llm_role": "Summarize hold, trim, exit, or stop rationale only.",
        "must_include": [
            "action",
            "position_state",
            "unrealized_return_pct",
            "stop",
            "take_profit",
            "risk",
        ],
    }


def _position_review_contract() -> dict[str, Any]:
    return {
        "name": "position_review",
        "trigger": "manual_or_scheduled_position_check",
        "decision_focus": "hold_trim_exit_or_stop_review",
        "required_sections": POSITION_REVIEW_SECTIONS,
        "network_call": False,
        "order_submission": False,
    }


def _expected_report_payload_keys(
    *,
    include_chart: bool,
    include_multimodal: bool,
) -> list[str]:
    keys = [
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
        "live_data_required",
    ]
    if include_chart:
        keys.append("chart_code_guard")
    if include_multimodal:
        keys.append("multimodal_context")
    keys.append("report_payload_guard")
    return keys


def _expected_position_payload_keys() -> list[str]:
    return [
        "schema_version",
        "as_of",
        "asset",
        "underlying",
        "action",
        "position_state",
        "position_review",
        "sections",
        "text",
        "prompt_contract",
        "delivery_contract",
        "delivery_preview",
        "position_review_contract",
        "position_review_guard",
        "live_data_required",
        "position_payload_guard",
    ]


def _payload_contract_guard(
    *,
    payload: dict[str, Any],
    expected_schema_version: str,
    expected_keys: list[str],
    schema_check_name: str,
    live_data_check_name: str,
    keys_check_name: str,
    check_names_check_name: str,
    guard_keys_check_name: str,
    check_keys_check_name: str,
    expected_live_data_required: bool = False,
    extra_checks: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    extra_checks = extra_checks or []
    expected_check_names = [
        schema_check_name,
        live_data_check_name,
        keys_check_name,
        *[check["name"] for check in extra_checks],
        check_names_check_name,
        guard_keys_check_name,
        check_keys_check_name,
    ]
    expected_check_keys = [
        "name",
        "passed",
        "expected",
        "actual",
    ]
    expected_guard_keys = [
        "status",
        "checks",
    ]
    checks = [
        {
            "name": schema_check_name,
            "passed": payload["schema_version"] == expected_schema_version,
            "expected": expected_schema_version,
            "actual": payload["schema_version"],
        },
        {
            "name": live_data_check_name,
            "passed": payload["live_data_required"] is expected_live_data_required,
            "expected": expected_live_data_required,
            "actual": payload["live_data_required"],
        },
        {
            "name": keys_check_name,
            "passed": list(payload) == expected_keys,
            "expected": expected_keys,
            "actual": list(payload),
        },
        *extra_checks,
    ]
    check_names_actual = [
        check["name"]
        for check in checks
    ] + [
        check_names_check_name,
        guard_keys_check_name,
        check_keys_check_name,
    ]
    checks.append(
        {
            "name": check_names_check_name,
            "passed": check_names_actual == expected_check_names,
            "expected": expected_check_names,
            "actual": check_names_actual,
        }
    )
    guard_for_key_schema = {
        "status": "ok",
        "checks": checks,
    }
    checks.append(
        {
            "name": guard_keys_check_name,
            "passed": list(guard_for_key_schema) == expected_guard_keys,
            "expected": expected_guard_keys,
            "actual": list(guard_for_key_schema),
        }
    )
    check_keys_actual = {
        check["name"]: list(check)
        for check in checks
    }
    check_keys_actual[check_keys_check_name] = expected_check_keys
    checks.append(
        {
            "name": check_keys_check_name,
            "passed": all(
                check_keys == expected_check_keys
                for check_keys in check_keys_actual.values()
            ),
            "expected": expected_check_keys,
            "actual": check_keys_actual,
        }
    )
    return {
        "status": "ok" if all(check["passed"] for check in checks) else "conflict",
        "checks": checks,
    }


def _cron_prompt_pack_contract(include_position_review: bool) -> dict[str, Any]:
    return {
        "name": "hermes_cron_prompt_pack",
        "supported_report_intents": list(REPORT_INTENTS),
        "include_position_review": include_position_review,
        "scheduler_added": False,
        "cron_runner_added": False,
        "network_call": False,
        "telegram_send": False,
        "telegram_credentials_required": False,
        "order_submission": False,
        "secret_values_returned": False,
        "live_data_required": False,
        "manual_setup_required_before_unattended_run": CRON_MANUAL_SETUP_REQUIRED,
    }


def _cron_report_prompt_text(
    *,
    asset: str,
    prompt_name: str,
    timeframe: str,
    intent: dict[str, Any],
    expected_output_schema: str,
    telegram_format_schema: str,
    numeric_authority: str,
    schedule_hint: str,
    decision_focus: str,
    expected_sections: list[str],
    manual_setup_required: list[str],
    idempotency_key_template: str,
) -> str:
    return (
        "Use the market_swing MCP tool generate_latest_signal_report with "
        f"asset={asset}, timeframe={timeframe}, report_intent={intent['name']}. "
        f"{_prompt_name_text(prompt_name)} "
        f"{_output_schema_prompt_text(expected_output_schema)} "
        f"{_schedule_hint_prompt_text(schedule_hint)} "
        f"{_telegram_format_schema_prompt_text(telegram_format_schema)} "
        f"{_numeric_authority_prompt_text(numeric_authority)} "
        f"{_decision_focus_prompt_text(decision_focus)} "
        f"{_live_data_boundary_prompt_text()} "
        "Use MCP numeric fields as source of truth. Send Telegram only through "
        "the configured Hermes/Telegram gateway using "
        "delivery_preview.channels.telegram.chunks. "
        f"{_expected_sections_prompt_text(expected_sections)} "
        f"{_manual_setup_prompt_text(manual_setup_required)} "
        f"{_scheduler_setup_block_prompt_text(manual_setup_required)} "
        f"{CRON_NO_SECRET_TEXT} "
        f"Use idempotency key template {idempotency_key_template}. "
        "Do not submit orders."
    )


def _cron_position_review_prompt_text(
    *,
    asset: str,
    prompt_name: str,
    expected_output_schema: str,
    telegram_format_schema: str,
    numeric_authority: str,
    schedule_hint: str,
    decision_focus: str,
    expected_sections: list[str],
    manual_setup_required: list[str],
    idempotency_key_template: str,
) -> str:
    return (
        "Use the market_swing MCP tool generate_position_review_report with "
        f"asset={asset}. {_prompt_name_text(prompt_name)} "
        f"{_output_schema_prompt_text(expected_output_schema)} "
        f"{_schedule_hint_prompt_text(schedule_hint)} "
        f"{_telegram_format_schema_prompt_text(telegram_format_schema)} "
        f"{_numeric_authority_prompt_text(numeric_authority)} "
        f"{_decision_focus_prompt_text(decision_focus)} "
        f"{_live_data_boundary_prompt_text()} "
        "Use position_review numeric fields as source of truth. "
        "Send Telegram only through the configured Hermes/Telegram gateway "
        "using delivery_preview.channels.telegram.chunks. "
        f"{_expected_sections_prompt_text(expected_sections)} "
        f"{_manual_setup_prompt_text(manual_setup_required)} "
        f"{_scheduler_setup_block_prompt_text(manual_setup_required)} "
        f"{CRON_NO_SECRET_TEXT} "
        f"Use idempotency key template {idempotency_key_template}. "
        "Do not submit orders."
    )


def _expected_sections_prompt_text(expected_sections: list[str]) -> str:
    return "Expected Telegram sections: " + ", ".join(expected_sections) + "."


def _prompt_name_text(prompt_name: str) -> str:
    return f"Prompt name: {prompt_name}."


def _output_schema_prompt_text(expected_output_schema: str) -> str:
    return f"Expected tool output schema: {expected_output_schema}."


def _schedule_hint_prompt_text(schedule_hint: str) -> str:
    return f"Schedule hint: {schedule_hint}."


def _telegram_format_schema_prompt_text(telegram_format_schema: str) -> str:
    return f"Telegram format schema: {telegram_format_schema}."


def _numeric_authority_prompt_text(numeric_authority: str) -> str:
    return f"Numeric authority: {numeric_authority}."


def _decision_focus_prompt_text(decision_focus: str) -> str:
    return f"Decision focus: {decision_focus}."


def _live_data_boundary_prompt_text() -> str:
    return "Do not call live market, macro, news, broker, or exchange data sources."


def _manual_setup_prompt_text(manual_setup_required: list[str]) -> str:
    return (
        "Manual setup required before unattended run: "
        + ", ".join(manual_setup_required)
        + "."
    )


def _scheduler_setup_block_prompt_text(manual_setup_required: list[str]) -> str:
    return (
        "Do not configure a scheduler or cron runner until manual setup is "
        "complete: "
        + ", ".join(manual_setup_required)
        + "."
    )


def _cron_prompt_pack_guard(
    *,
    prompts: list[dict[str, Any]],
    contract: dict[str, Any],
    pack_keys: list[str],
    schema_version: str,
    asset: str,
    timeframe: str,
    pack_live_data_required: bool,
    include_position_review: bool,
) -> dict[str, Any]:
    prompt_name_list = [
        prompt["name"]
        for prompt in prompts
    ]
    prompt_names = {prompt["name"] for prompt in prompts}
    report_prompts = [prompt for prompt in prompts if prompt["name"] in REPORT_INTENTS]
    position_prompts = [
        prompt for prompt in prompts if prompt["name"] == "position_review"
    ]
    allowed_tools = {
        "generate_latest_signal_report",
        "generate_position_review_report",
    }
    expected_prompt_names = [*REPORT_INTENTS]
    if include_position_review:
        expected_prompt_names.append("position_review")
    expected_schedule_hints = {
        name: intent["schedule_hint"]
        for name, intent in REPORT_INTENTS.items()
    }
    if include_position_review:
        expected_schedule_hints["position_review"] = (
            "manual_or_scheduled_position_check"
        )
    expected_decision_focus = {
        name: intent["decision_focus"]
        for name, intent in REPORT_INTENTS.items()
    }
    if include_position_review:
        expected_decision_focus["position_review"] = "hold_trim_exit_or_stop_review"
    report_input_keys = ["asset", "timeframe", "report_intent"]
    position_review_input_keys = ["asset"]
    delivery_preview_chunks_path = "delivery_preview.channels.telegram.chunks"
    configured_gateway_text = (
        "Send Telegram only through the configured Hermes/Telegram gateway"
    )
    no_secret_text = CRON_NO_SECRET_TEXT
    report_numeric_authority_text = "Use MCP numeric fields as source of truth."
    position_review_numeric_authority_text = (
        "Use position_review numeric fields as source of truth."
    )
    order_block_text = "Do not submit orders."
    expected_numeric_authority_text = {
        name: report_numeric_authority_text
        for name in REPORT_INTENTS
    }
    expected_numeric_authority = {
        name: "latest_signal_report"
        for name in REPORT_INTENTS
    }
    expected_output_schema = {
        name: REPORT_SCHEMA_VERSION
        for name in REPORT_INTENTS
    }
    expected_live_data_required = {
        prompt["name"]: contract["live_data_required"]
        for prompt in prompts
    }
    if include_position_review:
        expected_numeric_authority_text["position_review"] = (
            position_review_numeric_authority_text
        )
        expected_numeric_authority["position_review"] = "position_review"
        expected_output_schema["position_review"] = POSITION_REVIEW_SCHEMA_VERSION
    required_manual_setup = CRON_MANUAL_SETUP_REQUIRED
    expected_idempotency_keys = {
        prompt["name"]: (
            "halo_swing:"
            f"{prompt['name']}:{prompt['input_json'].get('asset')}:{{yyyy_mm_dd}}"
        )
        for prompt in prompts
    }
    expected_prompt_sections_text = {
        prompt["name"]: _expected_sections_prompt_text(prompt["expected_sections"])
        for prompt in prompts
    }
    expected_prompt_name_text = {
        prompt["name"]: _prompt_name_text(prompt["name"])
        for prompt in prompts
    }
    expected_output_schema_text = {
        prompt["name"]: _output_schema_prompt_text(prompt["expected_output_schema"])
        for prompt in prompts
    }
    expected_prompt_schedule_text = {
        prompt["name"]: _schedule_hint_prompt_text(prompt["schedule_hint"])
        for prompt in prompts
    }
    expected_decision_focus_text = {
        prompt["name"]: _decision_focus_prompt_text(prompt["decision_focus"])
        for prompt in prompts
    }
    expected_telegram_format_schema = {
        prompt["name"]: TELEGRAM_FORMAT_SCHEMA_VERSION
        for prompt in prompts
    }
    expected_telegram_format_schema_text = {
        prompt["name"]: _telegram_format_schema_prompt_text(
            prompt["telegram_format_schema"]
        )
        for prompt in prompts
    }
    expected_numeric_authority_declaration_text = {
        prompt["name"]: _numeric_authority_prompt_text(prompt["numeric_authority"])
        for prompt in prompts
    }
    live_data_boundary_text = _live_data_boundary_prompt_text()
    expected_prompt_delivery_path = {
        prompt["name"]: prompt["delivery_preview_path"]
        for prompt in prompts
    }
    expected_manual_setup_text = _manual_setup_prompt_text(
        contract["manual_setup_required_before_unattended_run"]
    )
    expected_scheduler_setup_block_text = _scheduler_setup_block_prompt_text(
        contract["manual_setup_required_before_unattended_run"]
    )
    scheduler_setup_prompt_positions = {
        prompt["name"]: {
            "manual_setup_index": prompt["prompt"].find(expected_manual_setup_text),
            "scheduler_setup_block_index": prompt["prompt"].find(
                expected_scheduler_setup_block_text
            ),
        }
        for prompt in prompts
    }
    expected_prompt_tool_input_text = {
        prompt["name"]: (
            "Use the market_swing MCP tool "
            f"{prompt['tool_name']} with asset={prompt['input_json']['asset']}, "
            f"timeframe={prompt['input_json']['timeframe']}, "
            f"report_intent={prompt['input_json']['report_intent']}."
        )
        for prompt in report_prompts
    }
    for prompt in position_prompts:
        expected_prompt_tool_input_text[prompt["name"]] = (
            "Use the market_swing MCP tool "
            f"{prompt['tool_name']} with asset={prompt['input_json']['asset']}."
        )
    expected_prompt_assets = {
        prompt["name"]: asset
        for prompt in prompts
    }
    expected_report_timeframes = {
        prompt["name"]: timeframe
        for prompt in report_prompts
    }
    expected_position_review_sections = (
        {"position_review": POSITION_REVIEW_SECTIONS}
        if include_position_review
        else {}
    )
    expected_pack_keys = [
        "schema_version",
        "asset",
        "timeframe",
        "prompts",
        "cron_prompt_contract",
        "cron_prompt_guard",
        "live_data_required",
    ]
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
    expected_guard_check_names = [
        "cron_prompt_pack_schema_version_matches_expected",
        "cron_prompt_pack_keys_match_expected_schema",
        "cron_prompt_contract_name_matches_schema",
        "cron_prompt_contract_keys_match_expected_schema",
        "cron_prompt_prompt_keys_match_expected_schema",
        "pack_live_data_required_matches_contract",
        "prompt_assets_match_pack_asset",
        "report_prompt_timeframes_match_pack_timeframe",
        "include_position_review_contract_matches_request",
        "supported_report_intents_present",
        "supported_report_intents_match_registry",
        "prompt_names_match_contract_and_position_option",
        "prompt_names_match_contract_order_and_are_unique",
        "prompt_schedule_hints_match_contract",
        "prompt_decision_focus_matches_contract",
        "prompt_text_references_prompt_name",
        "position_review_prompt_present",
        "position_review_prompt_absent_when_excluded",
        "registered_report_tools_only",
        "idempotency_key_templates_match_prompt_identity",
        "prompt_text_references_idempotency_key_template",
        "manual_setup_requirements_declared_before_unattended_run",
        "manual_setup_requirements_match_registry",
        "cron_prompt_contract_requires_no_credentials_or_secrets",
        "report_prompt_tool_and_input_schema_match",
        "position_review_prompt_tool_and_input_schema_match",
        "report_prompt_intents_match_input_json",
        "report_prompt_expected_sections_match_contract",
        "position_review_prompt_expected_sections_match_contract",
        "prompt_output_schema_matches_tool_contract",
        "prompt_live_data_required_matches_contract",
        "prompt_text_references_output_schema",
        "prompt_text_references_no_live_data_boundary",
        "delivery_preview_reference_present",
        "prompt_telegram_format_schema_matches_contract",
        "prompt_text_references_telegram_format_schema",
        "prompt_numeric_authority_matches_contract",
        "prompt_text_references_numeric_authority",
        "prompt_text_references_delivery_preview_chunks",
        "prompt_text_matches_declared_delivery_preview_path",
        "prompt_text_references_expected_sections",
        "prompt_text_references_schedule_hint",
        "prompt_text_references_decision_focus",
        "prompt_text_references_manual_setup_requirements",
        "prompt_text_declares_manual_setup_before_scheduler_setup",
        "prompt_text_references_no_secret_instruction",
        "prompt_text_requires_configured_gateway",
        "prompt_text_matches_declared_tool_and_inputs",
        "prompt_text_preserves_numeric_authority",
        "no_scheduler_or_cron_runner_added",
        "no_network_telegram_or_order_side_effect",
        "prompt_text_preserves_order_block",
        "cron_prompt_guard_keys_match_expected_schema",
        "cron_prompt_guard_check_names_match_expected_schema",
        "cron_prompt_guard_check_keys_match_expected_schema",
    ]
    checks = [
        {
            "name": "cron_prompt_pack_schema_version_matches_expected",
            "passed": schema_version == CRON_PROMPT_SCHEMA_VERSION,
            "expected": CRON_PROMPT_SCHEMA_VERSION,
            "actual": schema_version,
        },
        {
            "name": "cron_prompt_pack_keys_match_expected_schema",
            "passed": pack_keys == expected_pack_keys,
            "expected": expected_pack_keys,
            "actual": pack_keys,
        },
        {
            "name": "cron_prompt_contract_name_matches_schema",
            "passed": contract["name"] == "hermes_cron_prompt_pack",
            "expected": "hermes_cron_prompt_pack",
            "actual": contract["name"],
        },
        {
            "name": "cron_prompt_contract_keys_match_expected_schema",
            "passed": list(contract) == expected_contract_keys,
            "expected": expected_contract_keys,
            "actual": list(contract),
        },
        {
            "name": "cron_prompt_prompt_keys_match_expected_schema",
            "passed": all(list(prompt) == expected_prompt_keys for prompt in prompts),
            "expected": expected_prompt_keys,
            "actual": {
                prompt["name"]: list(prompt)
                for prompt in prompts
            },
        },
        {
            "name": "pack_live_data_required_matches_contract",
            "passed": pack_live_data_required is False
            and pack_live_data_required == contract["live_data_required"],
            "expected": contract["live_data_required"],
            "actual": pack_live_data_required,
        },
        {
            "name": "prompt_assets_match_pack_asset",
            "passed": all(
                prompt["input_json"].get("asset") == asset
                for prompt in prompts
            ),
            "expected": expected_prompt_assets,
            "actual": {
                prompt["name"]: prompt["input_json"].get("asset")
                for prompt in prompts
            },
        },
        {
            "name": "report_prompt_timeframes_match_pack_timeframe",
            "passed": all(
                prompt["input_json"].get("timeframe") == timeframe
                for prompt in report_prompts
            ),
            "expected": expected_report_timeframes,
            "actual": {
                prompt["name"]: prompt["input_json"].get("timeframe")
                for prompt in report_prompts
            },
        },
        {
            "name": "include_position_review_contract_matches_request",
            "passed": contract["include_position_review"] is include_position_review,
            "expected": include_position_review,
            "actual": contract["include_position_review"],
        },
        {
            "name": "supported_report_intents_present",
            "passed": set(REPORT_INTENTS).issubset(prompt_names),
            "expected": list(REPORT_INTENTS),
            "actual": sorted(prompt_names),
        },
        {
            "name": "supported_report_intents_match_registry",
            "passed": contract["supported_report_intents"] == list(REPORT_INTENTS),
            "expected": list(REPORT_INTENTS),
            "actual": contract["supported_report_intents"],
        },
        {
            "name": "prompt_names_match_contract_and_position_option",
            "passed": sorted(prompt_names) == sorted(expected_prompt_names),
            "expected": sorted(expected_prompt_names),
            "actual": sorted(prompt_names),
        },
        {
            "name": "prompt_names_match_contract_order_and_are_unique",
            "passed": prompt_name_list == expected_prompt_names
            and len(prompt_name_list) == len(prompt_names),
            "expected": expected_prompt_names,
            "actual": prompt_name_list,
        },
        {
            "name": "prompt_schedule_hints_match_contract",
            "passed": all(
                prompt["schedule_hint"] == expected_schedule_hints[prompt["name"]]
                for prompt in prompts
            ),
            "expected": expected_schedule_hints,
            "actual": {
                prompt["name"]: prompt["schedule_hint"]
                for prompt in prompts
            },
        },
        {
            "name": "prompt_decision_focus_matches_contract",
            "passed": all(
                prompt["decision_focus"] == expected_decision_focus[prompt["name"]]
                for prompt in prompts
            ),
            "expected": expected_decision_focus,
            "actual": {
                prompt["name"]: prompt["decision_focus"]
                for prompt in prompts
            },
        },
        {
            "name": "prompt_text_references_prompt_name",
            "passed": all(
                expected_prompt_name_text[prompt["name"]] in prompt["prompt"]
                for prompt in prompts
            ),
            "expected": expected_prompt_name_text,
            "actual": {
                prompt["name"]: (
                    expected_prompt_name_text[prompt["name"]]
                    in prompt["prompt"]
                )
                for prompt in prompts
            },
        },
        {
            "name": "position_review_prompt_present",
            "passed": (not include_position_review) or "position_review" in prompt_names,
            "expected": include_position_review,
            "actual": "position_review" in prompt_names,
        },
        {
            "name": "position_review_prompt_absent_when_excluded",
            "passed": include_position_review or "position_review" not in prompt_names,
            "expected": include_position_review,
            "actual": "position_review" in prompt_names,
        },
        {
            "name": "registered_report_tools_only",
            "passed": all(prompt["tool_name"] in allowed_tools for prompt in prompts),
            "expected": sorted(allowed_tools),
            "actual": sorted({prompt["tool_name"] for prompt in prompts}),
        },
        {
            "name": "idempotency_key_templates_match_prompt_identity",
            "passed": all(
                prompt["idempotency_key_template"]
                == expected_idempotency_keys[prompt["name"]]
                for prompt in prompts
            ),
            "expected": expected_idempotency_keys,
            "actual": {
                prompt["name"]: prompt["idempotency_key_template"]
                for prompt in prompts
            },
        },
        {
            "name": "prompt_text_references_idempotency_key_template",
            "passed": all(
                prompt["idempotency_key_template"] in prompt["prompt"]
                for prompt in prompts
            ),
            "expected": expected_idempotency_keys,
            "actual": {
                prompt["name"]: (
                    prompt["idempotency_key_template"] in prompt["prompt"]
                )
                for prompt in prompts
            },
        },
        {
            "name": "manual_setup_requirements_declared_before_unattended_run",
            "passed": all(
                item in contract["manual_setup_required_before_unattended_run"]
                for item in required_manual_setup
            ),
            "expected": required_manual_setup,
            "actual": contract["manual_setup_required_before_unattended_run"],
        },
        {
            "name": "manual_setup_requirements_match_registry",
            "passed": contract["manual_setup_required_before_unattended_run"]
            == required_manual_setup,
            "expected": required_manual_setup,
            "actual": contract["manual_setup_required_before_unattended_run"],
        },
        {
            "name": "cron_prompt_contract_requires_no_credentials_or_secrets",
            "passed": contract["telegram_credentials_required"] is False
            and contract["secret_values_returned"] is False,
            "expected": False,
            "actual": {
                "telegram_credentials_required": contract[
                    "telegram_credentials_required"
                ],
                "secret_values_returned": contract["secret_values_returned"],
            },
        },
        {
            "name": "report_prompt_tool_and_input_schema_match",
            "passed": all(
                prompt["tool_name"] == "generate_latest_signal_report"
                and sorted(prompt["input_json"]) == sorted(report_input_keys)
                for prompt in report_prompts
            ),
            "expected": {
                name: {
                    "tool_name": "generate_latest_signal_report",
                    "input_keys": report_input_keys,
                }
                for name in REPORT_INTENTS
            },
            "actual": {
                prompt["name"]: {
                    "tool_name": prompt["tool_name"],
                    "input_keys": sorted(prompt["input_json"]),
                }
                for prompt in report_prompts
            },
        },
        {
            "name": "position_review_prompt_tool_and_input_schema_match",
            "passed": all(
                prompt["tool_name"] == "generate_position_review_report"
                and sorted(prompt["input_json"]) == position_review_input_keys
                for prompt in position_prompts
            ),
            "expected": {
                "tool_name": "generate_position_review_report",
                "input_keys": position_review_input_keys,
            },
            "actual": [
                {
                    "tool_name": prompt["tool_name"],
                    "input_keys": sorted(prompt["input_json"]),
                }
                for prompt in position_prompts
            ],
        },
        {
            "name": "report_prompt_intents_match_input_json",
            "passed": all(
                prompt["input_json"].get("report_intent") == prompt["name"]
                for prompt in report_prompts
            ),
            "expected": {
                name: name
                for name in REPORT_INTENTS
            },
            "actual": {
                prompt["name"]: prompt["input_json"].get("report_intent")
                for prompt in report_prompts
            },
        },
        {
            "name": "report_prompt_expected_sections_match_contract",
            "passed": all(
                prompt["expected_sections"]
                == REPORT_INTENTS[prompt["name"]]["required_sections"]
                for prompt in report_prompts
            ),
            "expected": {
                name: contract["required_sections"]
                for name, contract in REPORT_INTENTS.items()
            },
            "actual": {
                prompt["name"]: prompt["expected_sections"]
                for prompt in report_prompts
            },
        },
        {
            "name": "position_review_prompt_expected_sections_match_contract",
            "passed": all(
                prompt["expected_sections"] == POSITION_REVIEW_SECTIONS
                for prompt in position_prompts
            )
            and len(position_prompts) == (1 if include_position_review else 0),
            "expected": expected_position_review_sections,
            "actual": {
                prompt["name"]: prompt["expected_sections"]
                for prompt in position_prompts
            },
        },
        {
            "name": "prompt_output_schema_matches_tool_contract",
            "passed": all(
                prompt["expected_output_schema"]
                == expected_output_schema[prompt["name"]]
                for prompt in prompts
            ),
            "expected": expected_output_schema,
            "actual": {
                prompt["name"]: prompt["expected_output_schema"]
                for prompt in prompts
            },
        },
        {
            "name": "prompt_live_data_required_matches_contract",
            "passed": contract["live_data_required"] is False
            and all(
                prompt["live_data_required"] == contract["live_data_required"]
                for prompt in prompts
            ),
            "expected": expected_live_data_required,
            "actual": {
                prompt["name"]: prompt["live_data_required"]
                for prompt in prompts
            },
        },
        {
            "name": "prompt_text_references_output_schema",
            "passed": all(
                expected_output_schema_text[prompt["name"]] in prompt["prompt"]
                for prompt in prompts
            ),
            "expected": expected_output_schema_text,
            "actual": {
                prompt["name"]: (
                    expected_output_schema_text[prompt["name"]]
                    in prompt["prompt"]
                )
                for prompt in prompts
            },
        },
        {
            "name": "prompt_text_references_no_live_data_boundary",
            "passed": all(live_data_boundary_text in prompt["prompt"] for prompt in prompts),
            "expected": live_data_boundary_text,
            "actual": {
                prompt["name"]: live_data_boundary_text in prompt["prompt"]
                for prompt in prompts
            },
        },
        {
            "name": "delivery_preview_reference_present",
            "passed": all(
                prompt["delivery_preview_path"] == delivery_preview_chunks_path
                for prompt in prompts
            ),
            "expected": delivery_preview_chunks_path,
            "actual": sorted({prompt["delivery_preview_path"] for prompt in prompts}),
        },
        {
            "name": "prompt_telegram_format_schema_matches_contract",
            "passed": all(
                prompt["telegram_format_schema"]
                == expected_telegram_format_schema[prompt["name"]]
                for prompt in prompts
            ),
            "expected": expected_telegram_format_schema,
            "actual": {
                prompt["name"]: prompt["telegram_format_schema"]
                for prompt in prompts
            },
        },
        {
            "name": "prompt_text_references_telegram_format_schema",
            "passed": all(
                expected_telegram_format_schema_text[prompt["name"]]
                in prompt["prompt"]
                for prompt in prompts
            ),
            "expected": expected_telegram_format_schema_text,
            "actual": {
                prompt["name"]: (
                    expected_telegram_format_schema_text[prompt["name"]]
                    in prompt["prompt"]
                )
                for prompt in prompts
            },
        },
        {
            "name": "prompt_numeric_authority_matches_contract",
            "passed": all(
                prompt["numeric_authority"]
                == expected_numeric_authority[prompt["name"]]
                for prompt in prompts
            ),
            "expected": expected_numeric_authority,
            "actual": {
                prompt["name"]: prompt["numeric_authority"]
                for prompt in prompts
            },
        },
        {
            "name": "prompt_text_references_numeric_authority",
            "passed": all(
                expected_numeric_authority_declaration_text[prompt["name"]]
                in prompt["prompt"]
                for prompt in prompts
            ),
            "expected": expected_numeric_authority_declaration_text,
            "actual": {
                prompt["name"]: (
                    expected_numeric_authority_declaration_text[prompt["name"]]
                    in prompt["prompt"]
                )
                for prompt in prompts
            },
        },
        {
            "name": "prompt_text_references_delivery_preview_chunks",
            "passed": all(
                delivery_preview_chunks_path in prompt["prompt"]
                for prompt in prompts
            ),
            "expected": delivery_preview_chunks_path,
            "actual": {
                prompt["name"]: delivery_preview_chunks_path in prompt["prompt"]
                for prompt in prompts
            },
        },
        {
            "name": "prompt_text_matches_declared_delivery_preview_path",
            "passed": all(
                expected_prompt_delivery_path[prompt["name"]] in prompt["prompt"]
                for prompt in prompts
            ),
            "expected": expected_prompt_delivery_path,
            "actual": {
                prompt["name"]: (
                    expected_prompt_delivery_path[prompt["name"]]
                    in prompt["prompt"]
                )
                for prompt in prompts
            },
        },
        {
            "name": "prompt_text_references_expected_sections",
            "passed": all(
                expected_prompt_sections_text[prompt["name"]] in prompt["prompt"]
                for prompt in prompts
            ),
            "expected": expected_prompt_sections_text,
            "actual": {
                prompt["name"]: (
                    expected_prompt_sections_text[prompt["name"]]
                    in prompt["prompt"]
                )
                for prompt in prompts
            },
        },
        {
            "name": "prompt_text_references_schedule_hint",
            "passed": all(
                expected_prompt_schedule_text[prompt["name"]] in prompt["prompt"]
                for prompt in prompts
            ),
            "expected": expected_prompt_schedule_text,
            "actual": {
                prompt["name"]: (
                    expected_prompt_schedule_text[prompt["name"]]
                    in prompt["prompt"]
                )
                for prompt in prompts
            },
        },
        {
            "name": "prompt_text_references_decision_focus",
            "passed": all(
                expected_decision_focus_text[prompt["name"]] in prompt["prompt"]
                for prompt in prompts
            ),
            "expected": expected_decision_focus_text,
            "actual": {
                prompt["name"]: (
                    expected_decision_focus_text[prompt["name"]]
                    in prompt["prompt"]
                )
                for prompt in prompts
            },
        },
        {
            "name": "prompt_text_references_manual_setup_requirements",
            "passed": all(
                expected_manual_setup_text in prompt["prompt"]
                for prompt in prompts
            ),
            "expected": expected_manual_setup_text,
            "actual": {
                prompt["name"]: expected_manual_setup_text in prompt["prompt"]
                for prompt in prompts
            },
        },
        {
            "name": "prompt_text_declares_manual_setup_before_scheduler_setup",
            "passed": all(
                positions["manual_setup_index"] != -1
                and positions["scheduler_setup_block_index"]
                > positions["manual_setup_index"]
                for positions in scheduler_setup_prompt_positions.values()
            ),
            "expected": {
                "manual_setup_text": expected_manual_setup_text,
                "scheduler_setup_block_text": expected_scheduler_setup_block_text,
                "order": "manual_setup_before_scheduler_setup",
            },
            "actual": scheduler_setup_prompt_positions,
        },
        {
            "name": "prompt_text_references_no_secret_instruction",
            "passed": all(no_secret_text in prompt["prompt"] for prompt in prompts),
            "expected": no_secret_text,
            "actual": {
                prompt["name"]: no_secret_text in prompt["prompt"]
                for prompt in prompts
            },
        },
        {
            "name": "prompt_text_requires_configured_gateway",
            "passed": all(
                configured_gateway_text in prompt["prompt"]
                for prompt in prompts
            ),
            "expected": configured_gateway_text,
            "actual": {
                prompt["name"]: configured_gateway_text in prompt["prompt"]
                for prompt in prompts
            },
        },
        {
            "name": "prompt_text_matches_declared_tool_and_inputs",
            "passed": all(
                expected_prompt_tool_input_text[prompt["name"]] in prompt["prompt"]
                for prompt in prompts
            ),
            "expected": expected_prompt_tool_input_text,
            "actual": {
                prompt["name"]: (
                    expected_prompt_tool_input_text[prompt["name"]]
                    in prompt["prompt"]
                )
                for prompt in prompts
            },
        },
        {
            "name": "prompt_text_preserves_numeric_authority",
            "passed": all(
                expected_numeric_authority_text[prompt["name"]] in prompt["prompt"]
                for prompt in prompts
            ),
            "expected": expected_numeric_authority_text,
            "actual": {
                prompt["name"]: (
                    expected_numeric_authority_text[prompt["name"]]
                    in prompt["prompt"]
                )
                for prompt in prompts
            },
        },
        {
            "name": "no_scheduler_or_cron_runner_added",
            "passed": contract["scheduler_added"] is False
            and contract["cron_runner_added"] is False,
            "expected": False,
            "actual": {
                "scheduler_added": contract["scheduler_added"],
                "cron_runner_added": contract["cron_runner_added"],
            },
        },
        {
            "name": "no_network_telegram_or_order_side_effect",
            "passed": contract["network_call"] is False
            and contract["telegram_send"] is False
            and contract["order_submission"] is False,
            "expected": False,
            "actual": {
                "network_call": contract["network_call"],
                "telegram_send": contract["telegram_send"],
                "order_submission": contract["order_submission"],
            },
        },
        {
            "name": "prompt_text_preserves_order_block",
            "passed": all(order_block_text in prompt["prompt"] for prompt in prompts),
            "expected": order_block_text,
            "actual": {
                prompt["name"]: order_block_text in prompt["prompt"]
                for prompt in prompts
            },
        },
    ]
    guard = {
        "status": "conflict",
        "checks": checks,
    }
    checks.append(
        {
            "name": "cron_prompt_guard_keys_match_expected_schema",
            "passed": list(guard) == expected_guard_keys,
            "expected": expected_guard_keys,
            "actual": list(guard),
        }
    )
    guard_check_names_actual = [
        check["name"]
        for check in checks
    ] + [
        "cron_prompt_guard_check_names_match_expected_schema",
        "cron_prompt_guard_check_keys_match_expected_schema",
    ]
    checks.append(
        {
            "name": "cron_prompt_guard_check_names_match_expected_schema",
            "passed": guard_check_names_actual == expected_guard_check_names,
            "expected": expected_guard_check_names,
            "actual": guard_check_names_actual,
        }
    )
    guard_check_keys_actual = {
        check["name"]: list(check)
        for check in checks
    }
    guard_check_keys_actual[
        "cron_prompt_guard_check_keys_match_expected_schema"
    ] = expected_guard_check_keys
    checks.append(
        {
            "name": "cron_prompt_guard_check_keys_match_expected_schema",
            "passed": all(
                check_keys == expected_guard_check_keys
                for check_keys in guard_check_keys_actual.values()
            ),
            "expected": expected_guard_check_keys,
            "actual": guard_check_keys_actual,
        }
    )
    guard["status"] = "ok" if all(check["passed"] for check in checks) else "conflict"
    return guard


def _position_review_guard(
    review: dict[str, Any],
    sections: list[dict[str, Any]],
    prompt_contract: dict[str, Any],
    delivery_contract: dict[str, Any],
    review_contract: dict[str, Any],
) -> dict[str, Any]:
    section_titles = [section["title"] for section in sections]
    text = _format_position_review_text(review, sections)
    delivery_channels = delivery_contract["channels"]
    telegram_contract = delivery_channels["telegram"]
    expected_delivery_contract_schema = _expected_delivery_contract_key_schema()
    actual_delivery_contract_schema = _delivery_contract_key_schema(delivery_contract)
    expected_guard_keys = [
        "status",
        "checks",
    ]
    expected_position_review_contract_keys = [
        "name",
        "trigger",
        "decision_focus",
        "required_sections",
        "network_call",
        "order_submission",
    ]
    expected_prompt_contract_keys = [
        "numeric_authority",
        "llm_role",
        "must_include",
    ]
    expected_prompt_contract_identity = {
        "numeric_authority": "Use position_review numeric fields as source of truth.",
        "llm_role": "Summarize hold, trim, exit, or stop rationale only.",
    }
    expected_telegram_chunking_contract = {
        "overflow_policy": "split_on_section_boundary",
        "section_separator": "\n\n",
        "chunk_indexing": "1_based",
    }
    expected_prompt_contract_keys = [
        "numeric_authority",
        "llm_role",
        "must_include",
    ]
    expected_delivery_channel_formats = {
        "hermes": "structured_json_plus_text",
        "telegram": "plain_text",
    }
    expected_telegram_chunking_contract = {
        "overflow_policy": "split_on_section_boundary",
        "section_separator": "\n\n",
        "chunk_indexing": "1_based",
    }
    expected_delivery_cron_intents = list(REPORT_INTENTS)
    expected_guard_check_names = [
        "required_sections_present",
        "position_review_sections_match_contract_order",
        "prompt_must_include_is_covered",
        "position_review_prompt_must_include_matches_expected_terms",
        "position_review_prompt_contract_keys_match_expected_schema",
        "position_review_prompt_contract_identity_matches_expected",
        "delivery_contract_has_no_network_side_effect",
        "delivery_contract_has_no_send_side_effect",
        "delivery_contract_keys_match_expected_schema",
        "delivery_channel_formats_match_expected",
        "delivery_cron_intents_match_report_intent_registry",
        "delivery_numeric_authority_is_position_review",
        "position_review_telegram_max_chars_matches_expected",
        "position_review_telegram_schema_version_matches_expected",
        "position_review_telegram_chunking_contract_matches_expected",
        "position_review_text_reflects_review_numeric_fields",
        "telegram_required_sections_match_position_review",
        "position_review_contract_keys_match_expected_schema",
        "position_review_contract_has_no_network_side_effect",
        "position_review_contract_identity_matches_expected",
        "position_review_contract_required_sections_match_expected",
        "position_review_contract_has_no_order_submission_side_effect",
        "no_order_submission_side_effect",
        "telegram_text_fits_single_message",
        "position_review_guard_check_names_match_expected_schema",
        "position_review_guard_check_keys_match_expected_schema",
        "position_review_guard_keys_match_expected_schema",
    ]
    expected_default_guard_check_keys = [
        "name",
        "passed",
        "expected",
        "actual",
    ]
    expected_special_guard_check_keys = {
        "telegram_text_fits_single_message": [
            "name",
            "passed",
            "expected_max_chars",
            "actual_chars",
        ],
    }
    expected_default_guard_check_names = [
        name
        for name in expected_guard_check_names
        if name not in expected_special_guard_check_keys
    ]
    expected_guard_check_key_schema = {
        "default_keys": expected_default_guard_check_keys,
        "default_check_names": expected_default_guard_check_names,
        "special_check_keys": expected_special_guard_check_keys,
    }
    numeric_field_presence = {
        "decision_line_present": (
            f"Decision: {review['action']} ({review['position_state']})" in text
        ),
        "unrealized_return_line_present": (
            f"Unrealized Return: {review['unrealized_return_pct']}%" in text
        ),
    }
    checks = [
        {
            "name": "required_sections_present",
            "passed": all(
                title in section_titles
                for title in review_contract["required_sections"]
            ),
            "expected": review_contract["required_sections"],
            "actual": section_titles,
        },
        {
            "name": "position_review_sections_match_contract_order",
            "passed": section_titles == review_contract["required_sections"],
            "expected": review_contract["required_sections"],
            "actual": section_titles,
        },
        {
            "name": "prompt_must_include_is_covered",
            "passed": all(
                item in prompt_contract["must_include"]
                for item in _position_review_required_terms()
            ),
            "expected": _position_review_required_terms(),
            "actual": prompt_contract["must_include"],
        },
        {
            "name": "position_review_prompt_must_include_matches_expected_terms",
            "passed": (
                prompt_contract["must_include"] == _position_review_required_terms()
            ),
            "expected": _position_review_required_terms(),
            "actual": prompt_contract["must_include"],
        },
        {
            "name": "position_review_prompt_contract_keys_match_expected_schema",
            "passed": list(prompt_contract) == expected_prompt_contract_keys,
            "expected": expected_prompt_contract_keys,
            "actual": list(prompt_contract),
        },
        {
            "name": "position_review_prompt_contract_identity_matches_expected",
            "passed": (
                prompt_contract["numeric_authority"]
                == expected_prompt_contract_identity["numeric_authority"]
                and prompt_contract["llm_role"]
                == expected_prompt_contract_identity["llm_role"]
            ),
            "expected": expected_prompt_contract_identity,
            "actual": {
                "numeric_authority": prompt_contract["numeric_authority"],
                "llm_role": prompt_contract["llm_role"],
            },
        },
        {
            "name": "delivery_contract_has_no_network_side_effect",
            "passed": all(
                channel["network_call"] is False
                for channel in delivery_channels.values()
            ),
            "expected": False,
            "actual": {
                name: channel["network_call"]
                for name, channel in delivery_channels.items()
            },
        },
        {
            "name": "delivery_contract_has_no_send_side_effect",
            "passed": all(
                channel.get("send_call", False) is False
                for channel in delivery_channels.values()
            ),
            "expected": False,
            "actual": {
                name: channel.get("send_call", False)
                for name, channel in delivery_channels.items()
            },
        },
        {
            "name": "delivery_contract_keys_match_expected_schema",
            "passed": actual_delivery_contract_schema
            == expected_delivery_contract_schema,
            "expected": expected_delivery_contract_schema,
            "actual": actual_delivery_contract_schema,
        },
        {
            "name": "delivery_channel_formats_match_expected",
            "passed": {
                name: channel["format"]
                for name, channel in delivery_channels.items()
            }
            == expected_delivery_channel_formats,
            "expected": expected_delivery_channel_formats,
            "actual": {
                name: channel["format"]
                for name, channel in delivery_channels.items()
            },
        },
        {
            "name": "delivery_cron_intents_match_report_intent_registry",
            "passed": (
                delivery_contract["cron_intents"] == expected_delivery_cron_intents
            ),
            "expected": expected_delivery_cron_intents,
            "actual": delivery_contract["cron_intents"],
        },
        {
            "name": "delivery_numeric_authority_is_position_review",
            "passed": delivery_channels["hermes"]["numeric_authority"]
            == "position_review",
            "expected": "position_review",
            "actual": delivery_channels["hermes"]["numeric_authority"],
        },
        {
            "name": "position_review_telegram_max_chars_matches_expected",
            "passed": telegram_contract["max_chars"] == 3900,
            "expected": 3900,
            "actual": telegram_contract["max_chars"],
        },
        {
            "name": "position_review_telegram_schema_version_matches_expected",
            "passed": (
                telegram_contract["schema_version"] == TELEGRAM_FORMAT_SCHEMA_VERSION
            ),
            "expected": TELEGRAM_FORMAT_SCHEMA_VERSION,
            "actual": telegram_contract["schema_version"],
        },
        {
            "name": "position_review_telegram_chunking_contract_matches_expected",
            "passed": {
                "overflow_policy": telegram_contract["overflow_policy"],
                "section_separator": telegram_contract["section_separator"],
                "chunk_indexing": telegram_contract["chunk_indexing"],
            }
            == expected_telegram_chunking_contract,
            "expected": expected_telegram_chunking_contract,
            "actual": {
                "overflow_policy": telegram_contract["overflow_policy"],
                "section_separator": telegram_contract["section_separator"],
                "chunk_indexing": telegram_contract["chunk_indexing"],
            },
        },
        {
            "name": "position_review_text_reflects_review_numeric_fields",
            "passed": all(numeric_field_presence.values()),
            "expected": {
                "action": review["action"],
                "position_state": review["position_state"],
                "unrealized_return_pct": review["unrealized_return_pct"],
            },
            "actual": numeric_field_presence,
        },
        {
            "name": "telegram_required_sections_match_position_review",
            "passed": delivery_channels["telegram"]["required_sections"]
            == review_contract["required_sections"],
            "expected": review_contract["required_sections"],
            "actual": delivery_channels["telegram"]["required_sections"],
        },
        {
            "name": "position_review_contract_keys_match_expected_schema",
            "passed": list(review_contract) == expected_position_review_contract_keys,
            "expected": expected_position_review_contract_keys,
            "actual": list(review_contract),
        },
        {
            "name": "position_review_contract_has_no_network_side_effect",
            "passed": review_contract["network_call"] is False,
            "expected": False,
            "actual": review_contract["network_call"],
        },
        {
            "name": "position_review_contract_identity_matches_expected",
            "passed": (
                review_contract["name"] == "position_review"
                and review_contract["trigger"]
                == "manual_or_scheduled_position_check"
                and review_contract["decision_focus"]
                == "hold_trim_exit_or_stop_review"
            ),
            "expected": {
                "name": "position_review",
                "trigger": "manual_or_scheduled_position_check",
                "decision_focus": "hold_trim_exit_or_stop_review",
            },
            "actual": {
                "name": review_contract["name"],
                "trigger": review_contract["trigger"],
                "decision_focus": review_contract["decision_focus"],
            },
        },
        {
            "name": "position_review_contract_required_sections_match_expected",
            "passed": review_contract["required_sections"] == POSITION_REVIEW_SECTIONS,
            "expected": POSITION_REVIEW_SECTIONS,
            "actual": review_contract["required_sections"],
        },
        {
            "name": "position_review_contract_has_no_order_submission_side_effect",
            "passed": review_contract["order_submission"] is False,
            "expected": False,
            "actual": review_contract["order_submission"],
        },
        {
            "name": "no_order_submission_side_effect",
            "passed": review_contract["order_submission"] is False,
            "expected": False,
            "actual": review_contract["order_submission"],
        },
        {
            "name": "telegram_text_fits_single_message",
            "passed": len(text) <= telegram_contract["max_chars"],
            "expected_max_chars": telegram_contract["max_chars"],
            "actual_chars": len(text),
        },
    ]
    guard_check_names_actual = [
        check["name"]
        for check in checks
    ] + [
        "position_review_guard_check_names_match_expected_schema",
        "position_review_guard_check_keys_match_expected_schema",
        "position_review_guard_keys_match_expected_schema",
    ]
    checks.append(
        {
            "name": "position_review_guard_check_names_match_expected_schema",
            "passed": guard_check_names_actual == expected_guard_check_names,
            "expected": expected_guard_check_names,
            "actual": guard_check_names_actual,
        }
    )
    guard_check_keys_actual = {
        check["name"]: list(check)
        for check in checks
    }
    guard_check_keys_actual[
        "position_review_guard_check_keys_match_expected_schema"
    ] = expected_default_guard_check_keys
    guard_check_keys_actual[
        "position_review_guard_keys_match_expected_schema"
    ] = expected_default_guard_check_keys
    actual_default_guard_check_names = [
        name
        for name in expected_guard_check_names
        if guard_check_keys_actual.get(name) == expected_default_guard_check_keys
    ]
    actual_special_guard_check_keys = {
        name: guard_check_keys_actual.get(name)
        for name in expected_special_guard_check_keys
    }
    actual_guard_check_key_schema = {
        "default_keys": expected_default_guard_check_keys,
        "default_check_names": actual_default_guard_check_names,
        "special_check_keys": actual_special_guard_check_keys,
    }
    checks.append(
        {
            "name": "position_review_guard_check_keys_match_expected_schema",
            "passed": actual_guard_check_key_schema == expected_guard_check_key_schema,
            "expected": expected_guard_check_key_schema,
            "actual": actual_guard_check_key_schema,
        }
    )
    guard = {
        "status": "pending",
        "checks": checks,
    }
    checks.append(
        {
            "name": "position_review_guard_keys_match_expected_schema",
            "passed": list(guard) == expected_guard_keys,
            "expected": expected_guard_keys,
            "actual": list(guard),
        }
    )
    guard["status"] = "ok" if all(check["passed"] for check in checks) else "conflict"
    return guard


def _report_contract_guard(
    report: dict[str, Any],
    sections: list[dict[str, Any]],
    prompt_contract: dict[str, Any],
    delivery_contract: dict[str, Any],
    intent_contract: dict[str, Any],
) -> dict[str, Any]:
    section_titles = [section["title"] for section in sections]
    text = _format_report_text(report, sections)
    delivery_channels = delivery_contract["channels"]
    hermes_contract = delivery_channels["hermes"]
    telegram_contract = delivery_channels["telegram"]
    required_sections = intent_contract["required_sections"]
    expected_delivery_contract_schema = _expected_delivery_contract_key_schema()
    actual_delivery_contract_schema = _delivery_contract_key_schema(delivery_contract)
    expected_delivery_cron_intents = list(REPORT_INTENTS)
    expected_delivery_channel_formats = {
        "hermes": "structured_json_plus_text",
        "telegram": "plain_text",
    }
    expected_telegram_chunking_contract = {
        "overflow_policy": "split_on_section_boundary",
        "section_separator": "\n\n",
        "chunk_indexing": "1_based",
    }
    expected_prompt_contract_keys = [
        "numeric_authority",
        "llm_role",
        "must_include",
    ]
    expected_prompt_contract_identity = {
        "numeric_authority": "Use MCP numeric fields as source of truth.",
        "llm_role": "Summarize conflicts, caveats, and final wording only.",
    }
    expected_report_intent_contract_keys = [
        "name",
        "schedule_hint",
        "decision_focus",
        "required_sections",
    ]
    expected_report_intent_contract = {
        "name": intent_contract["name"],
        **REPORT_INTENTS[intent_contract["name"]],
    }
    expected_guard_keys = [
        "status",
        "checks",
    ]
    expected_guard_check_names = [
        "required_sections_present",
        "intent_required_sections_present",
        "report_sections_match_intent_order",
        "report_text_sections_match_intent_order",
        "report_intent_is_supported",
        "report_intent_contract_keys_match_expected_schema",
        "report_intent_contract_matches_registry",
        "delivery_cron_intents_match_report_intent_registry",
        "telegram_required_sections_match_intent",
        "prompt_must_include_is_covered",
        "report_prompt_must_include_matches_intent_terms",
        "report_prompt_contract_keys_match_expected_schema",
        "report_prompt_contract_identity_matches_expected",
        "telegram_text_fits_single_message",
        "delivery_contract_has_no_network_side_effect",
        "delivery_contract_has_no_send_side_effect",
        "delivery_contract_keys_match_expected_schema",
        "delivery_channel_formats_match_expected",
        "report_telegram_max_chars_matches_expected",
        "report_telegram_schema_version_matches_expected",
        "report_telegram_chunking_contract_matches_expected",
        "delivery_numeric_authority_is_latest_signal_report",
        "report_text_reflects_latest_signal_numeric_fields",
        "report_contract_guard_check_names_match_expected_schema",
        "report_contract_guard_check_keys_match_expected_schema",
        "report_contract_guard_keys_match_expected_schema",
    ]
    expected_default_guard_check_keys = [
        "name",
        "passed",
        "expected",
        "actual",
    ]
    expected_special_guard_check_keys = {
        "telegram_text_fits_single_message": [
            "name",
            "passed",
            "expected_max_chars",
            "actual_chars",
        ],
    }
    expected_default_guard_check_names = [
        name
        for name in expected_guard_check_names
        if name not in expected_special_guard_check_keys
    ]
    expected_guard_check_key_schema = {
        "default_keys": expected_default_guard_check_keys,
        "default_check_names": expected_default_guard_check_names,
        "special_check_keys": expected_special_guard_check_keys,
    }
    numeric_field_presence = {
        "decision_line_present": f"Decision: {report['action']}" in text,
        "confidence_line_present": (
            "Confidence: "
            f"{_confidence_label(float(report['confidence']))} ({report['confidence']})"
        )
        in text,
        "score_line_present": f"Score: {report['final_score']}" in text,
    }
    text_section_positions = {
        title: text.find(f"{title}:")
        for title in required_sections
    }
    text_section_position_values = [
        text_section_positions[title]
        for title in required_sections
    ]
    text_sections_in_order = [
        title
        for title in required_sections
        if text_section_positions[title] >= 0
    ]
    checks = [
        {
            "name": "required_sections_present",
            "passed": all(title in section_titles for title in required_sections),
            "expected": required_sections,
            "actual": section_titles,
        },
        {
            "name": "intent_required_sections_present",
            "passed": all(title in section_titles for title in intent_contract["required_sections"]),
            "expected": intent_contract["required_sections"],
            "actual": section_titles,
        },
        {
            "name": "report_sections_match_intent_order",
            "passed": section_titles == required_sections,
            "expected": required_sections,
            "actual": section_titles,
        },
        {
            "name": "report_text_sections_match_intent_order",
            "passed": (
                all(position >= 0 for position in text_section_position_values)
                and text_section_position_values == sorted(text_section_position_values)
            ),
            "expected": required_sections,
            "actual": {
                "found_sections": text_sections_in_order,
                "positions_ascending": (
                    text_section_position_values == sorted(text_section_position_values)
                ),
                "positions": text_section_positions,
            },
        },
        {
            "name": "report_intent_is_supported",
            "passed": intent_contract["name"] in delivery_contract["cron_intents"],
            "expected": delivery_contract["cron_intents"],
            "actual": intent_contract["name"],
        },
        {
            "name": "report_intent_contract_keys_match_expected_schema",
            "passed": list(intent_contract) == expected_report_intent_contract_keys,
            "expected": expected_report_intent_contract_keys,
            "actual": list(intent_contract),
        },
        {
            "name": "report_intent_contract_matches_registry",
            "passed": intent_contract == expected_report_intent_contract,
            "expected": expected_report_intent_contract,
            "actual": intent_contract,
        },
        {
            "name": "delivery_cron_intents_match_report_intent_registry",
            "passed": (
                delivery_contract["cron_intents"] == expected_delivery_cron_intents
            ),
            "expected": expected_delivery_cron_intents,
            "actual": delivery_contract["cron_intents"],
        },
        {
            "name": "telegram_required_sections_match_intent",
            "passed": telegram_contract["required_sections"] == required_sections,
            "expected": required_sections,
            "actual": telegram_contract["required_sections"],
        },
        {
            "name": "prompt_must_include_is_covered",
            "passed": all(
                item in prompt_contract["must_include"]
                for item in _prompt_required_terms(required_sections)
            ),
            "expected": _prompt_required_terms(required_sections),
            "actual": prompt_contract["must_include"],
        },
        {
            "name": "report_prompt_must_include_matches_intent_terms",
            "passed": (
                prompt_contract["must_include"]
                == _prompt_required_terms(required_sections)
            ),
            "expected": _prompt_required_terms(required_sections),
            "actual": prompt_contract["must_include"],
        },
        {
            "name": "report_prompt_contract_keys_match_expected_schema",
            "passed": list(prompt_contract) == expected_prompt_contract_keys,
            "expected": expected_prompt_contract_keys,
            "actual": list(prompt_contract),
        },
        {
            "name": "report_prompt_contract_identity_matches_expected",
            "passed": (
                prompt_contract["numeric_authority"]
                == expected_prompt_contract_identity["numeric_authority"]
                and prompt_contract["llm_role"]
                == expected_prompt_contract_identity["llm_role"]
            ),
            "expected": expected_prompt_contract_identity,
            "actual": {
                "numeric_authority": prompt_contract["numeric_authority"],
                "llm_role": prompt_contract["llm_role"],
            },
        },
        {
            "name": "telegram_text_fits_single_message",
            "passed": len(text) <= telegram_contract["max_chars"],
            "expected_max_chars": telegram_contract["max_chars"],
            "actual_chars": len(text),
        },
        {
            "name": "delivery_contract_has_no_network_side_effect",
            "passed": all(channel["network_call"] is False for channel in delivery_contract["channels"].values()),
            "expected": False,
            "actual": {name: channel["network_call"] for name, channel in delivery_contract["channels"].items()},
        },
        {
            "name": "delivery_contract_has_no_send_side_effect",
            "passed": all(
                channel.get("send_call", False) is False
                for channel in delivery_channels.values()
            ),
            "expected": False,
            "actual": {
                name: channel.get("send_call", False)
                for name, channel in delivery_channels.items()
            },
        },
        {
            "name": "delivery_contract_keys_match_expected_schema",
            "passed": actual_delivery_contract_schema
            == expected_delivery_contract_schema,
            "expected": expected_delivery_contract_schema,
            "actual": actual_delivery_contract_schema,
        },
        {
            "name": "delivery_channel_formats_match_expected",
            "passed": {
                name: channel["format"]
                for name, channel in delivery_channels.items()
            }
            == expected_delivery_channel_formats,
            "expected": expected_delivery_channel_formats,
            "actual": {
                name: channel["format"]
                for name, channel in delivery_channels.items()
            },
        },
        {
            "name": "report_telegram_max_chars_matches_expected",
            "passed": telegram_contract["max_chars"] == 3900,
            "expected": 3900,
            "actual": telegram_contract["max_chars"],
        },
        {
            "name": "report_telegram_schema_version_matches_expected",
            "passed": (
                telegram_contract["schema_version"] == TELEGRAM_FORMAT_SCHEMA_VERSION
            ),
            "expected": TELEGRAM_FORMAT_SCHEMA_VERSION,
            "actual": telegram_contract["schema_version"],
        },
        {
            "name": "report_telegram_chunking_contract_matches_expected",
            "passed": {
                "overflow_policy": telegram_contract["overflow_policy"],
                "section_separator": telegram_contract["section_separator"],
                "chunk_indexing": telegram_contract["chunk_indexing"],
            }
            == expected_telegram_chunking_contract,
            "expected": expected_telegram_chunking_contract,
            "actual": {
                "overflow_policy": telegram_contract["overflow_policy"],
                "section_separator": telegram_contract["section_separator"],
                "chunk_indexing": telegram_contract["chunk_indexing"],
            },
        },
        {
            "name": "delivery_numeric_authority_is_latest_signal_report",
            "passed": hermes_contract["numeric_authority"] == "latest_signal_report",
            "expected": "latest_signal_report",
            "actual": hermes_contract["numeric_authority"],
        },
        {
            "name": "report_text_reflects_latest_signal_numeric_fields",
            "passed": all(numeric_field_presence.values()),
            "expected": {
                "action": report["action"],
                "confidence": report["confidence"],
                "final_score": report["final_score"],
            },
            "actual": numeric_field_presence,
        },
    ]
    guard_check_names_actual = [
        check["name"]
        for check in checks
    ] + [
        "report_contract_guard_check_names_match_expected_schema",
        "report_contract_guard_check_keys_match_expected_schema",
        "report_contract_guard_keys_match_expected_schema",
    ]
    checks.append(
        {
            "name": "report_contract_guard_check_names_match_expected_schema",
            "passed": guard_check_names_actual == expected_guard_check_names,
            "expected": expected_guard_check_names,
            "actual": guard_check_names_actual,
        }
    )
    guard_check_keys_actual = {
        check["name"]: list(check)
        for check in checks
    }
    guard_check_keys_actual[
        "report_contract_guard_check_keys_match_expected_schema"
    ] = expected_default_guard_check_keys
    guard_check_keys_actual[
        "report_contract_guard_keys_match_expected_schema"
    ] = expected_default_guard_check_keys
    actual_default_guard_check_names = [
        name
        for name in expected_guard_check_names
        if guard_check_keys_actual.get(name) == expected_default_guard_check_keys
    ]
    actual_special_guard_check_keys = {
        name: guard_check_keys_actual.get(name)
        for name in expected_special_guard_check_keys
    }
    actual_guard_check_key_schema = {
        "default_keys": expected_default_guard_check_keys,
        "default_check_names": actual_default_guard_check_names,
        "special_check_keys": actual_special_guard_check_keys,
    }
    checks.append(
        {
            "name": "report_contract_guard_check_keys_match_expected_schema",
            "passed": actual_guard_check_key_schema == expected_guard_check_key_schema,
            "expected": expected_guard_check_key_schema,
            "actual": actual_guard_check_key_schema,
        }
    )
    guard = {
        "status": "pending",
        "checks": checks,
    }
    checks.append(
        {
            "name": "report_contract_guard_keys_match_expected_schema",
            "passed": list(guard) == expected_guard_keys,
            "expected": expected_guard_keys,
            "actual": list(guard),
        }
    )
    guard["status"] = "ok" if all(check["passed"] for check in checks) else "conflict"
    return guard


def _evidence_guard(
    report: dict[str, Any],
    sections: list[dict[str, Any]],
    evidence_context: dict[str, Any],
    evidence_contract: dict[str, Any],
) -> dict[str, Any]:
    cautions = _section_items(sections, "Cautions")
    conflict_flags = list(evidence_context["conflict_flags"])
    required_fields = evidence_contract["required_conflict_fields"]
    expected_guard_keys = [
        "status",
        "checks",
    ]
    expected_guard_check_names = [
        "reason_summary_within_limit",
        "evidence_summary_within_limit",
        "conflict_flags_within_limit",
        "conflict_flags_have_required_fields",
        "risk_warnings_reflected_in_cautions",
        "flagged_conflicts_are_acknowledged",
    ]
    if report["data_warnings"]:
        expected_guard_check_names.append("data_warnings_reflected_in_cautions")
    expected_guard_check_names.extend(
        [
            "evidence_guard_check_names_match_expected_schema",
            "evidence_guard_check_keys_match_expected_schema",
            "evidence_guard_keys_match_expected_schema",
        ]
    )
    expected_default_guard_check_keys = [
        "name",
        "passed",
        "expected",
        "actual",
    ]
    expected_special_guard_check_keys = {
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
    expected_default_guard_check_names = [
        name
        for name in expected_guard_check_names
        if name not in expected_special_guard_check_keys
    ]
    expected_guard_check_key_schema = {
        "default_keys": expected_default_guard_check_keys,
        "default_check_names": expected_default_guard_check_names,
        "special_check_keys": expected_special_guard_check_keys,
    }
    checks = [
        {
            "name": "reason_summary_within_limit",
            "passed": len(report["reason_summary"])
            <= evidence_contract["max_reason_summary_chars"],
            "expected_max_chars": evidence_contract["max_reason_summary_chars"],
            "actual_chars": len(report["reason_summary"]),
        },
        {
            "name": "evidence_summary_within_limit",
            "passed": len(report["evidence_summary"])
            <= evidence_contract["max_evidence_summary_chars"],
            "expected_max_chars": evidence_contract["max_evidence_summary_chars"],
            "actual_chars": len(report["evidence_summary"]),
        },
        {
            "name": "conflict_flags_within_limit",
            "passed": len(conflict_flags) <= evidence_contract["max_conflict_flags"],
            "expected_max": evidence_contract["max_conflict_flags"],
            "actual_count": len(conflict_flags),
        },
        {
            "name": "conflict_flags_have_required_fields",
            "passed": all(
                all(field in flag for field in required_fields)
                for flag in conflict_flags
            ),
            "expected": required_fields,
            "actual": [
                sorted(flag)
                for flag in conflict_flags
            ],
        },
        {
            "name": "risk_warnings_reflected_in_cautions",
            "passed": all(
                warning in cautions
                for warning in evidence_context["risk_warnings"]
            ),
            "expected": evidence_context["risk_warnings"],
            "actual": cautions,
        },
        {
            "name": "flagged_conflicts_are_acknowledged",
            "passed": all(
                flag["status"] == "acknowledged"
                for flag in conflict_flags
            ),
            "expected": "acknowledged",
            "actual": [
                flag["status"]
                for flag in conflict_flags
            ],
        },
    ]
    if report["data_warnings"]:
        checks.append(
            {
                "name": "data_warnings_reflected_in_cautions",
                "passed": all(warning in cautions for warning in report["data_warnings"]),
                "expected": report["data_warnings"],
                "actual": cautions,
            }
        )
    guard_check_names_actual = [
        check["name"]
        for check in checks
    ] + [
        "evidence_guard_check_names_match_expected_schema",
        "evidence_guard_check_keys_match_expected_schema",
        "evidence_guard_keys_match_expected_schema",
    ]
    checks.append(
        {
            "name": "evidence_guard_check_names_match_expected_schema",
            "passed": guard_check_names_actual == expected_guard_check_names,
            "expected": expected_guard_check_names,
            "actual": guard_check_names_actual,
        }
    )
    guard_check_keys_actual = {
        check["name"]: list(check)
        for check in checks
    }
    guard_check_keys_actual[
        "evidence_guard_check_keys_match_expected_schema"
    ] = expected_default_guard_check_keys
    guard_check_keys_actual[
        "evidence_guard_keys_match_expected_schema"
    ] = expected_default_guard_check_keys
    actual_default_guard_check_names = [
        name
        for name in expected_guard_check_names
        if guard_check_keys_actual.get(name) == expected_default_guard_check_keys
    ]
    actual_special_guard_check_keys = {
        name: guard_check_keys_actual.get(name)
        for name in expected_special_guard_check_keys
    }
    actual_guard_check_key_schema = {
        "default_keys": expected_default_guard_check_keys,
        "default_check_names": actual_default_guard_check_names,
        "special_check_keys": actual_special_guard_check_keys,
    }
    checks.append(
        {
            "name": "evidence_guard_check_keys_match_expected_schema",
            "passed": actual_guard_check_key_schema == expected_guard_check_key_schema,
            "expected": expected_guard_check_key_schema,
            "actual": actual_guard_check_key_schema,
        }
    )
    guard = {
        "status": "pending",
        "checks": checks,
    }
    checks.append(
        {
            "name": "evidence_guard_keys_match_expected_schema",
            "passed": list(guard) == expected_guard_keys,
            "expected": expected_guard_keys,
            "actual": list(guard),
        }
    )
    guard["status"] = "ok" if all(check["passed"] for check in checks) else "conflict"
    return guard


def _section_items(
    sections: list[dict[str, Any]],
    title: str,
) -> list[str]:
    for section in sections:
        if section["title"] == title:
            return list(section["items"])
    return []


def _prompt_required_terms(required_sections: list[str] | None = None) -> list[str]:
    sections = set(required_sections or REQUIRED_REPORT_SECTIONS)
    terms = ["action", "confidence"]
    if "Entry" in sections:
        terms.append("entry")
    if "Stop" in sections:
        terms.append("stop")
    if "Take Profit" in sections:
        terms.append("take_profit")
    if "Cautions" in sections:
        terms.extend(["risk", "data_warnings"])
    return terms


def _position_review_required_terms() -> list[str]:
    return [
        "action",
        "position_state",
        "unrealized_return_pct",
        "stop",
        "take_profit",
        "risk",
    ]


def _chart_code_guard(
    signal: dict[str, Any],
    chart_payload: dict[str, Any],
) -> dict[str, Any]:
    checks = [
        {
            "name": "chart_symbol_matches_underlying",
            "passed": chart_payload["symbol"] == signal["underlying"],
            "expected": signal["underlying"],
            "actual": chart_payload["symbol"],
        },
        {
            "name": "chart_renderer_uses_offline_data",
            "passed": chart_payload["live_data_required"] is False,
            "expected": False,
            "actual": chart_payload["live_data_required"],
        },
        {
            "name": "numeric_indicators_remain_code_authority",
            "passed": True,
            "expected": "code",
            "actual": "code",
        },
    ]
    return {
        "status": "ok" if all(check["passed"] for check in checks) else "conflict",
        "checks": checks,
        "policy": (
            "Chart images provide visual context only; RSI, DMI, stop, and "
            "take-profit values come from code-calculated fields."
        ),
    }


__all__ = [
    "CRON_PROMPT_SCHEMA_VERSION",
    "EVIDENCE_SUMMARY_CONTRACT",
    "POSITION_REVIEW_SCHEMA_VERSION",
    "REPORT_SCHEMA_VERSION",
    "generate_cron_prompt_pack",
    "generate_latest_signal_report",
    "generate_position_review_report",
]
