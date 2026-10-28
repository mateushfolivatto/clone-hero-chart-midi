# Backlog navigation and Phase 0 report

## 2026-10-27 — Broad frozen song survey

64 additional songs across 20 artists completed 128 fixed excerpts and 14,534
mix references. Selection, bounded execution/resume and independent CSV scoring
are reproducible; source comparisons use matching excerpts. Component snare
benefits persisted while the earlier HH benefit did not generalize to twelve
new pairs. Density, simultaneous notes, negative cases and a temporal control
are retained in [broad-song-survey.md](broad-song-survey.md) and DCF-128.

## 2026-10-27 — Explicit components and free public reference

The follow-up audits actual stem samples, omits exactly silent drum/component
excerpts and reports coverage by class. Seven existing songs are compared with
unchanged rules; Afterlife/Crawling components improve snare/yellow agreement
and worsen kick. A chart-free component-candidate command was exercised. Seven
small author StemGMD/LarsNet demonstration MP3s were source/hash verified and
compared; no local model inference or paid service was used. See
[stem-component-study.md](stem-component-study.md) and canonical DCF-127.

## 2026-10-27 — Linkin Park timekeeping hi-hat

Faint and Crawling were inspected using the frozen profile and 13 pinned files.
Crawling exposed ignored disco-flip markers: Pro reference groups now resolve
the authored lane swap without altering original notes or detector parameters.
The original HH detector outperformed the restrictive profile on both songs;
Crawling drums recovered more attacks than its mix. See
[linkin-park-hihat.md](linkin-park-hihat.md) and canonical DCF-126.

## 2026-10-27 — Frozen profile on CoD and Avenged Sevenfold

The requested five-song external test used 25 pinned files, unchanged profile
rules, ten excerpts and 1,157 mix references. Text-chart support and missing-stem
handling allow 115 alongside four A7X songs. Mix kick agreement did not improve;
snare/yellow-cymbal proxies improved with lost recall. Carry On's poor chart/audio
agreement remains unexplained. See [cod-a7x-heldout.md](cod-a7x-heldout.md)
and canonical DCF-125; the overall transcription phase remains open.

## 2026-10-27 — Five chart/audio pairs

The user authorized a real-song inverse reference experiment. Five existing
Pro Drums packages supplied ten excerpts, mixes/drum stems and 860 target proxy
events. Whole-song holdout calibration improved kick/snare agreement and worsened
the yellow-cymbal proxy. Reproducible recipes, results, profile, study/predict
scripts and the existing skill now retain that evidence. See
[five-song-chart-reference.md](five-song-chart-reference.md); root BACKLOG.md owns
DCF-124 and the still-open Phase 1 acceptance. No ADTOF improvement or game
acceptance is claimed.

## 2026-10-20 — Raw MIDI diagnostics

The music-to-chart work resumes within Phase 1 using the local diagnostic skill
for every song. `inspect-midi` writes tempo-aware raw GM onset/velocity CSV and
JSON counts, preserving simultaneous attacks. Fifteen regressions (104 total)
and a synthetic skill-guided audio/MIDI demonstration passed. See
[phase-1-midi-diagnostics.md](phase-1-midi-diagnostics.md) for scope and commands;
root BACKLOG.md owns DCF-118/119 and the remaining private-song acceptance tasks.
No canonical pipeline/exporter or game acceptance is completed by this slice.

## 2026-10-17 — Recover the pilot after failed download

The user reported an artifact-download error and could not find data/. The resumed
machine was on the original work/83be509 checkout, with no song-library directory
or ignored outputs. origin/main contained later work (including concurrent hi-hat
diagnostics), which was fetched and preserved. Runtime policy was current,
unrestricted and enforced; sources were still publicly reachable.

All twelve original sources were recovered and checked again: 11 drum/conductor
MIDI, one ExpertDrums chart and all 40 decoded audio assets. A metadata-only
recipe records archive and per-file hashes, original archive paths and the one
INI adjustment. recover_pilot.py works as a standalone Python script, with no
project installation, FFmpeg, Mido, credentials or model download required on the
user's PC. The public GitHub instructions download the script/recipe and create
Downloads/MixDrumRock locally. Existing verified songs are reused; edits are
preserved and mismatched archives fail instead of being accepted.

The full standalone flow ran outside the checkout with site-packages disabled,
creating /workspace/shared/downloads/MixDrumRock/MixDrumRock-piloto-12.zip
(145,329,929 bytes). All 78 runtime files match the inspected recipe. A repeat run
preserved the completed ZIP. All 52 tests, Ruff, mypy, lock check and build passed;
recipe JSON is present in distributions and private media is absent. Native Windows,
client artifact download, game scanning and gameplay remain unverified. The
durable recovery path does not depend on future availability of this cloud copy.

## 2026-10-16 — Hi-hat diagnostic support

The project-local drum-audio-diagnostics skill provides a separately locked,
CPU-only visual analyzer for mix/stem excerpts. Synthetic checks covered quiet
high-band attacks over strong bass attacks, simultaneous events, silence, stereo
phase, absolute crop times, FFmpeg decoding and overwrite/NaN refusal. The demo
was inspected visually. This is diagnostic tooling, not real-song validation.

