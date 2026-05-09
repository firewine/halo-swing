# Full Goal Implementation Plan And Cross Review

> Date: 2026-05-09  
> Mode: staged implementation plan  
> Source of truth: `docs/halo-swing-development-plan.md`  
> Current baseline: offline MVP, audit log, local audit web viewer, 31 passing tests

## 1. Objective

Bring Halo Swing from the current offline MVP toward the full documented product goal while preserving these constraints:

- deterministic offline harness remains the default test path
- no automatic trading without explicit future approval
- no secrets or runtime artifacts committed
- reusable module boundaries stay stronger than one-off implementation
- every phase adds tests, CLI harness coverage, and audit visibility

## 2. Current Gap Summary

Implemented:

- FastMCP server and JSON CLI harness
- fixture-backed market, macro, event, news, indicator, chart tools
- leverage scoring, trade guide, position review
- JSONL signal ledger and triple-barrier labeling
- basic performance and Champion/Challenger comparison
- JSONL audit log, audit tools, local audit web viewer

Not yet implemented:

- shared tool registry
- live/replay provider interface
- SQLite/Postgres migrations and repository persistence
- runtime watchdog/checkpoint/retention controls
- live market/news/macro adapters
- Hermes/Telegram/crons
- multimodal Hermes report integration
- broker/order preview/approval flow

## 3. Team Plans

### FE

Plan:

- Keep report-facing DTOs readable and compact.
- Add audit web UI only for local inspection until auth exists.
- Define future Telegram/report formatter after tool payloads stabilize.
- Avoid dashboard-only schemas before storage/repository gates.

Deliverables:

- report snapshot contract
- audit UI usability checks
- Telegram report format draft after Hermes integration gate

Risks:

- if payloads keep growing without formatter boundary, Hermes-facing output will become noisy

### BE

Plan:

- Introduce shared tool registry first.
- Split provider interfaces before live data adapters.
- Keep scoring/indicator logic transport-independent.
- Add repository interfaces before database migrations.

Deliverables:

- `tool_registry.py`
- provider interfaces for replay/live data
- repository contracts for signal, audit, labels, strategy config, run journal

Risks:

- `server.py` and `harness.py` duplication can drift if registry is delayed
- scoring module can become too broad as rules grow

### DB

Plan:

- Do not write migrations until repository contracts and ID/timestamp policy are fixed.
- Start with SQLite-compatible schema, but keep PostgreSQL portability.
- Preserve replay/audit requirements before dashboard convenience.

Deliverables:

- repository contract review
- migration gate packet
- tmp_path SQLite migration tests after approval

Risks:

- JSONL runtime ledger lacks concurrency, indexing, retention, and transaction guarantees

### AI LLM

Plan:

- Keep LLM out of numeric authority.
- Define Hermes prompt/report contracts only after deterministic tool outputs are stable.
- Add evidence summary limits and conflict flags.

Deliverables:

- Hermes report prompt templates
- chart-vs-code conflict guard
- evidence bundle size limits

Risks:

- overlong evidence can degrade Hermes report quality and increase hallucination risk

### Security

Plan:

- Preserve secret redaction in audit logs.
- Keep audit web viewer local-only until auth exists.
- Add tests for no broker/live API imports in default path.
- For future broker work, require read-only first and approval-required execution.

Deliverables:

- boundary tests
- audit redaction tests
- auth requirement before non-local audit viewer

Risks:

- exposing audit viewer beyond localhost without auth would leak strategy and signal history

### DevOps

Plan:

- Keep all default tests offline.
- Add documented smoke commands for every phase.
- Add retention and supervisor docs before unattended cron.
- Avoid committed `state/`, `artifacts/`, `data/`, DB files, or logs.

Deliverables:

- updated DevOps guide per phase
- retention/watchdog config docs
- Hermes config examples

Risks:

- live adapters without timeout/retry/circuit breaker would make cron unsafe

### QC

Plan:

- Maintain fixture/golden coverage for every tool.
- Add architecture boundary tests.
- Add replay/live separation tests before live adapters.
- Use tmp_path for all persistence tests.

Deliverables:

- tool registry tests
- provider contract tests
- repository contract tests
- retention/watchdog tests

Risks:

- smoke-only live tests cannot substitute deterministic regression tests

### Docs Gardener

Plan:

- Keep SSOT in `halo-swing-development-plan.md`.
- Put gate packets under `docs/gates/`.
- Keep `WORKING.md` as operational state only.
- Avoid duplicating detailed implementation logic in durable docs.

Deliverables:

- phase gate packet updates
- architecture report updates when major structure changes
- DevOps command updates

Risks:

- stale docs can cause agents to reopen blocked scopes incorrectly

### CTO

Plan:

- Proceed in staged gates.
- Start with no-decision foundation: tool registry and boundary tests.
- Require explicit user decisions before live APIs, DB migrations, Hermes/Telegram setup, or broker integration.

Deliverables:

- staged implementation order
- go/no-go decisions per gate
- final completion audit per phase

Risks:

