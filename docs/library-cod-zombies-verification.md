# Kevin Sherwood / CoD Zombies — batch 44 verification

The user requested all ten newly found titles together and explicitly deferred
comparison with their pre-project installed songs until they supply the scanner's
duplicate report. This authorizes full-batch delivery; no inventory is required
before downloading. No files on the user's PC were inspected, installed or deleted.
BACKLOG.md DCF-LIB-019 owns preparation status.

## Sources actually obtained

Public RhythmVerse drum-filter searches considered Kevin Sherwood, Elena Siegman,
Treyarch, Malukah, Clark S. Nova and Lullaby. Composer/performer/title aliases were
checked against authored packages, retaining recording qualifiers. Encore's public
advanced API supplied Dead Again's original creator folder. Search results were
researched; the ten selected sources were actually downloaded and inspected.

The selected formats are four native ZIP packages, three original creator folders
and three console packages converted by the unchanged pinned Onyx. Dead Again's
Encore ID is 608597, MD5 8a9be2c65ee9ff255a9e1a80d4b5e4e8, charted by tomato;
its original Drive folder is linked in the guide and recipe. No mirror-only file
endpoint or account access was used. One native 2x Abracadavre source reported
Drive quota exhaustion; a different original 2x console source succeeded.

All ten expose actual Pro configuration and tom/cymbal markers, Expert gems and
kick notes. Native configuration uses the existing evidence-based Pro handling.
There are 55 runtime files, 24 fully decoded audio assets and 20,348 base Expert
gems. Prepared bytes: 103,006,129; selected original bytes: 103,140,086. The first
ZIP is 100,705,464 bytes, SHA256
67fc72be66b12a49eb3e056326283b21a25905b712b9014f349edf141f47ecd8.
Source/asset checksums and credits are in collection_44.json, SHA256
8b21fc0e109fe2d443ed7ef8a9afd134bb8afd05735c537b0c69870dbcf8a73f.
The initial index SHA256 is
7c86a95cc8ae33fc97d5f696a8b4e5cb01a6f22d99c725abae71347cd1c4dd2d.

## Two-pedal evidence

| Chart | Base kicks | Optional kicks | Evidence |
| --- | ---: | ---: | --- |
| Abracadavre | 858 | 674 | MIDI 95 after Onyx; source total 1,532 preserved |
| Beauty of Annihilation | 590 | 0 | Author's 2x edition; 27 additional ordinary MIDI-96 attacks versus paired 1x |
| Lullaby for a Deadman | 437 | 0 | 2x unverified |
| The One | 400 | 0 | 2x unverified |
| Pareidolia | 1,100 | 0 | 2x unverified |
| Coming Home | 722 | 509 | MIDI 95 after Onyx; source total 1,231 preserved |
| Archangel | 1,494 | 1,007 | Native .chart 32 |
| I am the Well | 1,074 | 648 | Native .chart 32 |
| Undone | 235 | 0 | 2x unverified |
| Dead Again | 1,086 | 630 | Native .chart 32 |

Independent original Onyx imports retained their logs/timing and MIDI: Abracadavre
has 1,532 ordinary source kicks, Coming Home 1,231 and Pareidolia 1,100. The exports
preserve each combined total, encoding some as optional kicks in the first two.
No manual MIDI/chart rewriting or kick synthesis was performed. The inspector's
base counts intentionally exclude optional kicks; five charts contain 3,468 extras.

Beauty's actual paired 1x original was downloaded only for comparison. Absolute
tick/note positive note-on multisets show exactly 27 added MIDI-96 events and no
removed events or other added note-ons. Both have identical shared song.ogg;
the 2x edition also includes its own guitar.ogg, whose decoded PCM differs from
song.ogg. Both authored audio assets are retained. The author's two-pedal edition
does not require optional notes to encode full kicks. This verifies source
authoring differences, not physical left/right pedal use or acoustic accuracy.

The remaining four sources have neither optional notes nor a verified full-2x
claim. Their status is explicitly unverified, not assumed single-pedal. The guide
explains Modifiers > 2x Kick and that the modifier cannot synthesize missing kicks.

## Delivery and preservation

The durable Windows guide downloads only batch 44 and the existing stdlib recovery
programs. It prepares a single folder/ZIP with all ten songs, without an installed
library comparison. The user copies it once, scans and sends badsongs.txt later.
Existing differing charts of the same song may require title/content comparison,
because duplicate-chart logs do not necessarily catch every repeated composition.
Backups stay outside scanned roots. Private logs, paths and media stay outside Git.

The index appends one cod-zombies batch and updates aggregate curation, storage
and mode totals: 686 default charts, 569 Pro and 117 ordinary Drums; the optional
Nightmare alternate stays separate. Earlier recipes, helpers and namespaces,
Qobuz 744-entry snapshot/254 active-new counts, and frozen study inputs/results
remain unchanged. recover_pilot.py changes only COLLECTION_SHA256. No model,
backend, acoustic rule, exporter or Onyx implementation was changed.

## Fresh recovery and gates

An isolated python -I -S process outside the checkout could not import drumforge,
Mido, gdown or pytest. It loaded byte-identical copies of the stdlib recovery
programs and only collection_44.json plus the index. The real selective CLI
downloaded all seven original packages and original assets from three creator
folders, then reconstructed all ten songs. Only the Onyx installer lookup was
substituted to reuse the existing Linux AppRun; this does not exercise the native
Windows installer or PowerShell. No source/archive/asset validation was replaced.

All 55 runtime asset hashes and ZIP CRC/member hashes passed. The three Onyx
conversions match pinned MIDI and record their own local audio/asset hashes;
the 24 recovered audio streams were fully decoded and the drum fields rechecked.
Each converter attempt retained its .log and .tempos.jsonl with import/export
outcome ok. The fresh ZIP has 100,705,618 bytes, SHA256
76d05de6d85ea012b79d432adbf646d63a00b86f21b72d61a87f8bad862acc0d.
ZIP timestamps and converted Ogg stream serials can differ from the first build.

With URL requests blocked, the second run preserved every hash, byte count and
mtime of 84 output files, including ZIP, sources, local receipts and logs. After
updating the three aggregate curation-byte counters, the final index/helper pin
was also rechecked against this exact unchanged recovered collection.

All 178 existing core tests, 19 optional DSP checks, project/three script locks,
Ruff lint/format, strict mypy (53 source files), CLI help/doctor/inspect-midi smoke,
wheel/sdist build and media/private-file archive hygiene pass. The doctor reports
ML/checkpoints absent as optional; none was installed or run. DSP dependencies
were explicitly installed only for verification. Existing metadata tests cover
this data-only change; no implementation-mirroring tests were added.

The preservation audit checks old tracked files and every earlier index batch,
helper and selection namespace; recover_pilot.py differs only in the index pin.
The PowerShell host is unavailable here; native Windows execution is not claimed.
Scratch sources, audit logs and verification scripts are ignored under
work/cod-zombies-019/. Native Windows, Scan Songs, perceived synchronization and
e-kit/two-pedal playtesting remain pending; game_verified stays false.
