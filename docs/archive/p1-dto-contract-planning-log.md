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
status: p1_contract_tests_work_order_ready
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
  - P0 close commit pushed to origin/main
  - P1 storage/schema decision log draft added to SSOT
  - P1 team detailed plans and two-round cross-review documented
  - FE/DB/BE/QC/DevOps/Docs sign-off recorded in SSOT P1 decision log
  - CTO DECISION_LOG_GO recorded in SSOT P1 decision log
  - P1 DTO contract next-action plan, two cross-check rounds, and CTO synthesis documented
  - P1 DTO_CONTRACT_GO approval packet, team reviews, and CTO synthesis documented
  - P1 DTO_CONTRACT_GO sign-off execution plan, team reviews, and CTO synthesis documented
  - P1 DTO contract implementation plan after GO, team reviews, and CTO synthesis documented
  - CTO DTO_CONTRACT_GO recorded in SSOT and WORKING
  - P1 DTO contract execution plan, two cross-check rounds, and CTO synthesis documented
  - P1 contracts.py first execution step plan, two cross-check rounds, and CTO synthesis documented
  - P1 contracts.py model spec plan, two cross-check rounds, and CTO synthesis documented
  - P1 contracts.py implementation work order, two cross-check rounds, and CTO synthesis documented
  - P1 contracts.py file creation checklist, two cross-check rounds, and CTO synthesis documented
  - P1 contracts.py create action final sign-off, two cross-check rounds, and CTO synthesis documented
  - src/halo_swing_mcp/contracts.py created from approved work order
  - contracts.py import-check passed
  - health_check, pytest, and ruff passed after contracts.py creation
  - P1 golden fixture creation next action defined with team plan, two cross-check rounds, and CTO synthesis
  - P1 golden fixture work order defined with fixture-level plan, two cross-check rounds, and CTO synthesis
  - P1 golden fixture create action final sign-off documented with two cross-check rounds and CTO synthesis
  - P1 golden fixture JSON files created
  - golden fixture JSON validity check passed
  - golden fixtures validate against contracts.py models
  - P1 contract tests next action defined with team plan, two cross-check rounds, and CTO synthesis
  - P1 contract tests work order defined with test-level plan, two cross-check rounds, and CTO synthesis
not_started:
  - strategy_config JSON/schema
  - run_journal/checkpoint/watchdog
  - supervisor/restart/backpressure/circuit-breaker runtime hardening
  - market data adapters
  - scoring engine
```

## Active Task

```yaml
doing: P1 contract tests work order reviewed
next_atomic_step: create tests/test_contracts.py exactly from work order, then run full verification
success_criteria:
  - PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check passes
  - PYTHONPATH=src ./.venv/bin/python -m pytest passes
  - PYTHONPATH=src ./.venv/bin/python -m ruff check . passes
  - server module imports and exposes halo_swing_mcp FastMCP server
  - SQLite/schema work is explicitly deferred to P1
  - SSOT P1 decision log exists before migration/repository code
  - FE/DB/BE/QC/DevOps/Docs sign-off is recorded in SSOT
  - CTO DECISION_LOG_GO is recorded in SSOT
  - CTO DTO_CONTRACT_GO is recorded in SSOT
guardrails:
  - DTO contract code is allowed only within approved contracts/fixtures/tests scope
  - migration/DDL code still requires MIGRATION_GO
  - repository persistence code still requires REPOSITORY_GO
approved_write_scope:
  - src/halo_swing_mcp/contracts.py
  - tests/golden/latest_signal_report.json
  - tests/golden/latest_signal_report_degraded.json
  - tests/golden/signal_replay_bundle.json
  - tests/golden/storage_health.json
  - tests/test_contracts.py
latest_verification:
  contracts_import_check: passed
  golden_fixture_json_validity: passed
  golden_fixture_contract_validation: passed
  health_check: passed
  pytest: "3 passed"
  ruff: passed
created_fixture_files:
  - tests/golden/latest_signal_report.json
  - tests/golden/latest_signal_report_degraded.json
  - tests/golden/signal_replay_bundle.json
  - tests/golden/storage_health.json
```

## P1 Contract Tests Work Order

```yaml
scope: execution-order action 3 work order for tests/test_contracts.py
mode: planning_only_no_code
target_file: tests/test_contracts.py
source_of_truth:
  contracts: src/halo_swing_mcp/contracts.py
  fixtures:
    - tests/golden/latest_signal_report.json
    - tests/golden/latest_signal_report_degraded.json
    - tests/golden/signal_replay_bundle.json
    - tests/golden/storage_health.json
  ssot_plan: docs/halo-swing-development-plan.md#320-p1-contract-tests-work-order

team_detailed_plans:
  fe:
    objective: preserve report semantics while avoiding brittle prose assertions.
    detailed_plan:
      - add test_latest_signal_report_fixtures_validate_and_contrast.
      - load normal and degraded report fixtures.
      - validate with LatestSignalReport.
      - assert normal.action is TradeAction.BUY_2X and degraded.action is TradeAction.WAIT.
      - assert degraded.confidence < normal.confidence.
      - assert summary fields are non-empty strings in both fixtures.
      - do not compare exact prose.
    acceptance:
      - report contrast is executable.
      - no UI/Telegram concern enters tests.
  db:
    objective: preserve replay traceability and avoid persistence leakage.
    detailed_plan:
      - add test_signal_replay_bundle_fixture_validates_and_preserves_links.
      - validate SignalReplayBundle fixture.
      - assert named sections are present in the parsed fixture.
      - assert signal.config_hash equals strategy_config.config_hash.
      - assert signal.run_id equals run_journal.run_id.
      - assert evidence_cards length is at least 2.
      - do not import sqlite3 or create DB connections.
    acceptance:
      - replay fixture remains structured.
      - no DB implementation is introduced.
  be:
    objective: implement stable contract round-trip tests.
    detailed_plan:
      - define ROOT, GOLDEN_DIR, load_json helper.
      - add assert_round_trip helper using model.model_validate(payload).model_dump(mode="json").
      - add round-trip tests for normal report, degraded report, replay bundle, storage_health.
      - add test_missing_required_field_fails by deleting signal_id.
      - add test_invalid_action_enum_fails by setting action to HOLD.
      - use pytest.raises(ValidationError).
    acceptance:
      - fixture changes and model changes fail deterministically.
      - no server/Hermes/DB imports.
  qc:
    objective: enforce negative, portability, and no-artifact checks.
    detailed_plan:
      - add recursive string walker for fixture payloads.
      - add test_golden_fixtures_do_not_contain_local_paths_or_db_artifacts.
      - flag /Users/, file://, ~/, .sqlite, .sqlite3, and drive-root-like prefixes.
      - add test_contract_tests_do_not_leave_sqlite_artifacts.
      - scan ROOT.rglob("*.sqlite") and ROOT.rglob("*.sqlite3").
    acceptance:
      - local-path regressions fail.
      - accidental DB artifacts fail.
  devops:
    objective: keep tests offline and dependency-neutral.
    detailed_plan:
      - use only json, re, pathlib, pytest, pydantic ValidationError, and halo_swing_mcp.contracts.
      - do not fetch example.invalid refs.
      - do not use jq, shell, network, env vars, browser, DB, or temp persistent files.
      - keep tests deterministic under .venv.
    acceptance:
      - no dependency changes.
      - no runtime service or local state requirement.
  docs_gardener:
    objective: keep docs aligned after executable tests exist.
    detailed_plan:
      - after implementation, update WORKING with tests/test_contracts.py created and verification results.
      - do not paste test code into docs.
      - next step becomes DTO contract slice sign-off.
      - keep MIGRATION_GO and REPOSITORY_GO blocked.
    acceptance:
      - docs reflect executable contract status.
      - no gate is accidentally opened.

round_1_cross_check:
  fe_to_be:
    issue: summary field list should be explicit to avoid missing one.
    required_change: define SUMMARY_FIELDS tuple in test file.
  be_to_fe:
    issue: summary non-empty check should cover both fixtures without duplicated loops.
    required_change: helper loops over [normal, degraded] models.
  db_to_be:
    issue: named sections should be checked on raw payload, not only model.
    required_change: assert expected keys subset of replay_payload.keys().
  be_to_db:
    issue: expected key set should not over-constrain future optional additions.
    required_change: use subset check, not exact equality.
  qc_to_devops:
    issue: drive-root regex should be simple and not over-match normal text.
    required_change: match ^[A-Za-z]:[\\/].
  devops_to_qc:
    issue: tilde check should catch "~/", not every tilde in prose.
    required_change: flag strings starting with "~/", not containing "~" anywhere.
  docs_to_all:
    issue: test implementation should close DTO contract executable slice.
    required_change: after tests pass, WORKING next step should be DTO slice sign-off.

round_1_improved_plans:
  fe:
    - SUMMARY_FIELDS tuple is explicit.
  db:
    - replay named sections use subset check.
  be:
    - round-trip helper is shared.
  qc:
    - local path checks are precise enough for fixtures.
  devops:
    - no external fetch or shell dependency.
  docs_gardener:
    - next state after implementation is DTO contract slice sign-off.

round_2_cross_check:
  fe_to_qc:
    issue: degraded data_warnings should be non-empty.
    final_change: report contrast test asserts normal.data_warnings == [] and degraded.data_warnings truthy.
  qc_to_fe:
    issue: direct empty-list comparison is stable for normal fixture.
    final_change: keep exact [] assertion for normal warnings.
  db_to_qc:
    issue: no-DB-artifact check may see committed future DB fixtures after MIGRATION_GO.
    final_change: current test remains valid until MIGRATION_GO; future gate may update it.
  qc_to_db:
    issue: this should not block current DTO stage.
    final_change: keep no-DB check now and document as DTO-stage guard.
  be_to_devops:
    issue: path scan should inspect every fixture, not only new strings in reports.
    final_change: scan all four DTO golden fixture payloads.
  cto_to_all:
    issue: work order is concrete enough.
    final_change: next action should create tests/test_contracts.py and run verification.

round_2_final_improved_plans:
  fe:
    final_gate: FE_READY_FOR_TEST_CONTRACTS_FILE
    final_requirements:
      - action/confidence/warning contrast is tested.
  db:
    final_gate: DB_READY_FOR_TEST_CONTRACTS_FILE
    final_requirements:
      - replay trace keys and linked IDs are tested.
  be:
    final_gate: BE_READY_FOR_TEST_CONTRACTS_FILE
    final_requirements:
      - round-trip and negative validation helpers are defined.
  qc:
    final_gate: QC_READY_FOR_TEST_CONTRACTS_FILE
    final_requirements:
      - path scan and no-DB-artifact checks are included.
  devops:
    final_gate: DEVOPS_READY_FOR_TEST_CONTRACTS_FILE
    final_requirements:
      - tests are offline and dependency-neutral.
  docs_gardener:
    final_gate: DOCS_READY_FOR_TEST_CONTRACTS_FILE
    final_requirements:
      - post-test next step is DTO slice sign-off.

cto_synthesis:
  call: CREATE_TEST_CONTRACTS_FILE_NOW
  recommendation: proceed with tests/test_contracts.py
  exact_next_action:
    - create tests/test_contracts.py with the helpers and tests above
    - run PYTHONPATH=src ./.venv/bin/python -m pytest
    - run PYTHONPATH=src ./.venv/bin/python -m ruff check .
    - run PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check
    - update WORKING with test creation and verification result
  hard_limits:
    - no migration/repository/adapters/scoring/Hermes code
    - no dependency changes
    - no DB files or data directory creation
```

## P1 Contract Tests Creation Plan

```yaml
scope: execution-order action 3, create tests/test_contracts.py
mode: planning_only_no_code
target_file: tests/test_contracts.py
source_of_truth:
  contracts: src/halo_swing_mcp/contracts.py
  fixtures:
    - tests/golden/latest_signal_report.json
    - tests/golden/latest_signal_report_degraded.json
    - tests/golden/signal_replay_bundle.json
    - tests/golden/storage_health.json
  ssot_plan: docs/halo-swing-development-plan.md#319-p1-contract-tests-creation-plan

team_detailed_plans:
  fe:
    objective: ensure tests preserve report semantics without testing investment correctness.
    detailed_plan:
      - validate normal and degraded LatestSignalReport fixtures.
      - assert normal action is BUY_2X and degraded action is WAIT.
      - assert degraded confidence is lower than normal confidence.
      - assert both fixtures include entry/stop/take-profit/invalidation/risk summaries.
      - do not assert exact prose quality or trading correctness.
    acceptance:
      - report contrast is protected.
      - tests stay UI/Telegram independent.
  db:
    objective: ensure replay fixture remains structured and future-storage-friendly.
    detailed_plan:
      - validate SignalReplayBundle fixture.
      - assert replay bundle has named sections: signal, feature_snapshot, evidence_cards, strategy_config, run_journal, label_outcome, missing_links.
      - assert signal.config_hash equals strategy_config.config_hash.
      - assert run_id is present in signal and run_journal.
      - do not add DB, migration, repository, sqlite connection, or schema tests.
    acceptance:
      - replay structure is executable.
      - no persistence layer work is introduced.
  be:
    objective: create durable Pydantic contract tests.
    detailed_plan:
      - load fixtures using json and pathlib.
      - validate fixtures through LatestSignalReport, SignalReplayBundle, StorageHealth.
      - compare canonical model_dump(mode="json") payloads to parsed fixture payloads.
      - add invalid enum negative test.
      - add missing required field negative test.
    acceptance:
      - tests fail on contract drift.
      - tests do not require server, Hermes, DB, network, or filesystem state beyond fixtures.
  qc:
    objective: cover positive, negative, portability, and local-state safety checks.
    detailed_plan:
      - add round-trip tests for four fixtures.
      - add missing required field test by removing signal_id from latest_signal_report.
      - add invalid enum test by changing action to HOLD.
      - scan new fixture JSON strings recursively for /Users, file://, ~/, drive roots, .sqlite, .sqlite3.
      - assert no .sqlite/.sqlite3 files exist under repo after tests.
    acceptance:
      - both positive and negative contract paths are tested.
      - fixture portability is test-enforced.
  devops:
    objective: ensure tests are offline and dependency-neutral.
    detailed_plan:
      - use stdlib json/pathlib only plus pytest and existing contracts.
      - do not add jq, network checks, browser, cron, env, DB, or service dependencies.
      - path scan must inspect nested JSON strings without fetching refs.
      - no generated data directory or artifact directory is created.
    acceptance:
      - tests run with existing .venv and requirements.
      - no persistent local state is produced.
  docs_gardener:
    objective: keep docs aligned after executable contract tests exist.
    detailed_plan:
      - record this test plan in SSOT.
      - after implementation, update WORKING with tests created and verification results.
      - do not duplicate test code in docs.
      - next step after tests is DTO slice sign-off and then MIGRATION_GO planning.
    acceptance:
      - docs point to tests as executable contract.
      - migration/repository gates remain blocked.

round_1_cross_check:
  fe_to_qc:
    issue: exact summary prose checks would be brittle.
    required_change: test required summary fields are non-empty, not exact wording.
  qc_to_fe:
    issue: merely non-empty summaries may miss field swaps.
    required_change: assert all five summary fields are present and strings; leave semantic nuance to fixture review.
  db_to_be:
    issue: canonical dump may coerce enum objects to strings.
    required_change: compare model_dump(mode="json") against parsed JSON payloads.
  be_to_db:
    issue: model_dump may include defaults for optional fields.
    required_change: fixtures include optional fields explicitly where expected, and comparison uses full payload.
  devops_to_qc:
    issue: path scan should not scan unrelated repo files.
    required_change: scan only the four new golden fixture files.
  docs_to_all:
    issue: no-DB-artifact check could fail on future deliberate DB work.
    required_change: keep the check scoped to current DTO contract tests until MIGRATION_GO.

round_1_improved_plans:
  fe:
    - tests assert summary field presence and string type.
  db:
    - canonical comparison uses model_dump(mode="json").
  be:
    - optional fixture fields are explicit enough for full comparison.
  qc:
    - path scan is limited to approved fixture files.
    - no-DB-artifact check remains a DTO-stage guard.
  devops:
    - no network or fetch behavior is added for example.invalid refs.
  docs_gardener:
    - docs will not copy test code.

round_2_cross_check:
  fe_to_be:
    issue: degraded-vs-normal confidence test depends on both fixtures loading first.
    final_change: load both report fixtures in one test and compare validated model values.
  be_to_fe:
    issue: action values should be enum instances after validation.
    final_change: compare to TradeAction.BUY_2X and TradeAction.WAIT, not raw strings.
  db_to_qc:
    issue: no-DB-artifact check needs a deterministic repo root.
    final_change: derive ROOT from Path(__file__).resolve().parents[1].
  qc_to_db:
    issue: scanning all repo paths for DB files can include ignored cache later.
    final_change: scan ROOT.rglob("*.sqlite") and ROOT.rglob("*.sqlite3") only.
  devops_to_be:
    issue: Windows drive-root pattern in tests should be simple and readable.
    final_change: use a small helper that flags strings starting with /Users/, file://, ~/, or matching a drive root prefix.
  cto_to_all:
    issue: plan is implementable without another gate.
    final_change: next action should create tests/test_contracts.py and run full verification.

round_2_final_improved_plans:
  fe:
    final_gate: FE_READY_FOR_CONTRACT_TESTS
    final_requirements:
      - report contrast is tested without prose brittleness.
  db:
    final_gate: DB_READY_FOR_CONTRACT_TESTS
    final_requirements:
      - replay structure and trace IDs are tested.
  be:
    final_gate: BE_READY_FOR_CONTRACT_TESTS
    final_requirements:
      - fixtures validate and round-trip through Pydantic models.
  qc:
    final_gate: QC_READY_FOR_CONTRACT_TESTS
    final_requirements:
      - positive, negative, path scan, and no-DB-artifact checks are included.
  devops:
    final_gate: DEVOPS_READY_FOR_CONTRACT_TESTS
    final_requirements:
      - tests are offline, dependency-neutral, and local-state free.
  docs_gardener:
    final_gate: DOCS_READY_FOR_CONTRACT_TESTS
    final_requirements:
      - docs record intent only and preserve gate locks.

cto_synthesis:
  call: CREATE_CONTRACT_TESTS_NEXT
  recommendation: proceed with tests/test_contracts.py
  exact_next_action:
    - create tests/test_contracts.py
    - run PYTHONPATH=src ./.venv/bin/python -m pytest
    - run PYTHONPATH=src ./.venv/bin/python -m ruff check .
    - run health_check
    - update WORKING with test creation and verification result
  hard_limits:
    - no migration/repository/adapters/scoring/Hermes code
    - no dependency changes
    - no DB files or data directory creation
```

## P1 Golden Fixture Create Action Final Sign-Off

```yaml
scope: final team sign-off for execution-order action 2
mode: planning_only_no_code
target_files:
  - tests/golden/latest_signal_report.json
  - tests/golden/latest_signal_report_degraded.json
  - tests/golden/signal_replay_bundle.json
  - tests/golden/storage_health.json
source_of_truth:
  work_order: docs/halo-swing-development-plan.md#317-p1-golden-fixture-work-order
  create_signoff: docs/halo-swing-development-plan.md#318-p1-golden-fixture-create-action-final-sign-off

