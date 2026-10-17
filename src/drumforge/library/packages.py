"""Safely stage runtime assets from one song ZIP; keep original archives intact."""

from __future__ import annotations

import argparse
import configparser
import hashlib
import json
import re
import shutil
import stat
import subprocess
import tempfile
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any

from drumforge.library.inspect_song import (
    AUDIO_EXTENSIONS,
    chart_drums,
    inspect_song,
    midi_drums,
    truth,
)


def check_members(archive: zipfile.ZipFile) -> None:
    seen = set()
    total = 0
    for info in archive.infolist():
        name = info.filename.replace("\\", "/")
        path = PurePosixPath(name)
        if path.is_absolute() or ".." in path.parts or ":" in name:
            raise ValueError("Unsafe archive path")
        if stat.S_ISLNK(info.external_attr >> 16):
            raise ValueError("Archive symlinks are not supported")
        canonical = path.as_posix().casefold()
        if canonical in seen:
            raise ValueError("Duplicate archive path on Windows")
        seen.add(canonical)
        total += info.file_size
        if total > 800 * 1024 * 1024:
            raise ValueError("Uncompressed song exceeds the pilot's 800 MiB limit")


def safe_folder_name(artist: str, title: str, file_id: str) -> str:
    label = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", f"{artist} - {title}")
    label = label.strip(" .")[:140].rstrip(" .")
    suffix = re.sub(r"[^A-Za-z0-9]", "", file_id)[:8]
    if not label or not suffix:
        raise ValueError("Invalid song identity")
    return f"{label} [{suffix}]"


def prepare_zip(
    archive_path: Path, destination: Path, *, require_pro: bool = True
) -> dict[str, Any]:
    if destination.exists():
        raise FileExistsError("Refusing to overwrite an existing song folder")
    destination.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive_path) as archive:
        check_members(archive)
        if archive.testzip() is not None:
            raise ValueError("ZIP integrity check failed")
        configs = [
            name for name in archive.namelist() if PurePosixPath(name).name.casefold() == "song.ini"
        ]
        if len(configs) != 1:
            raise ValueError("Expected one song.ini per archive")
        root = PurePosixPath(configs[0]).parent
        copied = []
        skipped = []
        changes = []
        with tempfile.TemporaryDirectory(
            prefix="song-prepare-", dir=destination.parent
        ) as temporary:
            folder = Path(temporary) / "song"
            folder.mkdir()
            for name in archive.namelist():
                path = PurePosixPath(name)
                if name.endswith("/"):
                    continue
                basename = path.name.casefold()
                keep = path.parent == root and (
                    basename
                    in {
                        "song.ini",
                        "notes.mid",
                        "notes.chart",
                        "readme.txt",
                        "credits.txt",
                        "license.txt",
                        "album.png",
                        "album.jpg",
                        "album.jpeg",
                        "background.png",
                        "background.jpg",
                        "background.jpeg",
                    }
                    or path.suffix.casefold() in AUDIO_EXTENSIONS
                )
                if not keep:
                    skipped.append(
                        str(path.relative_to(root)) if path.is_relative_to(root) else name
                    )
                    continue
                if re.search(r'[<>:"/\\|?*\x00-\x1f]', path.name) or path.name.endswith((" ", ".")):
                    raise ValueError("Runtime asset has a Windows-incompatible name")
                target_name = (
                    basename if basename in {"song.ini", "notes.mid", "notes.chart"} else path.name
                )
                with archive.open(name) as source, (folder / target_name).open("wb") as target:
                    shutil.copyfileobj(source, target)
                copied.append(target_name)
            # .chart cymbal markers are preserved; make their intended mode explicit.
            configuration = configparser.ConfigParser(
                interpolation=None, strict=False, comment_prefixes=("#", ";", "//")
            )
            configuration.read(folder / "song.ini", encoding="utf-8-sig")
            section = configuration[
                next(name for name in configuration.sections() if name.casefold() == "song")
            ]
            if not truth(section.get("pro_drums")) and not truth(section.get("five_lane_drums")):
                evidence = (
                    midi_drums((folder / "notes.mid").read_bytes())
                    if (folder / "notes.mid").exists()
                    else chart_drums((folder / "notes.chart").read_text(encoding="utf-8-sig"))
                )
                if evidence.get("cymbal_marker_count") or evidence.get("tom_marker_count"):
                    section["pro_drums"] = "True"
                    with (folder / "song.ini").open("w", encoding="utf-8", newline="\n") as file:
                        configuration.write(file)
                    changes.append("Added pro_drums=True from existing drum markers")
            report = (
                inspect_song(folder) if require_pro else inspect_song(folder, require_pro=False)
            )
            hashes = {
                path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                for path in sorted(folder.iterdir())
                if path.is_file()
            }
            if destination.exists():
                raise FileExistsError("Destination appeared during preparation")
            folder.rename(destination)
    return {
        **report,
        "copied_files": copied,
        "omitted_editor_files": skipped,
        "configuration_changes": changes,
        "files_sha256": hashes,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path, help="Original single-song ZIP")
    parser.add_argument("--output-dir", type=Path, required=True, help="New song folder")
    args = parser.parse_args()
    try:
        report = prepare_zip(args.archive, args.output_dir)
    except (
        OSError,
        ValueError,
        KeyError,
        configparser.Error,
        zipfile.BadZipFile,
        subprocess.CalledProcessError,
        subprocess.TimeoutExpired,
        ImportError,
    ) as exc:
        parser.exit(1, f"Preparation failed: {type(exc).__name__}: {exc}\n")
    print(json.dumps({"song_folder": str(args.output_dir), **report}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
