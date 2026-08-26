// Frozen scoring aggregator for the August 2026 cycle.
// Recomputes the published leaderboard from criteria.json + capabilities.json.
// Dimension score = mean(criterion values) / 4 * 100. Composite = weighted sum.

export function scoreCycle(criteria, capabilities) {
  const round1 = (x) => Math.round(x * 10) / 10;
  const rows = capabilities.tools.map((t) => {
    const dimensions = {};
    let composite = 0;
    for (const d of criteria.dimensions) {
      const vals = d.criteria.map((c) => {
        const s = t.scores[c.id];
        if (!s || typeof s.value !== 'number' || s.value < 0 || s.value > 4) {
          throw new Error(`${t.slug}: missing or out-of-range value for ${c.id}`);
        }
        return s.value;
      });
      const ds = (vals.reduce((a, b) => a + b, 0) / vals.length / 4) * 100;
      dimensions[d.id] = round1(ds);
      composite += d.weight * ds;
    }
    return {
      slug: t.slug,
      name: t.name,
      website: t.website,
      review: t.review,
      composite: round1(composite),
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
