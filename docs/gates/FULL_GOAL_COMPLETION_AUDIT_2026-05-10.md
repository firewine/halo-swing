# Full Goal Completion Audit - 2026-05-10

## 1. Objective Restatement

User objective:

```text
docs/halo-swing-development-plan.md의 개발 목표를 확인하고 개발 목표대로 개발한다.
```

Concrete success means:

- The documented Halo Swing MCP product goals are mapped to real artifacts.
- Implementable offline/default-safe scope is built with tests and harnesses.
- Blocked live, DB, Hermes/Telegram, and order-submission scope is not silently
  treated as complete.
- Every remaining gap has a concrete gate, required decision, or environment
  prerequisite.

Conclusion:

```text
overall_goal_complete: false
reason: multiple documented product requirements still require user/environment
        decisions or future hard-gate approval
```

Do not mark the active goal complete until the blocked rows below are resolved
or explicitly removed from the product objective.

## 2. Prompt-To-Artifact Checklist

| Requirement / Gate | Evidence Inspected | Status | Gap / Next Requirement |
| --- | --- | --- | --- |
| Read and follow `docs/halo-swing-development-plan.md` | SSOT sections 1, 2.2, 4, 5, 3.23-3.33; `docs/WORKING.md` current directive | Verified | Continue using SSOT plus gate packets before code changes. |
| Deterministic offline harness default | `src/halo_swing_mcp/harness.py`, `src/halo_swing_mcp/tool_registry.py`, `src/halo_swing_mcp/server.py`, `tests/test_tool_registry.py`, `tests/test_mvp_tools.py`, exact parity between `health_check.capabilities` and `tests/golden/mvp_tool_contracts.json` required tools, direct ordered parity between MVP `required_tools` and `tool_registry.tool_names()`, exact parity between `@mcp.tool()` server wrappers and `tool_registry.tool_names()`, exact parity between MCP wrapper names and registry dispatch strings, exact parity between MCP wrapper parameters and same-named payload bindings, exact parity between MCP wrapper parameters and registered implementation signatures, unique ordered ToolSpec registry with callable functions and nonempty descriptions, `audit_log.v1`/`audit_summary.v1` read tool contracts | Verified | Keep live smoke separate from deterministic regression tests. |
| No automatic trading as MVP default | `src/halo_swing_mcp/binance_btc.py`, `tests/test_binance_btc.py`, readiness gates | Verified | Live submission still requires explicit future approval. |
| No secrets or runtime artifacts committed | audit redaction tests, credential status masking, artifact audit | Verified | Local ignored `state/` may exist; do not commit runtime files. |
| Phase 0 project/server/health/harness/devops | `src/halo_swing_mcp/server.py`, `tools/health.py`, `.env.example`, `README.md`, `docs/devops-setup-guide.md` | Verified with scope caveat | P0 SQLite connection was intentionally deferred by later P0/P1 storage policy. |
| Phase 1 market data and indicator engine | `tools/market.py`, `indicators.py`, `providers.py`, `tests/test_mvp_tools.py`, `tests/test_providers.py`, `market_snapshot.v1` for QQQ/SPY/SMH/SOXX/BTC, fixture-backed `1d`/`4h`/`1h` timeframe contract, `swing_level_contract`, gap/support/resistance and previous swing high/low fields | Replay verified | Live OHLCV source and persistent `feature_store` remain blocked by live-data and DB gates. |
| Phase 2 leveraged ETF swing guide | `tools/scoring.py`, `strategy.py`, `tests/test_mvp_tools.py`, `strategy_config_contract`, `trade_guide.v1`, `position_management.v1`, `time_exit_conditions`, component score contract for trend/pullback/momentum/breadth/volatility/macro/event/theme | Verified for QLD/TQQQ/SSO/UPRO/SOXL fixture universe | Future live behavior depends on live data source decisions. |
| Phase 3 macro/event filter | `get_macro_snapshot`, `macro_filter_summary`, macro block flags, `get_event_calendar`, `event_policy.v1` covering CPI/FOMC/NFP/EARNINGS, high-event-risk 3x block coverage, `event_window_summary`, per-event `danger_window` | Fixture verified | Live macro source/API and exact event feed policy remain blocked. |
| Phase 4 news/policy/geopolitical engine | `get_news_bundle`, evidence cards, `news_source_policy.v1` covering Fed/Treasury/White House/EIA/Iran-Hormuz/AI-semiconductor fixture groups, `news_score_contract`, `news_score`, `policy_score`, `geopolitical_score`, `ai_semiconductor_theme_score`, `score_leverage_swing.news_usage_contract` | Fixture verified | Live RSS/API collection and external source policy remain blocked. |
| Phase 5 signal recording and labeling | `tools/recording.py`, `signal_repository.py`, `tests/test_signal_repository.py`, `tests/test_mvp_tools.py`, `run_journal.v1`, `signal_label_outcome.v1`, MFE/MAE/realized_R time-barrier metric contract, label outcomes `TAKE_PROFIT_FIRST`/`STOP_LOSS_FIRST`/`TIME_EXIT`/`NO_DATA`/`INVALIDATED_BY_EVENT` | JSONL verified | DB-backed `signal_ledger`/`label_store`/`run_journal` remains blocked until `MIGRATION_GO` and `REPOSITORY_GO`. |
| Phase 6 scoring feedback pipeline | `evaluate_score_performance(days=90)`, `evaluate_score_performance(days=180)`, `evaluate_score_performance(days=365)` unsupported-window guard, `fixture_oos_window.v1`, explicit `score_calibration`, component attribution, ablation report, 90-day and 180-day fixture OOS reports, coverage gap metadata for requests beyond fixture coverage, walk-forward fixture folds, `overfit_guard`, `deflated_sharpe_proxy.v1`, `suggest_weight_update`, `challenger_config.v1`, `compare_champion_challenger`, promotion report, `tests/golden/mvp_tool_contracts.json` required tool manifest, `tests/test_mvp_tools.py` | Offline MVP verified | Durable strategy repository and real out-of-sample datasets remain blocked by repository/live-data decisions. |
| Phase 7 Hermes integration | DevOps MCP config example, `generate_latest_signal_report`, `generate_position_review_report`, `generate_cron_prompt_pack`, intent-specific report sections for `pre_market_swing_report`/`intraday_risk_watch`/`post_market_review`, intent-aligned prompt contracts, cron prompt input/section alignment, cron prompt tool/input schema guard, cron prompt idempotency key guard, cron prompt idempotency text guard, cron prompt expected sections text guard, cron prompt position review sections guard, cron prompt output schema guard, cron prompt live data boundary guard, cron prompt decision focus guard, cron prompt supported intents registry guard, cron prompt pack identity guard, cron prompt position option contract guard, cron prompt pack top-level contract guard, cron prompt pack key schema guard, cron prompt guard key schema guard, cron prompt guard check key schema guard, cron prompt guard check name schema guard, cron prompt manual setup registry guard, cron prompt contract key schema guard, cron prompt prompt key schema guard, cron prompt schedule hint text guard, cron prompt manual setup text guard, cron prompt scheduler setup prerequisite guard, cron prompt no-secret text guard, cron prompt name text guard, cron prompt delivery path metadata guard, cron prompt Telegram format schema guard, cron prompt numeric authority metadata guard, cron prompt manual setup guard, cron prompt no-secret credential guard, cron prompt name set guard, cron prompt ordered unique prompt name guard, cron prompt schedule hint guard, cron prompt tool/input text guard, cron prompt configured gateway text guard, cron prompt delivery preview text guard, cron prompt numeric authority text guard, cron prompt order block text guard, report sections intent order guard, report intent contract key schema guard, report intent contract registry guard, report delivery contract, intent-aligned `telegram_report_format.v1` required sections with guard parity, report prompt exact must_include guard, report prompt contract key schema guard, report prompt contract identity guard, position review Telegram required section guard parity, position review max_chars contract guard, position review delivery cron intents registry guard, position review contract key schema guard, position review contract no-network guard, position review contract identity guard, position review contract required sections guard, delivery contract no-send/no-network guard coverage, delivery contract key schema guard, report and position review guard check name schema guard, report and position review guard check key schema guard, report contract numeric authority guard, report delivery cron intents registry guard, report delivery channel format guard, report Telegram max_chars identity guard, report Telegram schema_version guard, report Telegram chunking contract guard, report text numeric field guard, `delivery_preview`, delivery preview no-send/no-network guard, delivery preview Telegram format/max chunk/text preservation guard coverage, delivery preview guard check name schema guard, delivery preview guard check key schema guard, delivery preview payload key schema guard, Hermes payload_ref/numeric authority preview guard, Telegram required section presence preview guard, Telegram unrequested section absence preview guard, Telegram 1-based chunk index preview guard, Telegram message count preview guard, Telegram chunk char-count preview guard, Telegram nonempty chunk preview guard, Telegram section separator preview guard, Telegram overflow policy section-boundary guard, `evidence_guard`, evidence guard check name schema guard, evidence guard check key schema guard, report/position/evidence guard top-level key schema guard, report/position payload key schema guard, report/position payload schema/live-data guard, report/position payload guard check name schema guard, report/position payload guard check key schema guard, report/position payload guard top-level key schema guard, position payload top-level identity guard, position payload nested guard status guard, report payload intent contract guard, report payload top-level identity guard, report payload nested guard status guard, report payload optional context status guard, report payload optional context guard-status guard, report payload source signal ref key schema guard, report payload source signal ref identity guard, report payload source signal ref trace format guard, report payload source signal ref config hash digest guard, degraded `data_warnings` Cautions reflection guard, report/position guards, runtime guard, `get_runtime_status`, `record_runtime_checkpoint`, MVP required tool manifest coverage, readiness gate | Harness verified | Real Hermes config path, Telegram credential/gateway, and scheduler/crons require user environment decision. |
| Phase 8 multimodal extension | `render_chart`, `chart_artifact_contract`, `chart_artifact_guard`, optional `chart_ref`, `chart_code_guard`, CHART ref slot artifact type guard, CHART artifact_ref declaration negative coverage, CHART artifact_ref reserved evidence_id guard, CHART artifact_ref renderer value type guard, CHART artifact_ref renderer value negative coverage, CHART artifact_ref renderer text safety guard, CHART artifact_ref ref_type DTO validation coverage, evidence card `modality`, portable `artifact_ref`, `create_document_evidence_card`, document summary input guard, `multimodal_context`, `multimodal_context` payload key schema guard, `multimodal_context` artifact ref schema guard, `multimodal_context` artifact_ref string field type guard, PDF artifact_ref ref_type field negative coverage, `multimodal_context` evidence_id uniqueness guard, `multimodal_context` evidence card reserved id guard, `multimodal_context` evidence card safe id guard, `multimodal_context` artifact_ref evidence id safe guard, `multimodal_context` evidence_id type guard, `multimodal_context` artifact_ref value uniqueness guard, `multimodal_context` CHART artifact ref PNG contract guard, `multimodal_context` CHART artifact ref offline location guard, `multimodal_context` CHART artifact ref file URI rejection coverage, `multimodal_context` CHART artifact ref tilde path rejection coverage, `multimodal_context` CHART machine-specific path rejection coverage, `multimodal_context` artifact_ref embedded local path marker guard, `multimodal_context` artifact_ref string safety guard, `multimodal_context` content-address digest format guard, `multimodal_context` valid content-address acceptance coverage, `multimodal_context` evidence card supported modality guard, document modality type negative coverage, document modality nonempty negative coverage, document bias type negative coverage, `multimodal_context` evidence card explicit artifact URI guard, `multimodal_context` PDF artifact ref contract guard, `multimodal_context` evidence card observed_at UTC ISO timestamp guard, document observed_at type negative coverage, document observed_at nonempty negative coverage, `multimodal_context` evidence card observed_at temporal guard, `multimodal_context` evidence card asset scope guard, document asset_scope empty negative coverage, `multimodal_context` evidence card asset_scope string safety guard, `multimodal_context` asset_scope value type negative coverage, `multimodal_context` evidence card invalidating_condition actionability guard, document invalidating_condition type negative coverage, `multimodal_context` evidence card categorical value guard, document category/source type negative coverage, `multimodal_context` evidence card summary bounds guard, document summary nonempty negative coverage, `multimodal_context` evidence card summary truncation consistency guard, `multimodal_context` evidence card impact context-only guard, document impact type negative coverage, `multimodal_context` evidence card scalar string safety guard, `multimodal_context` evidence card text string safety guard, `multimodal_context` evidence card string field type guard, `multimodal_context` evidence card structural field type guard, `multimodal_context` document artifact_ref structural negative coverage, `multimodal_context` evidence card numeric bool negative coverage, document numeric type negative coverage, document numeric range negative coverage, `multimodal_context` summary truncation flag type negative coverage, `multimodal_context` artifact_ref metadata text string safety guard, `multimodal_context` artifact_ref ref_type contract guard, `multimodal_context` artifact_ref ref_type canonical case guard, `multimodal_context` artifact metadata per-entry schema guard, `multimodal_context` artifact metadata schema guard, `multimodal_context` artifact metadata value guard, `multimodal_context` artifact metadata value type guard, `multimodal_context` CHART metadata value type negative coverage, `multimodal_context` artifact_ref metadata non-dict negative coverage, CHART artifact_ref metadata DTO validation coverage, CHART artifact_ref scalar DTO validation coverage, `multimodal_context` modality count guard, `multimodal_context` evidence card key schema guard, `multimodal_context` artifact_ref identity guard, `multimodal_context` evidence card value safety guard, `multimodal_context` identity values guard, non-default report intent multimodal coverage, non-default document-only multimodal coverage, multimodal evidence/report guards, `multimodal_context.guard` schema self-checks, report/tests | Partial verified | Live Hermes multimodal call, real PDF/image parsing, and default chart policy remain deferred. |
| Phase 9 order integration | BTC-only Binance COIN-M module, local admin, preview, position-aware preview effect, read-only account tools, offline portfolio snapshot normalizer, safety guards, emergency kill switch, `binance_credential_policy.v1` trade-only/no-withdraw contract, guarded BTC tool manifest coverage, `live_order_submission` readiness gate | Guarded path verified; live smoke blocked | Testnet read-only smoke needs real encrypted testnet credentials and manual passphrase. Live submission needs explicit future approval, live-trading env flag, and operator permission attestation. |
| P1 storage/schema gate | `docs/gates/P1_MIGRATION_GATE_READINESS_2026-05-10.md` | Readiness recorded no-go | No migrations, DDL, schema runner, or DB connection until `MIGRATION_GO`; no DB repository persistence until `REPOSITORY_GO`. |
| Integration readiness | `src/halo_swing_mcp/tools/readiness.py`, `tests/test_readiness.py` | Verified | Tool correctly reports blocked `hermes_mcp_config_readiness.v1`, `telegram_delivery_readiness.v1`, migration, repository, Binance read-only, live-order, and `live_data_source_readiness.v1` market/macro/news gates. Top-level `next_actions` is now contract-tested against gate missing reasons and empty ready-state guidance. |

