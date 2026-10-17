"""Collection comparison uses content/metadata while preserving all source files."""

import csv
import json
import shutil
import stat
import subprocess
import sys
import zipfile
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from drumforge.library import complement, local_library


def song(
    root: Path,
    folder: str,
    title: str,
    *,
    artist: str = "Band",
    audio: bytes | None = None,
    notes: bytes | None = None,
    extra: str = "",
    encoding: str = "utf-8",
) -> Path:
    path = root / folder
    path.mkdir(parents=True)
    (path / "song.ini").write_bytes(
        (f"[Song]\nartist = {artist}\nname = {title}\n" + extra).encode(encoding)
    )
    (path / "notes.mid").write_bytes(notes or b"MThd synthetic " + title.encode())
    (path / "song.ogg").write_bytes(audio or b"OggS synthetic " + title.encode())
    return path


def compare(old: Path, new: Path) -> tuple[list[local_library.Song], list[dict[str, str]]]:
    return local_library.compare(
        local_library.scan(old, "old")[0], local_library.scan(new, "new")[0]
    )


def test_renamed_folders_nested_packs_and_different_charts_match_by_metadata(
    tmp_path: Path,
) -> None:
    old, new = tmp_path / "old", tmp_path / "new"
    song(old, "Avange/Meu nome para a musica", "Numb", artist="<color=red>Linkin Park</color>")
    song(
        new,
        "MixDrumRock - Lote 01/Linkin Park - Numb [123]",
        "NUMB",
        artist="Linkin Park",
        notes=b"MThd different author",
        audio=b"OggS different encode",
    )
    song(old, "Fora dos lotes", "Old Only")
    selected, rows = compare(old, new)
    assert [s.title for s in selected] == ["Old Only"]
    assert [r["status"] for r in rows] == ["ja_nos_lotes", "adicionar"]


def test_identical_chart_audio_overrides_edited_ini_and_removes_internal_copy(
    tmp_path: Path,
) -> None:
    old, new = tmp_path / "old", tmp_path / "new"
    args: dict[str, Any] = {"notes": b"MThd identical", "audio": b"OggS identical"}
    song(old, "a renamed", "My edited title", artist="My edited artist", **args)
    song(new, "new", "Original name", **args)
    source = song(old, "b unique", "Unique")
    shutil.copytree(source, old / "c copy")
    selected, rows = compare(old, new)
    assert [s.title for s in selected] == ["Unique"]
    assert [r["status"] for r in rows] == ["ja_nos_lotes", "adicionar", "repetida_antiga"]


def test_partial_new_downloads_do_not_hide_old_song_and_versions_need_review(
    tmp_path: Path,
) -> None:
    old, new = tmp_path / "old", tmp_path / "new"
    partial = song(new, "incomplete", "Keep Old")
    (partial / "song.ogg").unlink()
    song(new, "valid", "Another")
    song(old, "keep", "Keep Old")
    song(old, "edition", "Another (2019 Remastered)")
    song(old, "duration", "Another", extra="song_length = 300000\n", notes=b"MThd longer version")
    (new / "valid" / "song.ini").write_text(
        "[song]\nartist = Band\nname = Another\nsong_length = 200000\n"
    )
    song(old, "live-album", "Another", extra="album = Live at Fixture\n", audio=b"OggS live")
    selected, rows = compare(old, new)
    assert [s.title for s in selected] == ["Keep Old"]
    assert sum(r["status"] == "revisar" for r in rows) == 3
    assert next(r for r in rows if r["titulo"] == "Keep Old")["status"] == "adicionar"


@pytest.mark.parametrize("encoding", ["utf-8-sig", "cp1252", "utf-16"])
def test_ini_encodings_and_case_are_portable(tmp_path: Path, encoding: str) -> None:
    path = song(tmp_path, "renamed", "Canção", artist="Bänd", encoding=encoding)
    (path / "song.ini").rename(path / "SONG.INI")
    result = local_library.scan(tmp_path, "collection")[0][0]
    assert result.key == ("band", "cancao")
    assert not result.problem


def test_unknown_metadata_and_links_are_reported_and_never_exported(tmp_path: Path) -> None:
    old, new = tmp_path / "old", tmp_path / "new"
    source = song(old, "good", "Unique")
    song(old, "unknown", "Unknown", artist="Unknown Artist")
    linked_ini = song(old, "linked ini", "Do not follow") / "song.ini"
    linked_ini.unlink()
    linked_ini.symlink_to(tmp_path / "outside.ini")
    (source / "external.ogg").symlink_to(new / "not-in-collection")
    (old / "Songs.rar").write_bytes(b"do not scan or copy archives")
    song(new, "new", "Present")
    selected, rows = compare(old, new)
    assert selected == []
    assert all(r["status"] == "revisar" for r in rows)
    warnings = local_library.scan(old, "old")[1]
    assert any("Songs.rar" in r["pasta"] for r in warnings)


