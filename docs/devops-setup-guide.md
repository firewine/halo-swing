# DevOps Setup Guide

> Purpose: local development, dependency setup, smoke commands, and Hermes MCP registration notes.
> Owner: DevOps virtual team.
> Rule: this guide may contain operational commands, but architecture and phase scope remain in `docs/halo-swing-development-plan.md`.

## Current Baseline

```yaml
runtime: Python 3.11
environment: .venv
dependencies: requirements.txt
mcp_stack: official MCP Python SDK / FastMCP
server_status: offline_mvp_tools_implemented
harness_status: parameterized_cli_harness_implemented
storage_schema_status: sqlite_migration_and_explicit_repository_path_verified
audit_log_status: runtime_jsonl_with_local_web_viewer
runtime_guard_status: jsonl_retention_and_failure_watchdog
runtime_checkpoint_status: append_only_jsonl_checkpoint_tool
report_harness_status: deterministic_latest_signal_report_snapshot
position_review_report_status: deterministic_position_review_report_snapshot
delivery_preview_status: offline_hermes_telegram_payload_preview
evidence_guard_status: report_summary_limits_and_conflict_flags
multimodal_evidence_status: modality_and_portable_artifact_refs
document_summary_input_status: guarded_manual_document_summary_card
multimodal_report_status: optional_chart_ref_and_code_guard
integration_readiness_status: offline_gate_readiness_harness
hermes_readiness_status: config_path_and_mcp_registration_gate
telegram_readiness_status: bot_token_or_gateway_gate_no_send
live_data_readiness_status: market_macro_news_source_policy_gate
score_feedback_status: fixture_90d_oos_walk_forward_guard
trading_admin_status: local_only_btc_coin_m_settings_and_encrypted_credentials
btc_kill_switch_status: local_risk_setting_blocks_execution
btc_portfolio_snapshot_status: guarded_offline_coin_m_snapshot_normalizer
btc_credential_policy_status: trade_only_no_withdraw_contract
btc_live_order_readiness_status: explicit_approval_gate_blocked_by_default
live_network_tests: disabled
default_data_mode: fixture
```

## Local Setup

From the repository root:

```bash
/opt/homebrew/bin/python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pip check
```

Quick dependency smoke:

```bash
python -c "from mcp.server.fastmcp import FastMCP; print('fastmcp ok')"
```

## Secrets And Local Files

```yaml
commit_allowed:
  - requirements.txt
  - .env.example
  - docs/devops-setup-guide.md

commit_forbidden:
  - .venv/
  - .env
  - .env.*
  - API keys
  - local reports, artifacts, SQLite data files
  - runtime logs, state dumps, checkpoints
```

`.gitignore` must continue to exclude `.venv/`, local `.env` files, local data, artifacts, reports, state dumps, checkpoints, and logs.

Runtime dotenv loading:

```text
precedence:
  1. exported environment variables
  2. launch-directory .env
  3. repo-root .env

offline_test_isolation:
  - set HALO_SWING_DISABLE_DOTENV=true to ignore dotenv files
```

Normal local setup is to copy `.env.example` to the repository root as `.env`
and fill only the required API keys or config values. Hermes or MCP launchers
may start from another working directory; repo-root `.env` values are still
read. A launch-directory `.env` can override repo-root values for local runner
experiments. Default pytest runs set `HALO_SWING_DISABLE_DOTENV=true` so
operator secrets in local dotenv files cannot trigger live providers or network
calls during offline tests. The isolation flag may be exported or placed in
`.env`; when it is true, the runtime ignores other dotenv values.

## Offline MVP Server And Harness Commands

Verified offline smoke commands:

```bash
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_market_snapshot --input-json '{"symbols":["QQQ","TQQQ","BTC"]}'
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness calculate_indicators --input-json '{"symbol":"QQQ"}'
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness calculate_indicators --input-json '{"symbol":"QQQ","timeframe":"4h"}'
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness score_leverage_swing --input-json '{"asset":"TQQQ"}'
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_trade_guide --input-json '{"asset":"TQQQ"}'
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness evaluate_score_performance --input-json '{"days":90}'
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness create_document_evidence_card --input-json '{"summary":"FOMC minutes summary says policy remains restrictive but stable.","artifact_ref":"artifact://documents/fomc-minutes-summary.pdf","asset_scope":["QQQ","TQQQ"]}'
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_latest_signal_report --input-json '{"asset":"TQQQ"}'
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_position_review_report --input-json '{"asset":"TQQQ","entry_price":100,"current_price":114,"size":3}'
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_cron_prompt_pack --input-json '{"asset":"TQQQ"}'
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_latest_signal_report --input-json '{"asset":"TQQQ","include_chart":true,"chart_output_dir":"artifacts/charts"}'
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_audit_summary --input-json '{"audit_log_path":"state/audit_log.jsonl"}' --audit-log-path state/audit_log.jsonl
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_runtime_status --input-json '{"audit_log_path":"state/audit_log.jsonl","ledger_path":"state/signal_ledger.jsonl"}'
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness record_runtime_checkpoint --input-json '{"checkpoint_path":"state/runtime_checkpoints.jsonl","audit_log_path":"state/audit_log.jsonl","ledger_path":"state/signal_ledger.jsonl"}'
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness normalize_binance_coinm_account_snapshot --input-json '{"balance":[{"asset":"BTC","balance":"0.25","availableBalance":"0.2"}],"positions":[{"symbol":"BTCUSD_PERP","positionAmt":"3","entryPrice":"90000","markPrice":"92000"}]}'
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness preview_btc_order --input-json '{"side":"BUY","quantity":"1"}'
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_btc_risk_status
PYTHONPATH=src ./.venv/bin/python -m pytest
PYTHONPATH=src ./.venv/bin/python -m ruff check .
```

`generate_trade_guide` should include `trade_guide_contract.schema_version`
`trade_guide.v1`, `guide.time_exit_conditions`, and a `trade_guide_guard` with
no order submission or live data requirement.

`evaluate_position` should include `position_management_contract.schema_version`
`position_management.v1` and a `position_management_guard` proving the
WAIT/TRIM/EXIT/STOP decision is numeric-authoritative and does not submit orders.

`get_market_snapshot` should include `market_snapshot_contract.schema_version`
`market_snapshot.v1`, core fixture assets QQQ/SPY/SMH/SOXX/BTC, and a guard
showing fixture market snapshots do not implicitly persist feature-store rows.
SQLite feature persistence is only active through explicit repository commands
that pass `database_path`.

`get_event_calendar` should include `event_policy_contract.schema_version`
`event_policy.v1`, with CPI/FOMC/NFP/EARNINGS coverage and per-event danger
windows. The fixture policy guard must stay offline and no-network.

`get_news_bundle` should include `news_source_policy_contract.schema_version`
`news_source_policy.v1`, with fixture coverage for Fed, Treasury, White House,
EIA, Iran/Hormuz, and AI/semiconductor source groups. The source policy guard
must stay offline and no-network.

`label_signal_outcome` should include `signal_label_outcome.v1` with metric
fields `mfe`, `mae`, and `realized_r`. MFE/MAE are scoped to
`price_path[:time_barrier_days]`, so prices after the time barrier do not change
the label metrics.

`evaluate_score_performance` should include `overfit_guard.deflated_sharpe_proxy`
with schema `deflated_sharpe_proxy.v1`. This is an offline conservative proxy,
not an exact Deflated Sharpe Ratio, and it must not enable automatic promotion.

`record_signal` defaults to a local JSONL runtime ledger. Use an ignored or
temporary path during development:

```bash
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness record_signal --input-json '{"ledger_path":"state/signal_ledger.jsonl"}'
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness label_signal_outcome --input-json '{"ledger_path":"state/signal_ledger.jsonl"}'
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness evaluate_score_performance --input-json '{"ledger_path":"state/signal_ledger.jsonl"}'
```

After `MIGRATION_GO` and `REPOSITORY_GO`, the same recording tools also support
an explicit SQLite repository path. Keep the file under ignored local state or a
temporary directory; do not commit SQLite files. `HALO_SWING_DATABASE_URL`
remains blank by default because env-based repository selection is not wired in
this slice.

```bash
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness record_signal --input-json '{"database_path":"state/halo_swing.sqlite"}'
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness label_signal_outcome --input-json '{"database_path":"state/halo_swing.sqlite"}'
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_signal_replay_bundle --input-json '{"signal_id":"sig_fixture_20260511_tqqq","database_path":"state/halo_swing.sqlite"}'
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_latest_signal_record --input-json '{"database_path":"state/halo_swing.sqlite","asset":"TQQQ","timeframe":"swing_3d_10d"}'
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_latest_signal_report --input-json '{"database_path":"state/halo_swing.sqlite","asset":"TQQQ","timeframe":"swing_3d_10d"}'
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_storage_health --input-json '{"database_path":"state/halo_swing.sqlite"}'
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness apply_storage_migrations --input-json '{"database_path":"state/halo_swing.sqlite"}'
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness evaluate_score_performance --input-json '{"database_path":"state/halo_swing.sqlite"}'
```

The SQLite path applies migrations idempotently, stores `run_journal`,
`strategy_config`, `feature_store`, `evidence_card`, `artifact_ref`,
`signal_ledger`, and `label_store` rows, lets `get_signal_replay_bundle`
return replay sections plus structured missing-link errors, lets
`get_latest_signal_record` read the latest matching asset/timeframe signal for
report-oriented checks, lets `generate_latest_signal_report` build from the
stored latest signal and its label status when labeled, and exposes
`get_storage_health` for migration/table checks.
`apply_storage_migrations` can apply the same idempotent migration runner
explicitly before repository writes. The default JSONL path remains available
for lightweight local smoke runs.

SQLite repository files are local operational state. This project does not yet
ship backup tooling or retention automation for SQLite repositories. Before
keeping a local database beyond smoke testing, place it under ignored local
state or another backup-controlled path, snapshot it with SQLite-safe tooling
outside the repository, and rotate or delete old local copies manually according
to your local retention policy. Do not commit backups, dumps, WAL/SHM sidecars,
or copied database files.

P1 storage/repository final verification is local and offline:

```bash
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_storage_migrations.py tests/test_signal_repository.py -q
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_contracts.py tests/test_mvp_tools.py tests/test_tool_registry.py -q
PYTHONPATH=src ./.venv/bin/python -m pytest
PYTHONPATH=src ./.venv/bin/python -m ruff check .
```

The verification path must stay fixture/tmp_path based: no live network calls,
no Hermes runtime start, no Telegram send, no broker/order submission, no
automatic `.env` database activation, and no committed SQLite data files.

P1 storage/docs_devops close checklist:

```text
required_evidence:
  - MIGRATION_GO and REPOSITORY_GO are recorded in the SSOT
  - migration, repository, SQLite command guide, backup/retention note, and final verification guide records are verified
  - task contract mirror matches `.codex/tasks/current.json` and `docs/codex-task.json`
  - full pytest, ruff, and health_check pass from a clean worktree
  - DevOps guide still documents explicit `database_path` SQLite usage
  - `HALO_SWING_DATABASE_URL` remains blank unless a later env-activation gate approves it
  - no live adapters, broker/order submission, Hermes runtime start, Telegram send, scheduler, or committed SQLite artifacts are added
```

If any item is missing, keep P1 storage/docs_devops open and continue with the
next explicit SSOT slice instead of treating the phase as closed.

Current P1 storage/docs_devops close readiness is verified by the SSOT storage
records from 4.057 through 4.063 plus the mirrored task contract. This closes
only the P1 storage/docs_devops checklist evidence; it does not approve
live_adapters, broker/order submission, Hermes runtime start, Telegram send,
scheduler execution, env-based DB activation, or committed SQLite artifacts.

Indicator timeframe smoke:

```bash
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness calculate_indicators --input-json '{"symbol":"QQQ","timeframe":"1d"}'
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness calculate_indicators --input-json '{"symbol":"QQQ","timeframe":"4h"}'
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness calculate_indicators --input-json '{"symbol":"QQQ","timeframe":"1h"}'
```

The replay provider exposes only `1d`, `4h`, and `1h`. Unsupported timeframes
raise a deterministic validation error and do not call live adapters.

Score feedback OOS smoke:

```bash
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness evaluate_score_performance --input-json '{"days":90}'
```

The default fixture window returns `out_of_sample_report` with a deterministic
in-sample/OOS split, `walk_forward_report` with rolling fixture folds,
`overfit_guard`, and `score_calibration` with per-bin expected versus realized
take-profit rates. This report is evidence only; champion promotion still
requires explicit approval.

Audit log viewer:

```bash
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.audit_web --host 127.0.0.1 --port 8765 --audit-log-path state/audit_log.jsonl
```

Open `http://127.0.0.1:8765`. JSON APIs are available at:

```text
/api/events?limit=100&resource_id=score_leverage_swing&outcome=success
/api/summary
```

Audit events are append-only JSONL records with redacted sensitive keys such as
`api_key`, `authorization`, `password`, `passphrase`, `secret`, and `token`.

Runtime guard:

```bash
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_runtime_status --input-json '{"audit_log_path":"state/audit_log.jsonl","ledger_path":"state/signal_ledger.jsonl"}'
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_runtime_status --input-json '{"audit_log_path":"state/audit_log.jsonl","ledger_path":"state/signal_ledger.jsonl","apply_retention":true}'
```

Default local retention keeps the newest 1000 records and caps each JSONL file
at roughly 5 MB. Repeated tool failures trigger degraded mode when 3 failures
appear inside the most recent 20 audit events.

Runtime checkpoint:

```bash
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness record_runtime_checkpoint --input-json '{"checkpoint_path":"state/runtime_checkpoints.jsonl","audit_log_path":"state/audit_log.jsonl","ledger_path":"state/signal_ledger.jsonl"}'
```

This appends one local JSONL checkpoint with runtime status, watchdog resources,
and optional integration readiness. It does not install a scheduler, call
networks, send Telegram messages, or return secret values. Keep
`state/runtime_checkpoints.jsonl` ignored like other local runtime files.

Position review report:

```bash
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_position_review_report --input-json '{"asset":"TQQQ","entry_price":100,"current_price":114,"size":3}'
```

This wraps `evaluate_position` into a Hermes/Telegram-facing structured report.
The payload keeps `position_review` as the numeric authority, includes
Position/Decision/Rationale/Stop/Take Profit/Risk sections, and performs no
network call or order submission.

Hermes cron prompt pack:

```bash
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_cron_prompt_pack --input-json '{"asset":"TQQQ"}'
```

This returns prompt templates for `pre_market_swing_report`,
`intraday_risk_watch`, `post_market_review`, and `position_review`. It does not
install a scheduler, run cron, send Telegram messages, call networks, submit
orders, or require credentials.

Report delivery preview:

```text
generate_latest_signal_report.delivery_preview
generate_position_review_report.delivery_preview
```

The preview returns Hermes payload metadata and Telegram message chunks under
the same no-network contract used by the report guards. It is safe to inspect
offline and does not require Telegram credentials.

Report evidence guard:

```text
generate_latest_signal_report.evidence_contract
generate_latest_signal_report.evidence_context
generate_latest_signal_report.evidence_guard
```

The guard caps reason/evidence summaries, records acknowledged conflict flags
such as event-risk-vs-long-bias, and verifies that risk warnings are reflected
in the Cautions section.

Multimodal evidence metadata:

