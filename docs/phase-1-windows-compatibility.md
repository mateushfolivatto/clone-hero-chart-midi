# Phase 1 native Windows compatibility audit

Audit date: 2026-09-11. Target: Windows 10 x64, PowerShell 7.4.13,
CPython 3.12.0, 4 logical CPUs, 15.9 GiB RAM, Intel HD Graphics 630 and no
NVIDIA/CUDA. This is an engineering compatibility report, not legal advice.

## Executive conclusion

The smallest configuration that has actually produced `audio -> drum
transcription -> MIDI` on this host is:

```text
PCM WAV, 44.1 kHz mono
  -> ADTOF-pytorch 0.1.0 at 85c192e (explicit device="cpu")
  -> PyTorch 2.12.0+cpu and the resolved librosa/pretty_midi stack
  -> raw General MIDI percussion file
```

Use a portable native Windows FFmpeg executable to normalize MP3/FLAC/other
inputs to WAV before inference. FFmpeg is not needed for the already-normalized
WAV smoke test, but it is the smallest reliable codec boundary for Phase 1.
FFmpeg itself ships source; its official download page points Windows users to
external prebuilt providers.[^1]
Source separation should be **off by default** for the first spike. This avoids
another roughly 417--500 MiB checkpoint, much higher CPU cost and a second
unresolved weight license. It also provides the fastest way to learn whether
ADTOF on the full mix is useful enough. Separation remains a replaceable later
experiment, not a prerequisite.

This recommendation is viable for local research only. ADTOF-pytorch has no
license file, and its converted weights have no independent grant beyond their
provenance from the CC BY-NC-SA 4.0 original. Do not redistribute the wrapper or
weights, and do not assume commercial-use permission.

## Compatibility matrix

`Yes (tested)` means exercised on this exact native host. `Metadata` or `static`
means the narrower evidence stated; it is not an inference claim.

| Component / snapshot | Native Windows | Python 3.12 / artifact | Native compilation | FFmpeg | CUDA | Approximate transfer / disk | Code license | Weight license | Decision |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| FFmpeg 9.0.1, Gyan essentials | Yes; provider requires Windows 10+ | Not a Python package; `ffmpeg.exe`/`ffprobe.exe` | No; prebuilt archive | It is the codec tool | No | 33 MB `.7z` or 106 MB `.zip` | FFmpeg normally LGPL-2.1-or-later; this provider's static essentials build is GPLv3 | None | Recommended portable codec boundary; absent from PATH during audit |
| PyTorch 2.12.0+cpu | **Yes (tested)** | Official `cp312-cp312-win_amd64` wheel | No | No | No; `torch.cuda.is_available()` was false and inference worked | 122.9 MB wheel in the observed install | BSD-style | None | Pin CPU index/build; do not install a CUDA wheel |
| ADTOF-pytorch 0.1.0, `85c192e` | **Yes (tested)** for WAV-to-MIDI smoke | Declares Python >=3.9; source built a `py3-none-any` wheel on 3.12 | Wrapper no; binary transitives use wheels | No direct requirement for WAV; use FFmpeg before it for predictable compressed-input handling | No; API falls back, but Phase 1 must request `cpu` explicitly | Source-built wheel 1.9 MiB compressed; bundled checkpoint 3,617,805 bytes (3.45 MiB) | **No license file / no usable grant found** | Converted from original ADTOF weights; no independent grant found; treat as CC BY-NC-SA 4.0/noncommercial at minimum | Smallest working transcriber, local research only; pin commit and checkpoint SHA256 |
| ADTOF Plus 0.1.0, `58c1eb4` | **No as published** | Declares >=3.8, but requires Essentia; PyPI has no Windows/cp312 Essentia wheel | Essentia would require a complex C++ build; Git dependencies also build from source | Not direct, but codec support is delegated to audio libraries | No hard requirement; underlying models can use CPU | Approximately two old MDX checkpoints advertised near 500 MB each, plus ADTOF/PyTorch | MIT declared, with placeholder package metadata | Inherits unresolved ADTOF and MDX terms | Reject for this environment; do not hide Essentia incompatibility |
| `mdx23c-drum-separation` 0.1.0, `80ae44e` | Static syntax succeeds; inference not tested | Declares >=3.8; no PyPI release, source install only; transitives have cp312 wheels | Wrapper no; transitives use wheels | No direct requirement for WAV | CPU fallback exists; CUDA optional | Around 500 MB for mix-to-kit and 438 MB observed for the old five-stem checkpoint; cache may duplicate files | MIT | Not established; old five-stem primary host is gone | Reject: alpha/source-only, unpinned downloads, Unix-named cache convention, and load errors can degrade into random weights |
| `mdxnet-infer` 0.1.0, tag `84458e9` | **Yes (40 package tests)**; no real-weight inference | Declares >=3.10; 22 KB `py3-none-any` wheel; installed on 3.12 | Package no; transitives use wheels | No direct requirement for WAV | CPU accepted; CUDA optional | 417.4 MiB (437,652,699 bytes) for `drumsep-6stem`, plus tiny YAML; not downloaded | MIT, preserving KUIELab/ZFTurbo notices | Original authors supplied no explicit terms; treat as noncommercial-safe only, not MIT | Best later separator candidate, but optional and not cleared for redistribution |
| `mdxnet-infer` current `master`, `c86c9b6` | Static syntax succeeds; upstream CI is Ubuntu-only | Declares/test-matrix Python 3.10 and 3.12; unreleased APIs differ from 0.1.0 | Same wheel expectations when released | No direct requirement | CPU explicit; CUDA/MPS optional | Same model family | MIT | Same unresolved terms | Do not mix `master` tests/API with the 0.1.0 wheel; pin one immutable revision |

