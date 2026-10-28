"""Curated groups share immutable recipes and a song is recovered once per union."""

import json
import shutil
from pathlib import Path
from typing import Any

import pytest

from drumforge.library import recover_pilot, recover_selections


def test_group_union_preserves_old_choices_and_shared_enemy_once() -> None:
    metadata = Path(recover_pilot.__file__).parent
    before = {p: p.read_bytes() for p in metadata.glob("*.json")}
    union = recover_selections.selected_manifests(metadata)
    by_group = {
        g: recover_selections.selected_manifests(metadata, [g]) for g in recover_selections.GROUPS
    }

    def ids(manifests: list[dict[str, Any]]) -> set[str]:
        return {s["file_id"] for m in manifests for s in m["songs"]}

    assert ids(union) == set().union(*(ids(ms) for ms in by_group.values()))
    assert sum(len(m["songs"]) for m in union) == len(ids(union))
    # The original Enemy belongs to both Imagine Dragons and LoL, with one source.
    shared = ids(by_group["imagine"]) & ids(by_group["lol"])
    assert shared
    assert sum(s["file_id"] in shared for m in union for s in m["songs"]) == len(shared)
    assert any("Enemy" in s["title"] for m in union for s in m["songs"] if s["file_id"] in shared)
    old_lol = json.loads((metadata / "collection_13.json").read_text())
    enemy_id = next(s["file_id"] for s in old_lol["songs"] if s["artist"] == "Imagine Dragons")
    assert enemy_id in shared
    assert sum(s["file_id"] == enemy_id for m in union for s in m["songs"]) == 1
    for group, manifests in by_group.items():
        if group == "skillet":
            assert all(s["artist"].casefold() == "skillet" for m in manifests for s in m["songs"])
        assert {m["archive_name"] for m in manifests}.isdisjoint(m["archive_name"] for m in union)
    new = recover_selections.selected_manifests(metadata, new_only=True)
    index = json.loads((metadata / "collection_index.json").read_text())
    phase = index["selections"]["skillet-imagine-lol"]
    assert len(ids(new)) == phase["new_charts"]
    assert len(ids(union)) == phase["all_charts"]
    assert all(m["batch_number"] >= 31 for m in new)
    assert len(ids(union) - ids(new)) >= 36
    assert {p: p.read_bytes() for p in metadata.glob("*.json")} == before


def test_changed_scope_is_rejected_before_download(tmp_path: Path) -> None:
    metadata = Path(recover_pilot.__file__).parent
    for path in metadata.iterdir():
        if path.suffix in {".json", ".py"}:
            shutil.copy2(path, tmp_path / path.name)
    (tmp_path / "selection_skillet_imagine_lol.json").write_text("{}")
    with pytest.raises(ValueError, match="Selecao ou auxiliar"):
        recover_selections.selected_manifests(tmp_path)


def test_changed_index_and_unknown_group_fail_before_recipe_reads(tmp_path: Path) -> None:
    (tmp_path / "collection_index.json").write_text("{}")
    with pytest.raises(ValueError, match="Indice diferente"):
        recover_selections.selected_manifests(tmp_path)
    for groups in [[], ["other"]]:
        with pytest.raises(ValueError, match="Selecao desconhecida"):
            recover_selections.selected_manifests(tmp_path, groups)
