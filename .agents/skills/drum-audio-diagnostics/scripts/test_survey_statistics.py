"""Coverage, one-to-one conditions, bootstrap units and immutable resume checks."""

import csv
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import chart_reference as shared
from reference_signal import summarize
from survey_runner import run
from survey_statistics import (
    bootstrap_delta,
    metrics,
    observations,
    paired_sources,
    temporal_control,
)

ROOT = Path(__file__).resolve().parents[4]


def row(ident, excerpt, mode, tp, fp, fn, method="baseline"):
    return {
        "song_id": ident,
        "excerpt": excerpt,
        "mode": mode,
        "group": "YELLOW_CYMBAL_PROXY",
        "method": method,
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "reference_count": tp + fn,
        "duration_seconds": 20,
    }


class SurveyTests(unittest.TestCase):
    def test_shift_control_is_deterministic_and_preserves_empty_reference_behavior(self):
        self.assertEqual(temporal_control([], [1, 2], 0, 20, "key"), 0)
        actual = temporal_control([1, 2, 3], [1, 2, 3], 0, 20, "key")
        self.assertEqual(actual, temporal_control([1, 2, 3], [1, 2, 3], 0, 20, "key"))
        self.assertLess(actual, 3)

    def test_pairing_uses_only_the_same_available_excerpt(self):
        rows = [
            row("a", 0, "mix", 100, 0, 0),
            row("a", 1, "mix", 2, 0, 0),
            row("a", 1, "drums", 1, 0, 1),
        ]
        pair = paired_sources(rows, "mix", "drums", "YELLOW_CYMBAL_PROXY", "baseline")
        self.assertEqual(pair["left_metrics"]["tp"], 2)
        self.assertEqual(pair["right_metrics"]["tp"], 1)
        self.assertEqual(pair["left_metrics"]["excerpts"], 1)

    def test_song_bootstrap_keeps_methods_and_excerpts_paired(self):
        rows = [
            row(ident, excerpt, "mix", tp, fp, fn, method)
            for ident, tp, fp, fn in [("a", 2, 0, 8), ("b", 80, 10, 0)]
            for excerpt in [0, 1]
            for method in ["baseline", "frozen"]
        ]
        result = bootstrap_delta(rows, draws=100, seed=3)
        self.assertEqual(result["delta_f1_ci95"], [0, 0])
        self.assertEqual(result["unit"], "whole_song")
        self.assertEqual(result, bootstrap_delta(rows, draws=100, seed=3))

    def test_false_alarms_without_references_remain_in_pooled_f1(self):
        result = metrics([row("a", 0, "mix", 1, 0, 0), row("b", 0, "mix", 0, 9, 0)])
        self.assertAlmostEqual(result["f1"], 2 / 11)
        self.assertEqual(result["median_song_f1_with_references"], 1)
        self.assertEqual(result["positive_reference_songs"], 1)
        self.assertEqual(result["songs"], 2)

    def test_conditional_recall_does_not_double_match_duplicate_notes(self):
        with tempfile.TemporaryDirectory() as work:
            root = Path(work)
            folder = root / "new"
            folder.mkdir()
            recipe = {
                "frozen_profile_sha256": "authored",
                "songs": [{"id": "new", "artist": "Test", "title": "Authored"}],
            }
            score = summarize([{"tp": 1, "fp": 0, "fn": 1}])
            report = {
                "profile_sha256": "authored",
                "excerpts": [
                    {
                        "excerpt": 0,
                        "duration_seconds": 20,
                        "available_groups": {"mix": ["YELLOW_CYMBAL_PROXY"]},
                        "reference_counts": {"YELLOW_CYMBAL_PROXY": 2},
                    }
                ],
                "songs": [
                    {
                        "modes": {
                            "mix": {"YELLOW_CYMBAL_PROXY": {"baseline": score, "frozen": score}}
                        }
                    }
                ],
            }
            (folder / "report.json").write_text(json.dumps(report))
            with (folder / "chart-events.csv").open("w", newline="") as stream:
                writer = csv.DictWriter(
                    stream, fieldnames=["excerpt", "group", "tick", "time_seconds"]
                )
                writer.writeheader()
                for group in ["YELLOW_CYMBAL_PROXY", "YELLOW_CYMBAL_PROXY", "SNARE_PROXY"]:
                    writer.writerow({"excerpt": 0, "group": group, "tick": 480, "time_seconds": 1})
            with (folder / "candidates.csv").open("w", newline="") as stream:
                writer = csv.DictWriter(
                    stream, fieldnames=["excerpt", "group", "mode", "method", "time_seconds"]
                )
                writer.writeheader()
                for method in ["baseline", "frozen"]:
                    writer.writerow(
                        {
                            "excerpt": 0,
                            "group": "YELLOW_CYMBAL_PROXY",
                            "mode": "mix",
                            "method": method,
                            "time_seconds": 1.01,
                        }
                    )
            rows = observations(recipe, root)
            self.assertEqual(rows[0]["with_other_references"], 2)
            self.assertEqual(rows[0]["with_other_tp"], 1)
            self.assertEqual(rows[0]["without_other_tp"], 0)

    def test_resume_reuses_verified_outputs_and_rejects_modified_candidates(self):
        with tempfile.TemporaryDirectory() as work:
            root = Path(work)
            song = root / "song"
            song.mkdir()
            (song / "notes.mid").write_bytes(b"authored placeholder; inference mocked")
            profile = ROOT / "docs/experiments/five-song-spectral-profile.json"
            recipe = root / "recipe.json"
            recipe.write_text(
                json.dumps(
                    {
                        "frozen_profile_sha256": shared.digest(profile),
                        "songs": [
                            {
                                "id": "new",
                                "folder": "song",
                                "title": "Authored",
                                "artist": "Test",
                                "assets_sha256": {"notes.mid": shared.digest(song / "notes.mid")},
                                "excerpts": [{"start": 0, "duration": 2}],
                            }
                        ],
                    }
                )
            )
            args = shared.argparse.Namespace(
                recipe=recipe,
                profile=profile,
                training_recipe=ROOT / "docs/experiments/five-song-chart-reference.json",
                library_root=root,
                out=root / "result",
                jobs=1,
                resume=False,
                ffmpeg_path="ffmpeg",
            )

            def execute(command, **kwargs):
                destination = Path(command[command.index("--out") + 1])
                destination.mkdir()
                subrecipe = Path(command[command.index("--recipe") + 1])
                (destination / "report.json").write_text(
                    json.dumps({"evaluation_recipe_sha256": shared.digest(subrecipe)})
                )
                for name in ["chart-events.csv", "candidates.csv"]:
                    (destination / name).write_text("authored\n")
                return subprocess.CompletedProcess(command, 0, "", "")

            with (
                patch("survey_runner.subprocess.check_output", return_value="mock ffmpeg\n"),
                patch("survey_runner.subprocess.run", side_effect=execute) as execute_mock,
            ):
                run(args, shared)
                args.resume = True
                run(args, shared)
                self.assertEqual(execute_mock.call_count, 1)
                (args.out / "new/candidates.csv").write_text("modified")
                with self.assertRaisesRegex(ValueError, "failed"):
                    run(args, shared)
                self.assertEqual(execute_mock.call_count, 1)


if __name__ == "__main__":
    unittest.main()