Integration readiness latest audit addendum:

- Binance credential status schema contract coverage is verified by
  `tests/test_binance_btc.py::test_binance_credential_status_exposes_trade_only_policy_without_secrets`.
- The coverage proves direct and registry-backed `get_binance_credentials_status`
  outputs keep missing/configured credential status schemas stable, include only
  safe kdf/cipher metadata, and exclude api_secret, raw api_key, passphrase,
  salt_b64, and encrypted token values.
- configured credential schema coverage is verified by
  `tests/test_readiness.py::test_integration_readiness_configured_credential_schema_is_stable`.
- The coverage proves encrypted Binance credential metadata returns only safe
  configured status fields, api key hint, timestamp, kdf/cipher names, and
  policy metadata while excluding api_secret, passphrase, salt_b64, and encrypted
  token values.
- payload schema contract coverage is verified by
  `tests/test_readiness.py::test_integration_readiness_payload_schema_is_stable`.
- The coverage proves top-level payload keys, gate order, gate envelope keys,
  gate evidence keys, missing Binance credential status keys, and Binance
  credential policy keys remain stable without returning secrets or performing
  external side effects.
- next_actions contract coverage is verified by
  `tests/test_readiness.py::test_integration_readiness_reports_blocked_defaults`
  and `tests/test_readiness.py::test_integration_readiness_uses_safe_local_evidence`.
