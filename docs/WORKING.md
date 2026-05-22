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
status: WORKING_LEDGER_COMPACTION_VERIFIED
gate_id: WORKING_LEDGER_COMPACTION_2026_05_22
review_tier: S0_trivial

objective: redefine handoff docs so WORKING.md tracks current and next work only

edits:
  allowed:
    - .codex/tasks/current.json
    - AGENTS.md
    - docs/WORKING.md
    - docs/codex-task.json
    - docs/COMPLETED_WORK.md
    - docs/archive/working-ledger-compaction.md
  blocked_prefixes:
    - src/
    - tests/
    - migrations/
    - data/
    - artifacts/
    - state/

done_when:
  - WORKING.md is LLM-friendly and contains only current_work and next_work
  - completed work has a separate ledger document
  - full pre-compaction WORKING.md ledger is preserved in docs/archive/working-ledger-compaction.md
  - AGENTS.md defines the split between WORKING.md and completed work ledger
  - task mirror files are identical and valid JSON
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
  - wc -l docs/WORKING.md docs/COMPLETED_WORK.md docs/archive/working-ledger-compaction.md
  - git status --short --branch
results:
  - task mirror diff passed
  - current task JSON parsed
  - docs task JSON parsed
  - git diff --check passed
  - docs/WORKING.md reduced to compact current/next handoff
  - docs/COMPLETED_WORK.md created as compact completed work ledger
  - full pre-compaction WORKING.md ledger preserved in docs/archive/working-ledger-compaction.md
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
  - append completed slice summary to docs/COMPLETED_WORK.md

product_backlog_later_gate:
  - Telegram actual send
  - Hermes runtime connection_start
  - scheduler_cron automated execution
  - live adapter expansion
  - env_based_database_activation
  - ETF_order_or_general_broker_automation
```
