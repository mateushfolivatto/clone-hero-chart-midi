"""Recover the verified twelve-song pilot on a PC using Python's standard library."""

from __future__ import annotations

import argparse
import configparser
import csv
import hashlib
import html
import importlib
import io
import json
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import zipfile
from html.parser import HTMLParser
from pathlib import Path, PurePosixPath
from typing import Any
from urllib.parse import urlparse
from urllib.request import Request, urlopen

# Pinned after a fresh cloud inspection. Never change it to bypass a mismatch.
MANIFEST_SHA256 = "b7751d6a29d45237984e0e03be5c002de3ac912e9d32dac6dc6d84b7c27b92ed"
METADATA_FILES = {"LEIA-ME.txt", "musicas.csv", "receita-verificada.json"}
COLLECTION_SHA256 = "7c86a95cc8ae33fc97d5f696a8b4e5cb01a6f22d99c725abae71347cd1c4dd2d"


class DownloadLink(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.url: str | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if tag == "a" and attributes.get("id") == "downloadButton":
            self.url = attributes.get("href")


def resolve_public_download(url: str) -> str:
    host = urlparse(url).hostname or ""
    if url.startswith("http://"):
        url = "https://" + url[7:]
    if host in {"bit.ly", "tinyurl.com"}:
        with urlopen(url, timeout=60) as response:
            url = response.geturl()
        host = urlparse(url).hostname or ""
    if host in {"mediafire.com", "www.mediafire.com"}:
        with urlopen(url, timeout=60) as response:
            page = response.read(2 * 1024 * 1024).decode("utf-8")
        parser = DownloadLink()
        parser.feed(page)
        target = html.unescape(parser.url or "")
        if not (urlparse(target).hostname or "").endswith(".mediafire.com"):
            raise ValueError("O provedor requer interacao ou nao oferece download publico")
        return "https://" + target.split("://", 1)[1]
    if host == "drive.google.com":
        match = re.search(r"/file/d/([A-Za-z0-9_-]+)", url)
        if match:
            return "https://drive.google.com/uc?export=download&id=" + match[1]
    return url


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


def sng_as_zip(source: Path, target: Path) -> None:
    """Read SNG v1 using its published specification; preserve unmasked asset bytes."""
    limit = 512 * 1024 * 1024
    size = source.stat().st_size
    if size > limit:
        raise ValueError("SNG excede o limite de 512 MiB")
    with source.open("rb") as stream:

        def read(count: int) -> bytes:
            if count < 0 or count > limit or stream.tell() + count > size:
                raise ValueError("SNG truncado ou comprimento invalido")
            data = stream.read(count)
            if len(data) != count:
                raise ValueError("SNG truncado")
            return data

        def number(fmt: str) -> int:
            return int(struct.unpack(fmt, read(struct.calcsize(fmt)))[0])

        def section() -> int:
            length = number("<Q")
            end = stream.tell() + length
            if length < 8 or length > 2 * 1024 * 1024 or end > size:
                raise ValueError("Secao SNG invalida")
            return end

        if read(6) != b"SNGPKG" or number("<I") != 1:
            raise ValueError("SNG requer assinatura e versao 1")
        mask = read(16)
        end = section()
        count = number("<Q")
        if not 1 <= count <= 2048:
            raise ValueError("Quantidade de metadados SNG invalida")
        metadata: dict[str, str] = {}
        for _ in range(count):
            values = []
            for _ in range(2):
                length = number("<i")
                if length < 0 or stream.tell() + length > end:
                    raise ValueError("String SNG fora da secao")
                values.append(read(length).decode("utf-8"))
            key, value = values
            if (
                not re.fullmatch(r"[A-Za-z0-9_]+", key)
                or key.casefold() in metadata
                or any(ord(c) < 32 or ord(c) == 127 for c in value)
            ):
                raise ValueError("Metadados SNG inseguros ou repetidos")
            metadata[key.casefold()] = value
        if stream.tell() != end:
            raise ValueError("Comprimento de metadados SNG incorreto")
        end = section()
        count = number("<Q")
        if not 1 <= count <= 2048:
            raise ValueError("Quantidade de arquivos SNG invalida")
        members: list[tuple[str, int, int]] = []
        seen = {"song.ini"}
        reserved = {"con", "prn", "aux", "nul"} | {
            f"{prefix}{i}" for prefix in ("com", "lpt") for i in range(10)
        }
        for _ in range(count):
            name = read(number("<B")).decode("utf-8")
            path = relative_path(name)
            if (
                not path.parts
                or str(path) != name
                or name.casefold() in seen
                or any(
                    part.endswith((".", " "))
                    or part.split(".")[0].casefold() in reserved
                    or any(c in '<>:"\\|?*' or ord(c) < 32 or ord(c) == 127 for c in part)
                    for part in path.parts
                )
            ):
                raise ValueError("Nome de arquivo SNG inseguro ou repetido")
            seen.add(name.casefold())
            length, offset = number("<Q"), number("<Q")
            members.append((name, length, offset))
        if stream.tell() != end:
            raise ValueError("Comprimento do indice SNG incorreto")
        length = number("<Q")
        start = stream.tell()
        if start + length != size:
            raise ValueError("Comprimento dos dados SNG incorreto")
        cursor = start
        for _, length, offset in sorted(members, key=lambda item: item[2]):
            if offset != cursor or length > size - offset:
                raise ValueError("Dados SNG sobrepostos ou fora do arquivo")
            cursor += length
        if cursor != size:
            raise ValueError("Dados SNG nao indexados")
        # SNG resets the byte-position XOR key at the beginning of each asset.
        tables = [bytes(i ^ mask[pos % 16] ^ pos for i in range(256)) for pos in range(256)]
        partial = target.with_name(target.name + ".partial")
        try:
            with zipfile.ZipFile(partial, "w", compression=zipfile.ZIP_STORED) as archive:
                ini = "[song]\n" + "".join(f"{k} = {v}\n" for k, v in metadata.items())
                archive.writestr("song.ini", ini.encode("utf-8"))
                for name, length, offset in members:
                    stream.seek(offset)
                    position = 0
                    with archive.open(name, "w") as output:
                        while position < length:
                            block = bytearray(read(min(1024 * 1024, length - position)))
                            for phase in range(min(256, len(block))):
                                block[phase::256] = block[phase::256].translate(
                                    tables[(position + phase) % 256]
                                )
                            output.write(block)
                            position += len(block)
            partial.replace(target)
        finally:
            partial.unlink(missing_ok=True)


def read_manifest(path: Path, expected_sha256: str | None = None) -> dict[str, Any]:
    content = path.read_bytes()
    if hashlib.sha256(content).hexdigest() != (expected_sha256 or MANIFEST_SHA256):
        raise ValueError("A receita nao corresponde a versao verificada deste baixador")
    data = json.loads(content)
    if (
        not isinstance(data, dict)
        or data["schema_version"] != 1
        or not 1 <= len(data["songs"]) <= 50
        or (expected_sha256 is None and len(data["songs"]) != 12)
    ):
        raise ValueError("Receita de lote nao suportada")
    if len(relative_path(data["collection_folder"]).parts) != 1:
        raise ValueError("Pasta de lote invalida")
    if "archive_name" in data and len(relative_path(data["archive_name"]).parts) != 1:
        raise ValueError("Nome de ZIP invalido")
    seen = set()
    for song in data["songs"]:
        folder = relative_path(song["folder"])
        if len(folder.parts) != 1 or str(folder).casefold() in seen:
            raise ValueError("Pastas de musicas repetidas ou invalidas")
        seen.add(str(folder).casefold())
        if not re.fullmatch(r"[A-Za-z0-9_.-]{1,80}", song["file_id"]):
            raise ValueError("Identificador de pacote invalido")
        source = urlparse(song["download_url"])
        if (
            source.scheme != "https"
            or not source.hostname
            or source.username
            or source.port
            or (
                expected_sha256 is None
                and (
                    source.hostname != "rhythmverse.co"
                    or not source.path.startswith("/download_file/")
                )
            )
        ):
            raise ValueError("Origem de download inesperada")
        if song.get("archive_format") == "files":
            for asset in song["files"]:
                asset_url = urlparse(asset["download_url"])
                if (
                    asset_url.scheme != "https"
                    or asset_url.hostname != "drive.google.com"
                    or asset_url.path != "/uc"
                    or asset_url.username
                    or asset_url.port
                ):
                    raise ValueError("Origem de arquivo invalida")
                if not re.fullmatch(r"[a-f0-9]{64}", asset["source_sha256"]):
                    raise ValueError("Checksum de origem invalido")
                if not 0 < asset["bytes"] <= 300 * 1024 * 1024:
                    raise ValueError("Tamanho de arquivo inesperado")
        elif not re.fullmatch(r"[a-f0-9]{64}", song["archive_sha256"]):
            raise ValueError("Checksum de origem invalido")
        if (
            song.get("archive_format") != "files"
            and not 0 < song["archive_bytes"] <= 512 * 1024 * 1024
        ):
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
        resolved = resolve_public_download(song["download_url"])
        if urlparse(resolved).hostname in {"mega.nz", "mega.co.nz"}:
            provider = importlib.import_module(
                "drumforge.library.mega_recovery" if __package__ else "mega_recovery"
            )
            provider.download(resolved, partial, song["archive_bytes"])
            received = partial.stat().st_size
        else:
            request = Request(
                resolved,
                headers={"Referer": song["source_url"]},
            )
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
    config = configparser.ConfigParser(
        interpolation=None, strict=False, comment_prefixes=("#", ";", "//")
    )
    config.read_string(content.decode("utf-8-sig"))
    section = next(name for name in config.sections() if name.casefold() == "song")
    config[section]["pro_drums"] = "True"
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
        if song.get("archive_format") in {"rar", "7z"}:
            reader = importlib.import_module(
                "drumforge.library.sevenzip" if __package__ else "sevenzip"
            )
            executable = reader.install(destination.parents[2])
            for asset in song["files"]:
                content = reader.read_member(executable, archive_path, asset["archive_name"])
                publish_asset(song, asset, content, folder)
        elif song.get("archive_format") == "files":
            for asset in song["files"]:
                original = download_archive(
                    {
                        "file_id": hashlib.sha256(asset["download_url"].encode()).hexdigest(),
                        "archive_sha256": asset["source_sha256"],
                        "archive_bytes": asset["bytes"],
                        "download_url": asset["download_url"],
                        "source_url": song["source_url"],
                    },
                    archive_path,
                )
                publish_asset(song, asset, original.read_bytes(), folder)
        else:
            if song.get("archive_format") == "sng":
                converted = Path(temporary) / "source.zip"
                sng_as_zip(archive_path, converted)
                archive_path = converted
            with zipfile.ZipFile(archive_path) as archive:
                for asset in song["files"]:
                    publish_asset(song, asset, archive.read(asset["archive_name"]), folder)
        verify_song(song, folder)
        if destination.exists():
            raise FileExistsError("A pasta apareceu durante a preparacao; foi preservada")
        folder.rename(destination)


def publish_asset(
    song: dict[str, Any], asset: dict[str, Any], content: bytes, folder: Path
) -> None:
    if asset["name"] == "song.ini" and song.get("set_pro_drums"):
        content = patched_config(content)
    if hashlib.sha256(content).hexdigest() != asset["sha256"]:
        raise ValueError("Arquivo extraido difere da verificacao original")
    (folder / asset["name"]).write_bytes(content)


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
    if "archive_name" in manifest:
        selection = (
            "Drums / Expert (quatro pistas; Pro Drums nao comprovado)"
            if manifest.get("drum_mode") == "standard"
            else "Pro Drums / Expert"
        )
        lines = [
            f"{manifest['collection_folder']} - {len(manifest['songs'])} MUSICAS",
            "",
            "Copie esta pasta de dentro de Songs para sua biblioteca do Clone Hero.",
            f"Execute Scan Songs e selecione {selection}.",
            "Audio/notas preservados; configuracao Pro Drums explicitada quando ha marcadores.",
            "Arquivos conferidos por SHA256; gameplay e sincronismo aguardam seu teste.",
            "Mesma musica nao garante o mesmo master do Qobuz; mantenha o audio do chart.",
            "",
            *(f"{song['artist']} - {song['title']}" for song in manifest["songs"]),
        ]
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
    target = root / str(manifest.get("archive_name", "MixDrumRock-piloto-12.zip"))
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


def recover_song(song: dict[str, Any], destination: Path, root: Path) -> dict[str, Any]:
    if (
        sys.platform == "win32"
        and len(str(destination)) + max(len(a["name"]) for a in song["files"]) > 238
    ):
        raise ValueError("Caminho longo para Windows; escolha um --destino mais curto")
    if song.get("archive_format") == "onyx":
        converter = importlib.import_module(
            "drumforge.library.onyx_recovery" if __package__ else "onyx_recovery"
        )
        source = download_archive(song, root / "Originais")
        return dict(converter.prepare(song, source, destination, root))
    if destination.exists():
        verify_song(song, destination)
        return song
    archive = (
        root / "Originais"
        if song.get("archive_format") == "files"
        else download_archive(song, root / "Originais")
    )
    prepare_song(song, archive, destination)
    return song


def recover(manifest: dict[str, Any], root: Path) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    if "archive_name" in manifest:
        required = 0
        for song in manifest["songs"]:
            if not (root / "Songs" / manifest["collection_folder"] / song["folder"]).exists():
                required += 2 * song.get("prepared_bytes", 0)
                required += song.get("archive_bytes", sum(a.get("bytes", 0) for a in song["files"]))
        if required and required + 512 * 1024**2 > shutil.disk_usage(root).free:
            raise OSError("Espaco insuficiente para este lote, originais, pastas e ZIP")
    successes = []
    failures = []
    for index, song in enumerate(manifest["songs"], start=1):
        print(
            f"{index:02d}/{len(manifest['songs'])}: {song['artist']} - {song['title']}", flush=True
        )
        destination = root / "Songs" / manifest["collection_folder"] / song["folder"]
        try:
            ready = recover_song(song, destination, root)
            manifest["songs"][index - 1] = ready
            successes.append(ready)
            print("  Pronta; arquivos conferidos.", flush=True)
        except (
            OSError,
            ValueError,
            KeyError,
            subprocess.SubprocessError,
            zipfile.BadZipFile,
            configparser.Error,
        ) as exc:
            if "archive_name" not in manifest:
                raise
            failures.append({"file_id": song["file_id"], "error": str(exc)})
            print(f"  Pendente: {exc}. Continuando as outras musicas...", flush=True)
    if failures:
        report = root / (Path(manifest["archive_name"]).stem + "-falhas.json")
        report.write_text(json.dumps(failures, ensure_ascii=False, indent=2), encoding="utf-8")
        if successes:
            fingerprint = hashlib.sha256(
                json.dumps(successes, sort_keys=True).encode()
            ).hexdigest()[:8]
            partial = {
                **manifest,
                "songs": successes,
                "archive_name": Path(manifest["archive_name"]).stem + f"-parcial-{fingerprint}.zip",
            }
            print(f"ZIP parcial: {write_zip(partial, root)}", flush=True)
        raise ValueError(f"{len(failures)} musica(s) pendente(s); detalhes em {report}")
    print("Criando/conferindo o ZIP...", flush=True)
    return write_zip(manifest, root)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--destino", type=Path, default=Path.home() / "Downloads" / "MixDrumRock")
    parser.add_argument("--restante", action="store_true", help="Baixar os lotes da continuacao")
    parser.add_argument("--lote", type=int, help="Baixar somente este numero de lote")
    args = parser.parse_args()
    try:
        manifests = []
        if args.restante:
            index_path = Path(__file__).with_name("collection_index.json")
            content = index_path.read_bytes()
            if hashlib.sha256(content).hexdigest() != COLLECTION_SHA256:
                raise ValueError("Indice de lotes diferente da versao verificada")
            index = json.loads(content)
            for helper_name, digest in index.get("helpers", {}).items():
                name = relative_path(helper_name)
                if len(name.parts) != 1 or digest_file(index_path.with_name(str(name))) != digest:
                    raise ValueError("Atualize os arquivos auxiliares do baixador")
            for batch in index["batches"]:
                if args.lote is not None and batch["number"] != args.lote:
                    continue
                name = relative_path(batch["manifest"])
                if len(name.parts) != 1:
                    raise ValueError("Nome de receita invalido")
                manifests.append(read_manifest(index_path.with_name(str(name)), batch["sha256"]))
            if not manifests:
                raise ValueError("Lote nao encontrado")
        else:
            manifests.append(read_manifest(Path(__file__).with_name("pilot_01.json")))
        failures = []
        for manifest in manifests:
            try:
                target = recover(manifest, args.destino.absolute())
                print(f"\nConcluido! ZIP: {target}", flush=True)
            except (OSError, ValueError, subprocess.SubprocessError, zipfile.BadZipFile) as exc:
                if not args.restante:
                    raise
                failures.append(f"{manifest['collection_folder']}: {exc}")
                print(f"Lote interrompido: {exc}. Retome com o mesmo comando.", flush=True)
        if failures:
            parser.exit(1, "\n".join(failures) + "\nMusicas ja preparadas foram preservadas.\n")
    except KeyboardInterrupt:
        parser.exit(
            130,
            "\nInterrompido pelo teclado. Ctrl+C encerra a execucao; nao pula a musica.\n"
            "Musicas prontas e downloads concluidos foram preservados.\n"
            "Execute o mesmo comando para retomar.\n",
        )
    except (
        OSError,
        ValueError,
        KeyError,
        zipfile.BadZipFile,
        configparser.Error,
        subprocess.SubprocessError,
    ) as exc:
        parser.exit(1, f"Falha: {exc}\nArquivos existentes foram preservados.\n")
    print(f"Pastas para o Clone Hero: {args.destino.absolute() / 'Songs'}", flush=True)


if __name__ == "__main__":
    main()
