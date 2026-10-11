"""SHA-256 hash-chained QR = THE_CHIP receipts — offline, deterministic.

Each artifact carries a scannable QR with a hash chain:
    trust = sum(evidence) / sum(uncertainty)
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

CHAIN_MIN_LENGTH = 8  # default minimum hash chain depth


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_hex(data: bytes | str) -> str:
    if isinstance(data, str):
        data = data.encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def receipt_fields(
    tid: str,
    verdict: str,
    evidence: list[str] = None,
    uncertainty: list[str] = None,
    trust: float = 0.0,
) -> dict[str, Any]:
    return {
        "id": tid,
        "verdict": verdict,
        "evidence": evidence or [],
        "uncertainty": uncertainty or [],
        "trust": trust,
        "issued_at": now_iso(),
    }


def compute_trust(evidence: list[str] = None, uncertainty: list[str] = None) -> float:
    ev = evidence or []
    unc = uncertainty or []
    if not ev and not unc:
        return 0.0
    return round(sum(1 for e in ev if e) / (sum(1 for e in ev if e) + sum(1 for u in unc if u)) * 100, 2)


def seal_receipt(payload: dict[str, Any]) -> dict[str, Any]:
    """Hash-chain a receipt: prev_hash binds the chain."""
    prev_hash = payload.get("prev_hash")
    chain = payload.get("chain", [])
    payload = dict(payload)
    payload.pop("prev_hash", None)
    payload.pop("chain", None)
    payload["payload_hash"] = sha256_hex(json.dumps(payload, sort_keys=True).encode())
    chain.append(payload["payload_hash"])
    payload["chain"] = chain
    if prev_hash:
        payload["prev_hash"] = prev_hash
    payload["seal_hash"] = sha256_hex(json.dumps(payload, sort_keys=True).encode())
    payload["trust"] = compute_trust(payload.get("evidence", []), payload.get("uncertainty", []))
    return payload


def append_receipt(path: Path, receipt: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    chain = receipt.get("chain", [])
    receipt["prev_hash"] = sha256_hex(json.dumps(chain[-1], sort_keys=True).encode()) if chain else "genesis"
    sealed = seal_receipt(receipt)
    import json as _json
    path.write_text(_json.dumps(sealed, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def read_receipt(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def qr_data(receipt: dict[str, Any]) -> str:
    import json as _json
    return _json.dumps(receipt, ensure_ascii=False, separators=(",", ":"))
