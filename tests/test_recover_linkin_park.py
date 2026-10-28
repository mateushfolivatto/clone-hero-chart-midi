"""Band recovery references the immutable old and new recipes, including Given Up."""

import json
from pathlib import Path

import pytest

from drumforge.library import recover_linkin_park, recover_pilot


def test_selection_preserves_recipes_and_covers_given_up_once() -> None:
    metadata = Path(recover_pilot.__file__).parent
    paths = list(metadata.glob("*.json"))
    before = {path: path.read_bytes() for path in paths}
    manifests = recover_linkin_park.selected_manifests(metadata)
    songs = [song for manifest in manifests for song in manifest["songs"]]
    assert all(recover_linkin_park.band_song(song) for song in songs)
    assert len({song["file_id"] for song in songs}) == len(songs)
    given_up = [
        manifest
        for manifest in manifests
        if any(s["title"] == "Given Up" for s in manifest["songs"])
    ]
    assert len(given_up) == 1
    assert given_up[0]["batch_number"] == 2
    assert given_up[0]["archive_name"] == "MixDrumRock-LinkinPark-lote-02.zip"
    assert all(manifest["archive_name"].endswith(".zip") for manifest in manifests)
    additions = recover_linkin_park.selected_manifests(metadata, new_only=True)
    index = json.loads((metadata / "collection_index.json").read_text())
    assert sum(len(m["songs"]) for m in additions) == index.get("curated_by_theme", {}).get(
        "linkin-park", 0
    )
    assert all(m["theme"] == "linkin-park" for m in additions)
    assert {path: path.read_bytes() for path in paths} == before


def test_changed_index_is_rejected_before_selection(tmp_path: Path) -> None:
    (tmp_path / "collection_index.json").write_text("{}")
    with pytest.raises(ValueError, match="Indice diferente"):
        recover_linkin_park.selected_manifests(tmp_path)
