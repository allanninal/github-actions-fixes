import { test } from 'node:test';
import assert from 'node:assert/strict';
import { findSuperseded, billedMinutes } from './actions-redundant-runs.mjs';

const run = (n, { wf = 1, branch = 'main' } = {}) => ({
  run_number: n, workflow_id: wf, head_branch: branch,
  created_at: `2026-08-28T00:${String(n).padStart(2, '0')}:00Z`, name: `wf${wf}`,
});

test('a single run is not superseded', () => {
  assert.deepEqual(findSuperseded([run(1)]), []);
});

test('the earlier of two runs is superseded', () => {
  const out = findSuperseded([run(1), run(2)]);
  assert.equal(out.length, 1);
  assert.equal(out[0].run_number, 1);
});

test('different workflows do not compete', () => {
  assert.deepEqual(findSuperseded([run(1, { wf: 1 }), run(2, { wf: 2 })]), []);
});

test('the macOS multiplier applies', () => {
  assert.equal(billedMinutes({ labels: ['macos-latest'] }, 10), 100);
});

test('linux is billed one to one', () => {
  assert.equal(billedMinutes({ labels: ['ubuntu-latest'] }, 10), 10);
});
