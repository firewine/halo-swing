# Halo Swing

Halo Swing is a personal market-swing decision system designed to run as a Hermes Agent MCP server.

The first goal is not automatic trading. The system collects market, macro, event, policy, geopolitical, and technical evidence, then produces swing guides for BTC and 2x/3x long index products such as QLD, TQQQ, SSO, UPRO, and SOXL.

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

## P0 Smoke Commands

```bash
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.harness health_check
PYTHONPATH=src ./.venv/bin/python -m pytest
PYTHONPATH=src ./.venv/bin/python -m ruff check .
```

The MCP server entrypoint is available at:

```bash
PYTHONPATH=src ./.venv/bin/python -m halo_swing_mcp.server
```
