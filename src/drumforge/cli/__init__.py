"""Command-line entry point. Importing the CLI does not load ML backends."""

import argparse
import json
from pathlib import Path

from drumforge import __version__
from drumforge.audio import prepare_audio
from drumforge.audio.prepare import AudioPreparationError
from drumforge.doctor import diagnose
from drumforge.separation import PassthroughSeparator
from drumforge.transcription.adtof import AdtofTranscriber, TranscriptionError
from drumforge.transcription.inspect_midi import MidiInspectionError, write_midi_diagnostics


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
    inspect = commands.add_parser(
        "inspect-midi", help="Count raw GM drum notes and write timestamp/velocity diagnostics"
    )
    inspect.add_argument("input", type=Path, help="Raw GM percussion MIDI (not a game chart)")
    inspect.add_argument("--out", type=Path, required=True, help="New diagnostic directory")
    transcribe = commands.add_parser("transcribe", help="Create raw drum MIDI with ADTOF")
    transcribe.add_argument("input", type=Path, help="Prepared mono WAV input")
    transcribe.add_argument("--midi-out", type=Path, required=True)
    transcribe.add_argument("--weights", type=Path, required=True)
    transcribe.add_argument("--backend-python", type=Path)
    transcribe.add_argument("--skip-separation", action="store_true")
    threshold_group = transcribe.add_mutually_exclusive_group()
    threshold_group.add_argument("--threshold", type=float)
    threshold_group.add_argument(
        "--thresholds",
        type=float,
        nargs=5,
        metavar=("BD", "SD", "HH", "TT", "CY"),
        help="Detection thresholds: bass drum, snare, hi-hat, toms, cymbals",
    )
    args = parser.parse_args(argv)
    if args.command == "inspect-midi":
        try:
            inspection = write_midi_diagnostics(args.input, args.out)
        except MidiInspectionError as exc:
            parser.error(str(exc))
        print(json.dumps(inspection, indent=2, ensure_ascii=True))
        return 0
    if args.command == "prepare-audio":
        try:
            prepared_result = prepare_audio(
                args.input,
                args.work_dir,
                ffmpeg_path=args.ffmpeg_path,
                ffprobe_path=args.ffprobe_path,
            )
        except AudioPreparationError as exc:
            parser.error(str(exc))
        print(json.dumps(prepared_result.to_dict(), indent=2, ensure_ascii=True))
        return 0
    if args.command == "transcribe":
        if not args.skip_separation:
            parser.error("no separation backend is implemented; pass --skip-separation")
        try:
            separated = PassthroughSeparator().separate(args.input, args.midi_out.parent)
            transcription_result = AdtofTranscriber(
                args.weights,
                threshold=args.threshold,
                thresholds=args.thresholds,
                python_executable=args.backend_python,
            ).transcribe(separated.drums_audio, args.midi_out)
        except (AudioPreparationError, TranscriptionError) as exc:
            parser.error(str(exc))
        print(json.dumps(transcription_result.to_dict(), indent=2, ensure_ascii=True))
        return 0
    report = diagnose(args.write_dir, args.model_path)
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=True))
    else:
        for check in report["checks"]:
            print(f"[{check['status']}] {check['name']}: {check['detail']}")
    return 1 if any(check["status"] == "error" for check in report["checks"]) else 0
