import hashlib
import importlib
import json
from pathlib import Path
from typing import Any

import pytest

from drumforge.diagnostics.chart_reference import playback_assets, read_chart_reference
from drumforge.diagnostics.holdout import validate_holdout
from drumforge.diagnostics.matching import score_onsets, training_indices


def _chart(tmp_path: Path, *, delay: str = "125", broken_marker: bool = False) -> Path:
    mido = importlib.import_module("mido")
    folder = tmp_path / "Música com espaço"
    folder.mkdir()
    (folder / "song.ini").write_text(
        f"[song]\nname=Autoral\nartist=Teste\npro_drums=True\ndelay={delay}\n",
        encoding="utf-8",
    )
    midi = mido.MidiFile(type=1, ticks_per_beat=480)
    conductor = mido.MidiTrack()
    conductor.extend(
        [
            mido.MetaMessage("set_tempo", tempo=500_000, time=0),
            mido.MetaMessage("set_tempo", tempo=1_000_000, time=480),
        ]
    )
    drums = mido.MidiTrack()
    # Same-tick marker AFTER note: classification must be independent of ordering.
    drums.extend(
        [
            mido.MetaMessage("track_name", name="PART DRUMS"),
            mido.Message("note_on", note=98, velocity=100),
            mido.Message("note_on", note=110, velocity=100),
            mido.Message("note_on", note=96, velocity=90),
        ]
    )
    if not broken_marker:
        drums.append(mido.Message("note_off", note=110, time=480))
    drums.extend(
        [
            mido.Message("note_on", note=98, velocity=110),
            mido.Message("note_on", note=97, velocity=80, time=480),
            mido.Message("note_on", note=99, velocity=100),
        ]
    )
    midi.tracks.extend([conductor, drums])
    midi.save(folder / "notes.mid")
    return folder


def test_reference_integrates_tempo_delay_and_marker_boundaries(tmp_path: Path) -> None:
    events, meta = read_chart_reference(_chart(tmp_path))
    assert [(e.tick, e.group) for e in events] == [
        (0, "YELLOW_TOM"),
        (0, "KICK"),
        (480, "YELLOW_CYMBAL_PROXY"),
        (960, "SNARE_PROXY"),
        (960, "BLUE_CYMBAL_PROXY"),
    ]
    assert [e.time_seconds for e in events] == [0.125, 0.125, 0.625, 1.625, 1.625]
    assert meta["ini_delay_seconds"] == 0.125
    assert [e.velocity for e in events] == [100, 90, 110, 80, 100]


def test_unterminated_markers_are_not_silently_read_as_cymbals(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="unterminated"):
        read_chart_reference(_chart(tmp_path, broken_marker=True))


@pytest.mark.parametrize("delay", ["nan", "inf", "-inf"])
def test_nonfinite_delay_is_rejected(tmp_path: Path, delay: str) -> None:
    with pytest.raises(ValueError, match="finite"):
        read_chart_reference(_chart(tmp_path, delay=delay))


def test_nonpro_and_five_lane_charts_are_not_relabelled(tmp_path: Path) -> None:
    folder = _chart(tmp_path)
    ini = folder / "song.ini"
    ini.write_text("[song]\npro_drums=False\n")
    with pytest.raises(ValueError, match="four-lane Pro"):
        read_chart_reference(folder)
    ini.write_text("[song]\npro_drums=True\nfive_lane_drums=True\n")
    with pytest.raises(ValueError, match="four-lane Pro"):
        read_chart_reference(folder)


def test_playback_excludes_previews_crowd_and_duplicate_encodings(tmp_path: Path) -> None:
    for name in ["song.ogg", "drums_1.ogg", "drums_2.ogg", "preview.ogg", "crowd.ogg"]:
        (tmp_path / name).touch()
    assert [p.name for p in playback_assets(tmp_path)] == ["drums_1.ogg", "drums_2.ogg", "song.ogg"]
    (tmp_path / "song.mp3").touch()
    with pytest.raises(ValueError, match="multiple encodings"):
        playback_assets(tmp_path)


def test_combined_and_component_drums_require_explicit_selection(tmp_path: Path) -> None:
    for name in ["drums.ogg", "drums_1.ogg"]:
        (tmp_path / name).touch()
    with pytest.raises(ValueError, match="combined and component"):
        playback_assets(tmp_path)


def test_one_prediction_cannot_match_two_reference_attacks() -> None:
    result = score_onsets([1, 1.04], [1.02])
    assert (result["tp"], result["fp"], result["fn"]) == (1, 0, 1)
    assert result["precision"] == 1
    assert result["recall"] == 0.5
    assert result["f1"] == pytest.approx(2 / 3)


def test_duplicate_predictions_count_as_false_positives_and_boundary_is_inclusive() -> None:
    result = score_onsets([1, 2], [1.03, 1.03, 2.031])
    assert (result["tp"], result["fp"], result["fn"]) == (1, 2, 1)
    assert result["mean_absolute_error_ms"] == pytest.approx(30)


