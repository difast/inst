"""Fast "no parachute" reel from 1.mp4 (fall + plane assembly) and 2.mp4 (private jet).

Short pieces of the clips, slowed down a little for smoothness, are interrupted by
black cards with one word at a time (md.mp4 style: wide bold caps, pale blue, hard
cuts). The clip sound keeps playing under the cards, so the wind is heard already
on the opening black screen. The voice-over (VOICE) is cut into phrases that play
only on the cards; each card lasts as long as its phrase and the words appear in
sync with the speech. Writes baza/final/fall.mp4 and fall-nosound.mp4.
"""
import os
import subprocess
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REF = os.path.join(HERE, "..", "reference")
OUT = os.path.join(HERE, "..", "final")
FONT = os.path.join(HERE, "fonts", "ArchivoExpanded-ExtraBold.ttf")
WM_FONT = os.path.join(HERE, "fonts", "Cormorant.ttf")
W, H, FPS = 720, 1280, 30
SLOW = 1.25          # clip slowdown
VOICE = os.path.join(REF, "dreamina-2026-10-06-9487.mp3")
LEAD = 0.25          # card starts this long before its phrase
AMBIENT_ON_CARDS = 0.35  # clip sound level under the voice
TEXT_COLOR = "0xD6E8F8"
CROP = "crop=684:1216:30:54"  # hides the "AI" badge in the top-left corner

# ("card", [(word, syllables)], (voice_start, voice_end), tail)  or  ("clip", name, start, end)
# Word onsets are spread over the phrase by syllable count ("FALLS" is weighted
# up to cover the pause before "NOT EVERYONE").
TIMELINE = [
    ("card", [("STARTING", 2), ("A BUSINESS", 3), ("IS", 1), ("JUMPING", 2),
              ("WITHOUT", 2), ("A PARACHUTE", 4)], (0.00, 2.34), 0.20),
    ("clip", "1", 0.00, 2.20),   # back view, falling over the clouds
    ("card", [("PROBLEMS", 2), ("HIT YOU", 2), ("OUT OF", 2), ("NOWHERE", 2)], (2.85, 4.26), 0.15),
    ("clip", "1", 3.05, 4.40),   # the seagull
    ("card", [("STAY", 1), ("CALM", 1), ("AND BUILD", 2), ("THE PLANE", 2)], (4.75, 6.50), 0.15),
    ("clip", "1", 6.90, 9.10),   # eyes closed, the jet assembles around him
    ("card", [("ON THE", 2), ("WAY", 1), ("DOWN", 1)], (6.52, 7.44), 0.15),
    ("clip", "2", 0.40, 2.40),   # champagne
    ("clip", "2", 3.30, 5.05),   # camera to the window
    ("card", [("EVERYONE", 3), ("FALLS", 4.3), ("NOT EVERYONE", 4), ("BUILDS", 1), ("THE PLANE", 2)],
     (7.89, 10.56), 1.30),
]


def card_len(voice, tail):
    return LEAD + voice[1] - voice[0] + tail


def word_times(words, voice, d):
    total = sum(w for _, w in words)
    starts, acc = [], 0.0
    for _, w in words:
        starts.append(LEAD + (voice[1] - voice[0]) * acc / total)
        acc += w
    return [(s, starts[i + 1] if i + 1 < len(starts) else d) for i, s in enumerate(starts)]


