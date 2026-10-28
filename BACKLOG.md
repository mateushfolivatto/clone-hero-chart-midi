# Drum Chart Forge — Backlog

Status legend:

- `[ ]` TODO
- `[-]` IN PROGRESS
- `[x]` DONE
- `[!]` BLOCKED
- `[?]` RESEARCH / DECISION REQUIRED

Priority:

- **P0** mandatory for current milestone
- **P1** important
- **P2** later enhancement

---

## Phase 0 — Research & Bootstrap

### Repository and environment

- [x] **DCF-001 [P0]** Establish Git repository for `drum-chart-forge` (adapted: reuse existing `clone-hero-chart-midi`, preserving history and origin).
- [x] **DCF-002 [P0]** Use `main` as default branch.
- [x] **DCF-003 [P0]** Initialize Python project using `uv`.
- [x] **DCF-004 [P0]** Create `src/drumforge/` package.
- [x] **DCF-005 [P0]** Add `pytest`.
- [x] **DCF-006 [P0]** Configure formatter/linter.
- [x] **DCF-007 [P1]** Configure static type checking.
- [x] **DCF-008 [P0]** Add audio-safe `.gitignore`.
- [x] **DCF-009 [P0]** Add `README.md`.
- [x] **DCF-010 [P0]** Add canonical `CONTEXT.md`.
- [x] **DCF-011 [P0]** Add `AGENTS.md`.
- [x] **DCF-012 [P1]** Add `CONTRIBUTING.md`.

### Environment diagnostics

- [x] **DCF-013 [P0]** Implement `drumforge doctor`.
- [x] **DCF-014 [P0]** Detect Python version.
- [x] **DCF-015 [P0]** Detect ffmpeg availability/version.
- [x] **DCF-016 [P1]** Detect PyTorch device availability.
- [x] **DCF-017 [P1]** Detect CUDA and report without requiring it.
- [x] **DCF-018 [P1]** Identify WSL environment.
- [x] **DCF-019 [P1]** Record CPU/RAM-relevant diagnostics without collecting unnecessary personal data.

### Dependency/licensing research

- [x] **DCF-020 [P0]** Evaluate `ADTOF-pytorch`.
- [x] **DCF-021 [P0]** Evaluate `adtof_plus_drum_transcription`.
- [x] **DCF-022 [P0]** Evaluate current viable source-separation backend.
- [x] **DCF-023 [P0]** Evaluate `midi2clonehero` as reference/dependency.
- [x] **DCF-024 [P0]** Document code vs model-weight licenses.
- [x] **DCF-025 [P0]** Create `docs/dependency-licenses.md`.
- [x] **DCF-026 [P0]** Record Python-version compatibility.
- [x] **DCF-027 [P1]** Record expected model download sizes and cache locations.
- [x] **DCF-028 [P1]** Decide whether external ML backends are optional extras.

### Format research

- [x] **DCF-029 [P0]** Document Clone Hero minimum song folder requirements.
- [x] **DCF-030 [P0]** Document RB3-style Pro Drums lane semantics used by Clone Hero.
- [x] **DCF-031 [P0]** Compare `notes.mid` vs `notes.chart` for first exporter.
- [x] **DCF-032 [P0]** Document MIDI PPQN / tempo-event requirements.
- [x] **DCF-033 [P1]** Document cymbal markers.
- [x] **DCF-034 [P1]** Document Expert+/2x Kick conventions.
- [x] **DCF-035 [P2]** Document ghost/accent conventions.
- [x] **DCF-036 [P2]** Document roll/swell events.

### Phase 0 acceptance

- [x] **DCF-037 [P0]** `drumforge --help` works.
- [x] **DCF-038 [P0]** `drumforge doctor` works.
- [x] **DCF-039 [P0]** Tests pass.
- [x] **DCF-040 [P0]** Lint/format checks pass.
- [x] **DCF-041 [P0]** No copyrighted audio is tracked by Git.
- [x] **DCF-042 [P0]** Architecture and next experiment documented.

---

