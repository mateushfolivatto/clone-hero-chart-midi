"""Evaluate fixed spectral rules on new songs. This module never calibrates rules."""

from __future__ import annotations

import base64
import html
import json
from dataclasses import asdict
from importlib.metadata import version

import inspect_audio as spectral
from component_audio import prepare_views, validate_sources
from reference_signal import BASELINE, features, peaks, render_comparison, summarize

from drumforge.diagnostics.chart_reference import (
    TARGET_GROUPS,
    chart_asset,
    playback_assets,
    read_chart_reference,
)
from drumforge.diagnostics.holdout import validate_holdout
from drumforge.diagnostics.matching import score_onsets


def _number(value):
    return "—" if value is None else f"{value:.3f}"


def evaluate(args, shared):
    profile_hash = shared.digest(args.profile)
    profile = shared.load_profile(args.profile)
    recipe = json.loads(args.recipe.read_text(encoding="utf-8"))
    report_title = str(recipe.get("title", "Teste externo do perfil congelado"))
    if recipe.get("frozen_profile_sha256") != profile_hash:
        raise ValueError("frozen profile identity differs from the evaluation recipe")
    songs = recipe["songs"]
    if not 1 <= len(songs) <= 8:
        raise ValueError("evaluate one to eight songs")
    validate_holdout(profile, args.training_recipe, songs)
    root = args.library_root.resolve()
    inputs = []
    for song in songs:
        folder = (root / song["folder"]).resolve()
        if not folder.is_relative_to(root):
            raise ValueError("evaluation song folder escapes library root")
        assets = playback_assets(folder, require_drums=False)
        chart = chart_asset(folder)
        if set(song["assets_sha256"]) != {p.name for p in assets} | {"song.ini", chart.name}:
            raise ValueError("evaluation recipe audio/chart selection differs from the folder")
        for name, expected in song["assets_sha256"].items():
            if shared.digest(folder / name) != expected:
                raise ValueError(f"evaluation asset changed: {song['id']} / {name}")
        events, metadata = read_chart_reference(folder)
        validate_sources(song.get("component_sources", {}), {p.name for p in assets})
        if not 1 <= len(song["excerpts"]) <= 4:
            raise ValueError("use one to four bounded excerpts per song")
        spans = []
        for excerpt in song["excerpts"]:
            shared.interval(excerpt["start"], excerpt["duration"])
            spans.append((excerpt["start"], excerpt["start"] + excerpt["duration"]))
        spans.sort()
        if any(a[1] > b[0] for a, b in zip(spans, spans[1:], strict=False)):
            raise ValueError("evaluation excerpts overlap")
        inputs.append((song, assets, events, metadata))
    args.out.mkdir(parents=True, exist_ok=False)
    song_results, excerpt_results, event_rows, candidate_rows, pictures = [], [], [], [], []
    for song, assets, events, metadata in inputs:
        print(f"Perfil congelado: {metadata['artist']} — {metadata['title']}", flush=True)
        scores = {}
        for index, excerpt in enumerate(song["excerpts"]):
            start, duration = excerpt["start"], excerpt["duration"]
            end = start + duration
            pairs = [shared.exact_excerpt(p, args.ffmpeg_path, start, duration) for p in assets]
            streams = {p.name: pair[0] for p, pair in zip(assets, pairs, strict=True)}
            audio, views, audits, excluded, gain = prepare_views(
                streams, song.get("component_sources", {})
            )
            powers, candidates = {}, {}
            # Inference sees only audio and frozen rules; chart labels enter scoring below.
            for mode, groups in views.items():
                candidates[mode] = {}
                shared_curves = None
                if mode != "components":
                    powers[mode] = spectral.spectrum(next(iter(groups.values())))
                    shared_curves = features(powers[mode])
                for group, signal in groups.items():
                    curves = (
                        shared_curves
                        if shared_curves is not None
                        else features(spectral.spectrum(signal))
                    )
                    profile_mode = "drums" if mode == "components" else mode
                    candidates[mode][group] = {
                        "baseline": shared.inside(
                            peaks(curves, (BASELINE[group], 3, 0.02), start), start, end
                        ),
                        "frozen": shared.inside(
                            peaks(curves, tuple(profile["modes"][profile_mode][group]), start),
                            start,
                            end,
                        ),
                    }
            reference = {
                group: shared.inside(
                    [e.time_seconds for e in events if e.group == group], start, end
                )
                for group in TARGET_GROUPS
            }
            context = {
                "TOMS": shared.inside(
                    [e.time_seconds for e in events if e.group.endswith("_TOM")], start, end
                ),
                "OTHER_CYMBALS": shared.inside(
                    [
                        e.time_seconds
                        for e in events
                        if e.group in {"BLUE_CYMBAL_PROXY", "GREEN_CYMBAL_PROXY"}
                    ],
                    start,
                    end,
                ),
            }
            for mode, groups in candidates.items():
                scores.setdefault(mode, {})
                for group, methods in groups.items():
                    scores[mode].setdefault(group, {"baseline": [], "frozen": []})
                    for method, predicted in methods.items():
                        scores[mode][group][method].append(
                            score_onsets(reference[group], predicted)
                        )
                        candidate_rows.extend(
                            {
                                "song_id": song["id"],
                                "excerpt": index,
                                "mode": mode,
                                "method": method,
                                "group": group,
                                "time_seconds": t,
                            }
                            for t in predicted
                        )
            event_rows.extend(
                {"song_id": song["id"], "excerpt": index, **asdict(e)}
                for e in events
                if start + shared.EDGE <= e.time_seconds < end - shared.EDGE
            )
            excerpt_results.append(
                {
                    "song_id": song["id"],
                    "excerpt": index,
                    "start_seconds": start,
                    "duration_seconds": duration,
                    "decoded_samples_before_crop": [pair[1] for pair in pairs],
                    "retained_samples_per_stem": len(next(iter(streams.values()))),
                    "common_gain": gain,
                    "available_modes": list(views),
                    "available_groups": {m: list(g) for m, g in views.items()},
                    "source_audio_audit": audits,
                    "excluded_views": excluded,
                    "reference_counts": {g: len(t) for g, t in reference.items()},
                    "context_counts": {g: len(t) for g, t in context.items()},
                }
            )
            if getattr(args, "no_plots", False):
                continue
            path = args.out / f"{len(pictures) + 1:02d}-{song['id']}.png"
            plotted_mode, plotted_rule = "mix", "frozen"
            if "YELLOW_CYMBAL_PROXY" in views.get("components", {}):
                kit = views["components"]["YELLOW_CYMBAL_PROXY"]
                audio["kit sem bumbo/caixa"] = kit
                powers["kit sem bumbo/caixa"] = spectral.spectrum(kit)
                plotted_mode, plotted_rule = "components", "baseline"
            render_comparison(
                path,
                f"{metadata['title']} / {start} s — perfil congelado",
                start,
                audio,
                powers,
                {**reference, **context},
                {g: values[plotted_rule] for g, values in candidates[plotted_mode].items()},
                prediction_label=f"{plotted_rule} / {plotted_mode}; regras sem recalibração",
            )
            pictures.append(path)
        song_results.append(
            {
                "song_id": song["id"],
                **metadata,
                "audio_files": [p.name for p in assets],
                "component_sources": song.get("component_sources", {}),
                "audio_policy": "technical equal-gain stem sum"
                if len(assets) > 1
                else "single stream as delivered, used as mix",
                "modes": {
                    mode: {
                        g: {method: summarize(values) for method, values in methods.items()}
                        for g, methods in groups.items()
                    }
                    for mode, groups in scores.items()
                },
                "excerpt_metrics": scores,
            }
        )
    modes = [*shared.MODES]
    if any(s.get("component_sources") for s in songs):
        modes.append("components")
    coverage = {mode: [s["song_id"] for s in song_results if mode in s["modes"]] for mode in modes}
    class_coverage = {
        mode: {
            group: {
                "songs": sorted(
                    {
                        e["song_id"]
                        for e in excerpt_results
                        if group in e["available_groups"].get(mode, [])
                    }
                ),
                "excerpts": sum(
                    group in e["available_groups"].get(mode, []) for e in excerpt_results
                ),
                "duration_seconds": sum(
                    e["duration_seconds"]
                    for e in excerpt_results
                    if group in e["available_groups"].get(mode, [])
                ),
                "reference_count": sum(
                    e["reference_counts"][group]
                    for e in excerpt_results
                    if group in e["available_groups"].get(mode, [])
                ),
            }
            for group in TARGET_GROUPS
        }
        for mode in modes
    }
    aggregate = {
        mode: {
            g: {
                method: summarize(
                    [
                        s["modes"][mode][g][method]
                        for s in song_results
                        if g in s["modes"].get(mode, {})
                    ]
                )
                for method in ("baseline", "frozen")
            }
            for g in TARGET_GROUPS
            if class_coverage[mode][g]["excerpts"]
        }
        for mode, ids in coverage.items()
        if ids
    }
    if shared.digest(args.profile) != profile_hash:
        raise ValueError("profile changed during evaluation")
    report = {
        "schema_version": 2,
        "method": "frozen_profile_external_song_evaluation",
        "warning": shared.WARNING,
        "profile_sha256": profile_hash,
        "training_recipe_sha256": shared.digest(args.training_recipe),
        "evaluation_recipe_sha256": shared.digest(args.recipe),
        "calibration_performed": False,
        "offset_optimization_performed": False,
        "tolerance_seconds": 0.03,
        "edge_exclusion_seconds": shared.EDGE,
        "adtof_comparison_performed": False,
        "versions": {n: version(n) for n in ("numpy", "matplotlib", "mido")},
        "sources": songs,
        "training_song_ids": profile["source_songs"],
        "mode_coverage": coverage,
        "class_coverage": class_coverage,
        "component_policy": "explicit existing source per class; drums-profile rules unchanged",
        "silence_policy": "omit exactly-zero drum/component excerpts; never gate quiet audio",
        "aggregate": aggregate,
        "songs": song_results,
        "excerpts": excerpt_results,
    }
    (args.out / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    (args.out / "frozen-profile.json").write_bytes(args.profile.read_bytes())
    shared.write_csv(
        args.out / "chart-events.csv",
        event_rows,
        ["song_id", "excerpt", "time_seconds", "tick", "midi_note", "group", "velocity"],
    )
    shared.write_csv(
        args.out / "candidates.csv",
        candidate_rows,
        ["song_id", "excerpt", "mode", "method", "group", "time_seconds"],
    )
    rows = "".join(
        f"<tr><td>{mode} ({len(coverage[mode])} músicas)</td><td>{g}</td>"
        f"<td>{_number(v['baseline']['f1'])}</td><td>{_number(v['frozen']['f1'])}</td></tr>"
        for mode, groups in aggregate.items()
        for g, v in groups.items()
    )
    by_song = "".join(
        f"<tr><td>{html.escape(s['title'])}</td><td>{mode}</td><td>{g}</td>"
        f"<td>{v['baseline']['tp'] + v['baseline']['fn']}</td>"
        f"<td>{_number(v['baseline']['f1'])}</td><td>{_number(v['frozen']['f1'])}</td></tr>"
        for s in song_results
        for mode, groups in s["modes"].items()
        for g, v in groups.items()
    )
    images = "".join(
        '<img style="width:100%" src="data:image/png;base64,'
        + base64.b64encode(p.read_bytes()).decode()
        + '">'
        for p in pictures
    )
    page = (
        "<!doctype html><meta charset='utf-8'><title>" + html.escape(report_title) + "</title>"
        "<style>body{font:16px system-ui;max-width:1200px;margin:32px auto;padding:16px}"
        "td,th{padding:8px;border:1px solid #bbb}table{border-collapse:collapse}</style>"
        "<h1>"
        + html.escape(report_title)
        + "</h1><p>"
        + html.escape(shared.WARNING)
        + "</p><p>Sem recalibrar ou ajustar offsets nas novas músicas. "
        "F1 contra os charts a ±30 ms. Stems ausentes não são inventados. "
        "Silêncio digital é excluído de bateria/componentes; áudio fraco é preservado. "
        "class_coverage informa músicas, recortes e segundos por classe. "
        "O restante do kit ainda mistura chimbal, tons e outros pratos.</p>"
        "<table><tr><th>Áudio</th><th>Referência</th><th>F1 original</th>"
        "<th>F1 perfil congelado</th></tr>"
        + rows
        + "</table><h2>Por música e fonte</h2><table><tr><th>Música</th><th>Fonte</th>"
        "<th>Referência</th>"
        "<th>Notas do chart</th><th>F1 original</th><th>F1 perfil congelado</th></tr>"
        + by_song
        + "</table>"
        + images
    )
    (args.out / "report.html").write_text(page, encoding="utf-8")
    print(
        json.dumps(
            {"output": str(args.out), "mode_coverage": coverage, "aggregate": aggregate}, indent=2
        )
    )
