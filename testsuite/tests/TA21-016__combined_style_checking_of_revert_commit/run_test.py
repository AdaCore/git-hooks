def test_push_commit_on_master(testcase):
    """Push one new commit which is also a revert

    The purpose of this test is to verify that users are able to
    push changes in the following very specific scenario:
        - The repository's was configured with combined-style-checking
          enabled;
        - The user is pushing one single new commit;
        - The commit happens to be a revert commits, which means
          that this commit isn't included in the list of commits
          to check.
    What the above combination leads to is a list of "commits to check"
    which is empty, which means we can't really take the last commit
    of that list. Trying to do so in this case would lead to a crash
    due to an indext out of range.
    """
    # For this testcase, the contents of the emails being sent
    # is not important, so reduce their verbosity.
    testcase.change_email_sending_verbosity(full_verbosity=False)

    # Push master to the `origin' remote. The commit should be accepted,
    # with no commit being checked at all -- since the style_checker.py
    # script in this testcase generates a trace at every call, one piece
    # of evidence that style checking is not being done is lack of such
    # traces in the push's output).
    p = testcase.run("git push origin master".split())
    expected_out = """\
remote: DEBUG: Sending email: [repo] Revert "Rename "world" into "there""...
To ../bare/repo.git
   a2d7a20..73b1b7d  master -> master
"""

    assert p.status == 0, p.image
    testcase.assertRunOutputEqual(p, expected_out)
