# /// script
# requires-python = ">=3.11,<3.13"
# dependencies = ["numpy==2.3.5", "matplotlib==3.10.8", "mido==1.3.3"]
# ///
"""Compare charts and waves, or propose spectral candidates using a saved profile."""

from __future__ import annotations

import argparse
import base64
import csv
import hashlib
import html
import json
import math
import sys
from dataclasses import asdict
from importlib.metadata import version
from pathlib import Path

import inspect_audio as spectral
import numpy as np
from reference_signal import (
    BANDS,
    BASELINE,
    GRID,
    calibrate,
    features,
    peaks,
    render_comparison,
    summarize,
)

# This is a project-local skill; core helpers remain independently testable.
sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "src"))
from drumforge.diagnostics.chart_reference import (  # noqa: E402
    TARGET_GROUPS,
    chart_asset,
    playback_assets,
    read_chart_reference,
)
from drumforge.diagnostics.matching import score_onsets, training_indices  # noqa: E402

EDGE = 0.05
MODES = ("mix", "drums")
WARNING = (
    "Referência fraca de chart, não anotação acústica: "
    "prato amarelo pode ser chimbal, ride ou crash; "
    "pad vermelho é apenas proxy de caixa. Charts podem omitir ou simplificar ataques. "
    "Perfis espectrais não são ADTOF nem confiança calibrada; não há validação no jogo."
)


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def write_csv(path, rows, fields):
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def interval(start, duration):
    if (
        not math.isfinite(start)
        or start < 0
        or not math.isfinite(duration)
        or not 1 <= duration <= 60
    ):
        raise ValueError("excerpt requires finite start >= 0 and duration between 1 and 60 s")


def inside(times, start, end):
    return [float(t) for t in times if start + EDGE <= t < end - EDGE]


def exact_excerpt(path, ffmpeg, start, duration):
    # Vorbis/FFmpeg can flush a partial frame beyond -t. Decode a bounded 100 ms
    # tail guard, then crop by sample count, without shifting/normalizing any stem.
    audio = spectral.decode(path, ffmpeg, start, duration + 0.1)
    required = int(round(duration * spectral.RATE))
    if len(audio) < required:
        raise ValueError(f"audio does not cover the requested excerpt: {path.name}")
    return audio[:required], len(audio)


