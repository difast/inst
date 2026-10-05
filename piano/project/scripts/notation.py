"""Tiny text notation for transcribing scores into notes.json.

A bar is written per hand as space-separated tokens; durations are in quarter notes:
    G4/2          note (key signature applied unless an accidental is given)
    F#4/.5 Fn4/.5 explicit sharp / natural (b for flat)
    [G3,B3]/1     chord
    r/1           rest
    g:B4          grace note, played just before the next note
    a:[D3,F#3]/1  arpeggiated chord
Several voices in one hand are separated by " | " and all start at the bar start.
"""
import json
import os
import random

import mido

STEPS = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
GRACE = 0.07  # seconds
ARPEGGIO = 0.035  # seconds between arpeggiated notes


def to_midi(name, key):
    """key maps a letter to its key-signature shift, e.g. {"F": 1} or {"B": -1, "E": -1}."""
    letter, rest = name[0], name[1:]
    acc = ""
    while rest and rest[0] in "#bn":
        acc += rest[0]
        rest = rest[1:]
    n = 12 * (int(rest) + 1) + STEPS[letter]
    if acc == "#":
        return n + 1
    if acc == "b":
        return n - 1
    if acc == "n":
        return n
    return n + key.get(letter, 0)


def parse_voice(text):
    """Yields (offset_quarters, dur_quarters, pitches, kind) and returns total length."""
    events, t, pending_grace = [], 0.0, []
    for tok in text.split():
        if tok.startswith("g:"):
            pending_grace.append(tok[2:])
            continue
        kind = "note"
        if tok.startswith("a:"):
            kind, tok = "arp", tok[2:]
        body, dur = tok.rsplit("/", 1)
        dur = float(dur)
        if body != "r":
            pitches = body.strip("[]").split(",")
            for i, g in enumerate(reversed(pending_grace)):
                events.append((t, -(i + 1), [g], "grace"))
            events.append((t, dur, pitches, kind))
        pending_grace = []
        t += dur
    return events, t


class Score:
    def __init__(self, key_sharps="", key_flats=""):
        self.key = {**{c: 1 for c in key_sharps}, **{c: -1 for c in key_flats}}
        self.notes = []
        self.sections = []
        self.t = 0.0

    def section(self, label, gap=0.0):
        self.t += gap
        self.sections.append({"start": round(self.t, 3), "label": label})

    def bars(self, bars, bpm, vel=(64, 54), seed=0):
        rng = random.Random(seed)
        q = 60 / bpm
        for bar in bars:
            length = 0.0
            for hand, text, base in (("R", bar[0], vel[0]), ("L", bar[1], vel[1])):
                for voice in text.split(" | "):
                    events, total = parse_voice(voice)
                    length = max(length, total)
                    for off, dur, pitches, kind in events:
                        start = self.t + off * q
                        accent = 6 if abs(off % 1) < 1e-6 and off == 0 else 0
                        if kind == "grace":
                            start += dur * GRACE  # dur holds -index for graces
                            self._add(pitches[0], start, GRACE * 0.9, GRACE * 2, hand, base - 6)
                            continue
                        for i, p in enumerate(sorted(pitches, key=lambda p: to_midi(p, self.key))):
                            s = start + (i * ARPEGGIO if kind == "arp" else 0)
                            v = base + accent + rng.randint(-5, 5)
                            self._add(p, s, dur * q * 0.9, dur * q, hand, v)
            self.t += length * q

    def _add(self, name, start, vis_dur, sound_dur, hand, vel):
        self.notes.append({
            "midi": to_midi(name, self.key),
            "start": round(start, 4),
            "dur": round(vis_dur, 4),
            "release": round(start + sound_dur, 4),
            "hand": hand,
            "vel": max(20, min(120, vel)),
        })

    def write(self, song_dir, meta, start_offset=0.8, tail=2.0):
        for n in self.notes:
            n["start"] = round(n["start"] + start_offset, 4)
            n["release"] = round(n["release"] + start_offset, 4)
        for s in self.sections:
            s["start"] = round(s["start"] + start_offset, 3)
        end = max(n["release"] for n in self.notes)
        os.makedirs(song_dir, exist_ok=True)
        data = dict(meta, duration=round(end + tail, 2), sections=self.sections, notes=self.notes)
        with open(os.path.join(song_dir, "notes.json"), "w") as f:
            json.dump(data, f, indent=1)
        write_midi(self.notes, os.path.join(song_dir, "notes.mid"))
        return data


def write_midi(notes, path):
    mf = mido.MidiFile(ticks_per_beat=480)
    tr = mido.MidiTrack()
    mf.tracks.append(tr)
    tr.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(60)))
    ev = []
    for n in notes:
        ev.append((n["start"], 1, n["midi"], n["vel"]))
        ev.append((n["release"], 0, n["midi"], 0))
    ev.sort(key=lambda e: (e[0], e[1]))
    last = 0
    for t, on, m, v in ev:
        tick = round(t * 480)
        tr.append(mido.Message("note_on" if on else "note_off", note=m, velocity=v, time=tick - last))
        last = tick
    mf.save(path)
