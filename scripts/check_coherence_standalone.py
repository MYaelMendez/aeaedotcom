"""æææ.com backend coherence gate."""

import requests

BASE = "http://localhost:4174"

ROUTES = {
    "/health",
    "/api/status",
    "/api/brands",
    "/api/brands/ae",
    "/api/brands/missing",
    "/api/root",
    "/api/receipt",
    "/api/manifest",
}


def test_urls() -> list[tuple[str, int | str]]:
    results = []
    for url in ROUTES:
        try:
            r = requests.get(BASE + url, timeout=3)
            results.append((url, r.status_code))
        except Exception as e:
            results.append((url, f"ERROR: {e}"))
    for url, code in results:
        if isinstance(code, int) and code != 200 and code != 404:
            raise SystemExit(f"Unexpected status on {url}: {code}")
    return results


def test_root_payload() -> dict:
    r = requests.get(BASE + "/api/root", timeout=3)
    r.raise_for_status()
    data = r.json()
    assert data.get("origin") == "æææ.com"
    assert data.get("tagline") == "Open Intelligence · Private Authority · Sovereign Value"
    assert data.get("principal") == "human"
    assert data.get("default") == "local-sovereign"
    assert data.get("authority") == "human-principal"
    assert data.get("lineage") == "live"
    assert data.get("backend") == "python"
    assert data.get("status") == "sovereign"
    assert data.get("registry_count") == 14
    return data


def test_brand_lookup() -> None:
    r = requests.get(BASE + "/api/brands/ae", timeout=3)
    r.raise_for_status()
    brand = r.json()
    assert brand["key"] == "ae"
    assert brand["label"] == "æ:"
    assert brand["status"] == "root"
    assert brand["href"] == "https://æææ.com"


def test_missing_brand() -> None:
    r = requests.get(BASE + "/api/brands/missing", timeout=3)
    assert r.status_code == 404, f"expected 404, got {r.status_code}"
    assert r.json()["detail"] == "brand not found"


if __name__ == "__main__":
    print("running coherence checks...")
    test_urls()
    test_root_payload()
    test_brand_lookup()
    test_missing_brand()
    print("coherence OK")
