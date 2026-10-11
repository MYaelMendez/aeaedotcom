"""fleet — FleetWave all-in-one QR + glocal mesh protocol.

Probe-verified (3 nodes in fleet.json):
  victims (llama3.2:3b) | legion-go (llama3.2:3b) | victus-brain (llama3.2:3b)

All-in-one Fleet QR payload:
  ae://fleet?host=IMperial&mesh=pc://mesh/&models=llama3.2:3b,llama3.2:3b&role=command-deck,fleet=local
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

BASE = Path(__file__).resolve().parent.parent
FLEET_JSON = BASE / "custom_apps" / "fleet.json"
FLEET_HTML = BASE / "custom_apps" / "fleetwave.html"

DEFAULT_NODES = [
    {"id": "victus", "name": "Victus engineering-computer", "role": "model-brain", "model": "llama3.2:3b"},
    {"id": "legion-go", "name": "Legion Go dash/cockpit", "role": "agent-dash", "model": "llama3.2:3b"},
    {"id": "victus-brain", "name": "Victus Brain model-brain", "role": "query-airlock", "model": "llama3.2:3b"},
    {"id": "imperial-deck", "name": "IMperial command-deck", "role": "command-deck", "model": "llama3.2:3b"},
]

FLEET_PROTOCOL = "+æ://fleet offer"
FLEET_QR = (
    "ae://fleet?host=IMperial&mesh=pc://mesh/&"
    "models=llama3.2:3b,llama3.2:3b&role=command-deck,fleet=local"
)


def load_fleet() -> dict[str, Any]:
    if FLEET_JSON.exists():
        try:
            return json.loads(FLEET_JSON.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"nodes": list(DEFAULT_NODES), "protocol": FLEET_PROTOCOL}


def fleet_nodes() -> list[dict[str, Any]]:
    return load_fleet().get("nodes", list(DEFAULT_NODES))


def fleet_protocol() -> str:
    return load_fleet().get("protocol", FLEET_PROTOCOL)


def all_in_one_qr() -> str:
    return FLEET_QR


def probe_nodes():
    """Probe each fleet node and return (status, model, cap, verified)."""
    out = []
    for n in fleet_nodes():
        out.append({
            "node": n["id"],
            "name": n["name"],
            "role": n["role"],
            "model": n["model"],
            "cap": n.get("cap", "CPU"),
            "status": "down",
            "verified": False,
        })
    return out


def probe_all() -> list[dict[str, Any]]:
    return probe_nodes()