Phase 0 verified on 2026-09-10. Evidence: `docs/phase-0-verification.md`.
Research completion records unresolved model licensing and runtime risks; it does
not imply model installation or redistribution clearance. Read `lessons.md` with
this backlog. Phase 1 remains unstarted.

Windows-primary follow-up: DCF-013–019 and DCF-037–042 revalidated with 15 tests.
See `docs/environment.md` and `docs/phase-0-verification.md`. Windows/Python 3.12
CPU is mandatory for this stage; WSL/Linux is optional, CUDA is optional, and
Docker/administrative workarounds are prohibited. Perform only the compatibility
investigation before DCF-100; implementation awaits the user's next instruction.

Pre-Phase 1 Windows compatibility gate completed on 2026-09-11. Evidence and the
recommended minimum CPU configuration are in
`docs/phase-1-windows-compatibility.md`. This research did not complete or start
any DCF-100–122 implementation item; Phase 1 remains unstarted pending explicit
authorization.

## Phase 1 — Audio → Drum MIDI Spike

### Audio handling

- [x] **DCF-100 [P0]** Probe audio metadata: duration/sample rate/channels.
- [x] **DCF-101 [P0]** Normalize input audio to a backend-compatible working format.
- [x] **DCF-102 [P1]** Preserve original file unchanged.
- [x] **DCF-103 [P1]** Cache working intermediates by content/config hash.

### Separation

- [x] **DCF-104 [P0]** Implement `Separator` interface.
- [ ] **DCF-105 [P0]** Implement first separation backend.
- [ ] **DCF-106 [P0]** Generate isolated/estimated drums stem from full mix.
- [x] **DCF-107 [P1]** Add `--skip-separation`.
- [ ] **DCF-108 [P1]** Measure separation runtime.

DCF-100–103 implemented on 2026-09-12 as the first Phase 1 slice. The
`prepare-audio` command uses explicit FFmpeg/ffprobe executables, outputs mono
44.1 kHz PCM WAV, and caches by source content plus normalization configuration.
Unit gates passed on Linux portability/Python 3.12; native Windows and real-audio
execution remain required before Phase 1 acceptance. No model or audio was added.

### Transcription

- [x] **DCF-109 [P0]** Implement `Transcriber` interface.
- [x] **DCF-110 [P0]** Implement first ADTOF-compatible transcriber.
- [x] **DCF-111 [P0]** Export raw drum MIDI.
- [x] **DCF-112 [P0]** Preserve onset timestamps.
- [ ] **DCF-113 [P1]** Preserve velocity.
- [ ] **DCF-114 [P1]** Preserve confidence when backend exposes it.
- [x] **DCF-115 [P1]** Add configurable detection thresholds.

DCF-107 and DCF-110–112/115 were implemented on 2026-09-12. The isolated
ADTOF adapter forces CPU, validates the allowlisted checkpoint size/SHA256,
requires strict state loading, preserves unquantized backend timing, rejects
existing outputs and supports uniform or five-instrument thresholds. A synthetic
two-second WAV produced a parseable raw MIDI through the real pinned backend;
this is execution evidence, not musical-accuracy or private-song validation.

### Spike validation

- [ ] **DCF-116 [P0]** Run pipeline on local `Turn to Ashes` audio.
- [ ] **DCF-117 [P0]** Verify generated MIDI opens in a DAW/MIDI inspector.
- [x] **DCF-118 [P0]** Count events by MIDI note/instrument.
- [x] **DCF-119 [P0]** Generate debug CSV.
- [ ] **DCF-120 [P1]** Listen/inspect first 30 seconds against audio.
- [ ] **DCF-121 [P1]** Record obvious false positives/false negatives.
- [ ] **DCF-122 [P0]** Document Phase 1 findings.

### Phase 1 diagnostic support — 2026-10-16

- [x] **DCF-123 [P1]** Add a project-local drum-audio diagnostic skill and bounded
  spectrogram/report script; verify on authored synthetic signals. Correct public
  HH/TT threshold translation to pinned ADTOF class order and add regression coverage.

