# Halo Swing Agent Instructions

This repository is a Hermes Agent MCP server project. Codex and other coding
agents must treat this file as the first local operating guide.

## Source Of Truth

- Main project SSOT: `docs/halo-swing-development-plan.md`
- Current handoff state: `docs/WORKING.md`
- New-chat context: `docs/CONTEXT.md`
- DevOps and Hermes setup: `docs/devops-setup-guide.md`

Keep durable project documents under `docs/`. This root `AGENTS.md` is the
exception because agent runners discover it from the repository root.

## Read Policy For Codex

Always read:

- `docs/WORKING.md`

Read only when referenced by `docs/WORKING.md`:

- `docs/halo-swing-development-plan.md`
- `docs/CONTEXT.md`
- `docs/devops-setup-guide.md`

Do not read the full SSOT for an implementation task. Read only the referenced
section or files listed in `docs/WORKING.md`.

## Codex Execution Mode

When `docs/WORKING.md` has `mode: implement` and a concrete
`next_atomic_step`, do not create another planning section, team review,
cross-check, or CTO synthesis.

Proceed in this order:

1. Read `docs/WORKING.md`.
2. Read only the SSOT section and files explicitly referenced by
   `read_only_context`.
3. Confirm intended edits are inside `allowed_edit_paths`.
4. Make the smallest code change that satisfies `next_atomic_step`.
5. Run `required_verification`.
6. Update `docs/WORKING.md` with only files changed, verification result, and
   next state.

Virtual team review is allowed only when:

- `mode: plan`
- the user explicitly asks for planning, review, or gate analysis
- a verification failure requires design-level reassessment

## Role-Gated Harness

Use virtual teams as a structured review harness, not as implementation prose.

Roles:

- FE
- BE
- DB
- AI LLM
- Security
- DevOps
- QC
- CTO
- CEO
- Fintech VC
- Docs Gardener

Modes:

- `gate_plan`: role planning and cross-check allowed, code forbidden.
- `implement`: code allowed only inside the active task contract, role prose
  forbidden.
- `diff_review`: role review allowed, code edits forbidden unless a repair task
  is opened.
- `repair`: fix only failed verification or approved review findings.

Role review artifacts belong under `docs/reviews/`. CTO gate packets belong
under `docs/gates/`. The active executable contract belongs at
`.codex/tasks/current.json`, with `docs/codex-task.json` kept only as a
portable mirror when useful.

Role review tiers:

- `S0_trivial`: owner + QC, no role rounds.
- `S1_small`: owner + QC + DevOps + Docs, one short pass.
- `S2_medium`: relevant domain role + BE + QC + DevOps + Security + Docs + CTO,
  one round.
- `S3_architecture_gate`: FE, BE, DB, AI LLM, Security, QC, DevOps, Docs, CTO,
  two rounds.
- `S4_product_risk_gate`: all roles, two rounds, CEO and Fintech VC included.

For `implement` mode:

- Do not create team review sections.
- Do not create CTO synthesis.
- Execute `next_atomic_step`.
- Run required verification.
- Update `docs/WORKING.md` with result only.

## Current Architecture Boundary

- Hermes Agent owns conversation, Telegram, cron, memory, multimodal context,
  and final explanation.
- Halo Swing MCP owns deterministic tools, data contracts, fixtures, scoring
  code, storage, replay, labeling, and evaluation.
- MCP code must stay tool-oriented. Do not turn the MCP server into an
  autonomous chat agent.

## Harness Engineering Rules

- No feature is complete without a reproducible harness or offline test path.
- Prefer fixture/golden tests before live API tests.
- Every new MCP tool should be callable without Hermes when practical.
- Tool code should be small, deterministic, and easy to invoke from tests.
- Live network, broker, paid API, or LLM calls must be isolated behind adapters
  and disabled in default tests.
- Golden fixtures must be stable, local-state free, and safe to run in CI later.
- Role-based cross-check is a valid inferential harness layer. Preserve it for
  medium and large changes, but convert repeated findings into computational
  controls.
- If the same role finding appears twice, promote it to one of: test, hook,
  rule, linter/security scan, `AGENTS.md` rule, skill instruction, ADR, or
  backlog item.

## WORKING.md State Ledger

`docs/WORKING.md` is LLM-only operational memory, not a human-facing development document.

