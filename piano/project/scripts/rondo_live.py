"""Rondo alla Turca, live take: split-screen data and media.

Source (piano/reference): "video my real.mp4" (top-down phone video of the theme,
bars 0-8, right hand) and "вайбовое фото.png" (mood photo for the top part).

Note onsets were picked from the recording's audio (spectral flux) and the pitches
checked against the score, so the falling notes land exactly when the keys are
struck in the video. Bars 5-7 are played in thirds (B5 alone, then F#5/A5, E5/G5 ...).

Writes public/rondo-live/: notes.json (notes + key geometry of the video),
keys.mp4 (keyboard strip only), photo.jpg (top part) and audio.wav (cleaned take).
"""
import json
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
REF = os.path.join(HERE, "..", "..", "reference")
OUT = os.path.join(HERE, "..", "public", "rondo-live")
VIDEO = os.path.join(REF, "video my real.mp4")
PHOTO = os.path.join(REF, "вайбовое фото.png")

W = 1080
SRC_W = 464
# keyboard strip in the source frame (keys top edge .. white keys bottom edge)
KB_Y, KB_H = 414, 130
# white key boundaries in the source frame: x = X0 + WW * k, k = 0 is the F3|G3 line
X0, WW = 15.3, 18.56
FIRST_WHITE = 55  # G3
DURATION = 18.6
KB_PX = 302  # strip height on screen (even, for the encoder)

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


def notes():
    out = []
    for i, (t, keys, dur) in enumerate(EVENTS):
        if dur is None:
            dur = EVENTS[i + 1][0] - t - 0.03
        for m in keys:
            out.append({"midi": m, "start": t, "dur": round(dur, 3), "hand": "R", "vel": 0.8})
    return out


def main():
    os.makedirs(OUT, exist_ok=True)
    s = W / SRC_W
    data = {
        "composer": "W. A. Mozart",
        "title": "Rondo alla Turca",
        "duration": DURATION,
        "keyboard": [53, 96],
        "sections": [],
        "notes": notes(),
        "geometry": {"x0": X0 * s, "ww": WW * s, "firstWhite": FIRST_WHITE, "height": KB_PX},
    }
    with open(os.path.join(OUT, "notes.json"), "w") as f:
        json.dump(data, f, indent=1)

    # keyboard strip only: no music desk, no reflections above the keys, no arms below;
    # exposure flattened (the phone kept re-exposing), glare on the keys toned down
    subprocess.run([
        "ffmpeg", "-v", "error", "-y", "-i", VIDEO, "-t", str(DURATION),
        "-vf", f"crop={SRC_W}:{KB_H}:0:{KB_Y},hqdn3d=2:2:4:4,"
               "normalize=blackpt=black:whitept=white:smoothing=60:strength=0.8,"
               "eq=saturation=0.75:gamma=0.95,curves=all='0/0 0.75/0.8 1/0.9',"
               f"scale={W}:{KB_PX}:flags=lanczos,unsharp=5:5:0.6,fps=30",
        "-an", "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p",
        os.path.join(OUT, "keys.mp4")], check=True)

    # cleaned piano sound: rumble and hiss removed, a little room, Instagram loudness
    subprocess.run([
        "ffmpeg", "-v", "error", "-y", "-i", VIDEO, "-t", str(DURATION), "-vn",
        "-af", "highpass=f=70,afftdn=nr=14:nf=-45,equalizer=f=250:t=q:w=1:g=-3,"
               "equalizer=f=4000:t=q:w=1:g=2,aecho=0.8:0.6:45|90:0.18|0.10,"
               "loudnorm=I=-16:TP=-1.5:LRA=11,afade=t=in:d=0.3,"
               f"afade=t=out:st={DURATION - 1.2}:d=1.2",
        "-ar", "48000", "-ac", "2", os.path.join(OUT, "audio.wav")], check=True)

    # top part: candle, sheet music and rose, cut to the band's 1080x620 shape
    subprocess.run([
        "ffmpeg", "-v", "error", "-y", "-i", PHOTO,
        "-vf", "crop=940:540:0:330,scale=1080:620:flags=lanczos", "-q:v", "2",
        os.path.join(OUT, "photo.jpg")], check=True)
    print(f"{len(data['notes'])} notes, {DURATION}s")


if __name__ == "__main__":
    main()
