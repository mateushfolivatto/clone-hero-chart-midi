"""Run bounded one-song evaluations with two CPU workers and pinned resume state."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from importlib.metadata import version
from pathlib import Path

from drumforge.diagnostics.holdout import validate_holdout


def run(args, shared):
    recipe_bytes = args.recipe.read_bytes()
    recipe = json.loads(recipe_bytes)
    songs = recipe["songs"]
    if not 1 <= len(songs) <= 80 or not 1 <= args.jobs <= 2:
        raise ValueError("survey requires 1..80 songs and 1..2 CPU workers")
    profile = shared.load_profile(args.profile)
    if shared.digest(args.profile) != recipe["frozen_profile_sha256"]:
        raise ValueError("survey profile identity differs")
    validate_holdout(profile, args.training_recipe, songs)
    scripts = Path(__file__).parent
    source_paths = [
        scripts / name
        for name in [
            "chart_reference.py",
            "reference_holdout.py",
            "component_audio.py",
            "reference_signal.py",
            "inspect_audio.py",
            "survey_runner.py",
        ]
    ]
    source_paths.extend((scripts.parents[3] / "src/drumforge/diagnostics").glob("*.py"))
    source_paths.append(scripts.parents[3] / "src/drumforge/library/inspect_song.py")
    state = {
        "recipe_sha256": hashlib.sha256(recipe_bytes).hexdigest(),
        "profile_sha256": shared.digest(args.profile),
        "training_recipe_sha256": shared.digest(args.training_recipe),
        "source_sha256": {
            str(p.relative_to(scripts.parents[3])): shared.digest(p) for p in source_paths
        },
        "python": sys.version.split()[0],
        "versions": {name: version(name) for name in ("numpy", "matplotlib", "mido")},
        "ffmpeg": subprocess.check_output([args.ffmpeg_path, "-version"], text=True).splitlines()[
            0
        ],
    }
    if args.out.exists():
        if not args.resume or json.loads((args.out / "state.json").read_text()) != state:
            raise ValueError("resume requires identical recipe, profile, source and runtime")
    else:
        args.out.mkdir(parents=True)
        (args.out / "state.json").write_text(json.dumps(state, indent=2) + "\n")
    for song in songs:
        folder = (args.library_root / song["folder"]).resolve()
        if not folder.is_relative_to(args.library_root.resolve()):
            raise ValueError("survey path escapes root")
        for name, digest in song["assets_sha256"].items():
            if shared.digest(folder / name) != digest:
                raise ValueError(f"survey source changed: {song['id']} / {name}")

    def worker(song):
        ident = song["id"]
        destination = args.out / ident
        subrecipe = args.out / (ident + ".recipe.json")
        data = {
            "schema_version": 1,
            "title": song.get("title", ident),
            "frozen_profile_sha256": state["profile_sha256"],
            "songs": [song],
        }
        subrecipe.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        report = destination / "report.json"
        if report.exists():
            previous = json.loads(report.read_text())
            if previous["evaluation_recipe_sha256"] != shared.digest(subrecipe):
                raise ValueError("cached report differs from its recipe")
            receipt = json.loads((destination / "done.json").read_text())
            if any(shared.digest(destination / name) != value for name, value in receipt.items()):
                raise ValueError("cached report/CSV changed after completion")
            return {"song_id": ident, "status": "reused"}
        if destination.exists():
            return {
                "song_id": ident,
                "status": "failed",
                "reason": "incomplete output; inspect before retry",
            }
        command = [
            sys.executable,
            str(scripts / "chart_reference.py"),
            "evaluate",
            "--recipe",
            str(subrecipe),
            "--profile",
            str(args.profile),
            "--training-recipe",
            str(args.training_recipe),
            "--library-root",
            str(args.library_root),
            "--out",
            str(destination),
            "--ffmpeg-path",
            args.ffmpeg_path,
            "--no-plots",
        ]
        completed = subprocess.run(command, capture_output=True, text=True, timeout=180)
        (args.out / (ident + ".log")).write_text(
            completed.stdout + completed.stderr, encoding="utf-8"
        )
        if completed.returncode:
            return {"song_id": ident, "status": "failed", "reason": completed.stderr[-2000:]}
        # A complete report, not the directory alone, is the completion receipt.
        json.loads(report.read_text())
        receipt = {
            name: shared.digest(destination / name)
            for name in ("report.json", "chart-events.csv", "candidates.csv")
        }
        (destination / "done.json").write_text(json.dumps(receipt, indent=2) + "\n")
        return {"song_id": ident, "status": "completed"}

    results = []
    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        futures = {pool.submit(worker, song): song for song in songs}
        for future in as_completed(futures):
            song = futures[future]
            try:
                result = future.result()
            except (OSError, ValueError, subprocess.TimeoutExpired) as exc:
                result = {"song_id": song["id"], "status": "failed", "reason": str(exc)}
            results.append(result)
            (args.out / "progress.json").write_text(
                json.dumps(results, indent=2) + "\n", encoding="utf-8"
            )
            print(
                f"{len(results)}/{len(songs)} {result['status']}: "
                f"{song.get('artist')} — {song.get('title')}",
                flush=True,
            )
    if any(r["status"] == "failed" for r in results):
        raise ValueError(
            "some survey songs failed; see progress.json; "
            "no replacement or offset fitting performed"
        )
    (args.out / "complete.json").write_text(json.dumps(state, indent=2) + "\n")
