#!/usr/bin/env python3
"""#startabusiness four-media campaign generator (Pillow frame + ffmpeg H.264 encode).

Palette (ae-theme for aeaedotcom / æææ.com personalization):
  gold      #f5c842  / #b58a12  / rgba(253,185,39,.32)
  vault     #020617
  neon      #10b981
"""
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

# ---------------- configuration ----------------
W, H = 1280, 720
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)))
FONT = "consola"  # Windows Consolas (mono headline); falls back to default
VIDEO_FPS = 30
VIDEO_CROP = 1280  # seconds

def devnull():
    import tempfile
    return tempfile.NamedTemporaryFile(prefix="startabusiness_", suffix=".png", delete=False)

def find_font(name):
    candidates = [
        "C:/Windows/Fonts/consola.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/verdana.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    return None

def font_or_none(size):
    path = find_font("consolas")
    if path:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            pass
    return ImageFont.load_default()

def text_w(draw, s, fnt):
    bbox = draw.textbbox((0, 0), s, font=fnt)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]

def draw_gold_gradient(disc, cx, top, bottom, r=300):
    for i in range(r):
        t = i / r
        c = (
            int(245 + (255 - 245) * t),
            int(200 + (234 - 200) * t),
            int(66 + (20 - 66) * t),
        )
        disc.ellipse([cx - 40, top + i - 20, cx + 40, top + i + 20], fill=c)

def gold_line(draw, y, x0, x1, w=3, alpha=.55):
    pass

def render_frame(frame, label):
    img = Image.new("RGB", (W, H), (2, 6, 23))
    d = ImageDraw.Draw(img)

    # vault ground
    d.rectangle([0, H - 12, W, H], fill=(8, 12, 30))

    # gold vault gradient disc
    cx = W // 2
    top = H // 2 - 180
    draw_gold_gradient(d, cx, top, H, r=320)

    # neon accent bar
    d.rectangle([0, top + 60, W, top + 64], fill=(16, 185, 129))

    # headline (mono)
    fnt_lg = font_or_none(56)
    fnt_md = font_or_none(28)
    fnt_sm = font_or_none(22)

    # title
    title = LABELS[label]
    tw, th = text_w(d, title, fnt_lg)
    d.text(((W - tw) / 2, 90), title, fill=(245, 200, 66), font=fnt_lg)

    # tagline
    tag = TAGS.get(label, "one person + agents -> operating business")
    tw2, th2 = text_w(d, tag, fnt_md)
    d.text(((W - tw2) / 2, 170), tag, fill=(240, 212, 135), font=fnt_md)

    # spacer
    y = 330

    # list
    items = ITEMS.get(label, [])
    for it in items:
        # bullet
        d.rectangle([20, y + 14, 24, y + 24], fill=(245, 200, 66))
        # text
        tw3, th3 = text_w(d, it, fnt_sm)
        d.text((56, y), it, fill=(229, 231, 245), font=fnt_sm)
        y += 40

    # footer
    d.text((16, H - 22), "ae-theme · #250 · #startabusiness", fill=(156, 163, 175), font=fnt_sm)

    return img

def write_frames(label, n):
    p = os.path.join(OUT, "temp_frames")
    os.makedirs(p, exist_ok=True)
    for i in range(n):
        img = render_frame(i, label)
        img.save(os.path.join(p, f"{label}_{i:04d}.png"))
    return p

def encode(label, frames_dir, out_path, fps=VIDEO_FPS):
    cmd = [
        "ffmpeg", "-y", "-loglevel", "error",
        "-f", "image2", "-r", str(fps),
        "-i", os.path.join(frames_dir, f"{label}_%04d.png"),
        "-frames:v", str(VIDEO_CROP * fps),
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "fast",
        out_path,
    ]
    subprocess.run(cmd, check=True)
    # cleanup frames
    for f in os.listdir(frames_dir):
        os.remove(os.path.join(frames_dir, f))
    os.rmdir(frames_dir)

def write_index():
    with open(os.path.join(OUT, "campaign.txt"), "w", encoding="utf-8") as f:
        f.write("file hero.mp4\r\n")
        f.write("file weave.mp4\r\n")
        f.write("file close.mp4\r\n")
        f.write("file qr.mp4\r\n")

def main():
    labels = sys.argv[1:] or ["hero", "weave", "close", "qr"]
    for label in labels:
        p = write_frames(label, 1380)
        o = os.path.join(OUT, f"{label}.mp4")
        encode(label, p, o)
        print(o)
    write_index()

if __name__ == "__main__":
    main()
