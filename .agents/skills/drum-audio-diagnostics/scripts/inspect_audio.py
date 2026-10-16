# /// script
# requires-python = ">=3.11,<3.13"
# dependencies = ["numpy==2.3.5", "matplotlib==3.10.8"]
# ///
"""Local, bounded spectral diagnostics. Candidates are not classified drum notes."""

from __future__ import annotations

import argparse
import base64
import csv
import hashlib
import html
import json
import math
import os
import shutil
import subprocess
import tempfile
from importlib.metadata import version
from pathlib import Path

# Keep Matplotlib's optional cache out of the user's home and remove it on exit.
_MPL_CACHE = tempfile.TemporaryDirectory(prefix="drumforge-mpl-")
os.environ.setdefault("MPLCONFIGDIR", _MPL_CACHE.name)
os.environ.setdefault("XDG_CACHE_HOME", _MPL_CACHE.name)

import matplotlib  # noqa: E402
import numpy as np  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

RATE = 44_100
N_FFT = 2048
HOP = 256
BANDS = {"low": (40, 200), "mid": (200, 4000), "high": (4000, 16000)}
COLORS = {"low": "#dd7346", "mid": "#328bb5", "high": "#8c56bf"}


def decode(source: Path, ffmpeg: str, start: float, duration: float) -> np.ndarray:
    """Decode stereo so phase-opposed high frequencies cannot cancel in a mono sum."""
    command = [
        ffmpeg,
        "-nostdin",
        "-v",
        "error",
        "-ss",
        str(start),
        "-i",
        str(source),
        "-t",
        str(duration),
        "-map",
        "0:a:0",
        "-vn",
        "-ac",
        "2",
        "-ar",
        str(RATE),
        "-f",
        "f32le",
        "-c:a",
        "pcm_f32le",
        "pipe:1",
    ]
    result = subprocess.run(command, capture_output=True, timeout=120, check=False)
    if result.returncode:
        raise ValueError(result.stderr.decode(errors="replace").strip()[-1000:])
    if len(result.stdout) % 8:
        raise ValueError("FFmpeg returned incomplete stereo float32 samples")
    audio = np.frombuffer(result.stdout, dtype="<f4").reshape(-1, 2)
    if len(audio) < N_FFT or not np.isfinite(audio).all():
        raise ValueError("excerpt must contain at least 47 ms of finite audio samples")
    return audio


