"""Find workflow failures caused by secrets being empty in fork pull requests.

Secrets are not withheld with an error on a fork PR -- they resolve to empty
strings, so the job runs and fails downstream for a reason that looks unrelated.
This narrows the search to runs where that is possible.
"""
import argparse
import logging
import os
import sys

import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("fork_pr_secret_audit")

API = "https://api.github.com"


def is_fork_run(run):
    """Pure decision function over one workflow-run object.

    Secrets are unavailable when a pull_request event comes from a different
    repository. Same-repo PRs from branches DO get secrets, which is why comparing
    the repository names matters more than the event name alone.
    """
    if run.get("event") != "pull_request":
        return False
    head = (run.get("head_repository") or {}).get("full_name")
    base = (run.get("repository") or {}).get("full_name")
    return bool(head and base and head != base)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True, help="owner/name")
    ap.add_argument("--limit", type=int, default=100)
    args = ap.parse_args()

    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        log.error("set GITHUB_TOKEN")
        return 2
    headers = {"Authorization": f"Bearer {token}",
               "Accept": "application/vnd.github+json"}

    r = requests.get(f"{API}/repos/{args.repo}/actions/runs",
                     headers=headers, params={"per_page": args.limit}, timeout=30)
    r.raise_for_status()
    runs = r.json().get("workflow_runs", [])

    fork_runs = [x for x in runs if is_fork_run(x)]
    failed = [x for x in fork_runs if x.get("conclusion") == "failure"]

    log.info("%d recent run(s); %d from forks; %d of those failed",
             len(runs), len(fork_runs), len(failed))
    for run in failed:
        log.warning("FORK PR FAILURE  #%s %s -- %s",
                    run.get("run_number"),
                    (run.get("head_repository") or {}).get("full_name"),
                    run.get("html_url"))
    if failed:
        log.warning("secrets resolve to EMPTY STRINGS in these runs, so a step using "
                    "one fails downstream rather than reporting a missing secret")
    return 0


if __name__ == "__main__":
    sys.exit(main())
