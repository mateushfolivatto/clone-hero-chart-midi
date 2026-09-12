import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from drumforge.transcription.adtof import (
    ADTOF_CHECKPOINT_SHA256,
    AdtofTranscriber,
    TranscriptionError,
)


def _checkpoint(tmp_path: Path) -> Path:
    path = tmp_path / "weights.pth"
    path.write_bytes(b"x")
    return path


def test_checkpoint_identity_is_required(tmp_path: Path) -> None:
    with pytest.raises(TranscriptionError, match="identity mismatch"):
        AdtofTranscriber(_checkpoint(tmp_path))


def test_missing_checkpoint_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(TranscriptionError, match="not a file"):
        AdtofTranscriber(tmp_path / "missing.pth")


def test_missing_backend_python_is_rejected(tmp_path: Path) -> None:
    checkpoint = _checkpoint(tmp_path)
    with (
        patch("drumforge.transcription.adtof.ADTOF_CHECKPOINT_SIZE", 1),
        patch(
            "drumforge.transcription.adtof.checkpoint_sha256",
            return_value=ADTOF_CHECKPOINT_SHA256,
        ),
        pytest.raises(TranscriptionError, match="Python executable"),
    ):
        AdtofTranscriber(checkpoint, python_executable=tmp_path / "missing-python")


def test_backend_python_symlink_is_not_resolved(tmp_path: Path) -> None:
    checkpoint = _checkpoint(tmp_path)
    base_python = tmp_path / "base-python"
    base_python.touch()
    venv_python = tmp_path / "venv-python"
    venv_python.symlink_to(base_python)
    with (
        patch("drumforge.transcription.adtof.ADTOF_CHECKPOINT_SIZE", 1),
        patch(
            "drumforge.transcription.adtof.checkpoint_sha256",
            return_value=ADTOF_CHECKPOINT_SHA256,
        ),
    ):
        transcriber = AdtofTranscriber(checkpoint, python_executable=venv_python)
    assert transcriber.python_executable == venv_python.absolute()


def test_threshold_validation(tmp_path: Path) -> None:
    checkpoint = _checkpoint(tmp_path)
    with (
        patch("drumforge.transcription.adtof.ADTOF_CHECKPOINT_SIZE", 1),
        patch("drumforge.transcription.adtof.ADTOF_CHECKPOINT_SHA256", ADTOF_CHECKPOINT_SHA256),
        patch(
            "drumforge.transcription.adtof.checkpoint_sha256", return_value=ADTOF_CHECKPOINT_SHA256
        ),
    ):
        with pytest.raises(TranscriptionError, match="either threshold"):
            AdtofTranscriber(checkpoint, threshold=0.5, thresholds=[0.5] * 5)
        with pytest.raises(TranscriptionError, match="five values"):
            AdtofTranscriber(checkpoint, thresholds=[0.5] * 4)


def test_runs_isolated_on_cpu_and_requires_nonempty_midi(tmp_path: Path) -> None:
    source = tmp_path / "prepared.wav"
    source.write_bytes(b"wav")
    checkpoint = _checkpoint(tmp_path)
    midi = tmp_path / "raw.mid"
    calls: list[list[str]] = []

    def runner(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        assert kwargs["shell"] is False
        assert 'device="cpu"' in command[2]
        calls.append(command)
        midi.write_bytes(b"MThd")
        return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

    with (
        patch("drumforge.transcription.adtof.ADTOF_CHECKPOINT_SIZE", 1),
        patch(
            "drumforge.transcription.adtof.checkpoint_sha256", return_value=ADTOF_CHECKPOINT_SHA256
        ),
    ):
        result = AdtofTranscriber(checkpoint, runner=runner).transcribe(source, midi)

    assert result.midi_path == midi.resolve()
    assert result.backend.startswith("adtof-pytorch@")
    assert calls[0][3] == str(source.resolve())
    assert calls[0][5] == str(checkpoint.resolve())


def test_failed_backend_removes_partial_output(tmp_path: Path) -> None:
    source = tmp_path / "prepared.wav"
    source.write_bytes(b"wav")
    checkpoint = _checkpoint(tmp_path)
    midi = tmp_path / "raw.mid"

    def runner(command: list[str], **_: object) -> subprocess.CompletedProcess[str]:
        midi.write_bytes(b"partial")
        return subprocess.CompletedProcess(command, 1, stdout="", stderr="backend failed")

    with (
        patch("drumforge.transcription.adtof.ADTOF_CHECKPOINT_SIZE", 1),
        patch(
            "drumforge.transcription.adtof.checkpoint_sha256", return_value=ADTOF_CHECKPOINT_SHA256
        ),
    ):
        transcriber = AdtofTranscriber(checkpoint, runner=runner)
        with pytest.raises(TranscriptionError, match="backend failed"):
            transcriber.transcribe(source, midi)
    assert not midi.exists()


def test_existing_midi_is_not_overwritten(tmp_path: Path) -> None:
    source = tmp_path / "prepared.wav"
    source.write_bytes(b"wav")
    checkpoint = _checkpoint(tmp_path)
    midi = tmp_path / "raw.mid"
    midi.write_bytes(b"existing")
    with (
        patch("drumforge.transcription.adtof.ADTOF_CHECKPOINT_SIZE", 1),
        patch(
            "drumforge.transcription.adtof.checkpoint_sha256",
            return_value=ADTOF_CHECKPOINT_SHA256,
        ),
    ):
        transcriber = AdtofTranscriber(checkpoint)
        with pytest.raises(TranscriptionError, match="already exists"):
            transcriber.transcribe(source, midi)
    assert midi.read_bytes() == b"existing"


def test_transcribe_requires_explicit_skip_separation(tmp_path: Path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "drumforge",
            "transcribe",
            str(tmp_path / "input.wav"),
            "--midi-out",
            str(tmp_path / "raw.mid"),
            "--weights",
            str(tmp_path / "weights.pth"),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 2
    assert "pass --skip-separation" in result.stderr
