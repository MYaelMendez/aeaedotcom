"""menlo_command_demo.py — Command and control the Menlo robot.

Scenes: factory UI with face → HTTP verb sequence → face reactions →
full C2 loop. Gold-on-void, real bridge data captured 2026-10-18.
"""
import json
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
RED = (239, 68, 68)

WIDTH, HEIGHT = 1920, 1080
FPS = 30
OUT = Path("static/renders/constellation/menlo_command.mp4")

# Real bridge data (probed + driven 2026-10-18)
STATE_DAMP = {"mode": 0, "armed": False, "joints": 25, "commands_received": 2,
              "state_frames": 109, "velocities": [], "modes": ["stand", "damp"], "clock": 1000.54}
STATE_STAND = {"mode": 1, "armed": True, "joints": 25, "commands_received": 1,
               "state_frames": 105, "velocities": [], "modes": ["stand"], "clock": 1000.52}
COMMAND_LOG = [
    {"verb": "stand", "clock": 1000.52, "outcome": "Applied", "mode": 1, "armed": True, "ok": True},
    {"verb": "damp", "clock": 1000.54, "outcome": "Applied", "mode": 0, "armed": False, "ok": True},
]
VERBS = ["stand", "balance", "walk", "damp"]


def font(size, bold=True):
    for p in ("C:/Windows/Fonts/verdana.ttf", "C:/Windows/Fonts/arial.ttf",
              "C:/Windows/Fonts/calibri.ttf"):
        if Path(p).exists():
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()


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


def footer(d, text="#ioa · menlo · command and control · sovereign mesh"):
    d.text((WIDTH / 2, HEIGHT - 52), text, font=font(20), fill=DIM, anchor="mm")


def draw_face(d, cx, cy, mode, armed, flash=False, scale=1.0):
    """Draw the robot face SVG equivalent with Pillow primitives."""
    s = scale
    # Antenna
    ax, ay = cx, cy - 140 * s
    d.line([(ax, ay - 20 * s), (ax, ay)], fill=GOLD + (120,) if not flash else NEON + (255,), width=max(1, int(2 * s)))
    d.ellipse([ax - 8 * s, ay - 28 * s, ax + 8 * s, ay - 12 * s],
              fill=GOLD + (255,) if not flash else NEON + (255,))
    # Head
    hx, hy = cx - 120 * s, cy - 120 * s
    hw, hh = 240 * s, 200 * s
    d.rounded_rectangle([hx, hy, hx + hw, hy + hh], radius=int(20 * s),
                        fill=(15, 23, 42), outline=GLOW + (255,), width=max(1, int(2 * s)))
    # Eyes
    eye_color = (51, 65, 85) if mode == 0 else (GOLD if not armed else NEON)
    if flash:
        eye_color = NEON
    ey = cy - 40 * s
    for ex in [cx - 60 * s, cx + 20 * s]:
        if mode == 0 and not flash:
            d.rounded_rectangle([ex, ey, ex + 40 * s, ey + 20 * s], radius=int(6 * s),
                                fill=eye_color + (255,))
        else:
            glow_r = 12 * s if flash else (8 * s if armed else 6 * s)
            d.ellipse([ex - glow_r, ey - glow_r, ex + 40 * s + glow_r, ey + 20 * s + glow_r],
                      fill=eye_color + (60,))
            d.rounded_rectangle([ex, ey, ex + 40 * s, ey + 20 * s], radius=int(6 * s),
                                fill=eye_color + (255,))
    # Mouth
    my = cy + 50 * s
    mouth_opacity = 0.3 if mode == 0 else (0.8 if not flash else 1.0)
    mc = GOLD if not flash else NEON
    d.rounded_rectangle([cx - 50 * s, my, cx + 50 * s, my + 10 * s], radius=int(4 * s),
                        fill=mc + (int(255 * mouth_opacity),))
    return cy + 120 * s


