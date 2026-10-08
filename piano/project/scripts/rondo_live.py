"""Rondo alla Turca, live take: split-screen data and media.

Source (piano/reference): "video my real.mp4" (top-down phone video of the theme,
bars 0-8, right hand) and "вайбовое фото.png" (mood photo for the top part).

Note onsets were picked from the recording's audio (spectral flux) and the pitches
checked against the score, so the falling notes land exactly when the keys are
struck in the video. Bars 5-7 are played in thirds (B5 alone, then F#5/A5, E5/G5 ...).

Writes public/rondo-live/: notes.json (notes + key geometry of the video),
keys.mp4 (keyboard strip only, zoomed to the played range), photo.jpg (top part)
and audio.wav (the same notes rendered with the Salamander piano, see synth.py).
"""
import json
import os
import subprocess

import synth

HERE = os.path.dirname(os.path.abspath(__file__))
REF = os.path.join(HERE, "..", "..", "reference")
OUT = os.path.join(HERE, "..", "public", "rondo-live")
VIDEO = os.path.join(REF, "video my real.mp4")
PHOTO = os.path.join(REF, "вайбовое фото.png")

W = 1080
# keyboard strip in the source frame (keys top edge .. white keys bottom edge)
KB_Y, KB_H = 414, 130
# white key boundaries in the source frame: x = X0 + WW * k, k = 0 is the F3|G3 line
X0, WW = 15.3, 18.56
# zoom on the played range: white keys D4..F6 (k = 4 .. 21)
CROP_X, CROP_W = 89, 316
FIRST_WHITE = 55  # G3
DURATION = 20.0
KB_PX = 444  # strip height on screen (even, for the encoder)

B4, A4, Gs4, C5, D5, Ds5, E5, F5, Fs5, G5, Gs5, A5, B5, C6 = (
    71, 69, 68, 72, 74, 75, 76, 77, 78, 79, 80, 81, 83, 84)

# (onset s, [midi...], fixed duration or None = until the next onset)
EVENTS = [
    (2.30, [B4], None), (2.52, [A4], None), (2.75, [Gs4], None), (2.95, [A4], None),   # pick-up
    (3.17, [C5], 0.45), (3.97, [D5], None), (4.21, [C5], None), (4.42, [B4], None), (4.66, [C5], None),
    (4.90, [E5], 0.45), (5.89, [F5], None), (6.13, [E5], None), (6.37, [Ds5], None), (6.61, [E5], None),
    (6.92, [B5], None), (7.19, [A5], None), (7.47, [Gs5], None), (7.69, [A5], None),
    (7.92, [B5], None), (8.15, [A5], None), (8.39, [Gs5], None), (8.61, [A5], None),
    (8.86, [C6], None), (9.73, [A5], None), (10.12, [C6], None),
    (10.62, [B5], None), (11.09, [Fs5, A5], None), (11.55, [E5, G5], None), (11.97, [Fs5, A5], None),
    (12.46, [B5], None), (12.90, [Fs5, A5], None), (13.37, [E5, G5], None), (13.82, [Fs5, A5], None),
    (14.23, [B5], None), (14.62, [Fs5, A5], None), (15.09, [E5, G5], None), (15.57, [Ds5, Fs5], None),
    (16.08, [E5], 1.5),
]


ACCENTS = {4, 9, 14, 22, 25, 29, 33, 37}


def notes():
    out = []
    for i, (t, keys, dur) in enumerate(EVENTS):
        if dur is None:
            dur = EVENTS[i + 1][0] - t - 0.03
        for m in keys:
            # bar-line notes a little louder, like the take
            vel = 84 if i in ACCENTS else 70
            out.append({"midi": m, "start": t, "dur": round(dur, 3), "release": round(t + dur, 3),
                        "hand": "R", "vel": vel})
    return out


def main():
    os.makedirs(OUT, exist_ok=True)
    s = W / CROP_W
    data = {
        "composer": "W. A. Mozart",
        "title": "Rondo alla Turca",
        "duration": DURATION,
        "keyboard": [53, 96],
        "sections": [],
        "notes": notes(),
        "geometry": {"x0": (X0 - CROP_X) * s, "ww": WW * s, "firstWhite": FIRST_WHITE, "height": KB_PX},
    }
    with open(os.path.join(OUT, "notes.json"), "w") as f:
        json.dump(data, f, indent=1)

    # keyboard strip only: no music desk, no reflections above the keys, no arms below;
    # exposure flattened (the phone kept re-exposing), glare on the keys toned down
    subprocess.run([
        "ffmpeg", "-v", "error", "-y", "-i", VIDEO, "-t", str(DURATION),
        "-vf", f"crop={CROP_W}:{KB_H}:{CROP_X}:{KB_Y},hqdn3d=2:2:4:4,"
               "normalize=blackpt=black:whitept=white:smoothing=60:strength=0.8,"
               "eq=saturation=0.75:gamma=0.95,curves=all='0/0 0.75/0.8 1/0.9',"
               f"scale={W}:{KB_PX}:flags=lanczos,unsharp=7:7:0.9,fps=30",
        "-an", "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p",
        os.path.join(OUT, "keys.mp4")], check=True)

    synth.main("rondo-live")

    # top part: candle, sheet music and rose, cut to the band's 1080x660 shape
    subprocess.run([
        "ffmpeg", "-v", "error", "-y", "-i", PHOTO,
        "-vf", "crop=940:574:0:300,scale=1080:660:flags=lanczos", "-q:v", "2",
        os.path.join(OUT, "photo.jpg")], check=True)
    print(f"{len(data['notes'])} notes, {DURATION}s")


if __name__ == "__main__":
    main()
