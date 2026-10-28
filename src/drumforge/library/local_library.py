"""Offline song identity and conservative comparison, independent of folder names."""

from __future__ import annotations

import configparser
import hashlib
import html
import os
import re
import stat
import unicodedata
from dataclasses import dataclass
from pathlib import Path

AUDIO = {".ogg", ".mp3", ".wav", ".flac", ".opus"}
EXTRAS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".mp4", ".webm", ".txt", ".lrc"}
ARCHIVES = {".zip", ".rar", ".7z", ".sng"}
CHARTS = {"notes.mid", "notes.chart"}


def linked(path: Path) -> bool:
    info = path.lstat()
    # Name-surrogate reparse tags redirect paths (junctions/symlinks). OneDrive
    # cloud-file tags also have FILE_ATTRIBUTE_REPARSE_POINT, without redirection.
    return stat.S_ISLNK(info.st_mode) or bool(getattr(info, "st_reparse_tag", 0) & 0x20000000)


def digest(path: Path) -> str:
    result = hashlib.sha256()
    with path.open("rb") as file:
        for block in iter(lambda: file.read(1024 * 1024), b""):
            result.update(block)
    return result.hexdigest()


def normalized(text: str) -> str:
    text = html.unescape(re.sub(r"<[^>]*>", "", text)).casefold().replace("&", " and ")
    text = unicodedata.normalize("NFKD", text)
    return "".join(c for c in text if c.isalnum() and not unicodedata.combining(c))


def edition_key(title: str) -> str:
    # Edition-only differences are review candidates, never automatic exclusions.
    title = re.sub(
        r"\s*[\[(](?:RB3 Version|2x Bass Pedal|Drums Only|Rhythm Version)[\])]",
        "",
        title,
        flags=re.IGNORECASE,
    )
    title = re.sub(
        r"\b(?:\d{4}\s+)?remaster(?:ed)?(?:\s+(?:version|\d{4}))?\b",
        "",
        title,
        flags=re.IGNORECASE,
    )
    return normalized(title)


@dataclass(frozen=True)
class Asset:
    name: str
    size: int
    sha256: str


@dataclass(frozen=True)
class Song:
    folder: Path
    relative: str
    artist: str
    title: str
    album: str
    duration_ms: int | None
    assets: tuple[Asset, ...]
    problem: str = ""

    @property
    def key(self) -> tuple[str, str]:
        return normalized(self.artist), normalized(self.title)

    @property
    def fingerprint(self) -> tuple[tuple[str, ...], tuple[str, ...]]:
        notes = tuple(sorted(a.sha256 for a in self.assets if Path(a.name).name.lower() in CHARTS))
        audio = tuple(sorted(a.sha256 for a in self.assets if Path(a.name).suffix.lower() in AUDIO))
        return notes, audio


def metadata(path: Path) -> dict[str, str]:
    raw = path.read_bytes()
    if len(raw) > 1024 * 1024:
        raise ValueError("song.ini excede 1 MiB")
    if raw.startswith((b"\xff\xfe", b"\xfe\xff")):
        text = raw.decode("utf-16")
    else:
        try:
            text = raw.decode("utf-8-sig")
        except UnicodeDecodeError:
            text = raw.decode("cp1252")
    parser = configparser.ConfigParser(
        interpolation=None, strict=False, comment_prefixes=("#", ";", "//")
    )
    parser.read_string(text)
    section = next((s for s in parser.sections() if s.casefold() == "song"), None)
    if section is None:
        raise ValueError("song.ini sem secao [song]")
    return {k: v.strip() for k, v in parser[section].items()}


def payload(folder: Path) -> tuple[Asset, ...]:
    assets = []
    names = set()

    def fail(error: OSError) -> None:
        raise error

    for parent, dirs, files in os.walk(folder, followlinks=False, onerror=fail):
        for name in [*dirs, *files]:
            if linked(Path(parent) / name):
                raise ValueError("pasta de musica contem link/juncao; revisar manualmente")
        for name in sorted(files, key=str.casefold):
            path = Path(parent) / name
            if (
                name.lower() not in {"song.ini", *CHARTS}
                and path.suffix.lower() not in AUDIO | EXTRAS
            ):
                continue
            relative = path.relative_to(folder).as_posix()
            if relative.casefold() in names:
                raise ValueError("nomes de arquivos colidem no Windows")
            names.add(relative.casefold())
            before = path.stat()
            checksum = digest(path)
            after = path.stat()
            if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
                raise ValueError(
                    "arquivo mudou durante a leitura; execute apos terminar os downloads"
                )
            assets.append(Asset(relative, after.st_size, checksum))
    return tuple(assets)