The matrix combines the Windows provider's archive/license data,[^2] FFmpeg's
own license explanation,[^3] the official PyTorch CPU wheel index and license,[^4]
ADTOF's pinned metadata/API,[^5] and the original ADTOF license declaration.[^6]
ADTOF Plus exposes Git and Essentia dependencies directly,[^7] while the Essentia
index has no Windows wheel.[^8] The two MDX assessments use their pinned package
metadata and model provenance rather than treating a mirror as a license.[^9][^10]

## Transitive dependency result

The ADTOF smoke resolved and installed entirely from wheels on CPython 3.12 x64:

| Layer | Observed packages | Windows 3.12 result | Material license notes |
| --- | --- | --- | --- |
| Numeric/ML binaries | NumPy 2.5.3, SciPy 1.18.1, scikit-learn 1.9.1, Numba 0.67.0, llvmlite 0.49.0, PyTorch 2.12.0+cpu | Compatible wheels; no compiler invoked | BSD-family; llvmlite includes LLVM-related notices |
| Audio | librosa 1.0.0, SoundFile 0.14.0, soxr 1.1.0, cffi 2.1.1 | Compatible universal/Windows wheels | librosa ISC; SoundFile BSD, bundled libsndfile LGPL; libsoxr LGPL-2.1-or-later |
| MIDI | pretty_midi 0.2.11.post0, mido 1.3.3, six 1.17.0, importlib_resources 7.1.0 | Pure-Python wheels | MIT/BSD/PSF-family notices; no model |
| Utility/runtime | joblib, pooch, requests, msgpack, packaging, platformdirs, lazy_loader and PyTorch utilities | Wheels resolved; no compiler invoked | Predominantly BSD/MIT/Apache/PSF-family; retain notices when distributing |

The disposable environment occupied about 1,015 MiB after ADTOF, PyTorch, the
separator wheel and test tooling. The observed ADTOF/PyTorch dependency downloads
were roughly 235 MB before caches and unpacking. These numbers will change with
pins; upstream ADTOF provides no upper bounds, so Phase 1 must lock the exact
tested set rather than accept future latest versions silently.

PyPI evidence independently shows current Windows CPython 3.12 wheels for
NumPy, SciPy, Numba and SoundFile; librosa and pretty_midi publish universal
wheels.[^11] `pretty_midi`'s older releases were source-only, but 0.2.11.post0
has a universal wheel.

## Checkpoints and trust boundaries

| Checkpoint | Size / identity | Acquisition behavior | License conclusion |
| --- | --- | --- | --- |
| `adtof_frame_rnn_pytorch_weights.pth` | 3,617,805 bytes; observed SHA256 `1bc986e596ec47ba0b44916f87cd4a39f0b2bec23596df3fb5d0e87749217320` at `85c192e` | Bundled inside the Git source/package; ADTOF currently loads with `strict=False` and can continue when weights are absent or partially mismatched | No independent weight license; derived from original CC BY-NC-SA 4.0 material. Redistribution/commercial use blocked pending clarification |
| MDX23C old mix-to-kit | Upstream warning says approximately 500 MB; exact bytes not verified | Automatic Hugging Face download without immutable revision; copies into a second cache layout | Unknown; mirror is not a license grant |
| MDX23C old five-stem | A surviving mirror reports 438 MB; old adapter warns approximately 500 MB | Old primary source disappeared; old adapter names a mutable mirror | Unknown; do not ship |
| `mdxnet-infer` DrumSep six-stem | 437,652,699 bytes (417.4 MiB); SHA256 `d2a4aa53eb584d21eead358a4e66d1882ad182911be018f052b5da73be9096d0` | Release-pinned, verifies download and cached copy; not downloaded in this audit | Original authors did not state terms; noncommercial-safe only pending confirmation |

PyTorch checkpoints are pickle-based inputs and must be treated as executable
trust boundaries. Phase 1 must accept only an allowlisted filename/revision and
known SHA256. ADTOF's current permissive `strict=False` behavior is unsuitable
for the project adapter: missing, unexpected or absent weights must fail before
inference, never generate confident-looking MIDI from random parameters.