```bash
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_news_bundle --input-json '{"topic":"all"}'
```

Fixture evidence cards include `modality`, portable `artifact_ref`, bundle-level
`modality_counts`, and `multimodal_evidence_guard`. This does not parse PDFs,
call Hermes multimodal APIs, or write evidence artifacts.

Caller-supplied PDF/document summary input:

```bash
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness create_document_evidence_card --input-json '{"summary":"FOMC minutes summary says policy remains restrictive but stable.","artifact_ref":"artifact://documents/fomc-minutes-summary.pdf","asset_scope":["QQQ","TQQQ"]}'
```

This normalizes a manual document summary into one evidence card with
`document_summary_input_contract`, `document_summary_input_guard`,
`modality_counts`, `artifact_refs`, and `multimodal_evidence_guard`. It does not
read files, parse PDFs, call networks, return raw documents, or send anything to
Hermes/Telegram.

Multimodal report chart refs:

```bash
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_latest_signal_report --input-json '{"asset":"TQQQ","include_chart":true,"chart_output_dir":"artifacts/charts"}'
```

This writes a local chart PNG to an ignored artifact path, attaches `chart_ref`
to `latest_signal_report`, and returns `chart_code_guard`. The guard records
that chart images are visual context only; indicator values, stop levels, and
take-profit levels remain code-calculated fields.

When `generate_latest_signal_report` receives `extra_evidence_cards`, the report
also returns `multimodal_context`. This context links chart refs and manual
document evidence cards while keeping `latest_signal_report` as the numeric
authority and recording that no Hermes multimodal call or network call occurred.

Integration readiness:

```bash
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness
```

local setup checklist:

```bash
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_setup_checklist --no-audit
```

live data API-key status, without network calls:

```bash
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_live_data_api_key_status --no-audit
```

live data provider route, without provider network calls:

```bash
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_live_data_provider_route --no-audit
```

live data smoke result validation:

```bash
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness validate_live_data_smoke_result --input-file /path/to/live_data_smoke_payloads.json --no-audit
```

one-shot live data smoke runner:

```bash
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness run_live_data_smoke --input-json '{"symbols":["QQQ"],"topic":"macro"}' --no-audit
```

one-shot integration environment smoke runner:

```bash
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness run_integration_smoke --input-json '{"symbols":["QQQ"],"topic":"macro"}' --no-audit
```

one-shot live signal workflow smoke runner:

```bash
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness run_live_signal_workflow_smoke --input-json '{"asset":"TQQQ","timeframe":"swing_3d_10d"}' --no-audit
```

one-shot live recording smoke runner:

```bash
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness run_live_recording_smoke --input-json '{"asset":"TQQQ","timeframe":"swing_3d_10d"}' --no-audit
```

one-shot API-key pipeline smoke runner:

```bash
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness run_api_key_pipeline_smoke --summary-only --no-audit
```

API-key-backed live provider HTTP calls use
`HALO_SWING_LIVE_HTTP_TIMEOUT_SECONDS` with a default of `10` seconds. Keep the
default unless your local network needs a shorter or longer provider smoke
timeout; non-positive values are rejected during settings load.

The readiness and checklist commands do not call networks or return secret
values. They report which future gates are still blocked for Hermes, Telegram,
DB migration/repository, Binance testnet read-only smoke, live order submission,
and live data adapters. They can read readiness inputs from exported environment
variables, a launch-directory `.env`, or the repo-root `.env` using the
precedence documented above. The checklist payload also includes
`live_data_setup_summary` so API-key-only setup shows key readiness, provider
route status, selected provider classes, missing keys, and the one-shot
`run_api_key_pipeline_smoke` command without returning secret values. The
summary includes `ready_to_run_live_smoke`, `next_smoke_command`, and a no-secret
`provider_family_summary` with configured/missing live data provider families,
`provider_setup_actions` with provider-level preferred keys, next setup actions,
and no-secret `smoke_command` objects, `provider_smoke_plan` with per-provider
smoke readiness, `preferred_env_key`, `accepted_env_keys`, and final pipeline
smoke status, and a no-secret
`dotenv_template` with repo-root `.env` entries for Polygon, FRED, and NewsAPI
so the setup payload itself shows what to fill before running smoke commands.
It also includes `dotenv_file_status` so the payload shows
whether `.env.example` and repo-root `.env` exist, the next setup action, and
the repo-local copy command hint without writing files or returning secret
values. `next_operator_action` summarizes the single local action to copy
`.env`, fill API keys, run provider smokes, or run the one-shot smoke without
returning secret values. When provider smokes are next, it includes
`next_provider_smoke` so the first provider smoke command is visible without
reading the full provider list. `live_data_setup_steps` orders the local setup path as dotenv
preparation, live data API-key entry, provider smoke verification, and the
one-shot pipeline smoke. It also
includes `live_data_smoke_commands` for `get_market_snapshot`,
`get_macro_snapshot`, and `get_news_bundle`. After filling the matching API keys,
run those repo-local harness commands to verify the live provider outputs and
boundary contracts. The smoke commands are read-only and return no secret values,
but they can call provider networks when the configured keys select live
providers. If an individual provider smoke hits a provider or network exception,
it returns a no-secret `conflict` payload with the tool name and exception type
only, so URLs, exception messages, and API key values do not leak into smoke
output. Use
`validate_live_data_smoke_result` on the collected smoke payloads to verify
`live_data_required`, `network_call`, live guard checks, and secret-return
metadata offline. Use `get_live_data_api_key_status` before the first live smoke
when you only need to confirm that supported Polygon, FRED, and NewsAPI aliases
are configured; it reports key names, missing provider families,
provider-level `preferred_env_key`, `setup_status`, `next_setup_action`,
`provider_family_summary`, the no-secret `dotenv_template`, and
`dotenv_file_status` with the next setup action, `next_operator_action` with
the single local action to copy `.env`, fill API keys, run provider smokes, or
run the one-shot smoke, plus `next_provider_smoke` when provider smokes are next,
and `live_data_setup_steps`, but never secret values. Use
`get_live_data_provider_route` when you need to confirm that the actual
`get_market_data_provider` factory selected Polygon, FRED, and NewsAPI from
those keys without making provider network calls. Use
`run_live_data_smoke` for the same validation in one command after filling the
market, macro, and news API keys; its payload now includes the same no-network
provider route evidence and `live_data_setup_summary` before provider smoke
outputs. Successful direct provider smoke rows are aggregated as no-secret
`provider_smoke_summaries` with `provider_smoke_summary_count`, and the API-key
pipeline `live_data_smoke_summary` mirrors those fields so one-shot smoke output
shows each provider success contract without opening nested smoke payloads. Use
`run_integration_smoke` to combine offline readiness gates and the live data
smoke result without starting Hermes, sending Telegram messages, submitting
orders, or returning secrets. Its top-level `provider_route_summary` mirrors the
live data smoke route evidence, and `live_data_setup_summary` shows API-key
setup readiness for easier setup triage. After provider-level smoke passes, use
`run_live_signal_workflow_smoke` to verify the same API-key-backed live
boundary reaches `score_leverage_swing`, `generate_trade_guide`,
`evaluate_position`, and `generate_latest_signal_report` without starting
Hermes, sending Telegram messages, submitting orders, mutating state, or
returning secrets. Its payload also includes `live_data_setup_summary` so direct
workflow smoke runs show API-key setup readiness, selected provider route
evidence, and the next smoke command without exposing secret values. Use
`run_live_recording_smoke` to verify that a generated live signal can also pass
through `record_signal` with live run-journal metadata. Its payload also
includes `live_data_setup_summary` so recording smoke runs show API-key setup
readiness, selected provider route evidence, and the next smoke command without
exposing secret values.
By default it uses an ephemeral JSONL ledger and leaves no runtime file; provide
`ledger_path` only when you intentionally want a retained local smoke ledger.
Use `run_api_key_pipeline_smoke` as the single post-setup check after filling
API keys; it combines live-data readiness, provider smoke, signal workflow smoke,
and recording smoke while still avoiding Hermes runtime starts, Telegram sends,
order submissions, retained state, and secret returns. The pipeline payload also
includes top-level `next_operator_action`, `setup_status_summary`,
`api_key_next_action_summary`, `api_key_requirements_summary`,
`api_key_command_summary`,
`api_key_operator_checklist`, `api_key_pipeline_stage_summary`,
`api_key_pipeline_check_summary`, `live_data_setup_summary`, and a provider
route summary, then fails the route readiness check until all supported
live-data provider keys are configured. The top-level `readiness_summary` mirrors
`api_key_setup_status`, `api_key_status`, `provider_route_status`,
`ready_to_run_live_smoke`, `next_setup_step`, `next_operator_action_name`, and
the no-secret `next_operator_action` separately from broader integration gates.
When the mirrored next action carries provider smoke or recovery env-key hints,
`readiness_summary` also includes `preferred_env_key` and `accepted_env_keys`
without returning key values.
Pass `--summary-only` when you want the compact harness response without editing
the input JSON. For MCP callers, set `summary_only=true` or `"summary_only":true`
in the request payload for the same compact response:

```bash
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness run_api_key_pipeline_smoke --summary-only --no-audit
```

