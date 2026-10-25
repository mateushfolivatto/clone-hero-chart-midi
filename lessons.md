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

## 2026-10-16 — Hi-hat diagnostics

25. **Check class order at the backend boundary.** The public CLI declared
    BD SD HH TT CY but passed values directly to ADTOF LABELS_5, whose third and
    fourth labels are GM 47 (tom) and GM 42 (hi-hat). Translate the public vector
    once and assert the upstream order. Verify with distinct HH/TT thresholds
    against the serialized values by MIDI note; equal-valued tests hide swaps.
26. **A spectral attack is not an instrument label.** An abruptly truncated
    synthetic bass pulse produced an additional high-band candidate. Compare
    against ground truth, construct continuous synthetic tails when testing
    isolated attacks, and label band peaks as candidates. Verify silence and
    overlapping low/high attacks separately; never report candidate counts as
    musical transcription accuracy.

## 2026-10-17 — Pilot delivery recovery

27. **An ignored workspace file is not a delivered artifact.** On resumption,
    the checkout was back at 83be509 and no song-library/data directory existed,
    although origin/main retained the helper code. The user could not download
    the old ZIP. Preserve metadata-only source/checksum recipes in Git, provide
    a tested reconstruction command and distinguish current local existence from
    user-visible download success. Verify recovery in a clean directory and
    repeat it without modifying existing songs; keep media outside Git.

## 2026-10-17 — Full playlist preparation pass

28. **Folder visibility does not prove file access.** Public Drive folders listed
    their files while artwork, chart, INI and audio downloads returned an explicit
    quota-exceeded page. Classify that response and try other public sources;
    never count a catalog/listing response as a successful song download.
29. **Converted Ogg bytes are not reproducible identities.** Two independent
    Onyx builds of the same source produced equal MIDI/INI but different Ogg
    stream serials. Pin source/tool/MIDI; store local converted-asset hashes and
    reload that receipt on resume. Do not pretend cloud Ogg hashes match Windows.
30. **Separate ordinary drums from confirmed Pro Drums.** Usable four-lane
    Expert charts can lack Pro/tom evidence. Keep configuration and notes, label
    them explicitly and offer ordinary Drums. Onyx's default PS export retained
    five lanes in a real test; exporting or deleting a flag is not conversion.
31. **Validate delivery recipes before publishing.** One successfully prepared
    source still had an HTTP URL rejected by the standalone reader. Its HTTPS
    endpoint reproduced the exact pinned archive hash. Check every final recipe,
    helper hash and reconstructed format, including provider URL semantics such
    as MEGA's key-bearing fragment, rather than checking only local song folders.
32. **Distinguish duplicate catalog rows from repeated pages.** Real Linkin Park,
    Metallica and System of a Down results repeated one joined file row while
    total_filtered counted unique packages. Reject repeated page fingerprints or
    wrong offsets, deduplicate file IDs, and reconcile the unique total. The full
    148 cached searches then passed; rejecting any duplicate discarded valid artists.

## 2026-10-17 — Windows library recovery failure

33. **GUI and CLI distributions can need different runtime flags.** The cloud's
    threaded Onyx AppRun accepted `+RTS -N2`, but the pinned Windows `onyx-cli`
    target has no `-threaded`/`-rtsopts` settings. The downloader nevertheless sent
    that flag and the user's Windows imports repeatedly exited 1. Select options
    for the actual distribution, verify both platform command paths, and keep
    native Windows acceptance separate from Linux conversion results.
34. **Keep subprocess diagnostics outside disposable projects.** The failed
    Onyx logs lived inside TemporaryDirectory and disappeared before the user
    could inspect them; only CalledProcessError's command/exit status survived.
    Store a per-attempt log in the collection, include its path and diagnostic
    tail in the error, and test import/export/timeout failures after cleanup.

## 2026-10-17 — Local collection complement

35. **Folder names are not song identities.** The user's existing library has
    renamed folders, nested packs and already duplicated tracks. Compare INI
    artist/title plus chart-and-audio identity, report ambiguous versions, and
    verify with renamed/nested real copies. Export a complement without changing
    either input; merging into an already populated old folder retains its copies.
36. **A planned download is not a local replacement.** Comparing against all
    recipes would hide an old song even when its new download failed. Use only
    locally present INI/chart/audio folders as references. The incomplete-new-song
    regression keeps the old track selected; rerun after later batches finish.

## 2026-10-18 — Silent converter waits

37. **A KeyboardInterrupt is not a converter failure or a skip.** The user saw
    silent Onyx imports and pressed Ctrl+C; the supplied stack stopped in process
    wait and returned to PowerShell. Report stages, elapsed waits, deadlines and
    log paths while preserving the actual converter log. Handle intentional
    interruption with a clear resume message; do not equate a heartbeat with
    internal progress or a Linux timing with native Windows performance.

38. **Keep UI waits outside process measurements and supervision.** The runner
    started timing before console output and stopped after an unbounded reporter
    join. A delayed-print reproduction displayed success beyond the timeout even
    for a fast child. Separate launch/wait/output; freeze timing before reporter
    cleanup and bound its join. Test a real sleeping child that must be killed,
    a blocked output sink, slow process creation and a late successful return.
    A mocked TimeoutExpired alone does not validate real deadline enforcement.

## 2026-10-25 — Themed library additions

39. **Keep curated additions separate from playlist coverage.** League of Legends,
    Imagine Dragons and similar-band selections introduced songs outside the
    captured Qobuz playlist. Reusing playlist counters or inventing track IDs would
    misrepresent coverage. Append themed recipes with empty Qobuz/playlist ID lists,
    retain the original coverage CSV and track curated totals separately. Verify
    the unchanged snapshot and compare all old/new titles, source identities and
    chart/audio hashes; Enemy belongs to only one theme and Heavy Is the Crown
    remains in its already published batch.