team_detailed_plans:
  fe:
    objective: final sign-off that report examples are sufficient and non-UI.
    detailed_plan:
      - normal report fixture remains BUY_2X with confidence 0.72 and no warnings.
      - degraded report fixture remains WAIT with confidence 0.38 and non-empty warnings.
      - both report fixtures include distinct entry/stop/take-profit/invalidation/risk summaries.
      - no additional report fields are introduced during fixture creation.
    signoff: FE_GO_CREATE_GOLDEN_FIXTURES
    rejection_condition: fixture adds UI/dashboard/copy-only fields or changes action contrast.
  db:
    objective: final sign-off that replay fixture is structured and traceable.
    detailed_plan:
      - replay fixture keeps named sections.
      - signal and strategy_config share config_hash.
      - run_id appears in signal and run_journal.
      - no schema/table/SQL vocabulary appears in JSON.
    signoff: DB_GO_CREATE_GOLDEN_FIXTURES
    rejection_condition: replay fixture becomes one opaque blob or leaks schema terms.
  be:
    objective: final sign-off that fixtures match current contracts.py.
    detailed_plan:
      - keys match Pydantic field names.
      - enum strings match uppercase values.
      - latest_migration uses null.
      - JSON is valid and two-space formatted.
    signoff: BE_GO_CREATE_GOLDEN_FIXTURES
    rejection_condition: fixture requires contracts.py change in this action.
  qc:
    objective: final sign-off that fixtures are ready for future tests.
    detailed_plan:
      - degraded confidence remains lower than normal.
      - normal data_warnings is [] and degraded data_warnings is non-empty.
      - required fields are present.
      - fixture content does not imply trading correctness.
    signoff: QC_GO_CREATE_GOLDEN_FIXTURES
    rejection_condition: degraded-vs-normal checks are not possible.
  devops:
    objective: final sign-off that fixtures are portable.
    detailed_plan:
      - refs use example.invalid and are not fetched.
      - no local path, file URL, home path, drive root, sqlite artifact string.
      - fixed UTC timestamps only.
      - no new directories outside tests/golden.
    signoff: DEVOPS_GO_CREATE_GOLDEN_FIXTURES
    rejection_condition: fixture contains machine-specific or local-state string.
  docs_gardener:
    objective: final sign-off that planning is closed for fixture creation.
    detailed_plan:
      - do not add another planning layer for these four fixtures.
      - after creation, record created files and JSON validity result in WORKING.
      - next step is tests/test_contracts.py.
      - keep migration/repository gates blocked.
    signoff: DOCS_GO_CREATE_GOLDEN_FIXTURES
    rejection_condition: fixture action planning continues without scope change.

round_1_cross_check:
  fe_to_qc:
    issue: confidence values are good but summaries must also be distinct.
    required_change: entry/stop/take-profit/invalidation/risk summaries use different phrases in normal vs degraded fixtures.
  qc_to_fe:
    issue: phrase differences should not become brittle tests.
    required_change: future tests assert required fields and confidence/warning contrast, not exact prose.
  db_to_be:
    issue: evidence_cards should have at least two examples for replay usefulness.
    required_change: include macro_policy and market_technical example cards.
  be_to_db:
    issue: evidence card taxonomy should not become final schema.
    required_change: card values are examples only and remain dict payloads.
  devops_to_be:
    issue: example.invalid refs must be clearly non-fetch.
    required_change: use example.invalid consistently for chart/news refs and do not add fetch instructions.
  docs_to_all:
    issue: this is the second fixture planning layer.
    required_change: CTO synthesis must close planning and move to file creation.

round_1_improved_plans:
  fe:
    - summaries differ between normal and degraded fixtures.
  db:
    - evidence_cards has two example dicts.
  be:
    - all examples remain contract payloads, not schemas.
  qc:
    - future tests avoid exact prose assertions.
  devops:
    - example.invalid is consistent and non-fetch.
  docs_gardener:
    - this is final fixture planning artifact.

round_2_cross_check:
  fe_to_devops:
    issue: action examples should not imply live recommendation.
    final_change: fixture IDs/timestamps and example.invalid refs make payload clearly synthetic.
  devops_to_fe:
    issue: "synthetic" text field is not part of contract.
    final_change: do not add synthetic marker fields; keep synthetic nature in fixed IDs/refs/docs.
  db_to_qc:
    issue: storage_health has no DB tables yet but driver sqlite could confuse.
    final_change: storage_health represents target driver with migration_count 0 and no domain tables.
  qc_to_db:
    issue: target driver is acceptable because database_kind/driver are contract fields.
    final_change: keep driver/database_kind as sqlite.
  be_to_docs:
    issue: JSON validity check command should be simple and dependency-free.
    final_change: use .venv Python json.load loop, no jq dependency.
  cto_to_all:
    issue: planning is closed.
    final_change: next assistant action should create files and run JSON validity check.

round_2_final_improved_plans:
  fe:
    final_gate: FE_SIGNED_CREATE_GOLDEN_FIXTURES
    final_requirements:
      - normal/degraded semantic contrast preserved.
  db:
    final_gate: DB_SIGNED_CREATE_GOLDEN_FIXTURES
    final_requirements:
      - replay fixture structured and traceable.
  be:
    final_gate: BE_SIGNED_CREATE_GOLDEN_FIXTURES
    final_requirements:
      - fixtures match contracts.py without code changes.
  qc:
    final_gate: QC_SIGNED_CREATE_GOLDEN_FIXTURES
    final_requirements:
      - future validation tests are possible.
  devops:
    final_gate: DEVOPS_SIGNED_CREATE_GOLDEN_FIXTURES
    final_requirements:
      - fixtures are portable and non-fetch.
  docs_gardener:
    final_gate: DOCS_SIGNED_CREATE_GOLDEN_FIXTURES
    final_requirements:
      - no further planning for fixture creation unless scope changes.

cto_synthesis:
  call: CREATE_GOLDEN_FIXTURE_FILES_NOW_FINAL
  recommendation: implement immediately
  final_order:
    1: create tests/golden/latest_signal_report.json
    2: create tests/golden/latest_signal_report_degraded.json
    3: create tests/golden/signal_replay_bundle.json
    4: create tests/golden/storage_health.json
    5: run JSON validity check with .venv Python
    6: update WORKING with created files and JSON validity result
  hard_limits:
    - no further planning for fixture creation unless user changes scope
    - no tests/test_contracts.py in this action
    - no migration/repository/adapters/scoring/Hermes code
    - no dependency changes
```

## P1 Golden Fixture Work Order

```yaml
scope: execution-order action 2 work order for creating DTO golden fixtures
mode: planning_only_no_code
target_files:
  - tests/golden/latest_signal_report.json
  - tests/golden/latest_signal_report_degraded.json
  - tests/golden/signal_replay_bundle.json
  - tests/golden/storage_health.json
source_of_truth:
  contracts: src/halo_swing_mcp/contracts.py
  fixture_plan: docs/halo-swing-development-plan.md#316-p1-golden-fixture-creation-plan
  work_order: docs/halo-swing-development-plan.md#317-p1-golden-fixture-work-order

team_detailed_plans:
  fe:
    objective: define report fixture content that is readable but not presentation-bound.
    detailed_plan:
      - latest_signal_report.json should use action BUY_2X, action_label "Buy 2x swing", confidence 0.72, degraded_mode false, data_warnings [].
      - latest_signal_report_degraded.json should use action WAIT, action_label "Wait", confidence 0.38, degraded_mode true, and two data_warnings.
      - normal and degraded fixtures both include distinct entry_summary, stop_summary, take_profit_summary, invalidation_summary, and risk_summary.
      - optional reason_summary and evidence_summary should be filled with concise semantic examples; label_status may be null.
      - chart_ref may be an EXTERNAL https ArtifactRef for normal report and null for degraded report.
    acceptance:
      - degraded confidence is lower than normal confidence.
      - text examples are semantic and not final UI copy.
  db:
    objective: define replay fixture structure for future auditability.
    detailed_plan:
      - signal_replay_bundle.json includes signal.signal_id, signal.run_id, signal.config_hash, signal.action.
      - feature_snapshot includes feature_snapshot_id, asset, timeframe, observed_at, and a few numeric feature examples.
      - evidence_cards is a list with at least two cards: macro/news and market/technical.
      - strategy_config includes config_hash, version, status, weights.
      - run_journal includes run_id, started_at, finished_at, status.
      - label_outcome is null because labeling is not implemented.
      - missing_links is [] for the complete replay fixture.
    acceptance:
      - replay data is structured by named sections.
      - no schema/table/SQL terms appear.
  be:
    objective: make fixtures directly match contracts.py field names and enum values.
    detailed_plan:
      - use uppercase enum strings exactly as defined in contracts.py.
      - use fixed timestamps such as 2026-04-29T13:30:00Z.
      - storage_health.json uses status "ok", driver "sqlite", database_kind "sqlite", migration_count 0, latest_migration null, domain_tables_present [], live_data_required false.
      - use valid JSON with two-space indentation.
      - do not create tests/test_contracts.py in this action.
    acceptance:
      - fixture files are syntactically valid JSON.
      - no contract model change is required.
  qc:
    objective: make future contract tests deterministic.
    detailed_plan:
      - confidence values support degraded < normal.
      - data_warnings is explicitly [] for normal and non-empty for degraded.
      - all required LatestSignalReport fields are present in both report fixtures.
      - SignalReplayBundle missing_links is explicitly [].
      - storage_health reflects no migration/domain DB implementation.
    acceptance:
      - fixtures are ready for model_validate_json tests.
      - no assertion of trading correctness is implied.
  devops:
    objective: make fixture strings portable and path-scan safe.
    detailed_plan:
      - all refs use https://example.invalid/... or other reserved external example values.
      - no /Users, file://, ~/, C:\, .sqlite, or .sqlite3 strings.
      - no current date generation; timestamps are fixed strings.
      - create only the four approved JSON files.
    acceptance:
      - fixture content is machine independent.
      - no new runtime setup is introduced.
  docs_gardener:
    objective: keep docs and fixtures separated.
    detailed_plan:
      - SSOT records fixture work order, not full JSON payloads.
      - after fixture creation, WORKING records created files and JSON validity check.
      - next step remains tests/test_contracts.py planning or implementation.
      - keep migration/repository gates blocked.
    acceptance:
      - docs do not duplicate complete fixture contents.
      - approved write scope is not expanded.

round_1_cross_check:
  fe_to_qc:
    issue: degraded report should be visibly different from normal.
    required_change: degraded uses WAIT, confidence 0.38, two warnings, and stricter invalidation/risk wording.
  qc_to_fe:
    issue: prose should not become brittle in tests.
    required_change: future tests validate fields and canonical JSON, not subjective prose quality.
  db_to_be:
    issue: signal and strategy_config both need config_hash for replay traceability.
    required_change: include the same config_hash in both sections.
  be_to_db:
    issue: numeric feature examples should not define final indicator scale.
    required_change: use plausible values but treat them as example payload only.
  devops_to_be:
    issue: example domains should never be accidentally fetched.
    required_change: use example.invalid reserved domain for refs.
  docs_to_all:
    issue: storage_health fixture might imply DB exists.
    required_change: migration_count 0 and domain_tables_present [] make no-DB state explicit.

round_1_improved_plans:
  fe:
    - degraded fixture is clearly lower confidence and WAIT.
  db:
    - config_hash appears in signal and strategy_config.
  be:
    - example.invalid refs are used.
    - features are examples, not final feature schema.
  qc:
    - future tests avoid prose-quality assertions.
  devops:
    - no external fetch is implied by fixture URLs.
  docs_gardener:
    - storage_health no-DB state is explicit.

round_2_cross_check:
  fe_to_db:
    issue: chart_ref in normal report should align with artifact ref shape.
    final_change: chart_ref uses {"ref_type":"CHART","ref":"https://example.invalid/artifacts/halo-swing-chart.png","metadata":{"description":"Example chart artifact"}}.
  db_to_fe:
    issue: degraded chart_ref can be null because degraded mode may lack chart artifact.
    final_change: degraded chart_ref is null.
  be_to_qc:
    issue: JSON fixture key ordering should be stable but not over-optimized.
    final_change: manually order keys to match model field order for readability.
  qc_to_be:
    issue: storage_health latest_migration null must match Optional[str].
    final_change: use JSON null, not empty string.
  devops_to_docs:
    issue: example.invalid URLs should be documented as non-fetch fixtures.
    final_change: SSOT notes refs are examples only and tests must not fetch them.
  cto_to_all:
    issue: work order is concrete enough.
    final_change: next action should create the four fixture files.

round_2_final_improved_plans:
  fe:
    final_gate: FE_READY_FOR_FIXTURE_FILES
    final_requirements:
      - normal/degraded report fixtures are semantically distinct.
  db:
    final_gate: DB_READY_FOR_FIXTURE_FILES
    final_requirements:
      - replay fixture has traceable IDs and named sections.
  be:
    final_gate: BE_READY_FOR_FIXTURE_FILES
    final_requirements:
      - fixtures match contracts.py field names and enum strings.
  qc:
    final_gate: QC_READY_FOR_FIXTURE_FILES
    final_requirements:
      - fixtures are deterministic and future-test-ready.
  devops:
    final_gate: DEVOPS_READY_FOR_FIXTURE_FILES
    final_requirements:
      - refs are portable and non-fetch examples.
  docs_gardener:
    final_gate: DOCS_READY_FOR_FIXTURE_FILES
    final_requirements:
      - docs do not duplicate full JSON payloads.

cto_synthesis:
  call: CREATE_GOLDEN_FIXTURE_FILES_NOW
  recommendation: proceed with four JSON fixture files
  exact_next_action:
    - create tests/golden/latest_signal_report.json
    - create tests/golden/latest_signal_report_degraded.json
    - create tests/golden/signal_replay_bundle.json
    - create tests/golden/storage_health.json
    - run JSON validity check
    - update WORKING with created files and JSON check result
  hard_limits:
    - no tests/test_contracts.py in this action
    - no migration/repository/adapters/scoring/Hermes code
    - no dependency changes
```

## P1 Golden Fixture Creation Plan

```yaml
scope: execution-order action 2, create DTO golden fixtures after contracts.py
mode: planning_only_no_code
target_files:
  - tests/golden/latest_signal_report.json
  - tests/golden/latest_signal_report_degraded.json
  - tests/golden/signal_replay_bundle.json
  - tests/golden/storage_health.json
source_of_truth:
  contracts: src/halo_swing_mcp/contracts.py
  ssot_plan: docs/halo-swing-development-plan.md#316-p1-golden-fixture-creation-plan

team_detailed_plans:
  fe:
    objective: make report fixtures usable for first swing guidance examples.
    detailed_plan:
      - normal latest_signal_report fixture uses action BUY_2X, confidence above degraded fixture, empty data_warnings, degraded_mode false.
      - degraded report fixture uses action WAIT, degraded_mode true, non-empty data_warnings, and risk/invalidation text explaining reduced confidence.
      - both report fixtures include entry_summary, stop_summary, take_profit_summary, invalidation_summary, risk_summary.
      - fixture prose is example semantic content, not final Telegram/UI copy.
    acceptance:
      - normal and degraded examples can be read as plausible swing guidance.
      - no dashboard/layout fields appear.
  db:
    objective: keep fixtures replay-aware and future storage-mappable.
    detailed_plan:
      - signal_replay_bundle fixture includes signal, feature_snapshot, evidence_cards, strategy_config, run_journal, label_outcome, missing_links.
      - IDs are stable strings: signal_id, run_id, feature_snapshot_id, config_hash.
      - timestamps are fixed UTC ISO-8601 strings.
      - artifact refs use portable/external refs only.
    acceptance:
      - replay fixture is structured, not a single blob.
      - no schema/table/SQL details appear.
  be:
    objective: make fixtures validate directly against contracts.py models.
    detailed_plan:
      - each fixture key must match current Pydantic field names exactly.
      - enum values use uppercase strings from the enums.
      - optional fields may be present with useful example values or null.
      - JSON formatting should be stable with sorted-looking, human-readable key order.
    acceptance:
      - fixtures are ready for model_validate_json/model_validate in test step.
      - no fixture requires code changes to contracts.py.
  qc:
    objective: make fixtures ready for deterministic golden tests.
    detailed_plan:
      - normal/degraded confidence values should support degraded confidence < normal confidence.
      - degraded fixture must have non-empty data_warnings.
      - storage_health uses live_data_required false.
      - include values that will make missing-field and enum-negative tests meaningful later.
    acceptance:
      - fixture comparison can be parsed/canonical JSON, not raw string ordering.
      - no investment correctness is asserted by fixture values.
  devops:
    objective: keep fixtures portable and local-state free.
    detailed_plan:
      - no /Users, file://, ~/, Windows drive roots, .sqlite, or .sqlite3 strings.
      - allow https:// external refs.
      - no current-date generation; use fixed UTC timestamps.
      - no new directories outside approved golden files.
    acceptance:
      - fixture content is machine-independent.
      - no runtime setup or env var is needed.
  docs_gardener:
    objective: keep docs aligned and avoid duplicating fixture payloads.
    detailed_plan:
      - record this as action 2 plan in SSOT.
      - after fixture creation, WORKING records created files and validation status.
      - do not paste full fixture JSON into docs.
      - next action after fixtures is tests/test_contracts.py creation.
    acceptance:
      - docs keep next step clear.
      - MIGRATION_GO and REPOSITORY_GO remain blocked.

round_1_cross_check:
  fe_to_be:
    issue: normal and degraded report fixtures need contrasting guidance.
    required_change: normal uses BUY_2X, degraded uses WAIT with lower confidence.
  be_to_fe:
    issue: fixture action values must match enum casing exactly.
    required_change: use uppercase enum strings only.
  db_to_be:
    issue: replay fixture must include config_hash and run_id for future traceability.
    required_change: include config_hash in signal and strategy_config, and run_id in signal/run_journal.
  qc_to_fe:
    issue: degraded warning must be testable.
    required_change: degraded data_warnings is non-empty and confidence lower than normal.
  devops_to_db:
    issue: artifact refs can accidentally become local paths.
    required_change: use https:// or relative-like refs only; no file://.
  docs_to_all:
    issue: docs should not become a copy of fixture JSON.
    required_change: SSOT records fixture intent only.

round_1_improved_plans:
  fe:
    - normal/degraded fixtures intentionally contrast action and confidence.
  db:
    - traceability IDs are present in fixture sections.
  be:
    - enum strings must match contracts.py exactly.
  qc:
    - degraded confidence comparison is test-ready.
  devops:
    - fixture refs are path-scan safe by design.
  docs_gardener:
    - fixture JSON remains only in tests/golden.

round_2_cross_check:
  fe_to_qc:
    issue: BUY_2X example could look like advice.
    final_change: fixture values are deterministic examples only; tests verify schema, not trade correctness.
  qc_to_fe:
    issue: example prose should not be too generic to catch field mixups.
    final_change: summaries should mention distinct entry/stop/take-profit/invalidation concepts.
  db_to_devops:
    issue: relative refs need a future root policy.
    final_change: use https:// refs in first fixtures to avoid root ambiguity.
  devops_to_db:
    issue: future local artifact refs are still allowed later.
    final_change: first fixture uses external refs; local artifact root policy deferred.
  be_to_docs:
    issue: storage_health fixture should reflect no DB implementation yet.
    final_change: storage_health uses migration_count 0, latest_migration null, domain_tables_present [], live_data_required false.
  cto_to_all:
    issue: fixture creation can proceed without another gate.
    final_change: next action is to create the four approved JSON fixture files only.

round_2_final_improved_plans:
  fe:
    final_gate: FE_READY_FOR_GOLDEN_FIXTURES
    final_requirements:
      - report examples are semantically distinct and non-UI.
  db:
    final_gate: DB_READY_FOR_GOLDEN_FIXTURES
    final_requirements:
      - replay fixture is structured and traceable.
  be:
    final_gate: BE_READY_FOR_GOLDEN_FIXTURES
    final_requirements:
      - JSON keys/enums match contracts.py.
  qc:
    final_gate: QC_READY_FOR_GOLDEN_FIXTURES
    final_requirements:
      - degraded-vs-normal checks will be possible.
  devops:
    final_gate: DEVOPS_READY_FOR_GOLDEN_FIXTURES
    final_requirements:
      - fixture strings are portable and path-scan safe.
  docs_gardener:
    final_gate: DOCS_READY_FOR_GOLDEN_FIXTURES
    final_requirements:
      - docs record intent only and keep next action clear.

cto_synthesis:
  call: CREATE_GOLDEN_FIXTURES_NEXT
  recommendation: proceed with fixture creation
  exact_next_action:
    - create tests/golden/latest_signal_report.json
    - create tests/golden/latest_signal_report_degraded.json
    - create tests/golden/signal_replay_bundle.json
    - create tests/golden/storage_health.json
  hard_limits:
    - no tests/test_contracts.py in this action unless user asks to implement the whole remaining DTO slice
    - no migration/repository/adapters/scoring/Hermes code
    - no dependency changes
