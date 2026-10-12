"""
#startabusiness — four-media campaign
AE palette (from aeaedotcom index.html + ae-theme.yaml):
  void #020617 · gold #f5c842 · gold-dim #b58a1e · gold-glow rgba(253,185,39,.32)
  neon #10b981 · ink #e5e7eb

Frames: PIL RGBA → ffmpeg H.264.
Durations: 01 hero · 02 weave · 03 close · 04 qr
"""

from PIL import Image, ImageDraw, ImageFont
import subprocess, math, os

VOID = (2, 6, 23, 255)
GOLD = (245, 200, 66, 255)
GOLD_DIM = (181, 138, 18, 255)
GOLD_GLOW = (253, 185, 39, 96)
NEON = (16, 185, 129, 255)
INK = (229, 231, 235, 255)
OUT = "/c/Users/yaelm/vscode/aeaedotcom/custom_apps/startabusiness"

W, H = 1280, 720
FPS = 30
D = {
    "hero": 10,
    "weave": 12,
    "close": 14,
    "qr": 10,
}
TOTAL = sum(D.values())
FONT = "/c/Users/yaelm/AppData/Local/hermes/tools/fonts/Inter-Bold.ttf"
FONT_L = "/c/Users/yaelm/AppData/Local/hermes/tools/fonts/Inter-Regular.ttf"


def font(sz):
    for f in (FONT, FONT_L):
        try:
            return ImageFont.truetype(f, sz)
        except Exception:
            continue
    return ImageFont.load_default()


def elide(s, fnt, max_w):
    if fnt.getlength(s) <= max_w:
        return s
    for i in range(len(s), 0, -1):
        if fnt.getlength(s[:i]) <= max_w:
            return s[:i]
    return s[:10]


