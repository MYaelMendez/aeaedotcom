"""html_gen — HTML/CSS pacelets + local fallback renderer.

Probe-verified: local HTML fallback renders when API is down.
All pacelets are single-file, self-contained HTML/CSS written to
custom_apps/html/ for the hermes desktop window (preview.html).

Usage:
    import pyglocal.html_gen as h
    h.pacelet(data)      # write a pacelet
    h.render()           # render local HTML fallback when API down
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

BASE = Path(__file__).resolve().parent.parent
HTML_DIR = BASE / "custom_apps" / "html"
HTML_DIR.mkdir(parents=True, exist_ok=True)

GOLD = "#f5c842"
VOID = "#020617"
INK = "#e5e7eb"
MUTED = "#9ca3af"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def pacelet(title: str, body: str, id: str = None) -> Path:
    """Write a self-contained HTML/CSS pacelet to custom_apps/html/."""
    id = id or "pacelet-" + now_iso().replace(":", "-").replace(".", "-")[:10]
    html = """<!DOCTYPE html>
<html lang="en">
<head><meta charset="utf-8"><title>{title}</title>
<style>
  :root {{ --gold: {gold}; --void: {void}; --ink: {ink}; --muted: {muted}; }}
  * {{ box-sizing: border-box; margin:0; padding:0; }}
  body {{ background: var(--void); color: var(--ink); font-family: ui-monospace, monospace; height:100vh; overflow:hidden; }}
  header {{ padding: 12px 16px; border-bottom: 1px solid rgba(245,200,66,.15); display: flex; justify-content: space-between; }}
  h1 {{ font-size: 13px; letter-spacing: .1em; color: var(--gold); }}
  .meta {{ font-size: 10px; color: var(--muted); }}
  main {{ padding: 16px; overflow:auto; }}
  .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 12px; }}
  .card {{ background: rgba(245,200,66,.04); border: 1px solid rgba(245,200,66,.15); border-radius: 10px; padding: 12px; }}
  .card h3 {{ color: var(--gold); font-size: 11px; letter-spacing: .06em; }}
  pre {{ background: rgba(2,6,23,.8); border: 1px solid rgba(245,200,66,.12); border-radius: 6px; padding: 10px; font-size: 10px; color: var(--ink); overflow:auto; white-space: pre-wrap; }}
  footer {{ padding: 8px 16px; border-top: 1px solid rgba(245,200,66,.1); font-size: 10px; color: var(--muted); }}
</style></head>
<body>
<header><h1>{title}</h1><span class="meta">{ts}</span></header>
<main>
  <div class="grid">
    {body}
  </div>
</main>
<footer>
  <span>probe · dispatch · run → done · QR = THE_CHIP</span>
  <span>rendered local (offline-first)</span>
</footer>
</body>
</html>"""
    html = html.format(
        title=title, ts=now_iso(), gold=GOLD, void=VOID, ink=INK, muted=MUTED, body=body
    )
    p = HTML_DIR / (id + ".html")
    p.write_text(html, encoding="utf-8")
    return p


def render(data: dict[str, Any] = None) -> dict[str, Any]:
    """Render local HTML fallback when API is down (payload JSON)."""
    data = data or {}
    rows = json.dumps(data, indent=2, ensure_ascii=False)
    body = "<pre>{}</pre>".format(rows)
    p = pacelet("local fallback", body)
    return {"success": True, "path": str(p), "rendered": True}


def fleetpacelet(nodes: list[dict[str, Any]]) -> Path:
    """Write the fleet pacelet (all-in-one QR)."""
    rows = json.dumps({"nodes": nodes}, indent=2, ensure_ascii=False)
    body = "<pre>{}</pre>".format(rows)
    return pacelet("FleetWave · all-in-one QR", body, "fleetwave-pacelet")


def kabbanpacelet(tasks: list[dict[str, Any]]) -> Path:
    """Write the kænbæn enterprise board pacelet."""
    rows = json.dumps({"tasks": tasks, "assignees": ["imperial", "vice", "reviewer"]}, indent=2, ensure_ascii=False)
    body = "<pre>{}</pre>".format(rows)
    return pacelet("kænbæn · enterprise task board", body, "kabban-pacelet")


def mp4pacelet(path: str) -> Path:
    """Write the MP4 pacelet link page."""
    return pacelet("local_agent.mp4", "<pre>{" + "file: " + path + "}</pre>", "mp4-pacelet")
