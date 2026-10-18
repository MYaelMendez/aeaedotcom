"""fleet_demo.py — regenerates the glocal mesh fleet demo from capabilities.json.

The recursion: the manifest is the spine. Adding a capability = adding a JSON entry,
not writing a new scene function. This script iterates the manifest, probes each
surface live (graceful offline treatment where down), renders one scene per
capability, encodes fleet.mp4.
"""
import json
import shutil
import subprocess
import urllib.request
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

GOLD = (245, 200, 66)
GLOW = (253, 185, 39)
VOID = (2, 6, 23)
INK = (229, 231, 235)
NEON = (16, 185, 129)
DIM = (100, 116, 139)
RED = (239, 68, 68)

WIDTH, HEIGHT = 1920, 1080
FPS = 30
OUT = Path("static/renders/constellation/fleet.mp4")
MANIFEST = Path("capabilities.json")


def font(size):
    for p in ("C:/Windows/Fonts/verdana.ttf", "C:/Windows/Fonts/arial.ttf",
              "C:/Windows/Fonts/calibri.ttf"):
        if Path(p).exists():
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()


def probe(url, endpoint=None):
    """Probe a live endpoint. Returns (ok, data)."""
    try:
        target = url + endpoint if endpoint else url
        req = urllib.request.Request(target, headers={"User-Agent": "fleet-demo"})
        with urllib.request.urlopen(req, timeout=2) as resp:
            return True, json.loads(resp.read().decode())
    except Exception:
        return False, None


def base():
    img = Image.new("RGBA", (WIDTH, HEIGHT), VOID + (255,))
    ov = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    return img, ov, ImageDraw.Draw(ov)


def finish(img, ov):
    return Image.alpha_composite(img, ov).convert("RGB")


def title(d, text, sub=None):
    d.text((WIDTH / 2, 78), text, font=font(52), fill=GOLD, anchor="mm")
    if sub:
        d.text((WIDTH / 2, 138), sub, font=font(22), fill=INK, anchor="mm")


def footer(d, text="æ:// glocal mesh · recursive capabilities · sovereign fleet"):
    d.text((WIDTH / 2, HEIGHT - 52), text, font=font(20), fill=DIM, anchor="mm")


def draw_capability(d, cap, ok, data, t):
    """Draw one capability card. Gold border if live, dim if offline."""
    name = cap["name"]
    kind = cap["kind"]
    verbs = cap.get("verbs", [])
    col = GOLD if ok else DIM
    # Card
    d.rounded_rectangle([80, 220, 1840, 820], radius=12, fill=(15, 23, 42), outline=col, width=2)
    # Status dot
    status_col = NEON if ok else RED
    d.ellipse([110, 250, 122, 262], fill=status_col + (255,))
    d.text((132, 256), "LIVE" if ok else "OFFLINE", font=font(16), fill=status_col)
    # Name
    d.text((110, 290), name, font=font(36), fill=col)
    # Kind
    d.text((110, 345), kind, font=font(18), fill=INK)
    # URL / path
    loc = cap.get("url") or cap.get("path") or "—"
    d.text((110, 385), loc, font=font(14), fill=DIM)
    # Verbs
    verb_str = " · ".join(verbs) if verbs else "—"
    d.text((110, 430), f"verbs: {verb_str}", font=font(16), fill=GOLD)
    # Notes
    notes = cap.get("notes", "")
    if len(notes) > 90:
        notes = notes[:87] + "…"
    d.text((110, 470), notes, font=font(13), fill=INK)
    # Live data preview
    if ok and data:
        d.text((110, 530), "live data:", font=font(14), fill=DIM)
        preview = json.dumps(data, separators=(",", ":"))[:120]
        d.text((110, 560), preview, font=font(12), fill=NEON)
    elif ok:
        d.text((110, 530), "reachable — no data endpoint", font=font(13), fill=DIM)
    else:
        d.text((110, 530), "offline — graceful degradation", font=font(13), fill=RED)


def scene_capability(cap, ok, data, i, total):
    """Render one capability scene with a subtle pulse."""
    t = i / FPS
    img, ov, d = base()
    title(d, f"æ:// glocal mesh", f"recursive capabilities — {cap['name']}")
    draw_capability(d, cap, ok, data, t)
    footer(d)
    return finish(img, ov)


