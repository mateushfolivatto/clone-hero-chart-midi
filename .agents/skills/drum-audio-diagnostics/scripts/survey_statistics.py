"""Per-excerpt diagnostics and song-level uncertainty; never calibrates rules."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from statistics import median

import numpy as np
from reference_signal import summarize

from drumforge.diagnostics.matching import match_onsets, score_onsets
from drumforge.diagnostics.survey import identity


def temporal_control(reference, predictions, start, duration, key, draws=31):
    """Exploratory circular-shift control; never changes the actual prediction set."""
    lower, width = start + 0.05, duration - 0.1
    seed = int(hashlib.sha256(("20261027:" + key).encode()).hexdigest()[:8], 16)
    shifts = np.random.default_rng(seed).uniform(0.2, width - 0.2, size=draws)
    counts = []
    for shift in shifts:
        displaced = [lower + (time - lower + shift) % width for time in predictions]
        counts.append(len(match_onsets(reference, displaced)))
    return float(np.mean(counts))


def observations(recipe, reports):
    output = []
    for song in recipe["songs"]:
        folder = reports / song["id"]
        report = json.loads((folder / "report.json").read_text())
        if report["profile_sha256"] != recipe["frozen_profile_sha256"]:
            raise ValueError("survey report used a different profile")
        events, candidates = defaultdict(list), defaultdict(list)
        with (folder / "chart-events.csv").open() as stream:
            for row in csv.DictReader(stream):
                events[(int(row["excerpt"]), row["group"])].append(row)
        with (folder / "candidates.csv").open() as stream:
            for row in csv.DictReader(stream):
                key = (int(row["excerpt"]), row["mode"], row["group"], row["method"])
                candidates[key].append(float(row["time_seconds"]))
        for excerpt in report["excerpts"]:
            index = excerpt["excerpt"]
            duration = excerpt["duration_seconds"]
            hh = events[(index, "YELLOW_CYMBAL_PROXY")]
            count = len(hh)
            density = count / duration
            density_bin = (
                "none"
                if count == 0
                else "low"
                if density < 2
                else "medium"
                if density < 5
                else "high"
            )
            other_ticks = {
                row["tick"] for group in ("KICK", "SNARE_PROXY") for row in events[(index, group)]
            }
            deltas = Counter(
                int(b["tick"]) - int(a["tick"]) for a, b in zip(hh, hh[1:], strict=False)
            )
            regularity = max(deltas.values()) / (count - 1) if count > 1 else None
            for mode, groups in excerpt["available_groups"].items():
                for group in groups:
                    reference = events[(index, group)]
                    times = [float(row["time_seconds"]) for row in reference]
                    if len(times) != excerpt["reference_counts"][group]:
                        raise ValueError("CSV reference count differs from report")
                    for method in ("baseline", "frozen"):
                        detected = candidates[(index, mode, group, method)]
                        score = score_onsets(times, detected)
                        row = {
                            "song_id": song["id"],
                            "artist": song["artist"],
                            "artist_key": identity(song["artist"]),
                            "title": song["title"],
                            "genre": song.get("genre", "unknown"),
                            "excerpt": index,
                            "mode": mode,
                            "group": group,
                            "method": method,
                            "duration_seconds": duration,
                            "reference_count": len(times),
                            "hh_density_per_second": density,
                            "hh_density_bin": density_bin,
                            "hh_tick_regularity": regularity,
                            **score,
                        }
                        if group == "YELLOW_CYMBAL_PROXY":
                            pairs = match_onsets(times, detected)
                            matched = {r for r, _ in pairs}
                            with_other = {
                                i for i, e in enumerate(reference) if e["tick"] in other_ticks
                            }
                            row["with_other_references"] = len(with_other)
                            row["with_other_tp"] = len(matched & with_other)
                            row["without_other_references"] = len(reference) - len(with_other)
                            row["without_other_tp"] = len(matched - with_other)
                            row["shift_control_mean_tp"] = temporal_control(
                                times,
                                detected,
                                excerpt.get("start_seconds", 0),
                                duration,
                                f"{song['id']}:{index}",
                            )
                        output.append(row)
        # Independently recomputed metrics must equal every saved per-song count.
        for mode, groups in report["songs"][0]["modes"].items():
            for group, methods in groups.items():
                for method, expected in methods.items():
                    measured = summarize(
                        [
                            r
                            for r in output
                            if r["song_id"] == song["id"]
                            and (r["mode"], r["group"], r["method"]) == (mode, group, method)
                        ]
                    )
                    if measured != expected:
                        raise ValueError("recomputed onset scores differ from saved report")
    return output


def metrics(rows):
    totals = summarize(rows)
    by_song = defaultdict(list)
    for row in rows:
        by_song[row["song_id"]].append(row)
    song_scores = [summarize(group) for group in by_song.values()]
    positive = [s["f1"] for s in song_scores if s["tp"] + s["fn"] > 0 and s["f1"] is not None]
    return {
        **totals,
        "songs": len(by_song),
        "excerpts": len(rows),
        "duration_seconds": sum(r["duration_seconds"] for r in rows),
        "median_song_f1_with_references": median(positive) if positive else None,
        "positive_reference_songs": len(positive),
    }


def bootstrap_delta(rows, *, draws=1000, seed=20261027):
    """Resample whole songs, keeping their excerpts and both methods together."""
    ids = sorted({r["song_id"] for r in rows})
    if not ids:
        return None
    arrays = []
    for method in ("baseline", "frozen"):
        per_song = [
            summarize([r for r in rows if r["song_id"] == ident and r["method"] == method])
            for ident in ids
        ]
        arrays.append(np.array([[s["tp"], s["fp"], s["fn"]] for s in per_song]))
    indices = np.random.default_rng(seed).integers(0, len(ids), size=(draws, len(ids)))
    f1s = []
    for array in arrays:
        totals = array[indices].sum(axis=1)
        divisor = 2 * totals[:, 0] + totals[:, 1] + totals[:, 2]
        f1s.append(
            np.divide(2 * totals[:, 0], divisor, out=np.full(draws, np.nan), where=divisor > 0)
        )
    differences = f1s[1] - f1s[0]
    valid = differences[np.isfinite(differences)]
    return {
        "draws": draws,
        "seed": seed,
        "unit": "whole_song",
        "delta_f1_ci95": np.quantile(valid, [0.025, 0.975]).tolist() if len(valid) else None,
    }


def paired_sources(rows, left, right, group, method):
    def indexed(mode):
        return {
            (r["song_id"], r["excerpt"]): r
            for r in rows
            if (r["mode"], r["group"], r["method"]) == (mode, group, method)
        }

    a, b = indexed(left), indexed(right)
    common = sorted(set(a) & set(b))
    if any(a[key]["reference_count"] != b[key]["reference_count"] for key in common):
        raise ValueError("paired sources have different references")
    return {
        "left": left,
        "right": right,
        "group": group,
        "method": method,
        "left_metrics": metrics([a[k] for k in common]),
        "right_metrics": metrics([b[k] for k in common]),
        "uncertainty": bootstrap_delta(
            [{**a[k], "method": "baseline"} for k in common]
            + [{**b[k], "method": "frozen"} for k in common]
        ),
    }


def summarize_survey(rows):
    cells = {}
    for mode, group in sorted({(r["mode"], r["group"]) for r in rows}):
        subset = [r for r in rows if (r["mode"], r["group"]) == (mode, group)]
        cells.setdefault(mode, {})[group] = {
            **{
                method: metrics([r for r in subset if r["method"] == method])
                for method in ("baseline", "frozen")
            },
            "uncertainty": bootstrap_delta(subset),
        }
    paired = [
        paired_sources(rows, a, b, g, method)
        for a, b in [("mix", "drums"), ("drums", "components")]
        for g in ("KICK", "SNARE_PROXY", "YELLOW_CYMBAL_PROXY")
        for method in ("baseline", "frozen")
    ]
    density, simultaneity, absent = [], [], []
    for mode in sorted(cells):
        for method in ("baseline", "frozen"):
            hh = [
                r
                for r in rows
                if (r["mode"], r["group"], r["method"]) == (mode, "YELLOW_CYMBAL_PROXY", method)
            ]
            for level in ("none", "low", "medium", "high"):
                subset = [r for r in hh if r["hh_density_bin"] == level]
                denominator = sum(2 * r["tp"] + r["fp"] + r["fn"] for r in subset)
                shifted_tp = sum(r["shift_control_mean_tp"] for r in subset)
                density.append(
                    {
                        "mode": mode,
                        "method": method,
                        "density_bin": level,
                        "shift_control_f1": 2 * shifted_tp / denominator if denominator else None,
                        **metrics(subset),
                    }
                )
            for condition in ("with_other", "without_other"):
                n = sum(r[condition + "_references"] for r in hh)
                tp = sum(r[condition + "_tp"] for r in hh)
                simultaneity.append(
                    {
                        "mode": mode,
                        "method": method,
                        "condition": condition,
                        "references": n,
                        "tp": tp,
                        "recall": tp / n if n else None,
                    }
                )
            missing = [r for r in hh if r["reference_count"] == 0]
            minutes = sum(r["duration_seconds"] for r in missing) / 60
            absent.append(
                {
                    "mode": mode,
                    "method": method,
                    "excerpts": len(missing),
                    "fp": sum(r["fp"] for r in missing),
                    "fp_per_minute": sum(r["fp"] for r in missing) / minutes if minutes else None,
                }
            )
    return {
        "cells": cells,
        "paired_sources": paired,
        "hh_density": density,
        "hh_simultaneity": simultaneity,
        "hh_absent_in_chart": absent,
        "temporal_control_method": "exploratory: mean of 31 circular shifts per excerpt, "
        "seeded by song/excerpt, shared offsets across methods/sources, no prediction retiming",
    }
