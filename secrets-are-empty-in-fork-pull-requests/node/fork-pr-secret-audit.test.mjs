import { test } from 'node:test';
import assert from 'node:assert/strict';
import { isForkRun } from './fork-pr-secret-audit.mjs';

const run = ({ event = 'pull_request', head = 'contributor/proj', base = 'owner/proj' } = {}) => ({
  event, head_repository: { full_name: head }, repository: { full_name: base },
});

test('a fork PR is detected', () => {
  assert.equal(isForkRun(run()), true);
});

test('a same-repo branch PR keeps its secrets', () => {
  assert.equal(isForkRun(run({ head: 'owner/proj' })), false);
});

test('push events are not affected', () => {
  assert.equal(isForkRun(run({ event: 'push' })), false);
});

test('a missing head repository is not assumed to be a fork', () => {
  const r = run(); r.head_repository = null;
  assert.equal(isForkRun(r), false);
});
