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
status: AUDIT_WEB_VIEWER_VERIFIED
gate_id: AUDIT_WEB_VIEWER
review_tier: S2_medium

next_atomic_step: none; audit logging and web viewer verified

allowed_edit_paths:
  - src/halo_swing_mcp/
  - tests/
  - docs/
  - README.md

blocked_path_prefixes:
  - src/halo_swing_mcp/broker/
  - src/halo_swing_mcp/live_adapters/
  - migrations/
  - data/
  - artifacts/
  - state/

blocked_exact_paths:
  - requirements.txt

required_verification:
  - PYTHONPATH=src ./.venv/bin/python -m pytest
  - PYTHONPATH=src ./.venv/bin/python -m ruff check .
  - PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check
  - PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_audit_log
  - PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.audit_web local smoke
  - CLI smoke for representative MVP tools

done_means:
  - all CONTEXT initial MCP tools are registered in health_check and server
  - audit events are appended for CLI harness and MCP server tool calls
  - audit details redact likely secret-bearing keys
  - audit events can be read through get_audit_log and summarized through get_audit_summary
  - audit log web viewer serves HTML plus /api/events and /api/summary
  - deterministic fixture/replay path exists for market, macro, events, news
  - indicator, scoring, guide, position, ledger, labeling, feedback, chart tools work through harness
  - tests cover DTO contracts, MVP tool invariants, and audit/web payloads
  - no dependency, broker, live API, order execution, DB/data artifact changes are added
  - README, DevOps guide, SSOT, and WORKING reflect audit/web status

next_state_after_success: AUDIT_WEB_VIEWER_VERIFIED
```

Previous completed directive:

```yaml
p1_dto_contract_tests:
  status: DTO_CONTRACT_SLICE_SIGNOFF
  changed_files:
  - tests/test_contracts.py
  - docs/WORKING.md
```

## 2. CURRENT_TASK_CONTRACT

```yaml
task_contract: user directive 2026-05-09: make auditing possible and view audit logs on the web
portable_mirror: docs/halo-swing-development-plan.md#3.22
gate_packet: audit log and web viewer record in SSOT

read_only_context:
  - AGENTS.md
  - docs/CONTEXT.md
  - docs/halo-swing-development-plan.md#3.22
  - src/halo_swing_mcp/audit.py
  - src/halo_swing_mcp/audit_web.py
  - src/halo_swing_mcp/contracts.py
  - src/halo_swing_mcp/fixtures.py
  - src/halo_swing_mcp/indicators.py
  - src/halo_swing_mcp/strategy.py
  - src/halo_swing_mcp/tools/
  - tests/golden/

implementation_rule:
  - keep reusable module boundaries
  - keep default execution offline and deterministic
  - keep audit logging as a reusable cross-cutting module
  - keep web viewer local-only by default
  - do not implement automatic order execution
  - do not add live API dependencies or secrets
  - verify through tests and CLI harness
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
    - tests/test_contracts.py
  active_next:
    - DTO_CONTRACT_SLICE_SIGNOFF

offline_mvp:
  status: verified
  mode: fixture_replay_default
  implemented:
    - src/halo_swing_mcp/fixtures.py
    - src/halo_swing_mcp/indicators.py
    - src/halo_swing_mcp/strategy.py
    - src/halo_swing_mcp/tools/market.py
    - src/halo_swing_mcp/tools/scoring.py
    - src/halo_swing_mcp/tools/recording.py
    - src/halo_swing_mcp/server.py
    - src/halo_swing_mcp/harness.py
    - tests/test_mvp_tools.py
    - tests/golden/mvp_tool_contracts.json
  not_implemented_by_design:
    - live market/news adapters
    - broker or automatic order execution
    - SQLite migrations/repository persistence

audit_web:
  status: verified
  implemented:
    - src/halo_swing_mcp/audit.py
    - src/halo_swing_mcp/audit_web.py
    - src/halo_swing_mcp/tools/audit_tools.py
    - harness audit event integration
    - MCP server audit event integration
    - get_audit_log tool
    - get_audit_summary tool
    - tests/test_audit.py
  web:
    local_url: http://127.0.0.1:8765
    endpoints:
      - /
      - /api/events
      - /api/summary
