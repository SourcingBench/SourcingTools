#!/usr/bin/env node
// Evidence link checker: fetches every unique evidence URL in every published
// cycle and fails on dead links (DNS failure, 404/410, 5xx). Bot-challenge
// responses (401/403/429/999) count as reachable — the page exists, it just
// refuses automated clients.
//
// Usage: node scripts/check-links.mjs

import { readFileSync, readdirSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const CYCLES_DIR = join(ROOT, 'data', 'cycles');
const OK_BLOCKED = [401, 403, 429, 999];
const UA = 'Mozilla/5.0 (compatible; SourcingBench-link-check/1.0; +https://github.com/SourcingBench/SourcingTools)';

const urls = new Map(); // url -> first "cycle tool.criterion" that cites it
for (const cycle of readdirSync(CYCLES_DIR).sort()) {
  const caps = JSON.parse(readFileSync(join(CYCLES_DIR, cycle, 'capabilities.json'), 'utf8'));
  for (const t of caps.tools) {
    for (const [cid, s] of Object.entries(t.scores)) {
      for (const e of s.evidence ?? []) {
        if (!urls.has(e.url)) urls.set(e.url, `${cycle}: ${t.slug}.${cid}`);
      }
    }
  }
}

async function check(url) {
  for (const method of ['HEAD', 'GET']) {
    try {
      const res = await fetch(url, {
        method,
        redirect: 'follow',
        headers: { 'user-agent': UA },
        signal: AbortSignal.timeout(20000),
      });
      if (res.ok || OK_BLOCKED.includes(res.status)) return null;
      if (method === 'GET') return `HTTP ${res.status}`;
    } catch (err) {
      if (method === 'GET') return err.message;
    }
  }
  return 'unreachable';
}

const failures = [];
for (const [url, cited] of urls) {
  const problem = await check(url);
  console.log(`${problem ? 'FAIL' : ' ok '} ${url}${problem ? ` (${problem})` : ''}`);
  if (problem) failures.push(`${url} — ${problem} (first cited at ${cited})`);
}
console.log(`\nchecked ${urls.size} unique evidence URLs`);
if (failures.length) {
  console.error('check-links FAILED:');
  for (const f of failures) console.error(`  - ${f}`);
  process.exit(1);
}
console.log('check-links OK');
