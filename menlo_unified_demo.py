"""menlo_unified_demo.py — Menlo robot unified with local_agent.

Scene: the full chain — CLI dispatcher → HTTP bridge → SDK fake edge →
kabban board → live dashboard. Gold-on-void, real bridge data.
"""
import math
import shutil
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

GOLD = (245, 200, 66)
GLOW = (253, 185, 39)
VOID = (2, 6, 23)
INK = (229, 231, 235)
NEON = (16, 185, 129)
DIM = (100, 116, 139)

WIDTH, HEIGHT = 1920, 1080
FPS = 30
OUT = Path("static/renders/constellation/menlo_unified.mp4")

# Real bridge data (probed live)
STATE = {"mode": 0, "armed": False, "joints": 25, "commands_received": 3,
         "state_frames": 109, "clock": 1000.54}
LOG = [
    {"verb": "stand", "clock": 1000.52, "ok": True, "mode": 1, "armed": True},
    {"verb": "damp", "clock": 1000.54, "ok": True, "mode": 0, "armed": False},
    {"verb": "balance", "clock": 1000.54, "ok": False, "error": "stand() first"},
]
TASKS = [
    {"id": "740ce953", "intent": "menlo:stand", "status": "done", "evidence": 1},
    {"id": "373a677b", "intent": "menlo:damp", "status": "done", "evidence": 1},
]


def font(size, bold=True):
    for p in ("C:/Windows/Fonts/verdana.ttf", "C:/Windows/Fonts/arial.ttf",
              "C:/Windows/Fonts/calibri.ttf"):
        if Path(p).exists():
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()


def base(t):
    img = Image.new("RGBA", (WIDTH, HEIGHT), VOID + (255,))
    ov = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    return img, ov, ImageDraw.Draw(ov)


def finish(img, ov):
    return Image.alpha_composite(img, ov).convert("RGB")


def title(d, text, sub=None):
    d.text((WIDTH / 2, 78), text, font=font(52), fill=GOLD, anchor="mm")
    if sub:
        d.text((WIDTH / 2, 138), sub, font=font(22), fill=INK, anchor="mm")


def footer(d, text="#ioa · menlo · local_agent · sovereign mesh"):
    d.text((WIDTH / 2, HEIGHT - 52), text, font=font(20), fill=DIM, anchor="mm")


def scene_cli(i, total):
    """CLI dispatcher — localagent.py menlo subcommand."""
    t = i / FPS
    img, ov, d = base(t)
    title(d, "local_agent dispatcher", "python localagent.py menlo <verb> — kabban evidence · menlo:execute events")
    # CLI panel
    px, py = 100, 250
    d.rounded_rectangle([px, py, px + 800, py + 500], radius=12, fill=(15, 23, 42), outline=GLOW, width=2)
    d.text((px + 30, py + 30), "$ localagent.py menlo", font=font(24), fill=GOLD)
    verbs = ["status", "stand", "balance", "walk", "damp"]
    for k, v in enumerate(verbs):
        ry = py + 90 + k * 70
        p = min(1.0, (t * 3 + k * 0.2) % 1.0)
        if p > 0.3:
            d.text((px + 40, ry), f"→ {v}", font=font(22), fill=NEON if v != "balance" else GOLD)
    # Right panel: kabban evidence
    kx, ky = 1000, 250
    d.rounded_rectangle([kx, ky, kx + 780, ky + 500], radius=12, fill=(15, 23, 42), outline=GLOW, width=2)
    d.text((kx + 30, ky + 30), "kabban board", font=font(24), fill=GOLD)
    for k, task in enumerate(TASKS):
        ry = ky + 100 + k * 120
        d.text((kx + 40, ry), f"{task['id']} | {task['intent']} | {task['status']}", font=font(18), fill=INK)
        d.text((kx + 40, ry + 30), f"evidence={task['evidence']} · menlo:execute", font=font(14), fill=NEON)
    footer(d)
    return finish(img, ov)


