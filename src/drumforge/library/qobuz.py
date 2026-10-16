"""Export metadata from a public Qobuz playlist, without authentication or audio."""

from __future__ import annotations

import argparse
import csv
import importlib
import json
import re
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlencode, urljoin
from urllib.request import Request, urlopen

PAGE_SIZE = 100
HEADERS = {
    "User-Agent": "DrumForge-PlaylistMetadata/1.0",
    "Referer": "https://open.qobuz.com/",
}
FIELDS = [
    "position",
    "artist",
    "title",
    "album",
    "version",
    "duration_seconds",
    "qobuz_track_url",
    "isrc",
    "qobuz_track_id",
    "playlist_track_id",
]


def read_url(url: str) -> bytes:
    with urlopen(Request(url, headers=HEADERS), timeout=30) as response:
        return bytes(response.read())


def public_app_id() -> str:
    """Read the public application's identifier, never its secret or a user token."""
    page_url = "https://open.qobuz.com/"
    html = read_url(page_url).decode("utf-8")
    scripts = re.findall(r'<script[^>]+src="([^"]+\.js)"', html)
    for script in scripts:
        javascript = read_url(urljoin(page_url, script)).decode("utf-8")
        match = re.search(r'qobuzapi=\{app_id:"([0-9]+)"', javascript)
        if match:
            return match[1]
    raise ValueError("Qobuz's public frontend changed; application identifier not found")


def page(playlist_id: str, app_id: str, offset: int, limit: int = PAGE_SIZE) -> dict[str, Any]:
    query = urlencode(
        {
            "playlist_id": playlist_id,
            "extra": "tracks",
            "offset": offset,
            "limit": limit,
            "app_id": app_id,
        }
    )
    data = json.loads(read_url("https://www.qobuz.com/api.json/0.2/playlist/get?" + query))
    if not isinstance(data, dict) or data.get("status") == "error":
        raise ValueError("Qobuz did not return playlist metadata")
    return data


def snapshot_key(data: dict[str, Any]) -> tuple[Any, ...]:
    return data["id"], data["tracks_count"], data["updated_at"]


def fetch_playlist(playlist_id: str) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    app_id = public_app_id()
    first = page(playlist_id, app_id, 0)
    if first.get("is_public") is not True:
        raise ValueError("This helper supports public playlists only")
    total = first["tracks_count"]
    if not isinstance(total, int) or total < 0:
        raise ValueError("Invalid playlist track count")
    tracks: list[dict[str, Any]] = []
    current = first
    while True:
        if snapshot_key(current) != snapshot_key(first):
            raise ValueError("Playlist changed during export; retry into a new snapshot")
        block = current["tracks"]
        if block["total"] != total or block["offset"] != len(tracks):
            raise ValueError("Pagination total or offset is inconsistent")
        items = block["items"]
        if not isinstance(items, list) or len(tracks) + len(items) > total:
            raise ValueError("Invalid page length")
        tracks.extend(items)
        if len(tracks) == total:
            break
        if not items:
            raise ValueError("Pagination ended before all tracks were returned")
        current = page(playlist_id, app_id, len(tracks))
    if [track["position"] for track in tracks] != list(range(1, total + 1)):
        raise ValueError("Playlist positions are missing, repeated or out of order")
    if len({track["playlist_track_id"] for track in tracks}) != total:
        raise ValueError("Playlist entries are repeated across pages")
    if snapshot_key(page(playlist_id, app_id, 0, 1)) != snapshot_key(first):
        raise ValueError("Playlist changed before export finished; retry")
    return {key: value for key, value in first.items() if key != "tracks"}, tracks


def rows_for(tracks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for track in tracks:
        album = track.get("album") or {}
        performer = track.get("performer") or album.get("artist") or {}
        rows.append(
            dict(
                zip(
                    FIELDS,
                    [
                        track["position"],
                        performer.get("name", ""),
                        track["title"],
                        album.get("title", ""),
                        track.get("version") or "",
                        track.get("duration") or 0,
                        f"https://open.qobuz.com/track/{track['id']}",
                        track.get("isrc") or "",
                        str(track["id"]),
                        str(track["playlist_track_id"]),
                    ],
                    strict=True,
                )
            )
        )
    return rows


def write_xlsx(path: Path, rows: list[dict[str, Any]]) -> None:
    # Optional tool; never added to the core project's dependency declarations.
    openpyxl = importlib.import_module("openpyxl")
    styles = importlib.import_module("openpyxl.styles")
    utils = importlib.import_module("openpyxl.utils")

    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "Playlist"
    sheet.append(FIELDS)
    for row in rows:
        sheet.append([row[field] for field in FIELDS])
    for row in sheet.iter_rows():
        for cell in row:
            if isinstance(cell.value, str):
                cell.data_type = "s"
    for cell in sheet[1]:
        cell.font = styles.Font(bold=True, color="FFFFFF")
        cell.fill = styles.PatternFill("solid", fgColor="24476B")
    for index, width in enumerate([12, 30, 48, 48, 30, 20, 48, 20, 24, 24], start=1):
        sheet.column_dimensions[utils.get_column_letter(index)].width = width
    sheet.freeze_panes = "C2"
    sheet.auto_filter.ref = sheet.dimensions
    workbook.save(path)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("playlist", help="Numeric ID or https://open.qobuz.com/playlist/ID")
    parser.add_argument("--output-dir", type=Path, required=True, help="New snapshot directory")
    parser.add_argument("--xlsx", action="store_true", help="Also create Excel; needs openpyxl")
    args = parser.parse_args()
    match = re.fullmatch(r"(?:https://open\.qobuz\.com/playlist/)?([0-9]+)/?", args.playlist)
    if not match:
        parser.error("Use a numeric playlist ID or its open.qobuz.com URL")
    output = args.output_dir.absolute()
    if output.exists():
        parser.error("Output directory already exists; choose a new snapshot to preserve files")
    try:
        metadata, tracks = fetch_playlist(match[1])
        rows = rows_for(tracks)
        manifest = {
            "source_url": f"https://open.qobuz.com/playlist/{match[1]}",
            "exported_at_utc": datetime.now(UTC).isoformat(),
            "playlist_name": metadata["name"],
            "playlist_updated_at": metadata["updated_at"],
            "expected_tracks": metadata["tracks_count"],
            "exported_tracks": len(rows),
            "unique_track_ids": len({track["id"] for track in tracks}),
            "duration_seconds": sum(row["duration_seconds"] for row in rows),
            "complete": True,
            "audio_downloaded": False,
        }
        output.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="qobuz-export-", dir=output.parent) as temporary:
            staged = Path(temporary) / "snapshot"
            staged.mkdir()
            with (staged / "playlist.csv").open("w", encoding="utf-8-sig", newline="") as file:
                writer = csv.DictWriter(file, fieldnames=FIELDS)
                writer.writeheader()
                writer.writerows(rows)
            for filename, value in [
                ("playlist.json", {"playlist": metadata, "tracks": tracks}),
                ("manifest.json", manifest),
            ]:
                (staged / filename).write_text(
                    json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
                )
            if args.xlsx:
                write_xlsx(staged / "playlist.xlsx", rows)
            if output.exists():
                raise FileExistsError("Snapshot destination appeared during export")
            staged.rename(output)
        print(json.dumps({"output_dir": str(output), **manifest}, ensure_ascii=False, indent=2))
    except (OSError, ValueError, KeyError, TypeError, ImportError) as exc:
        parser.exit(1, f"Export failed: {type(exc).__name__}: {exc}\n")


if __name__ == "__main__":
    main()
