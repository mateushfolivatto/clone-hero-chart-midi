"""Playlist exports must never accept incomplete or changing pagination."""

from copy import deepcopy
from typing import Any

import pytest

from drumforge.library import qobuz


def response(offset: int, positions: list[int]) -> dict[str, Any]:
    return {
        "id": 123,
        "name": "Synthetic playlist",
        "tracks_count": 3,
        "updated_at": 1000,
        "is_public": True,
        "tracks": {
            "total": 3,
            "offset": offset,
            "items": [
                {
                    "position": position,
                    "playlist_track_id": position + 100,
                    # A repeated song in a playlist is legitimate; keep both entries.
                    "id": 99,
                    "title": "Synthetic song",
                    "version": "Live" if position == 2 else None,
                    "performer": {"name": "Synthetic artist"},
                    "album": {"title": "Synthetic album"},
                    "duration": 30,
                }
                for position in positions
            ],
        },
    }


def setup_pages(monkeypatch: pytest.MonkeyPatch, pages: list[dict[str, Any]]) -> None:
    pending = iter(pages)
    monkeypatch.setattr(qobuz, "public_app_id", lambda: "public-application-id")
    monkeypatch.setattr(qobuz, "page", lambda *args: deepcopy(next(pending)))


def test_complete_pagination_preserves_repeated_songs_and_versions(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    setup_pages(monkeypatch, [response(0, [1, 2]), response(2, [3]), response(0, [1])])
    metadata, tracks = qobuz.fetch_playlist("123")
    rows = qobuz.rows_for(tracks)
    assert metadata["tracks_count"] == len(rows) == 3
    assert [row["qobuz_track_id"] for row in rows] == ["99", "99", "99"]
    assert [row["version"] for row in rows] == ["", "Live", ""]
    assert [row["playlist_track_id"] for row in rows] == ["101", "102", "103"]


def test_incomplete_pagination_is_an_error(monkeypatch: pytest.MonkeyPatch) -> None:
    setup_pages(monkeypatch, [response(0, [1, 2]), response(2, [])])
    with pytest.raises(ValueError, match="before all tracks"):
        qobuz.fetch_playlist("123")


def test_playlist_mutation_during_pagination_is_an_error(monkeypatch: pytest.MonkeyPatch) -> None:
    changed = response(2, [3])
    changed["updated_at"] = 1001
    setup_pages(monkeypatch, [response(0, [1, 2]), changed])
    with pytest.raises(ValueError, match="changed during export"):
        qobuz.fetch_playlist("123")


def test_repeated_page_is_an_error(monkeypatch: pytest.MonkeyPatch) -> None:
    setup_pages(monkeypatch, [response(0, [1, 2]), response(2, [2])])
    with pytest.raises(ValueError, match="positions"):
        qobuz.fetch_playlist("123")


def test_mutation_after_last_page_is_an_error(monkeypatch: pytest.MonkeyPatch) -> None:
    changed = response(0, [1])
    changed["updated_at"] = 1001
    setup_pages(monkeypatch, [response(0, [1, 2, 3]), changed])
    with pytest.raises(ValueError, match="before export finished"):
        qobuz.fetch_playlist("123")
