"""Command-line entry point. Importing the CLI does not load ML backends."""

import argparse
import json
from pathlib import Path

from drumforge import __version__
from drumforge.audio import prepare_audio
from drumforge.audio.prepare import AudioPreparationError
from drumforge.doctor import diagnose


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="drumforge", description="Drum Chart Forge - audio-to-chart tooling"
    )
    parser.add_argument("--version", action="version", version=__version__)
    commands = parser.add_subparsers(dest="command", required=True)
    doctor = commands.add_parser("doctor", help="Check runtime and optional audio/ML tools")
    doctor.add_argument("--json", action="store_true", help="Print a structured report")
    doctor.add_argument("--write-dir", type=Path, default=Path.cwd())
    doctor.add_argument("--model-path", type=Path, help="Check a local checkpoint (no download)")
    prepare = commands.add_parser("prepare-audio", help="Probe and normalize audio to cached WAV")
    prepare.add_argument("input", type=Path)
    prepare.add_argument("--work-dir", type=Path, required=True)
    prepare.add_argument("--ffmpeg-path", type=Path, default=Path("ffmpeg"))
    prepare.add_argument("--ffprobe-path", type=Path)
    args = parser.parse_args(argv)
    if args.command == "prepare-audio":
        try:
            result = prepare_audio(
                args.input,
                args.work_dir,
                ffmpeg_path=args.ffmpeg_path,
                ffprobe_path=args.ffprobe_path,
            )
        except AudioPreparationError as exc:
            parser.error(str(exc))
        print(json.dumps(result.to_dict(), indent=2, ensure_ascii=True))
        return 0
    report = diagnose(args.write_dir, args.model_path)
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=True))
    else:
        for check in report["checks"]:
            print(f"[{check['status']}] {check['name']}: {check['detail']}")
    return 1 if any(check["status"] == "error" for check in report["checks"]) else 0
