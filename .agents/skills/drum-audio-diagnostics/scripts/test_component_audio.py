"""Optional regressions for source coverage and chart-free component candidates."""

import csv
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import chart_reference as shared
import numpy as np
from component_audio import prepare_views, validate_sources
from component_predict import predict_components
from reference_holdout import evaluate

ROOT = Path(__file__).resolve().parents[4]
PROFILE = ROOT / "docs/experiments/five-song-spectral-profile.json"


def tone(frequency):
    clock = np.arange(2 * shared.spectral.RATE) / shared.spectral.RATE - 0.5
    t = np.maximum(clock, 0)
    signal = np.sin(2 * np.pi * frequency * t) * (1 - np.exp(-t / 0.001)) * np.exp(-t / 0.03)
    return np.column_stack((signal, signal))


class ComponentAudioTests(unittest.TestCase):
    def test_digital_silence_is_excluded_but_very_quiet_audio_is_preserved(self):
        silent = np.zeros((100, 2))
        quiet = np.full((100, 2), 1e-20)
        signals, views, audits, excluded, gain = prepare_views(
            {"song.wav": np.ones((100, 2)), "drums_1.wav": quiet, "drums_2.wav": silent},
            {"KICK": "drums_1.wav", "SNARE_PROXY": "drums_2.wav"},
        )
        self.assertEqual(gain, 1)
        self.assertIn("drums", signals)
        self.assertEqual(set(views["components"]), {"KICK"})
        self.assertFalse(audits["drums_1.wav"]["digital_silence"])
        self.assertEqual(
            excluded, [{"mode": "components", "group": "SNARE_PROXY", "reason": "digital_silence"}]
        )

    def test_invalid_selection_shapes_and_nonfinite_audio_fail(self):
        for selection in [{"UNKNOWN": "a"}, {"KICK": "absent"}, {"KICK": "a", "SNARE_PROXY": "a"}]:
            with self.subTest(selection=selection), self.assertRaises(ValueError):
                validate_sources(selection, {"a"})
        for streams in [
            {"a": np.zeros((100, 2)), "b": np.zeros((99, 2))},
            {"a": np.full((100, 2), np.nan)},
        ]:
            with self.subTest(streams=list(streams)), self.assertRaises(ValueError):
                prepare_views(streams, {})

    def test_forward_components_need_no_chart_and_keep_simultaneous_attacks(self):
        with tempfile.TemporaryDirectory() as work:
            root = Path(work)
            paths = {name: root / (name + ".wav") for name in ["kick", "snare", "high"]}
            for name, path in paths.items():
                path.write_bytes(name.encode())
            args = shared.argparse.Namespace(
                kick=paths["kick"],
                snare=paths["snare"],
                high_percussion=paths["high"],
                start=12,
                duration=2,
                rules="baseline",
                profile=PROFILE,
                ffmpeg_path="ffmpeg",
                out=root / "result",
            )

            def decode(path, *_):
                audio = tone({"kick": 65, "snare": 900, "high": 9000}[path.stem])
                return audio, len(audio)

            with (
                patch.object(shared, "exact_excerpt", side_effect=decode),
                patch.object(
                    shared, "read_chart_reference", side_effect=AssertionError("chart forbidden")
                ),
            ):
                predict_components(args, shared)
            with (args.out / "candidate-notes.csv").open() as stream:
                rows = list(csv.DictReader(stream))
            for group in ["KICK", "YELLOW_CYMBAL_PROXY"]:
                self.assertTrue(
                    any(
                        r["group"] == group and abs(float(r["time_seconds"]) - 12.5) < 0.03
                        for r in rows
                    )
                )
            report = json.loads((args.out / "report.json").read_text())
            self.assertEqual(report["method"], "chart_free_explicit_components")
            self.assertEqual(report["profile_sha256"], shared.digest(PROFILE))

    def test_changing_source_during_decoding_is_rejected_before_output(self):
        with tempfile.TemporaryDirectory() as work:
            root = Path(work)
            paths = [root / f"{i}.wav" for i in range(3)]
            for path in paths:
                path.write_bytes(b"before")
            args = shared.argparse.Namespace(
                kick=paths[0],
                snare=paths[1],
                high_percussion=paths[2],
                start=0,
                duration=2,
                rules="baseline",
                profile=PROFILE,
                ffmpeg_path="ffmpeg",
                out=root / "result",
            )

            def decode(path, *_):
                path.write_bytes(b"after")
                return tone(65), 2 * shared.spectral.RATE

            with patch.object(shared, "exact_excerpt", side_effect=decode):
                with self.assertRaisesRegex(ValueError, "changed"):
                    predict_components(args, shared)
            self.assertFalse(args.out.exists())

    def test_evaluation_reports_per_class_coverage_without_scoring_missing_audio(self):
        with tempfile.TemporaryDirectory() as work:
            root = Path(work)
            folder = root / "song"
            folder.mkdir()
            (folder / "song.ini").write_text("[song]\npro_drums=True\nname=Authored\n")
            (folder / "notes.chart").write_text(
                "[Song]\n{\n Resolution = 480\n}\n[SyncTrack]\n{\n 0 = B 120000\n}\n"
                "[ExpertDrums]\n{\n 480 = N 0 0\n 480 = N 1 0\n 480 = N 2 0\n 480 = N 66 0\n"
                " 2400 = N 0 0\n 2400 = N 1 0\n 2400 = N 2 0\n 2400 = N 66 0\n}\n"
            )
            for name in ["song.wav", "drums_1.wav", "drums_2.wav", "drums_3.wav"]:
                (folder / name).write_bytes(name.encode())
            recipe = root / "recipe.json"
            recipe.write_text(
                json.dumps(
                    {
                        "frozen_profile_sha256": shared.digest(PROFILE),
                        "songs": [
                            {
                                "id": "authored-component-regression",
                                "folder": "song",
                                "assets_sha256": {
                                    p.name: shared.digest(p) for p in folder.iterdir()
                                },
                                "component_sources": {
                                    "KICK": "drums_1.wav",
                                    "SNARE_PROXY": "drums_2.wav",
                                    "YELLOW_CYMBAL_PROXY": "drums_3.wav",
                                },
                                "excerpts": [
                                    {"start": 0, "duration": 2},
                                    {"start": 2, "duration": 2},
                                ],
                            }
                        ],
                    }
                )
            )
            args = shared.argparse.Namespace(
                recipe=recipe,
                profile=PROFILE,
                training_recipe=ROOT / "docs/experiments/five-song-chart-reference.json",
                library_root=root,
                out=root / "result",
                ffmpeg_path="ffmpeg",
            )

            def decode(path, _, start, duration):
                audio = tone(9000)
                if path.stem == "drums_2" or (start == 2 and path.stem.startswith("drums")):
                    audio = np.zeros_like(audio)
                return audio, len(audio)

            with patch.object(shared, "exact_excerpt", side_effect=decode):
                evaluate(args, shared)
            report = json.loads((args.out / "report.json").read_text())
            self.assertEqual(report["class_coverage"]["mix"]["KICK"]["excerpts"], 2)
            self.assertEqual(report["class_coverage"]["drums"]["KICK"]["excerpts"], 1)
            self.assertEqual(report["class_coverage"]["components"]["SNARE_PROXY"]["excerpts"], 0)
            self.assertNotIn("SNARE_PROXY", report["aggregate"]["components"])
            self.assertEqual(report["class_coverage"]["components"]["KICK"]["reference_count"], 1)


if __name__ == "__main__":
    unittest.main()
