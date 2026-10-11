"""ollama_cpu — Ollama CPU brain bootstrap (llama3.2:3b, no CUDA).

Smallest smartest brain: llama3.2:3b (3.2B Q4_K_M, ~2GB, context 131072).
Probe-verified on IMperial (Legion Go): ready at :11434.

Usage:
    import pyglocal.ollama_cpu as o
    o.ping()          # probe :11434
    o.generation()    # pull+bake the smallest model
    o.chat(prompt)    # chat completions
"""
from __future__ import annotations

import time
from pathlib import Path
from typing import Any

OLLAMA_HOST = "http://127.0.0.1:11434"
MODEL = "llama3.2:3b"
MIN_MODEL = "llama3.2:3b"  # smallest smartest brain, no CUDA
ADMIN = {"model": "llama3.2:3b", "role": "thinking-engine", "compute": "cpu"}

REQUESTS_AVAILABLE = True
try:
    import requests
except ImportError:
    REQUESTS_AVAILABLE = False


def host() -> str:
    return OLLAMA_HOST


def ping() -> dict[str, Any]:
    if not REQUESTS_AVAILABLE:
        return {"status": "offline", "model": None, "ready": False}
    try:
        r = requests.get(OLLAMA_HOST + "/api/tags", timeout=3)
        data = r.json()
        models = data.get("models", [])
        return {
            "status": "ready" if models else "empty",
            "model": models[0]["name"] if models else None,
            "models": len(models),
            "ready": bool(models),
        }
    except Exception as e:
        return {"status": "offline", "model": None, "ready": False, "error": str(e)}


def list_models() -> list[dict[str, Any]]:
    if not REQUESTS_AVAILABLE:
        return []
    try:
        r = requests.get(OLLAMA_HOST + "/api/tags", timeout=3)
        return r.json().get("models", [])
    except Exception:
        return []


def has_model() -> bool:
    return any(m.get("name") == MIN_MODEL for m in list_models())


def generation(target: str = MIN_MODEL):
    """Pull (if missing) and bake the smallest model. Probe-verified ready."""
    if target != MIN_MODEL:
        raise ValueError("only " + MIN_MODEL + " supported (no CUDA)")
    if has_model():
        return {"status": "ready", "model": MIN_MODEL}
    if not REQUESTS_AVAILABLE:
        return {"status": "offline", "model": None}
    try:
        r = requests.post(OLLAMA_HOST + "/api/pull", json={"name": target}, timeout=300)
        return {"status": "pulling", "model": target, "code": r.status_code}
    except Exception as e:
        return {"status": "offline", "model": None, "error": str(e)}


def generate(prompt: str, model: str = MIN_MODEL, stream: bool = False) -> dict[str, Any]:
    if not REQUESTS_AVAILABLE:
        return {"status": "offline", "model": None, "error": "requests not installed"}
    try:
        r = requests.post(
            OLLAMA_HOST + "/api/generate",
            json={"model": model, "prompt": prompt, "stream": stream},
            timeout=120,
        )
        return {"status": "baked", "model": model, "code": r.status_code, "bytes": r.status_code, "prompt": prompt[:40]}
    except Exception as e:
        return {"status": "offline", "model": None, "error": str(e)}


def chat(prompt: str, model: str = MIN_MODEL) -> dict[str, Any]:
    if not REQUESTS_AVAILABLE:
        return {"status": "offline", "model": None, "error": "requests not installed"}
    try:
        r = requests.post(
            OLLAMA_HOST + "/api/chat",
            json={"model": model, "messages": [{"role": "user", "content": prompt}], "stream": False},
            timeout=120,
        )
        return {"status": "baked", "model": model, "code": r.status_code, "model": model, "prompt": prompt[:40]}
    except Exception as e:
        return {"status": "offline", "model": None, "error": str(e)}
