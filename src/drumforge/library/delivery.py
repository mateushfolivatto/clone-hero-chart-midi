"""Freeze inspected selections into immutable metadata recipes and a coverage CSV."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

from drumforge.library.batch import save
from drumforge.library.packages import safe_folder_name
from drumforge.library.recover_pilot import digest_file, verify_song
from drumforge.library.rhythmverse import candidates


def reason_for(error: str) -> str:
    messages = [
        ("quota exceeded", "Cota de downloads do Google Drive excedida."),
        ("web page", "Link devolveu uma página; arquivo ou acesso precisa de revisão."),
        ("Five-lane", "Cinco pistas; conversão para quatro/Pro Drums pendente."),
        ("explicit Pro Drums", "Pro Drums não comprovado nos arquivos."),
        ("No usable Expert drums", "Bateria Expert com bumbo não encontrada."),
        ("marketplace", "Catálogo aponta para uma loja, sem pacote público."),
        ("no public download", "Sem link público de download no catálogo."),
        ("HTTP Error 404", "Arquivo removido ou link inválido (HTTP 404)."),
        ("HTTP Error 500", "Erro do servidor de origem (HTTP 500)."),
        ("URLError", "Falha de conexão/TLS no provedor."),
        ("Actual package", "Metadados do pacote divergem do catálogo; revisão necessária."),
        ("name and artist", "Pacote sem título/artista válidos no song.ini."),
        ("PART DRUMS", "Trilha PART DRUMS ausente ou ambígua."),
        ("one song.ini", "Pacote exige seleção de música ou conversão."),
        ("not a supported", "Formato sem preparação/conversão validada."),
        ("Timeout", "Tempo limite de download/conversão excedido."),
    ]
    return next(
        (message for text, message in messages if text in error),
        "Preparação/conversão pendente; fonte requer revisão.",
    )


def freeze(playlist: Path, root: Path, metadata: Path, report: Path) -> dict[str, Any]:
    rows = list(csv.DictReader(playlist.open(encoding="utf-8-sig")))
    songs: list[dict[str, Any]] = []
    for path in sorted((root / "reports" / "search-rest").glob("*.json")):
        songs.extend(json.loads(path.read_text(encoding="utf-8"))["data"]["songs"] or [])
    receipts = {
        path.stem: json.loads(path.read_text(encoding="utf-8"))
        for path in (root / "reports" / "prepared").glob("*.json")
    }
    pilot = json.loads(Path(__file__).with_name("pilot_01.json").read_text(encoding="utf-8"))
    pilot_ids = {song["file_id"] for song in pilot["songs"]}
    batches = []
    prior = {}
    paths = sorted(
        (
            path
            for path in metadata.glob("collection_*.json")
            if path.stem.removeprefix("collection_").isdigit()
        ),
        key=lambda path: int(path.stem.removeprefix("collection_")),
    )
    for path in paths:
        data = json.loads(path.read_text(encoding="utf-8"))
        batches.append(
            {
                "number": data["batch_number"],
                "manifest": path.name,
                "sha256": digest_file(path),
                "songs": len(data["songs"]),
                "drum_mode": data.get("drum_mode", "pro"),
            }
        )
        prior.update({song["file_id"]: song for song in data["songs"]})
    failures = {}
    for filename in ["acquire-failures.json", "console-failures.json", "rv-failures.json"]:
        path = root / "reports" / filename
        if path.exists():
            failures.update(json.loads(path.read_text(encoding="utf-8")))
    selected: dict[str, dict[str, Any]] = {}
    coverage = []
    for row in rows:
        options = candidates(row, songs)
        compatible = [item for item in options if not item["version_review"]]
        previous = next(
            (s for s in prior.values() if row["qobuz_track_id"] in s.get("qobuz_track_ids", [])),
            None,
        )
        ready = [c for c in compatible if c["file_id"] in pilot_ids | receipts.keys()]
        ready.sort(
            key=lambda c: (
                c["file_id"] not in pilot_ids
                and receipts[c["file_id"]].get("drum_mode", "pro") == "standard"
            )
        )
        choice = previous or next(iter(ready), None)
        record = {**row, "status": "", "file_id": "", "batch": "", "source_url": "", "reason": ""}
        record["drum_mode"] = ""
        if options:
            record["source_url"] = options[0]["source_url"]
        if choice:
            identity = choice["file_id"]
            record.update(
                status="pilot" if identity in pilot_ids else "prepared",
                file_id=identity,
                source_url=choice["source_url"],
            )
            record["drum_mode"] = (
                "pro"
                if identity in pilot_ids
                else (prior.get(identity) or receipts[identity]).get("drum_mode", "pro")
            )
            if identity not in pilot_ids:
                receipt = prior.get(identity) or receipts[identity]
                if identity not in prior:
                    folder = root / "Songs" / "MixDrumRock - Continuacao" / receipt["folder"]
                    verify_song(receipt, folder)
                    receipt["prepared_bytes"] = sum(
                        (folder / asset["name"]).stat().st_size for asset in receipt["files"]
                    )
                selected[identity] = receipt
        elif compatible:
            record["status"] = "blocked"
            record["reason"] = " | ".join(
                dict.fromkeys(
                    reason_for(
                        failures.get(c["file_id"], "Candidate needs download/conversion review")
                    )
                    for c in compatible
                )
            )[:1500]
        elif options:
            record.update(
                status="needs_review",
                reason="Artista/título encontrados; duração/versão precisa de revisão.",
            )
        else:
            record.update(
                status="not_found",
                reason="Sem correspondência conservadora nos catálogos pesquisados.",
            )
        coverage.append(record)
    new = [song for identity, song in selected.items() if identity not in prior]
    new.sort(
        key=lambda song: (
            {"zip": 0, "files": 1, "rar": 2, "7z": 2, "onyx": 3}[song["archive_format"]],
            song["artist"].casefold(),
            song["title"].casefold(),
            song["file_id"],
        )
    )
    metadata.mkdir(parents=True, exist_ok=True)
    next_batch = max((item["number"] for item in batches), default=1) + 1
    groups: list[list[dict[str, Any]]] = []
    for mode in ["pro", "standard"]:
        section = [song for song in new if song.get("drum_mode", "pro") == mode]
        groups.extend(section[offset : offset + 25] for offset in range(0, len(section), 25))
    for group in groups:
        mode = group[0].get("drum_mode", "pro")
        mode_label = "Drums - " if mode == "standard" else ""
        for song in group:
            song["folder"] = safe_folder_name(song["artist"], song["title"], song["file_id"])
            song["qobuz_track_ids"] = [
                row["qobuz_track_id"] for row in coverage if row["file_id"] == song["file_id"]
            ]
            song["playlist_track_ids"] = [
                row["playlist_track_id"] for row in coverage if row["file_id"] == song["file_id"]
            ]
        data = {
            "schema_version": 1,
            "batch_number": next_batch,
            "collection_folder": f"MixDrumRock - {mode_label}Lote {next_batch:02d}",
            "archive_name": f"MixDrumRock-lote-{next_batch:02d}.zip",
            "game_verified": False,
            "drum_mode": mode,
            "songs": group,
        }
        path = metadata / f"collection_{next_batch:02d}.json"
        if path.exists():
            raise FileExistsError("Never overwrite an existing batch recipe")
        save(path, data)
        batches.append(
            {
                "number": next_batch,
                "manifest": path.name,
                "sha256": digest_file(path),
                "songs": len(group),
                "drum_mode": mode,
            }
        )
        prior.update({song["file_id"]: song for song in group})
        next_batch += 1
    batch_for = {}
    for batch in batches:
        data = json.loads((metadata / batch["manifest"]).read_text(encoding="utf-8"))
        batch_for.update({song["file_id"]: batch["number"] for song in data["songs"]})
    for row in coverage:
        row["batch"] = 1 if row["status"] == "pilot" else batch_for.get(row["file_id"], "")
    report.parent.mkdir(parents=True, exist_ok=True)
    with report.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(coverage[0]), delimiter=";")
        writer.writeheader()
        writer.writerows(coverage)
    all_songs = list(prior.values())
    download_bytes = sum(
        song.get("archive_bytes", sum(a.get("bytes", 0) for a in song["files"]))
        for song in all_songs
    )
    prepared_bytes = sum(song.get("prepared_bytes", 0) for song in all_songs)
    index = {
        "schema_version": 1,
        "playlist_url": "https://open.qobuz.com/playlist/69773629",
        "playlist_entries": len(rows),
        "unique_new_charts": len(prior),
        "active_new_charts": len(selected),
        "drum_modes": dict(Counter(song.get("drum_mode", "pro") for song in all_songs)),
        "coverage_entries": dict(Counter(row["status"] for row in coverage)),
        "download_bytes": download_bytes,
        "prepared_bytes": prepared_bytes,
        "recommended_free_bytes": download_bytes + 2 * prepared_bytes + 2 * 1024**3,
        "game_verified": False,
        "batches": batches,
        "helpers": {
            name: digest_file(metadata / name)
            for name in ["onyx_recovery.py", "sevenzip.py", "mega_recovery.py"]
        },
    }
    save(metadata / "collection_index.json", index)
    print(json.dumps(index, ensure_ascii=False, indent=2))
    print(
        "Pin collection_index.json SHA256:",
        hashlib.sha256((metadata / "collection_index.json").read_bytes()).hexdigest(),
    )
    return index


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("playlist", type=Path)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--metadata-dir", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    freeze(args.playlist, args.root, args.metadata_dir, args.report)


if __name__ == "__main__":
    main()
