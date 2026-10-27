"""One-to-one onset scoring and whole-song holdout boundaries for diagnostics."""

from __future__ import annotations

import math
import statistics
from collections.abc import Sequence


def score_onsets(
    reference: Sequence[float], predictions: Sequence[float], *, tolerance: float = 0.03
) -> dict[str, int | float | None]:
    if not math.isfinite(tolerance) or tolerance <= 0:
        raise ValueError("tolerance must be finite and positive")
    if any(not math.isfinite(value) for value in (*reference, *predictions)):
        raise ValueError("onset times must be finite")
    expected, detected = sorted(reference), sorted(predictions)
    i = j = 0
    errors = []
    # Earliest compatible pair maximizes the number of matches within a fixed window.
    while i < len(expected) and j < len(detected):
        error = detected[j] - expected[i]
        if error < -tolerance - 1e-12:
            j += 1
        elif error > tolerance + 1e-12:
            i += 1
        else:
            errors.append(error)
            i += 1
            j += 1
    tp = len(errors)
    fp, fn = len(detected) - tp, len(expected) - tp
    return {
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "precision": tp / (tp + fp) if tp + fp else None,
        "recall": tp / (tp + fn) if tp + fn else None,
        "f1": 2 * tp / (2 * tp + fp + fn) if 2 * tp + fp + fn else None,
        "mean_absolute_error_ms": statistics.mean(abs(v) for v in errors) * 1000 if tp else None,
        "median_signed_error_ms": statistics.median(errors) * 1000 if tp else None,
    }


def training_indices(song_ids: Sequence[str], held_out: str) -> list[int]:
    if held_out not in song_ids or len(set(song_ids)) < 2:
        raise ValueError("holdout requires a known song and at least two distinct songs")
    return [index for index, song in enumerate(song_ids) if song != held_out]
