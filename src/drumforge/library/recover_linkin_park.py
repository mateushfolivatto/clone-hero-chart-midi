"""Recupera as selecoes Linkin Park, inclusive as antigas, sem reescrever receitas."""

from __future__ import annotations

import argparse
import importlib
import json
import subprocess
import unicodedata
import zipfile
from pathlib import Path
from typing import Any

recovery = importlib.import_module(
    "drumforge.library.recover_pilot" if __package__ else "recover_pilot"
)


def band_song(song: dict[str, Any]) -> bool:
    def key(text: str) -> str:
        return "".join(c for c in unicodedata.normalize("NFKD", text.casefold()) if c.isalnum())

    return "linkinpark" in key(song["artist"]) or (
        key(song["artist"]) == "xecutioners" and "linkinpark" in key(song["title"])
    )


def selected_manifests(metadata: Path, *, new_only: bool = False) -> list[dict[str, Any]]:
    path = metadata / "collection_index.json"
    if recovery.digest_file(path) != recovery.COLLECTION_SHA256:
        raise ValueError("Indice diferente do baixador; atualize os arquivos e tente novamente")
    index = json.loads(path.read_text(encoding="utf-8"))
    for name, digest in index["helpers"].items():
        if len(recovery.relative_path(name).parts) != 1:
            raise ValueError("Nome de auxiliar invalido")
        if recovery.digest_file(metadata / name) != digest:
            raise ValueError("Auxiliar diferente do indice; atualize o baixador")
    recipes = [] if new_only else [(1, recovery.read_manifest(metadata / "pilot_01.json"))]
    for batch in index["batches"]:
        if new_only and batch.get("theme") != "linkin-park":
            continue
        name = recovery.relative_path(batch["manifest"])
        if len(name.parts) != 1:
            raise ValueError("Nome de receita invalido")
        recipes.append((batch["number"], recovery.read_manifest(metadata / name, batch["sha256"])))
    selected = []
    for number, manifest in recipes:
        songs = [song for song in manifest["songs"] if band_song(song)]
        if songs:
            selected.append(
                {
                    **manifest,
                    "songs": songs,
                    "archive_name": f"MixDrumRock-LinkinPark-lote-{number:02d}.zip",
                }
            )
    return selected


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--destino", type=Path, default=Path.home() / "Downloads" / "LinkinPark")
    parser.add_argument("--novas", action="store_true", help="Somente a ampliacao apos o lote 18")
    args = parser.parse_args()
    errors = (OSError, ValueError, KeyError, subprocess.SubprocessError, zipfile.BadZipFile)
    try:
        manifests = selected_manifests(Path(__file__).parent, new_only=args.novas)
        print(f"Selecao: {sum(len(m['songs']) for m in manifests)} charts Linkin Park.", flush=True)
        pending = []
        for manifest in manifests:
            try:
                recovery.recover(manifest, args.destino)
            except errors as exc:
                pending.append(manifest["archive_name"])
                print(f"Lote pendente: {exc}. Continuando os demais...", flush=True)
        if pending:
            parser.exit(1, "Execute o mesmo comando para retomar os lotes pendentes.\n")
    except errors as exc:
        parser.exit(1, f"Falha: {exc}\nArquivos existentes foram preservados.\n")
    except KeyboardInterrupt:
        parser.exit(
            130, "Interrompido. Execute o mesmo comando para retomar; arquivos preservados.\n"
        )


if __name__ == "__main__":
    main()
