import importlib
from pathlib import Path

import pytest

from drumforge.diagnostics.chart_reference import playback_assets, read_chart_reference
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
