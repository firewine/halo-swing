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
    assert "provider_smoke_count" in guide
    assert "ready_provider_smoke_count" in guide
    assert "blocked_provider_smoke_count" in guide
    assert "next_provider_smoke" in guide
    assert "next_provider_smoke_command_name" in guide
    assert "provider_error_summaries" in guide
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
    assert "api_key_setup_file_summary" in guide
    assert "api_key_setup_file_summary.v1" in guide
    assert "source_exists" in guide
    assert "target_exists" in guide
    assert "copy_required" in guide
    assert "preferred_env_keys" in guide
    assert "readiness_summary.next_operator_action" in guide
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
