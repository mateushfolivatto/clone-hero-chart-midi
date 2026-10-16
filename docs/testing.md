# Quality gates

Run from the repository root after `uv --cache-dir .uv-cache sync --locked`.
On this machine uv was installed locally: replace `uv` with
`.\.tools\bin\uv.exe` in PowerShell. No shell activation is required.

```text
uv --cache-dir .uv-cache lock --check
uv --cache-dir .uv-cache run --locked drumforge --help
uv --cache-dir .uv-cache run --locked drumforge doctor
uv --cache-dir .uv-cache run --locked drumforge doctor --json
uv --cache-dir .uv-cache run --locked pytest
uv --cache-dir .uv-cache run --locked ruff check src tests
uv --cache-dir .uv-cache run --locked ruff format --check src tests
uv --cache-dir .uv-cache run --locked mypy
uv --cache-dir .uv-cache build --no-build-isolation
git diff --check
git status --short
git ls-files
git check-ignore audio/probe.mp3 fixtures/private/probe.wav samples/private/probe.flac output/probe.mid outputs/probe.mid generated/probe.mid probe.MP3 probe.ogg
```

Inspect wheel/sdist members: only intended source, metadata and documentation;
no .tools, .uv-cache, private audio or model weights. Review tracked paths for audio
extensions; an empty audio list is required. Review the diff and doc/task status.
Build outputs stay in ignored dist/. Keep uv.lock version controlled.

Tests exercise CLI subprocesses, structured doctor output, temporary file cleanup,
unwritable/nonexistent target failure, absent ffmpeg, tool timeout, broken torch,
CUDA reporting and WSL detection. All inputs are synthetic; no audio/model download.
The Windows update adds explicit Windows/Linux/WSL labels, stale WSL-variable
handling, CPU-only CUDA status, a torch timeout and ffmpeg.exe paths with spaces.
There are 32 tests after the Phase 1 ADTOF-adapter update. Linux/WSL labels
are tested with mocks only. Audio preparation tests use synthetic bytes and
mocked FFmpeg/ffprobe subprocesses; native Windows real-codec verification remains.
Backend tests verify structural `Separator`/`Transcriber` compatibility and the
full-mix passthrough without importing optional ML packages.
ADTOF adapter tests cover checkpoint identity, threshold bounds, isolated Python
paths, CPU forcing, partial-output cleanup and overwrite refusal. A separate local
smoke used the real pinned backend and a synthetic two-second WAV; its parseable
MIDI contained one note-on and completed in about 4.6 seconds on this host.
Doctor returns 0 with optional-component warnings, 1 for a failed write target;
argparse returns 2 for invalid usage. Optional dependency warnings do not validate
ML readiness. Model path checks only existence/size, not checkpoint compatibility.

Later phases add meaningful mapping/timing/serialization golden tests and separate
slow/model tests. They do not belong in the Phase 0 executable skeleton.

The separate song-library workstream adds five public-playlist metadata tests,
bringing the suite to 37 tests. They run offline with synthetic pages, checking
incomplete pagination, repeated pages, playlist mutation and preservation of
repeated songs/versions. A real cloud export independently verified all 681
MixDrumRock entries in CSV/XLSX against a JSON snapshot. This verifies metadata
export only, not audio downloads, chart conversion or compatibility in the game.

The first private song pilot adds eight package-safety/chart tests (45 total):
path traversal, symlinks, Windows case collisions, overwrite refusal, atomic
cleanup after failed inspection, byte preservation, tempo changes and five-lane
rejection. No copyrighted media is used in tests.

Real pilot checks: 12 native song packages, 11 MIDI drum/conductor inspections and
one ExpertDrums .chart inspection, 17,146 Expert gems and 40 audio assets decoded
with FFmpeg. ZIP CRC and all runtime-asset hashes passed after a fresh extraction.
The preparation CLI reproduced Numb in a temporary directory, preserved its assets
and refused an existing destination. Mido 1.3.3 is optional through uv --with;
core development dependencies and lockfile are unchanged. Other instruments,
native Windows execution, perceived synchronization and game acceptance are not
established by these cloud checks. User Scan Songs/playtest remains required.
