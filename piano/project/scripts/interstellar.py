"""Interstellar - Main Theme (Hans Zimmer), piano arrangement by Patrik Pietschmann.

~55 s cut for Reels: the theme (bars 5-12), straight into the climax (bars 137-152,
8va from bar 145) and the fading E pulse at the end (bars 153-157). Sustain pedal per bar.
"""
import os
import re

from notation import Score


def s16(notes, octave=0):
    return " ".join(f"{up(n, octave)}/.25" for n in notes.split())


def up(name, octave):
    return re.sub(r"(\d)$", lambda m: str(int(m.group(1)) + octave), name)


PULSE = "E4/1 E4/1 E4/1"
FIG = {  # 16th-note figures of the climax: right hand, left hand
    "F": ("A5 F5 E5 C5 E6 C5 E5 F5 A5 F5 E5 C5", "F3 C4 E4 A4 E4 C4 F3 C4 E4 A4 E4 C4"),
    "G": ("B5 G5 E5 D5 E6 D5 E5 G5 B5 G5 E5 D5", "G3 D4 E4 B4 E4 D4 G3 D4 E4 B4 E4 D4"),
    "Am": ("C6 A5 E5 C5 E6 C5 E5 A5 C6 A5 E5 C5", "A3 C4 E4 A4 E4 C4 A3 C4 E4 A4 E4 C4"),
    "G/D": ("D6 G5 E5 D5 E6 D5 E5 G5 D6 G5 E5 D5", "G3 D4 E4 B4 E4 D4 G3 D4 E4 B4 E4 D4"),
    "G/B": ("D6 G5 E5 D5 E6 D5 E5 G5 B5 G5 E5 D5", "G3 D4 E4 B4 E4 D4 G3 D4 E4 B4 E4 D4"),
    "Esus": ("E6 B5 C6 D6 E6 B5 C6 D6 E6 B5 C6 D6", "G4 D5 E5 B5 E5 D5 G4 D5 E5 B5 E5 D5"),
}


def fig(name, rh_oct=0, lh_oct=0):
    rh, lh = FIG[name]
    return (s16(rh, rh_oct), s16(lh, lh_oct))


B = {
    5: (f"{PULSE} | A4/3", "A3/3"),
    6: (f"{PULSE} | B4/6", "B3/6"),  # tied into bar 7
    7: (PULSE, "r/3"),
    8: (f"{PULSE} | A4/1 B4/1 C5/1", "A3/1 B3/1 C4/1"),
    9: (f"{PULSE} | B4/1 A4/1 B4/1", "B3/1 A3/1 B3/1"),
    10: (f"{PULSE} | C5/3", "C4/3"),
    11: (f"{PULSE} | B4/6", "B3/6"),  # tied into bar 12
    12: (PULSE, "r/3"),
    137: fig("F"), 138: fig("F"),
    139: fig("G"), 140: fig("G"),
    141: fig("Am"), 142: fig("Am"),
    143: fig("G/D"), 144: fig("G/B"),
    145: fig("F", 1, 1), 146: fig("F", 1, 1),  # 8va
    147: fig("G", 1, 1), 148: fig("G", 1, 1),
    149: fig("Am", 1, 1), 150: fig("Am", 1, 1),
    151: fig("G/D", 1, 1),
    152: (s16(FIG["Esus"][0], 1), s16(FIG["G"][1], 1)),
    153: ("[E5,E6]/3", "E5/1 E5/1 E5/1 | E4/3"),
    154: ("r/3", "E5/1 E5/1 E5/1"),
    155: ("r/3", "E5/1 E5/1 E5/1"),
    156: ("r/3", "E5/1 E5/1 E5/1"),
    157: ("r/3", "E5/3"),
}

TEMPO = 100


def short():
    s = Score()
    s.bars([B[n] for n in range(5, 13)], TEMPO, vel=(58, 50), seed=1, pedal=3)
    s.bars([B[n] for n in range(137, 145)], TEMPO, vel=(80, 66), seed=2, pedal=3)
    s.bars([B[n] for n in range(145, 153)], TEMPO, vel=(92, 76), seed=3, pedal=3)
    s.bars([B[153]], TEMPO, vel=(86, 66), seed=4, pedal=3)
    for n, v in ((154, 56), (155, 46), (156, 38), (157, 32)):
        s.bars([B[n]], TEMPO, vel=(v, v), seed=n, pedal=3)
    return s


if __name__ == "__main__":
    meta = {"composer": "Hans Zimmer", "title": "Interstellar", "keyboard": [48, 101]}
    out = os.path.join(os.path.dirname(__file__), "..", "public", "interstellar-short")
    d = short().write(out, meta)
    lo = min(n["midi"] for n in d["notes"]); hi = max(n["midi"] for n in d["notes"])
    print(f"interstellar-short: {len(d['notes'])} notes, {d['duration']}s, range {lo}-{hi}")
