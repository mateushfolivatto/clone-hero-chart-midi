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

## Drum diagnostic support (2026-10-16)

The user requested investigation of missing hi-hats, spectral visualization and
possible Moises separation. A project-local skill and standalone diagnostic script
now compare short full-mix/stem excerpts using stereo power spectra and band flux.
Their Python dependencies are optional and separately locked; no ML model is
installed and no audio is uploaded. This supports Phase 1, not a GUI or exporter.

A confirmed configuration bug was fixed: public thresholds BD SD HH TT CY must
be translated to pinned ADTOF's BD SD TT HH CY (GM 35, 38, 47, 42, 49). Previously
the third/fourth thresholds affected the opposite classes from the CLI help.
The public order is retained, with translation at the isolated backend boundary
and a runtime label-order check. Untuned upstream defaults remain unchanged.
Review previously tuned explicit vectors. Real-song improvement is unmeasured;
private source audio/MIDI are unavailable. Phase 1 acceptance remains pending.
See docs/drum-audio-diagnostics.md and DCF-123; keep the full-mix baseline and
measure per-class precision/recall before choosing stems or fusion.

## Raw MIDI diagnostics (2026-10-20)

The user requested resuming music-to-chart development and using the local
drum-audio-diagnostics skill throughout every such task. AGENTS.md now records
that preference. Phase 1 gained `drumforge inspect-midi` for raw GM percussion:
counts by note/group, tempo-aware onset seconds, stored velocities, source hash
and JSON/CSV output in a new directory. Simultaneous notes and duplicates stay
intact. Mido 1.3.3 is a locked optional diagnostics extra and a dev dependency;
core runtime remains standard-library-only. This does not implement canonical
events, ML activations, acoustic dynamics or the Clone Hero exporter.
DCF-118/119 are implemented and synthetically verified; private Turn to Ashes
validation and native Windows remain pending. See docs/phase-1-midi-diagnostics.md.

## Existing charts as audio references (2026-10-27)

The user explicitly authorized studying five existing song packages to relate
charts to waves and retain a reusable file/skill. This is a Phase 1 reference
experiment, not a requirement to wait solely for private Turn to Ashes assets.
The five-artist recipe samples 60–80 and 120–140 seconds, with pinned chart/INI/audio
hashes. The skill now supplies study/predict commands and a saved spectral-rule
profile. Comparison uses technical full mixes versus existing drum stems, chart
tempo/delay, tom-marker intervals, simultaneous notes and whole-song holdouts.
Game lanes are weak references: yellow cymbal is not a verified hi-hat label.
Simple calibration improved chart agreement for kick/snare but worsened yellow
cymbal agreement. No ADTOF/model training or weights were used; automatic adoption
is not recommended. Keep original ADTOF defaults and full-mix baseline until an
independent, manually annotated instrument test supports a change. See
docs/five-song-chart-reference.md and DCF-124; overall Phase 1 remains in progress.

## CoD/A7X external evaluation (2026-10-27)

The user then requested other CoD and Avenged Sevenfold songs. The five-song
profile was kept frozen and applied to 115, Carry On, Not Ready To Die, Afterlife
and Brompton Cocktail, two fixed 20-second excerpts each. Mix mode uses all five;
existing drum stems are available only for Afterlife/Brompton Cocktail. The new
evaluate command rejects reuse of calibration IDs/chart hashes and records profile
identity. Read-only .chart support preserves its distinct cymbal flags, tempo and
offset; missing MIDI velocity stays null. No detector thresholds were changed.
Kick F1 was essentially unchanged on this sample, while snare/yellow-cymbal proxy
F1 improved with lost recall. Carry On had poor agreement even with the original
rule and needs pairing/alignment/masking investigation. No acoustic ground truth
or ADTOF improvement is established. See docs/cod-a7x-heldout.md and DCF-125.

The user subsequently recalled that the yellow notes in the discussed CoD/A7X
songs were hi-hat, usually open. Retain this as user-provided song-level context
and the leading hypothesis for audio review, not per-event acoustic annotation.
The next review should inspect attacks and overlapping decay, check 115's absent
yellow references against audible hi-hat, and distinguish open/closed hi-hat from
other cymbals. The current band-flux detector does not classify hi-hat openness.
Keep frozen proxy labels, profile and reported metrics unchanged.

