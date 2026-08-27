# Hands-on testing: pre-registered protocol

**Status: planned, not yet run.** No SourcingBench cycle to date includes
hands-on results. The current leaderboard is a capability rubric
(editorial 0/1/2 judgments with published evidence notes — see the README).
This document pre-registers the hands-on protocol so that when the first
hands-on cycle runs, it can be judged against a spec that predates its
results. Until raw run files exist under `data/runs/`, SourcingBench makes
no hands-on performance claims.

## Protocol

1. **Job specs.** Ten real job specifications (title, must-have
   qualifications, nice-to-haves, exclusions, location/remote policy,
   seniority), published in `data/runs/<cycle>/specs/` before any tool is
   run. Specs are drawn from real open roles with the hiring context
   anonymized.
2. **Runs.** Every spec is run through every tool by the same operator
   within the same window, using each tool as documented (no vendor
   hand-holding). Every run is preserved in
   `data/runs/<cycle>/<slug>/<spec-id>.json`: the exact query/inputs, the
   returned candidate list, and timestamps for every step. Candidate
   personal data is pseudonymized before publication; the pseudonym map is
   hashed into the manifest so lists are stable without exposing people.
3. **Judging.** Candidate relevance is labeled blind — judges see the spec
   and a pseudonymized profile, not which tool produced it. Labels and the
   judging instructions are published.
4. **Outreach.** Where a tool sends outreach, sequences run from
   disclosed, compliant test identities; sent / delivered / replied /
   qualified-reply events are logged per candidate.

## Metrics

- **Precision@25** — share of the top 25 returned candidates labeled
  relevant to the spec.
- **Time to first qualified shortlist** — elapsed time from spec entry to
  ten relevance-labeled candidates, from run timestamps.
- **Outreach response rate** — replies / delivered, and qualified replies /
  delivered, per tool across specs.

Scores are computed by a published script from the raw run files, exactly
as `scoring.mjs` computes the rubric today, and enter the leaderboard as a
separately labeled **observed-performance** layer — never blended silently
into the capability scores.

## What it costs, honestly

This protocol needs paid seats at all ten vendors, weeks of live roles,
and qualified human judging. Those don't exist yet for this project.
If a hands-on cycle produces a ranking different from the capability
rubric's — including a different #1 — the observed result is what gets
published.
