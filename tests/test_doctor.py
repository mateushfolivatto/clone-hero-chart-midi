import json
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from drumforge.doctor import command_version, environment_name, is_wsl, torch_checks, write_check


def test_help_runs_without_ml() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "drumforge", "--help"], capture_output=True, text=True, check=False
    )
    assert result.returncode == 0
    assert "doctor" in result.stdout


def test_doctor_json_and_cleanup(tmp_path: Path) -> None:
    result = subprocess.run(
        [sys.executable, "-m", "drumforge", "doctor", "--json", "--write-dir", str(tmp_path)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    report = json.loads(result.stdout)
    assert report["schema_version"] == 1
    assert {c["name"] for c in report["checks"]} >= {
        "python",
        "platform",
        "cpu",
        "cuda",
        "ffmpeg",
        "torch",
        "model",
        "write",
    }
    assert list(tmp_path.iterdir()) == []


def test_bad_write_target_fails(tmp_path: Path) -> None:
    assert write_check(tmp_path / "missing")["status"] == "error"
    result = subprocess.run(
        [sys.executable, "-m", "drumforge", "doctor", "--write-dir", str(tmp_path / "missing")],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 1


def test_missing_ffmpeg_is_optional() -> None:
    with patch("drumforge.doctor.shutil.which", return_value=None):
        assert command_version("ffmpeg")["status"] == "warning"


def test_ffmpeg_timeout_is_warning() -> None:
    with (
        patch("drumforge.doctor.shutil.which", return_value="ffmpeg"),
        patch(
            "drumforge.doctor.subprocess.run", side_effect=subprocess.TimeoutExpired("ffmpeg", 10)
        ),
    ):
        assert command_version("ffmpeg")["detail"] == "TimeoutExpired"


def test_broken_torch_is_warning() -> None:
    with patch("drumforge.doctor.subprocess.run", return_value=subprocess.CompletedProcess([], 1)):
        checks = torch_checks()
        assert checks[0]["status"] == "warning"
        assert checks[1]["status"] == "ok"
        assert "hardware unverified" in checks[1]["detail"]


@pytest.mark.parametrize("available", [True, False])
def test_cuda_detection(available: bool) -> None:
    output = json.dumps({"version": "test", "cuda_available": available})
    with patch(
        "drumforge.doctor.subprocess.run",
        return_value=subprocess.CompletedProcess([], 0, stdout=output),
    ):
        checks = torch_checks()
        assert all(check["status"] == "ok" for check in checks)
        assert checks[1]["detail"].startswith("available;" if available else "unavailable;")


def test_wsl_requires_linux() -> None:
    with (
        patch("drumforge.doctor.platform.system", return_value="Linux"),
        patch("drumforge.doctor.platform.release", return_value="5.15-microsoft-standard-WSL2"),
    ):
        assert is_wsl()
    with patch("drumforge.doctor.platform.system", return_value="Windows"):
        assert not is_wsl()


@pytest.mark.parametrize(
    ("system", "release", "expected"),
    [
        ("Windows", "10", "Windows"),
        ("Linux", "6.8", "Linux"),
        ("Linux", "5.15-microsoft-standard-WSL2", "WSL (Linux on Windows)"),
    ],
)
def test_environment_labels(system: str, release: str, expected: str) -> None:
    with (
        patch("drumforge.doctor.platform.system", return_value=system),
        patch("drumforge.doctor.platform.release", return_value=release),
        patch.dict("os.environ", {}, clear=True),
    ):
        assert environment_name() == expected


def test_windows_ignores_stale_wsl_environment() -> None:
    with (
        patch("drumforge.doctor.platform.system", return_value="Windows"),
        patch.dict("os.environ", {"WSL_INTEROP": "stale"}),
    ):
        assert environment_name() == "Windows"


def test_ffmpeg_exe_path_with_spaces() -> None:
    executable = str(Path("C:/Program Files/ffmpeg/bin/ffmpeg.exe"))
    with (
        patch("drumforge.doctor.shutil.which", return_value=executable),
        patch(
            "drumforge.doctor.subprocess.run",
            return_value=subprocess.CompletedProcess([], 0, stdout="ffmpeg version test\n"),
        ) as run,
    ):
        assert command_version("ffmpeg")["status"] == "ok"
        assert run.call_args.args[0] == [executable, "-version"]
        assert not run.call_args.kwargs.get("shell", False)


def test_torch_timeout_does_not_make_cuda_required() -> None:
    with patch(
        "drumforge.doctor.subprocess.run", side_effect=subprocess.TimeoutExpired("python", 20)
    ):
        checks = torch_checks()
        assert checks[0]["status"] == "warning"
        assert checks[1]["status"] == "ok"