The compact response uses `api_key_pipeline_smoke_summary_only.v1` and keeps
top-level `next_operator_action`, `readiness_summary`,
`api_key_integration_status_summary`,
`api_key_next_action_summary`,
`api_key_operator_checklist_summary`, `setup_status_summary`,
`live_data_setup_summary`, `api_key_requirements_summary`,
`api_key_command_summary`, `api_key_setup_file_summary`,
`api_key_dotenv_loading_summary`, `api_key_pipeline_failure_summary`,
`api_key_pipeline_stage_summary`, `api_key_pipeline_check_summary`,
`api_key_provider_selection_summary`, `api_key_provider_recovery_summary`,
`api_key_live_http_timeout_summary`, `provider_route_summary`, `checks`, and
safety flags while omitting nested full smoke sections.
It mirrors the same no-secret provider route status as top-level
`api_key_provider_route_summary_schema_version`,
`api_key_provider_route_summary_status`,
`api_key_provider_route_summary_provider_factory`,
`api_key_provider_route_summary_selected_provider_classes`,
`api_key_provider_route_summary_selected_provider_class_count`,
`api_key_provider_route_summary_missing_keys`,
`api_key_provider_route_summary_missing_key_count`,
`api_key_provider_route_summary_network_call`, and
`api_key_provider_route_summary_secret_values_returned`, so compact clients can
show selected live/replay provider state and missing route keys without opening
the nested summary.
It mirrors `api_key_pipeline_check_summary`
(`api_key_pipeline_check_summary.v1`) as top-level `api_key_check_status`,
`api_key_check_count`, `api_key_check_passed_count`,
`api_key_check_failed_count`, `api_key_check_failed_keys`,
`api_key_check_tools_with_failures`, `api_key_check_tool_failure_counts`,
`api_key_check_first_failed_tool`, `api_key_check_first_failed_name`,
`api_key_check_first_failed_key`, `api_key_check_first_failed_expected`,
`api_key_check_first_failed_actual`,
`api_key_check_first_failed_provider_family`,
`api_key_check_first_failed_provider`,
`api_key_check_first_failed_smoke_command_name`,
`api_key_check_first_failed_preferred_env_key`,
`api_key_check_first_failed_accepted_env_keys`,
`api_key_check_first_failed_secret_values_returned`,
`api_key_check_network_call`, `api_key_check_mutates_local_state`, and
`api_key_check_secret_values_returned`, so compact clients can show failed check
context and safety state without opening the nested summary or exposing secret
values.
The summary-only top-level provider smoke aggregates keep
`provider_smoke_summaries` and `provider_smoke_summary_count` copied from the
omitted `live_data_smoke_summary`, so compact output still shows provider
success contracts/checks without returning secret values.
The summary-only provider smoke status aggregate also exposes
`provider_smoke_success_count`, `provider_smoke_all_successful`,
`provider_smoke_success_provider_families`,
`provider_smoke_success_providers`, and
`provider_smoke_success_smoke_command_names` so compact output shows which live
provider smokes succeeded without scanning nested sections.
It also mirrors the first successful provider smoke as compact scalars:
`provider_smoke_first_success_provider_family`,
`provider_smoke_first_success_provider`,
`provider_smoke_first_success_smoke_command_name`,
`provider_smoke_first_success_status`,
`provider_smoke_first_success_expected_live_contract`,
`provider_smoke_first_success_expected_live_checks`,
`provider_smoke_first_success_preferred_env_key`,
`provider_smoke_first_success_accepted_env_keys`,
`provider_smoke_first_success_network_call`,
`provider_smoke_first_success_network_call_policy`,
`provider_smoke_first_success_mutates_local_state`, and
`provider_smoke_first_success_secret_values_returned`, so a one-line client can
show the first passing live provider contract/env/safety context without reading
the provider smoke row list.
It also keeps summary-only provider smoke contract/check aggregates:
`provider_smoke_success_expected_live_contracts`,
`provider_smoke_success_expected_live_checks`, and
`provider_smoke_success_check_count`.
Summary-only provider smoke safety aggregates include
`provider_smoke_success_network_call_count`,
`provider_smoke_success_all_network_calls`,
`provider_smoke_success_network_call_policies`,
`provider_smoke_success_mutates_local_state_count`,
`provider_smoke_success_any_mutates_local_state`,
`provider_smoke_success_secret_values_returned_count`, and
`provider_smoke_success_any_secret_values_returned`.
Summary-only provider smoke env-key aggregates include
`provider_smoke_success_preferred_env_keys`,
`provider_smoke_success_accepted_env_keys`, and
`provider_smoke_success_accepted_env_key_groups` without returning key values.
The kept top-level `next_operator_action` matches
`readiness_summary.next_operator_action`, including provider smoke or recovery
env-key hints, so the compact response still shows the next local command
without returning secret values.
For direct CLI/MCP consumers, the compact payload also mirrors one-line fields:
`next_operator_action_name`, `next_operator_action_command`,
`next_operator_action_next_after_action`,
`next_operator_action_dotenv_target_path`,
`next_operator_action_source_path`, `next_operator_action_target_path`,
`next_operator_action_provider_family`, `next_operator_action_provider`,
`next_operator_action_selected_provider_class`,
`next_operator_action_provider_route_data_mode`,
`next_operator_action_provider_route_live_data_required`,
`next_operator_action_smoke_command_name`,
`next_operator_action_expected_live_contract`,
`next_operator_action_expected_live_checks`,
`next_operator_action_preferred_env_key`,
`next_operator_action_accepted_env_keys`,
`next_operator_action_required_env_keys`, and no-secret
`next_operator_action_dotenv_examples`, plus safety fields
`next_operator_action_status`, `next_operator_action_network_call`,
`next_operator_action_network_call_policy`,
`next_operator_action_mutates_local_state`,
`next_operator_action_secret_input_required`, and
`next_operator_action_secret_values_returned`.
It also mirrors top-level API-key setup progress fields:
`api_key_setup_current_step`, `api_key_setup_ready`,
`api_key_setup_step_count`, `api_key_setup_ready_step_names`,
`api_key_setup_ready_step_count`, `api_key_setup_blocking_step_names`,
`api_key_setup_blocking_step_count`, and
`api_key_setup_next_blocking_step`.
It mirrors provider-family readiness at top level with
`api_key_setup_configured_provider_families`,
`api_key_setup_missing_provider_families`,
`api_key_setup_configured_provider_family_count`,
`api_key_setup_required_provider_family_count`,
`api_key_setup_ready_to_run_live_smoke`, and
`api_key_setup_provider_route_status`. It also mirrors setup-status route family
evidence as `api_key_setup_selected_provider_class_by_family`,
`api_key_setup_provider_route_data_mode_by_family`,
`api_key_setup_provider_route_live_data_required_by_family`, and
`api_key_setup_all_selected_routes_live`, plus route count aggregates
`api_key_setup_provider_route_family_count`,
`api_key_setup_selected_provider_family_count`,
`api_key_setup_provider_route_live_data_required_family_count`, and
`api_key_setup_provider_route_data_mode_counts`.
When provider recovery is required, the compact top-level payload also exposes
top-level summary-only recovery command lists:
`provider_recovery_smoke_command_names`, `provider_recovery_smoke_commands`,
`provider_recovery_pending_smoke_command_names`,
`provider_recovery_pending_smoke_commands`,
`provider_recovery_blocked_smoke_command_names`, and
`provider_recovery_blocked_smoke_commands`, without returning secret values.
It also exposes top-level summary-only recovery status and identity fields:
`provider_recovery_action_status`, `provider_recovery_item_count`,
`provider_recovery_pending_count`, `provider_recovery_blocked_count`,
`provider_error_count`, `provider_recovery_retry_ready`,
`provider_recovery_all_retryable`, `provider_recovery_has_pending`,
`provider_recovery_has_blocked`, `provider_recovery_provider_families`,
`provider_recovery_providers`, `provider_recovery_pending_provider_families`,
`provider_recovery_pending_providers`,
`provider_recovery_blocked_provider_families`, and
`provider_recovery_blocked_providers`.
It also exposes top-level summary-only recovery env hints and network policies:
`provider_recovery_preferred_env_keys`, `provider_recovery_accepted_env_keys`,
`provider_recovery_accepted_env_key_groups`, and
`provider_recovery_network_call_policies`.
It also exposes top-level summary-only recovery diagnostic and safety
aggregates, including smoke availability, network-call counts, mutation/secret
safety counters, next setup actions, exception types, recovery statuses, and
URL/exception-message returned flags, without returning URLs, exception
messages, or secret values.
It also exposes top-level summary-only recovery required status through
`provider_recovery_required` and `provider_recovery_summary_status`.
It also exposes top-level summary-only next recovery fields:
`next_recovery_smoke_command_name`, `next_recovery_smoke_command`,
`next_recovery_provider_family`, `next_recovery_provider`,
`next_recovery_selected_provider_class`,
`next_recovery_provider_route_data_mode`,
`next_recovery_provider_route_live_data_required`,
`next_recovery_next_setup_action`, `next_recovery_preferred_env_key`,
`next_recovery_accepted_env_keys`, `next_recovery_network_call_policy`,
`next_recovery_smoke_available`, `next_recovery_network_call`,
`next_recovery_mutates_local_state`, `next_recovery_exception_type`,
`next_recovery_exception_message_returned`, `next_recovery_url_returned`,
`next_recovery_secret_values_returned`, plus matching
`next_pending_recovery_*` and `next_blocked_recovery_*` fields, including
selected provider class, route data mode, and live-data-required mirrors.
It keeps `api_key_requirements_summary`
(`api_key_pipeline_api_key_requirements_summary.v1`) with
`required_env_keys`, configured env-key names, `missing_provider_families`,
`configured_provider_families`, and per-family `provider_requirements`
including `preferred_env_key` and `accepted_env_keys`, plus
`selected_provider_class_by_family`, `provider_route_data_mode_by_family`,
`provider_route_live_data_required_by_family`, and `all_selected_routes_live`,
so the compact response still shows which API-key names to fill and how those
keys map to live provider routes without returning secret values.
For compact clients that read only top-level fields, summary-only output also
mirrors requirement metadata as `api_key_requirement_schema_version`,
`api_key_requirement_status`, `api_key_required_env_keys`,
`api_key_required_env_key_count`, `api_key_configured_env_keys`,
`api_key_configured_env_key_count`,
`api_key_requirement_configured_provider_families`,
`api_key_requirement_configured_provider_family_count`,
`api_key_requirement_missing_provider_families`,
`api_key_requirement_missing_provider_family_count`,
`api_key_provider_requirement_families`, and
`api_key_provider_requirement_count`.
It mirrors the next missing provider requirement as
`api_key_requirement_next_missing_provider_family`,
`api_key_requirement_next_missing_provider`,
`api_key_requirement_next_missing_required_env_keys`,
`api_key_requirement_next_missing_required_env_key_count`,
`api_key_requirement_next_missing_configured_env_keys`,
`api_key_requirement_next_missing_configured_env_key_count`,
`api_key_requirement_next_missing_missing_env_keys`,
`api_key_requirement_next_missing_missing_env_key_count`,
`api_key_requirement_next_missing_preferred_env_key`,
`api_key_requirement_next_missing_accepted_env_keys`,
`api_key_requirement_next_missing_accepted_env_key_count`,
`api_key_requirement_next_missing_setup_status`,
`api_key_requirement_next_missing_configured`,
`api_key_requirement_next_missing_next_setup_action`,
`api_key_requirement_next_missing_smoke_command_name`,
`api_key_requirement_next_missing_network_call`,
`api_key_requirement_next_missing_mutates_local_state`, and
`api_key_requirement_next_missing_secret_values_returned`.
It also mirrors per-family provider requirement hints as
`api_key_provider_requirement_providers`,
`api_key_provider_requirement_required_env_keys`,
`api_key_provider_requirement_required_env_key_counts`,
`api_key_provider_requirement_configured_env_keys`,
`api_key_provider_requirement_configured_env_key_counts`,
`api_key_provider_requirement_missing_env_keys`,
`api_key_provider_requirement_missing_env_key_counts`,
`api_key_provider_requirement_preferred_env_keys`,
`api_key_provider_requirement_accepted_env_keys`,
`api_key_provider_requirement_accepted_env_key_counts`,
`api_key_provider_requirement_setup_statuses`,
`api_key_provider_requirement_configured`,
`api_key_provider_requirement_next_setup_actions`, and
`api_key_provider_requirement_smoke_command_names`. It mirrors no-secret safety
state as `api_key_provider_requirement_network_calls`,
`api_key_provider_requirement_mutates_local_state`,
`api_key_provider_requirement_secret_values_returned`,
`api_key_requirement_network_call`,
`api_key_requirement_mutates_local_state`, and
`api_key_requirement_secret_values_returned`. Route-family evidence is
mirrored as `api_key_requirement_provider_route_family_count`,
`api_key_requirement_selected_provider_family_count`,
`api_key_requirement_provider_route_live_data_required_family_count`,
`api_key_requirement_provider_route_data_mode_counts`,
`api_key_requirement_selected_provider_class_by_family`,
`api_key_requirement_provider_route_data_mode_by_family`,
`api_key_requirement_provider_route_live_data_required_by_family`, and
`api_key_requirement_all_selected_routes_live`.
It keeps `api_key_operator_checklist_summary`
(`api_key_operator_checklist_summary.v1`) with `current_step`, `ready`,
ready/blocking step names and counts, `next_blocking_action_name`,
`next_blocking_action_command`, provider recovery status, recovery env-key hints
such as `next_blocking_action_preferred_env_key`, provider identity fields such
as `next_blocking_action_provider_family`,
`next_blocking_action_provider`, and
`next_blocking_action_smoke_command_name`,
`selected_provider_class_by_family`,
`provider_route_data_mode_by_family`,
`provider_route_live_data_required_by_family`, `all_selected_routes_live`, and
compact setup step rows including
`configured_env_keys`, `missing_provider_families`, `required_env_keys`,
`network_call_policy`, `next_provider_smoke_command_name`,
`next_provider_recovery_smoke_command_name`, `provider_smoke_command_count`,
`recovery_smoke_available`, recovery `provider_family`, `provider`,
`smoke_command_name`, `preferred_env_key`, `accepted_env_keys`, and no-secret
`dotenv_examples` / `dotenv_example_count` on `fill_live_data_api_keys`, so the
compact response still shows the next local setup or recovery action and the
`KEY=placeholder` lines to fill without
returning the full checklist payload.
Placeholder examples such as `your_polygon_key`, `your_fred_key`, and
`your_newsapi_key` are documentation examples only; they are not treated as
configured live-data credentials.
For compact clients that read only top-level fields, summary-only output also
mirrors checklist action fields as
`api_key_operator_checklist_schema_version`, `api_key_setup_status`,
`api_key_setup_current_step`, `api_key_setup_ready`,
`api_key_setup_step_count`, `api_key_setup_ready_step_names`,
`api_key_setup_ready_step_count`, `api_key_setup_blocking_step_names`,
`api_key_setup_blocking_step_count`, `api_key_setup_next_blocking_step`,
`api_key_setup_next_blocking_action_name`,
`api_key_setup_next_blocking_action_status`,
`api_key_setup_next_blocking_action_command`,
`api_key_setup_next_blocking_action_network_call`,
`api_key_setup_next_blocking_action_network_call_policy`,
`api_key_setup_next_blocking_action_mutates_local_state`,
`api_key_setup_next_blocking_action_secret_values_returned`,
`api_key_setup_next_blocking_action_provider_family`,
`api_key_setup_next_blocking_action_provider`,
`api_key_setup_next_blocking_action_smoke_command_name`,
`api_key_setup_next_blocking_action_preferred_env_key`, and
`api_key_setup_next_blocking_action_accepted_env_keys`.
It also mirrors checklist route-family evidence as
`api_key_operator_checklist_selected_provider_class_by_family`,
`api_key_operator_checklist_provider_route_data_mode_by_family`,
`api_key_operator_checklist_provider_route_live_data_required_by_family`,
`api_key_operator_checklist_all_selected_routes_live`, plus route count
aggregates `api_key_operator_checklist_provider_route_family_count`,
`api_key_operator_checklist_selected_provider_family_count`,
`api_key_operator_checklist_provider_route_live_data_required_family_count`,
`api_key_operator_checklist_provider_route_data_mode_counts`,
`api_key_operator_checklist_network_call`,
`api_key_operator_checklist_mutates_local_state`, and
`api_key_operator_checklist_secret_values_returned`.
It also
mirrors the no-secret setup sequence as `api_key_setup_quickstart_steps`,
`api_key_setup_quickstart_step_names`,
`api_key_setup_quickstart_step_count`, `api_key_setup_quickstart_next_step`,
and `api_key_setup_quickstart_next_command`.
It also exposes `api_key_setup_quickstart_command_plan`,
`api_key_setup_quickstart_command_plan_names`,
`api_key_setup_quickstart_command_plan_count`,
`api_key_setup_quickstart_command_plan_provider_families`,
`api_key_setup_quickstart_command_plan_provider_family_count`,
`api_key_setup_quickstart_command_plan_ready_provider_families`,
`api_key_setup_quickstart_command_plan_blocked_provider_families`,
`api_key_setup_quickstart_command_plan_ready_command_names`,
`api_key_setup_quickstart_command_plan_ready_commands`,
`api_key_setup_quickstart_command_plan_blocked_command_names`,
`api_key_setup_quickstart_command_plan_blocked_commands`,
`api_key_setup_quickstart_command_plan_next_ready_provider_smoke_provider_family`,
`api_key_setup_quickstart_command_plan_next_ready_provider_smoke_provider`,
`api_key_setup_quickstart_command_plan_next_ready_provider_smoke_selected_provider_class`,
`api_key_setup_quickstart_command_plan_next_ready_provider_smoke_provider_route_data_mode`,
`api_key_setup_quickstart_command_plan_next_ready_provider_smoke_provider_route_live_data_required`,
`api_key_setup_quickstart_command_plan_next_ready_provider_smoke_command_name`,
`api_key_setup_quickstart_command_plan_next_ready_provider_smoke_command`,
`api_key_setup_quickstart_command_plan_next_ready_provider_smoke_has_command`,
`api_key_setup_quickstart_command_plan_next_ready_provider_smoke_ready_to_run`,
`api_key_setup_quickstart_command_plan_next_ready_provider_smoke_requires_api_keys`,
`api_key_setup_quickstart_command_plan_next_ready_provider_smoke_expected_live_contract`,
`api_key_setup_quickstart_command_plan_next_ready_provider_smoke_expected_live_checks`,
`api_key_setup_quickstart_command_plan_next_ready_provider_smoke_expected_live_check_count`,
`api_key_setup_quickstart_command_plan_next_ready_provider_smoke_preferred_env_key`,
`api_key_setup_quickstart_command_plan_next_ready_provider_smoke_accepted_env_keys`,
`api_key_setup_quickstart_command_plan_next_ready_provider_smoke_accepted_env_key_count`,
`api_key_setup_quickstart_command_plan_next_ready_provider_smoke_next_setup_action`,
`api_key_setup_quickstart_command_plan_next_ready_provider_smoke_status`,
`api_key_setup_quickstart_command_plan_next_ready_provider_smoke_network_call`,
`api_key_setup_quickstart_command_plan_next_ready_provider_smoke_network_call_policy`,
`api_key_setup_quickstart_command_plan_next_ready_provider_smoke_mutates_local_state`,
`api_key_setup_quickstart_command_plan_next_ready_provider_smoke_secret_values_returned`,
`api_key_setup_quickstart_command_plan_next_blocked_provider_smoke_provider_family`,
`api_key_setup_quickstart_command_plan_next_blocked_provider_smoke_provider`,
`api_key_setup_quickstart_command_plan_next_blocked_provider_smoke_selected_provider_class`,
`api_key_setup_quickstart_command_plan_next_blocked_provider_smoke_provider_route_data_mode`,
`api_key_setup_quickstart_command_plan_next_blocked_provider_smoke_provider_route_live_data_required`,
`api_key_setup_quickstart_command_plan_next_blocked_provider_smoke_command_name`,
`api_key_setup_quickstart_command_plan_next_blocked_provider_smoke_command`,
`api_key_setup_quickstart_command_plan_next_blocked_provider_smoke_has_command`,
`api_key_setup_quickstart_command_plan_next_blocked_provider_smoke_ready_to_run`,
`api_key_setup_quickstart_command_plan_next_blocked_provider_smoke_requires_api_keys`,
`api_key_setup_quickstart_command_plan_next_blocked_provider_smoke_expected_live_contract`,
`api_key_setup_quickstart_command_plan_next_blocked_provider_smoke_expected_live_checks`,
`api_key_setup_quickstart_command_plan_next_blocked_provider_smoke_expected_live_check_count`,
`api_key_setup_quickstart_command_plan_next_blocked_provider_smoke_preferred_env_key`,
`api_key_setup_quickstart_command_plan_next_blocked_provider_smoke_accepted_env_keys`,
`api_key_setup_quickstart_command_plan_next_blocked_provider_smoke_accepted_env_key_count`,
`api_key_setup_quickstart_command_plan_next_blocked_provider_smoke_next_setup_action`,
`api_key_setup_quickstart_command_plan_next_blocked_provider_smoke_status`,
`api_key_setup_quickstart_command_plan_next_blocked_provider_smoke_network_call`,
`api_key_setup_quickstart_command_plan_next_blocked_provider_smoke_network_call_policy`,
`api_key_setup_quickstart_command_plan_next_blocked_provider_smoke_mutates_local_state`,
`api_key_setup_quickstart_command_plan_next_blocked_provider_smoke_secret_values_returned`,
`api_key_setup_quickstart_command_plan_ready_provider_smoke_count`,
`api_key_setup_quickstart_command_plan_blocked_provider_smoke_count`,
`api_key_setup_quickstart_command_plan_all_provider_smokes_ready`,
`api_key_setup_quickstart_command_plan_all_provider_smokes_network_calls`,
`api_key_setup_quickstart_command_plan_all_provider_smokes_live_required`,
`api_key_setup_quickstart_command_plan_any_provider_smoke_mutates_local_state`,
`api_key_setup_quickstart_command_plan_any_provider_smoke_secret_values_returned`,
`api_key_setup_quickstart_command_plan_kinds_by_family`,
`api_key_setup_quickstart_command_plan_command_names_by_family`,
`api_key_setup_quickstart_command_plan_commands_by_family`,
`api_key_setup_quickstart_command_plan_provider_by_family`,
`api_key_setup_quickstart_command_plan_selected_provider_class_by_family`,
`api_key_setup_quickstart_command_plan_provider_route_data_mode_by_family`,
`api_key_setup_quickstart_command_plan_provider_route_live_data_required_by_family`,
`api_key_setup_quickstart_command_plan_provider_route_family_count`,
`api_key_setup_quickstart_command_plan_selected_provider_family_count`,
`api_key_setup_quickstart_command_plan_provider_route_live_data_required_family_count`,
`api_key_setup_quickstart_command_plan_provider_route_data_mode_counts`,
`api_key_setup_quickstart_command_plan_expected_live_check_count`,
`api_key_setup_quickstart_command_plan_expected_live_check_counts_by_family`,
`api_key_setup_quickstart_command_plan_expected_live_contracts_by_family`,
`api_key_setup_quickstart_command_plan_expected_live_checks_by_family`,
`api_key_setup_quickstart_command_plan_accepted_env_key_count`,
`api_key_setup_quickstart_command_plan_accepted_env_key_counts_by_family`,
`api_key_setup_quickstart_command_plan_preferred_env_key_by_family`,
`api_key_setup_quickstart_command_plan_accepted_env_keys_by_family`,
`api_key_setup_quickstart_command_plan_next_setup_actions_by_family`,
`api_key_setup_quickstart_command_plan_statuses_by_family`,
`api_key_setup_quickstart_command_plan_network_calls_by_family`,
`api_key_setup_quickstart_command_plan_network_call_policies_by_family`,
`api_key_setup_quickstart_command_plan_mutates_local_state_by_family`,
`api_key_setup_quickstart_command_plan_secret_values_returned_by_family`,
and `api_key_setup_quickstart_next_command_plan_item`, so compact clients can
show the copy/status/provider-smoke/one-shot commands in operator order with
provider route evidence, expected live checks, env-key hints, next setup
actions, ready/blocked provider-family lists, ready/blocked command lists, first
ready/blocked provider-smoke commands with route, expected-contract, env-key,
status, and safety flags, aggregate provider-smoke readiness/safety flags, and
safety/status maps on provider-smoke rows.
It mirrors the immediate command item as scalar
`api_key_setup_quickstart_next_command_plan_name`,
`api_key_setup_quickstart_next_command_plan_kind`,
`api_key_setup_quickstart_next_command_plan_command`,
`api_key_setup_quickstart_next_command_plan_has_command`,
`api_key_setup_quickstart_next_command_plan_provider_family`,
`api_key_setup_quickstart_next_command_plan_provider`,
`api_key_setup_quickstart_next_command_plan_selected_provider_class`,
`api_key_setup_quickstart_next_command_plan_provider_route_data_mode`,
`api_key_setup_quickstart_next_command_plan_provider_route_live_data_required`,
`api_key_setup_quickstart_next_command_plan_expected_live_contract`,
`api_key_setup_quickstart_next_command_plan_expected_live_checks`,
`api_key_setup_quickstart_next_command_plan_expected_live_check_count`,
`api_key_setup_quickstart_next_command_plan_preferred_env_key`,
`api_key_setup_quickstart_next_command_plan_accepted_env_keys`,
`api_key_setup_quickstart_next_command_plan_accepted_env_key_count`,
`api_key_setup_quickstart_next_command_plan_next_setup_action`,
`api_key_setup_quickstart_next_command_plan_status`,
`api_key_setup_quickstart_next_command_plan_ready_to_run`,
`api_key_setup_quickstart_next_command_plan_requires_api_keys`,
`api_key_setup_quickstart_next_command_plan_network_call`,
`api_key_setup_quickstart_next_command_plan_network_call_policy`,
`api_key_setup_quickstart_next_command_plan_mutates_local_state`, and
`api_key_setup_quickstart_next_command_plan_secret_values_returned`.
It also mirrors the no-secret `.env` lines to fill as
`api_key_setup_dotenv_example_lines`,
`api_key_setup_dotenv_example_line_count`,
`api_key_setup_dotenv_example_env_keys`, `api_key_setup_dotenv_source_path`,
`api_key_setup_dotenv_target_path`, `api_key_setup_dotenv_source_exists`,
`api_key_setup_dotenv_target_exists`, `api_key_setup_dotenv_copy_required`,
`api_key_setup_dotenv_copy_command`, `api_key_setup_dotenv_copy_command_name`,
`api_key_setup_dotenv_copy_command_network_call`,
`api_key_setup_dotenv_copy_command_mutates_local_state`,
`api_key_setup_dotenv_copy_command_secret_values_returned`,
`api_key_setup_dotenv_preferred_env_keys`,
`api_key_setup_dotenv_preferred_env_key_count`,
`api_key_setup_dotenv_configured_provider_families`,
`api_key_setup_dotenv_missing_provider_families`,
`api_key_setup_dotenv_configured_provider_family_count`,
`api_key_setup_dotenv_required_provider_family_count`,
`api_key_setup_dotenv_next_setup_step`,
`api_key_setup_dotenv_ready_to_run_live_smoke`,
`api_key_setup_dotenv_network_call`,
`api_key_setup_dotenv_mutates_local_state`, and
`api_key_setup_dotenv_secret_values_returned`.
It keeps `live_data_setup_summary` (`live_data_setup_summary.v1`) with
API-key setup status, provider family summary, provider smoke plan, dotenv
template/file status, setup steps, and no-secret next operator action.
Provider smoke plan rows include `network_call`, `network_call_policy`,
`preferred_env_key`, `accepted_env_keys`, `selected_provider_class`,
`provider_route_data_mode`, and `provider_route_live_data_required`, so the
compact response shows the same local setup readiness, live-call policy,
key-alias evidence, and selected live provider route as the full one-shot
pipeline response without returning secret values.
It also keeps `api_key_command_summary`
(`api_key_pipeline_api_key_command_summary.v1`) with `copy_dotenv_command`,
`next_smoke_command`, `one_shot_pipeline_smoke`,
`provider_smoke_commands`, `provider_smoke_command_count`, and
`next_provider_smoke_command_name`. Provider smoke rows include `network_call`,
`network_call_policy`, `expected_live_contract`, `expected_live_checks`,
`preferred_env_key`, `accepted_env_keys`, `selected_provider_class`,
`provider_route_data_mode`, and `provider_route_live_data_required` without
returning key values, so the compact response still shows accepted API-key
aliases, expected live
contract/checks, live-call policy, selected live provider route, and the exact
local smoke commands to use after API keys are configured.
For compact clients that read only top-level fields, summary-only output also
mirrors the no-secret command metadata as `api_key_copy_dotenv_command`,
`api_key_copy_dotenv_required`, `api_key_copy_dotenv_command_name`,
`api_key_copy_dotenv_command_network_call`,
`api_key_copy_dotenv_command_mutates_local_state`,
`api_key_copy_dotenv_command_secret_values_returned`,
`api_key_next_smoke_command`, `api_key_next_smoke_command_name`,
`api_key_next_smoke_command_network_call`,
`api_key_next_smoke_command_network_call_policy`,
`api_key_next_smoke_command_mutates_local_state`,
`api_key_next_smoke_command_secret_values_returned`,
`api_key_one_shot_pipeline_smoke_command`,
`api_key_one_shot_pipeline_smoke_command_name`,
`api_key_one_shot_pipeline_smoke_network_call`,
`api_key_one_shot_pipeline_smoke_network_call_policy`,
`api_key_one_shot_pipeline_smoke_mutates_local_state`,
`api_key_one_shot_pipeline_smoke_secret_values_returned`,
`api_key_one_shot_pipeline_smoke_expected_live_contracts`,
`api_key_one_shot_pipeline_smoke_expected_live_contract_count`,
`api_key_one_shot_pipeline_smoke_expected_live_contracts_by_family`,
`api_key_one_shot_pipeline_smoke_expected_live_checks`,
`api_key_one_shot_pipeline_smoke_expected_live_check_count`,
`api_key_one_shot_pipeline_smoke_expected_live_checks_by_family`,
`api_key_provider_smoke_command_count`,
`api_key_provider_smoke_command_names`,
`api_key_provider_smoke_provider_families`,
`api_key_provider_smoke_provider_family_count`,
`api_key_provider_smoke_ready_provider_families`,
`api_key_provider_smoke_blocked_provider_families`,
`api_key_provider_smoke_ready_command_names`,
`api_key_provider_smoke_ready_commands`,
`api_key_provider_smoke_blocked_command_names`, and
`api_key_provider_smoke_blocked_commands`.
The flat `api_key_provider_smoke_commands` list mirrors every provider smoke
command string in command-plan order, so compact clients can run the ready list
or display blocked commands without opening the command rows.
It also mirrors provider smoke progress as
`api_key_provider_smoke_total_count`, `api_key_provider_smoke_ready_count`,
`api_key_provider_smoke_blocked_count`,
`api_key_provider_smoke_all_ready`,
`api_key_provider_smoke_any_blocked`,
`api_key_provider_smoke_action_status`,
`api_key_provider_smoke_next_action`,
`api_key_provider_smoke_next_action_ready_to_run`,
`api_key_provider_smoke_next_action_requires_api_keys`,
`api_key_provider_smoke_next_action_primary_provider_family`,
`api_key_provider_smoke_next_action_primary_provider`,
`api_key_provider_smoke_next_action_primary_kind`,
`api_key_provider_smoke_next_action_primary_command_name`,
`api_key_provider_smoke_next_action_primary_command`,
`api_key_provider_smoke_next_action_primary_has_command`,
`api_key_provider_smoke_next_action_primary_status`,
`api_key_provider_smoke_next_action_primary_ready_to_run`,
`api_key_provider_smoke_next_action_primary_requires_api_keys`,
`api_key_provider_smoke_next_action_primary_setup_action`,
`api_key_provider_smoke_next_action_primary_selected_provider_class`,
`api_key_provider_smoke_next_action_primary_provider_route_data_mode`,
`api_key_provider_smoke_next_action_primary_provider_route_live_data_required`,
`api_key_provider_smoke_next_action_primary_network_call`,
`api_key_provider_smoke_next_action_primary_network_call_policy`,
`api_key_provider_smoke_next_action_primary_mutates_local_state`,
`api_key_provider_smoke_next_action_primary_secret_values_returned`,
`api_key_provider_smoke_next_action_primary_preferred_env_key`,
`api_key_provider_smoke_next_action_primary_accepted_env_keys`,
`api_key_provider_smoke_next_action_primary_accepted_env_key_count`,
`api_key_provider_smoke_next_action_primary_expected_live_contract`,
`api_key_provider_smoke_next_action_primary_expected_live_checks`,
`api_key_provider_smoke_next_action_primary_expected_live_check_count`,
`api_key_provider_smoke_next_action_command_count`,
`api_key_provider_smoke_next_action_command_names`,
`api_key_provider_smoke_next_action_commands`,
`api_key_provider_smoke_next_action_kinds_by_family`,
`api_key_provider_smoke_next_action_command_names_by_family`,
`api_key_provider_smoke_next_action_commands_by_family`,
`api_key_provider_smoke_next_action_provider_by_family`,
`api_key_provider_smoke_next_action_provider_families`,
`api_key_provider_smoke_next_action_provider_family_count`,
`api_key_provider_smoke_next_action_providers`,
`api_key_provider_smoke_next_action_provider_count`,
`api_key_provider_smoke_next_action_statuses`,
`api_key_provider_smoke_next_action_status_count`,
`api_key_provider_smoke_next_action_statuses_by_family`,
`api_key_provider_smoke_next_action_ready_count`,
`api_key_provider_smoke_next_action_blocked_count`,
`api_key_provider_smoke_next_action_all_ready`,
`api_key_provider_smoke_next_action_any_blocked`,
`api_key_provider_smoke_next_action_setup_actions`,
`api_key_provider_smoke_next_action_setup_action_count`,
`api_key_provider_smoke_next_action_setup_actions_by_family`,
`api_key_provider_smoke_next_action_network_call_policies`,
`api_key_provider_smoke_next_action_network_call_policy_count`,
`api_key_provider_smoke_next_action_network_call_policies_by_family`,
`api_key_provider_smoke_next_action_network_calls_by_family`,
`api_key_provider_smoke_next_action_network_call_count`,
`api_key_provider_smoke_next_action_all_network_calls`,
`api_key_provider_smoke_next_action_mutates_local_state_by_family`,
`api_key_provider_smoke_next_action_mutates_local_state_count`,
`api_key_provider_smoke_next_action_any_mutates_local_state`,
`api_key_provider_smoke_next_action_secret_values_returned_by_family`,
`api_key_provider_smoke_next_action_secret_values_returned_count`,
`api_key_provider_smoke_next_action_any_secret_values_returned`,
`api_key_provider_smoke_next_action_selected_provider_class_by_family`,
`api_key_provider_smoke_next_action_provider_route_data_mode_by_family`,
`api_key_provider_smoke_next_action_provider_route_live_data_required_by_family`,
`api_key_provider_smoke_next_action_all_selected_routes_live`,
`api_key_provider_smoke_next_action_provider_route_family_count`,
`api_key_provider_smoke_next_action_selected_provider_family_count`,
`api_key_provider_smoke_next_action_provider_route_live_data_required_family_count`,
`api_key_provider_smoke_next_action_provider_route_data_mode_counts`,
`api_key_provider_smoke_next_action_expected_live_contracts`,
`api_key_provider_smoke_next_action_expected_live_contract_count`,
`api_key_provider_smoke_next_action_expected_live_contracts_by_family`,
`api_key_provider_smoke_next_action_expected_live_checks`,
`api_key_provider_smoke_next_action_expected_live_check_count`,
`api_key_provider_smoke_next_action_expected_live_checks_by_family`,
`api_key_provider_smoke_next_action_expected_live_check_counts_by_family`,
`api_key_provider_smoke_next_action_preferred_env_keys`,
`api_key_provider_smoke_next_action_preferred_env_key_count`,
`api_key_provider_smoke_next_action_accepted_env_keys`,
`api_key_provider_smoke_next_action_accepted_env_key_count`,
`api_key_provider_smoke_next_action_accepted_env_key_groups`,
`api_key_provider_smoke_next_action_accepted_env_key_group_count`,
`api_key_provider_smoke_next_action_preferred_env_keys_by_family`,
`api_key_provider_smoke_next_action_accepted_env_keys_by_family`, and
`api_key_provider_smoke_next_action_accepted_env_key_counts_by_family`,
plus ready setup hints
`api_key_provider_smoke_ready_preferred_env_keys`,
`api_key_provider_smoke_ready_preferred_env_key_count`,
`api_key_provider_smoke_ready_accepted_env_keys`,
`api_key_provider_smoke_ready_accepted_env_key_count`,
`api_key_provider_smoke_ready_accepted_env_key_groups`, and
`api_key_provider_smoke_ready_accepted_env_key_group_count`,
`api_key_provider_smoke_ready_preferred_env_keys_by_family`,
`api_key_provider_smoke_ready_accepted_env_keys_by_family`, and
`api_key_provider_smoke_ready_accepted_env_key_counts_by_family`,
plus blocked setup hints
`api_key_provider_smoke_blocked_preferred_env_keys`,
`api_key_provider_smoke_blocked_preferred_env_key_count`,
`api_key_provider_smoke_blocked_accepted_env_keys`,
`api_key_provider_smoke_blocked_accepted_env_key_count`,
`api_key_provider_smoke_blocked_accepted_env_key_groups`, and
`api_key_provider_smoke_blocked_accepted_env_key_group_count`,
`api_key_provider_smoke_blocked_preferred_env_keys_by_family`,
`api_key_provider_smoke_blocked_accepted_env_keys_by_family`, and
`api_key_provider_smoke_blocked_accepted_env_key_counts_by_family`,
`api_key_next_provider_smoke_command_name`,
`api_key_next_provider_smoke_provider_family`,
`api_key_next_provider_smoke_provider`,
`api_key_next_provider_smoke_selected_provider_class`,
`api_key_next_provider_smoke_provider_route_data_mode`,
`api_key_next_provider_smoke_provider_route_live_data_required`,
`api_key_next_provider_smoke_command`,
`api_key_next_provider_smoke_has_command`,
`api_key_next_provider_smoke_ready_to_run`,
`api_key_next_provider_smoke_requires_api_keys`,
`api_key_next_provider_smoke_next_setup_action`,
`api_key_next_provider_smoke_status`,
`api_key_next_provider_smoke_network_call`,
`api_key_next_provider_smoke_network_call_policy`,
`api_key_next_provider_smoke_expected_live_contract`,
`api_key_next_provider_smoke_expected_live_checks`,
`api_key_next_provider_smoke_expected_live_check_count`,
`api_key_next_provider_smoke_preferred_env_key`,
`api_key_next_provider_smoke_accepted_env_keys`,
`api_key_next_provider_smoke_accepted_env_key_count`,
`api_key_next_provider_smoke_mutates_local_state`, and
`api_key_next_provider_smoke_secret_values_returned`.
The same first ready provider smoke is also exposed with explicit ready-field
names:
`api_key_next_ready_provider_smoke_provider_family`,
`api_key_next_ready_provider_smoke_provider`,
`api_key_next_ready_provider_smoke_selected_provider_class`,
`api_key_next_ready_provider_smoke_provider_route_data_mode`,
`api_key_next_ready_provider_smoke_provider_route_live_data_required`,
`api_key_next_ready_provider_smoke_command_name`,
`api_key_next_ready_provider_smoke_command`,
`api_key_next_ready_provider_smoke_has_command`,
`api_key_next_ready_provider_smoke_ready_to_run`,
`api_key_next_ready_provider_smoke_requires_api_keys`,
`api_key_next_ready_provider_smoke_expected_live_contract`,
`api_key_next_ready_provider_smoke_expected_live_checks`,
`api_key_next_ready_provider_smoke_expected_live_check_count`,
`api_key_next_ready_provider_smoke_preferred_env_key`,
`api_key_next_ready_provider_smoke_accepted_env_keys`,
`api_key_next_ready_provider_smoke_accepted_env_key_count`,
`api_key_next_ready_provider_smoke_next_setup_action`,
`api_key_next_ready_provider_smoke_status`,
`api_key_next_ready_provider_smoke_network_call`,
`api_key_next_ready_provider_smoke_network_call_policy`,
`api_key_next_ready_provider_smoke_mutates_local_state`, and
`api_key_next_ready_provider_smoke_secret_values_returned`.
For partial API-key setup, it also mirrors the first blocked provider smoke as
`api_key_next_blocked_provider_smoke_provider_family`,
`api_key_next_blocked_provider_smoke_provider`,
`api_key_next_blocked_provider_smoke_selected_provider_class`,
`api_key_next_blocked_provider_smoke_provider_route_data_mode`,
`api_key_next_blocked_provider_smoke_provider_route_live_data_required`,
`api_key_next_blocked_provider_smoke_command_name`,
`api_key_next_blocked_provider_smoke_command`,
`api_key_next_blocked_provider_smoke_has_command`,
`api_key_next_blocked_provider_smoke_ready_to_run`,
`api_key_next_blocked_provider_smoke_requires_api_keys`,
`api_key_next_blocked_provider_smoke_expected_live_contract`,
`api_key_next_blocked_provider_smoke_expected_live_checks`,
`api_key_next_blocked_provider_smoke_expected_live_check_count`,
`api_key_next_blocked_provider_smoke_preferred_env_key`,
`api_key_next_blocked_provider_smoke_accepted_env_keys`,
`api_key_next_blocked_provider_smoke_accepted_env_key_count`,
`api_key_next_blocked_provider_smoke_next_setup_action`,
`api_key_next_blocked_provider_smoke_status`,
`api_key_next_blocked_provider_smoke_network_call`,
`api_key_next_blocked_provider_smoke_network_call_policy`,
`api_key_next_blocked_provider_smoke_mutates_local_state`, and
`api_key_next_blocked_provider_smoke_secret_values_returned`.
It also mirrors provider smoke command details by family as
`api_key_provider_smoke_kinds_by_family`,
`api_key_provider_smoke_command_names_by_family`,
`api_key_provider_smoke_commands_by_family`,
`api_key_provider_smoke_provider_by_family`,
`api_key_provider_smoke_statuses_by_family`,
`api_key_provider_smoke_selected_provider_class_by_family`,
`api_key_provider_smoke_provider_route_data_mode_by_family`,
`api_key_provider_smoke_provider_route_live_data_required_by_family`,
`api_key_provider_smoke_all_live_data_required`,
`api_key_provider_smoke_provider_route_family_count`,
`api_key_provider_smoke_selected_provider_family_count`,
`api_key_provider_smoke_provider_route_live_data_required_family_count`,
`api_key_provider_smoke_provider_route_data_mode_counts`,
`api_key_provider_smoke_network_call_policies_by_family`,
`api_key_provider_smoke_network_calls_by_family`,
`api_key_provider_smoke_network_call_count`,
`api_key_provider_smoke_all_network_calls`,
`api_key_provider_smoke_mutates_local_state_by_family`,
`api_key_provider_smoke_mutates_local_state_count`,
`api_key_provider_smoke_any_mutates_local_state`,
`api_key_provider_smoke_secret_values_returned_by_family`,
`api_key_provider_smoke_secret_values_returned_count`,
`api_key_provider_smoke_any_secret_values_returned`,
`api_key_provider_smoke_next_setup_actions_by_family`,
`api_key_provider_smoke_expected_live_contracts_by_family`,
`api_key_provider_smoke_expected_live_checks_by_family`,
`api_key_provider_smoke_expected_live_check_count`,
`api_key_provider_smoke_expected_live_check_counts_by_family`,
`api_key_provider_smoke_accepted_env_keys_by_family`,
`api_key_provider_smoke_accepted_env_key_groups`,
`api_key_provider_smoke_accepted_env_key_group_count`,
`api_key_provider_smoke_unique_accepted_env_keys`,
`api_key_provider_smoke_unique_accepted_env_key_count`,
`api_key_provider_smoke_preferred_env_keys_by_family`,
`api_key_provider_smoke_preferred_env_keys`,
`api_key_provider_smoke_preferred_env_key_count`,
`api_key_provider_smoke_accepted_env_key_count`, and
`api_key_provider_smoke_accepted_env_key_counts_by_family`.
Returned one-shot command summaries use `--summary-only --no-audit` for
`run_api_key_pipeline_smoke`, so the displayed post-setup command opens the same
compact response without requiring input JSON edits.
It keeps `api_key_setup_file_summary`
(`api_key_setup_file_summary.v1`) with `.env.example`/`.env` source and target
status, `copy_required`, `copy_command`, `preferred_env_keys`,
`dotenv_examples`, configured/missing provider families, and
`ready_to_run_live_smoke`, so the compact response still shows whether the local
setup file must be copied and which no-secret `KEY=placeholder` lines to fill
before API keys are entered.
It keeps `api_key_dotenv_loading_summary`
(`api_key_dotenv_loading_summary.v1`) with `dotenv_loading_enabled`,
`disabled`, `disabled_env_key`, `configuration_precedence`, `.env` file status,
and `ready_to_run_live_smoke`, so disabled dotenv loading is visible in compact
output before retrying API-key smokes.
`api_key_live_http_timeout_summary`
(`api_key_live_http_timeout_summary.v1`) exposes the configured
`timeout_seconds`, `env_key`, `default_timeout_seconds`, and provider classes
listed in `applies_to`, so API-key smoke calls show the active live HTTP
timeout without returning secret values. It mirrors the same no-secret timeout
state as top-level `api_key_live_http_timeout_seconds`,
`api_key_live_http_timeout_env_key`,
`api_key_live_http_timeout_default_seconds`,
`api_key_live_http_timeout_applies_to`,
`api_key_live_http_timeout_applies_to_count`,
`api_key_live_http_timeout_network_call`,
`api_key_live_http_timeout_mutates_local_state`, and
`api_key_live_http_timeout_secret_values_returned`, so compact clients can show
timeout policy without opening the nested summary.
`api_key_provider_recovery_summary`
(`api_key_provider_recovery_summary.v1`) exposes
`provider_recovery_required`, `provider_error_count`,
`selected_provider_class_by_family`, `provider_route_data_mode_by_family`,
`provider_route_live_data_required_by_family`, `all_selected_routes_live`,
`provider_recovery_smoke_count`, `provider_recovery_smoke_available_count`,
`provider_recovery_smoke_unavailable_count`,
`provider_recovery_all_smokes_available`,
`provider_recovery_network_call_count`, `provider_recovery_all_network_calls`,
`provider_recovery_mutates_local_state_count`,
`provider_recovery_any_mutates_local_state`,
`provider_recovery_secret_values_returned_count`,
`provider_recovery_any_secret_values_returned`,
`provider_recovery_next_setup_actions`,
`provider_recovery_exception_types`,
`provider_recovery_exception_message_returned_count`,
`provider_recovery_any_exception_messages_returned`,
`provider_recovery_url_returned_count`,
`provider_recovery_any_urls_returned`,
`provider_recovery_network_call_policies`,
`provider_recovery_statuses`, `provider_recovery_pending_count`,
`provider_recovery_blocked_count`,
`provider_recovery_has_pending`, `provider_recovery_has_blocked`,
`provider_recovery_retry_ready`, `provider_recovery_all_retryable`,
`provider_recovery_action_status`, `provider_recovery_all_pending`,
`provider_recovery_pending_provider_families`,
`provider_recovery_blocked_provider_families`,
`provider_recovery_pending_providers`, `provider_recovery_blocked_providers`,
`provider_recovery_pending_smoke_command_names`,
`provider_recovery_pending_smoke_commands`,
`provider_recovery_blocked_smoke_command_names`,
`provider_recovery_blocked_smoke_commands`,
`provider_recovery_provider_families`,
`provider_recovery_providers`, `provider_recovery_smoke_command_names`,
`provider_recovery_smoke_commands`,
`provider_recovery_preferred_env_keys`, `provider_recovery_accepted_env_keys`,
`provider_recovery_accepted_env_key_groups`,
`item_count`,
`next_pending_recovery_smoke_command_name`,
`next_pending_recovery_smoke_command`,
`next_pending_recovery_provider_family`, `next_pending_recovery_provider`,
`next_pending_recovery_selected_provider_class`,
`next_pending_recovery_provider_route_data_mode`,
`next_pending_recovery_provider_route_live_data_required`,
`next_pending_recovery_next_setup_action`,
`next_pending_recovery_preferred_env_key`,
`next_pending_recovery_accepted_env_keys`,
`next_pending_recovery_network_call_policy`,
`next_pending_recovery_smoke_available`,
`next_pending_recovery_network_call`,
`next_pending_recovery_mutates_local_state`,
`next_pending_recovery_secret_values_returned`,
`next_blocked_recovery_smoke_command_name`,
`next_blocked_recovery_smoke_command`,
`next_blocked_recovery_provider_family`, `next_blocked_recovery_provider`,
`next_blocked_recovery_selected_provider_class`,
`next_blocked_recovery_provider_route_data_mode`,
`next_blocked_recovery_provider_route_live_data_required`,
`next_blocked_recovery_next_setup_action`,
`next_blocked_recovery_preferred_env_key`,
`next_blocked_recovery_accepted_env_keys`,
`next_blocked_recovery_network_call_policy`,
`next_blocked_recovery_smoke_available`,
`next_blocked_recovery_network_call`,
`next_blocked_recovery_mutates_local_state`,
`next_blocked_recovery_secret_values_returned`,
`next_recovery_smoke_command_name`, `next_recovery_smoke_command`,
`next_recovery_provider_family`, `next_recovery_provider`,
`next_recovery_selected_provider_class`,
`next_recovery_provider_route_data_mode`,
`next_recovery_provider_route_live_data_required`,
`next_recovery_smoke_available`,
`next_recovery_next_setup_action`,
`next_recovery_preferred_env_key`, `next_recovery_accepted_env_keys`,
`next_recovery_network_call_policy`, `next_recovery_network_call`,
`next_recovery_mutates_local_state`,
`next_recovery_exception_type`,
`next_recovery_exception_message_returned`, `next_recovery_url_returned`,
`next_recovery_secret_values_returned`, and compact provider-family recovery
items with `provider_family`, `provider`,
`smoke_command_name`, `recovery_smoke_command`, `recovery_smoke_available`,
`next_setup_action`, `preferred_env_key`, `accepted_env_keys`,
`network_call_policy`, `network_call`, `mutates_local_state`,
`exception_type`, `exception_message_returned`, and `url_returned`.
The compact top-level payload mirrors provider recovery route-family evidence as
`api_key_provider_recovery_selected_provider_class_by_family`,
`api_key_provider_recovery_provider_route_data_mode_by_family`,
`api_key_provider_recovery_provider_route_live_data_required_by_family`, and
`api_key_provider_recovery_all_selected_routes_live`, plus route count
aggregates `api_key_provider_recovery_provider_route_family_count`,
`api_key_provider_recovery_selected_provider_family_count`,
`api_key_provider_recovery_provider_route_live_data_required_family_count`, and
`api_key_provider_recovery_provider_route_data_mode_counts`.
It also keeps `api_key_provider_recovery_checklist_summary`
(`api_key_provider_recovery_checklist_summary.v1`) with checklist status,
provider error and recovery smoke counts, next recovery provider/smoke fields,
`selected_provider_class_by_family`, `provider_route_data_mode_by_family`,
`provider_route_live_data_required_by_family`, `all_selected_routes_live`, and
no secret values while the full `api_key_provider_recovery_checklist` remains
omitted from summary-only output. Compact clients can read the same checklist
route evidence from
`api_key_provider_recovery_checklist_selected_provider_class_by_family`,
`api_key_provider_recovery_checklist_provider_route_data_mode_by_family`,
`api_key_provider_recovery_checklist_provider_route_live_data_required_by_family`,
and `api_key_provider_recovery_checklist_all_selected_routes_live`, plus route
count aggregates
`api_key_provider_recovery_checklist_provider_route_family_count`,
`api_key_provider_recovery_checklist_selected_provider_family_count`,
`api_key_provider_recovery_checklist_provider_route_live_data_required_family_count`,
and `api_key_provider_recovery_checklist_provider_route_data_mode_counts`.
The checklist includes `ready`,
`ready_step_names`, `ready_step_count`, `blocking_step_names`,
`blocking_step_count`, `next_blocking_step`, and the no-secret
`next_blocking_action` so setup progress, the first local setup blocker, and
its command or key guidance are visible without reading every step. The
top-level `api_key_next_action_summary`
(`api_key_next_action_summary.v1`) mirrors the checklist `status`,
`current_step`, `ready`, `blocking_step_count`, `next_blocking_step`,
`provider_recovery_required`, `provider_recovery_status`,
`provider_recovery_item_count`, and compact `next_action_name`,
`next_action_command`, `next_action_status`, `next_action_is_recovery`,
`next_action_network_call`, `next_action_mutates_local_state`,
`next_action_provider_family`, `next_action_provider`, and
`next_action_smoke_command_name` fields, plus
`selected_provider_class_by_family`, `provider_route_data_mode_by_family`,
`provider_route_live_data_required_by_family`, and `all_selected_routes_live`
route evidence. When the next action points at a provider smoke or provider
recovery command, it also includes `preferred_env_key` and `accepted_env_keys`,
so the single next setup or recovery command, provider identity, and accepted API-key aliases are visible.
The compact row also shows the full provider route family map.
Summary-only top-level mirrors expose the same next-action route evidence as
`api_key_next_action_selected_provider_class_by_family`,
`api_key_next_action_provider_route_data_mode_by_family`,
`api_key_next_action_provider_route_live_data_required_by_family`, and
`api_key_next_action_all_selected_routes_live`, plus route count aggregates
`api_key_next_action_provider_route_family_count`,
`api_key_next_action_selected_provider_family_count`,
`api_key_next_action_provider_route_live_data_required_family_count`, and
`api_key_next_action_provider_route_data_mode_counts`.
When the next action is `fill_live_data_api_keys`, it also includes
`required_env_keys`, `next_after_action`, `dotenv_target_path`, `source_path`,
`target_path`, `secret_input_required`, and no-secret `dotenv_examples` /
`dotenv_example_count`, so the compact row shows the `KEY=placeholder` lines
to fill
without reading nested payloads. It keeps `api_key_pipeline_stage_summary`
(`api_key_pipeline_stage_summary.v1`) with the `run_live_data_smoke`,
`run_live_signal_workflow_smoke`, and `run_live_recording_smoke` stages in
execution order with `status`, `stage_count`, `failed_stage_count`,
`failed_stage_names`, `first_failed_stage`,
`selected_provider_class_by_family`, `provider_route_data_mode_by_family`,
`provider_route_live_data_required_by_family`, `all_selected_routes_live`, and
per-stage `stage_name`,
`failed`, `error_summary`, `provider_error_summary_count`,
`provider_recovery_smoke_count`, `provider_family`, `provider`,
`smoke_command_name`, `preferred_env_key`, `accepted_env_keys`, `network_call`,
`mutates_local_state`, and `secret_values_returned` fields.
When provider recovery smoke metadata exists, it includes stage recovery
provider identity and env-key hints without returning key values, so the failed
pipeline stage is visible without reading every nested smoke summary.
The compact top-level payload mirrors stage route-family evidence as
`api_key_stage_selected_provider_class_by_family`,
`api_key_stage_provider_route_data_mode_by_family`,
`api_key_stage_provider_route_live_data_required_by_family`, and
`api_key_stage_all_selected_routes_live`, plus route count aggregates
`api_key_stage_provider_route_family_count`,
`api_key_stage_selected_provider_family_count`,
`api_key_stage_provider_route_live_data_required_family_count`, and
`api_key_stage_provider_route_data_mode_counts`.
It keeps `api_key_pipeline_check_summary`
(`api_key_pipeline_check_summary.v1`) summarizing the pipeline `checks` array
with `check_count`, `passed_check_count`, `failed_check_count`,
`failed_check_keys`, `tools_with_failures`, `tool_failure_counts`,
`first_failed_check`,
`selected_provider_class_by_family`, `provider_route_data_mode_by_family`,
`provider_route_live_data_required_by_family`, `all_selected_routes_live`, and
no-secret `failed_checks` rows containing `tool`, `name`, `key`, `expected`,
`actual`, and `passed=false`. When the matching stage has provider recovery metadata,
the check summary includes
`provider_family`, `provider`, `smoke_command_name`, `preferred_env_key`, and
`accepted_env_keys` without returning key values. The compact top-level payload
mirrors check route-family evidence as
`api_key_check_selected_provider_class_by_family`,
`api_key_check_provider_route_data_mode_by_family`,
`api_key_check_provider_route_live_data_required_by_family`, and
`api_key_check_all_selected_routes_live`, plus route count aggregates
`api_key_check_provider_route_family_count`,
`api_key_check_selected_provider_family_count`,
`api_key_check_provider_route_live_data_required_family_count`, and
`api_key_check_provider_route_data_mode_counts`. It also mirrors the check summary
status fields as `api_key_check_status`, `api_key_check_count`,
`api_key_check_passed_count`, `api_key_check_failed_count`,
`api_key_check_failed_keys`, `api_key_check_tools_with_failures`,
`api_key_check_tool_failure_counts`, `api_key_check_network_call`,
`api_key_check_mutates_local_state`, and
`api_key_check_secret_values_returned`. The first failed check is mirrored as
`api_key_check_first_failed_tool`, `api_key_check_first_failed_name`,
`api_key_check_first_failed_key`, `api_key_check_first_failed_expected`,
`api_key_check_first_failed_actual`,
`api_key_check_first_failed_provider_family`,
`api_key_check_first_failed_provider`,
`api_key_check_first_failed_smoke_command_name`,
`api_key_check_first_failed_preferred_env_key`,
`api_key_check_first_failed_accepted_env_keys`, and
`api_key_check_first_failed_secret_values_returned`. The
top-level `api_key_pipeline_failure_summary`
(`api_key_pipeline_failure_summary.v1`) correlates those summaries into one
operator-facing row with `status`, `has_failures`, `failure_category`,
`failed_stage_names`, `failed_check_keys`, `tools_with_failures`,
`first_failed_stage_name`, `first_failed_check_key`, `next_action_name`,
`next_action_command`, `next_action_provider_family`,
`next_action_provider`, `next_action_smoke_command_name`,
`next_action_expected_live_contract`, `next_action_expected_live_checks`,
`next_action_is_recovery`, `provider_recovery_required`,
`provider_recovery_item_count`, `selected_provider_class_by_family`,
`provider_route_data_mode_by_family`,
`provider_route_live_data_required_by_family`, `all_selected_routes_live`,
`network_call`, `mutates_local_state`, and `secret_values_returned`. When the
failure category is provider recovery, it also includes `preferred_env_key` and
`accepted_env_keys` without returning key values, so failure summary provider identity,
expected live checks, route-family evidence, and safety flags are visible in
compact output. The
compact top-level payload also mirrors API-key failure one-line fields:
`api_key_failure_status`, `api_key_failure_category`, `api_key_has_failures`,
`api_key_failed_stage_names`, `api_key_failed_check_keys`,
`api_key_tools_with_failures`, `api_key_first_failed_stage_name`, and
`api_key_first_failed_check_key`,
`api_key_failure_next_action_name`, `api_key_failure_next_action_command`,
`api_key_failure_next_action_provider_family`,
`api_key_failure_next_action_provider`,
`api_key_failure_next_action_smoke_command_name`,
`api_key_failure_next_action_expected_live_contract`,
`api_key_failure_next_action_expected_live_checks`,
`api_key_failure_next_action_is_recovery`,
`api_key_failure_provider_recovery_required`,
`api_key_failure_provider_recovery_item_count`,
`api_key_failure_preferred_env_key`,
`api_key_failure_accepted_env_keys`, `api_key_failure_network_call`,
`api_key_failure_mutates_local_state`, and
`api_key_failure_secret_values_returned`, plus route-family mirrors
`api_key_failure_selected_provider_class_by_family`,
`api_key_failure_provider_route_data_mode_by_family`,
`api_key_failure_provider_route_live_data_required_by_family`, and
`api_key_failure_all_selected_routes_live`, plus route count aggregates
`api_key_failure_provider_route_family_count`,
`api_key_failure_selected_provider_family_count`,
`api_key_failure_provider_route_live_data_required_family_count`, and
`api_key_failure_provider_route_data_mode_counts`.
The top-level `api_key_setup_file_summary`
(`api_key_setup_file_summary.v1`) keeps `.env.example` and `.env` setup state
visible with `source_path`, `target_path`, `source_exists`, `target_exists`,
`copy_required`, `copy_command`, `preferred_env_keys`, `dotenv_examples`,
`configured_provider_families`, `missing_provider_families`,
`next_setup_step`, and `ready_to_run_live_smoke`, without returning secret
values or mutating files. The top-level `api_key_dotenv_loading_summary`
(`api_key_dotenv_loading_summary.v1`) shows `dotenv_supported`,
`dotenv_loading_enabled`, `disabled`, `disabled_env_key`,
`configuration_precedence`, `.env.example`/`.env` file status,
`next_setup_step`, and `ready_to_run_live_smoke`, so disabled dotenv loading or
precedence issues are visible without returning key values. The top-level
one-line dotenv fields mirror the same state as `api_key_dotenv_supported`,
`api_key_dotenv_loading_enabled`, `api_key_dotenv_disabled`,
`api_key_dotenv_disabled_env_key`, `api_key_dotenv_configuration_precedence`,
`api_key_dotenv_source_path`, `api_key_dotenv_target_path`,
`api_key_dotenv_source_exists`, `api_key_dotenv_target_exists`,
`api_key_dotenv_copy_required`, `api_key_dotenv_next_setup_step`,
`api_key_dotenv_ready_to_run_live_smoke`, `api_key_dotenv_network_call`,
`api_key_dotenv_mutates_local_state`, and
`api_key_dotenv_secret_values_returned`. The top-level
`api_key_provider_selection_summary`
(`api_key_provider_selection_summary.v1`) shows the actual provider factory
selection with `provider_factory`, `selected_provider_classes`,
`configured_provider_families`, `missing_provider_families`,
`configured_env_keys_by_provider_family`, `provider_env_key_hints_by_family`,
`provider_auto_selects_live_provider_by_family`,
`provider_optional_live_mode_env_by_family`,
`provider_live_mode_required_by_family`,
`all_configured_auto_select_live_provider`, `any_live_mode_required`,
`selected_provider_by_family`, `selected_provider_class_by_family`,
`provider_route_data_mode_by_family`,
`provider_route_live_data_required_by_family`,
`all_selected_routes_live`, and `ready_to_run_live_smoke`, so API-key
auto-selection, each provider family's `optional_live_mode_env`, and whether
`live_mode_required` is false can be verified together with the selected live
provider class and route mode, without secret values. The top-level
`api_key_provider_selection_status`, `api_key_provider_factory`,
`api_key_selected_provider_classes`, `api_key_selected_provider_class_count`,
`api_key_selected_provider_by_family`,
`api_key_selected_provider_class_by_family`,
`api_key_provider_route_data_mode_by_family`,
`api_key_provider_route_live_data_required_by_family`,
`api_key_provider_all_selected_routes_live`,
`api_key_provider_provider_route_family_count`,
`api_key_provider_selected_provider_family_count`,
`api_key_provider_provider_route_live_data_required_family_count`,
`api_key_provider_provider_route_data_mode_counts`,
`api_key_configured_env_keys_by_provider_family`, and
`api_key_provider_env_key_hints_by_family`,
`api_key_provider_auto_selects_live_provider_by_family`,
`api_key_provider_optional_live_mode_env_by_family`,
`api_key_provider_live_mode_required_by_family`,
`api_key_provider_all_configured_auto_select_live_provider`, and
`api_key_provider_any_live_mode_required` mirror this nested summary so
compact clients can show the actual API-key-selected route and confirm
`auto_selects_live_provider` directly. The top-level
`readiness_summary` mirrors provider smoke or recovery `preferred_env_key` and
`accepted_env_keys`, plus `next_operator_action_expected_live_contract` and
`next_operator_action_expected_live_checks`, from the next operator action
without returning key values. It also carries route-family readiness evidence
with `selected_provider_class_by_family`,
`provider_route_data_mode_by_family`,
`provider_route_live_data_required_by_family`, and
`all_selected_routes_live`, mirrored at top level as
`api_key_readiness_selected_provider_class_by_family`,
`api_key_readiness_provider_route_data_mode_by_family`,
`api_key_readiness_provider_route_live_data_required_by_family`, and
`api_key_readiness_all_selected_routes_live`, plus route count aggregates
`api_key_readiness_provider_route_family_count`,
`api_key_readiness_selected_provider_family_count`,
`api_key_readiness_provider_route_live_data_required_family_count`, and
`api_key_readiness_provider_route_data_mode_counts`.
The top-level
`api_key_integration_status_summary`
(`api_key_integration_status_summary.v1`) combines setup file, dotenv,
provider selection, failure, and next-action evidence into one operator row with
`status`, `api_keys_configured`, `dotenv_loading_enabled`,
`dotenv_target_exists`, `live_providers_selected`, `ready_to_run_live_smoke`,
`configured_provider_families`, `missing_provider_families`,
`selected_provider_classes`, `selected_provider_class_by_family`,
`provider_route_data_mode_by_family`,
`provider_route_live_data_required_by_family`, `all_selected_routes_live`,
`provider_smoke_count`, `ready_provider_smoke_count`,
`blocked_provider_smoke_count`,
`failure_category`, `has_failures`,
`next_action_name`, `next_action_provider_family`, `next_action_provider`,
`next_action_smoke_command_name`, `next_action_is_recovery`, and
`next_action_network_call`, plus `next_action_status`, `next_action_command`,
`next_action_required_env_keys`, `next_action_network_call_policy`,
`next_action_next_after_action`, `next_action_dotenv_target_path`,
`next_action_source_path`, `next_action_target_path`,
`next_action_secret_input_required`, `next_action_dotenv_examples`, and
`next_action_dotenv_example_count`,
`next_action_mutates_local_state`, and `next_action_secret_values_returned`, so
the integration status row itself carries the next executable local command,
required env-key names, network-call policy, and dotenv setup handoff details
without returning secrets. It also includes `provider_recovery_action_status`,
`provider_recovery_retry_ready`, `provider_recovery_all_retryable`,
`provider_recovery_has_pending`, `provider_recovery_has_blocked`,
`provider_recovery_item_count`, `provider_recovery_pending_count`,
`provider_recovery_blocked_count`, `provider_error_count`, and
`provider_recovery_smoke_count`. It also includes recovery identity lists:
`provider_recovery_provider_families`, `provider_recovery_providers`,
`provider_recovery_pending_provider_families`,
`provider_recovery_pending_providers`,
`provider_recovery_blocked_provider_families`, and
`provider_recovery_blocked_providers`. It also includes recovery command lists:
`provider_recovery_smoke_command_names`, `provider_recovery_smoke_commands`,
`provider_recovery_pending_smoke_command_names`,
`provider_recovery_pending_smoke_commands`,
`provider_recovery_blocked_smoke_command_names`, and
`provider_recovery_blocked_smoke_commands`. It mirrors the key integration
readiness values as top-level scalars/lists:
`api_key_integration_status`,
`api_key_integration_api_keys_configured`,
`api_key_integration_dotenv_loading_enabled`,
`api_key_integration_dotenv_target_exists`,
`api_key_integration_live_providers_selected`,
`api_key_integration_ready_to_run_live_smoke`,
`api_key_integration_configured_provider_families`,
`api_key_integration_missing_provider_families`,
`api_key_integration_selected_provider_classes`,
`api_key_integration_selected_provider_class_by_family`,
`api_key_integration_provider_route_data_mode_by_family`,
`api_key_integration_provider_route_live_data_required_by_family`,
`api_key_integration_all_selected_routes_live`,
`api_key_integration_provider_route_family_count`,
`api_key_integration_selected_provider_family_count`,
`api_key_integration_provider_route_live_data_required_family_count`,
`api_key_integration_provider_route_data_mode_counts`,
`api_key_integration_provider_smoke_count`,
`api_key_integration_ready_provider_smoke_count`,
`api_key_integration_blocked_provider_smoke_count`, and
`api_key_integration_next_action_name`. It also mirrors the one-shot pipeline
smoke command as `api_key_integration_one_shot_pipeline_smoke_name`,
`api_key_integration_one_shot_pipeline_smoke_command`,
`api_key_integration_one_shot_pipeline_smoke_status`,
`api_key_integration_one_shot_pipeline_smoke_blocked_reason`,
`api_key_integration_one_shot_pipeline_smoke_unblock_action_name`,
`api_key_integration_one_shot_pipeline_smoke_unblock_command`,
`api_key_integration_one_shot_pipeline_smoke_unblock_next_after_action`,
`api_key_integration_one_shot_pipeline_smoke_unblock_source_path`,
`api_key_integration_one_shot_pipeline_smoke_unblock_target_path`,
`api_key_integration_one_shot_pipeline_smoke_unblock_dotenv_target_path`,
`api_key_integration_one_shot_pipeline_smoke_unblock_followup_required_env_keys`,
`api_key_integration_one_shot_pipeline_smoke_unblock_followup_required_env_key_count`,
`api_key_integration_one_shot_pipeline_smoke_unblock_followup_dotenv_examples`,
`api_key_integration_one_shot_pipeline_smoke_unblock_followup_dotenv_example_count`,
`api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_name`,
`api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_provider_families`,
`api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_provider_family_count`,
`api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_provider_by_family`,
`api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_preferred_env_key_by_family`,
`api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_accepted_env_keys_by_family`,
`api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_required_env_keys_by_family`,
`api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_missing_env_keys_by_family`,
`api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_missing_env_keys`,
`api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_missing_env_key_count`,
`api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_configured_env_keys_by_family`,
`api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_configured_env_keys`,
`api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_configured_env_key_count`,
`api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_configured_by_family`,
`api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_configured_provider_families`,
`api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_blocked_provider_families`,
`api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_configured_provider_family_count`,
`api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_blocked_provider_family_count`,
`api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_all_provider_families_configured`,
`api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_setup_status_by_family`,
`api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_next_setup_action_by_family`,
`api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_next_setup_actions`,
`api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_next_setup_action_count`,
`api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_command`,
`api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_status`,
`api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_requires_api_keys`,
`api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_ready_after_env_keys`,
`api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_api_key_only_setup`,
`api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_api_key_only_setup_ready_after_env_keys`,
`api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_api_key_only_setup_next_command_name`,
`api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_api_key_only_setup_next_command`,
`api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_api_key_only_setup_next_command_status`,
`api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_api_key_only_setup_next_command_requires_api_keys`,
`api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_api_key_only_setup_next_command_ready_after_env_keys`,
`api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_api_key_only_setup_next_command_provider_families`,
`api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_api_key_only_setup_next_command_provider_family_count`,
`api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_api_key_only_setup_next_command_configured_provider_families`,
`api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_api_key_only_setup_next_command_blocked_provider_families`,
`api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_api_key_only_setup_next_command_configured_provider_family_count`,
`api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_api_key_only_setup_next_command_blocked_provider_family_count`,
`api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_api_key_only_setup_next_command_all_provider_families_configured`,
`api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_api_key_only_setup_next_command_selected_provider_classes`,
`api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_api_key_only_setup_next_command_selected_provider_class_count`,
`api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_api_key_only_setup_next_command_selected_provider_class_by_family`,
`api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_api_key_only_setup_next_command_provider_route_data_mode_by_family`,
`api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_api_key_only_setup_next_command_provider_route_live_data_required_by_family`,
`api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_api_key_only_setup_next_command_all_selected_routes_live`,
`api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_api_key_only_setup_next_command_provider_route_family_count`,
`api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_api_key_only_setup_next_command_selected_provider_family_count`,
`api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_api_key_only_setup_next_command_provider_route_live_data_required_family_count`,
`api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_api_key_only_setup_next_command_provider_route_data_mode_counts`,
`api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_api_key_only_setup_next_command_provider_by_family`,
`api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_api_key_only_setup_next_command_preferred_env_key_by_family`,
`api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_api_key_only_setup_next_command_accepted_env_keys_by_family`,
`api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_api_key_only_setup_next_command_required_env_keys_by_family`,
`api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_api_key_only_setup_next_command_missing_env_keys_by_family`,
`api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_api_key_only_setup_next_command_missing_env_keys`,
`api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_api_key_only_setup_next_command_missing_env_key_count`,
`api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_api_key_only_setup_next_command_configured_env_keys_by_family`,
`api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_api_key_only_setup_next_command_configured_env_keys`,
`api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_api_key_only_setup_next_command_configured_env_key_count`,
`api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_api_key_only_setup_next_command_configured_by_family`,
`api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_api_key_only_setup_next_command_setup_status_by_family`,
`api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_api_key_only_setup_next_command_next_setup_action_by_family`,
`api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_api_key_only_setup_next_command_next_setup_actions`,
`api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_api_key_only_setup_next_command_next_setup_action_count`,
`api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_api_key_only_setup_next_command_required_env_keys`,
`api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_api_key_only_setup_next_command_required_env_key_count`,
`api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_api_key_only_setup_next_command_dotenv_examples`,
`api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_api_key_only_setup_next_command_dotenv_example_count`,
`api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_api_key_only_setup_next_command_expected_live_contracts`,
`api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_api_key_only_setup_next_command_expected_live_contract_count`,
`api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_api_key_only_setup_next_command_expected_live_contracts_by_family`,
`api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_api_key_only_setup_next_command_expected_live_checks`,
`api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_api_key_only_setup_next_command_expected_live_check_count`,
`api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_api_key_only_setup_next_command_expected_live_checks_by_family`,
`api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_api_key_only_setup_next_command_network_call`,
`api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_api_key_only_setup_next_command_network_call_policy`,
`api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_api_key_only_setup_next_command_mutates_local_state`,
`api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_api_key_only_setup_next_command_secret_values_returned`,
`api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_network_call`,
`api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_network_call_policy`,
`api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_mutates_local_state`,
`api_key_integration_one_shot_pipeline_smoke_unblock_followup_smoke_secret_values_returned`,
`api_key_integration_one_shot_pipeline_smoke_unblock_ready_to_run`,
`api_key_integration_one_shot_pipeline_smoke_unblock_network_call`,
`api_key_integration_one_shot_pipeline_smoke_unblock_mutates_local_state`,
`api_key_integration_one_shot_pipeline_smoke_unblock_secret_values_returned`,
`api_key_integration_one_shot_pipeline_smoke_has_command`,
`api_key_integration_one_shot_pipeline_smoke_ready_to_run`,
`api_key_integration_one_shot_pipeline_smoke_requires_api_keys`,
`api_key_integration_one_shot_pipeline_smoke_network_call`,
`api_key_integration_one_shot_pipeline_smoke_network_call_policy`,
`api_key_integration_one_shot_pipeline_smoke_mutates_local_state`, and
`api_key_integration_one_shot_pipeline_smoke_secret_values_returned`, so compact
clients can show the API-key-only integration smoke command without exposing
secret values. It also mirrors next-action details as
`api_key_integration_next_action_provider_family`,
`api_key_integration_next_action_provider`,
`api_key_integration_next_action_selected_provider_class`,
`api_key_integration_next_action_provider_route_data_mode`,
`api_key_integration_next_action_provider_route_live_data_required`,
`api_key_integration_next_action_smoke_command_name`,
`api_key_integration_next_action_is_recovery`, and
`api_key_integration_next_action_network_call`. It also mirrors
`api_key_integration_next_action_status`,
`api_key_integration_next_action_command`,
`api_key_integration_next_action_has_command`,
`api_key_integration_next_action_ready_to_run`,
`api_key_integration_next_action_requires_api_keys`,
`api_key_integration_next_action_mutates_local_state`, and
`api_key_integration_next_action_secret_values_returned`. It also mirrors
`api_key_integration_next_action_preferred_env_key`,
`api_key_integration_next_action_accepted_env_keys`,
`api_key_integration_next_action_accepted_env_key_count`,
`api_key_integration_next_action_required_env_keys`,
`api_key_integration_next_action_required_env_key_count`,
`api_key_integration_next_action_network_call_policy`,
`api_key_integration_next_action_expected_live_contract`, and
`api_key_integration_next_action_expected_live_checks`,
`api_key_integration_next_action_expected_live_check_count`, so compact clients can
show whether API keys are configured, live providers are selected, and the next
live/recovery step can call the network, mutate local state, or satisfy the
expected live contract without nested parsing. It also mirrors dotenv setup
details as `api_key_integration_next_action_next_after_action`,
`api_key_integration_next_action_dotenv_target_path`,
`api_key_integration_next_action_source_path`,
`api_key_integration_next_action_target_path`,
`api_key_integration_next_action_secret_input_required`,
`api_key_integration_next_action_dotenv_examples`, and
`api_key_integration_next_action_dotenv_example_count`.
It also mirrors integration-wide provider smoke progress as
`api_key_integration_provider_smoke_count`,
`api_key_integration_ready_provider_smoke_count`, and
`api_key_integration_blocked_provider_smoke_count`.
It also mirrors provider smoke progress for that integration next action as
`api_key_integration_next_action_provider_smoke_count`,
`api_key_integration_next_action_ready_provider_smoke_count`,
`api_key_integration_next_action_blocked_provider_smoke_count`,
`api_key_integration_next_action_next_provider_smoke_command_name`,
`api_key_integration_next_action_next_provider_smoke_command`,
`api_key_integration_next_action_next_provider_smoke_has_command`,
`api_key_integration_next_action_next_provider_smoke_ready_to_run`,
`api_key_integration_next_action_next_provider_smoke_requires_api_keys`,
`api_key_integration_next_action_next_provider_smoke_next_setup_action`,
`api_key_integration_next_action_next_provider_smoke_provider_family`,
`api_key_integration_next_action_next_provider_smoke_provider`,
`api_key_integration_next_action_next_provider_smoke_selected_provider_class`,
`api_key_integration_next_action_next_provider_smoke_provider_route_data_mode`,
`api_key_integration_next_action_next_provider_smoke_provider_route_live_data_required`,
`api_key_integration_next_action_next_provider_smoke_status`,
`api_key_integration_next_action_next_provider_smoke_network_call`,
`api_key_integration_next_action_next_provider_smoke_network_call_policy`,
`api_key_integration_next_action_next_provider_smoke_expected_live_contract`,
`api_key_integration_next_action_next_provider_smoke_expected_live_checks`,
`api_key_integration_next_action_next_provider_smoke_expected_live_check_count`,
`api_key_integration_next_action_next_provider_smoke_preferred_env_key`,
`api_key_integration_next_action_next_provider_smoke_accepted_env_keys`,
`api_key_integration_next_action_next_provider_smoke_accepted_env_key_count`,
`api_key_integration_next_action_next_provider_smoke_mutates_local_state`, and
`api_key_integration_next_action_next_provider_smoke_secret_values_returned`.
The nested `api_key_integration_status_summary` carries the same next-provider-smoke
command, next setup action, provider identity, route, status, network policy, expected live
contract/checks, env-key hints, mutation flag, and secret redaction flag.
It also
mirrors the first pending recovery command as
`next_pending_recovery_smoke_command_name`,
`next_pending_recovery_smoke_command`,
`next_pending_recovery_provider_family`, `next_pending_recovery_provider`,
`next_pending_recovery_selected_provider_class`,
`next_pending_recovery_provider_route_data_mode`,
`next_pending_recovery_provider_route_live_data_required`,
`next_pending_recovery_next_setup_action`,
`next_pending_recovery_preferred_env_key`,
`next_pending_recovery_accepted_env_keys`,
`next_pending_recovery_network_call_policy`,
`next_pending_recovery_smoke_available`,
`next_pending_recovery_network_call`,
`next_pending_recovery_mutates_local_state`, and
`next_pending_recovery_secret_values_returned`. It mirrors the first blocked
recovery item as `next_blocked_recovery_smoke_command_name`,
`next_blocked_recovery_smoke_command`,
`next_blocked_recovery_provider_family`, `next_blocked_recovery_provider`,
`next_blocked_recovery_selected_provider_class`,
`next_blocked_recovery_provider_route_data_mode`,
`next_blocked_recovery_provider_route_live_data_required`,
`next_blocked_recovery_next_setup_action`,
`next_blocked_recovery_preferred_env_key`,
`next_blocked_recovery_accepted_env_keys`,
`next_blocked_recovery_network_call_policy`,
`next_blocked_recovery_smoke_available`,
`next_blocked_recovery_network_call`,
`next_blocked_recovery_mutates_local_state`, and
`next_blocked_recovery_secret_values_returned`. When the
next action summary carries provider smoke
or recovery metadata, it also includes `preferred_env_key` and
`accepted_env_keys`, so key-only live setup status is visible with provider
identity and env-key aliases without reading every nested summary or returning
secret values. The
top-level command summary and checklist also expose `next_provider_smoke` and
`next_provider_smoke_command_name` once at least one provider smoke command is
ready, and `setup_status_summary` mirrors the no-secret `next_provider_smoke`
object and `next_provider_smoke_command_name`, without returning secret values.
Its live data, signal workflow, and recording sub-smoke summaries include
stage-level setup fields such as `live_data_setup_summary_status`,
`ready_to_run_live_smoke`, `provider_route_status`, `provider_family_summary`,
`configured_provider_family_count`, `missing_provider_families`,
`live_data_setup_steps`, `next_setup_step`, `setup_step_count`,
`next_operator_action`, `provider_setup_actions`, `provider_setup_action_count`,
`provider_smoke_plan`, `provider_smoke_count`,
`ready_provider_smoke_count`, `blocked_provider_smoke_count`, and
`next_smoke_command_name` so the blocked stage, next provider setup action, and
provider smoke readiness are visible without returning secret values. Provider
or network failures during live sub-smokes are reported as no-secret `conflict` payloads
without returning exception messages, URLs, or API key values. Direct provider
smoke `error_summary` rows include no-secret `preferred_env_key`,
`accepted_env_keys`, `expected_live_contract`, and `expected_live_checks`, so a
failed API-key-backed smoke points to the provider key to check and the contract
that must pass. The one-shot payload and live-data sub-smoke summary also expose
`provider_error_summaries`,
`provider_error_summary_count`, `failed_provider_families`,
`failed_provider_count`, `first_provider_error_summary`,
`next_provider_recovery_action`, `next_provider_recovery_smoke`,
`next_provider_recovery_smoke_command_name`, `provider_recovery_smokes`, and
`provider_recovery_smoke_count` so failed provider families and their no-secret
recovery smoke commands are visible immediately after API-key-backed smoke
failures.
The top-level `api_key_provider_recovery_checklist`
(`api_key_provider_recovery_checklist.v1`) pairs each failed provider error row
with its matching no-secret `recovery_smoke_command` and
`recovery_smoke_available` flag, plus
`selected_provider_class_by_family`, `provider_route_data_mode_by_family`,
`provider_route_live_data_required_by_family`, and `all_selected_routes_live`,
so API-key-only recovery can rerun the right provider smoke with the selected
live provider route evidence visible without manually matching
`provider_error_summaries` to `provider_recovery_smokes`. Individual checklist
items also include no-secret `selected_provider_class`,
`provider_route_data_mode`, and `provider_route_live_data_required` for their
provider family.
The `api_key_operator_checklist` mirrors provider recovery state as
`provider_recovery_status`, `provider_recovery_required`,
`provider_recovery_item_count`, `next_provider_recovery_action`, and
`provider_recovery_checklist`, so the next no-secret provider recovery command
stays visible beside the setup steps. When recovery is required, the checklist
adds a `recover_failed_providers` blocking step so `ready=false`,
`blocking_step_names`, and `next_blocking_action` point at the rerunnable
no-secret recovery smoke command. In that recovery state,
`api_key_operator_checklist.status` becomes `conflict` and `current_step`
becomes `recover_failed_providers`. The one-shot top-level
`next_operator_action` and `readiness_summary.next_operator_action` also point
to `recover_failed_providers` so every summary exposes the same next recovery
command. Summary mirrors also expose
`next_operator_action_selected_provider_class`,
`next_operator_action_provider_route_data_mode`,
`next_operator_action_provider_route_live_data_required`,
`next_action_selected_provider_class`, `next_action_provider_route_data_mode`,
and `next_action_provider_route_live_data_required`, so the immediate command's
live provider route is visible without parsing nested rows.
The Hermes gate returns `hermes_mcp_config_readiness.v1`, including the expected
stdio server command, server module, MCP server name, config path existence, and
whether the operator has registered the MCP config. It does not start Hermes.
Set `HALO_SWING_HERMES_CONFIG_PATH` and the non-secret
`HALO_SWING_HERMES_MCP_CONFIG_REGISTERED=true` flag in `.env` after registering
the MCP server in the local Hermes config to make the readiness check
reproducible from local config values.
The live data gate returns `live_data_source_readiness.v1` and tracks market
OHLCV, macro, and news API-key readiness separately. The check may use
non-secret booleans or environment presence, but it does not return key values.
Live data providers auto-select when their supported API-key aliases are
present. Exported environment variables satisfy setup even when repo-root
`.env` has not been copied, so the next setup action moves directly to provider
smokes once all required provider keys are configured. Market OHLCV live data is
wired behind the provider boundary for Polygon:

