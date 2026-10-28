# Drum Chart Forge

Local-first tooling to turn legally obtained music into Clone Hero Expert Pro
Drums charts. **Phase 1 is in progress:** environment diagnostics, deterministic
audio preparation, raw MIDI transcription and MIDI diagnostics are implemented.
Chart export is a future phase. No music or model weights are included.

Para a playlist MixDrumRock, veja [baixar os 254 charts novos](song-library/CONTINUACAO.md)
e o [relatório das 744 entradas](song-library/reports/cobertura.csv). Essa biblioteca
de charts existentes é independente da transcrição de MP3.

Para ampliar a coleção de Linkin Park, use [os novos lotes e a comparação com
sua biblioteca instalada](song-library/LINKIN-PARK.md). Given Up já está no lote 02.

## Setup

Python 3.11–3.12 and [uv](https://docs.astral.sh/uv/getting-started/installation/).
Native Windows is the primary environment for development, tests and future chart
generation in this stage. Python 3.12.0 is validated here. CPU is the minimum target;
CUDA/GPU is optional acceleration. Linux/WSL may be supported later but is never
required. This college PC cannot install WSL Ubuntu: do not use docker-desktop,
Docker workarounds or administrative policy changes. See [environment](docs/environment.md).

```text
uv --cache-dir .uv-cache sync --locked
uv --cache-dir .uv-cache run --locked drumforge --help
uv --cache-dir .uv-cache run --locked drumforge doctor
uv --cache-dir .uv-cache run --locked drumforge doctor --json
uv --cache-dir .uv-cache run --locked drumforge prepare-audio INPUT --work-dir WORK \
  --ffmpeg-path PATH_TO_FFMPEG --ffprobe-path PATH_TO_FFPROBE
uv --cache-dir .uv-cache run --locked drumforge transcribe WORK/audio.wav \
  --midi-out WORK/raw.mid --weights PATH_TO_ALLOWLISTED_WEIGHTS \
  --backend-python PATH_TO_ADTOF_PYTHON --skip-separation
uv --cache-dir .uv-cache run --locked drumforge inspect-midi WORK/raw.mid \
  --out output/midi-diagnostics
```

This checkout has uv 0.12.13 in ignored `.tools/bin/uv.exe`; on this Windows host
use `.\.tools\bin\uv.exe` in place of `uv`. To reproduce that local tool install:
`py -3.12 -m pip install --target .tools uv==0.12.13`.
The committed lock pins development dependencies; the core has no runtime packages.
Raw MIDI inspection uses the locked optional `diagnostics` extra (Mido 1.3.3),
also included in development dependencies. For a runtime-only installation use
`uv --cache-dir .uv-cache sync --locked --no-dev --extra diagnostics`.

Doctor distinguishes Windows, native Linux and WSL; it reports CPU and CUDA as
separate checks. Missing CUDA is not an error. It also checks RAM, ffmpeg, PyTorch,
optional backend discovery and write access. Use `--write-dir PATH` to probe an
existing output directory, and `--model-path PATH` for a local checkpoint presence
check. No models are downloaded. Missing optional components produce warnings;
write failures produce exit 1. ML inference is not verified by this command.

`prepare-audio` probes the first audio stream, preserves the input unchanged, and
creates a cached mono 44.1 kHz 16-bit PCM WAV. On Windows, pass explicit paths to
portable `ffmpeg.exe` and `ffprobe.exe`; paths containing spaces are supported.
Its JSON result includes metadata, cache identity and cache-hit status.

`transcribe` runs the optional pinned ADTOF backend in an isolated Python process
on CPU. It refuses missing/modified checkpoints and existing MIDI outputs. The
backend environment and weights are intentionally not installed or downloaded by
the core project; consult the compatibility report before local research use.

Per-instrument `--thresholds` use **BD SD HH TT CY** (bass drum, snare, hi-hat,
toms, cymbals). The adapter translates this to the pinned backend's different
order; lowering the third value now targets hi-hat, not toms. Previous explicit
vectors need reassessment if they were tuned around the old swapped behavior.

For missing hi-hats, use the project skill `$drum-audio-diagnostics`. It supplies
a local spectrogram/report script and an experiment comparing full mix, drums
and Moises component stems. See [the diagnostic guide](docs/drum-audio-diagnostics.md).
Plots do not classify every note; real-song accuracy still needs measurement.

Use that skill for every music-to-chart task. `inspect-midi` writes `report.json`
and `events.csv` with GM drum counts, onset seconds and stored velocities, retaining
simultaneous notes and tempo changes. It reads raw GM percussion on MIDI channel
10, not an existing Clone Hero `PART DRUMS` chart, and refuses existing output
folders. See [Phase 1 MIDI diagnostics](docs/phase-1-midi-diagnostics.md).

The skill also supports [learning from five existing chart/audio pairs](docs/five-song-chart-reference.md).
That real-song experiment produced a reusable spectral profile and chart-overlaid
spectrograms, with whole-song holdouts. Simple rules improved kick/snare chart
agreement but did not improve the hi-hat proxy; the ADTOF baseline is unchanged.
The [CoD/Avenged Sevenfold follow-up](docs/cod-a7x-heldout.md) tests that frozen
profile on five other songs, including a .chart reference and packages without
drum stems. It records per-song failures and does not recalibrate on test data.
The [Faint/Crawling study](docs/linkin-park-hihat.md) examines timekeeping hi-hat
and fixes disco-flip interpretation in Pro reference charts. It retains original
note data and compares mix/drums using the same frozen detector profile.
The [component-source follow-up](docs/stem-component-study.md) audits silent
stems, compares explicit kick/snare/kit sources and adds chart-free component
candidates. It also inspects a small free StemGMD/LarsNet author demonstration;
local model inference and game-chart export remain pending.
The [64-song survey](docs/broad-song-survey.md) checks new artist-balanced song
excerpts with frozen rules, paired source comparisons, song-level uncertainty
and negative controls. It retains failures and documents which earlier patterns
generalized, without claiming instrument recognition from chart agreement.

## Project navigation

- [Baixar o lote de 12 músicas no Windows](song-library/BAIXAR.md): recuperação
  direta das fontes, independente dos arquivos temporários da nuvem.
- [Biblioteca MixDrumRock](song-library/README.md): exportação da playlist do
  Qobuz para CSV/Excel e planejamento de charts com bateria para Clone Hero.
- [CONTEXT.md](CONTEXT.md): mission and decisions.
- [BACKLOG.md](BACKLOG.md): single authoritative task list.
- [lessons.md](lessons.md): reread alongside the backlog every session.
- [Architecture](docs/architecture.md), [format notes](docs/clonehero-format-notes.md),
  [research](docs/research-notes.md), [Windows Phase 1 compatibility matrix](docs/phase-1-windows-compatibility.md),
  [license register](docs/dependency-licenses.md).
- [Quality gates](docs/testing.md) and [contribution rules](CONTRIBUTING.md).

Keep test music in ignored `audio/` or `fixtures/private/`. Never commit songs or
model weights. The existing repository name remains clone-hero-chart-midi;
drum-chart-forge is the Python distribution name and drumforge is the CLI.

The pre-Phase 1 audit found a viable native CPU research path: portable FFmpeg
normalization plus pinned ADTOF-pytorch/PyTorch CPU, initially without source
separation. A strict CPU-only ADTOF transcription command is implemented; private-song
validation is still pending. The ADTOF wrapper and model
terms are not cleared for redistribution; consult the compatibility matrix before
installing the optional ML stack.