```

## 4. ACTIVE_REVIEW_SUMMARY

```yaml
methodology: Role-Gated Codex Harness v2
working_file_role: llm_only_operational_state
review_tier: S2_medium
rounds_completed: implementation only after explicit user directive
cto_call: AUDIT_LOG_JSONL_AND_LOCAL_WEB_VIEWER_KEEP_RUNTIME_ARTIFACTS_IGNORED
blockers: []
implementation_ready: true

post_implementation_review:
  mode: final_completion_audit
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
    - docs/CONTEXT.md
    - docs/halo-swing-development-plan.md#3.22
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
  pytest: "31 passed"
  ruff: passed

p1_dto_contract_tests:
  status: passed
  changed_files:
    - tests/test_contracts.py
    - docs/WORKING.md
  verification:
    - command: PYTHONPATH=src ./.venv/bin/python -m pytest
      result: "16 passed"
    - command: PYTHONPATH=src ./.venv/bin/python -m ruff check .
      result: passed
    - command: PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check
      result: passed
  blocked_paths_changed: false
  db_data_artifact_or_state_files_added: false
  dependency_changes: false

offline_mvp_final:
  status: passed
  changed_files:
    - README.md
    - docs/WORKING.md
    - docs/devops-setup-guide.md
    - docs/halo-swing-development-plan.md
    - src/halo_swing_mcp/config.py
    - src/halo_swing_mcp/contracts.py
    - src/halo_swing_mcp/fixtures.py
    - src/halo_swing_mcp/harness.py
    - src/halo_swing_mcp/indicators.py
    - src/halo_swing_mcp/server.py
    - src/halo_swing_mcp/strategy.py
    - src/halo_swing_mcp/tools/health.py
    - src/halo_swing_mcp/tools/market.py
    - src/halo_swing_mcp/tools/recording.py
    - src/halo_swing_mcp/tools/scoring.py
    - tests/golden/health_check.json
    - tests/golden/mvp_tool_contracts.json
    - tests/test_mvp_tools.py
  verification:
    - command: PYTHONPATH=src ./.venv/bin/python -m pytest
      result: "26 passed"
    - command: PYTHONPATH=src ./.venv/bin/python -m ruff check .
      result: passed
    - command: PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check
      result: passed
    - command: CLI smoke for market, indicators, scoring, guide, chart, record, label, performance, champion/challenger
      result: passed
  blocked_paths_changed: false
  db_data_artifact_or_state_files_added: false
  dependency_changes: false
  live_api_or_broker_added: false

audit_web_final:
  status: passed
  changed_files:
    - README.md
    - docs/WORKING.md
    - docs/devops-setup-guide.md
    - docs/halo-swing-development-plan.md
    - src/halo_swing_mcp/audit.py
    - src/halo_swing_mcp/audit_web.py
    - src/halo_swing_mcp/config.py
    - src/halo_swing_mcp/harness.py
    - src/halo_swing_mcp/server.py
    - src/halo_swing_mcp/tools/audit_tools.py
    - src/halo_swing_mcp/tools/health.py
    - tests/golden/health_check.json
    - tests/golden/mvp_tool_contracts.json
    - tests/test_audit.py
    - tests/test_health_check.py
    - tests/test_mvp_tools.py
  verification:
    - command: PYTHONPATH=src ./.venv/bin/python -m pytest
      result: "31 passed"
    - command: PYTHONPATH=src ./.venv/bin/python -m ruff check .
      result: passed
    - command: PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --audit-log-path /private/tmp/halo_swing_audit_verify.jsonl
      result: passed
    - command: PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_audit_log --input-json '{"audit_log_path":"/private/tmp/halo_swing_audit_verify.jsonl","limit":5}' --audit-log-path /private/tmp/halo_swing_audit_verify.jsonl
      result: passed
    - command: PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.audit_web --host 127.0.0.1 --port 8765 --audit-log-path /private/tmp/halo_swing_audit_verify.jsonl
      result: running at http://127.0.0.1:8765
    - command: GET http://127.0.0.1:8765/api/summary
      result: passed
  blocked_paths_changed: false
  repo_runtime_artifacts_added: false
  dependency_changes: false
  live_api_or_broker_added: false
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
  - docs/halo-swing-development-plan.md#3.21
```
