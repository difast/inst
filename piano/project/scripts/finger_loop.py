"""Seamless "play after me" loop from a short close-up with numbers written on the keys.

Source: piano/reference/video_2026-10-09_15-53-23.mp4, the opening of "Ты не бойся
ночи" (ENZRO) in the right hand. The numbers on the keys are the order in which each
key first appears (E=1, C=2, B=3, A=4, F=5), so the phrase reads 1111 · 22342 · 5.

The clip is cut so that its end blends into its start (a short cross-dissolve of the
last frames into the frames just before the cut-in point): Instagram replays it
without a visible seam. Above the keys a number row lights up in time with each key
press, under a hook line. The lacquered panel with its reflections is cropped away,
glare on the keys is toned down, the edges sink into a warm dark.
Writes piano/final/finger-loop.mp4.
"""
import os
import subprocess

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "..", "reference", "video_2026-10-09_15-53-23.mp4")
OUT = os.path.join(HERE, "..", "..", "final", "finger-loop.mp4")
FONT = os.path.join(HERE, "..", "public", "fonts", "Cormorant.ttf")
W, H, FPS, SR = 1080, 1920, 30, 48000
SW, SH = 464, 848
START, END, XF = 0.40, 6.27, 0.30  # loop cut-in, cut-out, cross-dissolve length
CROP_Y = 305  # keys start below the felt strip; everything above is the lacquered panel
VIDEO_TOP = 480
# key presses (source seconds) and the number written on each key
PRESSES = [(0.66, 1), (1.03, 1), (1.39, 1), (1.75, 1), (2.07, 2), (2.46, 2), (3.62, 3),
           (4.38, 4), (4.78, 2), (5.46, 5)]
GROUPS = [4, 5, 1]  # bars: 1111 · 22342 · 5
TITLE = "ТЫ НЕ БОЙСЯ НОЧИ · ENZRO"
HOOK = "Сыграешь с первого раза?"
CREAM, AMBER, BG = (255, 240, 220), (255, 176, 84), (12, 8, 6)


def font(size, weight=600):
    f = ImageFont.truetype(FONT, size)
    f.set_variation_by_axes([weight])
    return f


def read_video():
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", SRC, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, SH, SW, 3)


