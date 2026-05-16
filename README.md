# Halo Swing

Halo Swing is a personal market-swing decision system designed to run as a Hermes Agent MCP server.

The system collects market, macro, event, policy, geopolitical, and technical evidence, then produces swing guides for BTC and 2x/3x long index products such as QLD, TQQQ, SSO, UPRO, and SOXL. Automatic order execution is restricted to BTC COIN-M futures only and is guarded by local risk settings, encrypted credentials, and explicit confirmation.

## Core Idea

```text
Hermes Agent
  -> conversation, Telegram, cron, memory, final explanation

Halo Swing MCP
  -> data collection, indicators, scoring, risk guides, signal logging, feedback
```

The system should answer:

```text
- Is this a swing-buy area?
- If yes, is 2x or 3x more appropriate?
- What invalidates the entry?
- Where should risk be cut?
- What is the take-profit zone?
- Did prior signals with similar conditions actually work?
```

## Documentation

All project documents live under [`docs/`](./docs/).

- [CONTEXT.md](./docs/CONTEXT.md): short project context for new chats and agents
- [WORKING.md](./docs/WORKING.md): current work tracker
- [devops-setup-guide.md](./docs/devops-setup-guide.md): local environment and Hermes MCP setup guide
- [halo-swing-development-plan.md](./docs/halo-swing-development-plan.md): SSOT development plan

## Local Environment

