# LLM Working State

> Purpose: compact handoff state for the next LLM/Codex session.
> Human-facing narrative belongs in `CONTEXT.md`; detailed scope belongs in the SSOT plan.
> Update rule: keep this file short, concrete, and action-oriented.

## Read First

1. `docs/CONTEXT.md`
2. `docs/WORKING.md`
3. `docs/halo-swing-development-plan.md` only for the section relevant to the current task

## SSOT

- Development plan and architecture SSOT: `docs/halo-swing-development-plan.md`
- Do not create project docs outside `docs/`.
- Do not duplicate the full architecture here.

## Project Snapshot

```yaml
project: Halo Swing
repo: firewine/halo-swing
local_root: /Users/june/Documents/New project 2
current_branch: main
product_type: Hermes Agent MCP server
primary_goal: swing decision support for BTC and 2x/3x long index products
mvp_scope: guide/report only, no automatic trading
docs_ssot: docs/halo-swing-development-plan.md
```

## Current State

```yaml
status: p0_closed
last_completed:
  - GitHub repo created and pushed
  - development plan moved to docs as SSOT
  - CONTEXT.md created
  - WORKING.md converted to LLM handoff format
  - harness engineering and virtual team gates documented
  - DevOps virtual team gate added
  - .venv created with Python 3.11.14
  - requirements.txt created and installed into .venv
  - P0 scaffold/health_check/harness team review documented
  - strategy config/runtime state/watchdog architecture documented
  - 24/7 reliability hardening review documented
  - src/halo_swing_mcp scaffold implemented
  - health_check MCP tool implemented
  - direct harness and golden tests implemented
  - README and DevOps guide updated with verified P0 commands
  - P0 closed with storage/schema design deferred to P1
not_started:
  - P1 storage/schema design
  - strategy_config JSON/schema
  - run_journal/checkpoint/watchdog
  - supervisor/restart/backpressure/circuit-breaker runtime hardening
  - market data adapters
  - scoring engine
```

## Active Task

```yaml
doing: P0 closed after scaffold/health_check/harness baseline
next_atomic_step: commit P0 close state, then start P1 storage/schema design review
success_criteria:
  - PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check passes
  - PYTHONPATH=src ./.venv/bin/python -m pytest passes
  - PYTHONPATH=src ./.venv/bin/python -m ruff check . passes
  - server module imports and exposes halo_swing_mcp FastMCP server
  - SQLite/schema work is explicitly deferred to P1
```

## Implementation Constraints

```yaml
trading:
  - MVP must not place orders
  - outputs must include stop and take-profit guidance when issuing buy signals
  - leveraged ETFs are swing/tactical only, not long-term holds
  - judge leveraged ETF entries from underlying indices, not only ETF charts

architecture:
  - Hermes handles conversation, Telegram, cron, memory, final explanation
  - MCP handles data collection, calculations, signal ledger, labeling, evaluation
  - numeric indicators must be calculated in code
  - LLM may interpret evidence and write explanations, but must not be the numeric calculator

harness_engineering:
  - every new MCP tool should have a direct CLI/test harness where practical
  - external data and LLM outputs should be replayable through fixtures
  - prefer deterministic golden fixtures before live API tests
  - build harnesses as scaffolding for future LLM edits, not as afterthoughts

virtual_team_gates:
  - Dev: implementation plus minimum harness
  - DevOps: local environment, dependency install, server commands, Hermes setup guide
  - QC: fixture/golden tests plus live smoke separation
  - CTO: architecture/risk/overfitting/scope review
  - Docs Gardener: keep SSOT/CONTEXT/WORKING aligned
  - roles may be simulated in one Codex session, but outputs/checks must stay separate

docs:
  - keep all docs under docs/
  - update SSOT first when architecture/scope changes
  - WORKING.md should stay short and machine-readable
```

## Planned Phases

