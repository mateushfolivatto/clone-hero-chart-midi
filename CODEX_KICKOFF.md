# Drum Chart Forge — Codex Kickoff Prompt

> **Use this file as the initial prompt/context for Codex in VS Code.**
>
> Goal: bootstrap a reproducible tool that converts a legally obtained music file into an automatically generated **Clone Hero Expert Pro Drums** chart, minimizing manual charting.

---

## 1. Mission

Build **Drum Chart Forge**, a local-first pipeline that takes an audio file (`.mp3`, `.wav`, `.flac`) and produces a Clone Hero song folder containing, at minimum:

```text
<Artist> - <Song>/
├── song.ini
├── notes.mid or notes.chart
└── song.ogg / song.mp3 / song.wav
```

The first real end-to-end validation song is:

- **Turn to Ashes**
- Artist/credits used by the user: Kevin Sherwood / Elena Siegman
- Target instrument: **Expert Pro Drums**
- The actual audio file is a local test asset and MUST NOT be committed to Git.

The application should eventually support a command conceptually similar to:

```bash
drumforge generate "/path/to/song.mp3" \
  --title "Turn to Ashes" \
  --artist "Kevin Sherwood" \
  --output "./out"
```

Expected result:

```text
out/
└── Kevin Sherwood - Turn to Ashes/
    ├── song.ini
    ├── notes.mid
    └── song.mp3
```

The generated folder should be scannable by Clone Hero and expose a playable **Pro Drums** track.

---

## 2. Product principle

The project is **not** a Clone Hero replacement.

Clone Hero already provides:

- gameplay;
- MIDI e-drum input;
- scoring;
- Pro Drums rendering;
- practice/gameplay UX.

Our value is the missing pipeline:

```text
music audio
   ↓
drum/source separation
   ↓
automatic drum transcription
   ↓
normalized drum events
   ↓
tempo/timing representation
   ↓
Clone Hero Pro Drums export
   ↓
playable song folder
```

The core problem is reducing manual note-by-note charting.

---

## 3. First milestone

The first milestone is an end-to-end proof of concept:

```text
Turn to Ashes audio
    ↓
automatic transcription
    ↓
MIDI drum events
    ↓
Clone Hero-compatible chart/song folder
    ↓
Clone Hero successfully scans it
    ↓
user can select Expert Pro Drums
```

It does **not** need to be perfectly transcribed in Milestone 1.

The milestone succeeds if:

1. the pipeline runs locally;
2. it produces deterministic/reproducible outputs for the same configuration;
3. the output is syntactically valid;
4. Clone Hero scans the generated folder;
5. Pro Drums is selectable;
6. kick/snare/hi-hat/toms/cymbals are broadly mapped to sensible lanes;
7. timing is close enough to evaluate where the transcription model fails.

---

## 4. Environment

Primary development environment:

- Windows host
- WSL Ubuntu
- VS Code Remote / WSL
- Git + GitHub
- Python
- `uv` preferred for Python dependency/project management

Prefer Python for the first implementation because the relevant MIR/audio/ML ecosystem is Python-centric.

Do not introduce Rust, a web API, Docker, frontend frameworks, databases, or distributed infrastructure unless a demonstrated requirement appears later.

CLI-first.

---

## 5. Candidate external components to investigate

Do not blindly vendor or copy these projects. Inspect their APIs, licenses, maintenance state, compatibility, and model requirements first.

### Drum transcription

Candidate:

- `xavriley/ADTOF-pytorch`
  - audio → MIDI drum transcription
  - PyTorch
  - bundled/default model weights according to its README
  - CLI and programmatic API

Candidate integrated pipeline:

- `xavriley/adtof_plus_drum_transcription`
  - source separation
  - drum stem/component separation
  - ADTOF transcription
  - MIDI export
  - velocity mapping

### Source separation

Investigate an actively usable source-separation backend.

Historical/reference candidate:

- Demucs / Hybrid Transformer Demucs

Important:
- the original `facebookresearch/demucs` repository was archived;
- do not hard-wire the architecture to that repository;
- use an adapter/provider boundary so a separation backend can be replaced.

The integrated ADTOF+ project references MDX23C, which may be preferable for the initial spike.

### MIDI → Clone Hero

Reference implementation:

- `apvilkko/midi2clonehero`

It already demonstrates conversion from General MIDI percussion notes into 4-lane Expert Pro Drums conventions and supports common kick, snare, tom, hi-hat, crash, ride, china and splash notes.

