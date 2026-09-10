# Contributing

Read AGENTS.md, CODEX_KICKOFF.md, CONTEXT.md, BACKLOG.md and lessons.md first.
Keep changes within the current phase and record evidence against task IDs.
Use the setup in README.md and all gates in docs/testing.md.

Create and switch to a task/phase branch from main before creating or editing
project files. After verification, commit on that branch and merge into main
with `git merge --no-ff`. Every completed phase must be committed and merged.
Review staged changes, preserve unrelated user work, and verify the final Git
status. Continue incomplete work on its branch until its acceptance gates pass.

Use conventional commit subjects when committing. Never commit music, generated
audio, model weights, environments or caches. Synthetic future fixtures need
documented provenance; copyrighted input stays in audio/ or fixtures/private/.

Review code and weight licenses separately before adding a dependency. Lock all
selected dependencies with uv. Prefer immutable upstream commit references.
Keep the standard-library CLI independent of optional ML imports. Preserve raw
onset times in later implementations and avoid unnecessary infrastructure.
