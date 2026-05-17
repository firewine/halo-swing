# ruff: noqa: F403,F405,F821
"""Summary-only API-key pipeline payload assembly."""

from __future__ import annotations

from .context import *
from .summary_only_integration_status_fields import (
    _api_key_integration_status_top_level_fields,
)
from .summary_only_live_http_timeout_fields import (
    _api_key_live_http_timeout_top_level_fields,
)
from .summary_only_pipeline_route_fields import (
    _api_key_pipeline_route_top_level_fields,
)
from .summary_only_pipeline_check_fields import (
    _api_key_pipeline_check_top_level_fields,
)
from .api_key_pipeline_payload_mirrors import (
    _api_key_failure_top_level_fields,
    _api_key_provider_recovery_top_level_fields,
)
from .provider_recovery_checklist_summary import (
    _api_key_provider_recovery_checklist_summary,
)
from .summary_only_provider_route_fields import (
    _api_key_provider_recovery_checklist_route_top_level_fields,
    _api_key_requirement_route_top_level_fields,
)
from .summary_only_provider_route_summary_fields import (
    _api_key_provider_route_summary_top_level_fields,
)
from .summary_only_provider_selection_fields import (
    _api_key_provider_selection_top_level_fields,
)
from .summary_only_provider_smoke_fields import (
    _api_key_provider_smoke_success_top_level_fields,
    _api_key_provider_smoke_top_level_fields,
)
from .summary_only_quickstart_fields import (
    _api_key_setup_quickstart_top_level_fields,
)
from .summary_only_setup_file_fields import (
    _api_key_setup_file_top_level_fields,
)
from .summary_only_command_fields import (
    _api_key_command_top_level_fields,
)


__all__ = ('_api_key_pipeline_summary_only_payload',)


