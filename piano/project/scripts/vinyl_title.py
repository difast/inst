"""Spinning vinyl record with the title on its label, laid over the dark top of a reel.

The record (grooves, sheen texture, a printed ring on the label) turns at 33 1/3 rpm;
the light highlight and the title stay still, so the name is always readable.

    python3 vinyl_title.py <in.mp4> <out.mp4> "The Black Star"
"""
import os
import subprocess
import sys
import tempfile

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONT = os.path.join(HERE, "..", "public", "fonts", "Cormorant.ttf")
D = 460  # disc diameter on the 1080x1920 frame
CX, CY = 540, 360  # disc centre, clear of the hands below
LABEL = 0.5  # label diameter / disc diameter
RPM = 100 / 3


def font(size, weight):
    f = ImageFont.truetype(FONT, size)
    try:
        f.set_variation_by_axes([weight])
    except Exception:
        pass
    return f


def disc():
    """The turning part: vinyl with grooves and uneven sheen, label with a printed ring."""
    y, x = np.mgrid[0:D, 0:D].astype(np.float32) - (D - 1) / 2
    r = np.hypot(x, y) / (D / 2)
    a = np.arctan2(y, x)
    rng = np.random.default_rng(7)
    grooves = 0.5 + 0.5 * np.sin(r * 420)
    tracks = np.ones_like(r)
    for gap in (0.52, 0.66, 0.8):  # quieter bands between tracks
        tracks -= 0.35 * np.exp(-((r - gap) / 0.006) ** 2)
    streak = np.zeros_like(r)
    for k in range(6):  # uneven sheen, makes the turning visible
        streak += rng.random() * np.cos((k + 2) * a + rng.random() * 6.28)
    v = 18 + 7 * grooves * tracks + 5 * streak * (r > LABEL / 1.9)
    rgb = np.stack([v * 1.05, v * 0.95, v * 0.9], -1)
    alpha = np.clip((1 - r) * D / 2, 0, 1)  # anti-aliased rim
    img = np.dstack([np.clip(rgb, 0, 255), alpha * 255]).astype(np.uint8)
    im = Image.fromarray(img, "RGBA")

    d = ImageDraw.Draw(im)
    lr = D * LABEL / 2
    c = (D - 1) / 2
    d.ellipse([c - lr, c - lr, c + lr, c + lr], fill=(226, 190, 136, 255))
    d.ellipse([c - lr + 8, c - lr + 8, c + lr - 8, c + lr - 8], outline=(150, 96, 44, 255), width=2)
    for k in range(48):  # printed tick ring near the label edge
        ang = 2 * np.pi * k / 48
        r0, r1 = lr - 16, lr - (24 if k % 4 == 0 else 20)
        d.line([(c + r0 * np.cos(ang), c + r0 * np.sin(ang)), (c + r1 * np.cos(ang), c + r1 * np.sin(ang))],
               fill=(150, 96, 44, 255), width=2)
    d.ellipse([c - 7, c - 7, c + 7, c + 7], fill=(10, 7, 5, 255))  # spindle hole
    return im


def still(title):
    """The still part: light reflection on the vinyl and the title on the label."""
    y, x = np.mgrid[0:D, 0:D].astype(np.float32) - (D - 1) / 2
    r = np.hypot(x, y) / (D / 2)
    a = np.arctan2(y, x)
    sheen = (np.exp(-((a + 2.2) / 0.32) ** 2) + np.exp(-((a - 0.94) / 0.32) ** 2)) * (r > LABEL / 1.9) * (r < 0.98)
    alpha = (sheen * 70).astype(np.uint8)
    im = Image.fromarray(np.dstack([np.full((D, D, 3), (255, 214, 160), np.uint8), alpha]), "RGBA")
    im = im.filter(ImageFilter.GaussianBlur(3))

    d = ImageDraw.Draw(im)
    c = (D - 1) / 2
    # title on one line above the spindle hole, a small star below it
    f = font(30, 600)
    while d.textlength(title, font=f) > D * LABEL * 0.72 and f.size > 16:
        f = font(f.size - 1, 600)
    box = d.textbbox((0, 0), title, font=f)
    tw, th = box[2] - box[0], box[3] - box[1]
    d.text((c - tw / 2 - box[0], c - 16 - th - box[1]), title, font=f, fill=(42, 22, 10, 255))
    star = [(c + (9 if k % 2 == 0 else 3.8) * np.sin(np.pi * k / 5),
             c + 26 - (9 if k % 2 == 0 else 3.8) * np.cos(np.pi * k / 5)) for k in range(10)]
    d.polygon(star, fill=(42, 22, 10, 255))
    return im


def main(src, out, title):
    tmp = tempfile.mkdtemp()
    disc_png, still_png, glow_png = (os.path.join(tmp, n) for n in ("disc.png", "still.png", "glow.png"))
    disc().save(disc_png)
    still(title).save(still_png)
    # warm glow behind the record so it separates from the black
    g = Image.new("RGBA", (D + 300, D + 300), (0, 0, 0, 0))
    ImageDraw.Draw(g).ellipse([150, 150, D + 150, D + 150], fill=(255, 150, 70, 60))
    g.filter(ImageFilter.GaussianBlur(70)).save(glow_png)

    w = 2 * np.pi * RPM / 60
    x0, y0 = CX - D // 2, CY - D // 2
    fc = (
        f"[1:v]format=rgba,fade=t=in:d=0.8:alpha=1[glow];"
        f"[2:v]format=rgba,rotate=a='{w:.4f}*t':c=none:ow={D}:oh={D},fade=t=in:d=0.8:alpha=1[disc];"
        f"[3:v]format=rgba,fade=t=in:d=0.8:alpha=1[still];"
        f"[0:v][glow]overlay={x0 - 150}:{y0 - 150}:shortest=1[a];"
        f"[a][disc]overlay={x0}:{y0}:shortest=1[b];"
        f"[b][still]overlay={x0}:{y0}:shortest=1[v]"
    )
    subprocess.run([
        "ffmpeg", "-v", "error", "-y", "-i", src,
        "-loop", "1", "-framerate", "30", "-i", glow_png,
        "-loop", "1", "-framerate", "30", "-i", disc_png,
        "-loop", "1", "-framerate", "30", "-i", still_png,
        "-filter_complex", fc, "-map", "[v]", "-map", "0:a",
        "-c:v", "libx264", "-crf", "20", "-preset", "slow", "-pix_fmt", "yuv420p",
        "-c:a", "copy", "-movflags", "+faststart", out], check=True)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "The Black Star")