def scene_bridge(i, total):
    """HTTP bridge on :8901 — real state + log."""
    t = i / FPS
    img, ov, d = base(t)
    title(d, "menlo bridge :8901", "stdlib HTTP server · fake edge firmware · /state /verb /log")
    # State panel
    px, py = 100, 250
    d.rounded_rectangle([px, py, px + 700, py + 400], radius=12, fill=(15, 23, 42), outline=GLOW, width=2)
    d.text((px + 30, py + 30), "bridge state", font=font(24), fill=GOLD)
    rows = [
        ("mode", f"{STATE['mode']} (DAMP)"),
        ("armed", str(STATE["armed"])),
        ("joints", str(STATE["joints"])),
        ("commands", str(STATE["commands_received"])),
        ("frames", str(STATE["state_frames"])),
        ("clock", f"{STATE['clock']}s"),
    ]
    for k, (label, val) in enumerate(rows):
        ry = py + 90 + k * 50
        d.text((px + 30, ry), label, font=font(20), fill=INK)
        d.text((px + 250, ry), val, font=font(20), fill=GOLD)
    # Log panel
    lx, ly = 850, 250
    d.rounded_rectangle([lx, ly, lx + 950, ly + 400], radius=12, fill=(15, 23, 42), outline=GLOW, width=2)
    d.text((lx + 30, ly + 30), "verb log", font=font(24), fill=GOLD)
    for k, entry in enumerate(LOG):
        ry = ly + 90 + k * 100
        ok = entry.get("ok", False)
        col = NEON if ok else GOLD
        d.text((lx + 30, ry), f"→ {entry['verb']}", font=font(22), fill=col)
        if ok:
            d.text((lx + 30, ry + 30), f"clock {entry['clock']}s · mode={entry['mode']} armed={entry['armed']}", font=font(14), fill=DIM)
        else:
            d.text((lx + 30, ry + 30), entry.get("error", "error"), font=font(14), fill=col)
    footer(d)
    return finish(img, ov)


def scene_kabban(i, total):
    """Kabban board + events — traceable handoff."""
    t = i / FPS
    img, ov, d = base(t)
    title(d, "kabban board", "offline-first task board · dispatch cap = 1 · dormant reroute · menlo:execute events")
    # Board panel
    px, py = 100, 250
    d.rounded_rectangle([px, py, px + 900, py + 500], radius=12, fill=(15, 23, 42), outline=GLOW, width=2)
    d.text((px + 30, py + 30), "board", font=font(24), fill=GOLD)
    d.text((px + 30, py + 80), f"{len(TASKS)} menlo tasks · all done · evidence recorded", font=font(18), fill=INK)
    for k, task in enumerate(TASKS):
        ry = py + 150 + k * 120
        d.text((px + 40, ry), f"✓ {task['intent']}", font=font(22), fill=NEON)
        d.text((px + 40, ry + 30), f"{task['id']} · {task['status']} · evidence={task['evidence']}", font=font(14), fill=DIM)
    # Events panel
    ex, ey = 1050, 250
    d.rounded_rectangle([ex, ey, ex + 800, ey + 500], radius=12, fill=(15, 23, 42), outline=GLOW, width=2)
    d.text((ex + 30, ey + 30), "events", font=font(24), fill=GOLD)
    d.text((ex + 30, ey + 80), "menlo:execute", font=font(22), fill=NEON)
    d.text((ex + 30, ey + 120), "actor: localagent", font=font(16), fill=INK)
    d.text((ex + 30, ey + 160), "hash-chained · QR = THE CHIP", font=font(14), fill=DIM)
    footer(d)
    return finish(img, ov)


def scene_dashboard(i, total):
    """Live dashboard panel — state grid + verb buttons."""
    t = i / FPS
    img, ov, d = base(t)
    title(d, "live dashboard", "custom_apps/local_agent.html — 1s polling · verb buttons · verb log")
    # State grid
    px, py = 100, 250
    d.rounded_rectangle([px, py, px + 700, py + 400], radius=12, fill=(15, 23, 42), outline=GLOW, width=2)
    d.text((px + 30, py + 30), "menlo state", font=font(24), fill=GOLD)
    grid = [
        ("mode", str(STATE["mode"])), ("armed", str(STATE["armed"])),
        ("joints", str(STATE["joints"])), ("cmds", str(STATE["commands_received"])),
        ("frames", str(STATE["state_frames"])), ("clock", f"{STATE['clock']}s"),
    ]
    for k, (label, val) in enumerate(grid):
        col = k % 3
        row = k // 3
        gx = px + 30 + col * 220
        gy = py + 100 + row * 100
        d.text((gx, gy), label, font=font(14), fill=DIM)
        d.text((gx, gy + 25), val, font=font(22), fill=GOLD)
    # Verb buttons
    bx, by = 850, 250
    d.rounded_rectangle([bx, by, bx + 950, by + 400], radius=12, fill=(15, 23, 42), outline=GLOW, width=2)
    d.text((bx + 30, by + 30), "verb buttons", font=font(24), fill=GOLD)
    verbs = ["stand", "balance", "walk", "damp"]
    for k, v in enumerate(verbs):
        p = min(1.0, (t * 2 + k * 0.25) % 1.0)
        if p > 0.2:
            col = NEON if v != "balance" else GOLD
            d.rounded_rectangle([bx + 40 + k * 220, by + 100, bx + 200 + k * 220, by + 160], radius=8, fill=col + (255,))
            d.text((bx + 120 + k * 220, by + 130), v, font=font(18), fill=VOID, anchor="mm")
    footer(d)
    return finish(img, ov)


