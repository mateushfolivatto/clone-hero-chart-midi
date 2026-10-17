"""Public catalog versions, resumable batches and portable conversion contracts."""

import csv
import hashlib
import io
import json
import subprocess
import zipfile
from pathlib import Path
from typing import Any

import pytest

from drumforge.library import delivery, onyx_recovery, packages, recover_pilot, rhythmverse
from drumforge.library import inspect_song as inspection


def candidate(title: str = "Song", artist: str = "Band", duration: int = 200) -> dict[str, Any]:
    return {
        "data": {"artist": artist, "title": title, "live": 0},
        "file": {
            "file_id": "a" * 32,
            "diff_drums": 0,
            "file_artist": artist,
            "file_title": title,
            "file_song_length": duration,
            "gameformat": "ch",
            "file_url_full": "https://rhythmverse.co/songfile/test",
            "download_url": "/download_file/test/song.zip",
        },
    }


def test_matching_preserves_live_covers_and_large_duration_differences() -> None:
    row = {"artist": "Band", "title": "Song (2018 Remaster)", "duration_seconds": "200"}
    songs = [
        candidate(),
        candidate("Song (Live)"),
        candidate(artist="Tribute Band"),
        candidate(duration=240),
    ]
    for number, item in enumerate(songs):
        item["file"]["file_id"] = f"{number:032x}"
    result = rhythmverse.candidates(row, songs)
    assert len(result) == 2
    assert not result[0]["version_review"]
    assert result[1]["version_review"]
    assert result[0]["match_basis"].endswith("master not established")


