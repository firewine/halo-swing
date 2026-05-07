# WORKING

> LLM-only operational state ledger.
> Human-facing durable plans live in `docs/halo-swing-development-plan.md`.
> Execute only `CURRENT_DIRECTIVE` unless the user explicitly asks for review,
> planning, or gate analysis.

## 0. Priority Rule

Instruction priority inside this file:

1. `CURRENT_DIRECTIVE`
2. `CURRENT_TASK_CONTRACT`
3. `CURRENT_GATE_STATE`
4. `LATEST_VERIFICATION`
5. `ACTIVE_REVIEW_SUMMARY`
6. `ARCHIVED_REVIEW_LEDGER`

Archived review sections are historical context only. Do not execute archived
`planning_only_no_code`, prior gate-plan, cross-check, or CTO synthesis blocks.

## 1. CURRENT_DIRECTIVE

```yaml
mode: implement
status: p1_contract_tests_work_order_ready
gate_id: P1_DTO_CONTRACT_TESTS
review_tier: S1_small

next_atomic_step: create tests/test_contracts.py exactly from the approved DTO contract work order

allowed_edit_paths:
  - tests/test_contracts.py
  - docs/WORKING.md

blocked_path_prefixes:
  - src/halo_swing_mcp/storage/
  - src/halo_swing_mcp/adapters/
  - src/halo_swing_mcp/scoring/
  - migrations/
  - data/
  - artifacts/
  - state/

blocked_exact_paths:
  - requirements.txt
  - src/halo_swing_mcp/server.py
  - src/halo_swing_mcp/config.py

required_verification:
  - PYTHONPATH=src ./.venv/bin/python -m pytest
  - PYTHONPATH=src ./.venv/bin/python -m ruff check .
  - PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check

done_means:
  - tests/test_contracts.py exists
  - required verification passed
  - no blocked paths changed
  - no DB files, data directory, artifact directory, or dependency changes added
  - WORKING updated with result only

next_state_after_success: DTO_CONTRACT_SLICE_SIGNOFF
```

## 2. CURRENT_TASK_CONTRACT

```yaml
task_contract: .codex/tasks/current.json
portable_mirror: docs/codex-task.json
gate_packet: docs/gates/P1_DTO_CONTRACT_TESTS.md

read_only_context:
  - AGENTS.md
  - .codex/tasks/current.json
  - docs/gates/P1_DTO_CONTRACT_TESTS.md
  - docs/CONTEXT.md
  - docs/halo-swing-development-plan.md#3.20
  - src/halo_swing_mcp/contracts.py
  - tests/golden/latest_signal_report.json
  - tests/golden/latest_signal_report_degraded.json
  - tests/golden/signal_replay_bundle.json
  - tests/golden/storage_health.json

implementation_rule:
  - do_not_spawn_role_agents
  - do_not_write_team_review_sections
  - do_not_write_cto_synthesis
  - do_not_reopen_architecture_decisions
  - implement_only_next_atomic_step
```

## 3. CURRENT_GATE_STATE

```yaml
p0:
  status: closed
  implemented:
    - MCP FastMCP server entrypoint
    - health_check tool
    - direct CLI harness for health_check
    - offline pytest golden test for health_check

p1_dto_contract:
  gates:
    DECISION_LOG_GO: recorded
    DTO_CONTRACT_GO: recorded
    MIGRATION_GO: not_recorded
    REPOSITORY_GO: not_recorded
  implemented:
    - src/halo_swing_mcp/contracts.py
    - tests/golden/latest_signal_report.json
    - tests/golden/latest_signal_report_degraded.json
    - tests/golden/signal_replay_bundle.json
    - tests/golden/storage_health.json
  active_next:
    - tests/test_contracts.py
```

## 4. ACTIVE_REVIEW_SUMMARY

```yaml
methodology: Role-Gated Codex Harness v2
working_file_role: llm_only_operational_state
review_tier: S1_small
rounds_completed: 2
cto_call: CREATE_TEST_CONTRACTS_FILE_NOW
blockers: []
implementation_ready: true

post_implementation_review:
  mode: diff_review
  roles:
    - be
    - qc
    - devops
    - docs-gardener
    - cto
  input_only:
    - git diff
    - changed files
    - verification output
    - .codex/tasks/current.json
    - docs/gates/P1_DTO_CONTRACT_TESTS.md
```

## 5. LATEST_VERIFICATION

```yaml
codex_harness_bootstrap:
  status: passed
  implemented:
    - WORKING.md LLM-only operational state ledger
    - AGENTS.md Role-Gated Harness policy
    - AGENTS.md WORKING state priority and harness promotion rules
    - .codex/config.toml
    - .codex/agents/*.toml
    - .codex/tasks/current.json
    - .codex/hooks.json
    - .codex/hooks/pre_bash_guard.py
    - .codex/hooks/stop_guard.py
    - .codex/rules/halo.rules
    - .agents/skills/role-gated-harness/SKILL.md
    - .agents/skills/role-gated-harness/references/harness-promotion.md
    - docs/gates/P1_DTO_CONTRACT_TESTS.md
    - docs/reviews/P1_DTO_CONTRACT_TESTS/README.md

checks:
  codex_task_json_validity: passed
  codex_agent_toml_validity: passed
  codex_hook_python_syntax: passed
  contracts_import_check: passed
  golden_fixture_json_validity: passed
  golden_fixture_contract_validation: passed
  health_check: passed
  pytest: "3 passed"
  ruff: passed
```

## 6. HARNESS_PROMOTION_RULE

```yaml
rule: if_the_same_role_finding_appears_twice_promote_it
promotion_targets:
  - test
  - hook
  - rule
  - linter_or_security_scan
  - AGENTS.md rule
  - skill instruction
  - ADR
  - backlog item

examples:
  scope_violation: Stop hook
  risky_command: .codex/rules
  fixture_local_path: pytest path scan
  secrets_leak: detect-secrets or security scan
  dependency_risk: pip-audit or dependency gate
  llm_numeric_authority: contract test or eval
  docs_stale: docs freshness check
```

## 7. ARCHIVED_REVIEW_LEDGER

Do not execute this section directly. Use only when asked to explain prior
reasoning or recover a review decision.

```yaml
archived_sources:
  p1_planning_log: docs/archive/p1-dto-contract-planning-log.md
  p1_contract_tests_gate: docs/gates/P1_DTO_CONTRACT_TESTS.md
  p1_contract_tests_reviews: docs/reviews/P1_DTO_CONTRACT_TESTS/

active_source_of_execution:
  - CURRENT_DIRECTIVE
  - .codex/tasks/current.json
```
