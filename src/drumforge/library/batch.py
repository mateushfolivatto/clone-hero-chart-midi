"""Resume public playlist matching and inspect every obtainable native/console candidate."""

from __future__ import annotations

import argparse
import csv
import json
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

from drumforge.library.acquire import acquire_native
from drumforge.library.rhythmverse import candidates, normalized, search, title_key


def save(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".partial")
    temporary.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    temporary.replace(path)


def run(
    playlist: Path,
    root: Path,
    onyx: Path | None,
    retry: bool = False,
    *,
    allow_standard: bool = True,
) -> list[dict[str, Any]]:
    rows = list(csv.DictReader(playlist.open(encoding="utf-8-sig")))
    reports = root / "reports"
    failure_path = reports / "acquire-failures.json"
    failures = (
        {}
        if retry or not failure_path.exists()
        else json.loads(failure_path.read_text(encoding="utf-8"))
    )
    searches = []
    errors = []
    tasks = [
        (artist, game)
        for artist in dict.fromkeys(r["artist"] for r in rows)
        for game in ("ch", "ps", "rb3xbox", "all")
    ]
    with ThreadPoolExecutor(max_workers=2) as pool:
        pending = {
            pool.submit(search, artist, game, reports / "search-rest"): (artist, game)
            for artist, game in tasks
        }
        for future in as_completed(pending):
            artist, game = pending[future]
            try:
                searches.extend(future.result())
                print(f"Catalogo {game}: {artist}", flush=True)
            except (OSError, ValueError, KeyError) as exc:
                errors.append({"artist": artist, "game": game, "error": str(exc)})
    save(reports / "search-errors.json", errors)
    pilot = json.loads(Path(__file__).with_name("pilot_01.json").read_text(encoding="utf-8"))
    known = {(normalized(s["artist"]), title_key(s["title"])): s for s in pilot["songs"]}
    locks = {str(s["file"]["file_id"]): threading.Lock() for s in searches}

    def prepare(row: dict[str, Any]) -> dict[str, Any]:
        key = (normalized(row["artist"]), title_key(row["title"]))
        if key in known:
            return {"track": row, "status": "pilot", "file_id": known[key]["file_id"]}
        options = candidates(row, searches)
        attempts = []
        standards = {}
        for candidate in options:
            if candidate["version_review"]:
                continue
            identity = str(candidate["file_id"])
            with locks[identity]:
                if (
                    identity in failures
                    and not (reports / "prepared" / (identity + ".json")).exists()
                ):
                    attempts.append({"file_id": identity, "error": failures[identity]})
                    if "explicit Pro Drums" in failures[identity]:
                        standards[identity] = candidate
                    continue
                try:
                    receipt = acquire_native(candidate, root, onyx)
                    if receipt.get("drum_mode") == "standard":
                        standards[identity] = candidate
                        continue
                    print(f"PRONTA {row['position']}: {row['artist']} - {row['title']}", flush=True)
                    return {
                        "track": row,
                        "status": "prepared",
                        "file_id": identity,
                        "folder": receipt["folder"],
                    }
                except Exception as exc:
                    error = f"{type(exc).__name__}: {str(exc)[:500]}"
                    failures[identity] = error
                    if "explicit Pro Drums" in error:
                        standards[identity] = candidate
                    attempts.append({"file_id": identity, "error": error})
                    print(f"PENDENTE {row['artist']} - {row['title']}: {error}", flush=True)
        if allow_standard:
            for identity, candidate in standards.items():
                with locks[identity]:
                    try:
                        receipt = acquire_native(candidate, root, onyx, allow_standard=True)
                        return {
                            "track": row,
                            "status": "prepared",
                            "file_id": identity,
                            "folder": receipt["folder"],
                            "drum_mode": receipt.get("drum_mode", "pro"),
                        }
                    except Exception as exc:
                        failures[identity] = f"{type(exc).__name__}: {str(exc)[:500]}"
        relevant_errors = [error for error in errors if error["artist"] == row["artist"]]
        return {
            "track": row,
            "status": "blocked"
            if attempts or relevant_errors
            else "needs_review"
            if options
            else "not_found_in_searched_catalogs",
            "attempts": attempts,
            "candidates": options,
            "search_errors": relevant_errors,
        }

    results: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=2) as pool:
        preparations = [pool.submit(prepare, row) for row in rows]
        for preparation in as_completed(preparations):
            results.append(preparation.result())
            results.sort(key=lambda item: int(item["track"]["position"]))
            save(reports / "collection-progress.json", results)
            save(failure_path, failures)
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("playlist", type=Path)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--onyx", type=Path)
    parser.add_argument("--retry-failures", action="store_true")
    parser.add_argument("--pro-only", action="store_true", help="Exclude ordinary four-lane drums")
    args = parser.parse_args()
    run(
        args.playlist.absolute(),
        args.root.absolute(),
        args.onyx.absolute() if args.onyx else None,
        args.retry_failures,
        allow_standard=not args.pro_only,
    )


if __name__ == "__main__":
    main()
