"""Command-line entry point. Importing the CLI does not load ML backends."""

import argparse
import json
from pathlib import Path

from drumforge import __version__
from drumforge.doctor import diagnose


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="drumforge", description="Drum Chart Forge - local environment diagnostics"
    )
    parser.add_argument("--version", action="version", version=__version__)
    commands = parser.add_subparsers(dest="command", required=True)
    doctor = commands.add_parser("doctor", help="Check runtime and optional audio/ML tools")
    doctor.add_argument("--json", action="store_true", help="Print a structured report")
    doctor.add_argument("--write-dir", type=Path, default=Path.cwd())
    doctor.add_argument("--model-path", type=Path, help="Check a local checkpoint (no download)")
    args = parser.parse_args(argv)
    report = diagnose(args.write_dir, args.model_path)
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=True))
    else:
        for check in report["checks"]:
            print(f"[{check['status']}] {check['name']}: {check['detail']}")
    return 1 if any(check["status"] == "error" for check in report["checks"]) else 0
