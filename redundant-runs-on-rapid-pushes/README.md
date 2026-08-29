# three pushes run three full pipelines and you pay for all of them

Somebody pushes a commit, spots a typo, pushes again, then fixes the lint error and pushes a third time. GitHub starts three full pipeline runs. Two of them are testing code that is already obsolete before they finish, and you are billed for every minute of all three. On a macOS runner, where minutes count at ten times the rate, those two wasted runs can cost more than the one you needed.

**Full guide with diagrams:** https://www.allanninal.dev/ci/redundant-runs-on-rapid-pushes/

## Run it

```bash
export DRY_RUN="true"   # report only, write nothing
python python/actions_redundant_runs.py
node node/actions-redundant-runs.mjs
```

## Test it

```bash
pytest python/test_actions_redundant_runs.py
node --test node/actions-redundant-runs.test.mjs
```
