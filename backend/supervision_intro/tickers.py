"""æææ.com ticker + collapsible helpers — dynamic design helpers.

These are consumed by the redesigned index.html below.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _first_line(text: str, width: int = 64) -> str:
    s = text.replace("\n", " ").strip()
    if len(s) <= width:
        return s
    return s[: width - 1].rstrip() + "…"


def _bytes_to_human(n: int) -> str:
    if n < 1024:
        return f"{n} B"
    if n < 1024 * 1024:
        return f"{n / 1024:.1f} KB"
    return f"{n / (1024 * 1024):.1f} MB"


@dataclass
class SiteTicker:
    brand_items: list[str] = field(default_factory=list)
    status_lines: list[str] = field(default_factory=list)
    intro_lines: list[str] = field(default_factory=list)

    @classmethod
    def from_backend(cls, parent: Path) -> "SiteTicker":
        from .model import build_machine_state

        buf = []

        def push(*parts: str) -> None:
            line = " · ".join(p for p in parts if p)
            if line:
                buf.append(line)

        # status
        push("sovereign", "python backend", "fastapi/uvicorn")

        # introspection
        state = build_machine_state(parent / "static" / "introspection" / "mcp_context_state.json")
        d = state.to_dict()["surfaces"]["digital"]
        if d.get("status") == "active":
            push("introspection active", f"{d.get('context_count', 0)} contexts")
        else:
            push("introspection standby")

        # brands
        try:
            import json as _json
            brands = _json.loads((parent / "static" / "brands.json").read_text(encoding="utf-8"))
            for b in brands.get("items", [])[:6]:
                push(b.get("label", b.get("key", ""))[:28])
        except Exception:
            pass

        return cls(
            status_lines=buf,
            brand_items=[],
            intro_lines=[],
        )


def render_ticker_html(ticker: SiteTicker) -> str:
    items = ticker.status_lines or ["sovereign runtime"]
    repeat = items * 2
    return "".join(
        f'<span class="ticker-item"><span class="dot"></span><span class="label">{label}</span><span class="value">{value}</span></span>'
        for label, value in _split_ticker(repeat)
    )


def _split_ticker(lines: list[str]) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    for line in lines:
        if " · " in line:
            a, b = line.split(" · ", 1)
            out.append((_first_line(a, 18), _first_line(b, 40)))
        else:
            out.append(("", _first_line(line, 48)))
    return out