def read_audio():
    raw = subprocess.run([
        "ffmpeg", "-v", "error", "-i", SRC, "-af",
        "highpass=f=70,afftdn=nr=12:nf=-50,equalizer=f=250:t=q:w=1:g=-2",
        "-f", "f32le", "-ac", "2", "-ar", str(SR), "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2)


def loop(seq, rate):
    """seq[START:END-XF] followed by seq[END-XF:END] dissolving into seq[START-XF:START]."""
    a, b, x = int(START * rate), int(END * rate), int(XF * rate)
    body = seq[a:b - x].astype(np.float32)
    w = np.linspace(0, 1, x, dtype=np.float32).reshape((-1,) + (1,) * (seq.ndim - 1))
    tail = seq[b - x:b].astype(np.float32) * (1 - w) + seq[a - x:a].astype(np.float32) * w
    return np.concatenate([body, tail])


def grade(f):
    """Warm tone, glare on the keys compressed, edges sinking into the dark."""
    f = f.astype(np.float32) / 255
    f = np.where(f > 0.72, 0.72 + (f - 0.72) * 0.45, f)  # soften hot spots
    f = f * np.array([1.03, 0.97, 0.88])
    y, x = np.mgrid[0:f.shape[0], 0:f.shape[1]].astype(np.float32)
    top = np.clip(y / 70, 0, 1)  # fade in from the text band
    vig = 1 - 0.35 * ((x / f.shape[1] - 0.5) * 2) ** 4
    return np.clip(f * (top * vig)[..., None], 0, 1)


def text_band():
    band = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(band)
    t = font(30, 600)
    tw = d.textlength(TITLE, font=t)
    x = (W - tw - 4 * (len(TITLE) - 1)) / 2
    for ch in TITLE:  # letter-spaced small caps
        d.text((x, 118), ch, font=t, fill=(214, 176, 128))
        x += d.textlength(ch, font=t) + 4
    hk = font(64, 600)
    d.text(((W - d.textlength(HOOK, font=hk)) / 2, 160), HOOK, font=hk, fill=CREAM)
    return band


def number_row(active, t_since):
    """The 1111 · 22342 · 5 row; past numbers cream, the current one amber and larger."""
    rh = 200
    layer = Image.new("RGBA", (W, rh), (0, 0, 0, 0))
    glow = Image.new("RGBA", (W, rh), (0, 0, 0, 0))
    d, g = ImageDraw.Draw(layer), ImageDraw.Draw(glow)
    step, gap = 88, 64  # between numbers, extra between bars
    xs, x = [], 0.0
    for gi, n in enumerate(GROUPS):
        for _ in range(n):
            xs.append(x)
            x += step
        x += gap
    x -= step + gap
    xs = [v + (W - x) / 2 for v in xs]
    lnum = ["lnum"]  # lining figures: Cormorant's default "1" looks like an "I"
    for k, cx in enumerate(xs):
        num = str(PRESSES[k][1])
        if k == active:
            f = font(int(112 * (1 + 0.3 * max(0.0, 1 - t_since / 0.25))), 700)
            col = AMBER + (255,)
        else:
            f = font(96, 600)
            col = CREAM + ((235,) if k < active else (75,))
        box = d.textbbox((0, 0), num, font=f, features=lnum)
        pos = (cx - (box[2] + box[0]) / 2, rh / 2 - (box[3] + box[1]) / 2)
        if k == active:
            g.text(pos, num, font=f, fill=(255, 150, 60, 255), features=lnum)
        d.text(pos, num, font=f, fill=col, features=lnum)
    k = 0
    for n in GROUPS[:-1]:  # dots between bars
        k += n
        cx = (xs[k - 1] + xs[k]) / 2
        d.ellipse([cx - 5, rh / 2 - 5, cx + 5, rh / 2 + 5], fill=(214, 176, 128, 170))
    return Image.alpha_composite(glow.filter(ImageFilter.GaussianBlur(16)), layer)


def main():
    frames = loop(read_video(), FPS)
    audio = loop(read_audio(), SR)
    n = len(frames)
    base = text_band()
    scale = W / SW
    vh = round((SH - CROP_Y) * scale)
    presses = [(t - START, i) for i, (t, _) in enumerate(PRESSES)]

    tmp_audio = OUT + ".f32"
    audio.astype(np.float32).tofile(tmp_audio)
    enc = subprocess.Popen([
        "ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
        "-i", "-", "-f", "f32le", "-ac", "2", "-ar", str(SR), "-i", tmp_audio,
        "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-vf", "noise=c0s=3:c0f=t+u",
        "-c:v", "libx264", "-crf", "18", "-preset", "slow", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", OUT], stdin=subprocess.PIPE)
    for i in range(n):
        t = i / FPS
        img = base.copy()
        keys = (grade(frames[i][CROP_Y:]) * 255).astype(np.uint8)
        img.paste(Image.fromarray(keys).resize((W, vh), Image.LANCZOS), (0, VIDEO_TOP))
        # bottom of the strip melts into the dark (Reels caption zone)
        fade = Image.linear_gradient("L").resize((W, 220))
        img.paste(Image.new("RGB", (W, 220), BG), (0, VIDEO_TOP + vh - 220), fade)
        img.paste(Image.new("RGB", (W, H - VIDEO_TOP - vh), BG), (0, VIDEO_TOP + vh))
        past = [p for p in presses if p[0] <= t]
        # at the loop seam the row starts over with the first press
        active, since = (past[-1][1], t - past[-1][0]) if past else (len(PRESSES) - 1, t + (END - START) - presses[-1][0])
        row = number_row(active, since)
        img.paste(row, (0, 262), row)
        enc.stdin.write(img.tobytes())
    enc.stdin.close()
    enc.wait()
    os.remove(tmp_audio)
    print(f"finger-loop.mp4: {n / FPS:.2f}s")


if __name__ == "__main__":
    main()
