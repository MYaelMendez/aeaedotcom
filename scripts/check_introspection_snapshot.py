"""æææ.com backend coherence gate."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SNAP = ROOT / "static" / "introspection" / "mcp_context_state.json"

errors = []

try:
    data = json.loads(SNAP.read_text(encoding="utf-8"))
except Exception as e:
    errors.append(f"snapshot parse failed: {e}")
    data = None

if data is not None:
    if "timestamp" not in data:
        errors.append("snapshot missing timestamp")
    if "resolution" not in data:
        errors.append("snapshot missing resolution")
    if "active_contexts" not in data:
        errors.append("snapshot missing active_contexts")

print(json.dumps({
    "snapshot": str(SNAP),
    "exists": SNAP.exists(),
    "valid": len(errors) == 0,
    "errors": errors,
    "keys": list(data.keys()) if data else None,
}, indent=2, default=str))

if errors:
    sys.exit(1)
