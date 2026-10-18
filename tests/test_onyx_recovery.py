"""Portable CLI invocation and diagnostics that survive conversion cleanup."""

import builtins
import json
import subprocess
import sys
import threading
import time
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

    monkeypatch.setattr(
        onyx_recovery,
        "run_logged",
        lambda command, log, stage, timeout, path: run(command, stdout=log, timeout=timeout),
    )
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

    monkeypatch.setattr(
        onyx_recovery,
        "run_logged",
        lambda command, log, stage, timeout, path: run(command, stdout=log, timeout=timeout),
    )
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
    monkeypatch.setattr(onyx_recovery, "PROGRESS_SECONDS", 0.02)
    log_path = tmp_path / "persistent.log"
    with log_path.open("w") as log:
        onyx_recovery.run_logged(
            [
                sys.executable,
                "-c",
                "import time; print('Actual converter diagnostic'); time.sleep(.15)",
            ],
            log,
            "importacao",
            5,
            log_path,
        )
    output = capsys.readouterr().out
    assert "limite de espera 5s" in output
    assert "aguardando ha" in output
    assert "processo terminou; espera" in output
    assert str(log_path) in output
    assert log_path.read_text() == "Actual converter diagnostic\n"
    assert not [t for t in threading.enumerate() if t.name == "onyx-elapsed-feedback"]


def events(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.with_suffix(".tempos.jsonl").read_text().splitlines()]


def test_real_child_exceeding_deadline_is_killed_reaped_and_recorded(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    original = subprocess.Popen
    children: list[subprocess.Popen[str]] = []

    def launch(*args: Any, **kwargs: Any) -> subprocess.Popen[str]:
        child: subprocess.Popen[str] = original(*args, **kwargs)
        children.append(child)
        return child

    monkeypatch.setattr(subprocess, "Popen", launch)
    path = tmp_path / "timeout.log"
    started = time.monotonic()
    with path.open("w") as log, pytest.raises(subprocess.TimeoutExpired):
        onyx_recovery.run_logged(
            [sys.executable, "-c", "import time; time.sleep(60)"], log, "importacao", 0.25, path
        )
    assert time.monotonic() - started < 5
    assert len(children) == 1
    assert children[0].poll() is not None
    result = events(path)[-1]
    assert result["outcome"] == "timeout"
    assert result["pid"] == children[0].pid
    assert result["returncode"] is not None
    assert result["wait_seconds"] >= 0.2


def test_blocked_console_cannot_hold_up_process_supervision_or_inflate_wait(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    original_print = builtins.print
    blocked, release = threading.Event(), threading.Event()

    def console(*args: object, **kwargs: Any) -> None:
        if threading.current_thread().name == "onyx-elapsed-feedback":
            blocked.set()
            release.wait(5)
        original_print(*args, **kwargs)

    monkeypatch.setattr(builtins, "print", console)
    path = tmp_path / "blocked.log"
    try:
        started = time.monotonic()
        with path.open("w") as log:
            onyx_recovery.run_logged([sys.executable, "-c", "pass"], log, "importacao", 2, path)
        assert blocked.is_set()
        assert not release.is_set()
        assert time.monotonic() - started < 3
        result = events(path)[-1]
        assert result["outcome"] == "ok"
        assert result["wait_seconds"] < 2
    finally:
        release.set()
        for reporter in threading.enumerate():
            if reporter.name == "onyx-elapsed-feedback":
                reporter.join(2)


@pytest.mark.parametrize("delayed_launch", [True, False])
def test_launch_delay_is_separate_and_late_success_is_not_reported_as_in_time(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, delayed_launch: bool
) -> None:
    clock = [0.0]

    class Process:
        pid = 12345
        returncode = 0

        def __init__(self, *args: Any, **kwargs: Any) -> None:
            if delayed_launch:
                clock[0] += 731

        def wait(self, timeout: float) -> int:
            clock[0] += 0.9 if delayed_launch else 731
            return 0

        def poll(self) -> int:
            return 0

    monkeypatch.setattr(subprocess, "Popen", Process)
    monkeypatch.setattr(time, "monotonic", lambda: clock[0])
    path = tmp_path / "timing.log"
    with path.open("w") as log:
        if delayed_launch:
            onyx_recovery.run_logged(["fixture"], log, "importacao", 180, path)
        else:
            with pytest.raises(subprocess.TimeoutExpired):
                onyx_recovery.run_logged(["fixture"], log, "importacao", 180, path)
    result = events(path)[-1]
    assert result["launch_seconds"] == (731 if delayed_launch else 0)
    assert result["wait_seconds"] == pytest.approx(0.9 if delayed_launch else 731)
    assert result["outcome"] == ("ok" if delayed_launch else "timeout")


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
