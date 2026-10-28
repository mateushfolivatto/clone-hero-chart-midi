"""Exporta somente musicas candidatas ausentes da biblioteca local, sem altera-la."""

from __future__ import annotations

import argparse
import importlib
import json
import zipfile
from pathlib import Path

complement = importlib.import_module(
    "drumforge.library.complement" if __package__ else "complement"
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidatas", type=Path, required=True, help="Songs dos novos lotes")
    parser.add_argument("--biblioteca", type=Path, required=True, help="Songs atual do Clone Hero")
    parser.add_argument(
        "--destino", type=Path, required=True, help="Pasta nova para ZIP e relatorios"
    )
    args = parser.parse_args()
    try:
        summary = complement.export(args.candidatas, args.biblioteca, args.destino, additions=True)
    except (OSError, ValueError, zipfile.BadZipFile) as exc:
        parser.exit(1, f"Falha: {exc}\nBiblioteca e downloads foram preservados.\n")
    print(json.dumps(summary, ensure_ascii=False, indent=2), flush=True)
    print(f"\nZIP e relatorios: {args.destino.absolute()}", flush=True)


if __name__ == "__main__":
    main()
