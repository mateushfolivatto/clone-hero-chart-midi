# Two-pedal priority and optional Nightmare replacement

The user requested a permanent preference for two-pedal charts and another
Nightmare edition. Future selections prioritize verified Expert+/2x Kick or
explicitly authored full-double-bass sources. AGENTS.md, CONTEXT.md, the local
drum-audio-diagnostics skill and the song-library guide retain this instruction.
Single-pedal/unverified fallback must be identified. No missing hits are invented.

## Existing song and the game setting

The original batch-06 source is ImPhanty's Nightmare, file
4767c1410f504d1d82ba58f0c2dfcef8. Its pinned chart/INI/audio were rechecked:
893 base kicks plus 471 optional .chart note-32 kicks, 1,364 total.
It already contains Expert+ data. The
[official modifiers guide](https://wiki.clonehero.net/books/clone-hero-manual/page/song-modifiers)
and [drum FAQ](https://wiki.clonehero.net/books/guitars-drums-controllers/page/drum-faqs-and-troubleshooting)
were read: enable **Modifiers > 2x Kick** to expose optional Expert+ kicks.
This does not establish which version/settings are installed on the user's PC.

The inspector adds `expert_plus_kick_note_on_count` and
`kick_note_on_count_with_2x`, using .chart 32 or positive MIDI note-ons at 95 in
PART DRUMS. Existing base-Expert counts retain their meaning. Four synthetic
regressions exercise both formats, absent extras, zero-velocity note-ons and
notes in another track/difficulty. The inspection never rewrites chart bytes.
A full 2x edition can encode every kick as ordinary 0/96, so absence of optional
notes is not proof that a source reduces double bass. Author provenance and
actual chart inspection remain required; density/Pro Drums alone are insufficient.

## Alternate edition, source and inspection

The public RhythmVerse drum-filter search for Nightmare was paginated and cached;
an Encore search with exact artist and a Nightmare title filter returned seven drum entries. These were
researched via their public catalog APIs. The selected original package is
[UriasP's 2x Bass Pedal Expert+ publication](https://rhythmverse.co/songfile/65648a0a2a394727890178908126c9be),
credited to Harmonix. It was obtained and actually inspected locally, not merely
listed or inferred from the catalog's Pro flag (which is zero).

- Original format: native 7z, 402,303,700 bytes.
- Original SHA256: efc4b58658075c76bba058bb2deecef877fc500075e89c0b4c4a44ff723350c9.
- MIDI SHA256: febd5bc79a4d3a08c2f252536305a9a42dc1af1bc2b8b157416311fa53a05d2b.
- Expert: 2,493 base gems, 916 base kicks, 454 optional kicks, 1,370 combined kicks
  and 2,947 gems with optional kicks. Forty tom markers and authored pro_drums=True.
- Optional kicks span 38.937096–363.166098 seconds; no simultaneous base/optional
  kick attacks were found. The source audio covers them.
- Ten runtime assets, 54,093,211 bytes; all seven Ogg streams fully decoded.
- Source and prepared notes, INI and audio are byte-identical. No Onyx conversion
  or Pro-flag patch was needed. The package's background video remains in the
  original, outside the runtime folder. The publication describes an edited live
  background, not a proven identity with a streaming master or a live audio edition.

The optional recipe is **nightmare_2x.json**, SHA256
911067fefd52499033138374531ccc2b6a57700b79b606bfb10a3e2d7d0e3894.
It references the unchanged batch-06 recipe/song as its replacement target.
It is outside collection_index.json and the automatic batches; the default
selection remains 675 charts. This adds an optional chart for the same song,
not another unique playlist entry. No coverage counts or old metadata were changed.
The metadata regression verifies its guide pin, 2x counts and optional scope.

## Delivery and real reconstruction

[DOIS-PEDAIS.md](../song-library/DOIS-PEDAIS.md) includes a complete Windows
PowerShell command and next-session prompt. It downloads only the recipe plus
two standard-library recovery programs pinned to already published revision
e6251a31a1e33658a152479664b84fa190667e65, verifying all SHA256 values before import.
The existing Onyx/7-Zip/MEGA/additions/group-recovery programs and index remain
byte-identical. No source, MIDI, audio, video or ZIP is committed.

The guide's exact embedded Python was extracted and run with **python -I -S**
in a separate directory, without drumforge, Mido, gdown or pytest imports.
It started with fresh output folders and the pinned original in its source cache;
the 402-MB original was not downloaded twice. The unchanged portable 7-Zip reader
performed the real extraction. All ten asset hashes, ZIP CRC and archived asset
hashes passed. The first local delivery ZIP has 53,663,955 bytes; ZIP container
bytes can differ between fresh outputs because file timestamps differ.

A second run blocked URL requests and verified every file, size, hash and mtime
unchanged, including the local ZIP. This proves cached-source reconstruction and
offline resume, not a second fresh HTTP download or native Windows execution.
Ignored execution evidence is under work/double-kick-017/.

The command prepares downloads only. The guide instructs the user to move the
old Nightmare outside every scanned root, copy the new folder once, Scan Songs,
and enable Pro Drums / Expert with 2x Kick. An absent-song comparator may treat
the alternate as already present because its original title is still Nightmare;
this is an explicit chart replacement. Both sources retain paired notes/audio.

## Gates and limits

178 core tests, 19 optional DSP checks, locked project/script checks, Ruff
lint/format, strict mypy, CLI smoke and distribution hygiene pass on Linux/
Python 3.12. Existing recipes, helpers, Qobuz coverage and frozen audio-study
inputs/profiles/results were checked against the initial baseline.

This task inspects existing charts; it does not measure acoustic transcription
accuracy, identify physical left/right hits, or establish that one edition is
more accurate. Native Windows, game scan, perceived synchronization and two-pedal
playtesting remain pending. No game_verified flag was changed.
