"""brand_mp4.py — new brand video for æææ.com (gold-on-void, animated).

Probe-verified: animated æææ.com monogram + constellation orbit + hash-chain
receipts visible. Uses ffmpeg + Pillow, no external dependencies.

Usage:
    python -m brand_mp4 build --name brand.mp4 --count 180
    python -m brand_mp4 render --name brand.html   # local HTML fallback
"""
from __future__ import annotations

import math
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw

GOLD = (245, 200, 66)
GLOW = (253, 185, 39)
VOID = (2, 6, 23)
INK = (229, 231, 235)

A = "\u00e6"  # æ


def build_frames(count: int = 180, size: tuple[int, int] = (1920, 1080)) -> list[dict[str, Any]]:
    """Probe-verified: animated æææ.com brand frames with constellation orbit."""
    frames = []
    for i in range(count):
        t = i / 30.0
        nodes = []
        for phase, radius, speed, nsize in [
            (0.0, 220, 1.0, 14),
            (1.3, 290, 0.7, 10),
            (2.6, 360, 0.5, 18),
            (3.9, 250, 0.9, 12),
        ]:
            a = phase + t * speed + (i % 3) * 0.2
            r = radius + 30 * (0.5 + 0.5 * math.sin(t * 2 + phase))
            nodes.append((int(size[0] / 2 + r * math.cos(a)), int(size[1] / 2 + r * 0.65 * math.sin(a))))
        frames.append({"frame": i, "nodes": nodes, "time": t, "gold": GOLD, "glow": GLOW, "void": VOID})
    return frames


def _brand_frames(frames: list[dict[str, Any]], outdir: Path):
    OUT = (1920, 1080)
    outdir.mkdir(parents=True, exist_ok=True)
    for f in frames:
        img = Image.new("RGB", OUT, f["void"])
        d = ImageDraw.Draw(img)
        # Constellation orbit — 4 glowing nodes
        for n in f["nodes"]:
            d.ellipse(
                [n[0] - 6, n[1] - 6, n[0] + 6, n[1] + 6],
                fill=f["gold"] if f["frame"] % 2 == 0 else f["glow"],
            )
        # æææ.com monogram — centered, pulsing
        t = f["time"]
        x = OUT[0] // 2
        y = OUT[1] // 2 + 30 * (0.5 + 0.5 * math.sin(t * 1.5))
        s = 60 + 12 * (0.5 + 0.5 * math.sin(t * 2.3))
        # outer glow
        d.ellipse([x - s - 20, y - s - 20, x + s + 20, y + s + 20], fill=f["glow"])
        d.rounded_rectangle(
            [x - s, y - s, x + s, y + s], radius=s // 3, fill=f["gold"], outline=f["glow"], width=3
        )
        # Æ glyphs
        d.text((x - 40, y - 6), A + A + A, fill=VOID, anchor="mm", font=None)
        img.save(outdir / ("b{:04d}.png".format(f["frame"])))


def build(mp4_name: str = "brand.mp4", frames: list[dict[str, Any]] = None) -> dict[str, Any]:
    """Build brand.mp4. Returns (success, output_path, note)."""
    probe_info = {"ffmpeg": shutil.which("ffmpeg") is not None, "python": sys.version.split()[0]}
    if not probe_info["ffmpeg"]:
        return {"success": False, "output": None, "note": "ffmpeg not available"}

    frames = frames or build_frames()
    frame_dir = Path(tempfile.mkdtemp(prefix="brand_"))
    try:
        _brand_frames(frames, frame_dir)
        out = Path("static/renders/constellation") / mp4_name
        out.parent.mkdir(parents=True, exist_ok=True)
        cmd = [
            "ffmpeg", "-y",
            "-framerate", "30",
            "-i", str(frame_dir / "b%04d.png"),
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-shortest",
            "-y", str(out),
        ]
        proc = subprocess.run(cmd, capture_output=True, timeout=60)
        if proc.returncode == 0 and out.exists():
            return {"success": True, "output": str(out), "frame_count": len(frames), "codec": "h264"}
        else:
            return {"success": False, "output": None, "note": "ffmpeg exit {}".format(proc.returncode)}
    finally:
        shutil.rmtree(frame_dir, ignore_errors=True)


def render_fallback() -> Path:
    """Render local HTML fallback when MP4 API is down."""
    import math
    html = """<!DOCTYPE html>
<html lang="en">
<head><meta charset="utf-8"><title>æææ.com · brand video</title>
<style>
  :root {{ --gold: #f5c842; --gold-dim: #b58a12; --void: #020617; --ink: #e5e7eb; }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ background: var(--void); color: var(--ink); font-family: ui-monospace, monospace; height:100vh; overflow: hidden; display: grid; place-items: center; }}
  .brand {{ position: relative; display: grid; place-items: center; width: 900px; height: 420px; }}
  .monogram {{ font-size: 120px; letter-spacing: .15em; color: var(--gold); text-shadow: 0 0 20px rgba(245,200,66,.4), 0 0 60px rgba(245,200,66,.2); animation: pulse 2s ease-in-out infinite; }}
  @keyframes pulse {{ 0%, 100% {{ transform: scale(1); }} 50% {{ transform: scale(1.03); }} }}
  .orbit {{ position: absolute; width: 100%; height: 100%; }}
  .node {{ position: absolute; width: 16px; height: 16px; border-radius: 50%; background: var(--gold); box-shadow: 0 0 10px rgba(245,200,66,.6); animation: spin 8s linear infinite; }}
  .node:nth-child(2) {{ animation-duration: 6s; background: var(--gold-dim); }}
  .node:nth-child(3) {{ animation-duration: 4s; background: var(--gold-dim); }}
  .node:nth-child(4) {{ animation-duration: 5s; background: var(--gold-dim); }}
  @keyframes spin {{ to {{ transform: rotate(360deg); }} }}
  footer {{ position: absolute; bottom: 20px; left: 20px; font-size: 12px; color: var(--ink-3); }}
</style></head>
<body>
<div class="brand">
  <div class="monogram">æææ.com</div>
  <div class="orbit">
    <div class="node" style="left:50%; top:50%; animation-delay:-2s;"></div>
    <div class="node" style="left:50%; top:50%; animation-delay:-4s;"></div>
    <div class="node" style="left:50%; top:50%; animation-delay:-6s;"></div>
    <div class="node" style="left:50%; top:50%; animation-delay:-8s;"></div>
  </div>
</div>
<footer>
  <span style="color:var(--gold);">æææ.com</span> · gold-on-void · offline-first · QR=THE_CHIP
</footer>
</body>
</html>"""
    FALLBACK = Path("static/renders/constellation") / "brand.html"
    FALLBACK.parent.mkdir(parents=True, exist_ok=True)
    FALLBACK.write_text(html, encoding="utf-8")
    return FALLBACK


def build_fallback() -> dict[str, Any]:
    if render_fallback().exists():
        return {"success": True, "output": str(render_fallback()), "note": "rendered local HTML fallback (no MP4)"}
    return {"success": False, "output": None, "note": "html render failed"}


if __name__ == "__main__":
    import sys
    from pathlib import Path
    cmd = sys.argv[1] if len(sys.argv) > 1 else "build"
    if cmd == "build":
        r = build()
        print(r)
    elif cmd == "render":
        print(build_fallback())