Do not merely shell out to it forever without understanding the mapping. It may be used as:

1. a reference;
2. a temporary adapter;
3. or an external dependency if that proves cleaner.

The project's internal representation must remain independent of any one converter.

---

## 6. Licensing constraint — mandatory

Before choosing dependencies, create:

```text
docs/dependency-licenses.md
```

Record for every external model/library:

- repository/package;
- license;
- whether code and model weights have different terms;
- redistribution constraints;
- commercial-use constraints;
- attribution requirements;
- whether we merely invoke it or distribute it.

Important known risk:

- the original ADTOF repository documents a CC BY-NC-SA 4.0 license;
- related PyTorch/integration repositories may advertise other code licenses;
- **do not infer that model weights are automatically covered by the wrapper's code license**.

Treat this as an engineering/legal-distribution risk to resolve before any public binary/model distribution.

For now the project may remain a research/personal-use local tool.

---

## 7. Copyright / repository hygiene

Never commit copyrighted songs or audio fixtures.

Create `.gitignore` entries for at least:

```gitignore
audio/
fixtures/private/
samples/private/
output/
outputs/
generated/
*.mp3
*.wav
*.flac
```

If a tiny synthetic/openly licensed test audio fixture is later added, place it in a clearly separate allowlisted test directory and document its license.

Generated metadata/chart fixtures are acceptable only if they do not embed copyrighted audio and their provenance is documented.

---

## 8. Architecture

Use clear boundaries.

Recommended logical architecture:

```text
src/drumforge/
├── cli/
├── audio/
│   ├── probe.py
│   └── convert.py
├── separation/
│   ├── base.py
│   └── <backend>.py
├── transcription/
│   ├── base.py
│   └── <backend>.py
├── domain/
│   ├── drum_hit.py
│   ├── instrument.py
│   ├── song.py
│   └── tempo_map.py
├── normalization/
│   ├── mapping.py
│   ├── dedupe.py
│   └── timing.py
├── export/
│   ├── clonehero/
│   │   ├── midi.py
│   │   ├── song_ini.py
│   │   ├── package.py
│   │   └── validate.py
│   └── debug/
└── pipeline.py
```

The exact filenames may change after investigation, but preserve these architectural boundaries:

```text
separation backend
        ↓
transcription backend
        ↓
canonical DrumHit[]
        ↓
normalization
        ↓
Clone Hero exporter
```

The Clone Hero exporter must not know ADTOF internals.

The transcription implementation must not know Clone Hero lane conventions.

---

## 9. Canonical domain model

Create a small, explicit canonical event model.

Example:

```python
@dataclass(frozen=True)
class DrumHit:
    time_seconds: float
    instrument: DrumInstrument
    velocity: int | None
    confidence: float | None
    source_note: int | None = None
```

Candidate canonical instruments:

```text
KICK
SNARE
SIDE_STICK
HI_HAT_CLOSED
HI_HAT_OPEN
HI_HAT_PEDAL
TOM_HIGH
TOM_MID
TOM_LOW
CRASH_1
CRASH_2
RIDE
RIDE_BELL
CHINA
SPLASH
UNKNOWN
```

The model should preserve information even if Clone Hero later has to collapse multiple physical instruments into the same lane.

Do **not** prematurely reduce everything to red/yellow/blue/green.

---

## 10. Clone Hero target

Target:

- 4-lane **Pro Drums**
- Expert difficulty first
- kick support
- cymbal markers
- future support for:
  - 2x kick;
  - ghost notes;
  - accents;
  - rolls;
  - sections;
  - star power;
  - lower difficulties.

The official Clone Hero custom-song structure expects a song folder containing a chart (`notes.chart` or `notes.mid`), an audio file, and `song.ini`.

Prefer generating `notes.mid` initially if that gives the cleanest standards-compatible route. If `.chart` is simpler or more reliable after investigation, document the decision.

Do not use legacy `song.ini delay` as the primary synchronization mechanism.

---

## 11. Timing strategy

Timing is critical.

Do not quantize detected hits aggressively in the first proof of concept.

Milestone 1 should preserve model-detected onset timing as faithfully as the target MIDI/chart representation allows.

Later, add an optional musical quantization layer:

```text
raw onset seconds
    ↓
tempo-map estimate
    ↓
nearest musically plausible grid point
    ↓
confidence-aware correction
```

