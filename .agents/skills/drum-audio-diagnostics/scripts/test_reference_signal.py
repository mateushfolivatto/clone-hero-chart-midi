"""Optional DSP regressions: run with the chart-reference script's dependencies."""

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


if __name__ == "__main__":
    unittest.main()