An audited upstream class order exposed a real bug: public HH and TT thresholds
were passed to opposite backend classes. Translation now preserves the CLI's
BD SD HH TT CY interface and targets the correct backend notes. A regression
test verifies distinct per-note values; the child rejects unexpected label order.
See [drum-audio-diagnostics.md](drum-audio-diagnostics.md). Root BACKLOG.md owns
DCF-123 and the still-pending Phase 1 acceptance tasks.

Concurrent remote library updates were merged without replacing either workstream.
The integrated tree passed all 46 tests, Ruff lint/format, strict mypy and builds.

## 2026-10-16 — Twelve-song private pilot

The user authorized at least ten playlist songs for a later Clone Hero test.
Twelve native-CH packages were selected, obtained and staged in a separate folder.
They cover Linkin Park, Nirvana, Iron Maiden, The Beatles and Avenged Sevenfold.
No audio/MIDI conversion was required. Heart-Shaped Box's five-lane version was
excluded; Dumb replaced it. Requiem's .chart already had cymbal markers, so its
local song.ini received pro_drums=True; chart/audio bytes were preserved.

Evidence: four-lane Expert drums and Pro Drums markers in all 12 packages,
17,146 Expert gems, all 40 audio assets decoded, no final drum notes past audio,
and ZIP CRC plus a complete hash comparison after fresh extraction. The delivery
is song-library/data/mixdrumrock/exports/MixDrumRock-piloto-12.zip (138.6 MiB),
with already extracted song folders, instructions, song list and source/validation
manifest. Originals and a catalog remain in ignored collection directories.

Reusable helpers safely curate single-song ZIPs, reject unsafe paths/symlinks and
overwrites, inspect drum tracks/tempo and decode audio. The preparation CLI was
exercised independently on Numb and reproduced its runtime hashes. MIDI inspection
covers conductor/PART DRUMS, leaving other instruments unverified. Native Windows,
Scan Songs, perceived synchronization and gameplay remain for the user's test.
Full-playlist matching/acquisition and existing-library inventory remain open;
see the canonical DCF-LIB entries for actual status and song-library/README.md for
the next-session prompt.

Final checks passed: all 45 tests, Ruff lint/format, strict mypy, locked dependency
validation, CLI help/doctor and wheel/sdist builds. Both code distributions were
inspected and contain no collection data, media, model files or caches. The pilot
ZIP is 145,332,049 bytes; SHA256 is recorded beside it in the ignored exports
directory. No song or archive is tracked or pushed to GitHub.

## 2026-10-16 — Qobuz metadata export

After unrestricted publication, Qobuz and RhythmVerse returned HTTP 200. The
public MixDrumRock playlist was captured completely: 681 entries in seven pages,
with a final revision check. CSV and XLSX were reopened and compared against the
source snapshot for count, order, titles, IDs and duration; a fresh export
reproduced the list. Reusing an existing output directory was rejected without
changing any files. Data remains ignored under song-library/data/mixdrumrock/.

`drumforge.library.qobuz` supports repeatable public-metadata exports. CSV/JSON
require only the standard library; XLSX optionally uses openpyxl 3.1.5 through
uv's transient --with option, keeping core dependencies unchanged. Five new tests
exercise incomplete/repeated pages, concurrent playlist changes and preservation
of repeated songs/versions. Existing-library inventory, chart search/downloads,
conversion and gameplay validation remain outstanding; no audio was downloaded.

Final gates passed: 37 pytest tests, Ruff lint/format, strict mypy, locked dependency
validation, CLI help/doctor and wheel/sdist builds. Archives include the new helper
and exclude private collection data, media, models and caches. The documented
`uv run --locked --with openpyxl==3.1.5` command produced the delivery files under
song-library/data/mixdrumrock/exports/qobuz-2026-10-16/; rows match the inbox snapshot.

## 2026-10-16 — Separate MixDrumRock library

The user requested library management for a growing Qobuz playlist and existing
drums charts. [../song-library/README.md](../song-library/README.md) records the
portable layout, metadata templates, conversion caveats and continuation prompt.
No executable downloader or conversion workflow was added. The playlist is not
yet supplied, and the network proxy currently denies RhythmVerse access.
Authoritative status is in DCF-LIB items in the root backlog; transcription
phase acceptance remains unchanged.

Validation on the cloud Linux/Python 3.12.14 environment: all 32 existing pytest
tests passed; locked dependency check, Ruff lint/format, strict mypy, CLI help,
doctor in text/JSON and wheel/sdist build passed. Doctor's optional ML/checkpoint
warnings remain expected; inference is not validated. Both archives were inspected
and contain no caches, collection data, media or weights. The CSV headers are
unique, all seven collection directories are ignored, and no media is tracked.
The build warns that the local uv cache could be included, but the actual archive
inspection confirms its absence. No new executable behavior was introduced.

