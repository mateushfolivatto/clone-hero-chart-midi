# Dependency and model license register

Audit date: 2026-09-10. Engineering inventory, not clearance to redistribute models.
No ML package or model is installed, invoked or distributed by Phase 0.
Each future adapter must pin a commit and record the checkpoint URL, size, SHA256
and independent weight terms before downloading. Unknown terms remain unresolved.

| Component / primary source | Code terms | Weight terms | Distribution / commercial use / attribution | Decision |
| --- | --- | --- | --- | --- |
| [ADTOF original](https://github.com/MZehren/ADTOF) | CC BY-NC-SA 4.0 declared for repository content | Trace provenance of each converted checkpoint; no independent permissive grant verified | Noncommercial restriction; attribution and ShareAlike obligations apply under declared terms | Research reference only |
| [ADTOF-pytorch](https://github.com/xavriley/ADTOF-pytorch) | No license field in inspected pyproject and no root LICENSE shown; unresolved | README says weights converted from original and bundled | Do not infer permission to redistribute or use commercially; preserve original authors' attribution | Candidate local transcription spike; no dependency yet |
| [ADTOF Plus](https://github.com/xavriley/adtof_plus_drum_transcription/blob/main/pyproject.toml) | MIT declared | ADTOF and MDX terms independent and unresolved | MIT code requires copyright/license notice; does not license weights or dependencies | Reference only; unpinned Git dependencies and Essentia complicate installation |
| [MDX23C adapter](https://github.com/xavriley/mdx23c-drum-separation/blob/main/pyproject.toml) | MIT declared | Check mix-to-kit and kit-to-components checkpoints separately | MIT code allows commercial reuse with notices; weight permission not verified | Candidate replaceable separator |
| [Music Source Separation Training](https://github.com/ZFTurbo/Music-Source-Separation-Training) | MIT | Per-checkpoint terms; not established by framework license | Code notices required; no model redistribution authorized by this audit | Alternative MDX23C host; inference not tested |
| [midi2clonehero](https://github.com/apvilkko/midi2clonehero/blob/main/LICENSE) | MIT, Antti Pekka Vilkko (2024); raw LICENSE read | No model | Commercial reuse allowed with copyright/license notice; no code copied or distributed | Mapping reference only |
| [mdxnet-infer 0.1.0](https://github.com/openmirlab/mdxnet-infer) | MIT; preserves KUIELab, ZFTurbo and OpenMIRLab notices | DrumSep authors supplied no explicit terms; upstream advises noncommercial-safe only | Code notices required; weight redistribution/commercial permission unresolved | Preferred optional separator spike, not minimum install; no checkpoint downloaded |

The 2026-09-11 audit strengthens the ADTOF conclusion: source commit `85c192e`
contains no LICENSE file. Its bundled converted checkpoint is 3,617,805 bytes with
observed SHA256 `1bc986e596ec47ba0b44916f87cd4a39f0b2bec23596df3fb5d0e87749217320`.
Local execution does not supply missing redistribution or commercial-use rights.
See `phase-1-windows-compatibility.md` for the complete matrix.

## Bootstrap tools

Runtime uses Python standard library only. Development tools are not runtime
dependencies or model providers. Exact resolved versions and transitives belong in
uv.lock; inspect installed distribution metadata after synchronization.

| Tool | Primary license source | Terms / use |
| --- | --- | --- |
| Python | https://docs.python.org/3/license.html | PSF and bundled notices; use installed interpreter |
| uv | https://github.com/astral-sh/uv | MIT OR Apache-2.0; local development tool |
| pytest | https://github.com/pytest-dev/pytest/blob/main/LICENSE | MIT; preserve notices if redistributed |
| Ruff | https://github.com/astral-sh/ruff/blob/main/LICENSE | MIT; preserve notices if redistributed |
| mypy | https://github.com/python/mypy/blob/master/LICENSE | MIT; preserve notices if redistributed |
| Hatchling | https://github.com/pypa/hatch/blob/master/LICENSE.txt | MIT; build tool, preserve notices if redistributed |

These tools have no model weights or noncommercial-only requirement under the
listed licenses. Public binary packaging is outside Phase 0; audit transitive
notices and Python bundled components before any such distribution.

## Resolved development/build inventory

Verified from installed distribution metadata, 2026-09-10. All entries have no
model weights and are development/build-only; none are embedded in our wheel.
Hatchling is also in the dev group so `build --no-build-isolation` uses locked
build dependencies rather than resolving transitives again.

| Package | Version | License / distribution obligations |
| --- | --- | --- |
| pytest | 9.1.1 | MIT, retain notices |
| ruff | 0.16.7 | MIT, retain notices |
| mypy | 1.20.2 | MIT, retain notices |
| hatchling | 1.27.0 | MIT, retain notices |
| trove-classifiers | 2026.6.1.19 | Apache-2.0, retain license/notices |
| colorama | 0.4.6 | BSD, retain copyright/disclaimer |
| iniconfig | 2.3.0 | MIT, retain notices |
| librt | 0.15.0 | MIT, retain notices |
| mypy-extensions | 1.1.0 | MIT, retain notices |
| packaging | 26.3 | Apache-2.0 OR BSD-2-Clause, comply with chosen license |
| pathspec | 1.1.1 | MPL-2.0, file-level source obligations if distributing modified covered files |
| pluggy | 1.6.0 | MIT, retain notices |
| Pygments | 2.21.0 | BSD-2-Clause, retain copyright/disclaimer |
| typing-extensions | 4.16.0 | PSF-2.0, retain notices |

Package source URLs and hashes are in uv.lock. All listed licenses allow commercial
use subject to their conditions. No tools were modified for redistribution; the
project itself has no public distribution license selected yet.

## Optional song-library tools (2026-10-16)

Mido 1.3.3 is an optional metadata/MIDI inspection tool under MIT, verified from
installed package metadata; source: https://github.com/mido/mido/blob/main/LICENSE.
It is invoked through `uv run --locked --with mido==1.3.3`, not embedded in the
project wheel or the song ZIP. It has no weights. Preserve notices if redistributed.
The existing FFmpeg build reports GPL terms via `ffmpeg -L`; it is invoked locally
for probing/decoding, and its executable is not included in the song delivery.
No upstream implementation was copied and no model was installed for the pilot.

Downloaded charts/media retain their original terms and credits; source, uploader
and the chart's own author field are recorded separately in private manifests.
They remain ignored by Git and excluded from project distributions. This private
preparation task does not infer redistribution permission from a wrapper or uploader.
