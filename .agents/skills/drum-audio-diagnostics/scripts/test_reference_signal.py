"""Optional DSP regressions: run with the chart-reference script's dependencies."""

import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import chart_reference as experiment
import inspect_audio as spectral
import numpy as np
from reference_signal import BASELINE, GRID, calibrate, features, peaks

from drumforge.diagnostics.matching import score_onsets


def authored_audio():
    clock = np.arange(spectral.RATE * 2) / spectral.RATE
    signal = np.zeros_like(clock)
    for onset, frequency, amplitude in [(0.25, 9000, 0.025), (0.5, 65, 0.8), (0.5, 9000, 0.025)]:
        elapsed = clock - onset
        selected = elapsed >= 0
        t = elapsed[selected]
        signal[selected] += (
            amplitude
            * (1 - np.exp(-t / 0.001))
            * np.exp(-t / 0.03)
            * np.sin(2 * np.pi * frequency * t)
        )
    return np.column_stack((signal, signal))


class SignalReferenceTests(unittest.TestCase):
    def test_original_peak_rules_are_reproduced_exactly(self):
        power = spectral.spectrum(authored_audio())
        original = spectral.band_candidates(power)
        curves = features(power)
        for band in ("low", "mid", "high"):
            expected = 12 + original[band]["peaks"] * spectral.HOP / spectral.RATE
            np.testing.assert_allclose(peaks(curves, (band, 3, 0.02), 12), expected)

    def test_silence_has_no_candidates_at_any_threshold(self):
        curves = features(spectral.spectrum(np.zeros((spectral.RATE, 2))))
        self.assertTrue(all(not peaks(curves, rule, 0) for rule in GRID))

    def test_stereo_power_preserves_opposite_phase_attacks(self):
        audio = authored_audio()
        opposite = audio.copy()
        opposite[:, 1] *= -1
        np.testing.assert_allclose(spectral.spectrum(audio), spectral.spectrum(opposite))

    def test_decoder_tail_crop_preserves_start_and_exact_sample_count(self):
        data = np.arange((spectral.RATE + 500) * 2).reshape(-1, 2)
        with patch.object(spectral, "decode", return_value=data) as decode:
            audio, length = experiment.exact_excerpt(Path("test.ogg"), "ffmpeg", 120, 1)
        decode.assert_called_once_with(Path("test.ogg"), "ffmpeg", 120, 1.1)
        np.testing.assert_array_equal(audio, data[: spectral.RATE])
        self.assertEqual(length, spectral.RATE + 500)

    def test_short_stem_is_rejected_without_padding(self):
        with patch.object(spectral, "decode", return_value=np.zeros((100, 2))):
            with self.assertRaisesRegex(ValueError, "does not cover"):
                experiment.exact_excerpt(Path("test.ogg"), "ffmpeg", 0, 1)

    def test_calibration_selects_a_rule_using_only_its_given_references(self):
        wanted = GRID[-1]
        predictions = {rule: ([1.0] if rule == wanted else []) for rule in GRID}
        chosen = calibrate(
            [{"truth": {"KICK": [1.0]}, "predictions": predictions}], "KICK", score_onsets
        )
        self.assertEqual(chosen, wanted)

    def test_forward_profile_needs_no_chart_and_preserves_simultaneous_groups(self):
        with tempfile.TemporaryDirectory() as work:
            root = Path(work)
            (root / "audio.wav").write_bytes(b"authored test data")
            profile = {
                "schema_version": 1,
                "kind": "experimental_spectral_peak_rules",
                "fft_size": spectral.N_FFT,
                "hop_samples": spectral.HOP,
                "sample_rate_hz": spectral.RATE,
                "bands_hz": experiment.BANDS,
                "modes": {"mix": {g: [band, 3, 0.02] for g, band in BASELINE.items()}},
            }
            path = root / "profile.json"
            path.write_text(json.dumps(profile))
            args = experiment.argparse.Namespace(
                start=0,
                duration=2,
                profile=path,
                mode="mix",
                audio=root / "audio.wav",
                ffmpeg_path="ffmpeg",
                out=root / "result",
            )
            audio = authored_audio()
            with patch.object(experiment, "exact_excerpt", return_value=(audio, len(audio))):
                experiment.predict(args)
            text = (args.out / "candidate-notes.csv").read_text()
            self.assertIn("KICK", text)
            self.assertIn("YELLOW_CYMBAL_PROXY", text)
            self.assertIn("unverified_spectral_candidate", text)

    def test_frozen_evaluation_never_calibrates_or_invents_missing_stems(self):
        from reference_holdout import evaluate

        with tempfile.TemporaryDirectory() as work:
            root = Path(work)
            song = root / "new-song"
            song.mkdir()
            (song / "song.ini").write_text("[song]\npro_drums=True\nname=Authored\nartist=Test\n")
            (song / "song.wav").write_bytes(b"authored placeholder; decoder is mocked")
            (song / "notes.chart").write_text(
                "[Song]\n{\n Resolution = 192\n}\n[SyncTrack]\n{\n 0 = B 120000\n}\n"
                "[ExpertDrums]\n{\n 192 = N 0 0\n 192 = N 1 0\n 192 = N 2 0\n 192 = N 66 0\n}\n"
            )
            training = root / "training.json"
            training.write_text(
                json.dumps({"songs": [{"id": "old", "assets_sha256": {"notes.mid": "old-chart"}}]})
            )
            profile = {
                "schema_version": 1,
                "kind": "experimental_spectral_peak_rules",
                "fft_size": spectral.N_FFT,
                "hop_samples": spectral.HOP,
                "sample_rate_hz": spectral.RATE,
                "bands_hz": experiment.BANDS,
                "source_songs": ["old"],
                "source_recipe_sha256": experiment.digest(training),
                "modes": {
                    m: {g: [b, 3, 0.02] for g, b in BASELINE.items()} for m in experiment.MODES
                },
            }
            path = root / "profile.json"
            path.write_text(json.dumps(profile))
            before = path.read_bytes()
            recipe = root / "recipe.json"
            recipe.write_text(
                json.dumps(
                    {
                        "frozen_profile_sha256": hashlib.sha256(before).hexdigest(),
                        "songs": [
                            {
                                "id": "new",
                                "folder": "new-song",
                                "assets_sha256": {
                                    p.name: experiment.digest(p) for p in song.iterdir()
                                },
                                "excerpts": [{"start": 0, "duration": 2}],
                            }
                        ],
                    }
                )
            )
            args = experiment.argparse.Namespace(
                recipe=recipe,
                profile=path,
                training_recipe=training,
                library_root=root,
                out=root / "result",
                ffmpeg_path="ffmpeg",
            )
            audio = authored_audio()
            with (
                patch.object(experiment, "exact_excerpt", return_value=(audio, len(audio))),
                patch.object(
                    experiment, "calibrate", side_effect=AssertionError("calibration forbidden")
                ),
                patch(
                    "reference_signal.calibrate",
                    side_effect=AssertionError("calibration forbidden"),
                ),
            ):
                evaluate(args, experiment)
            report = json.loads((args.out / "report.json").read_text())
            self.assertFalse(report["calibration_performed"])
            self.assertEqual(report["mode_coverage"], {"mix": ["new"], "drums": []})
            self.assertEqual(path.read_bytes(), before)
            self.assertEqual((args.out / "frozen-profile.json").read_bytes(), before)
            self.assertEqual(report["songs"][0]["chart_format"], "chart")


if __name__ == "__main__":
    unittest.main()