def scene_factory(i, total):
    """Factory UI with the robot face panel."""
    t = i / FPS
    img, ov, d = base()
    title(d, "æ electron factory", "menlo bridge panel · robot face · live telemetry")
    # Panel
    px, py = 100, 220
    d.rounded_rectangle([px, py, px + 500, py + 620], radius=12, fill=(15, 23, 42), outline=GLOW, width=2)
    d.text((px + 30, py + 24), "MENLO BRIDGE", font=font(20), fill=GOLD)
    # Status dot
    p = (t * 2) % 1.0
    online = p < 0.8
    status_col = NEON if online else RED
    d.ellipse([px + 30, py + 70, px + 42, py + 82], fill=status_col + (255,))
    d.text((px + 52, py + 76), "ONLINE" if online else "OFFLINE", font=font(16), fill=status_col)
    # Face
    face_cx = px + 250
    face_cy = py + 280
    mode = STATE_DAMP["mode"] if int(t * 2) % 2 == 0 else STATE_STAND["mode"]
    armed = STATE_STAND["armed"] if mode == 1 else False
    flash = (t * 3) % 1.0 > 0.9
    draw_face(d, face_cx, face_cy, mode, armed, flash, scale=0.7)
    # State grid
    gy = py + 420
    grid = [("mode", str(STATE_DAMP["mode"])), ("armed", str(STATE_DAMP["armed"])),
            ("joints", str(STATE_DAMP["joints"])), ("cmds", str(STATE_DAMP["commands_received"])),
            ("frames", str(STATE_DAMP["state_frames"])), ("clock", f"{STATE_DAMP['clock']}s")]
    for k, (label, val) in enumerate(grid):
        col = k % 3
        row = k // 3
        gx = px + 30 + col * 155
        d.text((gx, gy + row * 55), label, font=font(12), fill=DIM)
        d.text((gx, gy + row * 55 + 20), val, font=font(18), fill=GOLD)
    # Right: verb buttons
    bx, by = 680, 220
    d.rounded_rectangle([bx, by, bx + 1140, by + 620], radius=12, fill=(15, 23, 42), outline=GLOW, width=2)
    d.text((bx + 30, by + 24), "command and control", font=font(20), fill=GOLD)
    d.text((bx + 30, by + 70), "POST /verb → bridge :8901 → SDK → robot", font=font(14), fill=DIM)
    for k, v in enumerate(VERBS):
        p2 = min(1.0, (t * 1.5 + k * 0.2) % 1.0)
        if p2 > 0.2:
            btn_x = bx + 40 + k * 270
            btn_y = by + 130
            col = NEON if v != "balance" else GOLD
            d.rounded_rectangle([btn_x, btn_y, btn_x + 240, btn_y + 70], radius=8, fill=col + (255,))
            d.text((btn_x + 120, btn_y + 35), v, font=font(22), fill=VOID, anchor="mm")
    footer(d)
    return finish(img, ov)


def scene_sequence(i, total):
    """HTTP verb sequence — real commands sent to the bridge."""
    t = i / FPS
    img, ov, d = base()
    title(d, "command sequence", "curl -X POST http://127.0.0.1:8901/verb → SDK fake edge → robot state machine")
    # Terminal panel
    px, py = 100, 250
    d.rounded_rectangle([px, py, px + 900, py + 500], radius=12, fill=(15, 23, 42), outline=GLOW, width=2)
    d.text((px + 30, py + 30), "$ command", font=font(24), fill=GOLD)
    cmds = [
        ("stand", "curl -X POST .../verb -d '{\"name\":\"stand\"}'", "Applied · mode=1 armed=true"),
        ("damp", "curl -X POST .../verb -d '{\"name\":\"damp\"}'", "Applied · mode=0 armed=false"),
    ]
    for k, (verb, cmd, result) in enumerate(cmds):
        ry = py + 100 + k * 180
        p = min(1.0, (t * 2 + k * 0.3) % 1.0)
        if p > 0.2:
            d.text((px + 40, ry), f"→ {verb}", font=font(28), fill=NEON)
            d.text((px + 40, ry + 45), cmd, font=font(14), fill=DIM)
            d.text((px + 40, ry + 75), f"✓ {result}", font=font(18), fill=GOLD)
    # Right: state transition
    sx, sy = 1050, 250
    d.rounded_rectangle([sx, sy, sx + 800, sy + 500], radius=12, fill=(15, 23, 42), outline=GLOW, width=2)
    d.text((sx + 30, sy + 30), "state machine", font=font(24), fill=GOLD)
    # DAMP box
    p1 = min(1.0, t * 2 % 1.0)
    if p1 > 0.2:
        d.rounded_rectangle([sx + 60, sy + 100, sx + 340, sy + 200], radius=8, fill=(51, 65, 85, 80), outline=DIM, width=2)
        d.text((sx + 200, sy + 140), "DAMP (0)", font=font(20), fill=INK, anchor="mm")
        d.text((sx + 200, sy + 170), "safe · disarmed", font=font(12), fill=DIM, anchor="mm")
    # Arrow
    p2 = min(1.0, (t * 2 - 0.3) % 1.0)
    if p2 > 0.2:
        d.line([(sx + 350, sy + 150), (sx + 450, sy + 150)], fill=GOLD + (255,), width=3)
        d.polygon([(sx + 450, sy + 140), (sx + 470, sy + 150), (sx + 450, sy + 160)], fill=GOLD + (255,))
    # STAND box
    p3 = min(1.0, (t * 2 - 0.5) % 1.0)
    if p3 > 0.2:
        d.rounded_rectangle([sx + 480, sy + 100, sx + 760, sy + 200], radius=8, fill=NEON + (60,), outline=NEON, width=2)
        d.text((sx + 620, sy + 140), "STAND (1)", font=font(20), fill=NEON, anchor="mm")
        d.text((sx + 620, sy + 170), "armed · ready", font=font(12), fill=INK, anchor="mm")
    # Clock
    d.text((sx + 30, sy + 280), f"clock: {STATE_STAND['clock']}s → {STATE_DAMP['clock']}s", font=font(16), fill=INK)
    d.text((sx + 30, sy + 320), f"commands: {STATE_STAND['commands_received']} → {STATE_DAMP['commands_received']}", font=font(16), fill=INK)
    d.text((sx + 30, sy + 360), f"state_frames: {STATE_STAND['state_frames']} → {STATE_DAMP['state_frames']}", font=font(16), fill=INK)
    footer(d)
    return finish(img, ov)


