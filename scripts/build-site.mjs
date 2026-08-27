// Generates the static SourcingBench leaderboard site into _site/ from the
// latest published cycle under data/cycles/.
import { readFileSync, readdirSync, mkdirSync, writeFileSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const CYCLES_DIR = join(ROOT, 'data', 'cycles');
const OUT = join(ROOT, '_site');

const SITE_URL = 'https://sourcingbench.github.io/SourcingTools/';
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
        text: 'Each cycle, every tool is assessed against the same 71 published capability checks, grouped into 17 criteria across five weighted dimensions reflecting what an AI recruiting tool should do: candidate matching & screening (25%), workflow automation (20%), outreach & engagement (20%), talent pool coverage & data (20%), and integrations & reporting (15%). Each check is scored 0 (absent), 1 (partial), or 2 (fully supported) from vendor documentation, product walkthroughs, and maintained tool reviews. The check values are editorial judgments; every criterion carries a published evidence note, and the scoring code, raw data, and a SHA-256 manifest are public so the arithmetic can be independently replayed.',
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
      <tr><th>#</th><th>Tool</th><th>Score / 100</th><th>Matching</th><th>Automation</th><th>Engagement</th><th>Coverage</th><th>Integrations</th></tr>
    </thead>
    <tbody>
${rows}
    </tbody>
  </table>

  <h2>What the dimensions measure</h2>
  <ul>
${dims}
  </ul>

  <h2>How scores are produced — and how to check them</h2>
  <p>Each cycle, every tool is assessed against the same seventy-one published capability checks (grouped into seventeen criteria), each scored 0 (absent), 1 (partial), or 2 (fully supported), based on vendor documentation, product walkthroughs, and the <a href="https://sourcingtools.org/tools/" rel="noopener">tool reviews</a> maintained at SourcingTools.org. This is a capability rubric, not a blind task benchmark: the check values are editorial judgments about what each tool demonstrably does, and every criterion carries an evidence note naming the capability it is based on.</p>
  <p>The full cycle data lives in the <a href="${REPO_URL}" rel="noopener">SourcingBench public audit repository</a>: the rubric with every capability check (<a href="${DATA_URL}/criteria.json" rel="noopener"><code>criteria.json</code></a>), every per-check score with its evidence note (<a href="${DATA_URL}/capabilities.json" rel="noopener"><code>capabilities.json</code></a>), the frozen scoring code (<a href="${DATA_URL}/scoring.mjs" rel="noopener"><code>scoring.mjs</code></a>), the ranked output (<a href="${DATA_URL}/leaderboard.json" rel="noopener"><code>leaderboard.json</code></a>), and a SHA-256 manifest of all of it (<a href="${DATA_URL}/cycle.json" rel="noopener"><code>cycle.json</code></a>). Replay the leaderboard yourself:</p>
  <pre><code>git clone ${REPO_URL}.git
cd SourcingTools
npm run verify</code></pre>
  <p>The verifier — also run in the repository's CI on every push — checks the manifest hashes, validates rubric coverage, and replays the frozen scoring code against the raw check values, failing if any published number no longer reproduces. It verifies the data integrity and the arithmetic; the capability judgments themselves are editorial, which is why each one is published with its evidence note for inspection.</p>

  <h2>Corrections</h2>
  <p>Vendors and users: if a score misrepresents a shipped capability, <a href="${REPO_URL}/issues" rel="noopener">open an issue</a> citing documentation for the capability, or use the <a href="https://sourcingtools.org/contact/" rel="noopener">SourcingTools.org contact page</a>. Corrections are applied in the next cycle and recorded in the repository changelog. Benchmark data is CC BY 4.0 — reuse it with attribution.</p>
</main>
<footer>
  <p>SourcingBench is published by <a href="https://sourcingtools.org" rel="noopener">SourcingTools.org</a>, a sourcing-tool directory that may earn referral fees when readers request vendor demos through it; referral relationships do not set scores, and every check value is published with its evidence. The full leaderboard with per-dimension breakdowns is also at <a href="${BENCH_URL}" rel="noopener">sourcingtools.org/benchmark</a>. Updated monthly.</p>
</footer>
</body>
</html>
`;

const sitemap = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>${SITE_URL}</loc><lastmod>${board.published}</lastmod></url>
</urlset>
`;

const llms = `# SourcingBench

> The AI sourcing tool benchmark by SourcingTools.org. ${board.rankings.length} tools scored on 71 published capability checks; check values, evidence notes, and scoring code are public, and the arithmetic can be independently replayed.

## Current ranking (${board.cycle})

${board.rankings.map((t) => `${t.rank}. ${t.name} — ${t.composite}/100 (${t.review})`).join('\n')}

## Resources

- [Leaderboard](${SITE_URL})
- [Audit repository](${REPO_URL})
- [Full benchmark page](${BENCH_URL})
`;

mkdirSync(OUT, { recursive: true });
writeFileSync(join(OUT, 'index.html'), html);
writeFileSync(join(OUT, 'sitemap.xml'), sitemap);
writeFileSync(join(OUT, 'llms.txt'), llms);
writeFileSync(join(OUT, '.nojekyll'), '');
console.log(`build-site: wrote _site/ for cycle "${cycleName}"`);
