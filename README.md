# Drum Chart Forge

Local-first tooling to turn legally obtained music into Clone Hero Expert Pro
Drums charts. **Phase 0 bootstrap only:** environment diagnostics work; transcription
and chart generation are future milestones. No music or model weights are included.

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
```

This checkout has uv 0.12.13 in ignored `.tools/bin/uv.exe`; on this Windows host
use `.\.tools\bin\uv.exe` in place of `uv`. To reproduce that local tool install:
`py -3.12 -m pip install --target .tools uv==0.12.13`.
The committed lock pins development dependencies; the core has no runtime packages.

Doctor distinguishes Windows, native Linux and WSL; it reports CPU and CUDA as
separate checks. Missing CUDA is not an error. It also checks RAM, ffmpeg, PyTorch,
optional backend discovery and write access. Use `--write-dir PATH` to probe an
existing output directory, and `--model-path PATH` for a local checkpoint presence
check. No models are downloaded. Missing optional components produce warnings;
write failures produce exit 1. ML inference is not verified by this command.

## Project navigation

- [CONTEXT.md](CONTEXT.md): mission and decisions.
- [BACKLOG.md](BACKLOG.md): single authoritative task list.
- [lessons.md](lessons.md): reread alongside the backlog every session.
- [Architecture](docs/architecture.md), [format notes](docs/clonehero-format-notes.md),
  [research](docs/research-notes.md), [license register](docs/dependency-licenses.md).
- [Quality gates](docs/testing.md) and [contribution rules](CONTRIBUTING.md).

Keep test music in ignored `audio/` or `fixtures/private/`. Never commit songs or
model weights. The existing repository name remains clone-hero-chart-midi;
drum-chart-forge is the Python distribution name and drumforge is the CLI.
