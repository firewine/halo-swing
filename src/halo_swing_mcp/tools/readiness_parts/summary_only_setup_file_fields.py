# ruff: noqa: F403,F405,F821
"""Summary-only setup-file top-level field projection."""

from __future__ import annotations

from .contract_checks import _optional_mapping
from .context import *
from .live_data_setup import _string_list


__all__ = ("_api_key_setup_file_top_level_fields",)


def _api_key_setup_file_top_level_fields(
    api_key_setup_file_summary: dict[str, Any],
) -> dict[str, Any]:
    copy_command = (
        _optional_mapping(api_key_setup_file_summary.get("copy_command")) or {}
    )
    dotenv_examples = _string_list(
        api_key_setup_file_summary.get("dotenv_examples")
    )
    preferred_env_keys = _string_list(
        api_key_setup_file_summary.get("preferred_env_keys")
    )
    return {
        "api_key_setup_dotenv_example_lines": dotenv_examples,
        "api_key_setup_dotenv_example_line_count": len(dotenv_examples),
        "api_key_setup_dotenv_example_env_keys": preferred_env_keys,
        "api_key_setup_dotenv_source_path": api_key_setup_file_summary.get(
            "source_path"
        ),
        "api_key_setup_dotenv_target_path": api_key_setup_file_summary.get(
            "target_path"
        ),
        "api_key_setup_dotenv_source_exists": (
            api_key_setup_file_summary.get("source_exists") is True
        ),
        "api_key_setup_dotenv_target_exists": (
            api_key_setup_file_summary.get("target_exists") is True
        ),
        "api_key_setup_dotenv_copy_required": (
            api_key_setup_file_summary.get("copy_required") is True
        ),
        "api_key_setup_dotenv_copy_command": copy_command.get("command"),
        "api_key_setup_dotenv_copy_command_name": copy_command.get("name"),
        "api_key_setup_dotenv_copy_command_network_call": (
            copy_command.get("network_call") is True
        ),
        "api_key_setup_dotenv_copy_command_mutates_local_state": (
            copy_command.get("mutates_local_state") is True
        ),
        "api_key_setup_dotenv_copy_command_secret_values_returned": (
            copy_command.get("secret_values_returned") is True
        ),
        "api_key_setup_dotenv_preferred_env_keys": preferred_env_keys,
        "api_key_setup_dotenv_preferred_env_key_count": (
            api_key_setup_file_summary.get("preferred_env_key_count")
        ),
        "api_key_setup_dotenv_configured_provider_families": _string_list(
            api_key_setup_file_summary.get("configured_provider_families")
        ),
        "api_key_setup_dotenv_missing_provider_families": _string_list(
            api_key_setup_file_summary.get("missing_provider_families")
        ),
        "api_key_setup_dotenv_configured_provider_family_count": (
            api_key_setup_file_summary.get("configured_provider_family_count")
        ),
        "api_key_setup_dotenv_required_provider_family_count": (
            api_key_setup_file_summary.get("required_provider_family_count")
        ),
        "api_key_setup_dotenv_next_setup_step": (
            api_key_setup_file_summary.get("next_setup_step")
        ),
        "api_key_setup_dotenv_ready_to_run_live_smoke": (
            api_key_setup_file_summary.get("ready_to_run_live_smoke") is True
        ),
        "api_key_setup_dotenv_network_call": (
            api_key_setup_file_summary.get("network_call") is True
        ),
        "api_key_setup_dotenv_mutates_local_state": (
            api_key_setup_file_summary.get("mutates_local_state") is True
        ),
        "api_key_setup_dotenv_secret_values_returned": (
            api_key_setup_file_summary.get("secret_values_returned") is True
        ),
    }