```

## P1 Contracts.py Create Action Final Sign-Off

```yaml
scope: final team sign-off for execution-order action 1
mode: planning_only_no_code
target_file: src/halo_swing_mcp/contracts.py
source_of_truth:
  file_creation_checklist: docs/halo-swing-development-plan.md#314-p1-contractspy-file-creation-checklist
  create_signoff: docs/halo-swing-development-plan.md#315-p1-contractspy-create-action-final-sign-off

team_detailed_plans:
  fe:
    objective: final report-contract sign-off before file creation.
    detailed_plan:
      - confirm LatestSignalReport field list is not reopened.
      - confirm normal/degraded report support remains built into required fields.
      - confirm TradeAction uppercase values are final for this file.
      - confirm no UI/copy/dashboard fields enter the model.
    signoff: FE_GO_CREATE_CONTRACTS_PY
    rejection_condition: report fields or action enum change during implementation.
  db:
    objective: final schema-neutral replay sign-off before file creation.
    detailed_plan:
      - confirm SignalReplayBundle named sections are final for this file.
      - confirm ArtifactRef and ReplayMissingLinkError stay structured.
      - confirm no persistence vocabulary or imports appear.
      - confirm section internals may remain JSON-compatible dict/list.
    signoff: DB_GO_CREATE_CONTRACTS_PY
    rejection_condition: any SQL/schema/repository concept appears in contracts.py.
  be:
    objective: final implementation-order sign-off before file creation.
    detailed_plan:
      - implement only the agreed single file.
      - follow file order exactly: imports, StrictBaseModel, enums, small models, main DTOs, __all__.
      - use only stdlib enum/typing and pydantic.
      - run import-check immediately after file creation.
    signoff: BE_GO_CREATE_CONTRACTS_PY
    rejection_condition: implementation touches fixtures/tests or adds dependencies.
  qc:
    objective: final testability sign-off before file creation.
    detailed_plan:
      - confirm required fields have no defaults.
      - confirm optional fields default to None only.
      - confirm data_warnings remains explicitly supplied.
      - confirm extra="forbid" makes drift testable.
    signoff: QC_GO_CREATE_CONTRACTS_PY
    rejection_condition: defaults or free strings make later tests weak.
  devops:
    objective: final portability sign-off before file creation.
    detailed_plan:
      - confirm import has no IO/env/network/current-time behavior.
      - confirm no new dependency or requirements change.
      - confirm ArtifactRef does not resolve paths.
      - confirm no runtime service/config is added.
    signoff: DEVOPS_GO_CREATE_CONTRACTS_PY
    rejection_condition: import has side effects or dependency changes.
  docs_gardener:
    objective: final docs sign-off before implementation.
    detailed_plan:
      - record this as the final planning artifact for contracts.py creation.
      - do not add another planning section for this same action.
      - after implementation, record only file-created and import-check result.
      - keep next planned step as golden fixture creation.
    signoff: DOCS_GO_CREATE_CONTRACTS_PY
    rejection_condition: planning continues without scope change.

round_1_cross_check:
  fe_to_be:
    issue: final_score unconstrained can confuse report users.
    required_change: keep final_score field named clearly; scale is intentionally deferred to scoring phase.
  be_to_fe:
    issue: adding a score scale now would be strategy logic.
    required_change: no final_score range validator in contracts.py.
  db_to_be:
    issue: metadata may later hide path data.
    required_change: allow metadata as plain dict now; path-scan test handles local path ban next.
  qc_to_be:
    issue: extra="forbid" must apply to all DTOs, not only main ones.
    required_change: every public model inherits StrictBaseModel.
  devops_to_be:
    issue: import-check should use the project venv and PYTHONPATH.
    required_change: use approved import-check command exactly.
  docs_to_all:
    issue: repeated planning has reached diminishing returns.
    required_change: CTO synthesis must close planning for this action.

round_1_improved_plans:
  fe:
    - final_score remains float without scale/range.
    - score scale waits for scoring engine.
  db:
    - metadata stays plain dict.
    - path safety is next-step fixture/test concern.
  be:
    - all models inherit StrictBaseModel.
    - no fixtures/tests/dependencies in this action.
  qc:
    - extra forbid is universal.
    - later negative tests are viable.
  devops:
    - import-check command is exact and local.
    - no runtime setup changes.
  docs_gardener:
    - this action should not receive another planning layer.

round_2_cross_check:
  fe_to_qc:
    issue: action_label has no validator tying it to action.
    final_change: keep no validator; fixture tests later ensure example consistency.
  qc_to_fe:
    issue: strict relationship tests would be brittle before formatter/scoring exists.
    final_change: only type/required-field validation belongs in contracts.py now.
  db_to_docs:
    issue: implementation outcome should not rewrite schema decision log.
    final_change: post-code update goes to WORKING current state only unless scope changes.
  docs_to_db:
    issue: SSOT should still mention MIGRATION_GO lock.
    final_change: keep migration/repository locks in all summaries.
  be_to_devops:
    issue: pydantic Field(default_factory=dict) is still a factory.
    final_change: allowed only for empty metadata; ban all dynamic/time/state factories.
  cto_to_all:
    issue: action is over-planned.
    final_change: next assistant action should implement the file.

round_2_final_improved_plans:
  fe:
    final_gate: FE_SIGNED_CREATE_CONTRACTS_PY
    final_requirements:
      - no report field changes during implementation.
      - no action enum scope change.
  db:
    final_gate: DB_SIGNED_CREATE_CONTRACTS_PY
    final_requirements:
      - no schema leakage.
      - no replay blob collapse.
  be:
    final_gate: BE_SIGNED_CREATE_CONTRACTS_PY
    final_requirements:
      - one-file implementation only.
      - universal StrictBaseModel.
  qc:
    final_gate: QC_SIGNED_CREATE_CONTRACTS_PY
    final_requirements:
      - required/default/enum behavior remains testable.
  devops:
    final_gate: DEVOPS_SIGNED_CREATE_CONTRACTS_PY
    final_requirements:
      - side-effect-free import and no dependency changes.
  docs_gardener:
    final_gate: DOCS_SIGNED_CREATE_CONTRACTS_PY
    final_requirements:
      - planning for this action is closed.
      - post-code docs update only records outcome.

cto_synthesis:
  call: CREATE_CONTRACTS_PY_NOW_FINAL
  recommendation: implement immediately
  final_order:
    1: add src/halo_swing_mcp/contracts.py
    2: run import-check exactly:
       PYTHONPATH=src ./.venv/bin/python -c "from halo_swing_mcp.contracts import LatestSignalReport"
    3: update WORKING with file-created and import-check result
    4: move to golden fixture creation
  hard_limits:
    - no further planning for contracts.py creation unless user changes scope
    - no fixtures/tests in this action
    - no migration/repository/adapters/scoring/Hermes code
    - no dependency changes
```

## P1 Contracts.py File Creation Checklist

```yaml
scope: final checklist for execution-order action 1, adding contracts.py
mode: planning_only_no_code
target_file: src/halo_swing_mcp/contracts.py
source_of_truth:
  work_order: docs/halo-swing-development-plan.md#313-p1-contractspy-implementation-work-order
  file_creation_checklist: docs/halo-swing-development-plan.md#314-p1-contractspy-file-creation-checklist

team_detailed_plans:
  fe:
    objective: confirm no report-critical field is missed when file is created.
    checklist:
      - LatestSignalReport includes all 18 required fields from SSOT 3.12.
      - Optional report enrichments remain optional: reason_summary, evidence_summary, label_status, chart_ref.
      - TradeAction includes only BUY_2X, BUY_3X, WAIT, TRIM, EXIT, STOP for first pass.
      - degraded_mode and data_warnings are required and not hidden behind optional metadata.
      - no UI/Telegram/dashboard-only fields are added.
    no_go:
      - report summary fields are missing
      - TradeAction casing differs from uppercase wire value
  db:
    objective: confirm contract file is schema-neutral and replay-aware.
    checklist:
      - SignalReplayBundle named sections are present.
      - label_outcome is optional.
      - signal/config/run/evidence sections are JSON-compatible but named.
      - ArtifactRef has ref_type, ref, metadata.
      - no sqlite3, SQL, repository, migration, table, column, database_url vocabulary/import appears.
    no_go:
      - one opaque replay blob replaces named sections
      - schema or persistence code appears
  be:
    objective: execute the file creation in the agreed internal order.
    checklist:
      - imports use enum, typing.Any, and pydantic only.
      - StrictBaseModel uses ConfigDict(extra="forbid").
      - enums are defined before models.
      - ArtifactRef and ReplayMissingLinkError are defined before main DTOs.
      - LatestSignalReport, SignalReplayBundle, StorageHealth are defined before __all__.
      - __all__ lists every public contract name.
      - confidence uses Field(ge=0, le=1); final_score is float with no range constraint.
    no_go:
      - validators introduce cross-field strategy logic
      - default_factory or current-time defaults appear
  qc:
    objective: confirm first file will be testable by the next action.
    checklist:
      - required fields have no defaults.
      - optional fields default to None only.
      - enum fields are typed as enums, not free str.
      - data_warnings is required list[str].
      - extra fields are forbidden through base model.
    no_go:
      - defaults hide missing required data
      - free-form strings replace planned enums
  devops:
    objective: confirm import is side-effect free and dependency neutral.
    checklist:
      - no os/pathlib/file/network/env imports.
      - no settings/config import.
      - no datetime.now/utcnow/default_factory.
      - no new dependency or requirements change.
      - ArtifactRef does not validate path existence.
    no_go:
      - import reads local state
      - dependency changes are needed
  docs_gardener:
    objective: keep this as the final planning checkpoint before code.
    checklist:
      - SSOT and WORKING both say next action is file creation now.
      - docs do not expand beyond contracts.py for this step.
      - after code, only implementation result and import-check result should be recorded.
      - next planned step remains golden fixture creation.
    no_go:
      - another planning layer is introduced without scope change
      - docs imply fixtures/tests are part of this file-only step

round_1_cross_check:
  fe_to_be:
    issue: optional chart_ref needs model type.
    required_change: chart_ref is ArtifactRef | None.
  be_to_fe:
    issue: optional report enrichments should not become required accidentally.
    required_change: reason_summary, evidence_summary, label_status, chart_ref default to None.
  db_to_be:
    issue: ReplayMissingLinkError should be structured enough for later persistence.
    required_change: include code, message, missing_ref_type, missing_ref_id.
  be_to_db:
    issue: missing_ref_id may be unknown.
    required_change: missing_ref_id can be str | None.
  qc_to_be:
    issue: metadata default can hide omitted field behavior.
    required_change: ArtifactRef.metadata can default to empty dict only if accepted as non-critical; otherwise require explicit metadata.
  devops_to_qc:
    issue: empty dict default can be mutable if implemented incorrectly.
    required_change: if metadata defaults, use Field(default_factory=dict); this is the only allowed default_factory and it is not time/state based.
  docs_to_all:
    issue: previous ban on default_factory was too broad for safe empty containers.
    required_change: allow default_factory only for empty collection defaults, ban dynamic/time/state factories.

round_1_improved_plans:
  fe:
    - chart_ref is ArtifactRef | None.
    - optional report enrichments default to None.
  db:
    - ReplayMissingLinkError includes structured missing ref fields.
    - missing_ref_id may be None.
  be:
    - default_factory is allowed only for empty collections such as metadata.
    - time/state default factories remain banned.
  qc:
    - mutable defaults must use safe empty collection factories.
    - required fields remain without defaults.
  devops:
    - default_factory=dict is accepted for empty metadata.
    - no dynamic IO/time/env factories.
  docs_gardener:
    - default policy is clarified before code.

round_2_cross_check:
  fe_to_qc:
    issue: data_warnings as required list may tempt default empty list.
    final_change: no default for data_warnings; fixtures must supply [] or non-empty list explicitly.
  qc_to_fe:
    issue: ArtifactRef.metadata default_factory is acceptable because it is not report-critical.
    final_change: metadata may use Field(default_factory=dict), but report required lists may not.
  db_to_devops:
    issue: ArtifactRef.ref_type values need first-pass enum.
    final_change: ArtifactRefType includes CHART, PDF, NEWS, EXTERNAL, OTHER.
  devops_to_db:
    issue: EXTERNAL should allow https evidence later.
    final_change: ref string remains unconstrained; fixture tests handle local path bans later.
  be_to_docs:
    issue: implementation details are now clear enough.
    final_change: CTO synthesis should explicitly say "implement next, no further planning".
  cto_to_all:
    issue: repeated planning is now higher risk than implementation.
    final_change: next response should create contracts.py unless user changes scope.

round_2_final_improved_plans:
  fe:
    final_gate: FE_READY_FOR_FILE_CREATE
    final_requirements:
      - report-required fields and action enum are locked.
      - no UI-only fields.
  db:
    final_gate: DB_READY_FOR_FILE_CREATE
    final_requirements:
      - replay errors and artifact refs are structured.
      - no schema leakage.
  be:
    final_gate: BE_READY_FOR_FILE_CREATE
    final_requirements:
      - safe empty collection default_factory allowed only for metadata.
      - no dynamic default factories.
  qc:
    final_gate: QC_READY_FOR_FILE_CREATE
    final_requirements:
      - data_warnings remains explicitly supplied.
      - optional/report fields policy is testable.
  devops:
    final_gate: DEVOPS_READY_FOR_FILE_CREATE
    final_requirements:
      - side-effect-free import.
      - no dependency changes.
  docs_gardener:
    final_gate: DOCS_READY_FOR_FILE_CREATE
    final_requirements:
      - next action is implementation, not planning.
      - post-code docs record outcome only.

cto_synthesis:
  call: CREATE_CONTRACTS_PY_NOW
  recommendation: implement now
  exact_next_action:
    - add src/halo_swing_mcp/contracts.py
    - run PYTHONPATH=src ./.venv/bin/python -c "from halo_swing_mcp.contracts import LatestSignalReport"
    - update WORKING with file-created and import-check result
  hard_limits:
    - no fixtures/tests in this file-only action
    - no migration/repository/adapters/scoring/Hermes code
    - no dependency changes
    - no further planning unless user changes scope
```

## P1 Contracts.py Implementation Work Order

```yaml
scope: final work order for implementing src/halo_swing_mcp/contracts.py
mode: planning_only_no_code
target_file: src/halo_swing_mcp/contracts.py
source_of_truth:
  model_spec_plan: docs/halo-swing-development-plan.md#312-p1-contractspy-model-spec-plan
  work_order: docs/halo-swing-development-plan.md#313-p1-contractspy-implementation-work-order

team_detailed_plans:
  fe:
    objective: protect report usefulness during code implementation.
    detailed_plan:
      - verify LatestSignalReport field names match the 3.12 required/optional field list.
      - verify TradeAction contains BUY_2X, BUY_3X, WAIT, TRIM, EXIT, STOP exactly for first pass.
      - keep degraded_mode and data_warnings required so degraded reports cannot be silently flattened into normal reports.
      - reject any field that is purely formatting, layout, dashboard filtering, or Telegram wording.
    acceptance:
      - LatestSignalReport can be instantiated later with both normal and degraded fixtures.
      - no UI/report-rendering concern leaks into contracts.py.
  db:
    objective: keep DTO implementation future-storage-friendly but schema-neutral.
    detailed_plan:
      - ensure SignalReplayBundle has named top-level sections rather than one raw payload field.
      - ensure identifiers and config_hash remain explicit.
      - accept dict/list detail inside named sections where evidence/features will evolve.
      - scan for forbidden vocabulary/imports: sqlite3, SQL, migration, repository, database_url, table, column.
    acceptance:
      - contracts.py has no persistence imports and no schema naming.
      - replay data is not hidden in one top-level blob.
  be:
    objective: write the file in a stable, minimal order.
    detailed_plan:
      - file header and imports: enum, typing Any, pydantic BaseModel/ConfigDict/Field if needed.
      - define a shared StrictBaseModel with model_config = ConfigDict(extra="forbid").
      - define enums first: TradeAction, DataFreshnessStatus, SignalStatus, ArtifactRefType, ReplayErrorCode.
      - define small models next: ArtifactRef, ReplayMissingLinkError.
      - define main DTOs next: LatestSignalReport, SignalReplayBundle, StorageHealth.
      - define __all__ last with the public contract names.
      - avoid validators unless they are trivial and local.
    acceptance:
      - `PYTHONPATH=src ./.venv/bin/python -c "from halo_swing_mcp.contracts import LatestSignalReport"` succeeds.
      - no server/config/storage/Hermes/network import.
  qc:
    objective: make the first file easy to test in the next step.
    detailed_plan:
      - confirm extra="forbid" is applied to all public models through StrictBaseModel.
      - confirm required fields have no default values.
      - confirm optional fields default only to None.
      - confirm enum fields use enum classes, not free strings.
      - confirm data_warnings is required list[str].
    acceptance:
      - future missing-field and invalid-enum tests will fail predictably.
      - no default hides required fixture data.
  devops:
    objective: keep implementation side-effect-free and dependency-neutral.
    detailed_plan:
      - use no imports outside stdlib and pydantic.
      - avoid datetime.now, datetime.utcnow, default_factory, pathlib, os, environment reads, network clients, or file reads.
      - keep timestamps as str.
      - keep ArtifactRef as data only; do not resolve or validate path existence.
    acceptance:
      - import has no IO/env/network/current-time side effect.
      - requirements.txt does not change.
  docs_gardener:
    objective: make implementation status easy to record after code.
    detailed_plan:
      - after code, update WORKING with file created and import-check result only.
      - do not copy full code into docs.
      - keep next planned action as golden fixture creation.
      - keep MIGRATION_GO and REPOSITORY_GO blocked.
    acceptance:
      - docs remain a planning trail, code becomes executable source of truth.
      - approved write scope remains unchanged.

round_1_cross_check:
  fe_to_be:
    issue: enum values should be stable for report fixtures.
    required_change: implement TradeAction as string values identical to enum names/lower-level wire values agreed in code.
  be_to_fe:
    issue: exact casing affects fixtures.
    required_change: use uppercase string values matching action names for first pass.
  db_to_be:
    issue: SignalReplayBundle named fields need clear types without schema freeze.
    required_change: use dict[str, Any] for signal, feature_snapshot, strategy_config, run_journal, label_outcome and list[dict[str, Any]] for evidence_cards, plus list[ReplayMissingLinkError] for missing_links.
  be_to_db:
    issue: label_outcome may be absent.
    required_change: label_outcome should be optional.
  qc_to_be:
    issue: optional chart_ref and ArtifactRef need type clarity.
    required_change: chart_ref should be ArtifactRef | None.
  devops_to_be:
    issue: Field descriptions are fine, but no dynamic defaults.
    required_change: use Field only for static metadata/ranges, never default_factory.
  docs_to_all:
    issue: confidence range was undecided.
    required_change: use simple Field(ge=0, le=1) for confidence if pydantic already supports it without extra complexity.

round_1_improved_plans:
  fe:
    - TradeAction string values use uppercase action names.
    - chart_ref is typed as ArtifactRef | None.
  db:
    - SignalReplayBundle uses named dict/list sections.
    - label_outcome is optional.
  be:
    - use StrictBaseModel with extra="forbid".
    - use Field constraints only for simple static constraints such as confidence.
  qc:
    - confidence range becomes testable later.
    - optional fields are explicit None defaults.
  devops:
    - Field is allowed for static metadata/constraints.
    - dynamic defaults remain banned.
  docs_gardener:
    - enum casing decision is recorded for implementation.

