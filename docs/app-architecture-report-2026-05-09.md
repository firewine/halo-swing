# Halo Swing App Architecture Report

> Date: 2026-05-09  
> Scope: current worktree architecture snapshot, including offline MVP and audit web viewer changes.  
> Note: this report is an architecture review artifact. The durable SSOT remains `docs/halo-swing-development-plan.md`.

## 1. Executive Summary

Halo Swing is currently shaped as a tool-oriented MCP server for deterministic market swing decision support. The implementation is intentionally not a trading bot and does not include broker integration, automatic orders, live market/news adapters, migrations, or persistent database repositories.

The current architecture is strongest in three areas:

- Reusable boundaries: data fixtures, indicator calculation, strategy config, scoring, recording, audit, MCP transport, and CLI harness are separated.
- Offline repeatability: every default test and smoke path can run without live APIs, secrets, Hermes, or broker access.
- Auditability: CLI and MCP tool calls now produce structured JSONL audit events, with redaction and a local web viewer.

The main architectural gap is persistence maturity. Runtime JSONL files are appropriate for the current offline MVP, but future production use should move signal ledger, audit log, run journal, labels, and strategy config into a durable repository layer only after an explicit storage/migration gate.

## 2. Current Runtime Shape

```text
Hermes Agent / CLI / Tests
        |
        v
src/halo_swing_mcp/server.py       FastMCP tool registration
src/halo_swing_mcp/harness.py      parameterized local CLI runner
        |
        v
Tool Facades
  tools/market.py       market, macro, events, news, chart facade
  tools/scoring.py      scoring, guide, position, feedback facade
  tools/recording.py    signal ledger, labeling, recorded performance facade
  tools/audit_tools.py  audit log read and summary facade
        |
        v
Reusable Core Modules
  fixtures.py      deterministic replay data source
  indicators.py    pure Python indicator engine
  strategy.py      strategy config, validation, hash
  contracts.py     DTO/enums and schema contracts
  audit.py         append-only audit event model, redaction, filters
  audit_web.py     local web UI and JSON APIs for audit logs
```

## 3. Module Responsibilities

| Module | Current Responsibility | Architecture Assessment |
| --- | --- | --- |
| `server.py` | Registers MCP tools and wraps calls with audit events. | Correct transport boundary, but wrappers are verbose and could later be generated from a registry. |
| `harness.py` | Runs any tool from CLI with JSON input and audit logging. | Good reusable test/operator entry point. |
| `fixtures.py` | Supplies deterministic OHLCV, macro, event, and news data. | Good replay source for offline MVP; should become one adapter among live/replay providers later. |
| `indicators.py` | Computes RSI, DMI/ADX, MA, ATR, gaps, support/resistance. | Proper calculation boundary. No Hermes or MCP dependency. |
| `strategy.py` | Owns default config, validation, canonical JSON, config hash. | Good traceability boundary for Champion/Challenger work. |
| `tools/market.py` | Exposes market snapshots, macro, events, news, indicators, chart rendering. | Facade is coherent; chart renderer is dependency-free but should be swappable later. |
| `tools/scoring.py` | Scores leverage swing, builds trade guide, evaluates position, compares configs. | Domain logic is centralized; next improvement is extracting scoring subcomponents into smaller units once rules grow. |
| `tools/recording.py` | JSONL signal ledger, replay-friendly record contents, triple barrier labels. | Good interim runtime adapter. Needs repository abstraction before production persistence. |
| `audit.py` | Append-only audit JSONL, redaction, filtering, summaries. | Good cross-cutting concern. Keeps sensitive value redaction out of tool code. |
| `audit_web.py` | Local web UI plus `/api/events` and `/api/summary`. | Fits local operator visibility. Should stay local-only until auth is designed. |
| `contracts.py` | DTO models and enums. | Stable contract layer for tests and future storage mapping. |

## 4. Primary Data Flows

### 4.1 Swing Guide Flow

```text
CLI/Hermes
  -> score_leverage_swing / generate_trade_guide
  -> resolve asset and underlying
  -> fixture OHLCV + macro + events + news
  -> indicators
  -> component scores
  -> strategy config hash
  -> action, risk summaries, stop/take-profit/invalidation
  -> audit event
```

Key property: leveraged ETF decisions use the underlying symbol as the judgment basis. For example, `TQQQ` routes to `QQQ` indicators.

### 4.2 Signal Record And Label Flow

```text
score_leverage_swing
  -> record_signal
  -> JSONL signal ledger record
       - signal
       - feature_snapshot
       - evidence_cards
       - run_journal
       - config_hash
       - labels
  -> label_signal_outcome
  -> triple barrier outcome, MFE, MAE, realized_R
  -> evaluate_recorded_score_performance
```

Key property: current records preserve enough replay context for offline audit. They are not yet a normalized DB schema.

### 4.3 Audit Flow

```text
harness.py / server.py
  -> append_tool_audit_event
  -> redact_details
  -> append JSONL event
  -> get_audit_log / get_audit_summary
  -> audit_web.py
       - /
       - /api/events
       - /api/summary
```

