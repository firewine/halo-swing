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
server_status: implemented
harness_status: implemented
storage_schema_status: deferred_to_p1
live_network_tests: disabled for P0
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

## P0 Server And Harness Commands

Verified P0 smoke commands:

```bash
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check
PYTHONPATH=src ./.venv/bin/python -m pytest
PYTHONPATH=src ./.venv/bin/python -m ruff check .
```

SQLite/schema commands are intentionally absent in P0. P1 starts with storage/schema architecture review before migrations or DB smoke commands are added.

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
    command: "/Users/june/Documents/New project 2/.venv/bin/python"
    args: ["-m", "halo_swing_mcp.server"]
    env:
      PYTHONPATH: "/Users/june/Documents/New project 2/src"
    tools:
      include:
        - health_check
```

Later phases may add API keys to `env`, but P0 must not require them.

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
