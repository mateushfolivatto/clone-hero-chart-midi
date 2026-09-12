"""Probe and normalize local audio through explicit FFmpeg subprocesses."""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
from collections.abc import Callable, Sequence
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

CommandRunner = Callable[..., subprocess.CompletedProcess[str]]


class AudioPreparationError(RuntimeError):
    """Raised when input validation or the external codec boundary fails."""


@dataclass(frozen=True)
class AudioMetadata:
    duration_seconds: float
    sample_rate_hz: int
    channels: int
    codec: str

    def to_dict(self) -> dict[str, float | int | str]:
        return asdict(self)


@dataclass(frozen=True)
class PreparedAudio:
    source: Path
    output: Path
    cache_key: str
    cache_hit: bool
    source_metadata: AudioMetadata
    output_metadata: AudioMetadata

    def to_dict(self) -> dict[str, object]:
        return {
            "source": str(self.source),
            "output": str(self.output),
            "cache_key": self.cache_key,
            "cache_hit": self.cache_hit,
            "source_metadata": self.source_metadata.to_dict(),
            "output_metadata": self.output_metadata.to_dict(),
        }


def _resolve_tool(tool: str | Path, *, sibling_of: Path | None = None) -> Path:
    candidate = Path(tool)
    if candidate.parent != Path(".") or candidate.is_absolute():
        if candidate.is_file():
            return candidate.resolve()
        raise AudioPreparationError(f"executable not found: {candidate}")
    if sibling_of is not None:
        sibling = sibling_of.with_name(candidate.name)
        if sibling.is_file():
            return sibling.resolve()
    found = shutil.which(str(tool))
    if found is None:
        raise AudioPreparationError(f"{tool} not found; pass an explicit executable path")
    return Path(found).resolve()


def _run(command: Sequence[str], runner: CommandRunner) -> subprocess.CompletedProcess[str]:
    try:
        result = runner(
            list(command),
            capture_output=True,
            text=True,
            errors="replace",
            timeout=120,
            check=False,
            shell=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise AudioPreparationError(f"codec command failed: {type(exc).__name__}") from exc
    if result.returncode != 0:
        detail = (result.stderr or result.stdout or "unknown error").strip().splitlines()
        raise AudioPreparationError(detail[-1] if detail else "codec command failed")
    return result


def probe_audio(
    source: Path,
    *,
    ffprobe_path: str | Path = "ffprobe",
    runner: CommandRunner = subprocess.run,
) -> AudioMetadata:
    source = source.resolve()
    if not source.is_file():
        raise AudioPreparationError(f"input audio is not a file: {source}")
    executable = _resolve_tool(ffprobe_path)
    result = _run(
        [
            str(executable),
            "-v",
            "error",
            "-select_streams",
            "a:0",
            "-show_entries",
            "stream=codec_name,sample_rate,channels:format=duration",
            "-of",
            "json",
            str(source),
        ],
        runner,
    )
    try:
        payload: Any = json.loads(result.stdout)
        stream = payload["streams"][0]
        duration = float(payload["format"]["duration"])
        sample_rate = int(stream["sample_rate"])
        channels = int(stream["channels"])
        codec = str(stream["codec_name"])
        if duration < 0 or sample_rate <= 0 or channels <= 0:
            raise ValueError
    except (KeyError, IndexError, TypeError, ValueError, json.JSONDecodeError) as exc:
        raise AudioPreparationError("ffprobe returned invalid audio metadata") from exc
    return AudioMetadata(duration, sample_rate, channels, codec)


def _cache_key(source: Path, sample_rate_hz: int, channels: int) -> str:
    digest = hashlib.sha256()
    digest.update(f"drumforge-audio-v1\0{sample_rate_hz}\0{channels}\0".encode())
    with source.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def prepare_audio(
    source: Path,
    work_dir: Path,
    *,
    ffmpeg_path: str | Path = "ffmpeg",
    ffprobe_path: str | Path | None = None,
    sample_rate_hz: int = 44_100,
    channels: int = 1,
    runner: CommandRunner = subprocess.run,
) -> PreparedAudio:
    """Create a cached PCM WAV while leaving the source byte-for-byte untouched."""
    source = source.resolve()
    if not source.is_file():
        raise AudioPreparationError(f"input audio is not a file: {source}")
    if sample_rate_hz <= 0 or channels <= 0:
        raise AudioPreparationError("sample rate and channels must be positive")
    ffmpeg = _resolve_tool(ffmpeg_path)
    probe_tool = ffprobe_path or ffmpeg.with_name(
        "ffprobe.exe" if ffmpeg.name.lower().endswith(".exe") else "ffprobe"
    )
    ffprobe = _resolve_tool(probe_tool, sibling_of=ffmpeg)
    source_metadata = probe_audio(source, ffprobe_path=ffprobe, runner=runner)
    cache_key = _cache_key(source, sample_rate_hz, channels)
    cache_dir = work_dir.resolve() / cache_key
    output = cache_dir / "audio.wav"
    if output.is_file():
        output_metadata = probe_audio(output, ffprobe_path=ffprobe, runner=runner)
        return PreparedAudio(source, output, cache_key, True, source_metadata, output_metadata)

    cache_dir.mkdir(parents=True, exist_ok=True)
    temporary = cache_dir / "audio.partial.wav"
    command = [
        str(ffmpeg),
        "-nostdin",
        "-v",
        "error",
        "-y",
        "-i",
        str(source),
        "-vn",
        "-ac",
        str(channels),
        "-ar",
        str(sample_rate_hz),
        "-c:a",
        "pcm_s16le",
        str(temporary),
    ]
    try:
        _run(command, runner)
        if not temporary.is_file() or temporary.stat().st_size == 0:
            raise AudioPreparationError("ffmpeg did not create a nonempty WAV")
        temporary.replace(output)
    except (AudioPreparationError, OSError):
        temporary.unlink(missing_ok=True)
        raise
    output_metadata = probe_audio(output, ffprobe_path=ffprobe, runner=runner)
    if output_metadata.sample_rate_hz != sample_rate_hz or output_metadata.channels != channels:
        output.unlink(missing_ok=True)
        raise AudioPreparationError("normalized WAV does not match requested audio format")
    return PreparedAudio(source, output, cache_key, False, source_metadata, output_metadata)
