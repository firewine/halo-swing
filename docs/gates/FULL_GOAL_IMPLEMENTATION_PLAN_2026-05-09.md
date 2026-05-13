# Full Goal Implementation Plan And Cross Review

> Date: 2026-05-09  
> Mode: staged implementation plan  
> Source of truth: `docs/halo-swing-development-plan.md`  
> Current baseline: offline MVP plus staged gates A-H, audit log, local audit web
> viewer, Phase 6 attribution/ablation/OOS hardening, report intent variants,
> position review report, delivery previews, evidence guards, and 156 passing tests

## 1. Objective

Bring Halo Swing from the current offline MVP toward the full documented product goal while preserving these constraints:

- deterministic offline harness remains the default test path
- no automatic trading without explicit future approval
- no secrets or runtime artifacts committed
- reusable module boundaries stay stronger than one-off implementation
- every phase adds tests, CLI harness coverage, and audit visibility

## 2. Current Gap Summary

Implemented and verified:

- FastMCP server and JSON CLI harness
- exact parity between health_check capabilities and MVP required tool manifest
- fixture-backed market, macro, event, news, indicator, chart tools
- Phase 1 market_snapshot.v1 core universe contract
- fixture-backed `1d`/`4h`/`1h` indicator timeframe contract
- Phase 1 swing level contract with gap/support/resistance and previous swing high/low
- Phase 2 strategy_config validation contract with bounds/sum/hash checks
- Phase 2 pullback and breadth component score contract
- Phase 2 position_management.v1 position decision contract
- Phase 3 macro filter contract with VIX/VXN/DXY/rate/oil block flags
- Phase 3 event_policy.v1 CPI/FOMC/NFP/EARNINGS taxonomy contract
- Phase 3 event danger window contract with summary and per-event block flags
- Phase 4 news_source_policy.v1 source taxonomy contract
- Phase 4 explicit news_score usage contract in score_leverage_swing
- Phase 5 run_journal.v1 JSONL recording contract
- Phase 5 signal_label_outcome.v1 MFE/MAE time-barrier metric contract
- Phase 5 NO_DATA and INVALIDATED_BY_EVENT label outcome contract
- leverage scoring, trade guide, position review
- Phase 2 trade_guide.v1 time-exit contract
- JSONL signal ledger and triple-barrier labeling
- score performance, score calibration, component attribution, ablation, and Champion/Challenger comparison
- deterministic 90-day fixture out-of-sample performance report
- deterministic 180-day fixture out-of-sample performance report with `fixture_oos_window.v1`
- Phase 6 unsupported long fixture window guard for requests beyond fixture coverage
- walk-forward fixture folds and conservative overfit guard
- Phase 6 deflated_sharpe_proxy.v1 conservative metric contract
- Phase 6 challenger_config.v1 shadow candidate contract
- Phase 6 feedback tool manifest covers evaluate_score_performance,
  suggest_weight_update, and compare_champion_challenger
- multimodal evidence modality and portable artifact refs
- Phase 8 chart_artifact.v1 render_chart contract and guard
- CHART ref slot artifact type guard
- CHART artifact_ref declaration negative coverage
- CHART artifact_ref reserved evidence_id guard
- CHART artifact_ref renderer value type guard
- CHART artifact_ref renderer value negative coverage
- CHART artifact_ref renderer text safety guard
- CHART artifact_ref ref_type DTO validation coverage
- guarded manual PDF/document summary evidence input
- guarded offline multimodal report context
- multimodal_context.guard schema self-checks
- multimodal_context payload key schema guard
- multimodal_context artifact_refs schema guard
- multimodal_context artifact_ref string field type guard
- PDF artifact_ref ref_type field negative coverage
- multimodal_context evidence_id uniqueness guard
- multimodal_context evidence card reserved id guard
- multimodal_context evidence card safe id guard
- multimodal_context artifact_ref evidence id safe guard
- multimodal_context evidence_id type guard
- multimodal_context artifact_ref value uniqueness guard
- multimodal_context CHART artifact ref PNG contract guard
- multimodal_context CHART artifact ref offline location guard
- multimodal_context CHART artifact ref file URI rejection coverage
- multimodal_context CHART artifact ref tilde path rejection coverage
- multimodal_context CHART machine-specific path rejection coverage
- multimodal_context artifact_ref embedded local path marker guard
- multimodal_context artifact_ref string safety guard
- multimodal_context content-address digest format guard for CHART/PDF artifact refs
- multimodal_context valid content-address acceptance coverage for CHART/PDF artifact refs
- multimodal_context evidence card asset scope guard
- multimodal_context evidence card categorical value guard
- multimodal_context evidence card summary bounds guard
- multimodal_context evidence card summary truncation consistency guard
- multimodal_context evidence card impact context-only guard
- multimodal_context artifact_ref ref_type contract guard
- multimodal_context artifact_ref metadata per-entry schema guard
- multimodal_context artifact_ref metadata schema guard
- multimodal_context artifact_ref metadata value safety guard
- multimodal_context artifact_ref metadata text string safety guard
- multimodal_context modality_counts guard
- multimodal_context evidence card key schema guard
- multimodal_context artifact_ref identity guard
- multimodal_context evidence card value safety guard
- multimodal_context evidence card scalar string safety guard
- multimodal_context evidence card text string safety guard
- multimodal_context evidence card supported modality guard
- document modality type negative coverage
- document bias type negative coverage
- document bias empty negative coverage
- multimodal_context evidence card explicit artifact URI guard
- multimodal_context PDF artifact ref contract guard
- document PDF artifact_ref empty value negative coverage
- document PDF artifact_ref ref_type empty negative coverage
- document PDF metadata description nonempty negative coverage
- document PDF metadata bool values negative coverage
- document PDF metadata missing key negative coverage
- CHART metadata missing key negative coverage
- CHART metadata values negative coverage
- CHART artifact_ref ref_type empty DTO validation coverage
- CHART artifact_ref ref_type lowercase DTO validation coverage
- CHART artifact_ref control character negative coverage
- CHART artifact_ref duplicate value negative coverage
- document evidence_id duplicate negative coverage
- document evidence card source key schema negative coverage
- document evidence card unexpected key schema negative coverage
- PDF artifact_ref unexpected key schema negative coverage
- PDF artifact_ref missing ref key negative coverage
- PDF artifact_ref missing ref_type key negative coverage
- PDF artifact_ref missing metadata key negative coverage
- CHART artifact_ref missing metadata key negative coverage
- CHART artifact_ref missing ref key DTO negative coverage
- CHART artifact_ref missing ref_type key DTO negative coverage
- CHART artifact_ref unexpected key DTO negative coverage
- CHART metadata unexpected key negative coverage
- PDF metadata unexpected key aggregate negative coverage
- document artifact_ref missing key portable guard negative coverage
- empty document artifact_ref dict collection negative coverage
- artifact_ref collection coverage guard
- null document artifact_ref collection negative coverage
- multimodal_context evidence card observed_at UTC ISO timestamp guard
- document observed_at type negative coverage
- document observed_at nonempty negative coverage
- multimodal_context evidence card observed_at temporal guard
- multimodal_context evidence card asset_scope string safety guard
- document asset_scope empty negative coverage
- document asset_scope uppercase negative coverage
- document invalidating_condition type negative coverage
- document invalidating_condition nonempty negative coverage
- document impact type negative coverage
- document impact nonempty negative coverage
- document category/source type negative coverage
- document category/source empty negative coverage
- document numeric type negative coverage
- document numeric range negative coverage
- document summary nonempty negative coverage
- document modality nonempty negative coverage
- multimodal_context artifact_ref ref_type canonical case guard
- multimodal_context artifact_ref metadata value type guard
- multimodal_context CHART metadata value type negative coverage
- multimodal_context artifact_ref metadata non-dict negative coverage
- CHART artifact_ref metadata DTO validation coverage
- CHART artifact_ref scalar DTO validation coverage
- multimodal_context evidence card string field type guard
- multimodal_context evidence card structural field type guard
- multimodal_context document artifact_ref structural negative coverage
- multimodal_context evidence card numeric bool negative coverage
- multimodal_context summary truncation flag type negative coverage
- multimodal_context asset_scope value type negative coverage
- multimodal_context evidence card invalidating_condition actionability guard
- multimodal_context identity values guard
- multimodal_context report intent variant coverage
- multimodal_context document-only report intent variant coverage
- JSONL audit log, audit tools, local audit web viewer
- audit_log.v1 and audit_summary.v1 read tool payload contracts
- shared tool registry
- replay provider interface
- JSONL signal repository contract
- runtime watchdog, JSONL retention controls, and append-only runtime checkpoints
- Phase 7 runtime tool manifest covers get_runtime_status and
  record_runtime_checkpoint
- deterministic Hermes-facing report harness with delivery contract guard
- Phase 7 Telegram report format contract with section-separated chunks
- delivery preview no-send guard for report and position review payloads
- delivery preview no-network guard coverage for report and position review payloads
- delivery preview Telegram format, max chunk size, and text preservation guard coverage
- delivery preview guard check name schema guard verifies check names exactly match the expected schema
- delivery contract no-send guard for report and position review guards
- delivery contract no-network guard coverage for report and position review guards
- report contract numeric authority guard for latest signal delivery
- report text numeric field guard for latest signal and position review payloads
- Hermes delivery preview payload_ref and numeric authority guard
- Telegram delivery preview required section presence guard
- Telegram delivery preview unrequested section absence guard
- Telegram delivery preview 1-based sequential chunk index guard
- Telegram delivery preview message count and single-message flag guard
- Telegram delivery preview chunk char-count metadata guard
- Telegram delivery preview nonempty chunk guard
- Telegram delivery preview section separator reconstruction guard
- Telegram delivery preview overflow policy section-boundary guard
- intent-specific report sections and Telegram required sections for pre-market,
  intraday risk, and post-market report variants
- report_contract_guard verifies Telegram required_sections match selected report intent
- cron prompt tool/input schema guard verifies prompt tool_name and input_json keys
- cron prompt idempotency key guard verifies prompt identity and asset key templates
- cron prompt idempotency text guard verifies prompt text references idempotency key templates
- cron prompt expected sections text guard verifies prompt text references expected Telegram sections
- cron prompt output schema guard verifies metadata and prompt text reference expected tool output schemas
- cron prompt live data boundary guard verifies metadata and prompt text preserve no-live-data execution
- cron prompt decision focus guard verifies metadata and prompt text reference decision_focus values
- cron prompt supported intents registry guard verifies supported_report_intents matches the report intent registry
- cron prompt pack identity guard verifies contract name and pack asset/timeframe identity
- cron prompt position option contract guard verifies include_position_review matches the requested pack option
- cron prompt pack top-level contract guard verifies schema_version and top-level live_data_required
- cron prompt pack key schema guard verifies top-level pack keys exactly match the expected schema
- cron prompt guard key schema guard verifies cron_prompt_guard keys exactly match the expected schema
- cron prompt guard check name schema guard verifies cron_prompt_guard check names exactly match the expected schema
- cron prompt guard check key schema guard verifies cron_prompt_guard check keys exactly match the expected schema
- cron prompt manual setup registry guard verifies manual setup requirements exactly match the registry
- cron prompt contract key schema guard verifies cron_prompt_contract keys exactly match the expected schema
- cron prompt prompt key schema guard verifies each prompt object key schema exactly matches the expected schema
- cron prompt schedule hint text guard verifies prompt text references schedule_hint values
- cron prompt manual setup text guard verifies prompt text references unattended-run prerequisites
- cron prompt scheduler setup prerequisite guard verifies prompt text declares manual setup before scheduler setup
- cron prompt no-secret text guard verifies prompt text forbids credentials or secret values
- cron prompt name text guard verifies prompt text references prompt names
- cron prompt delivery path metadata guard verifies prompt text matches declared delivery_preview_path values
- cron prompt Telegram format schema guard verifies metadata and prompt text reference telegram_report_format.v1
- cron prompt numeric authority metadata guard verifies metadata and prompt text reference numeric authority values
- cron prompt manual setup guard verifies unattended run prerequisites are declared
- cron prompt no-secret credential guard verifies no credential requirement or secret return
- cron prompt name set guard verifies only supported prompt names are emitted
- cron prompt schedule hint guard verifies prompt schedule hints match report and position contracts
- cron prompt tool/input text guard verifies prompt text matches declared tool and input metadata
- cron prompt configured gateway text guard verifies prompt text requires the configured Hermes/Telegram gateway
- cron prompt delivery preview text guard verifies prompt text references Telegram chunks
- cron prompt numeric authority text guard verifies prompt text preserves numeric authority instructions
- cron prompt order block text guard verifies every prompt text preserves no-order instructions
- degraded report data_warnings are guarded for Cautions reflection
- report_contract_guard verifies generated section order exactly matches the selected report intent required_sections
- report_contract_guard verifies formatted report text section markers appear in selected intent order
- report_contract_guard verifies report_intent_contract key schema exactly matches name/schedule_hint/decision_focus/required_sections
- report_contract_guard verifies report_intent_contract values exactly match the REPORT_INTENTS registry
- report_contract_guard verifies delivery contract cron_intents match REPORT_INTENTS registry order
- report_contract_guard verifies delivery channel format values match expected Hermes and Telegram formats
- report_contract_guard verifies Telegram delivery contract max_chars remains 3900
- report_contract_guard verifies Telegram delivery contract schema_version remains telegram_report_format.v1
- report_contract_guard verifies Telegram delivery contract chunking policy fields match expected values
- report_contract_guard verifies prompt_contract must_include exactly matches selected report intent terms
- report_contract_guard verifies prompt_contract key schema exactly matches numeric_authority/llm_role/must_include
- report_contract_guard verifies prompt_contract numeric_authority and llm_role identity values
- deterministic Hermes-facing position review report harness
- position_review_guard verifies Telegram required_sections match position review contract
- position_review_guard verifies position_review_contract required_sections match the canonical position review section schema
- position_review_guard verifies position_review_contract order_submission remains false
- position_review_guard verifies generated section order matches the position review contract
- position_review_guard verifies prompt_contract must_include matches the expected position review terms
- position_review_guard verifies prompt_contract key schema matches the expected schema
- position_review_guard verifies prompt_contract numeric_authority and llm_role identity values
- position_review_guard verifies Telegram delivery contract max_chars remains 3900
- position_review_guard verifies Telegram delivery contract schema_version remains telegram_report_format.v1
- position_review_guard verifies Telegram delivery contract chunking policy fields match expected values
- position_review_guard verifies delivery channel format values match expected Hermes and Telegram formats
- position_review_guard verifies delivery contract cron_intents match REPORT_INTENTS registry order
- position_review_guard uses Telegram delivery contract max_chars for text length checks
- offline Hermes cron prompt pack without scheduler side effects
- cron prompt guard verifies prompt names are unique and ordered as report intents plus optional position_review
- cron prompt guard verifies position_review expected_sections match the position review section contract
- offline Hermes/Telegram delivery preview chunks for report payloads
- position review payload guard verifies top-level summary fields match position_review identity values
- position review payload guard verifies nested delivery_preview and position review guards are ok
- latest signal report payload guard verifies report_intent matches report_intent_contract.name
- latest signal report payload guard verifies top-level summary fields match latest_signal_report identity values
- latest signal report payload guard verifies nested delivery_preview, evidence, and report contract guards are ok
- latest signal report payload guard verifies optional chart and multimodal context statuses are ok when present
- latest signal report payload guard verifies optional chart and multimodal nested guard statuses are ok when present
- multimodal_context.guard verifies check names, check key schemas, and guard top-level keys
- multimodal_context.guard verifies multimodal_context top-level key schema
- multimodal_context.guard verifies evidence card and artifact_ref evidence_id values are nonempty and unique
- multimodal_context.guard verifies document evidence ids do not use reserved context ids
- multimodal_context.guard verifies document evidence ids match a safe lowercase ASCII underscore contract
- multimodal_context.guard verifies artifact_ref evidence ids match a safe lowercase ASCII underscore contract
- multimodal_context.guard verifies artifact_ref values are nonempty and unique
- multimodal_context.guard verifies CHART artifact refs match the PNG suffix or sha256 content-address contract
- multimodal_context.guard verifies CHART artifact refs use offline local, artifact://, or sha256 locations
- multimodal_context.guard rejects CHART artifact refs that use file:// URI syntax
- multimodal_context.guard rejects CHART artifact refs that use ~/ user-home syntax
- multimodal_context.guard rejects CHART artifact refs that use /Users/ or drive-root machine-specific paths
- multimodal_context.guard rejects artifact refs that embed local path markers inside otherwise allowed URI prefixes
- multimodal_context.guard verifies artifact_ref values have no surrounding whitespace or ASCII control characters
- multimodal_context.guard verifies sha256 content-addressed artifact refs include a 64-character hex digest
- multimodal_context tests verify valid sha256 content-addressed CHART and PDF refs stay accepted
- multimodal_context.guard verifies artifact_refs envelope and artifact_ref key schemas
- multimodal_context.guard verifies artifact_ref ref_type values stay within the CHART/PDF contract
- multimodal_context.guard verifies artifact_ref metadata key schema per artifact_ref entry
- multimodal_context.guard verifies CHART and PDF artifact_ref metadata key schemas
- multimodal_context.guard verifies CHART and PDF artifact_ref metadata safety values
- multimodal_context.guard verifies PDF artifact_ref metadata description has no surrounding whitespace or ASCII control characters
- multimodal_context.guard verifies modality_counts match chart and evidence card context
- multimodal_context.guard verifies evidence card key schemas for document evidence context
- multimodal_context.guard verifies document evidence modality stays on the supported pdf_summary contract
- multimodal_context.guard verifies document evidence modality and observed_at have no surrounding whitespace or ASCII control characters
- multimodal_context.guard verifies document evidence artifact_ref uses an explicit portable URI prefix
- multimodal_context.guard verifies PDF artifact refs match the PDF suffix or sha256 content-address contract
- multimodal_context.guard verifies document evidence observed_at is a parseable UTC ISO timestamp
- multimodal_context.guard verifies document evidence observed_at is not after report created_at
- multimodal_context.guard verifies document evidence asset_scope includes report asset and underlying
- multimodal_context.guard verifies document evidence asset_scope values have no surrounding whitespace or ASCII control characters
- multimodal_context.guard verifies document evidence summaries stay within normalized max length
- multimodal_context.guard verifies summary_truncated flags match normalized summary length
- multimodal_context.guard verifies document evidence invalidating_condition is non-placeholder and actionable
- multimodal_context.guard verifies document evidence card category/source/bias categorical values
- multimodal_context.guard verifies document evidence buy/sell impacts remain context_only
- multimodal_context.guard verifies artifact_refs match chart and evidence card context
- multimodal_context.guard verifies evidence card value safety for document evidence context
- multimodal_context.guard verifies document evidence summary and invalidating_condition have no surrounding whitespace or ASCII control characters
- multimodal_context.guard verifies identity values for schema_version, numeric_authority, and no-call/no-embed flags
- non-default report intents preserve guarded multimodal context with chart and document evidence
- non-default report intents preserve document-only guarded multimodal context without chart_code_guard
- latest signal report evidence summary limits and conflict flags
- optional chart ref and chart/code guard for reports
- BTC-only Binance COIN-M guarded preview/execution path, portfolio snapshot normalizer, and local admin
- BTC COIN-M emergency kill switch risk setting
- offline integration readiness harness
- integration readiness next_actions contract coverage
- integration readiness payload schema contract coverage
- integration readiness configured credential schema coverage
- Binance credential status schema contract coverage
- live order submission readiness gate, blocked by default until explicit
  approval, live-trading env flag, credential/passphrase, permission
  attestation, and kill-switch evidence are present
- live data source readiness gate for market OHLCV, macro, and news source/API
  decisions without adding live adapters
- Telegram delivery readiness gate for bot-token/gateway decisions without
  sending messages or storing credentials
- Hermes MCP config readiness gate for config path and explicit registration
  confirmation without starting Hermes

Still blocked or not yet implemented:

- SQLite/Postgres migrations and repository persistence
- live market/news/macro adapters
- Hermes/Telegram/crons
- live Hermes multimodal call and Telegram delivery
- Binance testnet read-only smoke with real testnet credentials
- live order submission

Required decisions before blocked scope:

- `MIGRATION_GO` and `REPOSITORY_GO` for migrations and DB-backed persistence.
- Live data source/API-key policy for market OHLCV, macro, and news adapters.
- Hermes config path and Telegram credential/gateway choice.
- Binance encrypted testnet credentials and manual passphrase procedure.
- Explicit future approval before any live order submission.

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

Status: JSONL signal ledger contract implemented and verified.

Scope decision recorded on 2026-05-10:

- Continue JSONL for the existing runtime signal ledger until a separate
  migration gate records DB direction.
- Keep fixture/text signal IDs and caller-supplied UTC ISO-8601 timestamps.
- Do not add SQLite, migrations, schema runners, or repository-backed DB
  persistence in this stage.

Tasks:

1. Define signal ledger repository interface. Done.
2. Keep JSONL adapter as the only implementation. Done.
3. Move record/label/evaluate tools behind the repository boundary. Done.
4. Add tmp_path repository contract tests. Done.

Implementation record:

- Added `src/halo_swing_mcp/signal_repository.py`.
- Added `SignalLedgerRepository` protocol and `JsonlSignalLedgerRepository`.
- Refactored `record_signal`, `label_signal_outcome`, and
  `evaluate_score_performance` to use the repository boundary.
- Added `tests/test_signal_repository.py`.

Verification:

```text
PYTHONPATH=src ./.venv/bin/python -m pytest -> 53 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check -> passed
CLI smoke for record_signal, label_signal_outcome, evaluate_score_performance with /private/tmp JSONL ledger -> passed
```

Decision still needed before DB implementation:

- SQLite migration naming/idempotency rules.
- PostgreSQL portability constraints for future schema work.
- Retention limits for local JSONL ledgers and audit logs.

Follow-up gate packet:

- `docs/gates/P1_MIGRATION_GATE_READINESS_2026-05-10.md` records recommended
  migration defaults and verification requirements.
- This packet is readiness only; `MIGRATION_GO` is still not recorded.

### Stage D. Runtime Watchdog, Retention, And Checkpoint

Status: local JSONL runtime guard and manual checkpoint tool implemented and verified.

Scope decision recorded on 2026-05-10:

- Use local JSONL retention defaults before introducing DB persistence.
- Default retention: 1000 records and 5,000,000 bytes per JSONL artifact.
- Default watchdog degraded-mode trigger: 3 failed tool audit events inside
  the most recent 20 audit events.
- Do not add background daemons, schedulers, live adapters, DB tables, or
  committed runtime state in this stage.
- Runtime checkpoints are manual append-only JSONL snapshots, not a scheduler
  or Hermes/Telegram delivery loop.

Tasks:

1. Add retention limits for audit and signal ledgers. Done.
2. Add watchdog event contract. Done.
3. Add degraded-mode controls for repeated failures. Done.
4. Expose runtime status through MCP/CLI harness. Done.
5. Expose append-only runtime checkpoint through MCP/CLI harness. Done.

Implementation record:

- Added `src/halo_swing_mcp/runtime_guard.py`.
- Added `src/halo_swing_mcp/tools/runtime.py`.
- Added `get_runtime_status` tool.
- Added `record_runtime_checkpoint` tool.
- Added `runtime_checkpoint_path` setting.
- Added runtime retention and failure threshold settings.
- Added `tests/test_runtime_guard.py`.

Verification:

```text
PYTHONPATH=src ./.venv/bin/python -m pytest -> 57 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_runtime_status --input-json '{"audit_log_path":"/private/tmp/halo_swing_runtime_guard_audit.jsonl","ledger_path":"/private/tmp/halo_swing_runtime_guard_ledger.jsonl","apply_retention":true,"max_records":2,"max_bytes":10000,"failure_window":4,"failure_threshold":3}' --audit-log-path /private/tmp/halo_swing_runtime_guard_audit.jsonl -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness record_runtime_checkpoint --input-json '{"checkpoint_path":"/private/tmp/halo_swing_runtime_checkpoints.jsonl","audit_log_path":"/private/tmp/halo_swing_checkpoint_audit.jsonl","ledger_path":"/private/tmp/halo_swing_checkpoint_ledger.jsonl","run_id":"manual_smoke"}' --no-audit -> passed
```

Decision needed:

- Retention age policy, if record count/size limits are not enough.
- Whether watchdog events should later persist to DB, JSONL, or both.
- Alert destination for critical watchdog events before unattended cron.

### Stage E. Hermes And Telegram Integration

Status: report harness, position review report, and offline cron prompt pack implemented; live Hermes/Telegram setup still requires user environment decision.

Tasks:

1. Write Hermes MCP config. Documented for stdio local server.
2. Add report prompt templates. Report prompt contract implemented.
3. Add cron prompt examples. Offline prompt pack implemented; no scheduler added.
4. Add Telegram report format. Deterministic report text snapshot implemented.

Implementation record:

- Added `src/halo_swing_mcp/tools/reporting.py`.
- Added `generate_latest_signal_report` tool.
- Added `generate_position_review_report` tool.
- Added `generate_cron_prompt_pack` tool.
- Added `tests/golden/hermes_latest_signal_report.json`.
- Added `tests/test_reporting.py`.
- Registered the report tool in the shared registry, MCP server wrappers,
  health golden, README, and DevOps guide.