```bash
POLYGON_API_KEY=your_polygon_key
```

`HALO_SWING_MARKET_DATA_API_KEY` is accepted as the project-specific alias for
the same key. Without either key, market data remains fixture-backed and
offline.
The summary-only pipeline CLI reads the same aliases from a launch-directory
`.env`. A local `.env` containing only `POLYGON_API_KEY`, `FRED_API_KEY`, and
`NEWSAPI_KEY` is enough to select the live Polygon, FRED, and NewsAPI providers
without exported API-key environment variables. Project-specific aliases remain
accepted for all three providers.
When one of these keys selects the live Polygon provider, market snapshot
payloads explicitly declare `live_data_required=true` and `network_call=true`
in `market_snapshot_contract`, and the guard reports
`live_data_boundary_declared`. Fixture/replay defaults keep `network_call=false`
and the `no_live_data_required` guard.

Macro live data is wired behind the same provider boundary for FRED:

```bash
FRED_API_KEY=your_fred_key
```

`HALO_SWING_MACRO_API_KEY` and `HALO_SWING_FRED_API_KEY` are accepted as
project-specific aliases. When one of these keys selects the live FRED provider,
`get_macro_snapshot` declares `live_data_required=true` and `network_call=true`
in `macro_filter_contract`, and `macro_filter_guard` reports
`live_data_boundary_declared` plus `network_call_declared`. Without one of these
keys, macro data remains fixture-backed with `no_live_data_required` and
`no_network_call` guard checks.