def test_simultaneous_classes_are_scored_independently() -> None:
    kick = score_onsets([1], [1.001])
    hat = score_onsets([1], [1.002])
    assert kick["tp"] == hat["tp"] == 1


def test_holdout_excludes_every_excerpt_of_the_test_song() -> None:
    ids = ["a", "a", "b", "b", "c", "c"]
    assert training_indices(ids, "b") == [0, 1, 4, 5]
    with pytest.raises(ValueError, match="at least two"):
        training_indices(["a", "a"], "a")


def test_invalid_metrics_inputs_are_rejected() -> None:
    with pytest.raises(ValueError, match="finite"):
        score_onsets([float("nan")], [])
    with pytest.raises(ValueError, match="positive"):
        score_onsets([], [], tolerance=0)
    assert score_onsets([], [1])["precision"] == 0
    assert score_onsets([], [])["f1"] is None


def _text_reference(tmp_path: Path, *, notes: str = "") -> Path:
    folder = tmp_path / "chart text"
    folder.mkdir()
    (folder / "song.ini").write_text("[song]\npro_drums=True\ndelay=125\n")
    (folder / "notes.chart").write_text(
        "[Song]\n{\n Resolution = 192\n Offset = 0.25\n}\n"
        "[SyncTrack]\n{\n 0 = B 120000\n 192 = B 60000\n}\n"
        "[ExpertDrums]\n{\n" + notes + "\n}\n"
    )
    return folder


def test_text_chart_cymbal_flags_tempo_and_offset_have_distinct_midi_semantics(
    tmp_path: Path,
) -> None:
    folder = _text_reference(
        tmp_path,
        notes=(
            " 0 = N 66 0\n 0 = N 2 0\n 0 = N 0 0\n 192 = N 2 0\n"
            " 384 = N 1 0\n 384 = N 3 0\n 384 = N 67 0"
        ),
    )
    events, meta = read_chart_reference(folder)
    assert [(e.time_seconds, e.group) for e in events] == [
        (0.375, "KICK"),
        (0.375, "YELLOW_CYMBAL_PROXY"),
        (0.875, "YELLOW_TOM"),
        (1.875, "SNARE_PROXY"),
        (1.875, "BLUE_CYMBAL_PROXY"),
    ]
    assert all(e.velocity is None for e in events)
    assert meta["chart_format"] == "chart"
    assert meta["chart_offset_seconds"] == 0.25


@pytest.mark.parametrize(
    ("old", "new", "message"),
    [
        ("0 = N 0 0", "0 = N 5 0", "five-lane"),
        ("0 = N 0 0", "0 = N 66 0", "same-tick"),
        ("Resolution = 192", "Resolution = 0", "Resolution"),
        ("Offset = 0.25", "Offset = nan", "finite"),
        ("0 = B 120000", "0 = B 0", "tempo"),
        ("0 = B 120000", "96 = B 120000", "tick zero"),
    ],
)
def test_invalid_text_references_are_refused(
    tmp_path: Path, old: str, new: str, message: str
) -> None:
    folder = _text_reference(tmp_path, notes=" 0 = N 0 0")
    path = folder / "notes.chart"
    path.write_text(path.read_text().replace(old, new))
    with pytest.raises(ValueError, match=message):
        read_chart_reference(folder)


def test_audio_only_package_does_not_invent_a_drums_stem(tmp_path: Path) -> None:
    (tmp_path / "guitar.ogg").touch()
    with pytest.raises(ValueError, match="drums stem"):
        playback_assets(tmp_path)
    assert [p.name for p in playback_assets(tmp_path, require_drums=False)] == ["guitar.ogg"]


@pytest.mark.parametrize("change", ["same_id", "same_chart", "bad_recipe", "duplicate_id"])
def test_frozen_holdout_rejects_reused_or_unverifiable_training_data(
    tmp_path: Path, change: str
) -> None:
    training = tmp_path / "training.json"
    training.write_text(
        json.dumps({"songs": [{"id": "old", "assets_sha256": {"notes.mid": "aaa"}}]})
    )
    profile = {
        "source_songs": ["old"],
        "source_recipe_sha256": hashlib.sha256(training.read_bytes()).hexdigest(),
    }
    songs: list[dict[str, Any]] = [{"id": "new", "assets_sha256": {"notes.chart": "bbb"}}]
    validate_holdout(profile, training, songs)
    if change == "same_id":
        songs[0]["id"] = "old"
    elif change == "same_chart":
        songs[0]["assets_sha256"]["notes.chart"] = "aaa"
    elif change == "bad_recipe":
        training.write_text(training.read_text() + " ")
    else:
        songs.append(songs[0].copy())
    with pytest.raises(ValueError):
        validate_holdout(profile, training, songs)


