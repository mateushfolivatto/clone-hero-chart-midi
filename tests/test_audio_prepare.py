import hashlib
import json
import subprocess
from pathlib import Path

import pytest

from drumforge.audio.prepare import AudioPreparationError, prepare_audio, probe_audio


def _tools(tmp_path: Path) -> tuple[Path, Path]:
    ffmpeg = tmp_path / "tools with spaces" / "ffmpeg.exe"
    ffprobe = ffmpeg.with_name("ffprobe.exe")
    ffmpeg.parent.mkdir()
    ffmpeg.touch()
    ffprobe.touch()
    return ffmpeg, ffprobe


def _metadata(sample_rate: int = 48_000, channels: int = 2) -> str:
    return json.dumps(
        {
            "streams": [
                {"codec_name": "pcm_s16le", "sample_rate": str(sample_rate), "channels": channels}
            ],
            "format": {"duration": "2.5"},
        }
    )


def test_probe_parses_metadata_and_uses_argument_list(tmp_path: Path) -> None:
    source = tmp_path / "song.wav"
    source.write_bytes(b"audio")
    _, ffprobe = _tools(tmp_path)
    calls: list[list[str]] = []

    def runner(command: list[str], **_: object) -> subprocess.CompletedProcess[str]:
        calls.append(command)
        return subprocess.CompletedProcess(command, 0, stdout=_metadata(), stderr="")

    metadata = probe_audio(source, ffprobe_path=ffprobe, runner=runner)
    assert metadata.duration_seconds == 2.5
    assert metadata.sample_rate_hz == 48_000
    assert metadata.channels == 2
    assert calls[0][-1] == str(source.resolve())


def test_prepare_preserves_source_and_reuses_content_cache(tmp_path: Path) -> None:
    source = tmp_path / "private song.mp3"
    original = b"private-audio-bytes"
    source.write_bytes(original)
    ffmpeg, ffprobe = _tools(tmp_path)
    calls: list[list[str]] = []

    def runner(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        assert kwargs["shell"] is False
        calls.append(command)
        if Path(command[0]) == ffmpeg.resolve():
            Path(command[-1]).write_bytes(b"normalized")
            return subprocess.CompletedProcess(command, 0, stdout="", stderr="")
        normalized = Path(command[-1]).suffix == ".wav"
        return subprocess.CompletedProcess(
            command,
            0,
            stdout=_metadata(44_100, 1) if normalized else _metadata(),
            stderr="",
        )

    first = prepare_audio(source, tmp_path / "cache", ffmpeg_path=ffmpeg, runner=runner)
    second = prepare_audio(source, tmp_path / "cache", ffmpeg_path=ffmpeg, runner=runner)
    assert source.read_bytes() == original
    assert first.output.read_bytes() == b"normalized"
    assert not first.cache_hit
    assert second.cache_hit
    assert first.cache_key == second.cache_key
    assert first.cache_key != hashlib.sha256(original).hexdigest()
    assert sum(Path(call[0]) == ffmpeg.resolve() for call in calls) == 1
    assert ffprobe.resolve() == Path(calls[0][0])


def test_cache_changes_with_content(tmp_path: Path) -> None:
    source = tmp_path / "song.wav"
    source.write_bytes(b"one")
    ffmpeg, _ = _tools(tmp_path)

    def runner(command: list[str], **_: object) -> subprocess.CompletedProcess[str]:
        if Path(command[0]) == ffmpeg.resolve():
            Path(command[-1]).write_bytes(b"normalized")
        return subprocess.CompletedProcess(command, 0, stdout=_metadata(44_100, 1), stderr="")

    first = prepare_audio(source, tmp_path / "cache", ffmpeg_path=ffmpeg, runner=runner)
    source.write_bytes(b"two")
    second = prepare_audio(source, tmp_path / "cache", ffmpeg_path=ffmpeg, runner=runner)
    assert first.cache_key != second.cache_key


def test_invalid_probe_output_is_rejected(tmp_path: Path) -> None:
    source = tmp_path / "song.wav"
    source.touch()
    _, ffprobe = _tools(tmp_path)

    def runner(command: list[str], **_: object) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(command, 0, stdout="{}", stderr="")

    with pytest.raises(AudioPreparationError, match="invalid audio metadata"):
        probe_audio(source, ffprobe_path=ffprobe, runner=runner)


def test_missing_input_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(AudioPreparationError, match="not a file"):
        prepare_audio(tmp_path / "missing.mp3", tmp_path / "cache")
