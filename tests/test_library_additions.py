"""New batches are compared with actual installed songs before export."""

import csv
import json
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

from drumforge.library import complement, local_library


def song(
    root: Path,
    folder: str,
    title: str,
    *,
    artist: str = "Band",
    notes: bytes | None = None,
    audio: bytes | None = None,
) -> Path:
    target = root / folder
    target.mkdir(parents=True)
    (target / "song.ini").write_text(f"[song]\nartist = {artist}\nname = {title}\n")
    (target / "notes.mid").write_bytes(notes or b"MThd synthetic " + title.encode())
    (target / "song.ogg").write_bytes(audio or b"OggS synthetic " + title.encode())
    return target


def test_shared_chart_with_edited_metadata_and_other_audio_requires_review(tmp_path: Path) -> None:
    candidates, installed = tmp_path / "candidates", tmp_path / "installed"
    song(candidates, "new", "Edited title", notes=b"identical chart", audio=b"other audio")
    song(installed, "old renamed", "Known", notes=b"identical chart", audio=b"original audio")
    selected, rows = local_library.compare(
        local_library.scan(candidates, "candidates")[0],
        local_library.scan(installed, "installed")[0],
    )
    assert not selected
    assert rows[0]["status"] == "revisar"
    assert "Chart identico" in rows[0]["motivo"]
    assert rows[0]["pasta_correspondente"] == "old renamed"


def test_platform_annotation_does_not_silently_add_an_existing_song(tmp_path: Path) -> None:
    candidates, installed = tmp_path / "candidates", tmp_path / "installed"
    song(candidates, "New source", "One Step Closer (RB3 Version)", notes=b"new chart")
    song(installed, "My old copy", "One Step Closer", notes=b"installed chart")
    summary = complement.export(candidates, installed, tmp_path / "output", additions=True)
    assert summary["resultado"] == {"revisar": 1}
    with zipfile.ZipFile(tmp_path / "output/Novas-musicas.zip") as archive:
        assert archive.namelist() == ["LEIA-ME.txt"]


def test_standalone_additions_export_skips_installed_and_internal_copies(tmp_path: Path) -> None:
    candidates, installed = tmp_path / "candidates", tmp_path / "installed"
    song(candidates, "Batch/Given Up", "Given Up", artist="Linkin Park")
    unique = song(candidates, "Batch/New Song", "New Song", artist="Linkin Park")
    shutil.copytree(unique, candidates / "Copy")
    present = song(installed, "My renamed folder", "Given Up", artist="Linkin Park")
    before = {p.name: p.read_bytes() for p in present.iterdir()}
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    for name in ["additions.py", "complement.py", "local_library.py"]:
        shutil.copy2(Path(complement.__file__).with_name(name), scripts / name)
    output = tmp_path / "output"
    result = subprocess.run(
        [
            sys.executable,
            "-I",
            "-S",
            "-c",
            "import runpy,sys; sys.path.insert(0,sys.argv[1]); "
            "sys.argv=sys.argv[2:]; runpy.run_path(sys.argv[0],run_name='__main__')",
            str(scripts),
            str(scripts / "additions.py"),
            "--candidatas",
            str(candidates),
            "--biblioteca",
            str(installed),
            "--destino",
            str(output),
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    with zipfile.ZipFile(output / "Novas-musicas.zip") as archive:
        assert archive.testzip() is None
        assert archive.read("Novas-musicas/Batch/New Song/song.ogg") == b"OggS synthetic New Song"
        assert not any("Given Up" in name or "/Copy/" in name for name in archive.namelist())
    with (output / "comparacao.csv").open(encoding="utf-8-sig", newline="") as file:
        rows = list(csv.DictReader(file, delimiter=";"))
    assert {r["status"] for r in rows} == {
        "ja_na_biblioteca",
        "adicionar",
        "repetida_candidata",
    }
    assert all("pasta_candidata" in r and "pasta_biblioteca" in r for r in rows)
    summary = json.loads((output / "resumo.json").read_text())
    assert summary["candidatas_lidas"] == 3
    assert summary["biblioteca_prontas"] == 1
    assert {p.name: p.read_bytes() for p in present.iterdir()} == before


def test_additions_can_target_an_empty_library_without_weakening_complement(tmp_path: Path) -> None:
    candidates, installed = tmp_path / "candidates", tmp_path / "installed"
    song(candidates, "Batch/Unique", "Unique")
    installed.mkdir()
    result = complement.export(candidates, installed, tmp_path / "output", additions=True)
    assert result["biblioteca_prontas"] == 0
    assert result["resultado"] == {"adicionar": 1}
    with zipfile.ZipFile(tmp_path / "output/Novas-musicas.zip") as archive:
        assert archive.read("Novas-musicas/Batch/Unique/notes.mid") == b"MThd synthetic Unique"