```yaml
P0_docs:
  status: done
  artifacts:
    - docs/CONTEXT.md
    - docs/WORKING.md
    - docs/halo-swing-development-plan.md

P0_project_initialization:
  status: closed
  tasks:
    - Python package scaffold
    - MCP server entrypoint
    - config/env loader
    - health_check tool
    - basic smoke test and CLI/test harness

P1_market_data:
  status: pending
  tasks:
    - OHLCV adapter
    - QQQ/SPY/SMH/SOXX/BTC snapshots
    - RSI/DMI/ADX/MA/ATR
    - feature_store schema

P2_swing_engine:
  status: pending
  tasks:
    - score_leverage_swing
    - generate_trade_guide
    - strategy_config JSON load/validation/hash
    - BUY_2X/BUY_3X/WAIT/TRIM/EXIT/STOP

P3_macro_news_events:
  status: pending
  tasks:
    - VIX/VXN/DXY/rates/oil
    - FOMC/CPI/PCE/NFP/earnings calendar
    - Fed/Treasury/White House/EIA news evidence cards

P4_feedback:
  status: pending
  tasks:
    - signal_ledger
    - triple barrier labeling
    - MFE/MAE
    - config_version/config_hash traceability
    - score calibration
    - champion/challenger

P5_hermes:
  status: pending
  tasks:
    - Hermes MCP config example
    - cron prompts
    - Telegram report format
    - run_journal/checkpoint/watchdog for long-running jobs
    - supervisor/restart/degraded-mode operating guide
```

## P0 Planning Review

```yaml
scope:
  phase: P0_project_initialization
  source: docs/halo-swing-development-plan.md#phase-0-프로젝트-초기화
  mode: planning_only_no_code

dev_plan:
  objective: create the smallest runnable MCP server foundation
  implementation_steps:
    - choose Python package layout: src/halo_swing_mcp
    - use .venv plus requirements.txt for P0 dependency management
    - create server entrypoint for stdio MCP
    - create config/env loader with .env.example
    - create health_check tool returning name/version/status/capabilities
    - create CLI/test harness able to call health_check without Hermes
    - create tests/fixtures and tests/golden directories
  dev_exit_criteria:
    - .venv based MCP server command starts without crashing
    - health_check callable from MCP server path
    - health_check callable from local harness path

devops_plan:
  objective: make P0 runnable from a clean local checkout and ready for Hermes registration
  setup_steps:
    - maintain .venv plus requirements.txt dependency path
    - document local setup and verification commands
    - document target Hermes MCP config for stdio server
    - document secrets/.env handling and no-commit rules
    - keep smoke commands separate from live network/API-key checks
  devops_exit_criteria:
    - docs/devops-setup-guide.md exists
    - setup guide distinguishes current commands from planned server commands
    - .gitignore excludes .venv and local secrets
    - Hermes config example matches the chosen server entrypoint after implementation

qc_plan:
  objective: make Phase 0 reproducible before live integrations exist
  validation_steps:
    - unit test health_check schema
    - CLI harness smoke test with deterministic output
    - verify no network access is required for P0 tests
    - verify .env.example contains placeholders only
    - verify import/package entrypoint from clean checkout
  qc_exit_criteria:
    - pytest passes for P0 tests
    - smoke command documented and repeatable
    - fixture/golden directories exist even if minimal

cto_plan:
  objective: prevent early architecture drift
  review_points:
    - MCP boundary is thin and tool-oriented, not a monolithic agent
    - no trading/order connector is introduced in P0
    - dependencies are minimal and justified
    - config does not assume paid data providers
    - package layout leaves room for data/engines/tools/storage layers from SSOT
    - harness path is first-class, not an afterthought
  cto_exit_criteria:
    - P0 does not make irreversible choices about data vendors or broker APIs
    - P0 keeps future Hermes integration stdio-friendly
    - P0 has no hidden live-network requirement

docs_gardener_plan:
  objective: keep docs aligned while code skeleton appears
  doc_steps:
    - update README with local run and smoke commands
    - update WORKING status from planning_review to implementation_ready
    - update SSOT only if package layout or phase boundary changes
    - keep all new project docs under docs/
    - do not duplicate the full development plan elsewhere
  docs_exit_criteria:
    - new commands in README match actual scripts
    - WORKING next_atomic_step points to the first implementation action

p0_go_no_go:
  current_cto_call: conditional_go_for_p1_after_blocking_decision
  blocking_decision_before_p1:
    - choose MCP Python stack
    - freeze script names for server and harness
  go_conditions:
    dev:
      - P1 scope is limited to scaffold, stdio MCP entrypoint, health_check, harness, offline tests
      - package layout follows SSOT layers or leaves room for them
      - no market/news/scoring feature is pulled into P1
    qc:
      - P1 tests are offline-only
      - health_check output schema is stable enough for golden test
      - harness command is defined before implementation starts
    devops:
      - .venv and requirements.txt are the P0 environment baseline
      - .venv is ignored by git
      - Hermes config is documented as a target until the server module exists
    cto:
      - MCP server remains a thin tool server
      - no broker/exchange/order connector
      - no irreversible vendor choice
      - dependencies remain minimal
    docs_gardener:
      - README will be updated with actual commands during P1
      - WORKING will move from planning_review to implementation_ready only after the blocking decision
      - SSOT will be updated if stack choice changes architecture
  no_go_conditions:
    dev:
      - P1 includes market data collection, scoring, LLM calls, DB feature schema, or trading connectors
      - server cannot run without Hermes
      - health_check cannot be called through a local harness
    qc:
      - P1 depends on live network/API keys
      - no fixture/golden directory convention exists
      - no repeatable smoke command is defined
    devops:
      - secrets are committed
      - setup guide claims unimplemented server commands are already working
      - Hermes config drifts from actual entrypoint
    cto:
      - MCP code starts to become an autonomous agent instead of tool server
      - paid data provider or broker API is hardcoded
      - automatic trading path appears before explicit future approval
    docs_gardener:
      - docs are created outside docs/
      - README commands drift from actual scripts
      - WORKING and SSOT phase names diverge
  p1_scope_guardrail:
    allowed:
      - Python .venv/requirements scaffold
      - stdio-compatible MCP server entrypoint
      - config/env loader
      - health_check tool
      - CLI/test harness for health_check
      - offline pytest/golden fixture skeleton
    forbidden:
      - market data adapters
      - news collectors
      - LLM prompts
      - scoring logic
      - DB migrations beyond minimal skeleton if needed
      - order execution or broker/exchange integration
```

