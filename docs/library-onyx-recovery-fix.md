# Onyx recovery correction — 2026-10-17

The user reported problems around batch 07. Their pasted output identifies batch
08 and contains repeated Onyx `import` exit-1 failures plus one independent
Octavarium network read timeout. Batch 07 contains no Onyx recipes; batches 08–11
contain 96 and batch 12 contains five. This report does not diagnose an unseen
batch-07 error or establish that its recovery succeeded.

## Diagnosis

The downloader passed `+RTS -N2 -RTS` to both distributions. Upstream release
20261016 defines `-threaded -with-rtsopts=-N` for the GUI `onyx` executable,
but the separate `onyx-cli` target specifies neither threaded nor runtime-option
support. The pinned Windows distribution is that CLI; the tested Linux AppRun
uses the GUI executable. The same flags cannot be assumed to work in both.

Authoritative release sources inspected:

- [package.yaml](https://github.com/mtolly/onyx/blob/20261016/haskell/packages/onyx-exe-toolkit/package.yaml)
- [CLI.hs](https://github.com/mtolly/onyx/blob/20261016/haskell/packages/onyx-exe-toolkit/CLI.hs)
- [CommandLine.hs](https://github.com/mtolly/onyx/blob/20261016/haskell/packages/onyx-lib/src/Onyx/CommandLine.hs)
- [Resources.hs](https://github.com/mtolly/onyx/blob/20261016/haskell/packages/onyx-lib/src/Onyx/Resources.hs)

The real Carolina IV source (`5f520f0378be4d45a7511d5e0e67fa4d`) imported
successfully on Linux even when named `.zip` like the Windows cache. It is a raw
STFS CON package, not a ZIP, but that filename alone does not explain the failure.
Onyx locates resources relative to its executable; changing working directory
without diagnostic evidence is unnecessary. No tool upgrade or replacement of
verified hashes is needed.

The old converter redirected stdout/stderr into its temporary project directory,
then deleted that directory on failure. The pasted message therefore omitted the
actual converter diagnostic. Unsupported Windows runtime options are a confirmed
invocation defect; the original native stderr was not preserved, so a successful
Windows retry remains necessary to confirm that no additional blocker exists.

## Correction and recovery

- Windows receives no RTS arguments; Linux retains its two-capability limit.
- Every PC conversion gets a unique log under `Logs/Onyx`, outside the temporary
  project. Errors include the import/export stage, exit code or timeout, log path
  and up to 4 KiB of the final output. Successful logs remain available too.
- `onyx_recovery.py`, its helper hash in `collection_index.json`, and the index
  hash in `recover_pilot.py` change together. Song recipes 02–12 and the pilot,
  source/tool hashes, receipts and output checks remain unchanged.
- The three-file PowerShell update in song-library/CONTINUACAO.md resumes every
  batch, checking existing originals and outputs before using them. A download
  timeout is retried on resume. Nothing asks the user to delete their collection.

## Verification

Regression tests exercise both platform command paths and import/export/timeout
diagnostics that survive temporary-project cleanup. Existing recovery, resume,
MIDI verification and local-edit preservation tests remain required.

Real conversion smoke checks use three sources named in the user's errors:
Angra — Carolina IV, Avenged Sevenfold — Brompton Cocktail, and Gojira — All the
Tears. They run outside the checkout with isolated Python and no external Python
libraries, using the pinned Linux executable explicitly. Source SHA256, converted
MIDI against the immutable recipe, local asset hashes, persistent logs and repeat
run preservation are checked. This is Linux evidence, not native Windows execution
or Clone Hero gameplay acceptance. No media or executable enters Git.

Results: all 70 offline tests passed, including the five new regressions. All
three real conversions passed source/MIDI and local-resume checks (17 assets);
three success logs survived. Ruff, strict mypy, locked dependency check, CLI
help/doctor and distribution build passed. Doctor's optional ML warnings remain
expected. The full pinned index, three helpers, eleven batch recipes and original
pilot validate; none of the published song recipes changed. Windows remains a
user-side confirmation, not a claimed execution result.
