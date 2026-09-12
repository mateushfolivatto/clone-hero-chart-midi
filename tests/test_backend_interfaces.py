from pathlib import Path

import pytest

from drumforge.audio.prepare import AudioPreparationError
from drumforge.separation import PassthroughSeparator, SeparationResult, Separator
from drumforge.transcription import Transcriber, TranscriptionResult


def test_passthrough_separator_preserves_prepared_audio(tmp_path: Path) -> None:
    source = tmp_path / "prepared.wav"
    contents = b"synthetic"
    source.write_bytes(contents)

    result = PassthroughSeparator().separate(source, tmp_path / "unused")

    assert result == SeparationResult(source.resolve(), source.resolve(), "passthrough", True)
    assert source.read_bytes() == contents


def test_passthrough_separator_rejects_missing_audio(tmp_path: Path) -> None:
    with pytest.raises(AudioPreparationError, match="not a file"):
        PassthroughSeparator().separate(tmp_path / "missing.wav", tmp_path)


def test_protocols_are_structurally_implementable(tmp_path: Path) -> None:
    class FakeSeparator:
        name = "fake-separator"

        def separate(self, source: Path, work_dir: Path) -> SeparationResult:
            return SeparationResult(source, work_dir / "drums.wav", self.name, False)

    class FakeTranscriber:
        name = "fake-transcriber"

        def transcribe(self, source_audio: Path, midi_path: Path) -> TranscriptionResult:
            return TranscriptionResult(source_audio, midi_path, self.name, 0.25)

    separator: Separator = FakeSeparator()
    transcriber: Transcriber = FakeTranscriber()
    separated = separator.separate(tmp_path / "mix.wav", tmp_path)
    transcribed = transcriber.transcribe(separated.drums_audio, tmp_path / "raw.mid")

    assert separated.backend == "fake-separator"
    assert transcribed.backend == "fake-transcriber"
    assert transcribed.elapsed_seconds == 0.25
