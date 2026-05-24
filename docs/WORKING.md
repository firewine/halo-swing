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
status: DOCS_WORKING_LEDGER_COMPACTION_ARCHIVE_INVENTORY_VERIFIED
gate_id: DOCS_WORKING_LEDGER_COMPACTION_ARCHIVE_INVENTORY_GATE
review_tier: S0_trivial

objective: clarify that completed WORKING.md ledger content is preserved in docs/archive/working-ledger-compaction.md and that post-compaction completed slices are tracked in docs/COMPLETED_WORK.md

edits:
  allowed:
    - .codex/tasks/current.json
    - docs/WORKING.md
    - docs/codex-task.json
    - docs/COMPLETED_WORK.md
    - docs/archive/working-ledger-compaction.md
  blocked_prefixes:
    - src/halo_swing_mcp/broker/
    - src/halo_swing_mcp/live_adapters/
    - migrations/
    - data/
    - artifacts/
    - state/

done_when:
  - docs/archive/working-ledger-compaction.md explicitly states completed WORKING.md ledger content was moved there
  - docs/COMPLETED_WORK.md explicitly remains the post-compaction completed-slice ledger
  - docs/WORKING.md explicitly remains current work and next work only
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
  - rg -c "Previous completed directive|Earlier completed directive" docs/archive/working-ledger-compaction.md
  - rg -c "Previous verification result|Latest verification result" docs/archive/working-ledger-compaction.md
  - rg -n "Moved Completed Work Ledger|post-compaction completed slices" docs/archive/working-ledger-compaction.md docs/COMPLETED_WORK.md docs/WORKING.md
results:
  - task mirror diff passed
  - current task JSON parsed
  - docs task JSON parsed
  - git diff --check passed
  - git status showed expected docs/task files only
  - archive completed directive markers preserved: 416
  - archive verification result markers preserved: 258
  - archive and compact ledger routing markers found
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
  - commit and push the docs correction
  - resume the next explicit repository_or_report_read_model_slice from SSOT
```
