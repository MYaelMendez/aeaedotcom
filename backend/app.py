"""æææ.com backend — agentic coherence main server."""

import json
import os
import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from pathlib import Path

from .supervision_intro.model import build_machine_state
from .supervision_intro.tickers import SiteTicker, render_ticker_html
from .commands import CommandRegistry, exec_command

app = FastAPI(title="æææ.com backend")

BASE = Path(__file__).resolve().parent
PARENT = BASE.parent
INDEX_HTML = (PARENT / "index.html").read_text(encoding="utf-8")
DASHBOARD_HTML = (PARENT / "templates" / "dashboard.html").read_text(encoding="utf-8")

STATUS = {
    "site": "æææ.com",
    "mode": "local-sovereign",
    "status": "online",
    "backend": "python",
}

BRAND_REGISTRY = [
    {"key": "ae", "label": "æ:", "href": "https://æææ.com", "status": "root"},
    {"key": "yael", "label": "yæl", "href": "https://æææ.com", "status": "identity"},
    {"key": "llmstore", "label": "LLM.store", "href": "https://llm.store", "status": "intelligence"},
    {"key": "privateclient", "label": "privateclient.ai", "href": "https://privateclient.ai", "status": "custody"},
    {"key": "molt", "label": "molt.earth", "href": "https://molt.earth", "status": "evolve"},
    {"key": "cli", "label": "cli.llc", "href": "https://cli.llc", "status": "execute"},
    {"key": "dao", "label": "daollc.ai", "href": "https://daollc.ai", "status": "economy"},
    {"key": "teologia", "label": "teologia.ai", "href": "https://teologia.ai", "status": "knowledge"},
    {"key": "zacapa", "label": "zacapa.ai", "href": "https://zacapa.ai", "status": "place"},
    {"key": "enchiridion", "label": "enchiridion", "href": "https://æææ.com/enchiridion", "status": "canon"},
    {"key": "neuromitosis", "label": "neuromitosis", "href": "https://æææ.com/neuromitosis", "status": "distribute"},
    {"key": "commandprompt", "label": "commandprompt", "href": "https://æææ.com/commandprompt", "status": "intent"},
    {"key": "ioa", "label": "ioa", "href": "https://æææ.com/ioa", "status": "network"},
    {"key": "consumerredline", "label": "Consumer Redline Index", "href": "https://æææ.com/consumer-redline-index", "status": "measure"},
]

REGISTRY_BY_KEY = {b["key"]: b for b in BRAND_REGISTRY}
CMD_REGISTRY = CommandRegistry.default()

INTRO_SPOT = PARENT / "static" / "introspection" / "mcp_context_state.json"
DEMO_INTRO = PARENT / "static" / "introspection" / "mcp_context_state.json"

ROUTE_MAP = {
    "/health": {"methods": ["GET"], "purpose": "liveness"},
    "/api/status": {"methods": ["GET"], "purpose": "public status"},
    "/api/brands": {"methods": ["GET"], "purpose": "brand registry index"},
    "/api/brands/{key}": {"methods": ["GET"], "purpose": "single brand"},
    "/api/root": {"methods": ["GET"], "purpose": "root of trust payload"},
    "/api/receipt": {"methods": ["GET"], "purpose": "human-principal receipt"},
    "/api/manifest": {"methods": ["GET"], "purpose": "route manifest for agents"},
    "/api/tech": {"methods": ["GET"], "purpose": "machine/supervision inventory"},
    "/api/tech/introspection": {"methods": ["GET"], "purpose": "digital introspection snapshot"},
    "/api/tech/introspect/scan": {"methods": ["POST"], "purpose": "run a real CV scan now"},
}


def _introspection_snapshot():
    for spot in (INTRO_SPOT, DEMO_INTRO):
        if not spot.exists():
            continue
        try:
            data = json.loads(spot.read_text(encoding="utf-8"))
            return {
                "live": True,
                "source": str(spot.relative_to(PARENT)),
                "snapshot": data,
            }
        except Exception as e:
            return {"live": False, "source": str(spot.relative_to(PARENT)), "detail": str(e)}
    return {"live": False, "detail": "no introspection snapshot on disk"}


@app.get("/health")
def health():
    return JSONResponse(STATUS)


@app.get("/api/status")
def api_status():
    return JSONResponse(STATUS)


@app.get("/api/brands")
def api_brands():
    return JSONResponse({
        "count": len(BRAND_REGISTRY),
        "items": BRAND_REGISTRY,
    })


@app.get("/api/brands/{key}")
def api_brand(key: str):
    brand = REGISTRY_BY_KEY.get(key)
    if not brand:
        return JSONResponse({"detail": "brand not found"}, status_code=404)
    return JSONResponse(brand)


@app.get("/api/root")
def api_root():
    return JSONResponse({
        "origin": "æææ.com",
        "tagline": "Open Intelligence · Private Authority · Sovereign Value",
        "principal": "human",
        "default": "local-sovereign",
        "authority": "human-principal",
        "lineage": "live",
        "backend": "python",
        "status": "sovereign",
        "registry_count": len(BRAND_REGISTRY),
    })


