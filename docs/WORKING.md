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
status: p0_plan_review_in_progress
last_completed:
  - GitHub repo created and pushed
  - development plan moved to docs as SSOT
  - CONTEXT.md created
  - WORKING.md converted to LLM handoff format
  - harness engineering and virtual team gates documented
not_started:
  - Python MCP project scaffold
  - MCP health_check tool
  - SQLite schema
  - market data adapters
  - scoring engine
```

## Active Task

```yaml
doing: P0 project initialization plan review only
next_atomic_step: review Phase 0 plan by Dev/QC/CTO/Docs Gardener before implementation
success_criteria:
  - each virtual team has a concrete Phase 0 checklist
  - cross-check risks and improvements are written down
  - no code implementation is performed during this review step
  - next implementation slice is clearly bounded
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
  status: planning_review
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
    - score calibration
    - champion/challenger

P5_hermes:
  status: pending
  tasks:
    - Hermes MCP config example
    - cron prompts
    - Telegram report format
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
    - create pyproject.toml with uv-compatible scripts
    - create server entrypoint for stdio MCP
    - create config/env loader with .env.example
    - create health_check tool returning name/version/status/capabilities
    - create CLI/test harness able to call health_check without Hermes
    - create tests/fixtures and tests/golden directories
  dev_exit_criteria:
    - uv run market-swing-mcp starts without crashing
    - health_check callable from MCP server path
    - health_check callable from local harness path

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
      - Python/uv scaffold
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
  verdict: P0 plan is implementable after one decision.
  blocking_decision: choose MCP Python stack and exact script names before code starts.
  non_blocking_improvements:
    - add harness directory convention to implementation slice
    - add golden fixture naming convention
    - update README immediately when scripts are created
```

## Open Decisions

```yaml
data_sources:
  decision_needed: true
  current_bias: start with free/simple sources and keep paid vendors behind interfaces

mcp_library:
  decision_needed: true
  current_bias: choose the smallest Python MCP stack compatible with Hermes stdio

harness_shape:
  decision_needed: true
  current_bias: pytest golden fixtures plus a small CLI runner for selected MCP tools

package_manager:
  decision_needed: true
  current_bias: uv

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
