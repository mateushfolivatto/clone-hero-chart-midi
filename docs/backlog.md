# Backlog navigation and Phase 0 report

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