- The coverage proves top-level operator guidance mirrors blocked gate missing
  reasons in gate order and becomes empty when all gates are ready with safe
  local evidence, without starting Hermes, sending Telegram, calling Binance,
  exposing credentials, adding live adapters, or submitting orders.

Phase 8 latest audit addendum:

- null document artifact_ref collection negative coverage is verified by
  `tests/test_reporting.py::test_latest_signal_report_rejects_null_document_artifact_ref`.
- The coverage proves present-but-null document artifact_ref values are included
  in artifact_refs collection and conflict through artifact_ref schema,
  portable-ref safety, explicit URI, structural type, and payload optional-context
  guards instead of being silently omitted.
- artifact_ref collection coverage guard is verified by
  `tests/test_reporting.py::test_latest_signal_report_rejects_empty_document_artifact_ref_dict`
  and `tests/test_reporting.py::test_latest_signal_report_rejects_missing_document_artifact_ref_key`.
- The guard independently compares evidence card ids with artifact_ref keys
  against non-chart artifact_refs evidence ids, reducing reliance on the same
  collection helper for expected and actual context.
- empty document artifact_ref dict collection negative coverage is verified by
  `tests/test_reporting.py::test_latest_signal_report_rejects_empty_document_artifact_ref_dict`.
- The coverage proves present-but-empty document artifact_ref dicts are included
  in artifact_refs collection and conflict through artifact_ref context/schema,
  string field type, ref type contract, ref value, value safety, and explicit
  URI guards instead of being silently omitted.
- document artifact_ref missing key portable guard negative coverage is verified by
  `tests/test_reporting.py::test_latest_signal_report_rejects_missing_document_artifact_ref_key`
  and `tests/test_reporting.py::test_latest_signal_report_rejects_empty_pdf_artifact_ref_value`.
- The coverage proves blank refs are non-portable and missing document
  artifact_ref keys conflict through evidence card schema, value safety,
  explicit URI, and structural guards even when artifact_refs collection omits
  the card.
- PDF metadata unexpected key aggregate negative coverage is verified by
  `tests/test_reporting.py::test_latest_signal_report_rejects_unexpected_pdf_metadata_key`.
- The coverage proves aggregate metadata schema and per-entry metadata schema
  guards conflict while PDF contract, metadata value safety, and metadata
  value-type guards remain ok.
- CHART metadata unexpected key negative coverage is verified by
  `tests/test_reporting.py::test_latest_signal_report_rejects_unexpected_chart_metadata_key`.
- The coverage proves exact metadata schema and per-entry metadata schema
  guards conflict while PNG, metadata value safety, and metadata value-type
  guards remain ok.
- CHART artifact_ref unexpected key DTO negative coverage is verified by
  `tests/test_reporting.py::test_latest_signal_report_rejects_unexpected_chart_artifact_ref_key`.
- The coverage proves `LatestSignalReport` rejects unexpected
  `chart_ref.mime_type` before downstream artifact schema, PNG,
  offline-location, metadata, or multimodal guard assumptions.
- CHART artifact_ref missing ref_type key DTO negative coverage is verified by
  `tests/test_reporting.py::test_latest_signal_report_rejects_missing_chart_artifact_ref_type_key`.
- The coverage proves `LatestSignalReport` rejects missing `chart_ref.ref_type`
  before downstream artifact type, canonical uppercase, PNG, or multimodal
  guard assumptions.
- CHART artifact_ref missing ref key DTO negative coverage is verified by
  `tests/test_reporting.py::test_latest_signal_report_rejects_missing_chart_artifact_ref_value_key`.
- The coverage proves `LatestSignalReport` rejects missing `chart_ref.ref`
  before downstream URI, PNG, offline-location, or multimodal guard assumptions.
- CHART artifact_ref missing metadata key negative coverage is verified by
  `tests/test_reporting.py::test_latest_signal_report_rejects_missing_chart_artifact_ref_metadata_key`.
- The coverage proves DTO defaulting keeps artifact_ref schema valid while
  metadata schema, per-entry schema, value, and value-type guards conflict.
- PDF artifact_ref missing metadata key negative coverage is verified by
  `tests/test_reporting.py::test_latest_signal_report_rejects_missing_pdf_artifact_ref_metadata_key`.
- The coverage proves a missing required `metadata` key trips artifact_ref
  schema, metadata schema, per-entry schema, value, and value-type guards.
- PDF artifact_ref missing ref_type key negative coverage is verified by
  `tests/test_reporting.py::test_latest_signal_report_rejects_missing_pdf_artifact_ref_type_key`.
- The coverage proves a missing required `ref_type` key trips artifact_ref
  schema, string type, ref_type contract, and canonical uppercase guards.
- PDF artifact_ref missing ref key negative coverage is verified by
  `tests/test_reporting.py::test_latest_signal_report_rejects_missing_pdf_artifact_ref_value_key`.
- The coverage proves a missing required `ref` key trips artifact_ref schema,
  string type, nonempty ref, explicit URI, and PDF contract guards.
- PDF artifact_ref unexpected key schema negative coverage is verified by
  `tests/test_reporting.py::test_latest_signal_report_rejects_unexpected_pdf_artifact_ref_key`.
- The coverage proves an unexpected `mime_type` top-level key trips the
  artifact_ref key schema while ref/type/PDF/metadata guards stay ok.
- document unexpected key schema negative coverage is verified by
  `tests/test_reporting.py::test_latest_signal_report_rejects_unexpected_document_card_key`.
- The coverage proves an unexpected `raw_text` top-level key trips the evidence
  card key schema while value/type/categorical guards stay ok.
- document source key schema negative coverage is verified by
  `tests/test_reporting.py::test_latest_signal_report_rejects_missing_document_source_key`.
- The coverage proves a missing required `source` key trips the evidence card
  key schema, string type, and categorical guards before downstream assumptions.
- document evidence_id duplicate negative coverage is verified by
  `tests/test_reporting.py::test_latest_signal_report_rejects_duplicate_document_evidence_ids`.
- The coverage proves reserved-id and artifact_ref value uniqueness guards stay
  ok while evidence card and artifact_ref evidence_id uniqueness conflict.
- CHART artifact_ref duplicate value negative coverage is verified by
  `tests/test_reporting.py::test_latest_signal_report_rejects_duplicate_chart_artifact_ref_values`.
- The coverage proves artifact_ref evidence ids stay unique while artifact_ref
  value uniqueness conflicts.
- CHART artifact_ref control character negative coverage is verified by
  `tests/test_reporting.py::test_latest_signal_report_rejects_chart_artifact_ref_with_control_character`.
- The coverage proves chart PNG contract and offline-location guards stay ok
  while artifact_ref string safety conflicts.
- CHART artifact_ref ref_type lowercase DTO validation coverage is verified by
  `tests/test_reporting.py::test_latest_signal_report_rejects_lowercase_chart_artifact_ref_type`.
- The coverage proves `LatestSignalReport` DTO rejects invalid non-canonical
  enum-string `chart_ref.ref_type` before malformed report payload emission.
- CHART artifact_ref ref_type empty DTO validation coverage is verified by
  `tests/test_reporting.py::test_latest_signal_report_rejects_empty_chart_artifact_ref_type`.
- The coverage proves `LatestSignalReport` DTO rejects invalid enum-string
  `chart_ref.ref_type` before malformed report payload emission.
- CHART metadata values negative coverage is verified by
  `tests/test_reporting.py::test_latest_signal_report_rejects_unsafe_chart_metadata_values`.
- The coverage proves chart PNG contract and metadata schema stay ok while
  metadata value safety and exact value/type guards conflict.
- CHART metadata missing key negative coverage is verified by
  `tests/test_reporting.py::test_latest_signal_report_rejects_missing_chart_metadata_key`.
- The coverage proves chart PNG contract stays ok while metadata schema,
  per-entry schema, value safety, and exact value/type guards conflict.
