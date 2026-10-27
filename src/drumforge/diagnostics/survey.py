"""Deterministic song sampling for a bounded, artist-balanced diagnostic survey."""

from __future__ import annotations

import hashlib
import unicodedata
from collections import defaultdict
from typing import Any


def identity(text: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", text).casefold() if c.isalnum())


def balanced_selection(
    candidates: list[dict[str, Any]], *, count: int, per_artist: int, seed: str
) -> list[dict[str, Any]]:
    if count < 1 or per_artist < 1:
        raise ValueError("positive song count and artist cap required")
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    keys = set()
    for song in sorted(candidates, key=lambda s: s["chart_sha256"]):
        artist = identity(song["artist"])
        key = (artist, identity(song["title"]))
        if key in keys:
            continue
        keys.add(key)
        groups[artist].append(song)

    def rank(value: str) -> str:
        return hashlib.sha256((seed + value).encode()).hexdigest()

    for values in groups.values():
        values.sort(
            key=lambda s: (
                not bool(s.get("component_sources")),
                not s["has_drum_files"],
                rank(s["chart_sha256"]),
            )
        )
    selected = []
    for index in range(per_artist):
        for artist in sorted(groups, key=rank):
            if index < len(groups[artist]):
                selected.append(groups[artist][index])
                if len(selected) == count:
                    return selected
    raise ValueError("not enough eligible songs under the artist cap")
