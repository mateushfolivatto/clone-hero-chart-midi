# Themed drum collections — 2026-10-25

The user requested League of Legends, Imagine Dragons and bands similar to
Linkin Park, independently of the Qobuz snapshot and the transcription pipeline.
The preparation produced 45 new charts in 6 append-only batches,
numbered 13–18: 39 Pro Drums and
6 ordinary four-lane Expert Drums.

## Evidence

- Cached public CH/PS/RB3/all drum-filtered searches for League of Legends,
  associated artists, Imagine Dragons and seven similar bands; additional title
  searches for Warriors, GODS, STAR WALKIN, Heavy Is the Crown, Legends Never Die
  and Awaken. Curated catalog editions are not asserted to be Qobuz masters.
- Each selected package passed actual artist/title checks, strict conductor and
  PART DRUMS or ExpertDrums inspection, kick/Expert usability, five-lane rejection,
  configuration/marker evidence for Pro claims, FFprobe and full FFmpeg decoding.
  Totals: **244 runtime assets, 107 decoded audio assets,
  51,469 Expert drum gems**. Inputs: 31 Onyx console conversions, seven public
  folders and seven native ZIPs.
- No duplicates against the 266 earlier songs or between the new themes by
  normalized artist/title, file ID, original package SHA256 and chart/audio hash
  sets. Heavy Is the Crown stays in batch 09; Enemy is included only in the LoL
  theme. The user's unprovided old local inventory remains outside this guarantee.
- Every new manifest passed the standalone reader; all source/tool/helper/index
  hashes were reconciled. Every ZIP passed CRC and every runtime asset was read
  back and matched to its recipe. New ZIPs total 427,278,999 bytes;
  source budget is 471,733,041 bytes.
- Fresh stdlib-only (`python -I -S`) reconstruction outside package imports checked
  ZIP (Mortal Reminder), direct public-folder assets (Lightbringer), and Onyx
  (Enemy), followed by resume with network explicitly disabled. Enemy reproduced
  pinned MIDI, stored local Ogg hashes and preserved logs plus timing JSONL.
  Linux used the already audited Onyx 20261016 AppRun explicitly; it did not run
  or substitute for the Windows CLI distribution.
- All old recipes and onyx_recovery.py/sevenzip.py/mega_recovery.py are byte
  identical to the starting revision cc69229. recover_pilot.py changes only its
  COLLECTION_SHA256 pin. The original Qobuz coverage CSV remains byte-identical;
  curated recipes have empty Qobuz/playlist ID lists and game_verified=false.
- Two metadata regressions check pinned index/recipe/helper consistency, counts,
  modes and absence of previous/new title, package or chart/audio duplicates.
  The complete suite has **91 passing tests**, including the unchanged real-child
  deadline, blocked-console, Windows RTS, interruption and retained-log regressions.
  Locked sync/lock check, CLI help/doctor, Ruff, strict mypy, build and archive
  hygiene gates passed. The optional diagnostic script's configured lint/format/help
  gates also passed. No model or copyrighted media entered Git/distributions.

## Limits and reproduction

See [TEMATICOS.md](../song-library/TEMATICOS.md) for the selective Windows command
and full song lists, and [lotes-tematicos.csv](../song-library/reports/lotes-tematicos.csv)
for selected/blocked/excluded entries. This is a curated subset, not complete
discography or soundtrack coverage. The report records 45 prepared selections,
nine blocked selections, three titles not found conservatively and one exclusion
already delivered in an earlier batch.
Catalog flags did not override actual chart evidence: Get Jinxed/RISE and other
ordinary charts are explicitly separate. A five-lane Last Resort candidate was
rejected and an inspected native four-lane Pro source selected instead.

Source media and preparation work are ignored under work/themed; only durable
metadata is published. User-facing ZIP copies are temporary conveniences; the
versioned recovery instructions are the persistent route. No claim is made that
the browser delivered a ZIP, that native Windows ran these recipes, or that the
user scanned/played them. Existing Onyx timing supervision and Windows diagnostics
were preserved; Linux timings do not explain the previous Windows delay.

The index retains the original 744-entry playlist coverage and active playlist
chart count. unique_new_charts/drum_modes/download/prepared budgets include both
the old continuation and this curatorial extension; curated_* fields identify the
extension separately. Future metadata refreshes must preserve those distinctions
and immutable theme recipes instead of reclassifying them as Qobuz coverage.