## Linkin Park hi-hat references and disco-flip correction (2026-10-27)

The user suggested Faint and Crawling for timekeeping hi-hat. Both local pairs
were evaluated over the same fixed excerpts with the frozen profile: 80 seconds
of music, 508 mix target references; Crawling alone supplies 40 seconds of drums.
Inspection found Expert disco-flip events in Crawling. The reference reader now
resolves these MIDI/.chart mix states before scoring Pro lanes, keeps raw source
notes/timing/velocity and records semantics version 2. It reclassifies 422 notes
in the full Crawling chart; all events in the previous ten songs and Faint were
verified unchanged. This corrects labels, not audio inference or original charts.
Charted hi-hat steps are typically 222 ms in Faint and 286/143 ms in Crawling.
The original high-band detector outperformed the restrictive frozen profile on
yellow-Pro F1 in both songs; Crawling drums recovered more attacks than its mix.
Do not infer openness, fill rhythm gaps, retune on these test labels or generalize
stem superiority. See docs/linkin-park-hihat.md and DCF-126. No ADTOF defaults,
canonical pipeline, exporter or game acceptance changed; Phase 1 remains open.

## Component-source follow-up and free external sample (2026-10-27)

The user authorized starting with existing songs, preferring a free route and
continual skill updates toward better unseen-song transcription. A seven-song
follow-up now compares mix, non-silent drum audio and explicit component sources
with unchanged rules. Crawling/Afterlife provide kick/snare/remaining-kit streams;
the last is not isolated hi-hat. Brompton's drum stream is digitally silent in
both excerpts and is excluded from the new drum aggregate. Version-2 evaluation
reports per-stream signal audits and per-class excerpt/second/reference coverage.
In the same 80 seconds, frozen F1 drums→components is .661→.610 kick,
.482→.761 snare proxy and .686→.776 yellow proxy. These are previously examined
songs, not a new independent test set. No automatic winner selection is justified.

The chart-free predict-components command accepts three already aligned stems
and exports spectral candidates with source hashes and common gain. It does not
separate audio or generate game charts. Seven small public StemGMD demonstration
MP3s were obtained through the GitHub connector, with references and precomputed
LarsNet outputs pinned to source revision/blob/SHA256. They were inspected and
compared over ten seconds; no MIDI truth or local LarsNet inference was used.
No local LarsNet runtime/weights or E-GMD dataset was installed; no paid service
or music upload was used.
See docs/stem-component-study.md and DCF-127. ML separation/transcription,
native Windows and game validation remain pending; Phase 1 stays open.

## Broad frozen survey (2026-10-27)

The user authorized analyzing many additional existing songs to check patterns.
The survey planned 64 new songs across 20 normalized artists before scoring:
128 fixed excerpts, 2,560 nominal seconds, 352 pinned files and 14,534 mix target
references. It excludes earlier songs/chart identities, balances artists and
keeps all planned failures/negative cases visible. All 64 completed. Thirty songs
provide non-silent drums, twelve have explicitly declared component layouts.
Whole-song bootstrap and per-song medians supplement pooled F1; source comparisons
use only identical available song/excerpt/class pairs.

With unchanged rules, mix F1 baseline→frozen is .420→.533 kick, .426→.526 snare
proxy and .417→.441 yellow proxy, with substantial recall loss. Component snare
gain persisted on twelve new pairs; the earlier strong HH gain did not (.501→.505,
interval crosses zero). Sparse/absent yellow references produce many extras.
Yellow recall is higher at charted kick/snare coincidences; that is not proof of
HH identification or universal masking. A post-score exploratory circular-shift
control checks timing opportunity without modifying real predictions.

New survey-plan/survey tools provide bounded workers and hash-verified resume;
survey_summary.py independently recomputes scores and plots patterns. The local
diagnostic skill records these findings for future music tasks. No model was
trained/downloaded/run and no game exporter or acceptance was advanced. See
docs/broad-song-survey.md and DCF-128; Phase 1 remains open.

## Separate song-library workstream (2026-10-16)

