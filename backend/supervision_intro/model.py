"""æææ.com shared machine-state model — asymptotic iteration 1."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import json


@dataclass
class Snapshot:
    timestamp: float
    resolution: dict[str, int]
    active_contexts: list[dict[str, Any]] = field(default_factory=list)
    source: str = ""
    method: str = ""
    metrics: dict[str, Any] = field(default_factory=dict)


@dataclass
class MachineState:
    origin: str = "æææ.com"
    sovereign_mode: str = "local-sovereign"
    timestamp: float = 0.0
    digital: dict[str, Any] | None = None
    physical: dict[str, Any] | None = None
    compute: dict[str, Any] | None = None
    agent_surface: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "origin": self.origin,
            "sovereign_mode": self.sovereign_mode,
            "timestamp": self.timestamp,
            "surfaces": {
                "digital": self.digital or {"status": "no-data"},
                "physical": self.physical or {"status": "not-wired"},
                "compute": self.compute or {"status": "not-wired"},
            },
            "agent_surface": self.agent_surface,
        }


def load_snapshot(path: Path) -> Snapshot | None:
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    return Snapshot(
        timestamp=data.get("timestamp", 0.0),
        resolution=data.get("resolution", {}),
        active_contexts=data.get("active_contexts", []),
        source=data.get("source", str(path)),
        method=data.get("method", ""),
        metrics=data.get("metrics", {}),
    )


def build_machine_state(
    snapshot_path: Path,
    compute: dict[str, Any] | None = None,
    physical: dict[str, Any] | None = None,
) -> MachineState:
    snap = load_snapshot(snapshot_path)
    ts = snap.timestamp if snap else datetime.now(timezone.utc).timestamp()
    state = MachineState(timestamp=ts)
    if snap:
        state.digital = {
            "status": "active",
            "source": snap.source,
            "method": snap.method,
            "resolution": snap.resolution,
            "last_scan": datetime.fromtimestamp(ts, tz=timezone.utc).isoformat(),
            "contexts": snap.active_contexts,
            "context_count": len(snap.active_contexts),
        }
    if compute:
        state.compute = compute
    if physical:
        state.physical = physical
    return state
