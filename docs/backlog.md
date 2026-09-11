# Backlog navigation and Phase 0 report

[../BACKLOG.md](../BACKLOG.md) is the sole task-status authority. Read
[../lessons.md](../lessons.md) every time you consult it. This document is a
session evidence summary, not a duplicate checklist.

## 2026-09-10 — Phase 0

Research and bootstrap delivered for DCF-001 through DCF-042. DCF-001 adapts the
suggested new repository to the user's existing clone-hero-chart-midi checkout:
preserve history, main and origin; distribution name is drum-chart-forge. No remote
rename or visibility change was performed. origin/HEAD targets main;
server-side settings remain unaudited.

Evidence: CLI help/doctor, eight passing pytest tests, Ruff lint/format, strict
mypy, lock validation, wheel/sdist build and archive/audio hygiene inspection.
See [testing.md](testing.md) for commands and [phase-0-verification.md](phase-0-verification.md)
for results. The application remains a diagnostic skeleton; Phase 1 is not started.

Known follow-up risks: ADTOF code/weight permission, exact MDX checkpoint byte sizes
and immutable revisions, backend Windows/Python wheels, absent ffmpeg/PyTorch,
and no WSL Ubuntu. Research tasks document these uncertainties rather than
asserting that the optional backends are installed or licensed for redistribution.

## Git closure instruction

After the initial uncommitted delivery, the user required branches before changes
and a commit followed by a merge into main for every completed phase. Phase 0
closure uses chore/phase-0-bootstrap, including this standing instruction. Consult
Git history for the resulting commit and merge; no remote push is part of this closure.

## Windows-primary follow-up

Phase 0 environment/doctor update revalidates DCF-013 through DCF-019 and
DCF-037 through DCF-042 on native Windows/Python 3.12 CPU. See environment.md and
phase-0-verification.md. DCF-100 onward remains unstarted: only a compatibility
audit is authorized next, before implementation.

The pre-Phase 1 compatibility audit was completed on 2026-09-11 without changing
DCF-100–122 status. See [phase-1-windows-compatibility.md](phase-1-windows-compatibility.md).
The next implementation session should start only after explicit user direction.
