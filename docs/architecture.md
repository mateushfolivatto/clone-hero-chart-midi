# Architecture decisions — Phase 0

## ADR-001: minimal executable core

Accepted: Python package in src/drumforge, argparse CLI, standard-library runtime.
doctor.py owns environment probes; cli/ only parses arguments and renders results.
pytest, Ruff, mypy and Hatchling are development/build tools, locked by uv.
The first Phase 1 slice adds `prepare-audio`; no generate/transcription command
exists yet.

## ADR-004: deterministic FFmpeg audio boundary

Accepted: `audio.prepare` invokes explicit FFmpeg/ffprobe paths with argument
lists and `shell=False`. It probes the first audio stream, normalizes to mono
44.1 kHz PCM s16le WAV, validates the output metadata, and atomically promotes a
temporary file. The cache key includes source bytes and normalization settings;
the source is opened read-only and is never used as an output path.

Use native Windows/Python 3.12 as the primary environment for the entire current
stage: development, tests and future chart generation. The initial Python range
is 3.11–3.12; only 3.12 has been exercised. CPU is the mandatory baseline; CUDA is
optional acceleration. Preserve future Linux/WSL portability without requiring
either. WSL Ubuntu cannot be installed here; docker-desktop must not be used.
No Docker workaround or machine policy changes. See environment.md for the audit.

## ADR-002: replaceable inference

Future flow: audio -> Separator -> Transcriber -> canonical DrumHit[] ->
normalization -> Clone Hero exporter. These boundaries are planned, not implemented.
Transcribers must not know game lanes; exporters must not import ML backends.
Canonical events will preserve raw seconds, instrument, velocity, confidence and
source note. Phase 2 owns their implementation.

Heavy ML dependencies will be opt-in extras or an isolated adapter environment.
Do not declare nonfunctional extras before a reproducible backend pin exists.
Prefer a small direct ADTOF-pytorch spike before the integrated wrapper; MDX23C
remains a separation candidate. Upstream license uncertainties remain explicit.

## ADR-003: eventual MIDI exporter

Choose notes.mid for the first exporter: established tempo events, track names and
Pro Drums conventions; easy independent inspection. .chart is readable and a good
debug/reference format but has distinct note-marker semantics. See format notes.
This decision does not implement Phase 3 or establish actual Clone Hero acceptance.

Keep tempo maps extensible. A constant reference tempo can encode raw seconds
without claiming the song has constant musical tempo. Quantization stays off.

## Next experiment

The Windows/Python 3.12 CPU compatibility audit is complete. Phase 1 should first
normalize input through a native `ffmpeg.exe` boundary and run pinned ADTOF
directly on the full mix with an explicit CPU device. Separation stays behind the
existing interface and is disabled for the smallest experiment. If measured
quality requires it, `mdxnet-infer` 0.1.0 is the preferred next separator spike;
its checkpoint is optional, large and not cleared for redistribution.

The future adapter must validate an allowlisted checkpoint revision and SHA256,
reject missing/unexpected weights, and use `pathlib.Path` plus argument-list
subprocess calls. See phase-1-windows-compatibility.md. Do not implement DCF-100
onward until the user explicitly starts Phase 1.
