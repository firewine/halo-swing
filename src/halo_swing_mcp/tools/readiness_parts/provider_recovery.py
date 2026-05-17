# ruff: noqa: F403,F405,F821
"""Provider Recovery readiness implementation."""

from __future__ import annotations

from .api_key_route_family_fields import _api_key_route_family_fields
from .context import *


__all__ = ('_api_key_provider_recovery_summary', '_api_key_provider_recovery_summary_item', '_api_key_pipeline_summary_only_checks')


def _api_key_provider_recovery_summary(
    recovery_checklist: dict[str, Any],
    *,
    route_family_summary: dict[str, Any] | None = None,
) -> dict[str, Any]:
    raw_items = recovery_checklist.get("items")
    items = (
        [item for item in raw_items if isinstance(item, dict)]
        if isinstance(raw_items, list)
        else []
    )
    compact_items = [_api_key_provider_recovery_summary_item(item) for item in items]
    first_item = compact_items[0] if compact_items else None
    smoke_available_count = sum(
        1 for item in compact_items if item.get("recovery_smoke_available") is True
    )
    network_call_count = sum(
        1 for item in compact_items if item.get("network_call") is True
    )
    mutates_local_state_count = sum(
        1 for item in compact_items if item.get("mutates_local_state") is True
    )
    secret_values_returned_count = sum(
        1 for item in compact_items if item.get("secret_values_returned") is True
    )
    exception_message_returned_count = sum(
        1 for item in compact_items if item.get("exception_message_returned") is True
    )
    url_returned_count = sum(
        1 for item in compact_items if item.get("url_returned") is True
    )
    recovery_pending_count = sum(
        1 for item in compact_items if item.get("recovery_status") == "pending"
    )
    recovery_blocked_count = sum(
        1 for item in compact_items if item.get("recovery_status") == "blocked"
    )
    provider_recovery_has_pending = recovery_pending_count > 0
    provider_recovery_has_blocked = recovery_blocked_count > 0
    if not compact_items:
        provider_recovery_action_status = "no_recovery_required"
    elif provider_recovery_has_pending and provider_recovery_has_blocked:
        provider_recovery_action_status = "partially_retryable"
    elif provider_recovery_has_pending:
        provider_recovery_action_status = "ready_to_retry"
    else:
        provider_recovery_action_status = "blocked"
    first_pending_item = next(
        (
            item
            for item in compact_items
            if item.get("recovery_status") == "pending"
        ),
        None,
    )
    first_blocked_item = next(
        (
            item
            for item in compact_items
            if item.get("recovery_status") == "blocked"
        ),
        None,
    )
    summary = {
        "schema_version": "api_key_provider_recovery_summary.v1",
        "status": recovery_checklist.get("status", "ok"),
        "provider_recovery_required": bool(compact_items),
        "provider_error_count": recovery_checklist.get("provider_error_count", 0),
        "provider_recovery_smoke_count": recovery_checklist.get(
            "provider_recovery_smoke_count",
            0,
        ),
        "provider_recovery_smoke_available_count": smoke_available_count,
        "provider_recovery_smoke_unavailable_count": (
            len(compact_items) - smoke_available_count
        ),
        "provider_recovery_all_smokes_available": (
            bool(compact_items) and smoke_available_count == len(compact_items)
        ),
        "provider_recovery_network_call_count": network_call_count,
        "provider_recovery_all_network_calls": (
            bool(compact_items) and network_call_count == len(compact_items)
        ),
        "provider_recovery_mutates_local_state_count": mutates_local_state_count,
        "provider_recovery_any_mutates_local_state": mutates_local_state_count > 0,
        "provider_recovery_secret_values_returned_count": (
            secret_values_returned_count
        ),
        "provider_recovery_any_secret_values_returned": (
            secret_values_returned_count > 0
        ),
        "provider_recovery_next_setup_actions": _ordered_unique_strings(
            [item.get("next_setup_action") for item in compact_items]
        ),
        "provider_recovery_exception_types": _ordered_unique_strings(
            [item.get("exception_type") for item in compact_items]
        ),
        "provider_recovery_exception_message_returned_count": (
            exception_message_returned_count
        ),
        "provider_recovery_any_exception_messages_returned": (
            exception_message_returned_count > 0
        ),
        "provider_recovery_url_returned_count": url_returned_count,
        "provider_recovery_any_urls_returned": url_returned_count > 0,
        "provider_recovery_network_call_policies": _ordered_unique_strings(
            [item.get("network_call_policy") for item in compact_items]
        ),
        "provider_recovery_statuses": _ordered_unique_strings(
            [item.get("recovery_status") for item in compact_items]
        ),
        "provider_recovery_pending_count": recovery_pending_count,
        "provider_recovery_blocked_count": recovery_blocked_count,
        "provider_recovery_has_pending": provider_recovery_has_pending,
        "provider_recovery_has_blocked": provider_recovery_has_blocked,
        "provider_recovery_retry_ready": provider_recovery_has_pending,
        "provider_recovery_all_retryable": (
            bool(compact_items) and not provider_recovery_has_blocked
        ),
        "provider_recovery_action_status": provider_recovery_action_status,
        "provider_recovery_all_pending": (
            bool(compact_items) and recovery_pending_count == len(compact_items)
        ),
        "provider_recovery_pending_provider_families": _ordered_unique_strings(
            [
                item.get("provider_family")
                for item in compact_items
                if item.get("recovery_status") == "pending"
            ]
        ),
        "provider_recovery_blocked_provider_families": _ordered_unique_strings(
            [
                item.get("provider_family")
                for item in compact_items
                if item.get("recovery_status") == "blocked"
            ]
        ),
        "provider_recovery_pending_providers": _ordered_unique_strings(
            [
                item.get("provider")
                for item in compact_items
                if item.get("recovery_status") == "pending"
            ]
        ),
        "provider_recovery_blocked_providers": _ordered_unique_strings(
            [
                item.get("provider")
                for item in compact_items
                if item.get("recovery_status") == "blocked"
            ]
        ),
        "provider_recovery_pending_smoke_command_names": _ordered_unique_strings(
            [
                item.get("smoke_command_name")
                for item in compact_items
                if item.get("recovery_status") == "pending"
            ]
        ),
        "provider_recovery_pending_smoke_commands": _string_list(
            [
                item.get("recovery_smoke_command")
                for item in compact_items
                if item.get("recovery_status") == "pending"
            ]
        ),
        "provider_recovery_blocked_smoke_command_names": _ordered_unique_strings(
            [
                item.get("smoke_command_name")
                for item in compact_items
                if item.get("recovery_status") == "blocked"
            ]
        ),
        "provider_recovery_blocked_smoke_commands": _string_list(
            [
                item.get("recovery_smoke_command")
                for item in compact_items
                if item.get("recovery_status") == "blocked"
            ]
        ),
        "provider_recovery_provider_families": _ordered_unique_strings(
            [item.get("provider_family") for item in compact_items]
        ),
        "provider_recovery_providers": _ordered_unique_strings(
            [item.get("provider") for item in compact_items]
        ),
        "provider_recovery_smoke_command_names": _ordered_unique_strings(
            [item.get("smoke_command_name") for item in compact_items]
        ),
        "provider_recovery_smoke_commands": _string_list(
            [item.get("recovery_smoke_command") for item in compact_items]
        ),
        "provider_recovery_preferred_env_keys": _ordered_unique_strings(
            [item.get("preferred_env_key") for item in compact_items]
        ),
        "provider_recovery_accepted_env_keys": _ordered_unique_strings(
            [
                env_key
                for item in compact_items
                for env_key in _string_list(item.get("accepted_env_keys"))
            ]
        ),
        "provider_recovery_accepted_env_key_groups": [
            accepted_env_keys
            for accepted_env_keys in (
                _string_list(item.get("accepted_env_keys")) for item in compact_items
            )
            if accepted_env_keys
        ],
        "item_count": len(compact_items),
        "next_pending_recovery_smoke_command_name": (
            first_pending_item.get("smoke_command_name")
            if first_pending_item
            else None
        ),
        "next_pending_recovery_smoke_command": (
            first_pending_item.get("recovery_smoke_command")
            if first_pending_item
            else None
        ),
        "next_pending_recovery_provider_family": (
            first_pending_item.get("provider_family")
            if first_pending_item
            else None
        ),
        "next_pending_recovery_provider": (
            first_pending_item.get("provider") if first_pending_item else None
        ),
        "next_pending_recovery_selected_provider_class": (
            first_pending_item.get("selected_provider_class")
            if first_pending_item
            else None
        ),
        "next_pending_recovery_provider_route_data_mode": (
            first_pending_item.get("provider_route_data_mode")
            if first_pending_item
            else None
        ),
        "next_pending_recovery_provider_route_live_data_required": (
            first_pending_item.get("provider_route_live_data_required") is True
            if first_pending_item
            else False
        ),
        "next_pending_recovery_next_setup_action": (
            first_pending_item.get("next_setup_action")
            if first_pending_item
            else None
        ),
        "next_pending_recovery_preferred_env_key": (
            first_pending_item.get("preferred_env_key")
            if first_pending_item
            else None
        ),
        "next_pending_recovery_accepted_env_keys": (
            _string_list(first_pending_item.get("accepted_env_keys"))
            if first_pending_item
            else []
        ),
        "next_pending_recovery_network_call_policy": (
            first_pending_item.get("network_call_policy")
            if first_pending_item
            else None
        ),
        "next_pending_recovery_smoke_available": first_pending_item is not None,
        "next_pending_recovery_network_call": (
            isinstance(first_pending_item.get("recovery_smoke_command"), str)
            if first_pending_item
            else False
        ),
        "next_pending_recovery_mutates_local_state": (
            first_pending_item.get("mutates_local_state") is True
            if first_pending_item
            else False
        ),
        "next_pending_recovery_secret_values_returned": False,
        "next_blocked_recovery_smoke_command_name": (
            first_blocked_item.get("smoke_command_name")
            if first_blocked_item
            else None
        ),
        "next_blocked_recovery_smoke_command": (
            first_blocked_item.get("recovery_smoke_command")
            if first_blocked_item
            else None
        ),
        "next_blocked_recovery_provider_family": (
            first_blocked_item.get("provider_family")
            if first_blocked_item
            else None
        ),
        "next_blocked_recovery_provider": (
            first_blocked_item.get("provider") if first_blocked_item else None
        ),
        "next_blocked_recovery_selected_provider_class": (
            first_blocked_item.get("selected_provider_class")
            if first_blocked_item
            else None
        ),
        "next_blocked_recovery_provider_route_data_mode": (
            first_blocked_item.get("provider_route_data_mode")
            if first_blocked_item
            else None
        ),
        "next_blocked_recovery_provider_route_live_data_required": (
            first_blocked_item.get("provider_route_live_data_required") is True
            if first_blocked_item
            else False
        ),
        "next_blocked_recovery_next_setup_action": (
            first_blocked_item.get("next_setup_action")
            if first_blocked_item
            else None
        ),
        "next_blocked_recovery_preferred_env_key": (
            first_blocked_item.get("preferred_env_key")
            if first_blocked_item
            else None
        ),
        "next_blocked_recovery_accepted_env_keys": (
            _string_list(first_blocked_item.get("accepted_env_keys"))
            if first_blocked_item
            else []
        ),
        "next_blocked_recovery_network_call_policy": (
            first_blocked_item.get("network_call_policy")
            if first_blocked_item
            else None
        ),
        "next_blocked_recovery_smoke_available": False,
        "next_blocked_recovery_network_call": (
            isinstance(first_blocked_item.get("recovery_smoke_command"), str)
            if first_blocked_item
            else False
        ),
        "next_blocked_recovery_mutates_local_state": (
            first_blocked_item.get("mutates_local_state") is True
            if first_blocked_item
            else False
        ),
        "next_blocked_recovery_secret_values_returned": False,
        "next_recovery_smoke_command_name": (
            first_item.get("smoke_command_name") if first_item else None
        ),
        "next_recovery_selected_provider_class": (
            first_item.get("selected_provider_class") if first_item else None
        ),
        "next_recovery_provider_route_data_mode": (
            first_item.get("provider_route_data_mode") if first_item else None
        ),
        "next_recovery_provider_route_live_data_required": (
            first_item.get("provider_route_live_data_required") is True
            if first_item
            else False
        ),
        "next_recovery_smoke_command": (
            first_item.get("recovery_smoke_command") if first_item else None
        ),
        "items": compact_items,
        "network_call": False,
        "mutates_local_state": False,
        "secret_values_returned": False,
    }
    summary.update(_api_key_route_family_fields(route_family_summary or {}))
    if first_item:
        provider_family = first_item.get("provider_family")
        provider = first_item.get("provider")
        preferred_env_key = first_item.get("preferred_env_key")
        accepted_env_keys = _string_list(first_item.get("accepted_env_keys"))
        network_call_policy = first_item.get("network_call_policy")
        next_recovery_command = first_item.get("recovery_smoke_command")
        next_setup_action = first_item.get("next_setup_action")
        selected_provider_class = first_item.get("selected_provider_class")
        provider_route_data_mode = first_item.get("provider_route_data_mode")
        if isinstance(provider_family, str):
            summary["next_recovery_provider_family"] = provider_family
        if isinstance(provider, str):
            summary["next_recovery_provider"] = provider
        if isinstance(selected_provider_class, str):
            summary["next_recovery_selected_provider_class"] = (
                selected_provider_class
            )
        if isinstance(provider_route_data_mode, str):
            summary["next_recovery_provider_route_data_mode"] = (
                provider_route_data_mode
            )
        summary["next_recovery_provider_route_live_data_required"] = (
            first_item.get("provider_route_live_data_required") is True
        )
        summary["next_recovery_smoke_available"] = (
            first_item.get("recovery_smoke_available") is True
        )
        if isinstance(next_setup_action, str):
            summary["next_recovery_next_setup_action"] = next_setup_action
        if isinstance(preferred_env_key, str):
            summary["next_recovery_preferred_env_key"] = preferred_env_key
        if accepted_env_keys:
            summary["next_recovery_accepted_env_keys"] = accepted_env_keys
        if isinstance(network_call_policy, str):
            summary["next_recovery_network_call_policy"] = network_call_policy
        summary["next_recovery_network_call"] = isinstance(
            next_recovery_command,
            str,
        )
        summary["next_recovery_mutates_local_state"] = (
            first_item.get("mutates_local_state") is True
        )
        exception_type = first_item.get("exception_type")
        if isinstance(exception_type, str):
            summary["next_recovery_exception_type"] = exception_type
        summary["next_recovery_exception_message_returned"] = (
            first_item.get("exception_message_returned") is True
        )
        summary["next_recovery_url_returned"] = first_item.get("url_returned") is True
        summary["next_recovery_secret_values_returned"] = False
    return summary