The user requested a separate, portable area for the growing MixDrumRock Qobuz
playlist (600+ tracks), existing drums charts from RhythmVerse, conversion when
needed, and a ZIP of extracted song folders for personal Clone Hero use.
`song-library/README.md` records this workflow and its limits; templates are
versioned while all private collection data stays in ignored `song-library/data/`.
This request authorizes library organization and investigation independently of
the MP3 transcription phases; it does not complete any Phase 1 acceptance item.
The public playlist link was provided and all 681 entries were exported to private
CSV/XLSX/JSON snapshots. The reusable metadata helper lives in
`drumforge.library.qobuz`, isolated from the transcription pipeline. The network
blocker was resolved after unrestricted publication; Qobuz and RhythmVerse return
HTTP 200. The user subsequently authorized at least ten songs for a later test.
Twelve native Clone Hero packages were selected from the playlist, downloaded,
inspected for four-lane Expert/Pro Drums and packaged in a private ZIP with sources
and instructions. All 40 audio assets decoded; audio and note files remain intact.
Only Requiem's song.ini received pro_drums=True from existing cymbal markers.
No console/five-lane conversion was needed. Scan Songs/playtest and inventory of
the existing user library remain pending; general search/acquisition automation
and full-playlist coverage are not complete. See song-library/README.md.
Do not promise complete coverage or infer drums from a Guitar Hero III label.
The collection should preserve source audio/chart pairing, existing songs and
manual choices, use relative paths, and distinguish structural checks from actual
user-confirmed game compatibility. See DCF-LIB items in BACKLOG.md for status.

### Pilot delivery recovery (2026-10-17)

The resumed cloud machine had the original checkout and no ignored collection
data, so the old workspace ZIP link failed. Latest source was recovered from
origin/main without discarding local work. All twelve pilot sources were fetched
and inspected again. The durable, metadata-only recipe is now packaged as
`drumforge/library/pilot_01.json`, with pinned archive/asset hashes. A standalone
standard-library downloader, recover_pilot.py, reconstructs the same runtime files
on the user's PC without uv, FFmpeg or Mido, and preserves existing local edits.
See song-library/BAIXAR.md for the PowerShell instructions. A reconstructed cloud
copy lives in /workspace/shared/downloads/MixDrumRock/, but it is not a permanent
download URL. Media remains outside Git; game acceptance still needs user testing.

## MixDrumRock bulk preparation — 2026-10-17

After confirming pilot delivery, the user authorized the remainder. The public
playlist grew to 744 entries. The library now has cached catalog searches,
conservative artist/title/version/duration matching, native archive preparation,
Onyx 20261016 conversion, pinned portable readers and standalone PC recovery.
254 additional charts were prepared in 11 batches: 246 Pro Drums and eight ordinary
four-lane Drums, clearly separated. Including the pilot, 266 charts cover 275
playlist entries; 469 entries remain explicitly pending in song-library/reports/cobertura.csv.
See song-library/CONTINUACAO.md. Sources, hashes and Qobuz IDs are durable JSON;
audio/charts remain private and ignored. Local ZIP paths are temporary conveniences.

Original chart/audio pairing is retained. Ordinary Drums does not imply Pro Drums;
five-lane charts are not relabeled. Onyx regenerates MIDI/audio for console inputs;
its Ogg serial numbers vary, so source/tool/MIDI identities are pinned and local
output hashes protect resume. Metadata recipes append without replacing earlier
batches. Actual Windows conversion, Scan Songs, synchronization and musical quality
remain unverified. No ML/model dependency or transcription implementation changed.

### Windows Onyx invocation correction — 2026-10-17

The user's Windows log showed repeated Onyx import exit 1 failures in batch 08
and a separate Octavarium download timeout. The downloader incorrectly sent
`+RTS -N2 -RTS` to the pinned Windows CLI, whose upstream target does not enable
threaded/runtime options; the Linux GUI/AppRun build does. Windows now receives
no runtime flags, while Linux retains its two-capability limit. Each PC conversion
keeps an independent log under `Logs/Onyx`, with the stage and diagnostic tail in
errors after temporary-project cleanup. The song recipes, originals, tool version
and output verification stay unchanged. Only the helper/index identities change.
See song-library/CONTINUACAO.md for the three-file update and resume command;
docs/library-onyx-recovery-fix.md records evidence and native-validation limits.

### Onyx elapsed feedback — 2026-10-18