- Wrapped `evaluate_position` into a Hermes/Telegram-facing position review
  payload with `position_review` numeric authority, required section guard,
  Telegram length check, and no network/order side effects.
- Added offline `delivery_preview` payloads for latest signal and position
  review reports, including Hermes payload refs, Telegram message chunks,
  chunk guard checks, and no network side effects.
- Added `evidence_contract`, `evidence_context`, and `evidence_guard` to latest
  signal reports so Hermes-facing summaries stay bounded and conflicting
  signals are explicitly acknowledged.

Verification:

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py tests/test_health_check.py tests/test_tool_registry.py tests/test_mvp_tools.py -> 21 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 61 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_latest_signal_report --input-json '{"asset":"TQQQ"}' --audit-log-path /private/tmp/halo_swing_report_harness_audit.jsonl -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py tests/test_health_check.py tests/test_tool_registry.py tests/test_mvp_tools.py -> 30 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py src/halo_swing_mcp/server.py src/halo_swing_mcp/tool_registry.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 73 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_position_review_report --input-json '{"asset":"TQQQ","entry_price":100,"current_price":114,"size":3}' --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py tests/test_health_check.py tests/test_tool_registry.py tests/test_mvp_tools.py -> 31 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py src/halo_swing_mcp/server.py src/halo_swing_mcp/tool_registry.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 74 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_latest_signal_report --input-json '{"asset":"TQQQ"}' --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py tests/test_health_check.py tests/test_tool_registry.py tests/test_mvp_tools.py -> 32 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py src/halo_swing_mcp/server.py src/halo_swing_mcp/tool_registry.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 75 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness evaluate_score_performance --input-json '{"days":90}' --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness compare_champion_challenger --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_news_bundle --input-json '{"topic":"all"}' --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_cron_prompt_pack --input-json '{"asset":"TQQQ"}' --no-audit -> passed, cron_prompt_guard.status ok
```

Decision needed:

- Is Hermes installed/configurable on this machine?
- Should Telegram be configured now, and are credentials available?

### Stage F. Multimodal Report Integration

Status: optional chart ref and chart/code guard implemented; live Hermes multimodal use still deferred.

Tasks:

1. Link chart refs into report payloads. Done when `include_chart=true`.
2. Add chart/code conflict guard. Done.
3. Add report snapshot tests. Done.
4. Normalize caller-supplied PDF/document summaries into evidence cards. Done.
5. Attach chart/document evidence into offline report multimodal context. Done.

Implementation record:

- Extended `generate_latest_signal_report` with `include_chart`,
  `chart_timeframe`, and `chart_output_dir`.
- Chart rendering uses the existing deterministic `render_chart` tool.
- `latest_signal_report.chart_ref` is populated from the chart artifact ref.
- `chart_code_guard` records that chart images are visual context only and
  numeric indicator authority remains code-calculated.
- `create_document_evidence_card` records caller-supplied PDF/document summaries
  as guarded evidence cards.
- `document_summary_input_contract` records no parser, file read, network call,
  raw document return, or secret return.
- `generate_latest_signal_report(extra_evidence_cards=...)` returns
  `multimodal_context` when chart refs or extra evidence cards are present.
- `multimodal_context` records latest_signal_report numeric authority, linked
  artifact refs, modality counts, no Hermes multimodal call, and no network call.
- Added chart ref and guard coverage to `tests/test_reporting.py`.

Verification:

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -> 6 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py src/halo_swing_mcp/server.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 63 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_latest_signal_report --input-json '{"asset":"TQQQ","include_chart":true,"chart_output_dir":"/private/tmp/halo_swing_chart_ref_guard"}' --audit-log-path /private/tmp/halo_swing_chart_ref_guard_audit.jsonl -> passed
```

Decision needed:

- Whether regular reports should include charts by default or only on demand.
- Which chart artifacts should be included in live Hermes multimodal reports.

### Stage G. Broker / Order Preview

Status: BTC-only Binance COIN-M Futures scope approved; guarded implementation and local admin verified.

Tasks:

1. Read-only portfolio sync. Live smoke blocked by credentials; offline snapshot normalizer implemented.
2. Order preview only. BTCUSD_PERP Binance COIN-M preview implemented.
3. Approval-required execution only. BTCUSD_PERP execution path implemented with default block guards.

Scope decision recorded on 2026-05-09:

- Automatic trading scope is BTC only.
- Exchange/API is Binance COIN-M Futures API.
- Initial symbol is `BTCUSD_PERP`.
- Non-BTC symbols are rejected by code.
- Binance trading API credentials are entered through a local admin page and saved encrypted in local state.
- Per-order notional, daily order count, and daily loss limits are configurable.

Implementation record:

- Added `src/halo_swing_mcp/binance_btc.py`.
- Added `src/halo_swing_mcp/secret_store.py`.
- Added `src/halo_swing_mcp/risk_settings.py`.
- Added `src/halo_swing_mcp/trading_admin_web.py`.
- Added `preview_btc_order` tool.
- Added `execute_btc_order` tool.
- Added BTC-only COIN-M validation, confirmation guard, live-trading env flag guard, encrypted credential guard, risk limit guard, testnet default, and Binance HMAC SHA256 signing helper.
- Added local-only trading admin page for encrypted credentials and BTC risk settings.
- Added read-only Binance COIN-M connectivity and account snapshot tools.
- Added offline COIN-M account snapshot normalizer for caller-supplied read-only payloads.
- Added position-aware order preview effect classification from portfolio snapshots.
- Added management page controls for public connectivity check, read-only account snapshot, and order preview.
- Added testnet-only execution policy guard with `HALO_SWING_BINANCE_FORCE_TESTNET_EXECUTION=true`.
- Added emergency kill switch risk setting that blocks execution even when the
  confirmation string is supplied.
- Added `binance_credential_policy.v1` to credential status and order previews,
  requiring COIN-M trade-only keys, forbidding withdraw permissions, and keeping
  passphrases manual-only.
- Added `live_order_submission` readiness gate so the remaining live-order
  blocker is visible without submitting orders or calling Binance.
- Added Phase 9 BTC tool manifest coverage for guarded risk, credential,
  account, preview, and execute tools.
- No live order is submitted unless `confirm` is `CONFIRM_BTC_BINANCE_COINM_ORDER`, `HALO_SWING_BINANCE_ENABLE_LIVE_TRADING=true`, encrypted credentials are configured, and `credential_passphrase` is provided.

Verification:

```text
PYTHONPATH=src ./.venv/bin/python -m pytest -> 50 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness preview_btc_order --input-json '{"side":"BUY","quantity":"1"}' --audit-log-path /private/tmp/halo_swing_coinm_verify.jsonl -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness save_binance_credentials --input-json '{"api_key":"abcde12345key","api_secret":"super-secret","passphrase":"local-passphrase","credentials_path":"/private/tmp/halo_swing_binance_credentials.enc.json"}' --audit-log-path /private/tmp/halo_swing_coinm_verify.jsonl -> passed
GET http://127.0.0.1:8766/api/status -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_binance_btc.py tests/test_tool_registry.py -> 20 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness execute_btc_order --input-json '{"confirm":"CONFIRM_BTC_BINANCE_COINM_ORDER","settings_path":"/private/tmp/halo_swing_kill_switch_settings.json"}' --no-audit -> passed, blocked_reason emergency_kill_switch_enabled
PYTHONPATH=src ./.venv/bin/python -m pytest -> 77 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_binance_credentials_status --no-audit -> passed, binance_credential_policy.v1 present
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness preview_btc_order --input-json '{"side":"BUY","quantity":"1"}' --no-audit -> passed, execution_guard credential_policy present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 92 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_readiness.py -> 5 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/readiness.py src/halo_swing_mcp/server.py tests/test_readiness.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --no-audit -> passed, live_order_submission blocked
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_readiness.py -> 6 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --no-audit -> passed, live_data_source_readiness.v1 present
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_readiness.py -> 7 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --no-audit -> passed, telegram_delivery_readiness.v1 present
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_readiness.py -> 8 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --no-audit -> passed, hermes_mcp_config_readiness.v1 present
```

Follow-up implementation record:

```text
implemented_not_live_smoked:
  - check_binance_coinm_connectivity
  - get_binance_coinm_account_snapshot
  - management page order preview form
  - management page read-only account form
  - testnet-only execution policy guard
```

Decision needed:

- Operational passphrase handling for unattended runs.

### Stage H. Offline Integration Readiness

Status: implemented and verified.

Purpose:

- Report which blocked gates are ready or still missing user/environment input.
- Avoid network calls, secret disclosure, schedulers, live adapters, migrations,
  and runtime artifact creation.

Implementation record:

- Added `src/halo_swing_mcp/tools/readiness.py`.
- Added `get_integration_readiness` tool.
- Registered the tool in the shared registry, MCP server wrappers, health
  golden, README, and DevOps guide.
- Added `tests/test_readiness.py`.
- Strengthened `tests/test_tool_registry.py` so `server.py` `@mcp.tool()`
  wrappers must exactly match `tool_registry.tool_names()`.
- Strengthened `tests/test_tool_registry.py` so every `@mcp.tool()` wrapper
  dispatches only to the matching shared registry tool name.
- Strengthened `tests/test_tool_registry.py` so every `@mcp.tool()` wrapper
  payload key matches a wrapper parameter and same-named parameter binding.
- Strengthened `tests/test_tool_registry.py` so every `@mcp.tool()` wrapper
  parameter set matches its registered implementation function signature.
- Strengthened `tests/test_tool_registry.py` so `TOOL_SPECS` names are unique,
  ordered, callable, and metadata-complete.
- Strengthened `tests/test_tool_registry.py` so MVP `required_tools` directly
  equals `tool_names()` in registry order.
- Aligned latest-signal report `prompt_contract.must_include` terms with
  intent-specific required sections for pre-market, intraday risk, and
  post-market reports.
- Strengthened `generate_cron_prompt_pack` guard so report prompt input JSON and
  expected sections match report intent contracts, including the
  `include_position_review=false` path.

Readiness gates covered:

- Hermes local config.
- Telegram token/gateway configured flag.
- `MIGRATION_GO` and `REPOSITORY_GO`.
- Binance testnet read-only smoke prerequisites, including encrypted
  credentials and non-secret manual passphrase confirmation.
- Live data source/API-key decisions.