def main():
    tmp = tempfile.mkdtemp()
    inputs, f, vl, al, vo = [], [], [], [], []
    t = 0.0
    for i, seg in enumerate(TIMELINE):
        if seg[0] == "card":
            _, words, voice, tail = seg
            d = card_len(voice, tail)
            chain = []
            for wi, ((word, _), (a, b)) in enumerate(zip(words, word_times(words, voice, d))):
                path = os.path.join(tmp, f"{i}_{wi}.txt")
                with open(path, "w") as fh:
                    fh.write(word)
                chain.append(
                    f"drawtext=fontfile='{FONT}':textfile='{path}':fontsize=44:"
                    f"fontcolor={TEXT_COLOR}:x=(w-text_w)/2:y=(h-text_h)/2:"
                    f"enable='gte(t,{a:.3f})*lt(t,{b:.3f})'")
            f.append(f"color=c=black:s={W}x{H}:r={FPS}:d={d:.3f},format=yuv420p,"
                     + ",".join(chain) + f",settb=1/{FPS}[v{i}]")
            # Sound under the card: the neighbouring clip's audio (the next one,
            # or the previous one for the closing card).
            nxt = next((s for s in TIMELINE[i + 1:] if s[0] == "clip"), None)
            if nxt:
                src, end = nxt[1], nxt[2]
            else:
                prv = [s for s in TIMELINE[:i] if s[0] == "clip"][-1]
                src, end = prv[1], prv[3]
            a0 = max(0.0, end - d / SLOW)
            inputs += ["-i", os.path.join(REF, f"{src}.mp4")]
            n = len(inputs) // 2 - 1
            f.append(f"[{n}:a]atrim={a0:.3f}:{a0 + d / SLOW:.3f},asetpts=PTS-STARTPTS,"
                     f"atempo={1 / SLOW:.4f},aresample=48000,apad,atrim=0:{d:.3f},"
                     f"volume={AMBIENT_ON_CARDS},"
                     f"afade=t=in:d=0.03,afade=t=out:st={d - 0.03:.3f}:d=0.03[a{i}]")
            # the phrase itself, placed at its absolute time in the reel
            inputs += ["-i", VOICE]
            n = len(inputs) // 2 - 1
            ms = round((t + LEAD) * 1000)
            f.append(f"[{n}:a]atrim={voice[0]}:{voice[1]},asetpts=PTS-STARTPTS,aresample=48000,"
                     f"aformat=channel_layouts=stereo,afade=t=in:d=0.02,"
                     f"afade=t=out:st={voice[1] - voice[0] - 0.04:.3f}:d=0.04,"
                     f"adelay={ms}|{ms}[vo{i}]")
            vo.append(f"[vo{i}]")
        else:
            _, src, a, b = seg
            d = (b - a) * SLOW
            inputs += ["-i", os.path.join(REF, f"{src}.mp4")]
            n = len(inputs) // 2 - 1
            f.append(f"[{n}:v]trim={a}:{b},setpts=(PTS-STARTPTS)*{SLOW},fps={FPS},"
                     f"{CROP},scale={W}:{H}:flags=lanczos,setsar=1,format=yuv420p,"
                     f"settb=1/{FPS}[v{i}]")
            f.append(f"[{n}:a]atrim={a}:{b},asetpts=PTS-STARTPTS,atempo={1 / SLOW:.4f},"
                     f"aresample=48000,apad,atrim=0:{d:.3f},"
                     f"afade=t=in:d=0.03,afade=t=out:st={d - 0.03:.3f}:d=0.03[a{i}]")
        vl.append(f"[v{i}]"); al.append(f"[a{i}]")
        t += d
    total = t

    f.append("".join(v + a for v, a in zip(vl, al)) + f"concat=n={len(vl)}:v=1:a=1[cv][ca]")
    f.append(f"[cv]noise=c0s=4:c0f=t+u,"
             f"drawtext=fontfile='{WM_FONT}':text='P':fontsize=52:fontcolor=white@0.65:"
             f"x=w-text_w-40:y=h-text_h-60:shadowcolor=black@0.35:shadowx=0:shadowy=1[vout]")
    f.append(f"[ca]aformat=channel_layouts=stereo[amb]")
    f.append("[amb]" + "".join(vo) + f"amix=inputs={len(vo) + 1}:normalize=0:duration=first[mix]")
    f.append(f"[mix]loudnorm=I=-16:TP=-1.5:LRA=11,afade=t=in:d=0.3,"
             f"afade=t=out:st={total - 1.0:.2f}:d=1.0[aout]")

    os.makedirs(OUT, exist_ok=True)
    out = os.path.join(OUT, "fall.mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", ";".join(f),
                    "-map", "[vout]", "-map", "[aout]", "-c:v", "libx264", "-crf", "17",
                    "-preset", "slow", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
                    "-movflags", "+faststart", out], check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", out, "-c:v", "copy", "-an",
                    os.path.join(OUT, "fall-nosound.mp4")], check=True)
    print(f"fall.mp4 / fall-nosound.mp4: {total:.2f}s")


if __name__ == "__main__":
    main()
