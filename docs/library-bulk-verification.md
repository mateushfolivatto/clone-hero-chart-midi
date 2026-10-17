# MixDrumRock bulk preparation — 2026-10-17

The user confirmed receiving the pilot and authorized the remainder. This pass
prepared existing public charts, independently of MP3 transcription. It did not
generate music, download Qobuz audio/models, or establish game acceptance.

## Delivered scope

| Measure | Verified result |
| --- | --- |
| Current public Qobuz snapshot | 744 ordered entries / 744 track IDs |
| Additional charts | 254: 246 Pro Drums, eight ordinary four-lane Drums |
| New batches | 11, numbered 02–12; ordinary Drums isolated in batch 12 |
| With the unchanged pilot | 266 charts cover 275 playlist entries |
| Outstanding entries | 358 without a conservative match, 50 version reviews, 61 access/preparation blockers |
| New runtime assets | 1,449 files, including 629 decoded audio files |
| Expert drum gems inspected | 504,992 |
| New archive inputs | 52 ZIP, 45 public Drive folders, 39 RAR, 17 7z, 101 Onyx console conversions |
| Final ZIP total | 3,294,838,600 bytes; 11 ZIPs with song folders, no nested source archives |
| Original download budget | 3,952,089,814 bytes; approximately 13 GB free recommended for complete recovery |

Sources, authors, sizes, hashes, configuration changes and Qobuz IDs are recorded
in `drumforge/library/collection_02.json` through `collection_12.json`. The pinned
index identifies the exact recipes and standalone helper versions. The metadata
coverage CSV preserves all 744 entries, original order, album/version and reasons
for gaps. Duplicate playlist entries may share a chart; matching title/duration
does not establish an identical master. Audio remains paired with its source chart.

## Checks performed

- Complete Qobuz CSV/XLSX/JSON export; cached CH/PS/RB3/all public catalog views
  for all 37 artists, with drums filtering and pagination guards. Exact normalized
  artist/title, explicit live/version checks and duration differences generate
  selections or reviews; fuzzy matches do not silently become prepared songs.
- Strict conductor/PART DRUMS or ExpertDrums parsing, usable Expert notes/kick,
  rejection of five lanes, Pro configuration/marker evidence where claimed,
  FFprobe duration checks and FFmpeg decoding of every delivered audio asset.
  Other instrument tracks and perceived synchronization are outside this check.
- Each of the 11 ZIPs passed CRC and every extracted runtime asset was compared
  with its recipe SHA256. Sources stay private in the ignored collection tree.
- Standard-library recovery outside the checkout exercised ZIP, Drive assets,
  solid RAR, 7z and console conversion, followed by unchanged resume. A separate
  fresh public MEGA download checked HTTPS, the provider MAC and pinned plaintext
  SHA256, reconstructed ordinary Drums, and resumed from a freshly read recipe
  without network/conversion. The original twelve-song recovery still passed
  with `python -I -S` and preserved its existing ZIP.
- 65 offline tests passed. These include pagination/mutation, archive safety,
  overwrite preservation, partial-batch continuation, C3-style INI comments,
  ordinary/Pro separation, append-only recipe updates, local converted-output
  receipts, NIST AES vectors, MEGA quota rejection and invalid-MAC rejection.
- Locked dependency check, CLI help/doctor, Ruff, strict mypy and distribution
  build passed. Doctor's optional ML warnings are expected; no model was installed.

The real reconstruction checks ran on cloud Linux/Python 3.12. For console smoke
tests the verified Linux Onyx executable was supplied explicitly; the portable
Windows release was hash-checked and its distribution structure inspected, but
was not executed on this machine. Windows execution, Scan Songs, e-kit input,
musical accuracy and synchronization still need user validation.

## Conversion and provider findings

Onyx 20261016 was fetched from its official release with SHA256 verification.
Its default PS export preserved five lanes in a real source test, so that output
was rejected; a different native four-lane Heart-Shaped Box package was found.
Eight charts with ordinary drums but insufficient Pro evidence were retained in
their own labeled batch. No five-lane flag or orange notes were deleted to claim
conversion. Native audio/notes remain intact; console inputs are converted by Onyx.

Independent Onyx builds reproduced MIDI/INI while Ogg serial numbers varied.
The PC route therefore pins original archive, tool and MIDI identities, then
records local converted-asset hashes for repeat-run/edit protection. It does not
pretend the converted Ogg bytes equal cloud output. Pro flags are only supplemented
from existing markers; ordinary drums are not forcibly promoted by the downloader.

Drive folder listings sometimes succeeded while required file downloads returned
an explicit quota-exceeded HTML page. Marketplace/missing links, inaccessible
providers, malformed charts and uncertain editions remain explicit gaps. No quota
or access-control workaround was used. MEGA reads only the supplied public link
and its key; it uses Python's existing OpenSSL library, not a third-party client.
One historical HTTP download URL was upgraded to HTTPS and its complete archive
matched the previously inspected SHA256 before recipe publication.

## Reproduction and continuation

User delivery: [CONTINUACAO.md](../song-library/CONTINUACAO.md). The current cloud
copies are in `/workspace/shared/downloads/MixDrumRock-continuacao/`; these are
temporary conveniences, not permanent public download URLs. The durable PC route
reconstructs the collection from upstream sources using versioned recipes.

Developer workflow, using a fresh public Qobuz export directory:

```text
uv --cache-dir .uv-cache run --locked --with openpyxl==3.1.5 python -m drumforge.library.qobuz 69773629 --output-dir NEW_SNAPSHOT --xlsx
uv --cache-dir .uv-cache run --locked --with mido==1.3.3 --with gdown==5.2.1 python -m drumforge.library.batch NEW_SNAPSHOT/playlist.csv --root PRIVATE_COLLECTION --onyx VERIFIED_ONYX_EXECUTABLE
uv --cache-dir .uv-cache run --locked python -m drumforge.library.delivery NEW_SNAPSHOT/playlist.csv --root PRIVATE_COLLECTION --metadata-dir src/drumforge/library --report song-library/reports/cobertura.csv
```

The collector caches pages and verified preparations; failures are retried only
when deliberately requested after diagnosis/state changes. `--pro-only` excludes
ordinary drums. The freezer appends recipes, keeps prior Qobuz selections and
prints the index digest to pin in `COLLECTION_SHA256`. Recheck every recipe/helper,
recover representative formats, validate new ZIPs and run configured gates before
commit, merge and push. Do not overwrite already published recipes to change a
selection. Existing user-library inventory and fully exercised Windows updates
remain DCF-LIB-002/006 follow-ups; the overall library workstream remains open.