This 2026-10-16 support slice did not complete DCF-114 or DCF-116–122. No failing private
audio, MIDI, stems or model checkpoint is available in this checkout. The core
separator remains passthrough; Moises is an optional external stem source, not
an implemented integration. See docs/drum-audio-diagnostics.md for evidence and
the measured next experiment. Phase 1 remains in progress.

### Phase 1 raw MIDI diagnostics — 2026-10-20

DCF-118/119 now have `drumforge inspect-midi`: counts by GM note/group plus
report.json/events.csv with onset seconds, stored MIDI velocities, source identity
and tempo changes. It preserves simultaneous/duplicate attacks and the source,
warns about ignored melodic channels/unknown notes and refuses unsafe outputs or
game-format PART DRUMS inputs. Fifteen synthetic regressions and a skill-guided
authored-audio/MIDI demonstration passed. See docs/phase-1-midi-diagnostics.md.
These are implemented diagnostic capabilities; applying them to Turn to Ashes
still depends on the unavailable private audio/checkpoint and native Windows run.
DCF-113/114 and DCF-116/117/120–122 remain open. Phase 1 is not complete.

### Phase 1 five-song chart-reference experiment — 2026-10-27

- [x] **DCF-124 [P1]** Use five existing chart/audio pairs to study spectral
  evidence, compare mix/drums, calibrate bounded rules with whole-song holdouts,
  and retain profiles, metrics, reproducible recipes and the project skill workflow.

Completed the explicitly requested reference experiment: Numb, All Apologies,
Come Together, The Number of the Beast and Forsaken; 36 pinned input files,
ten 20-second excerpts and 860 target proxy events per audio mode. Baseline and
calibrated rules were tested leaving each song out in turn. Mix F1 improved for
kick/snare proxies (0.385→0.599 / 0.339→0.468) but yellow-cymbal F1 fell
(0.472→0.456). This does not establish hi-hat identification or ADTOF improvement.
Code, seven optional DSP checks, thirteen core cases (117 total), reference PNGs,
HTML/CSV/JSON, recipe, spectral profile and skill guidance delivered. See
docs/five-song-chart-reference.md. Phase 1, acoustic annotation, ADTOF comparison,
Turn to Ashes and native Windows/game acceptance remain open.

### Phase 1 frozen-profile evaluation on CoD/A7X — 2026-10-27

- [x] **DCF-125 [P1]** Evaluate the existing spectral profile on other CoD and
  Avenged Sevenfold songs without recalibration; preserve results and extend the skill.

115, Carry On, Not Ready To Die, Afterlife and Brompton Cocktail supplied ten
fixed excerpts, 200 seconds and 1,157 target references in mix mode. Drum-stem
comparison is limited to the latter two songs. Twenty-five input files and the
unchanged frozen profile are pinned. Text-chart reference parsing, external-data
guards and an evaluation command were added. Mix F1: kick 0.428→0.424, snare proxy
0.395→0.513, yellow cymbal 0.218→0.279, with lost recall. Carry On remains an
unresolved poor match; 115's excerpts have zero yellow-cymbal references.
129 core plus eight optional DSP tests passed. See docs/cod-a7x-heldout.md.
This completes the requested external experiment, not acoustic annotation,
ADTOF comparison, native Windows/game acceptance or overall Phase 1.

### Phase 1 Linkin Park hi-hat reference study — 2026-10-27

- [x] **DCF-126 [P1]** Inspect Faint/Crawling as timekeeping hi-hat references,
  preserve the frozen-profile comparison and resolve disco-flip chart semantics.

The user suggested these two local pairs. Four fixed excerpts supply 80 seconds,
508 mix references and 40 seconds of Crawling drums. Expert disco-flip markers
exposed incorrect red/yellow reference groups in Crawling. The reader now resolves
MIDI/.chart states while retaining source notes/times/velocities; 422 full-song
groups change, and the previous ten songs plus Faint keep identical events.
Original yellow-Pro F1 exceeds the frozen profile on Faint/mix, Crawling/mix and
Crawling/drums. All 141 core and eight optional DSP tests, static gates, locks
and build passed on Linux. See docs/linkin-park-hihat.md.
This support experiment does not complete acoustic annotation, ADTOF comparison,
native Windows/game acceptance or overall Phase 1.

