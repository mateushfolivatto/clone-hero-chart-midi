# Architecture decisions — Phase 0

## ADR-001: minimal executable core

Accepted: Python package in src/drumforge, argparse CLI, standard-library runtime.
doctor.py owns environment probes; cli/ only parses arguments and renders results.
pytest, Ruff, mypy and Hatchling are development/build tools, locked by uv.
Only --help, --version and doctor are implemented. No fake generate command.

Use the available native Windows Python 3.12 for bootstrap. The project targets
Python 3.11–3.12 initially; only 3.12 is exercised here. WSL Ubuntu remains a
candidate for the ML spike, not a prerequisite for the lightweight CLI.

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

Verify Phase 0 gates first (see BACKLOG.md). Then, in a later
session, audit a pinned ADTOF checkpoint and dependencies in an isolated CPU
environment; disclose artifact size/source before download, measure a short legal
audio segment and inspect raw MIDI event timestamps. Do not attempt the entire
song before establishing the smallest reproducible inference run.