News live data is wired through NewsAPI:

```bash
NEWSAPI_KEY=your_newsapi_key
```

`HALO_SWING_NEWS_API_KEY` and `NEWS_API_KEY` are accepted aliases; `NEWSAPI_KEY`
is the preferred copy/paste setup key. Without one of these keys, news evidence remains fixture-backed. When
one of these keys selects the live NewsAPI provider, `get_news_bundle` declares
`live_data_required=true`, `network_call=true`, and `secret_values_returned=false`;
the `news_source_policy_guard` reports `live_data_boundary_declared` and
`network_call_declared`.

Direct live provider smoke success payloads for `get_market_snapshot`,
`get_macro_snapshot`, and `get_news_bundle` include `provider_smoke_summary`
(`provider_smoke_summary.v1`) with provider identity, smoke command name,
`preferred_env_key`, `accepted_env_keys`, `expected_live_contract`,
`expected_live_checks`, `network_call`, and `secret_values_returned=false`.
This keeps each successful API-key-backed provider smoke self-describing without
returning the API key value.

The optional `HALO_SWING_MARKET_DATA_MODE=live`,
`HALO_SWING_MACRO_DATA_MODE=live`, and `HALO_SWING_NEWS_DATA_MODE=live` env
values are still accepted for explicit operator intent and source validation,
but they are not required when the matching API key is present.

