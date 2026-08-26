#!/usr/bin/env node
// SourcingBench audit script.
//
// For each published cycle it runs three checks:
//   1. Manifest integrity — recompute the SHA-256 of every file named in
//      cycle.json and assert it matches. Catches truncated or doctored data.
//   2. Rubric coverage — every tool has an in-range value and an evidence note for
//      every criterion in the published rubric; the rubric weights sum to 1.
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
  const critIds = criteria.dimensions.flatMap((d) => d.criteria.map((c) => c.id));
  const weightSum = criteria.dimensions.reduce((a, d) => a + d.weight, 0);
  if (Math.abs(weightSum - 1) > 1e-9) errors.push(`${cycle}: dimension weights sum to ${weightSum}, not 1`);
  for (const t of capabilities.tools) {
    for (const id of critIds) {
      const s = t.scores[id];
      if (!s) errors.push(`${cycle}: ${t.slug} missing criterion ${id}`);
      else {
        if (!(Number.isInteger(s.value) && s.value >= 0 && s.value <= 10))
          errors.push(`${cycle}: ${t.slug}.${id} value out of range: ${s.value}`);
        if (!s.note || typeof s.note !== 'string')
          errors.push(`${cycle}: ${t.slug}.${id} has no evidence note`);
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
    console.log(`[ok] ${cycle}: ${capabilities.tools.length} tools x ${critIds.length} criteria verified, scores replayed`);
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
