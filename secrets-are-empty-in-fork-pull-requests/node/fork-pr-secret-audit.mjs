/**
 * Find workflow failures caused by secrets being empty in fork pull requests.
 *
 * Secrets are not withheld with an error on a fork PR -- they resolve to empty
 * strings, so the job runs and fails downstream for a reason that looks unrelated.
 */
const API = 'https://api.github.com';

/**
 * Pure decision function over one workflow-run object.
 *
 * Secrets are unavailable when a pull_request event comes from a different
 * repository. Same-repo PRs from branches DO get secrets, which is why comparing
 * repository names matters more than the event name alone.
 */
export function isForkRun(run) {
  if (run.event !== 'pull_request') return false;
  const head = run.head_repository?.full_name;
  const base = run.repository?.full_name;
  return Boolean(head && base && head !== base);
}

async function main() {
  const repo = process.argv[process.argv.indexOf('--repo') + 1];
  const token = (process.env.GITHUB_TOKEN || "");
  if (!token) { console.error('set GITHUB_TOKEN'); process.exit(2); }

  const res = await fetch(`${API}/repos/${repo}/actions/runs?per_page=100`, {
    headers: { Authorization: `Bearer ${token}`, Accept: 'application/vnd.github+json' },
  });
  if (!res.ok) { console.error(`${res.status} ${res.statusText}`); process.exit(1); }
  const { workflow_runs: runs = [] } = await res.json();

  const forkRuns = runs.filter(isForkRun);
  const failed = forkRuns.filter((r) => r.conclusion === 'failure');
  console.log(`${runs.length} recent run(s); ${forkRuns.length} from forks; ${failed.length} failed`);
  for (const run of failed) {
    console.warn(`FORK PR FAILURE  #${run.run_number} ${run.head_repository?.full_name} -- ${run.html_url}`);
  }
  if (failed.length) {
    console.warn('secrets resolve to EMPTY STRINGS in these runs, so a step using one '
      + 'fails downstream rather than reporting a missing secret');
  }
}

if (import.meta.url === `file://${process.argv[1]}`) main();
