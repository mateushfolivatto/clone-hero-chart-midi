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

Use Python, uv, small modules and isolated audio/ML/export boundaries. Never
download models implicitly, commit private audio, copy unreviewed upstream code,
or equate wrapper and checkpoint licenses. CPU operation is required.

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
If a phase is incomplete or gates fail, keep the work on its branch and report
its actual status instead of declaring completion. This workflow is already
authorized by the user; do not ask again for routine branch/commit/local merge.
