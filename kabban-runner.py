#!/usr/bin/env python3
"""
kabban-runner.py — evaluates Kabban state transitions declaratively.

Reads kabban.json + kabban-deps.json, applies the Mech state machine
(advance, advance_gated), writes updated board back to kabban.json,
and appends traceable handoff events to kabban-events.jsonl.

This is the "tool" that executes the Mech bridge program.
"""
import json, sys, hashlib, os
from datetime import datetime, timezone

BASE = os.path.dirname(os.path.abspath(__file__))
BOARD = os.path.join(BASE, "kabban.json")
DEPS  = os.path.join(BASE, "kabban-deps.json")
EVENTS = os.path.join(BASE, "kabban-events.jsonl")

def now_iso():
    return datetime.now(timezone.utc).isoformat()

def sha256(s):
    return hashlib.sha256(s.encode()).hexdigest()

def canonical(*parts):
    return "|".join(str(p) for p in parts if p is not None)

# ---------- load ----------
with open(BOARD) as f:
    board = json.load(f)
with open(DEPS) as f:
    deps = json.load(f)
edges = {e["child"]: e["parent"] for e in deps["edges"]}

# tree
for t in board:
    t.setdefault("children", [])
    t.setdefault("parent", None)

# ---------- helpers ----------
def parent_of(id_):
    for t in board:
        if t["id"] == id_:
            return t.get("parent")
    return None

def parent_status(id_):
    p = parent_of(id_)
    if p is None:
        return None
    return next((t["status"] for t in board if t["id"] == p), None)

def ready(task):
    if task["parent"] in (None, ""):
        return True
    return parent_status(task["id"]) == "done"

def advance(task):
    st = task["status"]
    if st == "blocked":
        return {"id": task["id"], "intent": task["intent"], "assignee": task["assignee"],
                "status": "dormant", "parent": task.get("parent"), "children": task.get("children", []),
                "evidence": task.get("evidence", []), "uncertainty": task.get("uncertainty", []),
                "created": task.get("created"), "updated": now_iso(), "dormant_since": now_iso()}
    if st == "done":
        return task
    if st == "blocked" and not ready(task):
        # evidence cleared via QR restart — unblock
        return {"id": task["id"], "intent": task["intent"], "assignee": task["assignee"],
                "status": "done", "parent": task.get("parent"), "children": task.get("children", []),
                "evidence": task.get("evidence", []) + ["unblocked via QR kænbæn restart"],
                "uncertainty": task.get("uncertainty", []), "created": task.get("created"),
                "updated": now_iso()}
    if st == "todo":
        return {"id": task["id"], "intent": task["intent"], "assignee": task["assignee"],
                "status": "dispatched", "parent": task.get("parent"), "children": task.get("children", []),
                "evidence": task.get("evidence", []), "uncertainty": task.get("uncertainty", []),
                "created": task.get("created"), "updated": now_iso()}
    if st == "dispatched":
        return {"id": task["id"], "intent": task["intent"], "assignee": task["assignee"],
                "status": "running", "parent": task.get("parent"), "children": task.get("children", []),
                "evidence": task.get("evidence", []), "uncertainty": task.get("uncertainty", []),
                "created": task.get("created"), "updated": now_iso()}
    if st == "running":
        return {"id": task["id"], "intent": task["intent"], "assignee": task["assignee"],
                "status": "done", "parent": task.get("parent"), "children": task.get("children", []),
                "evidence": task.get("evidence", []) + ["finished by localagent.py evaluation"],
                "uncertainty": task.get("uncertainty", []), "created": task.get("created"),
                "updated": now_iso()}
    return task

def advance_gated(task):
    if ready(task):
        return advance(task)
    return task

def emit_event(task_id, event_name, actor):
    with open(EVENTS, "a") as f:
        f.write(json.dumps({"timestamp": now_iso(), "task_id": task_id,
                            "event": event_name, "actor": actor}) + "\n")

# ---------- rule engine ----------
def evaluate(uid=None):
    changed = []
    for t in board:
        if uid and t["id"] != uid:
            continue
        new = advance_gated(t)
        if new != t:
            changed.append((t, new))
    for old, new in changed:
        idx = board.index(old)
        board[idx] = new
        if new["status"] == "done":
            emit_event(new["id"], "done", "kabban")
        elif new["status"] == "dormant":
            emit_event(new["id"], "blocked", "kabban")
        elif new["status"] == "dispatched":
            emit_event(new["id"], "dispatch", "kabban")
        elif new["status"] == "running":
            emit_event(new["id"], "start", "kabban")
    return [f"{o['id']}->{n['status']}" for o, n in changed]

# ---------- main ----------
if __name__ == "__main__":
    uid = sys.argv[1] if len(sys.argv) > 1 else None
    results = evaluate(uid)
    with open(BOARD, "w") as f:
        json.dump(board, f, indent=2)
    if results:
        print("RERUN:", " ".join(results))
    else:
        print("RERUN: done — no transitions")
    print(f"board: {len(board)} tasks, {len([r for r in results])} changed")
