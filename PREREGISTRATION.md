# Pre-registered rubrics

Starting with the September 2026 cycle, the rubric for each cycle is
**pre-registered**: published and committed in this repository *before* any
tool is assessed under it. This is the direct answer to the fair criticism
that earlier rubric drafts (v1, v2.0) were revised before public release —
a scoring function tuned after seeing the results cannot be audited, no
matter how reproducible the final arithmetic is. Pre-registration commits
the measurement before anyone knows who wins under it.

## How it works

1. Before a cycle's assessment begins, the exact rubric — every dimension,
   weight, criterion, and capability check — is committed to `rubrics/`
   and its SHA-256 recorded here. The git commit provides a public
   timestamp; GitHub's commit history makes it independently checkable.
2. Assessment for that cycle is scored **only** against the pre-registered
   rubric. The published cycle's `criteria.json` must be byte-identical to
   the pre-registered file (verifiable by hash).
3. Rubric changes are allowed only **between** cycles, must be
   pre-registered for the next cycle before it is scored, and must be
   explained in [CHANGES.md](CHANGES.md).

## Registered rubrics

| Cycle | File | SHA-256 | Registered |
|-------|------|---------|------------|
| September 2026 | [`rubrics/september-2026-criteria.json`](rubrics/september-2026-criteria.json) | `f1b96c1172a5eed8c4b07027de7efa2e7780e1b6255fa835eb61d740e8b9edfb` | 2026-08-26 |

The August 2026 cycle (rubric v2.1.0 → corrected to v2.2.0) predates this
policy and was **not** pre-registered; its revisions are disclosed in
[CHANGES.md](CHANGES.md). Treat pre-registration guarantees as applying
from September 2026 onward.

## What this does and does not fix

Pre-registration prevents silently tuning the rubric to a desired outcome
within a cycle. It does **not** make the 0/1/2 check values objective —
those remain editorial judgments (see the README's
"What verification does — and does not — prove"). The roadmap toward
hands-on, task-based testing with published raw runs is tracked in the
README's "Toward hands-on testing" section.
