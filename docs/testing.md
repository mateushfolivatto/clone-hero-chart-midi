# Quality gates

The hi-hat diagnostic slice added a regression, bringing its baseline to 38 tests;
integration with the concurrent private-library pilot passed all 46 tests.
The regression checks that the public hi-hat threshold reaches backend GM 42 and the tom
threshold reaches GM 47. The optional script lives outside src/tests; also run:

```text
uv --cache-dir .uv-cache run --locked ruff check .agents/skills/drum-audio-diagnostics/scripts
uv --cache-dir .uv-cache run --locked ruff format --check .agents/skills/drum-audio-diagnostics/scripts
uv --cache-dir .uv-cache run --no-project --locked --script .agents/skills/drum-audio-diagnostics/scripts/inspect_audio.py --help
```

Its separate script lock pins optional plotting dependencies without adding them
to the core. Use the synthetic acceptance procedure/evidence in
drum-audio-diagnostics.md when changing DSP; do not equate spectral candidates
with classified instrument notes. Real-song and Windows checks remain separate.

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

Pilot recovery adds six tests (52 total including the concurrent ADTOF fix):
changed/truncated download rejection, standalone recovery/resume without network,
existing edit preservation, atomic cleanup after a bad extracted hash, manifest
identity/path checks and byte-stable INI patching. Fixtures are synthetic.
The real recipe was also exercised with `python -I -S` outside the checkout,
downloading all twelve sources and reproducing 78 verified runtime files plus ZIP.
A second execution validated the existing collection and ZIP. This verifies
reconstruction on cloud Linux/Python 3.12, not Windows or the browser download UI.

The full-playlist preparation pass has 65 passing tests and eleven validated new
ZIPs, with 254 charts/1,449 assets/629 decoded audio files. Both ordinary drums and
Pro Drums are explicit. Standalone five-format recovery, authenticated public MEGA
recovery and unchanged resume were exercised outside the checkout without external
Python libraries; Windows execution/game acceptance remain separate. See
[library-bulk-verification.md](library-bulk-verification.md) for counts, scope,
provider blockers, artifact checks and reproduction instructions.

The Windows Onyx invocation correction adds five regressions (70 tests total):
supported Windows/Linux runtime options and persistent import/export/timeout
diagnostics after cleanup. Three real source conversions reproduced pinned MIDI,
17 runtime assets verified against local receipts, and repeated preparation kept
all assets unchanged. Linux isolated-Python evidence does not establish Windows
execution or game acceptance. See library-onyx-recovery-fix.md for the diagnosis.

The local library complement adds 13 regressions (83 tests total): renamed/nested
folders, INI encodings/case/color tags, chart-and-audio identity despite edited
metadata, repeated old copies, incomplete new downloads, uncertain versions,
source edits, links/archives/OneDrive tags, nested packs with a stray INI, standalone export,
output preservation and a lowered ZIP64 threshold. A real scan compared five
renamed old folders with all 254 new charts and selected only the synthetic
exclusive. Another stdlib-only subprocess exported two real exclusive songs
plus a synthetic one (12,223,459 bytes) and checked every ZIP asset hash.
The user's actual 4 GB collection, native Windows and game acceptance remain
unverified; use song-library/SEM-REPETIDAS.md to run on the user's PC.

Onyx wait feedback adds two regressions (85 tests total): a controlled blocking
converter confirms elapsed notifications, closed stdin, actual log retention and
reporter shutdown; KeyboardInterrupt exits 130 with a preservation/resume message.
Existing import/export/timeout diagnostics and platform arguments still pass.
The reported Endless, Nameless source imported in 1.35 s on Linux. An isolated
stdlib-only full reconstruction then took 0.9 s import and 23.3 s export, showing
elapsed feedback and verifying pinned MIDI, local hashes, persistent log and
unchanged resume. These Linux timings do not diagnose native Windows slowness;
the supplied Windows log records only import start, without completion/error.
The user confirmed interrupting that import before its 180-second deadline;
the traceback alone does not establish an actual timeout or hang.
