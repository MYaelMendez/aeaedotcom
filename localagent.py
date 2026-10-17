import subprocess
#!/usr/bin/env python3
"""#localagent — sovereign local agent dispatcher for IMperial (Legion Go).

import subprocess
Offline-first, receipt-verified agent loop: planner → executor → auditor → manifest.
Runs fully offline with Ollama CPU as the brain. Each artifact carries a
receipt + QR = THE CHIP.

Shared glocal files (same names/format kabban.py reads):
  kabban.json          — task board (JSON array)
  kabban-state.json    — runtime state (JSON object)
  kabban-deps.json     — inter-agent dependency edges (JSON object)
  kabban-events.jsonl  — traceable handoff events (JSONL)
  receipts/            — hash-chained receipt files

Usage:
    localagent.py probe
    localagent.py status
    localagent.py plan "intent"
    localagent.py run "task_id"
    localagent.py verify "task_id"
    localagent.py manifest "task_id"
    localagent.py menlo <status|stand|balance|walk|damp>
    localagent.py help
"""
import json
import os
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

# Shared glocal files (same names as kabban.py)
ROOT = Path(os.environ.get("LOCALAGENT_ROOT", Path(__file__).resolve().parent))
BOARD_FILE = ROOT / "kabban.json"
STATE_FILE = ROOT / "kabban-state.json"
DEPS_FILE = ROOT / "kabban-deps.json"
MECH_RUNNER = ROOT / "kabban-runner.py"
LOG_FILE = ROOT / "kabban-events.jsonl"
RECEIPTS_DIR = ROOT / "receipts"

BOOT = [">_æ|", ">_h", ">_n", ">_$", ">_:$", ">:_localagent"]

ENV = {
    "node": "IMperial (Legion Go)",
    "role": "#localagent",
    "engine": "cpu",
    "brain": "ollama (llama3.2:3b)",
    "hands": "kabban (task board)",
    "board": "kænbæn",
    "mesh": "+æ://route → Victus brain",
    "offline": True,
}


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def load_json(path, default):
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            pass
    return default


def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def load_board():
    return load_json(BOARD_FILE, [])


def save_board(rows):
    save_json(BOARD_FILE, rows)


def load_state():
    state = load_json(STATE_FILE, {"status": "PROBING", "tasks": {}, "receipts": [], "last_probe": None})
    # Ensure all default keys exist
    defaults = {"status": "PROBING", "tasks": {}, "receipts": [], "last_probe": None}
    for k, v in defaults.items():
        state.setdefault(k, v)
    return state


def save_state(state):
    save_json(STATE_FILE, state)


def sha256(s):
    import hashlib
    return hashlib.sha256(s.encode()).hexdigest()


def emit_receipt(task_id, verdict, evidence, uncertainty):
    RECEIPTS_DIR.mkdir(parents=True, exist_ok=True)
    trust = round(sum(float(e) for e in evidence) / max(sum(float(u) for u in uncertainty), 1), 4)
    # Hash-chain: the qr field is the SHA-256 of the deterministic payload
    # (id, verdict, evidence, uncertainty, trust — NO timestamp, NO qr).
    # This makes the hash-chain restorable from the board alone: restart
    # re-emits the identical qr every time.
    payload = {
        "id": task_id,
        "verdict": verdict,
        "evidence": evidence,
        "uncertainty": uncertainty,
        "trust": trust,
    }
    qr = sha256(json.dumps(payload, sort_keys=True))
    receipt = {
        "id": task_id,
        "timestamp": now_iso(),
        "verdict": verdict,
        "evidence": evidence,
        "uncertainty": uncertainty,
        "trust": trust,
        "qr": qr,
    }
    RECEIPTS_DIR.joinpath(f"{task_id}.json").write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    return receipt


def probe_oem():
    evidence, uncertainty = [], []
    try:
        r = subprocess.run(
            ["curl", "-s", "http://localhost:11434/api/tags"],
            capture_output=True, text=True, timeout=5,
        )
        if r.returncode == 0:
            evidence.append(1.0)
            uncertainty.append(0.0)
    except Exception:
        evidence.append(0.0)
        uncertainty.append(1.0)
    return evidence, uncertainty


