"""Inspect four-lane drum charts and decode their audio without changing media."""

from __future__ import annotations

import configparser
import importlib
import io
import json
import re
import subprocess
from collections import Counter
from pathlib import Path
from typing import Any

AUDIO_EXTENSIONS = {".ogg", ".opus", ".mp3", ".wav"}


def read_config(path: Path) -> configparser.SectionProxy:
    parser = configparser.ConfigParser(
        interpolation=None, strict=False, comment_prefixes=("#", ";", "//")
    )
    parser.read_string(path.read_text(encoding="utf-8-sig"))
    return parser[next(section for section in parser.sections() if section.casefold() == "song")]


def truth(value: str | None) -> bool:
    return (value or "").strip().casefold() in {"true", "1", "yes"}


def read_drum_midi(data: bytes) -> Any:
    """Parse the original conductor and PART DRUMS chunks with strict mido.

    Other instrument tracks can contain Phase Shift's extended SysEx bytes,
    unsupported by mido. They are outside this drum-only check; the delivered
    MIDI stays byte-for-byte intact. Never enable mido's generic clipping mode.
    """
    mido = importlib.import_module("mido")
    if data[:4] != b"MThd" or len(data) < 14:
        raise ValueError("Invalid MIDI header")
    header_length = int.from_bytes(data[4:8], "big")
    if header_length != 6 or int.from_bytes(data[8:10], "big") != 1:
        raise ValueError("This pilot inspector requires format-1 MIDI")
    count = int.from_bytes(data[10:12], "big")
    position = 14
    selected = []
    for index in range(count):
        if data[position : position + 4] != b"MTrk":
            raise ValueError("Missing MIDI track chunk")
        length = int.from_bytes(data[position + 4 : position + 8], "big")
        end = position + 8 + length
        if end > len(data):
            raise ValueError("Truncated MIDI track")
        chunk = data[position:end]
        if index == 0 or b"\xff\x03\x0aPART DRUMS" in chunk:
            selected.append(chunk)
        position = end
    if position != len(data):
        raise ValueError("Unexpected data after MIDI chunks")
    header = bytearray(data[:14])
    header[10:12] = len(selected).to_bytes(2, "big")
    midi = mido.MidiFile(file=io.BytesIO(bytes(header) + b"".join(selected)))
    drum_tracks = [track for track in midi.tracks if track.name == "PART DRUMS"]
    if len(drum_tracks) != 1:
        raise ValueError("Expected exactly one PART DRUMS track")
    if midi.ticks_per_beat <= 0:
        raise ValueError("Expected positive PPQN, not SMPTE time division")
    if midi.tracks[0].name != "PART DRUMS" and any(
        message.type == "note_on" for message in midi.tracks[0]
    ):
        raise ValueError("Unexpected note events in the conductor track")
    return midi


def midi_drums(data: bytes) -> dict[str, Any]:
    midi = read_drum_midi(data)
    drum_tracks = [track for track in midi.tracks if track.name == "PART DRUMS"]
    counts = Counter(
        message.note
        for message in drum_tracks[0]
        if message.type == "note_on" and message.velocity > 0
    )
    if counts[101]:
        raise ValueError("Five-lane Expert note 101 requires a separate conversion")
    seconds = last_onset = 0.0
    for message in midi:
        seconds += message.time
        if message.type == "note_on" and message.velocity > 0 and 96 <= message.note <= 100:
            last_onset = seconds
    gems = sum(counts[note] for note in range(96, 101))
    if gems < 20 or counts[96] == 0:
        raise ValueError("No usable Expert drums/kick notes")
    return {
        "format": "mid",
        "expert_note_on_count": gems,
        "kick_note_on_count": counts[96],
        "tom_marker_count": sum(counts[note] for note in range(110, 113)),
        "last_expert_onset_seconds": round(last_onset, 3),
        "validation_scope": "conductor and PART DRUMS; other instruments unverified",
    }


