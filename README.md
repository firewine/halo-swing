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
NewsAPI uses `HALO_SWING_NEWS_API_KEY` or `NEWS_API_KEY`. Exported environment
variables satisfy setup even if repo-root `.env` has not been copied, so the
next setup action moves directly to provider smokes. Without those keys, runs
remain fixture-backed and offline. The summary-only pipeline CLI reads the same
aliases from a launch-directory `.env`, so a local `.env` containing only
`HALO_SWING_MARKET_DATA_API_KEY`, `HALO_SWING_MACRO_API_KEY`, and
`HALO_SWING_NEWS_API_KEY` is enough to select the live Polygon, FRED, and
NewsAPI providers without exported API-key environment variables.
When a NewsAPI key selects live news,
`get_news_bundle` declares `live_data_required=true`, `network_call=true`, and
`secret_values_returned=false`, with guard checks for the live data boundary and
network call declaration. Direct live provider smoke success payloads include
`provider_smoke_summary` (`provider_smoke_summary.v1`) with provider identity,
smoke command name, `preferred_env_key`, `accepted_env_keys`,
`expected_live_contract`, `expected_live_checks`, `network_call`, and
`secret_values_returned=false`, so a single successful smoke result shows what
API-key-backed provider contract passed without exposing the key. Live provider
HTTP calls use
`HALO_SWING_LIVE_HTTP_TIMEOUT_SECONDS` with a default of `10` seconds, so
API-key-backed smokes fail back into no-secret provider recovery instead of
waiting indefinitely. The optional `*_DATA_MODE=live` env values are still
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
provider families, provider-level `preferred_env_key`, `setup_status`,
`next_setup_action`, `provider_family_summary`, the no-secret
`dotenv_template`, `dotenv_file_status`, `next_operator_action`, and the
one-shot smoke command without returning secrets. `next_operator_action` is the
single local action to take next: copy `.env.example` to `.env`, fill the
required API keys, run the provider smokes, or run `run_api_key_pipeline_smoke`:

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
includes `live_data_setup_summary`, aggregates direct provider smoke success
rows as no-secret `provider_smoke_summaries` with
`provider_smoke_summary_count`, and validates the combined payload:

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
top-level `next_operator_action`, `setup_status_summary`,
`api_key_next_action_summary`, `api_key_requirements_summary`,
`api_key_command_summary`,
`api_key_operator_checklist`, `api_key_pipeline_stage_summary`,
`api_key_pipeline_check_summary`, `live_data_setup_summary`, and the same
provider route summary so the one-shot smoke records API-key readiness, required
env keys and aliases, copy/smoke commands, ordered local setup steps, checklist
ready/blocking fields, progress counts, the no-secret `next_blocking_action`,
the compact `api_key_next_action_summary.v1` with `status`, `current_step`,
`ready`, `blocking_step_count`, `next_blocking_step`,
`provider_recovery_required`, `provider_recovery_status`,
`provider_recovery_item_count`, `next_action_name`, `next_action_command`,
`next_action_status`, `next_action_is_recovery`, `next_action_network_call`,
`next_action_mutates_local_state`, `next_action_provider_family`,
`next_action_provider`, `next_action_smoke_command_name`,
`selected_provider_class_by_family`, `provider_route_data_mode_by_family`,
`provider_route_live_data_required_by_family`, `all_selected_routes_live`,
`preferred_env_key`, `accepted_env_keys`, `required_env_keys`,
`next_after_action`, `dotenv_target_path`, `source_path`, `target_path`,
`secret_input_required`, and no-secret `dotenv_examples` /
`dotenv_example_count` when the next action points at a provider smoke command,
provider recovery, dotenv setup, or API-key fill step, plus provider
family counts, API-key setup status inside `readiness_summary`, the next local
action mirrored inside `readiness_summary`, readiness summary
`preferred_env_key` and `accepted_env_keys` when that action points at a
provider smoke command or provider recovery, the first no-secret
`next_provider_smoke` command in the top-level command summary and checklist
when a provider smoke is ready, the same no-secret `next_provider_smoke` object
and command name in `setup_status_summary`, and which provider factory route was
selected.
Pass `--summary-only` when you want a compact harness response after filling API
keys without editing the input JSON. For MCP callers, set `summary_only=true`
or `"summary_only":true` in the request payload for the same compact response.

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
It also keeps top-level `provider_smoke_summaries` and
`provider_smoke_summary_count` copied from the omitted
`live_data_smoke_summary`, so compact output still shows provider success
contracts/checks without returning secret values.
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
Summary-only next-action route evidence is mirrored at top level as
`api_key_next_action_selected_provider_class_by_family`,
`api_key_next_action_provider_route_data_mode_by_family`,
`api_key_next_action_provider_route_live_data_required_by_family`, and
`api_key_next_action_all_selected_routes_live`, plus route count aggregates
`api_key_next_action_provider_route_family_count`,
`api_key_next_action_selected_provider_family_count`,
`api_key_next_action_provider_route_live_data_required_family_count`, and
`api_key_next_action_provider_route_data_mode_counts`, so compact clients can
verify the full provider-family route map beside the single next command.
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
`api_key_setup_quickstart_command_plan_next_ready_provider_smoke_expected_live_contract`,
`api_key_setup_quickstart_command_plan_next_ready_provider_smoke_expected_live_checks`,
`api_key_setup_quickstart_command_plan_next_ready_provider_smoke_preferred_env_key`,
`api_key_setup_quickstart_command_plan_next_ready_provider_smoke_accepted_env_keys`,
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
`api_key_setup_quickstart_command_plan_next_blocked_provider_smoke_expected_live_contract`,
`api_key_setup_quickstart_command_plan_next_blocked_provider_smoke_expected_live_checks`,
`api_key_setup_quickstart_command_plan_next_blocked_provider_smoke_preferred_env_key`,
`api_key_setup_quickstart_command_plan_next_blocked_provider_smoke_accepted_env_keys`,
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
`api_key_setup_quickstart_next_command_plan_provider_family`,
`api_key_setup_quickstart_next_command_plan_provider`,
`api_key_setup_quickstart_next_command_plan_selected_provider_class`,
`api_key_setup_quickstart_next_command_plan_provider_route_data_mode`,
`api_key_setup_quickstart_next_command_plan_provider_route_live_data_required`,
`api_key_setup_quickstart_next_command_plan_expected_live_contract`,
`api_key_setup_quickstart_next_command_plan_expected_live_checks`,
`api_key_setup_quickstart_next_command_plan_preferred_env_key`,
`api_key_setup_quickstart_next_command_plan_accepted_env_keys`,
`api_key_setup_quickstart_next_command_plan_next_setup_action`,
`api_key_setup_quickstart_next_command_plan_status`,
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
returning key values, so the compact response still shows the exact local smoke
commands, expected live contract/checks, live-call policy, selected live
provider route, and accepted API-key aliases to use after API keys are
configured.
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
`api_key_provider_smoke_next_action_command_count`,
`api_key_provider_smoke_next_action_command_names`, and
`api_key_provider_smoke_next_action_commands`,
`api_key_next_provider_smoke_command_name`,
`api_key_next_provider_smoke_provider_family`,
`api_key_next_provider_smoke_provider`,
`api_key_next_provider_smoke_selected_provider_class`,
`api_key_next_provider_smoke_provider_route_data_mode`,
`api_key_next_provider_smoke_provider_route_live_data_required`,
`api_key_next_provider_smoke_command`,
`api_key_next_provider_smoke_next_setup_action`,
`api_key_next_provider_smoke_status`,
`api_key_next_provider_smoke_network_call`,
`api_key_next_provider_smoke_network_call_policy`,
`api_key_next_provider_smoke_expected_live_contract`,
`api_key_next_provider_smoke_expected_live_checks`,
`api_key_next_provider_smoke_preferred_env_key`,
`api_key_next_provider_smoke_accepted_env_keys`,
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
`api_key_next_ready_provider_smoke_expected_live_contract`,
`api_key_next_ready_provider_smoke_expected_live_checks`,
`api_key_next_ready_provider_smoke_preferred_env_key`,
`api_key_next_ready_provider_smoke_accepted_env_keys`,
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
`api_key_next_blocked_provider_smoke_expected_live_contract`,
`api_key_next_blocked_provider_smoke_expected_live_checks`,
`api_key_next_blocked_provider_smoke_preferred_env_key`,
`api_key_next_blocked_provider_smoke_accepted_env_keys`,
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
It keeps `api_key_pipeline_stage_summary`
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
When provider recovery smoke metadata exists, the stage summary includes stage
recovery provider identity and env-key hints without returning key values, so
the failed smoke stage is visible without reading every nested summary.
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
(`api_key_pipeline_check_summary.v1`) summarizing the top-level `checks` array
with `check_count`, `passed_check_count`, `failed_check_count`,
`failed_check_keys`, `tools_with_failures`, `tool_failure_counts`,
`first_failed_check`,
`selected_provider_class_by_family`, `provider_route_data_mode_by_family`,
`provider_route_live_data_required_by_family`, `all_selected_routes_live`, and
no-secret `failed_checks` rows containing `tool`, `name`, `key`, `expected`,
`actual`, and `passed=false`. When the matching stage has provider recovery
metadata, the check summary includes
`provider_family`, `provider`, `smoke_command_name`, `preferred_env_key`, and
`accepted_env_keys` without returning key values.
The compact top-level payload mirrors check route-family evidence as
`api_key_check_selected_provider_class_by_family`,
`api_key_check_provider_route_data_mode_by_family`,
`api_key_check_provider_route_live_data_required_by_family`, and
`api_key_check_all_selected_routes_live`, plus route count aggregates
`api_key_check_provider_route_family_count`,
`api_key_check_selected_provider_family_count`,
`api_key_check_provider_route_live_data_required_family_count`, and
`api_key_check_provider_route_data_mode_counts`.
It also mirrors the check summary status fields as
`api_key_check_status`, `api_key_check_count`,
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
`api_key_check_first_failed_secret_values_returned`.
The compact `api_key_pipeline_failure_summary`
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
`accepted_env_keys` without returning key values, so failure summary provider
identity, expected live checks, route-family evidence, and safety flags are
visible in compact output.
The compact top-level payload also mirrors API-key failure one-line fields:
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
(`api_key_setup_file_summary.v1`) keeps the `.env.example` and `.env` setup
state visible with `source_path`, `target_path`, `source_exists`,
`target_exists`, `copy_required`, `copy_command`, `preferred_env_keys`,
`dotenv_examples`, `configured_provider_families`,
`missing_provider_families`, `next_setup_step`, and
`ready_to_run_live_smoke`, without returning secret values or mutating files.
The top-level `api_key_dotenv_loading_summary`
(`api_key_dotenv_loading_summary.v1`) shows whether dotenv loading is supported
and enabled with `dotenv_supported`, `dotenv_loading_enabled`, `disabled`,
`disabled_env_key`, `configuration_precedence`, `.env.example`/`.env` file
status, `next_setup_step`, and `ready_to_run_live_smoke`, so a disabled dotenv
loader is visible without exposing key values.
Compact clients can also read the same dotenv state as top-level one-line
fields: `api_key_dotenv_supported`, `api_key_dotenv_loading_enabled`,
`api_key_dotenv_disabled`, `api_key_dotenv_disabled_env_key`,
`api_key_dotenv_configuration_precedence`, `api_key_dotenv_source_path`,
`api_key_dotenv_target_path`, `api_key_dotenv_source_exists`,
`api_key_dotenv_target_exists`, `api_key_dotenv_copy_required`,
`api_key_dotenv_next_setup_step`, `api_key_dotenv_ready_to_run_live_smoke`,
`api_key_dotenv_network_call`, `api_key_dotenv_mutates_local_state`, and
`api_key_dotenv_secret_values_returned`.
The top-level `api_key_provider_selection_summary`
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
provider class and route mode, without secret values.
It mirrors those values as top-level `api_key_provider_selection_status`,
`api_key_provider_factory`, `api_key_selected_provider_classes`,
`api_key_selected_provider_class_count`, `api_key_selected_provider_by_family`,
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
`api_key_provider_any_live_mode_required`, so compact clients can show the
actual API-key-selected route and confirm `auto_selects_live_provider` without
reading the nested summary.
The top-level `readiness_summary` mirrors the selected `next_operator_action`
and, when that action carries provider smoke or recovery env-key hints, also
includes `preferred_env_key`, `accepted_env_keys`,
`next_operator_action_expected_live_contract`, and
`next_operator_action_expected_live_checks` without returning key values. It
also carries route-family readiness evidence with
`selected_provider_class_by_family`, `provider_route_data_mode_by_family`,
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
The top-level `api_key_integration_status_summary`
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
`api_key_integration_next_action_name`. It also mirrors next-action details as
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
`api_key_integration_next_action_mutates_local_state`, and
`api_key_integration_next_action_secret_values_returned`. It also mirrors
`api_key_integration_next_action_preferred_env_key`,
`api_key_integration_next_action_accepted_env_keys`,
`api_key_integration_next_action_required_env_keys`,
`api_key_integration_next_action_network_call_policy`,
`api_key_integration_next_action_expected_live_contract`, and
`api_key_integration_next_action_expected_live_checks`, so compact clients can
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
`api_key_integration_next_action_next_provider_smoke_preferred_env_key`,
`api_key_integration_next_action_next_provider_smoke_accepted_env_keys`,
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
`accepted_env_keys`, so a key-only live setup can be checked with provider
identity and env-key aliases without reading every nested summary or returning
secret values.
Each sub-smoke summary also includes stage-level setup fields such as
`live_data_setup_summary_status`, `ready_to_run_live_smoke`,
`provider_route_status`, `provider_family_summary`,
`configured_provider_family_count`, `missing_provider_families`,
`live_data_setup_steps`, `next_setup_step`, `setup_step_count`,
`next_operator_action`, `provider_setup_actions`, `provider_setup_action_count`,
`provider_smoke_plan`, `provider_smoke_count`,
`ready_provider_smoke_count`, `blocked_provider_smoke_count`, and
`next_smoke_command_name`. Provider or network failures during live sub-smokes
are reported as no-secret `conflict` payloads without returning exception
messages, URLs, or API key values. Direct provider smoke `error_summary` rows
include no-secret `preferred_env_key`, `accepted_env_keys`,
`expected_live_contract`, and `expected_live_checks` so the failing API-key
source and success contract are visible without exposing the key. When provider
failures occur, `provider_error_summaries`, `provider_error_summary_count`,
`failed_provider_families`, `failed_provider_count`,
`first_provider_error_summary`, `next_provider_recovery_action`,
`next_provider_recovery_smoke`, `next_provider_recovery_smoke_command_name`,
`provider_recovery_smokes`, and `provider_recovery_smoke_count` identify the
failed providers and list the no-secret provider smoke commands to rerun.
The top-level `api_key_provider_recovery_checklist`
(`api_key_provider_recovery_checklist.v1`) pairs each failed provider row with
its matching no-secret `recovery_smoke_command` and
`recovery_smoke_available` flag, plus
`selected_provider_class_by_family`, `provider_route_data_mode_by_family`,
`provider_route_live_data_required_by_family`, and `all_selected_routes_live`,
so a failed API-key-backed smoke can be rerun with the selected live provider
route evidence visible without manually matching error and recovery arrays. The
individual checklist items also include no-secret `selected_provider_class`,
`provider_route_data_mode`, and `provider_route_live_data_required` for their
provider family.
`api_key_operator_checklist` mirrors this as `provider_recovery_status`,
`provider_recovery_required`, `provider_recovery_item_count`,
`next_provider_recovery_action`, and `provider_recovery_checklist`, keeping the
next recovery command visible in the same setup checklist. When recovery is
required, the checklist adds a `recover_failed_providers` blocking step so
`ready=false`, `blocking_step_names`, and `next_blocking_action` point at the
rerunnable no-secret recovery smoke command. In that recovery state,
`api_key_operator_checklist.status` becomes `conflict` and `current_step`
becomes `recover_failed_providers`. The one-shot top-level
`next_operator_action` and `readiness_summary.next_operator_action` also point
to `recover_failed_providers` so every summary exposes the same next recovery
command:

```bash
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness run_api_key_pipeline_smoke --summary-only --no-audit
```

The checklist is offline and non-mutating. It does not write `.env`, create
credential files, call networks, start Hermes, send Telegram messages, submit
orders, or return secret values. It also returns `live_data_setup_summary` so
API-key-only setup shows key readiness, provider route status, selected provider
classes, missing keys, and the one-shot pipeline smoke command without exposing
secret values. The summary includes `ready_to_run_live_smoke`,
`next_smoke_command`, `provider_family_summary`, `provider_setup_actions`
with no-secret `smoke_command` objects, `provider_smoke_plan`, and a no-secret
`dotenv_template` for the repo-root `.env` entries to fill before running smoke
commands. It also returns `dotenv_file_status` so the setup payload shows
whether `.env.example` and `.env` exist, the next setup action, and the
repo-local copy command hint without writing files or returning secret values.
`next_operator_action` summarizes the single next local action for API-key-only
setup without returning secret values, and points to provider smoke verification
before the one-shot pipeline smoke once API keys are ready. In that ready state,
it includes `next_provider_smoke` so the first provider smoke command is visible
without reading the full provider list. Summary mirrors also expose
`next_operator_action_selected_provider_class`,
`next_operator_action_provider_route_data_mode`,
`next_operator_action_provider_route_live_data_required`,
`next_action_selected_provider_class`, `next_action_provider_route_data_mode`,
and `next_action_provider_route_live_data_required`, so the immediate command's
live provider route is visible without parsing nested rows.
`live_data_setup_steps` orders the local setup path as dotenv preparation, live
data API-key entry, provider smoke verification, and the one-shot pipeline
smoke. It also returns
`live_data_smoke_commands` for
`get_market_snapshot`, `get_macro_snapshot`, and `get_news_bundle`; run those
repo-local harness commands after filling the matching API keys to verify the
live providers and boundary contracts. Those smoke commands are read-only and
return no secret values, but they can call provider networks when the configured
API keys select live providers. If an individual provider smoke hits a provider
or network exception, it returns a no-secret `conflict` payload with the tool
name and exception type only, so URLs, exception messages, and API key values do
not leak into smoke output.
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
