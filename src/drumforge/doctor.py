"""Bounded diagnostics; never installs packages or downloads model weights."""

import ctypes
import importlib.util
import json
import os
import platform
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Literal, TypedDict


class Check(TypedDict):
    name: str
    status: Literal["ok", "warning", "error"]
    detail: str


class Report(TypedDict):
    schema_version: int
    checks: list[Check]


def is_wsl() -> bool:
    return platform.system() == "Linux" and (
        "microsoft" in platform.release().lower() or bool(os.environ.get("WSL_INTEROP"))
    )


def environment_name() -> str:
    """Distinguish WSL from native Linux without invoking wsl.exe."""
    return "WSL (Linux on Windows)" if is_wsl() else platform.system()


def total_ram_bytes() -> int | None:
    """Return physical memory without user, host, serial or network identifiers."""
    try:
        if sys.platform == "win32":

            class MemoryStatus(ctypes.Structure):
                _fields_ = [
                    ("length", ctypes.c_ulong),
                    ("load", ctypes.c_ulong),
                    ("total", ctypes.c_ulonglong),
                    ("available", ctypes.c_ulonglong),
                    ("page_total", ctypes.c_ulonglong),
                    ("page_available", ctypes.c_ulonglong),
                    ("virtual_total", ctypes.c_ulonglong),
                    ("virtual_available", ctypes.c_ulonglong),
                    ("extended_available", ctypes.c_ulonglong),
                ]

            memory = MemoryStatus()
            memory.length = ctypes.sizeof(memory)
            if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(memory)):
                return int(memory.total)
            return None
        return int(os.sysconf("SC_PAGE_SIZE")) * int(os.sysconf("SC_PHYS_PAGES"))
    except (AttributeError, OSError, ValueError):
        return None


def command_version(name: str) -> Check:
    executable = shutil.which(name)
    if executable is None:
        return {"name": name, "status": "warning", "detail": "not found on PATH (optional)"}
    try:
        result = subprocess.run(
            [executable, "-version"],
            capture_output=True,
            text=True,
            timeout=10,
            errors="replace",
            check=False,
        )
        lines = (result.stdout or result.stderr).splitlines()
        return {
            "name": name,
            "status": "ok" if result.returncode == 0 and lines else "warning",
            "detail": lines[0] if lines else "version command returned no output",
        }
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"name": name, "status": "warning", "detail": type(exc).__name__}


def torch_checks() -> list[Check]:
    # A subprocess isolates broken native imports and applies a finite timeout.
    script = (
        "import json, torch; "
        "print(json.dumps({'version': str(torch.__version__), "
        "'cuda_available': bool(torch.cuda.is_available())}))"
    )
    try:
        result = subprocess.run(
            [sys.executable, "-c", script],
            capture_output=True,
            text=True,
            timeout=20,
            errors="replace",
            check=False,
        )
        if result.returncode != 0:
            detail = f"PyTorch missing or import failed (exit {result.returncode})"
        else:
            data = json.loads(result.stdout.strip())
            if not isinstance(data["cuda_available"], bool):
                raise ValueError("invalid CUDA probe result")
            cuda = "available" if data["cuda_available"] else "unavailable"
            return [
                {"name": "torch", "status": "ok", "detail": f"{data['version']}; CPU backend"},
                {"name": "cuda", "status": "ok", "detail": f"{cuda}; optional acceleration"},
            ]
    except (OSError, subprocess.TimeoutExpired, ValueError, KeyError, TypeError) as exc:
        detail = f"PyTorch probe failed: {type(exc).__name__}"
    return [
        {"name": "torch", "status": "warning", "detail": detail},
        {
            "name": "cuda",
            "status": "ok",
            "detail": (
                "unavailable to this runtime; PyTorch probe failed; hardware unverified; optional"
            ),
        },
    ]


def write_check(directory: Path) -> Check:
    try:
        with tempfile.TemporaryFile(dir=directory) as temporary:
            temporary.write(b"drumforge probe")
            temporary.flush()
        return {"name": "write", "status": "ok", "detail": "target directory is writable"}
    except OSError as exc:
        return {"name": "write", "status": "error", "detail": type(exc).__name__}


def diagnose(directory: Path, model_path: Path | None = None) -> Report:
    ram = total_ram_bytes()
    checks: list[Check] = [
        {"name": "python", "status": "ok", "detail": platform.python_version()},
        {"name": "platform", "status": "ok", "detail": environment_name()},
        {
            "name": "cpu",
            "status": "ok",
            "detail": f"available; minimum execution target; logical processors: {os.cpu_count()}",
        },
        {
            "name": "ram",
            "status": "ok" if ram else "warning",
            "detail": f"physical GiB: {ram / 2**30:.1f}" if ram else "unavailable",
        },
        command_version("ffmpeg"),
        *torch_checks(),
        write_check(directory),
    ]
    for name in ("adtof_pytorch", "mdx23c"):
        try:
            present = importlib.util.find_spec(name) is not None
        except (ImportError, ValueError):
            present = False
        checks.append(
            {
                "name": name,
                "status": "warning",
                "detail": "discoverable; inference not verified" if present else "not installed",
            }
        )
    try:
        available = (
            model_path is not None and model_path.is_file() and model_path.stat().st_size > 0
        )
    except OSError:
        available = False
    checks.append(
        {
            "name": "model",
            "status": "warning",
            "detail": "local nonempty file; compatibility/checksum unverified"
            if available
            else "no usable local checkpoint supplied; no download attempted",
        }
    )
    return {"schema_version": 1, "checks": checks}
