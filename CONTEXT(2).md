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

**Phase 0 — Research & Bootstrap**

See `BACKLOG.md` / `docs/backlog.md`.

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
