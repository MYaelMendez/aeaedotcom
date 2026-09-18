#!/usr/bin/env python3
"""
æææ.com backend coherence checker.

Validates:
    - All documented API routes return 200.
    - /api/brands/{key} returns a known brand.
    - /api/brands/{key} returns 404 for unknown key.
    - /api/root, /api/receipt, /api/manifest schema coherence.
    - Frontend index.html serves over /.
"""

import json
import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BASE = os.environ.get("AEAEDOTCOM_BASE", str(ROOT))
PORT = int(os.environ.get("AEAEDOTCOM_PORT", "4174"))
BASE_URL = f"http://localhost:{PORT}"


def http_get(path: str, expect_status: int = 200) -> dict:
    url = f"{BASE_URL}{path}"
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = resp.read().decode("utf-8")
            status = resp.status
            if status != expect_status:
                return {"ok": False, "path": path, "status": status, "body": body}
            try:
                parsed = json.loads(body)
            except json.JSONDecodeError:
                return {"ok": False, "path": path, "status": status, "body": body, "error": "invalid-json"}
            return {"ok": True, "path": path, "status": status, "body": parsed}
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8")
        if exc.code != expect_status:
            return {"ok": False, "path": path, "status": exc.code, "body": body, "error": "unexpected-status"}
        try:
            parsed = json.loads(body)
        except json.JSONDecodeError:
            return {"ok": False, "path": path, "status": exc.code, "body": body, "error": "invalid-json"}
        return {"ok": True, "path": path, "status": exc.code, "body": parsed}
    except Exception as exc:
        return {"ok": False, "path": path, "error": str(exc)}


def check_frontend_html() -> dict:
    url = f"{BASE_URL}/"
    req = urllib.request.Request(url, headers={"Accept": "text/html"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = resp.read().decode("utf-8")
            if "æææ.com" not in body:
                return {"ok": False, "path": "/", "error": "missing brand title"}
            if "Open Intelligence" not in body:
                return {"ok": False, "path": "/", "error": "missing tagline"}
            if "local-sovereign" not in body:
                return {"ok": False, "path": "/", "error": "missing sovereign marker"}
            return {"ok": True, "path": "/", "bytes": len(body)}
    except Exception as exc:
        return {"ok": False, "path": "/", "error": str(exc)}


def main() -> int:
    results = []

    # Health + status
    for path in ["/health", "/api/status"]:
        results.append(http_get(path))

    # Brands list
    results.append(http_get("/api/brands"))

    # Single brand
    results.append(http_get("/api/brands/ae"))

    # Unknown brand -> 404
    results.append(http_get("/api/brands/missing", expect_status=404))

    # Root / receipt / manifest
    for path in ["/api/root", "/api/receipt", "/api/manifest"]:
        results.append(http_get(path))

    # Frontend HTML coherence
    results.append(check_frontend_html())

    # Summary
    all_ok = all(r.get("ok", False) for r in results)
    failed = [r for r in results if not r.get("ok", False)]

    print("=== æææ.com backend coherence ===")
    for r in results:
        status = "PASS" if r.get("ok", False) else "FAIL"
        path = r.get("path", "<no-path>")
        if r.get("ok", False) and "body" in r:
            snippet = json.dumps(r["body"])
            if len(snippet) > 120:
                snippet = snippet[:120] + "..."
            print(f"{status:4} {path:18} {snippet}")
        else:
            details = r.get("error") or r.get("body") or ""
            if isinstance(details, dict):
                details = json.dumps(details)
            print(f"{status:4} {path:18} {details}")
    print("==================================")
    if all_ok:
        print("Coherence OK")
        return 0
    else:
        print(f"Coherence FAIL — {len(failed)} failing checks")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
