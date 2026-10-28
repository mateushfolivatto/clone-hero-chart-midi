"""Acquire public native-song packages for inspection; never replace source media."""

from __future__ import annotations

import hashlib
import importlib
import json
import re
import tempfile
import zipfile
from pathlib import Path
from typing import Any
from urllib.parse import quote, urlparse
from urllib.request import Request, urlopen

from drumforge.library.packages import check_members, prepare_zip, safe_folder_name
from drumforge.library.recover_pilot import digest_file, resolve_public_download, verify_song
from drumforge.library.rhythmverse import normalized, title_key

MAX_BYTES = 512 * 1024 * 1024


def drive_download_url(url: str) -> str:
    match = re.search(r"/file/d/([A-Za-z0-9_-]+)", url)
    if urlparse(url).hostname == "drive.google.com" and match:
        return "https://drive.google.com/uc?export=download&id=" + match[1]
    return url


def resolve_drive_url(url: str) -> str:
    if urlparse(url).hostname == "drive.google.com" and urlparse(url).path == "/open":
        with urlopen(url, timeout=60) as response:
            url = response.geturl()
    return drive_download_url(url)


def fetch(url: str, target: Path, source: str) -> Path:
    if target.is_file():
        return target
    target.parent.mkdir(parents=True, exist_ok=True)
    if urlparse(url).hostname in {"mega.nz", "mega.co.nz"}:
        from drumforge.library.mega_recovery import download

        with tempfile.TemporaryDirectory(prefix="mega-", dir=target.parent) as temporary:
            partial = Path(temporary) / "source"
            download(url, partial, MAX_BYTES)
            if target.exists():
                raise FileExistsError("Download destination appeared")
            partial.rename(target)
        return target
    with tempfile.TemporaryDirectory(prefix="download-", dir=target.parent) as temporary:
        partial = Path(temporary) / "source"
        with urlopen(Request(url, headers={"Referer": source}), timeout=90) as response:
            declared = response.headers.get("Content-Length", "")
            if declared.isdigit() and int(declared) > MAX_BYTES:
                raise ValueError("Download exceeds 512 MiB budget")
            if "text/html" in response.headers.get("Content-Type", ""):
                page = response.read(128 * 1024).decode("utf-8", errors="replace")
                if "quota exceeded" in page.casefold():
                    raise ValueError("Google Drive download quota exceeded; source unavailable now")
                raise ValueError("Source returned a web page; interaction or link review required")
            size = 0
            with partial.open("wb") as output:
                while block := response.read(1024 * 1024):
                    size += len(block)
                    if size > MAX_BYTES:
                        raise ValueError("Download exceeds 512 MiB budget")
                    output.write(block)
            if not size:
                raise ValueError("Source returned an empty file")
        if target.exists():
            raise FileExistsError("Download destination appeared")
        partial.rename(target)
    return target


def source_zip(raw: Path, target: Path, root: Path) -> str:
    """Inspect non-ZIP containers with the pinned portable reader, retaining raw input."""
    if zipfile.is_zipfile(raw):
        return "zip"
    with raw.open("rb") as file:
        signature = file.read(8)
    if not signature.startswith((b"Rar!", b"7z\xbc\xaf\x27\x1c")):
        raise ValueError("Source is not a supported ZIP/RAR/7z archive")
    from drumforge.library.sevenzip import as_zip

    as_zip(raw.absolute(), target.absolute(), root.absolute())
    with zipfile.ZipFile(target) as archive:
        check_members(archive)
    return "rar" if signature.startswith(b"Rar!") else "7z"


def drive_folder(candidate: dict[str, Any], cache: Path, target: Path) -> dict[str, Any]:
    gdown = importlib.import_module("gdown")
    index = cache / "folder-index.json"
    if index.exists():
        files = json.loads(index.read_text(encoding="utf-8"))
    else:
        listing = gdown.download_folder(
            url=candidate["download_url"],
            skip_download=True,
            quiet=True,
            use_cookies=False,
            output=str(cache / "listing"),
        )
        if not listing:
            raise ValueError("Public folder is unavailable or empty")
        files = [{"id": item.id, "path": item.path} for item in listing]
        index.parent.mkdir(parents=True, exist_ok=True)
        index.write_text(json.dumps(files), encoding="utf-8")
    # A song folder may contain editor files, but never fetch a whole shared library.
    if len(files) > 40 or sum(Path(item["path"]).name.lower() == "song.ini" for item in files) != 1:
        raise ValueError("Shared folder is not a single song; manual selection required")
    assets = {}
    with zipfile.ZipFile(target, "w") as archive:
        for item in files:
            path = Path(item["path"])
            if len(path.parts) != 1:
                continue
            if path.suffix.lower() not in {
                ".ogg",
                ".opus",
                ".mp3",
                ".wav",
                ".mid",
                ".chart",
                ".ini",
                ".jpg",
                ".jpeg",
                ".png",
                ".txt",
            }:
                continue
            url = "https://drive.google.com/uc?export=download&id=" + item["id"]
            raw = fetch(url, cache / item["id"], candidate["source_url"])
            content = raw.read_bytes()
            archive.writestr(item["path"], content)
            assets[item["path"]] = {
                "download_url": url,
                "source_sha256": hashlib.sha256(content).hexdigest(),
                "bytes": len(content),
            }
    return assets


