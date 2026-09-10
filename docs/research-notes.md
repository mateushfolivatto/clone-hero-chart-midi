# Research notes — 2026-09-10

## Verified external facts

- [ADTOF-pytorch metadata](https://github.com/xavriley/ADTOF-pytorch/blob/main/pyproject.toml):
  Python >=3.9; unpinned torch/librosa/pretty_midi/numpy dependencies. README exposes
  adtof CLI and transcribe_to_midi API, with bundled converted weights. Small
  repository history (5 commits observed) is not evidence of supported releases.
- [ADTOF Plus metadata](https://github.com/xavriley/adtof_plus_drum_transcription/blob/main/pyproject.toml):
  Python >=3.8 declared, Git dependencies without commit pins, Essentia required.
  Placeholder project metadata and 2 observed commits indicate an early prototype.
- [MDX23C adapter](https://github.com/xavriley/mdx23c-drum-separation): Python >=3.8,
  torch >=2.0.1; CLI and demix_audio/load_model API. Cache introspection is documented,
  but checkpoint acquisition and terms need a source-code audit. It is an alpha
  candidate, not locally proven. The [ZFTurbo framework](https://github.com/ZFTurbo/Music-Source-Separation-Training)
  offers MDX23C inference as an alternative with a larger history; local CPU runtime
  and checkpoint compatibility have not been measured.
- [midi2clonehero](https://github.com/apvilkko/midi2clonehero): MIT identified by
  repository license panel, small history, GM-to-Expert-Pro .chart converter.
  Supports a cymbal flip policy and expects type-0 MIDI with tempo/meter events.

## Compatibility assessment

Bootstrap is tested on installed Python 3.12.0, native Windows. Python >=3.11,<3.13
is the initial project range. Upstream lower-bound declarations do not establish
that every transitive dependency has Windows/3.12 wheels. Original ADTOF reports
testing Python 3.10 on macOS. The integrated wrapper's Essentia and transitive
audio stack require wheel/platform/license investigation before installation.
The earlier WSL fallback proposal is superseded by the user's college-PC constraint.
Use Windows/Python 3.12 CPU. Report incompatible backends explicitly; do not use
Docker, install WSL Ubuntu or change administrative policies to hide incompatibility.

## Decisions

Use a standard-library core and optional ML adapter environments. No upstream code
vendored. Keep MIDI export independent of transcription. See architecture.md and
dependency-licenses.md for the decisions and remaining license constraints.

## Unresolved questions and hypotheses

- Direct ADTOF on a short full mix may establish a baseline before separation;
  quality and runtime are hypotheses, not measured results.
- ADTOF-pytorch code grant and individual converted-checkpoint terms remain unresolved.
- Immutable checkpoint revisions and SHA256 remain prerequisites for the later
  installation spike. Size/cache research is documented below; no weight downloaded.
- No ffmpeg, torch or game integration was installed/tested during research.

## Environment audit and failure record

Initial repository: clean main tracking origin/main; remote name clone-hero-chart-midi,
not the suggested drum-chart-forge. Reuse existing history and remote. Server-side
visibility/default branch were not independently queried; origin/HEAD points to main.
Uploaded context/backlog names had numbered suffixes and were normalized intact.
Git 2.47.1.windows.2; PowerShell 7.4.13; Windows 10 build 19045.
Host audit: Python 3.12.0, 4 logical processors, 17,036,513,280 RAM bytes, Intel HD 630.
No NVIDIA device observed; PyTorch CUDA capability remains unavailable without torch.
WSL default version 2 with docker-desktop only; current session is not WSL.

Sandbox `py --list-paths` said `No installed Pythons found!`; WSL and CIM returned
access denied (WSL E_ACCESSDENIED). Approved host audit found the installed runtime.
Cause: sandbox access, not proof of missing software. Minimal workaround: approved
read-only host audit, then explicit Python path. No second Python installed.
uv default cache creation failed with os error 5 under the user profile. Repeated
with approval and repository-local .uv-cache. uv 0.12.13 was installed to ignored
.tools through pip (17.7 MB wheel). ffmpeg and nvidia-smi were not on PATH.

uv sync initially failed fetching PyPI after three retries: socket permissions,
os error 10013. Approved retry succeeded; no dependency workaround was necessary.
GitHub tree API returned rate-limit exceeded. Reading small raw source files and
HEAD metadata worked without authentication or downloading model contents.

## Checkpoint size/cache audit (DCF-027)

Inspected [ADTOF package entry point](https://github.com/xavriley/ADTOF-pytorch/blob/main/src/adtof_pytorch/__init__.py)
and [MDX model hub source](https://github.com/xavriley/mdx23c-drum-separation/blob/main/mdx23c/model_hub.py).

| Checkpoint | Expected transfer | Upstream location / cache |
| --- | --- | --- |
| adtof_frame_rnn_pytorch_weights.pth | 3,617,805 bytes (3.45 MiB), HTTP HEAD Content-Length on 2026-09-10 | ADTOF-pytorch src/adtof_pytorch/data; installed package data, not a separate runtime downloader |
| model_mdx23c_ep_168_sdr_7.0207.ckpt | Approximately 500 MB according to downloader warning; exact size unverified | Hugging Face xavriley/source_separation_mirror; config_musdb18_mdx23c.yaml.1 |
| drumsep_5stems_mdx23c_jarredou.ckpt | Approximately 500 MB according to downloader warning; exact size unverified | Same mirror; config_mdx23c_drumsep2025.yaml |

MDX cache is XDG_CACHE_HOME/mdx23c_models or ~/.cache/mdx23c_models. Downloads use
Hugging Face cache there and are copied into kit_from_mix/ or stems_from_kit/;
disk use can exceed transfer size because of copies. Its downloader does not pin
a revision. Disclose/check actual sizes and pin revisions before use. The integrated
wrapper depends on these components and inherits their model footprint.

Critical source finding: ADTOF transcribe_to_midi defaults to CUDA with CPU fallback,
but skips weight loading when the file does not exist, proceeding with initialized
weights. Its return_activations=True branch also differs from the Path annotation.
Future adapter must require a verified checkpoint, explicitly choose CPU, inspect
weight compatibility and test output semantics. Do not confuse this source audit
with a successful local ML installation or validated inference quality.
