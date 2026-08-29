from actions_redundant_runs import find_superseded, billed_minutes


def run(n, wf=1, branch="main", created=None):
    return {"run_number": n, "workflow_id": wf, "head_branch": branch,
            "created_at": created or f"2026-08-28T00:{n:02d}:00Z", "name": f"wf{wf}"}


def test_a_single_run_is_not_superseded():
    assert find_superseded([run(1)]) == []


def test_the_earlier_of_two_runs_is_superseded():
    out = find_superseded([run(1), run(2)])
    assert len(out) == 1 and out[0]["run_number"] == 1


def test_different_workflows_do_not_compete():
    """Two workflows on one branch are both meant to run."""
    assert find_superseded([run(1, wf=1), run(2, wf=2)]) == []


def test_different_branches_do_not_compete():
    assert find_superseded([run(1, branch="a"), run(2, branch="b")]) == []


def test_macos_multiplier_applies():
    r = {"labels": ["macos-latest"]}
    assert billed_minutes(r, 10) == 100


def test_linux_is_billed_one_to_one():
    assert billed_minutes({"labels": ["ubuntu-latest"]}, 10) == 10


def test_unknown_runner_does_not_inflate_the_estimate():
    assert billed_minutes({"labels": []}, 10) == 10
