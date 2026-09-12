"""Backend-neutral raw MIDI transcription contract."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


@dataclass(frozen=True)
class TranscriptionResult:
    source_audio: Path
    midi_path: Path
    backend: str
    elapsed_seconds: float

    def to_dict(self) -> dict[str, str | float]:
        return {
            "source_audio": str(self.source_audio),
            "midi_path": str(self.midi_path),
            "backend": self.backend,
            "elapsed_seconds": self.elapsed_seconds,
        }


class Transcriber(Protocol):
    """Convert prepared audio into backend-native raw drum MIDI."""

    @property
    def name(self) -> str: ...

    def transcribe(self, source_audio: Path, midi_path: Path) -> TranscriptionResult: ...
