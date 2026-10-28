# Linkin Park expansion — 2026-10-27

The user confirmed the duplicate cleanup worked and requested as much Linkin Park
as possible, specifically Given Up. That track is already Pro Drums/Expert in
batch 02 and remains there once. The original Emptiness Machine remains in batch
07; Heavy Is the Crown remains in batch 09. No transcription/ML work was advanced.

## Search and selection

Complete drum-filtered CH/PS/RB3/all catalog pagination returned 475 unique
packages: CH 72, PS 25, RB3 Xbox 318, all 475. Normalized titles, feature credits
and format-only annotations grouped the band's credited editions into 255
records, of which 33 were already published. Three third-party mashup packages
were outside scope. Supplemental title searches found no additional band packages.

The pass prepared **207 additional charts** in batches
19–30:
172 Pro Drums and 35 ordinary four-lane Expert Drums.
Edition groups: {'live': 56, 'studio_and_other': 92, 'demo': 59}.
Report outcomes: {'prepared': 207, 'previous': 33, 'blocked': 8, 'overlaps_previous': 5, 'covered_by_combined': 2}.
The collection now contains 518 charts overall,
including 240 Linkin Park/credited-collaboration editions.
Live/demo/remix editions are not counted as distinct studio compositions.

Intro-plus-main-song charts that overlap previous selections were omitted,
including Wake/Given Up and Tinfoil/Powerless. When both a separate song and its
selected intro medley were available, the combined chart represents that song
once. Alternative authors/platform formats do not create another edition.
The current installed library is not available in this cloud environment;
the user's PC comparison remains necessary for unprovided old songs.

Metadata from https://linkinpark.com/music supplies an additional 100-entry
reference: 97 tracks in eight core studio albums plus three From Zero Deluxe
extras. The album CSV maps titles/editions, including explicit combined charts;
it does not establish album-master identity. Reference results:
{'previous': 27, 'prepared': 52, 'not_found': 8, 'blocked': 5, 'combined': 6, 'no_usable_drums': 2}. Unavailable sources, tracks without usable Expert kick/drums
and conservative search gaps remain explicit rather than promised as delivered.

## Actual files and delivery checks

Every selected source passed package safety and actual artist/title checks,
strict conductor/PART DRUMS or ExpertDrums inspection, usable Expert/kick checks,
five-lane rejection and configuration/marker evidence for Pro claims. Ordinary
charts retain their original configuration and are separated from Pro batches.
Totals: **1527 runtime assets, 871 fully decoded audio
assets and 253,421 Expert drum gems**. Actual input formats:
{'zip': 43, 'onyx': 158, 'files': 6}. Every final manifest passed the standalone reader.

All 12 final ZIPs passed CRC and every runtime entry was
read back and matched to its pinned SHA256. ZIP bytes: 3,044,093,778;
source bytes: 3,953,240,881; prepared bytes:
3,109,549,220. Folder labels were bounded while retaining catalog
IDs, checking default Windows download and installed-export paths below 238
characters. Longer usernames/custom paths still require a shorter destination.

No new chart SHA256, package ID, original package SHA256 or normalized
artist/title repeats a prior selection or another new recipe. This stronger
chart-only check addresses scanner duplicates even when audio/metadata differ.
All recipes through batch 18, Qobuz cobertura.csv and the pinned Onyx/7-Zip/MEGA
helpers are byte-identical to starting main afed4ef. recover_pilot.py changes
only COLLECTION_SHA256. Old 744-entry Qobuz/active-chart counters remain unchanged;
new recipes have empty playlist/Qobuz ID lists and separate curated totals.

The collector now detects STFS signatures from the actual download instead of
trusting a platform label. A real previously cached RISE ZIP labeled rb3xbox
prepared natively without Onyx. Regressions exercise both mislabeled native ZIP
and mislabeled STFS, preserving source/chart/audio bytes. The playlist batch
caller also delegates this decision to the acquisition boundary. The Onyx
implementation, tool pin, Windows arguments and supervision were not modified.
Targeted searches without an instrument filter also found One More Light and
Good Goodbye packages. Actual native ZIP inspection rejected both for lack of
ExpertDrums; they are recorded as no_usable_drums in the album reference. This
does not establish that every package for those titles was inspected.

## PC additions and isolated reconstruction

The standalone additions.py wrapper reuses the local complement engine in an
explicit candidate/installed-library mode. It reads actual folders, preserves
installed choices and exports Novas-musicas.zip plus CSV/JSON without changing
either input. A shared chart with different audio/metadata and format-only title
differences are held for review. An empty installed reference is allowed here;
the legacy complement's empty-reference guard remains intact. No automatic game
installation, move or deletion was introduced.

recover_linkin_park.py validates the existing index, helpers and immutable source
recipes, then selects only the band's entries in memory. It includes the 33 old
charts and the new editions by default, so a missing Given Up can be recovered
without reissuing its recipe or downloading other artists. --novas limits it to
the new expansion. Separate ZIP names avoid collisions with full-batch exports.

Fresh-source recovery ran outside package imports with python -I -S and no
Mido/gdown/project installation for each selected input format. Every reconstructed
asset/ZIP was checked, then all network calls were forbidden for an unchanged
resume. Onyx used the already audited Linux AppRun explicitly, reproduced pinned
MIDI, stored local converted-asset hashes and preserved logs plus .tempos.jsonl.
A separate stdlib export using real newly prepared songs confirmed renamed
installed-copy exclusion, internal candidate deduplication, verified ZIP assets
and unchanged input bytes. This does not claim access to the user's actual PC.

## Gates and limits

All 155 core tests and 19 optional DSP checks passed after integrating existing
main diagnostic work from c3025cf. This includes Windows RTS handling, real-child deadlines,
blocked-console reporting, interruption/resume and retained diagnostics. Locked
sync/lock check, CLI help/doctor/JSON, Ruff lint/format, strict mypy, build and
archive-content audits passed. The optional diagnostic script's configured
lint/format/help gates passed. Doctor's absent optional ML/checkpoint warnings
are expected for this library-only environment; no models were downloaded.

The updated shared MIDI reader rechecked all 207 final charts: 253,421 Expert
gems and every stored validation field remained identical. The diagnostic skill,
frozen reference experiments, lockfiles and source changes from main were retained.
This pass acquired existing charts and ran structural checks; it did not perform
a new spectral/transcription experiment or measure acoustic per-class accuracy.

No audio, game charts, raw user scan logs, model files, caches or tools entered
Git or distributions. Ignored work/linkin-park contains source media and local
evidence, not a persistent download service. The durable Windows route, full
song lists, space budget and next-session prompt are in
[LINKIN-PARK.md](../song-library/LINKIN-PARK.md); report details are in
[linkin-park.csv](../song-library/reports/linkin-park.csv) and
[linkin-park-albuns.csv](../song-library/reports/linkin-park-albuns.csv).

The supplied scan log had 301 duplicate-chart relationships and two nonblocking
lyric warnings, rather than evidence of 300 corrupt downloads. The user's cleanup
confirmation does not verify each song's gameplay. Native Windows conversion,
Scan Songs/playtest, timing and musical quality for this expansion remain pending;
all new game_verified flags stay false. Linux timings do not explain earlier
Windows Onyx delays. Third-party sources may disappear or hit quotas later.