- document PDF metadata missing key negative coverage is verified by
  `tests/test_reporting.py::test_latest_signal_report_rejects_missing_pdf_metadata_key`.
- The coverage proves metadata schema, per-entry schema, value safety, and
  exact value/type guards conflict while text safety stays ok.
- document PDF metadata bool values negative coverage is verified by
  `tests/test_reporting.py::test_latest_signal_report_rejects_unsafe_pdf_metadata_bool_values`.
- The coverage proves metadata schema and text safety guards stay ok while
  metadata value safety and exact bool-value strictness conflict.
- document PDF metadata description nonempty negative coverage is verified by
  `tests/test_reporting.py::test_latest_signal_report_rejects_empty_pdf_metadata_description`.
- The coverage proves metadata schema, value type, and text trim/control guards
  stay ok while metadata value safety conflicts on `description_nonempty`.
- document PDF artifact_ref ref_type empty negative coverage is verified by
  `tests/test_reporting.py::test_latest_signal_report_rejects_empty_pdf_artifact_ref_type`.
- The coverage proves explicit URI and artifact_ref string type guards stay ok
  while artifact type contract and canonical uppercase guards conflict.
- document PDF artifact_ref empty value negative coverage is verified by
  `tests/test_reporting.py::test_latest_signal_report_rejects_empty_pdf_artifact_ref_value`.
- The coverage proves artifact_ref string type and trim/control guards stay ok
  while nonempty, explicit URI, and PDF contract guards conflict.
- document asset_scope uppercase negative coverage is verified by
  `tests/test_reporting.py::test_latest_signal_report_rejects_lowercase_document_asset_scope`.
- The coverage proves structural type, asset scope matching, and
  asset_scope trim/control guards stay ok while uppercase value safety
  conflicts.
- document bias empty negative coverage is verified by
  `tests/test_reporting.py::test_latest_signal_report_rejects_empty_document_evidence_bias`.
- The coverage proves value safety and strict string field type guards stay ok
  while the categorical bias allowed-set guard conflicts.
- document category/source empty negative coverage is verified by
  `tests/test_reporting.py::test_latest_signal_report_rejects_empty_document_category_source`.
- The coverage proves value safety and strict string field type guards stay ok
  while category/source identity categorical guard conflicts.
- document impact nonempty negative coverage is verified by
  `tests/test_reporting.py::test_latest_signal_report_rejects_empty_document_evidence_impact`.
- The coverage proves string type stays ok while impact presence,
  context-only, and value safety guards conflict.
- document invalidating_condition nonempty negative coverage is verified by
  `tests/test_reporting.py::test_latest_signal_report_rejects_empty_invalidating_condition`.
- The coverage proves string type and text trim/control guards stay ok while
  invalidating_condition presence, actionability, and value safety guards
  conflict.
- This remains offline-only; no parser, Hermes multimodal call, remote fetch,
  field normalization, live adapter, scheduler, credential, or artifact
  embedding was added.

## 3. Current Blockers

These are real blockers, not test failures:

- `MIGRATION_GO` and `REPOSITORY_GO` are not recorded.
- Hermes config path and MCP registration confirmation are not provided.
- Telegram credential/gateway decision is not provided.
- Binance encrypted testnet credentials and manual passphrase availability are
  not provided.
- Live market OHLCV, macro, and news source/API-key policies are not decided.
- Live order submission has no explicit future approval.

## 4. Scope Guard Result

Allowed during this audit:

- Offline fixture/replay implementation.
- Contract/golden/test strengthening.
- Documentation synchronization and readiness reporting.

Not added:

- `migrations/`
- DDL or schema runner
- DB connection code
- live market/news/macro adapter
- Hermes/Telegram runtime credential
- scheduler/cron runner
- committed chart or runtime artifact
- live order submission enablement

## 5. Verification To Maintain

Required final verification after any implementation change:

```bash
PYTHONPATH=src ./.venv/bin/python -m pytest
PYTHONPATH=src ./.venv/bin/python -m ruff check .
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness record_runtime_checkpoint --input-json '{"checkpoint_path":"/private/tmp/halo_swing_runtime_checkpoints.jsonl","audit_log_path":"/private/tmp/halo_swing_checkpoint_audit.jsonl","ledger_path":"/private/tmp/halo_swing_checkpoint_ledger.jsonl","run_id":"manual_smoke"}' --no-audit
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl
git diff --check
```

Artifact audit:

```bash
find . \( -path './migrations' -o -path './data' -o -path './src/halo_swing_mcp/live_adapters' -o -name '*.sqlite' -o -name '*.sqlite3' -o -name '*.png' \) -print
git status --short --ignored state
```

Latest execution:

