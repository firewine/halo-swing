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
storage_schema_status: runtime_jsonl_ledger_for_offline_mvp
audit_log_status: runtime_jsonl_with_local_web_viewer
trading_admin_status: local_only_btc_coin_m_settings_and_encrypted_credentials
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

## Offline MVP Server And Harness Commands

Verified offline smoke commands:

```bash
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_market_snapshot --input-json '{"symbols":["QQQ","TQQQ","BTC"]}'
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness calculate_indicators --input-json '{"symbol":"QQQ"}'
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness score_leverage_swing --input-json '{"asset":"TQQQ"}'
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness generate_trade_guide --input-json '{"asset":"TQQQ"}'
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_audit_summary --input-json '{"audit_log_path":"state/audit_log.jsonl"}' --audit-log-path state/audit_log.jsonl
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness preview_btc_order --input-json '{"side":"BUY","quantity":"1"}'
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness get_btc_risk_status
PYTHONPATH=src ./.venv/bin/python -m pytest
PYTHONPATH=src ./.venv/bin/python -m ruff check .
```

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
- daily counter reset
```

Credential storage:

```yaml
path: state/binance_credentials.enc.json
algorithm: Fernet
kdf: PBKDF2HMAC-SHA256
iterations: 390000
commit_policy: forbidden
```

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
        - get_audit_log
        - get_audit_summary
        - get_btc_risk_settings
        - update_btc_risk_settings
        - get_btc_risk_status
        - reset_btc_daily_risk_state
        - save_binance_credentials
        - get_binance_credentials_status
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