The Telegram gate returns `telegram_delivery_readiness.v1`. It accepts either a
bot-token readiness signal or a gateway readiness signal, exposes only booleans,
and keeps `send_call=false`, `network_call=false`, and
`credential_storage_added=false`. Actual Telegram delivery remains blocked until
the Hermes/Telegram environment is configured outside this offline harness.

For Binance testnet read-only smoke readiness, encrypted credentials alone are
not sufficient. Confirm passphrase availability with a non-secret boolean only:

```bash
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_readiness --input-json '{"binance_passphrase_confirmed":true}'
```

For reproducible local readiness, set the same non-secret confirmation in
`.env` after verifying that the credential passphrase is available at smoke
time:

```bash
HALO_SWING_BINANCE_PASSPHRASE_CONFIRMED=true
```

This flag does not store or reveal the passphrase; the read-only account
snapshot still requires the passphrase to be typed at smoke time.

Live BTC order submission readiness is separate from read-only smoke readiness.
It remains blocked unless all order-specific approvals are represented without
secrets: explicit live-order approval, `HALO_SWING_BINANCE_ENABLE_LIVE_TRADING=true`,
encrypted credentials, manual passphrase availability, Binance console
trade-only/no-withdraw attestation, testnet policy compatibility, and emergency
kill switch disabled. The readiness check still reports `order_submission=false`
and `network_call=false`.