def test_export_is_standalone_byte_preserving_and_wont_overwrite(tmp_path: Path) -> None:
    old, new = tmp_path / "old", tmp_path / "new"
    unique = song(old, "Pack/Minha pasta", "Old Only")
    (unique / "cover.jpg").write_bytes(b"synthetic picture")
    (unique / "backup.rar").write_bytes(b"do not copy archive")
    song(old, "Duplicate", "Present")
    song(new, "Batch/Present [id]", "Present")
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    for name in ["complement.py", "local_library.py"]:
        shutil.copyfile(Path(complement.__file__).with_name(name), scripts / name)
    output = tmp_path / "output"
    command = [
        sys.executable,
        "-S",
        str(scripts / "complement.py"),
        "--antigas",
        str(old),
        "--novas",
        str(new),
        "--destino",
        str(output),
    ]
    result = subprocess.run(command, capture_output=True, text=True, cwd=tmp_path)
    assert result.returncode == 0, result.stderr
    with zipfile.ZipFile(output / "Complemento-antigas.zip") as archive:
        assert archive.testzip() is None
        for name in ["song.ini", "notes.mid", "song.ogg", "cover.jpg"]:
            assert (
                archive.read("Complemento-antigas/Pack/Minha pasta/" + name)
                == (unique / name).read_bytes()
            )
        assert not any(n.endswith(".rar") or "Duplicate" in n for n in archive.namelist())
    with (output / "comparacao.csv").open(encoding="utf-8-sig", newline="") as file:
        rows = list(csv.DictReader(file, delimiter=";"))
    assert {r["status"] for r in rows} == {"adicionar", "ja_nos_lotes"}
    summary = json.loads((output / "resumo.json").read_text())
    assert summary["resultado"] == {"ja_nos_lotes": 1, "adicionar": 1}
    archive_before = (output / "Complemento-antigas.zip").read_bytes()
    result = subprocess.run(command, capture_output=True, text=True, cwd=tmp_path)
    assert result.returncode == 1
    assert (output / "Complemento-antigas.zip").read_bytes() == archive_before
    assert (unique / "backup.rar").read_bytes() == b"do not copy archive"


def test_overlap_paths_and_empty_new_collection_fail_before_creating_output(tmp_path: Path) -> None:
    old, new = tmp_path / "old", tmp_path / "new"
    song(old, "unique", "Unique")
    song(new, "existing", "Other")
    with pytest.raises(ValueError, match="separadas"):
        complement.export(old, old, tmp_path / "output")
    with pytest.raises(ValueError, match="fora"):
        complement.export(old, new, old / "output")
    (new / "existing" / "song.ogg").unlink()
    with pytest.raises(ValueError, match="Nenhuma musica nova completa"):
        complement.export(old, new, tmp_path / "output")
    assert not (tmp_path / "output").exists()


def test_changed_source_discards_partial_zip_without_modifying_inputs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    old, new = tmp_path / "old", tmp_path / "new"
    unique = song(old, "unique", "Unique")
    song(new, "present", "Present")
    original_compare = local_library.compare

    def mutate(*args: Any) -> Any:
        result = original_compare(*args)
        (unique / "song.ogg").write_bytes(b"user changed file")
        return result

    monkeypatch.setattr(local_library, "compare", mutate)
    output = tmp_path / "output"
    with pytest.raises(ValueError, match="mudou"):
        complement.export(old, new, output)
    assert not (output / "Complemento-antigas.zip").exists()
    assert not list(output.glob("compactando-*"))
    assert (unique / "song.ogg").read_bytes() == b"user changed file"


def test_pack_with_stray_ini_does_not_hide_nested_songs(tmp_path: Path) -> None:
    old, new = tmp_path / "old", tmp_path / "new"
    song(old, "Pack/Song", "Unique")
    (old / "Pack" / "song.ini").write_text("[song]\nartist = Pack\nname = Pack\n")
    song(new, "New", "Present")
    selected, rows = compare(old, new)
    assert [s.title for s in selected] == ["Unique"]
    assert {r["status"] for r in rows} == {"revisar", "adicionar"}


def test_zip64_boundary_works_without_a_four_gigabyte_fixture(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    old, new = tmp_path / "old", tmp_path / "new"
    song(old, "Unique", "Unique")
    song(new, "Present", "Present")
    monkeypatch.setattr(zipfile, "ZIP64_LIMIT", 200)
    output = tmp_path / "output"
    complement.export(old, new, output)
    archive_path = output / "Complemento-antigas.zip"
    assert b"PK\x06\x06" in archive_path.read_bytes()
    with zipfile.ZipFile(archive_path) as archive:
        assert archive.testzip() is None
        assert archive.read("Complemento-antigas/Unique/song.ogg") == b"OggS synthetic Unique"


def test_onedrive_cloud_files_are_not_confused_with_redirecting_junctions(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    for tag, expected in [(0x9000001A, False), (0xA0000003, True), (0xA000000C, True)]:
        monkeypatch.setattr(
            Path,
            "lstat",
            lambda path, tag=tag: SimpleNamespace(st_mode=stat.S_IFREG, st_reparse_tag=tag),
        )
        assert local_library.linked(Path("song.ogg")) is expected
