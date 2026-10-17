"""Cache public drum-catalog searches and suggest conservative playlist matches."""

from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from pathlib import Path
from typing import Any
from urllib.parse import urlencode, urljoin
from urllib.request import Request, urlopen

ROOT = "https://rhythmverse.co"


def normalized(value: str) -> str:
    value = unicodedata.normalize("NFKD", value.casefold()).replace("&", "and")
    return "".join(char for char in value if char.isalnum())


def title_key(value: str) -> str:
    # Editions can differ in mastering; never strip live, demo, remix or acoustic labels.
    value = re.sub(r"(?i)\s*[\[(][^\])]*(?:remaster|album version)[^\])]*[\])]", "", value)
    value = re.sub(r"(?i)\s*[-–]\s*(?:\d{4}\s+)?remaster(?:ed)?(?:\s+\d{4})?$", "", value)
    return normalized(value)


def search(artist: str, game: str, cache: Path) -> list[dict[str, Any]]:
    if game not in {"ch", "ps", "rb3xbox", "all"}:
        raise ValueError("Unsupported catalog")
    cache.mkdir(parents=True, exist_ok=True)
    prefix = game + "-" + hashlib.sha256(artist.encode()).hexdigest()[:12]
    songs: list[dict[str, Any]] = []
    seen: set[str] = set()
    pages: set[tuple[str, ...]] = set()
    expected_total: int | None = None
    for page in range(1, 31):
        target = cache / f"{prefix}-{page}.json"
        if target.exists():
            response = json.loads(target.read_text(encoding="utf-8"))
        else:
            payload = urlencode(
                {
                    "text": artist,
                    "instrument[]": "drums",
                    "data_type": "full",
                    "page": page,
                    "records": 100,
                }
            ).encode()
            request = Request(
                f"{ROOT}/api/{game}/songfiles/search/live",
                data=payload,
                headers={"Referer": f"{ROOT}/songfiles/game/{game}"},
            )
            with urlopen(request, timeout=90) as stream:
                response = json.load(stream)
            if response.get("status") != "success":
                raise ValueError("Catalog search did not succeed")
            target.write_text(json.dumps(response, ensure_ascii=False), encoding="utf-8")
        data = response["data"]
        batch = data["songs"] or []
        total = int(data["records"]["total_filtered"])
        if expected_total is not None and total != expected_total:
            raise ValueError("Catalog total changed during pagination")
        expected_total = total
        if not isinstance(batch, list):
            raise ValueError("Unexpected song list")
        pagination = data.get("pagination")
        if pagination and (
            int(pagination["page"]) != page or int(pagination["start"]) != (page - 1) * 100
        ):
            raise ValueError("Catalog page offset is inconsistent")
        fingerprint = tuple(str(song["file"]["file_id"]) for song in batch)
        if fingerprint in pages:
            raise ValueError("Catalog repeated a page")
        pages.add(fingerprint)
        for song in batch:
            identity = str(song["file"]["file_id"])
            if identity in seen:
                continue  # The real API can repeat a joined row within a page.
            seen.add(identity)
            songs.append(song)
        if len(songs) == total:
            return songs
        if not batch or len(songs) > total:
            raise ValueError("Incomplete or inconsistent catalog pagination")
    raise ValueError("Catalog search exceeded its page budget")


def candidates(row: dict[str, Any], songs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    matches = []
    seen = set()
    for song in songs:
        data, file = song["data"], song["file"]
        difficulty = file.get("diff_drums")
        if difficulty is None or int(difficulty) < 0 or file.get("retired") or file.get("deleted"):
            continue
        artist = file.get("file_artist") or data["artist"]
        title = file.get("file_title") or data["title"]
        if normalized(artist) != normalized(row["artist"]):
            continue
        if title_key(title) != title_key(row["title"]):
            continue
        source_live = bool(data.get("live")) or bool(re.search(r"\blive\b", title, re.I))
        wanted_live = bool(
            re.search(r"\blive\b", row["title"] + " " + row.get("version", ""), re.I)
        )
        if source_live != wanted_live:
            continue
        if file["file_id"] in seen:
            continue
        seen.add(file["file_id"])
        duration = float(file.get("file_song_length") or data.get("song_length") or 0)
        difference = abs(duration - float(row["duration_seconds"])) if duration else None
        url = urljoin(ROOT, file["download_url"])
        matches.append(
            {
                "file_id": file["file_id"],
                "artist": artist,
                "title": title,
                "album": file.get("file_album") or data.get("album"),
                "game": file["gameformat"],
                "source_url": file["file_url_full"],
                "download_url": url,
                "duration_seconds": duration,
                "duration_difference_seconds": difference,
                "version_review": difference is None or difference > 8,
                "catalog_pro_drums": file.get("pro_drums"),
                "catalog_charter": file.get("charter"),
                "uploader": (file.get("author") or {}).get("name"),
                "notes": file.get("file_notes"),
                "match_basis": "artist/title/version labels and duration; master not established",
            }
        )
    return sorted(
        matches,
        key=lambda item: (
            item["version_review"],
            {"ch": 0, "ps": 1, "rb3xbox": 2}.get(item["game"], 3),
            not item["download_url"].startswith(ROOT + "/download_file/"),
            item["duration_difference_seconds"] or 0,
            not item["catalog_pro_drums"],
        ),
    )
