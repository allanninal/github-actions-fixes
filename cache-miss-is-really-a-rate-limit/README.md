# a cache miss that is really a rate limit

The pipeline used to take four minutes and now takes eleven. Nothing failed. Nothing is red. The cache step reports Cache not found for input keys and the job installs everything from scratch, every time. The key has not changed and the cache still exists &mdash; the API declined to serve it, and actions/cache reports a decline the same way it reports an absence.

**Full guide with diagrams:** https://www.allanninal.dev/ci/cache-miss-is-really-a-rate-limit/

## Run it

```bash
export DRY_RUN="true"   # report only, write nothing
python python/actions_cache_audit.py
node node/actions-cache-audit.mjs
```

## Test it

```bash
pytest python/test_actions_cache_audit.py
node --test node/actions-cache-audit.test.mjs
```