```text
PYTHONPATH=src ./.venv/bin/python -m pytest -> 75 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness evaluate_score_performance --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness evaluate_score_performance --input-json '{"days":90}' --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_news_bundle --input-json '{"topic":"all"}' --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness execute_btc_order --input-json '{"confirm":"CONFIRM_BTC_BINANCE_COINM_ORDER","settings_path":"/private/tmp/halo_swing_kill_switch_settings.json"}' --no-audit -> passed, blocked_reason emergency_kill_switch_enabled
PYTHONPATH=src ./.venv/bin/python -m pytest -> 77 passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 78 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness record_runtime_checkpoint --input-json '{"checkpoint_path":"/private/tmp/halo_swing_runtime_checkpoints.jsonl","audit_log_path":"/private/tmp/halo_swing_checkpoint_audit.jsonl","ledger_path":"/private/tmp/halo_swing_checkpoint_ledger.jsonl","run_id":"manual_smoke"}' --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness evaluate_score_performance --input-json '{"days":90}' --no-audit -> passed, score_calibration present
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness create_document_evidence_card --input-json '{"summary":"FOMC minutes summary says policy remains restrictive but stable.","artifact_ref":"artifact://documents/fomc-minutes-summary.pdf","asset_scope":["QQQ","TQQQ"],"bias":"slightly_bullish","strength":0.57,"confidence":0.68}' --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 79 passed
PYTHONPATH=src ./.venv/bin/python -m pytest -> 80 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_latest_signal_report with include_chart=true and extra_evidence_cards -> passed, multimodal_context.status ok
PYTHONPATH=src ./.venv/bin/python -m pytest -> 81 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness normalize_binance_coinm_account_snapshot --input-json '{"balance":[{"asset":"BTC","balance":"0.25000000","availableBalance":"0.20000000","crossWalletBalance":"0.24000000","crossUnPnl":"0.01000000"}],"positions":[{"symbol":"BTCUSD_PERP","positionAmt":"3","entryPrice":"90000","markPrice":"92000","unRealizedProfit":"0.0065","liquidationPrice":"65000","leverage":"2","marginType":"cross","positionSide":"BOTH"}],"as_of":"2026-05-10T00:00:00Z","coinm_contract_size_usd":100}' --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_latest_signal_report --input-json '{"asset":"TQQQ"}' --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_latest_signal_report --input-json '{"asset":"TQQQ","report_intent":"post_market_review"}' --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_position_review_report --input-json '{"asset":"TQQQ","entry_price":100,"current_price":114,"size":3}' --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
blocked artifact audit -> passed
git status --short --ignored state -> ignored local state/ only
PYTHONPATH=src ./.venv/bin/python -m pytest -> 83 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness preview_btc_order with portfolio_snapshot -> passed, position_effect.effect reduces_long
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
blocked artifact audit -> passed
git status --short --ignored state -> ignored local state/ only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py -> 14 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness evaluate_score_performance --input-json '{"days":90}' --no-audit -> passed, sample_size 18, walk_forward_report.ready true, overfit_guard.status ok
PYTHONPATH=src ./.venv/bin/python -m pytest -> 83 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
blocked artifact audit -> passed
git status --short --ignored state -> ignored local state/ only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py tests/test_tool_registry.py tests/test_health_check.py -> 22 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_cron_prompt_pack --input-json '{"asset":"TQQQ"}' --no-audit -> passed, cron_prompt_guard.status ok
PYTHONPATH=src ./.venv/bin/python -m pytest -> 85 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed, generate_cron_prompt_pack advertised
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
blocked artifact audit -> passed
git status --short --ignored state -> ignored local state/ only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py tests/test_providers.py -> 17 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness calculate_indicators --input-json '{"symbol":"QQQ","timeframe":"4h"}' --no-audit -> passed, timeframe_contract.provider_supports_timeframe true
PYTHONPATH=src ./.venv/bin/python -m pytest -> 86 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness calculate_indicators --input-json '{"symbol":"QQQ","timeframe":"1h"}' --no-audit -> passed, timeframe_contract.provider_supports_timeframe true
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
blocked artifact audit -> passed
git status --short --ignored state -> ignored local state/ only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py tests/test_reporting.py -> 29 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness score_leverage_swing --input-json '{"asset":"TQQQ"}' --no-audit -> passed, component_scores includes pullback and breadth
PYTHONPATH=src ./.venv/bin/python -m pytest -> 86 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
blocked artifact audit -> passed
git status --short --ignored state -> ignored local state/ only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py tests/test_signal_repository.py tests/test_tool_registry.py -> 23 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness label_signal_outcome --input-json '{"invalidated_by_event":true,"invalidating_event_id":"evt_fixture_cpi"}' --no-audit -> passed, outcome INVALIDATED_BY_EVENT
PYTHONPATH=src ./.venv/bin/python -m pytest -> 87 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness label_signal_outcome --input-json '{"price_path":[]}' --no-audit -> passed, outcome NO_DATA
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
blocked artifact audit -> passed
git status --short --ignored state -> ignored local state/ only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py tests/test_providers.py -> 18 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_event_calendar --input-json '{"days":14}' --no-audit -> passed, event_window_summary.next_event_id evt_20260512_cpi
PYTHONPATH=src ./.venv/bin/python -m pytest -> 87 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
blocked artifact audit -> passed
git status --short --ignored state -> ignored local state/ only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py tests/test_providers.py -> 19 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_macro_snapshot --no-audit -> passed, macro_filter_summary present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 88 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
blocked artifact audit -> passed
git status --short --ignored state -> ignored local state/ only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py tests/test_providers.py -> 20 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_news_bundle --input-json '{"topic":"all"}' --no-audit -> passed, news_score_contract present
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness score_leverage_swing --input-json '{"asset":"TQQQ"}' --no-audit -> passed, news_usage_contract present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 89 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
blocked artifact audit -> passed
git status --short --ignored state -> ignored local state/ only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py tests/test_signal_repository.py -> 20 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness record_signal --input-json '{"ledger_path":"/private/tmp/halo_swing_run_journal_ledger.jsonl"}' --no-audit -> passed, run_journal.v1 present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 89 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
blocked artifact audit -> passed
git status --short --ignored state -> ignored local state/ only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py tests/test_providers.py -> 20 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness calculate_indicators --input-json '{"symbol":"QQQ","timeframe":"1d"}' --no-audit -> passed, swing_level_contract present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 89 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
blocked artifact audit -> passed
git status --short --ignored state -> ignored local state/ only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py tests/test_providers.py -> 21 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness score_leverage_swing --input-json '{"asset":"TQQQ"}' --no-audit -> passed, strategy_config_contract present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 90 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
blocked artifact audit -> passed
git status --short --ignored state -> ignored local state/ only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py tests/test_reporting.py -> 33 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness render_chart --input-json '{"symbol":"QQQ","timeframe":"1d","output_dir":"/private/tmp/halo_swing_chart_artifact_contract"}' --no-audit -> passed, chart_artifact.v1 present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 90 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
blocked artifact audit -> passed
git status --short --ignored state -> ignored local state/ only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py tests/test_mvp_tools.py -> 33 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_latest_signal_report --input-json '{"asset":"TQQQ"}' --no-audit -> passed, telegram_report_format.v1 present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 90 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
blocked artifact audit -> passed
git status --short --ignored state -> ignored local state/ only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py -> 19 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness suggest_weight_update --no-audit -> passed, challenger_config.v1 present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 90 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
blocked artifact audit -> passed
git status --short --ignored state -> ignored local state/ only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py -> 19 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_trade_guide --input-json '{"asset":"TQQQ"}' --no-audit -> passed, trade_guide.v1 and time_exit_conditions present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 90 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py tests/test_providers.py -> 21 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_market_snapshot --input-json '{"symbols":["QQQ","SPY","SMH","SOXX","BTC"]}' --no-audit -> passed, market_snapshot.v1 and SOXX core coverage present
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py tests/test_signal_repository.py -> 22 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness label_signal_outcome --input-json '{"price_path":[570.611014,576.260628,706.20175],"time_barrier_days":2,"stop_loss_pct":0.05,"take_profit_pct":0.10}' --no-audit -> passed, signal_label_outcome.v1 metric window present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 91 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py tests/test_reporting.py -> 34 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness evaluate_position --input-json '{"asset":"TQQQ","entry_price":100,"current_price":114,"size":3}' --no-audit -> passed, position_management.v1 present
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py tests/test_providers.py -> 22 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_event_calendar --input-json '{"days":14}' --no-audit -> passed, event_policy.v1 covers CPI/EARNINGS/FOMC/NFP
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py tests/test_reporting.py -> 34 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_news_bundle --input-json '{"topic":"all"}' --no-audit -> passed, news_source_policy.v1 covers required source groups
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py -> 20 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness evaluate_score_performance --input-json '{"days":90}' --no-audit -> passed, deflated_sharpe_proxy.v1 present
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_binance_btc.py -> 19 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/binance_btc.py src/halo_swing_mcp/secret_store.py tests/test_binance_btc.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_binance_credentials_status --no-audit -> passed, binance_credential_policy.v1 present
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness preview_btc_order --input-json '{"side":"BUY","quantity":"1"}' --no-audit -> passed, execution_guard credential_policy present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 92 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
blocked artifact audit -> passed
git status --short --ignored state -> ignored local state/ only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_readiness.py -> 5 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/readiness.py src/halo_swing_mcp/server.py tests/test_readiness.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --no-audit -> passed, live_order_submission blocked with explicit missing approvals
PYTHONPATH=src ./.venv/bin/python -m pytest -> 93 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected and live_order_submission gate present
git diff --check -> passed
blocked artifact audit -> passed
git status --short --ignored state -> ignored local state/ only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_readiness.py -> 6 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/readiness.py src/halo_swing_mcp/server.py tests/test_readiness.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --no-audit -> passed, live_data blocked with market/macro/news missing reasons
PYTHONPATH=src ./.venv/bin/python -m pytest -> 94 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, live_data_source_readiness.v1 present and status blocked as expected
git diff --check -> passed
blocked artifact audit -> passed
git status --short --ignored state -> ignored local state/ only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_readiness.py -> 7 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/readiness.py src/halo_swing_mcp/server.py tests/test_readiness.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --no-audit -> passed, telegram_delivery_readiness.v1 present and blocked without token/gateway
PYTHONPATH=src ./.venv/bin/python -m pytest -> 95 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, telegram_delivery_readiness.v1 present and status blocked as expected
git diff --check -> passed
blocked artifact audit -> passed
git status --short --ignored state -> ignored local state/ only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_readiness.py -> 8 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/readiness.py src/halo_swing_mcp/server.py tests/test_readiness.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --no-audit -> passed, hermes_mcp_config_readiness.v1 present and blocked without config path/registration
PYTHONPATH=src ./.venv/bin/python -m pytest -> 96 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, hermes_mcp_config_readiness.v1 present and status blocked as expected
git diff --check -> passed
blocked artifact audit -> passed
git status --short --ignored state -> ignored local state/ only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py -q -> 21 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/scoring.py tests/test_mvp_tools.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness evaluate_score_performance --input-json '{"days":90}' --no-audit -> passed, sample_size 18 and fixture_oos_window.v1 present
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness evaluate_score_performance --input-json '{"days":180}' --no-audit -> passed, sample_size 34, walk_forward_report.ready true, overfit_guard.status ok
PYTHONPATH=src ./.venv/bin/python -m pytest -> 97 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
blocked artifact audit -> passed
git status --short --ignored state -> ignored local state/ only
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_reporting.py -q -> 14 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/reporting.py tests/test_reporting.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_latest_signal_report --input-json '{"asset":"TQQQ","report_intent":"intraday_risk_watch"}' --no-audit -> passed, sections Target/Decision/Stop/Cautions and telegram required_sections aligned
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_latest_signal_report --input-json '{"asset":"TQQQ","report_intent":"post_market_review"}' --no-audit -> passed, sections Target/Decision/Reasons/Take Profit/Cautions and telegram required_sections aligned
PYTHONPATH=src ./.venv/bin/python -m pytest -> 97 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py -q -> 22 passed
./.venv/bin/ruff check tests/test_mvp_tools.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed, suggest_weight_update advertised
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness suggest_weight_update --no-audit -> passed, challenger_config.v1 present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 98 passed
./.venv/bin/ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py tests/test_runtime_guard.py -q -> 28 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_mvp_tools.py tests/test_runtime_guard.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed, get_runtime_status and record_runtime_checkpoint advertised
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_runtime_status --input-json '{"audit_log_path":"/private/tmp/halo_swing_runtime_manifest_audit.jsonl","ledger_path":"/private/tmp/halo_swing_runtime_manifest_ledger.jsonl"}' --no-audit -> passed, watchdog.v1 and retention resources present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 99 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py tests/test_binance_btc.py -q -> 43 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_mvp_tools.py tests/test_binance_btc.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed, Phase 9 BTC tools advertised
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness preview_btc_order --input-json '{"side":"BUY","quantity":"1"}' --no-audit -> passed, preview only with btc_order_execution_guard.v1 and no order submission
PYTHONPATH=src ./.venv/bin/python -m pytest -> 100 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py tests/test_health_check.py -q -> 27 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_mvp_tools.py tests/test_health_check.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed, 35 capabilities advertised
manifest/health parity check -> passed, manifest_equals_health true and count 35
PYTHONPATH=src ./.venv/bin/python -m pytest -> 100 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_audit.py -q -> 5 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check src/halo_swing_mcp/tools/audit_tools.py tests/test_audit.py -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_audit_summary --input-json '{"audit_log_path":"/private/tmp/halo_swing_audit_contract.jsonl"}' --no-audit -> passed, audit_summary.v1 present
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_audit_log --input-json '{"audit_log_path":"/private/tmp/halo_swing_audit_contract.jsonl","limit":5}' --no-audit -> passed, audit_log.v1 present
PYTHONPATH=src ./.venv/bin/python -m pytest -> 100 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_audit.jsonl -> passed, status blocked as expected
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
```

