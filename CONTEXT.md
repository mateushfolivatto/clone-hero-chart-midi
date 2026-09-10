# Drum Chart Forge — CONTEXT

## Mission

Automatically transform a music file into a useful **Clone Hero Expert Pro Drums** chart, so the user does not need to manually place thousands of drum notes.

## First validation target

**Turn to Ashes** is the first end-to-end test song.

The test audio exists only as a local/private asset. It must not be committed or redistributed by this repository.

## Scope

The project owns:

- local audio preprocessing;
- optional drum/source separation;
- automatic drum transcription;
- canonical drum-event normalization;
- Clone Hero Pro Drums mapping/export;
- diagnostics and validation;
- later, optional human correction tooling.

The project does not own:

- Clone Hero gameplay;
- e-drum MIDI input;
- Clone Hero scoring/rendering;
- music distribution.

## Architectural invariant

```text
Audio
  ↓
Separator interface
  ↓
Transcriber interface
  ↓
DrumHit[]
  ↓
Normalization
  ↓
Clone Hero exporter
```

The canonical `DrumHit` model is the boundary between machine-learning/audio inference and game-format export.

## Key engineering decisions

1. **Python-first** because the audio/MIR/ML ecosystem is Python-centric.
2. **CLI-first** to validate the pipeline before any GUI.
3. **uv** preferred for reproducible Python project/dependency management.
4. **No Rust initially**; optimize only after profiling.
5. **No web API/database/Docker initially** without a demonstrated need.
6. Preserve raw onset timestamps before optional quantization.
7. Keep source-separation and transcription backends replaceable.
8. Keep Clone Hero mapping isolated from ML/transcription internals.
9. Start with **Expert Pro Drums only**.
10. Treat copyrighted audio as local/private input, never repository content.
11. Create a dedicated branch before every new unit of changes. After validation,
    commit on that branch and merge into main; every completed phase must be
    committed and merged. This is the user's standing Git workflow instruction.

## Candidate technology

- ADTOF/ADTOF-pytorch family for drum transcription.
- MDX23C or another viable backend for source/drum separation.
- `midi2clonehero` as a reference for Pro Drums conversion rules.
- Clone Hero official format documentation as the target behavior.

Do not freeze these choices until compatibility and licensing are documented.

## Major risk: licensing

Wrapper code, original model code, datasets, and model weights can have different licenses.

Before public distribution:
- audit each dependency;
- audit model-weight terms separately;
- document commercial-use restrictions;
- document redistribution/attribution requirements.

Remain conservative until this is resolved.

## Definition of useful

The generated chart does not need perfect transcription to be useful.

Success means:
- automatically generated;
- synchronized;
- broadly correct kick/snare/hi-hat/tom/cymbal mapping;
- playable in Clone Hero;
- manual work becomes correction rather than full transcription.

## Current phase

**Phase 0 — Research & Bootstrap completed (2026-09-10).**

See `BACKLOG.md` for task status and `docs/phase-0-verification.md` for evidence.
Always reread `lessons.md` alongside the backlog and after context recovery.

Bootstrap provides a standard-library argparse CLI with help and doctor, pytest,
Ruff, strict mypy, uv.lock and locked Hatchling build dependencies. Only native
Windows/Python 3.12 was validated. No transcription or exporter is implemented.

Reuse the existing clone-hero-chart-midi Git repository and main branch rather
than replace history or rename its remote. Python distribution: drum-chart-forge;
CLI: drumforge. BACKLOG.md is canonical; docs/backlog.md is only a status summary.

ML remains optional and uninstalled. ADTOF code/checkpoint terms and exact backend
compatibility are unresolved; a local research audit does not authorize redistribution.
The next smallest milestone is an isolated CPU dependency/checkpoint readiness
spike toward DCF-100 through DCF-122. Pin source and checkpoint identity, explicitly
reject missing weights, disclose downloads, and establish a short reproducible
test before processing Turn to Ashes. Do not jump to canonical/exporter phases.

## Do not do yet

- GUI
- web service
- mobile app
- database
- Rust rewrite
- model training
- multi-user infrastructure
- four difficulty levels
- fully automatic publication/distribution of copyrighted songs

## First end-to-end acceptance

```text
input song
   ↓
drum transcription
   ↓
normalized events
   ↓
Clone Hero song folder
   ↓
Scan Songs succeeds
   ↓
Expert Pro Drums selectable
   ↓
user plays it on e-drums
```