round_2_cross_check:
  fe_to_qc:
    issue: final_score may not always be normalized like confidence.
    final_change: confidence uses 0..1 constraint; final_score remains float without range until scoring engine defines scale.
  qc_to_fe:
    issue: action_label could diverge from action.
    final_change: no validator enforces relationship yet; formatter/scoring phase may handle it later.
  db_to_devops:
    issue: dict[str, Any] may include path-like strings later.
    final_change: contracts.py allows plain data; fixture path scan in next step enforces path safety.
  devops_to_db:
    issue: ArtifactRef.ref should not validate path/URL yet.
    final_change: keep ref as str and defer safety checks to fixtures/tests.
  be_to_docs:
    issue: __all__ can drift if models change.
    final_change: include __all__ now; future tests may import all public names.
  cto_to_all:
    issue: enough planning has accumulated.
    final_change: next action must be implementation of contracts.py, not another planning pass.

round_2_final_improved_plans:
  fe:
    final_gate: FE_READY_FOR_CONTRACTS_PY_IMPLEMENTATION
    final_requirements:
      - uppercase TradeAction values.
      - confidence constrained, final_score unconstrained.
  db:
    final_gate: DB_READY_FOR_CONTRACTS_PY_IMPLEMENTATION
    final_requirements:
      - SignalReplayBundle named sections.
      - no schema vocabulary/imports.
  be:
    final_gate: BE_READY_FOR_CONTRACTS_PY_IMPLEMENTATION
    final_requirements:
      - StrictBaseModel, enums, small models, main DTOs, __all__ in that order.
      - no dynamic defaults.
  qc:
    final_gate: QC_READY_FOR_CONTRACTS_PY_IMPLEMENTATION
    final_requirements:
      - required/default/enum/range behavior is testable next.
  devops:
    final_gate: DEVOPS_READY_FOR_CONTRACTS_PY_IMPLEMENTATION
    final_requirements:
      - side-effect-free import.
      - no dependency or runtime setup change.
  docs_gardener:
    final_gate: DOCS_READY_FOR_CONTRACTS_PY_IMPLEMENTATION
    final_requirements:
      - next action is code.
      - docs update only after import-check.

cto_synthesis:
  call: IMPLEMENT_CONTRACTS_PY_NOW
  recommendation: proceed to code without another planning cycle
  exact_work_order:
    - add src/halo_swing_mcp/contracts.py only
    - implement StrictBaseModel
    - implement enums with uppercase string values
    - implement ArtifactRef and ReplayMissingLinkError
    - implement LatestSignalReport, SignalReplayBundle, StorageHealth
    - add __all__
    - run import-check
  hard_limits:
    - no fixtures/tests in this first file-only step unless the user explicitly asks to implement the whole DTO slice
    - no migration/repository/adapters/scoring/Hermes code
    - no dependency changes
```

## P1 Contracts.py Model Spec Plan

```yaml
scope: concrete model specification for src/halo_swing_mcp/contracts.py
mode: planning_only_no_code
target_file: src/halo_swing_mcp/contracts.py
source_of_truth:
  first_step_plan: docs/halo-swing-development-plan.md#311-p1-contractspy-first-execution-step-plan
  model_spec_plan: docs/halo-swing-development-plan.md#312-p1-contractspy-model-spec-plan

team_detailed_plans:
  fe:
    objective: lock the human-report-facing contract fields.
    detailed_plan:
      - LatestSignalReport must include signal_id, created_at, asset, underlying, timeframe, action, action_label, final_score, confidence, entry_summary, stop_summary, take_profit_summary, invalidation_summary, risk_summary, data_freshness_status, degraded_mode, data_warnings, and config_hash.
      - Optional report enrichments are reason_summary, evidence_summary, label_status, and chart_ref.
      - Action enum must cover BUY_2X, BUY_3X, WAIT, TRIM, EXIT, STOP.
      - Do not add UI layout, formatted Telegram copy, chart rendering hints, or dashboard sort/filter fields.
    acceptance:
      - fields match SSOT 3.5 DTO contract intent.
      - later normal/degraded fixtures can be built without adding new report fields.
  db:
    objective: preserve replay and future persistence mapping while avoiding schema decisions.
    detailed_plan:
      - identifiers remain explicit strings: signal_id, run_id, feature_snapshot_id, evidence_id where applicable, config_hash.
      - timestamps are explicit strings supplied by caller/fixture, not generated by the model.
      - SignalReplayBundle uses named sections: signal, feature_snapshot, evidence_cards, strategy_config, run_journal, label_outcome, missing_links.
      - sections that will evolve can be dict[str, Any] or list[dict[str, Any]], but not one opaque top-level blob.
      - ArtifactRef carries ref_type, ref, metadata.
    acceptance:
      - no table/column/index/migration terms appear in model names.
      - replay bundle structure remains mappable later.
  be:
    objective: define exact implementation shape using Pydantic with minimal helpers.
    detailed_plan:
      - create StrEnum or Literal-backed enums for TradeAction, DataFreshnessStatus, SignalStatus, ArtifactRefType, ReplayErrorCode.
      - define BaseModel classes: ArtifactRef, ReplayMissingLinkError, LatestSignalReport, SignalReplayBundle, StorageHealth.
      - use ConfigDict(extra="forbid") or equivalent to catch accidental contract drift.
      - use list[str], dict[str, Any], and optional fields sparingly and explicitly.
      - expose __all__ with public contract names if useful.
    acceptance:
      - contracts.py import succeeds independently.
      - no validators beyond simple local shape constraints are required for first pass.
  qc:
    objective: make the later test file straightforward and durable.
    detailed_plan:
      - extra="forbid" is preferred so fixture drift fails clearly.
      - required fields should have no defaults except data_warnings may still be required even when empty list is supplied.
      - enum fields should fail on invalid strings.
      - model fields should be stable enough for golden fixture round-trip tests.
    acceptance:
      - missing required field and invalid enum tests are obvious.
      - no validation depends on exact wall-clock time or file system state.
  devops:
    objective: keep model spec deterministic and dependency-light.
    detailed_plan:
      - only stdlib typing/enum and pydantic imports are allowed.
      - no environment settings, path resolution, file reads, or network references.
      - timestamp fields are strings to avoid timezone serialization surprises in first slice.
      - ArtifactRef does not validate existence of any local path.
    acceptance:
      - no new package requirement.
      - importing module has no side effects.
  docs_gardener:
    objective: keep docs as model intent and code as exact truth.
    detailed_plan:
      - SSOT records planned model names and field categories.
      - after implementation, WORKING records created file and import-check result.
      - exact enum values and Pydantic config should be trusted from code/tests.
      - next planned action remains golden fixture creation.
    acceptance:
      - docs do not duplicate full code after implementation.
      - migration/repository gates remain blocked.

round_1_cross_check:
  fe_to_be:
    issue: action values must reflect leveraged swing workflow.
    required_change: include BUY_2X and BUY_3X in TradeAction, not only BUY.
  be_to_fe:
    issue: future non-leveraged actions may appear.
    required_change: keep enum extensible later but do not add speculative actions now.
  db_to_be:
    issue: dict[str, Any] can hide all structure.
    required_change: use named top-level fields for replay bundle and allow dict detail only inside each section.
  be_to_db:
    issue: too many nested Pydantic models would prematurely freeze schema.
    required_change: keep feature/evidence/config/run sections JSON-compatible in first pass.
  qc_to_be:
    issue: Optional fields with defaults can hide missing fixture fields.
    required_change: required fields have no defaults; optional fields default to None only where explicitly optional.
  devops_to_be:
    issue: Python version must support chosen enum style.
    required_change: use stdlib StrEnum only if Python 3.11 baseline is confirmed; otherwise fall back to str, Enum.
  docs_to_all:
    issue: field list can drift from 3.5 DTO contract.
    required_change: align LatestSignalReport fields with SSOT 3.5 and record deviations explicitly.

round_1_improved_plans:
  fe:
    - TradeAction includes BUY_2X, BUY_3X, WAIT, TRIM, EXIT, STOP.
    - report fields align with SSOT 3.5.
  db:
    - replay bundle has named top-level sections.
    - section internals may remain JSON-compatible.
  be:
    - Python 3.11 allows StrEnum, but str, Enum remains acceptable if simpler.
    - extra="forbid" is preferred for all DTO models.
  qc:
    - required vs optional field policy is explicit.
    - negative tests will target action and freshness enum fields first.
  devops:
    - Python 3.11.14 baseline permits modern typing.
    - no dependency changes.
  docs_gardener:
    - 3.12 is implementation spec, not final code copy.

round_2_cross_check:
  fe_to_qc:
    issue: data_warnings is required but can be empty in normal case.
    final_change: field is required list[str]; fixtures supply [] for normal and non-empty list for degraded.
  qc_to_fe:
    issue: confidence range should be testable later.
    final_change: confidence is numeric; range validation can be deferred unless simple Field ge/le is cheap.
  db_to_devops:
    issue: timestamp as string avoids serialization issues but risks inconsistent format.
    final_change: contracts.py may document UTC ISO-8601 expectation in field descriptions, not generate/parse time yet.
  devops_to_db:
    issue: strict timestamp parsing can introduce timezone library behavior.
    final_change: keep string field in first pass; fixture tests enforce fixed UTC examples later.
  be_to_docs:
    issue: full field list in docs may become stale after code.
    final_change: after implementation, docs should point to contracts.py and tests as exact source.
  cto_to_all:
    issue: the spec is now detailed enough to implement.
    final_change: next turn should implement contracts.py, not add another planning layer unless scope changes.

round_2_final_improved_plans:
  fe:
    final_gate: FE_READY_FOR_MODEL_SPEC
    final_requirements:
      - LatestSignalReport field set is sufficient for normal/degraded swing report.
      - leveraged swing actions are represented.
  db:
    final_gate: DB_READY_FOR_MODEL_SPEC
    final_requirements:
      - replay bundle has named sections.
      - no schema vocabulary leaks into contracts.py.
  be:
    final_gate: BE_READY_FOR_MODEL_SPEC
    final_requirements:
      - exact class/enum set is implementable in one file.
      - contracts.py remains isolated and strict enough for fixtures.
  qc:
    final_gate: QC_READY_FOR_MODEL_SPEC
    final_requirements:
      - missing field and invalid enum tests will be meaningful.
      - required list fields are explicit.
  devops:
    final_gate: DEVOPS_READY_FOR_MODEL_SPEC
    final_requirements:
      - no dependency, IO, env, current-time, or path-resolution side effects.
      - timestamp string policy is deterministic enough for fixtures.
  docs_gardener:
    final_gate: DOCS_READY_FOR_MODEL_SPEC
    final_requirements:
      - docs capture intent only and will defer exact truth to code/tests after implementation.

cto_synthesis:
  call: IMPLEMENT_CONTRACTS_PY_FROM_MODEL_SPEC
  recommendation: proceed with code implementation next
  required_model_names:
    - TradeAction
    - DataFreshnessStatus
    - SignalStatus
    - ArtifactRefType
    - ReplayErrorCode
    - ArtifactRef
    - ReplayMissingLinkError
    - LatestSignalReport
    - SignalReplayBundle
    - StorageHealth
  implementation_rules:
    - use Pydantic BaseModel with extra fields forbidden
    - keep timestamps as caller-supplied UTC ISO-8601 strings in first pass
    - keep contracts.py independent from server/config/storage/Hermes/network
    - add no new dependency
    - implement only src/halo_swing_mcp/contracts.py in this step
  next_action_after_code:
    - import-check contracts.py
    - then prepare golden fixture creation plan or implement fixtures if requested
```

## P1 Contracts.py First Execution Step Plan

```yaml
scope: execution-order step 1 for the approved DTO contract slice
mode: planning_only_no_code
target_file: src/halo_swing_mcp/contracts.py
source_of_truth:
  execution_plan: docs/halo-swing-development-plan.md#310-p1-dto-contract-execution-plan
  first_step_plan: docs/halo-swing-development-plan.md#311-p1-contractspy-first-execution-step-plan

team_detailed_plans:
  fe:
    objective: ensure contracts.py can support the later report fixtures without UI coupling.
    detailed_plan:
      - require LatestSignalReport fields for action, action_label, score, confidence, entry, stop, take-profit, invalidation, risk, freshness, warnings, and config_hash.
      - keep report semantics domain-level, not Telegram copy or dashboard layout.
      - require degraded_mode and data_warnings to be first-class contract fields.
      - avoid adding view-specific formatting fields.
    acceptance:
      - model fields can represent both normal and degraded report fixtures.
      - no UI-only field names appear.
  db:
    objective: ensure contracts.py preserves future persistence needs without schema leakage.
    detailed_plan:
      - require identifiers and timestamps as explicit typed fields where replay/report depends on them.
      - keep action as durable enum/string value and action_label as report-derived text.
      - ensure ArtifactRef has ref_type, ref, and metadata, but no absolute-path assumption.
      - block SQL, table names, column names, sqlite imports, migration concepts, and repository concepts.
    acceptance:
      - contracts.py has no SQL/storage imports or table vocabulary.
      - future searchable values remain explicit DTO fields.
  be:
    objective: implement a small isolated Pydantic contract module.
    detailed_plan:
      - define enums/literals for action, data_freshness_status, degraded mode, signal status, artifact ref type, and replay error code.
      - define ArtifactRef, ReplayMissingLinkError, LatestSignalReport, SignalReplayBundle, StorageHealth.
      - use BaseModel with explicit type hints and deterministic JSON-compatible field types.
      - keep imports limited to stdlib typing and pydantic.
      - avoid validators unless needed to enforce simple local invariants.
    acceptance:
      - python can import halo_swing_mcp.contracts without importing server/config/storage.
      - models can be instantiated without filesystem, env, network, or current time.
  qc:
    objective: make contracts.py testable by fixtures and negative validation next.
    detailed_plan:
      - identify required fields that tests must fail when omitted.
      - identify enum fields that tests must fail when invalid.
      - avoid complex validators that make negative tests brittle.
      - ensure default values do not hide missing required fields.
    acceptance:
      - required fields are truly required.
      - validation error locations are predictable enough for tests.
  devops:
    objective: keep contracts.py portable and side-effect free.
    detailed_plan:
      - ensure module import performs no file IO, env reads, network calls, or settings load.
      - ensure timestamp fields are strings or datetime-compatible without generating now().
      - ensure artifact refs are plain data, not resolved local paths.
      - avoid dependencies beyond existing requirements.
    acceptance:
      - import has no side effects.
      - no new dependency is needed.
  docs_gardener:
    objective: keep exact model truth in code once implemented.
    detailed_plan:
      - record only contract intent in SSOT.
      - after implementation, update WORKING with file created and verification status.
      - avoid duplicating every field definition into docs after code exists.
      - keep next step as fixture creation after contracts.py lands.
    acceptance:
      - docs point to contracts.py as executable source after implementation.
      - approved scope remains unchanged.

round_1_cross_check:
  fe_to_be:
    issue: LatestSignalReport must not be too generic to render a swing guide.
    required_change: make entry_summary, stop_summary, take_profit_summary, invalidation_summary, risk_summary required fields.
  be_to_fe:
    issue: action taxonomy may expand later.
    required_change: keep current action enum broad enough for BUY_2X, BUY_3X, WAIT, TRIM, EXIT, STOP, but avoid strategy logic.
  db_to_be:
    issue: replay fields must not be hidden in arbitrary dicts.
    required_change: SignalReplayBundle should use named structured fields for signal, feature_snapshot, evidence_cards, strategy_config, run_journal, label_outcome, missing_links.
  be_to_db:
    issue: feature_snapshot and evidence details will evolve.
    required_change: allow JSON-compatible dict payloads inside structured containers without defining storage schema.
  qc_to_be:
    issue: defaults can mask missing data.
    required_change: do not add defaults for required report/replay/health fields.
  devops_to_be:
    issue: datetime defaults may introduce current-time nondeterminism.
    required_change: no default_factory=datetime.now/utcnow or equivalent.
  docs_to_all:
    issue: exact enum list may become stale in docs.
    required_change: docs state categories; code/tests become exact source after implementation.

round_1_improved_plans:
  fe:
    - report summary fields stay required.
    - action enum supports the first expected command set without adding strategy rules.
  db:
    - replay bundle is structured around named domain sections.
    - evolving raw details may remain JSON-compatible dicts.
  be:
    - no current-time defaults.
    - no persistence imports or table terms.
  qc:
    - missing-field tests will be meaningful because required fields have no defaults.
    - enum validation can target action and freshness first.
  devops:
    - import remains side-effect free.
    - timestamp values are supplied by callers/fixtures.
  docs_gardener:
    - after implementation, docs defer exact enum/model truth to code/tests.

round_2_cross_check:
  fe_to_qc:
    issue: degraded report must be represented in the model, not only fixtures.
    final_change: LatestSignalReport includes degraded_mode and data_warnings as required fields.
  qc_to_fe:
    issue: data_warnings could be empty in normal reports.
    final_change: allow empty list, but field itself is required.
  db_to_devops:
    issue: ArtifactRef metadata can contain local paths later.
    final_change: contracts.py keeps metadata plain; path safety is enforced by fixture tests in the next step.
  devops_to_db:
    issue: forbidding all URLs would block evidence refs.
    final_change: contracts.py does not ban https refs; fixture path scan bans local/file refs.
  be_to_qc:
    issue: Pydantic version differences can affect serialization details.
    final_change: tests should compare parsed JSON/canonical dict, not raw string order.
  cto_to_all:
    issue: first code step must stay only contracts.py.
    final_change: fixtures/tests are prepared next, but not created in this first step unless user asks to implement the full DTO slice.

round_2_final_improved_plans:
  fe:
    final_gate: FE_READY_FOR_CONTRACTS_PY
    final_requirements:
      - LatestSignalReport can represent normal/degraded swing report.
      - no UI formatting fields are introduced.
  db:
    final_gate: DB_READY_FOR_CONTRACTS_PY
    final_requirements:
      - replay/report identifiers remain explicit.
      - no schema/table leakage appears.
  be:
    final_gate: BE_READY_FOR_CONTRACTS_PY
    final_requirements:
      - isolated Pydantic models can be implemented in one file.
      - no runtime side effects or external dependencies.
  qc:
    final_gate: QC_READY_FOR_CONTRACTS_PY
    final_requirements:
      - required fields and enum validation are testable next.
      - no defaults hide missing required data.
  devops:
    final_gate: DEVOPS_READY_FOR_CONTRACTS_PY
    final_requirements:
      - import is side-effect free.
      - no current-time or local-path resolution.
  docs_gardener:
    final_gate: DOCS_READY_FOR_CONTRACTS_PY
    final_requirements:
      - docs keep intent only.
      - next step after contracts.py is fixture creation.

cto_synthesis:
  call: IMPLEMENT_CONTRACTS_PY_FIRST
  recommendation: proceed with contracts.py as the first implementation step
  execution_order:
    1: create src/halo_swing_mcp/contracts.py
    2: keep module isolated from server/config/storage/Hermes/network
    3: define DTO/enums with required fields and no current-time defaults
    4: import-check contracts.py
    5: then move to golden fixture creation
  hard_limits:
    - do not create fixtures/tests in this step unless implementing the whole approved DTO slice in one pass
    - do not add migration/repository/adapters/scoring/Hermes code
    - do not add new dependency
```

## P1 DTO Contract Execution Plan

```yaml
scope: execution plan for the approved DTO contract slice
mode: planning_only_no_code
gate_status: DTO_CONTRACT_GO_RECORDED
source_of_truth:
  gate_record: docs/halo-swing-development-plan.md#39-p1-dto-contract-implementation-plan-after-go
  execution_plan: docs/halo-swing-development-plan.md#310-p1-dto-contract-execution-plan

