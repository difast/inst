"""Primi Passi (Fabrizio Paterlini), bars 1-8 + 17-24, transcribed from the sheet music.

Writes public/notes.json (for the video) and public/primi-passi.mid.
Positions and lengths are in eighth notes; each 4/4 bar has 8 eighths.
"""
import json
import os

import mido

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


def write_midi(notes, path):
    mf = mido.MidiFile(ticks_per_beat=480)
    tr = mido.MidiTrack()
    mf.tracks.append(tr)
    tr.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(TEMPO_BPM)))
    tps = 480 * TEMPO_BPM / 60
    ev = []
    for n in notes:
        ev.append((n["start"], 1, n["midi"], n["vel"]))
        ev.append((n["start"] + n["dur"], 0, n["midi"], 0))
    ev.sort(key=lambda e: (e[0], e[1]))
    last = 0
    for t, on, m, v in ev:
        tick = round(t * tps)
        tr.append(mido.Message("note_on" if on else "note_off", note=m, velocity=v, time=tick - last))
        last = tick
    mf.save(path)


if __name__ == "__main__":
    root = os.path.join(os.path.dirname(__file__), "..", "public")
    notes, bar_len = build()
    with open(os.path.join(root, "notes.json"), "w") as f:
        json.dump({"tempo": TEMPO_BPM, "barLength": bar_len, "notes": notes}, f, indent=1)
    write_midi(notes, os.path.join(root, "primi-passi.mid"))
    end = max(n["release"] for n in notes)
    print(f"{len(notes)} notes, music ends at {end:.2f}s")
