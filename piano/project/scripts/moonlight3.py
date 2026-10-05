"""Moonlight Sonata, 3rd movement (L. van Beethoven, Op. 27 No. 2), Mutopia edition.

~33 s cut for Reels: the opening (bars 1-14, ending on the G# fermata),
then straight to the final bars 197-201 that close in C# minor. Sustain pedal throughout.
"""
import os

from notation import Score


def s16(notes):
    return " ".join(f"{n}/.25" for n in notes.split())


def e8(notes):
    return " ".join(f"{n}/.5" for n in notes.split())


B = {
    1: ("r/.25 " + s16("G#2 C#3 E3 G#3 C#3 E3 G#3 C#4 E3 G#3 C#4 E4 G#3 C#4 E4"),
        e8("C#2 G#2 C#2 G#2 C#2 G#2 C#2 G#2")),
    2: (s16("G#4 C#4 E4 G#4 C#5 E4 G#4 C#5 E5 G#4 C#5 E5") + " [G#4,C#5,E5,G#5]/.5 [G#4,C#5,E5,G#5]/.5",
        e8("C#2 G#2 C#2 G#2 C#2 G#2 [C#2,C#3] G#2")),
    3: ("r/.25 " + s16("G#2 B#2 D#3 G#3 B#2 D#3 G#3 B#3 D#3 G#3 B#3 D#4 G#3 B#3 D#4"),
        e8("B#1 G#2 B#1 G#2 B#1 G#2 B#1 G#2")),
    4: (s16("G#4 B#3 D#4 G#4 B#4 D#4 G#4 B#4 D#5 G#4 B#4 D#5") + " [G#4,B#4,D#5,G#5]/.5 [G#4,B#4,D#5,G#5]/.5",
        e8("B#1 G#2 B#1 G#2 B#1 G#2 [B#1,B#2] G#2")),
    5: ("r/.25 " + s16("C#3 E#3 G#3 C#4 E#3 G#3 C#4 E#4 G#3 C#4 E#4 G#4 C#4 E#4 G#4"),
        e8("B1 G#2 B1 G#2 B1 G#2 B1 G#2")),
    6: (s16("C#5 E#4 G#4 C#5 E#5 G#4 C#5 E#5 G#5 C#5 E#5 G#5") + " [C#5,E#5,G#5,C#6]/.5 [C#5,E#5,G#5,C#6]/.5",
        e8("B1 G#2 B1 G#2 B1 G#2 [B1,B2] G#2")),
    7: ("r/.25 " + s16("C#3 F#3 A3 C#4 C#4 F#4 A4 C#5 C#5 F#5 A5") + " [C#5,F#5,C#6]/.5 [C#5,F#5,C#6]/.5",
        e8("A1 A2 A1 A2 A1 A2 A1 A2")),
    8: ("r/.25 " + s16("C#3 E3 F##3 C#4 C#4 E4 F##4 C#5 C#5 E5 F##5") + " [C#5,F##5,C#6]/.5 [C#5,F##5,C#6]/.5",
        e8("A1 A2 A1 A2 A1 A2 A1 A2")),
    9: ("[B#4,G#5,B#5]/.5 " + s16("G#4 G#5 G#4 G#5 A#4 G#5 B#4 G#5 C#5 G#5 D#5 G#5 B#4 G#5"),
        "[G#1,G#2]/.5 " + e8("B#3 B#3 C#4 D#4 E4 F#4 D#4") + " | r/.5 G#3/7.5"),
    10: (s16("D#5 G#5 C#5 G#5 F#5 G#5 E5 G#5 D#5 G#5 C#5 G#5 B#4 G#5 An4 F##5"),
         e8("F#4 E4 A4 G#4 F#4 E4 D#4 C#4")),
    11: (s16("G#4 G#5 G#4 G#5 G#4 G#5 A#4 G#5 B#4 G#5 C#5 G#5 D#5 G#5 B#4 G#5"),
         e8("B#3 B#3 B#3 C#4 D#4 E4 F#4 D#4") + " | G#3/8"),
    12: (s16("D#5 G#5 C#5 G#5 F#5 G#5 E5 G#5 D#5 G#5 C#5 G#5 B#4 G#5 An4 F##5"),
         e8("F#4 E4 A4 G#4 F#4 E4 D#4 C#4")),
    13: (s16("G#4 G#5 An4 F##5 " * 4),
         e8("[G#3,B#3] [G#3,C#4] " * 4)),
    14: ("[G#4,G#5]/1 G#3/5", "[G#3,B#3]/1 [G#1,G#2]/5"),  # fermata
    197: ("g:E4 g:C#5 " + s16("G#5 E4 G#4 C#5 E5 G#4 C#5 E5 G#5 C#5 E5 G#5 C#6 E5 G#5 C#6"),
          "[C#2,G#2,C#3]/.25 " + s16("E3 G#3 C#4 E4 G#3 C#4 E4 G#4 C#4 E4 G#4 C#5 E4 G#4 C#5")),
    198: (s16("E6 C#6 G#5 E5 C#6 G#5 E5 C#5 G#5 E5 C#5 G#4 E5 C#5 G#4 E4"),
          s16("E5 C#5 G#4 E4 C#5 G#4 E4 C#4 G#4 E4 C#4 G#3 E4 C#4 G#3 E3")),
    199: (s16("C#5 G#4 E4 C#4 G#4 E4 C#4 G#3") + " r/2",
          s16("C#4 G#3 E3 C#3 G#3 E3 C#3 G#2") + " "
          + s16("[E3,E4] [C#3,C#4] [G#2,G#3] [E2,E3] [C#3,C#4] [G#2,G#3] [E2,E3] [G#2,G#3]")),
    200: ("r/2 [C#5,E5,G#5,C#6]/1 r/1", "[C#2,C#3]/1 r/1 [C#2,E2,G#2,C#3]/1 r/1"),
    201: ("[C#4,E4,G#4,C#5]/2.5", "[C#2,E2,G#2,C#3]/2.5"),
}

TEMPO = 160  # Presto agitato, quarter note


def short():
    s = Score(key_sharps="FCGD")
    s.section("III. Presto agitato")
    s.bars([B[1], B[2], B[3], B[4]], TEMPO, vel=(62, 54), seed=1, pedal=2)
    s.bars([B[5], B[6], B[7], B[8]], TEMPO, vel=(70, 60), seed=2, pedal=2)
    s.bars([B[n] for n in range(9, 14)], TEMPO, vel=(84, 66), seed=3, pedal=2)
    s.bars([B[14]], TEMPO, vel=(92, 80), seed=4, pedal=6)
    s.bars([B[197], B[198], B[199]], TEMPO, vel=(90, 78), seed=5, pedal=2)
    s.bars([B[200], B[201]], TEMPO, vel=(104, 92), seed=6, pedal=1)
    return s


if __name__ == "__main__":
    meta = {"composer": "Ludwig van Beethoven", "title": "Moonlight Sonata", "keyboard": [28, 91]}
    out = os.path.join(os.path.dirname(__file__), "..", "public", "moonlight3-short")
    d = short().write(out, meta)
    lo = min(n["midi"] for n in d["notes"]); hi = max(n["midi"] for n in d["notes"])
    print(f"moonlight3-short: {len(d['notes'])} notes, {d['duration']}s, range {lo}-{hi}")