def scene_face_react(i, total):
    """Face reactions — flash on click, mode transitions."""
    t = i / FPS
    img, ov, d = base()
    title(d, "face reaction", "verb click → 300ms neon flash · mode → eye color · armed → glow")
    # Large face center
    cx, cy = WIDTH // 2, HEIGHT // 2 + 40
    # Cycle through states
    cycle = int(t * 1.5) % 4
    if cycle == 0:
        mode, armed, flash = 0, False, False
        label = "DAMP — dark slate eyes"
    elif cycle == 1:
        mode, armed, flash = 1, True, False
        label = "STAND — neon eyes + glow"
    elif cycle == 2:
        mode, armed, flash = 0, False, True
        label = "FLASH — verb click reaction"
    else:
        mode, armed, flash = 1, False, False
        label = "MOVE — gold eyes"
    draw_face(d, cx, cy, mode, armed, flash, scale=1.8)
    # Label
    d.text((cx, cy + 260), label, font=font(28), fill=GOLD if not flash else NEON, anchor="mm")
    # Legend
    ly = cy + 340
    d.text((cx - 300, ly), "mode 0 → slate eyes", font=font(16), fill=INK)
    d.text((cx + 100, ly), "mode 1/2 → gold eyes", font=font(16), fill=GOLD)
    d.text((cx - 300, ly + 40), "armed → neon + glow", font=font(16), fill=NEON)
    d.text((cx + 100, ly + 40), "flash → neon burst", font=font(16), fill=NEON)
    footer(d)
    return finish(img, ov)


def scene_c2_loop(i, total):
    """Full command-and-control loop — state + buttons + log + face."""
    t = i / FPS
    img, ov, d = base()
    title(d, "command and control loop", "dashboard → verb button → bridge :8901 → SDK → state update → face react → log")
    # State grid (left)
    px, py = 80, 230
    d.rounded_rectangle([px, py, px + 420, py + 350], radius=12, fill=(15, 23, 42), outline=GLOW, width=2)
    d.text((px + 24, py + 20), "state", font=font(18), fill=GOLD)
    grid = [("mode", str(STATE_DAMP["mode"])), ("armed", str(STATE_DAMP["armed"])),
            ("joints", str(STATE_DAMP["joints"])), ("cmds", str(STATE_DAMP["commands_received"])),
            ("frames", str(STATE_DAMP["state_frames"])), ("clock", f"{STATE_DAMP['clock']}s")]
    for k, (label, val) in enumerate(grid):
        col = k % 3
        row = k // 3
        gx = px + 24 + col * 130
        gy = py + 70 + row * 60
        d.text((gx, gy), label, font=font(11), fill=DIM)
        d.text((gx, gy + 18), val, font=font(16), fill=GOLD)
    # Face (center-left)
    face_cx, face_cy = 700, 420
    mode = STATE_STAND["mode"] if int(t * 1.2) % 2 == 0 else STATE_DAMP["mode"]
    armed = True if mode == 1 else False
    flash = (t * 2.5) % 1.0 > 0.92
    draw_face(d, face_cx, face_cy, mode, armed, flash, scale=0.9)
    # Verb buttons (right)
    bx, by = 950, 230
    d.rounded_rectangle([bx, by, bx + 400, by + 350], radius=12, fill=(15, 23, 42), outline=GLOW, width=2)
    d.text((bx + 24, by + 20), "verbs", font=font(18), fill=GOLD)
    for k, v in enumerate(VERBS):
        btn_y = by + 70 + k * 70
        col = NEON if v != "balance" else GOLD
        d.rounded_rectangle([bx + 30, btn_y, bx + 370, btn_y + 55], radius=8, fill=col + (255,))
        d.text((bx + 200, btn_y + 27), v, font=font(18), fill=VOID, anchor="mm")
    # Log (far right)
    lx, ly = 1420, 230
    d.rounded_rectangle([lx, ly, lx + 440, ly + 350], radius=12, fill=(15, 23, 42), outline=GLOW, width=2)
    d.text((lx + 24, ly + 20), "verb log", font=font(18), fill=GOLD)
    for k, entry in enumerate(COMMAND_LOG):
        ry = ly + 80 + k * 100
        d.text((lx + 30, ry), f"→ {entry['verb']}", font=font(20), fill=NEON)
        d.text((lx + 30, ry + 35), f"{entry['outcome']} · mode={entry['mode']} armed={entry['armed']}", font=font(13), fill=DIM)
        d.text((lx + 30, ry + 60), f"clock {entry['clock']}s", font=font(12), fill=DIM)
    # Flow arrow
    d.line([(bx + 400, by + 175), (lx, by + 175)], fill=GOLD + (120,), width=2)
    d.polygon([(lx, by + 165), (lx + 20, by + 175), (lx, by + 185)], fill=GOLD + (120,))
    footer(d)
    return finish(img, ov)