def scan(root: Path, label: str) -> tuple[list[Song], list[dict[str, str]]]:
    songs = []
    warnings = []

    def fail(error: OSError) -> None:
        raise error

    for parent, dirs, files in os.walk(root, followlinks=False, onerror=fail):
        folder = Path(parent)
        relative = folder.relative_to(root).as_posix()
        safe_dirs = []
        for name in sorted(dirs, key=str.casefold):
            if linked(folder / name) or name.startswith(("convertendo-", "baixando-", ".")):
                warnings.append(
                    {
                        "colecao": label,
                        "pasta": str(Path(relative) / name),
                        "motivo": "link ou pasta temporaria ignorada",
                    }
                )
            else:
                safe_dirs.append(name)
        dirs[:] = safe_dirs
        by_name = {name.casefold(): name for name in files}
        if not ({"song.ini", *CHARTS} & by_name.keys()):
            for name in files:
                if Path(name).suffix.lower() in ARCHIVES:
                    warnings.append(
                        {
                            "colecao": label,
                            "pasta": str(Path(relative) / name),
                            "motivo": "arquivo compactado ignorado; usa apenas pastas extraidas",
                        }
                    )
            continue
        has_chart = bool(CHARTS & by_name.keys())
        has_audio = any(Path(n).suffix.lower() in AUDIO for n in files)
        if has_chart and has_audio:
            dirs[:] = []
        config: dict[str, str] = {}
        assets: tuple[Asset, ...] = ()
        problem = ""
        try:
            ini = by_name.get("song.ini")
            if ini is None:
                raise ValueError("song.ini ausente")
            if linked(folder / ini):
                raise ValueError("song.ini e um link; revisar manualmente")
            config = metadata(folder / ini)
            if not has_chart or not has_audio:
                raise ValueError("chart ou audio ausente na pasta da musica")
            assets = payload(folder)
            if any(
                a.size == 0
                for a in assets
                if Path(a.name).suffix.lower() in AUDIO or Path(a.name).name.lower() in CHARTS
            ):
                raise ValueError("chart ou audio vazio")
            if any(
                normalized(config.get(k, "")) in {"", "unknown", "unknownartist", "untitled"}
                for k in ("artist", "name")
            ):
                raise ValueError("artista ou titulo ausente/desconhecido")
        except (ValueError, UnicodeError, configparser.Error) as exc:
            problem = str(exc)
        duration = config.get("song_length", "")
        duration_ms = int(duration) if duration.isdigit() and int(duration) > 0 else None
        songs.append(
            Song(
                folder,
                relative if relative != "." else folder.name,
                config.get("artist", ""),
                config.get("name", ""),
                config.get("album", ""),
                duration_ms,
                assets,
                problem,
            )
        )
        if len(songs) % 20 == 0:
            print(f"  {label}: {len(songs)} pastas lidas...", flush=True)
    return songs, warnings


def compatible(left: Song, right: Song) -> bool:
    if left.duration_ms and right.duration_ms and abs(left.duration_ms - right.duration_ms) > 8000:
        return False
    # An album can expose a live/demo version omitted from the song name.
    markers = r"\b(live|demo|acoustic|remix|instrumental|karaoke)\b"
    versions = [
        set(re.findall(markers, s.title.casefold() + " " + s.album.casefold()))
        for s in (left, right)
    ]
    return versions[0] == versions[1]


def compare(
    old: list[Song], new: list[Song], *, allow_empty_reference: bool = False
) -> tuple[list[Song], list[dict[str, str]]]:
    ready = [s for s in new if not s.problem]
    if not ready and not allow_empty_reference:
        raise ValueError(
            "Nenhuma musica nova completa encontrada. Confira --novas e termine os downloads."
        )
    selected: list[Song] = []
    rows = []
    for song in old:
        status, reason, match = "adicionar", "Nao encontrada nas musicas novas presentes", ""
        if song.problem:
            status, reason = "revisar", song.problem
        else:
            for collection, duplicate_status in (
                (ready, "ja_nos_lotes"),
                (selected, "repetida_antiga"),
            ):
                exact = next((s for s in collection if s.fingerprint == song.fingerprint), None)
                same = [s for s in collection if s.key == song.key]
                matched = exact or next((s for s in same if compatible(song, s)), None)
                if matched:
                    status, reason, match = (
                        duplicate_status,
                        (
                            "Chart e audio identicos"
                            if exact
                            else "Mesmo artista/titulo; a outra copia tem prioridade"
                        ),
                        matched.relative,
                    )
                    break
                chart_hashes = set(song.fingerprint[0])
                shared_chart = next(
                    (s for s in collection if chart_hashes.intersection(s.fingerprint[0])), None
                )
                if shared_chart:
                    status, reason, match = (
                        "revisar",
                        "Chart identico, mas audio/metadados diferem; "
                        "evitar chart duplicado no jogo",
                        shared_chart.relative,
                    )
                    break
                review = same or [
                    s
                    for s in collection
                    if normalized(s.artist) == normalized(song.artist)
                    and edition_key(s.title) == edition_key(song.title)
                ]
                if review:
                    status, reason, match = (
                        "revisar",
                        "Duracao, versao ou edicao diferente; comparar antes de juntar",
                        review[0].relative,
                    )
                    break
        if status == "adicionar":
            selected.append(song)
        rows.append(
            {
                "status": status,
                "artista": song.artist,
                "titulo": song.title,
                "pasta_antiga": song.relative,
                "pasta_correspondente": match,
                "motivo": reason,
            }
        )
    return selected, rows
