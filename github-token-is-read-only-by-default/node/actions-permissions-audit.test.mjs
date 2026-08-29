import { test } from 'node:test';
import assert from 'node:assert/strict';
import { neededScopes, gaps } from './actions-permissions-audit.mjs';

const PUSHES = 'jobs:\n  release:\n    steps:\n      - run: git push origin main\n';
const GRANTED = 'jobs:\n  release:\n    permissions:\n      contents: write\n'
  + '    steps:\n      - run: git push origin main\n';

test('a push needs contents: write', () => {
  assert.ok(neededScopes(PUSHES).includes('contents: write'));
});

test('a workflow that grants what it needs is not flagged', () => {
  assert.deepEqual(gaps(GRANTED), []);
});

test('a workflow missing the grant is flagged', () => {
  assert.deepEqual(gaps(PUSHES), ['contents: write']);
});

test('a read-only workflow needs nothing', () => {
  assert.deepEqual(neededScopes('jobs:\n  test:\n    steps:\n      - run: pytest'), []);
});