## P0 Cross-Check Findings

```yaml
dev_to_qc:
  finding: P0 must define a harness command before adding market data tools.
  improvement: add a tiny CLI runner or pytest helper that calls tool functions directly.

qc_to_dev:
  finding: health_check needs a stable output schema for golden testing.
  improvement: freeze fields now: project, version, status, mcp_server, capabilities.

cto_to_dev:
  finding: choosing an MCP library is the only meaningful P0 technical decision.
  improvement: select the smallest stdio-compatible Python MCP stack; avoid broader agent frameworks in MCP server code.

cto_to_qc:
  finding: live-network tests in P0 would create false instability.
  improvement: mark all P0 tests offline-only; live tests begin in later data phases as smoke.

docs_to_all:
  finding: Phase numbering in WORKING previously differed from SSOT.
  improvement: align WORKING names with SSOT phase names, using P0_project_initialization for the next slice.

overall_recommendation:
  verdict: P0 implementation can start from the current .venv baseline.
  blocking_decision: freeze exact server and harness commands before code starts.
  non_blocking_improvements:
    - add harness directory convention to implementation slice
    - add golden fixture naming convention
    - update README immediately when scripts are created
```

## P0 Implementation Readiness Review

```yaml
scope: unresolved items needed to implement all remaining P0 work

dev_team:
  needed:
    - create src/halo_swing_mcp package scaffold
    - create stdio MCP server module using official MCP Python SDK / FastMCP
    - implement config/env loader and .env.example placeholders
    - implement health_check only; no market/news/scoring tools yet
    - create direct harness command for health_check
  decision_view:
    python_runtime: use .venv Python 3.11.14
    package_manager: use requirements.txt for P0
    server_command: prefer ./.venv/bin/python -m halo_swing_mcp.server

devops_team:
  needed:
    - own docs/devops-setup-guide.md
    - keep local setup commands reproducible from clean checkout
    - keep Hermes MCP config examples aligned with server entrypoint
    - define smoke commands for environment, MCP server, harness, and future live checks
    - ensure .env and API keys are never committed
  decision_view:
    environment_baseline: .venv plus requirements.txt
    hermes_config_status: target guide until halo_swing_mcp.server exists
    smoke_policy: offline smoke first; live smoke only after data adapters exist

qc_team:
  needed:
    - unit test stable health_check schema
    - CLI harness smoke test with deterministic output
    - tests/fixtures and tests/golden directories
    - verify P0 tests require no network and no API keys
  decision_view:
    health_check_schema: freeze project/version/status/mcp_server/capabilities
    live_tests: no-go in P0 except dependency installation

cto_team:
  needed:
    - keep MCP as thin tool server, not autonomous agent
    - avoid data vendors, broker APIs, order execution, and LLM prompts in P0
    - keep official MCP SDK dependency but avoid broader agent frameworks
    - require local harness before declaring the tool complete
  decision_view:
    call: GO_FOR_P0_IMPLEMENTATION
    condition: server/harness command names must be frozen in the first code slice

docs_gardener:
  needed:
    - keep SSOT aligned with .venv/requirements decision
    - link DevOps guide from CONTEXT and README
    - update README when actual run/smoke commands exist
    - keep WORKING focused on current state and next atomic step
  decision_view:
    current_docs: aligned for environment baseline plus DevOps role
    next_docs_update: after server and harness commands are implemented

cto_final_opinion:
  go_no_go: GO
  rationale:
    - Python 3.11 .venv resolves the local Python 3.9 mismatch
    - official MCP SDK / FastMCP is suitable for Hermes-compatible stdio tools
    - requirements.txt is enough for P0 and avoids waiting on uv
    - DevOps gate reduces future Hermes setup drift
    - scope remains narrow enough to avoid premature market/scoring complexity
  hard_no_go_triggers:
    - adding market data, news collection, scoring, LLM prompts, or trading connectors in P0
    - committing secrets or local .venv artifacts
    - health_check lacking direct harness coverage
    - tests depending on live network or secrets
```

