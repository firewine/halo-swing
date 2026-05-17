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
    assert "summary-only provider smoke contract/check aggregates" in guide
    assert "provider_smoke_success_expected_live_contracts" in guide
    assert "provider_smoke_success_expected_live_checks" in guide
    assert "provider_smoke_success_check_count" in guide
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
    assert "next_operator_action_smoke_command_name" in guide
    assert "next_operator_action_expected_live_contract" in guide
    assert "next_operator_action_expected_live_checks" in guide
    assert (
        "readiness_summary` mirrors provider smoke or recovery "
        "`preferred_env_key`"
    ) in guide
    assert "next_operator_action_preferred_env_key" in guide
    assert "next_operator_action_accepted_env_keys" in guide
    assert "next_operator_action_status" in guide
    assert "next_operator_action_network_call" in guide
    assert "next_operator_action_network_call_policy" in guide
    assert "next_operator_action_mutates_local_state" in guide
    assert "next_operator_action_secret_values_returned" in guide
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
    assert "keeps `live_data_setup_summary`" in guide
    assert "live_data_setup_summary.v1" in guide
    assert "provider smoke plan" in guide
    assert "Provider smoke plan rows include `network_call`" in guide
    assert "keeps `api_key_requirements_summary`" in guide
    assert "api_key_pipeline_api_key_requirements_summary.v1" in guide
    assert "required_env_keys" in guide
    assert "accepted_env_keys" in guide
    assert "provider_requirements" in guide
    assert "keeps `api_key_command_summary`" in guide
    assert "api_key_pipeline_api_key_command_summary.v1" in guide
    assert "provider_smoke_commands" in guide
    assert "Provider smoke rows include `network_call`" in guide
    assert "expected_live_contract" in guide
    assert "expected_live_checks" in guide
    assert "expected live\ncontract/checks" in guide
    assert "one_shot_pipeline_smoke" in guide
    assert "next_provider_smoke_command_name" in guide
    assert "accepted API-key aliases" in guide
    assert "next_blocking_action_preferred_env_key" in guide
    assert "keeps `api_key_setup_file_summary`" in guide
    assert "api_key_setup_file_summary.v1" in guide
    assert "preferred_env_keys" in guide
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
