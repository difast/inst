"""Spinning vinyl record with the title on its label, plus hook and CTA, over a dark reel.

The record (grooves, sheen texture, a printed ring on the label) turns at 33 1/3 rpm;
the light highlight and the title stay still, so the name is always readable.
The hook line takes the record's place for the first seconds, then the record fades
in; at the end the record gives way to the call to action.

    python3 vinyl_title.py <in.mp4> <out.mp4> [--end SECONDS]
"""
import argparse
import os
import subprocess
import tempfile

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONT = os.path.join(HERE, "..", "public", "fonts", "Cormorant.ttf")
D = 460  # disc diameter on the 1080x1920 frame
CX, CY = 540, 360  # disc centre, clear of the hands below
LABEL = 0.5  # label diameter / disc diameter
RPM = 100 / 3
TITLE = "The Black Star"
HOOK = "Сыграй это тому,\nпо кому скучаешь"
CTA = ("Хочешь сыграть это для кого-то?", "Научись в Piano Lab · ссылка в профиле")
HOOK_END = 3.2  # the record appears after the hook
CTA_LEN = 4.0  # last seconds


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


def text_card(lines, path):
    """Centered lines (text, size, weight, colour) with a warm glow, on a transparent 1080x560 card."""
    w, h = 1080, 560
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    rows = []
    for text, size, weight, colour in lines:
        f = font(size, weight)
        box = d.textbbox((0, 0), text, font=f)
        rows.append((text, f, colour, box))
    gap = 18
    total = sum(b[3] - b[1] for *_, b in rows) + gap * (len(rows) - 1)
    y = (h - total) / 2
    for text, f, colour, box in rows:
        d.text(((w - (box[2] - box[0])) / 2 - box[0], y - box[1]), text, font=f, fill=colour)
        y += box[3] - box[1] + gap
    alpha = layer.split()[3]
    glow = Image.new("RGBA", (w, h), (255, 150, 60, 0))
    glow.putalpha(alpha.filter(ImageFilter.GaussianBlur(14)).point(lambda v: int(v * 0.55)))
    shadow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    shadow.putalpha(alpha.filter(ImageFilter.GaussianBlur(6)).point(lambda v: int(v * 0.9)))
    Image.alpha_composite(Image.alpha_composite(shadow, glow), layer).save(path)


def main(src, out, end=None):
    tmp = tempfile.mkdtemp()
    disc_png, still_png, glow_png, hook_png, cta_png = (
        os.path.join(tmp, n) for n in ("disc.png", "still.png", "glow.png", "hook.png", "cta.png"))
    disc().save(disc_png)
    still(TITLE).save(still_png)
    # warm glow behind the record so it separates from the black
    g = Image.new("RGBA", (D + 300, D + 300), (0, 0, 0, 0))
    ImageDraw.Draw(g).ellipse([150, 150, D + 150, D + 150], fill=(255, 150, 70, 60))
    g.filter(ImageFilter.GaussianBlur(70)).save(glow_png)
    cream = (255, 240, 220, 255)
    text_card([(line, 76, 600, cream) for line in HOOK.split("\n")], hook_png)
    text_card([(CTA[0], 62, 600, cream), (CTA[1], 40, 500, (243, 211, 166, 255))], cta_png)

    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", src],
                               capture_output=True, text=True, check=True).stdout)
    if end:
        dur = end
    cta = dur - CTA_LEN
    w = 2 * np.pi * RPM / 60
    x0, y0 = CX - D // 2, CY - D // 2
    rec = f"fade=t=in:st={HOOK_END}:d=0.8:alpha=1,fade=t=out:st={cta - 0.6:.2f}:d=0.6:alpha=1"
    fc = (
        f"[1:v]format=rgba,{rec}[glow];"
        f"[2:v]format=rgba,rotate=a='{w:.4f}*t':c=none:ow={D}:oh={D},{rec}[disc];"
        f"[3:v]format=rgba,{rec}[still];"
        f"[4:v]format=rgba,fade=t=in:st=0.15:d=0.5:alpha=1,fade=t=out:st={HOOK_END - 0.5}:d=0.5:alpha=1[hook];"
        f"[5:v]format=rgba,fade=t=in:st={cta:.2f}:d=0.6:alpha=1[cta];"
        f"[0:v][glow]overlay={x0 - 150}:{y0 - 150}:shortest=1[a];"
        f"[a][disc]overlay={x0}:{y0}:shortest=1[b];"
        f"[b][still]overlay={x0}:{y0}:shortest=1[c];"
        f"[c][hook]overlay=0:{CY - 280}:shortest=1[d];"
        f"[d][cta]overlay=0:{CY - 280}:shortest=1,"
        f"fade=t=out:st={dur - 0.8:.2f}:d=0.8[v]"
    )
    subprocess.run([
        "ffmpeg", "-v", "error", "-y", "-i", src,
        *[a for p in (glow_png, disc_png, still_png, hook_png, cta_png)
          for a in ("-loop", "1", "-framerate", "30", "-i", p)],
        "-filter_complex", fc, "-map", "[v]", "-map", "0:a", "-t", f"{dur:.2f}",
        "-af", f"afade=t=out:st={dur - 1.6:.2f}:d=1.6",
        "-c:v", "libx264", "-crf", "20", "-preset", "slow", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", out], check=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("out")
    ap.add_argument("--end", type=float, help="cut the reel at this second (short version)")
    a = ap.parse_args()
    main(a.src, a.out, a.end)
