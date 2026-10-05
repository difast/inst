"""Render public/<song>/notes.json to public/<song>/audio.wav with Salamander Grand Piano samples.

Samples (CC-BY 3.0, Alexander Holm) are fetched from github.com/Tonejs/audio
into scripts/.samples on first run.
"""
import json
import os
import subprocess
import sys
import urllib.request

import numpy as np

SR = 44100
HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, ".samples")
URL = "https://raw.githubusercontent.com/Tonejs/audio/master/salamander/{}.mp3"
SAMPLE_NOTES = {"A": 9, "C": 0, "Ds": 3, "Fs": 6}
RELEASE = 0.45


def sample_list():
    out = {}
    for octave in range(0, 8):
        for name, pc in SAMPLE_NOTES.items():
            m = 12 * (octave + 1) + pc
            if 21 <= m <= 96:
                out[m] = f"{name}{octave}"
    return out


def load(name):
    os.makedirs(CACHE, exist_ok=True)
    path = os.path.join(CACHE, name + ".mp3")
    if not os.path.exists(path):
        urllib.request.urlretrieve(URL.format(name), path)
    raw = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", path, "-f", "f32le", "-ac", "2", "-ar", str(SR), "-"],
        check=True, capture_output=True,
    ).stdout
    return np.frombuffer(raw, dtype=np.float32).reshape(-1, 2)


def main(song):
    root = os.path.join(HERE, "..", "public", song)
    data = json.load(open(os.path.join(root, "notes.json")))
    notes, total_seconds = data["notes"], data["duration"]
    samples = sample_list()
    cache = {}
    out = np.zeros((int(total_seconds * SR) + SR, 2), dtype=np.float32)
    for n in notes:
        base = min(samples, key=lambda m: abs(m - n["midi"]))
        if base not in cache:
            cache[base] = load(samples[base])
        src = cache[base]
        ratio = 2 ** ((n["midi"] - base) / 12)
        hold = n["release"] - n["start"]
        length = int((hold + RELEASE) * SR)
        idx = np.arange(length) * ratio
        idx = idx[idx < len(src) - 1]
        wav = np.stack([np.interp(idx, np.arange(len(src)), src[:, c]) for c in range(2)], axis=1)
        env = np.ones(len(wav), dtype=np.float32)
        h = int(hold * SR)
        if h < len(wav):
            env[h:] = np.exp(-np.arange(len(wav) - h) / (RELEASE * SR / 5))
        gain = (n["vel"] / 127) ** 1.7
        s = int(n["start"] * SR)
        seg = out[s:s + len(wav)]
        seg += (wav[:len(seg)] * env[:len(seg), None] * gain).astype(np.float32)
    out = out[: int(total_seconds * SR)]
    fade = int(0.4 * SR)
    out[-fade:] *= np.linspace(1, 0, fade)[:, None]
    tmp = os.path.join(root, "audio_dry.f32")
    out.tofile(tmp)
    subprocess.run([
        "ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ac", "2", "-ar", str(SR), "-i", tmp,
        "-af", "aecho=0.8:0.6:45|90|140:0.22|0.14|0.08,loudnorm=I=-14:TP=-1.5:LRA=11",
        "-ar", str(SR), os.path.join(root, "audio.wav"),
    ], check=True)
    os.remove(tmp)


if __name__ == "__main__":
    main(sys.argv[1])