After confirming in the Binance console that the key is COIN-M trade-only and
withdraw/transfer permissions are disabled, record that non-secret attestation
in `.env`:

```bash
HALO_SWING_BINANCE_TRADE_ONLY_PERMISSION_ATTESTED=true
```

This flag only affects readiness evidence. It does not enable order submission;
live orders still require explicit live-order approval, the live trading env
flag, valid credentials, manual passphrase input, passing risk checks, and the
confirmation string.

If and only if you have made the live-order approval decision, record that
non-secret readiness approval in `.env` as readiness evidence only:

```bash
HALO_SWING_BINANCE_LIVE_ORDER_APPROVED=true
```

This still does not submit orders. `execute_btc_order` continues to require the
confirmation string `CONFIRM_BTC_BINANCE_COINM_ORDER`, the live trading env
flag, encrypted credentials, manual passphrase input, and passing risk checks.

At this point a repo-root `.env` can provide the local readiness values for
Hermes config/registration, Telegram token or gateway, live data API keys,
Binance encrypted credential path, live trading, passphrase confirmation,
trade-only/no-withdraw attestation, and live-order approval. With those values,
`get_integration_readiness` can mark the integration evidence gates ready
without public tool inputs. `MIGRATION_GO` and `REPOSITORY_GO` are durable
storage approvals recorded in the SSOT; database repository use still requires
explicit `database_path` tool inputs rather than automatic `.env` activation.
This all-env readiness smoke is offline only: no network call, no Hermes runtime
start, no Telegram send, no order submission, and no secret values returned.
Use `get_integration_setup_checklist` when you want the missing `.env` keys,
durable gate approvals, and local harness command templates in one structured
payload. The checklist itself is non-mutating: it does not write `.env`, create
credential files, call networks, start Hermes, send Telegram messages, submit
orders, or return secret values.