Requirements:

- preserve original raw timestamp;
- allow quantization to be disabled;
- measure the displacement introduced by quantization;
- never silently move a hit by a large amount.

The architecture must support songs with:
- constant tempo;
- tempo drift;
- tempo changes;
- pickup measures;
- non-4/4 meters.

Do not assume every song is exactly 4/4 at a constant integer BPM.

---

## 12. MIDI / lane mapping strategy

General MIDI percussion mappings are useful as an interchange layer.

Initial lane policy for Clone Hero Pro Drums should be configurable, not hard-coded throughout the codebase.

Conceptual target:

```text
snare       → red pad
high tom    → yellow pad
mid tom     → blue pad
low tom     → green pad

hi-hat      → yellow cymbal
ride        → blue or green cymbal (policy)
crash       → green or blue cymbal (policy)

kick        → kick
```

Store mapping rules in one module/configuration object.

Preserve source instrument metadata for debugging.

---

## 13. Validation and diagnostics

Every generated chart should have a machine-readable diagnostic report.

Example:

```json
{
  "audio_duration_seconds": 251.04,
  "total_hits": 5372,
  "hits_by_instrument": {
    "KICK": 1104,
    "SNARE": 584,
    "HI_HAT_CLOSED": 2140
  },
  "unknown_hits": 12,
  "mean_confidence": 0.83,
  "warnings": []
}
```

Also generate an optional debug CSV:

```text
time_seconds,instrument,velocity,confidence,source_note
4.527,KICK,112,0.96,36
4.529,CRASH_1,103,0.91,49
...
```

This is essential for comparing model output to what the user hears in Clone Hero.

---

## 14. Tests

Use `pytest`.

At minimum:

### Unit tests
- instrument normalization;
- MIDI note mapping;
- velocity bounds;
- duplicate-hit suppression;
- timestamp ordering;
- song.ini generation;
- folder naming/sanitization;
- chart/MIDI serialization.

### Golden tests
Use tiny synthetic event lists:

```python
[
    DrumHit(0.0, KICK, 110, 1.0),
    DrumHit(0.5, SNARE, 100, 1.0),
]
```

Export them and compare against known-good fixtures.

### Integration tests
Do not require a copyrighted MP3 in CI.

Create a synthetic click/drum-like fixture or programmatically generated short audio test if useful.

ML/model-dependent tests should be marked separately because they may:
- download weights;
- require large dependencies;
- be slow;
- require GPU.

---

## 15. Observability

The CLI should log pipeline stages and elapsed time.

Example:

```text
[1/6] probing audio             0.12s
[2/6] separating drums        21.43s
[3/6] transcribing            14.88s
[4/6] normalizing events       0.05s
[5/6] exporting Clone Hero     0.08s
[6/6] validating output        0.02s
```

Use structured internal results rather than parsing log strings.

---

## 16. CLI design — initial

Proposed commands:

```bash
drumforge doctor
drumforge transcribe INPUT --midi-out drums.mid
drumforge inspect INPUT
drumforge generate INPUT --title TITLE --artist ARTIST --output DIR
drumforge validate SONG_DIR
```

`doctor` should inspect:

- Python/runtime;
- ffmpeg availability if required;
- ML backend importability;
- model availability;
- CPU/CUDA visibility;
- write permissions;
- optional dependencies.

Do not require GPU. CPU must be supported, even if slower.

---

## 17. Configuration

Keep configuration explicit.

Potential options:

```text
--device auto|cpu|cuda
--separation-backend ...
--transcription-backend ...
--confidence-threshold ...
--quantize off|1/8|1/16|1/32|adaptive
--cymbal-policy ...
--enable-ghosts
--enable-accents
--enable-2x-kick
```

Do not expose dozens of options before the underlying feature works.

---

## 18. Documentation to create during bootstrap

Create:

```text
README.md
CONTEXT.md
AGENTS.md
CONTRIBUTING.md
docs/
├── architecture.md
├── backlog.md
├── dependency-licenses.md
├── clonehero-format-notes.md
├── research-notes.md
└── testing.md
```

`CONTEXT.md` is canonical for project mission, decisions, current status, and next milestone.

`docs/research-notes.md` should clearly separate:

- facts verified from external sources;
- hypotheses;
- engineering decisions;
- unresolved questions.

---

## 19. Git / repository policy

Recommended repository name:

```text
drum-chart-forge
```

