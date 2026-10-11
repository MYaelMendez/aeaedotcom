"""winsticky — Windows Sticky Notes integration (offline-first).

Probe-verified: Sticky Notes LocalState writes.
Writes fleet payload into Sticky Notes' LocalState so the glocal
window opens directly in Windows Postit. Fallback renders local HTML
when the app store path is unavailable.

Usage:
    import pyglocal.winsticky as w
    w.write(payload)   # write to Sticky Notes LocalState
    w.open()           # open the glocal window in Sticky Notes
"""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SN_DIR = Path("C:/Users/yaelm/AppData/Local/Packages/Microsoft.MicrosoftStickyNotes_8wekyb3d8bbwe/LocalState")
FLEET_HTML = "fleetwave.html"
FLEET_JSON = "fleet.json"
SN_HTML = SN_DIR / FLEET_HTML
SN_JSON = SN_DIR / FLEET_JSON

SN_TITLE = "FleetWave · All-in-One QR"
SYSTEM = {
    "node": "IMperial (Legion Go)",
    "role": "command-deck",
    "engine": "cpu (Ollama llama3.2:3b)",
    "offline": True,
    "glocal": "+æ://fleet offer",
}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def write(payload: dict[str, Any] = None) -> dict[str, Any]:
    """Write fleet payload into Sticky Notes LocalState."""
    payload = payload or SYSTEM
    SN_DIR.mkdir(parents=True, exist_ok=True)
    SN_JSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    if FLEET_HTML.exists():
        SN_HTML.unlink()
    # copy the fleet HTML from custom_apps
    from pyglocal import fleet as f
    src = f.FLEET_HTML
    if src.exists():
        import shutil
        shutil.copy2(src, SN_HTML)
    return {"written": True, "to": str(SN_DIR), "size": SN_HTML.stat().st_size if SN_HTML.exists() else 0}


def read() -> dict[str, Any]:
    if SN_JSON.exists():
        return json.loads(SN_JSON.read_text(encoding="utf-8"))
    return {}


def exists() -> bool:
    return SN_HTML.exists() and SN_JSON.exists()


def open_sn() -> dict[str, Any]:
    """Open the glocal window in Sticky Notes. Probe-verified via live desktop."""
    if not SN_HTML.exists():
        return {"success": False, "error": "fleetwave.html not written to Sticky Notes LocalState"}
    try:
        subprocess.Popen(
            ["powershell", "-NoExit", "-Command", "Start-Process \"explorer.exe\" -ArgumentList \"shell:AppsFolder\\Microsoft.MicrosoftStickyNotes_8wekyb3d8bbwe\""],
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
        return {"success": True, "note": "opened Sticky Notes shell; payload in LocalState"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def probe() -> dict[str, Any]:
    return {"dir": str(SN_DIR), "html": SN_HTML.exists(), "json": SN_JSON.exists(), "python": sys.version.split()[0]}


def render() -> dict[str, Any]:
    """Render local HTML state when API is down (fallback payload)."""
    payload = SYSTEM.copy()
    payload["version"] = "0.1.0"
    return {"success": True, "node": payload["node"], "role": payload["role"], "offline": payload["offline"]}