```bash
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Offline MVP Smoke Commands

```bash
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check
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
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_runtime_status --input-json '{"audit_log_path":"state/audit_log.jsonl","ledger_path":"state/signal_ledger.jsonl"}'
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness record_runtime_checkpoint --input-json '{"checkpoint_path":"state/runtime_checkpoints.jsonl","audit_log_path":"state/audit_log.jsonl","ledger_path":"state/signal_ledger.jsonl"}'
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness normalize_binance_coinm_account_snapshot --input-json '{"balance":[{"asset":"BTC","balance":"0.25","availableBalance":"0.2"}],"positions":[{"symbol":"BTCUSD_PERP","positionAmt":"3","entryPrice":"90000","markPrice":"92000"}]}'
PYTHONPATH=src ./.venv/bin/python -m pytest
PYTHONPATH=src ./.venv/bin/python -m ruff check .
```

The offline MVP exposes fixture-backed versions of the core MCP tools:

```text
get_market_snapshot
get_macro_snapshot
get_event_calendar
get_news_bundle
create_document_evidence_card
calculate_indicators
render_chart
score_leverage_swing
generate_trade_guide
evaluate_position
record_signal
label_signal_outcome
evaluate_score_performance
suggest_weight_update
compare_champion_challenger
generate_latest_signal_report
generate_position_review_report
generate_cron_prompt_pack
get_integration_readiness
get_audit_log
get_audit_summary
get_runtime_status
record_runtime_checkpoint
get_btc_risk_settings
update_btc_risk_settings
get_btc_risk_status
reset_btc_daily_risk_state
save_binance_credentials
get_binance_credentials_status
check_binance_coinm_connectivity
get_binance_coinm_account_snapshot
normalize_binance_coinm_account_snapshot
preview_btc_order
execute_btc_order
```

All default tests are offline and require no market data API keys. Runtime
ledger, runtime checkpoint, and chart artifacts are written only when those
tools are called and should stay under ignored runtime locations such as
`state/` or `artifacts/`.
Local setup reads ignored dotenv files without mutating `os.environ`: exported
environment variables take precedence, then a launch-directory `.env`, then the
repo-root `.env`. For the normal local path, copy `.env.example` to the
repository root as `.env` and fill only the API keys or config values you need.
Set `HALO_SWING_DISABLE_DOTENV=true` for isolated offline runs that must ignore
local operator secrets, such as tests or CI. This isolation flag may be
exported or set in `.env`; when it is true, other dotenv values are ignored.
Fixture OHLCV supports `1d`, `4h`, and `1h` timeframes for indicator and chart
tools; unsupported timeframes are rejected before any live adapter is involved.
`get_market_snapshot` returns `market_snapshot.v1` with QQQ, SPY, SMH, SOXX,
and BTC as the core fixture universe, freshness/degraded markers, and a guard
showing that feature-store persistence remains behind migration/repository
approval.
`calculate_indicators` exposes a `swing_level_contract` with gap detection,
20-bar support/resistance, and previous swing high/low levels.
`score_leverage_swing` returns `strategy_config_contract`, showing
`strategy_config.v1` validation, weight sum, threshold order, bounds checks, and
config hash reproducibility.
`generate_trade_guide` returns `trade_guide.v1` with entry, stop, take-profit,
time-exit, invalidation, config trace, and no-order-submission guards.
`evaluate_position` returns `position_management.v1` for WAIT/TRIM/EXIT/STOP
position decisions with numeric-authority and no-order-submission guards.
`get_macro_snapshot` exposes an offline `macro_filter_contract` and
`macro_filter_summary` for VIX, VXN, DXY, 2Y, 10Y, and WTI oil changes, and the
scoring path honors macro block flags without requiring live macro data.
Swing signals expose Phase 2 component scores for `trend`, `pullback`,
`breadth`, `volatility`, `theme`, and event risk. The new component diagnostics
do not automatically promote a challenger or change live behavior.
`get_event_calendar` exposes an offline `event_window_summary` plus per-event
`danger_window` payloads so 2x/3x pre-event blocks are visible without a live
calendar source or network call.
It also returns `event_policy.v1` covering CPI, FOMC, NFP, and large-cap
earnings fixture event types.
`get_news_bundle` exposes `news_score_contract`, and `score_leverage_swing`
returns `news_usage_contract` to show that the explicit `news_score` field feeds
the theme component used in swing scoring.
`get_news_bundle` also exposes `news_source_policy.v1`, covering Fed, Treasury,
White House, EIA, Iran/Hormuz, and AI/semiconductor fixture source groups
without enabling live collection.
Signal labels support `TAKE_PROFIT_FIRST`, `STOP_LOSS_FIRST`, `TIME_EXIT`,
`NO_DATA`, and `INVALIDATED_BY_EVENT` through the offline JSONL labeler.
`label_signal_outcome` exposes `signal_label_outcome.v1`; MFE, MAE, and
realized R are calculated only inside `price_path[:time_barrier_days]`.
`record_signal` stores a `run_journal.v1` entry in the JSONL ledger with
run/config traceability, an idempotency key, and no-network/no-DB guards.
`get_integration_readiness` reports blocked deployment gates without network
calls or secrets, including `live_data_source_readiness.v1` for market OHLCV,
macro, and news API-key readiness. Live data providers auto-select when their
supported API-key aliases are present: Polygon uses
`HALO_SWING_MARKET_DATA_API_KEY` or `POLYGON_API_KEY`; FRED uses
`HALO_SWING_MACRO_API_KEY`, `HALO_SWING_FRED_API_KEY`, or `FRED_API_KEY`; and
NewsAPI uses `HALO_SWING_NEWS_API_KEY` or `NEWS_API_KEY`. Without those keys,
runs remain fixture-backed and offline. When a NewsAPI key selects live news,
`get_news_bundle` declares `live_data_required=true`, `network_call=true`, and
`secret_values_returned=false`, with guard checks for the live data boundary and
network call declaration. The optional `*_DATA_MODE=live` env values are still
accepted for explicit operator intent/source validation, but they are not
required when the API key is present. It includes
`hermes_mcp_config_readiness.v1`
for config path and MCP registration evidence. `HALO_SWING_HERMES_CONFIG_PATH`
and the non-secret `HALO_SWING_HERMES_MCP_CONFIG_REGISTERED=true` flag may be
set in `.env` so readiness can be reproduced from local config values without
starting Hermes. It also exposes
`telegram_delivery_readiness.v1` for bot-token/gateway readiness while keeping
`send_call=false`, and a separate `live_order_submission` gate that requires
explicit approval, the live-trading env flag, encrypted credentials, manual
passphrase availability, trade-only/no-withdraw attestation, and kill-switch
evidence while still reporting `order_submission=false`.
`HALO_SWING_BINANCE_PASSPHRASE_CONFIRMED=true` may be set in `.env` as a
non-secret readiness confirmation; it never stores the passphrase, and read-only
account smoke calls still require the passphrase at call time.
`HALO_SWING_BINANCE_TRADE_ONLY_PERMISSION_ATTESTED=true` may also be set after
checking in the Binance console that the key is COIN-M trade-only with
withdraw/transfer permissions disabled. This is readiness evidence only and
does not enable order submission.
`HALO_SWING_BINANCE_LIVE_ORDER_APPROVED=true` may be set only after the
live-order approval decision has been made; it is also readiness evidence only.
`execute_btc_order` still requires `CONFIRM_BTC_BINANCE_COINM_ORDER`, the live
trading env flag, encrypted credentials, manual passphrase input, and passing
risk checks.
Together, repo-root `.env` values can make Hermes, Telegram, live data,
Binance testnet read-only, and live-order readiness evidence pass without
public tool inputs. `MIGRATION_GO` and `REPOSITORY_GO` remain blocked until
their durable gates are approved. This all-env readiness smoke still performs
no network call, no Hermes runtime start, no Telegram send, and no order
submission.
`get_integration_setup_checklist` turns the same readiness state into a local
setup checklist of `.env` keys, durable gate approvals, and harness commands:

```bash
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_integration_setup_checklist --no-audit
```

To check only live data API-key setup before making provider network calls, use
`get_live_data_api_key_status`; it reports configured alias names, missing
provider families, `provider_family_summary`, the no-secret `dotenv_template`,
`dotenv_file_status`, and the one-shot smoke command without returning secrets:

```bash
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_live_data_api_key_status --no-audit
```

To confirm the actual provider factory route selected by those keys, use
`get_live_data_provider_route`; it instantiates the configured provider chain
without calling provider networks:

```bash
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_live_data_provider_route --no-audit
```

After running the live data smoke commands from the checklist, pass the returned
payloads to `validate_live_data_smoke_result` to verify the market, macro, and
news live boundary contracts offline:

```bash
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness validate_live_data_smoke_result --input-file /path/to/live_data_smoke_payloads.json --no-audit
```

For a one-shot API-key-backed check, use `run_live_data_smoke`; it runs the
market, macro, and news smoke paths, includes no-network provider route evidence,
includes `live_data_setup_summary`, and validates the combined payload:

```bash
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness run_live_data_smoke --input-json '{"symbols":["QQQ"],"topic":"macro"}' --no-audit
```

To combine offline readiness evidence with the live data smoke result in one
payload, use `run_integration_smoke`; its top-level `provider_route_summary`
mirrors the live data smoke route evidence, and `live_data_setup_summary` shows
API-key setup readiness without returning secret values:

```bash
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness run_integration_smoke --input-json '{"symbols":["QQQ"],"topic":"macro"}' --no-audit
```

After the provider smoke passes, use `run_live_signal_workflow_smoke` to verify
that the API-key-backed live boundary reaches scoring, the trade guide, position
review, and the latest signal report. Its payload also includes
`live_data_setup_summary` so direct workflow smoke runs still show API-key setup
readiness and next smoke guidance:

```bash
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness run_live_signal_workflow_smoke --input-json '{"asset":"TQQQ","timeframe":"swing_3d_10d"}' --no-audit
```

To verify the live signal can also pass through the JSONL recording path without
leaving a runtime file, use `run_live_recording_smoke`; it uses an ephemeral
ledger unless you explicitly provide `ledger_path`. Its payload includes
`live_data_setup_summary` so recording smoke runs show API-key setup readiness
and next smoke guidance before any retained ledger is requested:

```bash
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness run_live_recording_smoke --input-json '{"asset":"TQQQ","timeframe":"swing_3d_10d"}' --no-audit
```

For a single post-setup check after filling API keys, use
`run_api_key_pipeline_smoke`; it combines readiness, provider live data, signal
workflow, and recording smoke checks. Its payload includes
`live_data_setup_summary` plus the same provider route summary so the one-shot
smoke records API-key readiness and which provider factory route was selected.
Each sub-smoke summary also includes stage-level setup fields such as
`live_data_setup_summary_status`, `ready_to_run_live_smoke`,
`provider_route_status`, `provider_family_summary`,
`configured_provider_family_count`, `missing_provider_families`, and
`next_smoke_command_name`:

```bash
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness run_api_key_pipeline_smoke --input-json '{"asset":"TQQQ","timeframe":"swing_3d_10d","symbols":["QQQ"],"topic":"macro"}' --no-audit
```

The checklist is offline and non-mutating. It does not write `.env`, create
credential files, call networks, start Hermes, send Telegram messages, submit
orders, or return secret values. It also returns `live_data_setup_summary` so
API-key-only setup shows key readiness, provider route status, selected provider
classes, missing keys, and the one-shot pipeline smoke command without exposing
secret values. The summary includes `ready_to_run_live_smoke`,
`next_smoke_command`, `provider_family_summary`, and a no-secret
`dotenv_template` for the repo-root `.env` entries to fill before running smoke
commands. It also returns `dotenv_file_status` so the setup payload shows
whether `.env.example` and `.env` exist, the next setup action, and the
repo-local copy command hint without writing files or returning secret values.
`live_data_setup_steps` orders the local setup path as dotenv preparation, live
data API-key entry, and the one-shot pipeline smoke. It also returns
`live_data_smoke_commands` for
`get_market_snapshot`, `get_macro_snapshot`, and `get_news_bundle`; run those
repo-local harness commands after filling the matching API keys to verify the
live providers and boundary contracts. Those smoke commands are read-only and
return no secret values, but they can call provider networks when the configured
API keys select live providers.
When a market data API key selects the live Polygon provider, market snapshot
payloads declare `live_data_required=true` and `network_call=true` in
`market_snapshot_contract`, and the guard uses
`live_data_boundary_declared`. Fixture/replay defaults keep
`network_call=false` and the existing `no_live_data_required` guard.
When a macro API key selects the live FRED provider, macro snapshots declare
`live_data_required=true` and `network_call=true` in `macro_filter_contract`,
and `macro_filter_guard` uses `live_data_boundary_declared` plus
`network_call_declared`. Fixture/replay macro snapshots keep
`network_call=false`, `no_live_data_required`, and `no_network_call`.
Report tools include an offline `delivery_preview` payload for Hermes and
Telegram. The preview contains Telegram message chunks and guard checks, but it
does not send messages or require credentials. Telegram previews expose the
`telegram_report_format.v1` contract for section-separated, 1-based message
chunks. Latest signal reports also include an `evidence_guard` that caps summary
sizes and records acknowledged conflict flags before text is handed to Hermes or
Telegram.
`generate_cron_prompt_pack` returns Hermes prompt templates for pre-market,
intraday, post-market, and position review jobs without installing a scheduler,
sending Telegram messages, or requiring credentials.
Performance evaluation supports explicit `score_calibration` plus a
deterministic 90-day fixture window with `out_of_sample_report`,
`walk_forward_report`, and `overfit_guard`; the guard includes
`deflated_sharpe_proxy.v1`, an offline conservative realized-R metric with a
multiple-testing penalty. It remains advisory and never promotes a challenger
without explicit approval. `suggest_weight_update`
returns a `challenger_config.v1` contract that keeps the candidate in shadow mode
with approval and out-of-sample requirements.
Evidence cards include `modality` and portable `artifact_ref` metadata.
`render_chart` returns a `chart_artifact.v1` contract and guard that confirm
the PNG was written with the offline stdlib renderer and no live data call.
`create_document_evidence_card` accepts caller-supplied PDF/document summaries
without parsing files, reading local documents, or calling networks, so Phase 8
multimodal inputs can be validated offline before any Hermes image/PDF flow is
enabled. `generate_latest_signal_report` can attach those cards through
`extra_evidence_cards` and returns a guarded `multimodal_context` when document
evidence or chart refs are present.
`normalize_binance_coinm_account_snapshot` turns caller-supplied COIN-M balance
and position payloads into a BTC-only read-only portfolio summary without
credentials, network calls, or order side effects. `preview_btc_order` can take
that snapshot as `portfolio_snapshot` and returns `position_effect`, showing
whether the preview would open, increase, reduce, close, or flip the BTC
position without submitting an order.

The MCP server entrypoint is available at:

```bash
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.server
```

## Audit Log Viewer

Tool calls are written as redacted JSONL audit events when invoked through the
CLI harness or MCP server. Use an ignored runtime path for local logs:

```bash
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check --audit-log-path state/audit_log.jsonl
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_audit_log --input-json '{"audit_log_path":"state/audit_log.jsonl","limit":50}' --audit-log-path state/audit_log.jsonl
```

Start the local web viewer:

```bash
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.audit_web --host 127.0.0.1 --port 8765 --audit-log-path state/audit_log.jsonl
```

Open `http://127.0.0.1:8765` to inspect events, filters, and summaries. The
viewer also exposes `/api/events` and `/api/summary` for automated checks.

## BTC COIN-M Trading Admin

Start the local-only management page:

```bash
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.trading_admin_web --host 127.0.0.1 --port 8766
```

Open `http://127.0.0.1:8766` to set Binance COIN-M API credentials, BTC risk
limits, run public connectivity checks, read account/position snapshots, and
preview orders. Credentials are encrypted into `state/binance_credentials.enc.json`;
plaintext API keys, API secrets, and passphrases are not committed. The local
risk settings include an emergency kill switch; when enabled it blocks order
execution even if the confirmation string is supplied. Credential status and
order previews expose `binance_credential_policy.v1`: the Binance key must be
trade-only for COIN-M futures, withdraw permissions are forbidden, and the
passphrase remains manual input only.
