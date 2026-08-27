# SourcingBench cycle changelog

Each entry records methodology, rubric, or scoring changes between cycles.

---

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
