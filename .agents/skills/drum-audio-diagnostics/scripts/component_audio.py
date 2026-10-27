"""Explicit component views and signal audits; no model or chart labels required."""

from __future__ import annotations

import numpy as np

from drumforge.diagnostics.chart_reference import TARGET_GROUPS


def validate_sources(sources, available):
    if not isinstance(sources, dict) or not set(sources).issubset(TARGET_GROUPS):
        raise ValueError("component_sources must map supported groups to selected audio files")
    if any(not isinstance(name, str) or name not in available for name in sources.values()):
        raise ValueError("component source is not a selected playback asset")
    if len(set(sources.values())) != len(sources):
        raise ValueError("distinct component groups require distinct source files")


def prepare_views(streams, sources):
    validate_sources(sources, streams)
    if not streams:
        raise ValueError("no audio streams")
    if len({a.shape for a in streams.values()}) != 1:
        raise ValueError("component streams must have identical decoded shapes")
    if any(a.ndim != 2 or a.shape[1] != 2 or not np.isfinite(a).all() for a in streams.values()):
        raise ValueError("component streams require finite stereo samples")
    audits = {
        name: {
            "peak": float(np.abs(a).max()),
            "rms": float(np.sqrt(np.mean(a.astype(np.float64) ** 2))),
            "digital_silence": not bool(np.any(a)),
        }
        for name, a in streams.items()
    }
    mix = np.sum(list(streams.values()), axis=0)
    signals = {"mix": mix}
    drum_parts = [a for name, a in streams.items() if name.casefold().startswith("drums")]
    excluded = []
    if drum_parts:
        drums = np.sum(drum_parts, axis=0)
        if np.any(drums):
            signals["drums"] = drums
        else:
            excluded.append({"mode": "drums", "reason": "digital_silence"})
    groups = {}
    for group, name in sources.items():
        if audits[name]["digital_silence"]:
            excluded.append({"mode": "components", "group": group, "reason": "digital_silence"})
        else:
            groups[group] = streams[name]
    gain = 1 / max(1, *(float(np.abs(a).max()) for a in [*signals.values(), *groups.values()]))
    signals = {name: a * gain for name, a in signals.items()}
    views = {mode: {g: a for g in TARGET_GROUPS} for mode, a in signals.items()}
    if groups:
        views["components"] = {g: a * gain for g, a in groups.items()}
    return signals, views, audits, excluded, gain