## 6. 3.348 Integration Readiness Input Normalization Verification - 2026-05-11

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

## 7. 3.349 BTC Risk Settings Input Normalization Verification - 2026-05-11

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

## 8. 3.350 BTC Order Input Normalization Verification - 2026-05-11

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

## 9. 3.351 BTC Portfolio Snapshot Input Normalization Verification - 2026-05-11

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

## 10. 3.352 Binance Credential Input Normalization Verification - 2026-05-11

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

## 11. 3.353 Trading Admin HTTP Input Normalization Verification - 2026-05-11

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

## 12. 3.354 Audit Web Query Input Normalization Verification - 2026-05-11

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

## 13. 3.355 Audit Web Local Bind Guard Verification - 2026-05-11

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

## 14. 3.356 Audit Tool Path Input Normalization Verification - 2026-05-11

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

## 15. 3.357 Runtime Path Input Normalization Verification - 2026-05-11

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

## 16. 3.358 Signal Ledger Path Input Normalization Verification - 2026-05-11

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

## 17. 3.359 Chart Output Path Input Normalization Verification - 2026-05-11

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

## 18. 3.360 Document Evidence Input Normalization Verification - 2026-05-11

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

## 19. 3.361 Document Evidence Control Character Input Normalization Verification - 2026-05-11

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

## 20. 3.362 Report Intent Input Normalization Verification - 2026-05-11

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

## 21. 3.363 Report Identity Control Character Input Normalization Verification - 2026-05-11

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

## 22. 3.364 Scoring Identity Control Character Input Normalization Verification - 2026-05-11

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

## 23. 3.365 Market Tool Control Character Input Normalization Verification - 2026-05-11

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

## 24. 3.366 Report Chart Output Dir Control Character Input Normalization Verification - 2026-05-11

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

## 25. 3.367 Audit Read Control Character Input Normalization Verification - 2026-05-11

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

## 26. 3.368 Readiness Path Control Character Input Normalization Verification - 2026-05-11

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

## 27. 3.369 BTC Risk Path Control Character Input Normalization Verification - 2026-05-11

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

## 28. 3.370 Signal Ledger Path Control Character Input Normalization Verification - 2026-05-11

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

## 29. 3.371 Binance Credential Path Control Character Input Normalization Verification - 2026-05-11

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

## 30. 3.372 BTC Order Text Control Character Input Normalization Verification - 2026-05-11

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

## 31. 3.373 Portfolio Snapshot Text Control Character Input Normalization Verification - 2026-05-11

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

## 32. 3.374 Binance Credential Secret Control Character Input Normalization Verification - 2026-05-11

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

## 33. 3.375 Trading Admin HTTP Control Character Input Normalization Verification - 2026-05-11

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

## 34. 3.376 Runtime Control Character Input Normalization Verification - 2026-05-11

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

## 35. 3.377 Signal Identity Control Character Input Normalization Verification - 2026-05-11

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

## 36. 3.378 Market Symbol List Container Input Contract Verification - 2026-05-11

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py::test_market_indicator_and_chart_tools_normalize_symbol_timeframe_identity tests/test_mvp_tools.py::test_market_indicator_and_chart_tools_reject_invalid_symbol_identity tests/test_mvp_tools.py::test_market_snapshot_rejects_invalid_symbols_container tests/test_mvp_tools.py::test_market_indicator_and_chart_tools_reject_symbol_control_character tests/test_mvp_tools.py::test_harness_rejects_invalid_market_symbols_container_with_failure_audit tests/test_mvp_tools.py::test_harness_rejects_blank_indicator_symbol_with_failure_audit tests/test_mvp_tools.py::test_harness_rejects_indicator_symbol_control_character_with_failure_audit -q -> 12 passed, market snapshot symbols container contract coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_mvp_tools.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py -q -> 107 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -q -> 442 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_3_378_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 37. 3.379 Event Calendar Days Failure Audit Verification - 2026-05-11

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py::test_event_and_news_tools_normalize_public_identity tests/test_mvp_tools.py::test_event_calendar_rejects_invalid_days_identity tests/test_mvp_tools.py::test_harness_rejects_invalid_event_calendar_days_with_failure_audit tests/test_mvp_tools.py::test_harness_rejects_blank_news_topic_with_failure_audit tests/test_mvp_tools.py::test_harness_rejects_news_topic_control_character_with_failure_audit -q -> 10 passed, event calendar invalid days failure-audit coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_mvp_tools.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py -q -> 108 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -q -> 443 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_3_379_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 38. 3.380 Evaluate Score Performance Days Failure Audit Verification - 2026-05-11

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py::test_evaluate_recorded_score_performance_rejects_invalid_days tests/test_mvp_tools.py::test_score_performance_includes_attribution_and_ablation tests/test_mvp_tools.py::test_harness_rejects_invalid_score_performance_days_with_failure_audit -q -> 3 passed, evaluate_score_performance invalid days failure-audit coverage enforced
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_mvp_tools.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py -q -> 109 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -q -> 444 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --no-audit -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --audit-log-path /private/tmp/halo_swing_readiness_3_380_audit.jsonl -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 39. 3.381 Evaluate Score Performance Ledger Path Failure Audit Verification - 2026-05-11

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

## 40. 3.382 Label Signal Ledger Path Failure Audit Verification - 2026-05-11

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

## 41. 3.383 Label Signal Ledger Path Control Character Failure Audit Verification - 2026-05-11

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

## 42. 3.384 Evaluate Score Performance Ledger Path Control Character Failure Audit Verification - 2026-05-11

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

## 43. 3.385 Label Signal Event Boolean Failure Audit Verification - 2026-05-11

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