## P0 Scaffold Health Harness Review

```yaml
scope: src/halo_swing_mcp scaffold plus health_check plus direct harness
mode: review_only_no_code_implementation

proposed_file_set:
  package:
    - src/halo_swing_mcp/__init__.py
    - src/halo_swing_mcp/config.py
    - src/halo_swing_mcp/server.py
    - src/halo_swing_mcp/harness.py
    - src/halo_swing_mcp/tools/__init__.py
    - src/halo_swing_mcp/tools/health.py
  tests:
    - tests/test_health_check.py
    - tests/fixtures/.gitkeep
    - tests/golden/health_check.json
  config:
    - .env.example

health_check_schema_v1:
  project: halo-swing
  version: stable package version string
  status: ok
  mcp_server: halo_swing_mcp
  capabilities:
    - health_check
  live_data_required: false

team_opinions:
  dev:
    recommendation: implement health_check as a pure function in tools/health.py; server.py only registers it with FastMCP.
    rationale:
      - harness and MCP tool can share one implementation
      - pure function keeps tests simple and deterministic
      - server entrypoint stays thin and stdio-friendly
    concerns:
      - avoid duplicating health_check logic in harness.py
      - avoid adding market/news/scoring placeholders that look implemented
      - no pyproject means commands must use PYTHONPATH=src until packaging changes
  devops:
    recommendation: freeze commands around PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp...
    rationale:
      - current baseline is .venv plus requirements.txt
      - Hermes config should use absolute paths after server.py exists
      - P0 smoke must distinguish long-running stdio server from one-shot harness
    concerns:
      - stdio MCP server may run until killed; use harness and import tests for deterministic smoke
      - README/devops guide must not claim planned server commands are working before implementation
      - spaces in local path require careful quoting in Hermes config examples
  qc:
    recommendation: golden-test health_check output and test harness stdout as sorted JSON.
    rationale:
      - no timestamp, machine path, Python version, or environment-specific field should appear in golden output
      - direct harness exit codes make failures easy to diagnose
      - tests must pass offline with no API keys
    concerns:
      - including dynamic dependency versions in health_check would make golden output brittle
      - MCP registration should be tested by import/structure first, not by requiring Hermes
      - unknown harness commands need a nonzero exit code
  cto:
    recommendation: GO, but keep P0 intentionally boring: scaffold, health_check, harness, offline tests only.
    rationale:
      - this creates the minimum reliable contract for Hermes and future teams
      - pure function plus MCP wrapper prevents tool-server drift into agent logic
      - no database, market data, LLM prompt, or scoring code is needed for this slice
    concerns:
      - do not add premature plugin registries, abstract factories, or feature schemas
      - do not add data vendor decisions while implementing health_check
      - do not treat server startup alone as sufficient without harness coverage
  docs_gardener:
    recommendation: update README and DevOps guide only after actual commands exist.
    rationale:
      - WORKING can hold implementation intent; README should show working commands
      - SSOT changes only if package layout or phase boundary changes
      - devops guide should mark target commands as planned until verified
    concerns:
      - docs can drift if server module path changes after implementation
      - golden schema must be copied only once, preferably from tests or WORKING summary

cross_checks:
  dev_to_qc:
    finding: pure health_check function enables unit tests without MCP protocol.
    adjustment: tests should import the function directly and compare to golden JSON.
  qc_to_dev:
    finding: schema must be deterministic.
    adjustment: exclude timestamp, host path, current date, Python version, and installed package versions from v1 output.
  devops_to_dev:
    finding: stdio server command is long-running.
    adjustment: provide harness one-shot command as the primary smoke path; server command verifies import/start path separately.
  dev_to_devops:
    finding: no pyproject means module execution depends on PYTHONPATH.
    adjustment: document PYTHONPATH=src in README/devops guide until editable packaging exists.
  cto_to_dev:
    finding: P0 should not create architecture for future scoring yet.
    adjustment: keep directories minimal; only create tools needed for health_check.
  cto_to_devops:
    finding: Hermes config must only expose implemented tools.
    adjustment: P0 include list contains health_check only.
  qc_to_devops:
    finding: live smoke and offline tests must be separated from day one.
    adjustment: P0 pytest/harness commands are offline; future live smoke gets separate command naming.
  docs_to_all:
    finding: commands become user-facing only after verification.
    adjustment: README receives actual commands after implementation; WORKING may keep planned commands.

frozen_decisions_for_next_code_slice:
  package_root: src/halo_swing_mcp
  mcp_library: official MCP Python SDK / FastMCP
  server_module: halo_swing_mcp.server
  harness_module: halo_swing_mcp.harness
  harness_command: PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check
  test_command: PYTHONPATH=src ./.venv/bin/python -m pytest
  health_check_output: health_check_schema_v1
  first_tool: health_check only

cto_final_call:
  go_no_go: GO_FOR_IMPLEMENTATION
  condition:
    - implement only the proposed file set unless a test requires a tiny helper
    - keep health_check deterministic and offline
    - update README/devops guide after commands are verified
```