def scene_summary(i, total):
    """Summary — what was commanded, what happened."""
    t = i / FPS
    img, ov, d = base()
    title(d, "command and control — summary", "real bridge · real SDK · real state transitions")
    # Left: commands issued
    px, py = 100, 250
    d.rounded_rectangle([px, py, px + 800, py + 500], radius=12, fill=(15, 23, 42), outline=GLOW, width=2)
    d.text((px + 30, py + 30), "commands issued", font=font(24), fill=GOLD)
    for k, entry in enumerate(COMMAND_LOG):
        ry = py + 100 + k * 160
        d.text((px + 40, ry), f"✓ {entry['verb'].upper()}", font=font(28), fill=NEON)
        d.text((px + 40, ry + 50), f"bridge :8901 → SDK → robot", font=font(16), fill=INK)
        d.text((px + 40, ry + 85), f"outcome: {entry['outcome']}", font=font(18), fill=GOLD)
        d.text((px + 40, ry + 120), f"mode={entry['mode']} armed={entry['armed']} clock={entry['clock']}s", font=font(14), fill=DIM)
    # Right: what changed
    sx, sy = 1000, 250
    d.rounded_rectangle([sx, sy, sx + 850, sy + 500], radius=12, fill=(15, 23, 42), outline=GLOW, width=2)
    d.text((sx + 30, sy + 30), "robot state", font=font(24), fill=GOLD)
    rows = [
        ("mode", "0 (DAMP)", "1 (STAND)", "0 (DAMP)"),
        ("armed", "false", "true", "false"),
        ("commands", "0", "1", "2"),
        ("frames", "1", "105", "109"),
        ("clock", "1000.0s", "1000.52s", "1000.54s"),
    ]
    for k, (label, before, after, final) in enumerate(rows):
        ry = sy + 100 + k * 80
        d.text((sx + 40, ry), label, font=font(18), fill=INK)
        d.text((sx + 250, ry), before, font=font(18), fill=DIM)
        d.text((sx + 450, ry), after, font=font(18), fill=GOLD)
        d.text((sx + 650, ry), final, font=font(18), fill=NEON)
    footer(d)
    return finish(img, ov)


SCENES = [
    ("factory", scene_factory, 150),
    ("sequence", scene_sequence, 150),
    ("face_react", scene_face_react, 150),
    ("c2_loop", scene_c2_loop, 150),
    ("summary", scene_summary, 120),
]


def build():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    tmp = OUT.parent / "_menlo_command_tmp"
    tmp.mkdir(parents=True, exist_ok=True)
    n = 0
    for _name, fn, count in SCENES:
        for i in range(count):
            fn(i, count).save(tmp / ("mc{:04d}.png".format(n)))
            n += 1
    subprocess.run([
        "ffmpeg", "-y", "-v", "error", "-f", "image2", "-r", str(FPS),
        "-i", str(tmp / "mc%04d.png"),
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(OUT),
    ], check=True)
    shutil.rmtree(tmp, ignore_errors=True)
    return {"success": True, "output": str(OUT), "frames": n, "duration": n / FPS}


if __name__ == "__main__":
    print(build())
