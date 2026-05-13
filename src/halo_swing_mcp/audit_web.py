"""Local web viewer for Halo Swing audit logs."""

from __future__ import annotations

import argparse
import json
import sys
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

from halo_swing_mcp.audit import audit_summary, read_audit_events, resolve_audit_log_path


DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8765
ALLOWED_HOSTS = {DEFAULT_HOST, "localhost", "::1"}


HTML = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Halo Swing Audit Log</title>
  <style>
    :root {
      color-scheme: light;
      --bg: #f7f8fb;
      --panel: #ffffff;
      --ink: #18202f;
      --muted: #667085;
      --line: #d8dee9;
      --accent: #2156d9;
      --ok: #0b7a45;
      --bad: #b42318;
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
      padding: 20px 24px 12px;
      border-bottom: 1px solid var(--line);
      background: var(--panel);
    }
    h1 { margin: 0; font-size: 22px; font-weight: 700; letter-spacing: 0; }
    main { padding: 18px 24px 28px; }
    .summary {
      display: grid;
      grid-template-columns: repeat(4, minmax(120px, 1fr));
      gap: 12px;
      margin-bottom: 16px;
    }
    .metric {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 12px;
    }
    .metric strong { display: block; font-size: 20px; margin-bottom: 4px; }
    .metric span { color: var(--muted); }
    .filters {
      display: grid;
      grid-template-columns: repeat(5, minmax(110px, 1fr)) auto;
      gap: 8px;
      margin-bottom: 14px;
    }
    input, button {
      min-height: 36px;
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 7px 9px;
      font: inherit;
      background: var(--panel);
    }
    button {
      background: var(--accent);
      border-color: var(--accent);
      color: #ffffff;
      cursor: pointer;
      font-weight: 600;
    }
    table {
      width: 100%;
      border-collapse: collapse;
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      overflow: hidden;
    }
    th, td {
      border-bottom: 1px solid var(--line);
      padding: 9px 10px;
      text-align: left;
      vertical-align: top;
    }
    th {
      background: #eef2f8;
      font-size: 12px;
      text-transform: uppercase;
      color: var(--muted);
    }
    tr:last-child td { border-bottom: 0; }
    code {
      white-space: pre-wrap;
      word-break: break-word;
      font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
      font-size: 12px;
    }
    .success { color: var(--ok); font-weight: 700; }
    .failure { color: var(--bad); font-weight: 700; }
    .empty {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 18px;
      color: var(--muted);
    }
    @media (max-width: 860px) {
      .summary { grid-template-columns: repeat(2, minmax(120px, 1fr)); }
      .filters { grid-template-columns: 1fr 1fr; }
      table { display: block; overflow-x: auto; }
    }
  </style>
</head>
<body>
  <header>
    <h1>Halo Swing Audit Log</h1>
  </header>
  <main>
    <section class="summary" id="summary"></section>
    <form class="filters" id="filters">
      <input name="limit" type="number" min="1" max="1000" value="100" aria-label="Limit">
      <input name="resource_id" placeholder="resource id" aria-label="Resource id">
      <input name="outcome" placeholder="outcome" aria-label="Outcome">
      <input name="actor" placeholder="actor (client filter)" aria-label="Actor">
      <input name="action" placeholder="action" aria-label="Action">
      <button type="submit">Refresh</button>
    </form>
    <div id="events"></div>
  </main>
  <script>
    const summary = document.querySelector("#summary");
    const events = document.querySelector("#events");
    const filters = document.querySelector("#filters");

    function metric(label, value) {
      return `<div class="metric"><strong>${escapeHtml(String(value ?? ""))}</strong><span>${escapeHtml(label)}</span></div>`;
    }

    function escapeHtml(value) {
      return value.replace(/[&<>"']/g, (char) => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#039;"
      }[char]));
    }

    function queryFromForm() {
      const params = new URLSearchParams(new FormData(filters));
      for (const [key, value] of Array.from(params.entries())) {
        if (!value) params.delete(key);
      }
      return params.toString();
    }

    async function load() {
      const query = queryFromForm();
      const [summaryResponse, eventsResponse] = await Promise.all([
        fetch("/api/summary"),
        fetch(`/api/events?${query}`)
      ]);
      const summaryPayload = await summaryResponse.json();
      let eventPayload = await eventsResponse.json();
      const actor = new FormData(filters).get("actor");
      if (actor) {
        eventPayload.events = eventPayload.events.filter((event) => event.actor === actor);
      }
      summary.innerHTML = [
        metric("total events", summaryPayload.total_events),
        metric("first event", summaryPayload.first_event_at || "none"),
        metric("last event", summaryPayload.last_event_at || "none"),
        metric("log path", summaryPayload.audit_log_path)
      ].join("");
      renderEvents(eventPayload.events);
    }

    function renderEvents(items) {
      if (!items.length) {
        events.innerHTML = `<div class="empty">No audit events match the current filters.</div>`;
        return;
      }
      const rows = items.map((event) => `
        <tr>
          <td>${escapeHtml(event.occurred_at || "")}</td>
          <td>${escapeHtml(event.actor || "")}</td>
          <td>${escapeHtml(event.resource_id || "")}</td>
          <td class="${event.outcome === "success" ? "success" : "failure"}">${escapeHtml(event.outcome || "")}</td>
          <td>${escapeHtml(event.correlation_id || "")}</td>
          <td><code>${escapeHtml(JSON.stringify(event.details || {}, null, 2))}</code></td>
        </tr>
      `).join("");
      events.innerHTML = `
        <table>
          <thead>
            <tr>
              <th>Time</th><th>Actor</th><th>Resource</th><th>Outcome</th><th>Correlation</th><th>Details</th>
            </tr>
          </thead>
          <tbody>${rows}</tbody>
        </table>
      `;
    }

    filters.addEventListener("submit", (event) => {
      event.preventDefault();
      load();
    });
    load();
  </script>
