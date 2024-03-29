def test_push_commit_to_ignored_ref(testcase):
    """Try pushing master to a reference that's configured to be ignored."""

    # Simulate one action that Gerrit does, which is to create
    # some "Special references" which are internal to its operations.
    # For instance, "refs/users/<last-2-digits-of-userid>/<userid>".
    #
    # The purpose of this testcase is to verify that the push is completely
    # ignored by the git-hooks (in particular no check, no style check, and
    # no emails).

    p = testcase.run("git push origin master:refs/users/01/104201".split())
    expected_out = testcase.massage_git_output(
        """\
To ../bare/repo.git
 * [new reference]   master -> refs/users/01/104201
"""
    )

    testcase.assertEqual(p.status, 0, p.image)
    testcase.assertRunOutputEqual(p, expected_out)
