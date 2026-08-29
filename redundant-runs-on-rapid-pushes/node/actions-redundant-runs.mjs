/**
 * Estimate CI minutes wasted on runs superseded by a later push.
 *
 * Reports only. Adding cancel-in-progress to a deploy workflow would leave a
 * half-finished deploy, so the change is left to a human.
 */
const API = 'https://api.github.com';
// Billed minutes per wall-clock minute, per runner OS.
export const MULTIPLIER = { ubuntu: 1, windows: 2, macos: 10 };

/**
 * Pure decision function.
 *
 * A run is superseded when a LATER run exists for the same workflow and branch.
 * Grouping by workflow as well as branch matters: two different workflows on one
 * branch are not competing.
 */
export function findSuperseded(runs) {
  const byKey = new Map();
  for (const r of runs) {
    const key = `${r.workflow_id}::${r.head_branch}`;
    byKey.set(key, [...(byKey.get(key) ?? []), r]);
  }
  const superseded = [];
  for (const group of byKey.values()) {
    group.sort((a, b) => (a.run_number ?? 0) - (b.run_number ?? 0));
    for (let i = 0; i < group.length - 1; i += 1) {
      if (group[i].created_at && group[i + 1].created_at
        && group[i].created_at < group[i + 1].created_at) superseded.push(group[i]);
    }
  }
  return superseded;
}

export function billedMinutes(run, wallMinutes) {
  const name = (run.labels ?? []).join(' ').toLowerCase() || 'ubuntu';
  for (const [os, mult] of Object.entries(MULTIPLIER)) {
    if (name.includes(os)) return wallMinutes * mult;
  }
  return wallMinutes;
}

async function main() {
  const repo = process.argv[process.argv.indexOf('--repo') + 1];
  const token = (process.env.GITHUB_TOKEN || "dummy-github-token");
  if (!token) { console.error('set GITHUB_TOKEN'); process.exit(2); }

  const res = await fetch(`${API}/repos/${repo}/actions/runs?per_page=100`, {
    headers: { Authorization: `Bearer ${token}`, Accept: 'application/vnd.github+json' },
  });
  const { workflow_runs: runs = [] } = await res.json();
  const wasted = findSuperseded(runs);
  console.log(`${runs.length} recent run(s), ${wasted.length} superseded by a later push`);

  const counts = {};
  for (const w of wasted) counts[w.name] = (counts[w.name] ?? 0) + 1;
  for (const [name, count] of Object.entries(counts).sort((a, b) => b[1] - a[1])) {
    console.warn(`  ${name.padEnd(40)} ${count} redundant run(s)`);
  }
  if (wasted.length) {
    console.warn('add a concurrency group; do NOT add cancel-in-progress to a deploy workflow');
  }
}

if (import.meta.url === `file://${process.argv[1]}`) main();