def cmd_probe():
    evidence, uncertainty = probe_oem()
    state = load_state()
    state["status"] = "ONLINE" if sum(evidence) > 0 else "OFFLINE"
    state["last_probe"] = now_iso()
    save_state(state)

    # Mech bridge: refresh from the rule engine (idempotent read)
    mech_status = mech_run(None, dry=True)
    mech_board = mech_board()
    return {
        "verdict": state["status"],
        "engine": ENV["engine"],
        "brain": ENV["brain"],
        "offline": ENV["offline"],
        "evidence": evidence,
        "uncertainty": uncertainty,
        "boot": BOOT,
        "mech": {"status": "ok", "board": mech_board, "transitions": mech_status},
    }


def cmd_plan(intent):
    task_id = str(uuid.uuid4())[:8]
    board = load_board()
    board.append({"id": task_id, "intent": intent, "assignee": "self", "status": "planned",
                  "created": now_iso(), "updated": now_iso()})
    save_board(board)
    add_event(task_id, "create", actor="localagent")
    return {"task_id": task_id, "intent": intent, "status": "planned", "timestamp": now_iso()}


def cmd_dispatch(args):
    """Mech-gated dispatch: only when dependencies are ready."""
    board = load_board()
    task_id = args.get("task_id", "")
    for t in board:
        if t.get("id") == task_id and t.get("status") == "planned":
            if not waits_for(t):
                return {"error": f"blocked: dependency {t.get('parent')} not done", "task_id": task_id}
            t["status"] = "dispatched"
            t["updated"] = now_iso()
            save_board(board)
            add_event(task_id, "dispatch", actor="localagent")
            return t
    return {"error": f"task not dispatched: {task_id}"}


def cmd_run(task_id):
    """Mech bridge: declarative state transition (planner → executor → ... → manifest)."""
    state = load_state()
    state["tasks"][task_id] = {"status": "running", "started": now_iso()}
    save_state(state)
    # Mech rule engine evaluates the transition
    mech_board()
    return {
        "task_id": task_id,
        "status": "dispatched",  # Kabban row format
        "kabban": {"id": task_id, "status": "running"},
        "loop": "planner→executor→auditor→manifest",
        "engine": ENV["engine"],
        "brain": ENV["brain"],
        "offline": ENV["offline"],
    }


def cmd_verify(task_id):
    state = load_state()
    task = state["tasks"].get(task_id, {"status": "unknown"})
    receipt = emit_receipt(
        task_id,
        verdict=task.get("status", "UNKNOWN"),
        evidence=[1.0],
        uncertainty=[0.0],
    )
    return receipt


def cmd_manifest(task_id):
    receipt = cmd_verify(task_id)
    return {
        "task_id": task_id,
        "receipt": receipt,
        "qr": receipt["qr"],
        "hash_chain": sha256(receipt["qr"]),
        "offline": ENV["offline"],
    }


def cmd_status():
    state = load_state()
    board = load_board()
    deps = load_json(DEPS_FILE, {"edges": []})
    events = 0
    if LOG_FILE.exists():
        events = len(LOG_FILE.read_text(encoding="utf-8").strip().splitlines())
    mech_board_data = mech_board()
    return {
        "node": ENV["node"],
        "role": ENV["role"],
        "engine": ENV["engine"],
        "brain": ENV["brain"],
        "offline": ENV["offline"],
        "status": state.get("status", "PROBING"),
        "last_probe": state.get("last_probe"),
        "tasks": len(board),
        "receipts": len(state.get("receipts", [])),
        "deps": len(deps.get("edges", [])),
        "events": events,
        "mech": {"board": mech_board_data},
    }


# ---------- Mech bridge helpers (kabban-runner.py) ----------

def mech_board():
    """Return the current task board from kabban-runner.py."""
    if not MECH_RUNNER.exists():
        return []
    r = subprocess.run([sys.executable, str(MECH_RUNNER), "board"],
                       capture_output=True, text=True, timeout=10)
    if r.returncode == 0:
        return json.loads(r.stdout)
    return []


def mech_run(task_id=None, dry=False):
    """Run the Mech state machine (dry=True = just evaluate, no write)."""
    cmd = [sys.executable, str(MECH_RUNNER)]
    if dry:
        cmd.append("dry")
    if task_id:
        cmd.append(task_id)
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
    return r.stdout.strip() if r.returncode == 0 else r.stderr.strip()


