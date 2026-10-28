# The Strokes preparation — 2026-10-28

DCF-LIB-016 is a curated 20-song selection, not a full-band catalog import. It
appends batches 41–42: {'pro': 18, 'standard': 2}, taking the collection from 655 to 675.
No previous The Strokes chart was found in the published recipes. All earlier
recipes remain byte-identical; new Qobuz/playlist ID lists are empty.

## Research and selection

The user confirmed that “strolks” meant The Strokes. Public RhythmVerse searches
in CH, PS, RB3 and all returned 29, 0, 54 and 85 rows respectively, reconciling
to 85 unique packages. Encore advanced exact-artist Expert/drums search returned
26 rows. These are discovery counts, not successfully downloaded songs. Native
creator Drive publications supply Encore sources; its unavailable mirror is not
used. The existing SNG reader and actual-container selection remain unchanged.

Read-only Spotify search/catalog calls supplied song/album references and URLs.
The generated recommendation was not an official best-song ranking. Only name,
artist, album, ordinary catalog URI/URL and duration metadata were retained;
playback URIs/preview audio were not persisted or used as song assets. No playlist
or user library was saved/edited. Primary source metadata, not streaming audio,
was used for chart acquisition. NME search snippets informed classic highlights:
https://www.nme.com/news/music/the-strokes-132-1274769 and
https://www.nme.com/lists/the-strokes-their-10-best-songs-so-far-ranked-1191.
Direct article retrieval returned 403; the full articles were not read and no
article/lyric prose was copied. Selection order is our editorial choice, with
six-album variety and validated drum availability, not a popularity statistic.

25 studio titles were planned; the first 20 validated songs by priority were
selected. Two other validated songs remain reserves. Bad Decisions and Call It
Fate, Call It Karma have no conservative drum match in these queries; Machu
Picchu has unavailable sources. Every case stays in the public metadata CSV.
A title-filter review corrected two false exclusions: You Only Live Once and
Under Cover of Darkness are studio titles. Recording qualifiers require brackets
or an explicit version suffix. A metadata regression retains these titles among
the essential highlights. No acquisition code or earlier recipe changed.

## Validation and preservation

All 92 runtime assets, 31 audio decodes, 28,994 Expert
gems and two ZIPs were checked; source/asset SHA256 and ZIP CRC agree. Formats:
{'sng': 2, 'files': 8, '7z': 1, 'zip': 2, 'onyx': 7}. Native source audio/notes are preserved; console material uses the
unchanged pinned Onyx path. Source evidence, not catalog Pro flags, determines
mode. Ordinary Drums is separate from Pro Drums.

The project-local diagnostic skill was applied to pairing/provenance and the
interpretation of game markers. This curation does not create a new transcription
or acoustic benchmark; no per-class acoustic accuracy is claimed. Existing mix
baselines, raw notes, profile and study inputs/results stay unchanged. No model,
weights, ML dependency or converter update was introduced.

Prior index playlist/coverage fields, Linkin Park expansion, group selection
metadata and all helper hashes remain unchanged. recover_pilot.py changes only
its collection-index SHA256 pin. Onyx still has the corrected native Windows
arguments, persistent logs/timing, elapsed feedback, deadline supervision and
Ctrl+C/resume behavior. Runtime media and raw logs remain ignored.

The Windows guide fetches only new The Strokes recipe JSONs and selects batches
through the existing --restante --lote CLI. additions.py compares actual present
folders against the installed library, handling renamed folders and uncertain
editions without modifying inputs. The user's PC inventory is not remotely known.

## Executed checks

- Linux/Python 3.12.14, uv 0.12.23 and FFmpeg 7.1.5 on CPU. Runtime network policy
  was current/unrestricted/enforced; no account credential or ML weight was used.
- 173 pytest cases and 19 optional DSP unittest cases pass. Locked sync/project
  lock and all three optional-script locks pass. Ruff lint/format (src/tests and
  diagnostic scripts), strict mypy, help/doctor text/JSON, inspect-midi help and
  diagnostic help pass. Dependencies/locks remain unchanged.
- python -I -S in a clean directory, without drumforge, Mido, gdown or pytest,
  reconstructs **all 20 final songs** through --restante --lote 41/42. All five
  source formats run locally. Only these two recipe JSONs are present, matching
  the guide's selective download. The existing verified Linux Onyx executable was
  reused; Windows CLI behavior is covered by the unchanged platform regressions,
  not claimed as natively run here.
- All 20 resume offline with every source/asset/ZIP/receipt/log hash unchanged.
  Seven successful Onyx logs retain both stage completions and timing JSONL.
- Actual recovered folders, three renamed installed copies and an internal copy
  produce 3 ja_na_biblioteca, 17 adicionar and 1 repetida_candidata. All exported
  ZIP asset hashes match their candidate files; inputs remain byte-identical.
- Both delivery ZIPs, 92 assets, Windows default path budgets, public report
  counts and all protected old source/recipe/helper/coverage/experiment hashes
  pass audit. The recover_pilot diff is exactly its index pin. The prior group
  selection namespace is preserved and all cumulative counters reconcile.
- Wheel/sdist members contain intended helpers/metadata/docs, without media,
  private logs, models or caches. The existing sdist selection intentionally
  excludes song-library; its Windows guide/CSV are published as GitHub files.
  The exact staged diff, tracked-path hygiene and remote synchronization are
  reviewed before closure.

 Native Windows/individual Scan Songs, timing and gameplay remain
pending. game_verified flags stay false; library preparation does not advance the
transcription/exporter acceptance phases.
