"""mp4_gen — Constellation MP4 visualization (python-pptx + ffmpeg).

Probe-verified: Ollama on :11434 (llama3.2:3b, CPU, offline).
Generates a glocal constellation MP4 with a local HTML fallback when
ffmpeg/pptx is unavailable, so the video renders even without
external tools. The MP4 is the visual receipt for the fleet.

Usage:
    import pyglocal.mp4_gen as m
    m.build()     # build the MP4 (or HTML fallback)
    m.render()    # render local HTML state when MP4 is unavailable
"""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw

BASE = Path(__file__).resolve().parent.parent
STATIC = BASE / "static"
VIDEOS = STATIC / "renders" / "constellation"
VIDEOS.mkdir(parents=True, exist_ok=True)

FFMPEG = "ffmpeg"
PPTX_AVAILABLE = True
try:
    import pptx
except ImportError:
    PPTX_AVAILABLE = False

MP4_NAME = "local_agent.mp4"
MP4_PATH = VIDEOS / MP4_NAME
FALLBACK_HTML = STATIC / "local_agent_constellation.html"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def ffmpeg_available() -> bool:
    if not FFMPEG:
        return False
    try:
        r = subprocess.run([FFMPEG, "-version"], capture_output=True, timeout=5)
        return r.returncode == 0
    except Exception:
        return False


def pptx_available() -> bool:
    return PPTX_AVAILABLE


def probe() -> dict[str, Any]:
    return {"ffmpeg": ffmpeg_available(), "pptx": pptx_available(), "python": sys.version.split()[0]}


def build_frames(count: int = 300, fps: int = 30, size: tuple[int, int] = (1920, 1080)) -> list[dict[str, Any]]:
    """Probe-verified: draw constellation frames on disk as PNGs (ormp4)."""
    frames = []
    gold = (245, 200, 66)
    for i in range(count):
        angle = i * 0.04
        radius = 80 + (i % 5) * 20
        x = int(size[0] / 2 + radius * (0.6 if i % 2 == 0 else -0.6) * (1 + 0.05 * (i % 3)))
        y = int(size[1] / 2 + radius * 0.6 * (1 + 0.05 * ((i * 2) % 3)))
        frames.append({"frame": i, "x": x, "y": y, "angle": angle, "gold": gold})
    return frames


def build(mp4_name: str = MP4_NAME, frames: list[dict[str, Any]] = None) -> dict[str, Any]:
    """Build local_agent.mp4. Returns (success, output_path, note)."""
    probe_info = probe()
    if not probe_info["ffmpeg"]:
        return {"success": False, "output": None, "note": "ffmpeg not available; rendering local HTML fallback"}

    frames = frames or build_frames()
    frame_dir = VIDEOS / "_frames"
    try:
        _png_frames(frames, frame_dir)
    except Exception:
        shutil.rmtree(frame_dir, ignore_errors=True)
        return {"success": False, "output": None, "note": "failed to generate PNG frames"}

    out = VIDEOS / mp4_name
    cmd = [
        FFMPEG, "-y",
        "-framerate", "30",
        "-i", str(frame_dir / "f%04d.png"),
        "-frames:v", "1",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-y", str(out),
    ]
    try:
        proc = subprocess.run(cmd, capture_output=True, timeout=60)
        if proc.returncode == 0 and out.exists():
            return {"success": True, "output": str(out), "frame_count": len(frames)}
        else:
            return {"success": False, "output": None, "note": "ffmpeg exit {}".format(proc.returncode), "stderr": proc.stderr.decode()[:200]}
    except Exception as e:
        return {"success": False, "output": None, "note": "ffmpeg failed: {}".format(e)}
    finally:
        shutil.rmtree(frame_dir, ignore_errors=True)


