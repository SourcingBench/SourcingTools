# SourcingBench: AI Sourcing Tool Rankings & Public Audit Record

**The best AI sourcing tools, ranked on a published capability rubric.** SourcingBench scores AI recruiting tools on what an AI recruiting tool should do: match and screen candidates accurately, engage them effectively, automate the recruiting workflow, cover the talent pool, and fit the surrounding stack. Every criterion definition, every per-tool check value with its evidence note, and the scoring code itself are published in this repository, so anyone can replay the published calculations and inspect the basis for every number.

SourcingBench is published and maintained by [SourcingTools.org](https://sourcingtools.org), a directory of candidate sourcing tools that may earn referral fees when readers request vendor demos through it. Referral relationships do not set scores — every check value is published with its evidence — but readers should weigh that relationship as they would for any publisher. The live leaderboard with per-dimension breakdowns is at [sourcingtools.org/benchmark](https://sourcingtools.org/benchmark/), with a standalone copy at [sourcingbench.github.io/SourcingTools](https://sourcingbench.github.io/SourcingTools/).

<!-- RANKINGS:START -->
## 🏆 Best AI sourcing tools: August 2026

| # | Tool | Score / 100 | Matching | Automation | Engagement | Coverage | Integrations |
|--:|------|:-----------:|:--------:|:----------:|:----------:|:--------:|:------------:|
| 1 | [Noon](https://sourcingtools.org/tools/noon/) | 74.95 | 82.4 | 68.8 | 85.7 | 61.1 | 75.0 |
| 2 | [hireEZ](https://sourcingtools.org/tools/hireez/) | 73.20 | 73.5 | 65.6 | 76.2 | 66.7 | 87.5 |
| 3 | [SeekOut](https://sourcingtools.org/tools/seekout/) | 69.22 | 76.5 | 56.3 | 66.7 | 66.7 | 81.3 |
| 4 | [Gem](https://sourcingtools.org/tools/gem/) | 67.84 | 64.7 | 56.3 | 76.2 | 55.6 | 93.8 |
| 5 | [Findem](https://sourcingtools.org/tools/findem/) | 67.32 | 85.3 | 50.0 | 52.4 | 66.7 | 81.3 |
| 6 | [Fetcher](https://sourcingtools.org/tools/fetcher/) | 62.67 | 61.8 | 75.0 | 64.3 | 50.0 | 62.5 |
| 7 | [Juicebox (PeopleGPT)](https://sourcingtools.org/tools/juicebox/) | 58.68 | 67.6 | 46.9 | 59.5 | 55.6 | 62.5 |
| 8 | [Dover](https://sourcingtools.org/tools/dover/) | 56.68 | 52.9 | 68.8 | 57.1 | 44.4 | 62.5 |
| 9 | [LinkedIn Recruiter](https://sourcingtools.org/tools/linkedin-recruiter/) | 56.06 | 64.7 | 34.4 | 35.7 | 77.8 | 68.8 |
| 10 | [HeroHunt (Uwi)](https://sourcingtools.org/tools/herohunt/) | 54.44 | 55.9 | 75.0 | 54.8 | 44.4 | 37.5 |

_The composite (out of 100) weights Candidate matching & screening (25%), Workflow automation (20%), Outreach & engagement (20%), Talent pool coverage & data (20%), and Integrations & reporting (15%). Each of the 17 criteria decomposes into published capability checks (71 in total) scored 0 (absent), 1 (partial), or 2 (fully supported); every criterion carries an evidence note and links to the underlying review. Noon edges out hireEZ this cycle on matching calibration and outreach engagement; LinkedIn Recruiter tops talent pool coverage with the largest member-maintained pool, Findem tops matching depth, Gem tops integrations & reporting, and Fetcher and HeroHunt lead the field on workflow automation. Raw data: [criteria.json](data/cycles/August%202026/criteria.json) · [capabilities.json](data/cycles/August%202026/capabilities.json) · [leaderboard.json](data/cycles/August%202026/leaderboard.json). Full breakdowns at [sourcingtools.org/benchmark](https://sourcingtools.org/benchmark/)._
<!-- RANKINGS:END -->

### [See the full leaderboard at sourcingtools.org/benchmark →](https://sourcingtools.org/benchmark/)

Per-dimension breakdowns, the complete 17-criterion rubric, per-tool evidence notes, and cycle history.

This repository is the **public audit record**: the leaderboard on the live site is rendered from the data here, and anyone can clone this repo and replay every published cycle's arithmetic from the raw check values.

## What's in here

```
data/
  cycles/
    <cycle>/                # one directory per published cycle
      criteria.json         # the rubric: dimensions, weights, criterion definitions
      capabilities.json     # every tool's 0/1/2 score per capability check, with evidence notes
      scoring.mjs           # the frozen scoring aggregator for this cycle
      leaderboard.json      # composite + per-dimension scores, ranked
      cycle.json            # SHA-256 manifest of the files above
  tools/
    <slug>.json             # per-tool score history across all cycles
scripts/
  verify-cycle.mjs          # the audit script (see below)
CHANGES.md                  # cycle-to-cycle methodology changelog
```

## How to verify a cycle

```bash
git clone https://github.com/SourcingBench/SourcingTools.git
cd SourcingTools
npm run verify                                      # verify every published cycle
node scripts/verify-cycle.mjs "August 2026"         # verify one cycle
```

A successful verification looks like:

```
[ok] August 2026: 10 tools x 17 criteria (71 checks) verified, scores replayed
verify-cycle OK
```

The script runs three checks for each cycle:

1. **Manifest integrity.** Recomputes the SHA-256 of every file named in `cycle.json` and asserts it matches. Catches truncated, corrupted, or doctored publishes.
2. **Rubric coverage.** Every tool has an in-range 0/1/2 value for every published capability check and an evidence note for every criterion, and the dimension weights sum to 1.
3. **Score replay.** Re-runs the cycle's frozen `scoring.mjs` against `capabilities.json` and asserts every composite, dimension score, and rank matches the published `leaderboard.json` exactly.

The verifier is wired into CI: every push runs `npm run verify` and fails the build if any published cycle no longer replays.

## What verification does — and does not — prove

The verifier proves the **publication is internally honest**: the files haven't been altered since publish, every check value is in range and carries evidence, and every published composite really is the weighted arithmetic of the raw check values. It does **not** prove the check values themselves are correct — those are editorial judgments made by the SourcingTools.org editorial team from vendor documentation, product walkthroughs, and maintained tool reviews, not the output of blind hands-on trials. That is why every criterion's evidence note is published alongside its score: the judgments are open to inspection and dispute (see [Corrections and disputes](#corrections-and-disputes)), but they are judgments. Treat SourcingBench as a transparent, checkable editorial assessment — not as independent third-party test results.

## Methodology in one paragraph

Each cycle, every tool is assessed against the same 71 published capability checks, grouped into 17 criteria across five dimensions weighted by what an AI recruiting tool should do (matching & screening 25%, workflow automation 20%, outreach & engagement 20%, coverage & data 20%, integrations & reporting 15%). Each check is scored 0 (absent), 1 (partial or assisted), or 2 (fully supported) from vendor documentation, product walkthroughs, and the tool reviews maintained at SourcingTools.org; every check value and each criterion's evidence note are published in `capabilities.json`, so the basis for every number is inspectable. This is a capability rubric, not a blind task benchmark: the check values are editorial judgments about what each tool demonstrably does, and the published code verifies the arithmetic and data integrity, not the judgments themselves. The full methodology is on the [benchmark page](https://sourcingtools.org/benchmark/).

## Corrections and disputes

Vendors and users: if a score misrepresents a shipped capability, open an issue in this repo citing the documentation for the capability, or use the contact path at [sourcingtools.org/contact](https://sourcingtools.org/contact/). Corrections are applied in the next cycle and noted in `CHANGES.md`.

## License

- Verifier code, workflows, and configuration: [MIT](LICENSE).
- Cycle data under `data/`: [CC BY 4.0](LICENSE-data). Reproduction with attribution ("Source: SourcingBench by SourcingTools.org") is welcome.