def acquire_native(
    candidate: dict[str, Any],
    root: Path,
    onyx_executable: Path | None = None,
    *,
    allow_standard: bool = False,
) -> dict[str, Any]:
    identity = str(candidate["file_id"])
    if not re.fullmatch(r"[A-Za-z0-9_.-]{1,80}", identity):
        raise ValueError("Invalid catalog identity")
    receipt_path = root / "reports" / "prepared" / (identity + ".json")
    if receipt_path.exists():
        receipt: dict[str, Any] = json.loads(receipt_path.read_text(encoding="utf-8"))
        verify_song(receipt, root / "Songs" / "MixDrumRock - Continuacao" / receipt["folder"])
        return receipt
    cache = root / "downloads" / "rest" / identity
    cache.mkdir(parents=True, exist_ok=True)
    folder = safe_folder_name(candidate["artist"], candidate["title"], identity)
    destination = root / "Songs" / "MixDrumRock - Continuacao" / folder
    with tempfile.TemporaryDirectory(prefix="inspect-", dir=cache) as temporary:
        staged_zip = Path(temporary) / "source.zip"
        url = resolve_drive_url(resolve_public_download(candidate["download_url"]))
        original_host = urlparse(candidate["download_url"]).hostname
        if urlparse(url).hostname in {"marketplace.xbox.com", "www.microsoft.com"}:
            raise ValueError("Catalog points to a marketplace; no public song archive")
        if url in {"https://rhythmverse.co/none", "https://rhythmverse.co/null"}:
            raise ValueError("Catalog has no public download URL")
        folder_assets = None
        if urlparse(url).hostname == "drive.google.com" and "/folders/" in url:
            folder_assets = drive_folder({**candidate, "download_url": url}, cache, staged_zip)
            source_format = "files"
            inspection_archive = staged_zip
            raw = None
        else:
            url = drive_download_url(url)
            if urlparse(url).hostname not in {"mega.nz", "mega.co.nz"}:
                url = quote(url, safe=":/?&=%+;,@!~*'()[]")
            raw = fetch(url, cache / "original", candidate["source_url"])
            # Catalog platform labels can also point at an already converted ZIP.
            # Select conversion from the downloaded bytes, preserving both inputs.
            with raw.open("rb") as source:
                signature = source.read(4)
            if signature in {b"CON ", b"LIVE", b"PIRS"}:
                if onyx_executable is None:
                    raise ValueError("Console package needs the pinned Onyx converter")
                from drumforge.library.onyx_recovery import build

                build(
                    onyx_executable,
                    raw.absolute(),
                    Path(temporary).absolute() / "project",
                    staged_zip.absolute(),
                )
                source_format = "onyx"
                inspection_archive = staged_zip
            else:
                source_format = source_zip(raw, staged_zip, root)
                inspection_archive = raw if source_format == "zip" else staged_zip
        report = prepare_zip(inspection_archive, destination, require_pro=not allow_standard)
        try:
            if normalized(report["artist"]) != normalized(candidate["artist"]):
                raise ValueError("Actual package artist differs from catalog match")
            if title_key(report["title"]) != title_key(candidate["title"]):
                raise ValueError("Actual package title differs from catalog match")
        except ValueError:
            # Only our freshly prepared files; preserve all original sources.
            import shutil

            shutil.rmtree(destination)
            raise
        with zipfile.ZipFile(inspection_archive) as archive:
            config_name = next(
                name for name in archive.namelist() if Path(name).name.casefold() == "song.ini"
            )
            song_root = Path(config_name).parent
            names = {
                Path(name).name.casefold(): name
                for name in archive.namelist()
                if not name.endswith("/") and Path(name).parent == song_root
            }
            assets = []
            for name, digest in report["files_sha256"].items():
                original_name = names[name.casefold()]
                asset = {"archive_name": original_name, "name": name, "sha256": digest}
                if folder_assets is not None:
                    asset.update(folder_assets[original_name])
                assets.append(asset)
        receipt = {
            "artist": candidate["artist"],
            "title": candidate["title"],
            "file_id": identity,
            "source_url": candidate["source_url"],
            "download_url": (
                candidate["download_url"].replace("http://", "https://", 1)
                if original_host in {"mediafire.com", "www.mediafire.com", "bit.ly", "tinyurl.com"}
                else url
            ),
            "archive_format": source_format,
            "folder": folder,
            "charter": report["charter"],
            "set_pro_drums": bool(report["configuration_changes"]),
            "drum_mode": "pro" if report["drums"]["pro_drums_evidence"] else "standard",
            "validation": {
                "drums": report["drums"],
                "decoded_audio_files": len(report["audio"]),
                "game_verified": False,
            },
            "match": candidate,
            "files": assets,
        }
        if raw is not None:
            receipt.update(
                archive_sha256=digest_file(raw),
                archive_bytes=raw.stat().st_size,
            )
        receipt_path.parent.mkdir(parents=True, exist_ok=True)
        receipt_path.write_text(
            json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        return receipt
