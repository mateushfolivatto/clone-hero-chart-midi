import csv
import hashlib
import json
import struct
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from drumforge.transcription.inspect_midi import (
    MidiInspectionError,
    inspect_raw_midi,
    write_midi_diagnostics,
)


def _midi(
    tmp_path: Path, tracks: list[bytes], *, division: int = 480, midi_format: int = 1
) -> Path:
    """Authored MIDI bytes; expected timing is independent of a MIDI writer."""
    path = tmp_path / "raw.mid"
    path.write_bytes(
        b"MThd"
        + struct.pack(">IHHH", 6, midi_format, len(tracks), division)
        + b"".join(b"MTrk" + struct.pack(">I", len(track)) + track for track in tracks)
    )
    return path


def _example(tmp_path: Path) -> Path:
    # 120 BPM until tick 480, then 60 BPM. End of conductor is not end of MIDI.
    conductor = bytes.fromhex("00 ff510307a120 8360 ff51030f4240 8360 ff2f00")
    drums = bytes.fromhex(
        "00 992364 00 992a20 00 992f40 8170 992a10 8170 99267f "
        "8170 997f01 8170 892a00 00 992a00 8360 993150 00 ff2f00"
    )
    melody = bytes.fromhex("00 903c70 8360 803c00 00 ff2f00")
    return _midi(tmp_path, [conductor, drums, melody])


def test_tempo_changes_simultaneous_classes_velocities_and_unknowns(tmp_path: Path) -> None:
    source = _example(tmp_path)
    original = source.read_bytes()
    inspection = inspect_raw_midi(source)
    assert [onset.time_seconds for onset in inspection.onsets] == [0, 0, 0, 0.25, 0.5, 1, 2.5]
    assert [onset.velocity for onset in inspection.onsets] == [100, 32, 64, 16, 127, 1, 80]
    assert [onset.midi_note for onset in inspection.onsets] == [35, 42, 47, 42, 38, 127, 49]
    assert inspection.report["counts_by_group"] == {
        "BD": 1,
        "SD": 1,
        "HH": 2,
        "TT": 1,
        "CY": 1,
        "UNKNOWN": 1,
    }
    assert inspection.report["midi_duration_seconds"] == 2.5
    assert inspection.report["ignored_nonpercussion_note_ons"] == 1
    assert inspection.report["tempo_changes"] == [
        {"tick": 0, "time_seconds": 0, "microseconds_per_quarter": 500_000},
        {"tick": 480, "time_seconds": 0.5, "microseconds_per_quarter": 1_000_000},
    ]
    assert inspection.report["source_sha256"] == hashlib.sha256(original).hexdigest()
    assert source.read_bytes() == original


def test_format_zero_default_tempo_running_status_and_duplicate_onsets(tmp_path: Path) -> None:
    source = _midi(
        tmp_path,
        [bytes.fromhex("8170 992a05 00 2a06 8170 2a00 00 ff2f00")],
        midi_format=0,
    )
    inspection = inspect_raw_midi(source)
    assert [onset.time_seconds for onset in inspection.onsets] == [0.25, 0.25]
    assert [onset.velocity for onset in inspection.onsets] == [5, 6]
    assert inspection.report["midi_duration_seconds"] == 0.5
    assert inspection.report["tempo_changes"] == []


def test_empty_percussion_is_reported_without_inventing_notes(tmp_path: Path) -> None:
    source = _midi(tmp_path, [bytes.fromhex("00 903c40 8360 803c00 00 ff2f00")])
    inspection = inspect_raw_midi(source)
    assert inspection.onsets == ()
    assert inspection.report["last_onset_seconds"] is None
    assert all(value == 0 for value in inspection.report["counts_by_group"].values())
    assert any("No positive-velocity" in warning for warning in inspection.report["warnings"])


@pytest.mark.parametrize(
    ("midi_format", "division", "track", "message"),
    [
        (2, 480, "00 ff2f00", "synchronous"),
        (1, 0, "00 ff2f00", "PPQN"),
        (1, 0xE728, "00 ff2f00", "SMPTE"),
        (1, 480, "00 ff5103000000 00 ff2f00", "tempo must be positive"),
        (1, 480, "00 ff030a50415254204452554d53 00 ff2f00", "PART DRUMS"),
        (1, 480, "00 992aff 00 ff2f00", "data byte"),
    ],
)
def test_unsupported_or_invalid_midi_is_rejected(
    tmp_path: Path, midi_format: int, division: int, track: str, message: str
) -> None:
    source = _midi(tmp_path, [bytes.fromhex(track)], midi_format=midi_format, division=division)
    with pytest.raises(MidiInspectionError, match=message):
        inspect_raw_midi(source)


def test_truncated_midi_creates_no_report(tmp_path: Path) -> None:
    source = _example(tmp_path)
    source.write_bytes(source.read_bytes()[:-5])
    with pytest.raises(MidiInspectionError, match="cannot inspect"):
        write_midi_diagnostics(source, tmp_path / "report")
    assert not (tmp_path / "report").exists()


def test_diagnostics_are_reproducible_and_keep_every_csv_onset(tmp_path: Path) -> None:
    source = _example(tmp_path)
    first, second = tmp_path / "first", tmp_path / "second"
    write_midi_diagnostics(source, first)
    write_midi_diagnostics(source, second)
    for name in ["report.json", "events.csv"]:
        assert (first / name).read_bytes() == (second / name).read_bytes()
    with (first / "events.csv").open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    assert len(rows) == 7
    assert [row["group"] for row in rows[:3]] == ["BD", "HH", "TT"]
    assert [float(row["time_seconds"]) for row in rows][-2:] == [1, 2.5]
    report = json.loads((first / "report.json").read_text())
    assert report["total_note_ons"] == len(rows)


def test_existing_output_is_preserved(tmp_path: Path) -> None:
    source = _example(tmp_path)
    output = tmp_path / "report"
    output.mkdir()
    sentinel = output / "report.json"
    sentinel.write_bytes(b"existing manual report")
    with pytest.raises(MidiInspectionError, match="already exists"):
        write_midi_diagnostics(source, output)
    assert sentinel.read_bytes() == b"existing manual report"


def test_failed_report_write_removes_partial_directory(tmp_path: Path) -> None:
    source = _example(tmp_path)
    output = tmp_path / "report"
    with (
        patch.object(Path, "write_text", side_effect=PermissionError("read-only")),
        pytest.raises(MidiInspectionError, match="cannot write"),
    ):
        write_midi_diagnostics(source, output)
    assert not output.exists()
    assert source.is_file()


def test_optional_midi_dependency_has_actionable_error(tmp_path: Path) -> None:
    with (
        patch(
            "drumforge.transcription.inspect_midi.importlib.import_module", side_effect=ImportError
        ),
        pytest.raises(MidiInspectionError, match="--extra diagnostics"),
    ):
        inspect_raw_midi(tmp_path / "raw.mid")


def test_cli_writes_diagnostics_and_refuses_overwrite(tmp_path: Path) -> None:
    working = tmp_path / "áudio e MIDI"
    working.mkdir()
    source = _example(working)
    command = [
        sys.executable,
        "-m",
        "drumforge",
        "inspect-midi",
        str(source),
        "--out",
        str(working / "relatório MIDI"),
    ]
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["counts_by_group"]["HH"] == 2
    repeat = subprocess.run(command, capture_output=True, text=True, check=False)
    assert repeat.returncode == 2
    assert "already exists" in repeat.stderr
    assert "Traceback" not in repeat.stderr