## Strategy Config Runtime State Review

```yaml
trigger_question: weights will later be tuned by feedback pipeline; do we need JSON settings, persistence, memory dumps, and watchdog?
cto_answer: yes, required for reproducibility and long-running stability, but not part of the P0 health_check code slice

architecture_decisions:
  strategy_config:
    format: versioned JSON first, DB-backed registry later
    must_include:
      - config_id
      - version
      - status: champion/challenger/archived
      - weights
      - thresholds
      - risk parameters
      - config_hash
    rules:
      - no scoring weights hardcoded in engine code
      - every signal records config_version and config_hash
      - feedback creates challenger candidates only
      - active/champion config is not auto-overwritten
      - schema validation, bounds check, and sum check are required
  persistence:
    run_journal: records each scheduled/user/evaluation run with input/output/error refs
    signal_ledger: records config_version/config_hash with each signal
    state_checkpoint: stores resumable state for long-running jobs
    artifacts: runtime dumps/logs/checkpoints stay out of git
  watchdog:
    purpose: detect memory growth, stale jobs, repeated errors, NaN/null explosions, oversized payloads, config hash mismatches
    actions:
      - record watchdog_event
      - attach summary to run_journal
      - write checkpoint before risky live calls or graceful shutdown
      - block new live work or request graceful shutdown on hard limit

team_opinions:
  dev:
    recommendation: keep config loader/schema separate from scoring engine; scoring receives a validated config object.
    risk: putting default weights inside scoring code makes feedback tuning unreproducible.
  devops:
    recommendation: keep logs/state/checkpoints ignored by git and document retention/cleanup policy before cron jobs run.
    risk: unchecked dumps can grow silently and fill disk.
  qc:
    recommendation: add config fixture/golden tests when scoring begins; test invalid weights, missing fields, and hash stability.
    risk: dynamic fields in config hash generation can break replay.
  cto:
    recommendation: add these as Phase 2/5/6/7 architecture, not P0 health_check implementation.
    risk: building watchdog too early can distract from the minimal MCP foundation.
  docs_gardener:
    recommendation: keep the full schema in SSOT; keep WORKING as a decision summary only.
    risk: duplicating full JSON schemas across docs will drift.

cross_checks:
  dev_to_qc:
    finding: config hash must be canonicalized.
    adjustment: sort JSON keys and exclude volatile metadata from hash input.
  qc_to_dev:
    finding: every signal must be replayable.
    adjustment: signal_ledger stores config_hash and input snapshot refs.
  devops_to_cto:
    finding: watchdog introduces runtime behavior.
    adjustment: first implementation should be observe-only; blocking/shutdown actions require explicit thresholds.
  cto_to_devops:
    finding: memory dumps may contain API responses or sensitive text.
    adjustment: dumps are local artifacts, ignored by git, and should prefer refs/summaries over raw full payloads.
  docs_to_all:
    finding: this changes architecture but not current P0 implementation scope.
    adjustment: SSOT updated; next code slice remains scaffold + health_check + harness.
```

