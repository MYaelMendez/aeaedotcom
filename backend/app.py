"""æææ.com backend — agentic coherence main server."""

import os
import signal
import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from pathlib import Path

app = FastAPI(title="æææ.com backend")

BASE = Path(__file__).resolve().parent
PARENT = BASE.parent
INDEX_HTML = (PARENT / "index.html").read_text(encoding="utf-8")

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
        "routes": [
            "/",
            "/health",
            "/api/status",
            "/api/brands",
            "/api/brands/{key}",
            "/api/root",
            "/api/receipt",
            "/api/manifest",
        ],
    })


@app.get("/{full_path:path}", response_class=HTMLResponse)
def index_or_static(full_path: str):
    if full_path and full_path != "index.html":
        return JSONResponse({"detail": "not found"}, status_code=404)
    return HTMLResponse(INDEX_HTML)


def run_dev(host: str = "127.0.0.1", port: int = 4173) -> None:
    uvicorn.run(app, host=host, port=port)


def run_prod(host: str = "127.0.0.1", port: int = 4173) -> None:
    uvicorn.run(app, host=host, port=port, log_level="warning")


def main() -> None:
    port = int(os.getenv("PORT", "4174"))
    host = os.getenv("HOST", "127.0.0.1")

    def shutdown_handler(signum, frame):
        print("shutting down")
        os._exit(0)

    signal.signal(signal.SIGTERM, shutdown_handler)

    uvicorn.run(app, host=host, port=port, log_level="info")


if __name__ == "__main__":
    main()
