"""Recover the verified twelve-song pilot on a PC using Python's standard library."""

from __future__ import annotations

import argparse
import configparser
import csv
import hashlib
import io
import json
import re
import tempfile
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any
from urllib.parse import urlparse
from urllib.request import Request, urlopen

# Pinned after a fresh cloud inspection. Never change it to bypass a mismatch.
MANIFEST_SHA256 = "b7751d6a29d45237984e0e03be5c002de3ac912e9d32dac6dc6d84b7c27b92ed"
METADATA_FILES = {"LEIA-ME.txt", "musicas.csv", "receita-verificada.json"}


def digest_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for block in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def relative_path(name: str) -> PurePosixPath:
    path = PurePosixPath(name.replace("\\", "/"))
    if not name or path.is_absolute() or ".." in path.parts or ":" in name:
        raise ValueError("Caminho inseguro na receita")
    return path


def read_manifest(path: Path) -> dict[str, Any]:
    content = path.read_bytes()
    if hashlib.sha256(content).hexdigest() != MANIFEST_SHA256:
        raise ValueError("A receita nao corresponde a versao verificada deste baixador")
    data = json.loads(content)
    if not isinstance(data, dict) or data["schema_version"] != 1 or len(data["songs"]) != 12:
        raise ValueError("Receita de lote nao suportada")
    relative_path(data["collection_folder"])
    seen = set()
    for song in data["songs"]:
        folder = relative_path(song["folder"])
        if len(folder.parts) != 1 or str(folder).casefold() in seen:
            raise ValueError("Pastas de musicas repetidas ou invalidas")
        seen.add(str(folder).casefold())
        if not re.fullmatch(r"[a-f0-9]{16,64}", song["file_id"]):
            raise ValueError("Identificador de pacote invalido")
        source = urlparse(song["download_url"])
        if (
            source.scheme != "https"
            or source.hostname != "rhythmverse.co"
            or source.username
            or source.port
            or not source.path.startswith("/download_file/")
        ):
            raise ValueError("Origem de download inesperada")
        if not re.fullmatch(r"[a-f0-9]{64}", song["archive_sha256"]):
            raise ValueError("Checksum de origem invalido")
        if not 0 < song["archive_bytes"] <= 300 * 1024 * 1024:
            raise ValueError("Tamanho de pacote inesperado")
        names = set()
        for asset in song["files"]:
            relative_path(asset["archive_name"])
            target = relative_path(asset["name"])
            if len(target.parts) != 1 or str(target).casefold() in names:
                raise ValueError("Nomes de arquivos invalidos ou repetidos")
            names.add(str(target).casefold())
            if not re.fullmatch(r"[a-f0-9]{64}", asset["sha256"]):
                raise ValueError("Checksum de arquivo invalido")
    return data


def download_archive(song: dict[str, Any], cache: Path) -> Path:
    cache.mkdir(parents=True, exist_ok=True)
    target = cache / (str(song["file_id"]) + ".zip")
    if target.exists():
        if digest_file(target) != song["archive_sha256"]:
            raise ValueError(f"Pacote existente foi alterado; preservado: {target}")
        return target
    with tempfile.TemporaryDirectory(prefix="baixando-", dir=cache) as temporary:
        partial = Path(temporary) / "pacote.zip"
        request = Request(song["download_url"], headers={"Referer": song["source_url"]})
        received = 0
        with urlopen(request, timeout=60) as response, partial.open("wb") as file:
            while block := response.read(1024 * 1024):
                received += len(block)
                if received > song["archive_bytes"]:
                    raise ValueError("O tamanho da origem mudou; pacote nao utilizado")
                file.write(block)
        if received != song["archive_bytes"] or digest_file(partial) != song["archive_sha256"]:
            raise ValueError("Download incompleto ou diferente do pacote verificado")
        if target.exists():
            raise FileExistsError(f"Outro arquivo apareceu no destino: {target}")
        partial.rename(target)
    return target


def patched_config(content: bytes) -> bytes:
    config = configparser.ConfigParser(interpolation=None, strict=False)
    config.read_string(content.decode("utf-8-sig"))
    config["song"]["pro_drums"] = "True"
    output = io.StringIO(newline="\n")
    config.write(output)
    return output.getvalue().encode("utf-8")


def verify_song(song: dict[str, Any], folder: Path) -> None:
    if folder.is_symlink():
        raise ValueError("A pasta de destino e um link; ela foi preservada")
    for asset in song["files"]:
        path = folder / asset["name"]
        if not path.is_file() or path.is_symlink() or digest_file(path) != asset["sha256"]:
            raise ValueError(f"Arquivo ausente ou alterado; nada foi sobrescrito: {path}")


