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

- [ ] **DCF-104 [P0]** Implement `Separator` interface.
- [ ] **DCF-105 [P0]** Implement first separation backend.
- [ ] **DCF-106 [P0]** Generate isolated/estimated drums stem from full mix.
- [ ] **DCF-107 [P1]** Add `--skip-separation`.
- [ ] **DCF-108 [P1]** Measure separation runtime.

DCF-100–103 implemented on 2026-09-12 as the first Phase 1 slice. The
`prepare-audio` command uses explicit FFmpeg/ffprobe executables, outputs mono
44.1 kHz PCM WAV, and caches by source content plus normalization configuration.
Unit gates passed on Linux portability/Python 3.12; native Windows and real-audio
execution remain required before Phase 1 acceptance. No model or audio was added.

### Transcription

- [ ] **DCF-109 [P0]** Implement `Transcriber` interface.
- [ ] **DCF-110 [P0]** Implement first ADTOF-compatible transcriber.
- [ ] **DCF-111 [P0]** Export raw drum MIDI.
- [ ] **DCF-112 [P0]** Preserve onset timestamps.
- [ ] **DCF-113 [P1]** Preserve velocity.
- [ ] **DCF-114 [P1]** Preserve confidence when backend exposes it.
- [ ] **DCF-115 [P1]** Add configurable detection thresholds.

### Spike validation

- [ ] **DCF-116 [P0]** Run pipeline on local `Turn to Ashes` audio.
- [ ] **DCF-117 [P0]** Verify generated MIDI opens in a DAW/MIDI inspector.
- [ ] **DCF-118 [P0]** Count events by MIDI note/instrument.
- [ ] **DCF-119 [P0]** Generate debug CSV.
- [ ] **DCF-120 [P1]** Listen/inspect first 30 seconds against audio.
- [ ] **DCF-121 [P1]** Record obvious false positives/false negatives.
- [ ] **DCF-122 [P0]** Document Phase 1 findings.

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

# Immediate next milestone

Do **not** work on the whole backlog.

Start with:

```text
DCF-001 → DCF-042
```

Then the next session should target:

```text
DCF-100 → DCF-122
```

The first meaningful product checkpoint is:

> A local audio file can be transformed into a drum MIDI with inspectable timestamps and instrument assignments.

The first end-to-end user checkpoint is:

> Turn to Ashes is generated automatically, scanned by Clone Hero, and selectable as Expert Pro Drums.
