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
There are 23 tests after the Phase 1 backend-interface update. Linux/WSL labels
are tested with mocks only. Audio preparation tests use synthetic bytes and
mocked FFmpeg/ffprobe subprocesses; native Windows real-codec verification remains.
Backend tests verify structural `Separator`/`Transcriber` compatibility and the
full-mix passthrough without importing optional ML packages.
Doctor returns 0 with optional-component warnings, 1 for a failed write target;
argparse returns 2 for invalid usage. Optional dependency warnings do not validate
ML readiness. Model path checks only existence/size, not checkpoint compatibility.

Later phases add meaningful mapping/timing/serialization golden tests and separate
slow/model tests. They do not belong in the Phase 0 executable skeleton.
