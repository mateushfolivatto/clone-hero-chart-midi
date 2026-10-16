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
5. No web API/database initially; do not use Docker as an environment workaround.
6. Preserve raw onset timestamps before optional quantization.
7. Keep source-separation and transcription backends replaceable.
8. Keep Clone Hero mapping isolated from ML/transcription internals.
9. Start with **Expert Pro Drums only**.
10. Treat copyrighted audio as local/private input, never repository content.
11. Create a dedicated branch before every new unit of changes. After validation,
    commit on that branch and merge into main; every completed phase must be
    committed and merged. Push `main` to `origin` after each successful merge;
    authentication failures must be reported without rewriting local history.
    This is the user's standing Git workflow instruction.

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

Native Windows is the primary environment for this stage, including development,
tests and future chart generation. CPU is the minimum supported execution target;
CUDA/GPU is optional acceleration and its absence is not an error. Linux/WSL must
remain supportable later, never required. Do not install WSL, use docker-desktop,
introduce Docker workarounds or modify this college PC's administrative policies.

Validated host: Windows 10, PowerShell 7.4.13, Python 3.12.0, uv 0.12.13, VS Code,
4 logical CPUs, 15.9 GiB RAM, Intel HD Graphics 630, no NVIDIA/CUDA. WSL contains
only docker-desktop and must not be used. See docs/environment.md.

**Phase 0 — Research & Bootstrap completed (2026-09-10).**

See `BACKLOG.md` for task status and `docs/phase-0-verification.md` for evidence.
Always reread `lessons.md` alongside the backlog and after context recovery.

Bootstrap provides a standard-library argparse CLI with help and doctor, pytest,
Ruff, strict mypy, uv.lock and locked Hatchling build dependencies. Only native
Windows/Python 3.12 was validated. Phase 1 now has audio preparation and a raw
ADTOF MIDI command; no Clone Hero exporter is implemented.

Reuse the existing clone-hero-chart-midi Git repository and main branch rather
than replace history or rename its remote. Python distribution: drum-chart-forge;
CLI: drumforge. BACKLOG.md is canonical; docs/backlog.md is only a status summary.

ML remains optional and uninstalled. ADTOF code/checkpoint terms and exact backend
compatibility are unresolved; a local research audit does not authorize redistribution.
Before DCF-100 onward, perform a Windows/Python 3.12 CPU compatibility audit of
dependencies and checkpoints. Do not implement Phase 1 in that audit. Distinguish
wheel/source compatibility evidence from actual inference validation. Await the
user's next instruction before starting implementation.

**Phase 1 in progress (2026-09-12).** DCF-100–103 now provide metadata probing,
FFmpeg normalization, original preservation and content/config caching through
`drumforge prepare-audio`. The slice has portable unit coverage but still needs
native Windows execution with real local audio. A later slice added the strict,
CPU-only ADTOF adapter and raw MIDI output, validated with synthetic audio only.

The pre-Phase 1 compatibility audit completed on 2026-09-11. The smallest native
path is portable FFmpeg normalization followed by pinned ADTOF-pytorch and
PyTorch CPU, with source separation disabled initially. A synthetic WAV-to-MIDI
smoke succeeded on this host; this is not a quality claim. See
`docs/phase-1-windows-compatibility.md`. ADTOF code licensing and ADTOF/MDX weight
terms still block redistribution. DCF-100 onward remains unstarted and requires
the user's explicit next instruction.

## Separate song-library workstream (2026-10-16)

The user requested a separate, portable area for the growing MixDrumRock Qobuz
playlist (600+ tracks), existing drums charts from RhythmVerse, conversion when
needed, and a ZIP of extracted song folders for personal Clone Hero use.
`song-library/README.md` records this workflow and its limits; templates are
versioned while all private collection data stays in ignored `song-library/data/`.
This request authorizes library organization and investigation independently of
the MP3 transcription phases; it does not complete any Phase 1 acceptance item.
No playlist or chart package has been received. RhythmVerse access currently fails
at the environment proxy, so site integration/conversion remains unverified.
Do not promise complete coverage or infer drums from a Guitar Hero III label.
The collection should preserve source audio/chart pairing, existing songs and
manual choices, use relative paths, and distinguish structural checks from actual
user-confirmed game compatibility. See DCF-LIB items in BACKLOG.md for status.

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
