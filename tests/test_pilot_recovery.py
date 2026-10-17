"""Recovery must work without ML tools and preserve existing local collections."""

import hashlib
import io
import json
import zipfile
from pathlib import Path
from typing import Any

import pytest

from drumforge.library import recover_pilot as recovery


def synthetic_song() -> tuple[dict[str, Any], bytes]:
    content = io.BytesIO()
    files = {"song.ini": b"[song]\nname = Synthetic\nartist = Test\n", "song.ogg": b"synthetic"}
    with zipfile.ZipFile(content, "w") as archive:
        for name, data in files.items():
            archive.writestr("source/" + name, data)
    raw = content.getvalue()
    return {
        "artist": "Test",
        "title": "Synthetic",
        "charter": "Authored test fixture",
        "file_id": "a" * 32,
        "folder": "Test - Synthetic [aaaaaaaa]",
        "source_url": "https://rhythmverse.co/songfile/" + "a" * 32,
        "download_url": "https://rhythmverse.co/download_file/test/archive.zip",
        "archive_sha256": hashlib.sha256(raw).hexdigest(),
        "archive_bytes": len(raw),
        "files": [
            {
                "archive_name": "source/" + name,
                "name": name,
                "sha256": hashlib.sha256(data).hexdigest(),
            }
            for name, data in files.items()
        ],
    }, raw


def test_changed_download_is_not_published_or_left_as_a_cache(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    song, _ = synthetic_song()
    monkeypatch.setattr(recovery, "urlopen", lambda *args, **kwargs: io.BytesIO(b"wrong download"))
    with pytest.raises(ValueError, match="incompleto ou diferente"):
        recovery.download_archive(song, tmp_path)
    assert list(tmp_path.iterdir()) == []


def test_local_recovery_and_resume_need_no_ffmpeg_or_mido(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    song, raw = synthetic_song()
    monkeypatch.setattr(recovery, "urlopen", lambda *args, **kwargs: io.BytesIO(raw))
    manifest = {"schema_version": 1, "collection_folder": "Pilot", "songs": [song]}
    target = recovery.recover(manifest, tmp_path)
    with zipfile.ZipFile(target) as archive:
        assert archive.read("Songs/Pilot/Test - Synthetic [aaaaaaaa]/song.ogg") == b"synthetic"
        assert "receita-verificada.json" in archive.namelist()
    before = hashlib.sha256(target.read_bytes()).hexdigest()

    def no_network(*args: Any, **kwargs: Any) -> None:
        raise AssertionError("A verified collection must resume without network")

    monkeypatch.setattr(recovery, "urlopen", no_network)
    assert recovery.recover(manifest, tmp_path) == target
    assert hashlib.sha256(target.read_bytes()).hexdigest() == before


def test_modified_local_song_is_preserved(tmp_path: Path) -> None:
    song, raw = synthetic_song()
    archive = tmp_path / "original.zip"
    archive.write_bytes(raw)
    destination = tmp_path / "Song"
    recovery.prepare_song(song, archive, destination)
    user_file = destination / "song.ogg"
    user_file.write_bytes(b"user-modified audio")
    with pytest.raises(ValueError, match="nada foi sobrescrito"):
        recovery.prepare_song(song, archive, destination)
    assert user_file.read_bytes() == b"user-modified audio"


def test_corrupt_extracted_asset_never_publishes_destination(tmp_path: Path) -> None:
    song, raw = synthetic_song()
    song["files"][0]["sha256"] = "0" * 64
    archive = tmp_path / "original.zip"
    archive.write_bytes(raw)
    destination = tmp_path / "Song"
    with pytest.raises(ValueError, match="difere da verificacao"):
        recovery.prepare_song(song, archive, destination)
    assert not destination.exists()


def test_manifest_identity_and_paths_are_checked(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = tmp_path / "manifest.json"
    path.write_text("{}")
    with pytest.raises(ValueError, match="nao corresponde"):
        recovery.read_manifest(path)
    song, _ = synthetic_song()
    songs = [{**song, "file_id": f"{index:032x}", "folder": f"Song {index}"} for index in range(12)]
    songs[0]["files"] = [{**song["files"][0], "name": "../outside"}]
    content = json.dumps(
        {"schema_version": 1, "collection_folder": "Pilot", "songs": songs}
    ).encode()
    path.write_bytes(content)
    monkeypatch.setattr(recovery, "MANIFEST_SHA256", hashlib.sha256(content).hexdigest())
    with pytest.raises(ValueError, match="Caminho inseguro"):
        recovery.read_manifest(path)
    assert not (tmp_path / "outside").exists()


def test_ini_patch_is_byte_stable_and_preserves_author() -> None:
    result = recovery.patched_config(b"[song]\r\ncharter = Synthetic Author\r\n")
    assert b"\r" not in result
    assert b"charter = Synthetic Author\n" in result
    assert b"pro_drums = True\n" in result
