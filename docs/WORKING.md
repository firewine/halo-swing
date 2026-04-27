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
status: docs_ready_code_not_started
last_completed:
  - GitHub repo created and pushed
  - development plan moved to docs as SSOT
  - CONTEXT.md created
  - WORKING.md converted to LLM handoff format
not_started:
  - Python MCP project scaffold
  - MCP health_check tool
  - SQLite schema
  - market data adapters
  - scoring engine
```

## Active Task

```yaml
doing: P1 MCP server MVP scaffold
next_atomic_step: create Python project skeleton and health_check MCP tool
success_criteria:
  - project has runnable MCP server entrypoint
  - health_check returns project/version/status
  - README or docs mention how to run locally
  - tests or a local smoke command verify the entrypoint
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

P1_mcp_mvp:
  status: next
  tasks:
    - Python package scaffold
    - MCP server entrypoint
    - config/env loader
    - health_check tool
    - basic smoke test and CLI/test harness

P2_market_data:
  status: pending
  tasks:
    - OHLCV adapter
    - QQQ/SPY/SMH/SOXX/BTC snapshots
    - RSI/DMI/ADX/MA/ATR
    - feature_store schema

P3_swing_engine:
  status: pending
  tasks:
    - score_leverage_swing
    - generate_trade_guide
    - BUY_2X/BUY_3X/WAIT/TRIM/EXIT/STOP

P4_macro_news_events:
  status: pending
  tasks:
    - VIX/VXN/DXY/rates/oil
    - FOMC/CPI/PCE/NFP/earnings calendar
    - Fed/Treasury/White House/EIA news evidence cards

P5_feedback:
  status: pending
  tasks:
    - signal_ledger
    - triple barrier labeling
    - MFE/MAE
    - score calibration
    - champion/challenger

P6_hermes:
  status: pending
  tasks:
    - Hermes MCP config example
    - cron prompts
    - Telegram report format
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
73c237e Simplify working handoff doc
338a6a1 Organize project docs
94ab5cc Merge remote-tracking branch 'origin/main'
```