The user reported slow per-song recovery and supplied a Python 3.13 Windows
KeyboardInterrupt while waiting in Onyx import for Endless, Nameless. Their output
shows batch 09 completed and the first seven batch-10 songs ready; it does not
establish game acceptance or why import was slow. The same source imported in
1.35 s on Linux. Recovery now prints import/export stages, elapsed waits every
15 seconds, existing deadlines and persistent log paths. Child stdin is closed
for noninteractive conversion; Ctrl+C exits 130 with a resume message rather
than a traceback. Deadlines, conversion inputs, pinned MIDI and recipes are
unchanged. This improves visibility and interruption handling; Windows slowness
still requires the local converter log, not a claim of faster conversion.
The returned native log contains only the initial “Importing Rock Band song”
line; no recorded completion or converter error. The import delay remains
unexplained. A full isolated Linux conversion subsequently verified the pinned
MIDI, local asset hashes and unchanged resume (0.9 s import, 23.3 s export).
The user then clarified that this interrupted import had waited less than three
minutes; a preceding song waited about three minutes, with its stage unspecified.
The supplied traceback therefore does not demonstrate an expired import deadline
or converter failure. Do not label it a proven hang or promise a speedup.

### Process timing and deadline supervision correction

The user's newer Windows output reports Stain import success after 731 s despite
a 180 s label; they denied console selection and system suspension. A real defect
was reproduced locally: timing began before initial console output and ended
after an unbounded reporter join, allowing UI delay to inflate the displayed
converter duration. This does not establish the source of the user's 731 s.
The runner now separates process creation from waiting, polls the owned Popen
process against a monotonic deadline, rejects a late observed success, and kills
and reaps that child on timeout/interruption. Console reporting is independent
and its join bounded; process-wait timing is frozen before reporting cleanup.
Adjacent .tempos.jsonl diagnostics record launch/wait/cleanup and outcomes.
OS process creation cannot be canceled by Python's wait timeout and remains
explicitly separate. Source/tool/MIDI identities and song recipes do not change.
Real-child timeout and blocked-console regressions are required; native Windows
performance/root cause and game acceptance remain unverified.

### Existing library complement

The user authorized a local complement of an existing ~4 GB song collection,
whose folders were renamed and cannot be uploaded. `library.complement` and its
standalone stdlib helper `local_library` compare actual extracted folders by INI
artist/title and chart-plus-audio hashes. Present new batches take precedence;
incomplete downloads do not exclude an old song. Ambiguous editions/durations
are reported for review, and repeated old songs are represented once. The tool
exports ZIP64 plus CSV/JSON without altering inputs or overwriting earlier outputs.
See song-library/SEM-REPETIDAS.md. The user must assemble batches plus complement
in an empty library, retaining the old folder as backup. The user's actual local
inventory, native Windows run and game acceptance remain pending.

### Themed library additions — 2026-10-25

The user requested new drum batches for League of Legends, Imagine Dragons and
bands similar to Linkin Park. Batches 13–18 add 45 charts: 11 LoL/associated
projects, 13 Imagine Dragons and three each from Papa Roach, Breaking Benjamin,
Three Days Grace, Evanescence, P.O.D., Limp Bizkit and Bring Me the Horizon.
There are 39 Pro Drums and six ordinary Drums, separated by theme and mode.
The collection now has 311 charts including the unchanged 266 earlier songs.

This is independent curation, not an updated Qobuz snapshot. The original
744-entry coverage CSV and active playlist counts remain unchanged; new recipes
have empty Qobuz/playlist ID lists, theme metadata and separate curated_* index
totals. Compare future selections against all recipes by artist/title, source and
chart/audio identity. Enemy appears only in the LoL theme; Heavy Is the Crown
remains in batch 09. Previously published recipes and Onyx helper bytes remain
unchanged. recover_pilot.py updates only its collection-index hash pin.

See song-library/TEMATICOS.md for the selective Windows command, song lists and
next-session prompt; docs/library-themed-verification.md records checks and
limits. Six ZIPs, 244 assets and 107 decoded audio files passed structural/hash
checks; fresh isolated ZIP/Drive/Onyx recovery and unchanged offline resume passed
on Linux. Native Windows execution, game acceptance and the cause of prior Windows
Onyx delays remain unverified. No ML or transcription scope was advanced.

### Scan feedback and Linkin Park expansion — 2026-10-27

The user's badsongs report contained 301 duplicate-chart relationships, including
a nested copy of the old complement and a loose duplicate of The Emptiness Machine.
It also had two nonblocking lyric warnings. The user confirmed that the duplicate
cleanup worked. This is scan/organization feedback, not a blanket playtest or
timing acceptance; individual game_verified flags remain unchanged. The raw log
and personal filesystem paths must stay outside Git.