def chart_drums(text: str) -> dict[str, Any]:
    sections = dict(re.findall(r"(?ms)^\[([^]]+)\]\s*\{\s*(.*?)^\s*\}", text))
    if "ExpertDrums" not in sections:
        raise ValueError("No ExpertDrums section")
    resolution_match = re.search(r"Resolution\s*=\s*(\d+)", sections.get("Song", ""))
    if not resolution_match or int(resolution_match[1]) <= 0:
        raise ValueError("No valid chart resolution")
    resolution = int(resolution_match[1])
    notes = [
        (int(tick), int(note))
        for tick, note in re.findall(
            r"(?m)^\s*(\d+)\s*=\s*N\s+(\d+)\s+\d+\s*$", sections["ExpertDrums"]
        )
    ]
    counts = Counter(note for _, note in notes)
    if counts[5]:
        raise ValueError("Five-lane chart requires a separate conversion")
    gems = [(tick, note) for tick, note in notes if 0 <= note <= 4]
    if len(gems) < 20 or counts[0] == 0:
        raise ValueError("No usable Expert drums/kick notes")
    tempos = sorted(
        (int(tick), int(bpm))
        for tick, bpm in re.findall(
            r"(?m)^\s*(\d+)\s*=\s*B\s+(\d+)\s*$", sections.get("SyncTrack", "")
        )
    )
    if not tempos or tempos[0][0] != 0 or any(bpm <= 0 for _, bpm in tempos):
        raise ValueError("No valid chart tempo map")
    last_tick = max(tick for tick, _ in gems)
    seconds = 0.0
    for index, (tick, bpm) in enumerate(tempos):
        if tick >= last_tick:
            break
        end = min(last_tick, tempos[index + 1][0] if index + 1 < len(tempos) else last_tick)
        seconds += (end - tick) * 60000 / bpm / resolution
    offset = re.search(r"Offset\s*=\s*(-?[\d.]+)", sections.get("Song", ""))
    if offset:
        seconds += float(offset[1])
    return {
        "format": "chart",
        "expert_note_on_count": len(gems),
        "kick_note_on_count": counts[0],
        "cymbal_marker_count": sum(counts[note] for note in range(66, 69)),
        "last_expert_onset_seconds": round(seconds, 3),
        "validation_scope": "ExpertDrums and tempo map; other instruments unverified",
    }


def inspect_song(folder: Path, *, require_pro: bool = True) -> dict[str, Any]:
    config = read_config(folder / "song.ini")
    if not config.get("name") or not config.get("artist"):
        raise ValueError("song.ini needs name and artist")
    if truth(config.get("five_lane_drums")):
        raise ValueError("Five-lane drums need a separate conversion")
    if (folder / "notes.mid").is_file():
        result = midi_drums((folder / "notes.mid").read_bytes())
    else:
        result = chart_drums((folder / "notes.chart").read_text(encoding="utf-8-sig"))
    result["pro_drums_configured"] = truth(config.get("pro_drums"))
    result["pro_drums_evidence"] = bool(
        result["pro_drums_configured"]
        and (result.get("tom_marker_count", 0) or result.get("cymbal_marker_count", 0))
    )
    if require_pro and not result["pro_drums_evidence"]:
        raise ValueError("This pilot requires explicit Pro Drums configuration and markers")
    audio: list[dict[str, Any]] = []
    for path in sorted(folder.iterdir()):
        if path.suffix.casefold() not in AUDIO_EXTENSIONS:
            continue
        response = subprocess.run(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration:stream=codec_type",
                "-of",
                "json",
                str(path),
            ],
            check=True,
            capture_output=True,
            text=True,
            timeout=30,
        )
        data = json.loads(response.stdout)
        if not any(stream["codec_type"] == "audio" for stream in data["streams"]):
            raise ValueError(f"No audio stream: {path.name}")
        duration = float(data["format"]["duration"])
        if duration <= 0:
            raise ValueError(f"Invalid duration: {path.name}")
        subprocess.run(
            [
                "ffmpeg",
                "-nostdin",
                "-v",
                "error",
                "-xerror",
                "-i",
                str(path),
                "-map",
                "0:a:0",
                "-f",
                "null",
                "-",
            ],
            check=True,
            capture_output=True,
            timeout=120,
        )
        audio.append({"file": path.name, "duration_seconds": round(duration, 3), "decoded": True})
    if not audio:
        raise ValueError("No audio assets")
    last_onset = result["last_expert_onset_seconds"] + float(config.get("delay", "0")) / 1000
    if last_onset > max(asset["duration_seconds"] for asset in audio) + 1:
        raise ValueError("Drum notes extend beyond the audio")
    return {
        "artist": config["artist"],
        "title": config["name"],
        "charter": config.get("charter", "Unknown"),
        "drums": result,
        "audio": audio,
        "game_verified": False,
    }
