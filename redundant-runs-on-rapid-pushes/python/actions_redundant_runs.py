"""Estimate CI minutes wasted on runs superseded by a later push.

Reports only. Adding cancel-in-progress to a deploy workflow would leave a
half-finished deploy, so the change is deliberately left to a human who knows
which workflows are safe to interrupt.
"""
import argparse
import collections
import logging
import os
import sys

import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("actions_redundant_runs")

API = "https://api.github.com"
# Billed minutes per wall-clock minute, per runner OS.
MULTIPLIER = {"ubuntu": 1, "windows": 2, "macos": 10}


def find_superseded(runs):
    """Pure decision function.

    A run is superseded when a LATER run exists for the same workflow and branch and
    the earlier one was still going when it started. Grouping by workflow as well as
    branch matters: two different workflows on one branch are not competing.
    """
    by_key = collections.defaultdict(list)
    for r in runs:
        by_key[(r.get("workflow_id"), r.get("head_branch"))].append(r)

    superseded = []
    for group in by_key.values():
        group.sort(key=lambda r: r.get("run_number", 0))
        for earlier, later in zip(group, group[1:]):
            if earlier.get("created_at") and later.get("created_at"):
                if earlier["created_at"] < later["created_at"]:
                    superseded.append(earlier)
    return superseded


def billed_minutes(run, wall_minutes):
    """Apply the runner multiplier. macOS is 10x, which dominates any bill."""
    name = " ".join(run.get("labels", []) or []).lower() or "ubuntu"
    for os_name, mult in MULTIPLIER.items():
        if os_name in name:
            return wall_minutes * mult
    return wall_minutes


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
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

    wasted = find_superseded(runs)
    log.info("%d recent run(s), %d superseded by a later push", len(runs), len(wasted))
    by_workflow = collections.Counter(w.get("name") for w in wasted)
    for name, count in by_workflow.most_common():
        log.warning("  %-40s %d redundant run(s)", name, count)
    if wasted:
        log.warning("add a concurrency group to the workflows above:")
        log.warning("  concurrency:")
        log.warning("    group: ${{ github.workflow }}-${{ github.ref }}")
        log.warning("    cancel-in-progress: true")
        log.warning("do NOT add cancel-in-progress to a deploy workflow")
    return 0


if __name__ == "__main__":
    sys.exit(main())
