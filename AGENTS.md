# Execution rules

At the start of every session, and after context loss, read **all** of
CODEX_KICKOFF.md, CONTEXT.md, BACKLOG.md and lessons.md before acting.
Whenever rereading or updating the backlog, reread lessons.md too. Record new
evidence-backed lessons (observation, prevention, verification), avoiding duplicates.

BACKLOG.md is the sole task-status authority; docs/backlog.md is a navigation and
session summary, never a second checklist. CONTEXT.md owns project decisions.
Audit repository status and runtime before edits. Do only the current phase;
verify its acceptance criteria before moving on. A session may end with explicitly
blocked items, but must not claim that the phase is complete.

For every music-to-chart task, read and apply the project-local skill
`.agents/skills/drum-audio-diagnostics/SKILL.md`, as requested by the user.
Use its audio evidence, raw-MIDI comparison and per-class measurement workflow
throughout chart creation, not only after a hi-hat problem. Preserve the full-mix
baseline and distinguish spectral candidates, transcribed notes and game acceptance.

Use Python, uv, small modules and isolated audio/ML/export boundaries. Never
download models implicitly, commit private audio, copy unreviewed upstream code,
or equate wrapper and checkpoint licenses. CPU operation is required.

Native Windows/Python 3.12 is primary for this stage: development, tests and future
chart generation. Linux/WSL is optional future portability, never a prerequisite.
Do not install WSL, use docker-desktop, introduce Docker workarounds or modify
administrative policies. CUDA is optional acceleration; absence is not an error.

Run the configured quality gates in docs/testing.md, inspect generated artifacts,
update status and lessons, and provide a complete next-session prompt.
Do not claim game compatibility until the user has actually scanned/played a chart.

## Mandatory Git workflow (user instruction)

Before creating or modifying project files, create and switch to a dedicated
task/phase branch from main. Continue on that branch for the same unit of work;
never implement changes directly on main. Inspect and preserve existing changes.
After completing and verifying the work, update documentation, review the exact
staged diff, commit on the branch, then merge into main. Every completed phase
must have a commit and a merge into main before the final report.
Use a non-fast-forward merge to keep the branch boundary visible in history.
Verify the merge, current branch and working-tree status, and report commit hashes.
After a successful local merge, push `main` to `origin` and verify synchronization.
If authentication or the remote blocks the push, preserve the local commits and
report the exact blocker; never discard or rewrite verified work to work around it.
If a phase is incomplete or gates fail, keep the work on its branch and report
its actual status instead of declaring completion. This workflow is already
authorized by the user; do not ask again for routine branch/commit/local merge.
