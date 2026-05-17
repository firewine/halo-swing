"""Summary-only API-key command top-level field projection."""

from __future__ import annotations

from typing import Any


__all__ = ("_api_key_command_top_level_fields",)


def _api_key_command_top_level_fields(
    *,
    copy_dotenv_command: dict[str, Any],
    next_smoke_command: dict[str, Any],
    one_shot_pipeline_smoke: dict[str, Any],
) -> dict[str, Any]:
    return {
        "api_key_copy_dotenv_command": copy_dotenv_command.get("command"),
        "api_key_copy_dotenv_required": (
            copy_dotenv_command.get("required") is True
        ),
        "api_key_copy_dotenv_command_name": copy_dotenv_command.get("name"),
        "api_key_copy_dotenv_command_network_call": (
            copy_dotenv_command.get("network_call") is True
        ),
        "api_key_copy_dotenv_command_mutates_local_state": (
            copy_dotenv_command.get("mutates_local_state") is True
        ),
        "api_key_copy_dotenv_command_secret_values_returned": (
            copy_dotenv_command.get("secret_values_returned") is True
        ),
        "api_key_next_smoke_command": next_smoke_command.get("command"),
        "api_key_next_smoke_command_name": next_smoke_command.get("name"),
        "api_key_next_smoke_command_network_call": (
            next_smoke_command.get("network_call") is True
        ),
        "api_key_next_smoke_command_network_call_policy": (
            next_smoke_command.get("network_call_policy")
        ),
        "api_key_next_smoke_command_mutates_local_state": (
            next_smoke_command.get("mutates_local_state") is True
        ),
        "api_key_next_smoke_command_secret_values_returned": (
            next_smoke_command.get("secret_values_returned") is True
        ),
        "api_key_one_shot_pipeline_smoke_command": (
            one_shot_pipeline_smoke.get("command")
        ),
        "api_key_one_shot_pipeline_smoke_command_name": (
            one_shot_pipeline_smoke.get("name")
        ),
        "api_key_one_shot_pipeline_smoke_network_call": (
            one_shot_pipeline_smoke.get("network_call") is True
        ),
        "api_key_one_shot_pipeline_smoke_network_call_policy": (
            one_shot_pipeline_smoke.get("network_call_policy")
        ),
        "api_key_one_shot_pipeline_smoke_mutates_local_state": (
            one_shot_pipeline_smoke.get("mutates_local_state") is True
        ),
        "api_key_one_shot_pipeline_smoke_secret_values_returned": (
            one_shot_pipeline_smoke.get("secret_values_returned") is True
        ),
    }
