---
name: role-gated-harness
description: Use when planning, reviewing, or gating medium and large Halo Swing changes with FE, BE, DB, AI LLM, Security, DevOps, QC, CTO, CEO, Fintech VC, and Docs Gardener roles. Applies to architecture, storage/schema, security-sensitive, LLM/eval, trading/risk/scoring, multi-module, release, and pre-merge review work.
---

# Role-Gated Harness

Use this workflow to turn role-based multi-agent review into executable gates,
task contracts, tests, hooks, rules, scans, and metrics.

Do not use this skill for one-file tests, formatting, or simple bug fixes with
a clear failing test.

## Modes

- `gate_plan`: role planning and cross-check allowed, code forbidden.
- `implement`: code allowed only inside the task contract, role prose forbidden.
- `diff_review`: role review allowed, code edits forbidden unless a repair task
  is opened.
- `repair`: fix only failed verification or approved review findings.

## Review Tiers

- `S0_trivial`: owner + QC, no role rounds.
- `S1_small`: owner + QC + DevOps + Docs, one short review pass.
- `S2_medium`: relevant domain role + BE + QC + DevOps + Security + Docs + CTO,
  one round.
- `S3_architecture_gate`: FE, DB, BE, AI LLM, Security, QC, DevOps, Docs, CTO,
  two rounds.
- `S4_product_or_risk_gate`: all roles, two rounds.

Use S3/S4 only for architecture, storage, security, LLM/eval, trading/risk, or
release decisions.

## Workflow

1. Frame the gate: define gate id, mode, review tier, allowed outputs, and
   forbidden outputs.
2. Select roles from `references/review-matrix.md`.
3. Run round 1 role reviews using `references/role-output-schema.md`.
4. Build a cross-check issue ledger. Do not run all-pairs review by default.
5. Run round 2 as blocker closure only.
6. Produce CTO synthesis: GO, NO_GO, or CHANGE_REQUEST.
7. Convert CTO synthesis into a gate packet and task contract.
8. Implement only from the task contract.
9. Run deterministic verification and Stop hook checks.
10. Run role-based diff review if the contract asks for it.
11. Promote repeated findings to a test, hook, rule, AGENTS rule, skill update,
    ADR, or backlog item.
12. Record useful quality metrics when the work is S2 or higher.

## Placement

- Active state: `docs/WORKING.md`
- Executable task contract: `.codex/tasks/current.json`
- Portable task mirror: `docs/codex-task.json`
- CTO gate packet: `docs/gates/<gate_id>.md`
- Role reviews: `docs/reviews/<gate_id>/`
- Durable architecture decisions: `docs/adr/`

`docs/WORKING.md` is LLM-only operational memory. It may contain state ledger
sections, but agents must execute only `CURRENT_DIRECTIVE`. Archived review
ledger entries are evidence only. Do not append long role review logs to it.

## Implementation Rule

After CTO GO, stop planning. In `implement` mode, read only the active task
contract, the gate packet, and referenced files. Do not spawn role agents or
write team-review sections unless the user explicitly switches back to planning
or review mode.

## References

- Role output schema: `references/role-output-schema.md`
- Review activation matrix: `references/review-matrix.md`
- Gate packet template: `references/gate-packet-template.md`
- Harness promotion and metrics: `references/harness-promotion.md`
