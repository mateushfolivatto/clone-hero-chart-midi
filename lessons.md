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

## 2026-10-20 — MIDI diagnostic fixtures

39. **Sort note-ons and note-offs together in synthetic MIDI.** An ad-hoc demo
    generator appended a note-off before the next simultaneous note-on, creating
    a negative delta and stalling an unchecked VLQ encoder. Build one tick-sorted
    event schedule and bound VLQ inputs to 0..0x0fffffff. The corrected demo parses
    all 22 expected attacks, including seven simultaneous pairs; independent
    hand-authored regression bytes verify timing without relying on that generator.

## 2026-10-27 — Existing chart/audio pairs

40. **A game lane is a weak instrument label.** In five real songs, yellow-cymbal
    tuning worsened held-out F1 even while kick/snare improved. Come Together has
    many blue toms and few yellow cymbals. Preserve marker intervals and label
    proxies honestly; exclude all excerpts of the test song from calibration.
    Verify TP/FP/FN and individual song results before adopting a spectral profile;
    agreement with charts is not independently annotated acoustic accuracy.
41. **FFmpeg -t can leave a codec tail beyond the requested sample count.** At
    120 s, two Numb Vorbis stems returned 352/448 extra samples for a 20 s request.
    Decode a bounded tail guard and crop by exact sample count without shifting
    the start; refuse stems that do not cover the interval. A regression verifies
    exact cropping/start preservation, and the real rerun preserves scoring.

42. **External tests must keep rules and coverage explicit.** CoD/A7X evaluation
    found three single-stream packages, one .chart and only two drum-stem pairs.
    Pin the frozen profile, reject calibration-data reuse, preserve .chart's
    opposite pad/cymbal flag convention and report mode-specific sample sizes.
    A regression forbids calibration calls and verifies profile byte identity and
    absent drum output. Keep Carry On's poor result and 115's zero yellow-cymbal
    reference count visible; do not optimize offsets/windows after seeing test scores.

43. **Resolve disco flip before interpreting Pro reference colors.** Crawling's
    Expert mix events with flag d place timekeeping hi-hat on stored red and
    snare on stored yellow. Ignoring them counted 52 instead of 212 Pro-yellow
    references in the fixed excerpts. Resolve state by difficulty/tick before
    scoring, distinguish dnoflip, preserve original note/timing/velocity and
    version reference semantics. MIDI/.chart regressions cover same-tick order,
    resets, toms, simultaneous notes and conflicts. Compare prior references:
    all events in the previous ten songs and Faint remained unchanged. A changed
    label score is not detector improvement.

44. **A drum filename can contain digital silence.** Brompton Cocktail's drums.ogg
    decoded to zero in both fixed excerpts; The Number of the Beast's drums_2.ogg
    was zero at 60–80 s. Audit decoded samples and record availability per excerpt
    and class before scoring components. Exclude exact-zero unavailable audio,
    preserve very quiet signals and keep the mix baseline. A regression verifies
    that missing snare audio is not counted as transcription false negatives.
45. **An author demo is not local model inference.** Seven source-verified
    StemGMD/LarsNet MP3s could be obtained through GitHub while shell networking
    was blocked. Record revision, blob identity, SHA256 and whether files are
    references or precomputed estimates. Compare those signals without claiming
    model execution, MIDI accuracy or performance on our songs. Keep E-GMD's
    unused status and the remaining weight/runtime work explicit.

46. **A two-song source gain needs broader paired validation.** Component yellow
    F1 improved strongly on Afterlife/Crawling, but twelve new song pairs changed
    only .501→.505 with a gain interval crossing zero; snare improvement persisted.
    Plan artist-balanced unseen songs before scoring, preserve negative/silent
    cases and compare sources on the same excerpts. Recompute scores from CSV,
    resample whole songs with methods paired, and report recall/precision as well
    as F1. Density and coincidence controls reveal opportunities for matching;
    they do not establish acoustic instrument identity or a causal masking effect.

## 2026-10-25 — Themed library additions

47. **Keep curated additions separate from playlist coverage.** League of Legends,
    Imagine Dragons and similar-band selections introduced songs outside the
    captured Qobuz playlist. Reusing playlist counters or inventing track IDs would
    misrepresent coverage. Append themed recipes with empty Qobuz/playlist ID lists,
    retain the original coverage CSV and track curated totals separately. Verify
    the unchanged snapshot and compare all old/new titles, source identities and
    chart/audio hashes; Enemy belongs to only one theme and Heavy Is the Crown
    remains in its already published batch.

