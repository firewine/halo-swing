from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
DEVOPS_GUIDE = ROOT / "docs" / "devops-setup-guide.md"


def _normalized_text(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").split())


def test_setup_docs_describe_repo_root_dotenv_precedence() -> None:
    text = _normalized_text(README)
    guide = _normalized_text(DEVOPS_GUIDE)

    for document in (text, guide):
        assert "repo-root `.env`" in document or "repo-root .env" in document
        assert "exported environment variables" in document
        assert "launch-directory `.env`" in document or "launch-directory .env" in document
        assert "HALO_SWING_DISABLE_DOTENV=true" in document
        assert "exported or set in `.env`" in document or "exported or placed in `.env`" in document
        assert "other dotenv values are ignored" in document or "ignores other dotenv values" in document


def test_devops_guide_shows_dotenv_key_only_live_data_setup() -> None:
    guide = DEVOPS_GUIDE.read_text(encoding="utf-8")

    assert "POLYGON_API_KEY=your_polygon_key" in guide
    assert "FRED_API_KEY=your_fred_key" in guide
    assert "NEWS_API_KEY=your_newsapi_key" in guide
    assert "HALO_SWING_LIVE_HTTP_TIMEOUT_SECONDS" in guide
    assert "default of `10` seconds" in guide
    assert "live_data_setup_summary" in guide
    assert "dotenv_template" in guide
    assert "dotenv_file_status" in guide
    assert "next setup action" in guide
    assert "next_operator_action" in guide
    assert "live_data_setup_steps" in guide
    assert "preferred_env_key" in guide
    assert "next_setup_action" in guide
    assert "setup_status" in guide
    assert "provider_setup_actions" in guide
    assert "provider_smoke_plan" in guide
    assert (
        "Provider smoke plan rows include `network_call`, `network_call_policy`,"
    ) in guide
    assert "selected_provider_class" in guide
    assert "provider_route_data_mode" in guide
    assert "provider_route_live_data_required" in guide
    assert "--summary-only" in guide
    assert "without editing" in guide
    assert "Returned one-shot command summaries use `--summary-only --no-audit`" in guide
    assert (
        "run_api_key_pipeline_smoke --input-json "
        "'{\"asset\":\"TQQQ\",\"timeframe\":\"swing_3d_10d\""
    ) not in guide
    assert "provider_smoke_count" in guide
    assert "ready_provider_smoke_count" in guide
    assert "blocked_provider_smoke_count" in guide
    assert "next_provider_smoke" in guide
    assert "next_provider_smoke_command_name" in guide
    assert "provider_smoke_summary" in guide
    assert "provider_smoke_summary.v1" in guide
    assert "Direct live provider smoke success payloads" in guide
    assert "provider_smoke_summaries" in guide
    assert "provider_smoke_summary_count" in guide
    assert "live_data_smoke_summary` mirrors those fields" in guide
    assert "provider_error_summaries" in guide
    assert "Direct provider\nsmoke `error_summary` rows include" in guide
    assert "expected_live_contract" in guide
    assert "expected_live_checks" in guide
    assert "provider_error_summary_count" in guide
    assert "failed_provider_families" in guide
    assert "failed_provider_count" in guide
    assert "first_provider_error_summary" in guide
    assert "next_provider_recovery_action" in guide
    assert "next_provider_recovery_smoke" in guide
    assert "next_provider_recovery_smoke_command_name" in guide
    assert "provider_recovery_smokes" in guide
    assert "provider_recovery_smoke_count" in guide
    assert "api_key_provider_recovery_checklist" in guide
    assert "api_key_provider_recovery_checklist.v1" in guide
    assert "recovery_smoke_command" in guide
    assert "recovery_smoke_available" in guide
    assert "provider_recovery_status" in guide
    assert "provider_recovery_required" in guide
    assert "provider_recovery_item_count" in guide
    assert "next_provider_recovery_action" in guide
    assert "provider_recovery_checklist" in guide
    assert "recover_failed_providers" in guide
    assert "blocking_step_names" in guide
    assert "next_blocking_action" in guide
    assert "api_key_operator_checklist.status" in guide
    assert "current_step" in guide
    assert "api_key_next_action_summary" in guide
    assert "api_key_next_action_summary.v1" in guide
    assert "next_action_name" in guide
    assert "next_action_command" in guide
    assert "next_action_is_recovery" in guide
    assert "next_action_network_call" in guide
    assert "next_action_mutates_local_state" in guide
    assert "accepted API-key aliases are visible" in guide
    assert "api_key_pipeline_stage_summary" in guide
    assert "api_key_pipeline_stage_summary.v1" in guide
    assert "stage_count" in guide
    assert "failed_stage_count" in guide
    assert "failed_stage_names" in guide
    assert "first_failed_stage" in guide
    assert "stage_name" in guide
    assert "run_live_signal_workflow_smoke" in guide
    assert "run_live_recording_smoke" in guide
    assert "api_key_pipeline_check_summary" in guide
    assert "api_key_pipeline_check_summary.v1" in guide
    assert "check_count" in guide
    assert "passed_check_count" in guide
    assert "failed_check_count" in guide
    assert "failed_check_keys" in guide
    assert "tools_with_failures" in guide
    assert "tool_failure_counts" in guide
    assert "first_failed_check" in guide
    assert "failed_checks" in guide
    assert "api_key_pipeline_failure_summary" in guide
    assert "api_key_pipeline_failure_summary.v1" in guide
    assert "has_failures" in guide
    assert "failure_category" in guide
    assert "first_failed_stage_name" in guide
    assert "first_failed_check_key" in guide
    assert "API-key failure one-line fields" in guide
    assert "api_key_failure_category" in guide
    assert "api_key_first_failed_stage_name" in guide
    assert "api_key_first_failed_check_key" in guide
    assert "api_key_setup_file_summary" in guide
    assert "api_key_setup_file_summary.v1" in guide
    assert "source_exists" in guide
    assert "target_exists" in guide
    assert "copy_required" in guide
    assert "preferred_env_keys" in guide
    assert "dotenv_examples" in guide
    assert "api_key_dotenv_loading_summary" in guide
    assert "api_key_dotenv_loading_summary.v1" in guide
    assert "dotenv_supported" in guide
    assert "dotenv_loading_enabled" in guide
    assert "disabled_env_key" in guide
    assert "configuration_precedence" in guide
    assert "api_key_provider_selection_summary" in guide
    assert "api_key_provider_selection_summary.v1" in guide
    assert "selected_provider_classes" in guide
    assert "configured_env_keys_by_provider_family" in guide
    assert "provider_env_key_hints_by_family" in guide
    assert "selected_provider_by_family" in guide
    assert "api_key_integration_status_summary" in guide
    assert "api_key_integration_status_summary.v1" in guide
    assert "api_keys_configured" in guide
    assert "live_providers_selected" in guide
    assert "dotenv_target_exists" in guide
    assert "failure_category" in guide
    assert "provider_recovery_action_status" in guide
    assert "provider_recovery_retry_ready" in guide
    assert "provider_recovery_all_retryable" in guide
    assert "provider_recovery_has_pending" in guide
    assert "provider_recovery_has_blocked" in guide
    assert "provider_recovery_item_count" in guide
    assert "provider_recovery_pending_count" in guide
    assert "provider_recovery_blocked_count" in guide
    assert "provider_error_count" in guide
    assert "provider_recovery_smoke_count" in guide
    assert "recovery identity lists" in guide
    assert "provider_recovery_provider_families" in guide
    assert "provider_recovery_providers" in guide
    assert "provider_recovery_pending_provider_families" in guide
    assert "provider_recovery_pending_providers" in guide
    assert "provider_recovery_blocked_provider_families" in guide
    assert "provider_recovery_blocked_providers" in guide
    assert "recovery command lists" in guide
    assert "provider_recovery_smoke_command_names" in guide
    assert "provider_recovery_smoke_commands" in guide
    assert "provider_recovery_pending_smoke_command_names" in guide
    assert "provider_recovery_pending_smoke_commands" in guide
    assert "provider_recovery_blocked_smoke_command_names" in guide
    assert "provider_recovery_blocked_smoke_commands" in guide
    assert "mirrors the first pending recovery command" in guide
    assert "mirrors the first blocked" in guide
    assert "next action summary carries provider smoke" in guide
    assert "next_action_provider_family" in guide
    assert "next_action_provider" in guide
    assert "next_action_smoke_command_name" in guide
    assert "failure summary provider identity" in guide
    assert "api_key_live_http_timeout_summary" in guide
    assert "api_key_live_http_timeout_summary.v1" in guide
    assert "timeout_seconds" in guide
    assert "default_timeout_seconds" in guide
    assert "applies_to" in guide
    assert "provider_recovery_smoke_available_count" in guide
    assert "provider_recovery_smoke_unavailable_count" in guide
    assert "provider_recovery_all_smokes_available" in guide
    assert "provider_recovery_network_call_count" in guide
    assert "provider_recovery_all_network_calls" in guide
    assert "provider_recovery_mutates_local_state_count" in guide
    assert "provider_recovery_any_mutates_local_state" in guide
    assert "provider_recovery_secret_values_returned_count" in guide
    assert "provider_recovery_any_secret_values_returned" in guide
    assert "provider_recovery_next_setup_actions" in guide
    assert "provider_recovery_exception_types" in guide
    assert "provider_recovery_exception_message_returned_count" in guide
    assert "provider_recovery_any_exception_messages_returned" in guide
    assert "provider_recovery_url_returned_count" in guide
    assert "provider_recovery_any_urls_returned" in guide
    assert "provider_recovery_network_call_policies" in guide
    assert "provider_recovery_statuses" in guide
    assert "provider_recovery_pending_count" in guide
    assert "provider_recovery_blocked_count" in guide
    assert "provider_recovery_has_pending" in guide
    assert "provider_recovery_has_blocked" in guide
    assert "provider_recovery_retry_ready" in guide
    assert "provider_recovery_all_retryable" in guide
    assert "provider_recovery_action_status" in guide
    assert "provider_recovery_all_pending" in guide
    assert "provider_recovery_pending_provider_families" in guide
    assert "provider_recovery_blocked_provider_families" in guide
    assert "provider_recovery_pending_providers" in guide
    assert "provider_recovery_blocked_providers" in guide
    assert "provider_recovery_pending_smoke_command_names" in guide
    assert "provider_recovery_pending_smoke_commands" in guide
    assert "provider_recovery_blocked_smoke_command_names" in guide
    assert "provider_recovery_blocked_smoke_commands" in guide
    assert "provider_recovery_provider_families" in guide
    assert "provider_recovery_providers" in guide
    assert "provider_recovery_smoke_command_names" in guide
    assert "provider_recovery_smoke_commands" in guide
    assert "provider_recovery_preferred_env_keys" in guide
    assert "provider_recovery_accepted_env_keys" in guide
    assert "provider_recovery_accepted_env_key_groups" in guide
    assert "next_pending_recovery_smoke_command_name" in guide
    assert "next_pending_recovery_smoke_command" in guide
    assert "next_pending_recovery_provider_family" in guide
    assert "next_pending_recovery_provider" in guide
    assert "next_pending_recovery_selected_provider_class" in guide
    assert "next_pending_recovery_provider_route_data_mode" in guide
    assert "next_pending_recovery_provider_route_live_data_required" in guide
    assert "next_pending_recovery_next_setup_action" in guide
    assert "next_pending_recovery_preferred_env_key" in guide
    assert "next_pending_recovery_accepted_env_keys" in guide
    assert "next_pending_recovery_network_call_policy" in guide
    assert "next_pending_recovery_smoke_available" in guide
    assert "next_pending_recovery_network_call" in guide
    assert "next_pending_recovery_mutates_local_state" in guide
    assert "next_pending_recovery_secret_values_returned" in guide
    assert "next_blocked_recovery_smoke_command_name" in guide
    assert "next_blocked_recovery_smoke_command" in guide
    assert "next_blocked_recovery_provider_family" in guide
    assert "next_blocked_recovery_provider" in guide
    assert "next_blocked_recovery_selected_provider_class" in guide
    assert "next_blocked_recovery_provider_route_data_mode" in guide
    assert "next_blocked_recovery_provider_route_live_data_required" in guide
    assert "next_blocked_recovery_next_setup_action" in guide
    assert "next_blocked_recovery_preferred_env_key" in guide
    assert "next_blocked_recovery_accepted_env_keys" in guide
    assert "next_blocked_recovery_network_call_policy" in guide
    assert "next_blocked_recovery_smoke_available" in guide
    assert "next_blocked_recovery_network_call" in guide
    assert "next_blocked_recovery_mutates_local_state" in guide
    assert "next_blocked_recovery_secret_values_returned" in guide
    assert "next_recovery_provider_family" in guide
    assert "next_recovery_provider" in guide
    assert "next_recovery_smoke_available" in guide
    assert "next_recovery_next_setup_action" in guide
    assert "next_recovery_preferred_env_key" in guide
    assert "next_recovery_accepted_env_keys" in guide
    assert "next_recovery_network_call_policy" in guide
    assert "next_recovery_network_call" in guide
    assert "next_recovery_mutates_local_state" in guide
    assert "next_recovery_exception_type" in guide
    assert "next_recovery_exception_message_returned" in guide
    assert "next_recovery_url_returned" in guide
    assert "next_recovery_secret_values_returned" in guide
    assert "network_call_policy" in guide
    assert "mutates_local_state" in guide
    assert "summary_only" in guide
    assert "api_key_pipeline_smoke_summary_only.v1" in guide
    assert '"summary_only":true' in guide
    assert "keeps\ntop-level `next_operator_action`" in guide
    assert "summary-only top-level provider smoke aggregates" in guide
    assert "provider\nsuccess contracts/checks" in guide
    assert "summary-only provider smoke status aggregate" in guide
    assert "provider_smoke_success_count" in guide
    assert "provider_smoke_all_successful" in guide
    assert "provider_smoke_success_provider_families" in guide
    assert "provider_smoke_success_providers" in guide
    assert "provider_smoke_success_smoke_command_names" in guide
    assert "provider_smoke_first_success_provider_family" in guide
    assert "provider_smoke_first_success_provider" in guide
    assert "provider_smoke_first_success_smoke_command_name" in guide
    assert "provider_smoke_first_success_status" in guide
    assert "provider_smoke_first_success_expected_live_contract" in guide
    assert "provider_smoke_first_success_expected_live_checks" in guide
    assert "provider_smoke_first_success_preferred_env_key" in guide
    assert "provider_smoke_first_success_accepted_env_keys" in guide
    assert "provider_smoke_first_success_network_call" in guide
    assert "provider_smoke_first_success_network_call_policy" in guide
    assert "provider_smoke_first_success_mutates_local_state" in guide
    assert "provider_smoke_first_success_secret_values_returned" in guide
    assert "summary-only provider smoke contract/check aggregates" in guide
    assert "provider_smoke_success_expected_live_contracts" in guide
    assert "provider_smoke_success_expected_live_checks" in guide
    assert "provider_smoke_success_check_count" in guide
    assert "Summary-only provider smoke safety aggregates" in guide
    assert "provider_smoke_success_network_call_count" in guide
    assert "provider_smoke_success_all_network_calls" in guide
    assert "provider_smoke_success_network_call_policies" in guide
    assert "provider_smoke_success_mutates_local_state_count" in guide
    assert "provider_smoke_success_any_mutates_local_state" in guide
    assert "provider_smoke_success_secret_values_returned_count" in guide
    assert "provider_smoke_success_any_secret_values_returned" in guide
    assert "Summary-only provider smoke env-key aggregates" in guide
    assert "provider_smoke_success_preferred_env_keys" in guide
    assert "provider_smoke_success_accepted_env_keys" in guide
    assert "provider_smoke_success_accepted_env_key_groups" in guide
    assert "matches\n`readiness_summary.next_operator_action`" in guide
    assert "next_operator_action_command" in guide
    assert "top-level summary-only recovery env hints and network policies" in guide
    assert (
        "top-level summary-only recovery diagnostic and safety\naggregates"
        in guide
    )
    assert "top-level summary-only recovery required status" in guide
    assert "provider_recovery_summary_status" in guide
    assert "next_operator_action_provider_family" in guide
    assert "next_operator_action_provider" in guide
    assert "next_operator_action_selected_provider_class" in guide
    assert "next_operator_action_provider_route_data_mode" in guide
    assert "next_operator_action_provider_route_live_data_required" in guide
    assert "next_operator_action_smoke_command_name" in guide
    assert "next_operator_action_expected_live_contract" in guide
    assert "next_operator_action_expected_live_checks" in guide
    assert (
        "readiness_summary` mirrors provider smoke or recovery "
        "`preferred_env_key`"
    ) in guide
    assert "next_operator_action_next_after_action" in guide
    assert "next_operator_action_dotenv_target_path" in guide
    assert "next_operator_action_source_path" in guide
    assert "next_operator_action_target_path" in guide
    assert "next_operator_action_preferred_env_key" in guide
    assert "next_operator_action_accepted_env_keys" in guide
    assert "next_operator_action_required_env_keys" in guide
    assert "next_operator_action_dotenv_examples" in guide
    assert "next_operator_action_status" in guide
    assert "next_operator_action_network_call" in guide
    assert "next_operator_action_network_call_policy" in guide
    assert "next_operator_action_mutates_local_state" in guide
    assert "next_operator_action_secret_input_required" in guide
    assert "next_operator_action_secret_values_returned" in guide
    assert "api_key_setup_current_step" in guide
    assert "api_key_setup_ready" in guide
    assert "api_key_setup_step_count" in guide
    assert "api_key_setup_ready_step_names" in guide
    assert "api_key_setup_ready_step_count" in guide
    assert "api_key_setup_blocking_step_names" in guide
    assert "api_key_setup_blocking_step_count" in guide
    assert "api_key_setup_next_blocking_step" in guide
    assert "api_key_setup_configured_provider_families" in guide
    assert "api_key_setup_missing_provider_families" in guide
    assert "api_key_setup_configured_provider_family_count" in guide
    assert "api_key_setup_required_provider_family_count" in guide
    assert "api_key_setup_ready_to_run_live_smoke" in guide
    assert "api_key_setup_provider_route_status" in guide
    assert "top-level summary-only recovery command lists" in guide
    assert "top-level summary-only recovery status and identity fields" in guide
    assert "top-level summary-only next recovery fields" in guide
    assert "top-level `next_operator_action`, `readiness_summary`" in guide
    assert "keeps `api_key_operator_checklist_summary`" in guide
    assert "api_key_operator_checklist_summary.v1" in guide
    assert "next_blocking_action_command" in guide
    assert "next_blocking_action_provider_family" in guide
    assert "next_blocking_action_provider" in guide
    assert "next_blocking_action_smoke_command_name" in guide
    assert "api_key_setup_quickstart_steps" in guide
    assert "api_key_setup_quickstart_step_names" in guide
    assert "api_key_setup_quickstart_step_count" in guide
    assert "api_key_setup_quickstart_next_step" in guide
    assert "api_key_setup_quickstart_next_command" in guide
    assert "api_key_setup_quickstart_command_plan" in guide
    assert "api_key_setup_quickstart_command_plan_names" in guide
    assert "api_key_setup_quickstart_command_plan_count" in guide
    assert "api_key_setup_quickstart_next_command_plan_item" in guide
    assert "api_key_setup_quickstart_next_command_plan_name" in guide
    assert "api_key_setup_quickstart_next_command_plan_kind" in guide
    assert "api_key_setup_quickstart_next_command_plan_command" in guide
    assert "api_key_setup_quickstart_next_command_plan_has_command" in guide
    assert (
        "api_key_setup_quickstart_next_command_plan_expected_live_check_count"
        in guide
    )
    assert (
        "api_key_setup_quickstart_next_command_plan_accepted_env_key_count"
        in guide
    )
    assert "api_key_setup_quickstart_next_command_plan_next_setup_action" in guide
    assert "api_key_setup_quickstart_next_command_plan_status" in guide
    assert "api_key_setup_quickstart_next_command_plan_ready_to_run" in guide
    assert "api_key_setup_quickstart_next_command_plan_requires_api_keys" in guide
    assert "api_key_setup_quickstart_next_command_plan_network_call" in guide
    assert (
        "api_key_setup_quickstart_next_command_plan_mutates_local_state" in guide
    )
    assert (
        "api_key_setup_quickstart_next_command_plan_secret_values_returned"
        in guide
    )
    assert "api_key_setup_dotenv_example_lines" in guide
    assert "api_key_setup_dotenv_example_line_count" in guide
    assert "api_key_setup_dotenv_example_env_keys" in guide
    assert "api_key_setup_dotenv_source_path" in guide
    assert "api_key_setup_dotenv_target_path" in guide
    assert "api_key_provider_selection_status" in guide
    assert "api_key_provider_factory" in guide
    assert "api_key_selected_provider_classes" in guide
    assert "api_key_selected_provider_class_count" in guide
    assert "api_key_selected_provider_by_family" in guide
    assert "api_key_configured_env_keys_by_provider_family" in guide
    assert "api_key_provider_env_key_hints_by_family" in guide
    assert "api_key_provider_smoke_total_count" in guide
    assert "api_key_provider_smoke_ready_count" in guide
    assert "api_key_provider_smoke_blocked_count" in guide
    assert "api_key_next_provider_smoke_command_name" in guide
    assert "api_key_next_provider_smoke_provider_family" in guide
    assert "api_key_next_provider_smoke_provider" in guide
    assert "api_key_next_provider_smoke_selected_provider_class" in guide
    assert "api_key_next_provider_smoke_provider_route_data_mode" in guide
    assert (
        "api_key_next_provider_smoke_provider_route_live_data_required" in guide
    )
    assert "api_key_next_provider_smoke_command" in guide
    assert "api_key_next_provider_smoke_next_setup_action" in guide
    assert "api_key_next_provider_smoke_status" in guide
    assert "api_key_integration_status" in guide
    assert "api_key_integration_api_keys_configured" in guide
    assert "api_key_integration_dotenv_loading_enabled" in guide
    assert "api_key_integration_dotenv_target_exists" in guide
    assert "api_key_integration_live_providers_selected" in guide
    assert "api_key_integration_ready_to_run_live_smoke" in guide
    assert "api_key_integration_configured_provider_families" in guide
    assert "api_key_integration_missing_provider_families" in guide
    assert "api_key_integration_selected_provider_classes" in guide
    assert "api_key_integration_next_action_name" in guide
    assert "api_key_integration_next_action_provider_family" in guide
    assert "api_key_integration_next_action_provider" in guide
    assert "api_key_integration_next_action_selected_provider_class" in guide
    assert "api_key_integration_next_action_provider_route_data_mode" in guide
    assert (
        "api_key_integration_next_action_provider_route_live_data_required"
        in guide
    )
    assert "api_key_integration_next_action_smoke_command_name" in guide
    assert "api_key_integration_next_action_is_recovery" in guide
    assert "api_key_integration_next_action_network_call" in guide
    assert "api_key_integration_next_action_status" in guide
    assert "api_key_integration_next_action_command" in guide
    assert "api_key_integration_next_action_has_command" in guide
    assert "api_key_integration_next_action_ready_to_run" in guide
    assert "api_key_integration_next_action_requires_api_keys" in guide
    assert "api_key_integration_next_action_mutates_local_state" in guide
    assert "api_key_integration_next_action_secret_values_returned" in guide
    assert "api_key_integration_next_action_preferred_env_key" in guide
    assert "api_key_integration_next_action_accepted_env_keys" in guide
    assert "api_key_integration_next_action_accepted_env_key_count" in guide
    assert "api_key_integration_next_action_required_env_keys" in guide
    assert "api_key_integration_next_action_required_env_key_count" in guide
    assert "api_key_integration_next_action_network_call_policy" in guide
    assert "api_key_integration_next_action_expected_live_contract" in guide
    assert "api_key_integration_next_action_expected_live_checks" in guide
    assert "api_key_integration_next_action_expected_live_check_count" in guide
    assert "api_key_integration_next_action_next_after_action" in guide
    assert "api_key_integration_next_action_dotenv_target_path" in guide
    assert "api_key_integration_next_action_source_path" in guide
    assert "api_key_integration_next_action_target_path" in guide
    assert "api_key_integration_next_action_secret_input_required" in guide
    assert "api_key_integration_next_action_dotenv_examples" in guide
    assert "api_key_integration_next_action_dotenv_example_count" in guide
    assert "api_key_integration_next_action_provider_smoke_count" in guide
    assert "api_key_integration_next_action_ready_provider_smoke_count" in guide
    assert "api_key_integration_next_action_blocked_provider_smoke_count" in guide
    assert "api_key_integration_provider_smoke_count" in guide
    assert "api_key_integration_ready_provider_smoke_count" in guide
    assert "api_key_integration_blocked_provider_smoke_count" in guide
    assert (
        "api_key_integration_next_action_next_provider_smoke_command_name" in guide
    )
    assert "api_key_integration_next_action_next_provider_smoke_command" in guide
    assert "api_key_integration_next_action_next_provider_smoke_has_command" in guide
    assert (
        "api_key_integration_next_action_next_provider_smoke_ready_to_run"
        in guide
    )
    assert (
        "api_key_integration_next_action_next_provider_smoke_requires_api_keys"
        in guide
    )
    assert (
        "api_key_integration_next_action_next_provider_smoke_next_setup_action"
        in guide
    )
    assert (
        "api_key_integration_next_action_next_provider_smoke_provider_family"
        in guide
    )
    assert "api_key_integration_next_action_next_provider_smoke_provider" in guide
    assert "api_key_integration_next_action_next_provider_smoke_status" in guide
    assert "api_key_integration_next_action_next_provider_smoke_network_call" in guide
    assert (
        "api_key_integration_next_action_next_provider_smoke_network_call_policy"
        in guide
    )
    assert (
        "api_key_integration_next_action_next_provider_smoke_expected_live_contract"
        in guide
    )
    assert (
        "api_key_integration_next_action_next_provider_smoke_expected_live_checks"
        in guide
    )
    assert (
        "api_key_integration_next_action_next_provider_smoke_expected_live_check_count"
        in guide
    )
    assert (
        "api_key_integration_next_action_next_provider_smoke_preferred_env_key"
        in guide
    )
    assert (
        "api_key_integration_next_action_next_provider_smoke_accepted_env_keys"
        in guide
    )
    assert (
        "api_key_integration_next_action_next_provider_smoke_accepted_env_key_count"
        in guide
    )
    assert (
        "api_key_integration_next_action_next_provider_smoke_mutates_local_state"
        in guide
    )
    assert (
        "api_key_integration_next_action_next_provider_smoke_secret_values_returned"
        in guide
    )
    assert "nested `api_key_integration_status_summary`" in guide
    assert "secret redaction flag" in guide
    assert "keeps `live_data_setup_summary`" in guide
    assert "live_data_setup_summary.v1" in guide
    assert "provider smoke plan" in guide
    assert "Provider smoke plan rows include `network_call`" in guide
    assert "keeps `api_key_requirements_summary`" in guide
    assert "api_key_pipeline_api_key_requirements_summary.v1" in guide
    assert "required_env_keys" in guide
    assert "accepted_env_keys" in guide
    assert "provider_requirements" in guide
    assert "api_key_required_env_keys" in guide
    assert "api_key_required_env_key_count" in guide
    assert "api_key_configured_env_keys" in guide
    assert "api_key_configured_env_key_count" in guide
    assert "api_key_requirement_configured_provider_families" in guide
    assert "api_key_requirement_missing_provider_families" in guide
    assert "api_key_provider_requirement_families" in guide
    assert "api_key_provider_requirement_count" in guide
    assert "api_key_requirement_next_missing_provider_family" in guide
    assert "api_key_requirement_next_missing_provider" in guide
    assert "api_key_requirement_next_missing_required_env_keys" in guide
    assert "api_key_requirement_next_missing_configured_env_keys" in guide
    assert "api_key_requirement_next_missing_missing_env_keys" in guide
    assert "api_key_requirement_next_missing_preferred_env_key" in guide
    assert "api_key_requirement_next_missing_accepted_env_keys" in guide
    assert "api_key_requirement_next_missing_accepted_env_key_count" in guide
    assert "api_key_requirement_next_missing_next_setup_action" in guide
    assert "api_key_requirement_next_missing_smoke_command_name" in guide
    assert "api_key_provider_requirement_required_env_keys" in guide
    assert "api_key_provider_requirement_required_env_key_counts" in guide
    assert "api_key_provider_requirement_configured_env_key_counts" in guide
    assert "api_key_provider_requirement_missing_env_keys" in guide
    assert "api_key_provider_requirement_missing_env_key_counts" in guide
    assert "api_key_provider_requirement_preferred_env_keys" in guide
    assert "api_key_provider_requirement_accepted_env_keys" in guide
    assert "api_key_provider_requirement_setup_statuses" in guide
    assert "api_key_provider_requirement_configured" in guide
    assert "api_key_provider_requirement_next_setup_actions" in guide
    assert "api_key_provider_requirement_smoke_command_names" in guide
    assert "api_key_requirement_selected_provider_class_by_family" in guide
    assert "api_key_requirement_provider_route_data_mode_by_family" in guide
    assert "api_key_requirement_provider_route_live_data_required_by_family" in guide
    assert "api_key_requirement_all_selected_routes_live" in guide
    assert "keeps `api_key_command_summary`" in guide
    assert "api_key_pipeline_api_key_command_summary.v1" in guide
    assert "provider_smoke_commands" in guide
    assert "Provider smoke rows include `network_call`" in guide
    assert "expected_live_contract" in guide
    assert "expected_live_checks" in guide
    assert "expected live\ncontract/checks" in guide
    assert "one_shot_pipeline_smoke" in guide
    assert "next_provider_smoke_command_name" in guide
    assert "api_key_copy_dotenv_command" in guide
    assert "api_key_copy_dotenv_required" in guide
    assert "api_key_next_smoke_command" in guide
    assert "api_key_next_smoke_command_name" in guide
    assert "api_key_one_shot_pipeline_smoke_command" in guide
    assert "api_key_provider_smoke_command_count" in guide
    assert "api_key_provider_smoke_command_names" in guide
    assert "api_key_provider_smoke_commands_by_family" in guide
    assert "api_key_provider_smoke_statuses_by_family" in guide
    assert "api_key_provider_smoke_selected_provider_class_by_family" in guide
    assert "api_key_provider_smoke_provider_route_data_mode_by_family" in guide
    assert (
        "api_key_provider_smoke_provider_route_live_data_required_by_family"
        in guide
    )
    assert "api_key_provider_smoke_network_call_policies_by_family" in guide
    assert "api_key_provider_smoke_next_setup_actions_by_family" in guide
    assert "api_key_provider_smoke_expected_live_contracts_by_family" in guide
    assert "api_key_provider_smoke_expected_live_checks_by_family" in guide
    assert "accepted API-key aliases" in guide
    assert "next_blocking_action_preferred_env_key" in guide
    assert "keeps `api_key_setup_file_summary`" in guide
    assert "api_key_setup_file_summary.v1" in guide
    assert "preferred_env_keys" in guide
    assert "dotenv_examples" in guide
    assert "KEY=placeholder" in guide
    assert "fill_live_data_api_keys" in guide
    assert "copy_command" in guide
    assert "copy_required" in guide
    assert "keeps `api_key_dotenv_loading_summary`" in guide
    assert "api_key_dotenv_loading_summary.v1" in guide
    assert "dotenv_loading_enabled" in guide
    assert "disabled_env_key" in guide
    assert "configuration_precedence" in guide
    assert "keeps `api_key_pipeline_stage_summary`" in guide
    assert "provider identity and env-key hints" in guide
    assert "keeps `api_key_pipeline_check_summary`" in guide
    assert "stage has provider recovery metadata" in guide
    assert "smoke_command_name" in guide
    assert "omitting nested full" in guide
    assert "smoke sections" in guide
    assert "api_key_provider_recovery_summary" in guide
    assert "api_key_provider_recovery_summary.v1" in guide
    assert "provider_error_count" in guide
    assert "next_recovery_smoke_command_name" in guide
    assert "next_recovery_smoke_command" in guide
    assert "preferred_env_key" in guide
    assert "failure category is provider recovery" in guide
    assert "next action summary carries provider smoke" in guide
    assert "exception_message_returned" in guide
    assert "url_returned" in guide
    assert "readiness_summary.next_operator_action" in guide
    assert "readiness_summary` also includes `preferred_env_key`" in guide
    assert "smoke_command" in guide
    assert "provider_family_summary" in guide
    assert "run_api_key_pipeline_smoke" in guide
    assert "readiness_summary" in guide
    assert "api_key_setup_status" in guide
    assert "ready_to_run_live_smoke" in guide
    assert "next_operator_action_name" in guide
    assert "Exported environment variables satisfy setup" in guide
    assert "no-secret `conflict` payloads" in guide
    assert "live_data_smoke_commands" in guide
    assert "get_live_data_api_key_status" in guide
    assert "get_live_data_provider_route" in guide
    assert "validate_live_data_smoke_result" in guide
    assert "run_live_data_smoke" in guide
    assert "run_integration_smoke" in guide
    assert "run_live_signal_workflow_smoke" in guide
    assert "run_live_recording_smoke" in guide
    assert "live_data_setup_summary_status" in guide
    assert "next_setup_step" in guide
    assert "setup_step_count" in guide
    assert "provider_setup_action_count" in guide
    assert "next_smoke_command_name" in guide
    assert "get_market_snapshot" in guide
    assert "get_macro_snapshot" in guide
    assert "get_news_bundle" in guide
    assert "export POLYGON_API_KEY" not in guide
    assert "export FRED_API_KEY" not in guide
    assert "export NEWS_API_KEY" not in guide


def test_setup_docs_document_project_alias_dotenv_cli_summary() -> None:
    readme = README.read_text(encoding="utf-8")
    guide = DEVOPS_GUIDE.read_text(encoding="utf-8")
    expected = (
        "summary-only pipeline CLI reads the same",
        "launch-directory `.env`",
        "HALO_SWING_MARKET_DATA_API_KEY",
        "HALO_SWING_MACRO_API_KEY",
        "HALO_SWING_NEWS_API_KEY",
        "without exported API-key environment variables",
    )

    for text in expected:
        assert text in readme
        assert text in guide


def test_readme_shows_api_key_integration_next_action_provider_smoke_progress() -> None:
    readme = README.read_text(encoding="utf-8")

    assert "api_key_integration_next_action_provider_smoke_count" in readme
    assert "api_key_integration_next_action_ready_provider_smoke_count" in readme
    assert "api_key_integration_next_action_blocked_provider_smoke_count" in readme
    assert "api_key_integration_provider_smoke_count" in readme
    assert "api_key_integration_ready_provider_smoke_count" in readme
    assert "api_key_integration_blocked_provider_smoke_count" in readme
    assert (
        "api_key_integration_next_action_next_provider_smoke_command_name"
        in readme
    )
    assert "api_key_integration_next_action_next_provider_smoke_command" in readme
    assert "api_key_integration_next_action_next_provider_smoke_has_command" in readme
    assert (
        "api_key_integration_next_action_next_provider_smoke_ready_to_run"
        in readme
    )
    assert (
        "api_key_integration_next_action_next_provider_smoke_requires_api_keys"
        in readme
    )
    assert (
        "api_key_integration_next_action_next_provider_smoke_next_setup_action"
        in readme
    )
    assert (
        "api_key_integration_next_action_next_provider_smoke_provider_family"
        in readme
    )
    assert "api_key_integration_next_action_next_provider_smoke_provider" in readme
    assert (
        "api_key_integration_next_action_next_provider_smoke_selected_provider_class"
        in readme
    )
    assert (
        "api_key_integration_next_action_next_provider_smoke_provider_route_data_mode"
        in readme
    )
    assert (
        "api_key_integration_next_action_next_provider_smoke_provider_route_live_data_required"
        in readme
    )
    assert "api_key_integration_next_action_next_provider_smoke_status" in readme
    assert "api_key_integration_next_action_next_provider_smoke_network_call" in readme
    assert (
        "api_key_integration_next_action_next_provider_smoke_network_call_policy"
        in readme
    )
    assert (
        "api_key_integration_next_action_next_provider_smoke_expected_live_contract"
        in readme
    )
    assert (
        "api_key_integration_next_action_next_provider_smoke_expected_live_checks"
        in readme
    )
    assert (
        "api_key_integration_next_action_next_provider_smoke_expected_live_check_count"
        in readme
    )
    assert (
        "api_key_integration_next_action_next_provider_smoke_preferred_env_key"
        in readme
    )
    assert (
        "api_key_integration_next_action_next_provider_smoke_accepted_env_keys"
        in readme
    )
    assert (
        "api_key_integration_next_action_next_provider_smoke_accepted_env_key_count"
        in readme
    )
    assert (
        "api_key_integration_next_action_next_provider_smoke_mutates_local_state"
        in readme
    )
    assert (
        "api_key_integration_next_action_next_provider_smoke_secret_values_returned"
        in readme
    )
    assert "nested `api_key_integration_status_summary`" in readme
    assert "secret redaction flag" in readme


def test_setup_docs_keep_api_key_integration_provider_smoke_progress_fields_in_sync() -> None:
    readme = README.read_text(encoding="utf-8")
    guide = DEVOPS_GUIDE.read_text(encoding="utf-8")
    field_names = (
        "api_key_integration_next_action_provider_smoke_count",
        "api_key_integration_next_action_ready_provider_smoke_count",
        "api_key_integration_next_action_blocked_provider_smoke_count",
        "api_key_integration_provider_smoke_count",
        "api_key_integration_ready_provider_smoke_count",
        "api_key_integration_blocked_provider_smoke_count",
        "api_key_integration_next_action_next_provider_smoke_command_name",
        "api_key_integration_next_action_next_provider_smoke_command",
        "api_key_integration_next_action_next_provider_smoke_has_command",
        "api_key_integration_next_action_next_provider_smoke_ready_to_run",
        "api_key_integration_next_action_next_provider_smoke_requires_api_keys",
        "api_key_integration_next_action_next_provider_smoke_next_setup_action",
        "api_key_integration_next_action_next_provider_smoke_provider_family",
        "api_key_integration_next_action_next_provider_smoke_provider",
        "api_key_integration_next_action_next_provider_smoke_selected_provider_class",
        "api_key_integration_next_action_next_provider_smoke_provider_route_data_mode",
        "api_key_integration_next_action_next_provider_smoke_provider_route_live_data_required",
        "api_key_integration_next_action_next_provider_smoke_status",
        "api_key_integration_next_action_next_provider_smoke_network_call",
        "api_key_integration_next_action_next_provider_smoke_network_call_policy",
        "api_key_integration_next_action_next_provider_smoke_expected_live_contract",
        "api_key_integration_next_action_next_provider_smoke_expected_live_checks",
        "api_key_integration_next_action_next_provider_smoke_expected_live_check_count",
        "api_key_integration_next_action_next_provider_smoke_preferred_env_key",
        "api_key_integration_next_action_next_provider_smoke_accepted_env_keys",
        "api_key_integration_next_action_next_provider_smoke_accepted_env_key_count",
        "api_key_integration_next_action_next_provider_smoke_mutates_local_state",
        "api_key_integration_next_action_next_provider_smoke_secret_values_returned",
    )

    for field_name in field_names:
        assert field_name in readme
        assert field_name in guide


def test_setup_docs_keep_api_key_provider_smoke_route_fields_in_sync() -> None:
    readme = README.read_text(encoding="utf-8")
    guide = DEVOPS_GUIDE.read_text(encoding="utf-8")
    field_names = (
        "selected_provider_class",
        "provider_route_data_mode",
        "provider_route_live_data_required",
        "api_key_next_provider_smoke_selected_provider_class",
        "api_key_next_provider_smoke_provider_route_data_mode",
        "api_key_next_provider_smoke_provider_route_live_data_required",
        "api_key_next_provider_smoke_has_command",
        "api_key_next_provider_smoke_ready_to_run",
        "api_key_next_provider_smoke_requires_api_keys",
        "api_key_next_provider_smoke_expected_live_check_count",
        "api_key_next_provider_smoke_accepted_env_key_count",
        "api_key_next_ready_provider_smoke_provider_family",
        "api_key_next_ready_provider_smoke_provider",
        "api_key_next_ready_provider_smoke_selected_provider_class",
        "api_key_next_ready_provider_smoke_provider_route_data_mode",
        "api_key_next_ready_provider_smoke_provider_route_live_data_required",
        "api_key_next_ready_provider_smoke_command_name",
        "api_key_next_ready_provider_smoke_command",
        "api_key_next_ready_provider_smoke_has_command",
        "api_key_next_ready_provider_smoke_ready_to_run",
        "api_key_next_ready_provider_smoke_requires_api_keys",
        "api_key_next_ready_provider_smoke_expected_live_contract",
        "api_key_next_ready_provider_smoke_expected_live_checks",
        "api_key_next_ready_provider_smoke_expected_live_check_count",
        "api_key_next_ready_provider_smoke_preferred_env_key",
        "api_key_next_ready_provider_smoke_accepted_env_keys",
        "api_key_next_ready_provider_smoke_accepted_env_key_count",
        "api_key_next_ready_provider_smoke_next_setup_action",
        "api_key_next_ready_provider_smoke_status",
        "api_key_next_ready_provider_smoke_network_call",
        "api_key_next_ready_provider_smoke_network_call_policy",
        "api_key_next_ready_provider_smoke_mutates_local_state",
        "api_key_next_ready_provider_smoke_secret_values_returned",
        "api_key_next_blocked_provider_smoke_provider_family",
        "api_key_next_blocked_provider_smoke_provider",
        "api_key_next_blocked_provider_smoke_selected_provider_class",
        "api_key_next_blocked_provider_smoke_provider_route_data_mode",
        "api_key_next_blocked_provider_smoke_provider_route_live_data_required",
        "api_key_next_blocked_provider_smoke_command_name",
        "api_key_next_blocked_provider_smoke_command",
        "api_key_next_blocked_provider_smoke_has_command",
        "api_key_next_blocked_provider_smoke_ready_to_run",
        "api_key_next_blocked_provider_smoke_requires_api_keys",
        "api_key_next_blocked_provider_smoke_expected_live_contract",
        "api_key_next_blocked_provider_smoke_expected_live_checks",
        "api_key_next_blocked_provider_smoke_expected_live_check_count",
        "api_key_next_blocked_provider_smoke_preferred_env_key",
        "api_key_next_blocked_provider_smoke_accepted_env_keys",
        "api_key_next_blocked_provider_smoke_accepted_env_key_count",
        "api_key_next_blocked_provider_smoke_next_setup_action",
        "api_key_next_blocked_provider_smoke_status",
        "api_key_next_blocked_provider_smoke_network_call",
        "api_key_next_blocked_provider_smoke_network_call_policy",
        "api_key_next_blocked_provider_smoke_mutates_local_state",
        "api_key_next_blocked_provider_smoke_secret_values_returned",
        "api_key_provider_smoke_provider_families",
        "api_key_provider_smoke_provider_family_count",
        "api_key_provider_smoke_ready_provider_families",
        "api_key_provider_smoke_blocked_provider_families",
        "api_key_provider_smoke_ready_command_names",
        "api_key_provider_smoke_ready_commands",
        "api_key_provider_smoke_blocked_command_names",
        "api_key_provider_smoke_commands",
        "api_key_provider_smoke_blocked_commands",
        "api_key_provider_smoke_kinds_by_family",
        "api_key_provider_smoke_command_names_by_family",
        "api_key_provider_smoke_provider_by_family",
        "api_key_provider_smoke_selected_provider_class_by_family",
        "api_key_provider_smoke_provider_route_data_mode_by_family",
        "api_key_provider_smoke_provider_route_live_data_required_by_family",
        "api_key_provider_smoke_all_live_data_required",
        "api_key_provider_smoke_provider_route_family_count",
        "api_key_provider_smoke_selected_provider_family_count",
        "api_key_provider_smoke_provider_route_live_data_required_family_count",
        "api_key_provider_smoke_provider_route_data_mode_counts",
        "api_key_provider_smoke_expected_live_check_count",
        "api_key_provider_smoke_expected_live_check_counts_by_family",
        "api_key_provider_smoke_accepted_env_keys_by_family",
        "api_key_provider_smoke_accepted_env_key_groups",
        "api_key_provider_smoke_accepted_env_key_group_count",
        "api_key_provider_smoke_unique_accepted_env_keys",
        "api_key_provider_smoke_unique_accepted_env_key_count",
        "api_key_provider_smoke_preferred_env_keys_by_family",
        "api_key_provider_smoke_preferred_env_keys",
        "api_key_provider_smoke_preferred_env_key_count",
        "api_key_provider_smoke_accepted_env_key_count",
        "api_key_provider_smoke_accepted_env_key_counts_by_family",
        "api_key_provider_smoke_network_calls_by_family",
        "api_key_provider_smoke_network_call_count",
        "api_key_provider_smoke_all_network_calls",
        "api_key_provider_smoke_all_ready",
        "api_key_provider_smoke_any_blocked",
        "api_key_provider_smoke_action_status",
        "api_key_provider_smoke_next_action",
        "api_key_provider_smoke_next_action_ready_to_run",
        "api_key_provider_smoke_next_action_requires_api_keys",
        "api_key_provider_smoke_next_action_primary_provider_family",
        "api_key_provider_smoke_next_action_primary_provider",
        "api_key_provider_smoke_next_action_primary_kind",
        "api_key_provider_smoke_next_action_primary_command_name",
        "api_key_provider_smoke_next_action_primary_command",
        "api_key_provider_smoke_next_action_primary_has_command",
        "api_key_provider_smoke_next_action_primary_status",
        "api_key_provider_smoke_next_action_primary_ready_to_run",
        "api_key_provider_smoke_next_action_primary_requires_api_keys",
        "api_key_provider_smoke_next_action_primary_setup_action",
        "api_key_provider_smoke_next_action_primary_selected_provider_class",
        "api_key_provider_smoke_next_action_primary_provider_route_data_mode",
        "api_key_provider_smoke_next_action_primary_provider_route_live_data_required",
        "api_key_provider_smoke_next_action_primary_network_call",
        "api_key_provider_smoke_next_action_primary_network_call_policy",
        "api_key_provider_smoke_next_action_primary_mutates_local_state",
        "api_key_provider_smoke_next_action_primary_secret_values_returned",
        "api_key_provider_smoke_next_action_primary_preferred_env_key",
        "api_key_provider_smoke_next_action_primary_accepted_env_keys",
        "api_key_provider_smoke_next_action_primary_accepted_env_key_count",
        "api_key_provider_smoke_next_action_primary_expected_live_contract",
        "api_key_provider_smoke_next_action_primary_expected_live_checks",
        "api_key_provider_smoke_next_action_primary_expected_live_check_count",
        "api_key_provider_smoke_next_action_command_count",
        "api_key_provider_smoke_next_action_command_names",
        "api_key_provider_smoke_next_action_commands",
        "api_key_provider_smoke_next_action_kinds_by_family",
        "api_key_provider_smoke_next_action_command_names_by_family",
        "api_key_provider_smoke_next_action_commands_by_family",
        "api_key_provider_smoke_next_action_provider_by_family",
        "api_key_provider_smoke_next_action_provider_families",
        "api_key_provider_smoke_next_action_provider_family_count",
        "api_key_provider_smoke_next_action_providers",
        "api_key_provider_smoke_next_action_provider_count",
        "api_key_provider_smoke_next_action_statuses",
        "api_key_provider_smoke_next_action_status_count",
        "api_key_provider_smoke_next_action_statuses_by_family",
        "api_key_provider_smoke_next_action_ready_count",
        "api_key_provider_smoke_next_action_blocked_count",
        "api_key_provider_smoke_next_action_all_ready",
        "api_key_provider_smoke_next_action_any_blocked",
        "api_key_provider_smoke_next_action_setup_actions",
        "api_key_provider_smoke_next_action_setup_action_count",
        "api_key_provider_smoke_next_action_setup_actions_by_family",
        "api_key_provider_smoke_next_action_network_call_policies",
        "api_key_provider_smoke_next_action_network_call_policy_count",
        "api_key_provider_smoke_next_action_network_call_policies_by_family",
        "api_key_provider_smoke_next_action_network_calls_by_family",
        "api_key_provider_smoke_next_action_network_call_count",
        "api_key_provider_smoke_next_action_all_network_calls",
        "api_key_provider_smoke_next_action_mutates_local_state_by_family",
        "api_key_provider_smoke_next_action_mutates_local_state_count",
        "api_key_provider_smoke_next_action_any_mutates_local_state",
        "api_key_provider_smoke_next_action_secret_values_returned_by_family",
        "api_key_provider_smoke_next_action_secret_values_returned_count",
        "api_key_provider_smoke_next_action_any_secret_values_returned",
        "api_key_provider_smoke_next_action_selected_provider_class_by_family",
        "api_key_provider_smoke_next_action_provider_route_data_mode_by_family",
        "api_key_provider_smoke_next_action_provider_route_live_data_required_by_family",
        "api_key_provider_smoke_next_action_all_selected_routes_live",
        "api_key_provider_smoke_next_action_provider_route_family_count",
        "api_key_provider_smoke_next_action_selected_provider_family_count",
        "api_key_provider_smoke_next_action_provider_route_live_data_required_family_count",
        "api_key_provider_smoke_next_action_provider_route_data_mode_counts",
        "api_key_provider_smoke_next_action_expected_live_contracts",
        "api_key_provider_smoke_next_action_expected_live_contract_count",
        "api_key_provider_smoke_next_action_expected_live_contracts_by_family",
        "api_key_provider_smoke_next_action_expected_live_checks",
        "api_key_provider_smoke_next_action_expected_live_check_count",
        "api_key_provider_smoke_next_action_expected_live_checks_by_family",
        "api_key_provider_smoke_next_action_expected_live_check_counts_by_family",
        "api_key_provider_smoke_next_action_preferred_env_keys",
        "api_key_provider_smoke_next_action_preferred_env_key_count",
        "api_key_provider_smoke_next_action_accepted_env_keys",
        "api_key_provider_smoke_next_action_accepted_env_key_count",
        "api_key_provider_smoke_next_action_accepted_env_key_groups",
        "api_key_provider_smoke_next_action_accepted_env_key_group_count",
        "api_key_provider_smoke_next_action_preferred_env_keys_by_family",
        "api_key_provider_smoke_next_action_accepted_env_keys_by_family",
        "api_key_provider_smoke_next_action_accepted_env_key_counts_by_family",
        "api_key_provider_smoke_ready_preferred_env_keys",
        "api_key_provider_smoke_ready_preferred_env_key_count",
        "api_key_provider_smoke_ready_accepted_env_keys",
        "api_key_provider_smoke_ready_accepted_env_key_count",
        "api_key_provider_smoke_ready_accepted_env_key_groups",
        "api_key_provider_smoke_ready_accepted_env_key_group_count",
        "api_key_provider_smoke_ready_preferred_env_keys_by_family",
        "api_key_provider_smoke_ready_accepted_env_keys_by_family",
        "api_key_provider_smoke_ready_accepted_env_key_counts_by_family",
        "api_key_provider_smoke_blocked_preferred_env_keys",
        "api_key_provider_smoke_blocked_preferred_env_key_count",
        "api_key_provider_smoke_blocked_accepted_env_keys",
        "api_key_provider_smoke_blocked_accepted_env_key_count",
        "api_key_provider_smoke_blocked_accepted_env_key_groups",
        "api_key_provider_smoke_blocked_accepted_env_key_group_count",
        "api_key_provider_smoke_blocked_preferred_env_keys_by_family",
        "api_key_provider_smoke_blocked_accepted_env_keys_by_family",
        "api_key_provider_smoke_blocked_accepted_env_key_counts_by_family",
        "api_key_provider_smoke_mutates_local_state_by_family",
        "api_key_provider_smoke_mutates_local_state_count",
        "api_key_provider_smoke_any_mutates_local_state",
        "api_key_provider_smoke_secret_values_returned_by_family",
        "api_key_provider_smoke_secret_values_returned_count",
        "api_key_provider_smoke_any_secret_values_returned",
    )

    for field_name in field_names:
        assert field_name in readme
        assert field_name in guide


def test_setup_docs_keep_api_key_integration_next_provider_smoke_route_fields_in_sync() -> None:
    readme = README.read_text(encoding="utf-8")
    guide = DEVOPS_GUIDE.read_text(encoding="utf-8")
    field_names = (
        "api_key_integration_next_action_next_provider_smoke_selected_provider_class",
        "api_key_integration_next_action_next_provider_smoke_provider_route_data_mode",
        "api_key_integration_next_action_next_provider_smoke_provider_route_live_data_required",
    )

    for field_name in field_names:
        assert field_name in readme
        assert field_name in guide


def test_setup_docs_keep_api_key_integration_status_fields_in_sync() -> None:
    readme = README.read_text(encoding="utf-8")
    guide = DEVOPS_GUIDE.read_text(encoding="utf-8")
    field_names = (
        "api_key_integration_status_summary",
        "api_key_integration_status_summary.v1",
        "api_key_integration_status",
        "api_key_integration_api_keys_configured",
        "api_key_integration_dotenv_loading_enabled",
        "api_key_integration_dotenv_target_exists",
        "api_key_integration_live_providers_selected",
        "api_key_integration_ready_to_run_live_smoke",
        "api_key_integration_configured_provider_families",
        "api_key_integration_missing_provider_families",
        "api_key_integration_selected_provider_classes",
        "selected_provider_class_by_family",
        "provider_route_data_mode_by_family",
        "provider_route_live_data_required_by_family",
        "all_selected_routes_live",
        "provider_smoke_count",
        "ready_provider_smoke_count",
        "blocked_provider_smoke_count",
        "api_key_integration_selected_provider_class_by_family",
        "api_key_integration_provider_route_data_mode_by_family",
        "api_key_integration_provider_route_live_data_required_by_family",
        "api_key_integration_all_selected_routes_live",
        "api_key_integration_provider_route_family_count",
        "api_key_integration_selected_provider_family_count",
        "api_key_integration_provider_route_live_data_required_family_count",
        "api_key_integration_provider_route_data_mode_counts",
        "api_key_integration_provider_smoke_count",
        "api_key_integration_ready_provider_smoke_count",
        "api_key_integration_blocked_provider_smoke_count",
        "api_key_integration_next_action_name",
        "api_key_integration_one_shot_pipeline_smoke_name",
        "api_key_integration_one_shot_pipeline_smoke_command",
        "api_key_integration_one_shot_pipeline_smoke_status",
        "api_key_integration_one_shot_pipeline_smoke_blocked_reason",
        "api_key_integration_one_shot_pipeline_smoke_unblock_action_name",
        "api_key_integration_one_shot_pipeline_smoke_unblock_command",
        "api_key_integration_one_shot_pipeline_smoke_unblock_next_after_action",
        "api_key_integration_one_shot_pipeline_smoke_unblock_source_path",
        "api_key_integration_one_shot_pipeline_smoke_unblock_target_path",
        "api_key_integration_one_shot_pipeline_smoke_unblock_dotenv_target_path",
        "api_key_integration_one_shot_pipeline_smoke_unblock_followup_required_env_keys",
        "api_key_integration_one_shot_pipeline_smoke_unblock_followup_required_env_key_count",
        "api_key_integration_one_shot_pipeline_smoke_unblock_followup_dotenv_examples",
        "api_key_integration_one_shot_pipeline_smoke_unblock_followup_dotenv_example_count",
        "api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_name",
        "api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_provider_families",
        "api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_provider_family_count",
        "api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_provider_by_family",
        "api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_preferred_env_key_by_family",
        "api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_accepted_env_keys_by_family",
        "api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_required_env_keys_by_family",
        "api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_missing_env_keys_by_family",
        "api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_missing_env_keys",
        "api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_missing_env_key_count",
        "api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_configured_env_keys_by_family",
        "api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_configured_env_keys",
        "api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_configured_env_key_count",
        "api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_configured_by_family",
        "api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_configured_provider_families",
        "api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_blocked_provider_families",
        "api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_configured_provider_family_count",
        "api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_blocked_provider_family_count",
        "api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_all_provider_families_configured",
        "api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_setup_status_by_family",
        "api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_next_setup_action_by_family",
        "api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_next_setup_actions",
        "api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_next_setup_action_count",
        "api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_command",
        "api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_status",
        "api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_requires_api_keys",
        "api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_ready_after_env_keys",
        "api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_api_key_only_setup",
        "api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_api_key_only_setup_ready_after_env_keys",
        "api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_api_key_only_setup_next_command_name",
        "api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_api_key_only_setup_next_command",
        "api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_api_key_only_setup_next_command_status",
        "api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_api_key_only_setup_next_command_requires_api_keys",
        "api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_api_key_only_setup_next_command_ready_after_env_keys",
        "api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_api_key_only_setup_next_command_provider_families",
        "api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_api_key_only_setup_next_command_provider_family_count",
        "api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_api_key_only_setup_next_command_configured_provider_families",
        "api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_api_key_only_setup_next_command_blocked_provider_families",
        "api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_api_key_only_setup_next_command_configured_provider_family_count",
        "api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_api_key_only_setup_next_command_blocked_provider_family_count",
        "api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_api_key_only_setup_next_command_all_provider_families_configured",
        "api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_api_key_only_setup_next_command_selected_provider_classes",
        "api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_api_key_only_setup_next_command_selected_provider_class_count",
        "api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_api_key_only_setup_next_command_selected_provider_class_by_family",
        "api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_api_key_only_setup_next_command_provider_route_data_mode_by_family",
        "api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_api_key_only_setup_next_command_provider_route_live_data_required_by_family",
        "api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_api_key_only_setup_next_command_all_selected_routes_live",
        "api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_api_key_only_setup_next_command_provider_route_family_count",
        "api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_api_key_only_setup_next_command_selected_provider_family_count",
        "api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_api_key_only_setup_next_command_provider_route_live_data_required_family_count",
        "api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_api_key_only_setup_next_command_provider_route_data_mode_counts",
        "api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_api_key_only_setup_next_command_provider_by_family",
        "api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_api_key_only_setup_next_command_preferred_env_key_by_family",
        "api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_api_key_only_setup_next_command_accepted_env_keys_by_family",
        "api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_api_key_only_setup_next_command_required_env_keys_by_family",
        "api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_api_key_only_setup_next_command_missing_env_keys_by_family",
        "api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_api_key_only_setup_next_command_missing_env_keys",
        "api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_api_key_only_setup_next_command_missing_env_key_count",
        "api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_api_key_only_setup_next_command_configured_env_keys_by_family",
        "api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_api_key_only_setup_next_command_configured_env_keys",
        "api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_api_key_only_setup_next_command_configured_env_key_count",
        "api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_api_key_only_setup_next_command_configured_by_family",
        "api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_api_key_only_setup_next_command_setup_status_by_family",
        "api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_api_key_only_setup_next_command_next_setup_action_by_family",
        "api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_api_key_only_setup_next_command_next_setup_actions",
        "api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_api_key_only_setup_next_command_next_setup_action_count",
        "api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_api_key_only_setup_next_command_required_env_keys",
        "api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_api_key_only_setup_next_command_required_env_key_count",
        "api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_api_key_only_setup_next_command_dotenv_examples",
        "api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_api_key_only_setup_next_command_dotenv_example_count",
        "api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_api_key_only_setup_next_command_network_call",
        "api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_api_key_only_setup_next_command_network_call_policy",
        "api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_api_key_only_setup_next_command_mutates_local_state",
        "api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_api_key_only_setup_next_command_secret_values_returned",
        "api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_network_call",
        "api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_network_call_policy",
        "api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_mutates_local_state",
        "api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_secret_values_returned",
        "api_key_integration_one_shot_pipeline_smoke_unblock_ready_to_run",
        "api_key_integration_one_shot_pipeline_smoke_unblock_network_call",
        "api_key_integration_one_shot_pipeline_smoke_unblock_mutates_local_state",
        "api_key_integration_one_shot_pipeline_smoke_unblock_secret_values_returned",
        "api_key_integration_one_shot_pipeline_smoke_has_command",
        "api_key_integration_one_shot_pipeline_smoke_ready_to_run",
        "api_key_integration_one_shot_pipeline_smoke_requires_api_keys",
        "api_key_integration_one_shot_pipeline_smoke_network_call",
        "api_key_integration_one_shot_pipeline_smoke_network_call_policy",
        "api_key_integration_one_shot_pipeline_smoke_mutates_local_state",
        "api_key_integration_one_shot_pipeline_smoke_secret_values_returned",
        "next_action_status",
        "next_action_command",
        "next_action_required_env_keys",
        "next_action_network_call_policy",
        "next_action_next_after_action",
        "next_action_dotenv_target_path",
        "next_action_source_path",
        "next_action_target_path",
        "next_action_secret_input_required",
        "next_action_dotenv_examples",
        "next_action_dotenv_example_count",
        "next_action_mutates_local_state",
        "next_action_secret_values_returned",
    )

    for field_name in field_names:
        assert field_name in readme
        assert field_name in guide


def test_setup_docs_keep_api_key_integration_next_action_fields_in_sync() -> None:
    readme = README.read_text(encoding="utf-8")
    guide = DEVOPS_GUIDE.read_text(encoding="utf-8")
    field_names = (
        "api_key_integration_next_action_provider_family",
        "api_key_integration_next_action_provider",
        "api_key_integration_next_action_selected_provider_class",
        "api_key_integration_next_action_provider_route_data_mode",
        "api_key_integration_next_action_provider_route_live_data_required",
        "api_key_integration_next_action_smoke_command_name",
        "api_key_integration_next_action_is_recovery",
        "api_key_integration_next_action_network_call",
        "api_key_integration_next_action_status",
        "api_key_integration_next_action_command",
        "api_key_integration_next_action_has_command",
        "api_key_integration_next_action_ready_to_run",
        "api_key_integration_next_action_requires_api_keys",
        "api_key_integration_next_action_mutates_local_state",
        "api_key_integration_next_action_secret_values_returned",
        "api_key_integration_next_action_preferred_env_key",
        "api_key_integration_next_action_accepted_env_keys",
        "api_key_integration_next_action_accepted_env_key_count",
        "api_key_integration_next_action_required_env_keys",
        "api_key_integration_next_action_required_env_key_count",
        "api_key_integration_next_action_network_call_policy",
        "api_key_integration_next_action_expected_live_contract",
        "api_key_integration_next_action_expected_live_checks",
        "api_key_integration_next_action_expected_live_check_count",
        "api_key_integration_next_action_next_after_action",
        "api_key_integration_next_action_dotenv_target_path",
        "api_key_integration_next_action_source_path",
        "api_key_integration_next_action_target_path",
        "api_key_integration_next_action_secret_input_required",
        "api_key_integration_next_action_dotenv_examples",
        "api_key_integration_next_action_dotenv_example_count",
    )

    for field_name in field_names:
        assert field_name in readme
        assert field_name in guide


def test_setup_docs_keep_api_key_setup_progress_fields_in_sync() -> None:
    readme = README.read_text(encoding="utf-8")
    guide = DEVOPS_GUIDE.read_text(encoding="utf-8")
    field_names = (
        "api_key_setup_current_step",
        "api_key_setup_ready",
        "api_key_setup_step_count",
        "api_key_setup_ready_step_names",
        "api_key_setup_ready_step_count",
        "api_key_setup_blocking_step_names",
        "api_key_setup_blocking_step_count",
        "api_key_setup_next_blocking_step",
        "api_key_setup_configured_provider_families",
        "api_key_setup_missing_provider_families",
        "api_key_setup_configured_provider_family_count",
        "api_key_setup_required_provider_family_count",
        "api_key_setup_ready_to_run_live_smoke",
        "api_key_setup_provider_route_status",
        "api_key_setup_selected_provider_class_by_family",
        "api_key_setup_provider_route_data_mode_by_family",
        "api_key_setup_provider_route_live_data_required_by_family",
        "api_key_setup_all_selected_routes_live",
        "api_key_setup_provider_route_family_count",
        "api_key_setup_selected_provider_family_count",
        "api_key_setup_provider_route_live_data_required_family_count",
        "api_key_setup_provider_route_data_mode_counts",
    )

    for field_name in field_names:
        assert field_name in readme
        assert field_name in guide


def test_setup_docs_keep_api_key_setup_quickstart_fields_in_sync() -> None:
    readme = README.read_text(encoding="utf-8")
    guide = DEVOPS_GUIDE.read_text(encoding="utf-8")
    field_names = (
        "api_key_setup_quickstart_steps",
        "api_key_setup_quickstart_step_names",
        "api_key_setup_quickstart_step_count",
        "api_key_setup_quickstart_next_step",
        "api_key_setup_quickstart_next_command",
        "api_key_setup_quickstart_command_plan",
        "api_key_setup_quickstart_command_plan_names",
        "api_key_setup_quickstart_command_plan_count",
        "api_key_setup_quickstart_command_plan_provider_families",
        "api_key_setup_quickstart_command_plan_provider_family_count",
        "api_key_setup_quickstart_command_plan_ready_provider_families",
        "api_key_setup_quickstart_command_plan_blocked_provider_families",
        "api_key_setup_quickstart_command_plan_ready_command_names",
        "api_key_setup_quickstart_command_plan_ready_commands",
        "api_key_setup_quickstart_command_plan_blocked_command_names",
        "api_key_setup_quickstart_command_plan_blocked_commands",
        "api_key_setup_quickstart_command_plan_next_ready_provider_smoke_provider_family",
        "api_key_setup_quickstart_command_plan_next_ready_provider_smoke_provider",
        "api_key_setup_quickstart_command_plan_next_ready_provider_smoke_selected_provider_class",
        "api_key_setup_quickstart_command_plan_next_ready_provider_smoke_provider_route_data_mode",
        "api_key_setup_quickstart_command_plan_next_ready_provider_smoke_provider_route_live_data_required",
        "api_key_setup_quickstart_command_plan_next_ready_provider_smoke_command_name",
        "api_key_setup_quickstart_command_plan_next_ready_provider_smoke_command",
        "api_key_setup_quickstart_command_plan_next_ready_provider_smoke_has_command",
        "api_key_setup_quickstart_command_plan_next_ready_provider_smoke_ready_to_run",
        "api_key_setup_quickstart_command_plan_next_ready_provider_smoke_requires_api_keys",
        "api_key_setup_quickstart_command_plan_next_ready_provider_smoke_expected_live_contract",
        "api_key_setup_quickstart_command_plan_next_ready_provider_smoke_expected_live_checks",
        "api_key_setup_quickstart_command_plan_next_ready_provider_smoke_expected_live_check_count",
        "api_key_setup_quickstart_command_plan_next_ready_provider_smoke_preferred_env_key",
        "api_key_setup_quickstart_command_plan_next_ready_provider_smoke_accepted_env_keys",
        "api_key_setup_quickstart_command_plan_next_ready_provider_smoke_accepted_env_key_count",
        "api_key_setup_quickstart_command_plan_next_ready_provider_smoke_next_setup_action",
        "api_key_setup_quickstart_command_plan_next_ready_provider_smoke_status",
        "api_key_setup_quickstart_command_plan_next_ready_provider_smoke_network_call",
        "api_key_setup_quickstart_command_plan_next_ready_provider_smoke_network_call_policy",
        "api_key_setup_quickstart_command_plan_next_ready_provider_smoke_mutates_local_state",
        "api_key_setup_quickstart_command_plan_next_ready_provider_smoke_secret_values_returned",
        "api_key_setup_quickstart_command_plan_next_blocked_provider_smoke_provider_family",
        "api_key_setup_quickstart_command_plan_next_blocked_provider_smoke_provider",
        "api_key_setup_quickstart_command_plan_next_blocked_provider_smoke_selected_provider_class",
        "api_key_setup_quickstart_command_plan_next_blocked_provider_smoke_provider_route_data_mode",
        "api_key_setup_quickstart_command_plan_next_blocked_provider_smoke_provider_route_live_data_required",
        "api_key_setup_quickstart_command_plan_next_blocked_provider_smoke_command_name",
        "api_key_setup_quickstart_command_plan_next_blocked_provider_smoke_command",
        "api_key_setup_quickstart_command_plan_next_blocked_provider_smoke_has_command",
        "api_key_setup_quickstart_command_plan_next_blocked_provider_smoke_ready_to_run",
        "api_key_setup_quickstart_command_plan_next_blocked_provider_smoke_requires_api_keys",
        "api_key_setup_quickstart_command_plan_next_blocked_provider_smoke_expected_live_contract",
        "api_key_setup_quickstart_command_plan_next_blocked_provider_smoke_expected_live_checks",
        "api_key_setup_quickstart_command_plan_next_blocked_provider_smoke_expected_live_check_count",
        "api_key_setup_quickstart_command_plan_next_blocked_provider_smoke_preferred_env_key",
        "api_key_setup_quickstart_command_plan_next_blocked_provider_smoke_accepted_env_keys",
        "api_key_setup_quickstart_command_plan_next_blocked_provider_smoke_accepted_env_key_count",
        "api_key_setup_quickstart_command_plan_next_blocked_provider_smoke_next_setup_action",
        "api_key_setup_quickstart_command_plan_next_blocked_provider_smoke_status",
        "api_key_setup_quickstart_command_plan_next_blocked_provider_smoke_network_call",
        "api_key_setup_quickstart_command_plan_next_blocked_provider_smoke_network_call_policy",
        "api_key_setup_quickstart_command_plan_next_blocked_provider_smoke_mutates_local_state",
        "api_key_setup_quickstart_command_plan_next_blocked_provider_smoke_secret_values_returned",
        "api_key_setup_quickstart_command_plan_ready_provider_smoke_count",
        "api_key_setup_quickstart_command_plan_blocked_provider_smoke_count",
        "api_key_setup_quickstart_command_plan_all_provider_smokes_ready",
        "api_key_setup_quickstart_command_plan_all_provider_smokes_network_calls",
        "api_key_setup_quickstart_command_plan_all_provider_smokes_live_required",
        "api_key_setup_quickstart_command_plan_any_provider_smoke_mutates_local_state",
        "api_key_setup_quickstart_command_plan_any_provider_smoke_secret_values_returned",
        "api_key_setup_quickstart_command_plan_kinds_by_family",
        "api_key_setup_quickstart_command_plan_command_names_by_family",
        "api_key_setup_quickstart_command_plan_commands_by_family",
        "api_key_setup_quickstart_command_plan_provider_by_family",
        "api_key_setup_quickstart_command_plan_selected_provider_class_by_family",
        "api_key_setup_quickstart_command_plan_provider_route_data_mode_by_family",
        "api_key_setup_quickstart_command_plan_provider_route_live_data_required_by_family",
        "api_key_setup_quickstart_command_plan_provider_route_family_count",
        "api_key_setup_quickstart_command_plan_selected_provider_family_count",
        "api_key_setup_quickstart_command_plan_provider_route_live_data_required_family_count",
        "api_key_setup_quickstart_command_plan_provider_route_data_mode_counts",
        "api_key_setup_quickstart_command_plan_expected_live_check_count",
        "api_key_setup_quickstart_command_plan_expected_live_check_counts_by_family",
        "api_key_setup_quickstart_command_plan_expected_live_contracts_by_family",
        "api_key_setup_quickstart_command_plan_expected_live_checks_by_family",
        "api_key_setup_quickstart_command_plan_accepted_env_key_count",
        "api_key_setup_quickstart_command_plan_accepted_env_key_counts_by_family",
        "api_key_setup_quickstart_command_plan_preferred_env_key_by_family",
        "api_key_setup_quickstart_command_plan_accepted_env_keys_by_family",
        "api_key_setup_quickstart_command_plan_next_setup_actions_by_family",
        "api_key_setup_quickstart_command_plan_statuses_by_family",
        "api_key_setup_quickstart_command_plan_network_calls_by_family",
        "api_key_setup_quickstart_command_plan_network_call_policies_by_family",
        "api_key_setup_quickstart_command_plan_mutates_local_state_by_family",
        "api_key_setup_quickstart_command_plan_secret_values_returned_by_family",
        "api_key_setup_quickstart_next_command_plan_item",
        "api_key_setup_quickstart_next_command_plan_name",
        "api_key_setup_quickstart_next_command_plan_kind",
        "api_key_setup_quickstart_next_command_plan_command",
        "api_key_setup_quickstart_next_command_plan_has_command",
        "api_key_setup_quickstart_next_command_plan_provider_family",
        "api_key_setup_quickstart_next_command_plan_provider",
        "api_key_setup_quickstart_next_command_plan_selected_provider_class",
        "api_key_setup_quickstart_next_command_plan_provider_route_data_mode",
        "api_key_setup_quickstart_next_command_plan_provider_route_live_data_required",
        "api_key_setup_quickstart_next_command_plan_expected_live_contract",
        "api_key_setup_quickstart_next_command_plan_expected_live_checks",
        "api_key_setup_quickstart_next_command_plan_expected_live_check_count",
        "api_key_setup_quickstart_next_command_plan_preferred_env_key",
        "api_key_setup_quickstart_next_command_plan_accepted_env_keys",
        "api_key_setup_quickstart_next_command_plan_accepted_env_key_count",
        "api_key_setup_quickstart_next_command_plan_next_setup_action",
        "api_key_setup_quickstart_next_command_plan_status",
        "api_key_setup_quickstart_next_command_plan_ready_to_run",
        "api_key_setup_quickstart_next_command_plan_requires_api_keys",
        "api_key_setup_quickstart_next_command_plan_network_call",
        "api_key_setup_quickstart_next_command_plan_network_call_policy",
        "api_key_setup_quickstart_next_command_plan_mutates_local_state",
        "api_key_setup_quickstart_next_command_plan_secret_values_returned",
        "api_key_setup_dotenv_example_lines",
        "api_key_setup_dotenv_example_line_count",
        "api_key_setup_dotenv_example_env_keys",
        "api_key_setup_dotenv_source_path",
        "api_key_setup_dotenv_target_path",
    )

    for field_name in field_names:
        assert field_name in readme
        assert field_name in guide


def test_setup_docs_keep_api_key_provider_requirement_fields_in_sync() -> None:
    readme = README.read_text(encoding="utf-8")
    guide = DEVOPS_GUIDE.read_text(encoding="utf-8")
    field_names = (
        "api_key_requirement_schema_version",
        "api_key_requirement_status",
        "api_key_required_env_keys",
        "api_key_required_env_key_count",
        "api_key_configured_env_keys",
        "api_key_configured_env_key_count",
        "api_key_requirement_configured_provider_families",
        "api_key_requirement_configured_provider_family_count",
        "api_key_requirement_missing_provider_families",
        "api_key_requirement_missing_provider_family_count",
        "api_key_provider_requirement_families",
        "api_key_provider_requirement_count",
        "api_key_requirement_next_missing_provider_family",
        "api_key_requirement_next_missing_provider",
        "api_key_requirement_next_missing_required_env_keys",
        "api_key_requirement_next_missing_required_env_key_count",
        "api_key_requirement_next_missing_configured_env_keys",
        "api_key_requirement_next_missing_configured_env_key_count",
        "api_key_requirement_next_missing_missing_env_keys",
        "api_key_requirement_next_missing_missing_env_key_count",
        "api_key_requirement_next_missing_preferred_env_key",
        "api_key_requirement_next_missing_accepted_env_keys",
        "api_key_requirement_next_missing_accepted_env_key_count",
        "api_key_requirement_next_missing_setup_status",
        "api_key_requirement_next_missing_configured",
        "api_key_requirement_next_missing_next_setup_action",
        "api_key_requirement_next_missing_smoke_command_name",
        "api_key_requirement_next_missing_network_call",
        "api_key_requirement_next_missing_mutates_local_state",
        "api_key_requirement_next_missing_secret_values_returned",
        "api_key_provider_requirement_providers",
        "api_key_provider_requirement_required_env_keys",
        "api_key_provider_requirement_required_env_key_counts",
        "api_key_provider_requirement_configured_env_keys",
        "api_key_provider_requirement_configured_env_key_counts",
        "api_key_provider_requirement_missing_env_keys",
        "api_key_provider_requirement_missing_env_key_counts",
        "api_key_provider_requirement_preferred_env_keys",
        "api_key_provider_requirement_accepted_env_keys",
        "api_key_provider_requirement_accepted_env_key_counts",
        "api_key_provider_requirement_setup_statuses",
        "api_key_provider_requirement_configured",
        "api_key_provider_requirement_next_setup_actions",
        "api_key_provider_requirement_smoke_command_names",
        "api_key_provider_requirement_network_calls",
        "api_key_provider_requirement_mutates_local_state",
        "api_key_provider_requirement_secret_values_returned",
        "api_key_requirement_network_call",
        "api_key_requirement_mutates_local_state",
        "api_key_requirement_secret_values_returned",
        "selected_provider_class_by_family",
        "provider_route_data_mode_by_family",
        "provider_route_live_data_required_by_family",
        "all_selected_routes_live",
        "api_key_requirement_provider_route_family_count",
        "api_key_requirement_selected_provider_family_count",
        "api_key_requirement_provider_route_live_data_required_family_count",
        "api_key_requirement_provider_route_data_mode_counts",
        "api_key_requirement_selected_provider_class_by_family",
        "api_key_requirement_provider_route_data_mode_by_family",
        "api_key_requirement_provider_route_live_data_required_by_family",
        "api_key_requirement_all_selected_routes_live",
    )

    for field_name in field_names:
        assert field_name in readme
        assert field_name in guide


def test_setup_docs_keep_api_key_command_summary_fields_in_sync() -> None:
    readme = README.read_text(encoding="utf-8")
    guide = DEVOPS_GUIDE.read_text(encoding="utf-8")
    field_names = (
        "api_key_command_summary",
        "api_key_pipeline_api_key_command_summary.v1",
        "api_key_copy_dotenv_command",
        "api_key_copy_dotenv_required",
        "api_key_copy_dotenv_command_name",
        "api_key_copy_dotenv_command_network_call",
        "api_key_copy_dotenv_command_mutates_local_state",
        "api_key_copy_dotenv_command_secret_values_returned",
        "api_key_next_smoke_command",
        "api_key_next_smoke_command_name",
        "api_key_next_smoke_command_network_call",
        "api_key_next_smoke_command_network_call_policy",
        "api_key_next_smoke_command_mutates_local_state",
        "api_key_next_smoke_command_secret_values_returned",
        "api_key_one_shot_pipeline_smoke_command",
        "api_key_one_shot_pipeline_smoke_command_name",
        "api_key_one_shot_pipeline_smoke_network_call",
        "api_key_one_shot_pipeline_smoke_network_call_policy",
        "api_key_one_shot_pipeline_smoke_mutates_local_state",
        "api_key_one_shot_pipeline_smoke_secret_values_returned",
        "api_key_provider_smoke_command_count",
        "api_key_provider_smoke_command_names",
        "api_key_provider_smoke_commands_by_family",
        "api_key_provider_smoke_statuses_by_family",
        "api_key_provider_smoke_network_call_policies_by_family",
        "api_key_provider_smoke_expected_live_contracts_by_family",
        "api_key_provider_smoke_expected_live_checks_by_family",
    )

    for field_name in field_names:
        assert field_name in readme
        assert field_name in guide


def test_setup_docs_keep_api_key_setup_file_fields_in_sync() -> None:
    readme = README.read_text(encoding="utf-8")
    guide = DEVOPS_GUIDE.read_text(encoding="utf-8")
    field_names = (
        "api_key_setup_file_summary",
        "api_key_setup_file_summary.v1",
        "source_path",
        "target_path",
        "source_exists",
        "target_exists",
        "copy_required",
        "copy_command",
        "preferred_env_keys",
        "dotenv_examples",
        "configured_provider_families",
        "missing_provider_families",
        "next_setup_step",
        "ready_to_run_live_smoke",
        "api_key_setup_dotenv_source_exists",
        "api_key_setup_dotenv_target_exists",
        "api_key_setup_dotenv_copy_required",
        "api_key_setup_dotenv_copy_command",
        "api_key_setup_dotenv_copy_command_name",
        "api_key_setup_dotenv_copy_command_network_call",
        "api_key_setup_dotenv_copy_command_mutates_local_state",
        "api_key_setup_dotenv_copy_command_secret_values_returned",
        "api_key_setup_dotenv_preferred_env_keys",
        "api_key_setup_dotenv_preferred_env_key_count",
        "api_key_setup_dotenv_configured_provider_families",
        "api_key_setup_dotenv_missing_provider_families",
        "api_key_setup_dotenv_configured_provider_family_count",
        "api_key_setup_dotenv_required_provider_family_count",
        "api_key_setup_dotenv_next_setup_step",
        "api_key_setup_dotenv_ready_to_run_live_smoke",
        "api_key_setup_dotenv_network_call",
        "api_key_setup_dotenv_mutates_local_state",
        "api_key_setup_dotenv_secret_values_returned",
    )

    for field_name in field_names:
        assert field_name in readme
        assert field_name in guide


def test_setup_docs_keep_api_key_live_http_timeout_fields_in_sync() -> None:
    readme = README.read_text(encoding="utf-8")
    guide = DEVOPS_GUIDE.read_text(encoding="utf-8")
    field_names = (
        "api_key_live_http_timeout_summary",
        "api_key_live_http_timeout_summary.v1",
        "timeout_seconds",
        "env_key",
        "default_timeout_seconds",
        "applies_to",
        "api_key_live_http_timeout_seconds",
        "api_key_live_http_timeout_env_key",
        "api_key_live_http_timeout_default_seconds",
        "api_key_live_http_timeout_applies_to",
        "api_key_live_http_timeout_applies_to_count",
        "api_key_live_http_timeout_network_call",
        "api_key_live_http_timeout_mutates_local_state",
        "api_key_live_http_timeout_secret_values_returned",
    )

    for field_name in field_names:
        assert field_name in readme
        assert field_name in guide


def test_setup_docs_keep_api_key_provider_route_summary_fields_in_sync() -> None:
    readme = README.read_text(encoding="utf-8")
    guide = DEVOPS_GUIDE.read_text(encoding="utf-8")
    field_names = (
        "provider_route_summary",
        "api_key_provider_route_summary_schema_version",
        "api_key_provider_route_summary_status",
        "api_key_provider_route_summary_provider_factory",
        "api_key_provider_route_summary_selected_provider_classes",
        "api_key_provider_route_summary_selected_provider_class_count",
        "api_key_provider_route_summary_missing_keys",
        "api_key_provider_route_summary_missing_key_count",
        "api_key_provider_route_summary_network_call",
        "api_key_provider_route_summary_secret_values_returned",
    )

    for field_name in field_names:
        assert field_name in readme
        assert field_name in guide


def test_setup_docs_keep_api_key_dotenv_loading_fields_in_sync() -> None:
    readme = README.read_text(encoding="utf-8")
    guide = DEVOPS_GUIDE.read_text(encoding="utf-8")
    field_names = (
        "api_key_dotenv_loading_summary",
        "api_key_dotenv_loading_summary.v1",
        "dotenv_supported",
        "dotenv_loading_enabled",
        "disabled",
        "disabled_env_key",
        "configuration_precedence",
        "source_path",
        "target_path",
        "source_exists",
        "target_exists",
        "copy_required",
        "next_setup_step",
        "ready_to_run_live_smoke",
        "api_key_dotenv_supported",
        "api_key_dotenv_loading_enabled",
        "api_key_dotenv_disabled",
        "api_key_dotenv_disabled_env_key",
        "api_key_dotenv_configuration_precedence",
        "api_key_dotenv_source_path",
        "api_key_dotenv_target_path",
        "api_key_dotenv_source_exists",
        "api_key_dotenv_target_exists",
        "api_key_dotenv_copy_required",
        "api_key_dotenv_next_setup_step",
        "api_key_dotenv_ready_to_run_live_smoke",
        "api_key_dotenv_network_call",
        "api_key_dotenv_mutates_local_state",
        "api_key_dotenv_secret_values_returned",
    )

    for field_name in field_names:
        assert field_name in readme
        assert field_name in guide


def test_setup_docs_keep_api_key_pipeline_failure_summary_fields_in_sync() -> None:
    readme = README.read_text(encoding="utf-8")
    guide = DEVOPS_GUIDE.read_text(encoding="utf-8")
    field_names = (
        "api_key_pipeline_failure_summary",
        "api_key_pipeline_failure_summary.v1",
        "status",
        "api_key_failure_status",
        "has_failures",
        "failure_category",
        "api_key_has_failures",
        "failed_stage_names",
        "failed_check_keys",
        "tools_with_failures",
        "first_failed_stage_name",
        "first_failed_check_key",
        "next_action_name",
        "next_action_command",
        "next_action_provider_family",
        "next_action_provider",
        "next_action_smoke_command_name",
        "next_action_expected_live_contract",
        "next_action_expected_live_checks",
        "next_action_is_recovery",
        "provider_recovery_required",
        "provider_recovery_item_count",
        "api_key_failure_next_action_name",
        "api_key_failure_next_action_command",
        "api_key_failure_next_action_provider_family",
        "api_key_failure_next_action_provider",
        "api_key_failure_next_action_smoke_command_name",
        "api_key_failure_next_action_expected_live_contract",
        "api_key_failure_next_action_expected_live_checks",
        "api_key_failure_next_action_is_recovery",
        "api_key_failure_provider_recovery_required",
        "api_key_failure_provider_recovery_item_count",
        "api_key_failure_preferred_env_key",
        "api_key_failure_accepted_env_keys",
        "selected_provider_class_by_family",
        "provider_route_data_mode_by_family",
        "provider_route_live_data_required_by_family",
        "all_selected_routes_live",
        "api_key_failure_selected_provider_class_by_family",
        "api_key_failure_provider_route_data_mode_by_family",
        "api_key_failure_provider_route_live_data_required_by_family",
        "api_key_failure_all_selected_routes_live",
        "api_key_failure_provider_route_family_count",
        "api_key_failure_selected_provider_family_count",
        "api_key_failure_provider_route_live_data_required_family_count",
        "api_key_failure_provider_route_data_mode_counts",
        "preferred_env_key",
        "accepted_env_keys",
        "network_call",
        "mutates_local_state",
        "secret_values_returned",
        "api_key_failure_network_call",
        "api_key_failure_mutates_local_state",
        "api_key_failure_secret_values_returned",
    )

    for field_name in field_names:
        assert field_name in readme
        assert field_name in guide


def test_setup_docs_keep_api_key_provider_selection_fields_in_sync() -> None:
    readme = README.read_text(encoding="utf-8")
    guide = DEVOPS_GUIDE.read_text(encoding="utf-8")
    field_names = (
        "api_key_provider_selection_summary",
        "api_key_provider_selection_summary.v1",
        "provider_factory",
        "selected_provider_classes",
        "configured_provider_families",
        "missing_provider_families",
        "configured_env_keys_by_provider_family",
        "provider_env_key_hints_by_family",
        "provider_auto_selects_live_provider_by_family",
        "provider_optional_live_mode_env_by_family",
        "provider_live_mode_required_by_family",
        "all_configured_auto_select_live_provider",
        "any_live_mode_required",
        "selected_provider_by_family",
        "selected_provider_class_by_family",
        "provider_route_data_mode_by_family",
        "provider_route_live_data_required_by_family",
        "all_selected_routes_live",
        "ready_to_run_live_smoke",
        "auto_selects_live_provider",
        "optional_live_mode_env",
        "live_mode_required",
        "preferred_env_key",
        "accepted_env_keys",
        "api_key_provider_selection_status",
        "api_key_provider_factory",
        "api_key_selected_provider_classes",
        "api_key_selected_provider_class_count",
        "api_key_selected_provider_by_family",
        "api_key_selected_provider_class_by_family",
        "api_key_provider_route_data_mode_by_family",
        "api_key_provider_route_live_data_required_by_family",
        "api_key_provider_all_selected_routes_live",
        "api_key_provider_provider_route_family_count",
        "api_key_provider_selected_provider_family_count",
        "api_key_provider_provider_route_live_data_required_family_count",
        "api_key_provider_provider_route_data_mode_counts",
        "api_key_configured_env_keys_by_provider_family",
        "api_key_provider_env_key_hints_by_family",
        "api_key_provider_auto_selects_live_provider_by_family",
        "api_key_provider_optional_live_mode_env_by_family",
        "api_key_provider_live_mode_required_by_family",
        "api_key_provider_all_configured_auto_select_live_provider",
        "api_key_provider_any_live_mode_required",
    )

    for field_name in field_names:
        assert field_name in readme
        assert field_name in guide


def test_setup_docs_keep_api_key_readiness_summary_fields_in_sync() -> None:
    readme = README.read_text(encoding="utf-8")
    guide = DEVOPS_GUIDE.read_text(encoding="utf-8")
    field_names = (
        "readiness_summary",
        "readiness_summary.next_operator_action",
        "next_operator_action",
        "next_operator_action_name",
        "next_operator_action_command",
        "next_operator_action_next_after_action",
        "next_operator_action_dotenv_target_path",
        "next_operator_action_source_path",
        "next_operator_action_target_path",
        "next_operator_action_provider_family",
        "next_operator_action_provider",
        "next_operator_action_selected_provider_class",
        "next_operator_action_provider_route_data_mode",
        "next_operator_action_provider_route_live_data_required",
        "next_operator_action_smoke_command_name",
        "next_operator_action_expected_live_contract",
        "next_operator_action_expected_live_checks",
        "next_operator_action_preferred_env_key",
        "next_operator_action_accepted_env_keys",
        "next_operator_action_required_env_keys",
        "next_operator_action_dotenv_examples",
        "next_operator_action_status",
        "next_operator_action_network_call",
        "next_operator_action_network_call_policy",
        "next_operator_action_mutates_local_state",
        "next_operator_action_secret_input_required",
        "next_operator_action_secret_values_returned",
        "selected_provider_class_by_family",
        "provider_route_data_mode_by_family",
        "provider_route_live_data_required_by_family",
        "all_selected_routes_live",
        "api_key_readiness_selected_provider_class_by_family",
        "api_key_readiness_provider_route_data_mode_by_family",
        "api_key_readiness_provider_route_live_data_required_by_family",
        "api_key_readiness_all_selected_routes_live",
        "api_key_readiness_provider_route_family_count",
        "api_key_readiness_selected_provider_family_count",
        "api_key_readiness_provider_route_live_data_required_family_count",
        "api_key_readiness_provider_route_data_mode_counts",
    )

    for field_name in field_names:
        assert field_name in readme
        assert field_name in guide


def test_setup_docs_keep_api_key_next_operator_action_fields_in_sync() -> None:
    readme = README.read_text(encoding="utf-8")
    guide = DEVOPS_GUIDE.read_text(encoding="utf-8")
    field_names = (
        "next_operator_action_selected_provider_class",
        "next_operator_action_provider_route_data_mode",
        "next_operator_action_provider_route_live_data_required",
        "next_action_selected_provider_class",
        "next_action_provider_route_data_mode",
        "next_action_provider_route_live_data_required",
        "api_key_integration_next_action_selected_provider_class",
        "api_key_integration_next_action_provider_route_data_mode",
        "api_key_integration_next_action_provider_route_live_data_required",
    )

    for field_name in field_names:
        assert field_name in readme
        assert field_name in guide


def test_setup_docs_keep_api_key_integration_recovery_state_fields_in_sync() -> None:
    readme = README.read_text(encoding="utf-8")
    guide = DEVOPS_GUIDE.read_text(encoding="utf-8")
    field_names = (
        "api_key_integration_status_summary",
        "api_key_integration_status_summary.v1",
        "provider_recovery_action_status",
        "provider_recovery_retry_ready",
        "provider_recovery_all_retryable",
        "provider_recovery_has_pending",
        "provider_recovery_has_blocked",
        "provider_recovery_item_count",
        "provider_recovery_pending_count",
        "provider_recovery_blocked_count",
        "provider_error_count",
        "provider_recovery_smoke_count",
    )

    for field_name in field_names:
        assert field_name in readme
        assert field_name in guide


def test_setup_docs_keep_api_key_integration_recovery_identity_fields_in_sync() -> None:
    readme = README.read_text(encoding="utf-8")
    guide = DEVOPS_GUIDE.read_text(encoding="utf-8")
    field_names = (
        "api_key_integration_status_summary",
        "api_key_integration_status_summary.v1",
        "recovery identity lists",
        "provider_recovery_provider_families",
        "provider_recovery_providers",
        "provider_recovery_pending_provider_families",
        "provider_recovery_pending_providers",
        "provider_recovery_blocked_provider_families",
        "provider_recovery_blocked_providers",
    )

    for field_name in field_names:
        assert field_name in readme
        assert field_name in guide


def test_setup_docs_keep_api_key_integration_recovery_command_fields_in_sync() -> None:
    readme = README.read_text(encoding="utf-8")
    guide = DEVOPS_GUIDE.read_text(encoding="utf-8")
    field_names = (
        "api_key_integration_status_summary",
        "api_key_integration_status_summary.v1",
        "recovery command lists",
        "provider_recovery_smoke_command_names",
        "provider_recovery_smoke_commands",
        "provider_recovery_pending_smoke_command_names",
        "provider_recovery_pending_smoke_commands",
        "provider_recovery_blocked_smoke_command_names",
        "provider_recovery_blocked_smoke_commands",
    )

    for field_name in field_names:
        assert field_name in readme
        assert field_name in guide


def test_setup_docs_keep_api_key_integration_next_recovery_item_fields_in_sync() -> None:
    readme = README.read_text(encoding="utf-8")
    guide = DEVOPS_GUIDE.read_text(encoding="utf-8")
    field_names = (
        "api_key_integration_status_summary",
        "api_key_integration_status_summary.v1",
        "next_pending_recovery_smoke_command_name",
        "next_pending_recovery_smoke_command",
        "next_pending_recovery_provider_family",
        "next_pending_recovery_provider",
        "next_pending_recovery_selected_provider_class",
        "next_pending_recovery_provider_route_data_mode",
        "next_pending_recovery_provider_route_live_data_required",
        "next_pending_recovery_next_setup_action",
        "next_pending_recovery_preferred_env_key",
        "next_pending_recovery_accepted_env_keys",
        "next_pending_recovery_network_call_policy",
        "next_pending_recovery_smoke_available",
        "next_pending_recovery_network_call",
        "next_pending_recovery_mutates_local_state",
        "next_pending_recovery_secret_values_returned",
        "next_blocked_recovery_smoke_command_name",
        "next_blocked_recovery_smoke_command",
        "next_blocked_recovery_provider_family",
        "next_blocked_recovery_provider",
        "next_blocked_recovery_selected_provider_class",
        "next_blocked_recovery_provider_route_data_mode",
        "next_blocked_recovery_provider_route_live_data_required",
        "next_blocked_recovery_next_setup_action",
        "next_blocked_recovery_preferred_env_key",
        "next_blocked_recovery_accepted_env_keys",
        "next_blocked_recovery_network_call_policy",
        "next_blocked_recovery_smoke_available",
        "next_blocked_recovery_network_call",
        "next_blocked_recovery_mutates_local_state",
        "next_blocked_recovery_secret_values_returned",
        "next_recovery_smoke_command_name",
        "next_recovery_smoke_command",
        "next_recovery_provider_family",
        "next_recovery_provider",
        "next_recovery_selected_provider_class",
        "next_recovery_provider_route_data_mode",
        "next_recovery_provider_route_live_data_required",
        "next_recovery_smoke_available",
        "next_recovery_next_setup_action",
        "next_recovery_preferred_env_key",
        "next_recovery_accepted_env_keys",
        "next_recovery_network_call_policy",
        "next_recovery_network_call",
        "next_recovery_mutates_local_state",
        "next_recovery_exception_type",
        "next_recovery_exception_message_returned",
        "next_recovery_url_returned",
        "next_recovery_secret_values_returned",
    )

    for field_name in field_names:
        assert field_name in readme
        assert field_name in guide


def test_setup_docs_keep_api_key_operator_checklist_summary_fields_in_sync() -> None:
    readme = README.read_text(encoding="utf-8")
    guide = DEVOPS_GUIDE.read_text(encoding="utf-8")
    field_names = (
        "api_key_operator_checklist_summary",
        "api_key_operator_checklist_summary.v1",
        "api_key_operator_checklist_schema_version",
        "api_key_setup_status",
        "api_key_setup_current_step",
        "api_key_setup_ready",
        "api_key_setup_step_count",
        "api_key_setup_ready_step_names",
        "api_key_setup_ready_step_count",
        "api_key_setup_blocking_step_names",
        "api_key_setup_blocking_step_count",
        "api_key_setup_next_blocking_step",
        "api_key_setup_next_blocking_action_name",
        "api_key_setup_next_blocking_action_status",
        "api_key_setup_next_blocking_action_command",
        "api_key_setup_next_blocking_action_network_call",
        "api_key_setup_next_blocking_action_network_call_policy",
        "api_key_setup_next_blocking_action_mutates_local_state",
        "api_key_setup_next_blocking_action_secret_values_returned",
        "api_key_setup_next_blocking_action_provider_family",
        "api_key_setup_next_blocking_action_provider",
        "api_key_setup_next_blocking_action_smoke_command_name",
        "api_key_setup_next_blocking_action_preferred_env_key",
        "api_key_setup_next_blocking_action_accepted_env_keys",
        "next_blocking_action_name",
        "next_blocking_action_command",
        "next_blocking_action_preferred_env_key",
        "next_blocking_action_provider_family",
        "next_blocking_action_provider",
        "next_blocking_action_smoke_command_name",
        "selected_provider_class_by_family",
        "provider_route_data_mode_by_family",
        "provider_route_live_data_required_by_family",
        "all_selected_routes_live",
        "api_key_operator_checklist_selected_provider_class_by_family",
        "api_key_operator_checklist_provider_route_data_mode_by_family",
        "api_key_operator_checklist_provider_route_live_data_required_by_family",
        "api_key_operator_checklist_all_selected_routes_live",
        "api_key_operator_checklist_provider_route_family_count",
        "api_key_operator_checklist_selected_provider_family_count",
        "api_key_operator_checklist_provider_route_live_data_required_family_count",
        "api_key_operator_checklist_provider_route_data_mode_counts",
        "api_key_operator_checklist_network_call",
        "api_key_operator_checklist_mutates_local_state",
        "api_key_operator_checklist_secret_values_returned",
        "configured_env_keys",
        "missing_provider_families",
        "required_env_keys",
        "network_call_policy",
        "next_provider_smoke_command_name",
        "next_provider_recovery_smoke_command_name",
        "provider_smoke_command_count",
        "recovery_smoke_available",
        "provider_family",
        "provider",
        "smoke_command_name",
        "preferred_env_key",
        "accepted_env_keys",
        "dotenv_examples",
        "dotenv_example_count",
    )

    for field_name in field_names:
        assert field_name in readme
        assert field_name in guide


def test_setup_docs_keep_api_key_next_action_summary_fields_in_sync() -> None:
    readme = README.read_text(encoding="utf-8")
    guide = DEVOPS_GUIDE.read_text(encoding="utf-8")
    field_names = (
        "api_key_next_action_summary",
        "api_key_next_action_summary.v1",
        "status",
        "current_step",
        "ready",
        "blocking_step_count",
        "next_blocking_step",
        "provider_recovery_required",
        "provider_recovery_status",
        "provider_recovery_item_count",
        "next_action_name",
        "next_action_command",
        "next_action_status",
        "next_action_is_recovery",
        "next_action_network_call",
        "next_action_mutates_local_state",
        "next_action_provider_family",
        "next_action_provider",
        "next_action_smoke_command_name",
        "selected_provider_class_by_family",
        "provider_route_data_mode_by_family",
        "provider_route_live_data_required_by_family",
        "all_selected_routes_live",
        "api_key_next_action_selected_provider_class_by_family",
        "api_key_next_action_provider_route_data_mode_by_family",
        "api_key_next_action_provider_route_live_data_required_by_family",
        "api_key_next_action_all_selected_routes_live",
        "api_key_next_action_provider_route_family_count",
        "api_key_next_action_selected_provider_family_count",
        "api_key_next_action_provider_route_live_data_required_family_count",
        "api_key_next_action_provider_route_data_mode_counts",
        "preferred_env_key",
        "accepted_env_keys",
        "required_env_keys",
        "next_after_action",
        "dotenv_target_path",
        "source_path",
        "target_path",
        "secret_input_required",
        "dotenv_examples",
        "dotenv_example_count",
    )

    for field_name in field_names:
        assert field_name in readme
        assert field_name in guide


def test_setup_docs_keep_api_key_next_provider_smoke_fields_in_sync() -> None:
    readme = README.read_text(encoding="utf-8")
    guide = DEVOPS_GUIDE.read_text(encoding="utf-8")
    field_names = (
        "api_key_command_summary",
        "api_key_operator_checklist",
        "setup_status_summary",
        "next_provider_smoke",
        "next_provider_smoke_command_name",
        "api_key_next_provider_smoke_command_name",
        "api_key_next_provider_smoke_provider_family",
        "api_key_next_provider_smoke_provider",
        "api_key_next_provider_smoke_command",
        "api_key_next_provider_smoke_next_setup_action",
        "api_key_next_provider_smoke_status",
        "api_key_next_provider_smoke_network_call",
        "api_key_next_provider_smoke_network_call_policy",
        "api_key_next_provider_smoke_expected_live_contract",
        "api_key_next_provider_smoke_expected_live_checks",
        "api_key_next_provider_smoke_preferred_env_key",
        "api_key_next_provider_smoke_accepted_env_keys",
        "api_key_next_provider_smoke_mutates_local_state",
        "api_key_next_provider_smoke_secret_values_returned",
    )

    for field_name in field_names:
        assert field_name in readme
        assert field_name in guide


def test_setup_docs_keep_api_key_stage_level_setup_fields_in_sync() -> None:
    readme = README.read_text(encoding="utf-8")
    guide = DEVOPS_GUIDE.read_text(encoding="utf-8")
    field_names = (
        "stage-level setup fields",
        "live_data_setup_summary_status",
        "ready_to_run_live_smoke",
        "provider_route_status",
        "provider_family_summary",
        "configured_provider_family_count",
        "missing_provider_families",
        "live_data_setup_steps",
        "next_setup_step",
        "setup_step_count",
        "next_operator_action",
        "provider_setup_actions",
        "provider_setup_action_count",
        "provider_smoke_plan",
        "provider_smoke_count",
        "ready_provider_smoke_count",
        "blocked_provider_smoke_count",
        "next_smoke_command_name",
    )

    for field_name in field_names:
        assert field_name in readme
        assert field_name in guide


def test_setup_docs_keep_api_key_provider_error_recovery_fields_in_sync() -> None:
    readme = README.read_text(encoding="utf-8")
    guide = DEVOPS_GUIDE.read_text(encoding="utf-8")
    field_names = (
        "provider_error_summaries",
        "provider_error_summary_count",
        "failed_provider_families",
        "failed_provider_count",
        "first_provider_error_summary",
        "next_provider_recovery_action",
        "next_provider_recovery_smoke",
        "next_provider_recovery_smoke_command_name",
        "provider_recovery_smokes",
        "provider_recovery_smoke_count",
        "api_key_provider_recovery_checklist",
        "api_key_provider_recovery_checklist.v1",
        "recovery_smoke_command",
        "recovery_smoke_available",
        "error_summary",
        "expected_live_contract",
        "expected_live_checks",
    )

    for field_name in field_names:
        assert field_name in readme
        assert field_name in guide


def test_setup_docs_keep_api_key_provider_recovery_checklist_fields_in_sync() -> None:
    readme = README.read_text(encoding="utf-8")
    guide = DEVOPS_GUIDE.read_text(encoding="utf-8")
    field_names = (
        "api_key_provider_recovery_checklist",
        "api_key_provider_recovery_checklist.v1",
        "recovery_smoke_command",
        "recovery_smoke_available",
        "selected_provider_class_by_family",
        "provider_route_data_mode_by_family",
        "provider_route_live_data_required_by_family",
        "all_selected_routes_live",
        "selected_provider_class",
        "provider_route_data_mode",
        "provider_route_live_data_required",
        "provider_recovery_checklist",
    )

    for field_name in field_names:
        assert field_name in readme
        assert field_name in guide


def test_setup_docs_keep_api_key_provider_recovery_checklist_summary_fields_in_sync() -> None:
    readme = README.read_text(encoding="utf-8")
    guide = DEVOPS_GUIDE.read_text(encoding="utf-8")
    field_names = (
        "api_key_provider_recovery_checklist_summary",
        "api_key_provider_recovery_checklist_summary.v1",
        "provider_error_count",
        "provider_recovery_smoke_count",
        "next_recovery_provider_family",
        "next_recovery_provider",
        "next_recovery_smoke_command_name",
        "next_recovery_smoke_available",
        "next_recovery_network_call",
        "selected_provider_class_by_family",
        "provider_route_data_mode_by_family",
        "provider_route_live_data_required_by_family",
        "all_selected_routes_live",
        "api_key_provider_recovery_checklist_selected_provider_class_by_family",
        "api_key_provider_recovery_checklist_provider_route_data_mode_by_family",
        "api_key_provider_recovery_checklist_provider_route_live_data_required_by_family",
        "api_key_provider_recovery_checklist_all_selected_routes_live",
        "api_key_provider_recovery_checklist_provider_route_family_count",
        "api_key_provider_recovery_checklist_selected_provider_family_count",
        "api_key_provider_recovery_checklist_provider_route_live_data_required_family_count",
        "api_key_provider_recovery_checklist_provider_route_data_mode_counts",
    )

    for field_name in field_names:
        assert field_name in readme
        assert field_name in guide


def test_setup_docs_keep_api_key_provider_recovery_summary_fields_in_sync() -> None:
    readme = README.read_text(encoding="utf-8")
    guide = DEVOPS_GUIDE.read_text(encoding="utf-8")
    field_names = (
        "api_key_provider_recovery_summary",
        "api_key_provider_recovery_summary.v1",
        "provider_error_count",
        "selected_provider_class_by_family",
        "provider_route_data_mode_by_family",
        "provider_route_live_data_required_by_family",
        "all_selected_routes_live",
        "api_key_provider_recovery_selected_provider_class_by_family",
        "api_key_provider_recovery_provider_route_data_mode_by_family",
        "api_key_provider_recovery_provider_route_live_data_required_by_family",
        "api_key_provider_recovery_all_selected_routes_live",
        "api_key_provider_recovery_provider_route_family_count",
        "api_key_provider_recovery_selected_provider_family_count",
        "api_key_provider_recovery_provider_route_live_data_required_family_count",
        "api_key_provider_recovery_provider_route_data_mode_counts",
        "provider_recovery_smoke_available_count",
        "provider_recovery_smoke_unavailable_count",
        "provider_recovery_all_smokes_available",
        "provider_recovery_network_call_count",
        "provider_recovery_all_network_calls",
        "provider_recovery_mutates_local_state_count",
        "provider_recovery_any_mutates_local_state",
        "provider_recovery_secret_values_returned_count",
        "provider_recovery_any_secret_values_returned",
        "provider_recovery_next_setup_actions",
        "provider_recovery_exception_types",
        "provider_recovery_exception_message_returned_count",
        "provider_recovery_any_exception_messages_returned",
        "provider_recovery_url_returned_count",
        "provider_recovery_any_urls_returned",
        "provider_recovery_network_call_policies",
        "provider_recovery_statuses",
        "provider_recovery_preferred_env_keys",
        "provider_recovery_accepted_env_keys",
        "provider_recovery_accepted_env_key_groups",
        "provider_recovery_summary_status",
        "next_recovery_smoke_command_name",
        "next_recovery_smoke_command",
        "next_recovery_provider_family",
        "next_recovery_provider",
        "next_recovery_smoke_available",
        "next_recovery_next_setup_action",
        "next_recovery_preferred_env_key",
        "next_recovery_accepted_env_keys",
        "next_recovery_network_call_policy",
        "next_recovery_network_call",
        "next_recovery_mutates_local_state",
        "next_recovery_exception_type",
        "next_recovery_exception_message_returned",
        "next_recovery_url_returned",
        "next_recovery_secret_values_returned",
    )

    for field_name in field_names:
        assert field_name in readme
        assert field_name in guide


def test_setup_docs_keep_api_key_pipeline_stage_summary_fields_in_sync() -> None:
    readme = README.read_text(encoding="utf-8")
    guide = DEVOPS_GUIDE.read_text(encoding="utf-8")
    field_names = (
        "api_key_pipeline_stage_summary",
        "api_key_pipeline_stage_summary.v1",
        "run_live_data_smoke",
        "run_live_signal_workflow_smoke",
        "run_live_recording_smoke",
        "status",
        "stage_count",
        "failed_stage_count",
        "failed_stage_names",
        "first_failed_stage",
        "selected_provider_class_by_family",
        "provider_route_data_mode_by_family",
        "provider_route_live_data_required_by_family",
        "all_selected_routes_live",
        "api_key_stage_selected_provider_class_by_family",
        "api_key_stage_provider_route_data_mode_by_family",
        "api_key_stage_provider_route_live_data_required_by_family",
        "api_key_stage_all_selected_routes_live",
        "api_key_stage_provider_route_family_count",
        "api_key_stage_selected_provider_family_count",
        "api_key_stage_provider_route_live_data_required_family_count",
        "api_key_stage_provider_route_data_mode_counts",
        "stage_name",
        "failed",
        "error_summary",
        "provider_error_summary_count",
        "provider_recovery_smoke_count",
        "provider_family",
        "provider",
        "smoke_command_name",
        "preferred_env_key",
        "accepted_env_keys",
        "network_call",
        "mutates_local_state",
        "secret_values_returned",
    )

    for field_name in field_names:
        assert field_name in readme
        assert field_name in guide


def test_setup_docs_keep_api_key_pipeline_check_summary_fields_in_sync() -> None:
    readme = README.read_text(encoding="utf-8")
    guide = DEVOPS_GUIDE.read_text(encoding="utf-8")
    field_names = (
        "api_key_pipeline_check_summary",
        "api_key_pipeline_check_summary.v1",
        "check_count",
        "passed_check_count",
        "failed_check_count",
        "failed_check_keys",
        "tools_with_failures",
        "tool_failure_counts",
        "first_failed_check",
        "failed_checks",
        "selected_provider_class_by_family",
        "provider_route_data_mode_by_family",
        "provider_route_live_data_required_by_family",
        "all_selected_routes_live",
        "api_key_check_selected_provider_class_by_family",
        "api_key_check_provider_route_data_mode_by_family",
        "api_key_check_provider_route_live_data_required_by_family",
        "api_key_check_all_selected_routes_live",
        "api_key_check_provider_route_family_count",
        "api_key_check_selected_provider_family_count",
        "api_key_check_provider_route_live_data_required_family_count",
        "api_key_check_provider_route_data_mode_counts",
        "api_key_check_status",
        "api_key_check_count",
        "api_key_check_passed_count",
        "api_key_check_failed_count",
        "api_key_check_failed_keys",
        "api_key_check_tools_with_failures",
        "api_key_check_tool_failure_counts",
        "api_key_check_network_call",
        "api_key_check_mutates_local_state",
        "api_key_check_secret_values_returned",
        "api_key_check_first_failed_tool",
        "api_key_check_first_failed_name",
        "api_key_check_first_failed_key",
        "api_key_check_first_failed_expected",
        "api_key_check_first_failed_actual",
        "api_key_check_first_failed_provider_family",
        "api_key_check_first_failed_provider",
        "api_key_check_first_failed_smoke_command_name",
        "api_key_check_first_failed_preferred_env_key",
        "api_key_check_first_failed_accepted_env_keys",
        "api_key_check_first_failed_secret_values_returned",
        "tool",
        "name",
        "key",
        "expected",
        "actual",
        "passed=false",
        "provider_family",
        "provider",
        "smoke_command_name",
        "preferred_env_key",
        "accepted_env_keys",
        "secret_values_returned",
    )

    for field_name in field_names:
        assert field_name in readme
        assert field_name in guide


def test_setup_docs_describe_hermes_registration_env_flag() -> None:
    text = README.read_text(encoding="utf-8")
    guide = DEVOPS_GUIDE.read_text(encoding="utf-8")

    for document in (text, guide):
        assert "HALO_SWING_HERMES_CONFIG_PATH" in document
        assert "HALO_SWING_HERMES_MCP_CONFIG_REGISTERED=true" in document
        assert "non-secret" in document


def test_setup_docs_describe_binance_passphrase_confirmation_env_flag() -> None:
    text = README.read_text(encoding="utf-8")
    guide = DEVOPS_GUIDE.read_text(encoding="utf-8")

    for document in (text, guide):
        assert "HALO_SWING_BINANCE_PASSPHRASE_CONFIRMED=true" in document
        assert "non-secret" in document
        assert "does not store" in document or "never stores" in document


def test_setup_docs_describe_binance_trade_only_attestation_env_flag() -> None:
    text = README.read_text(encoding="utf-8")
    guide = DEVOPS_GUIDE.read_text(encoding="utf-8")

    for document in (text, guide):
        assert "HALO_SWING_BINANCE_TRADE_ONLY_PERMISSION_ATTESTED=true" in document
        assert "trade-only" in document
        assert "does not enable order submission" in document


def test_setup_docs_describe_binance_live_order_approval_env_flag() -> None:
    text = README.read_text(encoding="utf-8")
    guide = DEVOPS_GUIDE.read_text(encoding="utf-8")

    for document in (text, guide):
        assert "HALO_SWING_BINANCE_LIVE_ORDER_APPROVED=true" in document
        assert "readiness evidence only" in document
        assert "CONFIRM_BTC_BINANCE_COINM_ORDER" in document


def test_setup_docs_describe_all_env_readiness_smoke_boundary() -> None:
    text = _normalized_text(README)
    guide = _normalized_text(DEVOPS_GUIDE)

    for document in (text, guide):
        assert "repo-root `.env`" in document or "repo-root .env" in document
        assert "MIGRATION_GO" in document
        assert "REPOSITORY_GO" in document
        assert "no network call" in document
        assert "no Telegram send" in document
        assert "no order submission" in document


def test_setup_docs_describe_integration_setup_checklist_tool() -> None:
    text = _normalized_text(README)
    guide = _normalized_text(DEVOPS_GUIDE)

    for document in (text, guide):
        assert "get_integration_setup_checklist" in document
        assert "local setup checklist" in document
        assert "non-mutating" in document
        assert "does not write `.env`" in document or "does not write .env" in document
        assert "does not" in document
        assert "return secret values" in document
