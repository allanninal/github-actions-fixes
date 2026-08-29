from actions_permissions_audit import needed_scopes, declared_scopes, gaps

PUSHES = """
jobs:
  release:
    steps:
      - run: git push origin main
"""

PUSHES_WITH_GRANT = """
jobs:
  release:
    permissions:
      contents: write
    steps:
      - run: git push origin main
"""


def test_a_push_needs_contents_write():
    assert "contents: write" in needed_scopes(PUSHES)


def test_a_workflow_that_grants_what_it_needs_is_not_flagged():
    assert gaps(PUSHES_WITH_GRANT) == []


def test_a_workflow_missing_the_grant_is_flagged():
    assert gaps(PUSHES) == ["contents: write"]


def test_declared_scopes_are_read_from_anywhere_in_the_file():
    assert "contents" in declared_scopes(PUSHES_WITH_GRANT)


def test_a_read_only_workflow_needs_nothing():
    assert needed_scopes("jobs:\n  test:\n    steps:\n      - run: pytest") == []
