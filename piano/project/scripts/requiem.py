"""Requiem for a Dream (Clint Mansell), piano arrangement by Dustin Nagel.

All 26 bars are transcribed below; the video is a ~45 s cut (bars 8-21 + 26) with sustain pedal.
"""
import os

from notation import Score

GG = "[G1,G2]"
EB = "[Eb1,Eb2]"
DD = "[D1,D2]"
GM = "[D3,G3,Bb3]"
EBM = "[Eb3,G3,Bb3,Eb4]"
D7 = "[D3,F#3,A3,D4]"
C1, C2, C3, BB = "[Bb4,D5,G5,Bb5]", "[A4,D5,G5,A5]", "[G4,Bb4,D5,G5]", "[Bb4,Bb5]"

MOTIF_A = "Bb5/.5 A5/.5 G5/.5 D5/.5 Bb5/.5 A5/.5 G5/.5 D5/.5"
MOTIF_B = "Bb5/.5 A5/.5 G5/.5 D5/.5 C6/.5 Bb5/.5 A5/.5 Bb5/.5"
MOTIF_C = "Bb5/.5 A5/.5 G5/.5 D5/.5 C6/.5 Bb5/.5 A5/.5 G5/.5"

B = {
    1: ("r/6", "[G1,G2]/6"),  # fermata
    2: ("r/4", "[G2,G3]/4"),
    3: ("r/4", "[Eb2,Eb3]/2 [D2,D3]/2"),
    4: (MOTIF_A, "[G2,G3]/4"),
    5: (MOTIF_B, "[Eb2,Bb2,Eb3]/2 [D2,A2,D3]/2"),
    6: (MOTIF_A, "[G2,G3]/4"),
    7: (MOTIF_C, "[Eb2,Bb2,Eb3]/2 [D2,A2,D3]/2"),
    8: (MOTIF_A, "[G2,Bb2,G3]/1 Bb2/1 Bb2/1 Bb2/1"),
    9: (MOTIF_B, "[Eb2,Bb2,Eb3]/1 Bb2/1 [D2,Bb2,D3]/1 Bb2/1"),
    10: (MOTIF_A, "[G2,C3,Eb3,G3]/1 [G2,C3,Eb3]/1 [G2,C3,Eb3]/1 [G2,C3,Eb3]/1"),
    11: (MOTIF_B, "[Eb2,G2,Bb2,Eb3]/1 [Eb2,G2,Bb2]/1 [D2,F#2,A2,D3]/1 [D2,F#2,A2,D3]/1"),
    12: ("[D4,Bb4]/.5 G4/.5 r/.5 Bb4/.25 G4/.25 [D4,Bb4]/.25 G4/.5 r/.25 r/.5 Bb4/.25 G4/.25",
         "[G2,D3,G3]/1 [G2,D3]/1 [G2,D3]/1 [G2,D3]/1"),
    13: ("[Eb4,Bb4]/.25 G4/.5 r/.25 r/.5 Bb4/.25 G4/.25 "
         "[D4,Bb4]/.25 G4/.25 Bb4/.25 G4/.25 Bb4/.25 G4/.25 Bb4/.25 G4/.25",
         "[Eb2,Bb2,Eb3]/1 [Eb2,Bb2]/1 [D2,A2,D3]/1 [D2,A2]/1"),
    14: ("[D4,Bb4]/.25 A4/.5 r/.25 r/.5 Bb4/.25 A4/.25 [D4,Bb4]/.25 A4/.5 r/.25 r/.5 Bb4/.25 A4/.25",
         "[G2,D3,G3]/1 [G2,D3]/1 [G2,D3]/1 [G2,D3]/1"),
    15: ("[Eb4,Bb4]/.25 A4/.5 r/.25 r/.5 Bb4/.25 A4/.25 "
         "[D4,Bb4]/.25 A4/.25 Bb4/.25 A4/.25 Bb4/.25 A4/.25 Bb4/.25 A4/.25",
         "[Eb2,Bb2,Eb3]/1 [Eb2,Bb2]/1 [D2,F#2,A2,D3]/.5 [F#2,A2,D3,F#3]/.5 "
         "[A2,D3,F#3,A3]/.5 [D3,F#3,A3,D4]/.5"),
    16: ("[Bb4,Bb5]/.5 [G4,G5]/.5 r/.5 [Bb4,Bb5]/.25 [G4,G5]/.25 "
         "[Bb4,Bb5]/.25 [G4,G5]/.25 [G4,G5]/.25 r/.25 r/.5 [Bb4,Bb5]/.25 [G4,G5]/.25",
         f"{GG}/1 {GM}/1 {GG}/1 {GM}/1"),
    17: ("[Bb4,Bb5]/.25 [G4,G5]/.25 [G4,G5]/.25 r/.25 r/.5 [Bb4,Bb5]/.25 [G4,G5]/.25 "
         + "[Bb4,Bb5]/.25 [G4,G5]/.25 " * 4,
         f"{EB}/1 {EBM}/1 {DD}/1 {D7}/1"),
    18: ("[Bb4,Bb5]/.25 [A4,A5]/.25 [A4,A5]/.25 r/.25 r/.5 [Bb4,Bb5]/.25 [A4,A5]/.25 " * 2,
         f"{GG}/1 {GM}/1 {GG}/1 {GM}/1"),
    19: ("[Bb4,Bb5]/.25 [A4,A5]/.25 [A4,A5]/.25 r/.25 r/.5 [Bb4,Bb5]/.25 [A4,A5]/.25 "
         + "[Bb4,Bb5]/.25 [A4,A5]/.25 " * 4,
         f"{EB}/1 {EBM}/1 {DD}/1 {D7}/1"),
    20: (f"{C1}/.5 {C2}/.5 {C3}/.5 {BB}/.25 {BB}/.25 "
         f"{C1}/.25 {C2}/.25 {C2}/.25 {C2}/.25 {C3}/.5 {BB}/.25 {BB}/.25",
         f"{GG}/.25 {GG}/.25 r/.5 [G2,D3,G3]/.25 [G2,D3,G3]/.25 r/.5 "
         f"{GG}/.25 {GG}/.25 {GG}/.25 {GG}/.25 [G2,D3,G3]/.25 [G2,D3,G3]/.25 r/.5"),
    21: ("[Bb4,Eb5,G5,Bb5]/.25 " + "[A4,Eb5,G5,A5]/.25 " * 3 + "[G4,Bb4,Eb5,G5]/.5 [G4,G5]/.25 [G4,G5]/.25 "
         "[G4,Eb5,G5]/.25 " + "[A4,D5,A5]/.25 " * 3 + "[A4,D5,F#5,A5]/.25 " + "[Bb4,D5,F#5,Bb5]/.25 " * 3,
         f"{EB}/.25 {EB}/.25 {EB}/.25 {EB}/.25 [Eb2,Bb2,Eb3]/.25 [Eb2,Bb2,Eb3]/.25 r/.5 "
         f"{DD}/.25 {DD}/.25 {DD}/.25 {DD}/.25 [D2,A2,D3]/.25 [D2,A2,D3]/.25 r/.5"),
    22: ("Bb4/.5 A4/.5 G4/.5 D4/.5 Bb4/.5 A4/.5 G4/.5 D4/.5", "[G2,G3]/4"),
    23: ("Bb4/.5 A4/.5 G4/.5 D4/.5 C5/.5 Bb4/.5 A4/.5 Bb4/.5", "[Eb2,Eb3]/2 [D2,D3]/2"),
    26: ("G4/5", "[G1,G2]/5"),
}
B[24], B[25] = B[22], B[23]

TEMPO = 90


def bars(*nums):
    return [B[n] for n in nums]


def short():
    """~45 s cut for Reels: theme with chords, the build-up and the fff climax, then the final G."""
    s = Score(key_flats="BE")
    s.bars(bars(8, 9, 10, 11), TEMPO, vel=(70, 60), seed=6, pedal=2)
    s.bars(bars(12, 13, 14, 15), TEMPO, vel=(82, 70), seed=8, pedal=2)
    s.bars(bars(16, 17, 18, 19), TEMPO, vel=(94, 82), seed=10, pedal=2)
    s.bars(bars(20, 21), TEMPO, vel=(106, 94), seed=12, pedal=2)
    s.bars(bars(26), 64, vel=(56, 52), seed=46, pedal=5)
    return s


if __name__ == "__main__":
    meta = {"composer": "Clint Mansell", "title": "Requiem for a Dream", "keyboard": [24, 84]}
    for name, build in (("requiem-short", short),):
        out = os.path.join(os.path.dirname(__file__), "..", "public", name)
        d = build().write(out, meta)
        print(f"{name}: {len(d['notes'])} notes, {d['duration']}s")