- trying to implement full production scope in one pass would blur live-data, persistence, and execution risks

## 4. Cross Review Results

1. BE -> DevOps/QC:
   Tool registry should come first because it reduces duplication across server, harness, health capabilities, and docs. QC agrees this is testable without external decisions.

2. DB -> CTO:
   Repository interfaces can be planned next, but migrations still need an explicit gate. CTO agrees no DDL until repository contracts are reviewed.

3. Security -> FE/DevOps:
   Audit web viewer must remain `127.0.0.1` by default. Any remote exposure needs auth and is out of current scope.

4. AI LLM -> BE:
   Hermes prompt contracts should depend on stable deterministic outputs, not raw tool internals. BE agrees to keep formatter/prompt layer separate.

5. QC -> All:
   Every future phase needs fixture tests and a CLI harness command. Live smoke can be added later but cannot be the only verification.

6. Docs -> CTO:
   SSOT should record phase outcomes, while detailed implementation plans belong in gate packets. CTO agrees.

## 5. Staged Implementation Order

### Stage A. Foundation Without User Decision

Status: implemented and verified.

Tasks:

1. Add shared tool registry.
2. Refactor `server.py`, `harness.py`, and `health.py` to use registry metadata.
3. Add architecture boundary tests.
4. Update docs and run full verification.

Success criteria:

- no tool capability drift between server, harness, and health
- all existing tools still callable through CLI and server wrappers
- tests pass offline

Implementation record:

- Added `src/halo_swing_mcp/tool_registry.py` as canonical tool metadata and dispatch source.
- Refactored health, CLI harness, and MCP server wrapper bodies to use registry-backed calls.
- Preserved existing public FastMCP wrapper function names and signatures.
- Added registry and architecture boundary tests in `tests/test_tool_registry.py`.

Verification:

```text
PYTHONPATH=src ./.venv/bin/python -m pytest -> 36 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --audit-log-path /private/tmp/halo_swing_registry_verify.jsonl -> passed
```

### Stage B. Provider Interface

Status: replay-only interface implemented and verified.

Tasks:

1. Introduce replay provider interface for market/macro/events/news. Done.
2. Move fixture data behind provider methods. Done.
3. Keep current tool outputs stable. Done.
4. Add provider contract tests. Done.

Implementation record:

- Added `src/halo_swing_mcp/providers.py`.
- Added `MarketDataProvider` protocol and `ReplayMarketDataProvider`.
- Routed market snapshot, macro snapshot, event calendar, news bundle, indicator, and chart data reads through the default replay provider.
- Kept scoring rules and public tool payload contracts unchanged.
- Added provider contract coverage in `tests/test_providers.py`.

Verification:

```text
PYTHONPATH=src ./.venv/bin/python -m pytest -> 38 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_market_snapshot --input-json '{"symbols":["QQQ","TQQQ"]}' --audit-log-path /private/tmp/halo_swing_provider_verify.jsonl -> passed
```

Decision needed before live implementation:

- Which live data source should be used for OHLCV and macro data?
- Which news/feed sources are acceptable?
- Are API keys available, and where should they be configured?

### Stage C. Repository Contract

Status: plan only until user approves storage direction.

Tasks:

1. Define repository interfaces.
2. Keep JSONL adapter as one implementation.
3. Add tmp_path repository contract tests.

Decision needed:

- Use SQLite first, or continue JSONL until Hermes integration?
- Confirm ID policy: text fixture IDs vs UUID/ULID.
- Confirm timestamp policy: UTC ISO-8601 text.

### Stage D. Runtime Watchdog And Retention

Status: implementation can proceed after repository/log retention direction.

Tasks:

1. Add retention limits for audit and signal ledgers.
2. Add watchdog event contract.
3. Add degraded-mode controls for repeated failures.

Decision needed:

- What retention period and max disk size should local audit/signal logs use?

### Stage E. Hermes And Telegram Integration

Status: requires user environment decision.

Tasks:

1. Write Hermes MCP config.
2. Add report prompt templates.
3. Add cron prompt examples.
4. Add Telegram report format.

Decision needed:

- Is Hermes installed/configurable on this machine?
- Should Telegram be configured now, and are credentials available?

### Stage F. Multimodal Report Integration

Status: after Hermes integration.

Tasks:

1. Link chart refs into report payloads.
2. Add chart/code conflict guard.
3. Add report snapshot tests.

Decision needed:

- Which chart artifacts should be included in regular reports?

### Stage G. Broker / Order Preview

Status: blocked by default.

Tasks:

1. Read-only portfolio sync.
2. Order preview only.
3. Approval-required execution only.

Decision needed:

- Explicit approval to enter broker integration scope.
- Broker/exchange choice.
- Read-only API key policy.

## 6. Immediate Next Action

Stage A is complete. Choose the next gate:

```text
Option 1: Stage B replay provider interface.
Option 2: Stage C repository contract.
```

Stage B replay-only implementation does not require live APIs, secrets, DB migrations, Hermes setup, broker setup, or user credentials. Live adapters remain blocked until source/API-key decisions are recorded.
