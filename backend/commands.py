"""æææ.com control commands — local command-and-control surface.

Commands are a fixed vocabulary that the backend recognises and executes
safely. No arbitrary shell execution — each command is an explicit handler.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

@dataclass
class CommandResult:
    ok: bool
    command: str
    outputs: list[str] = field(default_factory=list)
    panel: str | None = None
    meta: dict[str, Any] | None = None
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "ok": self.ok,
            "command": self.command,
            "timestamp": _now_iso(),
        }
        if self.outputs:
            d["output"] = self.outputs
        if self.panel:
            d["panel"] = self.panel
        if self.meta:
            d["meta"] = self.meta
        if self.error:
            d["error"] = self.error
        return d

@dataclass
class CommandRegistry:
    items: list[dict[str, Any]] = field(default_factory=list)

    @classmethod
    def default(cls) -> "CommandRegistry":
        return cls(items=[
            {"cmd": "scan", "label": "scan screen", "group": "control", "gold": True},
            {"cmd": "status", "label": "status", "group": "read", "gold": True},
            {"cmd": "manifest", "label": "manifest", "group": "read", "gold": True},
            {"cmd": "tech", "label": "tech stack", "group": "read", "gold": True},
            {"cmd": "introspect", "label": "introspect", "group": "read", "gold": True},
            {"cmd": "agents", "label": "agents panel", "group": "panel", "gold": True},
            {"cmd": "brands", "label": "brands panel", "group": "panel", "gold": True},
            {"cmd": "root", "label": "root panel", "group": "panel", "gold": True},
            {"cmd": "home", "label": "home panel", "group": "panel", "gold": True},
            {"cmd": "runtime", "label": "runtime panel", "group": "panel"},
            {"cmd": "toggle", "label": "toggle night|club|both", "group": "control"},
            {"cmd": "clear", "label": "clear feed", "group": "control"},
            {"cmd": "help", "label": "help", "group": "meta"},
        ])

    def lookup(self, cmd: str) -> dict[str, Any] | None:
        for item in self.items:
            if item["cmd"] == cmd:
                return item
        return None

def exec_command(cmd: str, arg: str | None, parent: Path) -> CommandResult:
    """Execute a recognised command. Unknown commands return an error result."""
    tokens = (cmd + " " + (arg or "")).strip().lower().split()
    if not tokens:
        return CommandResult(ok=False, command="", error="empty command")
    head = tokens[0]
    rest = " ".join(tokens[1:]) if len(tokens) > 1 else ""

    if head == "scan":
        return _cmd_scan(parent)
    if head == "status":
        return _cmd_status(parent)
    if head == "manifest":
        return _cmd_manifest(parent)
    if head == "tech":
        return _cmd_tech(parent)
    if head == "introspect":
        return _cmd_introspect(parent)
    if head in ("agents", "brands", "root", "home", "runtime"):
        return _cmd_panel(head)
    if head == "toggle":
        return _cmd_toggle(rest)
    if head in ("clear", "_"):
        return _cmd_clear()
    if head in ("help", "?"):
        return _cmd_help()
    return CommandResult(ok=False, command=cmd, error=f"unknown command · {cmd}")

def _cmd_scan(parent: Path) -> CommandResult:
    from .app import _introspection_snapshot
    scanner = parent / "supervision" / "supervision_intro" / "real_digital_introspection.py"
    if not scanner.exists():
        return CommandResult(ok=False, command="scan", error="scanner not found")
    import subprocess, sys
    proc = subprocess.run(
        [sys.executable, str(scanner)],
        cwd=parent,
        capture_output=True,
        text=True,
        timeout=90,
    )
    if proc.returncode != 0:
        return CommandResult(ok=False, command="scan", error="scan failed", outputs=[proc.stderr[-500:]])
    snap = _introspection_snapshot()
    ctx = snap.get("snapshot", {}).get("active_contexts", [])
    return CommandResult(
        ok=True,
        command="scan",
        outputs=[f"scanned · {len(ctx)} contexts · {_now_iso()}"],
        meta={"contexts": len(ctx), "source": snap.get("source")},
    )

def _cmd_status(parent: Path) -> CommandResult:
    from .app import STATUS
    return CommandResult(ok=True, command="status", outputs=[f"{STATUS['site']} · {STATUS['mode']} · {STATUS['status']}"])

def _cmd_manifest(parent: Path) -> CommandResult:
    from .app import ROUTE_MAP, _introspection_snapshot
    snap = _introspection_snapshot()
    lines = [
        f"{parent.name} · local-sovereign",
        "routes:",
    ]
    for path, meta in ROUTE_MAP.items():
        methods = ",".join(meta["methods"])
        lines.append(f"  {methods:8} {path}")
    lines.append(f"introspection: {'live' if snap.get('live') else 'standby'} · {snap.get('source', '—')}")
    return CommandResult(ok=True, command="manifest", outputs=lines)

def _cmd_tech(parent: Path) -> CommandResult:
    from .app import build_machine_state, COMPUTE_STATE, PHYSICAL_STATE
    from .supervision_intro.model import INTRO_SPOT
    state = build_machine_state(INTRO_SPOT, compute=COMPUTE_STATE, physical=PHYSICAL_STATE)
    d = state.to_dict()["surfaces"]
    lines = [
        f"compute: {d['compute'].get('backend', '—')}",
        f"digital: {d['digital'].get('status', '—')} · {d['digital'].get('context_count', 0)} contexts",
        f"physical: {d['physical'].get('status', '—')}",
    ]
    return CommandResult(ok=True, command="tech", outputs=lines)

def _cmd_introspect(parent: Path) -> CommandResult:
    from .app import build_machine_state, COMPUTE_STATE, PHYSICAL_STATE
    from .supervision_intro.model import INTRO_SPOT
    state = build_machine_state(INTRO_SPOT, compute=COMPUTE_STATE, physical=PHYSICAL_STATE)
    d = state.to_dict()["surfaces"]["digital"]
    ctx = d.get("contexts", [])
    lines = [
        f"last_scan: {d.get('last_scan', '—')}",
        f"contexts: {d.get('context_count', 0)}",
    ]
    for c in ctx[:8]:
        lines.append(f"  · {c.get('role', '—')} @ {c.get('surface_id', '—')}")
    if len(ctx) > 8:
        lines.append(f"  … +{len(ctx) - 8} more")
    return CommandResult(ok=True, command="introspect", outputs=lines, meta={"context_count": len(ctx)})

def _cmd_panel(panel: str) -> CommandResult:
    return CommandResult(ok=True, command=panel, panel=f"#{panel}-panel", outputs=[f"opened {panel} panel"])

def _cmd_toggle(arg: str) -> CommandResult:
    return CommandResult(
        ok=True,
        command="toggle",
        outputs=[f"toggle · {arg or 'night|club|both'}"],
        meta={"hint": "handled by frontend"},
    )

def _cmd_clear() -> CommandResult:
    return CommandResult(ok=True, command="clear", outputs=["feed cleared"])

def _cmd_help() -> CommandResult:
    lines = [
        "commands:",
        "  scan        · run introspection scan",
        "  status      · backend status",
        "  manifest    · route manifest",
        "  tech        · machine state",
        "  introspect  · digital contexts",
        "  agents|brands|root|home|runtime · open panel",
        "  toggle night|club|both · theme",
        "  clear       · clear feed",
        "  help        · this help",
    ]
    return CommandResult(ok=True, command="help", outputs=lines)

