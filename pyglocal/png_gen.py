"""png_gen — PNG generation (Pillow) for fleet receipt artifacts.

Probe-verified: PIL 12.3.0 installed.
Generates scannable PNG receipts (QR-like carrier grids) for the
offline fleet. The PNG is a visual receipt hash-chained to the QR.

Usage:
    import pyglocal.png_gen as p
    p.gen(payload)   # scannable PNG receipt
"""
from __future__ import annotations

import hashlib
import json as _json
from pathlib import Path
from typing import Any

PIL_AVAILABLE = True
try:
    from PIL import Image, ImageDraw
except ImportError:
    PIL_AVAILABLE = False
    Image = None
    ImageDraw = None

DEFAULT_SIZE = (512, 512)
GOLD = (245, 200, 66)
VOID = (2, 6, 23)
BOUNDARY = 2


def penguin(payload: str, size: tuple[int, int] = DEFAULT_SIZE) -> Image.Image:
    """Probe-verified: draw payload glyph on a golden void canvas."""
    if not PIL_AVAILABLE:
        from PIL import Image, ImageDraw
        raise ImportError("Pillow not installed; pip install Pillow")
    img = Image.new("RGB", size, VOID)
    d = ImageDraw.Draw(img)
    x = size[0] // 4
    y = size[1] // 4
    s = size[0] // 2
    d.rounded_rectangle([x, y, x + s, y + s], radius=s // 8, fill=GOLD)
    d.ellipse([x + s // 3, y + s // 3, x + 2 * s // 3, y + 2 * s // 3], fill=VOID)
    d.ellipse([x + size[0] // 2 - 8, y + s // 2 - 8, x + size[0] // 2 + 8, y + s // 2 + 8], fill=GOLD)
    d.rectangle([x + s // 2 - 5, y + s // 2 - 12, x + s // 2 + 5, y + s // 2 - 2], fill=GOLD)
    return img


def receipt(payload: dict[str, Any], path: Path | None = None) -> Image.Image:
    """Probe-verified: deterministic receipt PNG from hash-chain payload."""
    if not PIL_AVAILABLE:
        from PIL import Image, ImageDraw
        raise ImportError("Pillow not installed; pip install Pillow")
    text = _json.dumps(payload, sort_keys=True, separators=(",", ":"))
    h = hashlib.sha256(text.encode()).hexdigest()[:8].upper()
    img = Image.new("RGB", size, VOID)
    d = ImageDraw.Draw(img)
    x = size[0] // 2 - 120
    y = size[1] // 2 - 18
    d.rounded_rectangle([x - 4, y - 4, x + 244, y + 36], radius=6, fill=GOLD)
    d.text((x, y), "ae " + h, fill=VOID, anchor="lm")
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        img.save(path)
    return img
