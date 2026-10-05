"""Primi Passi (Fabrizio Paterlini), bars 1-8 + 17-24, transcribed from the sheet music.

Writes public/notes.json (for the video) and public/primi-passi.mid.
Positions and lengths are in eighth notes; each 4/4 bar has 8 eighths.
"""
import json
import os

from notation import write_midi

TEMPO_BPM = 132
START_OFFSET = 0.5  # seconds of silence before the first note

NOTE_NAMES = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
KEY_SHARPS = {"F", "C"}  # D major


def midi(name):
    letter, octave = name[0], int(name[-1])
    n = 12 * (octave + 1) + NOTE_NAMES[letter]
    return n + 1 if letter in KEY_SHARPS else n


# Right hand: pickup eighth on the "and" of beat 2, then four eighths.
RH_A = ["C5", "D5", "B4", "G5", "F5"]  # C# D B G F#
RH_B = ["D5", "E5", "C5", "G5", "F5"]  # D E C# G F#
RH_C = ["D5", "E5", "A4", "G5", "F5"]  # D E A G F#
RH_END = "half"  # C# then D held as a half note
RH_UP = ["D5", "D5", "B5", "A5", "A5"]  # D D B A A
RH_EF = ["E5", "E5", "F5", "G5", "G5"]  # E E F# G G

LH_Bm = ["B3", "F4", "B4"]
LH_D = ["D4", "A4", "C5"]
LH_A = ["A3", "E4", "B4"]
LH_G = ["G3", "D4", "B4"]
LH_A2 = ["A3", "E4", "C5"]

BARS = [
    (RH_A, LH_Bm), (RH_A, LH_Bm), (RH_B, LH_D), (RH_B, LH_D),
    (RH_A, LH_A), (RH_A, LH_A), (RH_A, LH_Bm), (RH_END, LH_Bm),
    # bars 17-24
    (RH_UP, LH_G), (RH_EF, LH_A2), (RH_A, LH_Bm), (RH_A, LH_Bm),
    (RH_UP, LH_G), (RH_EF, LH_A2), (RH_A, LH_Bm), (RH_A, LH_Bm),
]
GRACE_BARS = {8}  # bar 17 (index 8 here) has a grace B5 before the last A5


def build():
    eighth = 60 / TEMPO_BPM / 2
    bar_len = 8 * eighth
    notes = []

    def add(bar, pos, length, name, hand, vel):
        t = START_OFFSET + bar * bar_len + pos * eighth
        notes.append({
            "midi": midi(name),
            "start": round(t, 4),
            "dur": round(length * eighth * 0.92, 4),
            # sustain pedal is changed every bar, so notes ring to the bar end
            "release": round(START_OFFSET + (bar + 1) * bar_len, 4),
            "hand": hand,
            "vel": vel,
        })

    for b, (rh, lh) in enumerate(BARS):
        for i, n in enumerate(lh):
            add(b, i, 1, n, "L", [74, 62, 66][i])
        if rh == RH_END:
            add(b, 3, 1, "C5", "R", 70)
            add(b, 4, 4, "D5", "R", 78)
        else:
            vels = [70, 80, 66, 82, 72]
            for i, n in enumerate(rh):
                add(b, 3 + i, 1, n, "R", vels[i])
            if b in GRACE_BARS:
                add(b, 7 - 0.3, 0.3, "B5", "R", 60)
    return notes, bar_len


if __name__ == "__main__":
    out = os.path.join(os.path.dirname(__file__), "..", "public", "primi-passi")
    os.makedirs(out, exist_ok=True)
    notes, bar_len = build()
    data = {"composer": "Fabrizio Paterlini", "title": "Primi Passi", "duration": 30, "keyboard": [48, 96],
            "sections": [], "notes": notes}
    with open(os.path.join(out, "notes.json"), "w") as f:
        json.dump(data, f, indent=1)
    write_midi(notes, os.path.join(out, "notes.mid"))
    end = max(n["release"] for n in notes)
    print(f"{len(notes)} notes, music ends at {end:.2f}s")