Key property: likely secret-bearing keys such as `api_key`, `authorization`, `password`, `secret`, and `token` are redacted recursively before persistence.

## 5. Reusable Design Patterns In Use

### 5.1 Facade Over Core Logic

The `tools/` modules are facades. They expose MCP-ready payloads while delegating reusable calculation and configuration work to lower-level modules. This keeps MCP transport, CLI harness, and tests from becoming the owner of domain logic.

### 5.2 Fixture/Replay First

The application defaults to deterministic fixture mode. This supports repeatable tests, safe refactoring, and future live adapter comparison. Live adapters can be added later behind the same tool facades.

### 5.3 Config Hash Traceability

`strategy.py` creates a canonical JSON hash for the active strategy config. Signals carry `config_version` and `config_hash`, which is necessary for replay, label analysis, and Champion/Challenger comparisons.

### 5.4 Append-Only Runtime Logs

Signal ledger and audit log are append-oriented JSONL runtime artifacts. This is simple and inspectable for MVP work. The design should migrate to repository-backed persistence only after storage gates are reopened.

### 5.5 Cross-Cutting Audit Module

Audit logging is implemented as a reusable module rather than embedded ad hoc in every tool. This is the right pattern for future expansion into MCP, scheduler, Telegram, and repository events.

## 6. Quality And Verification Posture

Current verification surface:

- DTO contract tests validate report/replay/storage health models and golden fixtures.
- MVP tool tests validate market, macro, events, news, indicators, scoring, guide, position, ledger, labeling, chart, feedback, and server wrappers.
- Audit tests validate redaction, filtering, summary, harness audit writes, audit tools, and web payloads.
- `ruff` validates style.
- CLI harness validates representative end-to-end execution without Hermes.

Latest recorded verification in `docs/WORKING.md`:

```text
PYTHONPATH=src ./.venv/bin/python -m pytest
  31 passed

PYTHONPATH=src ./.venv/bin/python -m ruff check .
  passed
```

## 7. Boundaries That Should Stay Hard

These boundaries are currently correct and should remain explicit:

- No automatic trading or broker execution in the MVP path.
- No live API calls in default tests.
- No secrets in fixtures, golden files, audit logs, or docs.
- No committed runtime artifacts under `state/`, `artifacts/`, `data/`, or SQLite files.
- No scoring decisions based on chart images alone.
- No strategy promotion from Challenger to Champion without explicit validation and approval.

## 8. Architectural Risks And Gaps

### 8.1 Server Wrapper Duplication

`server.py` repeats a wrapper pattern for every MCP tool. This is acceptable now, but the next growth step should introduce a small tool registry that can power:

- FastMCP registration
- CLI harness command list
- audit metadata
- docs/tool inventory

### 8.2 JSONL Persistence Is MVP-Grade

JSONL is easy to audit locally, but it lacks concurrency controls, indexing, retention, compaction, and transactional integrity. Before live scheduled use, add a repository boundary and storage migration plan.

### 8.3 Audit Log Has No Auth Layer

The web viewer is local-only by default. It should not be exposed beyond `127.0.0.1` until authentication, access control, and retention policy are defined.

### 8.4 Scoring Rules Will Grow

`tools/scoring.py` currently owns component scoring, action selection, risk references, position review, and feedback examples. This is fine for MVP, but once rules expand, split into:

- `engines/scoring_components.py`
- `engines/action_policy.py`
- `engines/risk_references.py`
- `engines/feedback.py`

### 8.5 Runtime Watchdog Is Still A Design Requirement

The project documents require watchdog events and checkpoint discipline for long-running operation. Current implementation has audit logs and ledgers, but not watchdog/checkpoint runtime controls.

## 9. Recommended Next Architecture Steps

1. Create a shared tool registry.
   Use it to remove duplication between `server.py`, `harness.py`, health capabilities, and documentation.

2. Add a provider interface for replay/live data.
   Keep fixtures as `ReplayMarketProvider`; later add live providers behind the same interface with circuit breaker and timeout controls.

3. Extract scoring engine internals when rule count grows.
   Do not over-refactor immediately; split only when the policy surface becomes hard to test in one file.

4. Define persistence repository contracts before migrations.
   Start with repository interfaces for signal ledger, audit events, labels, strategy config, and run journal.

5. Add runtime watchdog and retention controls.
   Track max audit/ledger size, stale runs, repeated errors, and local artifact cleanup.

6. Add architecture tests for boundary rules.
   Examples: no tool imports broker/live adapters, no default tests write repo `state/`, no audit log stores sensitive values.

## 10. App Architect Verdict

The current architecture is appropriate for an offline MVP of a high-risk financial decision-support MCP server. It prioritizes deterministic computation, replayability, auditability, and explicit manual-control boundaries. The system is not production-live yet, but it has the right seams for the next phase: provider adapters, repository persistence, watchdog controls, and Hermes runtime integration.

The most important architectural principle to preserve is this:

```text
MCP tools expose deterministic, auditable decisions.
Hermes explains and schedules.
Storage and live providers remain replaceable adapters.
Automatic execution remains outside the core MVP.
```
