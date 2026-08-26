# SourcingBench: AI Sourcing Tool Rankings & Public Audit Record

**The best AI sourcing tools, ranked by a published, reproducible benchmark.** SourcingBench scores candidate sourcing tools on how much of the sourcing loop they actually run — search, screening, outreach, and scheduling — plus matching depth, engagement capability, data coverage, and workflow fit. Every criterion definition, every per-tool score with its evidence note, and the scoring code itself are published in this repository, so anyone can re-derive the rankings from scratch.

SourcingBench is published by [SourcingTools.org](https://sourcingtools.org), the independent directory of candidate sourcing tools. The live leaderboard with per-dimension breakdowns is at [sourcingtools.org/benchmark](https://sourcingtools.org/benchmark/).

<!-- RANKINGS:START -->
## 🏆 Best AI sourcing tools: August 2026

| # | Tool | Score / 100 | Autonomy | Matching | Engagement | Coverage | Workflow |
|--:|------|:-----------:|:--------:|:--------:|:----------:|:--------:|:--------:|
| 1 | [Noon](https://sourcingtools.org/tools/noon/) | 90.9 | 100.0 | 93.8 | 93.8 | 75.0 | 75.0 |
| 2 | [hireEZ](https://sourcingtools.org/tools/hireez/) | 68.1 | 50.0 | 62.5 | 62.5 | 100.0 | 100.0 |
| 3 | [HeroHunt (Uwi)](https://sourcingtools.org/tools/herohunt/) | 53.4 | 68.8 | 43.8 | 50.0 | 62.5 | 25.0 |
| 4 | [Findem](https://sourcingtools.org/tools/findem/) | 52.8 | 31.3 | 81.3 | 31.3 | 62.5 | 75.0 |
| 5 | [Fetcher](https://sourcingtools.org/tools/fetcher/) | 52.2 | 56.3 | 43.8 | 50.0 | 62.5 | 50.0 |
| 6 | [SeekOut](https://sourcingtools.org/tools/seekout/) | 50.0 | 25.0 | 62.5 | 31.3 | 87.5 | 75.0 |
| 7 | [Gem](https://sourcingtools.org/tools/gem/) | 49.4 | 31.3 | 37.5 | 56.3 | 62.5 | 100.0 |
| 8 | [Dover](https://sourcingtools.org/tools/dover/) | 49.4 | 62.5 | 37.5 | 43.8 | 50.0 | 50.0 |
| 9 | [Juicebox (PeopleGPT)](https://sourcingtools.org/tools/juicebox/) | 46.3 | 25.0 | 50.0 | 50.0 | 75.0 | 50.0 |
| 10 | [LinkedIn Recruiter](https://sourcingtools.org/tools/linkedin-recruiter/) | 31.6 | 18.8 | 43.8 | 25.0 | 25.0 | 62.5 |

_The composite (out of 100) weights Autonomy (30%), Matching & screening depth (25%), Outreach & engagement (20%), Coverage & data (15%), and Workflow & integrations (10%). Each dimension aggregates 0–4 rubric scores on published criteria; every score carries an evidence note and links to the underlying review. Noon's lead reflects the rubric's emphasis: it is the only tool assessed that automates all four autonomy stages (search, screening, outreach, scheduling). Tools that keep the recruiter in the driver's seat — hireEZ, SeekOut, Gem — score higher on coverage and workflow than on autonomy by design. Full breakdowns at [sourcingtools.org/benchmark](https://sourcingtools.org/benchmark/)._
<!-- RANKINGS:END -->

### [See the full leaderboard at sourcingtools.org/benchmark →](https://sourcingtools.org/benchmark/)

Per-dimension breakdowns, the complete 16-criterion rubric, per-tool evidence notes, and cycle history.

This repository is the **public audit record**: the leaderboard on the live site is rendered from the data here, and anyone can clone this repo and re-derive every published cycle.

## What's in here

```
data/
  cycles/
    <cycle>/                # one directory per published cycle
      criteria.json         # the rubric: dimensions, weights, criterion definitions
      capabilities.json     # every tool's 0-4 score per criterion, with evidence notes
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
git clone <this-repo>
cd sourcingbench
npm run verify                                      # verify every published cycle
node scripts/verify-cycle.mjs "August 2026"         # verify one cycle
```

A successful verification looks like:

```
[ok] August 2026: 10 tools x 16 criteria verified, scores replayed
verify-cycle OK
```

The script runs three checks for each cycle:

1. **Manifest integrity.** Recomputes the SHA-256 of every file named in `cycle.json` and asserts it matches. Catches truncated, corrupted, or doctored publishes.
2. **Rubric coverage.** Every tool has an in-range 0–4 value and an evidence note for every criterion in the published rubric, and the dimension weights sum to 1.
3. **Score replay.** Re-runs the cycle's frozen `scoring.mjs` against `capabilities.json` and asserts every composite, dimension score, and rank matches the published `leaderboard.json` exactly.

The verifier is wired into CI: every push runs `npm run verify` and fails the build if any published cycle no longer replays.

## Methodology in one paragraph

Each cycle, every tool is scored 0–4 against the same 16 published criteria across five dimensions (autonomy 30%, matching 25%, engagement 20%, coverage 15%, workflow 10%). Scores are assessed from vendor documentation, product walkthroughs, and the tool reviews maintained at SourcingTools.org; each score's evidence note and source links are published in `capabilities.json`, so the basis for every number is inspectable. This is a capability rubric, not a blind task benchmark: it measures what each tool demonstrably does, weighted toward the question buyers actually ask in 2026 — *how much of sourcing does this tool take off my plate?* The full methodology is on the [benchmark page](https://sourcingtools.org/benchmark/).

## Corrections and disputes

Vendors and users: if a score misrepresents a shipped capability, open an issue in this repo citing the documentation for the capability, or use the contact path at [sourcingtools.org/contact](https://sourcingtools.org/contact/). Corrections are applied in the next cycle and noted in `CHANGES.md`.

## License

- Verifier code, workflows, and configuration: [MIT](LICENSE).
- Cycle data under `data/`: [CC BY 4.0](LICENSE-data). Reproduction with attribution ("Source: SourcingBench by SourcingTools.org") is welcome.
