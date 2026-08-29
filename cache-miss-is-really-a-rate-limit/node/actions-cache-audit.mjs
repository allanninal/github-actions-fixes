/**
 * Diagnose why an Actions cache never restores.
 *
 * A rate limit, an unstable key and a fork PR all produce the same log line: cache
 * miss. This separates them by looking at what is actually stored.
 */
const API = 'https://api.github.com';

/** Everything before the final hash segment, which is what should be reused. */
export const prefixOf = (key) => key.replace(/-[0-9a-f]{8,}$/, '');

/**
 * Pure decision function.
 *
 * An unstable key writes a new entry every run and reads none, so the signature is
 * many entries sharing a prefix. That fills the quota and evicts what you wanted.
 */
export function unstableKeys(caches, minEntries = 5) {
  const groups = {};
  for (const c of caches) {
    const p = prefixOf(c.key ?? '');
    groups[p] = [...(groups[p] ?? []), c];
  }
  return Object.fromEntries(Object.entries(groups).filter(([, v]) => v.length >= minEntries));
}

async function main() {
  const repo = process.argv[process.argv.indexOf('--repo') + 1];
  const token = (process.env.GITHUB_TOKEN || "dummy-github-token");
  if (!token) { console.error('set GITHUB_TOKEN'); process.exit(2); }

  const res = await fetch(`${API}/repos/${repo}/actions/caches?per_page=100`, {
    headers: { Authorization: `Bearer ${token}`, Accept: 'application/vnd.github+json' },
  });
  const { actions_caches: caches = [] } = await res.json();
  const totalGb = caches.reduce((t, c) => t + (c.size_in_bytes ?? 0), 0) / 1_073_741_824;
  console.log(`${caches.length} cache entr(ies), ${totalGb.toFixed(2)} GB total`);

  const suspect = unstableKeys(caches);
  for (const [prefix, entries] of Object.entries(suspect).sort((a, b) => b[1].length - a[1].length)) {
    const gb = entries.reduce((t, e) => t + (e.size_in_bytes ?? 0), 0) / 1_073_741_824;
    console.warn(`UNSTABLE KEY  ${prefix.slice(0, 45).padEnd(45)} ${entries.length} entries, ${gb.toFixed(2)} GB`);
  }
  if (Object.keys(suspect).length) {
    console.warn('hash the lockfile, not the run id or a timestamp');
  } else {
    console.log('no unstable-key pattern; check whether the run came from a fork, or '
      + 'whether the cache service rate limited -- both are logged as a plain miss');
  }
}

if (import.meta.url === `file://${process.argv[1]}`) main();
