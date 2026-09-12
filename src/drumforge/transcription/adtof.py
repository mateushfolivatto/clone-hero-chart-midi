"""Strict, subprocess-isolated adapter for the optional ADTOF backend."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import time
from collections.abc import Callable, Sequence
from pathlib import Path

from drumforge.transcription.base import TranscriptionResult

ADTOF_CHECKPOINT_SHA256 = "1bc986e596ec47ba0b44916f87cd4a39f0b2bec23596df3fb5d0e87749217320"
ADTOF_CHECKPOINT_SIZE = 3_617_805
ADTOF_REVISION = "85c192e78f716ea0b111cc8a5ee4a8f6a3a4f8a9"

CommandRunner = Callable[..., subprocess.CompletedProcess[str]]


class TranscriptionError(RuntimeError):
    """Raised when a backend cannot safely produce a raw MIDI file."""


def checkpoint_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_checkpoint(path: Path) -> Path:
    resolved = path.resolve()
    if not resolved.is_file():
        raise TranscriptionError(f"ADTOF checkpoint is not a file: {resolved}")
    try:
        size = resolved.stat().st_size
        digest = checkpoint_sha256(resolved)
    except OSError as exc:
        raise TranscriptionError(f"cannot read ADTOF checkpoint: {type(exc).__name__}") from exc
    if size != ADTOF_CHECKPOINT_SIZE or digest != ADTOF_CHECKPOINT_SHA256:
        raise TranscriptionError(
            "ADTOF checkpoint identity mismatch; expected the allowlisted Phase 1 checkpoint"
        )
    return resolved


def _validate_thresholds(
    threshold: float | None, thresholds: Sequence[float] | None
) -> tuple[float | None, tuple[float, ...] | None]:
    if threshold is not None and thresholds is not None:
        raise TranscriptionError("use either threshold or per-instrument thresholds, not both")
    if threshold is not None and not 0.0 < threshold < 1.0:
        raise TranscriptionError("threshold must be between 0 and 1")
    normalized = tuple(thresholds) if thresholds is not None else None
    if normalized is not None and (
        len(normalized) != 5 or any(not 0.0 < value < 1.0 for value in normalized)
    ):
        raise TranscriptionError("thresholds must contain five values between 0 and 1")
    return threshold, normalized


_CHILD_SCRIPT = r"""
import json
import sys
from importlib.metadata import version

import adtof_pytorch

if version("adtof-pytorch") != "0.1.0":
    raise RuntimeError("expected adtof-pytorch 0.1.0 from the allowlisted revision")

audio, midi_out, weights, threshold_json, thresholds_json = sys.argv[1:]
original_loader = adtof_pytorch.load_pytorch_weights

def strict_loader(model, path, strict=False):
    del strict
    return original_loader(model, path, strict=True)

adtof_pytorch.load_pytorch_weights = strict_loader
adtof_pytorch.transcribe_to_midi(
    audio,
    midi_out,
    weights=weights,
    device="cpu",
    threshold=json.loads(threshold_json),
    thresholds=json.loads(thresholds_json),
)
"""


class AdtofTranscriber:
    """Run allowlisted ADTOF weights on CPU without importing ML in this process."""

    name = f"adtof-pytorch@{ADTOF_REVISION[:7]}"

    def __init__(
        self,
        checkpoint: Path,
        *,
        threshold: float | None = None,
        thresholds: Sequence[float] | None = None,
        python_executable: Path | None = None,
        runner: CommandRunner = subprocess.run,
        timeout_seconds: float = 7_200,
    ) -> None:
        self.checkpoint = validate_checkpoint(checkpoint)
        self.threshold, self.thresholds = _validate_thresholds(threshold, thresholds)
        self.python_executable = (python_executable or Path(sys.executable)).absolute()
        if not self.python_executable.is_file():
            raise TranscriptionError(
                f"backend Python executable is not a file: {self.python_executable}"
            )
        self.runner = runner
        self.timeout_seconds = timeout_seconds

    def transcribe(self, source_audio: Path, midi_path: Path) -> TranscriptionResult:
        source = source_audio.resolve()
        output = midi_path.resolve()
        if not source.is_file():
            raise TranscriptionError(f"prepared audio is not a file: {source}")
        if source == output:
            raise TranscriptionError("MIDI output must differ from the input audio")
        if output.exists():
            raise TranscriptionError(f"MIDI output already exists: {output}")
        output.parent.mkdir(parents=True, exist_ok=True)
        command = [
            str(self.python_executable),
            "-c",
            _CHILD_SCRIPT,
            str(source),
            str(output),
            str(self.checkpoint),
            json.dumps(self.threshold),
            json.dumps(self.thresholds),
        ]
        started = time.monotonic()
        try:
            result = self.runner(
                command,
                capture_output=True,
                text=True,
                errors="replace",
                timeout=self.timeout_seconds,
                check=False,
                shell=False,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            output.unlink(missing_ok=True)
            raise TranscriptionError(f"ADTOF process failed: {type(exc).__name__}") from exc
        elapsed = time.monotonic() - started
        if result.returncode != 0:
            output.unlink(missing_ok=True)
            detail = (result.stderr or result.stdout or "unknown error").strip().splitlines()
            raise TranscriptionError(detail[-1] if detail else "ADTOF process failed")
        if not output.is_file() or output.stat().st_size == 0:
            output.unlink(missing_ok=True)
            raise TranscriptionError("ADTOF did not create a nonempty MIDI file")
        return TranscriptionResult(source, output, self.name, elapsed)
