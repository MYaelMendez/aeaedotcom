"""kænbæn — Knowledge Breadbasket: sovereign local agent task board + CLI.

Offline-first, traceable handoff + dispatch system for the #localagent
planner→executor→auditor→manifest loop. Runs fully offline with
local-first storage (kabban.json + kabban-state.json).

Enterprise demo requirements (probe-verified):
  - >=4 tasks across >=3 assignees (imperial, vice, reviewer)
  - inter-agent dependency graph with gating
  - dispatch cap of 1
  - blocked -> dormant -> reroute
  - traceable handoff events (run->done, run->blocked, block->unblock, task->package)
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

APP = Path(__file__).resolve().parent.parent
STATE_FILE = APP / "kabban-state.json"
BOARD_FILE = APP / "kabban.json"
DEPS_FILE = APP / "kabban-deps.json"
LOG_FILE = APP / "kabban-events.jsonl"
RECEIPTS_DIR = APP / "receipts"

VALID_ASSIGNEES = {"imperial", "vice", "reviewer", "self"}

SYSTEM = {
    "node": "IMperial (Legion Go)",
    "role": "#localagent",
    "engine": "cpu (Ollama llama3.2:3b)",
    "offline": True,
    "brain": "ollama :11434",
    "board": "kænbæn",
    "mesh": "+æ://route → Victus",
    "qr": "THE_CHIP",
}

DEFAULT_STATE = {
    "status": "PROBING",
    "last_probe": None,
    "last_run": None,
    "dormant_cutoff_hours": 24,
    "logged": 0,
    "task_counter": 0,
}


def now_iso() -> str:
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


def load_state():
    return load_json(STATE_FILE, DEFAULT_STATE)


def save_state(state):
    save_json(STATE_FILE, state)


def load_board():
    return load_json(BOARD_FILE, [])


def save_board(rows):
    save_json(BOARD_FILE, rows)


def new_task(intent, assignee="self"):
    if assignee not in VALID_ASSIGNEES:
        raise ValueError("assignee must be one of " + str(VALID_ASSIGNEES))
    state = load_state()
    n = int(state.get("task_counter", 0)) + 1
    state["task_counter"] = n
    save_state(state)
    task_id = "k{:03d}".format(n)
    task = {
        "id": task_id,
        "intent": intent,
        "assignee": assignee,
        "status": "todo",
        "parent": None,
        "children": [],
        "evidence": [],
        "uncertainty": [],
        "created": now_iso(),
        "updated": now_iso(),
        "dormant_since": None,
        "qr_hash": None,
    }
    board = load_board()
    board.append(task)
    save_board(board)
    return task


def add_event(task_id, event, actor="system"):
    entry = {"timestamp": now_iso(), "task_id": task_id, "event": event, "actor": actor}
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")
    STATE = load_state()
    STATE["logged"] = STATE.get("logged", 0) + 1
    save_state(STATE)


def dep_add(child, parent):
    deps = load_json(DEPS_FILE, {})
    if child not in deps:
        deps[child] = []
    deps[child].append(parent)
    save_json(DEPS_FILE, deps)
    return True


def dep_remove(child, parent):
    deps = load_json(DEPS_FILE, {})
    if child in deps and parent in deps[child]:
        deps[child].remove(parent)
    save_json(DEPS_FILE, deps)
    return True


def deps_list():
    deps = load_json(DEPS_FILE, {})
    out = []
    for child, parents in deps.items():
        for p in parents:
            out.append({"child": child, "parent": p})
    return out


def is_blocked(task):
    if task["status"] in ("blocked", "dormant"):
        return True
    deps = load_json(DEPS_FILE, {})
    parents = deps.get(task["id"], [])
    for p in parents:
        parent = next((t for t in load_board() if t["id"] == p), None)
        if parent and parent["status"] in ("blocked", "dormant"):
            return True
    return False


def priority_order(tids):
    deps = load_json(DEPS_FILE, {})
    by_id = {}
    for t in load_board():
        by_id[t["id"]] = t
    for tid in tids:
        if tid not in by_id:
            by_id[tid] = {"id": tid, "status": "todo"}
    if not tids:
        return tids

    def dag_key(tid):
        parents = deps.get(tid, [])
        if not parents:
            return 0
        return max(dag_key(p) for p in parents if p in by_id) + 1

    return sorted(tids, key=dag_key)


def dispatch(max_tasks=1):
    board = load_board()
    ready = []
    for t in board:
        if t["status"] == "todo" and not is_blocked(t):
            t["status"] = "dispatched"
            ready.append(t)
    if len(ready) > max_tasks:
        ready = ready[:max_tasks]
    for t in ready:
        add_event(t["id"], "run", "dispatch")
    save_board(board)
    return ready


def start(tid):
    board = load_board()
    t = next((x for x in board if x["id"] == tid), None)
    if not t:
        return None
    if t["status"] != "dispatched":
        return t
    t["status"] = "running"
    t["started"] = now_iso()
    add_event(t["id"], "run", "start")
    save_board(board)
    return t


def done(tid, evidence=""):
    board = load_board()
    t = next((x for x in board if x["id"] == tid), None)
    if not t:
        return None
    if t["status"] != "running":
        return t
    t["status"] = "done"
    t["evidence"] = (t["evidence"] + [evidence]) if evidence else t["evidence"]
    t["finished"] = now_iso()
    from pyglocal.crypto import append_receipt, receipt_fields
    append_receipt(RECEIPTS_DIR / ("{}.json".format(tid)), receipt_fields(tid, "done", t["evidence"]))
    add_event(t["id"], "run->done", "done")
    save_board(board)
    return t


def block(tid, reason=""):
    board = load_board()
    t = next((x for x in board if x["id"] == tid), None)
    if not t:
        return None
    if t["status"] == "blocked":
        return t
    t["status"] = "blocked"
    t["blocked_reason"] = reason
    t["blocked_at"] = now_iso()
    add_event(t["id"], "run->blocked", "block")
    save_board(board)
    return t


def unblock(tid):
    board = load_board()
    t = next((x for x in board if x["id"] == tid), None)
    if not t:
        return None
    if t["status"] != "blocked":
        return t
    t["status"] = "todo"
    t["blocked_reason"] = None
    t["blocked_at"] = None
    add_event(t["id"], "block->unblock", "unblock")
    save_board(board)
    return t


def dormant(tid):
    board = load_board()
    t = next((x for x in board if x["id"] == tid), None)
    if not t:
        return None
    if t["status"] in ("running", "done"):
        return t
    t["status"] = "dormant"
    t["dormant_since"] = now_iso()
    add_event(t["id"], "run->dormant", "dormant")
    save_board(board)
    return t


def reroute(tid, new_assignee="self"):
    board = load_board()
    t = next((x for x in board if x["id"] == tid), None)
    if not t:
        return None
    if t["status"] not in ("dormant", "blocked"):
        return t
    t["assignee"] = new_assignee
    t["reroute"] = {"from": t["assignee"], "to": new_assignee, "at": now_iso()}
    add_event(t["id"], "dormant->reroute", "reroute")
    save_board(board)
    return t


def show(tid):
    board = load_board()
    return next((x for x in board if x["id"] == tid), None)


def list_tasks():
    return load_board()


def stats(compact=False):
    board = load_board()
    return {
        "total": len(board),
        "todo": sum(1 for t in board if t["status"] == "todo"),
        "dispatched": sum(1 for t in board if t["status"] == "dispatched"),
        "running": sum(1 for t in board if t["status"] == "running"),
        "done": sum(1 for t in board if t["status"] == "done"),
        "blocked": sum(1 for t in board if t["status"] == "blocked"),
        "dormant": sum(1 for t in board if t["status"] == "dormant"),
        "assignees": sorted({t["assignee"] for t in board if t["assignee"] in VALID_ASSIGNEES}),
        "events": load_json(LOG_FILE, []),
    }
