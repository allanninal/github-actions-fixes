"""Diagnose why an Actions cache never restores.

A rate limit, an unstable key and a fork PR all produce the same log line: cache
miss. This separates them by looking at what is actually stored rather than at the
log, which cannot tell the difference.
"""
import argparse
import collections
import logging
import os
import re
import sys

import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("actions_cache_audit")

API = "https://api.github.com"


def prefix_of(key):
    """Everything before the final hash segment, which is what should be reused."""
    return re.sub(r"-[0-9a-f]{8,}$", "", key)


def unstable_keys(caches, min_entries=5):
    """Pure decision function.

    An unstable key writes a new entry every run and reads none, so the signature is
    many entries sharing a prefix. That fills the quota and evicts the entries you
    actually wanted, which makes it worse than a plain miss.
    """
    groups = collections.defaultdict(list)
    for c in caches:
        groups[prefix_of(c.get("key", ""))].append(c)
    return {p: entries for p, entries in groups.items() if len(entries) >= min_entries}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    args = ap.parse_args()

    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        log.error("set GITHUB_TOKEN")
        return 2
    headers = {"Authorization": f"Bearer {token}",
               "Accept": "application/vnd.github+json"}

    r = requests.get(f"{API}/repos/{args.repo}/actions/caches",
                     headers=headers, params={"per_page": 100}, timeout=30)
    r.raise_for_status()
    body = r.json()
    caches = body.get("actions_caches", [])

    total_gb = sum(c.get("size_in_bytes", 0) for c in caches) / 1_073_741_824
    log.info("%d cache entr(ies), %.2f GB total", len(caches), total_gb)

    suspect = unstable_keys(caches)
    for prefix, entries in sorted(suspect.items(), key=lambda x: -len(x[1])):
        size = sum(e.get("size_in_bytes", 0) for e in entries) / 1_073_741_824
        log.warning("UNSTABLE KEY  %-45s %3d entries, %.2f GB",
                    prefix[:45], len(entries), size)
    if suspect:
        log.warning("a key that changes every run writes a new entry and reads none. "
                    "Hash the lockfile, not the run id or a timestamp.")
    else:
        log.info("no unstable-key pattern; if restores still miss, check whether the "
                 "run came from a fork (forks cannot write cache entries) or whether "
                 "the cache service rate limited -- both are logged as a plain miss")
    return 0


if __name__ == "__main__":
    sys.exit(main())
