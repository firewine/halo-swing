# WORKING

```yaml
doc_type: llm_operational_handoff
audience: llm_agents_only
rule: keep_only_current_work_and_next_work
completed_work_ledger: docs/COMPLETED_WORK.md
ssot: docs/halo-swing-development-plan.md
```

## current_work

```yaml
mode: implement
status: P1_REPOSITORY_SQLITE_LATEST_REPORT_FILTERED_SOURCE_SOURCE_REPOSITORY_REF_GUARD_PASS_CHECK_ORDER_VERIFIED
gate_id: P1_REPOSITORY_SQLITE_LATEST_REPORT_FILTERED_SOURCE_SOURCE_REPOSITORY_REF_GUARD_PASS_CHECK_ORDER_GATE
review_tier: S1_small

objective: extend SQLite filtered latest report coverage proving source repository ref guard pass check order after repository selection

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
  - SQLite repository-backed latest report timeframe source repository ref guard pass check order is verified after repository selection
  - SQLite repository-backed latest report underlying source repository ref guard pass check order is verified after repository selection
  - source repository ref guard pass checks preserve filtered report check order after repository selection
  - database_path marker remains absent from report and delivery surfaces
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
  - git status showed expected modified task/docs/test files only
  - focused pytest passed: 3 passed in 1.35s
  - full pytest passed: 935 passed in 43.03s
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
  - update .codex/tasks/current.json and docs/codex-task.json for that slice
  - replace this current_work block with the new active task
```
