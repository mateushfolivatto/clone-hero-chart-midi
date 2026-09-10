# Architecture decisions — Phase 0

## ADR-001: minimal executable core

Accepted: Python package in src/drumforge, argparse CLI, standard-library runtime.
doctor.py owns environment probes; cli/ only parses arguments and renders results.
pytest, Ruff, mypy and Hatchling are development/build tools, locked by uv.
Only --help, --version and doctor are implemented. No fake generate command.

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

Close the Windows Phase 0 update and its gates first. Then perform a metadata/source
compatibility audit for Windows/Python 3.12 CPU. Do not implement DCF-100 onward
or run transcription until the user starts that subsequent milestone.
