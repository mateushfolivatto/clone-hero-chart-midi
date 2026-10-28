"""Recupera Skillet, Imagine Dragons e LoL, comparando depois com a biblioteca local."""

from __future__ import annotations

import argparse
import importlib
import json
import subprocess
import zipfile
from pathlib import Path
from typing import Any

recovery = importlib.import_module(
    "drumforge.library.recover_pilot" if __package__ else "recover_pilot"
)
GROUPS = ("skillet", "imagine", "lol")


def selected_manifests(
    metadata: Path, groups: list[str] | None = None, *, new_only: bool = False
) -> list[dict[str, Any]]:
    requested = sorted(set(groups if groups is not None else GROUPS))
    if not requested or set(requested) - set(GROUPS):
        raise ValueError("Selecao desconhecida ou vazia")
    path = metadata / "collection_index.json"
    if recovery.digest_file(path) != recovery.COLLECTION_SHA256:
        raise ValueError("Indice diferente do baixador; atualize os arquivos")
    index = json.loads(path.read_text(encoding="utf-8"))
    for name, digest in index["helpers"].items():
        if len(recovery.relative_path(name).parts) != 1:
            raise ValueError("Nome de auxiliar invalido")
        if recovery.digest_file(metadata / name) != digest:
            raise ValueError("Auxiliar diferente do indice")
    selection = index["selections"]["skillet-imagine-lol"]
    for name, digest in [
        (selection["manifest"], selection["sha256"]),
        (selection["helper"], selection["helper_sha256"]),
    ]:
        if len(recovery.relative_path(name).parts) != 1:
            raise ValueError("Nome de selecao invalido")
        if recovery.digest_file(metadata / name) != digest:
            raise ValueError("Selecao ou auxiliar diferente do indice")
    scope = json.loads((metadata / selection["manifest"]).read_text(encoding="utf-8"))
    if scope["schema_version"] != 1 or set(scope["groups"]) != set(GROUPS):
        raise ValueError("Formato de selecao desconhecido")
    recipes = [(1, recovery.read_manifest(metadata / "pilot_01.json"))]
    for batch in index["batches"]:
        name = recovery.relative_path(batch["manifest"])
        if len(name.parts) != 1:
            raise ValueError("Nome de receita invalido")
        recipes.append((batch["number"], recovery.read_manifest(metadata / name, batch["sha256"])))
    published = {s["file_id"] for _, m in recipes for s in m["songs"]}
    wanted: set[str] = set()
    for group in GROUPS:
        entry = scope["groups"][group]
        ids, new_ids = set(entry["file_ids"]), set(entry["new_file_ids"])
        if (
            not new_ids <= ids <= published
            or len(ids) != len(entry["file_ids"])
            or len(new_ids) != len(entry["new_file_ids"])
        ):
            raise ValueError("Selecao referencia musicas ausentes ou repetidas")
        if group in requested:
            wanted.update(new_ids if new_only else ids)
    selected = []
    seen: set[str] = set()
    label = "-".join(requested) + ("-novas" if new_only else "-todas")
    for number, manifest in recipes:
        songs = []
        for song in manifest["songs"]:
            identity = song["file_id"]
            if identity in wanted:
                if identity in seen:
                    raise ValueError("Musica repetida nas receitas")
                seen.add(identity)
                songs.append(song)
        if songs:
            selected.append(
                {
                    **manifest,
                    "songs": songs,
                    "archive_name": f"MixDrumRock-{label}-lote-{number:02d}.zip",
                }
            )
    if seen != wanted:
        raise ValueError("Selecao incompleta")
    return selected


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--destino", type=Path, default=Path.home() / "Downloads/Skillet-Imagine-LoL"
    )
    parser.add_argument("--grupos", nargs="+", choices=GROUPS, default=list(GROUPS))
    parser.add_argument(
        "--novas", action="store_true", help="Somente os novos lotes, a partir do 31"
    )
    args = parser.parse_args()
    errors = (OSError, ValueError, KeyError, subprocess.SubprocessError, zipfile.BadZipFile)
    try:
        manifests = selected_manifests(Path(__file__).parent, args.grupos, new_only=args.novas)
        print(f"Selecao: {sum(len(m['songs']) for m in manifests)} charts.", flush=True)
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
        parser.exit(130, "Interrompido. Execute novamente para retomar; arquivos preservados.\n")


if __name__ == "__main__":
    main()