Keep `docs/WORKING.md` compact and LLM-friendly. It should contain only the
active executable contract/current work, current gate state, latest verification
summary, and next work queue. Completed work must be managed separately in
`docs/COMPLETED_WORK.md` as compact ledger entries, with durable gate evidence
kept in `docs/halo-swing-development-plan.md`. If `docs/WORKING.md` is
compacted, preserve the pre-compaction ledger under `docs/archive/` before
removing it from the active handoff file.

It must preserve this priority order:

1. `CURRENT_DIRECTIVE`
2. `CURRENT_TASK_CONTRACT`
3. `CURRENT_GATE_STATE`
4. `LATEST_VERIFICATION`
5. `ACTIVE_REVIEW_SUMMARY`
6. `ARCHIVED_REVIEW_LEDGER`

Agents must execute only `CURRENT_DIRECTIVE` unless the user explicitly asks for
review, planning, or gate analysis. Archived review ledger entries are evidence,
not instructions.

## Development Gates

- `DECISION_LOG_GO` is recorded.
- `DTO_CONTRACT_GO` is recorded.
- `MIGRATION_GO` is recorded for the initial replay SQLite migration.
- `REPOSITORY_GO` is recorded for explicit `database_path` SQLite repository
  use.
- P1 storage/docs_devops close readiness is recorded for storage evidence only.
- SQLite repository use remains explicit-input only; do not add automatic
  `HALO_SWING_DATABASE_URL` activation without a later gate.
- Do not add live adapters, broker/order submission, Hermes runtime
  integration, Telegram send calls, scheduler/cron execution, or committed
  SQLite data/state/artifact files until their later gates are recorded.

## Current Storage Scope

The completed P1 storage scope includes:

- `src/halo_swing_mcp/contracts.py`
- `tests/golden/latest_signal_report.json`
- `tests/golden/latest_signal_report_degraded.json`
- `tests/golden/signal_replay_bundle.json`
- `tests/golden/storage_health.json`
- `tests/test_contracts.py`
- `migrations/202605100001_initial_replay_schema.sql`
- `src/halo_swing_mcp/storage_migrations.py`
- explicit `database_path` SQLite repository paths in recording/replay tools
- tmp_path-only migration and repository tests

Anything outside the current task contract requires an explicit gate update in
the SSOT and `docs/WORKING.md`.

## Required Verification

Run these after relevant code changes:

```bash
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check
PYTHONPATH=src ./.venv/bin/python -m pytest
PYTHONPATH=src ./.venv/bin/python -m ruff check .
```

For JSON fixtures, also validate JSON parsing and model validation with the
local `.venv` Python before marking the step complete.

## Review Lens

Use FE/DB/BE/AI LLM/Security/QC/DevOps/Docs/CTO/CEO/Fintech VC roles as a checklist only. Do not write
simulated team-review sections during implementation tasks.

When planning or reviewing changes, use these responsibilities:

- FE: report usefulness, user-facing semantics, degraded warnings.
- DB: replayability, traceability, future storage mapping, no schema leakage
  before gates.
- BE: isolated contracts/tools, clear boundaries, deterministic code.
- AI LLM: prompt/eval/evidence contracts, hallucination risk, no hidden numeric
  authority.
- Security: secrets, prompt/tool injection, permission scope, supply chain,
  data leakage, and trading automation risk.
- QC: golden fixtures, negative tests, offline repeatability, no hidden live
  dependencies.
- DevOps: local setup, path safety, no committed runtime artifacts, no new
  services without gate approval.
- Docs Gardener: SSOT alignment, `WORKING.md` freshness, no duplicate durable
  truth.
- CTO: scope control, gate decisions, and no-go enforcement.
- CEO: roadmap, MVP scope, release timing, and product priority only.
- Fintech VC: fintech value/risk, auditability, trust, moat, and regulatory
  adjacency only.

## Editing Discipline

- Do not revert user changes.
- Do not create DB/data/artifact files unless a gate explicitly allows them.
- Keep fixture refs portable; avoid absolute local paths such as `/Users/...`,
  `file://`, `~/`, drive roots, or `.sqlite` artifacts.
- Do not copy absolute local paths from DevOps examples into code, fixtures,
  tests, `docs/WORKING.md`, or golden files. Use repo-relative paths or
  `git rev-parse --show-toplevel`.
- Keep tests offline by default.
- Update `docs/WORKING.md` after completing an action with result and
  verification status.