## Local evidence and limitations

- Phase 0 was already closed on `main` by merge commit `b988f37`; the initial
  Windows fix commit is `9833d7b`. The tree was clean before this audit branch.
- `ffmpeg` and `nvidia-smi` were absent from PATH. No CUDA runtime was installed.
- All four source snapshots compiled as Python syntax under CPython 3.12.0.
- ADTOF and all direct/transitive dependencies installed without compiling a
  native extension. The produced ADTOF wheel was pure Python.
- A two-second, 44.1 kHz mono synthetic impulse WAV produced a valid 96-byte MIDI
  with six notes in 9.79 seconds on CPU. This validates the execution path only;
  it says nothing about accuracy, whole-song runtime or memory.
- `mdxnet-infer` 0.1.0 installed from its universal wheel and its matching
  `v0.1.0` suite passed 40 tests on this Windows/Python 3.12 host. One PyTorch
  warning reported deprecated `stft(return_complex=False)` behavior.
- Tests from current `master` failed against the 0.1.0 wheel because unreleased
  modules/APIs are absent. This is version skew, not proof that either snapshot's
  own matching installation fails.
- No MDX checkpoint was downloaded and no source-separation inference ran.
- No private/copyrighted audio was accessed. The synthetic WAV, MIDI, cloned
  sources and temporary virtual environment were deleted after evidence capture.

## Phase 1 entry recommendation

When DCF-100 is explicitly authorized, use one locked optional ML environment:

1. Add a project-controlled FFmpeg/ffprobe path option and detect `ffmpeg.exe`
   via `shutil.which`; never require a Bash shell or global PATH edit.
2. Normalize a copied working file to mono PCM WAV at 44.1 kHz. Keep all paths as
   `pathlib.Path` and invoke subprocesses with argument lists and `shell=False`.
3. Pin PyTorch CPU and the exact successful transitive set. Do not expose CUDA as
   required or select a CUDA index on this host.
4. Pin ADTOF to `85c192e`, require the checkpoint SHA256 above, force `device="cpu"`,
   and reject missing/unexpected model keys before running.
5. Start with full-mix transcription and `--skip-separation` semantics. Measure
   accuracy/runtime on a short private excerpt before paying the separation cost.
6. If separation materially improves the result, evaluate `mdxnet-infer` 0.1.0
   in its own adapter and explicitly approved local cache. Do not redistribute its
   weights, and do not make it the minimum install.

Phase 1 must not begin until the user explicitly starts DCF-100 onward.

## Sources

[^1]: FFmpeg Project. “[Download FFmpeg](https://ffmpeg.org/download.html).” Accessed 2026-09-11.
[^2]: Gyan Doshi. “[FFmpeg Builds for Windows](https://www.gyan.dev/ffmpeg/builds/).” Accessed 2026-09-11.
[^3]: FFmpeg Project. “[FFmpeg License and Legal Considerations](https://www.ffmpeg.org/legal.html).” Accessed 2026-09-11.
[^4]: PyTorch. “[CPU Wheel Index](https://download.pytorch.org/whl/cpu/torch/)” and “[LICENSE](https://github.com/pytorch/pytorch/blob/main/LICENSE).” Accessed 2026-09-11.
[^5]: Xavier Riley. “[ADTOF-pytorch at 85c192e](https://github.com/xavriley/ADTOF-pytorch/tree/85c192e78f716ea0b111cc8a5ee4a8f6a3a4f8a9).” Accessed 2026-09-11.
[^6]: M. Zehren et al. “[ADTOF](https://github.com/MZehren/ADTOF).” Accessed 2026-09-11.
[^7]: Xavier Riley. “[ADTOF Plus at 58c1eb4](https://github.com/xavriley/adtof_plus_drum_transcription/tree/58c1eb431cddc2c10530f4f369f36825677b78ec).” Accessed 2026-09-11.
[^8]: Python Package Index. “[Essentia file index](https://pypi.org/simple/essentia/).” Accessed 2026-09-11.
[^9]: Xavier Riley. “[mdx23c-drum-separation at 80ae44e](https://github.com/xavriley/mdx23c-drum-separation/tree/80ae44e3d2c091e7413512bfb2a2ec7c989a095c).” Accessed 2026-09-11.
[^10]: OpenMIRLab. “[mdxnet-infer](https://github.com/openmirlab/mdxnet-infer)” and “[v0.1.0 release](https://github.com/openmirlab/mdxnet-infer/releases/tag/v0.1.0).” Accessed 2026-09-11.
[^11]: Python Package Index. File indexes for [NumPy](https://pypi.org/simple/numpy/), [SciPy](https://pypi.org/simple/scipy/), [Numba](https://pypi.org/simple/numba/), [SoundFile](https://pypi.org/simple/soundfile/), [librosa](https://pypi.org/simple/librosa/) and [pretty_midi](https://pypi.org/simple/pretty-midi/). Accessed 2026-09-11.