### Phase 1 explicit component references and public sample — 2026-10-27

- [x] **DCF-127 [P1]** Audit actual local stem signals, compare explicit component
  sources on the discussed songs, add chart-free component candidates and inspect
  a bounded free public reference while retaining findings in the project skill.

Seven songs/38 pinned files supply 280 seconds of mix. Only Afterlife/Crawling
provide useful drums/components for this comparison: 80 seconds/511 references.
Brompton's silent drum excerpts are excluded and class-specific coverage is
reported. Components improve snare/yellow agreement and worsen kick with unchanged
rules. predict-components works without chart input. Seven public author MP3s
from the StemGMD/LarsNet demo (3.35 MB) are source/hash verified and compared;
this is not local model inference. All 141 core and 13 optional DSP tests, locks,
static gates and build passed; input/profile hashes and archive hygiene verified.
See docs/stem-component-study.md. DCF-105/106, ML/game/native acceptance remain open.

### Phase 1 broad song survey — 2026-10-27

- [x] **DCF-128 [P1]** Survey many additional chart/audio pairs with frozen rules,
  artist-balanced selection, source/coverage audits, per-song uncertainty and
  reusable pattern findings in the project skill.

64 new songs/20 artists completed 128 fixed excerpts: 2,560 nominal seconds,
352 pinned inputs and 14,534 mix references. There are 30 useful drum-source pairs
and 12 component-source pairs. Mix F1 improves with major recall losses; component
snare gains persist but the earlier strong HH gain does not generalize. Density,
simultaneity and absent-reference cases are reported, with a post-score temporal
control. Full rerun reproduces all candidate/reference CSVs; real resume reuses
64 verified reports. All 146 combined core and 19 optional DSP tests, lock/static/
build gates and media hygiene pass on Linux. A CRC/SHA-verified 570-file report
ZIP is prepared; remote themed-library additions are preserved. See
docs/broad-song-survey.md. This does not complete ML, acoustic labels, exporter,
native Windows/game acceptance or overall Phase 1.

---

## Phase 2 — Canonical Event Pipeline

### Domain model

- [ ] **DCF-200 [P0]** Define `DrumInstrument`.
- [ ] **DCF-201 [P0]** Define immutable `DrumHit`.
- [ ] **DCF-202 [P0]** Define song metadata model.
- [ ] **DCF-203 [P1]** Define optional tempo-map model.

### Normalization

- [ ] **DCF-204 [P0]** Convert backend output to `DrumHit[]`.
- [ ] **DCF-205 [P0]** Sort/validate timestamps.
- [ ] **DCF-206 [P0]** Validate MIDI velocity range.
- [ ] **DCF-207 [P1]** Handle duplicate near-simultaneous events.
- [ ] **DCF-208 [P1]** Preserve source MIDI note.
- [ ] **DCF-209 [P1]** Preserve source/backend metadata.
- [ ] **DCF-210 [P1]** Map unknown instruments explicitly to `UNKNOWN`.
- [ ] **DCF-211 [P1]** Generate normalized JSON/CSV diagnostics.

### Tests

- [ ] **DCF-212 [P0]** Unit tests for canonical mappings.
- [ ] **DCF-213 [P0]** Unit tests for timestamp ordering.
- [ ] **DCF-214 [P1]** Unit tests for duplicate suppression.
- [ ] **DCF-215 [P1]** Golden event fixtures.

---

## Phase 3 — Clone Hero Exporter

### Metadata/package

- [ ] **DCF-300 [P0]** Generate valid `song.ini`.
- [ ] **DCF-301 [P0]** Sanitize song folder names.
- [ ] **DCF-302 [P0]** Copy/link chosen local audio to generated song folder.
- [ ] **DCF-303 [P1]** Add charter metadata (`Drum Chart Forge` + version/model provenance).

