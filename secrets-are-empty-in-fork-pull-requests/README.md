# secrets are empty strings in fork pull requests

The workflow passes on main and on every branch pushed by someone with write access. An outside contributor opens a pull request and the same workflow fails somewhere strange &mdash; a deploy step authenticating as nobody, an API call returning 401, a test asserting on a config value that is suddenly blank. GitHub did not refuse to give the job its secrets. It gave them as empty strings, and the job carried on.

**Full guide with diagrams:** https://www.allanninal.dev/ci/secrets-are-empty-in-fork-pull-requests/

## Run it

```bash
export DRY_RUN="true"   # report only, write nothing
python python/fork_pr_secret_audit.py
node node/fork-pr-secret-audit.mjs
```

## Test it

```bash
pytest python/test_fork_pr_secret_audit.py
node --test node/fork-pr-secret-audit.test.mjs
```
