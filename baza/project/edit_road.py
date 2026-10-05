"""Edit p1-p4 (baza/reference) into one smooth ~20 s road-trip video.

Soft dissolves between all shots, the final sky rise slowed down a little so the
closing phrase can be read. Film look: light grain and 2.39:1 letterbox bars.
Writes baza/final/road.mp4 (clip sound) and road-nosound.mp4.
"""
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
REF = os.path.join(HERE, "..", "reference")
OUT = os.path.join(HERE, "..", "final")
FONT = os.path.join(HERE, "fonts", "Cormorant.ttf")
W, H, FPS = 1280, 720, 60
BAR = round((H - W / 2.39) / 2)

# (clip, start, end, slowdown)
SHOTS = [
    [("p1", 0.00, 5.05, 1.0)],                          # coffee by the car
    [("p2", 0.00, 5.05, 1.0)],                          # driving
    [("p3", 0.00, 3.53, 1.0)],                          # drone over the coast road
    [("p3", 3.58, 6.90, 1.0)],                          # at the cliff (the rest of p3 is cut)
    [("p4", 0.00, 2.50, 1.0), ("p4", 2.50, 5.05, 1.6)], # sunset, camera rises into the sky
]
FADES = [0.8, 0.8, 0.7, 0.9]  # dissolve between shot i and i+1
LINES = ["Лучшие дороги ведут туда,", "где ты ещё не был"]
TEXT_IN = 2.6  # seconds into the last shot (after the slow-down starts)


def shot_len(parts):
    return sum((b - a) * k for _, a, b, k in parts)


def main():
    inputs, f = [], []
    n = 0
    for si, parts in enumerate(SHOTS):
        vlab, alab = [], []
        for clip, a, b, k in parts:
            inputs += ["-i", os.path.join(REF, f"{clip}.mp4")]
            f.append(f"[{n}:v]trim={a}:{b},setpts=(PTS-STARTPTS)*{k},fps={FPS},"
                     f"crop=1216:684:32:18,scale={W}:{H}:flags=lanczos,setsar=1,format=yuv420p[v{n}]")
            tempo = f",atempo={1 / k:.4f}" if k != 1.0 else ""
            f.append(f"[{n}:a]atrim={a}:{b},asetpts=PTS-STARTPTS{tempo},aresample=48000[a{n}]")
            vlab.append(f"[v{n}]"); alab.append(f"[a{n}]")
            n += 1
        if len(parts) > 1:
            f.append("".join(v + a for v, a in zip(vlab, alab)) + f"concat=n={len(parts)}:v=1:a=1[cv{si}][sa{si}]")
            f.append(f"[cv{si}]fps={FPS},settb=1/{FPS}[sv{si}]")
        else:
            f.append(f"{vlab[0]}settb=1/{FPS}[sv{si}]"); f.append(f"{alab[0]}anull[sa{si}]")

    lengths = [shot_len(p) for p in SHOTS]
    cur_v, cur_a, t = "[sv0]", "[sa0]", lengths[0]
    for i, d in enumerate(FADES):
        off = t - d
        f.append(f"{cur_v}[sv{i + 1}]xfade=transition=fade:duration={d}:offset={off:.3f}[xv{i}]")
        f.append(f"{cur_a}[sa{i + 1}]acrossfade=d={d}[xa{i}]")
        cur_v, cur_a = f"[xv{i}]", f"[xa{i}]"
        t = off + lengths[i + 1]
    total = t
    last_start = total - lengths[-1]
    t_in = last_start + TEXT_IN

    alpha = f"if(lt(t,{t_in:.2f}),0,if(lt(t,{t_in + 1.2:.2f}),(t-{t_in:.2f})/1.2,1))"
    text = []
    for li, line in enumerate(LINES):
        y = f"h*0.30+{li}*70"
        text.append(
            f"drawtext=fontfile='{FONT}':text='{line}':fontsize=60:fontcolor=white:"
            f"x=(w-text_w)/2:y={y}:alpha='{alpha}':shadowcolor=black@0.45:shadowx=0:shadowy=2")
    f.append(
        f"{cur_v}noise=c0s=5:c0f=t+u,"
        f"drawbox=x=0:y=0:w={W}:h={BAR}:color=black:t=fill,"
        f"drawbox=x=0:y={H - BAR}:w={W}:h={BAR}:color=black:t=fill,"
        + ",".join(text) +
        f",fade=t=in:d=0.6,fade=t=out:st={total - 1.0:.2f}:d=1.0[vout]")
    f.append(f"{cur_a}loudnorm=I=-16:TP=-1.5:LRA=11,afade=t=in:d=0.4,"
             f"afade=t=out:st={total - 1.2:.2f}:d=1.2[aout]")

    os.makedirs(OUT, exist_ok=True)
    out = os.path.join(OUT, "road.mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", ";".join(f),
                    "-map", "[vout]", "-map", "[aout]", "-c:v", "libx264", "-crf", "17",
                    "-preset", "slow", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
                    "-movflags", "+faststart", out], check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", out, "-c:v", "copy", "-an",
                    os.path.join(OUT, "road-nosound.mp4")], check=True)
    print(f"road.mp4 / road-nosound.mp4: {total:.2f}s, phrase from {t_in:.2f}s")


if __name__ == "__main__":
    main()