### Pro Drums mapping

- [ ] **DCF-304 [P0]** Map snare → red.
- [ ] **DCF-305 [P0]** Map toms → yellow/blue/green pads.
- [ ] **DCF-306 [P0]** Map hi-hat → yellow cymbal.
- [ ] **DCF-307 [P0]** Map ride/crashes according to configurable cymbal policy.
- [ ] **DCF-308 [P0]** Map kick.
- [ ] **DCF-309 [P1]** Warn on target-format lane collisions.
- [ ] **DCF-310 [P1]** Preserve double-crash intent where possible.

### MIDI/chart generation

- [ ] **DCF-311 [P0]** Choose initial `notes.mid` or `.chart` output.
- [ ] **DCF-312 [P0]** Implement serializer.
- [ ] **DCF-313 [P0]** Include tempo/time-signature events required by target.
- [ ] **DCF-314 [P0]** Emit Expert Pro Drums track.
- [ ] **DCF-315 [P0]** Validate generated file structure.
- [ ] **DCF-316 [P0]** Implement `drumforge validate`.

### Clone Hero acceptance

- [ ] **DCF-317 [P0]** Clone Hero Scan Songs detects generated song.
- [ ] **DCF-318 [P0]** Song appears with correct title/artist.
- [ ] **DCF-319 [P0]** Pro Drums is selectable.
- [ ] **DCF-320 [P0]** Kick/snare/cymbal/tom notes render.
- [ ] **DCF-321 [P0]** Song plays without chart parser errors.
- [ ] **DCF-322 [P0]** Record screenshots/log observations in docs without committing copyrighted media.

---

## Phase 4 — Turn to Ashes Playability

### Timing

- [ ] **DCF-400 [P0]** Measure start alignment.
- [ ] **DCF-401 [P0]** Verify no obvious cumulative drift.
- [ ] **DCF-402 [P1]** Estimate tempo map if needed.
- [ ] **DCF-403 [P1]** Support pickup before first full measure.

### Accuracy audit

- [ ] **DCF-404 [P0]** Audit first 30 seconds.
- [ ] **DCF-405 [P0]** Audit one dense chorus/heavy section.
- [ ] **DCF-406 [P0]** Audit one fill/tom-heavy section.
- [ ] **DCF-407 [P0]** Audit one ride/crash-heavy section.
- [ ] **DCF-408 [P1]** Track precision-like manual observations by instrument.
- [ ] **DCF-409 [P1]** Track false negatives by instrument.
- [ ] **DCF-410 [P1]** Tune confidence thresholds.

### Playability

- [ ] **DCF-411 [P0]** Play generated chart using user's e-kit in Clone Hero.
- [ ] **DCF-412 [P0]** Record systematic mapping errors.
- [ ] **DCF-413 [P0]** Fix mapping/configuration rather than hand-editing individual notes where possible.
- [ ] **DCF-414 [P0]** Reach "useful practice chart" quality.
- [ ] **DCF-415 [P1]** Produce reproducibility config for this song without distributing the audio.

---

## Phase 5 — Musical Quality

### Quantization

- [ ] **DCF-500 [P1]** Implement optional quantization.
- [ ] **DCF-501 [P1]** Support 1/8, 1/16, 1/32.
- [ ] **DCF-502 [P1]** Explore triplet grids.
- [ ] **DCF-503 [P1]** Implement adaptive/confidence-aware quantization.
- [ ] **DCF-504 [P1]** Reject excessive timestamp displacement.

### Tempo/meter

- [ ] **DCF-505 [P1]** Tempo estimation backend abstraction.
- [ ] **DCF-506 [P1]** Constant-tempo estimator.
- [ ] **DCF-507 [P2]** Variable tempo map.
- [ ] **DCF-508 [P2]** Meter estimation.
- [ ] **DCF-509 [P2]** Non-4/4 validation fixtures.

### Drumming semantics

