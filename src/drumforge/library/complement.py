"""Cria um ZIP das musicas antigas ausentes dos lotes novos, sem alterar originais."""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib
import json
import shutil
import tempfile
import zipfile
from collections import Counter
from pathlib import Path, PurePosixPath
from typing import Any

library = importlib.import_module(
    "drumforge.library.local_library" if __package__ else "local_library"
)


def csv_report(path: Path, rows: list[dict[str, str]], columns: list[str]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=columns, delimiter=";")
        writer.writeheader()
        writer.writerows(rows)


def export(old_root: Path, new_root: Path, destination: Path) -> dict[str, Any]:
    old_root, new_root, destination = [p.resolve() for p in (old_root, new_root, destination)]
    if not old_root.is_dir() or not new_root.is_dir():
        raise ValueError("As pastas --antigas e --novas precisam existir")
    if old_root.is_relative_to(new_root) or new_root.is_relative_to(old_root):
        raise ValueError("As colecoes antigas e novas precisam estar em pastas separadas")
    if any(destination.is_relative_to(p) for p in (old_root, new_root)):
        raise ValueError("O destino precisa ficar fora das duas colecoes")
    if destination.exists():
        raise FileExistsError(
            "O destino ja existe; escolha outra pasta para preservar esse resultado"
        )
    print("Lendo musicas antigas (apenas neste computador)...", flush=True)
    old, old_warnings = library.scan(old_root, "antigas")
    if not old:
        raise ValueError("Nenhuma pasta de musica antiga encontrada; extraia os pacotes primeiro")
    print("Lendo musicas novas ja presentes no disco...", flush=True)
    new, new_warnings = library.scan(new_root, "novas")
    selected, rows = library.compare(old, new)
    counts = dict(Counter(r["status"] for r in rows))
    summary: dict[str, Any] = {
        "antigas_lidas": len(old),
        "novas_prontas": sum(not s.problem for s in new),
        "novas_incompletas": sum(bool(s.problem) for s in new),
        "resultado": counts,
        "bytes_para_adicionar": sum(a.size for s in selected for a in s.assets),
        "originais_alterados": False,
        "game_verified": False,
    }
    destination.parent.mkdir(parents=True, exist_ok=True)
    if shutil.disk_usage(destination.parent).free < summary["bytes_para_adicionar"] + 64 * 1024**2:
        raise OSError("Espaco insuficiente para o ZIP do complemento; originais preservados")
    destination.mkdir()
    csv_report(
        destination / "comparacao.csv",
        rows,
        ["status", "artista", "titulo", "pasta_antiga", "pasta_correspondente", "motivo"],
    )
    warnings = (
        old_warnings
        + new_warnings
        + [{"colecao": "novas", "pasta": s.relative, "motivo": s.problem} for s in new if s.problem]
    )
    csv_report(destination / "avisos.csv", warnings, ["colecao", "pasta", "motivo"])
    (destination / "resumo.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    readme = (
        "COMPLEMENTO DAS MUSICAS ANTIGAS\n\n"
        "Junte a pasta Complemento-antigas deste ZIP aos lotes novos em uma biblioteca separada.\n"
        "Comparacao.csv lista as musicas incluidas, sobrepostas e para revisar.\n"
        "Itens revisar continuam nos originais e nao entram automaticamente neste ZIP.\n"
        "Os originais e os lotes novos nao foram modificados.\n"
        "O ZIP considera apenas as musicas novas completas presentes no momento da execucao.\n"
        "Se baixar mais lotes, execute novamente para um novo destino.\n"
        "Apos montar a biblioteca, confira a quantidade, execute Scan Songs e teste\n"
        "antes de substituir a pasta antiga.\n"
    )
    (destination / "LEIA-ME.txt").write_text(readme, encoding="utf-8")
    expected = {}
    with tempfile.TemporaryDirectory(prefix="compactando-", dir=destination) as temporary:
        partial = Path(temporary) / "complemento.zip"
        with zipfile.ZipFile(
            partial, "w", compression=zipfile.ZIP_STORED, allowZip64=True
        ) as archive:
            archive.writestr("LEIA-ME.txt", readme)
            for index, song in enumerate(selected, 1):
                print(f"ZIP {index}/{len(selected)}: {song.artist} - {song.title}", flush=True)
                for asset in song.assets:
                    source = song.folder / asset.name
                    if library.linked(source):
                        raise ValueError("Arquivo virou link durante a copia; execute novamente")
                    name = "Complemento-antigas/" + song.relative + "/" + asset.name
                    if "\\" in name or ":" in name or ".." in PurePosixPath(name).parts:
                        raise ValueError("Caminho de musica nao e portatil para Windows")
                    if name.casefold() in expected:
                        raise ValueError("Nomes de destino repetidos no Windows")
                    result = hashlib.sha256()
                    size = 0
                    with (
                        source.open("rb") as file,
                        archive.open(name, "w", force_zip64=True) as output,
                    ):
                        for block in iter(lambda: file.read(1024 * 1024), b""):
                            result.update(block)
                            size += len(block)
                            output.write(block)
                    if result.hexdigest() != asset.sha256 or size != asset.size:
                        raise ValueError(
                            "Arquivo mudou depois da comparacao; ZIP incompleto descartado"
                        )
                    expected[name.casefold()] = asset.sha256
        print("Conferindo todos os arquivos do ZIP...", flush=True)
        with zipfile.ZipFile(partial) as archive:
            for name in archive.namelist():
                if name == "LEIA-ME.txt":
                    continue
                result = hashlib.sha256()
                with archive.open(name) as file:
                    for block in iter(lambda: file.read(1024 * 1024), b""):
                        result.update(block)
                if result.hexdigest() != expected[name.casefold()]:
                    raise ValueError("Falha na verificacao do ZIP; resultado descartado")
        partial.rename(destination / "Complemento-antigas.zip")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--antigas", type=Path, required=True, help="Songs atual do Clone Hero")
    parser.add_argument("--novas", type=Path, required=True, help="Songs dos lotes baixados")
    parser.add_argument(
        "--destino", type=Path, required=True, help="Pasta nova para ZIP e relatorios"
    )
    args = parser.parse_args()
    try:
        summary = export(args.antigas, args.novas, args.destino)
    except (OSError, ValueError, zipfile.BadZipFile) as exc:
        parser.exit(1, f"Falha: {exc}\nSuas colecoes originais foram preservadas.\n")
    print(json.dumps(summary, ensure_ascii=False, indent=2), flush=True)
    print(f"\nConcluido! ZIP e relatorios: {args.destino.absolute()}", flush=True)


if __name__ == "__main__":
    main()
