# Governance

How SourcingBench separates the people, incentives, and process behind the
scores. Companion documents: [PREREGISTRATION.md](PREREGISTRATION.md)
(rubrics fixed before scoring), [HANDS-ON.md](HANDS-ON.md) (planned
task-based testing), [CORRECTIONS.md](CORRECTIONS.md) (public corrections
log), and [`data/replies/`](data/replies/) (vendor right of reply).

## Separation of duties: weights vs. values

The person who sets the rubric (dimensions, weights, criteria, checks) must
not be the only person who assigns the 0/1/2 check values under it.
From the September 2026 cycle onward:

1. **Rubric author** — writes and pre-registers the rubric before assessment
   begins, then does not assign values.
2. **Primary scorer** — assigns every check value with its evidence record.
3. **Second scorer** — independently re-scores a published sample of
   criteria (minimum: every tool's two highest-weight dimensions) from the
   same evidence packets, without seeing the primary scorer's values.
4. **Disagreements are published, not reconciled** — both values appear in
   the cycle data with the divergence flagged; the primary value stands in
   the leaderboard, and the disagreement rate is reported on the cycle page.

Current status: the August 2026 cycle was scored by a single scorer and is
labeled accordingly. Second-scorer records will appear under
`data/cycles/<cycle>/second-scorer.json` when the process is first run.

## Blind scoring

Where feasible, check values are assigned from evidence packets with vendor
names stripped: the scorer sees the quoted documentation language and the
capability check, not the brand. This is imperfect — sourcing products are
recognizable from their own docs — so blinding status is recorded per cycle
rather than claimed universally.

## Conflict of interest statements

Every named contributor must publish a conflict statement covering, at
minimum:

- current and prior employment at any listed vendor;
- advisory, board, or consulting relationships with any listed vendor;
- equity, options, or other financial interest in any listed vendor;
- referral, affiliate, or commercial relationships beyond those already
  disclosed in [`data/disclosures.json`](data/disclosures.json).

Template: `Name — Role. Employment: … Advisory: … Equity: … Commercial: …`
Statements live in `MAINTAINERS.md` once contributors are named. Until the
project has named maintainers, that absence is a disclosed limitation, not
a claim of neutrality: an unsigned benchmark should be discounted
accordingly.

## Commercial model: revenue must not move with rank

The publisher, SourcingTools.org, earns referral fees from some listed
vendors (disclosed per vendor in the leaderboard itself and in
[`data/disclosures.json`](data/disclosures.json)). Policy:

- **Flat fees only.** Any vendor referral fee must be a flat per-demo or
  flat listing amount, identical in structure across vendors that pay, and
  must not vary with leaderboard position, score, or movement.
- **No rank-contingent payments.** No payment, bonus, or contract term may
  depend on a vendor's rank, score, or inclusion.
- **No pay-to-play.** Vendors cannot pay to be added, removed, re-scored,
  or re-ranked. Non-paying vendors are listed and scored identically —
  the current cycle includes non-paying vendors both above and below
  paying ones.
- Changes to any vendor's commercial status are recorded by dated commits
  to `data/disclosures.json`.

## Changes to this document

Governance changes are made by commit to this file, take effect from the
next cycle, and are noted in [CHANGES.md](CHANGES.md).