- [ ] **DCF-510 [P1]** Better open/closed hi-hat classification.
- [ ] **DCF-511 [P1]** Better ride vs crash classification.
- [ ] **DCF-512 [P1]** Better tom-height classification.
- [ ] **DCF-513 [P1]** Double-kick detection/Expert+ generation.
- [ ] **DCF-514 [P2]** Ghost note generation from velocity/confidence.
- [ ] **DCF-515 [P2]** Accent generation.
- [ ] **DCF-516 [P2]** Flam handling.
- [ ] **DCF-517 [P2]** Roll/swell handling.

---

## Phase 6 — CLI & Reproducibility

- [ ] **DCF-600 [P1]** Stable `drumforge generate`.
- [ ] **DCF-601 [P1]** Stable `drumforge transcribe`.
- [ ] **DCF-602 [P1]** Stable `drumforge inspect`.
- [ ] **DCF-603 [P1]** Batch directory processing.
- [ ] **DCF-604 [P1]** Config file support.
- [ ] **DCF-605 [P1]** Seed/version/model provenance in report.
- [ ] **DCF-606 [P1]** Cache intermediate stems/transcriptions.
- [ ] **DCF-607 [P1]** `--force` / safe overwrite behavior.
- [ ] **DCF-608 [P1]** Progress reporting.
- [ ] **DCF-609 [P1]** Human-readable error messages.
- [ ] **DCF-610 [P1]** Installation documentation for WSL/Windows.
- [ ] **DCF-611 [P2]** Native Windows packaging.
- [ ] **DCF-612 [P2]** CI matrix.

---

## Phase 7 — Evaluation & Human Correction

- [ ] **DCF-700 [P2]** Side-by-side raw vs normalized event viewer.
- [ ] **DCF-701 [P2]** Confidence histogram.
- [ ] **DCF-702 [P2]** Instrument-specific thresholds.
- [ ] **DCF-703 [P2]** Manual correction file that overlays generated output.
- [ ] **DCF-704 [P2]** Regeneration that preserves manual corrections.
- [ ] **DCF-705 [P2]** Export correction data for model evaluation.
- [ ] **DCF-706 [P2]** Compare multiple transcription backends.
- [ ] **DCF-707 [P2]** Benchmark corpus using only legally redistributable/open data.

---

## Phase 8 — Optional GUI / Product

Do not start until the CLI pipeline is reliable.

- [ ] **DCF-800 [P2]** Waveform + event visualization.
- [ ] **DCF-801 [P2]** Click-to-correct instrument.
- [ ] **DCF-802 [P2]** Drag timing correction.
- [ ] **DCF-803 [P2]** Section loop playback.
- [ ] **DCF-804 [P2]** Difficulty derivation (Hard/Medium/Easy).
- [ ] **DCF-805 [P2]** Clone Hero Songs-folder export shortcut.
- [ ] **DCF-806 [P2]** Optional desktop packaging.

---

## Separate workstream — MixDrumRock song library

Authorized by the user on 2026-10-16, independently of the transcription phases.
See song-library/README.md for scope, evidence and the continuation prompt.

- [x] **DCF-LIB-001 [P0]** Create a portable library area, private-data ignore rule,
  metadata templates and a documented staged workflow. No downloader is implied.
- [-] **DCF-LIB-002 [P0]** Import the real playlist and inventory existing songs.
  Public Qobuz playlist 69773629 refreshed completely: 744 entries, CSV/XLSX/JSON,
  original order and version metadata preserved. Reusable metadata exporter and
  pagination safeguards verified. Existing-library inventory is still not supplied.
- [x] **DCF-LIB-003 [P0]** Inspect RhythmVerse search/download behavior for drums
  and implement matching with recorded sources and reviewable ambiguous versions.
  Cached CH/PS/RB3/all searches, conservative version/duration matching and source
  receipts implemented. Public ZIP/RAR/7z, Drive files/folders, MediaFire, short links
  and authenticated public MEGA downloads exercised. Unavailable/ambiguous sources
  are recorded rather than counted as prepared.