def spectrum(audio: np.ndarray) -> np.ndarray:
    """Mean channel power, centered frames, Hann window; FFT in bounded batches."""
    padded = np.pad(audio, ((N_FFT // 2, N_FFT // 2), (0, 0)))
    frames = np.lib.stride_tricks.sliding_window_view(padded, N_FFT, axis=0)[::HOP]
    window = np.hanning(N_FFT)
    batches = []
    for offset in range(0, len(frames), 256):
        transformed = np.fft.rfft(frames[offset : offset + 256] * window, axis=-1)
        batches.append((np.abs(transformed) ** 2).mean(axis=1) / window.sum() ** 2)
    return np.concatenate(batches)


def band_candidates(power: np.ndarray) -> dict[str, dict[str, np.ndarray]]:
    """Positive log spectral changes with a separate local threshold for each band."""
    frequencies = np.fft.rfftfreq(N_FFT, 1 / RATE)
    log_magnitude = np.log1p(1000 * np.sqrt(power))
    change = np.maximum(np.diff(log_magnitude, axis=0, prepend=log_magnitude[:1]), 0)
    # Ignore crop boundaries; their zero padding can create artificial attacks.
    guard = math.ceil(N_FFT / (2 * HOP))
    result = {}
    for label, (low, high) in BANDS.items():
        curve = change[:, (frequencies >= low) & (frequencies < high)].mean(axis=1)
        neighborhoods = np.lib.stride_tricks.sliding_window_view(
            np.pad(curve, (43, 43), mode="edge"), 87
        )
        baseline = np.median(neighborhoods, axis=1)
        mad = np.median(np.abs(neighborhoods - baseline[:, None]), axis=1)
        threshold = baseline + 3 * mad + max(float(curve.max()) * 0.02, 1e-7)
        possible = np.flatnonzero(
            (curve > threshold) & (curve > np.roll(curve, 1)) & (curve >= np.roll(curve, -1))
        )
        possible = possible[(possible >= guard) & (possible < len(curve) - guard)]
        selected: list[int] = []
        # Suppress close peaks only within this band, never across simultaneous bands.
        for index in sorted(possible, key=lambda index: float(curve[index]), reverse=True):
            if all(abs(index - previous) * HOP / RATE >= 0.03 for previous in selected):
                selected.append(int(index))
        result[label] = {
            "flux": curve,
            "threshold": threshold,
            "peaks": np.array(sorted(selected), dtype=int),
        }
    return result


def render(audio, power, bands, start, title, vmax, destination):
    times = start + np.arange(len(power)) * HOP / RATE
    fig, axes = plt.subplots(3, 1, figsize=(14, 8), sharex=True, layout="constrained")
    block_size = max(1, len(audio) // 1800)
    blocks = audio[: len(audio) // block_size * block_size].reshape(-1, block_size, 2)
    envelope_times = start + (np.arange(len(blocks)) + 0.5) * block_size / RATE
    axes[0].fill_between(
        envelope_times, blocks.min(axis=(1, 2)), blocks.max(axis=(1, 2)), color="#328bb5"
    )
    axes[0].set(ylabel="Amplitude", ylim=(-1.05, 1.05), title=title)
    frequencies = np.fft.rfftfreq(N_FFT, 1 / RATE)
    image = axes[1].pcolormesh(
        times,
        frequencies[1:],
        10 * np.log10(np.maximum(power[:, 1:].T, 1e-16)),
        shading="auto",
        cmap="magma",
        vmin=vmax - 80,
        vmax=vmax,
        rasterized=True,
    )
    axes[1].set(yscale="log", ylim=(40, 18000), ylabel="Frequência (Hz)")
    fig.colorbar(image, ax=axes[1], label="dB relativos; escala comum entre arquivos")
    for label, values in bands.items():
        scale = max(float(values["flux"].max()), 1e-12)
        peaks = values["peaks"]
        low, high = BANDS[label]
        axes[2].plot(
            times, values["flux"] / scale, color=COLORS[label], label=f"{label}: {low}–{high} Hz"
        )
        axes[2].plot(
            times, values["threshold"] / scale, color=COLORS[label], linestyle="--", alpha=0.45
        )
        axes[2].scatter(times[peaks], values["flux"][peaks] / scale, color=COLORS[label], s=14)
    axes[2].set(
        xlabel="Tempo no arquivo original (s)", ylabel="Fluxo normalizado por faixa", ylim=(0, 1.5)
    )
    axes[2].legend(loc="upper right")
    axes[2].set_xlim(start, start + len(audio) / RATE)
    for axis in axes:
        axis.grid(alpha=0.15)
    fig.savefig(destination, dpi=130)
    plt.close(fig)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inputs", type=Path, nargs="+", help="Full mix and/or aligned stems")
    parser.add_argument("--start", type=float, default=0)
    parser.add_argument("--duration", type=float, default=30, help="Excerpt length, at most 60 s")
    parser.add_argument("--out", type=Path, required=True, help="New, nonexistent report directory")
    parser.add_argument("--ffmpeg-path", default="ffmpeg")
    args = parser.parse_args(argv)
    if not math.isfinite(args.start) or args.start < 0:
        parser.error("start must be finite and nonnegative")
    if not math.isfinite(args.duration) or not 0 < args.duration <= 60:
        parser.error("duration must be finite, positive and at most 60 seconds")
    if len(args.inputs) > 8:
        parser.error("compare at most eight files per report")
    sources = [path.resolve() for path in args.inputs]
    if any(not path.is_file() for path in sources):
        parser.error("every input must be an existing local audio file")
    executable = shutil.which(args.ffmpeg_path)
    if executable is None:
        parser.error("FFmpeg not found; pass --ffmpeg-path with its executable path")
    out = args.out.resolve()
    if out.exists():
        parser.error("output directory already exists; choose a new directory")
    try:
        clips = [decode(source, executable, args.start, args.duration) for source in sources]
    except (OSError, ValueError, subprocess.TimeoutExpired) as exc:
        parser.error(str(exc))
    powers = [spectrum(audio) for audio in clips]
    vmax = 10 * math.log10(max(max(float(power.max()) for power in powers), 1e-12))
    out.mkdir(parents=True, exist_ok=False)
    report = {
        "schema_version": 1,
        "diagnostic_only": True,
        "start_seconds": args.start,
        "requested_duration_seconds": args.duration,
        "sample_rate_hz": RATE,
        "fft_size": N_FFT,
        "hop_samples": HOP,
        "channel_policy": "mean_channel_power",
        "numpy": version("numpy"),
        "matplotlib": version("matplotlib"),
        "bands_hz": BANDS,
        "files": [],
        "warning": "Spectral candidates are not classified notes or model confidence. "
        "Stems must share the same origin and speed; alignment is not estimated. "
        "The first and last 24 ms are excluded from candidate detection.",
    }
    sections = []
    with (out / "candidates.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(["file_index", "source", "band", "time_seconds", "flux", "threshold"])
        for index, (source, audio, power) in enumerate(zip(sources, clips, powers, strict=True)):
            bands = band_candidates(power)
            png = out / f"{index + 1:02d}-spectrum.png"
            render(audio, power, bands, args.start, source.name, vmax, png)
            for label, values in bands.items():
                for frame in values["peaks"]:
                    writer.writerow(
                        [
                            index + 1,
                            source.name,
                            label,
                            f"{args.start + frame * HOP / RATE:.6f}",
                            f"{values['flux'][frame]:.8f}",
                            f"{values['threshold'][frame]:.8f}",
                        ]
                    )
            report["files"].append(
                {
                    "source": str(source),
                    "decoded_excerpt_sha256": hashlib.sha256(audio).hexdigest(),
                    "decoded_duration_seconds": len(audio) / RATE,
                    "peak_amplitude": float(np.abs(audio).max()),
                    "near_full_scale_sample_fraction": float((np.abs(audio) >= 0.999).mean()),
                    "candidate_counts": {
                        label: len(values["peaks"]) for label, values in bands.items()
                    },
                }
            )
            encoded = base64.b64encode(png.read_bytes()).decode("ascii")
            sections.append(
                f"<h2>{html.escape(source.name)}</h2>"
                f'<img alt="Espectrograma e candidatos espectrais" '
                f'src="data:image/png;base64,{encoded}">'
            )
    (out / "report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    document = """<!doctype html><html lang="pt-BR"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Diagnóstico de bateria</title>
<style>body{font:17px system-ui;max-width:1200px;margin:32px auto;padding:0 20px;
background:#f7f7fa;color:#202536}img{width:100%;height:auto}p{line-height:1.6}</style>
<h1>Diagnóstico espectral de bateria</h1>
<p>Gráficos calculados do áudio fornecido. Os pontos são candidatos de ataque por faixa,
não notas reconhecidas. Graves, médios e agudos contêm vários instrumentos sobrepostos.
Linhas tracejadas: limiar local. Curvas de fluxo normalizadas separadamente;
amplitudes e cores do espectrograma usam escalas comuns entre arquivos.</p>
<p>Compare stems da mesma versão, sem cortar silêncio inicial, alterar velocidade ou
normalizar volumes individualmente. O alinhamento não é corrigido automaticamente.
Nas bordas do recorte, 24 ms ficam fora da detecção. Nenhum áudio é incluído neste relatório.</p>"""
    (out / "report.html").write_text(document + "".join(sections) + "</html>", encoding="utf-8")
    print(json.dumps({"report": str(out / "report.html"), "sources": len(sources)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
