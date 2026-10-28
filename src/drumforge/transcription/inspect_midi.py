"""Read raw General MIDI percussion for Phase 1 diagnostics, without rewriting it."""

from __future__ import annotations

import csv
import hashlib
import importlib
import io
import json
import shutil
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

# Diagnostic groups, not Clone Hero lanes or the future canonical event model.
GM_DRUMS = {
    35: ("BD", "acoustic_bass_drum"),
    36: ("BD", "bass_drum"),
    37: ("SD", "side_stick"),
    38: ("SD", "acoustic_snare"),
    39: ("UNKNOWN", "hand_clap"),
    40: ("SD", "electric_snare"),
    41: ("TT", "low_floor_tom"),
    42: ("HH", "closed_hi_hat"),
    43: ("TT", "high_floor_tom"),
    44: ("HH", "pedal_hi_hat"),
    45: ("TT", "low_tom"),
    46: ("HH", "open_hi_hat"),
    47: ("TT", "low_mid_tom"),
    48: ("TT", "high_mid_tom"),
    49: ("CY", "crash_cymbal_1"),
    50: ("TT", "high_tom"),
    51: ("CY", "ride_cymbal_1"),
    52: ("CY", "chinese_cymbal"),
    53: ("CY", "ride_bell"),
    54: ("UNKNOWN", "tambourine"),
    55: ("CY", "splash_cymbal"),
    57: ("CY", "crash_cymbal_2"),
    59: ("CY", "ride_cymbal_2"),
}
GROUPS = ("BD", "SD", "HH", "TT", "CY", "UNKNOWN")


class MidiInspectionError(RuntimeError):
    """Invalid/unsupported MIDI, unavailable optional parser, or unsafe output."""


@dataclass(frozen=True)
class RawMidiOnset:
    time_seconds: float
    midi_note: int
    instrument: str
    group: str
    velocity: int
    channel: int


@dataclass(frozen=True)
class MidiInspection:
    report: dict[str, Any]
    onsets: tuple[RawMidiOnset, ...]


def inspect_raw_midi(source: Path) -> MidiInspection:
    """Keep all channel-10 note-ons, duplicates and simultaneous classes included.

    Mido's merged track has tick deltas across all tracks. Apply a tempo change
    only *after* advancing to its tick. The MIDI default is 500000 us/quarter.
    No timing quantization, acoustic velocity estimation or confidence inference.
    """
    try:
        mido = importlib.import_module("mido")
    except ImportError as exc:
        raise MidiInspectionError(
            "MIDI inspection needs the diagnostics extra; run uv sync --locked --extra diagnostics"
        ) from exc
    source = source.resolve()
    try:
        data = source.read_bytes()
        midi = mido.MidiFile(file=io.BytesIO(data), clip=False)
        if midi.type not in (0, 1):
            raise ValueError("only synchronous MIDI formats 0 and 1 are supported")
        if midi.ticks_per_beat <= 0:
            raise ValueError("SMPTE/zero time division is unsupported; use PPQN MIDI")
        if any(track.name == "PART DRUMS" for track in midi.tracks):
            raise ValueError("expected raw General MIDI percussion, not Clone Hero PART DRUMS")
        tempo = 500_000
        ticks = 0
        seconds = 0.0
        ignored = 0
        onsets = []
        tempos = []
        for message in mido.merge_tracks(midi.tracks):
            seconds += message.time * tempo / (midi.ticks_per_beat * 1_000_000)
            ticks += message.time
            if message.type == "set_tempo":
                if message.tempo <= 0:
                    raise ValueError("tempo must be positive")
                tempo = message.tempo
                tempos.append(
                    {"tick": ticks, "time_seconds": seconds, "microseconds_per_quarter": tempo}
                )
            elif message.type == "note_on" and message.velocity > 0:
                if message.channel != 9:
                    ignored += 1
                    continue
                group, instrument = GM_DRUMS.get(message.note, ("UNKNOWN", "unknown"))
                onsets.append(
                    RawMidiOnset(
                        seconds, message.note, instrument, group, message.velocity, message.channel
                    )
                )
    except (OSError, ValueError, EOFError, KeyError, IndexError) as exc:
        raise MidiInspectionError(f"cannot inspect raw MIDI: {exc}") from exc
    counts = Counter(onset.group for onset in onsets)
    by_note = Counter(onset.midi_note for onset in onsets)
    warnings = []
    if not onsets:
        warnings.append("No positive-velocity note-ons on GM percussion channel 10.")
    if ignored:
        warnings.append(f"Ignored {ignored} note-ons on other MIDI channels.")
    if counts["UNKNOWN"]:
        warnings.append(
            "Unknown/unmapped percussion notes are retained; review their MIDI numbers."
        )
    return MidiInspection(
        {
            "schema_version": 1,
            "source_midi": str(source),
            "source_sha256": hashlib.sha256(data).hexdigest(),
            "midi_format": midi.type,
            "ticks_per_beat": midi.ticks_per_beat,
            "midi_duration_seconds": seconds,
            "last_onset_seconds": onsets[-1].time_seconds if onsets else None,
            "total_note_ons": len(onsets),
            "counts_by_group": {group: counts[group] for group in GROUPS},
            "counts_by_midi_note": {str(note): by_note[note] for note in sorted(by_note)},
            "ignored_nonpercussion_note_ons": ignored,
            "tempo_changes": tempos,
            "channel_numbering": "zero-based; channel 9 is GM percussion channel 10",
            "velocity_semantics": "stored MIDI velocity; not acoustic dynamics or confidence",
            "validation_scope": "raw GM note/timing inspection; audio and game not validated",
            "warnings": warnings,
        },
        tuple(onsets),
    )


def write_midi_diagnostics(source: Path, output: Path) -> dict[str, Any]:
    """Create report.json and events.csv in a new folder, preserving the source."""
    # absolute(), not resolve(): an existing symlink must also be refused.
    output = output.absolute()
    if output.exists() or output.is_symlink():
        raise MidiInspectionError(f"diagnostic output already exists: {output}")
    inspection = inspect_raw_midi(source)
    created = False
    try:
        output.mkdir(parents=True, exist_ok=False)
        created = True
        (output / "report.json").write_text(
            json.dumps(inspection.report, indent=2, ensure_ascii=True) + "\n", encoding="utf-8"
        )
        with (output / "events.csv").open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(
                stream,
                fieldnames=[
                    "time_seconds",
                    "midi_note",
                    "instrument",
                    "group",
                    "velocity",
                    "channel",
                ],
            )
            writer.writeheader()
            writer.writerows(asdict(onset) for onset in inspection.onsets)
    except OSError as exc:
        if created:
            shutil.rmtree(output)
        raise MidiInspectionError(f"cannot write MIDI diagnostics: {exc}") from exc
    return {**inspection.report, "output_directory": str(output)}