- [-] **DCF-LIB-004 [P0]** Validate a small pilot, choose conversion by actual input
  format, verify drums/Pro Drums and obtain the user's Scan Songs/playtest result.
  Twelve native songs prepared: Expert four-lane drums and Pro Drums evidence,
  40 audio assets decoded, ZIP extracted and hashes checked. Heart-Shaped Box's
  five-lane candidate was replaced with Dumb. User confirmed pilot delivery;
  explicit Scan Songs/playtest acceptance remains pending.
- [x] **DCF-LIB-005 [P1]** Implement resumable acquisition/preparation, preserve
  existing files, and export a ZIP of song folders with a missing/blocked report.
  Resumable batch acquisition, atomic preparation, pinned standalone PC recovery,
  separate Pro/ordinary Drums batches, original retention, local edit preservation,
  partial ZIP/failure handling and a complete coverage CSV delivered. Linux checks
  passed; new Windows conversions/game acceptance still need user execution.
- [-] **DCF-LIB-006 [P1]** Support incremental playlist updates without losing
  selections or repeating verified downloads; check space and Windows path limits.
  Immutable append-only recipes preserve Qobuz selections; repeat-run source/assets
  and ZIP checks, disk budgeting and Windows path guards implemented. Offline
  snapshot-extension regression passed. Whole-workflow updates against the user's
  existing library and native Windows conversion checks remain pending.
- [x] **DCF-LIB-007 [P0]** Recover the missing pilot and provide a durable local
  download/preparation route after cloud files disappeared. Twelve sources and
  all 78 runtime files revalidated; pinned metadata recipe and standalone Python
  recovery tested without external libraries, including repeat-run preservation.
  Windows user instructions are in song-library/BAIXAR.md. Browser download from
  the cloud UI and native Windows execution are not claimed as verified.
- [x] **DCF-LIB-008 [P0]** Process the remaining public playlist snapshot and
  deliver every validated selection with durable recovery and explicit gaps.
  254 additional charts: 246 Pro Drums, eight ordinary four-lane Drums, 11 ZIPs,
  1,449 runtime assets and 629 decoded audio files. With the pilot, 266 charts cover
  275 of 744 entries. The remaining 469 comprise 358 not found conservatively,
  50 version reviews and 61 access/preparation blockers. This completes this bulk
  preparation pass, not full-playlist coverage or game acceptance.
- [x] **DCF-LIB-009 [P0]** Correct Windows Onyx invocation and preserve diagnostics
  after the user's batch-08 import failures. Remove unsupported Windows RTS flags,
  keep the Linux CPU limit, retain per-attempt logs and supply a cache-preserving
  update/resume command. All 70 tests passed; three real source conversions,
  pinned MIDI, 17 asset hashes, logs and unchanged resume checked on Linux.
  Native Windows retry/game acceptance still requires the user's result.
- [x] **DCF-LIB-010 [P0]** Provide a local complement for the user's renamed
  existing song folders without uploading ~4 GB. Stdlib scanner, content/INI
  matching, present-batch precedence, old-copy deduplication, edition/duration
  reviews, immutable inputs, ZIP64 export and CSV/JSON reports implemented.
  Thirteen regressions and standalone real-collection checks passed on Linux;
  the user's actual inventory, Windows run and game acceptance remain pending.
- [x] **DCF-LIB-011 [P0]** Clarify silent Onyx waits and Ctrl+C behavior after
  the user's Windows report. Print stage/deadline/log and periodic elapsed waits;
  close child stdin and report interruption/resume without a traceback. Same-source
  Linux import succeeded in 1.35 s; full conversion/MIDI/local hashes/resume also
  checked. Two regressions bring the suite to 85 tests. The native log contains
  only import-start text; the cause of Windows slowness remains under investigation.
