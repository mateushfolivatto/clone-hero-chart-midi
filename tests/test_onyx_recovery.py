"""Portable CLI invocation and diagnostics that survive conversion cleanup."""

import builtins
import subprocess
import sys
import threading
from pathlib import Path
from typing import Any

import pytest

from drumforge.library import onyx_recovery, recover_pilot


@pytest.mark.parametrize("platform", ["win32", "linux"])
def test_conversion_uses_runtime_options_supported_by_its_distribution(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, platform: str
) -> None:
    monkeypatch.setattr(sys, "platform", platform)
    project = tmp_path / "project"
    target = tmp_path / "song.zip"
    stages = []

    def run(command: list[str], **kwargs: Any) -> subprocess.CompletedProcess[str]:
        stages.append(command[1])
        if platform == "win32" and "+RTS" in command:
            kwargs["stdout"].write("the flag -N2 requires the program to be built with -threaded\n")
            raise subprocess.CalledProcessError(1, command)
        if platform == "linux":
            assert command[-3:] == ["+RTS", "-N2", "-RTS"]
        if command[1] == "import":
            project.mkdir()
            (project / "song.yml").write_text("metadata: {}\ntargets:\n  existing: {}\n")
        else:
            content = (project / "song.yml").read_text()
            assert "clonehero:\n    game: ps\n" in content
            assert "existing: {}" in content
            target.write_bytes(b"synthetic converted archive")
        return subprocess.CompletedProcess(command, 0)

    monkeypatch.setattr(subprocess, "run", run)
    onyx_recovery.build(tmp_path / "onyx", tmp_path / "source.zip", project, target)
    assert stages == ["import", "build"]
    assert target.read_bytes() == b"synthetic converted archive"


@pytest.mark.parametrize("failure", ["import", "build", "timeout"])
def test_failure_keeps_converter_diagnostic_after_temporary_project_is_deleted(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, failure: str
) -> None:
    monkeypatch.setattr(onyx_recovery, "install", lambda root: tmp_path / "onyx")
    source = tmp_path / "original.zip"
    source.write_bytes(b"synthetic source to preserve")
    destination = tmp_path / "Songs" / "Batch" / "Song"

    def run(command: list[str], **kwargs: Any) -> subprocess.CompletedProcess[str]:
        if command[1] == failure or failure == "timeout":
            kwargs["stdout"].write("Specific converter diagnostic: fixture failure\n")
            kwargs["stdout"].flush()
            if failure == "timeout":
                raise subprocess.TimeoutExpired(command, kwargs["timeout"])
            raise subprocess.CalledProcessError(1, command)
        project = Path(command[command.index("--to") + 1])
        project.mkdir()
        (project / "song.yml").write_text("targets:\n")
        return subprocess.CompletedProcess(command, 0)

    monkeypatch.setattr(subprocess, "run", run)
    song: dict[str, Any] = {"file_id": "fixture", "files": []}
    with pytest.raises(ValueError) as error:
        onyx_recovery.prepare(song, source, destination, tmp_path)
    expected_stage = "exportacao" if failure == "build" else "importacao"
    assert expected_stage in str(error.value)
    assert "Specific converter diagnostic: fixture failure" in str(error.value)
    assert ("tempo limite de 180" if failure == "timeout" else "codigo de saida 1") in str(
        error.value
    )
    logs = list((tmp_path / "Logs" / "Onyx").glob("fixture-*.log"))
    assert len(logs) == 1
    assert str(logs[0]) in str(error.value)
    assert "fixture failure" in logs[0].read_text()
    assert not list(destination.parent.glob("convertendo-*"))
    assert not destination.exists()
    assert not (tmp_path / "Verificacoes").exists()
    assert source.read_bytes() == b"synthetic source to preserve"


def test_elapsed_feedback_during_wait_retains_log_and_stops_after_process(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    seen = threading.Event()
    original_print = builtins.print

    def observe(*values: object, **kwargs: Any) -> None:
        original_print(*values, **kwargs)
        if any("aguardando ha" in str(value) for value in values):
            seen.set()

    def run(command: list[str], **kwargs: Any) -> subprocess.CompletedProcess[str]:
        assert kwargs["stdin"] == subprocess.DEVNULL
        assert kwargs["timeout"] == 180
        assert seen.wait(5), "No elapsed feedback while the converter was waiting"
        kwargs["stdout"].write("Actual converter diagnostic\n")
        return subprocess.CompletedProcess(command, 0)

    monkeypatch.setattr(onyx_recovery, "PROGRESS_SECONDS", 0.001)
    monkeypatch.setattr(builtins, "print", observe)
    monkeypatch.setattr(subprocess, "run", run)
    log_path = tmp_path / "persistent.log"
    with log_path.open("w") as log:
        onyx_recovery.run_logged(["converter"], log, "importacao", 180, log_path)
    output = capsys.readouterr().out
    assert "limite 180s" in output
    assert "aguardando ha" in output
    assert "terminou em" in output
    assert str(log_path) in output
    assert log_path.read_text() == "Actual converter diagnostic\n"
    assert not [t for t in threading.enumerate() if t.name == "onyx-elapsed-feedback"]


def test_ctrl_c_reports_interruption_and_resume_without_traceback(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    def interrupt(*args: Any) -> None:
        raise KeyboardInterrupt

    monkeypatch.setattr(sys, "argv", ["recover_pilot.py", "--destino", str(tmp_path)])
    monkeypatch.setattr(recover_pilot, "read_manifest", lambda *args: {})
    monkeypatch.setattr(recover_pilot, "recover", interrupt)
    with pytest.raises(SystemExit) as exit:
        recover_pilot.main()
    assert exit.value.code == 130
    error = capsys.readouterr().err
    assert "Ctrl+C encerra a execucao; nao pula a musica" in error
    assert "foram preservados" in error
    assert "retomar" in error
    assert "Traceback" not in error