## 24x7 Reliability Architecture Review

```yaml
trigger_question: what else must be added now so 24/7 operation does not suffer from memory overflow or hard-to-debug failures?
cto_answer: add reliability guardrails now in architecture; implement incrementally after the minimal MCP foundation

team_opinions:
  dev:
    add:
      - liveness and readiness should be separate from health_check
      - all live tools need timeout/deadline parameters
      - collectors should stream/chunk large payloads instead of loading full documents/news bundles into memory
      - caches must have TTL plus max_items or max_bytes
      - every scheduled job needs idempotency key and duplicate-run lock
    risk:
      - unbounded list/dict caches, accumulated evidence bundles, and duplicate cron overlap are likely memory leak sources
  devops:
    add:
      - external supervisor with restart policy and crash-loop backoff
      - log rotation and retention limits for logs/state/checkpoints/artifacts
      - process RSS soft/hard limits and disk usage alerts
      - critical watchdog_event notification to Telegram or an ops channel
      - graceful shutdown path that writes checkpoint before exit
    risk:
      - internal watchdog cannot help if the process is already dead or the host disk is full
  qc:
    add:
      - soak tests with repeated health_check/tool runs
      - memory regression test for bounded cache behavior
      - fake API timeout/429/5xx tests for retry and circuit breaker
      - duplicate cron/idempotency tests
      - corrupted checkpoint/config recovery tests
    risk:
      - tests that only verify happy-path outputs will miss 24/7 failure modes
  cto:
    add:
      - degraded mode as a first-class output state
      - circuit breaker before provider-specific integrations
      - stale-data detection so BUY signals cannot be produced from old data silently
      - atomic persistence for config/checkpoint writes
      - database migration/backup/restore strategy before signal ledger grows
    risk:
      - 24/7 systems fail by slow degradation more often than one obvious crash
  docs_gardener:
    add:
      - operations runbook with restart, backup, restore, log cleanup, and incident steps
      - explicit resource budget table once real tools exist
      - document which commands are offline smoke, live smoke, and production cron
    risk:
      - undocumented operational assumptions become invisible architecture

cross_checks:
  dev_to_devops:
    finding: code-level watchdog must expose metrics/events for supervisor and alerts.
    adjustment: watchdog_event should be structured and machine-readable.
  devops_to_dev:
    finding: restart policy requires idempotent jobs.
    adjustment: run_id/idempotency key and duplicate-run lock are mandatory before cron automation.
  qc_to_dev:
    finding: memory overflow risks require tests, not only code review.
    adjustment: add soak and bounded-cache tests when collectors/caches appear.
  qc_to_devops:
    finding: log/checkpoint retention must be testable.
    adjustment: cleanup command or retention policy should have a dry-run mode.
  cto_to_all:
    finding: degraded mode must be safer than stale confidence.
    adjustment: stale or partial data should downgrade to WAIT/BLOCK with warnings, not BUY_2X/BUY_3X.
  docs_to_all:
    finding: 24/7 readiness is not a P0 health_check blocker but is an architecture gate before live cron.
    adjustment: keep P0 narrow; require reliability gate before Phase 7 production cron.

new_architecture_decisions:
  process_model:
    - MCP server remains restartable and mostly stateless
    - long-running jobs persist progress through run_journal and checkpoint
    - external supervisor handles process death and crash-loop backoff
  resource_limits:
    - define soft/hard memory budgets before live data collectors
    - bound queue length, cache size, evidence bundle size, and artifact retention
    - watchdog observes memory trend and triggers checkpoint/degraded mode before hard failure
  failure_policy:
    - provider failures use timeout, retry, circuit breaker, and degraded mode
    - stale data or partial evidence cannot produce aggressive BUY signals silently
    - repeated critical failures alert the user instead of continuing normal reports

cto_final_call:
  go_no_go: GO_TO_KEEP_P0_NARROW
  required_before_24x7_cron:
    - external supervisor/restart plan
    - run_id/idempotency and duplicate-run lock
    - watchdog_event persistence
    - bounded caches/queues/artifacts
    - retry/circuit breaker/degraded mode
    - operations runbook
```

