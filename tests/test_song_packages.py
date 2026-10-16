"""Private song packages must not escape staging or overwrite existing songs."""

import hashlib
import stat
import zipfile
from pathlib import Path

import pytest

from drumforge.library import packages
from drumforge.library.inspect_song import chart_drums


@pytest.mark.parametrize("unsafe", ["../outside.txt", "/outside.txt", "C:/outside.txt"])
def test_rejects_unsafe_paths(tmp_path: Path, unsafe: str) -> None:
    archive = tmp_path / "unsafe.zip"
    with zipfile.ZipFile(archive, "w") as file:
        file.writestr(unsafe, b"synthetic")
    with zipfile.ZipFile(archive) as file, pytest.raises(ValueError, match="Unsafe archive path"):
        packages.check_members(file)


def test_rejects_symlinks_and_windows_collisions(tmp_path: Path) -> None:
    archive = tmp_path / "symlink.zip"
    link = zipfile.ZipInfo("song/link")
    link.create_system = 3
    link.external_attr = (stat.S_IFLNK | 0o777) << 16
    with zipfile.ZipFile(archive, "w") as file:
        file.writestr(link, "../../outside")
    with zipfile.ZipFile(archive) as file, pytest.raises(ValueError, match="symlinks"):
        packages.check_members(file)
    with zipfile.ZipFile(archive, "w") as file:
        file.writestr("song/notes.mid", b"synthetic")
        file.writestr("song/NOTES.MID", b"synthetic")
    with zipfile.ZipFile(archive) as file, pytest.raises(ValueError, match="Duplicate"):
        packages.check_members(file)
    with zipfile.ZipFile(archive, "w") as file:
        file.writestr("song/notes.mid", b"synthetic")
        file.writestr("song//notes.mid", b"synthetic")
    with zipfile.ZipFile(archive) as file, pytest.raises(ValueError, match="Duplicate"):
        packages.check_members(file)


def synthetic_archive(path: Path) -> None:
    with zipfile.ZipFile(path, "w") as file:
        file.writestr(
            "song/song.ini", "[song]\nartist = Synthetic\nname = Test\npro_drums = True\n"
        )
        file.writestr("song/notes.mid", b"synthetic chart bytes")
        file.writestr("song/song.ogg", b"synthetic audio bytes")
        file.writestr("song/credits.txt", "Synthetic fixture, no music included")
        file.writestr("song/notes.eof", b"editor-only data")


def test_curated_copy_preserves_assets_and_refuses_overwrite(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    archive = tmp_path / "song.zip"
    synthetic_archive(archive)
    original = hashlib.sha256(archive.read_bytes()).hexdigest()
    monkeypatch.setattr(packages, "inspect_song", lambda folder: {"game_verified": False})
    destination = tmp_path / "Songs" / "Synthetic"
    report = packages.prepare_zip(archive, destination)
    assert (destination / "song.ogg").read_bytes() == b"synthetic audio bytes"
    assert (destination / "notes.mid").read_bytes() == b"synthetic chart bytes"
    assert (destination / "credits.txt").is_file()
    assert not (destination / "notes.eof").exists()
    assert report["omitted_editor_files"] == ["notes.eof"]
    assert hashlib.sha256(archive.read_bytes()).hexdigest() == original
    with pytest.raises(FileExistsError, match="overwrite"):
        packages.prepare_zip(archive, destination)


def test_failed_inspection_never_publishes_a_song(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    archive = tmp_path / "song.zip"
    synthetic_archive(archive)

    def fail(folder: Path) -> None:
        raise ValueError("Unusable drum track")

    monkeypatch.setattr(packages, "inspect_song", fail)
    destination = tmp_path / "Songs" / "Synthetic"
    with pytest.raises(ValueError, match="Unusable drum track"):
        packages.prepare_zip(archive, destination)
    assert not destination.exists()
    assert list(destination.parent.iterdir()) == []


def synthetic_chart(extra: str = "") -> str:
    notes = "\n".join(f"{index * 192} = N {0 if index % 2 else 2} 0" for index in range(20))
    return (
        "[Song]\n{\nResolution = 192\n}\n"
        "[SyncTrack]\n{\n0 = B 120000\n1536 = B 60000\n}\n"
        f"[ExpertDrums]\n{{\n{notes}\n0 = N 66 0\n{extra}\n}}\n"
    )


def test_chart_tempo_changes_and_cymbal_markers() -> None:
    report = chart_drums(synthetic_chart())
    assert report["expert_note_on_count"] == 20
    assert report["kick_note_on_count"] == 10
    assert report["cymbal_marker_count"] == 1
    assert report["last_expert_onset_seconds"] == 15


def test_five_lane_chart_requires_conversion() -> None:
    with pytest.raises(ValueError, match="Five-lane"):
        chart_drums(synthetic_chart("192 = N 5 0"))