team_detailed_plans:
  fe:
    objective: make the golden report payloads sufficient for the first non-UI swing report.
    detailed_plan:
      - define normal report fixture with clear action, confidence, entry, stop, take-profit, invalidation, risk, freshness, and warning fields.
      - define degraded report fixture where data_warnings explain the reduced confidence and the impacted guidance.
      - review names and semantics only; do not add UI layout, Telegram copy, dashboard filters, or chart presentation.
      - ensure report fixture values are plausible but not treated as investment correctness.
    owned_files:
      - tests/golden/latest_signal_report.json
      - tests/golden/latest_signal_report_degraded.json
    acceptance:
      - both fixtures validate through LatestSignalReport
      - degraded fixture has non-empty data_warnings and degraded_mode=true
  db:
    objective: preserve future storage compatibility without adding schema code.
    detailed_plan:
      - verify DTO includes future searchable identifiers and market/action fields.
      - keep action as durable action value and action_label as derived/report value.
      - require ArtifactRef to be type/ref/metadata oriented and portable.
      - review tests for no accidental sqlite migration, connection, repository, or table-name coupling.
    owned_files:
      - src/halo_swing_mcp/contracts.py
      - tests/test_contracts.py
    acceptance:
      - no SQL, sqlite3, database_url, repository, migration, or table names appear in contracts.py
      - artifact refs do not store absolute paths
  be:
    objective: implement isolated Pydantic contracts with deterministic validation.
    detailed_plan:
      - add contracts.py with enums/literals and Pydantic models only.
      - implement LatestSignalReport, SignalReplayBundle, StorageHealth, ArtifactRef, ReplayMissingLinkError.
      - use Pydantic validation for required fields, enum values, nested refs, and fixed shape errors.
      - keep imports limited to stdlib typing/datetime where needed and pydantic.
      - do not register MCP tools or touch server/harness behavior.
    owned_files:
      - src/halo_swing_mcp/contracts.py
    acceptance:
      - contracts.py imports by itself
      - model validation works from JSON fixtures
      - no runtime settings or filesystem dependency
  qc:
    objective: catch contract drift and unsafe fixtures offline.
    detailed_plan:
      - add golden round-trip tests for normal report, degraded report, replay bundle, and storage health.
      - add negative tests for missing required field and invalid enum/action/freshness values.
      - add fixture scan for absolute local paths and DB artifact extensions.
      - add no-DB-artifact assertion after tests.
      - run full existing verification commands after implementation.
    owned_files:
      - tests/test_contracts.py
      - tests/golden/*.json
    acceptance:
      - pytest passes offline
      - no .sqlite/.sqlite3 files are created under repo
      - tests do not assert trading profitability or correctness
  devops:
    objective: keep the implementation portable and local-state free.
    detailed_plan:
      - require fixed UTC timestamps in fixtures.
      - require relative/external artifact refs only.
      - ensure no new env var, cron, process supervisor, Hermes runtime, database path, or data directory dependency appears.
      - ensure .gitignore policy remains adequate and no generated artifact is committed.
    owned_files:
      - tests/golden/*.json
      - tests/test_contracts.py
    acceptance:
      - no machine-specific path or current-time dependency
      - no new local runtime setup step
  docs_gardener:
    objective: keep docs aligned while code becomes the executable contract.
    detailed_plan:
      - keep SSOT 3.10 as execution plan only.
      - after implementation, update WORKING current state with test results.
      - avoid copying full model definitions into docs once code exists.
      - keep MIGRATION_GO and REPOSITORY_GO visibly blocked.
    owned_files:
      - docs/WORKING.md
      - docs/halo-swing-development-plan.md
    acceptance:
      - docs do not expand approved write scope
      - next_atomic_step points to implementation and verification

round_1_cross_check:
  fe_to_be:
    issue: LatestSignalReport needs enough summary fields to be usable without UI.
    required_change: keep entry_summary, stop_summary, take_profit_summary, invalidation_summary, risk_summary as required fields.
  be_to_fe:
    issue: report fixture wording may become brittle.
    required_change: tests validate structure and allowed values, not exact prose except fixture round-trip equality.
  db_to_be:
    issue: replay bundle could become an untyped JSON blob.
    required_change: SignalReplayBundle must have structured fields for signal, feature_snapshot, evidence_cards, strategy_config, run_journal, label_outcome, and missing_links.
  be_to_db:
    issue: storage-like names could leak into contract layer.
    required_change: use domain names and defer table/column names to migration gate.
  qc_to_be:
    issue: negative tests need precise failure targets.
    required_change: include one missing required field test and one invalid enum test without asserting full error strings.
  devops_to_qc:
    issue: path scan should include generated fixture names but not scan the whole repo noisily.
    required_change: scan only new JSON golden fixtures for path patterns and separately check repo for DB artifact extensions.
  docs_to_all:
    issue: approved scope can accidentally widen during implementation.
    required_change: keep approved_write_scope exactly six files unless CTO reopens scope.

round_1_improved_plans:
  fe:
    - report summary fields stay required.
    - fixture text remains example data, not final UI copy.
  db:
    - replay bundle must be structured enough for future mapping.
    - table and column names remain deferred.
  be:
    - contracts.py uses domain DTO names only.
    - no MCP tool registration in this slice.
  qc:
    - negative tests target missing field and invalid enum classes.
    - path scan is fixture-scoped plus DB artifact repo check.
  devops:
    - no new runtime setup remains a hard condition.
    - fixed UTC timestamps are mandatory.
  docs_gardener:
    - approved write scope remains six files.
    - post-implementation docs must summarize test results.

round_2_cross_check:
  fe_to_qc:
    issue: degraded_mode boolean alone is too weak.
    final_change: degraded fixture must have degraded_mode=true plus data_warnings and lower confidence than normal fixture.
  qc_to_fe:
    issue: comparing confidence numerically between fixtures can be stable and objective.
    final_change: test degraded confidence < normal confidence.
  db_to_devops:
    issue: artifact ref metadata can become a loophole for local paths.
    final_change: path scan must inspect nested JSON string values, including metadata.
  devops_to_db:
    issue: external URLs may appear later and should not be blocked.
    final_change: allow https:// external refs, block file:// and local absolute paths.
  be_to_qc:
    issue: round-trip equality may fail if model defaults add omitted fields.
    final_change: fixtures should include every required field and tests compare parsed canonical dumps.
  cto_to_all:
    issue: planning is complete enough; implementation should be small and sequential.
    final_change: implement in order: contracts.py, fixtures, tests, verification.

round_2_final_improved_plans:
  fe:
    final_gate: FE_READY_FOR_DTO_CODE
    final_requirements:
      - normal and degraded report fixtures validate and remain report-usable.
      - degraded confidence is lower and warning impact is visible.
  db:
    final_gate: DB_READY_FOR_DTO_CODE
    final_requirements:
      - replay bundle is structured, not an opaque blob.
      - no SQL/schema leakage appears.
  be:
    final_gate: BE_READY_FOR_DTO_CODE
    final_requirements:
      - isolated Pydantic contract file is implemented first.
      - fixtures drive tests, not live services.
  qc:
    final_gate: QC_READY_FOR_DTO_CODE
    final_requirements:
      - golden, degraded comparison, negative validation, path scan, and no-DB-artifact tests are present.
  devops:
    final_gate: DEVOPS_READY_FOR_DTO_CODE
    final_requirements:
      - fixtures are portable and deterministic.
      - https refs are allowed; file/local paths are blocked.
  docs_gardener:
    final_gate: DOCS_READY_FOR_DTO_CODE
    final_requirements:
      - scope stays six approved files.
      - docs remain aligned after verification.

cto_synthesis:
  call: IMPLEMENT_DTO_CONTRACT_SLICE_NOW
  recommendation: proceed with implementation
  execution_order:
    1: create src/halo_swing_mcp/contracts.py
    2: create normal/degraded/replay/health golden fixtures
    3: create tests/test_contracts.py
    4: run health_check, pytest, and ruff
    5: update WORKING with implementation result
  hard_limits:
    - no migration/DDL
    - no repository persistence
    - no adapter/scoring/Hermes runtime code
    - no write scope beyond approved files unless CTO reopens gate
```

## P1 DTO Contract Implementation Plan After GO

```yaml
scope: implementation plan for the first code slice after explicit DTO_CONTRACT_GO
mode: planning_only_no_code
target_gate: DTO_CONTRACT_GO
source_of_truth:
  signoff_plan: docs/halo-swing-development-plan.md#38-p1-dto_contract_go-sign-off-execution-plan
  implementation_plan: docs/halo-swing-development-plan.md#39-p1-dto-contract-implementation-plan-after-go

team_detailed_plans:
  fe:
    objective: make the fixture payloads prove the first swing report can be rendered later.
    detailed_plan:
      - review fixture values for normal report and degraded report before accepting tests.
      - ensure required report fields include action, action_label, final_score, confidence, entry_summary, stop_summary, take_profit_summary, invalidation_summary, risk_summary, data_freshness_status, degraded_mode, data_warnings, and config_hash.
      - ensure degraded fixture has lower confidence, visible warning, and an impacted guidance field.
      - keep presentation formatting, chart layout, dashboard widgets, and Telegram copy outside this implementation.
    implementation_touchpoints:
      - tests/golden/latest_signal_report.json
      - tests/golden/latest_signal_report_degraded.json
    no_go:
      - fixture cannot explain why confidence is reduced
      - DTO requires UI-only fields
  db:
    objective: make every DTO field classifiable for future storage without writing schema code.
    detailed_plan:
      - create a storage_category field or test-side mapping note for DTO fields if needed.
      - verify future indexed candidates are present: signal_id, run_id, config_hash, created_at, asset, underlying, timeframe, action, final_score, data_freshness_status.
      - ensure artifact refs are represented as portable ref_type/ref objects.
      - block any migration runner, SQL file, sqlite connection, or repository function.
    implementation_touchpoints:
      - src/halo_swing_mcp/contracts.py
      - tests/test_contracts.py
    no_go:
      - contracts.py starts defining table names or SQL
      - future searchable fields disappear into untyped JSON only
  be:
    objective: implement isolated Pydantic contracts and deterministic serialization.
    detailed_plan:
      - define enums/literals for action, signal status, data_freshness_status, degraded_mode, artifact_ref type, and replay error code.
      - define LatestSignalReport, SignalReplayBundle, StorageHealth, ArtifactRef, ReplayMissingLinkError models.
      - define helper serialization path using model_dump(mode="json") or equivalent deterministic JSON dump.
      - keep contracts.py importable without server, config, DB, Hermes, or network imports.
      - expose no MCP tool in this slice.
    implementation_touchpoints:
      - src/halo_swing_mcp/contracts.py
      - tests/test_contracts.py
    no_go:
      - model validation depends on runtime settings or filesystem
      - DTO models import MCP server or repository modules
  qc:
    objective: verify contract behavior offline and catch unsafe fixture drift.
    detailed_plan:
      - add golden round-trip tests for normal report, degraded report, replay bundle, and storage health.
      - add negative tests for missing required fields and invalid enum values.
      - add path scan over new JSON fixtures for /Users/, file://, ~/, Windows drive roots, and sqlite artifact names.
      - add post-test assertion that repo has no new .sqlite or .sqlite3 files.
      - keep assertions away from investment correctness.
    implementation_touchpoints:
      - tests/test_contracts.py
      - tests/golden/*.json
    no_go:
      - tests require network, DB file, Hermes, MCP transport, or current time
      - tests only compare happy-path JSON
  devops:
    objective: ensure implementation remains portable, deterministic, and local-state free.
    detailed_plan:
      - verify fixed ISO-8601 UTC timestamps in fixtures.
      - verify artifact refs use relative or external refs only.
      - verify no new env vars, supervisor, cron, service, or data directory is required.
      - verify current .gitignore remains adequate and no new generated artifact is committed.
    implementation_touchpoints:
      - tests/golden/*.json
      - tests/test_contracts.py
    no_go:
      - fixture includes local absolute path or generated timestamp
      - implementation creates persistent local state
  docs_gardener:
    objective: keep code/tests as executable contract and avoid doc duplication after implementation.
    detailed_plan:
      - keep DTO_CONTRACT_GO recorded in SSOT before code starts.
      - keep WORKING in implementation-ready state now that GO is recorded.
      - after implementation, summarize results and point to contracts.py/tests instead of copying all model fields.
      - keep MIGRATION_GO and REPOSITORY_GO blocked.
    implementation_touchpoints:
      - docs/WORKING.md
      - docs/halo-swing-development-plan.md
    no_go:
      - docs imply migration or repository work is part of DTO gate
      - implementation proceeds without explicit GO record

round_1_cross_check:
  fe_to_be:
    issue: DTO names alone do not guarantee report usefulness.
    required_change: fixtures must include both normal and degraded report examples with summaries populated.
  be_to_fe:
    issue: fixture values should not turn into final report wording.
    required_change: tests assert field presence/types/categories, not final prose style.
  db_to_be:
    issue: ArtifactRef model must not allow raw local absolute paths by default.
    required_change: include portable ref_type/ref structure and path-scan tests.
  be_to_db:
    issue: DTO code should not include storage category metadata if it pollutes domain models.
    required_change: keep storage classification in tests/docs unless a field is naturally part of DTO.
  qc_to_be:
    issue: model_dump order and JSON formatting can cause brittle golden tests.
    required_change: deterministic serialization with sorted keys or stable comparison by parsed JSON.
  devops_to_qc:
    issue: path scan should not accidentally flag harmless relative refs.
    required_change: scan only absolute/local patterns and DB artifact extensions.
  docs_to_all:
    issue: historical implementation plan text can be mistaken for current gate state.
    required_change: record that DTO_CONTRACT_GO is now explicit, while scope remains narrow.

round_1_improved_plans:
  fe:
    - normal/degraded fixtures are mandatory.
    - tests avoid judging prose quality.
  db:
    - storage classification stays outside domain models unless naturally required.
    - ArtifactRef remains portable.
  be:
    - JSON tests compare parsed deterministic payloads.
    - contracts.py remains isolated.
  qc:
    - path scan targets local absolute paths and DB artifacts.
    - no-DB-artifact check is included.
  devops:
    - fixed UTC timestamps are required.
    - no new env/runtime dependency remains a gate.
  docs_gardener:
    - GO record is present before code.
    - docs after implementation should summarize, not duplicate model internals.

round_2_cross_check:
  fe_to_qc:
    issue: degraded fixture must show which guidance is affected by stale/partial data.
    final_change: degraded fixture includes data_warnings plus invalidation_summary or risk_summary impact.
  qc_to_fe:
    issue: tests should not enforce financial advice correctness.
    final_change: tests verify schema and allowed values only.
  db_to_devops:
    issue: relative artifact refs need a root interpretation later.
    final_change: DTO allows portable refs; runtime path resolution is deferred to DevOps/storage gate.
  devops_to_db:
    issue: future path resolution should not block DTO implementation.
    final_change: no absolute paths now; root policy deferred.
  be_to_docs:
    issue: exact enum list may evolve during implementation.
    final_change: docs name required enum categories; code/tests become exact source after GO.
  cto_to_all:
    issue: implementation should begin immediately after GO, not another broad planning cycle.
    final_change: next step after explicit GO is code implementation and verification.

round_2_final_improved_plans:
  fe:
    final_gate: FE_READY_FOR_DTO_IMPLEMENTATION_AFTER_GO
    final_requirements:
      - normal/degraded report fixtures express first swing guide semantics.
      - degraded report exposes warning and impacted guidance.
  db:
    final_gate: DB_READY_FOR_DTO_IMPLEMENTATION_AFTER_GO
    final_requirements:
      - future searchable fields remain explicit.
      - no SQL/migration/repository code appears.
  be:
    final_gate: BE_READY_FOR_DTO_IMPLEMENTATION_AFTER_GO
    final_requirements:
      - isolated Pydantic contract module is the only production code change.
      - replay missing-link error is structured.
  qc:
    final_gate: QC_READY_FOR_DTO_IMPLEMENTATION_AFTER_GO
    final_requirements:
      - golden, degraded, negative, path scan, and no-DB-artifact tests are implemented.
      - tests are offline and deterministic.
  devops:
    final_gate: DEVOPS_READY_FOR_DTO_IMPLEMENTATION_AFTER_GO
    final_requirements:
      - fixtures are portable and local-state free.
      - no new runtime/process/env dependency exists.
  docs_gardener:
    final_gate: DOCS_READY_FOR_DTO_IMPLEMENTATION_AFTER_GO
    final_requirements:
      - SSOT records GO before implementation starts.
      - post-implementation docs point to executable contract.

cto_synthesis:
  call: DTO_CONTRACT_GO
  recommendation: implement the approved DTO contract slice immediately
  rationale:
    - the implementation slice is narrow and testable
    - cross-checks preserve report usefulness without leaking UI or schema work
    - QC/DevOps controls cover determinism, fixture safety, and local-state risk
  exact_next_action:
    - implement contracts.py, fixtures, and test_contracts.py only
    - run health_check, pytest, and ruff
  still_blocked:
    - migration/DDL until MIGRATION_GO
    - repository persistence until REPOSITORY_GO
    - adapters, scoring, Hermes runtime until later gates
```

## P1 DTO_CONTRACT_GO Sign-Off Execution Plan

```yaml
scope: final sign-off procedure before DTO contract implementation
mode: planning_only_no_code
target_gate: DTO_CONTRACT_GO
source_of_truth:
  approval_packet: docs/halo-swing-development-plan.md#37-p1-dto_contract_go-approval-packet
  signoff_plan: docs/halo-swing-development-plan.md#38-p1-dto_contract_go-sign-off-execution-plan

team_detailed_plans:
  fe:
    objective: sign off only if report fixtures can support the first human-readable swing guide.
    detailed_plan:
      - review normal latest_signal_report fixture fields before code.
      - review degraded latest_signal_report fixture fields before code.
      - require entry/stop/take_profit/invalidation/risk summaries in both normal and degraded cases.
      - require warnings to make confidence reduction visible.
      - reject chart/dashboard-only fields in the DTO gate.
    signoff_artifacts:
      - FE_DTO_CONTRACT_SIGNOFF row in SSOT
      - accepted normal/degraded report fixture field checklist
    no_go:
      - degraded report has warnings but no action guidance
      - stop or invalidation summary is absent
  db:
    objective: sign off only if DTO fields are classifiable without prematurely writing DDL.
    detailed_plan:
      - attach storage-category mapping to each planned DTO field.
      - verify future searchable candidates remain explicit.
      - verify action/action_label and summary/detail separation.
      - verify artifact refs are portable.
      - block any SQL, migration, repository, or DB connection work.
    signoff_artifacts:
      - DB_DTO_CONTRACT_SIGNOFF row in SSOT
      - field classification checklist
    no_go:
      - DTO field lacks future storage category
      - implementation scope includes SQL or migrations
  be:
    objective: sign off only if the code slice can be implemented as isolated contracts.
    detailed_plan:
      - confirm model names and fixture names before code.
      - confirm contracts.py does not import server, storage, Hermes, or network modules.
      - confirm deterministic JSON serialization is testable.
      - confirm structured replay missing-link error fields.
      - define the exact verification commands to run after implementation.
    signoff_artifacts:
      - BE_DTO_CONTRACT_SIGNOFF row in SSOT
      - implementation file list and command checklist
    no_go:
      - contract code needs runtime settings beyond Pydantic validation
      - missing-link error is unstructured free-form JSON only
  qc:
    objective: sign off only if tests can catch contract drift and unsafe fixture content.
    detailed_plan:
      - require fixture round-trip tests.
      - require degraded report fixture test.
      - require negative validation tests.
      - require absolute-path scan across new JSON fixtures.
      - require no DB/data/artifact file creation during test run.
    signoff_artifacts:
      - QC_DTO_CONTRACT_SIGNOFF row in SSOT
      - acceptance and negative test checklist
    no_go:
      - tests assert only happy path
      - tests depend on live API, DB file, or current time
  devops:
    objective: sign off only if the slice is portable and local-state free.
    detailed_plan:
      - scan fixture examples for /Users, file://, drive roots, home-directory expansion, and absolute paths.
      - verify fixture timestamps are fixed UTC examples.
      - verify no new env vars, service processes, cron jobs, or Hermes runtime config is needed.
      - verify existing .gitignore remains enough for any accidental local artifacts.
    signoff_artifacts:
      - DEVOPS_DTO_CONTRACT_SIGNOFF row in SSOT
      - portability checklist
    no_go:
      - fixture contains local absolute path or generated current timestamp
      - implementation requires background runtime
  docs_gardener:
    objective: sign off only if docs and current task point to the same narrow code slice.
    detailed_plan:
      - add SSOT sign-off matrix for DTO_CONTRACT_GO.
      - keep detailed execution trace in WORKING.
      - after implementation, replace speculative field prose with links to executable tests where useful.
      - keep migration/repository gates visibly blocked.
    signoff_artifacts:
      - DOCS_DTO_CONTRACT_SIGNOFF row in SSOT
      - WORKING next_atomic_step update
    no_go:
      - SSOT and WORKING disagree on write scope
      - docs imply migration/repository work is allowed

round_1_cross_check:
  fe_to_qc:
    issue: fixture tests can pass while degraded report is unhelpful.
    required_change: degraded fixture must include both warning text and the affected decision field.
  qc_to_fe:
    issue: helpfulness is not deterministic.
    required_change: test field presence and allowed categories, not subjective prose quality.
  db_to_be:
    issue: field classification may become disconnected from model names.
    required_change: include model-field-to-storage-category mapping in sign-off notes.
  be_to_db:
    issue: mapping should not freeze migration columns.
    required_change: mapping remains category-level until MIGRATION_GO.
  devops_to_qc:
    issue: absolute-path scan must catch common macOS patterns and file URLs.
    required_change: scan for /Users/, file://, ~/, and drive-like roots.
  docs_to_all:
    issue: another sign-off section can look like approval already happened.
    required_change: state that code remains blocked until CTO explicitly records DTO_CONTRACT_GO.

round_1_improved_plans:
  fe:
    - degraded fixture requires warning plus impacted decision field.
    - prose quality is reviewed manually, not enforced as test truth.
  db:
    - mapping checklist uses DTO field names and storage categories.
    - migration column names remain deferred.
  be:
    - implementation file list stays unchanged.
    - missing-link error remains structured.
  qc:
    - negative tests avoid exact Pydantic wording.
    - absolute-path scan patterns are explicit.
  devops:
    - no new runtime/env dependency is a hard gate.
    - fixed UTC timestamps are required.
  docs_gardener:
    - SSOT sign-off matrix must use "ready" language until CTO GO is recorded.

round_2_cross_check:
  fe_to_docs:
    issue: docs should preserve why degraded reports matter.
    final_change: SSOT notes degraded report must expose reduced confidence reason and affected guidance.
  docs_to_fe:
    issue: SSOT should not become report copywriting.
    final_change: SSOT states semantic requirement only.
  db_to_qc:
    issue: no DB writes is easy to miss if tests add tmp files later.
    final_change: QC checks absence of .sqlite/.sqlite3 under repo after contract tests.
  qc_to_db:
    issue: no DB files should not ban harmless pytest cache already ignored.
    final_change: check DB artifact patterns, not all generated cache directories.
  be_to_devops:
    issue: deterministic timestamps should be allowed in fixtures.
    final_change: fixed ISO-8601 UTC timestamps are allowed; current-time generation is banned.
  cto_to_all:
    issue: planning is sufficient; further planning should not delay the narrow implementation.
    final_change: next decision should be explicit DTO_CONTRACT_GO or change request.

round_2_final_improved_plans:
  fe:
    final_gate: FE_READY_FOR_DTO_CONTRACT_GO
    final_requirements:
      - normal/degraded report fixture semantics are sufficient for first swing guide.
      - degraded guidance exposes reason and impacted field.
  db:
    final_gate: DB_READY_FOR_DTO_CONTRACT_GO
    final_requirements:
      - field-to-storage-category mapping is ready.
      - no migration naming or DDL is implied.
  be:
    final_gate: BE_READY_FOR_DTO_CONTRACT_GO
    final_requirements:
      - isolated contracts.py implementation is feasible.
      - missing-link error shape is fixed.
  qc:
    final_gate: QC_READY_FOR_DTO_CONTRACT_GO
    final_requirements:
      - round-trip, degraded, negative, path scan, and no-DB-artifact checks are planned.
      - tests remain offline.
  devops:
    final_gate: DEVOPS_READY_FOR_DTO_CONTRACT_GO
    final_requirements:
      - fixtures are portable with fixed UTC timestamps.
      - no runtime service or env dependency is introduced.
  docs_gardener:
    final_gate: DOCS_READY_FOR_DTO_CONTRACT_GO
    final_requirements:
      - SSOT records sign-off readiness.
      - WORKING points to CTO GO as the only remaining blocker.

cto_synthesis:
  call: FINAL_READY_FOR_DTO_CONTRACT_GO
  recommendation: go
  rationale:
    - all teams converge on a narrow, testable, offline code slice
    - migration and repository boundaries remain locked
    - QC and DevOps gates cover drift, paths, time, and local-state risks
  exact_next_decision:
    - record DTO_CONTRACT_GO in SSOT and WORKING
    - then implement the approved DTO contract slice
  approved_scope_if_go:
    - src/halo_swing_mcp/contracts.py
    - tests/golden/latest_signal_report.json
    - tests/golden/latest_signal_report_degraded.json
    - tests/golden/signal_replay_bundle.json
    - tests/golden/storage_health.json
    - tests/test_contracts.py
  still_blocked:
    - migration/DDL until MIGRATION_GO
    - repository persistence until REPOSITORY_GO
    - adapters/scoring/Hermes runtime until their later gates
  no_go_conditions:
    - user/CTO wants additional action taxonomy before DTO implementation
    - any team expands scope beyond contracts/fixtures/tests
    - fixture portability or offline-test rules are relaxed
```

## P1 DTO_CONTRACT_GO Approval Packet

```yaml
scope: final planning review before DTO contract code
mode: planning_only_no_code
target_gate: DTO_CONTRACT_GO
source_of_truth:
  dto_plan: docs/halo-swing-development-plan.md#36-p1-dto-contract-next-action-plan
  go_packet: docs/halo-swing-development-plan.md#37-p1-dto_contract_go-approval-packet

team_detailed_plans:
  fe:
    objective: approve the report contract only if it can express swing guidance clearly.
    detailed_plan:
      - verify latest_signal_report has action, action_label, final_score, confidence, entry_summary, stop_summary, take_profit_summary, invalidation_summary, risk_summary, freshness, and warnings.
      - verify degraded report still tells the user whether to wait, reduce confidence, or invalidate a setup.
      - reject dashboard-only fields and decorative wording from the contract.
      - require examples for BUY_2X/BUY_3X/WAIT/TRIM/EXIT/STOP semantics later, but only fixture one normal and one degraded case now.
    signoff_inputs:
      - latest_signal_report fixture field list
      - degraded report fixture field list
    no_go:
      - report cannot explain stop/invalidation
      - degraded state hides the reason for lower confidence
  db:
    objective: approve DTO work only if every field can later map to durable storage.
    detailed_plan:
      - classify each DTO field as future indexed column, derived field, JSON detail, or artifact_ref.
      - ensure IDs and timestamps appear in replay/report DTOs without selecting final DDL.
      - require artifact refs to be portable and not absolute paths.
      - keep DDL, indexes, and migration runner out of this slice.
    signoff_inputs:
      - DTO-to-storage mapping table
      - portable artifact_ref examples
    no_go:
      - fields are only prose with no storage classification
      - DTO implementation starts defining SQL tables
  be:
    objective: approve a small implementation slice that creates executable DTO contracts.
    detailed_plan:
      - implement only Pydantic models, enums/literals, fixtures, and tests after GO.
      - keep contracts importable without server, Hermes, DB, or network imports.
      - use deterministic serialization for golden tests.
      - include structured replay missing-link error shape.
    signoff_inputs:
      - proposed contracts.py model list
      - fixture serialization rules
      - negative validation test list
    no_go:
      - DTOs import MCP server or storage modules
      - tests depend on current time or live services
  qc:
    objective: approve the slice only if contract drift can be caught offline.
    detailed_plan:
      - require golden fixtures for latest_signal_report normal, latest_signal_report degraded, signal_replay_bundle, and storage_health.
      - require missing required field and invalid enum negative tests.
      - require no SQLite/data/artifact writes during tests.
      - keep investment correctness out of fixture assertions.
    signoff_inputs:
      - golden fixture checklist
      - negative test checklist
      - no-local-state assertion
    no_go:
      - fixtures verify only happy paths
      - tests write DB files or depend on repo data/
  devops:
    objective: approve only if local/CI execution stays portable and stateless.
    detailed_plan:
      - verify fixtures avoid absolute paths, machine usernames, local browser paths, and generated current timestamps.
      - verify artifact refs use ref_type plus ref metadata.
      - verify no service, cron, supervisor, or Hermes runtime is required.
      - preserve current .gitignore data/artifacts/state policy.
    signoff_inputs:
      - fixture portability checklist
      - local-state risk review
    no_go:
      - fixture contains /Users, file://, or machine-specific paths
      - DTO tests require background process
  docs_gardener:
    objective: keep sign-off readable without making docs the executable schema.
    detailed_plan:
      - record this GO packet in SSOT.
      - keep detailed debate in WORKING.
      - after implementation, point docs to code/tests instead of copying full models.
      - update next_atomic_step to code implementation only after explicit GO.
    signoff_inputs:
      - SSOT 3.7 section
      - WORKING current state
    no_go:
      - SSOT and WORKING disagree on allowed write scope
      - code starts before the gate is recorded

round_1_cross_check:
  fe_to_be:
    issue: BE plan mentions enums but not enough report-level summaries.
    required_change: latest_signal_report fixture must include risk, invalidation, entry, stop, and take-profit summaries.
  be_to_fe:
    issue: FE wants future action variants, but first slice should not model every future trading command.
    required_change: include stable action enum now and leave extended action taxonomy for scoring phase.
  db_to_be:
    issue: structured replay errors could become arbitrary JSON.
    required_change: missing-link error needs code, message, missing_ref_type, and missing_ref_id fields.
  be_to_db:
    issue: storage classification should not force table names too early.
    required_change: classify by storage category, not final table column names.
  qc_to_fe:
    issue: "actionable" is subjective and hard to test.
    required_change: tests assert required fields and warnings, not correctness of trade decision.
  qc_to_devops:
    issue: no-local-path rule needs an automated test.
    required_change: add fixture scan for absolute path patterns.
  docs_to_all:
    issue: approval packet can become another duplicated spec.
    required_change: SSOT keeps summary; executable truth moves to tests after GO.

round_1_improved_plans:
  fe:
    - normal and degraded fixtures both require risk/invalidation/entry/stop/take-profit summaries.
    - expanded trading taxonomy is deferred to scoring engine.
  db:
    - storage classification uses category names, not final DDL.
    - replay error fields remain persistable as JSON detail later.
  be:
    - missing-link error shape is explicit.
    - DTO implementation remains independent from server/storage.
  qc:
    - tests focus on schema/contract, not trading correctness.
    - fixture absolute-path scan is required.
  devops:
    - portable artifact_ref pattern is mandatory.
    - no background services in test setup.
  docs_gardener:
    - post-implementation docs should link to tests/code instead of duplicating contracts.

round_2_cross_check:
  fe_to_db:
    issue: action_label may be derived and should not block storage.
    final_change: action_label is a DTO-derived field; action remains the durable future indexed value.
  db_to_fe:
    issue: summaries can be generated from guide_json later.
    final_change: summaries are required DTO fields, but storage mapping can be DTO-derived or JSON detail.
  be_to_qc:
    issue: negative tests can become brittle if they assert exact Pydantic wording.
    final_change: assert validation fails and field/error category exists, not full message text.
  qc_to_be:
    issue: serialization order can drift across implementations.
    final_change: use deterministic JSON dump options in contract tests.
  devops_to_docs:
    issue: docs should not promise CI until CI exists.
    final_change: say portable/local test ready, not CI-integrated.
  cto_to_all:
    issue: gate should approve a narrow code slice, not the whole P1 storage phase.
    final_change: DTO_CONTRACT_GO authorizes only contracts, fixtures, and offline tests.

round_2_final_improved_plans:
  fe:
    final_gate: FE_DTO_GO_READY
    final_requirements:
      - normal and degraded report fixtures remain human-actionable.
      - no dashboard-only scope enters the contract.
  db:
    final_gate: DB_DTO_GO_READY
    final_requirements:
      - field classification exists without DDL.
      - future searchable values are preserved.
  be:
    final_gate: BE_DTO_GO_READY
    final_requirements:
      - contracts.py can be implemented without server/storage imports.
      - structured replay error shape is fixed.
  qc:
    final_gate: QC_DTO_GO_READY
    final_requirements:
      - golden, degraded, negative, and path-scan tests are planned.
      - no investment correctness assertion is encoded.
  devops:
    final_gate: DEVOPS_DTO_GO_READY
    final_requirements:
      - fixtures are portable/local-test ready.
      - no services or local state are introduced.
  docs_gardener:
    final_gate: DOCS_DTO_GO_READY
    final_requirements:
      - SSOT and WORKING agree on scope and next action.
      - code remains blocked until explicit CTO GO.

cto_synthesis:
  call: READY_TO_MARK_DTO_CONTRACT_GO
  recommendation: go, if the user/CTO accepts the narrow scope
  approved_scope_after_go:
    - src/halo_swing_mcp/contracts.py
    - tests/golden/latest_signal_report.json
    - tests/golden/latest_signal_report_degraded.json
    - tests/golden/signal_replay_bundle.json
    - tests/golden/storage_health.json
    - tests/test_contracts.py
  blocked_scope_after_go:
    - migrations
    - SQLite connection or repository persistence
    - market/news adapters
    - scoring engine
    - Hermes runtime integration
  first_implementation_order_after_go:
    1: define enums/literals and DTO models
    2: add normal/degraded/replay/health golden fixtures
    3: add round-trip serialization tests
    4: add negative validation tests
    5: add fixture absolute-path scan
    6: run health_check, pytest, and ruff
  no_go_conditions:
    - team scope expands beyond DTO contracts
    - tests require live network, DB file, Hermes, or MCP transport
    - fixtures contain local absolute paths or current-time dependencies
    - DTOs cannot model degraded report or structured replay missing-link error
```

## P1 DTO Contract Next Action Plan

```yaml
scope: plan the next implementation slice after DECISION_LOG_GO
mode: planning_only_no_code
target_gate: DTO_CONTRACT_GO
source_of_truth:
  decision_log: docs/halo-swing-development-plan.md#35-p1-storageschema-decision-log
  dto_plan: docs/halo-swing-development-plan.md#36-p1-dto-contract-next-action-plan

next_action_definition:
  objective: define DTO models and golden fixtures before SQLite migration or repository persistence code
  proposed_write_scope_after_go:
    - src/halo_swing_mcp/contracts.py
    - tests/golden/latest_signal_report.json
    - tests/golden/signal_replay_bundle.json
    - tests/golden/storage_health.json
    - tests/test_contracts.py
  forbidden_until_later_gates:
    - SQLite migration files before MIGRATION_GO
    - repository persistence code before REPOSITORY_GO
    - live market/news/API adapters
    - writes to repo data/

team_detailed_plans:
  fe:
    objective: make latest_signal_report useful for swing decision reporting.
    steps:
      - freeze required vs optional report fields.
      - define stale/degraded warning examples.
      - define display-neutral semantic labels for action, risk, invalidation, entry, stop, and take profit.
      - verify DTO can answer buy/hold/trim/exit/stop guidance without dashboard-only fields.
    deliverables:
      - latest_signal_report fixture expectations
      - stale/degraded report fixture expectations
      - semantic glossary for report fields
  db:
    objective: ensure DTOs map cleanly to future indexed columns, JSON detail, and artifact refs.
    steps:
      - map each DTO field to indexed column, DTO-derived field, JSON detail, or artifact ref.
      - flag any field that cannot be persisted later without schema ambiguity.
      - keep config_hash, signal_id, run_id, created_at, asset, timeframe, action, final_score, and data_freshness_status searchable.
      - avoid DDL decisions in this slice except field classification feedback.
    deliverables:
      - DTO-to-storage mapping notes
      - fields requiring future migration constraints
  be:
    objective: create stable Pydantic DTO contracts without touching persistence.
    steps:
      - define LatestSignalReport, SignalReplayBundle, StorageHealth models.
      - define enums/literals for action, status, data_freshness_status, degraded_mode, and missing replay errors.
      - add deterministic serialization suitable for golden tests.
      - keep DTOs independent from MCP server imports and DB imports.
    deliverables:
      - contract model file plan
      - JSON golden fixture plan
      - offline unit test plan
  qc:
    objective: prove DTO contracts are deterministic and do not require live data.
    steps:
      - create golden fixtures for normal report, degraded report, replay bundle, and storage health.
      - test round-trip model validation and JSON serialization.
      - test required-field failures and invalid enum values.
      - assert no test writes DB files or repo data/.
    deliverables:
      - acceptance matrix
      - negative test list
      - golden fixture checklist
  devops:
    objective: keep contract tests portable across local paths and future CI.
    steps:
      - ensure fixtures contain portable refs only.
      - avoid absolute local paths and machine-specific timestamps.
      - keep database_url unused by DTO tests.
      - confirm no new runtime service or cron requirement.
    deliverables:
      - fixture portability checklist
      - no-local-state checklist
  docs_gardener:
    objective: keep SSOT concise and WORKING useful for handoff.
    steps:
      - add concise DTO_CONTRACT_GO packet to SSOT.
      - keep detailed review trail in WORKING.
      - avoid duplicating final model definitions in multiple docs after code exists.
      - update current state and next gate.
    deliverables:
      - SSOT 3.6 DTO plan
      - WORKING detailed planning log
  cto:
    objective: decide whether the DTO contract slice is safe to implement.
    steps:
      - verify the slice does not sneak in migration/repository work.
      - verify DTOs support replay/report and future field classification.
      - verify tests can run offline with golden fixtures.
      - decide DTO_CONTRACT_GO or request changes.

round_1_cross_check:
  fe_to_be:
    issue: action enum alone is not enough for a human report.
    required_change: include action_label, risk_summary, invalidation_summary, entry_summary, stop_summary, and take_profit_summary.
  be_to_fe:
    issue: display copy should not become the durable DTO contract.
    required_change: keep semantic fields stable and let future formatter own presentation text.
  db_to_be:
    issue: DTO fields must not become impossible to persist later.
    required_change: add DTO-to-storage classification for each field.
  be_to_db:
    issue: DTO slice should not freeze DDL prematurely.
    required_change: record mapping notes without creating migration files.
  qc_to_be:
    issue: happy-path fixtures alone will miss contract drift.
    required_change: add negative validation tests for missing required fields and invalid enum values.
  devops_to_qc:
    issue: fixtures can accidentally include local paths.
    required_change: add portable artifact_ref examples and a no-absolute-path assertion.
  docs_to_all:
    issue: detailed planning could make SSOT noisy.
    required_change: SSOT gets gate summary; WORKING keeps full review trace.

round_1_improved_plans:
  fe:
    - report DTO includes semantic summary fields and stale/degraded warnings.
    - future dashboard-only fields stay out of DTO_CONTRACT_GO.
  db:
    - DTO field classification becomes a required deliverable.
    - DDL remains explicitly blocked.
  be:
    - contract module stays independent from DB and MCP imports.
    - enums/literals are part of the planned contract.
  qc:
    - negative validation tests are part of the acceptance gate.
    - normal and degraded golden fixtures are both required.
  devops:
    - artifact refs must be portable relative refs or external refs.
    - fixture timestamps must be deterministic UTC examples.
  docs_gardener:
    - SSOT section 3.6 summarizes gate outcome only.
    - WORKING remains the planning trace.

round_2_cross_check:
  fe_to_qc:
    issue: degraded report must still be actionable and not just an error blob.
    final_change: degraded fixture must include action, confidence, warnings, and invalidation guidance.
  qc_to_fe:
    issue: actionability can be subjective.
    final_change: fixture asserts required fields exist, not investment correctness.
  db_to_devops:
    issue: artifact refs need a future path policy.
    final_change: fixture uses artifact_ref object with ref_type and ref, not local absolute path.
  devops_to_db:
    issue: future DB portability should not leak into DTO names.
    final_change: DTOs stay domain-named; storage mapping notes handle persistence.
  be_to_docs:
    issue: docs should not duplicate exact Pydantic definitions after implementation.
    final_change: SSOT records contract intent; code becomes executable contract after DTO_CONTRACT_GO.
  cto_to_all:
    issue: this slice must remain small.
    final_change: implementation scope is limited to contracts, fixtures, and tests.

round_2_final_improved_plans:
  fe:
    final_gate: FE_DTO_SIGNOFF
    final_requirements:
      - latest_signal_report can answer current action, risk, invalidation, entry, stop, take-profit, freshness.
      - degraded report remains explicit and actionable.
  db:
    final_gate: DB_DTO_SIGNOFF
    final_requirements:
      - every DTO field is classifiable for future storage.
      - no migration or DDL is added in this slice.
  be:
    final_gate: BE_DTO_SIGNOFF
    final_requirements:
      - Pydantic models validate fixtures.
      - contracts import without server, Hermes, live APIs, or DB.
  qc:
    final_gate: QC_DTO_SIGNOFF
    final_requirements:
      - golden and negative tests run offline.
      - tests do not write DB/data artifacts.
  devops:
    final_gate: DEVOPS_DTO_SIGNOFF
    final_requirements:
      - fixtures are portable and path-safe.
      - no new service, cron, or local state dependency is introduced.
  docs_gardener:
    final_gate: DOCS_DTO_SIGNOFF
    final_requirements:
      - SSOT points to DTO gate and constraints.
      - WORKING names the next atomic implementation step.

cto_synthesis:
  call: READY_FOR_DTO_CONTRACT_GO_REVIEW
  approved_sequence_if_go:
    1: add contract models
    2: add golden fixtures
    3: add offline contract tests
    4: run health_check, pytest, and ruff
    5: return for DTO_CONTRACT_GO sign-off or corrections
  no_go_conditions:
    - migration, DDL, or repository persistence appears in the DTO slice
    - DTO tests require live APIs, Hermes, MCP transport, or SQLite files
    - fixtures contain absolute local paths
    - report DTO cannot represent stale/degraded data
  cto_recommendation: proceed only after explicit DTO_CONTRACT_GO
```

## P1 Storage Schema FE DB BE Review

```yaml
scope: P1 storage/schema architecture review before migrations
mode: review_only_no_code
context:
  p0_status: closed_and_pushed
  starting_point: design storage contracts before SQLite migrations or domain tables

fe_team:
  focus: future report/dashboard/query experience, even before UI exists
  required_views:
    - latest_market_snapshot_by_symbol
    - latest_signal_by_asset
    - signal_detail_with_features_reasons_and_guide
    - signal_outcome_timeline
    - score_performance_by_bin
    - config_version_comparison
    - watchdog_or_data_staleness_status
  schema_requirements:
    - every user-facing signal needs action, score, confidence/weakness, entry, stop, take_profit, and invalidation fields
    - explanations should be stored as structured reason_json plus concise summary fields for list views
    - evidence cards need source, timestamp, asset_scope, bias, strength, confidence, and ref/path
    - stale data and degraded mode must be queryable so UI/report can warn instead of showing silent BUY
  concerns:
    - pure JSON blobs will be hard to filter/sort for reports
    - too many normalized tables too early can slow iteration
    - missing timestamps/timezones will make market-session views confusing
  recommendation:
    - use hybrid schema: indexed core columns for common filters plus raw_json for replay detail
    - define API/report DTOs before finalizing tables

db_team:
  focus: durable schema, migrations, replay, performance, backup path
  required_decisions:
    - primary key strategy: text UUID/run_id/signal_id vs integer ids
    - timestamp convention: UTC ISO string or epoch milliseconds
    - symbol/asset normalization: asset, underlying, universe, timeframe
    - JSON storage policy: which fields get columns vs JSON blobs
    - indexes for latest snapshot, signal lookup, labeling window, config hash, run status
    - migration convention and idempotency tests
    - retention policy for raw evidence/artifacts/checkpoints
  proposed_initial_tables:
    - schema_migrations
    - strategy_config
    - run_journal
    - feature_store
    - evidence_card
    - signal_ledger
    - label_store
    - watchdog_event
    - artifact_ref
  concerns:
    - SQLite JSON querying is possible but limited; do not bury all searchable fields in JSON
    - high-volume raw news/PDF/chart artifacts should be file/ref based, not stored inline
    - schema must make signal replay possible from config_hash plus feature/evidence refs
  recommendation:
    - start with SQLite plus explicit SQL migrations and stdlib sqlite3
    - keep PostgreSQL portability in mind by avoiding SQLite-only cleverness in core schema

be_team:
  focus: MCP tool contracts, data ingestion, scoring, replay, and harnessability
  required_contracts:
    - repository layer for DB access, separate from MCP tools
    - Pydantic schemas for tool inputs/outputs and stored records
    - write paths for snapshots/signals/labels/configs/runs
    - replay path from signal_id to features/evidence/config
    - idempotency key handling for cron/report jobs
    - degraded mode and stale-data propagation into generated guides
  concerns:
    - schema should not force live API calls during tests
    - storage code should not import Hermes-facing report code
    - scoring must receive validated strategy_config, not hardcoded defaults
  recommendation:
    - implement storage with repository functions and fixture/golden tests before adding market adapters
    - make all P1 storage tests offline with tmp_path SQLite DBs

cross_checks:
  fe_to_db:
    finding: list/detail/report views need sortable/filterable columns.
    adjustment: expose action, final_score, asset, underlying, timeframe, created_at, config_hash, status as columns, not only JSON.
  db_to_fe:
    finding: not every explanation field should become a column.
    adjustment: keep detailed reasons/evidence in JSON/ref tables; project concise summaries for views.
  fe_to_be:
    finding: UI/report needs degraded/stale warnings.
    adjustment: BE tool outputs include data_freshness and degraded_mode fields.
  be_to_fe:
    finding: early UI DTOs must not require final dashboard design.
    adjustment: define minimal report DTO around current Telegram/report needs first.
  db_to_be:
    finding: replay requires stable references.
    adjustment: signal_ledger stores config_hash plus feature_snapshot_id/evidence_bundle_ref/run_id.
  be_to_db:
    finding: tests need isolated DBs.
    adjustment: storage API accepts explicit database path and never writes to data/ in tests.
  cto_to_all:
    finding: P1 schema should optimize for replay and audit before dashboards.
    adjustment: no migration is written until replay query for one signal is designed.
  docs_to_all:
    finding: SSOT currently has conceptual tables but not final DDL.
    adjustment: next doc update should add P1 schema decision log before code.

open_decisions_before_p1_code:
  - timestamp representation and timezone convention
  - ID convention and whether ids are text UUIDs
  - exact initial table list
  - core columns vs JSON blob split
  - evidence/artifact storage by DB row vs file/ref
  - migration file naming and rollback policy
  - minimum replay query contract
  - whether P1 includes only storage skeleton or also first market snapshot table

cto_report:
  recommendation: do not write migrations yet
  reason: FE/DB/BE all depend on the same replay/report contract, so the next step is a schema decision log
  next_action:
    - create P1 storage/schema decision doc section in SSOT
    - freeze initial DTOs and replay query
    - then implement SQLite migration skeleton and tests
```

## P1 Cross-Team Review And Revised Plan

```yaml
scope: reconcile FE/DB/BE opinions into an executable P1 plan
mode: review_only_no_code

cross_team_review:
  fe_reviews_db:
    agrees:
      - core columns are needed for common list/detail/report queries
      - raw evidence and large artifacts should be references, not inline blobs
    concerns:
      - DB table design should not expose only internal audit concepts; report consumers need concise fields
      - too much normalization may make simple Telegram reports tedious
    requested_changes:
      - define minimal report DTO before DDL
      - include data_freshness/degraded_mode fields early
  fe_reviews_be:
    agrees:
      - BE should expose DTOs instead of making FE/report code understand DB tables
      - degraded/stale warnings must be tool output, not only DB metadata
    concerns:
      - replay-first design might miss quick "what should I do now?" report needs
    requested_changes:
      - define latest signal/report read model alongside replay query
      - keep summary fields separate from detailed reason_json
  db_reviews_fe:
    agrees:
      - searchable columns are needed for asset/action/time/config/status filters
      - list views need stable concise fields
    concerns:
      - every UI/report desire cannot become a column
      - dashboard-oriented schema could hurt replay/audit if built first
    requested_changes:
      - split read models into core indexed columns plus JSON detail
      - treat dashboard convenience views as derived later
  db_reviews_be:
    agrees:
      - repository layer and tmp_path SQLite tests are mandatory
      - config_hash plus feature/evidence refs are needed for replay
    concerns:
      - BE may hide schema issues behind repository abstractions if DDL is vague
      - idempotency and uniqueness must be enforced at DB level, not only service code
    requested_changes:
      - define unique constraints and indexes in the decision log
      - define replay query before repository implementation
  be_reviews_fe:
    agrees:
      - report DTOs are needed before schema implementation
      - degraded/stale states must be surfaced explicitly
    concerns:
      - FE/dashboard needs should not force premature web UI architecture
    requested_changes:
      - start with Telegram/report DTO, not full dashboard DTO
      - keep DTO versioned so future UI can evolve
  be_reviews_db:
    agrees:
      - explicit SQL migrations and SQLite tmp_path tests are the right start
      - raw artifacts should be stored by reference
    concerns:
      - schema cannot be so generic that repository code becomes complex mapping glue
      - SQLite/PostgreSQL portability should not block MVP speed
    requested_changes:
      - choose pragmatic SQLite-compatible DDL now, document portability notes
      - keep first migration small but useful

resolved_consensus:
  principles:
    - replay/audit is the primary schema driver
    - report/read DTO is the second driver
    - dashboard convenience is deferred
    - hybrid storage is required: indexed core columns plus JSON/ref detail
    - large artifacts stay file/ref based
    - no live API dependency in P1 storage tests
  first_read_models:
    - latest_signal_report_dto
    - signal_replay_bundle
    - storage_health_or_db_check
  first_replay_query:
    input: signal_id
    output:
      - signal_ledger row
      - linked feature_store snapshot
      - linked evidence_card refs
      - strategy_config by config_hash
      - run_journal context
      - label_store outcome if available
  proposed_id_policy:
    direction: text ids for externally referenced records
    candidates:
      - run_id
      - signal_id
      - feature_snapshot_id
      - evidence_id
      - config_hash
    still_open: exact UUID/ULID format
  proposed_time_policy:
    direction: UTC timestamps everywhere
    still_open: ISO-8601 text vs epoch milliseconds
  proposed_p1_scope:
    include:
      - schema decision log in SSOT
      - DTO definitions for latest signal report and replay bundle
      - migration skeleton
      - initial DDL for schema_migrations, strategy_config, run_journal, feature_store, evidence_card, signal_ledger, label_store, artifact_ref
      - offline migration/idempotency/replay fixture tests
    defer:
      - watchdog_event table until runtime watchdog implementation starts
      - dashboard materialized views
      - live market adapters
      - scoring engine

revised_p1_execution_plan:
  step_1_decision_log:
    owner: CTO + DB
    outputs:
      - final initial table list
      - ID and timestamp policy
      - core-column vs JSON/ref policy
      - replay query contract
      - migration naming and idempotency rules
    gate: FE/DB/BE sign-off before code
  step_2_dto_contracts:
    owner: BE + FE
    outputs:
      - latest_signal_report DTO
      - signal_replay_bundle DTO
      - storage_health/db_check DTO
    gate: DTOs can be tested without DB and do not imply live APIs
  step_3_migration_skeleton:
    owner: DB + BE
    outputs:
      - storage/db.py
      - storage/migrations
      - schema_migrations
      - initial DDL only after decision log
    gate: repeated migration run is idempotent
  step_4_fixture_tests:
    owner: QC
    outputs:
      - tmp_path SQLite tests
      - golden replay fixture
      - migration idempotency test
      - no writes to repo data/
    gate: pytest and ruff pass offline
  step_5_docs_devops_update:
    owner: Docs Gardener + DevOps
    outputs:
      - README storage commands after verified
      - DevOps DB path/backup notes
      - WORKING updated to P1 implementation state
    gate: no unverified commands in README

cto_final_plan:
  call: proceed_to_p1_decision_log
  do_not_code_yet:
    - migrations
    - repository layer
    - domain tables
  immediate_next_action:
    - write P1 storage/schema decision log into SSOT
    - include FE/DB/BE sign-off criteria
```

## CTO Synthesis For P1 Storage Schema

```yaml
scope: CTO synthesis of FE/DB/BE cross-review
decision_level: architecture_gate_before_p1_code

cto_summary:
  primary_goal: make every future signal replayable, auditable, and reportable
  secondary_goal: keep P1 small enough to implement and test offline
  hard_rule: no migration or repository code until the decision log freezes DTOs, replay query, and initial table list

what_each_team_got_right:
  fe:
    - reporting/query needs must influence schema now
    - degraded_mode and data_freshness must be first-class
    - pure JSON blobs would make future reporting painful
  db:
    - replay/audit requires stable ids, timestamps, indexes, and refs
    - large artifacts should be file/ref based
    - schema should remain PostgreSQL-portable where practical
  be:
    - MCP tools should not talk directly to raw SQL
    - repository and DTO boundaries are needed
    - storage tests must be offline and fixture-driven

cto_corrections:
  fe:
    - do not design a dashboard database yet
    - start with Telegram/report read model only
  db:
    - do not over-normalize before real data arrives
    - allow JSON detail where replay needs flexible evidence
  be:
    - do not hide ambiguous schema behind repository abstractions
    - force replay query and constraints to be explicit before implementation

final_architecture_direction:
  storage_style: hybrid relational core plus JSON/ref detail
  first_optimization_target: replay one signal completely
  second_optimization_target: produce latest actionable report quickly
  deferred_target: dashboard/materialized analytics views

minimum_p1_contract_before_code:
  dto_contracts:
    - latest_signal_report
    - signal_replay_bundle
    - storage_health
  replay_contract:
    input: signal_id
    must_return:
      - signal metadata and action
      - feature snapshot used at decision time
      - evidence refs/cards used at decision time
      - strategy_config/config_hash used at decision time
      - run_journal context
      - label outcome if available
  schema_contract:
    must_decide:
      - ID policy
      - timestamp policy
      - initial table list
      - searchable columns
      - JSON/ref fields
      - indexes and uniqueness
      - migration naming/idempotency

initial_table_direction:
  include_in_first_p1_migration_if_decision_log_confirms:
    - schema_migrations
    - strategy_config
    - run_journal
    - feature_store
    - evidence_card
    - signal_ledger
    - label_store
    - artifact_ref
  defer:
    - watchdog_event until runtime watchdog implementation starts
    - dashboard-specific summary/materialized views
    - market adapter provider-specific tables

implementation_sequence_cto_approved:
  1_decision_log:
    output: SSOT section with table intent, DTOs, replay query, IDs, timestamps, indexes
    exit_gate: FE/DB/BE sign-off
  2_contract_tests:
    output: DTO fixture/golden tests without SQLite
    exit_gate: report DTO and replay bundle shape are stable
  3_sqlite_migration_skeleton:
    output: sqlite3 migration runner plus first migration
    exit_gate: idempotent tmp_path migration tests
  4_repository_layer:
    output: minimal read/write functions for chosen tables
    exit_gate: replay query fixture passes offline
  5_docs_devops:
    output: verified DB commands, path policy, backup/retention notes
    exit_gate: no unverified commands in README

go_no_go:
  current_call: GO_FOR_DECISION_LOG_ONLY
  no_go_for_code_until:
    - latest_signal_report DTO is defined
    - signal_replay_bundle DTO is defined
    - signal_id replay query is defined
    - ID/timestamp policy is frozen
    - initial table list is frozen
    - FE/DB/BE sign-off is recorded

cto_rationale:
  - schema mistakes are expensive because they poison feedback, replay, and scoring evaluation
  - P1 should be designed around one complete replay path, not around all future analytics
  - this keeps the system useful for Telegram reports while preserving long-term auditability
```

## P1 Team-Level Detailed Development Plan

```yaml
scope: detailed team plans following CTO-approved execution sequence
mode: planning_only_no_code

sequence_1_decision_log:
  objective: write the P1 storage/schema decision log in SSOT before implementation
  teams:
    cto:
      owns:
        - final architecture tradeoff call
        - P1 scope boundary
        - go/no-go after FE/DB/BE review
      deliverables:
        - approved initial table list
        - approved replay-first principle
        - approved report DTO priority
        - list of explicitly deferred tables/views
      exit_criteria:
        - no code is allowed until CTO marks decision_log_go
    db:
      owns:
        - table intent definitions
        - ID policy proposal
        - timestamp policy proposal
        - index/unique constraint proposal
        - migration naming/idempotency proposal
      deliverables:
        - schema_migrations policy
        - initial table intent for strategy_config, run_journal, feature_store, evidence_card, signal_ledger, label_store, artifact_ref
        - column-vs-json/ref split proposal
        - replay query draft
      exit_criteria:
        - every proposed table explains why it is needed for replay/report
    fe:
      owns:
        - report/read-model requirements
        - list/detail fields for Telegram/report use
        - data_freshness/degraded_mode visibility
      deliverables:
        - latest_signal_report field list
        - signal detail/report fields
        - minimum warning fields for stale/partial data
      exit_criteria:
        - FE confirms report DTO can answer "what should I do now?"
    be:
      owns:
        - DTO boundaries
        - repository boundary proposal
        - replay query contract from API/tool perspective
      deliverables:
        - latest_signal_report DTO sketch
        - signal_replay_bundle DTO sketch
        - storage_health DTO sketch
        - repository function list
      exit_criteria:
        - BE confirms DTOs can be tested without DB/live API
    qc:
      owns:
        - acceptance criteria for schema decision
        - fixture/golden test plan
      deliverables:
        - migration idempotency test cases
        - replay fixture requirements
        - tmp_path SQLite isolation rules
      exit_criteria:
        - QC confirms future tests can prove replay and no data/ writes
    devops:
      owns:
        - DB path policy
        - local artifact/backup/retention considerations
      deliverables:
        - default SQLite URL policy
        - data/ ignore policy confirmation
        - future backup/restore notes
      exit_criteria:
        - DevOps confirms local DB artifacts will stay out of git
    docs_gardener:
      owns:
        - SSOT update structure
        - no duplicated schema truth
      deliverables:
        - P1 decision log section in docs/halo-swing-development-plan.md
        - WORKING pointer to the decision log
      exit_criteria:
        - docs contain one canonical schema decision source

sequence_2_dto_contract_tests:
  objective: freeze DTO shape before SQLite migration code
  teams:
    fe:
      deliverables:
        - latest_signal_report expected sample
        - stale/degraded report example
      review_focus:
        - human-readable action, score, entry, stop, take_profit, invalidation, warning fields
    be:
      deliverables:
        - Pydantic DTOs or typed schema module proposal
        - fixture builders for latest_signal_report and signal_replay_bundle
      review_focus:
        - no DB dependency
        - no live API dependency
    qc:
      deliverables:
        - golden JSON fixtures for DTOs
        - tests proving deterministic serialization
      review_focus:
        - no timestamp/path nondeterminism
    db:
      deliverables:
        - mapping note from DTO fields to future table columns/json/ref fields
      review_focus:
        - DTOs do not require unplanned tables
    cto:
      exit_gate:
        - DTO_CONTRACT_GO only if FE/DB/BE all sign off

sequence_3_sqlite_migration_skeleton:
  objective: implement storage foundation only after decision log and DTOs are frozen
  teams:
    db:
      deliverables:
        - first migration file
        - schema_migrations table
        - initial approved tables only
        - indexes/unique constraints from decision log
      review_focus:
        - idempotency
        - PostgreSQL portability notes
    be:
      deliverables:
        - storage/db.py migration runner
        - database URL/path helper
        - storage health/db_check function
      review_focus:
        - stdlib sqlite3 unless explicitly revised
        - no global long-lived connection
    devops:
      deliverables:
        - DB path examples
        - local data directory handling
      review_focus:
        - no committed DB files
        - paths with spaces handled by Path APIs
    qc:
      deliverables:
        - tmp_path migration tests
        - repeated migration idempotency tests
        - db_check golden fixture
      review_focus:
        - no writes to repo data/
    cto:
      exit_gate:
        - MIGRATION_SKELETON_GO only if tests prove idempotency and scope does not include live adapters/scoring

sequence_4_repository_layer:
  objective: add minimal storage read/write API around approved tables
  teams:
    be:
      deliverables:
        - repository functions for strategy_config, run_journal, feature_store, evidence_card, signal_ledger, label_store, artifact_ref
        - replay query function by signal_id
      review_focus:
        - repository stays below MCP tool layer
        - replay query returns signal_replay_bundle DTO
    db:
      deliverables:
        - query/index review for replay and latest report
      review_focus:
        - constraints enforce idempotency where needed
    fe:
      deliverables:
        - latest report read-model verification
      review_focus:
        - latest_signal_report can be produced without custom dashboard logic
    qc:
      deliverables:
        - replay fixture test
        - repository round-trip tests
      review_focus:
        - deterministic fixtures
        - no live APIs
    cto:
      exit_gate:
        - REPOSITORY_GO only if one signal can be replayed from fixture data

sequence_5_docs_devops_update:
  objective: publish only verified commands and update operational notes
  teams:
    docs_gardener:
      deliverables:
        - README storage commands after verification
        - WORKING current state update
        - SSOT links to schema decision log
      review_focus:
        - no unverified command in README
    devops:
      deliverables:
        - DB path/backup/restore/retention notes
        - local artifact safety checklist
      review_focus:
        - data/ remains ignored
        - production cron still not enabled
    qc:
      deliverables:
        - final verification command list
      review_focus:
        - pytest and ruff pass
        - storage smoke is offline

overall_cto_gates:
  no_go_conditions:
    - migrations before decision log
    - DTOs that require live APIs
    - DB writes to repo data/ during tests
    - signal/report data stored only as opaque JSON with no indexed core columns
    - repository layer hiding undefined schema rules
    - README listing commands before verification
  success_definition:
    - P1 starts with a signed-off schema decision log
    - DTOs are testable before DB code
    - migrations are idempotent
    - one signal replay path works offline from fixture data
```

## P1 Team Plan Review Round 1 And 2

```yaml
scope: each team reviews every other team plan, then plans are improved twice before CTO synthesis
mode: planning_only_no_code

round_1_cross_review:
  fe_reviews:
    db_plan:
      issue: DB plan names tables but does not yet identify which fields are needed for list/report rendering.
      requested_improvement:
        - add read-model columns for action, final_score, confidence, asset, underlying, timeframe, data_freshness, degraded_mode, created_at
    be_plan:
      issue: BE DTO plan is right but could drift from report language if it starts from internal records.
      requested_improvement:
        - create latest_signal_report from user-facing report needs first
        - keep reason_summary separate from reason_json
    qc_plan:
      issue: QC fixtures mention deterministic serialization but not human report examples.
      requested_improvement:
        - add one golden latest_signal_report fixture with stale/degraded warning
    devops_plan:
      issue: DB path and backup policy are useful later but FE needs artifact URLs/refs to be renderable.
      requested_improvement:
        - define artifact_ref fields that can later resolve to image/PDF/chart locations
  db_reviews:
    fe_plan:
      issue: FE wants many user-facing fields; risk of turning every display field into a physical column.
      requested_improvement:
        - separate indexed columns, derived DTO fields, and JSON detail
    be_plan:
      issue: repository layer plan lacks explicit transaction and uniqueness strategy.
      requested_improvement:
        - define transaction boundaries for writing signal plus feature/evidence refs
        - define unique constraints for idempotency keys and config_hash
    qc_plan:
      issue: migration idempotency test is necessary but insufficient.
      requested_improvement:
        - add constraint violation tests and replay query missing-link tests
    devops_plan:
      issue: backup policy cannot be designed after schema because artifact refs and DB file must move together.
      requested_improvement:
        - include artifact directory and DB backup as one backup unit
  be_reviews:
    fe_plan:
      issue: latest report DTO could become too presentation-specific.
      requested_improvement:
        - define semantic fields, not formatted strings
        - leave final text rendering to Hermes/report layer
    db_plan:
      issue: table list may be too broad for first migration if all tables are implemented at once.
      requested_improvement:
        - split first migration into core replay tables and later operational tables if needed
    qc_plan:
      issue: QC should test DTOs before DB, but repository tests also need realistic relational links.
      requested_improvement:
        - add fixture pack that contains one complete replay bundle across all core tables
    docs_plan:
      issue: SSOT decision log must be easy for code agents to consume.
      requested_improvement:
        - use table-by-table structured blocks with columns, indexes, references, and purpose
  qc_reviews:
    fe_plan:
      issue: FE acceptance needs exact expected fields, not broad view names.
      requested_improvement:
        - define mandatory/optional fields for latest_signal_report
    db_plan:
      issue: DB plan must define expected failure behavior.
      requested_improvement:
        - specify what happens when replay links are missing or config_hash is unknown
    be_plan:
      issue: BE repository tests need command-level harness coverage too.
      requested_improvement:
        - add storage_health/db_check harness after migration skeleton
    devops_plan:
      issue: no test should write to data/ but the plan needs a check for that.
      requested_improvement:
        - QC adds assertion that repo data/ is not created by tests
  devops_reviews:
    fe_plan:
      issue: artifact refs must not assume local absolute paths in reports.
      requested_improvement:
        - store artifact_ref as type plus relative path/ref, with absolute resolution at runtime
    db_plan:
      issue: SQLite file layout and artifact directories must be migration/backup friendly.
      requested_improvement:
        - define data/db, data/artifacts, data/backups conventions later in P1
    be_plan:
      issue: repository functions need explicit connection lifecycle.
      requested_improvement:
        - one connection per operation/test context unless a transaction is passed in
    qc_plan:
      issue: tests can pass while leaving temp files if cleanup is implicit.
      requested_improvement:
        - ensure tmp_path-only tests and no repo-local DB/artifact files
  docs_reviews:
    all_plans:
      issue: responsibilities are clear, but sign-off artifacts are scattered.
      requested_improvement:
        - add one P1 sign-off matrix with rows FE/DB/BE/QC/DevOps/Docs/CTO and columns decision_log, DTO, migration, repository, docs

round_1_improved_plan:
  changes:
    - split fields into indexed_columns, dto_derived_fields, json_detail, artifact_refs
    - add latest_signal_report mandatory/optional field list to decision log
    - add signal_replay_bundle missing-link behavior
    - add transaction/idempotency design to DB decision log
    - add storage fixture pack with one full replay bundle
    - add artifact_ref portability rule: no committed absolute local paths
    - add sign-off matrix to WORKING and SSOT decision log
  updated_sequence:
    1_decision_log:
      additions:
        - field classification policy
        - transaction/idempotency policy
        - artifact_ref portability policy
        - missing-link failure policy
        - sign-off matrix
    2_dto_contract_tests:
      additions:
        - latest_signal_report stale/degraded golden
        - mandatory/optional field checks
    3_migration_skeleton:
      additions:
        - unique constraints and transaction boundaries from decision log
        - no repo data/ write test
    4_repository_layer:
      additions:
        - one complete replay bundle fixture
        - missing-link error tests

round_2_cross_review:
  fe_reviews_improved_plan:
    verdict: mostly_approved
    remaining_issue: latest_signal_report still needs semantic field names stable enough for Hermes output.
    final_adjustment:
      - include action_label, risk_summary, invalidation_summary, data_warnings as semantic fields
  db_reviews_improved_plan:
    verdict: approved_with_scope_guard
    remaining_issue: initial table list may still be too large if watchdog/artifact concerns creep in.
    final_adjustment:
      - first migration includes artifact_ref but defers watchdog_event
      - artifact_ref is minimal and generic
  be_reviews_improved_plan:
    verdict: approved
    remaining_issue: repository transaction scope needs one clear first use case.
    final_adjustment:
      - first transaction use case is record_signal_bundle(feature + evidence refs + signal + run link)
  qc_reviews_improved_plan:
    verdict: approved_with_tests_added
    remaining_issue: missing-link behavior must be deterministic.
    final_adjustment:
      - missing replay link returns structured error code, not partial success
  devops_reviews_improved_plan:
    verdict: approved
    remaining_issue: backup/restore should not block first migration.
    final_adjustment:
      - document backup conventions, but do not implement backup tooling in first P1 slice
  docs_reviews_improved_plan:
    verdict: approved
    remaining_issue: WORKING is growing long.
    final_adjustment:
      - SSOT gets durable decision log; WORKING keeps current state and gates after next doc pass

round_2_final_improved_plan:
  decision_log_must_include:
    field_classes:
      indexed_columns:
        - identifiers
        - timestamps
        - asset/underlying/timeframe
        - action/status
        - score/config_hash
        - data_freshness/degraded_mode
      dto_derived_fields:
        - action_label
        - risk_summary
        - invalidation_summary
        - data_warnings
      json_detail:
        - reason_json
        - guide_json
        - component_scores_json
        - raw_features_json
      artifact_refs:
        - chart_ref
        - pdf_ref
        - news_ref
        - evidence_source_ref
    replay_contract:
      first_use_case: replay one signal by signal_id
      missing_link_policy: structured error code, no silent partial success
    write_contract:
      first_transaction: record_signal_bundle
      includes:
        - run_journal row
        - feature_store snapshot
        - evidence_card refs
        - signal_ledger row
      idempotency: enforced by run_id/idempotency_key and unique constraints
    artifact_policy:
      storage: file/ref based
      portability: no committed absolute local paths
      first_migration: minimal artifact_ref table only
    test_policy:
      dto_tests_before_db: true
      tmp_path_sqlite_only: true
      no_repo_data_writes: true
      complete_replay_fixture_required: true

cto_synthesis_after_two_rounds:
  call: SSOT_DECISION_LOG_DRAFTED
  code_status: still_no_code
  approved_changes_to_plan:
    - latest_signal_report starts from semantic report fields, not UI widgets
    - schema separates indexed columns, DTO-derived fields, JSON detail, and artifact refs
    - first repository transaction is record_signal_bundle
    - replay missing-link behavior is explicit and deterministic
    - artifact refs are portable and minimal in first migration
    - backup conventions are documented but backup tooling is deferred
  next_action:
    - implement DTO contracts and golden fixtures
    - prepare MIGRATION_GO decision packet after DTO_CONTRACT_GO
  no_go_until:
    - DTO_CONTRACT_GO before migration design freeze
    - MIGRATION_GO before migration/DDL code
    - REPOSITORY_GO before repository persistence code
```

## P1 Team Plans Two-Pass Review And CTO Synthesis

```yaml
scope: team detailed development plans, first cross-check, improvement, second cross-check, second improvement, CTO synthesis
mode: planning_only_no_code
source_of_truth: docs/halo-swing-development-plan.md#35-p1-storageschema-decision-log

baseline_team_plans:
  fe:
    objective: make storage useful for Telegram/report and future UI without designing a dashboard database.
    detailed_plan:
      - define latest_signal_report semantic field list.
      - define stale/degraded report sample.
      - classify report fields into required, optional, derived, and warning fields.
      - verify the report can answer "what should I do now?" from stored data.
      - confirm chart/pdf/news refs can be rendered later without absolute local paths.
    deliverables:
      - latest_signal_report sample
      - stale/degraded report sample
      - semantic field glossary
    initial_risks:
      - overfitting schema to future dashboard views
      - hiding report-critical fields in JSON only
  db:
    objective: design durable replay-first SQLite schema that can later migrate to PostgreSQL.
    detailed_plan:
      - propose ID policy and timestamp policy.
      - classify indexed columns vs JSON detail vs artifact refs.
      - define table intent and references for initial P1 tables.
      - define indexes and unique constraints for replay, latest report, config_hash, and idempotency.
      - define migration naming and idempotency rules.
    deliverables:
      - initial table list
      - table-by-table purpose/columns/indexes/ref notes
      - replay query draft
      - idempotency and constraint proposal
    initial_risks:
      - over-normalization before real data
      - under-indexing common report/replay queries
  be:
    objective: define DTO and repository contracts without coupling MCP tools to raw SQL.
    detailed_plan:
      - define latest_signal_report DTO.
      - define signal_replay_bundle DTO.
      - define storage_health DTO.
      - define repository function list and transaction boundaries.
      - define record_signal_bundle as first transaction use case.
    deliverables:
      - DTO contract sketches
      - repository boundary proposal
      - first transaction contract
      - replay API contract
    initial_risks:
      - repository abstraction hiding incomplete schema decisions
      - DTOs drifting from actual report needs
  qc:
    objective: ensure P1 storage is provable offline before live data adapters exist.
    detailed_plan:
      - define DTO golden fixture tests.
      - define migration idempotency tests.
      - define replay fixture pack.
      - define missing-link error tests.
      - assert tests never write to repo data/.
    deliverables:
      - acceptance test matrix
      - fixture/golden plan
      - missing-link behavior test plan
    initial_risks:
      - testing only happy-path migrations
      - missing path/timestamp nondeterminism
  devops:
    objective: keep local DB/artifact state reproducible, portable, and out of git.
    detailed_plan:
      - define default SQLite URL and data directory convention.
      - define artifact ref portability rule.
      - define backup/restore/retention notes.
      - define local absolute path resolution rule.
      - confirm no production cron is enabled in P1 storage work.
    deliverables:
      - DB path policy
      - artifact path policy
      - backup/retention notes
      - local artifact safety checklist
    initial_risks:
      - committed DB/artifact files
      - absolute local paths leaking into persisted records
  docs_gardener:
    objective: keep SSOT as canonical schema decision source and prevent WORKING from becoming the durable spec.
    detailed_plan:
      - keep P1 decision log in SSOT.
      - keep WORKING focused on current state, gates, and next action.
      - link docs instead of duplicating final schemas.
      - remove unverified commands from README/DevOps docs.
    deliverables:
      - SSOT decision log structure
      - WORKING pointer and current task update
      - sign-off matrix location
    initial_risks:
      - schema truth split across WORKING and SSOT
      - commands documented before verification

round_1_cross_check:
  fe_to_db:
    issue: DB plan needs explicit report/read fields, not only replay fields.
    required_change: mark action, score, asset, timeframe, data_freshness, degraded_mode, created_at as indexed/read fields.
  fe_to_be:
    issue: DTOs should start from report semantics, not internal record names.
    required_change: add action_label, risk_summary, invalidation_summary, data_warnings.
  db_to_fe:
    issue: FE field list could turn every report phrase into a column.
    required_change: split fields into indexed_columns, dto_derived_fields, json_detail, artifact_refs.
  db_to_be:
    issue: repository plan needs DB-enforced idempotency.
    required_change: define unique constraints for run_id/idempotency_key/config_hash before repository code.
  be_to_db:
    issue: first migration table set may be too broad.
    required_change: first migration must justify every table by replay/report need.
  be_to_qc:
    issue: replay tests need realistic linked records, not isolated DTO objects.
    required_change: add one complete replay fixture pack.
  qc_to_fe:
    issue: FE acceptance criteria need exact mandatory/optional fields.
    required_change: latest_signal_report fields must be explicitly required/optional.
  qc_to_db:
    issue: missing replay links need deterministic behavior.
    required_change: define structured error code policy.
  devops_to_all:
    issue: artifact refs and DB paths must be portable.
    required_change: no absolute local paths in persisted records.
  docs_to_all:
    issue: sign-off artifacts are scattered.
    required_change: add one sign-off matrix in SSOT.

round_1_improved_plans:
  fe:
    changes:
      - latest_signal_report now defines required/optional fields.
      - report fields are semantic, not display strings.
      - stale/degraded warning sample becomes required fixture.
  db:
    changes:
      - field classification policy added.
      - unique/index/idempotency section added.
      - first table list tied to replay/report purpose.
  be:
    changes:
      - record_signal_bundle chosen as first transaction.
      - DTO contracts precede repository implementation.
      - replay API must return structured errors.
  qc:
    changes:
      - golden DTO tests occur before DB tests.
      - replay fixture pack spans run, features, evidence, signal, config, and optional label.
      - no repo data/ write assertion added.
  devops:
    changes:
      - artifact_ref portability rule added.
      - DB/artifact backup considered one future unit.
      - backup tooling deferred.
  docs_gardener:
    changes:
      - SSOT decision log holds final policy.
      - WORKING keeps review trail and current gate only.
      - sign-off matrix added to SSOT.

round_2_cross_check:
  fe_to_db:
    issue: field classification is good, but data_freshness/degraded_mode must be persisted early.
    final_change: keep data_freshness_status and degraded_mode in indexed/core columns.
  db_to_fe:
    issue: action_label/risk_summary are derived and should not drive DB constraints.
    final_change: store summary-capable source fields; DTO derives action_label/risk_summary.
  be_to_db:
    issue: transaction contract needs explicit first operation.
    final_change: first operation is record_signal_bundle with run_journal, feature_store, evidence_card refs, signal_ledger.
  db_to_be:
    issue: transaction idempotency must be enforceable.
    final_change: run_id/idempotency_key/config_hash uniqueness remains a pre-code decision.
  qc_to_be:
    issue: structured errors must be testable.
    final_change: missing required replay link returns deterministic error code, not partial success.
  devops_to_db:
    issue: artifact_ref should not require backup tooling in first migration.
    final_change: artifact_ref is minimal and portable; backup tooling deferred.
  docs_to_all:
    issue: WORKING is becoming too long.
    final_change: next doc pass should trim WORKING after SSOT sign-off is recorded.

round_2_final_improved_plans:
  fe:
    final_plan:
      - sign off latest_signal_report required/optional fields in SSOT.
      - provide stale/degraded report sample.
      - verify report can be generated from core columns plus JSON/ref detail.
    final_gate: FE_SIGNOFF_DECISION_LOG
  db:
    final_plan:
      - sign off field classification policy.
      - sign off table intent, indexes, unique constraints, and migration naming.
      - keep watchdog_event and dashboard views deferred.
    final_gate: DB_SIGNOFF_DECISION_LOG
  be:
    final_plan:
      - sign off latest_signal_report, signal_replay_bundle, storage_health DTO contracts.
      - sign off record_signal_bundle transaction contract.
      - sign off repository boundary below MCP tools.
    final_gate: BE_SIGNOFF_DECISION_LOG
  qc:
    final_plan:
      - sign off DTO golden fixtures before DB code.
      - sign off migration idempotency and replay fixture tests.
      - sign off missing-link structured error tests.
    final_gate: QC_SIGNOFF_DECISION_LOG
  devops:
    final_plan:
      - sign off SQLite path/artifact_ref portability policy.
      - sign off no committed DB/artifacts.
      - document backup/retention conventions, defer tooling.
    final_gate: DEVOPS_SIGNOFF_DECISION_LOG
  docs_gardener:
    final_plan:
      - keep SSOT decision log as canonical.
      - update WORKING to sign-off status.
      - remove review-trail bulk once no longer needed.
    final_gate: DOCS_SIGNOFF_DECISION_LOG

cto_final_synthesis:
  call: READY_FOR_SIGNOFF_NOT_CODE
  summary:
    - team plans are now mutually compatible
    - no team is blocked by another team if sign-off happens in SSOT order
    - first implementation slice remains blocked until sign-off is recorded
  approved_execution_after_signoff:
    1: DTO contract/golden fixtures
    2: SQLite migration skeleton
    3: repository replay path
    4: docs/devops verified command update
  no_go_until:
    - DTO_CONTRACT_GO before migration design freeze
    - MIGRATION_GO before migration/DDL code
    - REPOSITORY_GO before repository persistence code
  cto_notes:
    - schema is now replay-first and report-aware
    - dashboard convenience remains deferred
    - artifact and path portability risk is handled early
    - missing-link behavior is explicit enough for QC
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