## P0 Scaffold Implementation Result

```yaml
status: implemented
implemented_files:
  package:
    - src/halo_swing_mcp/__init__.py
    - src/halo_swing_mcp/config.py
    - src/halo_swing_mcp/server.py
    - src/halo_swing_mcp/harness.py
    - src/halo_swing_mcp/tools/__init__.py
    - src/halo_swing_mcp/tools/health.py
  tests:
    - tests/test_health_check.py
    - tests/fixtures/.gitkeep
    - tests/golden/health_check.json
  config:
    - .env.example

verified_commands:
  harness: PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check
  tests: PYTHONPATH=src ./.venv/bin/python -m pytest
  lint: PYTHONPATH=src ./.venv/bin/python -m ruff check .
  import_server: PYTHONPATH=src ./.venv/bin/python -c "import halo_swing_mcp.server as s; print(s.mcp.name)"

verified_results:
  harness: passed
  tests: 3 passed
  lint: passed
  server_import: halo_swing_mcp

remaining_p0_questions:
  - none; P0 is ready to commit/push

still_not_p0_code:
  - strategy_config JSON/schema implementation
  - run_journal/checkpoint/watchdog implementation
  - supervisor/circuit-breaker implementation
  - feature_store/signal_ledger/label_store domain schemas
  - SQLite migration/domain schema implementation
  - market/news/scoring/trading integrations
```

## P0 Close Decision

