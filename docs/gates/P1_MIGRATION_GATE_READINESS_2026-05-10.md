# P1 Migration Gate Readiness

> Date: 2026-05-10
> Gate target: `MIGRATION_GO`
> Status: readiness packet only; `MIGRATION_GO` is not recorded.

## Gate Result

```yaml
call: NO_GO_UNTIL_USER_APPROVAL
gate_id: P1_MIGRATION_GATE_READINESS_2026_05_10
review_tier: S2_medium
mode_after_gate: plan
recommendation: approve or revise the migration policy before any DDL is written
```

## Current Evidence

Implemented and verified before this gate packet:

- DTO contracts and golden fixtures for latest report, replay bundle, and storage health.
- JSONL signal repository contract behind `SignalLedgerRepository`.
- Runtime retention/watchdog JSONL guard.
- Hermes-facing report snapshot harness.
- Optional chart refs and chart/code guard.

Still blocked:

- SQLite migration files.
- DDL, schema runner, DB connection code.
- Repository-backed database persistence.
- Repo `data/`, `state/`, or committed DB artifacts.

## Recommended Migration Decisions

```yaml
id_policy:
  type: text
  rationale: preserve deterministic fixture IDs and portable replay references

timestamp_policy:
  type: utc_iso8601_text
  rationale: aligns with current DTO fixtures, audit events, and run journals

initial_tables:
  - schema_migrations
  - strategy_config
  - run_journal
  - feature_store
  - evidence_card
  - artifact_ref
  - signal_ledger
  - label_store

deferred_tables:
  - watchdog_event
  - state_checkpoint
  - position_journal
```

`watchdog_event` remains deferred even though the local runtime guard exists,
because Stage D has not yet decided whether watchdog events should persist to
DB, JSONL, or both.

## Table Intent

```yaml
schema_migrations:
  purpose: idempotent migration tracking
  key: version

strategy_config:
  purpose: reproduce score weights and thresholds by config_hash
  key: config_hash

run_journal:
  purpose: trace scheduled, user, labeling, and evaluation runs
  key: run_id

feature_store:
  purpose: store code-calculated numeric features at signal time
  key: feature_snapshot_id

evidence_card:
  purpose: store structured text/news/policy/chart evidence summaries
  key: evidence_id

artifact_ref:
  purpose: store portable chart/pdf/news/raw references
  key: artifact_ref_id

signal_ledger:
  purpose: store final action, score, risk guide, and replay links
  key: signal_id

label_store:
  purpose: store one or more post-signal outcome labels
  key: label_id
```

## Required Constraints And Indexes

```yaml
unique_constraints:
  - schema_migrations.version
  - strategy_config.config_hash
  - run_journal.run_id
  - run_journal.idempotency_key when not null
  - feature_store.feature_snapshot_id
  - evidence_card.evidence_id
  - artifact_ref.artifact_ref_id
  - signal_ledger.signal_id
  - label_store.label_id

search_indexes:
  - signal_ledger.created_at
  - signal_ledger.asset
  - signal_ledger.underlying
  - signal_ledger.timeframe
  - signal_ledger.action
  - signal_ledger.config_hash
  - signal_ledger.data_freshness_status
  - feature_store.asset
  - feature_store.underlying
  - feature_store.timeframe
  - run_journal.status
  - label_store.signal_id
  - label_store.outcome
```

Foreign key direction should preserve replay:

```text
signal_ledger.run_id -> run_journal.run_id
signal_ledger.feature_snapshot_id -> feature_store.feature_snapshot_id
signal_ledger.config_hash -> strategy_config.config_hash
label_store.signal_id -> signal_ledger.signal_id
```

Evidence and artifact links may start as JSON arrays of IDs in
`signal_ledger` until the repository gate decides whether join tables are
needed.

## Migration Naming And Idempotency

```yaml
directory: migrations/
name_format: YYYYMMDDHHMM_description.sql
first_candidate: 202605100001_initial_replay_schema.sql
runner_policy:
  - execute inside a transaction where SQLite permits it
  - insert schema_migrations row only after success
  - skip already-applied migration versions
  - fail loudly on checksum mismatch
```

## Required Verification After `MIGRATION_GO`

```bash
PYTHONPATH=src ./.venv/bin/python -m pytest
PYTHONPATH=src ./.venv/bin/python -m ruff check .
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check
```

Migration-specific tests must also prove:

- SQLite database is created only under `tmp_path`.
- No repo `data/`, `state/`, `.sqlite`, or `.sqlite3` artifact is created.
- Migration runner is idempotent.
- `storage_health` reports applied migration count and domain tables.
- Golden DTO fixtures still validate.
- No live API, Hermes runtime, or broker credential is required.

## NO-GO Conditions

- Writing migration files before explicit `MIGRATION_GO`.
- Adding repository-backed DB persistence before `REPOSITORY_GO`.
- Creating DB files under repo `data/` or `state/` during tests.
- Storing absolute local paths in artifact refs.
- Hiding replay links inside opaque JSON with no searchable signal fields.
- Adding live market/news adapters as part of migration work.

## CTO Decision Needed

Approve, revise, or reject these migration defaults:

```yaml
id_policy: text
timestamp_policy: utc_iso8601_text
initial_tables:
  - schema_migrations
  - strategy_config
  - run_journal
  - feature_store
  - evidence_card
  - artifact_ref
  - signal_ledger
  - label_store
label_store_policy: one_signal_to_many_labels
watchdog_event_table: deferred
```
