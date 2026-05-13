"""Local-only BTC COIN-M trading settings admin page."""

from __future__ import annotations

import argparse
import json
import math
import sys
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import urlparse

from halo_swing_mcp.binance_btc import (
    check_binance_coinm_connectivity,
    get_binance_coinm_account_snapshot,
    preview_btc_order,
)
from halo_swing_mcp.config import get_settings
from halo_swing_mcp.risk_settings import (
    get_btc_risk_status,
    reset_btc_daily_risk_state,
    update_btc_risk_settings,
)
from halo_swing_mcp.secret_store import (
    get_binance_credentials_status,
    save_binance_credentials,
)


DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8766


HTML = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Halo Swing Trading Admin</title>
  <style>
    :root {
      color-scheme: light;
      --bg: #f6f7f9;
      --panel: #ffffff;
      --ink: #172033;
      --muted: #667085;
      --line: #d7dde7;
      --accent: #1d5fd1;
      --warn: #9a3412;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      background: var(--bg);
      color: var(--ink);
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      font-size: 14px;
    }
    header {
      padding: 18px 24px 12px;
      border-bottom: 1px solid var(--line);
      background: var(--panel);
    }
    h1 { margin: 0; font-size: 22px; font-weight: 700; letter-spacing: 0; }
    main {
      display: grid;
      grid-template-columns: minmax(260px, 380px) minmax(320px, 1fr);
      gap: 16px;
      padding: 18px 24px 28px;
    }
    section {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 14px;
    }
    h2 { margin: 0 0 12px; font-size: 15px; letter-spacing: 0; }
    label { display: block; margin-bottom: 10px; color: var(--muted); }
    input {
      display: block;
      width: 100%;
      min-height: 36px;
      margin-top: 4px;
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 7px 9px;
      font: inherit;
      color: var(--ink);
      background: #fff;
    }
    button {
      min-height: 36px;
      border: 1px solid var(--accent);
      border-radius: 6px;
      padding: 7px 11px;
      font: inherit;
      font-weight: 650;
      color: #fff;
      background: var(--accent);
      cursor: pointer;
    }
    .secondary { background: #fff; color: var(--accent); }
    .stack { display: grid; gap: 16px; }
    .status {
      display: grid;
      grid-template-columns: repeat(2, minmax(130px, 1fr));
      gap: 10px;
    }
    .metric {
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 10px;
      background: #fbfcfe;
    }
    .metric strong { display: block; font-size: 18px; margin-bottom: 4px; }
    .metric span { color: var(--muted); }
    code {
      display: block;
      white-space: pre-wrap;
      word-break: break-word;
      font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
      font-size: 12px;
      background: #f1f4f8;
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 10px;
      max-height: 280px;
      overflow: auto;
    }
    .message { min-height: 20px; margin-top: 10px; color: var(--warn); }
    @media (max-width: 860px) {
      main { grid-template-columns: 1fr; padding: 14px; }
      .status { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>
  <header>
    <h1>Halo Swing Trading Admin</h1>
  </header>
  <main>
    <div class="stack">
      <section>
        <h2>Binance COIN-M Credentials</h2>
        <form id="credentialsForm">
          <label>API Key<input name="api_key" autocomplete="off" required></label>
          <label>API Secret<input name="api_secret" type="password" autocomplete="off" required></label>
          <label>Encryption Passphrase<input name="passphrase" type="password" autocomplete="new-password" minlength="8" required></label>
          <button type="submit">Save Encrypted</button>
        </form>
        <div class="message" id="credentialsMessage"></div>
      </section>
      <section>
        <h2>Risk Settings</h2>
        <form id="riskForm">
          <label>Max USDT Per Order<input name="max_notional_usd_per_order" type="number" step="0.01" min="0.01" required></label>
          <label>Max Daily Orders<input name="max_daily_order_count" type="number" step="1" min="1" required></label>
          <label>Max Daily Loss USDT<input name="max_daily_loss_usd" type="number" step="0.01" min="0.01" required></label>
          <label>COIN-M Contract Size USD<input name="coinm_contract_size_usd" type="number" step="0.01" min="0.01" required></label>
          <label><input name="emergency_kill_switch_enabled" type="checkbox"> Emergency Kill Switch</label>
          <button type="submit">Save Settings</button>
        </form>
        <div class="message" id="riskMessage"></div>
      </section>
      <section>
        <h2>Order Preview</h2>
        <form id="previewForm">
          <label>Side<input name="side" value="BUY" required></label>
          <label>Contracts<input name="quantity" type="number" step="1" min="1" value="1" required></label>
          <label>Position Side<input name="position_side" placeholder="BOTH / LONG / SHORT"></label>
          <button type="submit">Preview Order</button>
        </form>
        <div class="message" id="previewMessage"></div>
      </section>
    </div>
    <div class="stack">
      <section>
        <h2>Status</h2>
        <div class="status" id="status"></div>
        <button class="secondary" id="checkConnectivity" type="button">Check Binance Public</button>
        <button class="secondary" id="resetState" type="button">Reset Daily Counters</button>
      </section>
      <section>
        <h2>Read-Only Account</h2>
        <form id="accountForm">
          <label>Credential Passphrase<input name="credential_passphrase" type="password" autocomplete="current-password" required></label>
          <button type="submit">Read Account Snapshot</button>
        </form>
        <div class="message" id="accountMessage"></div>
      </section>
      <section>
        <h2>Payload</h2>
        <code id="payload">{}</code>
      </section>
    </div>
  </main>
  <script>
    const statusEl = document.querySelector("#status");
    const payloadEl = document.querySelector("#payload");
    const riskForm = document.querySelector("#riskForm");
    const credentialsForm = document.querySelector("#credentialsForm");
    const riskMessage = document.querySelector("#riskMessage");
    const credentialsMessage = document.querySelector("#credentialsMessage");
    const accountForm = document.querySelector("#accountForm");
    const accountMessage = document.querySelector("#accountMessage");
    const previewForm = document.querySelector("#previewForm");
    const previewMessage = document.querySelector("#previewMessage");

    function escapeHtml(value) {
      return value.replace(/[&<>"']/g, (char) => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#039;"
      }[char]));
    }

    function metric(label, value) {
      return `<div class="metric"><strong>${escapeHtml(String(value ?? ""))}</strong><span>${escapeHtml(label)}</span></div>`;
    }

    function formObject(form) {
      const payload = Object.fromEntries(new FormData(form).entries());
      for (const input of form.querySelectorAll("input[type='checkbox']")) {
        payload[input.name] = input.checked;
      }
      return payload;
    }

    async function postJson(path, body) {
      const response = await fetch(path, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(body)
      });
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.error || "request_failed");
      return payload;
    }

    function fillRiskForm(settings) {
      for (const [key, value] of Object.entries(settings)) {
        const input = riskForm.elements[key];
        if (!input) continue;
        if (input.type === "checkbox") input.checked = Boolean(value);
        else input.value = value;
      }
    }

    async function loadStatus() {
      const response = await fetch("/api/status");
      const payload = await response.json();
      const settings = payload.risk.settings;
      fillRiskForm(settings);
      statusEl.innerHTML = [
        metric("credentials", payload.credentials.configured ? "configured" : "missing"),
        metric("api key", payload.credentials.api_key_hint || "none"),
        metric("environment", payload.execution.testnet ? "testnet" : "live"),
        metric("execution policy", payload.execution.force_testnet_execution ? "testnet only" : "env selected"),
        metric("kill switch", settings.emergency_kill_switch_enabled ? "enabled" : "off"),
        metric("remaining orders", payload.risk.remaining_daily_order_count),
        metric("remaining loss", payload.risk.remaining_daily_loss_usd)
      ].join("");
      payloadEl.textContent = JSON.stringify(payload, null, 2);
    }

    credentialsForm.addEventListener("submit", async (event) => {
      event.preventDefault();
      credentialsMessage.textContent = "";
      try {
        const payload = await postJson("/api/credentials", formObject(credentialsForm));
        credentialsForm.reset();
        credentialsMessage.textContent = "saved";
        payloadEl.textContent = JSON.stringify(payload, null, 2);
        await loadStatus();
      } catch (error) {
        credentialsMessage.textContent = error.message;
      }
    });

    riskForm.addEventListener("submit", async (event) => {
      event.preventDefault();
      riskMessage.textContent = "";
      try {
        const payload = await postJson("/api/risk-settings", formObject(riskForm));
        riskMessage.textContent = "saved";
        payloadEl.textContent = JSON.stringify(payload, null, 2);
        await loadStatus();
      } catch (error) {
        riskMessage.textContent = error.message;
      }
    });

    previewForm.addEventListener("submit", async (event) => {
      event.preventDefault();
      previewMessage.textContent = "";
      try {
        const payload = await postJson("/api/order-preview", formObject(previewForm));
        payloadEl.textContent = JSON.stringify(payload, null, 2);
      } catch (error) {
        previewMessage.textContent = error.message;
      }
    });

    accountForm.addEventListener("submit", async (event) => {
      event.preventDefault();
      accountMessage.textContent = "";
      try {
        const payload = await postJson("/api/account-snapshot", formObject(accountForm));
        accountForm.reset();
        payloadEl.textContent = JSON.stringify(payload, null, 2);
      } catch (error) {
        accountMessage.textContent = error.message;
      }
    });

    document.querySelector("#checkConnectivity").addEventListener("click", async () => {
      try {
        const payload = await postJson("/api/connectivity", {});
        payloadEl.textContent = JSON.stringify(payload, null, 2);
      } catch (error) {
        payloadEl.textContent = JSON.stringify({error: error.message}, null, 2);
      }
    });

    document.querySelector("#resetState").addEventListener("click", async () => {
      const payload = await postJson("/api/risk-state/reset", {});
      payloadEl.textContent = JSON.stringify(payload, null, 2);
      await loadStatus();
    });

    loadStatus();
  </script>
