# Sonne — requested single-song addition

The user requested adding Sonne by Rammstein after checking that it was absent
from the published recipes. Batch **43** appends one Pro Drums / Expert chart;
the default collection now has **676 charts**. Existing recipes and the separate
optional Nightmare replacement remain immutable. This is independent of the
744-entry Qobuz snapshot and does not fabricate playlist IDs or change coverage.

## Search and two-pedal priority

Public RhythmVerse drum-filter search for Sonne returned 13 packages overall,
three by Rammstein: two studio sources and a distinct live recording. Encore's
exact-artist/title-filter search returned two more entries, one studio/one live.
These APIs and a targeted 2x web search were researched. The three studio options
were actually attempted; different live recordings were excluded.

Two studio sources were obtained and inspected with the existing Onyx revision.
Separate import-only audits also examined the MIDI before PS export:

| Source | Expert gems | Base kicks | Optional MIDI-95 kicks | Outcome |
| --- | ---: | ---: | ---: | --- |
| beard216 / original | 1,194 | 407 | 0 | Inspected; not selected |
| GeeForce11 / alternate drums + MT | 1,294 | 464 | 0 | Selected |
| Rayzenn59 / native RAR | — | — | — | Unsupported archive link metadata; not prepared |

Neither imported MIDI has PART DRUMS_2X or optional kicks, and neither source
description explicitly promises full 2x authoring. The selected recipe states
**double_kick.status=unverified**. This does not establish that ordinary kicks
are a single-pedal reduction: full double-bass can use ordinary notes, and no
acoustic or physical-pedal ground truth was measured. No extra hits were invented.
The unavailable RAR was preserved and not extracted around the reader's checks.

## Selected source and preserved pairing

[RhythmVerse publication fb2e16c957934a20b716c9f651b41dc7](https://rhythmverse.co/songfile/fb2e16c957934a20b716c9f651b41dc7)
describes alternative drums, sync fixes and MT audio. Credits remain beard216,
Mastergox, Furiouss, Imitable and GeeForce11. Sync improvements are the author's
description, not an independently measured gameplay improvement.

- Console original: 32,514,048 bytes, SHA256
  f408754618a56fea530d78a00e8d4f5274c6a3ce290e28bcece92bf0a6dc8a8d.
- Recovered MIDI SHA256:
  0b62f9c60fce144e76bf31bcff3273eb8f2eda6d9671a6fa5bb96ff18016b6d7.
- Pro configuration and 82 tom markers; final Expert onset 243.497 seconds.
- Nine runtime assets, 23,950,373 bytes; six complete audio decodes.
- Initial delivery ZIP: 23,674,837 bytes, CRC/assets checked.
- Recipe collection_43.json SHA256:
  1f336811e5678d3522df0dadb022b10a179168a6094ad207a8942733295785f3.
- Collection index SHA256:
  c8cb0edc338c0e9771a6bb84118403608a90a156ee448ea877aa39a3b89cfc5a.

The old studio source supplies one audio stream, so the two-source inspection
decoded seven streams overall. Only the selected six-stream edition is delivered.
The source bytes are retained, and Onyx performs the existing paired conversion;
no manual changes to notes, timing or audio were made. Other instruments and
streaming-master identity remain unverified. Ogg container serials vary, so
fresh Onyx output audio uses local receipt hashes, with fixed source/tool/MIDI
identity, exactly as before.

## Durable delivery and execution

[SONNE.md](../song-library/SONNE.md) provides the selective Windows PowerShell
command, installed-library comparison, limitations and a full next-session prompt.
The general downloader now includes batches 02–43. Original active coverage,
prior themed counts and the old group/band selection namespaces remain unchanged;
the new requests theme contains only this one song. recover_pilot.py changes
only COLLECTION_SHA256. Onyx/7-Zip/MEGA/additions/group helpers are byte-identical.
The Nightmare guide continues to use its pinned older helper revision.

All metadata/helpers for the isolated run were copied to a clean directory and
the actual selective CLI ran under **python -I -S**, without drumforge, Mido,
gdown or pytest imports. It downloaded the real 32-MB original, imported/exported
it and verified the pinned MIDI and local output assets. Only the Onyx install
lookup reused the already verified Linux AppRun of the same revision; helper
bytes, conversion commands, deadlines and validation were not changed.
This is Linux execution evidence, not a Windows test.

The second run blocked recovery URL requests and preserved every file's hash,
size and mtime, including originals, receipts, ZIP and logs. The persistent Onyx
log and neighboring .tempos.jsonl record successful import/export. ZIP CRC and
every archived runtime hash match the local receipt.

The real-song additions command exported one absent song against an empty local
library and then recognized the same song in a renamed installed folder. Candidate
files remained unchanged; the installed copy retains all source hashes/mtimes.
The exported addition ZIP passed CRC and all asset hashes. No real PC Songs
folder was accessed or modified. Execution artifacts are ignored under
work/sonne-018/; source/audio/charts/logs are not committed.

## Gates and acceptance limits

The 178 existing core tests and 19 optional DSP checks pass; generic recipe/index
tests cover the append, pin, counts, novelty and all old recipes. Locked project
and diagnostic-script checks, Ruff lint/format, strict mypy, CLI smoke, build
and distribution hygiene pass. No new parser/converter behavior or test that
mirrors this one song's metadata was introduced. Previous audio-study recipes,
profiles, aggregates, Qobuz coverage, metadata and helpers were checked against
the starting baseline.

Game/native-Windows execution, perceived synchronization, quality and two-pedal
fidelity remain pending. All game_verified flags remain false. The user must run
Scan Songs and test Pro Drums / Expert with the audio paired to this chart.
