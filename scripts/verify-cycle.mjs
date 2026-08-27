#!/usr/bin/env node
// SourcingBench audit script.
//
// For each published cycle it runs three checks:
//   1. Manifest integrity — recompute the SHA-256 of every file named in
//      cycle.json and assert it matches. Catches truncated or doctored data.
//   2. Rubric coverage — every tool has an in-range 0/1/2 value for every
//      capability check and an evidence note for every criterion in the
//      published rubric; the rubric weights sum to 1.
//   2b. Evidence integrity — every criterion carries at least one structured
//      evidence record (url, source_type from the fixed enum, accessed date
//      inside the cycle window, and the claim relied on); publisher-owned
//      pages are banned as evidence; a criterion whose best source is
//      vendor_claim or inference cannot award any check a 2.
//   3. Score replay — re-run the cycle's frozen scoring.mjs against
//      capabilities.json and assert every composite, dimension score, and
//      rank matches the published leaderboard.json exactly.
//
// Usage:
//   node scripts/verify-cycle.mjs --all
//   node scripts/verify-cycle.mjs "August 2026"

import { createHash } from 'node:crypto';
import { readFileSync, readdirSync, existsSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const CYCLES_DIR = join(ROOT, 'data', 'cycles');
const REQUIRED = ['criteria.json', 'capabilities.json', 'scoring.mjs', 'leaderboard.json'];

const sha256 = (p) => createHash('sha256').update(readFileSync(p)).digest('hex');
const readJson = (p) => JSON.parse(readFileSync(p, 'utf8'));

const SOURCE_TYPES = ['hands_on', 'api_docs', 'product_docs', 'changelog', 'vendor_claim', 'third_party_review', 'inference'];
const WEAK_SOURCES = ['vendor_claim', 'inference']; // cannot support a check value of 2
const SELF_HOSTS = ['sourcingtools.org', 'sourcingbench.github.io', 'github.com/sourcingbench'];

function checkEvidence(cycle, tool, critId, s, checkVals, errors) {
  const ev = s.evidence;
  if (!Array.isArray(ev) || ev.length === 0) {
    errors.push(`${cycle}: ${tool}.${critId} has no structured evidence records`);
    return;
  }
  let best = SOURCE_TYPES.length;
  for (const [i, e] of ev.entries()) {
    const where = `${tool}.${critId}.evidence[${i}]`;
    let url;
    try {
      url = new URL(e.url);
      if (!['http:', 'https:'].includes(url.protocol)) throw new Error('non-http');
    } catch {
      errors.push(`${cycle}: ${where} has invalid url: ${e.url}`);
    }
    if (url && SELF_HOSTS.some((h) => `${url.hostname}${url.pathname}`.toLowerCase().includes(h)))
      errors.push(`${cycle}: ${where} cites a publisher-owned page as evidence: ${e.url}`);
    const tier = SOURCE_TYPES.indexOf(e.source_type);
    if (tier === -1) errors.push(`${cycle}: ${where} source_type not in enum: ${e.source_type}`);
    else best = Math.min(best, tier);
    if (!/^\d{4}-\d{2}-\d{2}$/.test(e.accessed ?? '') || Number.isNaN(Date.parse(e.accessed)))
      errors.push(`${cycle}: ${where} has invalid accessed date: ${e.accessed}`);
    if (!e.claim || typeof e.claim !== 'string')
      errors.push(`${cycle}: ${where} has no claim`);
  }
  if (best < SOURCE_TYPES.length && WEAK_SOURCES.includes(SOURCE_TYPES[best]) && checkVals.some((v) => v === 2))
    errors.push(`${cycle}: ${tool}.${critId} awards a 2 but its best source is ${SOURCE_TYPES[best]} (capped at 1)`);
}

async function verifyCycle(cycle) {
  const errors = [];
  const dir = join(CYCLES_DIR, cycle);

  // 1. Manifest integrity
  const manifest = readJson(join(dir, 'cycle.json'));
  for (const name of REQUIRED) {
    if (!(name in manifest.files)) errors.push(`${cycle}: manifest missing required entry ${name}`);
  }
  for (const [name, expected] of Object.entries(manifest.files)) {
    if (!REQUIRED.includes(name)) {
      errors.push(`${cycle}: unknown filename in manifest: ${name}`);
      continue;
    }
    const p = join(dir, name);
    if (!existsSync(p)) {
      errors.push(`${cycle}: manifested file missing on disk: ${name}`);
      continue;
    }
    const actual = sha256(p);
    if (actual !== expected) errors.push(`${cycle}: sha256 mismatch for ${name}: expected ${expected}, got ${actual}`);
  }
  if (errors.length) return errors; // don't replay over tampered inputs

  // 2. Rubric coverage
  const criteria = readJson(join(dir, 'criteria.json'));
  const capabilities = readJson(join(dir, 'capabilities.json'));
  const crits = criteria.dimensions.flatMap((d) => d.criteria);
  const critIds = crits.map((c) => c.id);
  const weightSum = criteria.dimensions.reduce((a, d) => a + d.weight, 0);
  if (Math.abs(weightSum - 1) > 1e-9) errors.push(`${cycle}: dimension weights sum to ${weightSum}, not 1`);
  for (const t of capabilities.tools) {
    for (const c of crits) {
      const s = t.scores[c.id];
      if (!s) { errors.push(`${cycle}: ${t.slug} missing criterion ${c.id}`); continue; }
      const checkIds = c.checks.map((k) => k.id);
      for (const k of checkIds) {
        const v = s.checks?.[k];
        if (![0, 1, 2].includes(v)) errors.push(`${cycle}: ${t.slug}.${c.id}.${k} check value out of range: ${v}`);
      }
      for (const k of Object.keys(s.checks ?? {})) {
        if (!checkIds.includes(k)) errors.push(`${cycle}: ${t.slug}.${c.id} scores unknown check ${k}`);
      }
      if (typeof s.value !== 'number' || s.value < 0 || s.value > 10)
        errors.push(`${cycle}: ${t.slug}.${c.id} value out of range: ${s.value}`);
      if (!s.note || typeof s.note !== 'string')
        errors.push(`${cycle}: ${t.slug}.${c.id} has no evidence note`);
      checkEvidence(cycle, t.slug, c.id, s, checkIds.map((k) => s.checks?.[k]), errors);
      for (const e of s.evidence ?? []) {
        if (e.accessed && capabilities.assessed && e.accessed > capabilities.assessed)
          errors.push(`${cycle}: ${t.slug}.${c.id} evidence accessed ${e.accessed} after cycle assessment date ${capabilities.assessed}`);
      }
    }
    for (const id of Object.keys(t.scores)) {
      if (!critIds.includes(id)) errors.push(`${cycle}: ${t.slug} scores unknown criterion ${id}`);
    }
  }

  // 3. Score replay through the frozen aggregator
  const { scoreCycle } = await import(pathToFileURL(join(dir, 'scoring.mjs')).href);
  const replayed = scoreCycle(criteria, capabilities);
  const published = readJson(join(dir, 'leaderboard.json'));
  const pubBySlug = Object.fromEntries(published.rankings.map((r) => [r.slug, r]));
  if (replayed.rankings.length !== published.rankings.length)
    errors.push(`${cycle}: replayed ${replayed.rankings.length} tools, published ${published.rankings.length}`);
  for (const r of replayed.rankings) {
    const p = pubBySlug[r.slug];
    if (!p) { errors.push(`${cycle}: ${r.slug} missing from published leaderboard`); continue; }
    if (r.composite !== p.composite) errors.push(`${cycle}: ${r.slug} composite ${r.composite} != published ${p.composite}`);
    if (r.rank !== p.rank) errors.push(`${cycle}: ${r.slug} rank ${r.rank} != published ${p.rank}`);
    for (const [d, v] of Object.entries(r.dimensions)) {
      if (p.dimensions[d] !== v) errors.push(`${cycle}: ${r.slug}.${d} ${v} != published ${p.dimensions[d]}`);
    }
  }
  if (!errors.length) {
    const nChecks = crits.reduce((a, c) => a + c.checks.length, 0);
    console.log(`[ok] ${cycle}: ${capabilities.tools.length} tools x ${critIds.length} criteria (${nChecks} checks) verified, scores replayed`);
  }
  return errors;
}

const arg = process.argv[2];
if (!arg) {
  console.error('usage: verify-cycle.mjs --all | "<cycle name>"');
  process.exit(2);
}
const cycles = arg === '--all' ? readdirSync(CYCLES_DIR).sort() : [arg];
let allErrors = [];
for (const c of cycles) allErrors = allErrors.concat(await verifyCycle(c));
if (allErrors.length) {
  console.error('verify-cycle FAILED:');
  for (const e of allErrors) console.error(`  - ${e}`);
  process.exit(1);
}
console.log('verify-cycle OK');
