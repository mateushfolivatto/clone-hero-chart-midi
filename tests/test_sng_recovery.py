"""Authored SNG v1 fixtures: XOR resets, streaming boundaries, safety and recovery."""

import hashlib
import struct
import zipfile
from pathlib import Path

import pytest

from drumforge.library import acquire
from drumforge.library import recover_pilot as recovery


def fixture_sng(
    files: list[tuple[str, bytes]], *, metadata: list[tuple[str, str]] | None = None
) -> bytes:
    metadata = metadata if metadata is not None else [("name", "Synthetic"), ("artist", "Test")]
    mask = bytes(range(16, 32))
    pairs = b""
    for key, value in metadata:
        for text in (key, value):
            raw = text.encode()
            pairs += struct.pack("<i", len(raw)) + raw
    meta = struct.pack("<Q", len(metadata)) + pairs
    index_size = 8 + sum(1 + len(name.encode()) + 16 for name, _ in files)
    cursor = 26 + 8 + len(meta) + 8 + index_size + 8
    index = struct.pack("<Q", len(files))
    payload = b""
    for name, data in files:
        raw = name.encode()
        index += bytes([len(raw)]) + raw + struct.pack("<QQ", len(data), cursor)
        # Independent scalar implementation of the published position-dependent mask.
        payload += bytes(value ^ mask[i % 16] ^ (i & 255) for i, value in enumerate(data))
        cursor += len(data)
    return (
        b"SNGPKG\x01\x00\x00\x00"
        + mask
        + struct.pack("<Q", len(meta))
        + meta
        + struct.pack("<Q", len(index))
        + index
        + struct.pack("<Q", len(payload))
        + payload
    )


def test_sng_streaming_preserves_assets_and_stdlib_recovery(tmp_path: Path) -> None:
    assets = [("notes.mid", b"MThd\x00\x00\x00\x06"), ("song.opus", bytes(range(256)) * 4097)]
    raw = fixture_sng(assets)
    source, target = tmp_path / "original.sng", tmp_path / "converted.zip"
    source.write_bytes(raw)
    assert acquire.source_zip(source, target, tmp_path) == "sng"
    with zipfile.ZipFile(target) as archive:
        for name, data in assets:
            assert archive.read(name) == data
        ini = b"[song]\nname = Synthetic\nartist = Test\n"
        assert archive.read("song.ini") == ini
    recipe = {
        "archive_format": "sng",
        "files": [
            {"name": name, "archive_name": name, "sha256": hashlib.sha256(data).hexdigest()}
            for name, data in [("song.ini", ini), *assets]
        ],
    }
    destination = tmp_path / "Song"
    recovery.prepare_song(recipe, source, destination)
    recovery.prepare_song(recipe, source, destination)
    assert source.read_bytes() == raw
    (destination / "song.opus").write_bytes(b"user edit")
    with pytest.raises(ValueError, match="sobrescrito"):
        recovery.prepare_song(recipe, source, destination)
    assert (destination / "song.opus").read_bytes() == b"user edit"


@pytest.mark.parametrize(
    "name", ["../escape", "C:/escape", "a\\escape", "CON.txt", "song.ini", "a.", "."]
)
def test_sng_rejects_unsafe_names(tmp_path: Path, name: str) -> None:
    source, target = tmp_path / "bad.sng", tmp_path / "out.zip"
    source.write_bytes(fixture_sng([(name, b"unsafe")]))
    with pytest.raises(ValueError):
        recovery.sng_as_zip(source, target)
    assert not target.exists()


@pytest.mark.parametrize(
    "metadata", [[("name", "bad\nnew = value")], [("name", "a"), ("NAME", "b")], [("a=b", "c")]]
)
def test_sng_rejects_ini_injection_and_duplicate_metadata(
    tmp_path: Path, metadata: list[tuple[str, str]]
) -> None:
    source = tmp_path / "bad.sng"
    source.write_bytes(fixture_sng([("song.opus", b"audio")], metadata=metadata))
    with pytest.raises(ValueError):
        recovery.sng_as_zip(source, tmp_path / "out.zip")


def test_sng_rejects_wrong_lengths_offsets_version_and_case_collisions(tmp_path: Path) -> None:
    valid = fixture_sng([("song.opus", b"data")])
    mutations = [valid[:-1], valid + b"extra", valid[:6] + b"\x02\x00\x00\x00" + valid[10:]]
    bad_offset = bytearray(valid)
    # The final index record's uint64 offset is immediately before fileDataLen.
    bad_offset[-20:-12] = struct.pack("<Q", 0)
    mutations += [bytes(bad_offset), fixture_sng([("Song.opus", b"a"), ("song.opus", b"b")])]
    for raw in mutations:
        source, target = tmp_path / "bad.sng", tmp_path / "out.zip"
        source.write_bytes(raw)
        with pytest.raises(ValueError):
            recovery.sng_as_zip(source, target)
        assert not target.exists()
        assert not target.with_name(target.name + ".partial").exists()
