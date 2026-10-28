"""Plan an artist-balanced frozen survey before looking at detection scores."""

from __future__ import annotations

import json
import re

from drumforge.diagnostics.survey import balanced_selection, identity
from drumforge.library.inspect_song import read_config, read_drum_midi


def plan(args, shared):
    root = args.library_root.resolve()
    excluded_hashes, excluded_titles = set(), set()
    for path in args.exclude_recipe:
        for song in json.loads(path.read_text(encoding="utf-8"))["songs"]:
            excluded_hashes.update(
                v for k, v in song["assets_sha256"].items() if k in {"notes.mid", "notes.chart"}
            )
            cfg = read_config(root / song["folder"] / "song.ini")
            excluded_titles.add((identity(cfg.get("artist", "")), identity(cfg.get("name", ""))))
    candidates, excluded, seen = [], [], set()
    for ini in sorted(root.rglob("song.ini")):
        folder = ini.parent
        relative = folder.relative_to(root)
        if "Songs" not in relative.parts:
            continue
        try:
            cfg = read_config(ini)
            chart = shared.chart_asset(folder)
            chart_hash = shared.digest(chart)
            title_key = (identity(cfg.get("artist", "")), identity(cfg.get("name", "")))
            if chart_hash in excluded_hashes or title_key in excluded_titles:
                reason = "previously_examined_song"
            elif chart_hash in seen:
                reason = "duplicate_chart"
            else:
                reason = None
            seen.add(chart_hash)
            if reason:
                excluded.append({"folder": str(relative), "reason": reason})
                continue
            events, metadata = shared.read_chart_reference(folder)
            if max(e.time_seconds for e in events) < 140.05:
                excluded.append({"folder": str(relative), "reason": "short_for_fixed_windows"})
                continue
            assets = shared.playback_assets(folder, require_drums=False)
            names = {p.name for p in assets}
            mixes = []
            if chart.suffix == ".mid":
                midi = read_drum_midi(chart.read_bytes())
                track = next(t for t in midi.tracks if t.name == "PART DRUMS")
                mixes = [
                    m.text
                    for m in track
                    if m.type == "text" and re.match(r"\[?mix[ _]+3[ _]+drums", m.text)
                ]
            layouts = [
                re.fullmatch(r"\[?mix[ _]+3[ _]+drums([123])(?:d|dnoflip|easy|easynokick)?\]?", m)
                for m in mixes
            ]
            components = {}
            if (
                mixes
                and all(layouts)
                and len({m[1] for m in layouts}) == 1
                and {n for n in names if n.startswith("drums")}
                == {"drums_1.ogg", "drums_2.ogg", "drums_3.ogg"}
            ):
                components = dict(
                    zip(
                        shared.TARGET_GROUPS,
                        ["drums_1.ogg", "drums_2.ogg", "drums_3.ogg"],
                        strict=True,
                    )
                )
            candidates.append(
                {
                    "artist": metadata["artist"],
                    "title": metadata["title"],
                    "genre": cfg.get("genre", "unknown"),
                    "folder": str(relative),
                    "chart_sha256": chart_hash,
                    "format": metadata["chart_format"],
                    "assets": sorted(names),
                    "has_drum_files": any(n.startswith("drums") for n in names),
                    "expert_mixes": sorted(set(mixes)),
                    "component_sources": components,
                    "disco_starts": metadata["expert_disco_flip_starts"],
                }
            )
        except (ValueError, OSError, StopIteration, KeyError) as exc:
            excluded.append(
                {"folder": str(relative), "reason": type(exc).__name__ + ": " + str(exc)}
            )
    selected = balanced_selection(
        candidates, count=args.count, per_artist=args.per_artist, seed=args.seed
    )
    songs = []
    for song in selected:
        folder = root / song["folder"]
        paths = [
            folder / "song.ini",
            shared.chart_asset(folder),
            *shared.playback_assets(folder, require_drums=False),
        ]
        songs.append(
            {
                "id": "survey-" + song["chart_sha256"][:16],
                "artist": song["artist"],
                "title": song["title"],
                "genre": song["genre"],
                "folder": song["folder"],
                "component_sources": song["component_sources"],
                "component_basis": song["expert_mixes"],
                "assets_sha256": {p.name: shared.digest(p) for p in paths},
                "excerpts": [{"start": 60, "duration": 20}, {"start": 120, "duration": 20}],
            }
        )
    recipe = {
        "schema_version": 1,
        "title": f"{args.count} músicas novas — regras congeladas",
        "purpose": "Broad frozen survey; no recalibration or test-label offset fitting",
        "frozen_profile_sha256": shared.digest(args.profile),
        "songs": songs,
    }
    selection = {
        "seed": args.seed,
        "count": args.count,
        "artist_cap": args.per_artist,
        "policy": (
            "round robin normalized artists; prioritize declared components, "
            "then drum filenames, then seeded hash; no scores used"
        ),
        "excluded_recipes": {str(p): shared.digest(p) for p in args.exclude_recipe},
        "eligible_count": len(candidates),
        "eligible_drum_filenames": sum(s["has_drum_files"] for s in candidates),
        "eligible": candidates,
        "excluded": excluded,
        "selected": [s["id"] for s in songs],
    }
    args.out.mkdir(parents=True, exist_ok=False)
    for name, data in [("recipe.json", recipe), ("selection.json", selection)]:
        (args.out / name).write_text(
            json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
    print(f"{len(songs)} músicas selecionadas de {len(candidates)} elegíveis; {args.out}")
