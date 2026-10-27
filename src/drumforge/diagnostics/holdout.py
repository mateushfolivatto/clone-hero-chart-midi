"""Guard frozen-profile evaluations against accidental reuse of calibration songs."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


def validate_holdout(
    profile: dict[str, Any], training_recipe: Path, evaluation_songs: list[dict[str, Any]]
) -> None:
    data = training_recipe.read_bytes()
    if hashlib.sha256(data).hexdigest() != profile.get("source_recipe_sha256"):
        raise ValueError("training recipe identity differs from the frozen profile")
    training = json.loads(data)["songs"]
    training_ids = {song["id"] for song in training}
    if training_ids != set(profile["source_songs"]):
        raise ValueError("profile source songs differ from its training recipe")
    training_charts = {
        value
        for song in training
        for name, value in song["assets_sha256"].items()
        if name in {"notes.mid", "notes.chart"}
    }
    test_ids = [song["id"] for song in evaluation_songs]
    if not test_ids or len(set(test_ids)) != len(test_ids):
        raise ValueError("evaluation requires unique song ids")
    for song in evaluation_songs:
        if song["id"] in training_ids:
            raise ValueError("evaluation song was used to calibrate the frozen profile")
        if any(
            value in training_charts
            for name, value in song["assets_sha256"].items()
            if name in {"notes.mid", "notes.chart"}
        ):
            raise ValueError("evaluation chart duplicates calibration data under another id")