def study(args):
    recipe = json.loads(args.recipe.read_text(encoding="utf-8"))
    songs = recipe["songs"]
    if not 2 <= len(songs) <= 8 or len({s["id"] for s in songs}) != len(songs):
        raise ValueError("study requires 2..8 unique song ids")
    root = args.library_root.resolve()
    # Validate every asset before creating output, decoding or using chart labels.
    validated = []
    for song in songs:
        folder = (root / song["folder"]).resolve()
        if not folder.is_relative_to(root):
            raise ValueError("song folder escapes library root")
        assets = playback_assets(folder)
        names = {p.name for p in assets} | {"song.ini", chart_asset(folder).name}
        if names != set(song["assets_sha256"]):
            raise ValueError(f"unexpected asset selection: {song['id']}")
        for name, expected in song["assets_sha256"].items():
            if digest(folder / name) != expected:
                raise ValueError(f"source identity changed: {song['id']} / {name}")
        events, meta = read_chart_reference(folder)
        for excerpt in song["excerpts"]:
            interval(excerpt["start"], excerpt["duration"])
        if not 1 <= len(song["excerpts"]) <= 4:
            raise ValueError("use one to four bounded excerpts per song")
        spans = sorted((e["start"], e["start"] + e["duration"]) for e in song["excerpts"])
        if any(a[1] > b[0] for a, b in zip(spans, spans[1:], strict=False)):
            raise ValueError("overlapping excerpts would double-count test events")
        validated.append((song, folder, assets, events, meta))
    args.out.mkdir(parents=True, exist_ok=False)
    datasets = []
    event_rows = []
    sources = []
    for song, _folder, assets, events, meta in validated:
        print(f"Analisando {meta['artist']} — {meta['title']}", flush=True)
        sources.append({**song, **meta})
        for number, excerpt in enumerate(song["excerpts"]):
            start, duration = excerpt["start"], excerpt["duration"]
            decoded_pairs = [exact_excerpt(p, args.ffmpeg_path, start, duration) for p in assets]
            decoded = [pair[0] for pair in decoded_pairs]
            lengths = [pair[1] for pair in decoded_pairs]
            mix = np.sum(decoded, axis=0)
            drums = np.sum(
                [
                    a
                    for p, a in zip(assets, decoded, strict=True)
                    if p.stem.casefold().startswith("drums")
                ],
                axis=0,
            )
            gain = 1 / max(1, float(np.abs(mix).max()), float(np.abs(drums).max()))
            audios = {"mix": mix * gain, "drums": drums * gain}
            end = start + duration
            refs = {
                group: inside([e.time_seconds for e in events if e.group == group], start, end)
                for group in TARGET_GROUPS
            }
            event_rows.extend(
                {"song_id": song["id"], "excerpt": number, **asdict(e)}
                for e in events
                if start + EDGE <= e.time_seconds < end - EDGE
            )
            entry = {
                "song_id": song["id"],
                "excerpt": number,
                "start": start,
                "end": end,
                "gain_shared_between_mix_and_drums": gain,
                "decoded_samples": lengths,
                "retained_samples_per_stem": len(decoded[0]),
                "decode_tail_guard_seconds": 0.1,
                "truth": refs,
                "context_reference": {
                    "TOMS": inside(
                        [e.time_seconds for e in events if e.group.endswith("_TOM")], start, end
                    ),
                    "OTHER_CYMBALS": inside(
                        [
                            e.time_seconds
                            for e in events
                            if e.group in {"BLUE_CYMBAL_PROXY", "GREEN_CYMBAL_PROXY"}
                        ],
                        start,
                        end,
                    ),
                },
                "audios": audios,
                "modes": {},
            }
            for mode, audio in audios.items():
                power = spectral.spectrum(audio)
                curves = features(power)
                predictions = {
                    rule: inside(peaks(curves, rule, start), start, end) for rule in GRID
                }
                entry["modes"][mode] = {"power": power, "truth": refs, "predictions": predictions}
            datasets.append(entry)
    folds = []
    candidate_rows = []
    for held_out in [s["id"] for s in songs]:
        train = training_indices([c["song_id"] for c in datasets], held_out)
        fold = {
            "held_out_song": held_out,
            "training_songs": [s["id"] for s in songs if s["id"] != held_out],
            "modes": {},
        }
        for mode in MODES:
            groups = {}
            for group in TARGET_GROUPS:
                rule = calibrate([datasets[i]["modes"][mode] for i in train], group, score_onsets)
                baseline, calibrated = [], []
                for clip in [c for c in datasets if c["song_id"] == held_out]:
                    data = clip["modes"][mode]
                    predictions = data["predictions"][rule]
                    baseline.append(
                        score_onsets(
                            clip["truth"][group], data["predictions"][(BASELINE[group], 3, 0.02)]
                        )
                    )
                    calibrated.append(score_onsets(clip["truth"][group], predictions))
                    candidate_rows.extend(
                        {
                            "song_id": held_out,
                            "excerpt": clip["excerpt"],
                            "mode": mode,
                            "group": group,
                            "time_seconds": t,
                        }
                        for t in predictions
                    )
                groups[group] = {
                    "rule": rule,
                    "baseline": summarize(baseline),
                    "calibrated": summarize(calibrated),
                    "excerpt_metrics": calibrated,
                }
            fold["modes"][mode] = groups
        folds.append(fold)
    profile = {
        "schema_version": 1,
        "kind": "experimental_spectral_peak_rules",
        "automatic_use_recommended": False,
        "source_recipe_sha256": digest(args.recipe),
        "reference_kind": WARNING,
        "bands_hz": BANDS,
        "source_songs": [s["id"] for s in songs],
        "fft_size": spectral.N_FFT,
        "hop_samples": spectral.HOP,
        "sample_rate_hz": spectral.RATE,
        "evaluation": (
            "leave-one-song-out; final profile fitted on all sources is not independently tested"
        ),
        "modes": {
            mode: {
                group: calibrate([c["modes"][mode] for c in datasets], group, score_onsets)
                for group in TARGET_GROUPS
            }
            for mode in MODES
        },
    }
    aggregate = {
        mode: {
            group: {
                method: summarize([f["modes"][mode][group][method] for f in folds])
                for method in ("baseline", "calibrated")
            }
            for group in TARGET_GROUPS
        }
        for mode in MODES
    }
    report = {
        "schema_version": 1,
        "warning": WARNING,
        "sources": sources,
        "recipe_sha256": digest(args.recipe),
        "versions": {n: version(n) for n in ("numpy", "matplotlib", "mido")},
        "tolerance_seconds": 0.03,
        "evaluation_edge_exclusion_seconds": EDGE,
        "mix_policy": (
            "sum listed playback stems equally; exclude preview/crowd; "
            "one common anti-clip gain; not a commercial master"
        ),
        "alignment_policy": "tempo map plus song.ini delay; no offset fitted from held-out chart",
        "independent_acoustic_labels": False,
        "adtof_comparison_performed": False,
        "folds": folds,
        "aggregate": aggregate,
        "excerpts": [
            {k: v for k, v in c.items() if k not in {"audios", "modes"}} for c in datasets
        ],
    }
    (args.out / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    (args.out / "spectral-profile.json").write_text(
        json.dumps(profile, indent=2) + "\n", encoding="utf-8"
    )
    write_csv(
        args.out / "chart-events.csv",
        event_rows,
        ["song_id", "excerpt", "time_seconds", "tick", "midi_note", "group", "velocity"],
    )
    write_csv(
        args.out / "held-out-candidates.csv",
        candidate_rows,
        ["song_id", "excerpt", "mode", "group", "time_seconds"],
    )
    images = []
    for index, clip in enumerate(datasets):
        fold = next(f for f in folds if f["held_out_song"] == clip["song_id"])
        predicted = {
            g: clip["modes"]["mix"]["predictions"][tuple(fold["modes"]["mix"][g]["rule"])]
            for g in TARGET_GROUPS
        }
        path = args.out / f"{index + 1:02d}-comparison.png"
        render_comparison(
            path,
            f"{clip['song_id']} / {clip['start']} s",
            clip["start"],
            clip["audios"],
            {m: clip["modes"][m]["power"] for m in MODES},
            {**clip["truth"], **clip["context_reference"]},
            predicted,
        )
        images.append(path)
    rows = "".join(
        f"<tr><td>{m}</td><td>{g}</td><td>{v['baseline']['f1']:.3f}</td><td>{v['calibrated']['f1']:.3f}</td></tr>"
        for m, groups in aggregate.items()
        for g, v in groups.items()
    )
    pictures = "".join(
        '<img style="width:100%" src="data:image/png;base64,'
        + base64.b64encode(p.read_bytes()).decode()
        + '">'
        for p in images
    )
    page = (
        "<!doctype html><meta charset='utf-8'><title>Charts e ondas</title>"
        "<style>body{max-width:1200px;margin:32px auto;font:16px system-ui;padding:16px}"
        "td,th{padding:10px;border:1px solid #ccc}table{border-collapse:collapse}</style>"
        "<h1>Charts e ondas</h1><p>" + html.escape(WARNING) + "</p>"
        f"<p>{len(songs)} músicas e {len(datasets)} trechos. "
        "Teste: deixar uma música inteira fora da calibração. "
        "F1 mede coincidência com o chart a ±30 ms, "
        "não acurácia acústica ou melhora sobre ADTOF.</p>"
        "<table><tr><th>Áudio</th><th>Classe proxy</th><th>F1 regra original</th>"
        "<th>F1 regra calibrada</th></tr>"
        + rows
        + "</table><p>Mix = soma técnica dos stems, com ganho comum. Report.json contém hashes, "
        "offsets, TP/FP/FN e regras de cada fold. "
        "spectral-profile.json foi calibrado em todas as músicas.</p>" + pictures
    )
    (args.out / "report.html").write_text(page, encoding="utf-8")
    print(json.dumps({"output": str(args.out), "aggregate": aggregate}, indent=2))


def load_profile(path, modes=MODES):
    profile = json.loads(path.read_text(encoding="utf-8"))
    if (
        profile.get("kind") != "experimental_spectral_peak_rules"
        or profile.get("schema_version") != 1
    ):
        raise ValueError("unsupported spectral profile")
    expected = {
        "fft_size": spectral.N_FFT,
        "hop_samples": spectral.HOP,
        "sample_rate_hz": spectral.RATE,
    }
    if any(profile.get(k) != v for k, v in expected.items()) or profile.get("bands_hz") != {
        k: list(v) for k, v in BANDS.items()
    }:
        raise ValueError("profile spectral configuration differs from this script")
    for mode in modes:
        rules = profile["modes"][mode]
        if set(rules) != set(TARGET_GROUPS) or any(
            tuple(rule) not in GRID for rule in rules.values()
        ):
            raise ValueError("profile rule is outside the fixed calibration grid")
    return profile


def predict(args):
    interval(args.start, args.duration)
    profile = load_profile(args.profile, (args.mode,))
    rules = profile["modes"][args.mode]
    audio, decoded_samples = exact_excerpt(args.audio, args.ffmpeg_path, args.start, args.duration)
    curves = features(spectral.spectrum(audio))
    rows = [
        {"time_seconds": t, "group": g, "status": "unverified_spectral_candidate"}
        for g, rule in rules.items()
        for t in inside(
            peaks(curves, tuple(rule), args.start),
            args.start,
            args.start + len(audio) / spectral.RATE,
        )
    ]
    args.out.mkdir(parents=True, exist_ok=False)
    write_csv(
        args.out / "candidate-notes.csv",
        sorted(rows, key=lambda r: (r["time_seconds"], r["group"])),
        ["time_seconds", "group", "status"],
    )
    (args.out / "provenance.json").write_text(
        json.dumps(
            {
                "warning": WARNING,
                "audio_sha256": digest(args.audio),
                "profile_sha256": digest(args.profile),
                "start_seconds": args.start,
                "requested_duration_seconds": args.duration,
                "mode": args.mode,
                "decoded_samples_before_tail_crop": decoded_samples,
                "retained_samples": len(audio),
                "candidate_count": len(rows),
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"{len(rows)} candidatos experimentais em {args.out}; não é um chart validado.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    research = commands.add_parser(
        "study", help="Compare existing Pro Drums charts with aligned audio"
    )
    research.add_argument("--recipe", type=Path, required=True)
    research.add_argument("--library-root", type=Path, required=True)
    forward = commands.add_parser("predict", help="Propose candidates without reading a chart")
    forward.add_argument("audio", type=Path)
    forward.add_argument("--profile", type=Path, required=True)
    forward.add_argument("--mode", choices=MODES, default="mix")
    forward.add_argument("--start", type=float, default=0)
    forward.add_argument("--duration", type=float, default=20)
    evaluation = commands.add_parser(
        "evaluate", help="Test a frozen profile on other chart/audio pairs"
    )
    evaluation.add_argument("--recipe", type=Path, required=True)
    evaluation.add_argument("--profile", type=Path, required=True)
    evaluation.add_argument("--training-recipe", type=Path, required=True)
    evaluation.add_argument("--library-root", type=Path, required=True)
    evaluation.add_argument(
        "--no-plots", action="store_true", help="Skip waveform figures in batch studies"
    )
    components = commands.add_parser(
        "predict-components", help="Use existing aligned stems without a chart"
    )
    components.add_argument("--kick", type=Path, required=True)
    components.add_argument("--snare", type=Path, required=True)
    components.add_argument("--high-percussion", type=Path, required=True)
    components.add_argument("--profile", type=Path, required=True)
    components.add_argument("--rules", choices=("baseline", "frozen"), default="baseline")
    components.add_argument("--start", type=float, default=0)
    components.add_argument("--duration", type=float, default=20)
    planning = commands.add_parser("survey-plan", help="Select diverse new songs before scoring")
    planning.add_argument("--library-root", type=Path, required=True)
    planning.add_argument("--profile", type=Path, required=True)
    planning.add_argument("--exclude-recipe", type=Path, nargs="+", required=True)
    planning.add_argument("--count", type=int, default=64)
    planning.add_argument("--per-artist", type=int, default=5)
    planning.add_argument("--seed", default="drumforge-survey-20261027-v1")
    survey = commands.add_parser("survey", help="Run bounded frozen comparisons on up to 80 songs")
    survey.add_argument("--recipe", type=Path, required=True)
    survey.add_argument("--profile", type=Path, required=True)
    survey.add_argument("--training-recipe", type=Path, required=True)
    survey.add_argument("--library-root", type=Path, required=True)
    survey.add_argument("--jobs", type=int, default=2)
    survey.add_argument("--resume", action="store_true")
    for command in (research, forward, evaluation, components, planning, survey):
        command.add_argument("--out", type=Path, required=True)
        command.add_argument("--ffmpeg-path", default="ffmpeg")
    args = parser.parse_args()
    if (args.out.exists() or args.out.is_symlink()) and not (
        args.command == "survey" and args.resume and not args.out.is_symlink()
    ):
        parser.error("output directory exists; choose a new directory")
    try:
        if args.command == "evaluate":
            from reference_holdout import evaluate

            evaluate(args, sys.modules[__name__])
        elif args.command == "predict-components":
            from component_predict import predict_components

            predict_components(args, sys.modules[__name__])
        elif args.command in {"survey-plan", "survey"}:
            from survey_plan import plan
            from survey_runner import run

            (plan if args.command == "survey-plan" else run)(args, sys.modules[__name__])
        else:
            (study if args.command == "study" else predict)(args)
    except (OSError, ValueError, KeyError, RuntimeError) as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