The user then requested as much Linkin Park as possible, specifically checking
Given Up. It already exists as Pro Drums/Expert in batch 02 and was not
republished. The 475-package/255-edition drum-catalog pass appended 207 charts
in batches 19–30: 172 Pro Drums and 35 ordinary Drums, with demos
and live editions separated. The collection now has 518 charts overall;
there are 240 band/credited-collaboration editions including the 33 earlier ones.
Gaps remain explicit in the catalog and 100-entry official-album reference CSVs.
One More Light and Good Goodbye native probes had no ExpertDrums section.

Catalog platform labels now defer to actual container signatures. Band-only
recovery validates immutable source recipes and can restore missing earlier tracks,
including Given Up, without downloading the other artists in those batches.
The standalone additions helper compares actual candidate/installed folders and
exports only absent songs; uncertain shared-chart/format-label cases stay for
review. Onyx's Windows arguments, supervision and persistent diagnostics are
unchanged, as are all prior recipes and Qobuz coverage. recover_pilot.py changes
only its index pin. After retaining concurrent diagnostic work, all 155 core
tests and 19 optional DSP checks passed, with isolated fresh recovery,
offline resume and real-song export checks on Linux. See song-library/LINKIN-PARK.md
and docs/library-linkin-park-verification.md. Native Windows/individual playtests
remain pending. BACKLOG.md DCF-LIB-014 owns preparation-pass status.

## Skillet / Imagine Dragons / LoL expansion — 2026-10-28

The user requested every obtainable drum chart for these three selections. Batches
31–40 append 137 charts: 133 Skillet, two Imagine Dragons and two LoL, with
71 Pro Drums and 66 ordinary Drums separated. There are 655 charts overall.
The group totals, including retained old choices, are 143 Skillet, 16 Imagine
Dragons and 16 LoL; shared Enemy makes the union 174 unique selections. Live
editions are labeled; format-only 6-fret alternatives do not duplicate a song.
The 197-edition pass leaves 23 explicit blockers and a separate title checklist;
this does not establish complete global discography availability.

Native public SNG sources require a small bounded standard-library reader:
header metadata becomes deterministic song.ini while unmasked notes/audio stay
intact. Display color tags no longer cause false catalog mismatches, without
removing recording qualifiers. Public Encore metadata was researched/called;
original creator Drive publications supply the actual packages. No upstream code,
media, model or checkpoint is distributed. The local diagnostic skill retains
the source/validation finding without acoustic-accuracy or transcription claims.

A separately pinned group-selection helper references immutable old/new recipes
and supports one or more groups/new-only recovery. The installed-library comparator
continues to export only absent actual folders and hold uncertain editions for
review. Onyx/7-Zip/MEGA and four old additions helpers are byte-identical, as are
all prior recipes, Qobuz coverage and pinned audio-study inputs/results. Only the
new SNG recovery path and index identity extend recover_pilot.py.

All 864 runtime assets, 450 audio decodes, 173,176 Expert gems and ten ZIPs were
checked. The 172 core tests, 19 optional DSP checks, locked/static/CLI/build and
archive-hygiene gates pass on Linux. Fresh stdlib recovery/offline resume passed
for SNG, ZIP, public Drive files and Onyx; isolated group selection and actual-song
additions export preserve inputs. Native Windows, Scan Songs and individual
playtests remain pending. See song-library/SKILLET-IMAGINE-LOL.md and
docs/library-skillet-imagine-lol-verification.md; BACKLOG.md DCF-LIB-015 owns status.

## The Strokes highlights — 2026-10-28

The user confirmed The Strokes and requested the best songs to add to Clone Hero.
A curated 25-title plan combines classic highlights, six-album variety and actual
drum availability, using read-only Spotify metadata and NME search references.
Twenty songs are prepared in batches 41–42: 18 Pro Drums and two ordinary Drums
(Ode to the Mets and 12:51). The full collection now has 675 charts. There were
no earlier band selections; all 655 previous charts retain their recipe bytes.
Two validated alternatives remain reserves; Bad Decisions/Call It Fate, Call It
Karma lack conservative drum matches, and Machu Picchu's sources are unavailable.

