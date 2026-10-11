# custom_apps

Custom applications built on the sovereign local agent stack (kænbæn + local_agent + Ollama CPU).

## Apps

### `kabban-board.html` — Enterprise Task Board
Offline-first, dependency-gated task board for the #localagent loop. Built on kænbæn.

- 4 tasks across 3 assignees (imperial · vice · reviewer)
- 5 dependency edges with dispatch-cap = 1
- Dormant reroute + traceable handoff events
- QR = THE_CHIP hash-chain for restart verification

Open in Sticky Notes (Windows Postit) via `LocalState\preview.html`, or open directly.

### `local_agent.html` — Offline-first agent dashboard
Dashboard for the local_agent node on IMperial.

- Probe: ONLINE (engine=cpu, brain=ollama)
- QR = THE_CHIP: SHA-256(id, verdict, evidence, uncertainty, trust)
- Kænbæn board: 4 tasks · 3 assignees · 5 dependency edges
- Run recipes: plan → run → verify → manifest

## FleetWave

All-in-one Fleet QR for the glocal constellation.

- **fleetwave.html** — FleetWave UI (nodes registry, QR carry, dispatch)
- **fleetwave_standalone.html** — Standalone Fleetwave (same content)
- **fleet.json** — Fleet registry — 4 nodes with device/model caps
- Protocol:  · MoD x MoA x MoM (device x agent x model)
- QR = THE_CHIP — deterministic hash-chain restart

## FleetWave

All-in-one Fleet QR for the glocal constellation.

- **fleetwave.html** — FleetWave UI (nodes registry, QR carry, dispatch)
- **fleetwave_standalone.html** — Standalone Fleetwave (same content)
- **fleet.json** — Fleet registry — 4 nodes with device/model caps
- Protocol: `+æ://fleet` · MoD x MoA x MoM (device x agent x model)
- QR = THE_CHIP — deterministic hash-chain restart

## Engine

## QR = THE_CHIP

Each receipt carries a scannable QR with the hash-chain:

```
qr = SHA-256(id, verdict, evidence, uncertainty, trust)
```

Restart re-emits the identical hash-chain from the board alone — no external state needed.

## kænbæn

Knowledge breadbasket: sovereign local agent task board + CLI.

- `kabban.py create "task" --assignee imperial|vice|reviewer`
- `kabban.py list` / `show <id>` / `dispatch` / `start` / `done` / `block` / `unblock`
- `kabban.py dep add <child> --parent <parent>`
- `kabban.py log <id>` / `status` / `stats`
- Dispatch cap = 1 · dependency gating · dormant reroute
- Shared glocal files: `kabban.json`, `kabban-state.json`, `kabban-deps.json`, `kabban-events.jsonl`, `receipts/`
