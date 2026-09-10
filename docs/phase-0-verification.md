# Phase 0 verification — 2026-09-10

Environment: Windows 10, PowerShell 7.4.13, Python 3.12.0, uv 0.12.13.
Commands use `.\.tools\bin\uv.exe --cache-dir .uv-cache` as the uv prefix.

| Gate | Outcome |
| --- | --- |
| uv init --bare --name drum-chart-forge --python 3.12 --no-python-downloads --vcs none | Project initialized after cache-permission retry |
| uv sync / sync --locked | Environment and uv.lock resolved; successful approved network retry |
| uv lock --check | Lock matches project metadata |
| uv run --locked drumforge --help | Exit 0; doctor command listed |
| uv run --locked drumforge doctor / doctor --json | Exit 0; text and schema-version-1 JSON reports |
| uv run --locked pytest | 8 passed; synthetic tests only |
| uv run --locked ruff check src tests | Passed |
| uv run --locked ruff format --check src tests | 5 files formatted |
| uv run --locked mypy | Passed; 5 source files, strict configuration |
| uv build --no-build-isolation | Wheel and source distribution built using locked build environment |
| Archive inspection | No caches, local tools, audio or weights included |
| git diff --check | Passed |
| git ls-files and check-ignore | No tracked audio; audio/private/output patterns effective |

## Warnings and limits

Doctor reports ffmpeg, torch, adtof_pytorch, mdx23c and model unavailable. CUDA is
unverified by PyTorch; host hardware audit found Intel HD 630, no NVIDIA device.
This does not block the bootstrap CLI and does not prove inference readiness.
CPU count 4; physical RAM 15.9 GiB. Current session is not WSL; installed WSL distro
is docker-desktop only. Python 3.11/Linux were not exercised.

uv build warns that .uv-cache is inside the source tree. The build uses explicit
source inclusion and .gitignore; archives are inspected for actual contents.
An early archive inspection incorrectly tried to open dist/.gitignore as tar;
the corrected inspection selects only .whl/.tar.gz files. An initial CLI help
em dash decoded incorrectly in captured Windows output; help now uses ASCII.

No ML dependencies or checkpoints downloaded. No transcription, game scan,
playability check or phase after Phase 0 claimed. The initial delivery was local
and uncommitted. The subsequent user instruction requires closing Phase 0 through
chore/phase-0-bootstrap, a commit and a merge into main; see Git history for hashes.
