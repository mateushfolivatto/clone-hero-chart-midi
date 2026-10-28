"""Published recipes must remain pinned and incremental collections must be new."""

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

from drumforge.library import recover_pilot
from drumforge.library.rhythmverse import normalized, title_key

METADATA = Path(__file__).resolve().parents[1] / "src/drumforge/library"


def test_published_collection_index_and_recipes_are_consistent() -> None:
    path = METADATA / "collection_index.json"
    assert recover_pilot.digest_file(path) == recover_pilot.COLLECTION_SHA256
    index = json.loads(path.read_text(encoding="utf-8"))
    songs: list[dict[str, Any]] = []
    themed_counts: Counter[str] = Counter()
    numbers = []
    for batch in index["batches"]:
        manifest = recover_pilot.read_manifest(METADATA / batch["manifest"], batch["sha256"])
        assert manifest["batch_number"] == batch["number"]
        assert len(manifest["songs"]) == batch["songs"]
        assert len(manifest["songs"]) <= 25
        assert manifest.get("drum_mode", "pro") == batch["drum_mode"]
        assert all(s.get("drum_mode", "pro") == batch["drum_mode"] for s in manifest["songs"])
        numbers.append(batch["number"])
        songs.extend(manifest["songs"])
        if manifest.get("theme"):
            themed_counts[manifest["theme"]] += len(manifest["songs"])
    assert numbers == sorted(set(numbers))
    assert index["unique_new_charts"] == len(songs)
    assert index["drum_modes"] == dict(Counter(s.get("drum_mode", "pro") for s in songs))
    for name, digest in index["helpers"].items():
        assert recover_pilot.digest_file(METADATA / name) == digest
    assert index["curated_charts"] == sum(themed_counts.values())
    assert index["curated_by_theme"] == dict(themed_counts)
    if "linkin-park" in themed_counts:
        assert index["linkin_park_expansion"]["charts"] == themed_counts["linkin-park"]
        assert set(index["addition_helpers"]) == {
            "additions.py",
            "complement.py",
            "local_library.py",
            "recover_linkin_park.py",
        }
        for name, digest in index["addition_helpers"].items():
            assert recover_pilot.digest_file(METADATA / name) == digest


def test_themed_additions_do_not_repeat_previous_songs_or_packages() -> None:
    pilot = json.loads((METADATA / "pilot_01.json").read_text(encoding="utf-8"))
    earlier = list(pilot["songs"])
    additions: list[dict[str, Any]] = []
    for path in sorted(METADATA.glob("collection_[0-9]*.json")):
        manifest = json.loads(path.read_text(encoding="utf-8"))
        (additions if manifest.get("theme") else earlier).extend(manifest["songs"])
    keys = {(normalized(s["artist"]), title_key(s["title"])) for s in earlier}
    ids = {s["file_id"] for s in earlier}
    archives = {s["archive_sha256"] for s in earlier if "archive_sha256" in s}

    def chart_audio(song: dict[str, Any]) -> tuple[tuple[str, ...], tuple[str, ...]]:
        chart = []
        audio = []
        for asset in song["files"]:
            suffix = Path(asset["name"]).suffix.casefold()
            if suffix in {".mid", ".chart"}:
                chart.append(asset["sha256"])
            elif suffix in {".ogg", ".opus", ".mp3", ".wav"}:
                audio.append(asset["sha256"])
        return tuple(sorted(chart)), tuple(sorted(audio))

    contents = {chart_audio(s) for s in earlier}
    chart_hashes = {digest for s in earlier for digest in chart_audio(s)[0]}
    for song in additions:
        key = (normalized(song["artist"]), title_key(song["title"]))
        assert key not in keys, key
        assert song["file_id"] not in ids
        assert chart_audio(song) not in contents
        assert not chart_hashes.intersection(chart_audio(song)[0])
        assert not song.get("qobuz_track_ids")
        assert not song.get("playlist_track_ids")
        if "archive_sha256" in song:
            assert song["archive_sha256"] not in archives
            archives.add(song["archive_sha256"])
        assert not song["validation"]["game_verified"]
        assert song["validation"]["decoded_audio_files"] > 0
        assert song["validation"]["drums"]["expert_note_on_count"] >= 20
        assert song["validation"]["drums"]["kick_note_on_count"] > 0
        assert all(len(a["sha256"]) == hashlib.sha256().digest_size * 2 for a in song["files"])
        keys.add(key)
        ids.add(song["file_id"])
        contents.add(chart_audio(song))
        chart_hashes.update(chart_audio(song)[0])


def test_strokes_highlights_keep_studio_titles_with_live_or_cover_words() -> None:
    index = json.loads((METADATA / "collection_index.json").read_text())
    numbers = set(index["strokes_selection"]["batch_numbers"])
    songs = [
        song
        for batch in index["batches"]
        if batch["number"] in numbers
        for song in json.loads((METADATA / batch["manifest"]).read_text())["songs"]
    ]
    assert len(songs) == len({title_key(song["title"]) for song in songs}) == 20
    assert all(normalized(song["artist"]) == "thestrokes" for song in songs)
    assert {
        "reptilia",
        "lastnite",
        "someday",
        "hardtoexplain",
        "youonlyliveonce",
        "undercoverofdarkness",
        "theadultsaretalking",
    } <= {title_key(song["title"]) for song in songs}


def test_given_up_stays_once_in_its_existing_batch() -> None:
    matches: list[tuple[int, dict[str, Any]]] = []
    for path in METADATA.glob("collection_[0-9]*.json"):
        manifest = json.loads(path.read_text(encoding="utf-8"))
        matches.extend(
            (manifest["batch_number"], song)
            for song in manifest["songs"]
            if normalized(song["artist"]) == "linkinpark" and title_key(song["title"]) == "givenup"
        )
    assert len(matches) == 1
    assert matches[0][0] == 2
    assert matches[0][1]["validation"]["drums"]["pro_drums_evidence"]
