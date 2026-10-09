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

## Engine

- Ollama CPU: llama3.2:3b (3.2B Q4_K_M, 2GB, context 131072)
- Local LLM plugin auto-detects Ollama on :11434
- Boots: >_æ| → >_h → >_n → >_$ → >_:$ → >:_localagent

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