Verification:

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_readiness.py tests/test_health_check.py tests/test_tool_registry.py tests/test_mvp_tools.py -> 22 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/readiness.py tests/test_readiness.py src/halo_swing_mcp/server.py src/halo_swing_mcp/tool_registry.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 71 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_event_calendar --input-json '{"days":14}' --no-audit -> passed, event_window_summary and danger_window present
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_macro_snapshot --no-audit -> passed, macro_filter_summary present
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness score_leverage_swing --input-json '{"asset":"TQQQ"}' --no-audit -> passed, news_usage_contract present
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness record_signal --input-json '{"ledger_path":"/private/tmp/halo_swing_run_journal_ledger.jsonl"}' --no-audit -> passed, run_journal.v1 present
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness calculate_indicators --input-json '{"symbol":"QQQ","timeframe":"1d"}' --no-audit -> passed, swing_level_contract present
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness score_leverage_swing --input-json '{"asset":"TQQQ"}' --no-audit -> passed, strategy_config_contract present
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness render_chart --input-json '{"symbol":"QQQ","timeframe":"1d","output_dir":"/private/tmp/halo_swing_chart_artifact_contract"}' --no-audit -> passed, chart_artifact.v1 present
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_latest_signal_report --input-json '{"asset":"TQQQ"}' --no-audit -> passed, telegram_report_format.v1 present
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness suggest_weight_update --no-audit -> passed, challenger_config.v1 present
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_trade_guide --input-json '{"asset":"TQQQ"}' --no-audit -> passed, trade_guide.v1 and time_exit_conditions present
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_market_snapshot --input-json '{"symbols":["QQQ","SPY","SMH","SOXX","BTC"]}' --no-audit -> passed, market_snapshot.v1 and SOXX core coverage present
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness label_signal_outcome --input-json '{"price_path":[570.611014,576.260628,706.20175],"time_barrier_days":2,"stop_loss_pct":0.05,"take_profit_pct":0.10}' --no-audit -> passed, signal_label_outcome.v1 metric window present
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness evaluate_position --input-json '{"asset":"TQQQ","entry_price":100,"current_price":114,"size":3}' --no-audit -> passed, position_management.v1 present
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_event_calendar --input-json '{"days":14}' --no-audit -> passed, event_policy.v1 covers CPI/EARNINGS/FOMC/NFP
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_news_bundle --input-json '{"topic":"all"}' --no-audit -> passed, news_source_policy.v1 covers required source groups
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness evaluate_score_performance --input-json '{"days":90}' --no-audit -> passed, deflated_sharpe_proxy.v1 present
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness evaluate_score_performance --input-json '{"days":180}' --no-audit -> passed, sample_size 34 and fixture_oos_window.v1 present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 97 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 14 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_latest_signal_report --input-json '{"asset":"TQQQ","report_intent":"intraday_risk_watch"}' --no-audit -> passed, intent-specific sections and telegram required_sections aligned
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_latest_signal_report --input-json '{"asset":"TQQQ","report_intent":"post_market_review"}' --no-audit -> passed, intent-specific sections and telegram required_sections aligned
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py -q -> 22 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness suggest_weight_update --no-audit -> passed, challenger_config.v1 present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 98 passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py tests/test_runtime_guard.py -q -> 28 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_runtime_status --input-json '{"audit_log_path":"/private/tmp/halo_swing_runtime_manifest_audit.jsonl","ledger_path":"/private/tmp/halo_swing_runtime_manifest_ledger.jsonl"}' --no-audit -> passed, watchdog.v1 and retention resources present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 99 passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py tests/test_binance_btc.py -q -> 43 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness preview_btc_order --input-json '{"side":"BUY","quantity":"1"}' --no-audit -> passed, preview only with btc_order_execution_guard.v1
PYTHONPATH=src ./.venv/bin/python -m pytest -> 100 passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py tests/test_health_check.py -q -> 27 passed
manifest/health parity check -> passed, manifest_equals_health true and count 35
PYTHONPATH=src ./.venv/bin/python -m pytest -> 100 passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_audit.py -q -> 5 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_audit_summary --input-json '{"audit_log_path":"/private/tmp/halo_swing_audit_contract.jsonl"}' --no-audit -> passed, audit_summary.v1 present
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_audit_log --input-json '{"audit_log_path":"/private/tmp/halo_swing_audit_contract.jsonl","limit":5}' --no-audit -> passed, audit_log.v1 present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 100 passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_tool_registry.py -q -> 5 passed, MCP wrapper registry parity enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_tool_registry.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 100 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_tool_registry.py -q -> 6 passed, MCP wrapper dispatch parity enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_tool_registry.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 101 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_tool_registry.py -q -> 7 passed, MCP wrapper payload parity enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_tool_registry.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 102 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_tool_registry.py -q -> 8 passed, MCP wrapper signature parity enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_tool_registry.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 103 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_tool_registry.py -q -> 9 passed, ToolSpec registry invariants enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_tool_registry.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 104 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_tool_registry.py -q -> 9 passed, MVP required_tools equals registry tool_names order
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_tool_registry.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 104 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 14 passed, intent prompt contracts aligned with required sections
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_health_check.py tests/test_tool_registry.py -q -> 12 passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 104 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_latest_signal_report --input-json '{"asset":"TQQQ","report_intent":"intraday_risk_watch"}' --no-audit -> passed, prompt terms aligned
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_latest_signal_report --input-json '{"asset":"TQQQ","report_intent":"post_market_review"}' --no-audit -> passed, prompt terms aligned
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
blocked artifact audit -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 15 passed, cron prompt intent alignment enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_cron_prompt_pack --input-json '{"asset":"TQQQ","include_position_review":false}' --no-audit -> passed, no position_review prompt and no side effects
PYTHONPATH=src ./.venv/bin/python -m pytest -> 105 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
blocked artifact audit -> passed
git status --short --ignored state -> ignored local state/ only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py -q -> 25 passed, unsupported long fixture window guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/scoring.py tests/test_mvp_tools.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness evaluate_score_performance --input-json '{"days":365}' --no-audit -> passed, coverage_status unsupported_requested_window
PYTHONPATH=src ./.venv/bin/python -m pytest -> 106 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
blocked artifact audit -> passed
git status --short --ignored state -> ignored local state/ only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 16 passed, degraded data_warnings Cautions guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_latest_signal_report --input-json '{"asset":"TQQQ"}' --no-audit -> passed, normal report snapshot unchanged
PYTHONPATH=src ./.venv/bin/python -m pytest -> 107 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
blocked artifact audit -> passed
git status --short --ignored state -> ignored local state/ only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 16 passed, Telegram required_sections intent guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_latest_signal_report --input-json '{"asset":"TQQQ","report_intent":"intraday_risk_watch"}' --no-audit -> passed, telegram_required_sections_match_intent present
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_latest_signal_report --input-json '{"asset":"TQQQ","report_intent":"post_market_review"}' --no-audit -> passed, telegram_required_sections_match_intent present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 107 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
blocked artifact audit -> passed
git status --short --ignored state -> ignored local state/ only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 16 passed, position review Telegram required_sections guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_position_review_report --input-json '{"asset":"TQQQ","entry_price":100,"current_price":114,"size":3}' --no-audit -> passed, telegram_required_sections_match_position_review present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 107 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
blocked artifact audit -> passed
git status --short --ignored state -> ignored local state/ only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 16 passed, delivery_preview no-send guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_latest_signal_report --input-json '{"asset":"TQQQ"}' --no-audit -> passed, delivery_preview_has_no_send_side_effect present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 107 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
blocked artifact audit -> passed
git status --short --ignored state -> ignored local state/ only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 16 passed, Hermes delivery preview payload guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_latest_signal_report --input-json '{"asset":"TQQQ"}' --no-audit -> passed, hermes_payload_ref_matches_structured_payload present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 107 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
blocked artifact audit -> passed
git status --short --ignored state -> ignored local state/ only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 16 passed, Telegram preview required section guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_latest_signal_report --input-json '{"asset":"TQQQ"}' --no-audit -> passed, telegram_required_sections_present_in_preview present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 107 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
blocked artifact audit -> passed
git status --short --ignored state -> ignored local state/ only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 16 passed, Telegram preview unrequested section guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_latest_signal_report --input-json '{"asset":"TQQQ"}' --no-audit -> passed, telegram_unrequested_sections_absent_from_preview present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 107 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
blocked artifact audit -> passed
git status --short --ignored state -> ignored local state/ only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 16 passed, Telegram preview chunk index guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_latest_signal_report --input-json '{"asset":"TQQQ"}' --no-audit -> passed, telegram_chunks_are_1_based_sequential present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 107 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
blocked artifact audit -> passed
git status --short --ignored state -> ignored local state/ only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 16 passed, Telegram preview message count guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_latest_signal_report --input-json '{"asset":"TQQQ"}' --no-audit -> passed, telegram_message_count_matches_chunks present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 107 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
blocked artifact audit -> passed
git status --short --ignored state -> ignored local state/ only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 16 passed, Telegram preview section separator guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_latest_signal_report --input-json '{"asset":"TQQQ"}' --no-audit -> passed, telegram_section_separator_preserves_preview_text present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 107 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
blocked artifact audit -> passed
git status --short --ignored state -> ignored local state/ only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 16 passed, Telegram preview overflow policy guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_latest_signal_report --input-json '{"asset":"TQQQ"}' --no-audit -> passed, telegram_overflow_policy_splits_on_section_boundary present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 107 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
blocked artifact audit -> passed
git status --short --ignored state -> ignored local state/ only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 16 passed, Telegram preview chunk char-count guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_latest_signal_report --input-json '{"asset":"TQQQ"}' --no-audit -> passed, telegram_chunk_char_counts_match_text present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 107 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
blocked artifact audit -> passed
git status --short --ignored state -> ignored local state/ only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 16 passed, Telegram preview nonempty chunk guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_latest_signal_report --input-json '{"asset":"TQQQ"}' --no-audit -> passed, telegram_chunks_are_nonempty present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 107 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
blocked artifact audit -> passed
git status --short --ignored state -> ignored local state/ only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 16 passed, position review max_chars contract guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_position_review_report --input-json '{"asset":"TQQQ","entry_price":100,"current_price":114,"size":3}' --no-audit -> passed, telegram_text_fits_single_message expected_max_chars matches delivery contract
PYTHONPATH=src ./.venv/bin/python -m pytest -> 107 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
blocked artifact audit -> passed
git status --short --ignored state -> ignored local state/ only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 16 passed, delivery contract no-send guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_latest_signal_report --input-json '{"asset":"TQQQ"}' --no-audit -> passed, delivery_contract_has_no_send_side_effect present
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_position_review_report --input-json '{"asset":"TQQQ","entry_price":100,"current_price":114,"size":3}' --no-audit -> passed, delivery_contract_has_no_send_side_effect present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 107 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
blocked artifact audit -> passed
git status --short --ignored state -> ignored local state/ only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 16 passed, report contract numeric authority guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_latest_signal_report --input-json '{"asset":"TQQQ"}' --no-audit -> passed, delivery_numeric_authority_is_latest_signal_report present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 107 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
blocked artifact audit -> passed
git status --short --ignored state -> ignored local state/ only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 16 passed, report text numeric field guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_latest_signal_report --input-json '{"asset":"TQQQ"}' --no-audit -> passed, report_text_reflects_latest_signal_numeric_fields present
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_position_review_report --input-json '{"asset":"TQQQ","entry_price":100,"current_price":114,"size":3}' --no-audit -> passed, position_review_text_reflects_review_numeric_fields present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 107 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
blocked artifact audit -> passed
git status --short --ignored state -> ignored local state/ only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 16 passed, cron prompt tool/input schema guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_cron_prompt_pack --input-json '{"asset":"TQQQ"}' --no-audit -> passed, report_prompt_tool_and_input_schema_match present
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_cron_prompt_pack --input-json '{"asset":"TQQQ","include_position_review":false}' --no-audit -> passed, position_review schema guard actual empty
PYTHONPATH=src ./.venv/bin/python -m pytest -> 107 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
blocked artifact audit -> passed
git status --short --ignored state -> ignored local state/ only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 16 passed, cron prompt idempotency key guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_cron_prompt_pack --input-json '{"asset":"TQQQ"}' --no-audit -> passed, idempotency_key_templates_match_prompt_identity present
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_cron_prompt_pack --input-json '{"asset":"TQQQ","include_position_review":false}' --no-audit -> passed, idempotency_key_templates_match_prompt_identity present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 107 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
blocked artifact audit -> passed
git status --short --ignored state -> ignored local state/ only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 16 passed, cron prompt manual setup guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_cron_prompt_pack --input-json '{"asset":"TQQQ"}' --no-audit -> passed, manual_setup_requirements_declared_before_unattended_run present
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_cron_prompt_pack --input-json '{"asset":"TQQQ","include_position_review":false}' --no-audit -> passed, manual_setup_requirements_declared_before_unattended_run present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 107 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
blocked artifact audit -> passed
git status --short --ignored state -> ignored local state/ only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 16 passed, cron prompt no-secret credential guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_cron_prompt_pack --input-json '{"asset":"TQQQ"}' --no-audit -> passed, cron_prompt_contract_requires_no_credentials_or_secrets present
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_cron_prompt_pack --input-json '{"asset":"TQQQ","include_position_review":false}' --no-audit -> passed, cron_prompt_contract_requires_no_credentials_or_secrets present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 107 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
blocked artifact audit -> passed
git status --short --ignored state -> ignored local state/ only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 16 passed, cron prompt name set guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_cron_prompt_pack --input-json '{"asset":"TQQQ"}' --no-audit -> passed, prompt_names_match_contract_and_position_option present
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_cron_prompt_pack --input-json '{"asset":"TQQQ","include_position_review":false}' --no-audit -> passed, prompt_names_match_contract_and_position_option present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 107 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
blocked artifact audit -> passed
git status --short --ignored state -> ignored local state/ only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 16 passed, cron prompt schedule hint guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_cron_prompt_pack --input-json '{"asset":"TQQQ"}' --no-audit -> passed, prompt_schedule_hints_match_contract present
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_cron_prompt_pack --input-json '{"asset":"TQQQ","include_position_review":false}' --no-audit -> passed, prompt_schedule_hints_match_contract present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 107 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
blocked artifact audit -> passed
git status --short --ignored state -> ignored local state/ only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 16 passed, cron prompt delivery preview text guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_cron_prompt_pack --input-json '{"asset":"TQQQ"}' --no-audit -> passed, prompt_text_references_delivery_preview_chunks present
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_cron_prompt_pack --input-json '{"asset":"TQQQ","include_position_review":false}' --no-audit -> passed, prompt_text_references_delivery_preview_chunks present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 107 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
blocked artifact audit -> passed
git status --short --ignored state -> ignored local state/ only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 16 passed, cron prompt numeric authority text guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_cron_prompt_pack --input-json '{"asset":"TQQQ"}' --no-audit -> passed, prompt_text_preserves_numeric_authority present
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_cron_prompt_pack --input-json '{"asset":"TQQQ","include_position_review":false}' --no-audit -> passed, prompt_text_preserves_numeric_authority present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 107 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
blocked artifact audit -> passed
git status --short --ignored state -> ignored local state/ only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 16 passed, cron prompt order block text guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_cron_prompt_pack --input-json '{"asset":"TQQQ"}' --no-audit -> passed, prompt_text_preserves_order_block per prompt
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_cron_prompt_pack --input-json '{"asset":"TQQQ","include_position_review":false}' --no-audit -> passed, prompt_text_preserves_order_block per prompt
PYTHONPATH=src ./.venv/bin/python -m pytest -> 107 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
blocked artifact audit -> passed
git status --short --ignored state -> ignored local state/ only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 16 passed, cron prompt tool/input text guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_cron_prompt_pack --input-json '{"asset":"TQQQ"}' --no-audit -> passed, prompt_text_matches_declared_tool_and_inputs present
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_cron_prompt_pack --input-json '{"asset":"TQQQ","include_position_review":false}' --no-audit -> passed, prompt_text_matches_declared_tool_and_inputs present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 107 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
blocked artifact audit -> passed
git status --short --ignored state -> ignored local state/ only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 16 passed, cron prompt configured gateway text guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_cron_prompt_pack --input-json '{"asset":"TQQQ"}' --no-audit -> passed, prompt_text_requires_configured_gateway present
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_cron_prompt_pack --input-json '{"asset":"TQQQ","include_position_review":false}' --no-audit -> passed, prompt_text_requires_configured_gateway present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 107 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
blocked artifact audit -> passed
git status --short --ignored state -> ignored local state/ only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 16 passed, cron prompt idempotency text guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_cron_prompt_pack --input-json '{"asset":"TQQQ"}' --no-audit -> passed, prompt_text_references_idempotency_key_template present
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_cron_prompt_pack --input-json '{"asset":"TQQQ","include_position_review":false}' --no-audit -> passed, prompt_text_references_idempotency_key_template present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 107 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
blocked artifact audit -> passed
git status --short --ignored state -> ignored local state/ only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 16 passed, cron prompt expected sections text guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_cron_prompt_pack --input-json '{"asset":"TQQQ"}' --no-audit -> passed, prompt_text_references_expected_sections present
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_cron_prompt_pack --input-json '{"asset":"TQQQ","include_position_review":false}' --no-audit -> passed, prompt_text_references_expected_sections present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 107 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
blocked artifact audit -> passed
git status --short --ignored state -> ignored local state/ only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 16 passed, cron prompt schedule hint text guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_cron_prompt_pack --input-json '{"asset":"TQQQ"}' --no-audit -> passed, prompt_text_references_schedule_hint present
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_cron_prompt_pack --input-json '{"asset":"TQQQ","include_position_review":false}' --no-audit -> passed, prompt_text_references_schedule_hint present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 107 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
blocked artifact audit -> passed
git status --short --ignored state -> ignored local state/ only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 16 passed, cron prompt manual setup text guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_cron_prompt_pack --input-json '{"asset":"TQQQ"}' --no-audit -> passed, prompt_text_references_manual_setup_requirements present
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_cron_prompt_pack --input-json '{"asset":"TQQQ","include_position_review":false}' --no-audit -> passed, prompt_text_references_manual_setup_requirements present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 107 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
blocked artifact audit -> passed
git status --short --ignored state -> ignored local state/ only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 16 passed, cron prompt no-secret text guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_cron_prompt_pack --input-json '{"asset":"TQQQ"}' --no-audit -> passed, prompt_text_references_no_secret_instruction present
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_cron_prompt_pack --input-json '{"asset":"TQQQ","include_position_review":false}' --no-audit -> passed, prompt_text_references_no_secret_instruction present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 107 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
blocked artifact audit -> passed
git status --short --ignored state -> ignored local state/ only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 16 passed, cron prompt name text guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_cron_prompt_pack --input-json '{"asset":"TQQQ"}' --no-audit -> passed, prompt_text_references_prompt_name present
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_cron_prompt_pack --input-json '{"asset":"TQQQ","include_position_review":false}' --no-audit -> passed, prompt_text_references_prompt_name present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 107 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
blocked artifact audit -> passed
git status --short --ignored state -> ignored local state/ only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 16 passed, cron prompt delivery path metadata guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_cron_prompt_pack --input-json '{"asset":"TQQQ"}' --no-audit -> passed, prompt_text_matches_declared_delivery_preview_path present
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_cron_prompt_pack --input-json '{"asset":"TQQQ","include_position_review":false}' --no-audit -> passed, prompt_text_matches_declared_delivery_preview_path present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 107 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
blocked artifact audit -> passed
git status --short --ignored state -> ignored local state/ only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 16 passed, cron prompt Telegram format schema guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_cron_prompt_pack --input-json '{"asset":"TQQQ"}' --no-audit -> passed, prompt_telegram_format_schema_matches_contract and prompt_text_references_telegram_format_schema present
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_cron_prompt_pack --input-json '{"asset":"TQQQ","include_position_review":false}' --no-audit -> passed, prompt_telegram_format_schema_matches_contract and prompt_text_references_telegram_format_schema present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 107 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
blocked artifact audit -> passed
git status --short --ignored state -> ignored local state/ only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 16 passed, cron prompt numeric authority metadata guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_cron_prompt_pack --input-json '{"asset":"TQQQ"}' --no-audit -> passed, prompt_numeric_authority_matches_contract and prompt_text_references_numeric_authority present
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_cron_prompt_pack --input-json '{"asset":"TQQQ","include_position_review":false}' --no-audit -> passed, prompt_numeric_authority_matches_contract and prompt_text_references_numeric_authority present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 107 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
blocked artifact audit -> passed
git status --short --ignored state -> ignored local state/ only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 16 passed, cron prompt output schema guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_cron_prompt_pack --input-json '{"asset":"TQQQ"}' --no-audit -> passed, prompt_output_schema_matches_tool_contract and prompt_text_references_output_schema present
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_cron_prompt_pack --input-json '{"asset":"TQQQ","include_position_review":false}' --no-audit -> passed, prompt_output_schema_matches_tool_contract and prompt_text_references_output_schema present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 107 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state/ only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 16 passed, cron prompt live data boundary guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_cron_prompt_pack --input-json '{"asset":"TQQQ"}' --no-audit -> passed, prompt_live_data_required_matches_contract and prompt_text_references_no_live_data_boundary present
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_cron_prompt_pack --input-json '{"asset":"TQQQ","include_position_review":false}' --no-audit -> passed, prompt_live_data_required_matches_contract and prompt_text_references_no_live_data_boundary present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 107 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state/ only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 16 passed, cron prompt decision focus guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_cron_prompt_pack --input-json '{"asset":"TQQQ"}' --no-audit -> passed, prompt_decision_focus_matches_contract and prompt_text_references_decision_focus present
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_cron_prompt_pack --input-json '{"asset":"TQQQ","include_position_review":false}' --no-audit -> passed, prompt_decision_focus_matches_contract and prompt_text_references_decision_focus present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 107 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state/ only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 16 passed, cron prompt supported intents registry guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_cron_prompt_pack --input-json '{"asset":"TQQQ"}' --no-audit -> passed, supported_report_intents_match_registry present
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_cron_prompt_pack --input-json '{"asset":"TQQQ","include_position_review":false}' --no-audit -> passed, supported_report_intents_match_registry present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 107 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state/ only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 16 passed, cron prompt pack identity guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_cron_prompt_pack --input-json '{"asset":"TQQQ"}' --no-audit -> passed, cron_prompt_contract_name_matches_schema, prompt_assets_match_pack_asset, and report_prompt_timeframes_match_pack_timeframe present
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_cron_prompt_pack --input-json '{"asset":"TQQQ","include_position_review":false}' --no-audit -> passed, cron_prompt_contract_name_matches_schema, prompt_assets_match_pack_asset, and report_prompt_timeframes_match_pack_timeframe present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 107 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state/ only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 16 passed, cron prompt position option contract guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_cron_prompt_pack --input-json '{"asset":"TQQQ"}' --no-audit -> passed, include_position_review_contract_matches_request present
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_cron_prompt_pack --input-json '{"asset":"TQQQ","include_position_review":false}' --no-audit -> passed, include_position_review_contract_matches_request present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 107 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state/ only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 16 passed, cron prompt pack top-level contract guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_cron_prompt_pack --input-json '{"asset":"TQQQ"}' --no-audit -> passed, cron_prompt_pack_schema_version_matches_expected and pack_live_data_required_matches_contract present
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_cron_prompt_pack --input-json '{"asset":"TQQQ","include_position_review":false}' --no-audit -> passed, cron_prompt_pack_schema_version_matches_expected and pack_live_data_required_matches_contract present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 107 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state/ only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 16 passed, cron prompt manual setup registry guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_cron_prompt_pack --input-json '{"asset":"TQQQ"}' --no-audit -> passed, manual_setup_requirements_match_registry present
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_cron_prompt_pack --input-json '{"asset":"TQQQ","include_position_review":false}' --no-audit -> passed, manual_setup_requirements_match_registry present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 107 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state/ only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 16 passed, cron prompt contract key schema guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_cron_prompt_pack --input-json '{"asset":"TQQQ"}' --no-audit -> passed, cron_prompt_contract_keys_match_expected_schema present
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_cron_prompt_pack --input-json '{"asset":"TQQQ","include_position_review":false}' --no-audit -> passed, cron_prompt_contract_keys_match_expected_schema present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 107 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state/ only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 16 passed, cron prompt prompt key schema guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_cron_prompt_pack --input-json '{"asset":"TQQQ"}' --no-audit -> passed, cron_prompt_prompt_keys_match_expected_schema present
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_cron_prompt_pack --input-json '{"asset":"TQQQ","include_position_review":false}' --no-audit -> passed, cron_prompt_prompt_keys_match_expected_schema present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 107 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state/ only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 16 passed, cron prompt pack key schema guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_cron_prompt_pack --input-json '{"asset":"TQQQ"}' --no-audit -> passed, cron_prompt_pack_keys_match_expected_schema present
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_cron_prompt_pack --input-json '{"asset":"TQQQ","include_position_review":false}' --no-audit -> passed, cron_prompt_pack_keys_match_expected_schema present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 107 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state/ only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 16 passed, cron prompt guard check key schema guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_cron_prompt_pack --input-json '{"asset":"TQQQ"}' --no-audit -> passed, cron_prompt_guard_check_keys_match_expected_schema present
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_cron_prompt_pack --input-json '{"asset":"TQQQ","include_position_review":false}' --no-audit -> passed, cron_prompt_guard_check_keys_match_expected_schema present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 107 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state/ only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 16 passed, cron prompt guard key schema guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_cron_prompt_pack --input-json '{"asset":"TQQQ"}' --no-audit -> passed, cron_prompt_guard_keys_match_expected_schema present
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_cron_prompt_pack --input-json '{"asset":"TQQQ","include_position_review":false}' --no-audit -> passed, cron_prompt_guard_keys_match_expected_schema present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 107 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state/ only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 16 passed, cron prompt guard check name schema guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_cron_prompt_pack --input-json '{"asset":"TQQQ"}' --no-audit -> passed, cron_prompt_guard_check_names_match_expected_schema present
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_cron_prompt_pack --input-json '{"asset":"TQQQ","include_position_review":false}' --no-audit -> passed, cron_prompt_guard_check_names_match_expected_schema present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 107 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state only
```

## 6. Immediate Next Action

Current completed gates: Stage A, Stage B replay provider, Stage C JSONL signal
repository contract, Stage D runtime watchdog/retention/checkpoint, Stage E report harness,
Stage E position review report, delivery preview, and evidence guard, Stage F
optional chart ref/code guard, Stage G BTC COIN-M guarded path/admin, and Stage
H offline integration readiness, Phase 6 extended 180-day OOS fixture
hardening, report intent output variants, and Phase 6 feedback tool manifest
alignment, plus Phase 7 runtime tool manifest alignment.
Phase 9 BTC tool manifest alignment is also complete.
Health capability and MVP required tool manifest parity is complete.
Audit read tool payload contracts are complete.
MCP server wrapper parity with the shared registry is complete.
MCP server dispatch parity with the shared registry is complete.
MCP server payload parity with wrapper parameters is complete.
MCP server signature parity with registered implementation functions is complete.
Tool registry spec invariants are complete.
MVP manifest and shared registry ordered parity is complete.
Report intent prompt contract alignment is complete.
Cron prompt intent/input alignment is complete.
Phase 6 unsupported long fixture window guard is complete.
Report data warning Cautions guard is complete.
Report Telegram required_sections intent guard is complete.
Position review Telegram required_sections guard is complete.
Delivery preview no-send guard is complete.
Hermes delivery preview payload guard is complete.
Telegram preview required section guard is complete.
Telegram preview unrequested section guard is complete.
Telegram preview chunk index guard is complete.
Telegram preview message count guard is complete.
Telegram preview chunk char-count guard is complete.
Telegram preview nonempty chunk guard is complete.
Telegram preview section separator guard is complete.
Telegram preview overflow policy guard is complete.
Position review max_chars contract guard is complete.
Position review contract key schema guard is complete.
Position review contract no-network guard is complete.
Position review contract identity guard is complete.
Delivery contract no-send guard is complete.
Delivery contract no-network guard coverage is complete.
Delivery contract key schema guard is complete.
Report and position review guard check name schema guard is complete.
Report and position review guard check key schema guard is complete.
Evidence guard check name schema guard is complete.
Evidence guard check key schema guard is complete.
Report, position, and evidence guard top-level key schema guard is complete.
Report and position payload key schema guard is complete.
Report and position payload schema/live-data guard is complete.
Report and position payload guard check name schema guard is complete.
Report and position payload guard check key schema guard is complete.
Report and position payload guard top-level key schema guard is complete.
Report payload source signal ref key schema guard is complete.
Report payload source signal ref identity guard is complete.
Report payload source signal ref trace format guard is complete.
Report payload source signal ref config hash digest guard is complete.
Delivery preview no-network and chunk guard coverage is complete.
Delivery preview guard check name schema guard is complete.
Delivery preview guard check key schema guard is complete.
Delivery preview payload key schema guard is complete.
Report contract numeric authority guard is complete.
Report text numeric field guard is complete.
Cron prompt tool/input schema guard is complete.
Cron prompt idempotency key guard is complete.
Cron prompt idempotency text guard is complete.
Cron prompt manual setup guard is complete.
Cron prompt no-secret credential guard is complete.
Cron prompt name set guard is complete.
Cron prompt schedule hint guard is complete.
Cron prompt tool/input text guard is complete.
Cron prompt configured gateway text guard is complete.
Cron prompt delivery preview text guard is complete.
Cron prompt numeric authority text guard is complete.
Cron prompt order block text guard is complete.
Cron prompt expected sections text guard is complete.
Cron prompt schedule hint text guard is complete.
Cron prompt manual setup text guard is complete.
Cron prompt no-secret text guard is complete.
Cron prompt name text guard is complete.
Cron prompt delivery path metadata guard is complete.
Cron prompt Telegram format schema guard is complete.
Cron prompt numeric authority metadata guard is complete.
Cron prompt output schema guard is complete.
Cron prompt live data boundary guard is complete.
Cron prompt decision focus guard is complete.
Cron prompt supported intents registry guard is complete.
Cron prompt pack identity guard is complete.
Cron prompt position option contract guard is complete.
Cron prompt pack top-level contract guard is complete.
Cron prompt pack key schema guard is complete.
Cron prompt guard key schema guard is complete.
Cron prompt guard check name schema guard is complete.
Cron prompt guard check key schema guard is complete.
Cron prompt manual setup registry guard is complete.
Cron prompt contract key schema guard is complete.
Cron prompt prompt key schema guard is complete.
Cron prompt scheduler setup prerequisite guard is complete.

PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 16 passed, cron prompt scheduler setup prerequisite guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_cron_prompt_pack --input-json '{"asset":"TQQQ"}' --no-audit -> passed, prompt_text_declares_manual_setup_before_scheduler_setup present
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_cron_prompt_pack --input-json '{"asset":"TQQQ","include_position_review":false}' --no-audit -> passed, prompt_text_declares_manual_setup_before_scheduler_setup present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 107 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 16 passed, delivery preview no-network and chunk guards asserted
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_latest_signal_report --input-json '{"asset":"TQQQ"}' --no-audit -> passed, delivery preview no-network/chunk guards present
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_position_review_report --input-json '{"asset":"TQQQ","entry_price":100,"current_price":114,"size":3}' --no-audit -> passed, delivery preview no-network/chunk guards present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 107 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 16 passed, delivery preview guard check name schema guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_latest_signal_report --input-json '{"asset":"TQQQ"}' --no-audit -> passed, delivery_preview_guard_check_names_match_expected_schema present
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_position_review_report --input-json '{"asset":"TQQQ","entry_price":100,"current_price":114,"size":3}' --no-audit -> passed, delivery_preview_guard_check_names_match_expected_schema present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 107 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 16 passed, delivery preview guard check key schema guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_latest_signal_report --input-json '{"asset":"TQQQ"}' --no-audit -> passed, delivery_preview_guard_check_keys_match_expected_schema present
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_position_review_report --input-json '{"asset":"TQQQ","entry_price":100,"current_price":114,"size":3}' --no-audit -> passed, delivery_preview_guard_check_keys_match_expected_schema present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 107 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 16 passed, delivery preview payload key schema guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_latest_signal_report --input-json '{"asset":"TQQQ"}' --no-audit -> passed, delivery_preview_payload_keys_match_expected_schema present
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_position_review_report --input-json '{"asset":"TQQQ","entry_price":100,"current_price":114,"size":3}' --no-audit -> passed, delivery_preview_payload_keys_match_expected_schema present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 107 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 16 passed, delivery contract key schema guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_latest_signal_report --input-json '{"asset":"TQQQ"}' --no-audit -> passed, delivery_contract_keys_match_expected_schema present
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_position_review_report --input-json '{"asset":"TQQQ","entry_price":100,"current_price":114,"size":3}' --no-audit -> passed, delivery_contract_keys_match_expected_schema present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 107 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 16 passed, report/position guard check name schema guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_latest_signal_report --input-json '{"asset":"TQQQ"}' --no-audit -> passed, report_contract_guard_check_names_match_expected_schema present
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_position_review_report --input-json '{"asset":"TQQQ","entry_price":100,"current_price":114,"size":3}' --no-audit -> passed, position_review_guard_check_names_match_expected_schema present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 107 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 16 passed, report/position guard check key schema guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_latest_signal_report --input-json '{"asset":"TQQQ"}' --no-audit -> passed, report_contract_guard_check_keys_match_expected_schema present
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_position_review_report --input-json '{"asset":"TQQQ","entry_price":100,"current_price":114,"size":3}' --no-audit -> passed, position_review_guard_check_keys_match_expected_schema present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 107 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 16 passed, evidence guard check name schema guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_latest_signal_report --input-json '{"asset":"TQQQ"}' --no-audit -> passed, evidence_guard_check_names_match_expected_schema present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 107 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 16 passed, evidence guard check key schema guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_latest_signal_report --input-json '{"asset":"TQQQ"}' --no-audit -> passed, evidence_guard_check_keys_match_expected_schema present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 107 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 16 passed, report/position/evidence guard top-level key schema guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_latest_signal_report --input-json '{"asset":"TQQQ"}' --no-audit -> passed, report_contract_guard_keys_match_expected_schema and evidence_guard_keys_match_expected_schema present
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_position_review_report --input-json '{"asset":"TQQQ","entry_price":100,"current_price":114,"size":3}' --no-audit -> passed, position_review_guard_keys_match_expected_schema present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 107 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 16 passed, report/position payload key schema guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_latest_signal_report --input-json '{"asset":"TQQQ"}' --no-audit -> passed, report_payload_keys_match_expected_schema present
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_position_review_report --input-json '{"asset":"TQQQ","entry_price":100,"current_price":114,"size":3}' --no-audit -> passed, position_payload_keys_match_expected_schema present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 107 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 16 passed, report/position payload schema/live-data guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_latest_signal_report --input-json '{"asset":"TQQQ"}' --no-audit -> passed, report_payload_schema_version_matches_expected and report_payload_live_data_required_matches_expected present
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_position_review_report --input-json '{"asset":"TQQQ","entry_price":100,"current_price":114,"size":3}' --no-audit -> passed, position_payload_schema_version_matches_expected and position_payload_live_data_required_matches_expected present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 107 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 16 passed, report/position payload guard check name schema guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_latest_signal_report --input-json '{"asset":"TQQQ"}' --no-audit -> passed, report_payload_guard_check_names_match_expected_schema present
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_position_review_report --input-json '{"asset":"TQQQ","entry_price":100,"current_price":114,"size":3}' --no-audit -> passed, position_payload_guard_check_names_match_expected_schema present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 107 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 16 passed, report/position payload guard check key schema guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_latest_signal_report --input-json '{"asset":"TQQQ"}' --no-audit -> passed, report_payload_guard_check_keys_match_expected_schema present
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_position_review_report --input-json '{"asset":"TQQQ","entry_price":100,"current_price":114,"size":3}' --no-audit -> passed, position_payload_guard_check_keys_match_expected_schema present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 107 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 16 passed, report/position payload guard top-level key schema guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_latest_signal_report --input-json '{"asset":"TQQQ"}' --no-audit -> passed, report_payload_guard_keys_match_expected_schema present
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_position_review_report --input-json '{"asset":"TQQQ","entry_price":100,"current_price":114,"size":3}' --no-audit -> passed, position_payload_guard_keys_match_expected_schema present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 107 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 16 passed, report payload source_signal_ref key schema guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_latest_signal_report --input-json '{"asset":"TQQQ"}' --no-audit -> passed, report_payload_source_signal_ref_keys_match_expected_schema present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 107 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 16 passed, report payload source_signal_ref identity guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_latest_signal_report --input-json '{"asset":"TQQQ"}' --no-audit -> passed, report_payload_source_signal_ref_matches_report_identity present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 107 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 16 passed, report payload source_signal_ref trace format guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_latest_signal_report --input-json '{"asset":"TQQQ"}' --no-audit -> passed, report_payload_source_signal_ref_values_have_traceable_format present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 107 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 16 passed, report payload source_signal_ref config hash digest guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_latest_signal_report --input-json '{"asset":"TQQQ"}' --no-audit -> passed, report_payload_source_signal_ref_config_hash_digest_is_sha256 present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 107 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 16 passed, position review contract key schema guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_position_review_report --input-json '{"asset":"TQQQ","entry_price":100,"current_price":114,"size":3}' --no-audit -> passed, position_review_contract_keys_match_expected_schema present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 107 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 16 passed, position review contract no-network guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_position_review_report --input-json '{"asset":"TQQQ","entry_price":100,"current_price":114,"size":3}' --no-audit -> passed, position_review_contract_has_no_network_side_effect present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 107 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 16 passed, position review contract identity guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_position_review_report --input-json '{"asset":"TQQQ","entry_price":100,"current_price":114,"size":3}' --no-audit -> passed, position_review_contract_identity_matches_expected present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 107 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 16 passed, position review contract required sections guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_position_review_report --no-audit -> passed, position_review_contract_required_sections_match_expected present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 107 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 16 passed, position review contract order submission guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_position_review_report --no-audit -> passed, position_review_contract_has_no_order_submission_side_effect present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 107 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 16 passed, position review section order guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_position_review_report --no-audit -> passed, position_review_sections_match_contract_order present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 107 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 16 passed, position review prompt must_include guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_position_review_report --no-audit -> passed, position_review_prompt_must_include_matches_expected_terms present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 107 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 16 passed, position review prompt contract key schema guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_position_review_report --no-audit -> passed, position_review_prompt_contract_keys_match_expected_schema present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 107 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 16 passed, position review prompt contract identity guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_position_review_report --no-audit -> passed, position_review_prompt_contract_identity_matches_expected present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 107 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 16 passed, position review Telegram max_chars identity guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_position_review_report --no-audit -> passed, position_review_telegram_max_chars_matches_expected present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 107 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 16 passed, position review Telegram schema version guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_position_review_report --no-audit -> passed, position_review_telegram_schema_version_matches_expected present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 107 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 16 passed, position review Telegram chunking contract guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_position_review_report --no-audit -> passed, position_review_telegram_chunking_contract_matches_expected present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 107 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 16 passed, position review delivery channel format guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_position_review_report --no-audit -> passed, delivery_channel_formats_match_expected present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 107 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 16 passed, position review delivery cron intents guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_position_review_report --no-audit -> passed, delivery_cron_intents_match_report_intent_registry present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 107 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 16 passed, report delivery cron intents guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_latest_signal_report --no-audit -> passed, delivery_cron_intents_match_report_intent_registry present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 107 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 16 passed, report delivery channel format guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_latest_signal_report --no-audit -> passed, delivery_channel_formats_match_expected present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 107 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 16 passed, report Telegram max_chars identity guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_latest_signal_report --no-audit -> passed, report_telegram_max_chars_matches_expected present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 107 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 16 passed, report Telegram schema_version guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_latest_signal_report --no-audit -> passed, report_telegram_schema_version_matches_expected present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 107 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 16 passed, report Telegram chunking contract guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_latest_signal_report --no-audit -> passed, report_telegram_chunking_contract_matches_expected present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 107 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 16 passed, report prompt must_include exact guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_latest_signal_report --no-audit -> passed, report_prompt_must_include_matches_intent_terms present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 107 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 16 passed, report prompt contract key schema guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_latest_signal_report --no-audit -> passed, report_prompt_contract_keys_match_expected_schema present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 107 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 16 passed, report prompt contract identity guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_latest_signal_report --no-audit -> passed, report_prompt_contract_identity_matches_expected present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 107 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 16 passed, report intent contract key schema guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_latest_signal_report --no-audit -> passed, report_intent_contract_keys_match_expected_schema present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 107 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 16 passed, report intent contract registry guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_latest_signal_report --no-audit -> passed, report_intent_contract_matches_registry present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 107 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 16 passed, report sections intent order guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_latest_signal_report --no-audit -> passed, report_sections_match_intent_order present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 107 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 16 passed, report text sections intent order guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_latest_signal_report --no-audit -> passed, report_text_sections_match_intent_order present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 107 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 16 passed, report payload intent contract guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_latest_signal_report --no-audit -> passed, report_payload_intent_matches_contract present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 107 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 16 passed, report payload top-level identity guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_latest_signal_report --no-audit -> passed, report_payload_top_level_identity_matches_latest_signal_report present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 107 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 16 passed, report payload nested guard status guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_latest_signal_report --no-audit -> passed, report_payload_nested_guard_statuses_are_ok present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 107 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 16 passed, position payload top-level identity guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_position_review_report --input-json '{"asset":"TQQQ","entry_price":100,"current_price":114,"size":3}' --no-audit -> passed, position_payload_top_level_identity_matches_position_review present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 107 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 16 passed, position payload nested guard status guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_position_review_report --input-json '{"asset":"TQQQ","entry_price":100,"current_price":114,"size":3}' --no-audit -> passed, position_payload_nested_guard_statuses_are_ok present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 107 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 16 passed, cron prompt ordered unique prompt names guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_cron_prompt_pack --input-json '{"asset":"TQQQ"}' --no-audit -> passed, prompt_names_match_contract_order_and_are_unique present
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_cron_prompt_pack --input-json '{"asset":"TQQQ","include_position_review":false}' --no-audit -> passed, prompt_names_match_contract_order_and_are_unique present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 107 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 16 passed, cron prompt position review sections guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_cron_prompt_pack --input-json '{"asset":"TQQQ"}' --no-audit -> passed, position_review_prompt_expected_sections_match_contract present
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_cron_prompt_pack --input-json '{"asset":"TQQQ","include_position_review":false}' --no-audit -> passed, position_review_prompt_expected_sections_match_contract present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 107 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 16 passed, report payload optional context status guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_latest_signal_report --no-audit -> passed, report_payload_optional_context_statuses_are_ok present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 107 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 17 passed, report payload optional context guard-status guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_latest_signal_report --no-audit -> passed, report_payload_optional_context_guards_are_ok present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 108 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 17 passed, multimodal context guard schema guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_latest_signal_report --input-json '{"asset":"TQQQ","include_chart":true,"chart_output_dir":"/private/tmp/halo_swing_multimodal_guard_schema"}' --no-audit -> passed, multimodal_context guard schema checks present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 108 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 17 passed, multimodal context payload key schema guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_latest_signal_report --input-json '{"asset":"TQQQ","include_chart":true,"chart_output_dir":"/private/tmp/halo_swing_multimodal_context_keys"}' --no-audit -> passed, multimodal_context_keys_match_expected_schema present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 108 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 17 passed, multimodal context artifact ref schema guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_latest_signal_report --input-json '{"asset":"TQQQ","include_chart":true,"chart_output_dir":"/private/tmp/halo_swing_multimodal_artifact_ref_schema"}' --no-audit -> passed, multimodal_context_artifact_refs_match_expected_schema present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 108 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 17 passed, multimodal context artifact metadata schema guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_latest_signal_report --input-json '{"asset":"TQQQ","include_chart":true,"chart_output_dir":"/private/tmp/halo_swing_multimodal_artifact_metadata_schema"}' --no-audit -> passed, multimodal_context_artifact_ref_metadata_matches_expected_schema present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 108 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 17 passed, multimodal context artifact metadata value guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_latest_signal_report --input-json '{"asset":"TQQQ","include_chart":true,"chart_output_dir":"/private/tmp/halo_swing_multimodal_artifact_metadata_values"}' --no-audit -> passed, multimodal_context_artifact_ref_metadata_values_are_safe present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 108 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 17 passed, multimodal context modality count guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_latest_signal_report --input-json '{"asset":"TQQQ","include_chart":true,"chart_output_dir":"/private/tmp/halo_swing_multimodal_modality_counts"}' --no-audit -> passed, multimodal_context_modality_counts_match_expected_context present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 108 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 17 passed, multimodal context evidence card schema guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_latest_signal_report --input-json '{"asset":"TQQQ","include_chart":true,"chart_output_dir":"/private/tmp/halo_swing_multimodal_evidence_card_schema"}' --no-audit -> passed, multimodal_context_evidence_cards_match_expected_schema present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 108 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 17 passed, multimodal context artifact_ref identity guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_latest_signal_report --input-json '{"asset":"TQQQ","include_chart":true,"chart_output_dir":"/private/tmp/halo_swing_multimodal_artifact_ref_identity"}' --no-audit -> passed, multimodal_context_artifact_refs_match_expected_context present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 108 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 17 passed, multimodal context evidence card value guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_latest_signal_report --input-json '{"asset":"TQQQ","include_chart":true,"chart_output_dir":"/private/tmp/halo_swing_multimodal_evidence_card_values"}' --no-audit -> passed, multimodal_context_evidence_card_values_are_safe present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 108 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 17 passed, multimodal context identity values guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_latest_signal_report --input-json '{"asset":"TQQQ","include_chart":true,"chart_output_dir":"/private/tmp/halo_swing_multimodal_identity_values"}' --no-audit -> passed, multimodal_context_identity_values_match_expected_contract present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 108 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 18 passed, multimodal context report intent variants covered
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_latest_signal_report --input-json '{"asset":"TQQQ","report_intent":"intraday_risk_watch","include_chart":true,"chart_output_dir":"/private/tmp/halo_swing_multimodal_intraday_variant"}' --no-audit -> passed, intraday multimodal context and optional context guards present
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_latest_signal_report --input-json '{"asset":"TQQQ","report_intent":"post_market_review","include_chart":true,"chart_output_dir":"/private/tmp/halo_swing_multimodal_post_market_variant"}' --no-audit -> passed, post-market multimodal context and optional context guards present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 109 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 19 passed, document-only multimodal report intent variants covered
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_latest_signal_report --input-json '{"asset":"TQQQ","report_intent":"intraday_risk_watch","extra_evidence_cards":[{"evidence_id":"manual_document_summary","category":"manual_document","source":"manual:document_summary","modality":"pdf_summary","observed_at":"2026-05-11T00:00:00Z","asset_scope":["QQQ","TQQQ"],"bias":"neutral","strength":0.5,"confidence":0.5,"summary":"FOMC minutes summary says policy remains restrictive but stable.","summary_truncated":false,"buy_impact":"context_only","sell_impact":"context_only","invalidating_condition":"Document summary becomes stale or contradicted.","artifact_ref":{"ref_type":"PDF","ref":"artifact://documents/fomc-minutes-summary.pdf","metadata":{"description":"Caller-supplied document summary reference","portable":true,"parsed_by_mcp":false}}}]}' --no-audit -> passed, intraday document-only multimodal context and optional context guards present
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_latest_signal_report --input-json '{"asset":"TQQQ","report_intent":"post_market_review","extra_evidence_cards":[{"evidence_id":"manual_document_summary","category":"manual_document","source":"manual:document_summary","modality":"pdf_summary","observed_at":"2026-05-11T00:00:00Z","asset_scope":["QQQ","TQQQ"],"bias":"neutral","strength":0.5,"confidence":0.5,"summary":"FOMC minutes summary says policy remains restrictive but stable.","summary_truncated":false,"buy_impact":"context_only","sell_impact":"context_only","invalidating_condition":"Document summary becomes stale or contradicted.","artifact_ref":{"ref_type":"PDF","ref":"artifact://documents/fomc-minutes-summary.pdf","metadata":{"description":"Caller-supplied document summary reference","portable":true,"parsed_by_mcp":false}}}]}' --no-audit -> passed, post-market document-only multimodal context and optional context guards present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 110 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 20 passed, multimodal context artifact_ref ref_type guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 111 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 21 passed, multimodal context artifact_ref metadata per-entry schema guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 112 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 22 passed, multimodal context evidence_id uniqueness guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 113 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 23 passed, multimodal context evidence card categorical guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 114 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 24 passed, multimodal context evidence card summary bounds guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 115 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 25 passed, multimodal context evidence card summary truncation guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 116 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 26 passed, multimodal context evidence card impact context-only guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 117 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 27 passed, multimodal context evidence card asset_scope guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 118 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 28 passed, multimodal context evidence card invalidating_condition guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 119 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 29 passed, multimodal context evidence card observed_at guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 120 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 30 passed, multimodal context evidence card modality guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 121 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 31 passed, multimodal context evidence card artifact URI guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 122 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 32 passed, multimodal context PDF artifact ref contract guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 123 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 33 passed, multimodal context observed_at temporal guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 124 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 34 passed, multimodal context evidence card reserved id guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 125 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 35 passed, multimodal context evidence card safe id guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 126 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 35 passed, multimodal context artifact_ref evidence id safe guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 126 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 36 passed, multimodal context artifact_ref value uniqueness guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 127 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 37 passed, multimodal context CHART artifact ref PNG contract guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 128 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 38 passed, multimodal context CHART artifact ref offline location guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 129 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 39 passed, multimodal context CHART artifact ref file URI rejection enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 130 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 40 passed, multimodal context CHART artifact ref tilde path rejection enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 131 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 42 passed, multimodal context content-address digest format guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 133 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 44 passed, valid content-address CHART/PDF artifact refs accepted
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 135 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 46 passed, CHART machine-specific path refs rejected
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 137 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 48 passed, embedded local path markers in artifact refs rejected
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 139 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 50 passed, artifact_ref string safety guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 141 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 52 passed, evidence card text string safety guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 143 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 53 passed, artifact_ref metadata text string safety guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 144 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 55 passed, evidence card scalar string safety guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 146 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 56 passed, evidence card asset_scope string safety guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 147 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 57 passed, artifact_ref ref_type canonical case guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 148 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 58 passed, artifact_ref metadata value type guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 149 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 59 passed, CHART metadata value type negative coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 150 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 60 passed, evidence card string field type guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 151 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 61 passed, evidence card structural field type guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 152 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 62 passed, document artifact_ref structural negative coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 153 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 63 passed, evidence card numeric bool negative coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 154 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 64 passed, summary truncation flag type negative coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 155 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 65 passed, asset_scope value type negative coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 156 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 66 passed, evidence_id type guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 157 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 67 passed, artifact_ref string field type guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 158 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 68 passed, artifact_ref metadata non-dict negative coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 159 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 69 passed, CHART artifact_ref metadata DTO validation coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 160 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 70 passed, CHART artifact_ref scalar DTO validation coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 161 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 71 passed, CHART ref slot artifact type guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 162 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 72 passed, CHART artifact_ref declaration negative coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 163 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 73 passed, CHART artifact_ref reserved evidence_id guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 164 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 74 passed, CHART artifact_ref renderer value type guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 165 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 75 passed, CHART artifact_ref renderer value negative coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 166 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 76 passed, CHART artifact_ref renderer text safety guard enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 167 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 77 passed, PDF artifact_ref ref_type field negative coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 168 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 78 passed, CHART artifact_ref ref_type DTO validation coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 169 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 79 passed, document observed_at type negative coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 170 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 80 passed, document modality type negative coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 171 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 81 passed, document bias type negative coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 172 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 82 passed, document invalidating_condition type negative coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 173 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 83 passed, document impact type negative coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 174 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 84 passed, document category/source type negative coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 175 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 85 passed, document numeric type negative coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 176 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 86 passed, document numeric range negative coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 177 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 87 passed, document summary nonempty negative coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 178 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 88 passed, document modality nonempty negative coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 179 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 89 passed, document observed_at nonempty negative coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 180 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 90 passed, document asset_scope empty negative coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 181 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 91 passed, document invalidating_condition nonempty negative coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 182 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 92 passed, document impact nonempty negative coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 183 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 93 passed, document category/source empty negative coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 184 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 94 passed, document bias empty negative coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 185 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 95 passed, document asset_scope uppercase negative coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 186 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 96 passed, document PDF artifact_ref empty value negative coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 187 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 97 passed, document PDF artifact_ref ref_type empty negative coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 188 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 98 passed, document PDF metadata description nonempty negative coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 189 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 99 passed, document PDF metadata bool values negative coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 190 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 100 passed, document PDF metadata missing key negative coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 191 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 101 passed, CHART metadata missing key negative coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 192 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 102 passed, CHART metadata values negative coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 193 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 103 passed, CHART artifact_ref ref_type empty DTO validation coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 194 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 104 passed, CHART artifact_ref ref_type lowercase DTO validation coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 195 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 105 passed, CHART artifact_ref control character negative coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 196 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 106 passed, CHART artifact_ref duplicate value negative coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 197 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 107 passed, document evidence_id duplicate negative coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 198 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py::test_latest_signal_report_rejects_missing_document_source_key -q -> 1 passed, document source key schema negative coverage enforced
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 108 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 199 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py::test_latest_signal_report_rejects_unexpected_document_card_key -q -> 1 passed, document unexpected key schema negative coverage enforced
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 109 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 200 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py::test_latest_signal_report_rejects_unexpected_pdf_artifact_ref_key -q -> 1 passed, PDF artifact_ref unexpected key schema negative coverage enforced
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 110 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 201 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py::test_latest_signal_report_rejects_missing_pdf_artifact_ref_value_key -q -> 1 passed, PDF artifact_ref missing ref key negative coverage enforced
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 111 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 202 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py::test_latest_signal_report_rejects_missing_pdf_artifact_ref_type_key -q -> 1 passed, PDF artifact_ref missing ref_type key negative coverage enforced
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 112 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 203 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py::test_latest_signal_report_rejects_missing_pdf_artifact_ref_metadata_key -q -> 1 passed, PDF artifact_ref missing metadata key negative coverage enforced
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 113 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 204 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py::test_latest_signal_report_rejects_missing_chart_artifact_ref_metadata_key -q -> 1 passed, CHART artifact_ref missing metadata key negative coverage enforced
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 114 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 205 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py::test_latest_signal_report_rejects_missing_chart_artifact_ref_value_key -q -> 1 passed, CHART artifact_ref missing ref key DTO negative coverage enforced
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 115 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 206 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py::test_latest_signal_report_rejects_missing_chart_artifact_ref_type_key -q -> 1 passed, CHART artifact_ref missing ref_type key DTO negative coverage enforced
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 116 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 207 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py::test_latest_signal_report_rejects_unexpected_chart_artifact_ref_key -q -> 1 passed, CHART artifact_ref unexpected key DTO negative coverage enforced
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 117 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 208 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py::test_latest_signal_report_rejects_unexpected_chart_metadata_key -q -> 1 passed, CHART metadata unexpected key negative coverage enforced
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 118 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 209 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py::test_latest_signal_report_rejects_unexpected_pdf_metadata_key -q -> 1 passed, PDF metadata unexpected key aggregate negative coverage enforced
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 119 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 210 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py::test_latest_signal_report_rejects_missing_document_artifact_ref_key tests/test_reporting.py::test_latest_signal_report_rejects_empty_pdf_artifact_ref_value -q -> 2 passed, document artifact_ref missing key portable guard negative coverage enforced
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 120 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 211 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py::test_latest_signal_report_rejects_empty_document_artifact_ref_dict tests/test_reporting.py::test_latest_signal_report_rejects_missing_document_artifact_ref_key tests/test_reporting.py::test_latest_signal_report_rejects_non_dict_document_artifact_ref -q -> 3 passed, empty document artifact_ref dict collection negative coverage enforced
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 121 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 212 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py::test_latest_signal_report_rejects_empty_document_artifact_ref_dict tests/test_reporting.py::test_latest_signal_report_rejects_missing_document_artifact_ref_key -q -> 2 passed, artifact_ref collection coverage guard enforced
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 121 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 212 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py::test_latest_signal_report_rejects_null_document_artifact_ref -q -> 1 passed, null document artifact_ref collection negative coverage enforced
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py::test_latest_signal_report_rejects_empty_document_artifact_ref_dict tests/test_reporting.py::test_latest_signal_report_rejects_null_document_artifact_ref tests/test_reporting.py::test_latest_signal_report_rejects_missing_document_artifact_ref_key -q -> 3 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 122 passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 213 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_readiness.py -q -> 8 passed, integration readiness next_actions contract coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_readiness.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 213 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_readiness.py -q -> 9 passed, integration readiness payload schema contract coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_readiness.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 214 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_readiness.py -q -> 10 passed, integration readiness configured credential schema coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_readiness.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 215 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_binance_btc.py -q -> 19 passed, Binance credential status schema contract coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_binance_btc.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 215 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_audit.py::test_harness_save_binance_credentials_audit_redacts_secret_inputs -q -> 1 passed, harness save_binance_credentials audit redaction coverage enforced
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_audit.py -q -> 6 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_audit.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 216 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_binance_btc.py::test_trading_admin_status_is_secret_safe -q -> 1 passed, trading admin credential status secret-safe coverage enforced
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_binance_btc.py -q -> 19 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_binance_btc.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 216 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_binance_btc.py::test_trading_admin_credentials_endpoint_returns_secret_safe_status -q -> 1 passed, trading admin credentials endpoint secret-safe coverage enforced
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_binance_btc.py -q -> 20 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_binance_btc.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 217 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_binance_btc.py::test_trading_admin_account_snapshot_endpoint_blocks_secret_safely -q -> 1 passed, trading admin account endpoint secret-safe block coverage enforced
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_binance_btc.py -q -> 21 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_binance_btc.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 218 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_audit.py::test_mcp_server_execute_order_audit_redacts_credential_passphrase -q -> 1 passed, MCP server order passphrase audit redaction coverage enforced
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_audit.py -q -> 7 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_audit.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 219 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_audit.py::test_mcp_server_account_snapshot_audit_redacts_credential_passphrase -q -> 1 passed, MCP server account passphrase audit redaction coverage enforced
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_audit.py -q -> 8 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_audit.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 220 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_audit.py::test_harness_account_snapshot_failure_audit_redacts_passphrase -q -> 1 passed, harness account failure passphrase audit redaction coverage enforced
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_audit.py -q -> 9 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_audit.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 221 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_audit.py::test_audit_read_surfaces_preserve_redacted_failure_event -q -> 1 passed, audit read-surface failure redaction coverage enforced
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_audit.py -q -> 10 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_audit.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 222 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_runtime_guard.py::test_runtime_status_watchdog_does_not_return_audit_event_details_or_secrets -q -> 1 passed, runtime status audit failure secret boundary coverage enforced
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_runtime_guard.py -q -> 6 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_runtime_guard.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 223 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_runtime_guard.py::test_runtime_checkpoint_does_not_persist_audit_event_details_or_secrets -q -> 1 passed, runtime checkpoint audit failure secret boundary coverage enforced
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_runtime_guard.py -q -> 7 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_runtime_guard.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 224 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_runtime_guard.py::test_runtime_checkpoint_readiness_snapshot_does_not_persist_env_secrets -q -> 1 passed, runtime checkpoint readiness env secret boundary coverage enforced
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_runtime_guard.py -q -> 8 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_runtime_guard.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 225 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_readiness.py::test_integration_readiness_env_secrets_are_boolean_only -q -> 1 passed, integration readiness env secret boolean coverage enforced
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_readiness.py -q -> 11 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_readiness.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 226 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state/ only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_audit.py::test_harness_integration_readiness_audit_redacts_env_secrets -q -> 1 passed, harness readiness audit env secret boundary coverage enforced
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_audit.py -q -> 11 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_audit.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 227 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state/ only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_audit.py::test_mcp_server_integration_readiness_audit_redacts_env_secrets -q -> 1 passed, MCP server readiness audit env secret boundary coverage enforced
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_audit.py -q -> 12 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_audit.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 228 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state/ only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_audit.py::test_audit_read_surfaces_preserve_readiness_env_secret_boundary -q -> 1 passed, audit read-surface readiness env secret boundary coverage enforced
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_audit.py -q -> 13 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_audit.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 229 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state/ only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_audit.py::test_audit_summary_surfaces_preserve_readiness_env_secret_boundary -q -> 1 passed, audit summary readiness env secret boundary coverage enforced
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_audit.py -q -> 14 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_audit.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 230 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state/ only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_readiness.py::test_integration_readiness_env_secret_aliases_are_boolean_only -q -> 1 passed, integration readiness env alias secret boolean coverage enforced
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_readiness.py -q -> 12 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_readiness.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 231 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state/ only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_readiness.py::test_integration_readiness_live_data_source_env_values_are_boolean_only -q -> 1 passed, integration readiness live data source env boolean coverage enforced
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_readiness.py -q -> 13 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_readiness.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 232 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state/ only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py::test_latest_signal_report_rejects_unsupported_report_intent_at_boundary -q -> 1 passed, unsupported report_intent boundary coverage enforced
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 123 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_reporting.py src/halo_swing_mcp/tools/reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 233 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state/ only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py::test_harness_rejects_unsupported_report_intent_with_failure_audit -q -> 1 passed, harness unsupported report_intent failure audit coverage enforced
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 124 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_reporting.py src/halo_swing_mcp/tools/reporting.py src/halo_swing_mcp/harness.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 234 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state/ only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py::test_cron_prompt_pack_trims_and_uppercases_asset_identity -q -> 1 passed, cron prompt asset identity normalization coverage enforced
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 125 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_reporting.py src/halo_swing_mcp/tools/reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_cron_prompt_pack --input-json '{"asset":" tqqq "}' --no-audit -> passed, asset normalized to TQQQ and idempotency keys use TQQQ
PYTHONPATH=src ./.venv/bin/python -m pytest -> 235 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state/ only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py::test_cron_prompt_pack_rejects_blank_asset_identity tests/test_reporting.py::test_harness_rejects_blank_cron_prompt_asset_with_failure_audit -q -> 2 passed, cron prompt blank asset rejection coverage enforced
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 127 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_reporting.py src/halo_swing_mcp/tools/reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_cron_prompt_pack --input-json '{"asset":"   "}' --no-audit -> exited nonzero as expected with asset must be a nonempty string
PYTHONPATH=src ./.venv/bin/python -m pytest -> 237 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state/ only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py::test_cron_prompt_pack_trims_timeframe_identity tests/test_reporting.py::test_cron_prompt_pack_rejects_invalid_timeframe_identity tests/test_reporting.py::test_harness_rejects_blank_cron_prompt_timeframe_with_failure_audit -q -> 5 passed, cron prompt timeframe identity normalization coverage enforced
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 132 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_reporting.py src/halo_swing_mcp/tools/reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_cron_prompt_pack --input-json '{"asset":"TQQQ","timeframe":" swing_3d_10d "}' --no-audit -> passed, timeframe normalized to swing_3d_10d
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_cron_prompt_pack --input-json '{"asset":"TQQQ","timeframe":"   "}' --no-audit -> exited nonzero as expected with timeframe must be a nonempty string
PYTHONPATH=src ./.venv/bin/python -m pytest -> 242 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state/ only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py::test_cron_prompt_pack_rejects_non_bool_include_position_review tests/test_reporting.py::test_harness_rejects_non_bool_include_position_review_with_failure_audit -q -> 6 passed, cron prompt include_position_review strict boolean coverage enforced
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 138 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_reporting.py src/halo_swing_mcp/tools/reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_cron_prompt_pack --input-json '{"asset":"TQQQ","include_position_review":false}' --no-audit -> passed, valid false option omits position_review with guard status ok
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_cron_prompt_pack --input-json '{"asset":"TQQQ","include_position_review":"false"}' --no-audit -> exited nonzero as expected with include_position_review must be a boolean
PYTHONPATH=src ./.venv/bin/python -m pytest -> 248 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state/ only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py::test_latest_signal_report_rejects_non_bool_include_chart tests/test_reporting.py::test_harness_rejects_non_bool_include_chart_with_failure_audit -q -> 6 passed, latest report include_chart strict boolean coverage enforced
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 144 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_reporting.py src/halo_swing_mcp/tools/reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_latest_signal_report --input-json '{"asset":"TQQQ","include_chart":true,"chart_output_dir":"/private/tmp/halo_swing_include_chart_bool_smoke"}' --no-audit -> passed, chart_code_guard ok
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_latest_signal_report --input-json '{"asset":"TQQQ","include_chart":"false","chart_output_dir":"/private/tmp/halo_swing_include_chart_string_false"}' --no-audit -> exited nonzero as expected with include_chart must be a boolean
PYTHONPATH=src ./.venv/bin/python -m pytest -> 254 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state/ only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py::test_latest_signal_report_trims_and_lowercases_chart_timeframe tests/test_reporting.py::test_latest_signal_report_rejects_invalid_chart_timeframe tests/test_reporting.py::test_harness_rejects_blank_chart_timeframe_with_failure_audit -q -> 5 passed, latest report chart_timeframe normalization coverage enforced
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 149 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_reporting.py src/halo_swing_mcp/tools/reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_latest_signal_report --input-json '{"asset":"TQQQ","include_chart":true,"chart_timeframe":" 1D ","chart_output_dir":"/private/tmp/halo_swing_chart_timeframe_normalized"}' --no-audit -> passed, chart_timeframe normalized and chart_code_guard ok
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_latest_signal_report --input-json '{"asset":"TQQQ","include_chart":true,"chart_timeframe":"   ","chart_output_dir":"/private/tmp/halo_swing_chart_timeframe_blank"}' --no-audit -> exited nonzero as expected with chart_timeframe must be a nonempty string
PYTHONPATH=src ./.venv/bin/python -m pytest -> 259 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state/ only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py::test_latest_signal_report_trims_and_uppercases_asset_identity tests/test_reporting.py::test_latest_signal_report_rejects_invalid_asset_identity tests/test_reporting.py::test_latest_signal_report_trims_timeframe_identity tests/test_reporting.py::test_latest_signal_report_rejects_invalid_timeframe_identity tests/test_reporting.py::test_harness_rejects_blank_latest_report_asset_with_failure_audit tests/test_reporting.py::test_harness_rejects_blank_latest_report_timeframe_with_failure_audit -q -> 10 passed, latest report asset/timeframe normalization coverage enforced
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 159 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_reporting.py src/halo_swing_mcp/tools/reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_latest_signal_report --input-json '{"asset":" tqqq ","timeframe":" swing_3d_10d "}' --no-audit -> passed, asset normalized to TQQQ and timeframe normalized to swing_3d_10d
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_latest_signal_report --input-json '{"asset":"   "}' --no-audit -> exited nonzero as expected with asset must be a nonempty string
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_latest_signal_report --input-json '{"asset":"TQQQ","timeframe":"   "}' --no-audit -> exited nonzero as expected with timeframe must be a nonempty string
PYTHONPATH=src ./.venv/bin/python -m pytest -> 269 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state/ only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py::test_position_review_report_trims_and_uppercases_asset_identity tests/test_reporting.py::test_position_review_report_rejects_invalid_asset_identity tests/test_reporting.py::test_harness_rejects_blank_position_review_asset_with_failure_audit -q -> 5 passed, position review asset normalization coverage enforced
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 164 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_reporting.py src/halo_swing_mcp/tools/reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_position_review_report --input-json '{"asset":" tqqq ","entry_price":100,"current_price":114,"size":3}' --no-audit -> passed, asset normalized to TQQQ and position_review_guard ok
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_position_review_report --input-json '{"asset":"   ","entry_price":100,"current_price":114,"size":3}' --no-audit -> exited nonzero as expected with asset must be a nonempty string
PYTHONPATH=src ./.venv/bin/python -m pytest -> 274 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state/ only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py::test_scoring_tools_normalize_asset_and_timeframe_identity tests/test_mvp_tools.py::test_scoring_tools_reject_invalid_asset_identity tests/test_mvp_tools.py::test_scoring_tools_reject_invalid_timeframe_identity tests/test_mvp_tools.py::test_harness_rejects_blank_scoring_asset_with_failure_audit -q -> 8 passed, scoring tool identity normalization coverage enforced
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py -q -> 33 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_mvp_tools.py src/halo_swing_mcp/tools/scoring.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness score_leverage_swing --input-json '{"asset":" tqqq ","timeframe":" swing_3d_10d "}' --no-audit -> passed, asset normalized to TQQQ and timeframe normalized to swing_3d_10d
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_trade_guide --input-json '{"asset":" qld ","timeframe":" swing_3d_10d "}' --no-audit -> passed, asset normalized to QLD and trade_guide_guard ok
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness evaluate_position --input-json '{"asset":" tqqq ","entry_price":100,"current_price":114,"size":3}' --no-audit -> passed, asset normalized to TQQQ and position_management_guard ok
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_trade_guide --input-json '{"asset":"TQQQ","timeframe":"   "}' --no-audit -> exited nonzero as expected with timeframe must be a nonempty string
PYTHONPATH=src ./.venv/bin/python -m pytest -> 282 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state/ only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py::test_market_indicator_and_chart_tools_normalize_symbol_timeframe_identity tests/test_mvp_tools.py::test_market_indicator_and_chart_tools_reject_invalid_symbol_identity tests/test_mvp_tools.py::test_indicator_and_chart_tools_reject_invalid_timeframe_identity tests/test_mvp_tools.py::test_harness_rejects_blank_indicator_symbol_with_failure_audit -q -> 8 passed, market/indicator/chart identity normalization coverage enforced
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py -q -> 41 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_mvp_tools.py src/halo_swing_mcp/tools/market.py src/halo_swing_mcp/indicators.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_market_snapshot --input-json '{"symbols":[" qqq "," tqqq "]}' --no-audit -> passed, symbols normalized to QQQ/TQQQ and market_snapshot_guard ok
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness calculate_indicators --input-json '{"symbol":" tqqq ","timeframe":" 1D "}' --no-audit -> passed, symbol normalized to TQQQ and timeframe normalized to 1d
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness render_chart --input-json '{"symbol":" qqq ","timeframe":" 1D ","output_dir":"/private/tmp/halo_swing_market_identity_chart"}' --no-audit -> passed, wrote normalized QQQ_1d.png with chart_artifact_guard ok
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness calculate_indicators --input-json '{"symbol":"   "}' --no-audit -> exited nonzero as expected with symbol must be a nonempty string
PYTHONPATH=src ./.venv/bin/python -m pytest -> 290 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state/ only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py::test_event_and_news_tools_normalize_public_identity tests/test_mvp_tools.py::test_event_calendar_rejects_invalid_days_identity tests/test_mvp_tools.py::test_news_bundle_rejects_invalid_topic_identity tests/test_mvp_tools.py::test_harness_rejects_blank_news_topic_with_failure_audit -q -> 11 passed, event/news input normalization coverage enforced
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py -q -> 52 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_mvp_tools.py src/halo_swing_mcp/tools/market.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_event_calendar --input-json '{"days":14}' --no-audit -> passed, event_policy_guard ok
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_news_bundle --input-json '{"topic":" ALL "}' --no-audit -> passed, topic normalized to all and news_source_policy_guard ok
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_event_calendar --input-json '{"days":0}' --no-audit -> exited nonzero as expected with days must be a positive integer
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_news_bundle --input-json '{"topic":"   "}' --no-audit -> exited nonzero as expected with topic must be a nonempty string
PYTHONPATH=src ./.venv/bin/python -m pytest -> 301 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed
git status --short --ignored state -> ignored local state/ only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py::test_label_signal_outcome_normalizes_public_inputs tests/test_mvp_tools.py::test_label_signal_outcome_rejects_invalid_public_inputs tests/test_mvp_tools.py::test_evaluate_recorded_score_performance_rejects_invalid_days tests/test_mvp_tools.py::test_harness_rejects_invalid_label_price_path_with_failure_audit -q -> 4 passed, recording label input normalization coverage enforced
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py -q -> 56 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/recording.py tests/test_mvp_tools.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness label_signal_outcome --input-json '{"signal_id":" sig_fixture_20260511_tqqq ","price_path":[500,510],"time_barrier_days":2,"stop_loss_pct":0.05,"take_profit_pct":0.1}' --no-audit -> passed, signal_id normalized to sig_fixture_20260511_tqqq and signal_label_outcome.v1 returned
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness label_signal_outcome --input-json '{"price_path":["not-a-price"]}' --no-audit -> exited nonzero as expected with price_path must be a list of positive finite numbers
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness evaluate_score_performance --input-json '{"days":0}' --no-audit -> exited nonzero as expected with days must be a positive integer
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness evaluate_score_performance --input-json '{"days":90}' --no-audit -> passed, evaluation_window requested_days 90
PYTHONPATH=src ./.venv/bin/python -m pytest -> 305 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py::test_record_signal_normalizes_public_signal_identity tests/test_mvp_tools.py::test_record_signal_rejects_invalid_public_signal_identity tests/test_mvp_tools.py::test_harness_rejects_invalid_record_signal_with_failure_audit -q -> 3 passed, record signal input normalization coverage enforced
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py -q -> 59 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/recording.py tests/test_mvp_tools.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness record_signal --input-json '{"signal":{"signal_id":"   "}}' --no-audit -> exited nonzero as expected with signal.signal_id must be a nonempty string
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness record_signal --input-json '{"ledger_path":"/private/tmp/halo_swing_record_signal_identity_ledger.jsonl"}' --no-audit -> passed, run_journal.v1 returned for default fixture path
PYTHONPATH=src ./.venv/bin/python -m pytest -> 308 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py::test_evaluate_position_returns_management_action tests/test_mvp_tools.py::test_evaluate_position_rejects_invalid_numeric_inputs tests/test_mvp_tools.py::test_harness_rejects_invalid_position_numeric_input_with_failure_audit -q -> 3 passed, position numeric input normalization coverage enforced
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py -q -> 61 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/scoring.py tests/test_mvp_tools.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness evaluate_position --input-json '{"asset":" tqqq ","entry_price":100,"current_price":114,"size":3}' --no-audit -> passed, asset normalized to TQQQ, size normalized to 3.0, and position_management_guard ok
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness evaluate_position --input-json '{"asset":"TQQQ","entry_price":100,"current_price":0}' --no-audit -> exited nonzero as expected with current_price must be a positive finite number
PYTHONPATH=src ./.venv/bin/python -m pytest -> 310 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_audit.py::test_audit_log_normalizes_public_limit_and_filters tests/test_audit.py::test_audit_log_rejects_invalid_public_inputs tests/test_audit.py::test_harness_rejects_invalid_audit_log_limit_with_failure_audit -q -> 3 passed, audit log input normalization coverage enforced
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_audit.py -q -> 17 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/audit_tools.py tests/test_audit.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_audit_log --input-json '{"audit_log_path":"/private/tmp/halo_swing_audit_input_normalization.jsonl","limit":0}' --audit-log-path /private/tmp/halo_swing_audit_input_normalization.jsonl -> exited nonzero as expected with limit must be a positive integer
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_audit_log --input-json '{"audit_log_path":"/private/tmp/halo_swing_audit_input_normalization.jsonl","limit":5,"action":" tool_call "}' --no-audit -> passed, action normalized to tool_call and audit_log.v1 returned
PYTHONPATH=src ./.venv/bin/python -m pytest -> 313 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_runtime_guard.py::test_runtime_status_rejects_invalid_public_inputs tests/test_runtime_guard.py::test_harness_rejects_invalid_runtime_status_input_with_failure_audit tests/test_runtime_guard.py::test_runtime_checkpoint_normalizes_public_run_id tests/test_runtime_guard.py::test_runtime_checkpoint_rejects_invalid_public_inputs -q -> 4 passed, runtime guard input normalization coverage enforced
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_runtime_guard.py -q -> 12 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/runtime.py tests/test_runtime_guard.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_runtime_status --input-json '{"audit_log_path":"/private/tmp/halo_swing_runtime_input_normalization_audit.jsonl","ledger_path":"/private/tmp/halo_swing_runtime_input_normalization_ledger.jsonl","apply_retention":"false"}' --audit-log-path /private/tmp/halo_swing_runtime_input_normalization_audit.jsonl -> exited nonzero as expected with apply_retention must be a boolean
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_runtime_status --input-json '{"audit_log_path":"/private/tmp/halo_swing_runtime_input_normalization_audit.jsonl","ledger_path":"/private/tmp/halo_swing_runtime_input_normalization_ledger.jsonl","apply_retention":false,"max_records":10,"max_bytes":10000,"failure_window":5,"failure_threshold":2}' --no-audit -> passed, explicit retention policy and watchdog bounds returned
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness record_runtime_checkpoint --input-json '{"checkpoint_path":"/private/tmp/halo_swing_runtime_input_normalization_checkpoints.jsonl","audit_log_path":"/private/tmp/halo_swing_runtime_input_normalization_audit.jsonl","ledger_path":"/private/tmp/halo_swing_runtime_input_normalization_ledger.jsonl","run_id":" run_runtime ","include_readiness":false}' --no-audit -> passed, run_id normalized to run_runtime and readiness omitted
PYTHONPATH=src ./.venv/bin/python -m pytest -> 317 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only

Choose the next gate:

```text
Option 1: Hermes/Telegram local integration setup.
Option 2: Stage G Binance testnet read-only smoke prerequisites.
Option 3: MIGRATION_GO / REPOSITORY_GO approval or policy revision.
Option 4: Live data source decisions for macro/news inputs.
Option 5: Continue offline hardening for report variants or larger fixture coverage.
```

Stage G live submission remains blocked by default. The next executable broker
check is Binance testnet read-only smoke after encrypted testnet credentials
and manual passphrase availability are confirmed; live submission still requires
explicit future approval.

## 3.348 Integration Readiness Input Normalization Verification - 2026-05-11

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_readiness.py::test_integration_readiness_normalizes_public_path_inputs tests/test_readiness.py::test_integration_readiness_rejects_invalid_public_inputs tests/test_readiness.py::test_harness_rejects_invalid_readiness_input_with_failure_audit -q -> 3 passed, readiness public input normalization coverage enforced
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_readiness.py -q -> 16 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/readiness.py tests/test_readiness.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --input-json '{"migration_go_approved":"false"}' --audit-log-path /private/tmp/halo_swing_readiness_input_normalization_audit.jsonl -> exited nonzero as expected with migration_go_approved must be a boolean
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --input-json '{"migration_go_approved":false,"repository_go_approved":false,"market_data_source_configured":false,"macro_source_configured":false,"news_source_configured":false}' --no-audit -> passed, status blocked with explicit false readiness evidence and expected next_actions
PYTHONPATH=src ./.venv/bin/python -m pytest -> 320 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 3.349 BTC Risk Settings Input Normalization Verification - 2026-05-11

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_binance_btc.py::test_update_btc_risk_settings_normalizes_public_inputs tests/test_binance_btc.py::test_update_btc_risk_settings_rejects_invalid_public_inputs tests/test_binance_btc.py::test_reset_btc_daily_risk_state_normalizes_public_inputs tests/test_binance_btc.py::test_reset_btc_daily_risk_state_rejects_invalid_public_inputs tests/test_binance_btc.py::test_harness_rejects_invalid_risk_settings_input_with_failure_audit -q -> 5 passed, BTC risk/state input normalization coverage enforced
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_binance_btc.py -q -> 26 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/risk_settings.py tests/test_binance_btc.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness update_btc_risk_settings --input-json '{"settings_path":"/private/tmp/halo_swing_risk_input_normalization_settings.json","emergency_kill_switch_enabled":"false"}' --audit-log-path /private/tmp/halo_swing_risk_input_normalization_audit.jsonl -> exited nonzero as expected with emergency_kill_switch_enabled must be a boolean
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness update_btc_risk_settings --input-json '{"settings_path":" /private/tmp/halo_swing_risk_input_normalization_settings.json ","max_notional_usd_per_order":150,"max_daily_order_count":4,"max_daily_loss_usd":75,"coinm_contract_size_usd":100,"emergency_kill_switch_enabled":false}' --no-audit -> passed, settings_path trimmed and numeric fields normalized
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness reset_btc_daily_risk_state --input-json '{"state_path":" /private/tmp/halo_swing_risk_input_normalization_state.json ","daily_realized_loss_usd":12,"daily_order_count":2}' --no-audit -> passed, state_path trimmed and daily_realized_loss_usd normalized to 12.0
PYTHONPATH=src ./.venv/bin/python -m pytest -> 325 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 3.350 BTC Order Input Normalization Verification - 2026-05-11

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_binance_btc.py::test_preview_btc_order_normalizes_public_order_inputs tests/test_binance_btc.py::test_preview_btc_order_rejects_invalid_public_order_inputs tests/test_binance_btc.py::test_harness_rejects_invalid_btc_order_input_with_failure_audit -q -> 3 passed, BTC order public input normalization coverage enforced
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_binance_btc.py -q -> 29 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/binance_btc.py tests/test_binance_btc.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness preview_btc_order --input-json '{"side":"BUY","quantity":"1","reduce_only":"false"}' --audit-log-path /private/tmp/halo_swing_btc_order_input_normalization_audit.jsonl -> exited nonzero as expected with reduce_only must be a boolean
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness preview_btc_order --input-json '{"side":" buy ","order_type":" limit ","quantity":" 1 ","price":" 90000 ","time_in_force":" gtc ","position_side":" both ","reduce_only":false,"client_order_id":" order-1 "}' --no-audit -> passed, side/order_type/position_side/time_in_force uppercased and string fields trimmed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness execute_btc_order --input-json '{"side":"BUY","quantity":"1","reduce_only":"false"}' --audit-log-path /private/tmp/halo_swing_btc_order_execute_input_normalization_audit.jsonl -> exited nonzero as expected with reduce_only must be a boolean
PYTHONPATH=src ./.venv/bin/python -m pytest -> 328 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 3.351 BTC Portfolio Snapshot Input Normalization Verification - 2026-05-11

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_binance_btc.py::test_normalize_binance_coinm_account_snapshot_is_offline_read_only tests/test_binance_btc.py::test_normalize_binance_coinm_account_snapshot_normalizes_public_inputs tests/test_binance_btc.py::test_normalize_binance_coinm_account_snapshot_rejects_invalid_public_inputs tests/test_binance_btc.py::test_harness_rejects_invalid_portfolio_snapshot_input_with_failure_audit -q -> 4 passed, BTC portfolio snapshot input normalization coverage enforced
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_binance_btc.py -q -> 32 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/binance_btc.py tests/test_binance_btc.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness normalize_binance_coinm_account_snapshot --input-json '{"balance":{"asset":"BTC"}}' --audit-log-path /private/tmp/halo_swing_portfolio_snapshot_input_normalization_audit.jsonl -> exited nonzero as expected with balance must be a list of objects
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness normalize_binance_coinm_account_snapshot --input-json '{"balance":[{"asset":" BTC ","balance":" 0.25000000 ","availableBalance":" 0.20000000 ","crossWalletBalance":" 0.24000000 ","crossUnPnl":" 0.01000000 "}],"positions":[{"symbol":"BTCUSD_PERP","positionAmt":" 3 ","entryPrice":" 90000 ","markPrice":" 92000 ","unRealizedProfit":" 0.0065 ","liquidationPrice":" 65000 ","leverage":" 2 ","marginType":" cross ","positionSide":" BOTH "}],"as_of":" 2026-05-10T00:00:00Z ","coinm_contract_size_usd":100}' --no-audit -> passed, snapshot rows trimmed and decimal fields normalized with portfolio_sync_contract read_only/no-network/no-order
PYTHONPATH=src ./.venv/bin/python -m pytest -> 331 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 3.352 Binance Credential Input Normalization Verification - 2026-05-11

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_binance_btc.py::test_save_binance_credentials_normalizes_public_inputs tests/test_binance_btc.py::test_save_binance_credentials_rejects_invalid_public_inputs tests/test_binance_btc.py::test_harness_rejects_invalid_save_credentials_input_with_failure_audit -q -> 3 passed, Binance credential input normalization coverage enforced
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_binance_btc.py tests/test_audit.py -q -> 52 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/secret_store.py tests/test_binance_btc.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness save_binance_credentials --input-json '{"api_key":"   ","api_secret":"super-secret","passphrase":"local-passphrase","credentials_path":"/private/tmp/halo_swing_credentials_input_normalization.enc.json"}' --audit-log-path /private/tmp/halo_swing_credentials_input_normalization_audit.jsonl -> exited nonzero as expected with api_key must be a nonempty string
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness save_binance_credentials --input-json '{"api_key":" abcde12345key ","api_secret":" super-secret ","passphrase":"local-passphrase","credentials_path":" /private/tmp/halo_swing_credentials_input_normalization.enc.json "}' --no-audit -> passed, credentials_path trimmed and api_key_hint derived from normalized api_key
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_binance_credentials_status --input-json '{"credentials_path":" /private/tmp/halo_swing_credentials_input_normalization.enc.json "}' --no-audit -> passed, configured true with safe metadata only
PYTHONPATH=src ./.venv/bin/python -m pytest -> 334 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 3.353 Trading Admin HTTP Input Normalization Verification - 2026-05-11

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_binance_btc.py::test_trading_admin_risk_settings_endpoint_normalizes_form_inputs tests/test_binance_btc.py::test_trading_admin_risk_settings_endpoint_rejects_invalid_inputs tests/test_binance_btc.py::test_trading_admin_credentials_endpoint_rejects_invalid_input_without_write tests/test_binance_btc.py::test_trading_admin_order_preview_endpoint_rejects_invalid_text_inputs tests/test_binance_btc.py::test_trading_admin_account_snapshot_endpoint_rejects_invalid_passphrase_type -q -> 5 passed, trading admin HTTP payload normalization coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/trading_admin_web.py tests/test_binance_btc.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_binance_btc.py -q -> 40 passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_binance_btc.py tests/test_audit.py -q -> 57 passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 339 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 3.354 Audit Web Query Input Normalization Verification - 2026-05-11

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_audit.py::test_audit_web_events_payload_normalizes_query_inputs tests/test_audit.py::test_audit_web_events_payload_rejects_invalid_query_inputs tests/test_audit.py::test_audit_web_events_endpoint_returns_bad_request_for_invalid_query -q -> 3 passed, audit web query input normalization coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/audit_web.py tests/test_audit.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_audit.py -q -> 20 passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 342 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 3.355 Audit Web Local Bind Guard Verification - 2026-05-11

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_audit.py::test_audit_web_main_rejects_non_localhost_bind -q -> 1 passed, audit web local bind guard coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/audit_web.py tests/test_audit.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_audit.py -q -> 21 passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 343 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 3.356 Audit Tool Path Input Normalization Verification - 2026-05-11

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_audit.py::test_audit_log_normalizes_public_limit_and_filters tests/test_audit.py::test_audit_log_rejects_invalid_public_inputs tests/test_audit.py::test_harness_rejects_invalid_audit_log_path_with_failure_audit -q -> 3 passed, audit tool path input normalization coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/audit_tools.py tests/test_audit.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_audit.py -q -> 22 passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 344 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 3.357 Runtime Path Input Normalization Verification - 2026-05-11

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_runtime_guard.py::test_runtime_status_applies_retention_and_degraded_mode tests/test_runtime_guard.py::test_runtime_status_rejects_invalid_public_inputs tests/test_runtime_guard.py::test_harness_rejects_invalid_runtime_path_input_with_failure_audit tests/test_runtime_guard.py::test_runtime_checkpoint_normalizes_public_run_id tests/test_runtime_guard.py::test_runtime_checkpoint_rejects_invalid_public_inputs -q -> 5 passed, runtime path input normalization coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/runtime.py tests/test_runtime_guard.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_runtime_guard.py -q -> 13 passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 345 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 3.358 Signal Ledger Path Input Normalization Verification - 2026-05-11

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py::test_record_label_and_evaluate_ledger tests/test_mvp_tools.py::test_record_signal_rejects_invalid_ledger_path tests/test_mvp_tools.py::test_label_signal_outcome_rejects_invalid_public_inputs tests/test_mvp_tools.py::test_evaluate_recorded_score_performance_rejects_invalid_ledger_path tests/test_mvp_tools.py::test_harness_rejects_invalid_record_signal_ledger_path_with_failure_audit -q -> 5 passed, signal ledger path input normalization coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/recording.py tests/test_mvp_tools.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py -q -> 64 passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 348 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 3.359 Chart Output Path Input Normalization Verification - 2026-05-11

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py::test_market_indicator_and_chart_tools_normalize_symbol_timeframe_identity tests/test_mvp_tools.py::test_render_chart_rejects_invalid_output_dir tests/test_mvp_tools.py::test_harness_rejects_invalid_render_chart_output_dir_with_failure_audit tests/test_reporting.py::test_latest_signal_report_trims_and_lowercases_chart_timeframe tests/test_reporting.py::test_latest_signal_report_rejects_invalid_chart_output_dir tests/test_reporting.py::test_harness_rejects_blank_chart_output_dir_with_failure_audit -q -> 12 passed, chart output path input normalization coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/market.py src/halo_swing_mcp/tools/reporting.py tests/test_mvp_tools.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py -q -> 69 passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 169 passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 358 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 3.360 Document Evidence Input Normalization Verification - 2026-05-11

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py::test_document_summary_input_creates_guarded_evidence_card tests/test_mvp_tools.py::test_document_summary_input_rejects_invalid_public_inputs tests/test_mvp_tools.py::test_harness_rejects_invalid_document_summary_input_with_failure_audit tests/test_reporting.py::test_latest_signal_report_rejects_pdf_artifact_ref_with_control_character tests/test_reporting.py::test_latest_signal_report_rejects_document_asset_scope_with_control_character -q -> 14 passed, document evidence input normalization coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/market.py tests/test_mvp_tools.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py::test_latest_signal_report_rejects_document_modality_with_surrounding_whitespace tests/test_reporting.py::test_latest_signal_report_rejects_invalidating_condition_with_surrounding_whitespace tests/test_reporting.py::test_latest_signal_report_rejects_document_observed_at_with_control_character -q -> 3 passed, drifted report-side guard coverage preserved
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py -q -> 80 passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 169 passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 369 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 3.361 Document Evidence Control Character Input Normalization Verification - 2026-05-11

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py::test_document_summary_input_rejects_invalid_public_inputs tests/test_mvp_tools.py::test_harness_rejects_document_summary_control_character_with_failure_audit tests/test_reporting.py::test_latest_signal_report_rejects_document_summary_with_control_character tests/test_reporting.py::test_latest_signal_report_rejects_pdf_artifact_ref_with_control_character tests/test_reporting.py::test_latest_signal_report_rejects_document_observed_at_with_control_character tests/test_reporting.py::test_latest_signal_report_rejects_document_asset_scope_with_control_character -q -> 19 passed, document evidence control-character input normalization coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/market.py tests/test_mvp_tools.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py -q -> 85 passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 169 passed
PYTHONPATH=src ./.venv/bin/python -m pytest -q -> 374 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 3.362 Report Intent Input Normalization Verification - 2026-05-11

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py::test_latest_signal_report_rejects_unsupported_report_intent_at_boundary tests/test_reporting.py::test_latest_signal_report_trims_and_lowercases_report_intent tests/test_reporting.py::test_latest_signal_report_rejects_invalid_report_intent_identity tests/test_reporting.py::test_latest_signal_report_rejects_report_intent_control_character tests/test_reporting.py::test_harness_rejects_unsupported_report_intent_with_failure_audit tests/test_reporting.py::test_harness_rejects_invalid_report_intent_with_failure_audit tests/test_reporting.py::test_harness_rejects_report_intent_control_character_with_failure_audit -q -> 9 passed, report_intent input normalization coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 176 passed
PYTHONPATH=src ./.venv/bin/python -m pytest -q -> 381 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 3.363 Report Identity Control Character Input Normalization Verification - 2026-05-11

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py::test_latest_signal_report_trims_and_uppercases_asset_identity tests/test_reporting.py::test_latest_signal_report_rejects_invalid_asset_identity tests/test_reporting.py::test_latest_signal_report_rejects_asset_control_character tests/test_reporting.py::test_latest_signal_report_trims_timeframe_identity tests/test_reporting.py::test_latest_signal_report_rejects_invalid_timeframe_identity tests/test_reporting.py::test_latest_signal_report_rejects_timeframe_control_character tests/test_reporting.py::test_latest_signal_report_trims_and_lowercases_chart_timeframe tests/test_reporting.py::test_latest_signal_report_rejects_invalid_chart_timeframe tests/test_reporting.py::test_latest_signal_report_rejects_chart_timeframe_control_character tests/test_reporting.py::test_cron_prompt_pack_trims_and_uppercases_asset_identity tests/test_reporting.py::test_cron_prompt_pack_rejects_blank_asset_identity tests/test_reporting.py::test_cron_prompt_pack_rejects_asset_control_character tests/test_reporting.py::test_cron_prompt_pack_trims_timeframe_identity tests/test_reporting.py::test_cron_prompt_pack_rejects_invalid_timeframe_identity tests/test_reporting.py::test_cron_prompt_pack_rejects_timeframe_control_character tests/test_reporting.py::test_position_review_report_trims_and_uppercases_asset_identity tests/test_reporting.py::test_position_review_report_rejects_invalid_asset_identity tests/test_reporting.py::test_position_review_report_rejects_asset_control_character tests/test_reporting.py::test_harness_rejects_latest_report_asset_control_character_with_failure_audit tests/test_reporting.py::test_harness_rejects_latest_report_timeframe_control_character_with_failure_audit tests/test_reporting.py::test_harness_rejects_cron_prompt_asset_control_character_with_failure_audit tests/test_reporting.py::test_harness_rejects_cron_prompt_timeframe_control_character_with_failure_audit tests/test_reporting.py::test_harness_rejects_position_review_asset_control_character_with_failure_audit tests/test_reporting.py::test_harness_rejects_chart_timeframe_control_character_with_failure_audit -q -> 34 passed, report identity control-character input normalization coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 188 passed
PYTHONPATH=src ./.venv/bin/python -m pytest -q -> 393 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 3.364 Scoring Identity Control Character Input Normalization Verification - 2026-05-11

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py::test_scoring_tools_normalize_asset_and_timeframe_identity tests/test_mvp_tools.py::test_scoring_tools_reject_invalid_asset_identity tests/test_mvp_tools.py::test_scoring_tools_reject_asset_control_character tests/test_mvp_tools.py::test_scoring_tools_reject_invalid_timeframe_identity tests/test_mvp_tools.py::test_scoring_tools_reject_timeframe_control_character tests/test_mvp_tools.py::test_harness_rejects_blank_scoring_asset_with_failure_audit tests/test_mvp_tools.py::test_harness_rejects_scoring_asset_control_character_with_failure_audit tests/test_mvp_tools.py::test_harness_rejects_trade_guide_timeframe_control_character_with_failure_audit -q -> 12 passed, scoring identity control-character input normalization coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/scoring.py tests/test_mvp_tools.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py -q -> 89 passed
PYTHONPATH=src ./.venv/bin/python -m pytest -q -> 397 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 3.365 Market Tool Control Character Input Normalization Verification - 2026-05-11

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py::test_market_indicator_and_chart_tools_normalize_symbol_timeframe_identity tests/test_mvp_tools.py::test_event_and_news_tools_normalize_public_identity tests/test_mvp_tools.py::test_news_bundle_rejects_invalid_topic_identity tests/test_mvp_tools.py::test_news_bundle_rejects_topic_control_character tests/test_mvp_tools.py::test_market_indicator_and_chart_tools_reject_invalid_symbol_identity tests/test_mvp_tools.py::test_market_indicator_and_chart_tools_reject_symbol_control_character tests/test_mvp_tools.py::test_indicator_and_chart_tools_reject_invalid_timeframe_identity tests/test_mvp_tools.py::test_indicator_and_chart_tools_reject_timeframe_control_character tests/test_mvp_tools.py::test_render_chart_rejects_invalid_output_dir tests/test_mvp_tools.py::test_render_chart_rejects_output_dir_control_character tests/test_mvp_tools.py::test_harness_rejects_blank_indicator_symbol_with_failure_audit tests/test_mvp_tools.py::test_harness_rejects_indicator_symbol_control_character_with_failure_audit tests/test_mvp_tools.py::test_harness_rejects_invalid_render_chart_output_dir_with_failure_audit tests/test_mvp_tools.py::test_harness_rejects_render_chart_output_dir_control_character_with_failure_audit tests/test_mvp_tools.py::test_harness_rejects_blank_news_topic_with_failure_audit tests/test_mvp_tools.py::test_harness_rejects_news_topic_control_character_with_failure_audit -q -> 25 passed, market tool control-character input normalization coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/market.py src/halo_swing_mcp/indicators.py tests/test_mvp_tools.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py -q -> 96 passed
PYTHONPATH=src ./.venv/bin/python -m pytest -q -> 404 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 3.366 Report Chart Output Dir Control Character Input Normalization Verification - 2026-05-11

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py::test_latest_signal_report_trims_and_lowercases_chart_timeframe tests/test_reporting.py::test_latest_signal_report_rejects_invalid_chart_output_dir tests/test_reporting.py::test_latest_signal_report_rejects_chart_output_dir_control_character tests/test_reporting.py::test_harness_rejects_blank_chart_output_dir_with_failure_audit tests/test_reporting.py::test_harness_rejects_chart_output_dir_control_character_with_failure_audit -q -> 8 passed, report chart_output_dir control-character input normalization coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 190 passed
PYTHONPATH=src ./.venv/bin/python -m pytest -q -> 406 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 3.367 Audit Read Control Character Input Normalization Verification - 2026-05-11

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_audit.py::test_audit_log_normalizes_public_limit_and_filters tests/test_audit.py::test_audit_log_rejects_invalid_public_inputs tests/test_audit.py::test_audit_log_rejects_control_character_public_inputs tests/test_audit.py::test_harness_rejects_invalid_audit_log_path_with_failure_audit tests/test_audit.py::test_harness_rejects_audit_log_path_control_character_with_failure_audit tests/test_audit.py::test_harness_rejects_audit_log_filter_control_character_with_failure_audit tests/test_audit.py::test_audit_web_events_payload_normalizes_query_inputs tests/test_audit.py::test_audit_web_events_payload_rejects_invalid_query_inputs tests/test_audit.py::test_audit_web_events_payload_rejects_control_character_query_inputs tests/test_audit.py::test_audit_web_events_endpoint_returns_bad_request_for_invalid_query tests/test_audit.py::test_audit_web_events_endpoint_returns_bad_request_for_control_character_query -q -> 11 passed, audit read control-character input normalization coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/audit_tools.py src/halo_swing_mcp/audit_web.py tests/test_audit.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_audit.py -q -> 27 passed
PYTHONPATH=src ./.venv/bin/python -m pytest -q -> 411 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 3.368 Readiness Path Control Character Input Normalization Verification - 2026-05-11

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_readiness.py::test_integration_readiness_normalizes_public_path_inputs tests/test_readiness.py::test_integration_readiness_rejects_invalid_public_inputs tests/test_readiness.py::test_integration_readiness_rejects_path_control_character_inputs tests/test_readiness.py::test_harness_rejects_invalid_readiness_input_with_failure_audit tests/test_readiness.py::test_harness_rejects_readiness_path_control_character_with_failure_audit tests/test_readiness.py::test_harness_returns_integration_readiness -q -> 6 passed, readiness path control-character input normalization coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/readiness.py tests/test_readiness.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_readiness.py -q -> 18 passed
PYTHONPATH=src ./.venv/bin/python -m pytest -q -> 413 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 3.369 BTC Risk Path Control Character Input Normalization Verification - 2026-05-11

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_binance_btc.py::test_update_btc_risk_settings_normalizes_public_inputs tests/test_binance_btc.py::test_update_btc_risk_settings_rejects_invalid_public_inputs tests/test_binance_btc.py::test_btc_risk_tools_reject_path_control_character_inputs tests/test_binance_btc.py::test_reset_btc_daily_risk_state_normalizes_public_inputs tests/test_binance_btc.py::test_reset_btc_daily_risk_state_rejects_invalid_public_inputs tests/test_binance_btc.py::test_harness_rejects_invalid_risk_settings_input_with_failure_audit tests/test_binance_btc.py::test_harness_rejects_risk_settings_path_control_character_with_failure_audit -q -> 7 passed, BTC risk path control-character input normalization coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/risk_settings.py tests/test_binance_btc.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_binance_btc.py -q -> 42 passed
PYTHONPATH=src ./.venv/bin/python -m pytest -q -> 415 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 3.370 Signal Ledger Path Control Character Input Normalization Verification - 2026-05-11

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py::test_record_label_and_evaluate_ledger tests/test_mvp_tools.py::test_record_signal_rejects_invalid_ledger_path tests/test_mvp_tools.py::test_recording_tools_reject_ledger_path_control_character_inputs tests/test_mvp_tools.py::test_label_signal_outcome_rejects_invalid_public_inputs tests/test_mvp_tools.py::test_evaluate_recorded_score_performance_rejects_invalid_ledger_path tests/test_mvp_tools.py::test_harness_rejects_invalid_record_signal_ledger_path_with_failure_audit tests/test_mvp_tools.py::test_harness_rejects_record_signal_ledger_path_control_character_with_failure_audit -q -> 7 passed, signal ledger path control-character input normalization coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/recording.py tests/test_mvp_tools.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py -q -> 98 passed
PYTHONPATH=src ./.venv/bin/python -m pytest -q -> 417 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 3.371 Binance Credential Path Control Character Input Normalization Verification - 2026-05-11

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_binance_btc.py::test_save_binance_credentials_normalizes_public_inputs tests/test_binance_btc.py::test_save_binance_credentials_rejects_invalid_public_inputs tests/test_binance_btc.py::test_binance_credentials_reject_credentials_path_control_character_inputs tests/test_binance_btc.py::test_harness_rejects_invalid_save_credentials_input_with_failure_audit tests/test_binance_btc.py::test_harness_rejects_credentials_path_control_character_with_failure_audit tests/test_binance_btc.py::test_binance_credential_status_exposes_trade_only_policy_without_secrets -q -> 6 passed, Binance credential path control-character input normalization coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/secret_store.py tests/test_binance_btc.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_binance_btc.py -q -> 44 passed
PYTHONPATH=src ./.venv/bin/python -m pytest -q -> 419 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 3.372 BTC Order Text Control Character Input Normalization Verification - 2026-05-11

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_binance_btc.py::test_preview_btc_order_normalizes_public_order_inputs tests/test_binance_btc.py::test_preview_btc_order_rejects_invalid_public_order_inputs tests/test_binance_btc.py::test_btc_order_tools_reject_order_text_control_character_inputs tests/test_binance_btc.py::test_harness_rejects_invalid_btc_order_input_with_failure_audit tests/test_binance_btc.py::test_harness_rejects_btc_order_text_control_character_with_failure_audit tests/test_binance_btc.py::test_execute_btc_order_blocks_without_confirmation -q -> 6 passed, BTC order text control-character input normalization coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/binance_btc.py tests/test_binance_btc.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_binance_btc.py -q -> 46 passed
PYTHONPATH=src ./.venv/bin/python -m pytest -q -> 421 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 3.373 Portfolio Snapshot Text Control Character Input Normalization Verification - 2026-05-11

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_binance_btc.py::test_normalize_binance_coinm_account_snapshot_is_offline_read_only tests/test_binance_btc.py::test_normalize_binance_coinm_account_snapshot_normalizes_public_inputs tests/test_binance_btc.py::test_normalize_binance_coinm_account_snapshot_rejects_invalid_public_inputs tests/test_binance_btc.py::test_normalize_binance_coinm_account_snapshot_rejects_text_control_characters tests/test_binance_btc.py::test_harness_rejects_invalid_portfolio_snapshot_input_with_failure_audit tests/test_binance_btc.py::test_harness_rejects_portfolio_snapshot_text_control_character_with_failure_audit -q -> 6 passed, portfolio snapshot text control-character input normalization coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/binance_btc.py tests/test_binance_btc.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_binance_btc.py -q -> 48 passed
PYTHONPATH=src ./.venv/bin/python -m pytest -q -> 423 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 3.374 Binance Credential Secret Control Character Input Normalization Verification - 2026-05-11

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_binance_btc.py::test_save_binance_credentials_normalizes_public_inputs tests/test_binance_btc.py::test_save_binance_credentials_rejects_invalid_public_inputs tests/test_binance_btc.py::test_binance_credentials_reject_secret_control_character_inputs tests/test_binance_btc.py::test_harness_rejects_invalid_save_credentials_input_with_failure_audit tests/test_binance_btc.py::test_harness_rejects_secret_control_character_with_failure_audit tests/test_binance_btc.py::test_binance_credential_status_exposes_trade_only_policy_without_secrets -q -> 6 passed, Binance credential secret control-character input normalization coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/secret_store.py tests/test_binance_btc.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_binance_btc.py -q -> 50 passed
PYTHONPATH=src ./.venv/bin/python -m pytest -q -> 425 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 3.375 Trading Admin HTTP Control Character Input Normalization Verification - 2026-05-11

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_binance_btc.py::test_trading_admin_risk_settings_endpoint_normalizes_form_inputs tests/test_binance_btc.py::test_trading_admin_risk_settings_endpoint_rejects_invalid_inputs tests/test_binance_btc.py::test_trading_admin_risk_settings_endpoint_rejects_control_characters tests/test_binance_btc.py::test_trading_admin_credentials_endpoint_rejects_invalid_input_without_write tests/test_binance_btc.py::test_trading_admin_credentials_endpoint_rejects_control_characters_without_write tests/test_binance_btc.py::test_trading_admin_order_preview_endpoint_rejects_invalid_text_inputs tests/test_binance_btc.py::test_trading_admin_order_preview_endpoint_rejects_control_characters tests/test_binance_btc.py::test_trading_admin_account_snapshot_endpoint_rejects_invalid_passphrase_type tests/test_binance_btc.py::test_trading_admin_account_snapshot_endpoint_rejects_passphrase_control_character -q -> 9 passed, trading admin HTTP control-character input normalization coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/trading_admin_web.py tests/test_binance_btc.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_binance_btc.py -q -> 54 passed
PYTHONPATH=src ./.venv/bin/python -m pytest -q -> 429 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_3_375_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 3.376 Runtime Control Character Input Normalization Verification - 2026-05-11

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_runtime_guard.py::test_runtime_status_applies_retention_and_degraded_mode tests/test_runtime_guard.py::test_runtime_status_rejects_invalid_public_inputs tests/test_runtime_guard.py::test_runtime_status_rejects_path_control_character_inputs tests/test_runtime_guard.py::test_harness_rejects_invalid_runtime_path_input_with_failure_audit tests/test_runtime_guard.py::test_harness_rejects_runtime_path_control_character_with_failure_audit tests/test_runtime_guard.py::test_runtime_checkpoint_normalizes_public_run_id tests/test_runtime_guard.py::test_runtime_checkpoint_rejects_invalid_public_inputs tests/test_runtime_guard.py::test_runtime_checkpoint_rejects_control_character_inputs tests/test_runtime_guard.py::test_harness_rejects_runtime_checkpoint_control_character_with_failure_audit -q -> 9 passed, runtime control-character input normalization coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/runtime.py tests/test_runtime_guard.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_runtime_guard.py -q -> 17 passed
PYTHONPATH=src ./.venv/bin/python -m pytest -q -> 433 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_3_376_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 3.377 Signal Identity Control Character Input Normalization Verification - 2026-05-11

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py::test_record_signal_normalizes_public_signal_identity tests/test_mvp_tools.py::test_record_signal_rejects_invalid_public_signal_identity tests/test_mvp_tools.py::test_record_signal_rejects_signal_identity_control_character_inputs tests/test_mvp_tools.py::test_label_signal_outcome_normalizes_public_inputs tests/test_mvp_tools.py::test_label_signal_outcome_rejects_invalid_public_inputs tests/test_mvp_tools.py::test_label_signal_outcome_rejects_identity_control_character_inputs tests/test_mvp_tools.py::test_harness_rejects_invalid_record_signal_with_failure_audit tests/test_mvp_tools.py::test_harness_rejects_record_signal_identity_control_character_with_failure_audit tests/test_mvp_tools.py::test_harness_rejects_label_signal_identity_control_character_with_failure_audit -q -> 9 passed, signal identity control-character input normalization coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/recording.py tests/test_mvp_tools.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py -q -> 102 passed
PYTHONPATH=src ./.venv/bin/python -m pytest -q -> 437 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_3_377_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 3.378 Market Symbol List Container Input Contract Verification - 2026-05-11

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py::test_market_indicator_and_chart_tools_normalize_symbol_timeframe_identity tests/test_mvp_tools.py::test_market_indicator_and_chart_tools_reject_invalid_symbol_identity tests/test_mvp_tools.py::test_market_snapshot_rejects_invalid_symbols_container tests/test_mvp_tools.py::test_market_indicator_and_chart_tools_reject_symbol_control_character tests/test_mvp_tools.py::test_harness_rejects_invalid_market_symbols_container_with_failure_audit tests/test_mvp_tools.py::test_harness_rejects_blank_indicator_symbol_with_failure_audit tests/test_mvp_tools.py::test_harness_rejects_indicator_symbol_control_character_with_failure_audit -q -> 12 passed, market snapshot symbols container contract coverage enforced
./.venv/bin/ruff check tests/test_mvp_tools.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py -q -> 107 passed
./.venv/bin/ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -q -> 442 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_3_378_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 3.379 Event Calendar Days Failure Audit Verification - 2026-05-11

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py::test_event_and_news_tools_normalize_public_identity tests/test_mvp_tools.py::test_event_calendar_rejects_invalid_days_identity tests/test_mvp_tools.py::test_harness_rejects_invalid_event_calendar_days_with_failure_audit tests/test_mvp_tools.py::test_harness_rejects_blank_news_topic_with_failure_audit tests/test_mvp_tools.py::test_harness_rejects_news_topic_control_character_with_failure_audit -q -> 10 passed, event calendar invalid days failure-audit coverage enforced
./.venv/bin/ruff check tests/test_mvp_tools.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py -q -> 108 passed
./.venv/bin/ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -q -> 443 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_3_379_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 3.380 Evaluate Score Performance Days Failure Audit Verification - 2026-05-11

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py::test_evaluate_recorded_score_performance_rejects_invalid_days tests/test_mvp_tools.py::test_score_performance_includes_attribution_and_ablation tests/test_mvp_tools.py::test_harness_rejects_invalid_score_performance_days_with_failure_audit -q -> 3 passed, evaluate_score_performance invalid days failure-audit coverage enforced
./.venv/bin/ruff check tests/test_mvp_tools.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py -q -> 109 passed
./.venv/bin/ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -q -> 444 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_3_380_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 3.381 Evaluate Score Performance Ledger Path Failure Audit Verification - 2026-05-11

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py::test_evaluate_recorded_score_performance_rejects_invalid_days tests/test_mvp_tools.py::test_evaluate_recorded_score_performance_rejects_invalid_ledger_path tests/test_mvp_tools.py::test_harness_rejects_invalid_score_performance_days_with_failure_audit tests/test_mvp_tools.py::test_harness_rejects_invalid_score_performance_ledger_path_with_failure_audit -q -> 4 passed, evaluate_score_performance invalid ledger_path failure-audit coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_mvp_tools.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py -q -> 110 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -q -> 445 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_3_381_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 3.382 Label Signal Ledger Path Failure Audit Verification - 2026-05-11

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py::test_label_signal_outcome_rejects_invalid_public_inputs tests/test_mvp_tools.py::test_harness_rejects_invalid_record_signal_ledger_path_with_failure_audit tests/test_mvp_tools.py::test_harness_rejects_invalid_label_signal_ledger_path_with_failure_audit tests/test_mvp_tools.py::test_harness_rejects_label_signal_identity_control_character_with_failure_audit -q -> 4 passed, label_signal_outcome invalid ledger_path failure-audit coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_mvp_tools.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py -q -> 111 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -q -> 446 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_3_382_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 3.383 Label Signal Ledger Path Control Character Failure Audit Verification - 2026-05-11

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py::test_recording_tools_reject_ledger_path_control_character_inputs tests/test_mvp_tools.py::test_harness_rejects_record_signal_ledger_path_control_character_with_failure_audit tests/test_mvp_tools.py::test_harness_rejects_invalid_label_signal_ledger_path_with_failure_audit tests/test_mvp_tools.py::test_harness_rejects_label_signal_ledger_path_control_character_with_failure_audit -q -> 4 passed, label_signal_outcome control-character ledger_path failure-audit coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_mvp_tools.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py -q -> 112 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -q -> 447 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_3_383_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 3.384 Evaluate Score Performance Ledger Path Control Character Failure Audit Verification - 2026-05-11

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py::test_recording_tools_reject_ledger_path_control_character_inputs tests/test_mvp_tools.py::test_harness_rejects_invalid_score_performance_ledger_path_with_failure_audit tests/test_mvp_tools.py::test_harness_rejects_score_performance_ledger_path_control_character_with_failure_audit tests/test_mvp_tools.py::test_harness_rejects_invalid_score_performance_days_with_failure_audit -q -> 4 passed, evaluate_score_performance control-character ledger_path failure-audit coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_mvp_tools.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py -q -> 113 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -q -> 448 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_3_384_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 3.385 Label Signal Event Boolean Failure Audit Verification - 2026-05-11

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py::test_label_signal_outcome_rejects_invalid_public_inputs tests/test_mvp_tools.py::test_label_signal_outcome_supports_no_data_and_event_invalidation tests/test_mvp_tools.py::test_harness_rejects_invalid_label_event_boolean_with_failure_audit tests/test_mvp_tools.py::test_harness_rejects_invalid_label_price_path_with_failure_audit -q -> 4 passed, label_signal_outcome invalidated_by_event failure-audit coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_mvp_tools.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py -q -> 114 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -q -> 449 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_3_385_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 3.386 Label Signal Invalidating Event ID Control Character Failure Audit Verification - 2026-05-11

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py::test_label_signal_outcome_rejects_identity_control_character_inputs tests/test_mvp_tools.py::test_harness_rejects_label_signal_identity_control_character_with_failure_audit tests/test_mvp_tools.py::test_harness_rejects_label_invalidating_event_id_control_character_with_failure_audit tests/test_mvp_tools.py::test_harness_rejects_invalid_label_event_boolean_with_failure_audit -q -> 4 passed, label_signal_outcome invalidating_event_id control-character failure-audit coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_mvp_tools.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py -q -> 115 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -q -> 450 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_3_386_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 3.387 Label Signal Stop Loss Failure Audit Verification - 2026-05-11

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py::test_label_signal_outcome_rejects_invalid_public_inputs tests/test_mvp_tools.py::test_harness_rejects_invalid_label_price_path_with_failure_audit tests/test_mvp_tools.py::test_harness_rejects_invalid_label_stop_loss_with_failure_audit tests/test_mvp_tools.py::test_label_signal_outcome_metrics_respect_time_barrier -q -> 4 passed, label_signal_outcome stop_loss_pct failure-audit coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_mvp_tools.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py -q -> 116 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -q -> 451 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_3_387_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 3.388 Label Signal Take Profit Failure Audit Verification - 2026-05-11

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py::test_label_signal_outcome_rejects_invalid_public_inputs tests/test_mvp_tools.py::test_harness_rejects_invalid_label_stop_loss_with_failure_audit tests/test_mvp_tools.py::test_harness_rejects_invalid_label_take_profit_with_failure_audit tests/test_mvp_tools.py::test_label_signal_outcome_metrics_respect_time_barrier -q -> 4 passed, label_signal_outcome take_profit_pct failure-audit coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_mvp_tools.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py -q -> 117 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -q -> 452 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_3_388_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 3.389 Label Signal Time Barrier Failure Audit Verification - 2026-05-11

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py::test_label_signal_outcome_rejects_invalid_public_inputs tests/test_mvp_tools.py::test_harness_rejects_invalid_label_take_profit_with_failure_audit tests/test_mvp_tools.py::test_harness_rejects_invalid_label_time_barrier_with_failure_audit tests/test_mvp_tools.py::test_label_signal_outcome_metrics_respect_time_barrier -q -> 4 passed, label_signal_outcome time_barrier_days failure-audit coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_mvp_tools.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py -q -> 118 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -q -> 453 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_3_389_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 3.390 Label Signal Signal ID Failure Audit Verification - 2026-05-11

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py::test_label_signal_outcome_rejects_invalid_public_inputs tests/test_mvp_tools.py::test_harness_rejects_invalid_label_signal_id_with_failure_audit tests/test_mvp_tools.py::test_harness_rejects_label_signal_identity_control_character_with_failure_audit tests/test_mvp_tools.py::test_label_signal_outcome_normalizes_public_inputs -q -> 4 passed, label_signal_outcome signal_id failure-audit coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_mvp_tools.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py -q -> 119 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -q -> 454 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_3_390_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 3.391 Label Signal Invalidating Event ID Failure Audit Verification - 2026-05-11

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py::test_label_signal_outcome_rejects_invalid_public_inputs tests/test_mvp_tools.py::test_label_signal_outcome_supports_no_data_and_event_invalidation tests/test_mvp_tools.py::test_harness_rejects_blank_label_invalidating_event_id_with_failure_audit tests/test_mvp_tools.py::test_harness_rejects_label_invalidating_event_id_control_character_with_failure_audit -q -> 4 passed, label_signal_outcome invalidating_event_id failure-audit coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_mvp_tools.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py -q -> 120 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -q -> 455 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_3_391_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 3.392 Label Signal Ledger Path Type Failure Audit Verification - 2026-05-11

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py::test_label_signal_outcome_rejects_invalid_public_inputs tests/test_mvp_tools.py::test_harness_rejects_invalid_label_signal_ledger_path_with_failure_audit tests/test_mvp_tools.py::test_harness_rejects_label_signal_ledger_path_type_with_failure_audit tests/test_mvp_tools.py::test_harness_rejects_label_signal_ledger_path_control_character_with_failure_audit -q -> 4 passed, label_signal_outcome ledger_path type failure-audit coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_mvp_tools.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py -q -> 121 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -q -> 456 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_3_392_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 3.393 Record Signal Ledger Path Type Failure Audit Verification - 2026-05-11

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py::test_record_signal_rejects_invalid_ledger_path tests/test_mvp_tools.py::test_harness_rejects_invalid_record_signal_ledger_path_with_failure_audit tests/test_mvp_tools.py::test_harness_rejects_record_signal_ledger_path_type_with_failure_audit tests/test_mvp_tools.py::test_harness_rejects_record_signal_ledger_path_control_character_with_failure_audit -q -> 4 passed, record_signal ledger_path type failure-audit coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_mvp_tools.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py -q -> 122 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -q -> 457 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_3_393_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 3.394 Evaluate Score Performance Ledger Path Type Failure Audit Verification - 2026-05-11

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py::test_evaluate_recorded_score_performance_rejects_invalid_ledger_path tests/test_mvp_tools.py::test_harness_rejects_invalid_score_performance_ledger_path_with_failure_audit tests/test_mvp_tools.py::test_harness_rejects_score_performance_ledger_path_type_with_failure_audit tests/test_mvp_tools.py::test_harness_rejects_score_performance_ledger_path_control_character_with_failure_audit -q -> 4 passed, evaluate_score_performance ledger_path type failure-audit coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_mvp_tools.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py -q -> 123 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -q -> 458 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_3_394_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 3.395 Record Signal Object Type Failure Audit Verification - 2026-05-11

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py::test_record_signal_rejects_invalid_public_signal_identity tests/test_mvp_tools.py::test_harness_rejects_record_signal_object_type_with_failure_audit tests/test_mvp_tools.py::test_harness_rejects_invalid_record_signal_with_failure_audit tests/test_mvp_tools.py::test_harness_rejects_record_signal_identity_control_character_with_failure_audit -q -> 4 passed, record_signal object type failure-audit coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_mvp_tools.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py -q -> 124 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -q -> 459 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_3_395_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 3.396 Label Signal Price Path Type Failure Audit Verification - 2026-05-11

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py::test_label_signal_outcome_rejects_invalid_public_inputs tests/test_mvp_tools.py::test_harness_rejects_invalid_label_price_path_with_failure_audit tests/test_mvp_tools.py::test_harness_rejects_label_price_path_type_with_failure_audit -q -> 3 passed, label_signal_outcome price_path type failure-audit coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_mvp_tools.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py -q -> 125 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -q -> 460 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_3_396_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 3.397 Label Signal Price Path Nonpositive Failure Audit Verification - 2026-05-11

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py::test_label_signal_outcome_rejects_invalid_public_inputs tests/test_mvp_tools.py::test_harness_rejects_invalid_label_price_path_with_failure_audit tests/test_mvp_tools.py::test_harness_rejects_label_price_path_type_with_failure_audit tests/test_mvp_tools.py::test_harness_rejects_label_price_path_nonpositive_with_failure_audit -q -> 4 passed, label_signal_outcome price_path nonpositive failure-audit coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_mvp_tools.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py -q -> 126 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -q -> 461 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_3_397_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 3.398 Label Signal Price Path Nonfinite Failure Audit Verification - 2026-05-11

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py::test_label_signal_outcome_rejects_invalid_public_inputs tests/test_mvp_tools.py::test_harness_rejects_invalid_label_price_path_with_failure_audit tests/test_mvp_tools.py::test_harness_rejects_label_price_path_type_with_failure_audit tests/test_mvp_tools.py::test_harness_rejects_label_price_path_nonpositive_with_failure_audit tests/test_mvp_tools.py::test_harness_rejects_label_price_path_nonfinite_with_failure_audit -q -> 5 passed, label_signal_outcome price_path nonfinite failure-audit coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_mvp_tools.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py -q -> 127 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -q -> 462 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_3_398_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 3.399 Label Signal Stop Loss Type Failure Audit Verification - 2026-05-11

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py::test_label_signal_outcome_rejects_invalid_public_inputs tests/test_mvp_tools.py::test_harness_rejects_invalid_label_stop_loss_with_failure_audit tests/test_mvp_tools.py::test_harness_rejects_label_stop_loss_type_with_failure_audit -q -> 3 passed, label_signal_outcome stop_loss_pct type failure-audit coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_mvp_tools.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py -q -> 128 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -q -> 463 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_3_399_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 3.400 Label Signal Take Profit Nonpositive Failure Audit Verification - 2026-05-11

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py::test_label_signal_outcome_rejects_invalid_public_inputs tests/test_mvp_tools.py::test_harness_rejects_invalid_label_take_profit_with_failure_audit tests/test_mvp_tools.py::test_harness_rejects_label_take_profit_nonpositive_with_failure_audit -q -> 3 passed, label_signal_outcome take_profit_pct nonpositive failure-audit coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_mvp_tools.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py -q -> 129 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -q -> 464 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_3_400_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 3.401 Label Signal Time Barrier Nonpositive Failure Audit Verification - 2026-05-11

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py::test_label_signal_outcome_rejects_invalid_public_inputs tests/test_mvp_tools.py::test_harness_rejects_invalid_label_time_barrier_with_failure_audit tests/test_mvp_tools.py::test_harness_rejects_label_time_barrier_nonpositive_with_failure_audit -q -> 3 passed, label_signal_outcome time_barrier_days nonpositive failure-audit coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_mvp_tools.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py -q -> 130 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -q -> 465 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_3_401_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 3.402 Label Signal Time Barrier Type Failure Audit Verification - 2026-05-11

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py::test_label_signal_outcome_rejects_invalid_public_inputs tests/test_mvp_tools.py::test_harness_rejects_invalid_label_time_barrier_with_failure_audit tests/test_mvp_tools.py::test_harness_rejects_label_time_barrier_nonpositive_with_failure_audit tests/test_mvp_tools.py::test_harness_rejects_label_time_barrier_type_with_failure_audit -q -> 4 passed, label_signal_outcome time_barrier_days type failure-audit coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_mvp_tools.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py -q -> 131 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -q -> 466 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_3_402_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 3.403 Label Signal Stop Loss Nonfinite Failure Audit Verification - 2026-05-11

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py::test_label_signal_outcome_rejects_invalid_public_inputs tests/test_mvp_tools.py::test_harness_rejects_invalid_label_stop_loss_with_failure_audit tests/test_mvp_tools.py::test_harness_rejects_label_stop_loss_type_with_failure_audit tests/test_mvp_tools.py::test_harness_rejects_label_stop_loss_nonfinite_with_failure_audit -q -> 4 passed, label_signal_outcome stop_loss_pct nonfinite failure-audit coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_mvp_tools.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py -q -> 132 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -q -> 467 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_3_403_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 3.404 Label Signal Take Profit Nonfinite Failure Audit Verification - 2026-05-11

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py::test_label_signal_outcome_rejects_invalid_public_inputs tests/test_mvp_tools.py::test_harness_rejects_invalid_label_take_profit_with_failure_audit tests/test_mvp_tools.py::test_harness_rejects_label_take_profit_nonpositive_with_failure_audit tests/test_mvp_tools.py::test_harness_rejects_label_take_profit_nonfinite_with_failure_audit -q -> 4 passed, label_signal_outcome take_profit_pct nonfinite failure-audit coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_mvp_tools.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py -q -> 133 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -q -> 468 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_3_404_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 3.405 Label Signal Invalidating Event ID Type Failure Audit Verification - 2026-05-11

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py::test_label_signal_outcome_rejects_invalid_public_inputs tests/test_mvp_tools.py::test_label_signal_outcome_supports_no_data_and_event_invalidation tests/test_mvp_tools.py::test_harness_rejects_blank_label_invalidating_event_id_with_failure_audit tests/test_mvp_tools.py::test_harness_rejects_label_invalidating_event_id_type_with_failure_audit tests/test_mvp_tools.py::test_harness_rejects_label_invalidating_event_id_control_character_with_failure_audit -q -> 5 passed, label_signal_outcome invalidating_event_id type failure-audit coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_mvp_tools.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py -q -> 134 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -q -> 469 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_3_405_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 3.406 Label Signal Signal ID Type Failure Audit Verification - 2026-05-11

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py::test_label_signal_outcome_rejects_invalid_public_inputs tests/test_mvp_tools.py::test_harness_rejects_invalid_label_signal_id_with_failure_audit tests/test_mvp_tools.py::test_harness_rejects_label_signal_id_type_with_failure_audit tests/test_mvp_tools.py::test_harness_rejects_label_signal_identity_control_character_with_failure_audit tests/test_mvp_tools.py::test_label_signal_outcome_normalizes_public_inputs -q -> 5 passed, label_signal_outcome signal_id type failure-audit coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_mvp_tools.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py -q -> 135 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -q -> 470 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_3_406_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 3.407 Record Signal Run ID Type Failure Audit Verification - 2026-05-11

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py::test_record_signal_rejects_invalid_public_signal_identity tests/test_mvp_tools.py::test_harness_rejects_record_signal_object_type_with_failure_audit tests/test_mvp_tools.py::test_harness_rejects_invalid_record_signal_with_failure_audit tests/test_mvp_tools.py::test_harness_rejects_record_signal_run_id_type_with_failure_audit tests/test_mvp_tools.py::test_harness_rejects_record_signal_identity_control_character_with_failure_audit -q -> 5 passed, record_signal signal.run_id type failure-audit coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_mvp_tools.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py -q -> 136 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -q -> 471 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_3_407_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 3.408 Record Signal Created At Blank Failure Audit Verification - 2026-05-11

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py::test_record_signal_rejects_invalid_public_signal_identity tests/test_mvp_tools.py::test_harness_rejects_record_signal_object_type_with_failure_audit tests/test_mvp_tools.py::test_harness_rejects_invalid_record_signal_with_failure_audit tests/test_mvp_tools.py::test_harness_rejects_record_signal_run_id_type_with_failure_audit tests/test_mvp_tools.py::test_harness_rejects_record_signal_created_at_blank_with_failure_audit tests/test_mvp_tools.py::test_harness_rejects_record_signal_identity_control_character_with_failure_audit -q -> 6 passed, record_signal signal.created_at blank failure-audit coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_mvp_tools.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py -q -> 137 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -q -> 472 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_3_408_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 3.409 Record Signal Underlying Null Failure Audit Verification - 2026-05-11

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py::test_record_signal_rejects_invalid_public_signal_identity tests/test_mvp_tools.py::test_harness_rejects_record_signal_object_type_with_failure_audit tests/test_mvp_tools.py::test_harness_rejects_invalid_record_signal_with_failure_audit tests/test_mvp_tools.py::test_harness_rejects_record_signal_run_id_type_with_failure_audit tests/test_mvp_tools.py::test_harness_rejects_record_signal_created_at_blank_with_failure_audit tests/test_mvp_tools.py::test_harness_rejects_record_signal_underlying_null_with_failure_audit tests/test_mvp_tools.py::test_harness_rejects_record_signal_identity_control_character_with_failure_audit -q -> 7 passed, record_signal signal.underlying null failure-audit coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_mvp_tools.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py -q -> 138 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -q -> 473 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_3_409_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 3.410 Record Signal Config Version Blank Failure Audit Verification - 2026-05-11

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py::test_record_signal_rejects_invalid_public_signal_identity tests/test_mvp_tools.py::test_harness_rejects_record_signal_object_type_with_failure_audit tests/test_mvp_tools.py::test_harness_rejects_invalid_record_signal_with_failure_audit tests/test_mvp_tools.py::test_harness_rejects_record_signal_run_id_type_with_failure_audit tests/test_mvp_tools.py::test_harness_rejects_record_signal_created_at_blank_with_failure_audit tests/test_mvp_tools.py::test_harness_rejects_record_signal_underlying_null_with_failure_audit tests/test_mvp_tools.py::test_harness_rejects_record_signal_config_version_blank_with_failure_audit tests/test_mvp_tools.py::test_harness_rejects_record_signal_identity_control_character_with_failure_audit -q -> 8 passed, record_signal signal.config_version blank failure-audit coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_mvp_tools.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py -q -> 139 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -q -> 474 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_3_410_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 3.411 Record Signal Config Hash Type Failure Audit Verification - 2026-05-11

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py::test_record_signal_rejects_invalid_public_signal_identity tests/test_mvp_tools.py::test_harness_rejects_record_signal_object_type_with_failure_audit tests/test_mvp_tools.py::test_harness_rejects_invalid_record_signal_with_failure_audit tests/test_mvp_tools.py::test_harness_rejects_record_signal_run_id_type_with_failure_audit tests/test_mvp_tools.py::test_harness_rejects_record_signal_created_at_blank_with_failure_audit tests/test_mvp_tools.py::test_harness_rejects_record_signal_underlying_null_with_failure_audit tests/test_mvp_tools.py::test_harness_rejects_record_signal_config_version_blank_with_failure_audit tests/test_mvp_tools.py::test_harness_rejects_record_signal_config_hash_type_with_failure_audit tests/test_mvp_tools.py::test_harness_rejects_record_signal_identity_control_character_with_failure_audit -q -> 9 passed, record_signal signal.config_hash type failure-audit coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_mvp_tools.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py -q -> 140 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -q -> 475 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_3_411_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 3.412 Record Signal Config Hash Control Character Failure Audit Verification - 2026-05-11

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py::test_record_signal_rejects_invalid_public_signal_identity tests/test_mvp_tools.py::test_record_signal_rejects_signal_identity_control_character_inputs tests/test_mvp_tools.py::test_harness_rejects_record_signal_object_type_with_failure_audit tests/test_mvp_tools.py::test_harness_rejects_invalid_record_signal_with_failure_audit tests/test_mvp_tools.py::test_harness_rejects_record_signal_run_id_type_with_failure_audit tests/test_mvp_tools.py::test_harness_rejects_record_signal_created_at_blank_with_failure_audit tests/test_mvp_tools.py::test_harness_rejects_record_signal_underlying_null_with_failure_audit tests/test_mvp_tools.py::test_harness_rejects_record_signal_config_version_blank_with_failure_audit tests/test_mvp_tools.py::test_harness_rejects_record_signal_config_hash_type_with_failure_audit tests/test_mvp_tools.py::test_harness_rejects_record_signal_config_hash_control_character_with_failure_audit tests/test_mvp_tools.py::test_harness_rejects_record_signal_identity_control_character_with_failure_audit -q -> 11 passed, record_signal signal.config_hash control-character failure-audit coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_mvp_tools.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py -q -> 141 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -q -> 476 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_3_412_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 3.413 Record Signal Config Version Control Character Failure Audit Verification - 2026-05-11

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py::test_record_signal_rejects_invalid_public_signal_identity tests/test_mvp_tools.py::test_record_signal_rejects_signal_identity_control_character_inputs tests/test_mvp_tools.py::test_harness_rejects_record_signal_object_type_with_failure_audit tests/test_mvp_tools.py::test_harness_rejects_invalid_record_signal_with_failure_audit tests/test_mvp_tools.py::test_harness_rejects_record_signal_run_id_type_with_failure_audit tests/test_mvp_tools.py::test_harness_rejects_record_signal_created_at_blank_with_failure_audit tests/test_mvp_tools.py::test_harness_rejects_record_signal_underlying_null_with_failure_audit tests/test_mvp_tools.py::test_harness_rejects_record_signal_config_version_blank_with_failure_audit tests/test_mvp_tools.py::test_harness_rejects_record_signal_config_version_control_character_with_failure_audit tests/test_mvp_tools.py::test_harness_rejects_record_signal_config_hash_type_with_failure_audit tests/test_mvp_tools.py::test_harness_rejects_record_signal_config_hash_control_character_with_failure_audit tests/test_mvp_tools.py::test_harness_rejects_record_signal_identity_control_character_with_failure_audit -q -> 12 passed, record_signal signal.config_version control-character failure-audit coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_mvp_tools.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py -q -> 142 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -q -> 477 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_3_413_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 3.414 Record Signal Remaining Identity Control Character Failure Audit Verification - 2026-05-11

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py::test_record_signal_rejects_invalid_public_signal_identity tests/test_mvp_tools.py::test_record_signal_rejects_signal_identity_control_character_inputs tests/test_mvp_tools.py::test_harness_rejects_record_signal_object_type_with_failure_audit tests/test_mvp_tools.py::test_harness_rejects_invalid_record_signal_with_failure_audit tests/test_mvp_tools.py::test_harness_rejects_record_signal_run_id_type_with_failure_audit tests/test_mvp_tools.py::test_harness_rejects_record_signal_created_at_blank_with_failure_audit tests/test_mvp_tools.py::test_harness_rejects_record_signal_underlying_null_with_failure_audit tests/test_mvp_tools.py::test_harness_rejects_record_signal_config_version_blank_with_failure_audit tests/test_mvp_tools.py::test_harness_rejects_record_signal_config_version_control_character_with_failure_audit tests/test_mvp_tools.py::test_harness_rejects_record_signal_config_hash_type_with_failure_audit tests/test_mvp_tools.py::test_harness_rejects_record_signal_config_hash_control_character_with_failure_audit tests/test_mvp_tools.py::test_harness_rejects_record_signal_remaining_identity_control_characters_with_failure_audit tests/test_mvp_tools.py::test_harness_rejects_record_signal_identity_control_character_with_failure_audit -q -> 15 passed, record_signal remaining identity control-character failure-audit coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_mvp_tools.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py -q -> 145 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -q -> 480 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_3_414_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 3.415 Label Signal Unused Invalidating Event ID Control Character Failure Audit Verification - 2026-05-11

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py::test_label_signal_outcome_rejects_identity_control_character_inputs tests/test_mvp_tools.py::test_harness_rejects_label_signal_identity_control_character_with_failure_audit tests/test_mvp_tools.py::test_harness_rejects_label_invalidating_event_id_control_character_with_failure_audit tests/test_mvp_tools.py::test_harness_rejects_label_unused_invalidating_event_id_control_character_with_failure_audit tests/test_mvp_tools.py::test_harness_rejects_invalid_label_event_boolean_with_failure_audit -q -> 5 passed, label_signal_outcome unused invalidating_event_id control-character failure-audit coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_mvp_tools.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py -q -> 146 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -q -> 481 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_3_415_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 3.416 Evaluate Score Performance Remaining Days Failure Audit Verification - 2026-05-11

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py::test_evaluate_recorded_score_performance_rejects_invalid_days tests/test_mvp_tools.py::test_harness_rejects_invalid_score_performance_days_with_failure_audit tests/test_mvp_tools.py::test_harness_rejects_score_performance_remaining_days_values_with_failure_audit tests/test_mvp_tools.py::test_harness_rejects_invalid_score_performance_ledger_path_with_failure_audit -q -> 6 passed, evaluate_score_performance remaining days failure-audit coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_mvp_tools.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py -q -> 149 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -q -> 484 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_3_416_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 3.417 Latest Report Extra Evidence Cards Type Failure Audit Verification - 2026-05-12

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py::test_latest_signal_report_rejects_invalid_extra_evidence_cards_container tests/test_reporting.py::test_latest_signal_report_rejects_extra_evidence_card_non_object tests/test_reporting.py::test_harness_rejects_invalid_extra_evidence_cards_container_with_failure_audit tests/test_reporting.py::test_harness_rejects_extra_evidence_card_non_object_with_failure_audit -q -> 6 passed, latest report extra_evidence_cards type failure-audit coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 196 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -q -> 499 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_3_417_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 3.418 Position Review Report Numeric Input Failure Audit Verification - 2026-05-12

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py::test_position_review_report_rejects_invalid_numeric_inputs_before_position_evaluation tests/test_reporting.py::test_harness_rejects_position_review_numeric_inputs_with_failure_audit -q -> 9 passed, position review report numeric input failure-audit coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 205 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -q -> 499 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_3_418_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 3.419 Latest Report Identity Type Failure Audit Verification - 2026-05-12

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py::test_latest_signal_report_rejects_invalid_report_intent_identity tests/test_reporting.py::test_latest_signal_report_rejects_invalid_asset_identity tests/test_reporting.py::test_latest_signal_report_rejects_invalid_timeframe_identity tests/test_reporting.py::test_harness_rejects_report_intent_type_with_failure_audit tests/test_reporting.py::test_harness_rejects_latest_report_asset_type_with_failure_audit tests/test_reporting.py::test_harness_rejects_latest_report_timeframe_type_with_failure_audit -q -> 12 passed, latest report identity type failure-audit coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 208 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -q -> 502 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_3_419_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 3.420 Cron Prompt Type Failure Audit Verification - 2026-05-12

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py::test_cron_prompt_pack_rejects_blank_asset_identity tests/test_reporting.py::test_cron_prompt_pack_rejects_invalid_timeframe_identity tests/test_reporting.py::test_cron_prompt_pack_rejects_non_bool_include_position_review tests/test_reporting.py::test_harness_rejects_cron_prompt_asset_type_with_failure_audit tests/test_reporting.py::test_harness_rejects_cron_prompt_timeframe_type_with_failure_audit tests/test_reporting.py::test_harness_rejects_non_bool_include_position_review_with_failure_audit tests/test_reporting.py::test_harness_rejects_remaining_non_bool_include_position_review_with_failure_audit -q -> 14 passed, cron prompt type failure-audit coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 212 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -q -> 517 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_3_420_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 3.421 Score Performance Provided Signals Input Audit Verification - 2026-05-12

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py::test_score_performance_marks_unsupported_long_fixture_window tests/test_mvp_tools.py::test_score_performance_treats_empty_provided_signals_as_empty_sample tests/test_mvp_tools.py::test_score_performance_rejects_invalid_provided_signals -q -> 12 passed, score performance provided signals input coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/scoring.py tests/test_mvp_tools.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py -q -> 160 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -q -> 517 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_3_421_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 3.422 Latest Report Chart Input Type Failure Audit Verification - 2026-05-12

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py::test_latest_signal_report_rejects_non_bool_include_chart tests/test_reporting.py::test_latest_signal_report_rejects_invalid_chart_timeframe tests/test_reporting.py::test_latest_signal_report_rejects_invalid_chart_output_dir tests/test_reporting.py::test_harness_rejects_non_bool_include_chart_with_failure_audit tests/test_reporting.py::test_harness_rejects_remaining_non_bool_include_chart_with_failure_audit tests/test_reporting.py::test_harness_rejects_chart_timeframe_type_with_failure_audit tests/test_reporting.py::test_harness_rejects_chart_output_dir_type_with_failure_audit -q -> 19 passed, latest report chart input type failure-audit coverage enforced
./.venv/bin/ruff check tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 218 passed
./.venv/bin/ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -q -> 523 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 3.423 Position Review Asset Type Failure Audit Verification - 2026-05-12

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py::test_position_review_report_rejects_invalid_asset_identity tests/test_reporting.py::test_harness_rejects_blank_position_review_asset_with_failure_audit tests/test_reporting.py::test_harness_rejects_position_review_asset_type_with_failure_audit tests/test_reporting.py::test_harness_rejects_position_review_asset_control_character_with_failure_audit -q -> 7 passed, position review asset type failure-audit coverage enforced
./.venv/bin/ruff check tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 220 passed
./.venv/bin/ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -q -> 525 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 3.424 Scoring Tool Identity Type Failure Audit Verification - 2026-05-12

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py::test_scoring_tools_reject_invalid_asset_identity tests/test_mvp_tools.py::test_scoring_tools_reject_invalid_timeframe_identity tests/test_mvp_tools.py::test_harness_rejects_blank_scoring_asset_with_failure_audit tests/test_mvp_tools.py::test_harness_rejects_scoring_tool_identity_types_with_failure_audit tests/test_mvp_tools.py::test_harness_rejects_scoring_asset_control_character_with_failure_audit tests/test_mvp_tools.py::test_harness_rejects_trade_guide_timeframe_control_character_with_failure_audit -q -> 14 passed, scoring tool identity type failure-audit coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_mvp_tools.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py -q -> 165 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -q -> 530 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_3_424_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 3.425 Scoring Tool Remaining Identity Control Character Audit Verification - 2026-05-12

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py::test_scoring_tools_reject_asset_control_character tests/test_mvp_tools.py::test_scoring_tools_reject_timeframe_control_character tests/test_mvp_tools.py::test_harness_rejects_scoring_asset_control_character_with_failure_audit tests/test_mvp_tools.py::test_harness_rejects_remaining_scoring_identity_control_characters_with_failure_audit tests/test_mvp_tools.py::test_harness_rejects_trade_guide_timeframe_control_character_with_failure_audit -q -> 7 passed, scoring tool remaining identity control-character coverage enforced
./.venv/bin/ruff check tests/test_mvp_tools.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py -q -> 168 passed
./.venv/bin/ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -q -> 533 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 3.426 Position Numeric Remaining Failure Audit Verification - 2026-05-12

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py::test_evaluate_position_rejects_invalid_numeric_inputs tests/test_mvp_tools.py::test_harness_rejects_invalid_position_numeric_input_with_failure_audit tests/test_mvp_tools.py::test_harness_rejects_remaining_position_numeric_inputs_with_failure_audit -q -> 7 passed, position numeric remaining failure-audit coverage enforced
./.venv/bin/ruff check tests/test_mvp_tools.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py -q -> 173 passed
./.venv/bin/ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -q -> 538 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 3.427 Score Performance Provided Signals Harness Failure Audit Verification - 2026-05-12

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py::test_score_performance_treats_empty_provided_signals_as_empty_sample tests/test_mvp_tools.py::test_score_performance_rejects_invalid_provided_signals tests/test_mvp_tools.py::test_harness_rejects_invalid_score_performance_signals_with_failure_audit -q -> 17 passed, score performance provided signals harness failure-audit coverage enforced
./.venv/bin/ruff check src/halo_swing_mcp/server.py src/halo_swing_mcp/tools/recording.py tests/test_mvp_tools.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py -q -> 179 passed
./.venv/bin/ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -q -> 544 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 3.428 Public Tool Boundary Failure Audit Verification - 2026-05-12

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py::test_score_performance_treats_empty_provided_signals_as_empty_sample tests/test_mvp_tools.py::test_score_performance_rejects_invalid_provided_signals tests/test_mvp_tools.py::test_harness_rejects_invalid_score_performance_signals_with_failure_audit tests/test_mvp_tools.py::test_harness_rejects_remaining_score_performance_signals_with_failure_audit tests/test_tool_registry.py::test_registry_rejects_unexpected_payload_keys_before_dispatch tests/test_tool_registry.py::test_registry_rejects_non_object_payloads_before_dispatch tests/test_tool_registry.py::test_registry_keeps_var_keyword_tools_permissive tests/test_tool_registry.py::test_harness_rejects_unexpected_payload_key_with_failure_audit -q -> 25 passed, public tool boundary failure-audit coverage enforced
./.venv/bin/ruff check src/halo_swing_mcp/tool_registry.py tests/test_tool_registry.py tests/test_mvp_tools.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py tests/test_tool_registry.py -q -> 196 passed
./.venv/bin/ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -q -> 552 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 3.429 Public Tool Input Boundary Failure Audit Verification - 2026-05-12

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_tool_registry.py::test_registry_rejects_missing_required_payload_keys_before_dispatch tests/test_tool_registry.py::test_registry_rejects_multiple_missing_required_payload_keys_in_signature_order tests/test_tool_registry.py::test_harness_rejects_missing_required_payload_key_with_failure_audit tests/test_tool_registry.py::test_harness_rejects_non_object_input_json_with_failure_audit tests/test_tool_registry.py::test_harness_rejects_non_object_input_file_with_failure_audit -q -> 5 passed, public tool input-boundary failure-audit coverage enforced
./.venv/bin/ruff check src/halo_swing_mcp/audit.py src/halo_swing_mcp/harness.py src/halo_swing_mcp/tool_registry.py tests/test_tool_registry.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_tool_registry.py -q -> 18 passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_audit.py -q -> 27 passed
./.venv/bin/ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -q -> 557 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 3.430 Harness Invalid JSON Failure Audit Verification - 2026-05-12

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_tool_registry.py::test_harness_rejects_invalid_input_json_with_failure_audit tests/test_tool_registry.py::test_harness_rejects_invalid_input_file_json_with_failure_audit -q -> 2 passed, harness invalid JSON failure-audit coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/harness.py tests/test_tool_registry.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_tool_registry.py -q -> 20 passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_audit.py -q -> 27 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -q -> 559 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 3.431 Harness Unreadable Input File Failure Audit Verification - 2026-05-12

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_tool_registry.py::test_harness_rejects_unreadable_input_file_with_failure_audit tests/test_tool_registry.py::test_harness_rejects_invalid_utf8_input_file_with_failure_audit -q -> 2 passed, harness unreadable/undecodable input-file failure-audit coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/harness.py tests/test_tool_registry.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_tool_registry.py -q -> 22 passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_audit.py -q -> 27 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -q -> 561 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 3.432 Harness Input Source Conflict Failure Audit Verification - 2026-05-12

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_tool_registry.py::test_harness_rejects_input_source_conflict_with_failure_audit -q -> 1 passed, harness input source conflict failure-audit coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/harness.py tests/test_tool_registry.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_tool_registry.py -q -> 23 passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_audit.py -q -> 27 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -q -> 562 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 3.433 Harness Input File Argument Failure Audit Verification - 2026-05-12

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_tool_registry.py::test_harness_rejects_blank_input_file_with_failure_audit tests/test_tool_registry.py::test_harness_rejects_input_file_control_character_with_failure_audit -q -> 2 passed, harness input-file argument failure-audit coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/harness.py tests/test_tool_registry.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_tool_registry.py -q -> 25 passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_audit.py -q -> 27 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -q -> 564 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 3.434 Harness Audit Log Path Argument Validation Verification - 2026-05-12

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_tool_registry.py::test_harness_rejects_blank_audit_log_path_without_fallback_audit tests/test_tool_registry.py::test_harness_rejects_audit_log_path_control_character_without_fallback_audit -q -> 2 passed, harness audit-log-path argument validation coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/harness.py tests/test_tool_registry.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_tool_registry.py -q -> 27 passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_audit.py -q -> 27 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -q -> 566 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 3.435 Harness Argument DEL Control Validation Verification - 2026-05-13

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_tool_registry.py::test_harness_rejects_input_file_delete_character_with_failure_audit tests/test_tool_registry.py::test_harness_rejects_audit_log_path_delete_character_without_fallback_audit -q -> 2 passed, harness DEL control-character argument validation coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/harness.py tests/test_tool_registry.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_tool_registry.py -q -> 29 passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_audit.py -q -> 27 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -q -> 568 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 3.436 Audit Environment Path Validation Verification - 2026-05-13

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_audit.py::test_resolve_audit_log_path_normalizes_env_path tests/test_audit.py::test_append_audit_event_rejects_invalid_env_audit_path_without_fallback -q -> 2 passed, audit env path validation coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/audit.py tests/test_audit.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_audit.py -q -> 29 passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_tool_registry.py -q -> 29 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -q -> 570 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 3.437 Signal Ledger Environment Path Validation Verification - 2026-05-13

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_signal_repository.py -q -> 4 passed, signal ledger env path validation coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/signal_repository.py tests/test_signal_repository.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py -q -> 183 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -q -> 572 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 3.438 Binance Credentials Environment Path Validation Verification - 2026-05-13

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_binance_btc.py::test_binance_credentials_normalizes_env_credentials_path tests/test_binance_btc.py::test_binance_credentials_reject_env_credentials_path_without_fallback -q -> 2 passed, Binance credential env path validation coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/secret_store.py tests/test_binance_btc.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_binance_btc.py -q -> 56 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -q -> 574 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 3.439 BTC Risk Environment Path Validation Verification - 2026-05-13

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_binance_btc.py::test_btc_risk_tools_normalize_env_paths tests/test_binance_btc.py::test_btc_risk_tools_reject_env_settings_path_without_fallback tests/test_binance_btc.py::test_btc_risk_tools_reject_env_state_path_without_fallback -q -> 3 passed, BTC risk env path validation coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/risk_settings.py tests/test_binance_btc.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_binance_btc.py -q -> 59 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -q -> 577 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 3.440 Runtime Checkpoint Environment Path Validation Verification - 2026-05-13

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_runtime_guard.py::test_runtime_checkpoint_normalizes_env_checkpoint_path tests/test_runtime_guard.py::test_runtime_checkpoint_rejects_env_checkpoint_path_without_fallback -q -> 2 passed, runtime checkpoint env path validation coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/runtime.py tests/test_runtime_guard.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_runtime_guard.py -q -> 19 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -q -> 579 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 3.441 Hermes Config Environment Path Validation Verification - 2026-05-13

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_readiness.py::test_integration_readiness_normalizes_env_hermes_config_path tests/test_readiness.py::test_integration_readiness_rejects_env_hermes_config_path_without_fallback -q -> 2 passed, Hermes config env path validation coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/readiness.py tests/test_readiness.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_readiness.py -q -> 20 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -q -> 581 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 3.442 Readiness Environment Boolean Normalization Verification - 2026-05-13

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_readiness.py::test_integration_readiness_ignores_invalid_env_secret_values_without_exposure tests/test_readiness.py::test_integration_readiness_ignores_invalid_live_data_source_env_values -q -> 2 passed, readiness env boolean normalization coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/readiness.py tests/test_readiness.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_readiness.py -q -> 22 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -q -> 583 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 3.443 Runtime Environment Limits Validation Verification - 2026-05-13

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_runtime_guard.py::test_runtime_status_uses_valid_env_runtime_limits tests/test_runtime_guard.py::test_runtime_status_rejects_invalid_env_runtime_limits_without_fallback -q -> 2 passed, runtime env limits validation coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/runtime_guard.py tests/test_runtime_guard.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_runtime_guard.py -q -> 21 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -q -> 585 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 3.444 Binance Recv Window Environment Validation Verification - 2026-05-13

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_binance_btc.py::test_execute_btc_order_uses_valid_env_recv_window_in_signed_request tests/test_binance_btc.py::test_signed_queries_reject_invalid_recv_window_ms tests/test_binance_btc.py::test_execute_btc_order_rejects_invalid_env_recv_window_without_network tests/test_binance_btc.py::test_account_snapshot_rejects_invalid_env_recv_window_without_network -q -> 4 passed, Binance recvWindow env validation coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/binance_btc.py tests/test_binance_btc.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_binance_btc.py -q -> 63 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -q -> 589 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 3.445 Artifact Directory Environment Validation Verification - 2026-05-13

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py::test_render_chart_uses_valid_env_artifact_dir tests/test_mvp_tools.py::test_render_chart_rejects_invalid_env_artifact_dir_without_fallback -q -> 2 passed, artifact_dir env validation coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/market.py tests/test_mvp_tools.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py -q -> 185 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -q -> 591 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 3.446 Binance Boolean Environment Canonicalization Verification - 2026-05-13

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_readiness.py::test_integration_readiness_uses_canonical_binance_boolean_env tests/test_readiness.py::test_integration_readiness_rejects_noncanonical_binance_boolean_env -q -> 2 passed, Binance boolean env canonicalization coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/config.py tests/test_readiness.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_readiness.py -q -> 24 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -q -> 593 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 3.447 Readiness Binance Credentials Environment Path Validation Verification - 2026-05-13

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_readiness.py::test_integration_readiness_normalizes_env_binance_credentials_path tests/test_readiness.py::test_integration_readiness_rejects_env_binance_credentials_path_without_fallback -q -> 2 passed, readiness Binance credentials env path validation coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/readiness.py tests/test_readiness.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_readiness.py -q -> 26 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -q -> 595 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 3.448 Readiness BTC Risk Environment Path Prevalidation Verification - 2026-05-13

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_readiness.py::test_integration_readiness_uses_env_btc_risk_settings_path tests/test_readiness.py::test_integration_readiness_rejects_env_btc_risk_settings_path_before_credentials -q -> 2 passed, readiness BTC risk env path prevalidation coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/readiness.py tests/test_readiness.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_readiness.py -q -> 28 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -q -> 597 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 3.449 Binance Execution Boolean Environment Canonicalization Coverage Verification - 2026-05-13

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_binance_btc.py::test_preview_btc_order_rejects_noncanonical_testnet_env tests/test_binance_btc.py::test_execute_btc_order_rejects_noncanonical_live_trading_env_before_credentials -q -> 2 passed, direct Binance boolean env canonicalization coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_binance_btc.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_binance_btc.py -q -> 65 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -q -> 599 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 3.450 Binance Read-Only Boolean Environment Canonicalization Coverage Verification - 2026-05-13

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_binance_btc.py::test_check_binance_connectivity_rejects_noncanonical_testnet_env_without_network tests/test_binance_btc.py::test_account_snapshot_rejects_noncanonical_testnet_env_before_credentials -q -> 2 passed, direct read-only Binance boolean env canonicalization coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_binance_btc.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_binance_btc.py -q -> 67 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -q -> 601 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 3.451 Binance Account Snapshot Missing Passphrase Environment Prevalidation Verification - 2026-05-13

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_binance_btc.py::test_check_binance_connectivity_rejects_noncanonical_testnet_env_without_network tests/test_binance_btc.py::test_account_snapshot_rejects_noncanonical_testnet_env_before_credentials tests/test_binance_btc.py::test_account_snapshot_rejects_noncanonical_testnet_env_before_missing_passphrase_status -q -> 3 passed, account snapshot missing-passphrase env prevalidation enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/binance_btc.py tests/test_binance_btc.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_binance_btc.py -q -> 68 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -q -> 602 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 3.452 Trading Admin Status Environment Prevalidation Verification - 2026-05-13

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_binance_btc.py::test_trading_admin_status_prevalidates_binance_env_before_local_reads tests/test_binance_btc.py::test_trading_admin_status_is_secret_safe -q -> 2 passed, trading admin status env prevalidation enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/trading_admin_web.py tests/test_binance_btc.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_binance_btc.py -q -> 69 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -q -> 603 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 3.453 Trading Admin Status HTTP Environment Error Handling Verification - 2026-05-13

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_binance_btc.py::test_trading_admin_status_endpoint_returns_json_error_for_invalid_binance_env tests/test_binance_btc.py::test_trading_admin_status_prevalidates_binance_env_before_local_reads -q -> 2 passed, trading admin status HTTP env error handling enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/trading_admin_web.py tests/test_binance_btc.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_binance_btc.py -q -> 70 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -q -> 604 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 3.454 Trading Admin Connectivity HTTP Environment Error Handling Verification - 2026-05-13

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_binance_btc.py::test_trading_admin_connectivity_endpoint_rejects_invalid_env_without_network tests/test_binance_btc.py::test_check_binance_connectivity_rejects_noncanonical_testnet_env_without_network -q -> 2 passed, trading admin connectivity HTTP env error handling enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_binance_btc.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_binance_btc.py -q -> 71 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -q -> 605 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 3.455 Trading Admin Account Snapshot HTTP Environment Error Handling Verification - 2026-05-13

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_binance_btc.py::test_trading_admin_account_snapshot_endpoint_rejects_invalid_env_before_status tests/test_binance_btc.py::test_account_snapshot_rejects_noncanonical_testnet_env_before_missing_passphrase_status -q -> 2 passed, trading admin account snapshot HTTP env error handling enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_binance_btc.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_binance_btc.py -q -> 72 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -q -> 606 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 3.456 Trading Admin Order Preview HTTP Environment Error Handling Verification - 2026-05-13

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_binance_btc.py::test_trading_admin_order_preview_endpoint_rejects_invalid_env_before_risk tests/test_binance_btc.py::test_preview_btc_order_rejects_noncanonical_testnet_env -q -> 2 passed, trading admin order preview HTTP env error handling enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_binance_btc.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_binance_btc.py -q -> 73 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -q -> 607 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 3.457 Trading Admin Risk-State Reset HTTP Environment Path Validation Verification - 2026-05-13

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_binance_btc.py::test_trading_admin_risk_state_reset_endpoint_rejects_invalid_env_path_without_write tests/test_binance_btc.py::test_btc_risk_tools_reject_env_state_path_without_fallback -q -> 2 passed, trading admin risk-state reset HTTP env path validation enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_binance_btc.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_binance_btc.py -q -> 74 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -q -> 608 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 3.458 Trading Admin Credentials HTTP Environment Path Validation Verification - 2026-05-13

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_binance_btc.py::test_trading_admin_credentials_endpoint_rejects_invalid_env_path_without_secret_leak tests/test_binance_btc.py::test_binance_credentials_reject_env_credentials_path_without_fallback -q -> 2 passed, trading admin credentials HTTP env path validation enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_binance_btc.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_binance_btc.py -q -> 75 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -q -> 609 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 3.459 Trading Admin Risk-Settings HTTP Environment Path Validation Verification - 2026-05-13

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_binance_btc.py::test_trading_admin_risk_settings_endpoint_rejects_invalid_env_path_without_write tests/test_binance_btc.py::test_btc_risk_tools_reject_env_settings_path_without_fallback -q -> 2 passed, trading admin risk-settings HTTP env path validation enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_binance_btc.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_binance_btc.py -q -> 76 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -q -> 610 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 3.460 Trading Admin Non-Object JSON Payload Boundary Verification - 2026-05-13

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_binance_btc.py::test_trading_admin_post_endpoints_reject_non_object_json_before_side_effects -q -> 1 passed, trading admin POST non-object JSON payload boundary enforced before side-effect paths
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_binance_btc.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_binance_btc.py -q -> 77 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -q -> 611 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 3.461 Trading Admin Malformed JSON Payload Boundary Verification - 2026-05-13

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_binance_btc.py::test_trading_admin_post_endpoints_reject_malformed_json_before_side_effects -q -> 1 passed, trading admin POST malformed JSON payload boundary enforced before side-effect paths without echoing secret-looking text
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_binance_btc.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_binance_btc.py -q -> 78 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -q -> 612 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 3.462 Trading Admin Content-Length Boundary Verification - 2026-05-13

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_binance_btc.py::test_trading_admin_post_endpoints_reject_invalid_content_length_before_side_effects -q -> 1 passed, trading admin invalid Content-Length boundary enforced before side-effect paths without echoing secret-looking text
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/trading_admin_web.py tests/test_binance_btc.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_binance_btc.py -q -> 79 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -q -> 613 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 3.463 Trading Admin Content-Type Boundary Verification - 2026-05-13

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_binance_btc.py::test_trading_admin_post_endpoints_reject_non_json_content_type_before_side_effects -q -> 1 passed, trading admin non-JSON Content-Type boundary enforced before side-effect paths without echoing secret-looking text
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/trading_admin_web.py tests/test_binance_btc.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_binance_btc.py -q -> 80 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -q -> 614 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 3.464 Trading Admin Content-Type Compatibility Verification - 2026-05-13

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_binance_btc.py::test_trading_admin_post_accepts_json_content_type_with_parameters -q -> 1 passed, trading admin accepts application/json Content-Type parameters and mixed case after media-type validation
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_binance_btc.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_binance_btc.py -q -> 81 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -q -> 615 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 3.465 Trading Admin UTF-8 Body Boundary Verification - 2026-05-13

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_binance_btc.py::test_trading_admin_post_endpoints_reject_invalid_utf8_body_before_side_effects -q -> 1 passed, trading admin invalid UTF-8 body boundary enforced before side-effect paths without echoing secret-looking text
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/trading_admin_web.py tests/test_binance_btc.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_binance_btc.py -q -> 82 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -q -> 616 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 3.466 Trading Admin Bind Host Guard Verification - 2026-05-13

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_binance_btc.py::test_trading_admin_web_main_rejects_non_localhost_bind_without_server -q -> 1 passed, trading admin rejects non-localhost bind hosts before ThreadingHTTPServer construction
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_binance_btc.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_binance_btc.py -q -> 83 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -q -> 617 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 3.467 Trading Admin Port Guard Verification - 2026-05-13

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_binance_btc.py::test_trading_admin_web_main_rejects_invalid_port_without_server tests/test_binance_btc.py::test_trading_admin_web_main_allows_localhost_ephemeral_port -q -> 2 passed, trading admin rejects invalid ports before ThreadingHTTPServer construction while preserving localhost port 0
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/trading_admin_web.py tests/test_binance_btc.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_binance_btc.py -q -> 85 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -q -> 619 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 3.468 Audit Web Port Guard Verification - 2026-05-13

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_audit.py::test_audit_web_main_rejects_invalid_port_without_server tests/test_audit.py::test_audit_web_main_allows_localhost_ephemeral_port -q -> 2 passed, audit web rejects invalid ports before audit path resolution and ThreadingHTTPServer construction while preserving localhost port 0
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/audit_web.py tests/test_audit.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_audit.py -q -> 31 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -q -> 621 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 3.469 Audit Web Audit Log Path Guard Verification - 2026-05-13

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_audit.py::test_audit_web_main_rejects_invalid_audit_log_path_without_server tests/test_audit.py::test_audit_web_main_rejects_invalid_env_audit_log_path_without_server -q -> 2 passed, audit web rejects invalid explicit/env audit log paths before handler creation or ThreadingHTTPServer construction
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/audit_web.py tests/test_audit.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_audit.py -q -> 33 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -q -> 623 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 3.470 Audit Web Summary Path Guard Verification - 2026-05-13

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_audit.py::test_audit_web_summary_endpoint_returns_bad_request_for_invalid_audit_log_path tests/test_audit.py::test_audit_web_summary_endpoint_returns_bad_request_for_invalid_env_audit_path -q -> 2 passed, audit web summary endpoint returns HTTP 400 JSON for invalid explicit/env audit log paths before audit reads or fallback file creation
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/audit_web.py tests/test_audit.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_audit.py -q -> 35 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -q -> 625 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 3.471 Audit Web Events Path Guard Verification - 2026-05-13

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_audit.py::test_audit_web_events_endpoint_returns_bad_request_for_invalid_audit_log_path tests/test_audit.py::test_audit_web_events_endpoint_returns_bad_request_for_invalid_env_audit_path -q -> 2 passed, audit web events endpoint returns HTTP 400 JSON for invalid explicit/env audit log paths before audit reads or fallback file creation
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_audit.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_audit.py -q -> 37 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -q -> 627 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 3.472 Runtime Checkpoint Invalid Input No-Write Guard Verification - 2026-05-13

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_runtime_guard.py::test_runtime_checkpoint_rejects_invalid_public_inputs -q -> 1 passed, invalid runtime checkpoint public inputs do not create checkpoint/audit/ledger files before validation failure
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_runtime_guard.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_runtime_guard.py -q -> 21 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -q -> 627 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```
