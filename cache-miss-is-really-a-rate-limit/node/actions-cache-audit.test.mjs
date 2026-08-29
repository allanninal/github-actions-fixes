import { test } from 'node:test';
import assert from 'node:assert/strict';
import { prefixOf, unstableKeys } from './actions-cache-audit.mjs';

const cache = (key, size = 1000) => ({ key, size_in_bytes: size });

test('the prefix strips the hash segment', () => {
  assert.equal(prefixOf('Linux-node-a1b2c3d4e5f6'), 'Linux-node');
});

test('a key with no hash is unchanged', () => {
  assert.equal(prefixOf('Linux-node'), 'Linux-node');
});

test('a healthy cache is not flagged', () => {
  assert.deepEqual(unstableKeys([cache('Linux-node-a1b2c3d4'), cache('Linux-node-b2c3d4e5')]), {});
});

test('many entries on one prefix is flagged', () => {
  const caches = Array.from({ length: 9 }, (_, i) => cache(`Linux-node-${i.toString(16).padStart(8, '0')}`));
  assert.ok('Linux-node' in unstableKeys(caches));
});
