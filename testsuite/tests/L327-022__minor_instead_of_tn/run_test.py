def test_push(testcase):
    """Try pushing master..."""
    # The revision log of the commit we are trying to push
    # has the word "minor" in it, which used to be a valid
    # substitute for a TN, but this is no longer the case
    # as of 2017-07-28, so the push should now be rejected.
    p = testcase.run("git push origin master".split())
    expected_out = """\
remote: *** The following commit is missing a ticket number inside
remote: *** its revision history.  If the change is sufficiently
remote: *** minor that a ticket number is not meaningful, please use
remote: *** the word "no-tn-check" in place of a ticket number.
remote: ***
remote: *** commit 4076043f3bfa9fb473e1788ba4356c99135fc071
remote: *** Subject: Minor update to file a.
remote: error: hook declined to update refs/heads/master
To ../bare/repo.git
 ! [remote rejected] master -> master (hook declined)
error: failed to push some refs to '../bare/repo.git'
"""

    testcase.assertNotEqual(p.status, 0, p.image)
    testcase.assertRunOutputEqual(p, expected_out)
