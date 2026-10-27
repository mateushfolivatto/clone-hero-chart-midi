"""Read existing Pro Drums charts as weak timing/lane references, not acoustic truth."""

from __future__ import annotations

import math
import re
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
    velocity: int | None


def chart_asset(folder: Path) -> Path:
    for name in ("notes.mid", "notes.chart"):
        path = folder / name
        if path.is_file():
            return path
    raise ValueError("reference folder needs notes.mid or notes.chart")


def read_chart_reference(folder: Path) -> tuple[list[ChartOnset], dict[str, str | float]]:
    config = read_config(folder / "song.ini")
    if not truth(config.get("pro_drums")) or truth(config.get("five_lane_drums")):
        raise ValueError("reference requires explicit four-lane Pro Drums")
    delay = float(config.get("delay", "0")) / 1000
    if not math.isfinite(delay):
        raise ValueError("chart delay must be finite")
    path = chart_asset(folder)
    offset = 0.0
    if path.suffix == ".chart":
        events, offset = _text_chart_events(path, delay)
    else:
        events = _midi_chart_events(path, delay)
    return events, {
        "artist": config.get("artist", ""),
        "title": config.get("name", ""),
        "charter": config.get("charter", config.get("frets", "")),
        "ini_delay_seconds": delay,
        "chart_offset_seconds": offset,
        "chart_format": path.suffix.lstrip("."),
        "note_semantics": "Expert MIDI lanes 96-100; .chart lanes mapped only for comparison",
        "velocity_semantics": "stored MIDI velocity or null for .chart; not acoustic dynamics",
        "reference_kind": "chart lane/tom-marker proxy, not manually verified acoustic labels",
    }


def _midi_chart_events(path: Path, delay: float) -> list[ChartOnset]:
    midi = read_drum_midi(path.read_bytes())
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
    return events


def _text_chart_events(path: Path, delay: float) -> tuple[list[ChartOnset], float]:
    pairs = re.findall(
        r"(?ms)^\[([^]]+)\]\s*\{\s*(.*?)^\s*\}", path.read_text(encoding="utf-8-sig")
    )
    if len({name for name, _ in pairs}) != len(pairs):
        raise ValueError("duplicate .chart section")
    sections = dict(pairs)
    resolution_match = re.search(r"(?m)^\s*Resolution\s*=\s*(\d+)\s*$", sections.get("Song", ""))
    if not resolution_match or int(resolution_match[1]) <= 0:
        raise ValueError(".chart needs a positive Resolution")
    resolution = int(resolution_match[1])
    offset_match = re.search(r"(?m)^\s*Offset\s*=\s*(\S+)\s*$", sections.get("Song", ""))
    offset = float(offset_match[1]) if offset_match else 0.0
    if not math.isfinite(offset):
        raise ValueError(".chart offset must be finite")
    tempos = sorted(
        (int(t), int(b))
        for t, b in re.findall(r"(?m)^\s*(\d+)\s*=\s*B\s+(\d+)\s*$", sections.get("SyncTrack", ""))
    )
    if (
        not tempos
        or tempos[0][0] != 0
        or any(b <= 0 for _, b in tempos)
        or len({t for t, _ in tempos}) != len(tempos)
    ):
        raise ValueError(".chart needs unique positive tempo events starting at tick zero")
    notes = [
        (int(t), int(n))
        for t, n in re.findall(
            r"(?m)^\s*(\d+)\s*=\s*N\s+(\d+)\s+\d+\s*$", sections.get("ExpertDrums", "")
        )
    ]
    if any(note == 5 for _, note in notes):
        raise ValueError("five-lane .chart is not a four-lane reference")
    gems = [(tick, note) for tick, note in notes if 0 <= note <= 4]
    flags = {(tick, note - 64) for tick, note in notes if 66 <= note <= 68}
    if not flags.issubset(set(gems)):
        raise ValueError(".chart cymbal flag has no same-tick colored note")
    events = []
    segment = 0
    previous_tick = 0
    elapsed = 0.0
    for tick, note in sorted(gems):
        while segment + 1 < len(tempos) and tempos[segment + 1][0] <= tick:
            boundary = tempos[segment + 1][0]
            elapsed += (boundary - previous_tick) * 60_000 / tempos[segment][1] / resolution
            previous_tick = boundary
            segment += 1
        seconds = elapsed + (tick - previous_tick) * 60_000 / tempos[segment][1] / resolution
        if note <= 1:
            group = "KICK" if note == 0 else "SNARE_PROXY"
        else:
            color = {2: "YELLOW", 3: "BLUE", 4: "GREEN"}[note]
            group = f"{color}_CYMBAL_PROXY" if (tick, note) in flags else f"{color}_TOM"
        events.append(ChartOnset(seconds + delay + offset, tick, note + 96, group, None))
    if not events:
        raise ValueError("reference .chart has no ExpertDrums notes")
    return events, offset


def playback_assets(folder: Path, *, require_drums: bool = True) -> list[Path]:
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
    if not assets:
        raise ValueError("no recognized playback audio")
    if require_drums and not any(p.stem.casefold().startswith("drums") for p in assets):
        raise ValueError("this experiment requires an existing drums stem")
    if any(p.stem.casefold() == "drums" for p in assets) and any(
        p.stem.casefold().startswith("drums_") for p in assets
    ):
        raise ValueError("both combined and component drum stems; explicit selection required")
    return assets
