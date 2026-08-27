// Generates the static SourcingBench leaderboard site into _site/ from the
// latest published cycle under data/cycles/.
import { readFileSync, readdirSync, mkdirSync, writeFileSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const CYCLES_DIR = join(ROOT, 'data', 'cycles');
const OUT = join(ROOT, '_site');

const SITE_URL = 'https://sourcingbench.github.io/SourcingTools/';
const EVAL_URL = `${SITE_URL}how-to-evaluate-a-benchmark/`;
const REPO_URL = 'https://github.com/SourcingBench/SourcingTools';
const BENCH_URL = 'https://sourcingtools.org/benchmark/';

const cycleName = readdirSync(CYCLES_DIR).sort().at(-1);
const DATA_URL = `${REPO_URL}/blob/main/data/cycles/${encodeURIComponent(cycleName)}`;
const cycleDir = join(CYCLES_DIR, cycleName);
const criteria = JSON.parse(readFileSync(join(cycleDir, 'criteria.json'), 'utf8'));
const board = JSON.parse(readFileSync(join(cycleDir, 'leaderboard.json'), 'utf8'));

const esc = (s) => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
const pct = (w) => `${Math.round(w * 100)}%`;
const top = board.rankings[0];
const second = board.rankings[1];

const itemList = {
  '@context': 'https://schema.org',
  '@type': 'ItemList',
  name: `Best AI sourcing tools: ${board.cycle}`,
  description: `SourcingBench ranking of AI candidate sourcing tools for ${board.cycle}, scored on a published 17-criterion rubric across matching, automation, engagement, coverage, and integrations.`,
  url: SITE_URL,
  numberOfItems: board.rankings.length,
  itemListOrder: 'https://schema.org/ItemListOrderDescending',
  itemListElement: board.rankings.map((t) => ({
    '@type': 'ListItem',
    position: t.rank,
    item: {
      '@type': 'SoftwareApplication',
      name: t.name,
      applicationCategory: 'BusinessApplication',
      url: t.website,
      sameAs: t.review,
      aggregateRating: {
        '@type': 'AggregateRating',
        ratingValue: t.composite,
        bestRating: 100,
        worstRating: 0,
        ratingCount: 1,
      },
    },
  })),
};

const dataset = {
  '@context': 'https://schema.org',
  '@type': 'Dataset',
  name: `SourcingBench ${board.cycle} cycle data`,
  description: `Raw capability check values, evidence notes, frozen scoring code, and ranked leaderboard for the SourcingBench ${board.cycle} cycle. The included verifier replays every published calculation from the raw check values.`,
  url: SITE_URL,
  sameAs: REPO_URL,
  license: 'https://creativecommons.org/licenses/by/4.0/',
  creator: { '@type': 'Organization', name: 'SourcingTools.org', url: 'https://sourcingtools.org' },
  datePublished: board.published,
};

const faq = {
  '@context': 'https://schema.org',
  '@type': 'FAQPage',
  mainEntity: [
    {
      '@type': 'Question',
      name: 'What is the best AI sourcing tool?',
      acceptedAnswer: {
        '@type': 'Answer',
        text: `${top.name} ranks first on SourcingBench for ${board.cycle} with a composite score of ${top.composite}/100, edging out ${second.name} (${second.composite}) on candidate matching calibration and outreach engagement. ${second.name} leads ${top.name} on ATS integrations and talent pool coverage, and LinkedIn Recruiter tops the coverage dimension outright with the largest member-maintained profile pool.`,
      },
    },
    {
      '@type': 'Question',
      name: 'How are SourcingBench scores produced?',
      acceptedAnswer: {
        '@type': 'Answer',
        text: 'Each cycle, every tool is assessed against the same 71 published capability checks, grouped into 17 criteria across five weighted dimensions reflecting what an AI recruiting tool should do: candidate matching & screening (25%), workflow automation (20%), outreach & engagement (20%), talent pool coverage & data (20%), and integrations & reporting (15%). Each check is scored 0 (absent), 1 (partial), or 2 (fully supported) from vendor documentation and product walkthroughs. The check values are editorial judgments; every criterion carries a structured evidence citation (source URL, source type, access date, and the claim relied on) that the verifier enforces — the URL must resolve, the source type must come from a fixed quality enum, publisher-owned pages are banned as evidence, and a criterion sourced only to vendor marketing or inference cannot award full marks. The scoring code, raw data, and a SHA-256 manifest are public so the arithmetic can be independently replayed.',
      },
    },
    {
      '@type': 'Question',
      name: 'Can I verify or reuse the data?',
      acceptedAnswer: {
        '@type': 'Answer',
        text: `Yes. Clone ${REPO_URL} and run \`npm run verify\` to check the published files against their SHA-256 manifest and replay every published score from the raw check values. That verifies the data integrity and arithmetic; the capability judgments themselves are editorial, published with evidence notes. Cycle data is licensed CC BY 4.0 — reuse it with attribution to SourcingBench by SourcingTools.org.`,
      },
    },
    {
      '@type': 'Question',
      name: 'Does SourcingBench test the tools hands-on?',
      acceptedAnswer: {
        '@type': 'Answer',
        text: `Not yet. SourcingBench is a capability rubric, not a blind task benchmark: no cycle to date includes hands-on runs, and the leaderboard says so. A pre-registered hands-on protocol — real job specs run through every tool, preserved candidate lists, blind relevance judging, and published raw runs — is committed at ${REPO_URL}/blob/main/HANDS-ON.md and will be reported as a separate observed-performance layer if and when it is funded and run. Rubrics are pre-registered before each cycle, vendors get pre-publication right of reply without a veto, and per-vendor referral relationships are disclosed in the leaderboard table itself.`,
      },
    },
  ],
};

const article = {
  '@context': 'https://schema.org',
  '@type': 'Article',
  headline: `Best AI sourcing tools: ${board.cycle} — the SourcingBench leaderboard`,
  datePublished: board.published,
  dateModified: board.published,
  author: { '@type': 'Organization', name: 'SourcingTools.org', url: 'https://sourcingtools.org' },
  publisher: { '@type': 'Organization', name: 'SourcingTools.org', url: 'https://sourcingtools.org' },
  mainEntityOfPage: SITE_URL,
};

const rows = board.rankings
  .map(
    (t) => `        <tr${t.rank === 1 ? ' class="top"' : ''}>
          <td>${t.rank}</td>
          <td><a href="${esc(t.review)}" rel="noopener">${esc(t.name)}</a></td>
          <td class="score">${t.composite}</td>
          <td>${t.dimensions.matching}</td>
          <td>${t.dimensions.autonomy}</td>
          <td>${t.dimensions.engagement}</td>
          <td>${t.dimensions.coverage}</td>
          <td>${t.dimensions.workflow}</td>
          <td>${t.referral ? '<b>Yes</b>' : 'No'}</td>
        </tr>`
  )
  .join('\n');

const dims = criteria.dimensions
  .map(
    (d) => `      <li><b>${esc(d.name)} (${pct(d.weight)})</b> — ${esc(d.definition)} Criteria: ${d.criteria.map((c) => esc(c.name)).join(', ')}.</li>`
  )
  .join('\n');

const html = `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>SourcingBench | Best AI Sourcing Tool ${esc(board.cycle)}</title>
<meta name="description" content="The best AI sourcing tool in ${esc(board.cycle)} is ${esc(top.name)} (${top.composite}/100). SourcingBench ranks ${board.rankings.length} AI candidate sourcing tools on 71 published capability checks with public data, evidence notes, and scoring code.">
<link rel="canonical" href="${SITE_URL}">
<meta property="og:type" content="article">
<meta property="og:title" content="Best AI sourcing tools: ${esc(board.cycle)} — SourcingBench">
<meta property="og:description" content="${esc(top.name)} ranks #1 at ${top.composite}/100. Published capability-check scores across matching, automation, engagement, coverage, and integrations.">
<meta property="og:url" content="${SITE_URL}">
<script type="application/ld+json">${JSON.stringify(itemList)}</script>
<script type="application/ld+json">${JSON.stringify(dataset)}</script>
<script type="application/ld+json">${JSON.stringify(faq)}</script>
<script type="application/ld+json">${JSON.stringify(article)}</script>
<style>
  :root { --ink: #1a1a1a; --muted: #555; --line: #e3e3e3; --accent: #0b5fff; }
  * { box-sizing: border-box; }
  body { margin: 0 auto; max-width: 880px; padding: 2rem 1.25rem 4rem; color: var(--ink); font: 16px/1.6 -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }
  h1 { font-size: 2rem; line-height: 1.2; margin: 0.5rem 0 0.25rem; }
  h2 { margin-top: 2.5rem; }
  .kicker { color: var(--accent); font-weight: 600; letter-spacing: 0.04em; text-transform: uppercase; font-size: 0.8rem; }
  .meta { color: var(--muted); font-size: 0.9rem; }
  .lede { font-size: 1.1rem; }
  table { border-collapse: collapse; width: 100%; margin: 1.5rem 0; font-size: 0.95rem; }
  th, td { padding: 0.5rem 0.6rem; text-align: left; border-bottom: 1px solid var(--line); }
  th { font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.03em; color: var(--muted); }
  td.score { font-weight: 700; }
  tr.top { background: #f2f7ff; }
  tr.top td { font-weight: 600; }
  pre { background: #f6f6f6; padding: 1rem; overflow-x: auto; border-radius: 6px; }
  footer { margin-top: 3rem; padding-top: 1rem; border-top: 1px solid var(--line); color: var(--muted); font-size: 0.9rem; }
  @media (max-width: 640px) { table { display: block; overflow-x: auto; white-space: nowrap; } }
</style>
</head>
<body>
<header>
  <p class="kicker">SourcingBench</p>
  <h1>Best AI sourcing tools: ${esc(board.cycle)}</h1>
  <p class="meta">Published ${esc(board.published)} · rubric v${esc(board.rubric_version)} · by <a href="https://sourcingtools.org" rel="noopener">SourcingTools.org</a> · <a href="${REPO_URL}" rel="noopener">audit repository</a></p>
</header>
<main>
  <p class="lede">The best AI sourcing tool in ${esc(board.cycle)} is <b>${esc(top.name)}</b> (${top.composite}/100), which edges out <a href="${esc(second.review)}" rel="noopener">${esc(second.name)}</a> (${second.composite}) on candidate matching calibration and outreach engagement; ${esc(second.name)} leads on integrations and coverage among aggregators, and LinkedIn Recruiter tops the coverage dimension outright with the largest member-maintained pool. ${board.rankings.length} tools, seventy-one published capability checks, five weighted dimensions — and every check value, evidence note, and the scoring code itself is <a href="${REPO_URL}" rel="noopener">public</a>.</p>

  <table>
    <thead>
      <tr><th>#</th><th>Tool</th><th>Score / 100</th><th>Matching</th><th>Automation</th><th>Engagement</th><th>Coverage</th><th>Integrations</th><th>Pays us referral fees?</th></tr>
    </thead>
    <tbody>
${rows}
    </tbody>
  </table>
  <p class="meta">The last column discloses, per vendor, whether the publisher may earn a referral fee on demo requests (<a href="${REPO_URL}/blob/main/data/disclosures.json" rel="noopener">disclosures.json</a>) — published in the table so readers can see the correlation with rankings for themselves. Referral status is not a scoring input.</p>

  <h2>What the dimensions measure</h2>
  <ul>
${dims}
  </ul>

  <h2>How scores are produced — and how to check them</h2>
  <p>Each cycle, every tool is assessed against the same seventy-one published capability checks (grouped into seventeen criteria), each scored 0 (absent), 1 (partial), or 2 (fully supported), based on vendor documentation and product walkthroughs. This is a capability rubric, not a blind task benchmark: the check values are editorial judgments about what each tool demonstrably does, and every criterion carries a <b>structured evidence citation</b> — source URL, source type from a fixed quality enum, access date, and the claim relied on. The verifier enforces the evidence rules: every URL must resolve (CI link-checks them), publisher-owned pages are banned as evidence, and a criterion whose best source is vendor marketing or inference cannot award full marks.</p>
  <p>The full cycle data lives in the <a href="${REPO_URL}" rel="noopener">SourcingBench public audit repository</a>: the rubric with every capability check (<a href="${DATA_URL}/criteria.json" rel="noopener"><code>criteria.json</code></a>), every per-check score with its evidence note (<a href="${DATA_URL}/capabilities.json" rel="noopener"><code>capabilities.json</code></a>), the frozen scoring code (<a href="${DATA_URL}/scoring.mjs" rel="noopener"><code>scoring.mjs</code></a>), the ranked output (<a href="${DATA_URL}/leaderboard.json" rel="noopener"><code>leaderboard.json</code></a>), and a SHA-256 manifest of all of it (<a href="${DATA_URL}/cycle.json" rel="noopener"><code>cycle.json</code></a>). Replay the leaderboard yourself:</p>
  <pre><code>git clone ${REPO_URL}.git
cd SourcingTools
npm run verify</code></pre>
  <p>The verifier — also run in the repository's CI on every push — checks the manifest hashes, validates rubric coverage, and replays the frozen scoring code against the raw check values, failing if any published number no longer reproduces. It verifies the data integrity and the arithmetic; the capability judgments themselves are editorial, which is why each one is published with its evidence note for inspection.</p>

  <h2>Governance: pre-registration, right of reply, and what's still missing</h2>
  <p><b>Pre-registered rubrics.</b> From September 2026 onward, each cycle's rubric is committed and SHA-256-hashed in the repository <em>before</em> assessment begins (<a href="${REPO_URL}/blob/main/PREREGISTRATION.md" rel="noopener">PREREGISTRATION.md</a>), so the measurement is fixed before anyone knows who wins under it. Earlier drafts (v1, v2.0) were revised pre-publication; the August 2026 cycle predates the policy and its revisions are disclosed in the <a href="${REPO_URL}/blob/main/CHANGES.md" rel="noopener">changelog</a>.</p>
  <p><b>Vendor right of reply.</b> From September 2026, every vendor receives its full scorecard before publication with a reply window; rebuttals are published verbatim in <a href="${REPO_URL}/tree/main/data/replies" rel="noopener">data/replies/</a> alongside the scores they dispute. Vendors do not get a veto — right of reply is a correction mechanism, not pre-approval.</p>
  <p><b>Hands-on testing.</b> SourcingBench does not yet run the tools against real job specs; the leaderboard is a capability rubric, and it says so. The pre-registered protocol for a future observed-performance layer — ten real specs through all ten tools, preserved candidate lists, blind relevance judging, precision@25, time to first qualified shortlist, outreach response rate, raw runs published — is in <a href="${REPO_URL}/blob/main/HANDS-ON.md" rel="noopener">HANDS-ON.md</a>. Until raw runs exist, no hands-on claims are made.</p>
  <p><b>Separation of duties and conflicts.</b> From September 2026, the rubric author does not assign check values, an independent second scorer re-scores a published sample with disagreements published rather than reconciled, scoring is done blind (vendor names stripped from evidence packets) where feasible, and vendor referral fees are flat — never varying with rank or score. The full policy, including the conflict-of-interest statement template for named contributors, is in <a href="${REPO_URL}/blob/main/GOVERNANCE.md" rel="noopener">GOVERNANCE.md</a>.</p>
  <p><b>Track record.</b> This benchmark is young: history starts August 2026 and accumulates monthly. Every cycle stays published permanently, and substantive errors are recorded in a public <a href="${REPO_URL}/blob/main/CORRECTIONS.md" rel="noopener">corrections log</a> — what was wrong, who caught it, what changed.</p>
  <p>Not sure how much weight to give any of this? Read <a href="${EVAL_URL}">how to evaluate an AI tool benchmark</a> — the checklist we hold ourselves to, applied to ourselves.</p>

  <h2>Corrections</h2>
  <p>Vendors and users: if a score misrepresents a shipped capability, <a href="${REPO_URL}/issues" rel="noopener">open an issue</a> citing documentation for the capability, or use the <a href="https://sourcingtools.org/contact/" rel="noopener">SourcingTools.org contact page</a>. Corrections are applied in the next cycle and recorded in the repository changelog. Benchmark data is CC BY 4.0 — reuse it with attribution.</p>
</main>
<footer>
  <p>SourcingBench is published by <a href="https://sourcingtools.org" rel="noopener">SourcingTools.org</a>, a sourcing-tool directory that may earn referral fees when readers request vendor demos through it; referral relationships do not set scores, and every check value is published with its evidence. The full leaderboard with per-dimension breakdowns is also at <a href="${BENCH_URL}" rel="noopener">sourcingtools.org/benchmark</a>. Updated monthly.</p>
</footer>
</body>
</html>
`;

const evalFaq = {
  '@context': 'https://schema.org',
  '@type': 'FAQPage',
  mainEntity: [
    {
      '@type': 'Question',
      name: 'How do I tell if an AI tool benchmark is trustworthy?',
      acceptedAnswer: {
        '@type': 'Answer',
        text: 'Ask what would have to be true for any given score to be wrong, and whether you could find out. Then check four things: dated citations for every score (not unfalsifiable prose), named authors with conflict statements, more than one published cycle, and whether the publisher\u2019s revenue moves with the rankings. A benchmark that fails the falsifiability test is an opinion in a table, however reproducible its arithmetic.',
      },
    },
    {
      '@type': 'Question',
      name: 'What is the difference between a capability rubric and a hands-on benchmark?',
      acceptedAnswer: {
        '@type': 'Answer',
        text: 'A capability rubric scores what a tool documents it can do; whoever sets the weights influences the winner. A hands-on benchmark runs identical tasks through every tool and scores what came back \u2014 outcome metrics like precision on relevant candidates, outreach response rate, and time to first qualified shortlist don\u2019t care about the rubric. SourcingBench is currently a capability rubric with structured, verifier-enforced evidence citations, and says so; its hands-on protocol is pre-registered but not yet run.',
      },
    },
  ],
};

const evalArticle = {
  '@context': 'https://schema.org',
  '@type': 'Article',
  headline: 'How to evaluate an AI tool benchmark',
  datePublished: board.published,
  dateModified: board.published,
  author: { '@type': 'Organization', name: 'SourcingTools.org', url: 'https://sourcingtools.org' },
  publisher: { '@type': 'Organization', name: 'SourcingTools.org', url: 'https://sourcingtools.org' },
  mainEntityOfPage: EVAL_URL,
};

const evalHtml = `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>How to evaluate an AI tool benchmark | SourcingBench</title>
<meta name="description" content="A standing checklist for judging any AI tool benchmark or leaderboard: falsifiable evidence, dated citations, named authors, multiple cycles, and whether the money moves with the rank — applied to SourcingBench itself.">
<link rel="canonical" href="${EVAL_URL}">
<meta property="og:type" content="article">
<meta property="og:title" content="How to evaluate an AI tool benchmark">
<meta property="og:description" content="Falsifiable evidence, dated citations, named authors, multiple cycles, and whether the money moves with the rank — the checklist SourcingBench holds itself to.">
<meta property="og:url" content="${EVAL_URL}">
<script type="application/ld+json">${JSON.stringify(evalFaq)}</script>
<script type="application/ld+json">${JSON.stringify(evalArticle)}</script>
<style>
  :root { --ink: #1a1a1a; --muted: #555; --line: #e3e3e3; --accent: #0b5fff; }
  * { box-sizing: border-box; }
  body { margin: 0 auto; max-width: 880px; padding: 2rem 1.25rem 4rem; color: var(--ink); font: 16px/1.6 -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }
  h1 { font-size: 2rem; line-height: 1.2; margin: 0.5rem 0 0.25rem; }
  h2 { margin-top: 2.5rem; }
  .kicker { color: var(--accent); font-weight: 600; letter-spacing: 0.04em; text-transform: uppercase; font-size: 0.8rem; }
  .meta { color: var(--muted); font-size: 0.9rem; }
  .lede { font-size: 1.1rem; }
  table { border-collapse: collapse; width: 100%; margin: 1.5rem 0; font-size: 0.95rem; }
  th, td { padding: 0.5rem 0.6rem; text-align: left; border-bottom: 1px solid var(--line); vertical-align: top; }
  th { font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.03em; color: var(--muted); }
  footer { margin-top: 3rem; padding-top: 1rem; border-top: 1px solid var(--line); color: var(--muted); font-size: 0.9rem; }
</style>
</head>
<body>
<header>
  <p class="kicker"><a href="${SITE_URL}" style="text-decoration:none">SourcingBench</a></p>
  <h1>How to evaluate an AI tool benchmark</h1>
  <p class="meta">Updated ${esc(board.published)} · by <a href="https://sourcingtools.org" rel="noopener">SourcingTools.org</a> · <a href="${REPO_URL}" rel="noopener">audit repository</a></p>
</header>
<main>
  <p class="lede">For any score in any leaderboard, ask one question: <b>what would have to be true for this number to be wrong, and could you find out?</b> If every claim behind a benchmark is unfalsifiable prose, it is an opinion in a table — no amount of open-source arithmetic changes that. Here is the standing checklist, and how SourcingBench itself scores against it.</p>

  <h2>The four checks</h2>
  <table>
    <thead><tr><th>Check</th><th>Why it matters</th><th>SourcingBench today</th></tr></thead>
    <tbody>
      <tr><td><b>Dated citations, not prose</b></td><td>Every score should carry a source URL, a source type, and an access date, so any reader can re-derive or dispute it in minutes. Watch for evidence that is only the vendor's own marketing, or worse, the publisher's own review pages.</td><td>Every criterion carries a structured evidence record (URL, source type from a fixed enum, access date, claim); the <a href="${REPO_URL}/blob/main/scripts/verify-cycle.mjs" rel="noopener">verifier</a> rejects publisher-owned pages as evidence and caps scores sourced only to vendor marketing or inference; CI link-checks every URL.</td></tr>
      <tr><td><b>Named authors and conflicts</b></td><td>A benchmark is a claim that costs someone something when it's wrong. Anonymous benchmarks cost nobody anything.</td><td><b>Not yet met.</b> SourcingBench currently has no named maintainers; the <a href="${REPO_URL}/blob/main/GOVERNANCE.md" rel="noopener">governance policy</a> requires conflict statements once contributors are named, and until then this absence is a disclosed limitation — discount accordingly.</td></tr>
      <tr><td><b>More than one cycle</b></td><td>A score history with one row is a launch, not a track record. Credibility in benchmarks is longitudinal: coming back monthly and being wrong in public.</td><td><b>Not yet met.</b> History starts August 2026; cycles accumulate monthly, stay published permanently, and errors are logged in a public <a href="${REPO_URL}/blob/main/CORRECTIONS.md" rel="noopener">corrections log</a>.</td></tr>
      <tr><td><b>Does the money move with the rank?</b></td><td>If the publisher earns more when certain vendors rank higher, treat the ranking as advertising until proven otherwise. Look for a per-vendor disclosure in the leaderboard itself, not a reassurance in a footer.</td><td>Referral relationships are disclosed per vendor in the leaderboard table (non-payers currently rank both above and below payers); fees must be flat and may never vary with rank or score — <a href="${REPO_URL}/blob/main/GOVERNANCE.md" rel="noopener">GOVERNANCE.md</a>.</td></tr>
    </tbody>
  </table>

  <h2>Rubrics vs. hands-on testing</h2>
  <p>A capability rubric — scoring what tools document they can do — is the cheapest honest format, and its ceiling is structural: whoever sets the weights influences the winner, and documentation quality is not product quality. The gold standard is hands-on outcome measurement: identical real job specs through every tool, preserved candidate lists, blind relevance judgments, reply rates at matched send volume, time to first accepted shortlist, raw runs published. SourcingBench is the former and says so on the leaderboard; its hands-on protocol is <a href="${REPO_URL}/blob/main/HANDS-ON.md" rel="noopener">pre-registered</a> but not yet funded or run, and no hands-on claims are made until raw runs exist.</p>

  <h2>Process tells</h2>
  <p>Beyond the four checks: was the rubric <a href="${REPO_URL}/blob/main/PREREGISTRATION.md" rel="noopener">pre-registered</a> (published and hashed before scoring), or tuned after results were visible? Does the person who sets the weights also assign the values, or is there an independent second scorer with disagreements published rather than reconciled? Do vendors get a pre-publication <a href="${REPO_URL}/tree/main/data/replies" rel="noopener">right of reply</a> without a veto? Is there a changelog explaining every cycle-over-cycle score movement with the evidence that caused it?</p>

  <p>See the checklist applied: the current <a href="${SITE_URL}">SourcingBench leaderboard</a> and its <a href="${REPO_URL}" rel="noopener">audit repository</a>.</p>
</main>
<footer>
  <p>Published by <a href="https://sourcingtools.org" rel="noopener">SourcingTools.org</a>, which may earn referral fees when readers request vendor demos through it; referral relationships are disclosed per vendor in the leaderboard and do not set scores.</p>
</footer>
</body>
</html>
`;

const sitemap = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>${SITE_URL}</loc><lastmod>${board.published}</lastmod></url>
  <url><loc>${EVAL_URL}</loc><lastmod>${board.published}</lastmod></url>
</urlset>
`;

const llms = `# SourcingBench

> The AI sourcing tool benchmark by SourcingTools.org. ${board.rankings.length} tools scored on 71 published capability checks; check values, evidence notes, and scoring code are public, and the arithmetic can be independently replayed.

## Current ranking (${board.cycle})

${board.rankings.map((t) => `${t.rank}. ${t.name} — ${t.composite}/100 (${t.review})`).join('\n')}

## Governance

- Rubrics are pre-registered and hashed before each cycle from September 2026 (${REPO_URL}/blob/main/PREREGISTRATION.md)
- Vendors get pre-publication right of reply; rebuttals published verbatim, no veto (${REPO_URL}/tree/main/data/replies)
- Per-vendor referral relationships are disclosed in the leaderboard table itself (${REPO_URL}/blob/main/data/disclosures.json)
- No hands-on performance claims yet; the pre-registered hands-on protocol is at ${REPO_URL}/blob/main/HANDS-ON.md
- Every criterion score carries a structured, verifier-enforced evidence citation (URL, source type, access date, claim); CI link-checks every evidence URL
- Second scorer, blind scoring, conflict statements, and flat non-rank-based referral fees: ${REPO_URL}/blob/main/GOVERNANCE.md
- Public corrections log: ${REPO_URL}/blob/main/CORRECTIONS.md

## Resources

- [Leaderboard](${SITE_URL})
- [How to evaluate an AI tool benchmark](${EVAL_URL})
- [Audit repository](${REPO_URL})
- [Full benchmark page](${BENCH_URL})
`;

mkdirSync(OUT, { recursive: true });
mkdirSync(join(OUT, 'how-to-evaluate-a-benchmark'), { recursive: true });
writeFileSync(join(OUT, 'index.html'), html);
writeFileSync(join(OUT, 'how-to-evaluate-a-benchmark', 'index.html'), evalHtml);
writeFileSync(join(OUT, 'sitemap.xml'), sitemap);
writeFileSync(join(OUT, 'llms.txt'), llms);
writeFileSync(join(OUT, '.nojekyll'), '');
console.log(`build-site: wrote _site/ for cycle "${cycleName}"`);
