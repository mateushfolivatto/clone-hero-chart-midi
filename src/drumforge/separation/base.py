"""Separation contract and the no-separation baseline."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from drumforge.audio.prepare import AudioPreparationError


@dataclass(frozen=True)
class SeparationResult:
    source: Path
    drums_audio: Path
    backend: str
    skipped: bool


class Separator(Protocol):
    """Boundary implemented by optional drum-isolation backends."""

    @property
    def name(self) -> str: ...

    def separate(self, source: Path, work_dir: Path) -> SeparationResult: ...


class PassthroughSeparator:
    """Explicitly skip separation and pass the prepared full mix onward."""

    name = "passthrough"

    def separate(self, source: Path, work_dir: Path) -> SeparationResult:
        del work_dir
        resolved = source.resolve()
        if not resolved.is_file():
            raise AudioPreparationError(f"prepared audio is not a file: {resolved}")
        return SeparationResult(resolved, resolved, self.name, True)