```yaml
scope: close P0 and defer SQLite/schema to P1
decision: P0 closes at MCP scaffold plus health_check plus harness plus docs/devops baseline
rationale:
  - storage schemas affect future replay, signal ledger, config hash, labeling, and watchdog design
  - shallow P0 schema would likely be rewritten in P1
  - current P0 already proves MCP runtime, dependency path, harness, and offline tests

deferred_to_p1:
  - SQLite connection/migration skeleton
  - feature_store/schema design
  - signal_ledger/schema design
  - strategy_config schema
  - run_journal/checkpoint/watchdog persistence schema

team_opinions_after_deferral:
  dev:
    recommendation: close P0 now; design storage contracts first in P1 before writing migrations.
    reason: database helpers are easy, but the durable schema must match replay/evaluation needs.
  devops:
    recommendation: keep data/ ignored and do not create local DB artifacts in P0.
    reason: P1 should define DB path, backup, migration, and retention policy together.
  qc:
    recommendation: require schema fixtures and migration idempotency tests in P1.
    reason: P0 tests should remain focused on MCP/harness health; DB tests need fuller schema acceptance criteria.
  cto:
    recommendation: close P0; make P1 start with storage/schema architecture review.
    reason: schema choices are high-leverage and should be decided with feature_store, signal_ledger, strategy_config, and runtime observability together.
  docs_gardener:
    recommendation: mark P0 closed and remove planned db_check commands from active setup docs.
    reason: setup docs should contain only verified P0 commands.

cross_checks:
  dev_to_qc:
    finding: deferring schema avoids locking tests to a throwaway table layout.
    adjustment: P1 starts with schema fixture design.
  qc_to_dev:
    finding: DB migration idempotency remains mandatory later.
    adjustment: add it as a P1 entry criterion.
  devops_to_dev:
    finding: no DB artifact should be created during P0 smoke.
    adjustment: keep P0 commands limited to health_check, pytest, and lint.
  dev_to_devops:
    finding: future DB paths must handle local paths with spaces.
    adjustment: P1 storage design includes path parsing and backup/restore policy.
  cto_to_dev:
    finding: P0 should become a clean baseline commit.
    adjustment: commit current scaffold before starting schema work.
  qc_to_cto:
    finding: P1 needs deeper schema acceptance criteria.
    adjustment: open P1 with team review before migrations.
  docs_to_all:
    finding: no unimplemented commands should remain in README/DevOps guide.
    adjustment: remove planned db_check from active docs.

cto_final_call:
  go_no_go: P0_CLOSE_GO
  p1_first_topic: storage/schema architecture review
```

## Local Environment

```yaml
python_runtime:
  decision_needed: false
  current_choice: .venv with Python 3.11.14

package_manager:
  decision_needed: false
  current_choice: .venv plus requirements.txt

installed_direct_dependencies:
  mcp: 1.27.0
  pydantic: managed by requirements.txt
  pydantic-settings: managed by requirements.txt
  python-dotenv: managed by requirements.txt
  pytest: managed by requirements.txt
  pytest-asyncio: managed by requirements.txt
  ruff: managed by requirements.txt

activation:
  command: source .venv/bin/activate
```

## Open Decisions

```yaml
data_sources:
  decision_needed: true
  current_bias: start with free/simple sources and keep paid vendors behind interfaces

mcp_library:
  decision_needed: false
  current_choice: official MCP Python SDK / FastMCP

harness_shape:
  decision_needed: false
  current_choice: pytest golden fixtures plus a small CLI runner for selected MCP tools

package_manager:
  decision_needed: false
  current_choice: .venv plus requirements.txt

strategy_config_storage:
  decision_needed: false
  current_choice: versioned JSON first, DB-backed strategy_config later

runtime_observability:
  decision_needed: false
  current_choice: run_journal plus state_checkpoint plus watchdog_event

database:
  decision_needed: false
  current_choice: SQLite for MVP, PostgreSQL later
```

## Recent Commits

```text
596c4c8 Document virtual team gates
8b25fb6 Add harness engineering context
73c237e Simplify working handoff doc
```
