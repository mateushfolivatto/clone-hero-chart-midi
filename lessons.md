# Lessons learned

Read this file in full whenever BACKLOG.md is read, at session start and after
context recovery. Add lessons only when supported by an observed issue or verified
finding. This file supplements the backlog; it does not redefine task completion.

## 2026-09-10 — Bootstrap

1. **Look for uploaded filename variants.** The initial files were BACKLOG(1).md
   and CONTEXT(2).md. Read them fully before normalizing names; preserve their
   contents and task IDs. Verify that only one canonical task list remains.
2. **Sandbox visibility is not installation state.** `py --list-paths` initially
   reported no Python; the approved host audit found Python 3.12.0. WSL/CIM also
   returned access denied. Retry through the permission mechanism and distinguish
   inaccessible from absent. Never install a second runtime based on PATH alone.
3. **Keep tool cache location explicit.** uv's default user cache was denied.
   Use the repository-local ignored .uv-cache and document the actual command.
4. **MIDI and .chart drum markers differ.** MIDI notes 110/111/112 mark toms;
   .chart uses 66/67/68 to mark cymbals. Check the format reference before coding;
   future golden fixtures must distinguish cymbal and tom at separate timestamps.
5. **A wrapper's license does not license converted weights.** ADTOF-pytorch
   documents conversion of original weights; ADTOF declares CC BY-NC-SA 4.0.
   Track code, datasets and each checkpoint separately before adoption/distribution.
6. **Optional missing tools are diagnostic warnings.** A usable bootstrap must
   run without ffmpeg, PyTorch or CUDA. Test missing/broken tools and subprocess
   timeouts; a successful doctor does not mean transcription is available.
7. **Validate checkpoints before calling ADTOF.** The inspected upstream API
   skips loading when a weights path is absent and can continue with random
   initialization. The future adapter must fail on missing/incompatible weights
   and verify identity before inference; successful MIDI output alone proves nothing.
8. **Limit format/lint scope to project files.** The first Ruff invocation using
   `.` also traversed the local .tools installer directory. Exclude .tools and
   .uv-cache explicitly, and run gates against src/ and tests/.
9. **Inspect only actual distribution archives.** uv creates a dist/.gitignore;
   an initial audit tried to open it as tar. Filter .whl and .tar.gz explicitly,
   then verify every archive member. Do not treat a build warning as proof of leakage.
10. **Finish phases in Git, not only in the working tree.** The user explicitly
    requires a branch before new work, then a verified commit and merge into main.
    Phase 0 originally ended uncommitted on main before this instruction arrived.
    Carry those existing changes onto a dedicated branch, and for future work
    create the branch first. Verify branch name before edits and commit/merge
    history plus working-tree status before reporting a phase as delivered.
11. **Portability is not a WSL requirement.** The college PC cannot install WSL
    Ubuntu; Windows/Python 3.12 CPU is primary for this stage. Remove stale WSL
    fallback instructions from active documentation. Never propose Docker or policy
    changes to hide a Windows dependency failure. Verify native gates and distinguish
    wheel availability, source compatibility and actual inference results.
12. **Missing CUDA is not a failed CPU environment.** Report platform, CPU,
    PyTorch and CUDA separately. Missing/broken PyTorch leaves hardware unverified;
    it does not prove that a GPU is absent. Test CPU-only and unavailable probes.

## 2026-09-11 — Pre-Phase 1 compatibility audit

13. **Test a release against its matching source tag.** `mdxnet-infer` master had
    APIs absent from its 0.1.0 wheel, so master tests failed during collection
    against the release. The matching v0.1.0 suite passed 40 tests on Windows
    Python 3.12. Pin one revision and never mix release artifacts with HEAD tests.
14. **A successful ML smoke is narrower than model validation.** ADTOF generated
    valid MIDI from a synthetic WAV on CPU, proving install/import/inference paths.
    It does not prove musical accuracy, full-song performance or license clearance.
15. **Prefer the no-separation baseline.** Direct ADTOF avoids a 417–500 MiB
    separator checkpoint and a second unresolved weight license. Add separation
    only after measured full-mix results justify its CPU and distribution cost.

## 2026-09-12 — Phase 1 audio foundation

16. **Anchor private-media ignore rules at the repository root.** The unanchored
    `audio/` rule also ignored `src/drumforge/audio/`, which could silently omit
    implementation modules from commits. Use `/audio/` for the private input
    directory and verify new source paths with `git check-ignore` and `git status`.
17. **Verify remote authentication after local closure.** A valid local merge did
    not imply that HTTPS credentials were available to `git push`. Push `main`
    after each merge, verify `main` against `origin/main`, and preserve/report
    commits unchanged when authentication blocks publication.
18. **Do not resolve a virtual-environment Python symlink.** Resolving the backend
    executable to its base interpreter discarded the venv's site-packages and made
    an installed ADTOF appear missing. Preserve the absolute venv executable path
    and cover symlink behavior with a test before isolated-backend inference.
19. **Pin the CPU wheel index before resolving ML dependencies.** Installing an
    unconstrained current Linux `torch` attempted several gigabytes of CUDA 13
    packages. Stop that resolution immediately; install the audited `+cpu` wheel
    from PyTorch's CPU index first, then add the pinned optional backend and verify
    the installed package list contains no NVIDIA/CUDA dependencies.

## 2026-10-16 — Song-library feasibility

20. **A proxy denial does not describe the destination site.** Requests to the
    RhythmVerse catalog and robots.txt failed during HTTP CONNECT with 403 before
    site content was available. Record the environment-network blocker, save only
    the required domain addition, and retry after application. Do not infer a site
    ban, download API or automation permission from an uninspected destination.

21. **A public playlist page may show only its first batch.** Qobuz's open-page
    frontend requests 50 entries by default, while this playlist contains 681.
    Read public metadata in pages and compare expected count, offsets, entry IDs,
    positions and revision before calling an export complete. Verify CSV/XLSX rows
    against the captured source and preserve repeated songs as distinct entries.

22. **Catalog flags are weaker than chart evidence.** RhythmVerse reported
    pro_drums=0 for Numb, but its original song.ini had pro_drums=True and its
    PART DRUMS contained tom markers. Inspect actual configuration and notes;
    preserve source flags separately and leave game acceptance pending a playtest.
23. **Do not remove a five-lane flag to pretend conversion.** The first
    Heart-Shaped Box candidate had five_lane_drums=True and Expert MIDI note 101.
    Exclude it from a four-lane pilot or perform a separately verified conversion.
    The pilot used Dumb instead, preserving the excluded original archive.
24. **Scope MIDI inspection around supported game data.** Mido rejected extended
    Phase Shift SysEx bytes in Numb's guitar track. Strictly parse original conductor
    and PART DRUMS chunks for drum checks; do not enable generic clipping or rewrite
    the delivered MIDI. Record that other instruments were not validated, and
    verify the original chart/audio hashes through ZIP extraction.