def scene_mesh_overview(caps, ok_map, i, total):
    """Overview scene — the full mesh topology as a node graph."""
    t = i / FPS
    img, ov, d = base()
    title(d, "æ:// glocal mesh", f"{len(caps)} capabilities · {sum(ok_map.values())} live · recursive")
    cx, cy = WIDTH // 2, HEIGHT // 2
    # Center node
    d.ellipse([cx - 28, cy - 28, cx + 28, cy + 28], fill=GLOW + (255,))
    d.text((cx, cy), "æ", font=font(20), fill=VOID, anchor="mm")
    # Capability nodes in a circle
    n = len(caps)
    for k, cap in enumerate(caps):
        angle = (2 * 3.14159 * k / n) - 3.14159 / 2
        nx = cx + 500 * (0.6 + 0.4 * (1 if ok_map.get(cap["id"], False) else 0.3)) * (1 if k % 2 == 0 else -1)
        ny = cy + 300 * (0.6 + 0.4 * (1 if ok_map.get(cap["id"], False) else 0.3)) * (1 if k % 3 == 0 else -1)
        ok = ok_map.get(cap["id"], False)
        col = GOLD if ok else DIM
        node_r = 18 if ok else 12
        d.line([(cx, cy), (nx, ny)], fill=col + (80,), width=1)
        d.ellipse([nx - node_r, ny - node_r, nx + node_r, ny + node_r], fill=col + (255,))
        d.text((nx, ny + node_r + 18), cap["name"], font=font(12), fill=col, anchor="mm")
    footer(d)
    return finish(img, ov)


def scene_summary(caps, ok_map, i, total):
    """Summary — counts + recursion note."""
    t = i / FPS
    img, ov, d = base()
    title(d, "recursive capabilities", "manifest → fleet render → CLI verb → glocal mesh")
    live = sum(ok_map.values())
    total_caps = len(caps)
    lines = [
        f"capabilities: {total_caps}",
        f"live: {live}",
        f"offline: {total_caps - live}",
        "",
        "manifest: capabilities.json",
        "renderer: fleet_demo.py",
        "cli verb: localagent.py render fleet",
        "",
        "adding a capability = adding a JSON entry",
        "the fleet demo regenerates itself",
    ]
    for k, line in enumerate(lines):
        col = GOLD if k < 4 else (NEON if "regenerates" in line else INK)
        d.text((WIDTH // 2, 280 + k * 55), line, font=font(24), fill=col, anchor="mm")
    footer(d)
    return finish(img, ov)


def build():
    caps = json.loads(MANIFEST.read_text())["capabilities"]
    ok_map = {}
    data_map = {}
    for cap in caps:
        url = cap.get("url")
        endpoint = cap.get("state_endpoint")
        if url and endpoint and url.startswith("http"):
            ok, data = probe(url, endpoint)
        elif url and url.startswith("http"):
            ok, data = probe(url)
        else:
            ok, data = False, None
        ok_map[cap["id"]] = ok
        data_map[cap["id"]] = data

    OUT.parent.mkdir(parents=True, exist_ok=True)
    tmp = OUT.parent / "_fleet_tmp"
    tmp.mkdir(parents=True, exist_ok=True)
    n = 0
    # Overview
    for i in range(90):
        scene_mesh_overview(caps, ok_map, i, 90).save(tmp / ("fl{:04d}.png".format(n)))
        n += 1
    # Per-capability scenes
    for cap in caps:
        ok = ok_map[cap["id"]]
        data = data_map[cap["id"]]
        for i in range(90):
            scene_capability(cap, ok, data, i, 90).save(tmp / ("fl{:04d}.png".format(n)))
            n += 1
    # Summary
    for i in range(90):
        scene_summary(caps, ok_map, i, 90).save(tmp / ("fl{:04d}.png".format(n)))
        n += 1
    subprocess.run([
        "ffmpeg", "-y", "-v", "error", "-f", "image2", "-r", str(FPS),
        "-i", str(tmp / "fl%04d.png"),
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(OUT),
    ], check=True)
    shutil.rmtree(tmp, ignore_errors=True)
    return {"success": True, "output": str(OUT), "frames": n, "duration": n / FPS,
            "live": sum(ok_map.values()), "total": len(caps)}


if __name__ == "__main__":
    print(json.dumps(build()))
