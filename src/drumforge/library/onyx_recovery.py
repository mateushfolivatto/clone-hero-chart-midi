"""Pinned portable Onyx conversion, also usable beside the standalone downloader."""

from __future__ import annotations

import hashlib
import importlib
import json
import subprocess
import sys
import tempfile
import threading
import time
import zipfile
from datetime import UTC, datetime
from functools import cache
from pathlib import Path
from typing import Any, TextIO

recovery = importlib.import_module(
    "drumforge.library.recover_pilot" if __package__ else "recover_pilot"
)
ONYX_URL = (
    "https://github.com/mtolly/onyx/releases/download/20261016/"
    "onyx-command-line-20261016-windows-x64.zip"
)
ONYX_SHA256 = "d6131d67cef8d442590a618bcc2d582f5332fd0aa7077547a02f02d34958288c"
PROGRESS_SECONDS = 15.0
REPORT_JOIN_SECONDS = 0.05


def timing_event(path: Path, stage: str, event: str, **values: Any) -> None:
    entry = {
        "utc": datetime.now(UTC).isoformat(),
        "stage": stage,
        "event": event,
        **values,
    }
    with path.with_suffix(".tempos.jsonl").open("a", encoding="utf-8") as file:
        file.write(json.dumps(entry, ensure_ascii=False) + "\n")


def run_logged(command: list[str], log: TextIO, stage: str, timeout: float, path: Path) -> None:
    timing_event(path, stage, "launch_started", timeout_seconds=timeout)
    launch_started = time.monotonic()
    try:
        process = subprocess.Popen(
            command, stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT
        )
    except OSError as exc:
        timing_event(path, stage, "launch_failed", error=str(exc))
        raise
    started = time.monotonic()
    launch_seconds = started - launch_started
    finished = threading.Event()
    elapsed = 0.0
    outcome = "error"

    def report() -> None:
        print(
            f"  Onyx {stage}: processo {process.pid}; abertura {launch_seconds:.1f}s; "
            f"limite de espera {timeout:g}s. Log: {path}",
            flush=True,
        )
        while not finished.wait(PROGRESS_SECONDS):
            waiting = int(time.monotonic() - started)
            print(f"  Onyx {stage}: aguardando ha {waiting}s (limite {timeout:g}s)...", flush=True)
        if outcome == "ok":
            print(f"  Onyx {stage}: processo terminou; espera {elapsed:.1f}s.", flush=True)

    reporter = threading.Thread(target=report, name="onyx-elapsed-feedback", daemon=True)
    try:
        timing_event(path, stage, "process_started", pid=process.pid, launch_seconds=launch_seconds)
        reporter.start()
        deadline = started + timeout
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise subprocess.TimeoutExpired(command, timeout)
            try:
                returncode = process.wait(timeout=min(0.5, remaining))
            except subprocess.TimeoutExpired:
                continue
            if time.monotonic() > deadline:
                raise subprocess.TimeoutExpired(command, timeout)
            if returncode:
                raise subprocess.CalledProcessError(returncode, command)
            outcome = "ok"
            break
    except subprocess.TimeoutExpired:
        outcome = "timeout"
        raise
    except KeyboardInterrupt:
        outcome = "interrupted"
        raise
    finally:
        elapsed = time.monotonic() - started
        try:
            if process.poll() is None:
                process.kill()
                process.wait(timeout=5)
        finally:
            try:
                timing_event(
                    path,
                    stage,
                    "finished",
                    pid=process.pid,
                    outcome=outcome,
                    launch_seconds=launch_seconds,
                    wait_seconds=elapsed,
                    cleanup_seconds=time.monotonic() - started - elapsed,
                    returncode=process.returncode,
                )
            finally:
                finished.set()
                if reporter.ident is not None:
                    reporter.join(timeout=REPORT_JOIN_SECONDS)


def build(
    executable: Path,
    source: Path,
    project: Path,
    target: Path,
    *,
    log_path: Path | None = None,
) -> None:
    # The pinned Windows onyx-cli target has no -threaded/-rtsopts options.
    # Linux AppRun uses the threaded GUI binary, whose default is all CPUs.
    runtime = [] if sys.platform == "win32" else ["+RTS", "-N2", "-RTS"]
    log_path = log_path or project.with_suffix(".log")
    stage = "importacao"
    try:
        with log_path.open("w", encoding="utf-8") as log:
            run_logged(
                [str(executable), "import", str(source), "--to", str(project), *runtime],
                log,
                stage,
                180,
                log_path,
            )
            yaml = project / "song.yml"
            content = yaml.read_text(encoding="utf-8")
            if "targets:\n" not in content:
                raise ValueError("Onyx nao criou um projeto com destinos")
            content = content.replace("targets:\n", "targets:\n  clonehero:\n    game: ps\n", 1)
            yaml.write_text(content, encoding="utf-8", newline="\n")
            stage = "exportacao"
            run_logged(
                [
                    str(executable),
                    "build",
                    str(yaml),
                    "--target",
                    "clonehero",
                    "--to",
                    str(target),
                    *runtime,
                ],
                log,
                stage,
                900,
                log_path,
            )
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        detail = str(exc)
        if isinstance(exc, subprocess.CalledProcessError):
            detail = f"codigo de saida {exc.returncode}"
        elif isinstance(exc, subprocess.TimeoutExpired):
            detail = f"tempo limite de {exc.timeout} segundos"
        tail = ""
        if log_path.is_file():
            with log_path.open("rb") as log:
                log.seek(max(0, log_path.stat().st_size - 4096))
                tail = log.read().decode("utf-8", errors="replace").strip()
        raise ValueError(
            f"Onyx falhou na {stage}: {detail}. Log: {log_path}" + (f"\n{tail}" if tail else "")
        ) from exc