def draw_frame(t, kind):
    """One RGBA frame at global time t (0..TOTAL-1)."""
    img = Image.new("RGBA", (W, H), VOID)
    d = ImageDraw.Draw(img)

    # ── gold wave / scan background ──
    for i in range(0, W + H, 20):
        s = max(0, min(t, TOTAL - 1))
        yy = int(H * (0.5 + 0.25 * math.sin(i * 0.005 + s * 0.02)))
        d.line([(i, yy), (i + H, yy - H)], fill=GOLD_DIM if s % 2 == 0 else GOLD, width=2)

    ty = 0
    if kind == "hero":
        ty = H // 2 - 140
        d.text((W // 2, ty), "#STARTABUSINESS", font=font(72), fill=NEON, anchor="mm")
        ty += 90
        d.text((W // 2, ty), "ONE PERSON COMPANY", font=font(36), fill=GOLD, anchor="mm")
        ty += 56
        d.text((W // 2, ty), "one person + agents  →  operating business", font=font(26), fill=INK, anchor="mm")
        ty += 40
        d.text((W // 2, ty), "sovereign bootstrap + doola daollc + #250", font=font(20), fill=GOLD_DIM, anchor="mm")
    elif kind == "weave":
        d.text((W // 2, 90), "#STARTABUSINESS", font=font(56), fill=NEON, anchor="mm")
        rows = [
            ("#07 · ECONOMICS · ORGANIZATION · VALUE", 40, GOLD),
            ("#08 · ONE PERSON COMPANY", 34, GOLD),
            ("    BUILD", 30, NEON),
            ("    ENTREPRISE · one person + agents → operating business", 24, INK),
            ("domain: ONE PERSON COMPANY", 22, GOLD_DIM),
        ]
        for txt, sz, col in rows:
            fnt_s = font(sz)
            max_w = W - 240
            txt = elide(txt, fnt_s, max_w)
            d.text((W // 2, ty), txt, font=fnt_s, fill=col, anchor="mm")
            ty += sz + 22
    elif kind == "close":
        d.text((W // 2, H // 2 - 60), "#STARTABUSINESS", font=font(72), fill=NEON, anchor="mm")
        ty = H // 2 + 20
        d.text((W // 2, ty), "SOVEREIGN", font=font(40), fill=GOLD, anchor="mm")
        ty += 48
        d.text((W // 2, ty), "BOOTSTRAP · FOREIGN AGENTS · OPERATING BUSINESS", font=font(24), fill=INK, anchor="mm")
        ty += 40
        d.text((W // 2, ty), "#250 · #OSW · CUDA blueprint", font=font(20), fill=GOLD_DIM, anchor="mm")
    elif kind == "qr":
        d.text((W // 2, 70), "#STARTABUSINESS", font=font(56), fill=NEON, anchor="mm")
        ty = 150
        # QR-ish grid
        qw, qh = 320, 320
        gx, gy = W // 2 - qw // 2, ty - 20
        for r in range(0, qh, 28):
            for c in range(0, qw, 28):
                if (r // 28) % 2 == 0 and (c // 28) % 2 == 1:
                    d.rectangle([gx + c, gy + r, gx + c + 28, gy + r + 28], fill=GOLD)
        tx = gx + qw + 40
        d.text((tx, ty - 10), "ENTERPRISE", font=font(34), fill=GOLD, anchor="lm")
        d.text((tx, ty + 44), "· one person + agents", font=font(26), fill=INK, anchor="lm")
        d.text((tx, ty + 90), "→ operating business", font=font(26), fill=INK, anchor="lm")
        d.text((tx, gy + qh + 40), "qr = SHA-256(id, verdict, evidence, uncertainty, trust)", font=font(18), fill=GOLD_DIM, anchor="lm")

    return img


def main():
    os.makedirs(OUT, exist_ok=True)
    # dodge: erase overlapping leftover frames from earlier runs
    for f in os.listdir(OUT):
        if f.endswith(".png"):
            os.remove(os.path.join(OUT, f))

    frames = []
    for kind, dur in D.items():
        for i in range(dur * FPS):
            t = i / FPS
            idx = i % FPS
            img = draw_frame(t, kind)
            png = os.path.join(OUT, f"{kind}_{idx:04d}.png").replace("\\", "/")
            img.save(png)
            if idx == 0:
                frames.append((kind, t, png))

    # 1) render all frames
    for kind, dur in D.items():
        for i in range(dur * FPS):
            t = i / FPS
            idx = i % FPS
            img = draw_frame(t, kind)
            png = os.path.join(OUT, f"{kind}_{idx:04d}.png").replace("\\", "/")
            img.save(png)

    # 2) encode each clip to H.264 (temp frames kept as fallback)
    for kind in D:
        fs = [os.path.join(OUT, f"{kind}_{i:04d}.png").replace("\\", "/")
              for i in range(D[kind] * FPS)]
        concat = os.path.join(OUT, f"{kind}.txt").replace("\\", "/")
        with open(concat, "w") as f:
            f.write("\n".join(f"file '{p}'" for p in fs))
        out = os.path.join(OUT, kind + ".mp4")
        subprocess.run(
            ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat,
             "-vf", "scale=1280:720:flags=lanczos,format=yuv420p",
             "-r", str(FPS), "-c:v", "libx264", "-pix_fmt", "yuv420p",
             "-preset", "fast", "-crf", "20", "-shortest", out],
            check=True, capture_output=True, text=True,
        )

    # 3) stitch the four clips into one campaign
    clips = [os.path.join(OUT, k + ".mp4") for k in D]
    concat_ts = os.path.join(OUT, "campaign.txt").replace("\\", "/")
    with open(concat_ts, "w") as f:
        for k in D:
            f.write(f"file '{clips[list(D).index(k)]}'\n")
    campaign = os.path.join(OUT, "campaign.mp4").replace("\\", "/")
    subprocess.run(
        ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_ts,
         "-c:v", "libx264", "-pix_fmt", "yuv420p", "-shortest", campaign],
        check=True, capture_output=True, text=True,
    )
    os.remove(concat_ts)

    print("campaign:", campaign)
    for k in D:
        p = os.path.join(OUT, k + ".mp4")
        r = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                            "format=duration", "-of", "default=noprint_wrappers=1",
                            p], capture_output=True, text=True)
        dur = r.stdout.strip().split("=")[-1]
        print(f"{k:8s} {dur}s")


if __name__ == "__main__":
    main()
