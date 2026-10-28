"""Chart-free candidates from three explicitly supplied, already aligned stems."""

from __future__ import annotations

import json

import inspect_audio as spectral
from component_audio import prepare_views
from reference_signal import BASELINE, features, peaks


def predict_components(args, shared):
    shared.interval(args.start, args.duration)
    profile_hash = shared.digest(args.profile)
    profile = shared.load_profile(args.profile, modes=("drums",))
    paths = {
        "KICK": args.kick,
        "SNARE_PROXY": args.snare,
        "YELLOW_CYMBAL_PROXY": args.high_percussion,
    }
    if len({p.resolve() for p in paths.values()}) != len(paths):
        raise ValueError("provide three distinct component paths")
    streams, sources, receipts = {}, {}, {}
    for group, path in paths.items():
        source_hash = shared.digest(path)
        signal, decoded = shared.exact_excerpt(path, args.ffmpeg_path, args.start, args.duration)
        if shared.digest(path) != source_hash:
            raise ValueError("component source changed during decoding")
        streams[group] = signal
        sources[group] = group
        receipts[group] = {
            "path": str(path.resolve()),
            "sha256": source_hash,
            "decoded_samples_before_crop": decoded,
        }
    _, views, audits, excluded, gain = prepare_views(streams, sources)
    rows = []
    for group, signal in views.get("components", {}).items():
        rule = (
            (BASELINE[group], 3, 0.02)
            if args.rules == "baseline"
            else tuple(profile["modes"]["drums"][group])
        )
        detected = shared.inside(
            peaks(features(spectral.spectrum(signal)), rule, args.start),
            args.start,
            args.start + args.duration,
        )
        rows.extend(
            {
                "time_seconds": t,
                "group": group,
                "status": "unverified_spectral_candidate",
                "source_group": group,
            }
            for t in detected
        )
    if shared.digest(args.profile) != profile_hash:
        raise ValueError("profile changed during prediction")
    args.out.mkdir(parents=True, exist_ok=False)
    shared.write_csv(
        args.out / "candidate-notes.csv",
        sorted(rows, key=lambda r: r["time_seconds"]),
        ["time_seconds", "group", "status", "source_group"],
    )
    report = {
        "schema_version": 1,
        "method": "chart_free_explicit_components",
        "rules": args.rules,
        "profile_sha256": profile_hash,
        "start_seconds": args.start,
        "duration_seconds": args.duration,
        "sources": receipts,
        "source_audio_audit": audits,
        "excluded_views": excluded,
        "common_gain": gain,
        "candidate_count": len(rows),
        "warning": "Inputs must already be aligned; no separator, classifier of openness, "
        "MIDI export or game acceptance is supplied by this command.",
    }
    (args.out / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"{len(rows)} candidatos por componentes em {args.out}; não é chart de jogo.")
