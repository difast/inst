"""Hands at the piano on a dark background, from piano/reference/"видео с руками второй.mp4".

The room never appears: every pixel outside the keys and the hands is replaced with a
generated dark backdrop (warm glow behind the keys, slow faint smoke). The keys are a
fixed mask (the camera stands still); the hands are found in every frame by skin
colour, smoothed in time and feathered. The lacquered panel next to the keys (it
mirrors the hands and the room) is outside the mask, so its reflections are gone.
A slow push-in, warm grade and film grain finish the look. The live sound is kept,
only cleaned. vinyl_title.py then adds the spinning record, the hook and the CTA.
Writes piano/final/hands-dark.mp4 (47 s) and hands-dark-short.mp4 (25.6 s, ends on
the G minor cadence).
"""
import os
import subprocess
import tempfile

import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage

import vinyl_title

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "..", "reference", "видео с руками второй.mp4")
FINAL = os.path.join(HERE, "..", "..", "final")
OUT = os.path.join(tempfile.gettempdir(), "hands-dark-base.mp4")  # before titles
SHORT_END = 25.6
SW, SH = 464, 848
W, H, FPS = 1080, 1920, 30
START, END = 5.92, 53.4  # from the loud entry to the end of the last chord
ZOOM = (1.18, 1.32)  # framed tighter than the source, slow push-in over the clip
FOCUS = (215, 600)  # the hands (source pixels); the crop is centred here when it fits

# keys only: far end of the keyboard, along the felt strip, down to the frame edge
KEYS = [(210, 510), (278, 510), (300, 543), (325, 573), (350, 598), (390, 633), (425, 678),
        (464, 726), (464, 848), (0, 848), (0, 735), (60, 665), (110, 610), (160, 560)]
# where hands can be: everything left of the felt strip, below the wall shelf
HAND_ZONE = [(0, 380), (300, 380), (300, 543), (325, 573), (350, 598), (390, 633), (425, 678),
             (464, 726), (464, 848), (0, 848)]


def poly_mask(points, blur):
    m = Image.new("L", (SW, SH), 0)
    ImageDraw.Draw(m).polygon(points, fill=255)
    if blur:
        m = m.filter(ImageFilter.GaussianBlur(blur))
    return np.asarray(m, np.float32) / 255


def backdrop(t, rng_fields):
    """Near-black warm background with a soft glow behind the keys and drifting smoke."""
    y, x = np.mgrid[0:SH, 0:SW].astype(np.float32)
    glow = np.exp(-(((x - 230) / 260) ** 2 + ((y - 600) / 220) ** 2))
    a, b = rng_fields
    sx = int(t * 6) % SW
    smoke = 0.6 * np.roll(a, sx, axis=1) + 0.4 * np.roll(b, -sx // 2, axis=1)
    smoke *= np.clip((y - 250) / 400, 0, 1)  # smoke stays low
    v = 0.035 + 0.11 * glow + 0.05 * smoke
    return np.stack([v * 255 * 1.0, v * 255 * 0.72, v * 255 * 0.5], -1)


def smoke_field(seed):
    rng = np.random.default_rng(seed)
    f = ndimage.gaussian_filter(rng.random((SH, SW)).astype(np.float32), 28)
    f = (f - f.min()) / (f.max() - f.min())
    return f


def main():
    keys = poly_mask(KEYS, 3)
    zone = poly_mask(HAND_ZONE, 0) > 0.5
    fields = (smoke_field(1), smoke_field(2))
    dur = END - START
    n_frames = int(dur * FPS)

    dec = subprocess.Popen(
        ["ffmpeg", "-v", "error", "-ss", str(START), "-i", SRC, "-t", str(dur), "-r", str(FPS),
         "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    audio = os.path.join(tempfile.gettempdir(), "hands-dark-audio.wav")
    subprocess.run([
        "ffmpeg", "-v", "error", "-y", "-ss", str(START), "-i", SRC, "-t", str(dur), "-vn",
        "-af", "highpass=f=60,afftdn=nr=12:nf=-50,equalizer=f=220:t=q:w=1.2:g=-2,"
               "acompressor=threshold=-18dB:ratio=2:attack=15:release=250,"
               "loudnorm=I=-14:TP=-1.5:LRA=11,afade=t=in:d=0.05,"
               f"afade=t=out:st={dur - 1.6:.2f}:d=1.6",
        "-ar", "48000", "-ac", "2", audio], check=True)
    enc = subprocess.Popen(
        ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
         "-r", str(FPS), "-i", "-", "-i", audio,
         "-vf", "noise=c0s=4:c0f=t+u,fade=t=in:d=0.25,"
                f"fade=t=out:st={dur - 1.4:.2f}:d=1.4",
         "-c:v", "libx264", "-crf", "22", "-preset", "slow", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", OUT],
        stdin=subprocess.PIPE)

    prev = None
    for i in range(n_frames):
        raw = dec.stdout.read(SW * SH * 3)
        if len(raw) < SW * SH * 3:
            break
        f = np.frombuffer(raw, np.uint8).reshape(SH, SW, 3).astype(np.float32)
        r, g, b = f[..., 0], f[..., 1], f[..., 2]
        skin = (r > 85) & (r - g > 28) & (g - b < 28) & (g - b > -8) & zone
        skin = ndimage.binary_opening(skin, iterations=2)
        skin = ndimage.binary_closing(skin, iterations=4)
        skin = ndimage.binary_fill_holes(skin)
        lab, nlab = ndimage.label(skin)
        if nlab:  # keep only real blobs (hands), drop specks
            sizes = ndimage.sum(skin, lab, range(1, nlab + 1))
            skin = np.isin(lab, 1 + np.flatnonzero(sizes > 400))
        hand = ndimage.gaussian_filter(ndimage.binary_dilation(skin, iterations=3).astype(np.float32), 4.5)
        prev = hand if prev is None else np.maximum(hand, prev * 0.55)  # no flicker at the edges
        # the yellow box behind the hands must not ride along the hand edges
        yellow = ndimage.binary_dilation((g - b > 55) & (r > 110) & (keys < 0.5), iterations=2)
        hand_m = prev * (1 - ndimage.gaussian_filter(yellow.astype(np.float32), 1.5))
        m = np.clip(np.maximum(keys, hand_m), 0, 1)[..., None]

        t = i / FPS
        # warm, slightly crushed grade on the kept picture
        lit = np.clip((f / 255) ** 1.08 * np.array([1.04, 0.98, 0.88]) * 255, 0, 255)
        comp = lit * m + backdrop(t, fields) * (1 - m)

        # slow push-in towards the hands
        z = ZOOM[0] + (ZOOM[1] - ZOOM[0]) * (t / dur)
        cw, ch = SW / z, SH / z
        x0 = min(max(FOCUS[0] - cw / 2, 0), SW - cw)
        y0 = min(max(FOCUS[1] - ch / 2, 0), SH - ch)
        img = Image.fromarray(comp.astype(np.uint8)).transform(
            (W, H), Image.EXTENT, (x0, y0, x0 + cw, y0 + ch), Image.BICUBIC)
        enc.stdin.write(img.tobytes())
    enc.stdin.close()
    enc.wait()
    dec.stdout.close()
    dec.wait()
    os.remove(audio)
    vinyl_title.main(OUT, os.path.join(FINAL, "hands-dark.mp4"))
    vinyl_title.main(OUT, os.path.join(FINAL, "hands-dark-short.mp4"), SHORT_END)
    print(f"hands-dark.mp4: {dur:.1f}s, hands-dark-short.mp4: {SHORT_END}s")


if __name__ == "__main__":
    main()
