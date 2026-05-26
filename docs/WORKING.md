# WORKING

```yaml
doc_type: llm_operational_handoff
audience: llm_agents_only
rule: keep_only_current_work_and_next_work
completed_work_ledger: docs/COMPLETED_WORK.md
pre_compaction_completed_ledger: docs/archive/working-ledger-compaction.md
ssot: docs/halo-swing-development-plan.md
ledger_rule:
  - pre-compaction completed work was moved to docs/archive/working-ledger-compaction.md
  - post-compaction completed work is appended to docs/COMPLETED_WORK.md
  - this file keeps only active work, verification, gate state, and next work
```

## current_work

```yaml
mode: implement
status: P1_REPOSITORY_SQLITE_LATEST_REPORT_FILTERED_SOURCE_SELECTED_LABEL_STATUS_GUARD_PASS_DIRECT_STATUS_MIRROR_VERIFIED
gate_id: P1_REPOSITORY_SQLITE_LATEST_REPORT_FILTERED_SOURCE_SELECTED_LABEL_STATUS_GUARD_PASS_DIRECT_STATUS_MIRROR_GATE
review_tier: S1_small

objective: extend SQLite filtered latest report coverage proving selected label status guard pass summary mirrors direct surface status after repository selection

edits:
  allowed:
    - .codex/tasks/current.json
    - docs/WORKING.md
    - docs/codex-task.json
    - docs/COMPLETED_WORK.md
    - docs/halo-swing-development-plan.md
    - tests/test_reporting.py
  blocked_prefixes:
    - src/halo_swing_mcp/broker/
    - src/halo_swing_mcp/live_adapters/
    - migrations/
    - data/
    - artifacts/
    - state/

done_when:
  - SQLite repository-backed latest report timeframe selected label status guard pass summary mirrors direct surface status after repository selection
  - SQLite repository-backed latest report underlying selected label status guard pass summary mirrors direct surface status after repository selection
  - selected label status guard pass aggregate remains aligned with direct per-surface booleans
  - database_path marker, storage markers, and local path component markers remain absent from report and delivery surfaces
  - default no-repository latest report payload and golden snapshot remain unchanged
  - no migrations, live_adapters, broker, Telegram send, Hermes runtime, scheduler, automatic env DB activation, secret output, or repo data/state/artifact files are added
  - verification passes
```

## verification

```yaml
status: passed
required_commands:
  - diff -u .codex/tasks/current.json docs/codex-task.json
  - PYTHONPATH=src ./.venv/bin/python -m json.tool .codex/tasks/current.json
  - PYTHONPATH=src ./.venv/bin/python -m json.tool docs/codex-task.json
  - git diff --check
  - git status --short --branch
  - PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py::test_latest_signal_report_repository_source_filters_by_timeframe tests/test_reporting.py::test_latest_signal_report_repository_source_filters_by_underlying tests/test_reporting.py::test_latest_signal_report_contains_required_report_sections -q
  - PYTHONPATH=src ./.venv/bin/python -m pytest
  - PYTHONPATH=src ./.venv/bin/python -m ruff check .
  - PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check
results:
  - task mirror diff passed
  - current task JSON parsed
  - docs task JSON parsed
  - git diff --check passed
  - focused pytest passed: 3 passed in 1.99s
  - full pytest passed: 935 passed in 47.46s
  - ruff passed
  - health_check passed with status ok
```

## current_gate_state

```yaml
go_recorded:
  - DECISION_LOG_GO
  - DTO_CONTRACT_GO
  - MIGRATION_GO
  - REPOSITORY_GO

still_requires_later_gate:
  - automatic HALO_SWING_DATABASE_URL activation
  - live_adapters expansion
  - broker_order expansion beyond already guarded BTC tooling
  - Telegram send calls
  - Hermes runtime start
  - scheduler_cron execution
  - committed SQLite data_state_artifact files
```

## next_work

```yaml
immediate:
  - choose the next explicit repository_or_report_read_model_slice from SSOT
```