def _api_key_provider_recovery_summary_item(
    item: dict[str, Any],
) -> dict[str, Any]:
    recovery_smoke = _optional_mapping(item.get("recovery_smoke")) or {}
    recovery_smoke_available = item.get("recovery_smoke_available") is True
    summary = {
        "provider_family": item.get("provider_family"),
        "provider": item.get("provider"),
        "smoke_command_name": item.get("smoke_command_name"),
        "selected_provider_class": item.get("selected_provider_class"),
        "provider_route_data_mode": item.get("provider_route_data_mode"),
        "provider_route_live_data_required": (
            item.get("provider_route_live_data_required") is True
        ),
        "recovery_smoke_command": item.get("recovery_smoke_command"),
        "recovery_smoke_available": recovery_smoke_available,
        "recovery_status": "pending" if recovery_smoke_available else "blocked",
        "next_setup_action": item.get("next_setup_action"),
        "preferred_env_key": item.get("preferred_env_key"),
        "accepted_env_keys": _string_list(item.get("accepted_env_keys")),
        "network_call": isinstance(item.get("recovery_smoke_command"), str),
        "mutates_local_state": recovery_smoke.get("mutates_local_state") is True,
        "exception_type": item.get("exception_type"),
        "exception_message_returned": item.get("exception_message_returned") is True,
        "url_returned": item.get("url_returned") is True,
        "secret_values_returned": False,
    }
    network_call_policy = recovery_smoke.get("network_call_policy")
    if isinstance(network_call_policy, str):
        summary["network_call_policy"] = network_call_policy
    return summary


def _api_key_pipeline_summary_only_checks(raw_checks: Any) -> list[dict[str, Any]]:
    checks = raw_checks if isinstance(raw_checks, list) else []
    return [
        {
            "tool": check.get("tool"),
            "name": check.get("name"),
            "passed": check.get("passed") is True,
            "secret_values_returned": False,
        }
        for check in checks
        if isinstance(check, dict)
    ]