- [x] **DCF-LIB-012 [P0]** Correct misleading converter timing and supervise the
  actual process deadline after a reported 731 s import with a 180 s label.
  Separate creation/wait/reporting, bound reporter shutdown, record per-stage
  timing events and kill/reap the owned child on timeout. Four regressions include
  a real timed-out child and blocked output; full Stain conversion/pinned MIDI/
  local hashes/resume verified on Linux. The specific cause of native Windows
  delay and acceptance of the update there remain unestablished.
- [x] **DCF-LIB-013 [P0]** Prepare nonrepeating themed drum batches for League of
  Legends, Imagine Dragons and bands similar to Linkin Park. Batches 13–18 append
  45 charts (39 Pro Drums, six ordinary Drums): 11 LoL/associated projects,
  13 Imagine Dragons and 21 across seven similar bands. All 244 assets, 107 audio
  files, 51,469 Expert gems and six ZIPs checked; index/novelty regressions bring
  the suite to 91 passing tests. Old recipes, Qobuz coverage and Onyx helper bytes
  preserved; standalone fresh-source recovery/resume checked for ZIP, Drive files
  and Onyx. Windows selective recovery and song lists: song-library/TEMATICOS.md.
  Nine attempted selections remain blocked, three theme titles were not found
  conservatively and Heavy Is the Crown was excluded as already delivered.
  Native Windows execution and Scan Songs/playtest remain pending.

- [x] **DCF-LIB-014 [P0]** Complete the Linkin Park catalog preparation pass:
  207 new charts in batches 19–30, 172 Pro Drums and
  35 ordinary Drums; the 33 earlier band charts are retained.
  Given Up remains once in batch 02. All 475 drum-catalog packages/255 grouped
  editions considered, plus explicit album-reference gaps and targeted non-drum
  package checks. 1527 runtime assets, 871 decoded audio assets,
  253,421 Expert gems and 12 ZIPs checked. Actual-container acquisition,
  pinned band-only recovery of old/new recipes and local additions comparison
  implemented; 155 core tests, 19 optional DSP checks and all artifact gates passed.
  Concurrent diagnostic work from origin/main was retained. Fresh stdlib-only
  reconstruction, offline resume and real-song additions export verified on Linux.
  Old recipes, Qobuz coverage and Onyx helper bytes preserved. Durable Windows
  route/song lists: song-library/LINKIN-PARK.md. This completes the preparation
  pass, not full discography availability or native Windows/game acceptance.

No real songs were searched, downloaded, converted or verified in the game during
the organization slice. DCF-LIB-001 completion does not complete the workstream.
The subsequent metadata-export slice captured the playlist only; it did not
download audio or prepare charts. The workstream remains in progress.
The user then explicitly authorized at least ten songs for a later playtest.
That preparation slice delivered twelve in a private ZIP; game acceptance and
the full-playlist workflow remain incomplete.
On 2026-10-17 the cloud link failed because ignored outputs were absent after a
machine restart. The pilot was reconstructed and a PC recovery recipe delivered;
user Scan Songs/playtest remains pending. Do not treat an ignored workspace path
as a persistent download or as a file that GitHub will restore.

The user subsequently confirmed successful delivery and authorized the remainder.
The 2026-10-17 bulk pass and recovery instructions are in song-library/CONTINUACAO.md;
metadata-only recipes and reports are versioned. No media/models entered Git and
the transcription phases were not advanced. Provider quotas, unavailable sources,
uncertain editions and game acceptance keep the overall workstream open.

# Immediate next milestone

Do **not** work on the whole backlog.

Phase 0 is complete. Continue Phase 1 with DCF-116/117/120–122 using the existing
audio preparation/transcription and the DCF-118/119 inspector. Follow the local
drum-audio-diagnostics skill for every music-to-chart task. Private audio,
allowlisted local weights/backend and native Windows results are still needed.
Do not advance the canonical-event pipeline or Clone Hero exporter in this slice.

The first meaningful product checkpoint is:

> A local audio file can be transformed into a drum MIDI with inspectable timestamps and instrument assignments.

The first end-to-end user checkpoint is:

> Turn to Ashes is generated automatically, scanned by Clone Hero, and selectable as Expert Pro Drums.
