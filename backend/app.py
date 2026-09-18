from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import importlib.util

app = FastAPI(title="æææ.com backend")

BASE = Path(__file__).resolve().parent
STATIC = BASE / "static"
TEMPLATES = BASE / "templates"
DATA = BASE / "data"
DATA.mkdir(exist_ok=True)

for folder in (STATIC, TEMPLATES):
    folder.mkdir(exist_ok=True)

INDEX_HTML = (BASE.parent / "index.html").read_text(encoding="utf-8")

STATUS = {
    "site": "æææ.com",
    "mode": "local-sovereign",
    "status": "online",
    "backend": "python",
}

BRANDS = [
    {"key": "ae", "label": "æ:", "href": "https://xn--6caaa.com/%C3%A6%3A", "status": "root"},
    {"key": "yael", "label": "yæl", "href": "https://xn--6caaa.com/y%C3%A6l", "status": "identity"},
    {"key": "llmstore", "label": "LLM.store", "href": "https://xn--6caaa.com/llm-store-1", "status": "intelligence"},
    {"key": "privateclient", "label": "privateclient.ai", "href": "https://xn--6caaa.com/privateclient-ai", "status": "custody"},
    {"key": "molt", "label": "molt.earth", "href": "https://xn--6caaa.com/molt-earth", "status": "evolve"},
    {"key": "cli", "label": "cli.llc", "href": "https://xn--6caaa.com/cli-llc", "status": "execute"},
    {"key": "dao", "label": "daollc.ai", "href": "https://xn--6caaa.com/daollc-ai", "status": "economy"},
    {"key": "teologia", "label": "teologia.ai", "href": "https://xn--6caaa.com/teologia-ai", "status": "knowledge"},
    {"key": "zacapa", "label": "zacapa.ai", "href": "https://xn--6caaa.com/zacapa-ai", "status": "place"},
    {"key": "enchiridion", "label": "enchiridion", "href": "https://xn--6caaa.com/enchiridion", "status": "canon"},
    {"key": "neuromitosis", "label": "neuromitosis", "href": "https://xn--6caaa.com/neuromitosis", "status": "distribute"},
    {"key": "commandprompt", "label": "commandprompt", "href": "https://xn--6caaa.com/commandprompt", "status": "intent"},
    {"key": "ioa", "label": "ioa", "href": "https://xn--6caaa.com/ioa", "status": "network"},
    {"key": "consumerredline", "label": "Consumer Redline Index", "href": "https://xn--6caaa.com/consumer-redline-index", "status": "measure"},
]


@app.get("/health")
def health():
    return JSONResponse(STATUS)


@app.get("/api/status")
def api_status():
    return JSONResponse(STATUS)


@app.get("/api/brands")
def api_brands():
    return JSONResponse({"count": len(BRANDS), "items": BRANDS})


@app.get("/api/receipt")
def api_receipt():
    return JSONResponse({
        "receipt": {
            "origin": "æææ.com",
            "authority": "human-principal",
            "lineage": "live",
            "backend": "python",
            "status": "sovereign"
        }
    })


@app.get("/api/manifest")
def api_manifest():
    return JSONResponse({
        "name": "æææ.com",
        "tagline": "Open Intelligence · Private Authority · Sovereign Value",
        "backend": "python",
        "routes": [
            "/",
            "/health",
            "/api/status",
            "/api/brands",
            "/api/receipt",
            "/api/manifest"
        ]
    })


@app.get("/{full_path:path}", response_class=HTMLResponse)
def index_or_static(full_path: str):
    if full_path and full_path != "index.html":
        return JSONResponse({"detail": "not found"}, status_code=404)
    return HTMLResponse(INDEX_HTML)


def run_dev(host: str = "127.0.0.1", port: int = 4173):
    import uvicorn
    uvicorn.run(app, host=host, port=port)


def run_prod(host: str = "127.0.0.1", port: int = 4173):
    import uvicorn
    uvicorn.run(app, host=host, port=port, log_level="warning")