[../BACKLOG.md](../BACKLOG.md) is the sole task-status authority. Read
[../lessons.md](../lessons.md) every time you consult it. This document is a
session evidence summary, not a duplicate checklist.

## 2026-09-10 — Phase 0

Research and bootstrap delivered for DCF-001 through DCF-042. DCF-001 adapts the
suggested new repository to the user's existing clone-hero-chart-midi checkout:
preserve history, main and origin; distribution name is drum-chart-forge. No remote
rename or visibility change was performed. origin/HEAD targets main;
server-side settings remain unaudited.

Evidence: CLI help/doctor, eight passing pytest tests, Ruff lint/format, strict
mypy, lock validation, wheel/sdist build and archive/audio hygiene inspection.
See [testing.md](testing.md) for commands and [phase-0-verification.md](phase-0-verification.md)
for results. The application remains a diagnostic skeleton; Phase 1 is not started.

Known follow-up risks: ADTOF code/weight permission, exact MDX checkpoint byte sizes
and immutable revisions, backend Windows/Python wheels, absent ffmpeg/PyTorch,
and no WSL Ubuntu. Research tasks document these uncertainties rather than
asserting that the optional backends are installed or licensed for redistribution.

## Git closure instruction

After the initial uncommitted delivery, the user required branches before changes
and a commit followed by a merge into main for every completed phase. Phase 0
closure uses chore/phase-0-bootstrap, including this standing instruction. Consult
Git history for the resulting commit and merge; no remote push is part of this closure.

## Windows-primary follow-up

Phase 0 environment/doctor update revalidates DCF-013 through DCF-019 and
DCF-037 through DCF-042 on native Windows/Python 3.12 CPU. See environment.md and
phase-0-verification.md. DCF-100 onward remains unstarted: only a compatibility
audit is authorized next, before implementation.

The pre-Phase 1 compatibility audit was completed on 2026-09-11 without changing
DCF-100–122 status. See [phase-1-windows-compatibility.md](phase-1-windows-compatibility.md).
The next implementation session should start only after explicit user direction.

## 2026-09-12 — Phase 1 audio foundation

After explicit user authorization, DCF-100–103 were implemented on
`phase-1-audio-foundation`: metadata probing, mono 44.1 kHz PCM normalization,
source preservation and content/config cache. Twenty tests plus lint, formatting
and strict typing passed on the Linux portability environment with Python 3.12.
Native Windows/real-audio verification remains before Phase 1 acceptance.

The next Phase 1 slice added the `Separator` and `Transcriber` contracts
(DCF-104 and DCF-109) plus an explicit full-mix passthrough implementation.
Twenty-three tests and all static gates passed. `--skip-separation` remains open
until the transcription command can expose meaningful pipeline selection.

The standing Git workflow now also requires pushing `main` after every successful
merge. The first push attempt from this environment failed because HTTPS GitHub
credentials were unavailable; local commits were preserved unchanged.

The ADTOF slice completed DCF-107, DCF-110–112 and DCF-115. The real pinned
backend converted a synthetic two-second WAV to parseable MIDI on CPU in about
4.6 seconds. Private-song quality, velocities/confidences and debug inspection
remain open. An initial unpinned Linux resolution attempted CUDA packages; it was
stopped and replaced with the explicit PyTorch 2.12.0 CPU index.

## 2026-10-25 — Themed library batches

The separate library workstream appended batches 13–18 with 45 structurally
verified charts for LoL, Imagine Dragons and seven bands similar to Linkin Park.
Old recipes, Qobuz coverage and Onyx conversion behavior remain unchanged.
See [library-themed-verification.md](library-themed-verification.md) for evidence,
[../song-library/TEMATICOS.md](../song-library/TEMATICOS.md) for selective Windows
recovery/song lists and BACKLOG.md DCF-LIB-013 for authoritative task status.
Native Windows execution and Scan Songs/playtest still require user feedback.

## 2026-10-27 — Linkin Park expansion and installed-library additions

The user's duplicate cleanup succeeded; their scan report had duplicate-chart
relationships and two lyric warnings, not evidence of 300 corrupt downloads.
The raw log/private paths remain outside Git. Given Up was found in batch 02.
The band catalog pass prepared 207 additional editions in batches 19–30,
with 172 Pro Drums and 35 ordinary Drums. All 1527 assets,
871 audio decodes, 253,421 Expert gems and 12 ZIPs passed checks.

Band-only recovery references the 33 earlier charts without duplicating recipes;
the local comparator exports only absent songs and holds shared-chart/edition
uncertainty for review. Prior recipes, Qobuz coverage and Onyx helper bytes are
preserved. All 155 core tests, 19 optional DSP checks and distribution audits
passed after integrating existing main diagnostics, alongside
fresh stdlib recovery/offline resume and real-song additions checks on Linux.
See [the Windows guide and next prompt](../song-library/LINKIN-PARK.md) and
[technical evidence](library-linkin-park-verification.md). Root BACKLOG.md owns
DCF-LIB-014; native Windows/game acceptance and explicit catalog gaps remain open.