@cache
def install(root: Path) -> Path:
    if sys.platform != "win32":
        raise ValueError("Os lotes Onyx deste baixador requerem Windows 10/11 x64")
    archive = recovery.download_archive(
        {
            "file_id": "onyx-20261016-windows",
            "download_url": ONYX_URL,
            "source_url": "https://github.com/mtolly/onyx/releases/tag/20261016",
            "archive_bytes": 63005066,
            "archive_sha256": ONYX_SHA256,
        },
        root / "Ferramentas",
    )
    installation = root / "Ferramentas" / "Onyx-20261016"
    with zipfile.ZipFile(archive) as package:
        for info in package.infolist():
            relative = recovery.relative_path(info.filename)
            if info.is_dir():
                continue
            path = installation.joinpath(*relative.parts)
            content = package.read(info)
            if path.exists():
                if path.read_bytes() != content:
                    raise ValueError("Ferramenta local alterada; preservada")
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(content)
    matches = list(installation.rglob("onyx.exe"))
    if len(matches) != 1:
        raise ValueError("Executavel do Onyx ausente na distribuicao oficial")
    return matches[0]


def prepare(song: dict[str, Any], source: Path, destination: Path, root: Path) -> dict[str, Any]:
    # Ogg serial numbers vary between conversions. Pin source/tool/MIDI and record
    # local output hashes for resumption instead of pretending cloud hashes match.
    receipt_path = root / "Verificacoes" / (song["file_id"] + ".json")
    if destination.exists():
        local = json.loads(receipt_path.read_text(encoding="utf-8"))
        if local["archive_sha256"] != song["archive_sha256"] or local["converter"] != ONYX_SHA256:
            raise ValueError("Verificacao local pertence a outra fonte ou conversor")
        recovery.verify_song(local, destination)
        return dict(local)
    executable = install(root)
    destination.parent.mkdir(parents=True, exist_ok=True)
    logs = root / "Logs" / "Onyx"
    logs.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        prefix=song["file_id"] + "-", suffix=".log", dir=logs, delete=False
    ) as log:
        log_path = Path(log.name)
    with tempfile.TemporaryDirectory(prefix="convertendo-", dir=destination.parent) as temporary:
        workspace = Path(temporary)
        target = workspace / "clonehero.zip"
        build(executable, source, workspace / "projeto", target, log_path=log_path)
        folder = workspace / "musica"
        folder.mkdir()
        assets = []
        with zipfile.ZipFile(target) as archive:
            by_name = {}
            for name in archive.namelist():
                path = recovery.relative_path(name)
                if not name.endswith("/"):
                    if path.name.casefold() in by_name:
                        raise ValueError("Conversao criou nomes repetidos")
                    by_name[path.name.casefold()] = name
            for asset in song["files"]:
                content = archive.read(by_name[asset["name"].casefold()])
                if asset["name"] == "song.ini" and song.get("set_pro_drums"):
                    content = recovery.patched_config(content)
                if asset["name"] == "notes.mid":
                    if hashlib.sha256(content).hexdigest() != asset["sha256"]:
                        raise ValueError("O MIDI convertido difere do MIDI inspecionado na nuvem")
                if Path(asset["name"]).suffix.lower() == ".ogg" and not content.startswith(b"OggS"):
                    raise ValueError("Conversao nao criou o audio Ogg esperado")
                (folder / asset["name"]).write_bytes(content)
                assets.append({**asset, "sha256": hashlib.sha256(content).hexdigest()})
        local = {
            **song,
            "files": assets,
            "converter": ONYX_SHA256,
            "output_hash_scope": "local conversion; source/tool/MIDI pinned",
        }
        recovery.verify_song(local, folder)
        receipt_path.parent.mkdir(parents=True, exist_ok=True)
        receipt_path.write_text(json.dumps(local, ensure_ascii=False, indent=2), encoding="utf-8")
        if destination.exists():
            raise FileExistsError("Destino apareceu durante a conversao; preservado")
        folder.rename(destination)
        return local