All 92 assets, 31 audio decodes, 28,994 Expert gems and two ZIPs were verified.
Fresh isolated stdlib-only selective CLI recovery reproduced all 20 songs across
SNG, public files, 7z, ZIP and Onyx; unchanged offline resume and persistent logs
pass. A real-song comparison preserves inputs and exports only absent songs.
The 173 core tests, 19 optional DSP checks, lock/static/CLI/build and archive
hygiene gates pass. No acquisition/converter code, old helper, model, Qobuz coverage
or audio-study input/profile/result changed; recover_pilot.py updates only the
index SHA256. A recipe regression keeps studio titles containing Live/Cover words.
See song-library/THE-STROKES.md and docs/library-strokes-verification.md;
BACKLOG.md DCF-LIB-016 owns status. This completes the curated preparation pass,
not native Windows, individual Scan Songs/playtesting or full-band coverage.

## Standing library preference: two pedals — 2026-10-28

The user requests priority for double-bass/two-pedal charts in every future
selection, including a second Nightmare edition. Prefer verified Expert+/2x Kick
or explicitly authored full-double-bass versions, retaining source notes/audio.
If only a single-pedal or unverified edition is obtainable, state that limit.
Pro Drums alone does not imply double bass. Optional Expert+ kicks use .chart 32
or MIDI 95; some full-2x editions encode every kick as ordinary 0/96 instead.
Do not invent extra kicks or silently relabel a reduced chart.

Inspection of the existing batch-06 Nightmare (ImPhanty) finds 893 base kicks plus
471 optional Expert+ kicks, 1,364 total. These optional notes require Clone Hero's
Modifiers > 2x Kick. This is structural evidence, not a new game playtest. The
inspector now reports optional kicks and combined totals without changing its
previous base counts or rewriting any chart. Existing recipes remain immutable;
alternate replacement delivery must keep backups outside all scanned roots.

An optional second Nightmare source, credited to Harmonix and published by
UriasP, is prepared separately in nightmare_2x.json: 916 base + 454 optional MIDI
95 kicks (1,370 total), Pro Drums, ten assets/seven decoded audio files. Source
7z/MIDI/audio are preserved. It is deliberately outside the default batch index,
which still describes 675 charts; Qobuz coverage and all old recipes/helpers,
including Onyx and recover_pilot.py, are unchanged. The durable guide pins the
two recovery programs to published revision e6251a31 and the optional recipe to
its checksum, so later index updates do not break this download. Fresh isolated
stdlib extraction from the pinned cached original and byte-identical offline
resume pass. All 178 core tests and 19 DSP tests pass. Windows/Scan Songs/playtest
remain pending. See song-library/DOIS-PEDAIS.md and
docs/library-double-kick-verification.md; DCF-LIB-017 owns preparation status.

## Sonne addition — 2026-10-28

The user requested Sonne by Rammstein. Batch 43 adds the inspected alternative
drum/sync/MT publication, credited to beard216, Mastergox, Furiouss, Imitable and
GeeForce11. It has Pro Drums / Expert, 1,294 base gems, 464 kicks, 82 tom markers
and six decoded audio files in nine runtime assets. Default collection: 676 charts;
the 675 old recipes plus optional Nightmare source/guide remain unchanged.

Two-pedal priority was applied. Both obtainable studio sources were inspected
before and after Onyx PS export: zero optional note-95 kicks and no separate
PART DRUMS_2X track. No explicit full-2x author claim was found. The selected
recipe records double_kick.status=unverified, rather than inferring a single-pedal
reduction or inventing hits. Another native RAR could not be prepared because its
link metadata is unsupported by the reader; two live recordings stay excluded.

The collection index appends one requests-theme recipe and updates counts/budgets;
recover_pilot.py changes only its index checksum pin. Onyx/other helpers, all
previous selections, Qobuz coverage and audio-study inputs/profiles/results stay
unchanged. All 178 existing core tests, 19 DSP tests and configured gates pass.
Fresh isolated stdlib recovery downloaded the real source and converted through
the existing Linux AppRun; offline resume, persistent logs and actual-song
comparison with empty/renamed libraries pass. Native Windows/Scan Songs/playtest
remain pending. See song-library/SONNE.md, docs/library-sonne-verification.md
and canonical BACKLOG.md DCF-LIB-018. This completes the single-song preparation.

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
