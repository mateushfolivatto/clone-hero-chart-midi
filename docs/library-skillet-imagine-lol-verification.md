# Skillet / Imagine Dragons / LoL preparation — 2026-10-28

DCF-LIB-015 appends 137 charts in batches 31–40: {'pro': 71, 'standard': 66}.
The full collection contains 655 charts. Selection membership is
{'skillet': 143, 'imagine': 16, 'lol': 16}; groups overlap and their union is 174 songs.
Previous authored selections are retained. Song metadata and SHA256 recipes are
versioned; original packages, runtime media, receipt logs and ZIPs remain ignored.

## Scope and source evidence

RhythmVerse drum-filter searches plus additional unfiltered Skillet/Imagine Dragons native probes
were cached with pagination/count reconciliation. Encore general search is fuzzy:
strict artist/title/album affiliation is applied after retrieval. The broad K/DA
query reached its pagination ceiling; a separate exact-artist advanced search
completed with zero drum hits. No partial general search is called exhaustive.
503/429 responses from the first Encore pass were recorded; serial retries and
exact advanced searches supplied the final metadata. No credentials were used.
Sources unavailable at download time remain explicit in the public CSV.
The unfiltered Skillet snapshot contains 243 packages; only native CH/PS/RV
alternatives supplement the drum-filter catalog. Additional console rows explicitly
declaring no drums are not represented as inspected drum sources.

Public metadata requests use POST /search at https://api.enchor.us with search,
page, per_page=250, instrument=drums, difficulty=expert, drumsReviewed=false and
source=api. POST /search/advanced supports artist/album objects with value, exact
and exclude. Original creator Drive publications are the durable source links;
Encore chart IDs and catalog MD5 are retained as discovery metadata, while SHA256
of the actual original and resulting assets remains the integrity authority.

Primary references researched, without copying/vendoring/running upstream code:

- [Bridge search and original-source fields](https://github.com/Geomitron/Bridge),
  GPL-3.0 repository; public search API protocol studied and called.
- [SNG v1 specification](https://github.com/mdsitton/SngFileFormat), MIT repository;
  own bounded standard-library reader implemented from the specification.
- [parse-sng](https://github.com/Geomitron/parse-sng), npm 4.0.3/MIT; researched to
  locate the specification, not installed, invoked or distributed.
- [Netflix Arcane soundtrack credits](https://www.netflix.com/tudum/articles/arcane-season-2-soundtrack),
  [Riot music index](https://www.leagueoflegends.com/en-au/news/tags/music/),
  [Worlds 2026 anthem](https://lolesports.com/en-AU/news/worlds-anthem-presented-by-true-damage)
  used only as affiliation/title references; no news prose, lyrics or media copied.

Encore's mirror file host returned 403 and was not used. New packages use their
separately published original creator Drive file/folder URLs. This is independent
source acquisition, without a proxy for the denied mirror. Package metadata and
actual drum/audio bytes must still pass inspection. Catalog flags alone do not
establish instrument availability, Pro status, recording identity or acoustic labels.

## Native formats and preserved behavior

New sources: {'sng': 2, 'files': 2, 'zip': 10, 'onyx': 123}. SNG v1 verifies signature/version, bounded metadata
and index sections, UTF-8, INI-safe keys/values, counts, filenames, duplicate/case
collisions and contiguous non-overlapping offsets inside the source. Extraction
streams fixed-size chunks and resets the position-dependent XOR key per asset.
A deterministic INI is generated from the header; notes/audio are not transcoded.
The source archive and every resulting asset are pinned. Synthetic scalar-encoded
fixtures cross 1 MiB/256-byte boundaries and reset between assets. Malformed files
fail before publication; local edits and offline resume remain protected.

A real I Bet My Life original SNG restored notes.mid and six Opus streams;
813 Expert gems, 260 kicks and 69 tom markers were inspected, and audio decoded.
Take Me to the Beach's original INI uses color tags. Acquisition now ignores only
game display tags when matching catalog identity, preserving the original source,
runtime display tags and all version words. Take Me to the Beach retains the
existing documented pro_drums=True patch from its 620 authored cymbal markers;
notes/audio remain unchanged. Regression rejects a colored Live title against a
studio query.

Onyx helper bytes remain identical to the start commit, including native Windows
arguments, process supervision, deadlines, persistent logs/timing and Ctrl+C paths.
Pilot and recipes 02–30, the four existing additions helpers, the Qobuz coverage
snapshot/index fields and all pinned audio-study inputs/results are unchanged.
recover_pilot.py now adds native SNG extraction besides updating the index pin;
this is an explicit format extension, not a change to console conversion.

## Artifact and delivery checks

All 864 runtime assets, 450 decoded audio files and
173,176 Expert gems were checked during preparation. Each of the
10 ZIPs passes CRC and SHA256 for every song asset. Original source
sizes/hashes, mode, absence of previous/new title/source/chart duplicates and the
Windows default path budgets are rechecked before freezing recipes. Runtime folder
copies use local hardlinks only for ignored verification output; PC recovery writes
normal files and requires no hardlink permission.

recover_selections.py validates the pinned index, old helper bytes, selection
membership/helper and every recipe before selecting a union of file IDs. Shared
Enemy is recovered once. Old songs are referenced from their existing batches.
Different group/new-only selections have distinct ZIP names, preventing reuse of
a ZIP for a different subset. additions.py then compares actual downloaded folders
with actual installed folders; missing downloads do not count as replacements.

The completed pass covers 197 grouped editions: 137 prepared, 37 previous and
23 blocked. The reference-title CSV has 130 rows; this is a search checklist,
not an official-album coverage denominator. All previous selection bytes, source
and chart identities remain protected.

## Executed gates

- 172 pytest cases pass; 19 optional DSP unittest cases pass with their pinned
  NumPy/Matplotlib/Mido environment. A first core-only invocation lacked optional
  Matplotlib; rerunning in the explicit optional environment passed all 19.
- Locked sync/lock validation, Ruff lint/format for src/tests and diagnostic scripts,
  strict mypy, core help/doctor/text/JSON, inspect-midi help and diagnostic help pass.
  The three optional script locks remain unchanged and validate offline.
- Wheel/sdist build and inspection verify intended helpers, all recipes, selection
  metadata and technical documentation, without media, models, private logs or caches.
  The Windows guide/CSV remain GitHub artifacts outside the existing sdist include
  list; no packaging scope was enlarged.
- Fresh source reconstruction in python -I -S passes for SNG (I Bet My Life), ZIP
  (Heavy Is the Crown Original Score), Drive files (Ma Meilleure Ennemie) and
  Onyx (Podcast Song). Source/pinned MIDI/local asset hashes, persistent Onyx
  logs/timing and unchanged offline resume pass. Existing installed Linux Onyx
  was used for the isolated conversion; native Windows execution is not inferred.
- An independent stdlib-only copy validates all group/helper/recipe pins and
  174 total / 137 new selections. A real I Bet My Life/Take Me to the Beach
  comparison recognizes the renamed installed copy, exports one absent song,
  removes an internal duplicate and leaves all inputs unchanged; ZIP CRC/hashes pass.
- All ten final ZIPs and 864 song assets pass CRC/SHA256 checks. Protected old
  recipes/helpers/coverage/experiment hashes, cumulative index counters, report
  counts, actual default Windows path budgets, staged diff and Git/media hygiene
  are audited before publishing.
Native Windows execution, Scan Songs, perceived timing and playability of these
new charts remain pending. No game_verified flag, ML default, checkpoint, spectral
profile, transcription/exporter phase or acoustic accuracy claim is advanced.
