---
name: kænbæn
description: Knowledge Breadbasket — sovereign local agent task board CLI. Offline-first multi-node coordination: dispatch cap, dependency gating, dormant reroute, traceable handoff event log, and QR hash-chain receipts. Use when the user wants to track local agent tasks across multiple nodes, coordinate the agent loop planner→executor→auditor→manifest, or drive the kænbæn board from the command line.
author: æææ.com
version: "0.2.0"
metadata:
  hermes:
    tags: [localagent, glocal, kanban, task, agent-loop, imperial, sovereign, dispatch]
---

# kænbæn — Knowledge Breadbasket

A durable, offline-first task board for the sovereign local agent. Promotes the
`localagent` loop (planner→executor→auditor→manifest) into a **multi-node
enterprise coordination layer**: `vice` (Victus GPU brain), `imperial`
(Legion Go CPU), `reviewer` (audit), with dispatch caps, dependency gating,
dormant reroute, and SHA-256 hash-chain receipts.

It is driven by the `kabban.py` CLI over plain JSON files (single source of
truth) — the agent may also drive the human-facing `kanban_*` tools, but the
class-stable surface is the board itself.

## Always-on rules

- **Local is default** — HTML/CSS/Rust/WASM primary; remote APIs optional
- **Offline-first UX** — show ONLINE/OFFLINE/PROBING state; queue writes while offline
- **Action-first, no preamble** — lead with the change
- **QR = THE CHIP** — every done task carries a SHA-256 hash-chained `qr`
  receipt; the board resumes identical work from the JSON alone
- **Evidence ≠ Authority** — receipts verify; the human decides

## The board

```
kabban.json      task board — JSON array, ALL state lives here
kabban-state.json runtime state — status, task_counter, blocked reason
kabban-deps.json  dependency edges (child → parent)
kabban-events.jsonl traceable handoff events, one JSON row each
receipts/{id}.json hash-chained receipt per done task
```

Board row fields: `id`, `intent`, `assignee`, `status`, `parent`, `children`,
`evidence`, `uncertainty`, `created`, `updated`, `dormant_since`, `glocal_tag`.

## Enterprise workflow

1. **Create** — 4–8 tasks across ≥3 assignees (vice/imperial/reviewer)
   `python kabban.py create "intent" --assignee X`
2. **Depend** — wire consumer→producer edges
   `python kabban.py dep add <child> --parent <parent>`
3. **Dispatch** — `dispatch --max N` selects by readiness, longest chain first;
   blocked tasks return `blocked_reason` instead of dispatching
4. **Start / done** — `start <id>` → `done <id> --evidence "..."`
   (writes `start`/`done` handoff events)
5. **Reroute** — cold or blocked task → `block <id> --dormant --reroute`
   (`todo` → `blocked` → `review`, `glocal` tag, Victus handoff)
6. **Audit** — `list` / `show` / `stats` / `deplist` / `log` to verify the chain
7. **QR resume** — `localagent.py verify <id>` / `manifest <id>` re-emits the
   identical `qr` hash chain from the board alone; no in-process state

## Diagnostics

- `dispatch` stops consuming when it hits `--max`: returns
  `{"at_cap": true, "count": N}` and skips blocked tasks
- `deplist` printed by `kabban.py` wraps edges with `child_name`/`parent_name`
  from the board — do not hand-build from the raw edge store
- Dormant cutoff and event counters live in `kabban-state.json` — reading it
  with defaults avoids `KeyError` on a fresh board
