/**
 * Audit GITHUB_TOKEN permissions: too little to work, or more than needed.
 *
 * The 403 message never names the missing scope, so this maps the operation a job
 * performs back to the scope it requires.
 */
import { readdir, readFile } from 'node:fs/promises';
import path from 'node:path';

const API = 'https://api.github.com';

// Operations that write, and the scope each one needs. The API will not tell you.
const WRITE_HINTS = [
  [/\bgit\s+push\b|actions\/create-release|softprops\/action-gh-release/, 'contents: write'],
  [/gh\s+release\s+create|\bgh\s+api\b.*releases/, 'contents: write'],
  [/gh\s+pr\s+comment|actions\/github-script.*createComment/, 'pull-requests: write'],
  [/docker\/build-push-action|npm\s+publish|gh\s+api.*packages/, 'packages: write'],
  [/aws-actions\/configure-aws-credentials|id-token/, 'id-token: write'],
];

/** Pure decision function: which scopes does this workflow appear to need? */
export function neededScopes(text) {
  return [...new Set(WRITE_HINTS.filter(([re]) => re.test(text)).map(([, s]) => s))].sort();
}

export function declaredScopes(text) {
  return [...new Set([...text.matchAll(/^\s*([a-z-]+):\s*write\s*$/gm)].map((m) => m[1]))].sort();
}

export function gaps(text) {
  const have = new Set(declaredScopes(text));
  return neededScopes(text).filter((s) => !have.has(s.split(':')[0].trim()));
}

async function main() {
  const repo = process.argv[process.argv.indexOf('--repo') + 1];
  const dir = '.github/workflows';
  const token = (process.env.GITHUB_TOKEN || "dummy-github-token");
  if (!token) { console.error('set GITHUB_TOKEN'); process.exit(2); }

  const res = await fetch(`${API}/repos/${repo}/actions/permissions/workflow`, {
    headers: { Authorization: `Bearer ${token}`, Accept: 'application/vnd.github+json' },
  });
  if (res.ok) {
    const { default_workflow_permissions: d } = await res.json();
    if (d === 'write') console.warn(`${repo} defaults to WRITE: every workflow token can push`);
    else console.log(`${repo} defaults to ${d}`);
  }

  let failed = false;
  for (const f of (await readdir(dir)).filter((n) => /\.ya?ml$/.test(n))) {
    const text = await readFile(path.join(dir, f), 'utf8');
    const missing = gaps(text);
    if (missing.length) { failed = true; console.error(`${f} needs ${missing.join(', ')}`); }
    else console.log(`${f}: permissions look sufficient`);
  }
  if (failed) {
    console.error('a missing scope surfaces as: 403 Resource not accessible by integration');
  }
  process.exit(failed ? 1 : 0);
}

if (import.meta.url === `file://${process.argv[1]}`) main();
