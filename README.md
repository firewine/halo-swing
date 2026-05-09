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
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness score_leverage_swing --input-json '{"asset":"TQQQ"}'
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_trade_guide --input-json '{"asset":"TQQQ"}'
PYTHONPATH=src ./.venv/bin/python -m pytest
PYTHONPATH=src ./.venv/bin/python -m ruff check .
```

The offline MVP exposes fixture-backed versions of the core MCP tools:

```text
get_market_snapshot
get_macro_snapshot
get_event_calendar
get_news_bundle
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
get_audit_log
get_audit_summary
get_btc_risk_settings
update_btc_risk_settings
get_btc_risk_status
reset_btc_daily_risk_state
save_binance_credentials
get_binance_credentials_status
preview_btc_order
execute_btc_order
```

All default tests are offline and require no market data API keys. Runtime
ledger and chart artifacts are written only when those tools are called and
should stay under ignored runtime locations such as `state/` or `artifacts/`.

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

Open `http://127.0.0.1:8766` to set Binance COIN-M API credentials and BTC risk
limits. Credentials are encrypted into `state/binance_credentials.enc.json`;
plaintext API keys, API secrets, and passphrases are not committed.
