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
storage_schema_status: jsonl_signal_repository_contract
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
showing feature-store persistence is not active before `MIGRATION_GO` and
`REPOSITORY_GO`.

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

`record_signal` writes a local JSONL runtime ledger. Use an ignored or temporary
path during development:

```bash
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness record_signal --input-json '{"ledger_path":"state/signal_ledger.jsonl"}'
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness label_signal_outcome --input-json '{"ledger_path":"state/signal_ledger.jsonl"}'
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness evaluate_score_performance --input-json '{"ledger_path":"state/signal_ledger.jsonl"}'
```

SQLite/schema commands remain absent from the offline MVP. The current ledger is
a reusable JSONL runtime adapter; migrations and repository persistence can be a
later implementation behind the same tool contracts.

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
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness run_api_key_pipeline_smoke --input-json '{"asset":"TQQQ","timeframe":"swing_3d_10d","symbols":["QQQ"],"topic":"macro"}' --no-audit
```

The readiness and checklist commands do not call networks or return secret
values. They report which future gates are still blocked for Hermes, Telegram,
DB migration/repository, Binance testnet read-only smoke, live order submission,
and live data adapters. They can read readiness inputs from exported environment
variables, a launch-directory `.env`, or the repo-root `.env` using the
precedence documented above. The checklist payload also includes
`live_data_smoke_commands` for
`get_market_snapshot`, `get_macro_snapshot`, and `get_news_bundle`. After
filling the matching API keys, run those repo-local harness commands to verify
the live provider outputs and boundary contracts. The smoke commands are
read-only and return no secret values, but they can call provider networks when
the configured keys select live providers. Use
`validate_live_data_smoke_result` on the collected smoke payloads to verify
`live_data_required`, `network_call`, live guard checks, and secret-return
metadata offline. Use `get_live_data_api_key_status` before the first live smoke
when you only need to confirm that supported Polygon, FRED, and NewsAPI aliases
are configured; it reports key names and missing provider families but never
secret values. Use `run_live_data_smoke` for the same validation in one
command after filling the market, macro, and news API keys. Use
`run_integration_smoke` to combine offline readiness gates and the live data
smoke result without starting Hermes, sending Telegram messages, submitting
orders, or returning secrets. After provider-level smoke passes, use
`run_live_signal_workflow_smoke` to verify the same API-key-backed live
boundary reaches `score_leverage_swing`, `generate_trade_guide`,
`evaluate_position`, and `generate_latest_signal_report` without starting
Hermes, sending Telegram messages, submitting orders, mutating state, or
returning secrets. Use `run_live_recording_smoke` to verify that a generated
live signal can also pass through `record_signal` with live run-journal metadata.
By default it uses an ephemeral JSONL ledger and leaves no runtime file; provide
`ledger_path` only when you intentionally want a retained local smoke ledger.
Use `run_api_key_pipeline_smoke` as the single post-setup check after filling
API keys; it combines live-data readiness, provider smoke, signal workflow smoke,
and recording smoke while still avoiding Hermes runtime starts, Telegram sends,
order submissions, retained state, and secret returns.
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
present. Market OHLCV live data is wired behind the provider boundary for
Polygon:

```bash
POLYGON_API_KEY=your_polygon_key
```

`HALO_SWING_MARKET_DATA_API_KEY` is accepted as the project-specific alias for
the same key. Without either key, market data remains fixture-backed and
offline.
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
NEWS_API_KEY=your_newsapi_key
```

`HALO_SWING_NEWS_API_KEY` is accepted as the project-specific alias. Without
either key, news evidence remains fixture-backed. When one of these keys selects
the live NewsAPI provider, `get_news_bundle` declares `live_data_required=true`,
`network_call=true`, and `secret_values_returned=false`; the
`news_source_policy_guard` reports `live_data_boundary_declared` and
`network_call_declared`.

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
without public tool inputs. `MIGRATION_GO` and `REPOSITORY_GO` still stay
blocked until their durable gates are approved. This all-env readiness smoke is
offline only: no network call, no Hermes runtime start, no Telegram send, no
order submission, and no secret values returned.
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
        - suggest_weight_update
        - compare_champion_challenger
        - generate_latest_signal_report
        - generate_position_review_report
        - generate_cron_prompt_pack
        - get_integration_readiness
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
