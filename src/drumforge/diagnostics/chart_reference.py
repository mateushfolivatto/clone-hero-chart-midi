"""Read existing Pro Drums charts as weak timing/lane references, not acoustic truth."""

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

from drumforge.library.inspect_song import read_config, read_drum_midi, truth

TARGET_GROUPS = ("KICK", "SNARE_PROXY", "YELLOW_CYMBAL_PROXY")
PLAYBACK_NAMES = {
    "song",
    "guitar",
    "guitar_1",
    "guitar_2",
    "rhythm",
    "bass",
    "keys",
    "vocals",
    "vocals_1",
    "vocals_2",
    "drums",
    "drums_1",
    "drums_2",
    "drums_3",
    "drums_4",
}


@dataclass(frozen=True)
class ChartOnset:
    time_seconds: float
    tick: int
    midi_note: int
    group: str
    velocity: int


def read_chart_reference(folder: Path) -> tuple[list[ChartOnset], dict[str, str | float]]:
    config = read_config(folder / "song.ini")
    if not truth(config.get("pro_drums")) or truth(config.get("five_lane_drums")):
        raise ValueError("reference requires explicit four-lane Pro Drums")
    delay = float(config.get("delay", "0")) / 1000
    if not math.isfinite(delay):
        raise ValueError("chart delay must be finite")
    midi = read_drum_midi((folder / "notes.mid").read_bytes())
    track = next(t for t in midi.tracks if t.name == "PART DRUMS")
    # Resolve marker spans first, so onsets at the same tick are order-independent.
    intervals: dict[int, list[tuple[int, int]]] = {110: [], 111: [], 112: []}
    active: dict[int, int] = {}
    tick = 0
    for msg in track:
        tick += msg.time
        if msg.type not in {"note_on", "note_off"}:
            continue
        if msg.type == "note_on" and msg.velocity > 0 and msg.note == 101:
            raise ValueError("five-lane Expert note is not a four-lane reference")
        if msg.note not in intervals:
            continue
        if msg.type == "note_on" and msg.velocity > 0:
            if msg.note in active:
                raise ValueError("overlapping tom marker starts")
            active[msg.note] = tick
        elif msg.note in active:
            start = active.pop(msg.note)
            if tick <= start:
                raise ValueError("tom marker must have positive length")
            intervals[msg.note].append((start, tick))
        else:
            raise ValueError("tom marker ends without a start")
    if active:
        raise ValueError("unterminated tom marker")
    # Keep original ticks and integrate the conductor tempo over merged messages.
    # Use explicit ticks rather than mido iteration so marker membership stays exact.
    import importlib

    mido = importlib.import_module("mido")
    seconds = 0.0
    tempo = 500_000
    tick = 0
    events = []
    for msg in mido.merge_tracks(midi.tracks):
        seconds += msg.time * tempo / (midi.ticks_per_beat * 1_000_000)
        tick += msg.time
        if msg.type == "set_tempo":
            if msg.tempo <= 0:
                raise ValueError("chart tempo must be positive")
            tempo = msg.tempo
        elif msg.type == "note_on" and msg.velocity > 0 and 96 <= msg.note <= 100:
            note = msg.note
            if note == 96:
                group = "KICK"
            elif note == 97:
                group = "SNARE_PROXY"
            else:
                color = {98: "YELLOW", 99: "BLUE", 100: "GREEN"}[note]
                tom = any(start <= tick < end for start, end in intervals[note + 12])
                group = f"{color}_TOM" if tom else f"{color}_CYMBAL_PROXY"
            events.append(ChartOnset(seconds + delay, tick, note, group, msg.velocity))
    if not events:
        raise ValueError("reference chart has no Expert drum notes")
    return events, {
        "artist": config.get("artist", ""),
        "title": config.get("name", ""),
        "charter": config.get("charter", config.get("frets", "")),
        "ini_delay_seconds": delay,
        "reference_kind": "chart lane/tom-marker proxy, not manually verified acoustic labels",
    }


def playback_assets(folder: Path) -> list[Path]:
    """Ignore preview/crowd and alternate encodings; do not double-count streams."""
    assets = sorted(
        p
        for p in folder.iterdir()
        if p.suffix.lower() in {".ogg", ".wav", ".mp3", ".opus"}
        and p.stem.lower() in PLAYBACK_NAMES
    )
    stems = [p.stem.casefold() for p in assets]
    if len(stems) != len(set(stems)):
        raise ValueError("multiple encodings of one playback stem; select a single source")
    if not any(p.stem.casefold().startswith("drums") for p in assets):
        raise ValueError("this experiment requires an existing drums stem")
    if any(p.stem.casefold() == "drums" for p in assets) and any(
        p.stem.casefold().startswith("drums_") for p in assets
    ):
        raise ValueError("both combined and component drum stems; explicit selection required")
    return assets