## 2026-10-27 — Duplicate scan feedback and Linkin Park expansion

48. **Read the scanner's category before diagnosing corruption.** The uploaded
    badsongs report listed 301 duplicate-chart relationships and two nonblocking
    lyric warnings. Most duplicates involved a complement copied inside itself;
    the user confirmed that moving duplicates out of scanned paths resolved the
    problem. Compare additions against the actual installed library before export,
    retain uncertain chart-only collisions for review and keep backups outside
    scanned roots. Verify renamed copies, changed audio/metadata, standalone export
    and unchanged input bytes; scan feedback alone does not verify every chart's
    gameplay or timing. Do not publish the user's raw log or personal paths.

49. **Inspect the container before choosing conversion.** A catalog entry labeled
    rb3xbox actually downloaded a native RISE ZIP with song.ini, notes and audio;
    the collector rejected it as non-STFS solely because of that label. Detect
    STFS signatures from the downloaded bytes and otherwise use the validated
    ZIP/RAR/7z path. Verify native ZIP without Onyx despite an Xbox label and
    STFS conversion despite a CH label, preserving original bytes and leaving
    platform-specific Onyx options/supervision unchanged.

## 2026-10-28 — Native SNG sources and display metadata

50. **Restore the native container before choosing a converter.** I Bet My Life's
    public original is SNG v1, with metadata in its header rather than song.ini.
    A bounded reader following the published layout restores its masked assets
    without audio transcoding; six Opus streams decode and 813 Expert gems remain.
    Verify per-file XOR reset/chunk boundaries, unsafe names/offsets, source/asset
    hashes and clean stdlib recovery plus unchanged offline resume. Keep generated
    INI provenance explicit and leave the established Onyx behavior untouched.

51. **Display tags do not identify another recording.** Take Me to the Beach's
    original INI wraps its title/guest in color tags, causing a false catalog
    mismatch. Ignore known display tags only during identity comparison; retain
    source bytes and authored tags, document any existing Pro-flag patch and keep
    Live/demo/version words. Verify an accepted colored title and a rejected
    colored Live edition. Skillet's studio titles I Want to Live and Live Free
    or Let Me Die also require recording qualifiers rather than a bare Live word
    when separating studio/live delivery groups. The Strokes follow-up exposed
    the same risk in You Only Live Once and Under Cover of Darkness. Match an
    explicit recording qualifier, not incidental Live/Cover words; a published
    selection regression now requires both studio titles among the highlights.

## 2026-10-28 — Two-pedal chart preference

52. **Check optional Expert+ notes before diagnosing a reduced kick chart.**
    Nightmare's existing batch-06 chart already contained 471 .chart-32 kicks
    beyond its 893 base kicks. They need the game's 2x Kick modifier. The requested
    alternate has 454 MIDI-95 extras and 916 base kicks. Count these separately,
    preserve authored notes/audio and explain the setting; Pro Drums alone does
    not establish double bass. Tests cover both encodings and excluded tracks,
    difficulties and zero-velocity events. A full-2x edition can instead encode
    all kicks as ordinary notes, so zero optional notes is not definitive. Keep
    requested alternate delivery outside automatic batches, with explicit swap
    instructions, source pins and verified offline resume, to avoid duplicate
    installations without rewriting the old recipes.
    Sonne's follow-up found zero optional kicks in both imported studio sources
    (407/464 base kicks), with no explicit full-2x author claim. Keep 2x unverified
    in that case; do not present ordinary kick density as proof of two-pedal fidelity.
    The CoD follow-up confirmed a concrete ordinary-note case: the author's 2x
    Beauty of Annihilation has 590 MIDI-96 kicks versus 563 in the paired 1x,
    adding exactly 27 kick attacks without removing other note-ons. Shared
    song.ogg is identical, but the 2x has an additional authored guitar.ogg;
    compare actual asset sets before claiming whole-package audio equality.

## 2026-10-30 — CoD Zombies source identities

53. **Search composer, performer and known title variants before declaring gaps.**
    The old conservative snapshot listed Lullaby Of A Deadman as not found under
    Kevin Sherwood. A composer-wide search located Lullaby for a Deadman with
    featured Elena Siegman credits and a source description identifying Verrückt.
    The real original package then validated Pro Drums and paired audio. Search
    aliases explicitly and verify source identity; do not globally strip recording
    qualifiers or accept every fuzzy match. Preserve the old coverage snapshot and
    record the new curated outcome separately. Five other charts' optional kicks
    and the paired Beauty 1x/2x comparison verify that title labels alone are weaker
    than actual note/source evidence.
