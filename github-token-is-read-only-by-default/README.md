# GITHUB_TOKEN is read-only and the error just says 403

The workflow builds fine and then dies on the last step with 403: Resource not accessible by integration. The token is right there in the environment. Nothing changed in the code. What changed, some time ago and for everyone, is the default: GITHUB_TOKEN now starts read-only, and any step that pushes a commit, cuts a release or comments on an issue needs the permission granted explicitly.

**Full guide with diagrams:** https://www.allanninal.dev/ci/github-token-is-read-only-by-default/

## Run it

```bash
export DRY_RUN="true"   # report only, write nothing
python python/actions_permissions_audit.py
node node/actions-permissions-audit.mjs
```

## Test it

```bash
pytest python/test_actions_permissions_audit.py
node --test node/actions-permissions-audit.test.mjs
```