Recommended initial visibility:

```text
PRIVATE
```

Reason:
- early dependency/model licensing review;
- avoid accidentally pushing copyrighted audio;
- architecture is still exploratory.

After license review and repository hygiene are proven, consider making it public.

Suggested initial branch:

```text
main
```

Use conventional commits if practical:

```text
feat:
fix:
docs:
test:
refactor:
chore:
```

---

## 20. Backlog / implementation phases

Use the provided `BACKLOG.md` as the source of truth.

High-level phases:

### Phase 0 — Research & Bootstrap
Validate formats, dependencies, licenses, runtime and architecture.

### Phase 1 — Audio → Drum MIDI spike
Produce a credible drum MIDI from one real song.

### Phase 2 — Canonical event pipeline
Normalize model output into stable `DrumHit[]`.

### Phase 3 — Clone Hero exporter
Generate a scannable Expert Pro Drums song folder.

### Phase 4 — Turn to Ashes validation
Iterate against the actual song until broadly playable.

### Phase 5 — Quality improvements
Quantization, cymbal discrimination, double kick, ghosts, accents, tempo maps.

### Phase 6 — Usability
Stable CLI, batch mode, installability, reports.

### Phase 7 — Optional future product
GUI/editor, model comparison, interactive correction, dataset/evaluation tooling.

---

# Codex execution instructions

You are the implementation agent for this project.

## First action: inspect, do not assume

Before writing code:

1. inspect the current repository;
2. inspect installed Python/uv/Git versions;
3. verify whether this is WSL;
4. check whether `ffmpeg` is installed;
5. check whether CUDA is available, but do not require it;
6. inspect candidate upstream repositories/documentation and licensing;
7. identify any Python-version incompatibilities.

Report findings before selecting dependencies.

## Bootstrap target

For the first implementation session, complete **Phase 0 only**, plus the smallest executable skeleton needed to prove the repository works.

Expected deliverables:

1. initialize project configuration with `uv`;
2. create package skeleton;
3. create CLI with a working:
   ```bash
   drumforge --help
   drumforge doctor
   ```
4. create documentation listed above;
5. create `.gitignore` that prevents committing music/audio;
6. create initial test suite;
7. document dependency/license findings;
8. create architecture decision notes;
9. update `docs/backlog.md` with status;
10. run tests/lint/type checks that are actually configured;
11. provide a concise final report.

Do **not** attempt to fully transcribe Turn to Ashes during the bootstrap session unless Phase 0 is complete and the dependency spike is clearly safe and reproducible.

## Engineering constraints

- Python-first.
- `uv` preferred.
- Keep modules small and cohesive.
- No premature GUI.
- No web server.
- No database.
- No Docker unless an actual environment blocker justifies it.
- No Rust until profiling proves Python is a bottleneck.
- No copyrighted audio in Git.
- Never silently download very large models without explaining size/source.
- Pin or lock dependencies.
- Prefer reproducibility over cleverness.
- Preserve raw transcription timestamps.
- Make model/transcriber/separator implementations replaceable.
- Keep Clone Hero format logic isolated from ML logic.

## Quality gates

A task is not complete merely because code was generated.

Before declaring success:

1. run the command;
2. run tests;
3. run formatter/linter;
4. inspect generated files;
5. report any warnings;
6. update docs/status;
7. distinguish completed work from proposed work.

If an external dependency fails, do not patch around it blindly. Record:
- exact failure;
- environment;
- likely cause;
- minimal workaround options;
- recommended next experiment.

## End-of-session response format

Return:

### Completed
What was actually implemented and verified.

### Verification
Commands executed and their outcomes.

### Decisions
Architecture/dependency decisions made.

### Risks / blockers
Especially licensing, model weights, Python compatibility, ffmpeg, CUDA or WSL issues.

### Files changed
Concise list.

### Backlog updates
Task IDs completed/in progress/blocked.

### Next prompt
Provide a complete prompt for the next Codex session, targeting the next smallest milestone.

---

# Definition of success for the project

The project is successful when the user can take a legally obtained song file and execute one command that creates a Clone Hero folder that:

1. scans successfully;
2. exposes Expert Pro Drums;
3. is rhythmically aligned with the source audio;
4. automatically captures enough of kick/snare/hi-hat/toms/cymbals to be useful;
5. requires correction rather than full manual transcription.

The long-term target is **automation-first, human-correction-second**.