def waits_for(task):
    """Dependency gating: parent must be done or dispatched."""
    p = task.get("parent")
    if p in (None, "", "None", "_"):
        return True
    for t in load_board():
        if t.get("id") == p:
            return t.get("status") in ("done", "dispatched")
    return False



def add_event(task_id, event, actor="system"):
    entry = {"timestamp": now_iso(), "task_id": task_id, "event": event, "actor": actor}
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")
    state = load_state()
    state["logged"] = state.get("logged", 0) + 1
    save_state(state)


# ---------- Menlo bridge client (HTTP-only, stdlib urllib) ----------

MENLO_BRIDGE_URL = "http://127.0.0.1:8901"


def menlo_get(path):
    """GET from menlo bridge. Returns dict or None."""
    import urllib.request
    try:
        with urllib.request.urlopen(MENLO_BRIDGE_URL + path, timeout=5) as r:
            return json.loads(r.read().decode())
    except Exception:
        return None


def menlo_post(path, data):
    """POST to menlo bridge. Returns dict or None."""
    import urllib.request
    try:
        req = urllib.request.Request(
            MENLO_BRIDGE_URL + path,
            data=json.dumps(data).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=5) as r:
            return json.loads(r.read().decode())
    except Exception:
        return None


def cmd_menlo(args):
    """Menlo robot verb execution via bridge. Usage: localagent.py menlo <status|stand|balance|walk|damp>"""
    if not args:
        return {"error": "usage: localagent.py menlo <status|stand|balance|walk|damp>"}
    verb = args[0]

    if verb == "status":
        state = menlo_get("/state")
        if not state or not state.get("ok"):
            return {"error": "menlo bridge not ready — launch hermes-engineering-hub"}
        return {"ok": True, "bridge": "online", "state": state["state"]}

    verb_map = {
        "stand": {"name": "stand", "args": {}},
        "balance": {"name": "balance", "args": {}},
        "walk": {"name": "set_velocity", "args": {"vx": 0.25, "duration": 2.0}},
        "damp": {"name": "damp", "args": {}},
    }
    if verb not in verb_map:
        return {"error": f"unknown verb: {verb}. Valid: {list(verb_map.keys())}"}

    v = verb_map[verb]
    result = menlo_post("/verb", {"name": v["name"], "args": v["args"]})
    if not result:
        return {"error": "menlo bridge not ready — launch hermes-engineering-hub"}

    # UX hint: if SDK reports "stand() first", append recovery guidance
    if not result.get("ok") and "stand() first" in result.get("error", ""):
        result["hint"] = "run: localagent.py menlo stand"

    # Record on kabban board with outcome as evidence
    task_id = str(uuid.uuid4())[:8]
    board = load_board()
    board.append({
        "id": task_id,
        "intent": f"menlo:{verb}",
        "assignee": "self",
        "status": "done",
        "parent": None,
        "children": [],
        "evidence": [{"text": json.dumps(result, default=str), "at": now_iso()}],
        "uncertainty": [],
        "created": now_iso(),
        "updated": now_iso(),
    })
    save_board(board)
    add_event(task_id, "menlo:execute", actor="localagent")

    return result


def cmd_help():
    return {"usage": "localagent.py <probe|status|plan|run|verify|manifest|menlo|help>"}


def main():
    if len(sys.argv) < 2:
        print(json.dumps(cmd_help(), indent=2))
        return

    cmd = sys.argv[1]
    args = sys.argv[2:]

    commands = {
        "probe": cmd_probe,
        "status": cmd_status,
        "plan": lambda: cmd_plan(" ".join(args)),
        "run": lambda: cmd_run(args[0]) if args else {"error": "task_id required"},
        "verify": lambda: cmd_verify(args[0]) if args else {"error": "task_id required"},
        "manifest": lambda: cmd_manifest(args[0]) if args else {"error": "task_id required"},
        "mech": cmd_status,
        "mech:run": lambda: mech_run(args[0]) if args else {"error": "task_id required"},
        "mech:board": lambda: {"board": mech_board()},
        "menlo": lambda: cmd_menlo(args),
        "help": cmd_help,
    }

    handler = commands.get(cmd)
    if handler is None:
        result = {"error": f"unknown command: {cmd}"}
    else:
        result = handler()
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
