from fork_pr_secret_audit import is_fork_run


def run(event="pull_request", head="contributor/proj", base="owner/proj"):
    return {"event": event,
            "head_repository": {"full_name": head},
            "repository": {"full_name": base}}


def test_fork_pr_is_detected():
    assert is_fork_run(run()) is True


def test_same_repo_branch_pr_keeps_its_secrets():
    """Also a pull_request event, but from a branch. Secrets ARE available."""
    assert is_fork_run(run(head="owner/proj")) is False


def test_push_events_are_not_affected():
    assert is_fork_run(run(event="push")) is False


def test_missing_head_repository_is_not_assumed_to_be_a_fork():
    r = run()
    r["head_repository"] = None
    assert is_fork_run(r) is False