def prepare_song(song: dict[str, Any], archive_path: Path, destination: Path) -> None:
    if destination.exists():
        verify_song(song, destination)
        return
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="preparando-", dir=destination.parent) as temporary:
        folder = Path(temporary) / "musica"
        folder.mkdir()
        with zipfile.ZipFile(archive_path) as archive:
            for asset in song["files"]:
                content = archive.read(asset["archive_name"])
                if asset["name"] == "song.ini" and song.get("set_pro_drums"):
                    content = patched_config(content)
                if hashlib.sha256(content).hexdigest() != asset["sha256"]:
                    raise ValueError("Arquivo extraido difere da verificacao original")
                (folder / asset["name"]).write_bytes(content)
        verify_song(song, folder)
        if destination.exists():
            raise FileExistsError("A pasta apareceu durante a preparacao; foi preservada")
        folder.rename(destination)


def delivery_metadata(manifest: dict[str, Any]) -> dict[str, bytes]:
    lines = [
        "MIXDRUMROCK - LOTE DE TESTE COM 12 MUSICAS",
        "",
        "Copie a pasta MixDrumRock - Lote teste 01, de dentro de Songs,",
        "para a pasta de musicas configurada no seu Clone Hero.",
        "Execute Scan Songs e selecione Pro Drums / Expert em uma versao atual do jogo.",
        "Os arquivos foram conferidos por SHA256 contra o lote inspecionado na nuvem.",
        "Scan Songs, gameplay, e-kit e sincronismo percebido aguardam seu teste.",
        "Audio e notas foram preservados. Em Requiem, song.ini recebeu pro_drums=True.",
        "Mantenha o audio original de cada chart; nao substitua por outra gravacao.",
        "",
    ]
    lines.extend(f"{song['artist']} - {song['title']}" for song in manifest["songs"])
    lines += ["", "Fontes, autores e hashes: receita-verificada.json.", ""]
    csv_buffer = io.StringIO(newline="")
    writer = csv.writer(csv_buffer, delimiter=";")
    writer.writerow(["artista", "musica", "autor_chart", "fonte", "pasta"])
    for song in manifest["songs"]:
        writer.writerow(
            [song["artist"], song["title"], song["charter"], song["source_url"], song["folder"]]
        )
    return {
        "LEIA-ME.txt": "\n".join(lines).encode("utf-8-sig"),
        "musicas.csv": csv_buffer.getvalue().encode("utf-8-sig"),
        "receita-verificada.json": (
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"
        ).encode(),
    }


def write_zip(manifest: dict[str, Any], root: Path) -> Path:
    target = root / "MixDrumRock-piloto-12.zip"
    metadata = delivery_metadata(manifest)
    entries = {}
    for song in manifest["songs"]:
        for asset in song["files"]:
            name = str(
                PurePosixPath("Songs", manifest["collection_folder"], song["folder"], asset["name"])
            )
            entries[name] = asset["sha256"]
    if target.exists():
        with zipfile.ZipFile(target) as archive:
            if set(archive.namelist()) != set(entries) | METADATA_FILES:
                raise ValueError("ZIP existente diferente; ele foi preservado")
            for name, digest in entries.items():
                if hashlib.sha256(archive.read(name)).hexdigest() != digest:
                    raise ValueError("ZIP existente alterado; ele foi preservado")
            if any(archive.read(name) != content for name, content in metadata.items()):
                raise ValueError("Metadados do ZIP existente diferem; ele foi preservado")
        return target
    with tempfile.TemporaryDirectory(prefix="compactando-", dir=root) as temporary:
        partial = Path(temporary) / "lote.zip"
        with zipfile.ZipFile(partial, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
            for name, content in metadata.items():
                archive.writestr(name, content)
            for name in entries:
                archive.write(root / Path(name), arcname=name)
        with zipfile.ZipFile(partial) as archive:
            if archive.testzip() is not None:
                raise ValueError("Falha de integridade ao criar ZIP")
        if target.exists():
            raise FileExistsError("Outro ZIP apareceu; ele foi preservado")
        partial.rename(target)
    return target


def recover(manifest: dict[str, Any], root: Path) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    for index, song in enumerate(manifest["songs"], start=1):
        print(
            f"{index:02d}/{len(manifest['songs'])}: {song['artist']} - {song['title']}", flush=True
        )
        destination = root / "Songs" / manifest["collection_folder"] / song["folder"]
        if destination.exists():
            verify_song(song, destination)
            print("  Ja preparada; arquivos conferidos.", flush=True)
            continue
        archive = download_archive(song, root / "Originais")
        prepare_song(song, archive, destination)
        print("  Pronta para testar.", flush=True)
    print("Criando/conferindo o ZIP...", flush=True)
    return write_zip(manifest, root)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--destino", type=Path, default=Path.home() / "Downloads" / "MixDrumRock")
    args = parser.parse_args()
    try:
        manifest = read_manifest(Path(__file__).with_name("pilot_01.json"))
        target = recover(manifest, args.destino.absolute())
    except (OSError, ValueError, KeyError, zipfile.BadZipFile, configparser.Error) as exc:
        parser.exit(1, f"Falha: {exc}\nArquivos existentes foram preservados.\n")
    print(f"\nConcluido! ZIP: {target}", flush=True)
    print(f"Pastas para o Clone Hero: {target.parent / 'Songs'}", flush=True)


if __name__ == "__main__":
    main()
