# P1 Repository GO Record - 2026-05-20

## Decision

```text
status: GO
gate_id: P1_REPOSITORY_GO_SQLITE_SIGNAL_REPOSITORY_GATE
approval_source: user message "REPOSITORY_GO 승인"
source_context:
  - docs/halo-swing-development-plan.md#3.5
  - docs/halo-swing-development-plan.md#4.057
  - migrations/202605100001_initial_replay_schema.sql
```

## Approved Slice

```text
allowed:
  - explicit database_path SQLite signal repository
  - repository-backed record_signal path
  - repository-backed label_signal_outcome path
  - repository-backed evaluate_score_performance path
  - get_signal_replay_bundle replay query
  - tmp_path-only SQLite repository tests
  - storage health verification against migrated domain tables

still_blocked:
  - live_adapters
  - broker/order execution
  - Hermes runtime, Telegram send, scheduler, or cron runner
  - committed repo data/state/artifact DB files
  - automatic .env mutation or secret value output
```

## Verification Contract

```text
required:
  - task contract mirror stays identical
  - JSON task contracts parse
  - git diff has no whitespace errors
  - SQLite repository path records exactly one signal under tmp_path
  - duplicate record_signal remains idempotent
  - label_signal_outcome writes label_store row
  - evaluate_score_performance reads repository labels
  - get_signal_replay_bundle returns linked signal, feature, evidence, strategy config, run journal, latest label, and structured missing links
  - default JSONL behavior remains unchanged
  - sqlite3 default import is allowed only for storage_migrations.py and signal_repository.py
  - full pytest, ruff, and health_check pass
```