## 44. 3.386 Label Signal Invalidating Event ID Control Character Failure Audit Verification - 2026-05-11

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

## 45. 3.387 Label Signal Stop Loss Failure Audit Verification - 2026-05-11

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

## 46. 3.388 Label Signal Take Profit Failure Audit Verification - 2026-05-11

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

## 47. 3.389 Label Signal Time Barrier Failure Audit Verification - 2026-05-11

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

## 48. 3.390 Label Signal Signal ID Failure Audit Verification - 2026-05-11

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

## 49. 3.391 Label Signal Invalidating Event ID Failure Audit Verification - 2026-05-11

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

## 50. 3.392 Label Signal Ledger Path Type Failure Audit Verification - 2026-05-11

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

## 51. 3.393 Record Signal Ledger Path Type Failure Audit Verification - 2026-05-11

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

## 52. 3.394 Evaluate Score Performance Ledger Path Type Failure Audit Verification - 2026-05-11

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

## 53. 3.395 Record Signal Object Type Failure Audit Verification - 2026-05-11

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

## 54. 3.396 Label Signal Price Path Type Failure Audit Verification - 2026-05-11

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

## 55. 3.397 Label Signal Price Path Nonpositive Failure Audit Verification - 2026-05-11

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

## 56. 3.398 Label Signal Price Path Nonfinite Failure Audit Verification - 2026-05-11

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

## 57. 3.399 Label Signal Stop Loss Type Failure Audit Verification - 2026-05-11

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

## 58. 3.400 Label Signal Take Profit Nonpositive Failure Audit Verification - 2026-05-11

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

## 59. 3.401 Label Signal Time Barrier Nonpositive Failure Audit Verification - 2026-05-11

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

## 60. 3.402 Label Signal Time Barrier Type Failure Audit Verification - 2026-05-11

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

## 61. 3.403 Label Signal Stop Loss Nonfinite Failure Audit Verification - 2026-05-11

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

## 62. 3.404 Label Signal Take Profit Nonfinite Failure Audit Verification - 2026-05-11

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

## 63. 3.405 Label Signal Invalidating Event ID Type Failure Audit Verification - 2026-05-11

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

## 64. 3.406 Label Signal Signal ID Type Failure Audit Verification - 2026-05-11

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

## 65. 3.407 Record Signal Run ID Type Failure Audit Verification - 2026-05-11

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

## 66. 3.408 Record Signal Created At Blank Failure Audit Verification - 2026-05-11

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

## 67. 3.409 Record Signal Underlying Null Failure Audit Verification - 2026-05-11

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

## 68. 3.410 Record Signal Config Version Blank Failure Audit Verification - 2026-05-11

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

## 69. 3.411 Record Signal Config Hash Type Failure Audit Verification - 2026-05-11

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

## 70. 3.412 Record Signal Config Hash Control Character Failure Audit Verification - 2026-05-11

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

## 71. 3.413 Record Signal Config Version Control Character Failure Audit Verification - 2026-05-11

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

## 72. 3.414 Record Signal Remaining Identity Control Character Failure Audit Verification - 2026-05-11

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

## 73. 3.415 Label Signal Unused Invalidating Event ID Control Character Failure Audit Verification - 2026-05-11

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

## 74. 3.416 Evaluate Score Performance Remaining Days Failure Audit Verification - 2026-05-11

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

## 75. 3.417 Latest Report Extra Evidence Cards Type Failure Audit Verification - 2026-05-12

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

## 76. 3.418 Position Review Report Numeric Input Failure Audit Verification - 2026-05-12

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

## 77. 3.419 Latest Report Identity Type Failure Audit Verification - 2026-05-12

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

## 78. 3.420 Cron Prompt Type Failure Audit Verification - 2026-05-12

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

## 79. 3.421 Score Performance Provided Signals Input Audit Verification - 2026-05-12

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

## 80. 3.422 Latest Report Chart Input Type Failure Audit Verification - 2026-05-12

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

## 81. 3.423 Position Review Asset Type Failure Audit Verification - 2026-05-12

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

## 82. 3.424 Scoring Tool Identity Type Failure Audit Verification - 2026-05-12

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

## 83. 3.425 Scoring Tool Remaining Identity Control Character Audit Verification - 2026-05-12

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

## 84. 3.426 Position Numeric Remaining Failure Audit Verification - 2026-05-12

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

## 85. 3.427 Score Performance Provided Signals Harness Failure Audit Verification - 2026-05-12

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

## 86. 3.428 Public Tool Boundary Failure Audit Verification - 2026-05-12

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_mvp_tools.py::test_score_performance_treats_empty_provided_signals_as_empty_sample tests/test_mvp_tools.py::test_score_performance_rejects_invalid_provided_signals tests/test_mvp_tools.py::test_harness_rejects_invalid_score_performance_signals_with_failure_audit tests/test_mvp_tools.py::test_harness_rejects_remaining_score_performance_signals_with_failure_audit tests/test_tool_registry.py::test_registry_rejects_unexpected_payload_keys_before_dispatch tests/test_tool_registry.py::test_registry_rejects_non_object_payloads_before_dispatch tests/test_tool_registry.py::test_registry_keeps_var_keyword_tools_permissive tests/test_tool_registry.py::test_harness_rejects_unexpected_payload_key_with_failure_audit -q -> 25 passed, public tool-boundary failure-audit coverage enforced
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

## 87. 3.429 Public Tool Input Boundary Failure Audit Verification - 2026-05-12

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

## 88. 3.430 Harness Invalid JSON Failure Audit Verification - 2026-05-12

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

## 89. 3.431 Harness Unreadable Input File Failure Audit Verification - 2026-05-12

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

## 90. 3.432 Harness Input Source Conflict Failure Audit Verification - 2026-05-12

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

## 91. 3.433 Harness Input File Argument Failure Audit Verification - 2026-05-12

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

## 92. 3.434 Harness Audit Log Path Argument Validation Verification - 2026-05-12

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

## 93. 3.435 Harness Argument DEL Control Validation Verification - 2026-05-13

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

## 94. 3.436 Audit Environment Path Validation Verification - 2026-05-13

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

## 95. 3.437 Signal Ledger Environment Path Validation Verification - 2026-05-13

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

## 96. 3.438 Binance Credentials Environment Path Validation Verification - 2026-05-13

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

## 97. 3.439 BTC Risk Environment Path Validation Verification - 2026-05-13

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

## 98. 3.440 Runtime Checkpoint Environment Path Validation Verification - 2026-05-13

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

## 99. 3.441 Hermes Config Environment Path Validation Verification - 2026-05-13

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

## 100. 3.442 Readiness Environment Boolean Normalization Verification - 2026-05-13

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

## 101. 3.443 Runtime Environment Limits Validation Verification - 2026-05-13

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

## 102. 3.444 Binance Recv Window Environment Validation Verification - 2026-05-13

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

## 103. 3.445 Artifact Directory Environment Validation Verification - 2026-05-13

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

## 104. 3.446 Binance Boolean Environment Canonicalization Verification - 2026-05-13

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

## 105. 3.447 Readiness Binance Credentials Environment Path Validation Verification - 2026-05-13

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

## 106. 3.448 Readiness BTC Risk Environment Path Prevalidation Verification - 2026-05-13

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

## 107. 3.449 Binance Execution Boolean Environment Canonicalization Coverage Verification - 2026-05-13

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

## 108. 3.450 Binance Read-Only Boolean Environment Canonicalization Coverage Verification - 2026-05-13

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

## 109. 3.451 Binance Account Snapshot Missing Passphrase Environment Prevalidation Verification - 2026-05-13

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

## 110. 3.452 Trading Admin Status Environment Prevalidation Verification - 2026-05-13

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

## 111. 3.453 Trading Admin Status HTTP Environment Error Handling Verification - 2026-05-13

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

## 112. 3.454 Trading Admin Connectivity HTTP Environment Error Handling Verification - 2026-05-13

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

## 113. 3.455 Trading Admin Account Snapshot HTTP Environment Error Handling Verification - 2026-05-13

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

## 114. 3.456 Trading Admin Order Preview HTTP Environment Error Handling Verification - 2026-05-13

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

