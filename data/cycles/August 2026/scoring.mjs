// Frozen scoring aggregator for the August 2026 cycle.
// Recomputes the published leaderboard from criteria.json + capabilities.json.
// Each capability check is scored 0/1/2. Criterion value = points/max * 10.
// Dimension score = dimension points / dimension max * 100. Composite = weighted sum.

export function scoreCycle(criteria, capabilities) {
  const round1 = (x) => Math.round(x * 10) / 10;
  const round2 = (x) => Math.round(x * 100) / 100;
  const rows = capabilities.tools.map((t) => {
    const dimensions = {};
    let composite = 0;
    for (const d of criteria.dimensions) {
      let points = 0;
      let max = 0;
      for (const c of d.criteria) {
        const s = t.scores[c.id];
        if (!s || !s.checks) throw new Error(`${t.slug}: missing checks for ${c.id}`);
        let critPoints = 0;
        for (const chk of c.checks) {
          const v = s.checks[chk.id];
          if (![0, 1, 2].includes(v)) {
            throw new Error(`${t.slug}: missing or out-of-range value for ${c.id}.${chk.id}`);
          }
          critPoints += v;
        }
        const critMax = 2 * c.checks.length;
        if (s.points !== critPoints || s.max !== critMax) {
          throw new Error(`${t.slug}: published points for ${c.id} do not match checks`);
        }
        if (s.value !== round1((critPoints / critMax) * 10)) {
          throw new Error(`${t.slug}: published value for ${c.id} does not match checks`);
        }
        points += critPoints;
        max += critMax;
      }
      dimensions[d.id] = round1((points / max) * 100);
      composite += d.weight * ((points / max) * 100);
    }
    return {
      slug: t.slug,
      name: t.name,
      website: t.website,
      review: t.review,
      composite: round2(composite),
      dimensions,
    };
  });
  rows.sort((a, b) => b.composite - a.composite);
  rows.forEach((r, i) => (r.rank = i + 1));
  return {
    cycle: criteria.cycle,
    rubric_version: criteria.version,
    weights: Object.fromEntries(criteria.dimensions.map((d) => [d.id, d.weight])),
    rankings: rows,
  };
}