def _disco_reference(tmp_path: Path, kind: str, mixes: list[tuple[int, str]]) -> Path:
    folder = tmp_path / kind
    folder.mkdir()
    (folder / "song.ini").write_text("[song]\npro_drums=True\n")
    notes = [(0, 97), (480, 96), (480, 97), (480, 98), (480, 99)] + [
        (tick, note) for tick in (960, 1440) for note in (97, 98)
    ]
    if kind == "chart":
        lines = [(tick, f"N {note - 96} 0") for tick, note in notes]
        lines.extend([(480, "N 67 0"), (1440, "N 66 0")])
        lines.extend((tick, f'E "{text}"') for tick, text in mixes)
        (folder / "notes.chart").write_text(
            "[Song]\n{\n Resolution = 480\n}\n[SyncTrack]\n{\n 0 = B 120000\n}\n"
            "[ExpertDrums]\n{\n"
            + "\n".join(f" {tick} = {text}" for tick, text in sorted(lines, key=lambda x: x[0]))
            + "\n}\n"
        )
    else:
        mido = importlib.import_module("mido")
        midi = mido.MidiFile(type=1, ticks_per_beat=480)
        conductor = mido.MidiTrack([mido.MetaMessage("set_tempo", tempo=500_000)])
        schedule = [(tick, mido.Message("note_on", note=note, velocity=90)) for tick, note in notes]
        # Events follow notes at identical ticks: status resolution must be order-independent.
        schedule.extend(
            [
                (480, mido.Message("note_on", note=110, velocity=100)),
                (1440, mido.Message("note_off", note=110)),
            ]
        )
        schedule.extend((tick, mido.MetaMessage("text", text=text)) for tick, text in mixes)
        track = mido.MidiTrack([mido.MetaMessage("track_name", name="PART DRUMS")])
        previous = 0
        for tick, msg in sorted(schedule, key=lambda x: x[0]):
            track.append(msg.copy(time=tick - previous))
            previous = tick
        midi.tracks.extend([conductor, track])
        midi.save(folder / "notes.mid")
    return folder


@pytest.mark.parametrize("kind", ["mid", "chart"])
@pytest.mark.parametrize("reset", ["[mix 3 drums2]", "mix_3_drumsdnoflip", "mix 3 drums5easy"])
def test_pro_reference_unflips_disco_and_resets_at_the_exact_tick(
    tmp_path: Path, kind: str, reset: str
) -> None:
    folder = _disco_reference(
        tmp_path, kind, [(480, "[mix 3 drums2d]"), (480, "mix_3_drums2d"), (960, reset)]
    )
    source = folder / f"notes.{kind}"
    before = source.read_bytes()
    events, meta = read_chart_reference(folder)
    assert [(e.tick, e.midi_note, e.group) for e in events] == [
        (0, 97, "SNARE_PROXY"),
        (480, 96, "KICK"),
        (480, 97, "YELLOW_CYMBAL_PROXY"),
        (480, 98, "SNARE_PROXY"),
        (480, 99, "BLUE_CYMBAL_PROXY"),
        (960, 97, "SNARE_PROXY"),
        (960, 98, "YELLOW_TOM"),
        (1440, 97, "SNARE_PROXY"),
        (1440, 98, "YELLOW_CYMBAL_PROXY"),
    ]
    assert [e.time_seconds for e in events] == [0, 0.5, 0.5, 0.5, 0.5, 1, 1, 1.5, 1.5]
    assert all(e.velocity == (90 if kind == "mid" else None) for e in events)
    assert meta["expert_disco_flip_starts"] == 1
    assert meta["expert_disco_reclassified_notes"] == 2
    assert source.read_bytes() == before


@pytest.mark.parametrize("kind", ["mid", "chart"])
def test_other_difficulty_mix_does_not_reset_expert_disco(tmp_path: Path, kind: str) -> None:
    folder = _disco_reference(tmp_path, kind, [(480, "mix 3 drumsd"), (960, "mix 2 drums2")])
    events, _ = read_chart_reference(folder)
    assert [(e.midi_note, e.group) for e in events if e.tick == 1440] == [
        (97, "YELLOW_CYMBAL_PROXY"),
        (98, "SNARE_PROXY"),
    ]


@pytest.mark.parametrize("kind", ["mid", "chart"])
@pytest.mark.parametrize(
    ("commands", "message"),
    [
        ([(480, "mix 3 drums2d"), (480, "mix 3 drums2")], "conflicting"),
        ([(480, "mix 3 drums2unexpected")], "unsupported Expert"),
    ],
)
def test_ambiguous_expert_disco_states_are_rejected(
    tmp_path: Path, kind: str, commands: list[tuple[int, str]], message: str
) -> None:
    with pytest.raises(ValueError, match=message):
        read_chart_reference(_disco_reference(tmp_path, kind, commands))
