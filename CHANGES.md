# SourcingBench cycle changelog

Each entry records methodology, rubric, or scoring changes between cycles.

---

## Evidence layer and governance II (2026-08-26)

No score changes; every composite, dimension score, and rank is identical.
The evidence and process layer was hardened:

- **Structured evidence citations**: every criterion score in
  `capabilities.json` now carries structured evidence records — source URL,
  source type from a fixed quality enum (`hands_on > api_docs >
  product_docs > changelog > vendor_claim > third_party_review >
  inference`), access date, and the claim relied on — replacing
  prose-only notes. Only URLs verified to resolve are cited; bot-blocked
  pages (e.g. G2) are deliberately not cited.
- **Verifier enforcement** (`scripts/verify-cycle.mjs`): evidence is now
  machine-checked — URL validity, enum membership, date format, access
  date within the cycle window, a ban on publisher-owned pages
  (sourcingtools.org, sourcingbench.github.io) as evidence, and a cap:
  a criterion whose best source is `vendor_claim` or `inference` cannot
  award any check a 2.
- **Self-referential evidence removed**: one Noon note read "above
  category average in our review" — the publisher's own opinion page as
  evidence for the publisher's own score. Rewritten to describe documented
  product behavior; the ban above makes recurrence a CI failure. Logged in
  [CORRECTIONS.md](CORRECTIONS.md).
- **CI link checking** (`scripts/check-links.mjs`, `npm run check-links`):
  a CI job fetches every evidence URL and fails on dead links.
- **Scoring code pre-registered**: `rubrics/september-2026-scoring.mjs` is
  now hashed in [PREREGISTRATION.md](PREREGISTRATION.md) alongside the
  rubric, so the aggregation code is also fixed before scoring.
- **Governance policy** ([GOVERNANCE.md](GOVERNANCE.md)): separation of
  rubric author and scorer, independent second scorer with published
  disagreements, blind scoring where feasible, conflict-of-interest
  statement requirements for named contributors, and flat non-rank-based
  referral fees — no pay-to-play, no rank-contingent payments.
- **Public corrections log** ([CORRECTIONS.md](CORRECTIONS.md)): what was
  wrong, who caught it, what changed — seeded with the two errors caught
  by external review to date.
- **"How to evaluate a benchmark" page** on the site: the standing
  checklist (falsifiability, dated citations, named authors, multiple
  cycles, whether the money moves with the rank) applied to SourcingBench
  itself, including the checks it currently fails (no named maintainers
  yet, single-cycle history).

## Governance additions (2026-08-26)

No score changes. In response to public criticism that the project audits
only its own arithmetic, four governance mechanisms were added:

- **Pre-registration** ([PREREGISTRATION.md](PREREGISTRATION.md)): from
  September 2026, each cycle's rubric is committed and SHA-256-hashed
  before assessment begins. The September 2026 rubric (identical to
  v2.2.0) is registered in `rubrics/`. The August 2026 cycle and the
  privately revised v1/v2.0 drafts predate this policy.
- **Vendor right of reply** (`data/replies/`): pre-publication scorecards
  to every vendor, rebuttals published verbatim, no veto. Applies from
  September 2026.
- **Per-vendor referral disclosure** (`data/disclosures.json`): whether
  each vendor pays the publisher referral fees is now a visible column in
  the leaderboard table, not just a footer sentence. Kept outside the
  hashed cycle files because it is disclosure metadata, not a scoring
  input.
- **Hands-on protocol pre-registered** ([HANDS-ON.md](HANDS-ON.md)): the
  task-based testing design (real specs, preserved candidate lists, blind
  judging, precision@25, time to first qualified shortlist, outreach
  response rate, raw runs published) is committed now, before any hands-on
  cycle exists. No hands-on claims are made until raw runs are published.

## August 2026 — revision 2.2.0 (2026-08-26)

Correction to the coverage dimension, in response to public feedback that
"talent pool coverage & data" mixed contact enrichment into pool coverage
and consequently understated single-network pools.

- `rubric_version`: 2.2.0 — the coverage dimension now measures the pool
  itself: **Talent pool size & quality** (scale, freshness, completeness,
  activity signals, geographic/industry reach, identity resolution, niche
  coverage) and **Discovery reach** (multi-source aggregation, ATS
  rediscovery). **Contact finding** moved to Outreach & engagement, where
  it belongs — contact data determines whether outreach is possible, not
  how large the pool is. Now 17 criteria, 71 checks.
- Effect: LinkedIn Recruiter — the largest, freshest, member-maintained
  pool — now leads coverage (77.8) and rises to #9 overall; Noon's
  coverage drops to 61.1 (younger data asset) and its composite to 74.95,
  still #1 on matching and engagement strength. hireEZ remains #2.
- LinkedIn Recruiter's company-context check in Trajectory & context
  inference raised 1 → 2 (first-party employment data).

## August 2026 (published 2026-08-26)

First published cycle.

- `rubric_version`: 2.1.0 — 16 criteria across five dimensions weighted by
  what an AI recruiting tool should do (candidate matching & screening 25%,
  workflow automation 20%, outreach & engagement 20%, talent pool coverage
  & data 20%, integrations & reporting 15%). Each criterion decomposes into
  published capability checks (67 in total) scored 0 (absent), 1 (partial),
  or 2 (fully supported); criterion and dimension scores are derived from
  check points.
- Earlier rubric drafts (v1: 0–4 criterion scale, autonomy-weighted;
  v2.0: 0–10 criterion scale) were replaced before wide publication;
  v2.1 replaces holistic criterion scores with itemized capability checks
  so every published number traces to concrete product behavior.
- 10 tools assessed: Noon, hireEZ, SeekOut, Juicebox, Gem, Findem,
  Fetcher, HeroHunt, Dover, LinkedIn Recruiter.

📦 [Cycle data](data/cycles/August%202026/)
