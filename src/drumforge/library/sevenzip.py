"""Pinned portable archive reader; no installer or administrator access needed."""

from __future__ import annotations

import importlib
import subprocess
import sys
import tarfile
import zipfile
from functools import cache
from pathlib import Path
from typing import Any

recovery = importlib.import_module(
    "drumforge.library.recover_pilot" if __package__ else "recover_pilot"
)
BASE = "https://github.com/ip7z/7zip/releases/download/26.04/"
ARTIFACTS = {
    "linux": (
        "7z2604-linux-x64.tar.xz",
        1576336,
        "fc0327ba27e89bd086cf426dff17d77de582953cdbbc10a6576540a06853ffcd",
    ),
    "windows": (
        "7z2604-x64.exe",
        1664082,
        "d54bf805f9f3704d1e8db2fa3498ae7ef2df0312b40b558e7c71c734430a665d",
    ),
    "bootstrap": (
        "7zr.exe",
        602624,
        "256feca8e274e5da655e2a284fabafd9f554365eb164862089dacd4e8276d282",
    ),
}


def download(kind: str, root: Path) -> Path:
    filename, size, digest = ARTIFACTS[kind]
    return Path(
        recovery.download_archive(
            {
                "file_id": "7zip-26.04-" + kind,
                "download_url": BASE + filename,
                "source_url": "https://github.com/ip7z/7zip/releases/tag/26.04",
                "archive_bytes": size,
                "archive_sha256": digest,
            },
            root / "Ferramentas",
        )
    )


def immutable_write(path: Path, content: bytes) -> None:
    if path.exists():
        if path.read_bytes() != content:
            raise ValueError("Leitor de arquivos local alterado; preservado")
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)


@cache
def install(root: Path) -> Path:
    folder = root / "Ferramentas" / "7zip-26.04"
    if sys.platform == "win32":
        bootstrap = folder / "7zr.exe"
        immutable_write(bootstrap, download("bootstrap", root).read_bytes())
        source = download("windows", root)
        # Read the installer as an archive; never execute the installer.
        for name in ["7z.exe", "7z.dll", "License.txt"]:
            result = subprocess.run(
                [str(bootstrap), "x", "-so", "-spd", str(source), name],
                check=True,
                capture_output=True,
                timeout=60,
            )
            immutable_write(folder / name, result.stdout)
        return folder / "7z.exe"
    if sys.platform != "linux":
        raise ValueError("Leitor portatil disponivel para Windows/Linux x64")
    source = download("linux", root)
    with tarfile.open(source, "r:xz") as archive:
        for name in ["7zz", "License.txt"]:
            member = archive.extractfile(name)
            if member is None:
                raise ValueError("Distribuicao oficial incompleta")
            immutable_write(folder / name, member.read())
    executable = folder / "7zz"
    executable.chmod(0o755)
    return executable


def read_member(executable: Path, source: Path, name: str) -> bytes:
    result = subprocess.run(
        [str(executable), "x", "-so", "-spd", str(source), "--", name],
        capture_output=True,
        check=True,
        timeout=120,
    )
    return result.stdout


def as_zip(source: Path, target: Path, root: Path) -> None:
    executable = install(root)
    result = subprocess.run(
        [str(executable), "l", "-slt", "-sccUTF-8", str(source)],
        capture_output=True,
        check=True,
        timeout=60,
    )
    listing = result.stdout.decode("utf-8").split("----------\n", 1)[1]
    total = 0
    with zipfile.ZipFile(target, "w") as archive:
        for block in listing.split("\n\n"):
            fields: dict[str, Any] = dict(
                line.split(" = ", 1) for line in block.splitlines() if " = " in line
            )
            if (
                not fields
                or fields.get("Folder") == "+"
                or fields.get("Attributes", "").startswith("D")
            ):
                continue
            name = fields["Path"]
            recovery.relative_path(name)
            if "Symbolic Link" in fields or "Hard Link" in fields:
                raise ValueError("Archive links are unsupported")
            size = int(fields["Size"])
            total += size
            if total > 800 * 1024 * 1024:
                raise ValueError("Archive exceeds 800 MiB budget")
            content = read_member(executable, source, name)
            if len(content) != size:
                raise ValueError("Archive member length differs from index")
            archive.writestr(name, content)
