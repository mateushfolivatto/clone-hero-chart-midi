"""Catalog platform labels must not override the downloaded container format."""

import io
import json
import subprocess
import zipfile
from pathlib import Path
from typing import Any

import pytest

from drumforge.library import acquire, onyx_recovery


def native_zip(title: str = "Song") -> bytes:
    chart = (
        "[Song]\n{\nResolution = 192\n}\n"
        "[SyncTrack]\n{\n0 = B 120000\n}\n"
        "[ExpertDrums]\n{\n"
        + "\n".join(f"{n * 192} = N {n % 5} 0" for n in range(25))
        + "\n0 = N 66 0\n}\n"
    )
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w") as archive:
        archive.writestr(
            "Song/song.ini", f"[song]\nartist = Fixture\nname = {title}\npro_drums = True\n"
        )
        archive.writestr("Song/notes.chart", chart)
        archive.writestr("Song/song.ogg", b"synthetic audio")
    return output.getvalue()


@pytest.mark.parametrize(
    ("catalog_game", "console", "title", "accepted"),
    [
        ("rb3xbox", False, "Song", True),
        ("ch", True, "Song", True),
        ("ch", False, "<color=#FFA500>Song</color>", True),
        ("ch", False, "<color=#FFA500>Song (Live)</color>", False),
    ],
)
def test_actual_container_selects_native_or_onyx_preparation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    catalog_game: str,
    console: bool,
    title: str,
    accepted: bool,
) -> None:
    package = native_zip(title)
    source = b"CON synthetic STFS" if console else package
    conversions = []

    def fetch(url: str, target: Path, referer: str) -> Path:
        target.write_bytes(source)
        return target

    def build(executable: Path, raw: Path, project: Path, target: Path) -> None:
        assert raw.read_bytes() == source
        conversions.append(executable)
        target.write_bytes(package)

    def probe(*args: Any, **kwargs: Any) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(
            args[0],
            0,
            stdout=json.dumps({"format": {"duration": "30"}, "streams": [{"codec_type": "audio"}]}),
        )

    monkeypatch.setattr(acquire, "fetch", fetch)
    monkeypatch.setattr(onyx_recovery, "build", build)
    monkeypatch.setattr(subprocess, "run", probe)
    candidate = {
        "file_id": "format-fixture",
        "artist": "Fixture",
        "title": "Song",
        "game": catalog_game,
        "download_url": "https://example.com/source",
        "source_url": "https://example.com/catalog",
    }
    if not accepted:
        with pytest.raises(ValueError, match="title differs"):
            acquire.acquire_native(candidate, tmp_path)
        assert not list((tmp_path / "Songs/MixDrumRock - Continuacao").iterdir())
        assert (tmp_path / "downloads/rest/format-fixture/original").read_bytes() == source
        return
    receipt = acquire.acquire_native(candidate, tmp_path, Path("audited-onyx") if console else None)
    assert receipt["archive_format"] == ("onyx" if console else "zip")
    assert conversions == ([Path("audited-onyx")] if console else [])
    folder = tmp_path / "Songs/MixDrumRock - Continuacao" / receipt["folder"]
    with zipfile.ZipFile(io.BytesIO(package)) as archive:
        assert (folder / "notes.chart").read_bytes() == archive.read("Song/notes.chart")
        assert (folder / "song.ogg").read_bytes() == archive.read("Song/song.ogg")
        assert (folder / "song.ini").read_bytes() == archive.read("Song/song.ini")
    assert (tmp_path / "downloads/rest/format-fixture/original").read_bytes() == source
