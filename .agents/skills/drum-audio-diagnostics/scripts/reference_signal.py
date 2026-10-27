"""Bounded spectral rules for the chart-reference experiment, without ML weights."""

from __future__ import annotations

import math

import inspect_audio as spectral
import numpy as np

BANDS = {
    "low": (40, 200),
    "mid": (200, 4000),
    "high": (4000, 16000),
    "sub_bass": (40, 120),
    "upper_mid": (1000, 4000),
    "upper_high": (8000, 16000),
}
BASELINE = {"KICK": "low", "SNARE_PROXY": "mid", "YELLOW_CYMBAL_PROXY": "high"}
# Fixed before seeing evaluation labels. Tuning changes only band/peak threshold.
GRID = [
    (band, mad, floor) for band in BANDS for mad in (1, 2, 3, 4, 6) for floor in (0.01, 0.02, 0.05)
]


def features(power):
    frequencies = np.fft.rfftfreq(spectral.N_FFT, 1 / spectral.RATE)
    magnitude = np.log1p(1000 * np.sqrt(power))
    flux = np.maximum(np.diff(magnitude, axis=0, prepend=magnitude[:1]), 0)
    curves = {}
    for name, (low, high) in BANDS.items():
        curve = flux[:, (frequencies >= low) & (frequencies < high)].mean(axis=1)
        windows = np.lib.stride_tricks.sliding_window_view(np.pad(curve, (43, 43), mode="edge"), 87)
        median = np.median(windows, axis=1)
        mad = np.median(np.abs(windows - median[:, None]), axis=1)
        curves[name] = (curve, median, mad)
    return curves


def peaks(curves, rule, start):
    band, factor, floor = rule
    curve, median, mad = curves[band]
    threshold = median + factor * mad + max(float(curve.max()) * floor, 1e-7)
    candidates = np.flatnonzero(
        (curve > threshold) & (curve > np.roll(curve, 1)) & (curve >= np.roll(curve, -1))
    )
    guard = math.ceil(spectral.N_FFT / (2 * spectral.HOP))
    candidates = candidates[(candidates >= guard) & (candidates < len(curve) - guard)]
    selected = []
    for index in sorted(candidates, key=lambda i: float(curve[i]), reverse=True):
        if all(
            abs(index - previous) * spectral.HOP / spectral.RATE >= 0.03 for previous in selected
        ):
            selected.append(int(index))
    return [start + i * spectral.HOP / spectral.RATE for i in sorted(selected)]


def summarize(scores):
    tp = sum(s["tp"] for s in scores)
    fp = sum(s["fp"] for s in scores)
    fn = sum(s["fn"] for s in scores)
    return {
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "precision": tp / (tp + fp) if tp + fp else None,
        "recall": tp / (tp + fn) if tp + fn else None,
        "f1": 2 * tp / (2 * tp + fp + fn) if 2 * tp + fp + fn else None,
    }


def calibrate(clips, group, score_onsets):
    # No test-song inputs are accepted here: caller passes only training_indices.
    best_rule, best_f1 = None, -1
    for rule in GRID:
        scores = [score_onsets(c["truth"][group], c["predictions"][rule]) for c in clips]
        f1 = summarize(scores)["f1"]
        if f1 is not None and f1 > best_f1:
            best_rule, best_f1 = rule, f1
    if best_rule is None:
        raise ValueError(f"no calibration references for {group}")
    return best_rule


def render_comparison(
    destination,
    title,
    start,
    audios,
    powers,
    references,
    predictions,
    prediction_label="candidatos calibrados na mix (outras músicas)",
):
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(
        len(powers) + 2, 1, figsize=(14, 10), sharex=True, layout="constrained"
    )
    for label, audio in audios.items():
        width = max(1, len(audio) // 1800)
        blocks = audio[: len(audio) // width * width].reshape(-1, width, 2)
        times = start + (np.arange(len(blocks)) + 0.5) * width / spectral.RATE
        axes[0].plot(times, np.max(np.abs(blocks), axis=(1, 2)), label=label, alpha=0.7)
    axes[0].set(title=title, ylabel="Envelope |amplitude|")
    axes[0].legend()
    vmax = max(float(10 * np.log10(np.maximum(p, 1e-16)).max()) for p in powers.values())
    for axis, (label, power) in zip(axes[1:-1], powers.items(), strict=True):
        times = start + np.arange(len(power)) * spectral.HOP / spectral.RATE
        frequencies = np.fft.rfftfreq(spectral.N_FFT, 1 / spectral.RATE)
        axis.pcolormesh(
            times,
            frequencies[1:],
            10 * np.log10(np.maximum(power[:, 1:].T, 1e-16)),
            shading="auto",
            cmap="magma",
            vmin=vmax - 80,
            vmax=vmax,
            rasterized=True,
        )
        axis.set(yscale="log", ylim=(40, 18000), ylabel=f"{label}\nHz")
    names = list(references)
    colors = ["#e07830", "#3b8fba", "#9159bd", "#67706a", "#a76648"]
    for index, (group, color) in enumerate(zip(names, colors, strict=True)):
        axes[-1].scatter(
            references[group], [index] * len(references[group]), color=color, marker="|", s=180
        )
        candidate = predictions.get(group, [])
        axes[-1].scatter(
            candidate,
            [index - 0.22] * len(candidate),
            color=color,
            marker="x",
            s=14,
        )
    axes[-1].set(
        yticks=range(len(names)),
        yticklabels=names,
        xlabel="Tempo no áudio (s)",
        title=f"Traços: chart de referência; x: {prediction_label}",
    )
    axes[-1].set_xlim(start, start + len(next(iter(audios.values()))) / spectral.RATE)
    for axis in axes:
        axis.grid(alpha=0.12)
    fig.savefig(destination, dpi=110)
    plt.close(fig)