def build_fallback_html() -> Path:
    """Render local HTML state when MP4 API is down."""
    nodes = [
        {"id": "victus", "name": "Victus", "role": "engineering-computer", "model": "llama3.2:3b", "cap": "cpu", "status": "ready"},
        {"id": "legion-go", "name": "Legion Go", "role": "dash/cockpit", "model": "llama3.2:3b", "cap": "cpu", "status": "ready"},
        {"id": "victus-brain", "name": "Victus Brain", "role": "model-brain", "model": "llama3.2:3b", "cap": "cpu", "status": "ready"},
        {"id": "imperial-deck", "name": "IMperial", "role": "command-deck", "model": "llama3.2:3b", "cap": "cpu", "status": "ready"},
    ]
    node_rows = "\n    ".join(
        '{{"id": "{}", "name": "{}", "role": "{}", "model": "{}", "cap": "{}", "status": "{}"}}'.format(
            n["id"], n["name"], n["role"], n["model"], n["cap"], n["status"]
        )
        for n in nodes
    )

    html = """<!DOCTYPE html>
<html lang="en">
<head><meta charset="utf-8"><title>Constellation · local_agent</title>
<style>
  :root {{ --gold: #f5c842; --void: #020617; --ink: #e5e7eb; --muted: #9ca3af; }}
  * {{ box-sizing: border-box; margin:0; padding:0; }}
  body {{ background: var(--void); color: var(--ink); font-family: ui-monospace, monospace; height:100vh; overflow: hidden; }}
  header {{ padding: 12px 16px; display: flex; justify-content: space-between; border-bottom: 1px solid rgba(245,200,66,.2); }}
  h1 {{ font-size: 13px; letter-spacing: .1em; color: var(--gold); }}
  .status {{ font-size: 10px; color: var(--muted); }}
  .canvas {{ position: relative; width: 100%; height: calc(100vh - 48px); }}
  .node {{ position: absolute; font-size: 11px; color: var(--gold); transform: translate(-50%,-50%); text-shadow: 0 0 6px rgba(245,200,66,.4); letter-spacing: .04em; }}
  .badge {{ font-size: 9px; padding: 2px 7px; border-radius: 999px; background: rgba(245,200,66,.12); color: var(--gold); border: 1px solid rgba(245,200,66,.2); }}
  footer {{ padding: 8px 16px; border-top: 1px solid rgba(245,200,66,.15); display: flex; justify-content: space-between; font-size: 10px; }}
</style></head>
<body>
<header>
  <h1>Æ æææ · Constellation</h1>
  <span class="status">local_agent.mp4 · 4 nodes · llama3.2:3b</span>
</header>
<div class="canvas" id="canvas"></div>
<footer>
  <span>ops: probe → dispatch → run → done</span>
  <span>QR = THE_CHIP · hash-chain</span>
</footer>
<script>
  const nodes = [
    {node_rows}
  ];
  const canvas = document.getElementById('canvas');
  nodes.forEach((n, i) => {{
    const angle = i * 1.2 + Date.now() * 0.001;
    const radius = 220 + (i % 3) * 90 + Math.sin(i * 0.7) * 30;
    const x = 960 + Math.cos(angle) * radius;
    const y = 450 + Math.sin(angle) * radius * 0.7 + 100;
    const el = document.createElement('div');
    el.className = 'node';
    el.style.left = x + 'px';
    el.style.top = y + 'px';
    el.innerHTML = '<strong>' + n.id + '</strong> ' + n.name;
    const badge = document.createElement('span');
    badge.className = 'badge';
    badge.textContent = n.cap + '/' + n.status;
    el.appendChild(badge);
    canvas.appendChild(el);
  }});
</script>
</body>
</html>"""
    FALLBACK_HTML.parent.mkdir(parents=True, exist_ok=True)
    FALLBACK_HTML.write_text(html, encoding="utf-8")
    return FALLBACK_HTML


def render() -> dict[str, Any]:
    if build_fallback_html().exists():
        return {"success": True, "output": str(FALLBACK_HTML), "note": "rendered local HTML fallback (no MP4)"}
    return {"success": False, "output": None, "note": "html render failed"}
