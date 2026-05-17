"""Offline integration readiness checks for blocked deployment gates."""

from __future__ import annotations

import sys
import types

from .readiness_parts import (
    public_tools as _public_tools,
    api_key_pipeline_runner as _api_key_pipeline_runner,
    live_smoke_contracts as _live_smoke_contracts,
    api_key_pipeline_summaries as _api_key_pipeline_summaries,
    summary_only_context as _summary_only_context,
    summary_only_payload as _summary_only_payload,
    provider_recovery as _provider_recovery,
    setup_file_integration as _setup_file_integration,
    command_checklists as _command_checklists,
    live_data_setup as _live_data_setup,
    contract_checks as _contract_checks,
    provider_commands as _provider_commands,
    readiness_gates as _readiness_gates,
)
from .readiness_parts import context as _context
from .readiness_parts.context import *  # noqa: F403,F405

_IMPLEMENTATION_MODULES = (
    _public_tools,
    _api_key_pipeline_runner,
    _live_smoke_contracts,
    _api_key_pipeline_summaries,
    _summary_only_context,
    _summary_only_payload,
    _provider_recovery,
    _setup_file_integration,
    _command_checklists,
    _live_data_setup,
    _contract_checks,
    _provider_commands,
    _readiness_gates,
)
_PATCH_MODULES = (_context, *_IMPLEMENTATION_MODULES)

for _module in _IMPLEMENTATION_MODULES:
    for _name in getattr(_module, "__all__", ()):
        globals()[_name] = getattr(_module, _name)

_READINESS_EXPORTS = {
    _name: globals()[_name]
    for _module in _IMPLEMENTATION_MODULES
    for _name in getattr(_module, "__all__", ())
}

for _module in _IMPLEMENTATION_MODULES:
    _module.__dict__.update(_READINESS_EXPORTS)


class _ReadinessFacade(types.ModuleType):
    def __setattr__(self, name: str, value: object) -> None:
        super().__setattr__(name, value)
        for module in _PATCH_MODULES:
            module.__dict__[name] = value


sys.modules[__name__].__class__ = _ReadinessFacade

__all__ = tuple(_READINESS_EXPORTS)