def _api_key_pipeline_summary_only_payload(
    payload: dict[str, Any],
) -> dict[str, Any]:
    _summary_context = _api_key_pipeline_summary_only_context(payload)
    input_payload = _summary_context['input_payload']
    next_operator_action = _summary_context['next_operator_action']
    next_provider_smoke = _summary_context['next_provider_smoke']
    next_provider_recovery_action = _summary_context['next_provider_recovery_action']
    api_key_next_action_summary = _summary_context['api_key_next_action_summary']
    api_key_integration_status_summary = _summary_context['api_key_integration_status_summary']
    provider_smoke_rows = _summary_context['provider_smoke_rows']
    provider_smoke_summary_count = _summary_context['provider_smoke_summary_count']
    provider_smoke_success_rows = _summary_context['provider_smoke_success_rows']
    provider_smoke_success_count = _summary_context['provider_smoke_success_count']
    provider_smoke_success_expected_live_checks = _summary_context['provider_smoke_success_expected_live_checks']
    provider_smoke_success_network_call_count = _summary_context['provider_smoke_success_network_call_count']
    provider_smoke_success_mutates_local_state_count = _summary_context['provider_smoke_success_mutates_local_state_count']
    provider_smoke_success_secret_values_returned_count = _summary_context['provider_smoke_success_secret_values_returned_count']
    provider_smoke_success_accepted_env_key_groups = _summary_context['provider_smoke_success_accepted_env_key_groups']
    api_key_operator_checklist_summary = _summary_context['api_key_operator_checklist_summary']
    setup_quickstart_rows = _summary_context['setup_quickstart_rows']
    setup_status_summary = _summary_context['setup_status_summary']
    api_key_setup_file_summary = _summary_context['api_key_setup_file_summary']
    api_key_provider_selection_summary = _summary_context['api_key_provider_selection_summary']
    api_key_requirements_summary = _summary_context['api_key_requirements_summary']
    provider_requirement_families = _summary_context['provider_requirement_families']
    provider_requirement_rows = _summary_context['provider_requirement_rows']
    api_key_command_summary = _summary_context['api_key_command_summary']
    copy_dotenv_command = _summary_context['copy_dotenv_command']
    next_smoke_command = _summary_context['next_smoke_command']
    one_shot_pipeline_smoke = _summary_context['one_shot_pipeline_smoke']
    provider_smoke_command_rows = _summary_context['provider_smoke_command_rows']
    provider_smoke_command_count = _summary_context['provider_smoke_command_count']
    provider_smoke_command_rows_by_family = _summary_context['provider_smoke_command_rows_by_family']
    quickstart_command_plan = _summary_context['quickstart_command_plan']
    next_quickstart_command_plan_item = _summary_context['next_quickstart_command_plan_item']
    next_quickstart_command_plan_row = _summary_context['next_quickstart_command_plan_row']
    readiness_summary = _optional_mapping(payload.get("readiness_summary")) or {}
    api_key_pipeline_stage_summary = _optional_mapping(
        payload.get("api_key_pipeline_stage_summary")
    ) or {}
    api_key_pipeline_check_summary = _optional_mapping(
        payload.get("api_key_pipeline_check_summary")
    ) or {}
    api_key_pipeline_failure_summary = _optional_mapping(
        payload.get("api_key_pipeline_failure_summary")
    ) or {}
    provider_route_summary = (
        _optional_mapping(payload.get("provider_route_summary")) or {}
    )
    api_key_dotenv_loading_summary = (
        _optional_mapping(payload.get("api_key_dotenv_loading_summary")) or {}
    )
    api_key_live_http_timeout_summary = (
        _optional_mapping(payload.get("api_key_live_http_timeout_summary")) or {}
    )
    api_key_provider_recovery_checklist = _optional_mapping(
        payload.get("api_key_provider_recovery_checklist")
    ) or {}
    api_key_provider_recovery_checklist_summary = (
        _api_key_provider_recovery_checklist_summary(
            api_key_provider_recovery_checklist
        )
    )
    api_key_provider_recovery_summary = _api_key_provider_recovery_summary(
        api_key_provider_recovery_checklist,
        route_family_summary=setup_status_summary,
    )
    return {
        "schema_version": "api_key_pipeline_smoke_summary_only.v1",
        "status": payload.get("status"),
        "summary_only": True,
        "input": {
            "asset": input_payload.get("asset"),
            "timeframe": input_payload.get("timeframe"),
            "symbols": input_payload.get("symbols"),
            "topic": input_payload.get("topic"),
            "summary_only": True,
        },
        "executed_tools": _string_list(payload.get("executed_tools")),
        "next_operator_action_name": (
            next_operator_action.get("name")
            or api_key_next_action_summary.get("next_action_name")
        ),
        "next_operator_action_status": (
            next_operator_action.get("status")
            or api_key_next_action_summary.get("next_action_status")
        ),
        "next_operator_action_command": api_key_next_action_summary.get(
            "next_action_command"
        ),
        "next_operator_action_next_after_action": next_operator_action.get(
            "next_after_action"
        ),
        "next_operator_action_dotenv_target_path": next_operator_action.get(
            "dotenv_target_path"
        ),
        "next_operator_action_source_path": next_operator_action.get("source_path"),
        "next_operator_action_target_path": next_operator_action.get("target_path"),
        "next_operator_action_provider_family": (
            next_operator_action.get("provider_family")
            or next_provider_recovery_action.get("provider_family")
            or next_provider_smoke.get("provider_family")
        ),
        "next_operator_action_provider": (
            next_operator_action.get("provider")
            or next_provider_recovery_action.get("provider")
            or next_provider_smoke.get("provider")
        ),
        "next_operator_action_selected_provider_class": (
            api_key_next_action_summary.get("next_action_selected_provider_class")
        ),
        "next_operator_action_provider_route_data_mode": (
            api_key_next_action_summary.get("next_action_provider_route_data_mode")
        ),
        "next_operator_action_provider_route_live_data_required": (
            api_key_next_action_summary.get(
                "next_action_provider_route_live_data_required"
            )
            is True
        ),
        "next_operator_action_smoke_command_name": (
            next_operator_action.get("smoke_command_name")
            or next_operator_action.get("next_provider_smoke_command_name")
            or next_operator_action.get("next_provider_recovery_smoke_command_name")
            or next_provider_recovery_action.get("smoke_command_name")
            or next_provider_smoke.get("smoke_command_name")
        ),
        "next_operator_action_expected_live_contract": (
            api_key_next_action_summary.get("next_action_expected_live_contract")
        ),
        "next_operator_action_expected_live_checks": _string_list(
            api_key_next_action_summary.get("next_action_expected_live_checks")
        ),
        "next_operator_action_network_call": (
            api_key_next_action_summary.get("next_action_network_call") is True
        ),
        "next_operator_action_network_call_policy": next_operator_action.get(
            "network_call_policy"
        ),
        "next_operator_action_mutates_local_state": (
            api_key_next_action_summary.get("next_action_mutates_local_state")
            is True
        ),
        "next_operator_action_secret_input_required": (
            next_operator_action.get("secret_input_required") is True
        ),
        "next_operator_action_preferred_env_key": api_key_next_action_summary.get(
            "preferred_env_key"
        ),
        "next_operator_action_accepted_env_keys": _string_list(
            api_key_next_action_summary.get("accepted_env_keys")
        ),
        "next_operator_action_required_env_keys": _string_list(
            api_key_next_action_summary.get("required_env_keys")
        ),
        "next_operator_action_dotenv_examples": _string_list(
            api_key_next_action_summary.get("dotenv_examples")
        ),
        "next_operator_action_dotenv_example_count": (
            api_key_next_action_summary.get("dotenv_example_count")
        ),
        "next_operator_action_secret_values_returned": (
            next_operator_action.get("secret_values_returned") is True
            or api_key_next_action_summary.get("secret_values_returned") is True
        ),
        "api_key_next_action_selected_provider_class_by_family": (
            _optional_mapping(
                api_key_next_action_summary.get(
                    "selected_provider_class_by_family"
                )
            )
            or {}
        ),
        "api_key_next_action_provider_route_data_mode_by_family": (
            _optional_mapping(
                api_key_next_action_summary.get(
                    "provider_route_data_mode_by_family"
                )
            )
            or {}
        ),
        "api_key_next_action_provider_route_live_data_required_by_family": (
            _optional_mapping(
                api_key_next_action_summary.get(
                    "provider_route_live_data_required_by_family"
                )
            )
            or {}
        ),
        "api_key_next_action_all_selected_routes_live": (
            api_key_next_action_summary.get("all_selected_routes_live") is True
        ),
        "api_key_setup_current_step": api_key_operator_checklist_summary.get(
            "current_step"
        ),
        "api_key_setup_ready": api_key_operator_checklist_summary.get("ready") is True,
        "api_key_setup_step_count": api_key_operator_checklist_summary.get(
            "step_count"
        ),
        "api_key_setup_ready_step_names": _string_list(
            api_key_operator_checklist_summary.get("ready_step_names")
        ),
        "api_key_setup_ready_step_count": api_key_operator_checklist_summary.get(
            "ready_step_count"
        ),
        "api_key_setup_blocking_step_names": _string_list(
            api_key_operator_checklist_summary.get("blocking_step_names")
        ),
        "api_key_setup_blocking_step_count": api_key_operator_checklist_summary.get(
            "blocking_step_count"
        ),
        "api_key_setup_next_blocking_step": api_key_operator_checklist_summary.get(
            "next_blocking_step"
        ),
        "api_key_operator_checklist_selected_provider_class_by_family": (
            _optional_mapping(
                api_key_operator_checklist_summary.get(
                    "selected_provider_class_by_family"
                )
            )
            or {}
        ),
        "api_key_operator_checklist_provider_route_data_mode_by_family": (
            _optional_mapping(
                api_key_operator_checklist_summary.get(
                    "provider_route_data_mode_by_family"
                )
            )
            or {}
        ),
        "api_key_operator_checklist_provider_route_live_data_required_by_family": (
            _optional_mapping(
                api_key_operator_checklist_summary.get(
                    "provider_route_live_data_required_by_family"
                )
            )
            or {}
        ),
        "api_key_operator_checklist_all_selected_routes_live": (
            api_key_operator_checklist_summary.get("all_selected_routes_live")
            is True
        ),
        **_api_key_setup_quickstart_top_level_fields(
            setup_quickstart_rows=setup_quickstart_rows,
            api_key_operator_checklist_summary=(
                api_key_operator_checklist_summary
            ),
            quickstart_command_plan=quickstart_command_plan,
            next_quickstart_command_plan_item=(
                next_quickstart_command_plan_item
            ),
            next_quickstart_command_plan_row=next_quickstart_command_plan_row,
        ),
        **_api_key_setup_file_top_level_fields(api_key_setup_file_summary),
        "api_key_dotenv_supported": (
            api_key_dotenv_loading_summary.get("dotenv_supported") is True
        ),
        "api_key_dotenv_loading_enabled": (
            api_key_dotenv_loading_summary.get("dotenv_loading_enabled") is True
        ),
        "api_key_dotenv_disabled": (
            api_key_dotenv_loading_summary.get("disabled") is True
        ),
        "api_key_dotenv_disabled_env_key": api_key_dotenv_loading_summary.get(
            "disabled_env_key"
        ),
        "api_key_dotenv_configuration_precedence": _string_list(
            api_key_dotenv_loading_summary.get("configuration_precedence")
        ),
        "api_key_dotenv_source_path": api_key_dotenv_loading_summary.get(
            "source_path"
        ),
        "api_key_dotenv_target_path": api_key_dotenv_loading_summary.get(
            "target_path"
        ),
        "api_key_dotenv_source_exists": (
            api_key_dotenv_loading_summary.get("source_exists") is True
        ),
        "api_key_dotenv_target_exists": (
            api_key_dotenv_loading_summary.get("target_exists") is True
        ),
        "api_key_dotenv_copy_required": (
            api_key_dotenv_loading_summary.get("copy_required") is True
        ),
        "api_key_dotenv_next_setup_step": api_key_dotenv_loading_summary.get(
            "next_setup_step"
        ),
        "api_key_dotenv_ready_to_run_live_smoke": (
            api_key_dotenv_loading_summary.get("ready_to_run_live_smoke") is True
        ),
        "api_key_dotenv_network_call": (
            api_key_dotenv_loading_summary.get("network_call") is True
        ),
        "api_key_dotenv_mutates_local_state": (
            api_key_dotenv_loading_summary.get("mutates_local_state") is True
        ),
        "api_key_dotenv_secret_values_returned": (
            api_key_dotenv_loading_summary.get("secret_values_returned") is True
        ),
        **_api_key_live_http_timeout_top_level_fields(
            api_key_live_http_timeout_summary
        ),
        **_api_key_provider_selection_top_level_fields(
            api_key_provider_selection_summary
        ),
        **_api_key_integration_status_top_level_fields(
            api_key_integration_status_summary=api_key_integration_status_summary,
            api_key_next_action_summary=api_key_next_action_summary,
            next_operator_action=next_operator_action,
            next_provider_smoke=next_provider_smoke,
        ),
        "api_key_setup_configured_provider_families": _string_list(
            setup_status_summary.get("configured_provider_families")
        ),
        "api_key_setup_missing_provider_families": _string_list(
            setup_status_summary.get("missing_provider_families")
        ),
        "api_key_setup_configured_provider_family_count": (
            setup_status_summary.get("configured_provider_family_count")
        ),
        "api_key_setup_required_provider_family_count": (
            setup_status_summary.get("required_provider_family_count")
        ),
        "api_key_setup_ready_to_run_live_smoke": (
            setup_status_summary.get("ready_to_run_live_smoke") is True
        ),
        "api_key_setup_provider_route_status": setup_status_summary.get(
            "provider_route_status"
        ),
        "api_key_setup_selected_provider_class_by_family": (
            _optional_mapping(
                setup_status_summary.get("selected_provider_class_by_family")
            )
            or {}
        ),
        "api_key_setup_provider_route_data_mode_by_family": (
            _optional_mapping(
                setup_status_summary.get("provider_route_data_mode_by_family")
            )
            or {}
        ),
        "api_key_setup_provider_route_live_data_required_by_family": (
            _optional_mapping(
                setup_status_summary.get(
                    "provider_route_live_data_required_by_family"
                )
            )
            or {}
        ),
        "api_key_setup_all_selected_routes_live": (
            setup_status_summary.get("all_selected_routes_live") is True
        ),
        "api_key_readiness_selected_provider_class_by_family": (
            _optional_mapping(
                readiness_summary.get("selected_provider_class_by_family")
            )
            or {}
        ),
        "api_key_readiness_provider_route_data_mode_by_family": (
            _optional_mapping(
                readiness_summary.get("provider_route_data_mode_by_family")
            )
            or {}
        ),
        "api_key_readiness_provider_route_live_data_required_by_family": (
            _optional_mapping(
                readiness_summary.get(
                    "provider_route_live_data_required_by_family"
                )
            )
            or {}
        ),
        "api_key_readiness_all_selected_routes_live": (
            readiness_summary.get("all_selected_routes_live") is True
        ),
        "api_key_required_env_keys": _string_list(
            api_key_requirements_summary.get("required_env_keys")
        ),
        "api_key_required_env_key_count": len(
            _string_list(api_key_requirements_summary.get("required_env_keys"))
        ),
        "api_key_configured_env_keys": _string_list(
            api_key_requirements_summary.get("configured_env_keys")
        ),
        "api_key_configured_env_key_count": len(
            _string_list(api_key_requirements_summary.get("configured_env_keys"))
        ),
        "api_key_requirement_configured_provider_families": _string_list(
            api_key_requirements_summary.get("configured_provider_families")
        ),
        "api_key_requirement_missing_provider_families": _string_list(
            api_key_requirements_summary.get("missing_provider_families")
        ),
        "api_key_provider_requirement_families": provider_requirement_families,
        "api_key_provider_requirement_count": len(provider_requirement_families),
        "api_key_provider_requirement_preferred_env_keys": {
            family: row.get("preferred_env_key")
            for family, row in provider_requirement_rows.items()
        },
        "api_key_provider_requirement_accepted_env_keys": {
            family: _string_list(row.get("accepted_env_keys"))
            for family, row in provider_requirement_rows.items()
        },
        "api_key_provider_requirement_setup_statuses": {
            family: row.get("setup_status")
            for family, row in provider_requirement_rows.items()
        },
        "api_key_provider_requirement_configured": {
            family: row.get("configured") is True
            for family, row in provider_requirement_rows.items()
        },
        "api_key_provider_requirement_next_setup_actions": {
            family: row.get("next_setup_action")
            for family, row in provider_requirement_rows.items()
        },
        "api_key_provider_requirement_smoke_command_names": {
            family: row.get("smoke_command_name")
            for family, row in provider_requirement_rows.items()
        },
        **_api_key_requirement_route_top_level_fields(
            api_key_requirements_summary
        ),
        **_api_key_command_top_level_fields(
            copy_dotenv_command=copy_dotenv_command,
            next_smoke_command=next_smoke_command,
            one_shot_pipeline_smoke=one_shot_pipeline_smoke,
        ),
        **_api_key_provider_smoke_top_level_fields(
            setup_status_summary,
            next_provider_smoke,
            provider_smoke_command_rows,
            provider_smoke_command_count,
            provider_smoke_command_rows_by_family,
        ),
        "next_operator_action": next_operator_action,
        "readiness_summary": readiness_summary,
        "api_key_integration_status_summary": api_key_integration_status_summary,
        "api_key_next_action_summary": api_key_next_action_summary,
        "api_key_operator_checklist_summary": api_key_operator_checklist_summary,
        "setup_status_summary": setup_status_summary,
        "live_data_setup_summary": _optional_mapping(
            payload.get("live_data_setup_summary")
        )
        or {},
        "api_key_requirements_summary": api_key_requirements_summary,
        "api_key_command_summary": api_key_command_summary,
        "api_key_setup_file_summary": api_key_setup_file_summary,
        "api_key_dotenv_loading_summary": api_key_dotenv_loading_summary,
        "api_key_pipeline_failure_summary": api_key_pipeline_failure_summary,
        "api_key_pipeline_stage_summary": api_key_pipeline_stage_summary,
        "api_key_pipeline_check_summary": api_key_pipeline_check_summary,
        **_api_key_pipeline_check_top_level_fields(
            api_key_pipeline_check_summary
        ),
        **_api_key_pipeline_route_top_level_fields(
            api_key_pipeline_stage_summary=api_key_pipeline_stage_summary,
            api_key_pipeline_check_summary=api_key_pipeline_check_summary,
        ),
        "api_key_provider_selection_summary": api_key_provider_selection_summary,
        "api_key_live_http_timeout_summary": api_key_live_http_timeout_summary,
        **_api_key_live_http_timeout_top_level_fields(
            api_key_live_http_timeout_summary
        ),
        "api_key_provider_recovery_summary": (
            api_key_provider_recovery_summary
        ),
        "api_key_provider_recovery_checklist_summary": (
            api_key_provider_recovery_checklist_summary
        ),
        "provider_smoke_summaries": provider_smoke_rows,
        "provider_smoke_summary_count": provider_smoke_summary_count,
        **_api_key_provider_smoke_success_top_level_fields(
            provider_smoke_summary_count=provider_smoke_summary_count,
            provider_smoke_success_rows=provider_smoke_success_rows,
            provider_smoke_success_count=provider_smoke_success_count,
            provider_smoke_success_expected_live_checks=(
                provider_smoke_success_expected_live_checks
            ),
            provider_smoke_success_network_call_count=(
                provider_smoke_success_network_call_count
            ),
            provider_smoke_success_mutates_local_state_count=(
                provider_smoke_success_mutates_local_state_count
            ),
            provider_smoke_success_secret_values_returned_count=(
                provider_smoke_success_secret_values_returned_count
            ),
            provider_smoke_success_accepted_env_key_groups=(
                provider_smoke_success_accepted_env_key_groups
            ),
        ),
        **_api_key_failure_top_level_fields(api_key_pipeline_failure_summary),
        "provider_route_summary": provider_route_summary,
        **_api_key_provider_route_summary_top_level_fields(
            provider_route_summary
        ),
        "checks": _api_key_pipeline_summary_only_checks(payload.get("checks")),
        "failed_provider_families": _string_list(
            payload.get("failed_provider_families")
        ),
        "failed_provider_count": payload.get("failed_provider_count"),
        "next_provider_recovery_action": payload.get(
            "next_provider_recovery_action"
        ),
        "next_provider_recovery_smoke_command_name": payload.get(
            "next_provider_recovery_smoke_command_name"
        ),
        "provider_recovery_smoke_count": payload.get(
            "provider_recovery_smoke_count"
        ),
        **_api_key_provider_recovery_top_level_fields(
            api_key_provider_recovery_summary
        ),
        **_api_key_provider_recovery_checklist_route_top_level_fields(
            api_key_provider_recovery_checklist_summary
        ),
        "omitted_sections": [
            "api_key_operator_checklist",
            "api_key_provider_recovery_checklist",
            "live_data_smoke_summary",
            "signal_workflow_smoke_summary",
            "recording_smoke_summary",
            "provider_recovery_smokes",
        ],
        "network_call": payload.get("network_call") is True,
        "live_data_required": payload.get("live_data_required") is True,
        "hermes_runtime_started": False,
        "telegram_send_call": False,
        "send_call": False,
        "order_submission": False,
        "mutates_local_state": False,
        "secret_values_returned": False,
    }