def scene_mesh(i, total):
    """Full unified #ioa mesh — hermes hub + local_agent + menlo bridge + robot."""
    t = i / FPS
    img, ov, d = base(t)
    title(d, "#ioa unified", "hermes hub → bridge :8901 → robot · local_agent → kabban board → dashboard")
    cx, cy = WIDTH / 2, HEIGHT / 2
    # Hermes center
    d.ellipse([cx - 34, cy - 34, cx + 34, cy + 34], fill=GLOW + (255,))
    d.text((cx, cy), "hermes", font=font(14), fill=VOID, anchor="mm")
    # Bridge node
    bx, by = cx + 300, cy - 100
    d.line([(cx, cy), (bx, by)], fill=GOLD + (120,), width=3)
    d.ellipse([bx - 24, by - 24, bx + 24, by + 24], fill=NEON + (255,))
    d.text((bx, by + 34), "bridge :8901", font=font(14), fill=INK, anchor="mm")
    # Robot node
    rx, ry = bx + 300, by
    d.line([(bx, by), (rx, ry)], fill=NEON + (120,), width=3)
    d.ellipse([rx - 30, ry - 30, rx + 30, ry + 30], fill=GLOW + (255,))
    d.text((rx, ry), "ROBOT", font=font(16), fill=VOID, anchor="mm")
    # local_agent node
    lx, ly = cx - 300, cy - 100
    d.line([(cx, cy), (lx, ly)], fill=GOLD + (120,), width=3)
    d.ellipse([lx - 24, ly - 24, lx + 24, ly + 24], fill=GOLD + (255,))
    d.text((lx, ly + 34), "local_agent", font=font(14), fill=INK, anchor="mm")
    # kabban node
    kx, ky = cx - 300, cy + 150
    d.line([(lx, ly), (kx, ky)], fill=DIM + (80,), width=2)
    d.ellipse([kx - 20, ky - 20, kx + 20, ky + 20], fill=NEON + (200,))
    d.text((kx, ky + 30), "kabban", font=font(12), fill=DIM, anchor="mm")
    # dashboard node
    dx, dy = cx + 300, cy + 150
    d.line([(cx, cy), (dx, dy)], fill=DIM + (80,), width=2)
    d.ellipse([dx - 20, dy - 20, dx + 20, dy + 20], fill=GOLD + (200,))
    d.text((dx, dy + 30), "dashboard", font=font(12), fill=DIM, anchor="mm")
    # Packet flow
    ph = (t * 0.8) % 1.0
    px = cx + (bx - cx) * ph
    py = cy + (by - cy) * ph
    d.ellipse([px - 6, py - 6, px + 6, py + 6], fill=NEON + (255,))
    footer(d)
    return finish(img, ov)


SCENES = [
    ("cli", scene_cli, 150),
    ("bridge", scene_bridge, 150),
    ("kabban", scene_kabban, 150),
    ("dashboard", scene_dashboard, 150),
    ("mesh", scene_mesh, 180),
]


def build():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    tmp = OUT.parent / "_menlo_unified_tmp"
    tmp.mkdir(parents=True, exist_ok=True)
    n = 0
    for _name, fn, count in SCENES:
        for i in range(count):
            fn(i, count).save(tmp / ("mu{:04d}.png".format(n)))
            n += 1
    subprocess.run([
        "ffmpeg", "-y", "-v", "error", "-f", "image2", "-r", str(FPS),
        "-i", str(tmp / "mu%04d.png"),
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(OUT),
    ], check=True)
    shutil.rmtree(tmp, ignore_errors=True)
    return {"success": True, "output": str(OUT), "frames": n, "duration": n / FPS}


if __name__ == "__main__":
    print(build())