BTC COIN-M trading admin:

```bash
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.trading_admin_web --host 127.0.0.1 --port 8766
```

Open `http://127.0.0.1:8766`. The admin page is local-only and manages:

```text
- encrypted Binance COIN-M API credentials
- max_notional_usd_per_order
- max_daily_order_count
- max_daily_loss_usd
- coinm_contract_size_usd
- emergency_kill_switch_enabled
- Binance public connectivity check
- read-only account and BTC position snapshot
- BTC COIN-M order preview
- daily counter reset
```

Offline COIN-M account snapshot normalization:

```bash
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness normalize_binance_coinm_account_snapshot --input-json '{"balance":[{"asset":"BTC","balance":"0.25","availableBalance":"0.2"}],"positions":[{"symbol":"BTCUSD_PERP","positionAmt":"3","entryPrice":"90000","markPrice":"92000"}]}'
```

This normalizes caller-supplied Binance COIN-M balance/position rows into a
BTC-only read-only `portfolio_sync_contract`. It does not require credentials,
call networks, submit orders, or return secret values. The live read-only
account snapshot still requires encrypted testnet credentials and a manual
passphrase at smoke time.

Pass the resulting snapshot to `preview_btc_order` as `portfolio_snapshot` to
receive `position_effect`. This indicates whether the preview opens, increases,
reduces, closes, or flips the BTC position. It remains a dry run and does not
submit orders.

Credential storage:

```yaml
path: state/binance_credentials.enc.json
algorithm: Fernet
kdf: PBKDF2HMAC-SHA256
iterations: 390000
commit_policy: forbidden
permission_policy_schema: binance_credential_policy.v1
required_permission: coin_m_futures_trade
withdraw_permission_allowed: false
passphrase_handling: manual_input_only
```

`get_binance_credentials_status` and `preview_btc_order` return the same
non-secret credential policy. The tooling does not verify Binance console
permissions by network call; the operator must attest that the key is COIN-M
trade-only and has withdraw/transfer permissions disabled before any live order
approval is considered.

Emergency kill switch smoke:

```bash
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness update_btc_risk_settings --input-json '{"emergency_kill_switch_enabled":true,"settings_path":"/private/tmp/halo_swing_kill_switch_settings.json"}' --no-audit
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness execute_btc_order --input-json '{"confirm":"CONFIRM_BTC_BINANCE_COINM_ORDER","settings_path":"/private/tmp/halo_swing_kill_switch_settings.json"}' --no-audit
```

The second command must return `blocked_reason:
emergency_kill_switch_enabled`. Use an ignored or temporary settings path for
local smoke checks.

MCP stdio server command:

```bash
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.server
```

The stdio server waits for an MCP client; use the harness command for one-shot smoke checks.

P0 smoke must stay offline. Dependency installation may use the network; tests and health checks must not require live APIs or secrets.

## Hermes MCP Config Target

Current P0 target shape:

```yaml
mcp_servers:
  halo_swing:
    type: stdio
    command: "<repo>/.venv/bin/python"
    args: ["-m", "halo_swing_mcp.server"]
    env:
      PYTHONPATH: "<repo>/src"
    tools:
      include:
        - health_check
        - get_market_snapshot
        - get_macro_snapshot
        - get_event_calendar
        - get_news_bundle
        - create_document_evidence_card
        - calculate_indicators
        - render_chart
        - score_leverage_swing
        - generate_trade_guide
        - evaluate_position
        - record_signal
        - label_signal_outcome
        - evaluate_score_performance
        - get_signal_replay_bundle
        - get_latest_signal_record
        - get_storage_health
        - apply_storage_migrations
        - suggest_weight_update
        - compare_champion_challenger
        - generate_latest_signal_report
        - generate_position_review_report
        - generate_cron_prompt_pack
        - get_integration_readiness
        - get_integration_setup_checklist
        - get_live_data_api_key_status
        - get_live_data_provider_route
        - validate_live_data_smoke_result
        - run_live_data_smoke
        - run_integration_smoke
        - run_live_signal_workflow_smoke
        - run_live_recording_smoke
        - run_api_key_pipeline_smoke
        - get_audit_log
        - get_audit_summary
        - get_runtime_status
        - record_runtime_checkpoint
        - get_btc_risk_settings
        - update_btc_risk_settings
        - get_btc_risk_status
        - reset_btc_daily_risk_state
        - save_binance_credentials
        - get_binance_credentials_status
        - check_binance_coinm_connectivity
        - get_binance_coinm_account_snapshot
        - normalize_binance_coinm_account_snapshot
        - preview_btc_order
        - execute_btc_order
```

Replace `<repo>` with the repository root. Later live-data phases may add API
keys to `env`, but the offline MVP tools must not require them.

## DevOps Gate Checklist

```yaml
before_dev_starts:
  - .venv exists or setup command is documented
  - requirements.txt installs successfully
  - dependency smoke passes
  - .gitignore excludes local environment and secrets

before_qc_starts:
  - server command is documented
  - harness command is documented
  - pytest command is documented
  - live smoke commands are clearly separated from offline tests

before_hermes_registration:
  - MCP server starts by stdio command
  - health_check returns a stable schema
  - Hermes config path uses absolute paths
  - no API key is required for health_check

before_cron_or_long_running_jobs:
  - run journal path is configured
  - checkpoint path is configured and ignored by git
  - watchdog thresholds are documented
  - dump retention/cleanup policy is documented
  - external supervisor restart policy is documented
  - crash-loop backoff is documented
  - log rotation and disk retention limits are documented
  - critical watchdog alerts have a destination
  - production cron jobs have idempotency keys and duplicate-run locks
```

## 24x7 Operating Guardrails

These are required before enabling unattended live cron jobs:

```yaml
process_supervision:
  required: true
  examples:
    - launchd on macOS
    - systemd on Linux
    - Hermes runner if it provides restart/backoff controls
  required_controls:
    - restart on crash
    - crash-loop backoff
    - graceful shutdown timeout
    - stdout/stderr log capture

resource_limits:
  required: true
  controls:
    - memory soft limit
    - memory hard limit
    - max queue length
    - max evidence bundle size
    - max checkpoint/log/artifact retention

failure_controls:
  required: true
  controls:
    - timeout per live call
    - retry limit with backoff and jitter
    - circuit breaker per data provider
    - stale-data warning
    - degraded-mode report

alerting:
  required: true
  critical_events:
    - hard memory limit approached
    - repeated provider failures
    - checkpoint write failure
    - database write failure
    - duplicate cron lock conflict
    - stale data used in report
```