## 115. 3.457 Trading Admin Risk-State Reset HTTP Environment Path Validation Verification - 2026-05-13

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

## 116. 3.458 Trading Admin Credentials HTTP Environment Path Validation Verification - 2026-05-13

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

## 117. 3.459 Trading Admin Risk-Settings HTTP Environment Path Validation Verification - 2026-05-13

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

## 118. 3.460 Trading Admin Non-Object JSON Payload Boundary Verification - 2026-05-13

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

## 119. 3.461 Trading Admin Malformed JSON Payload Boundary Verification - 2026-05-13

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

## 120. 3.462 Trading Admin Content-Length Boundary Verification - 2026-05-13

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

## 121. 3.463 Trading Admin Content-Type Boundary Verification - 2026-05-13

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

## 122. 3.464 Trading Admin Content-Type Compatibility Verification - 2026-05-13

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

## 123. 3.465 Trading Admin UTF-8 Body Boundary Verification - 2026-05-13

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

## 124. 3.466 Trading Admin Bind Host Guard Verification - 2026-05-13

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

## 125. 3.467 Trading Admin Port Guard Verification - 2026-05-13

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

## 126. 3.468 Audit Web Port Guard Verification - 2026-05-13

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

## 127. 3.469 Audit Web Audit Log Path Guard Verification - 2026-05-13

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

## 128. 3.470 Audit Web Summary Path Guard Verification - 2026-05-13

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

## 129. 3.471 Audit Web Events Path Guard Verification - 2026-05-13

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

## 130. 3.472 Runtime Checkpoint Invalid Input No-Write Guard Verification - 2026-05-13

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

## 131. 3.473 Runtime Checkpoint Control Character No-Write Guard Verification - 2026-05-13

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_runtime_guard.py::test_runtime_checkpoint_rejects_control_character_inputs -q -> 1 passed, control-character runtime checkpoint inputs do not create checkpoint/audit/ledger files before validation failure
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

## 132. 3.474 Runtime Status Control Character No-Write Guard Verification - 2026-05-13

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_runtime_guard.py::test_runtime_status_rejects_path_control_character_inputs -q -> 1 passed, control-character runtime status path inputs do not create audit/ledger files before validation failure
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

## 133. 3.475 Runtime Status Invalid Input No-Write Guard Verification - 2026-05-13

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_runtime_guard.py::test_runtime_status_rejects_invalid_public_inputs -q -> 1 passed, invalid runtime status public inputs do not create audit/ledger files before validation failure
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

## 134. 3.476 Runtime Status Harness Failure Ledger No-Write Guard Verification - 2026-05-13

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_runtime_guard.py::test_harness_rejects_invalid_runtime_status_input_with_failure_audit tests/test_runtime_guard.py::test_harness_rejects_invalid_runtime_path_input_with_failure_audit -q -> 2 passed, harness runtime status validation failures record failure audit without creating requested ledger files
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

## 135. 3.477 Runtime Checkpoint Harness Invalid Input No-Write Guard Verification - 2026-05-13

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_runtime_guard.py::test_harness_rejects_invalid_runtime_checkpoint_input_with_failure_audit -q -> 1 passed, harness runtime checkpoint invalid include_readiness records failure audit without creating checkpoint/ledger files
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_runtime_guard.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_runtime_guard.py -q -> 22 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -q -> 628 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 136. 3.478 Runtime Checkpoint Harness Path No-Fallback Guard Verification - 2026-05-13

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_runtime_guard.py::test_harness_rejects_invalid_runtime_checkpoint_path_without_fallback -q -> 1 passed, harness runtime checkpoint blank checkpoint_path records failure audit without default state fallback or requested ledger file creation
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_runtime_guard.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_runtime_guard.py -q -> 23 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -q -> 629 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 137. 3.479 Runtime Checkpoint Harness Path Control No-Fallback Guard Verification - 2026-05-13

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_runtime_guard.py::test_harness_rejects_runtime_checkpoint_path_control_character_without_fallback -q -> 1 passed, harness runtime checkpoint control-character checkpoint_path records failure audit without malformed checkpoint file, default state fallback, or requested ledger file creation
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_runtime_guard.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_runtime_guard.py -q -> 24 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -q -> 630 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 138. 3.480 Runtime Checkpoint Harness Audit Path No-Write Guard Verification - 2026-05-13

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_runtime_guard.py::test_harness_rejects_invalid_runtime_checkpoint_audit_path_without_checkpoint -q -> 1 passed, harness runtime checkpoint blank audit_log_path records failure audit without checkpoint or requested ledger file creation
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_runtime_guard.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_runtime_guard.py -q -> 25 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -q -> 631 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 139. 3.481 Runtime Checkpoint Harness Audit Path Control No-Write Guard Verification - 2026-05-13

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_runtime_guard.py::test_harness_rejects_runtime_checkpoint_audit_path_control_character_without_checkpoint -q -> 1 passed, harness runtime checkpoint control-character audit_log_path records failure audit without malformed runtime audit, checkpoint, or requested ledger file creation
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_runtime_guard.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_runtime_guard.py -q -> 26 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -q -> 632 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 140. 3.482 Runtime Checkpoint Harness Ledger Path No-Write Guard Verification - 2026-05-13

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_runtime_guard.py::test_harness_rejects_invalid_runtime_checkpoint_ledger_path_without_checkpoint -q -> 1 passed, harness runtime checkpoint blank ledger_path records failure audit without checkpoint, default state fallback, or malformed ledger file creation
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_runtime_guard.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_runtime_guard.py -q -> 27 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -q -> 633 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 141. 3.483 Runtime Checkpoint Harness Ledger Path Control No-Write Guard Verification - 2026-05-13

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_runtime_guard.py::test_harness_rejects_runtime_checkpoint_ledger_path_control_character_without_checkpoint -q -> 1 passed, harness runtime checkpoint control-character ledger_path records failure audit without checkpoint or malformed ledger file creation
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_runtime_guard.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_runtime_guard.py -q -> 28 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -q -> 634 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 142. 3.484 Runtime Checkpoint Harness Run ID No-Write Guard Verification - 2026-05-13

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_runtime_guard.py::test_harness_rejects_invalid_runtime_checkpoint_run_id_without_checkpoint -q -> 1 passed, harness runtime checkpoint blank run_id records failure audit without checkpoint or ledger file creation
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_runtime_guard.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_runtime_guard.py -q -> 29 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -q -> 635 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 143. 3.485 Runtime Checkpoint Harness Run ID Type No-Write Guard Verification - 2026-05-13

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_runtime_guard.py::test_harness_rejects_runtime_checkpoint_run_id_type_without_checkpoint -q -> 1 passed, harness runtime checkpoint non-string run_id records failure audit without checkpoint or ledger file creation
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_runtime_guard.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_runtime_guard.py -q -> 30 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -q -> 636 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 144. 3.486 Runtime Checkpoint Harness Checkpoint Path Type No-Write Guard Verification - 2026-05-13

```text
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_runtime_guard.py::test_harness_rejects_runtime_checkpoint_path_type_without_fallback -q -> 1 passed, harness runtime checkpoint non-string checkpoint_path records failure audit without default state fallback or ledger file creation
PYTHONPATH=src ./.venv/bin/python -m ruff check tests/test_runtime_guard.py -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_runtime_guard.py -q -> 31 passed
PYTHONPATH=src ./.venv/bin/python -m ruff check . -> passed
PYTHONPATH=src ./.venv/bin/python -m pytest -q -> 637 passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check -> passed
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness -> passed, status blocked as expected
git diff --check -> passed
git status --short -- data artifacts src/halo_swing_mcp/broker src/halo_swing_mcp/live_adapters migrations -> passed, no blocked-path changes
git status --short --ignored state -> ignored local state/ only
```

## 145. Next Concrete Actions

Choose one of:

```text
1. Provide Hermes config path and Telegram credential/gateway choice.
2. Provide Binance testnet credentials/passphrase procedure for read-only smoke.
3. Approve or revise MIGRATION_GO / REPOSITORY_GO.
4. Choose live data source/API-key policy.
5. Continue offline hardening for additional Phase 6 fixture coverage or report variants.
```
