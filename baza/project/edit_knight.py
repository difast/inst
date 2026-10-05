"""Edit the 6 Seedance clips (baza/reference/1-6.mp4) into one ~18 s 16:9 video.

Each segment is (clip, start, end, crop). crop is an (x, y, w, h) window in source pixels;
by default a small centre crop hides the "AI" badge in the top-left corner.
Writes baza/final/knight.mp4 (clip sound, levelled) and knight-nosound.mp4
(for adding a track inside Instagram).
"""
import os
import subprocess

REF = os.path.join(os.path.dirname(__file__), "..", "reference")
OUT = os.path.join(os.path.dirname(__file__), "..", "final")
W, H, FPS = 1280, 720, 60
DEFAULT_CROP = (32, 18, 1216, 684)

SEGMENTS = [
    (1, 1.75, 5.00, None),               # lifts his head, lightning
    (2, 2.50, 5.00, None),               # raises the sword in the storm
    (3, 0.25, 1.60, None),               # ice giant rises
    (3, 3.50, 5.00, None),               # battle stance in the snow
    (4, 0.00, 1.50, None),               # dragon breathes fire
    (4, 3.00, 3.45, None),               # crouched in the flames
    (4, 4.35, 5.05, (400, 0, 853, 480)), # the strike, framed waist-up (hides the jump)
    (5, 0.20, 1.20, None),               # running through the snow
    (5, 2.30, 5.00, None),               # opens the doors, light bursts out
    (6, 1.75, 5.05, None),               # on the peak, army below
]
AFADE = 0.03


def build():
    inputs, filters, labels = [], [], []
    for i, (clip, a, b, crop) in enumerate(SEGMENTS):
        inputs += ["-i", os.path.join(REF, f"{clip}.mp4")]
        x, y, w, h = crop or DEFAULT_CROP
        d = b - a
        filters.append(
            f"[{i}:v]trim={a}:{b},setpts=PTS-STARTPTS,fps={FPS},crop={w}:{h}:{x}:{y},"
            f"scale={W}:{H}:flags=lanczos,setsar=1[v{i}]")
        filters.append(
            f"[{i}:a]atrim={a}:{b},asetpts=PTS-STARTPTS,aresample=48000,"
            f"afade=t=in:d={AFADE},afade=t=out:st={d - AFADE:.3f}:d={AFADE}[a{i}]")
        labels.append(f"[v{i}][a{i}]")
    total = sum(b - a for _, a, b, _ in SEGMENTS)
    filters.append("".join(labels) + f"concat=n={len(SEGMENTS)}:v=1:a=1[vc][ac]")
    filters.append(
        f"[vc]eq=contrast=1.05:saturation=1.06,fade=t=in:d=0.3,"
        f"fade=t=out:st={total - 0.6:.3f}:d=0.6[vout]")
    filters.append(
        f"[ac]loudnorm=I=-16:TP=-1.5:LRA=11,afade=t=out:st={total - 0.6:.3f}:d=0.6[aout]")
    cmd = ["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", ";".join(filters),
           "-map", "[vout]", "-c:v", "libx264", "-crf", "17", "-preset", "slow",
           "-pix_fmt", "yuv420p", "-movflags", "+faststart"]
    cmd += ["-map", "[aout]", "-c:a", "aac", "-b:a", "192k"]
    os.makedirs(OUT, exist_ok=True)
    out = os.path.join(OUT, "knight.mp4")
    subprocess.run(cmd + [out], check=True)
    # same picture without sound, for adding a track inside Instagram
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", out, "-c:v", "copy", "-an",
                    os.path.join(OUT, "knight-nosound.mp4")], check=True)
    print(f"knight.mp4 / knight-nosound.mp4: {total:.2f}s")


if __name__ == "__main__":
    build()