@app.get("/api/receipt")
def api_receipt():
    return JSONResponse({
        "receipt": {
            "origin": "æææ.com",
            "principal": "human",
            "default": "local-sovereign",
            "authority": "human-principal",
            "lineage": "live",
            "backend": "python",
            "status": "sovereign",
        }
    })


@app.get("/api/manifest")
def api_manifest():
    return JSONResponse({
        "name": "æææ.com",
        "tagline": "Open Intelligence · Private Authority · Sovereign Value",
        "principal": "human",
        "default": "local-sovereign",
        "backend": "python",
        "routes": list(ROUTE_MAP.keys()),
        "introspection": {
            "live": _introspection_snapshot().get("live", False),
            "source": _introspection_snapshot().get("source"),
        },
    })


@app.get("/api/tech")
def api_tech():
    state = build_machine_state(INTRO_SPOT, compute=COMPUTE_STATE, physical=PHYSICAL_STATE)
    return JSONResponse({
        "site": "æææ.com",
        "mode": "local-sovereign",
        "machine": state.to_dict()["surfaces"],
        "routes": ROUTE_MAP,
    })


COMPUTE_STATE = {
    "python": "3.11",
    "backend": "fastapi/uvicorn",
    "supervision_repo": "roboflow/supervision (cloned, shallow)",
    "digital_introspection": {
        "status": "active",
        "source": "supervision_intro/real_digital_introspection.py",
    },
}

PHYSICAL_STATE = {
    "zone": "workstation",
    "status": "not-wired",
    "note": "webcam zone introspection pending",
}


@app.get("/api/tech/introspection")
def api_tech_introspection():
    state = build_machine_state(INTRO_SPOT, compute=COMPUTE_STATE, physical=PHYSICAL_STATE)
    return JSONResponse(state.to_dict())


@app.post("/api/tech/introspect/scan")
def api_tech_introspect_scan():
    from pathlib import Path
    scanner = Path(__file__).resolve().parent.parent / "supervision" / "supervision_intro" / "real_digital_introspection.py"
    if not scanner.exists():
        return JSONResponse({"error": "scanner not found"}, status_code=503)
    import subprocess, sys
    proc = subprocess.run(
        [sys.executable, str(scanner)],
        cwd=PARENT,
        capture_output=True,
        text=True,
        timeout=90,
    )
    if proc.returncode != 0:
        return JSONResponse(
            {"error": "scan failed", "stderr": proc.stderr[-2000:]},
            status_code=500,
        )
    return JSONResponse(_introspection_snapshot())


@app.get("/dashboard", response_class=HTMLResponse)
@app.get("/dashboard/", response_class=HTMLResponse)
def dashboard():
    return HTMLResponse(DASHBOARD_HTML)


@app.get("/api/ticker")
def api_ticker():
    ticker = SiteTicker.from_backend(PARENT)
    return JSONResponse({
        "site": "æææ.com",
        "ticker": ticker.status_lines,
        "render": render_ticker_html(ticker),
    })


@app.get("/api/introspect")
def api_introspect():
    state = build_machine_state(INTRO_SPOT, compute=COMPUTE_STATE, physical=PHYSICAL_STATE)
    return JSONResponse({
        "site": "æææ.com",
        "surfaces": state.to_dict()["surfaces"],
    })


@app.post("/api/cmd")
def api_cmd(body: dict = None):
    if body is None:
        body = {}
    raw = (body.get("cmd") or "").strip()
    if not raw:
        from .commands import CommandResult
        return JSONResponse(CommandResult(ok=False, command="", error="missing cmd").to_dict(), status_code=400)
    tokens = raw.lower().split()
    cmd = tokens[0]
    arg = " ".join(tokens[1:]) if len(tokens) > 1 else ""
    result = exec_command(cmd, arg, PARENT)
    status = 200 if result.ok else 422
    return JSONResponse(result.to_dict(), status_code=status)


@app.get("/api/cmd/registry")
def api_cmd_registry():
    return JSONResponse({
        "commands": CMD_REGISTRY.items,
    })


@app.get("/")
def index():
    return HTMLResponse(INDEX_HTML)


@app.get("/{full_path:path}", response_class=HTMLResponse)
def index_or_static(full_path: str):
    if full_path and full_path not in ("index.html", "dashboard.html", ""):
        return JSONResponse({"detail": "not found"}, status_code=404)
    if full_path in ("dashboard.html", ""):
        return HTMLResponse(DASHBOARD_HTML)
    return HTMLResponse(INDEX_HTML)


def run_dev(host: str = "127.0.0.1", port: int = 4173) -> None:
    uvicorn.run(app, host=host, port=port)


def run_prod(host: str = "127.0.0.1", port: int = 4173) -> None:
    uvicorn.run(app, host=host, port=port, log_level="warning")


def main() -> None:
    port = int(os.getenv("PORT", "4177"))
    host = os.getenv("HOST", "127.0.0.1")

    try:
        uvicorn.run(app, host=host, port=port, log_level="info")
    except KeyboardInterrupt:
        print("shutting down")


if __name__ == "__main__":
    main()
