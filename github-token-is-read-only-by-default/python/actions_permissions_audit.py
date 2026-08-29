"""Audit GITHUB_TOKEN permissions: too little to work, or more than needed.

The 403 message never names the missing scope, so this maps the operation a job
performs back to the scope it requires. It also flags repositories still defaulting
to write permissions, which is the same problem pointing the other way.
"""
import argparse
import logging
import os
import re
import sys

import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("actions_permissions_audit")

API = "https://api.github.com"

# Operations that write, and the scope each one needs. The API will not tell you.
WRITE_HINTS = [
    (re.compile(r"\bgit\s+push\b|actions/create-release|softprops/action-gh-release"),
     "contents: write"),
    (re.compile(r"gh\s+release\s+create|\bgh\s+api\b.*releases"), "contents: write"),
    (re.compile(r"gh\s+pr\s+comment|actions/github-script.*createComment"),
     "pull-requests: write"),
    (re.compile(r"docker/build-push-action|npm\s+publish|gh\s+api.*packages"),
     "packages: write"),
    (re.compile(r"aws-actions/configure-aws-credentials|id-token"), "id-token: write"),
]


def needed_scopes(workflow_text):
    """Pure decision function: which scopes does this workflow appear to need?"""
    return sorted({scope for pattern, scope in WRITE_HINTS
                   if pattern.search(workflow_text)})


def declared_scopes(workflow_text):
    """Scopes the workflow actually grants, anywhere in the file."""
    return sorted(set(re.findall(r"^\s*([a-z-]+):\s*write\s*$", workflow_text, re.M)))


def gaps(workflow_text):
    """What the workflow needs but has not granted."""
    have = {s.split(":")[0] for s in declared_scopes(workflow_text)}
    return [s for s in needed_scopes(workflow_text) if s.split(":")[0].strip() not in have]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--workflow-dir", default=".github/workflows")
    args = ap.parse_args()

    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        log.error("set GITHUB_TOKEN")
        return 2
    headers = {"Authorization": f"Bearer {token}",
               "Accept": "application/vnd.github+json"}

    r = requests.get(f"{API}/repos/{args.repo}/actions/permissions/workflow",
                     headers=headers, timeout=30)
    if r.ok:
        default = r.json().get("default_workflow_permissions")
        if default == "write":
            log.warning("%s defaults to WRITE: every workflow token can push, release "
                        "and comment whether it needs to or not", args.repo)
        else:
            log.info("%s defaults to %s", args.repo, default)

    from pathlib import Path
    failed = False
    for wf in sorted(Path(args.workflow_dir).glob("*.y*ml")):
        text = wf.read_text(encoding="utf-8")
        missing = gaps(text)
        if missing:
            failed = True
            log.error("%s needs %s but does not declare it",
                      wf.name, ", ".join(missing))
        else:
            log.info("%s: permissions look sufficient", wf.name)
    if failed:
        log.error("a missing scope surfaces as: 403 Resource not accessible by "
                  "integration -- the message never says which one")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