</body>
</html>
"""


def create_handler(audit_log_path: str | None = None) -> type[BaseHTTPRequestHandler]:
    """Create a request handler bound to one audit log path."""

    class AuditLogHandler(BaseHTTPRequestHandler):
        server_version = "HaloSwingAuditWeb/0.1"

        def do_GET(self) -> None:  # noqa: N802
            parsed = urlparse(self.path)
            if parsed.path == "/":
                self._send_text(HTTPStatus.OK, "text/html; charset=utf-8", HTML)
                return
            if parsed.path == "/api/events":
                query = parse_qs(parsed.query)
                try:
                    payload = events_payload(audit_log_path, query)
                except ValueError as exc:
                    self._send_json(HTTPStatus.BAD_REQUEST, {"error": str(exc)})
                    return
                self._send_json(HTTPStatus.OK, payload)
                return
            if parsed.path == "/api/summary":
                self._send_json(HTTPStatus.OK, summary_payload(audit_log_path))
                return
            self._send_json(
                HTTPStatus.NOT_FOUND,
                {"error": "not_found", "path": parsed.path},
            )

        def log_message(self, format: str, *args: Any) -> None:
            return

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

    return AuditLogHandler


def events_payload(
    audit_log_path: str | None,
    query: dict[str, list[str]] | None = None,
) -> dict[str, Any]:
    """Build the JSON payload for the events API."""

    query = query or {}
    normalized_limit = _int_query(query, "limit", 100)
    normalized_action = _str_query(query, "action")
    normalized_resource_type = _str_query(query, "resource_type")
    normalized_resource_id = _str_query(query, "resource_id")
    normalized_outcome = _str_query(query, "outcome")
    return {
        "events": read_audit_events(
            audit_log_path=audit_log_path,
            limit=normalized_limit,
            action=normalized_action,
            resource_type=normalized_resource_type,
            resource_id=normalized_resource_id,
            outcome=normalized_outcome,
        )
    }


def summary_payload(audit_log_path: str | None) -> dict[str, Any]:
    """Build the JSON payload for the summary API."""

    return audit_summary(audit_log_path=audit_log_path)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Serve Halo Swing audit logs over HTTP")
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--audit-log-path", help="Path to the JSONL audit log")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.host not in ALLOWED_HOSTS:
        print("Audit web must bind to localhost only.", file=sys.stderr)
        return 2
    if args.port < 0 or args.port > 65535:
        print("Audit web port must be between 0 and 65535.", file=sys.stderr)
        return 2
    audit_path = str(resolve_audit_log_path(args.audit_log_path))
    handler = create_handler(audit_path)
    server = ThreadingHTTPServer((args.host, args.port), handler)
    host, port = server.server_address
    print(f"Serving Halo Swing audit log at http://{host}:{port}")
    print(f"Audit log: {Path(audit_path)}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        return 0
    finally:
        server.server_close()
    return 0


def _str_query(query: dict[str, list[str]], key: str) -> str | None:
    value = query.get(key, [""])[0]
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError(f"{key} must be a string when provided")
    if not _has_no_control_characters(value):
        raise ValueError(f"{key} must not contain control characters")
    normalized = value.strip()
    return normalized or None


def _int_query(query: dict[str, list[str]], key: str, default: int) -> int:
    raw = query.get(key, [str(default)])[0]
    if raw is None:
        return default
    if not isinstance(raw, str):
        raise ValueError(f"{key} must be a positive integer")
    if not _has_no_control_characters(raw):
        raise ValueError(f"{key} must not contain control characters")
    normalized = raw.strip()
    if not normalized:
        return default
    try:
        value = int(normalized)
    except ValueError:
        raise ValueError(f"{key} must be a positive integer") from None
    if value <= 0:
        raise ValueError(f"{key} must be a positive integer")
    return min(value, 1000)


def _has_no_control_characters(value: str) -> bool:
    return all(ord(character) >= 32 and ord(character) != 127 for character in value)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
