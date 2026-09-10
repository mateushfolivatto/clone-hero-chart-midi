import json
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

from drumforge.doctor import command_version, is_wsl, torch_check, write_check


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
    assert {c["name"] for c in report["checks"]} >= {"python", "ffmpeg", "torch", "model", "write"}
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
        assert torch_check()["status"] == "warning"


def test_cuda_detection() -> None:
    output = json.dumps({"version": "test", "cuda_available": True})
    with patch(
        "drumforge.doctor.subprocess.run",
        return_value=subprocess.CompletedProcess([], 0, stdout=output),
    ):
        assert "CUDA available: True" in torch_check()["detail"]


def test_wsl_requires_linux() -> None:
    with (
        patch("drumforge.doctor.platform.system", return_value="Linux"),
        patch("drumforge.doctor.platform.release", return_value="5.15-microsoft-standard-WSL2"),
    ):
        assert is_wsl()
    with patch("drumforge.doctor.platform.system", return_value="Windows"):
        assert not is_wsl()