def test_ordinary_drums_are_explicit_and_do_not_gain_a_false_pro_flag(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    ini = b"[song]\nname = Synthetic\nartist = Fixture\npro_drums = False\n"
    (tmp_path / "song.ini").write_bytes(ini)
    notes = "\n".join(f"{n * 192} = N {n % 5} 0" for n in range(25))
    chart = (
        "[Song]\n{\nResolution = 192\n}\n[SyncTrack]\n{\n0 = B 120000\n}\n"
        f"[ExpertDrums]\n{{\n{notes}\n}}\n"
    )
    (tmp_path / "notes.chart").write_text(chart)
    (tmp_path / "song.ogg").write_bytes(b"synthetic audio")
    from subprocess import CompletedProcess

    monkeypatch.setattr(
        subprocess,
        "run",
        lambda *a, **kw: CompletedProcess(
            a[0],
            0,
            stdout=json.dumps({"format": {"duration": "30"}, "streams": [{"codec_type": "audio"}]}),
        ),
    )
    with pytest.raises(ValueError, match="explicit Pro Drums"):
        inspection.inspect_song(tmp_path)
    result = inspection.inspect_song(tmp_path, require_pro=False)
    assert result["drums"]["expert_note_on_count"] == 25
    assert result["drums"]["pro_drums_evidence"] is False
    assert (tmp_path / "song.ini").read_bytes() == ini


def test_empty_catalog_and_repeated_page_are_distinct(tmp_path: Path) -> None:
    artist = "Band"
    prefix = "ch-" + hashlib.sha256(artist.encode()).hexdigest()[:12]
    first = tmp_path / (prefix + "-1.json")
    first.write_text(json.dumps({"data": {"songs": False, "records": {"total_filtered": 0}}}))
    assert rhythmverse.search(artist, "ch", tmp_path) == []
    response = {"data": {"songs": [candidate()], "records": {"total_filtered": 2}}}
    first.write_text(json.dumps(response))
    (tmp_path / (prefix + "-2.json")).write_text(json.dumps(response))
    with pytest.raises(ValueError, match="repeated"):
        rhythmverse.search(artist, "ch", tmp_path)


def test_uppercase_ini_and_missing_pro_flag_use_existing_midi_markers(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source = tmp_path / "source.zip"
    with zipfile.ZipFile(source, "w") as archive:
        archive.writestr(
            "Song/song.ini", "[Song]\nartist = Band\nname = Song\n//C3 conversion credit\n"
        )
        archive.writestr("Song/notes.mid", b"synthetic MIDI")
        archive.writestr("Song/song.ogg", b"synthetic audio")
    monkeypatch.setattr(packages, "midi_drums", lambda data: {"tom_marker_count": 1})
    monkeypatch.setattr(packages, "inspect_song", lambda folder: {})
    target = tmp_path / "prepared"
    report = packages.prepare_zip(source, target)
    assert report["configuration_changes"]
    assert b"[Song]" in (target / "song.ini").read_bytes()
    assert b"pro_drums = True" in (target / "song.ini").read_bytes()
    assert (target / "notes.mid").read_bytes() == b"synthetic MIDI"


def test_catalog_join_duplicates_are_deduplicated_without_rejecting_the_artist(
    tmp_path: Path,
) -> None:
    prefix = "ch-" + hashlib.sha256(b"Band").hexdigest()[:12]
    response = {
        "data": {
            "songs": [candidate(), candidate()],
            "records": {"total_filtered": 1},
            "pagination": {"start": 0, "page": "1"},
        }
    }
    (tmp_path / (prefix + "-1.json")).write_text(json.dumps(response))
    assert len(rhythmverse.search("Band", "ch", tmp_path)) == 1


def test_public_folder_assets_recover_and_resume_without_external_libraries(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    content = b"synthetic audio"
    digest = hashlib.sha256(content).hexdigest()
    song: dict[str, Any] = {
        "file_id": "a" * 32,
        "folder": "Band - Song",
        "artist": "Band",
        "title": "Song",
        "charter": "Fixture author",
        "source_url": "https://rhythmverse.co/songfile/test",
        "archive_format": "files",
        "files": [
            {
                "name": "song.ogg",
                "archive_name": "song.ogg",
                "download_url": "https://drive.google.com/uc?id=synthetic",
                "source_sha256": digest,
                "bytes": len(content),
                "sha256": digest,
            }
        ],
    }
    monkeypatch.setattr(recover_pilot, "urlopen", lambda *a, **kw: io.BytesIO(content))
    manifest = {"songs": [song], "collection_folder": "Batch", "archive_name": "Batch.zip"}
    archive = recover_pilot.recover(manifest, tmp_path)
    assert archive.is_file()
    monkeypatch.setattr(recover_pilot, "urlopen", lambda *a, **kw: pytest.fail("network on resume"))
    assert recover_pilot.recover(manifest, tmp_path) == archive


def test_one_failed_song_does_not_block_later_songs(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    songs = [
        {
            "file_id": str(n),
            "folder": f"Song{n}",
            "artist": "Band",
            "title": str(n),
            "charter": "Test",
            "source_url": "https://example.com",
            "files": [],
        }
        for n in range(2)
    ]
    completed = []

    def recover(song: dict[str, Any], destination: Path, root: Path) -> dict[str, Any]:
        if song["file_id"] == "0":
            raise ValueError("Temporary network failure")
        completed.append(song["file_id"])
        return song

    monkeypatch.setattr(recover_pilot, "recover_song", recover)
    manifest = {"songs": songs, "collection_folder": "Batch", "archive_name": "Batch.zip"}
    with pytest.raises(ValueError, match="1 musica"):
        recover_pilot.recover(manifest, tmp_path)
    assert completed == ["1"]
    assert (tmp_path / "Batch-falhas.json").is_file()
    assert len(list(tmp_path.glob("Batch-parcial-*.zip"))) == 1


def test_onyx_output_hashes_are_local_but_midi_is_pinned_and_edits_are_preserved(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    midi = b"synthetic MIDI"
    song: dict[str, Any] = {
        "file_id": "test",
        "archive_sha256": "source hash",
        "files": [
            {"name": "notes.mid", "sha256": hashlib.sha256(midi).hexdigest()},
            {"name": "song.ogg", "sha256": "different cloud Ogg hash"},
        ],
    }

    def build(executable: Path, source: Path, project: Path, target: Path) -> None:
        with zipfile.ZipFile(target, "w") as archive:
            archive.writestr("Song/notes.mid", midi)
            archive.writestr("Song/song.ogg", b"OggS synthetic local serial")

    monkeypatch.setattr(onyx_recovery, "install", lambda root: Path("mock-converter"))
    monkeypatch.setattr(onyx_recovery, "build", build)
    destination = tmp_path / "Songs" / "Test"
    result = onyx_recovery.prepare(song, tmp_path / "source", destination, tmp_path)
    assert result["files"][1]["sha256"] != song["files"][1]["sha256"]
    monkeypatch.setattr(onyx_recovery, "install", lambda root: pytest.fail("install on resume"))
    assert onyx_recovery.prepare(song, tmp_path / "source", destination, tmp_path) == result
    (destination / "song.ogg").write_bytes(b"user edit")
    with pytest.raises(ValueError, match="nada foi sobrescrito"):
        onyx_recovery.prepare(song, tmp_path / "source", destination, tmp_path)
    assert (destination / "song.ogg").read_bytes() == b"user edit"


def test_incremental_delivery_keeps_existing_recipes_and_appends_only_new_charts(
    tmp_path: Path,
) -> None:
    root = tmp_path / "private"
    metadata = tmp_path / "metadata"
    metadata.mkdir()
    for helper in ["onyx_recovery.py", "sevenzip.py", "mega_recovery.py"]:
        (metadata / helper).write_text("synthetic helper")
    catalog = root / "reports" / "search-rest"
    catalog.mkdir(parents=True)
    receipts = root / "reports" / "prepared"
    receipts.mkdir()
    entries = []
    for number, title in enumerate(["Song", "New Song"]):
        identity = ("a" if number == 0 else "b") * 32
        entry = candidate(title)
        entry["file"]["file_id"] = identity
        entries.append(entry)
        folder = root / "Songs" / "MixDrumRock - Continuacao" / title
        folder.mkdir(parents=True)
        content = b"synthetic asset"
        (folder / "notes.mid").write_bytes(content)
        receipt = {
            "file_id": identity,
            "folder": title,
            "artist": "Band",
            "title": title,
            "archive_format": "zip",
            "archive_bytes": 100,
            "source_url": "https://rhythmverse.co/songfile/test",
            "files": [{"name": "notes.mid", "sha256": hashlib.sha256(content).hexdigest()}],
        }
        (receipts / (identity + ".json")).write_text(json.dumps(receipt))
    (catalog / "catalog.json").write_text(json.dumps({"data": {"songs": entries}}))
    playlist = tmp_path / "playlist.csv"

    def write_playlist(count: int) -> None:
        with playlist.open("w", newline="") as file:
            writer = csv.DictWriter(
                file,
                fieldnames=[
                    "artist",
                    "title",
                    "duration_seconds",
                    "qobuz_track_id",
                    "playlist_track_id",
                ],
            )
            writer.writeheader()
            for number, title in enumerate(["Song", "New Song"][:count]):
                writer.writerow(
                    {
                        "artist": "Band",
                        "title": title,
                        "duration_seconds": "200",
                        "qobuz_track_id": str(number),
                        "playlist_track_id": str(number),
                    }
                )

    write_playlist(1)
    delivery.freeze(playlist, root, metadata, tmp_path / "coverage.csv")
    original = (metadata / "collection_02.json").read_bytes()
    write_playlist(2)
    index = delivery.freeze(playlist, root, metadata, tmp_path / "coverage.csv")
    assert index["unique_new_charts"] == 2
    assert [batch["number"] for batch in index["batches"]] == [2, 3]
    assert (metadata / "collection_02.json").read_bytes() == original
    before = (metadata / "collection_index.json").read_bytes()
    delivery.freeze(playlist, root, metadata, tmp_path / "coverage.csv")
    assert (metadata / "collection_index.json").read_bytes() == before