</body>
</html>
"""


def admin_status_payload() -> dict[str, Any]:
    """Return trading admin status without exposing secrets."""

    settings = get_settings()
    return {
        "credentials": get_binance_credentials_status(),
        "risk": get_btc_risk_status(),
        "execution": {
            "testnet": settings.binance_testnet,
            "force_testnet_execution": settings.binance_force_testnet_execution,
            "live_trading_enabled": settings.binance_enable_live_trading,
        },
    }


def create_handler() -> type[BaseHTTPRequestHandler]:
    """Create the local trading admin request handler."""

    class TradingAdminHandler(BaseHTTPRequestHandler):
        server_version = "HaloSwingTradingAdmin/0.1"

        def do_GET(self) -> None:  # noqa: N802
            parsed = urlparse(self.path)
            if parsed.path == "/":
                self._send_text(HTTPStatus.OK, "text/html; charset=utf-8", HTML)
                return
            if parsed.path == "/api/status":
                self._send_json(HTTPStatus.OK, admin_status_payload())
                return
            self._send_json(HTTPStatus.NOT_FOUND, {"error": "not_found"})

        def do_POST(self) -> None:  # noqa: N802
            parsed = urlparse(self.path)
            try:
                payload = self._read_json()
                if parsed.path == "/api/credentials":
                    result = save_binance_credentials(
                        api_key=_required_str(payload.get("api_key"), "api_key"),
                        api_secret=_required_str(
                            payload.get("api_secret"),
                            "api_secret",
                        ),
                        passphrase=_required_str(
                            payload.get("passphrase"),
                            "passphrase",
                        ),
                    )
                    self._send_json(HTTPStatus.OK, result)
                    return
                if parsed.path == "/api/connectivity":
                    self._send_json(HTTPStatus.OK, check_binance_coinm_connectivity())
                    return
                if parsed.path == "/api/account-snapshot":
                    self._send_json(
                        HTTPStatus.OK,
                        get_binance_coinm_account_snapshot(
                            credential_passphrase=_optional_str(
                                payload.get("credential_passphrase"),
                                "credential_passphrase",
                            )
                        ),
                    )
                    return
                if parsed.path == "/api/order-preview":
                    self._send_json(
                        HTTPStatus.OK,
                        preview_btc_order(
                            side=_required_str(payload.get("side", "BUY"), "side"),
                            quantity=_required_str(
                                payload.get("quantity", "1"),
                                "quantity",
                            ),
                            position_side=_optional_str(
                                payload.get("position_side"),
                                "position_side",
                            ),
                        ),
                    )
                    return
                if parsed.path == "/api/risk-settings":
                    result = update_btc_risk_settings(
                        max_notional_usd_per_order=_optional_float(
                            payload.get("max_notional_usd_per_order"),
                            "max_notional_usd_per_order",
                        ),
                        max_daily_order_count=_optional_int(
                            payload.get("max_daily_order_count"),
                            "max_daily_order_count",
                        ),
                        max_daily_loss_usd=_optional_float(
                            payload.get("max_daily_loss_usd"),
                            "max_daily_loss_usd",
                        ),
                        coinm_contract_size_usd=_optional_float(
                            payload.get("coinm_contract_size_usd"),
                            "coinm_contract_size_usd",
                        ),
                        emergency_kill_switch_enabled=_optional_bool(
                            payload.get("emergency_kill_switch_enabled"),
                            "emergency_kill_switch_enabled",
                        ),
                    )
                    self._send_json(HTTPStatus.OK, result)
                    return
                if parsed.path == "/api/risk-state/reset":
                    self._send_json(HTTPStatus.OK, reset_btc_daily_risk_state())
                    return
                self._send_json(HTTPStatus.NOT_FOUND, {"error": "not_found"})
            except Exception as exc:
                self._send_json(HTTPStatus.BAD_REQUEST, {"error": str(exc)})

        def log_message(self, format: str, *args: Any) -> None:
            return

        def _read_json(self) -> dict[str, Any]:
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0:
                return {}
            body = self.rfile.read(length).decode("utf-8")
            payload = json.loads(body)
            if not isinstance(payload, dict):
                raise ValueError("payload must be a JSON object")
            return payload

        def _send_json(self, status: HTTPStatus, payload: dict[str, Any]) -> None:
            body = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _send_text(self, status: HTTPStatus, content_type: str, text: str) -> None:
            body = text.encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    return TradingAdminHandler


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Serve BTC COIN-M trading admin over HTTP")
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.host not in {DEFAULT_HOST, "localhost", "::1"}:
        print("Trading admin must bind to localhost only.", file=sys.stderr)
        return 2
    handler = create_handler()
    server = ThreadingHTTPServer((args.host, args.port), handler)
    host, port = server.server_address
    print(f"Serving Halo Swing trading admin at http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping trading admin server")
    finally:
        server.server_close()
    return 0


def _required_str(value: Any, field_name: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be a nonempty string")
    if not _has_no_control_characters(value):
        raise ValueError(f"{field_name} must not contain control characters")
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{field_name} must be a nonempty string")
    return normalized


def _optional_float(value: Any, field_name: str) -> float | None:
    if value is None:
        return None
    if isinstance(value, str):
        if not _has_no_control_characters(value):
            raise ValueError(f"{field_name} must not contain control characters")
        normalized_text = value.strip()
        if not normalized_text:
            return None
        try:
            normalized = float(normalized_text)
        except ValueError as exc:
            raise ValueError(f"{field_name} must be a positive finite number") from exc
    elif isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{field_name} must be a positive finite number")
    else:
        normalized = float(value)
    if not math.isfinite(normalized) or normalized <= 0.0:
        raise ValueError(f"{field_name} must be a positive finite number")
    return normalized


def _optional_int(value: Any, field_name: str) -> int | None:
    if value is None:
        return None
    if isinstance(value, str):
        if not _has_no_control_characters(value):
            raise ValueError(f"{field_name} must not contain control characters")
        normalized_text = value.strip()
        if not normalized_text:
            return None
        if not normalized_text.isdecimal():
            raise ValueError(f"{field_name} must be a positive integer")
        normalized = int(normalized_text)
    elif type(value) is int:
        normalized = value
    else:
        raise ValueError(f"{field_name} must be a positive integer")
    if normalized < 1:
        raise ValueError(f"{field_name} must be a positive integer")
    return normalized


def _optional_bool(value: Any, field_name: str) -> bool | None:
    if value is None:
        return None
    if type(value) is not bool:
        raise ValueError(f"{field_name} must be a boolean")
    return value


def _optional_str(value: Any, field_name: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be a string when provided")
    if not _has_no_control_characters(value):
        raise ValueError(f"{field_name} must not contain control characters")
    normalized = value.strip()
    return normalized or None


def _has_no_control_characters(value: str) -> bool:
    return all(ord(character) >= 32 and ord(character) != 127 for character in value)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
