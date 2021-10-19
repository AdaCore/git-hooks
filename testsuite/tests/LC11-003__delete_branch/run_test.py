def test_delete_branch(testcase):
    """Try deleting a branch on the remote."""
    p = testcase.run("git push origin :old-branch".split())
    expected_out = """\
remote: DEBUG: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: Content-Type: text/plain; charset="utf-8"
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Subject: [repo] Deleted branch 'old-branch'
remote: X-Act-Checkin: repo
remote: X-Git-Author: Test Suite <testsuite@adacore.com>
remote: X-Git-Refname: refs/heads/old-branch
remote: X-Git-Oldrev: cc8d2c2637bda27f0bc2125181dd2f8534d16222
remote: X-Git-Newrev: 0000000000000000000000000000000000000000
remote:
remote: The branch 'old-branch' was deleted.
remote: It previously pointed to:
remote:
remote:  cc8d2c2... Modify `c', delete `b'.
To ../bare/repo.git
 - [deleted]         old-branch
"""
    testcase.assertEqual(p.status, 0, p.image)
    testcase.assertRunOutputEqual(p, expected_out)

    # Same as above: Delete a branch, but passing the branch's
    # full reference name to the push command, instead of using
    # the (short) branch name (i.e 'refs/heads/other-old-branch'
    # instead of just 'other-old-branch').

    p = testcase.run("git push origin :refs/heads/other-old-branch".split())
    expected_out = """\
remote: DEBUG: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: Content-Type: text/plain; charset="utf-8"
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Subject: [repo] Deleted branch 'other-old-branch'
remote: X-Act-Checkin: repo
remote: X-Git-Author: Test Suite <testsuite@adacore.com>
remote: X-Git-Refname: refs/heads/other-old-branch
remote: X-Git-Oldrev: cc8d2c2637bda27f0bc2125181dd2f8534d16222
remote: X-Git-Newrev: 0000000000000000000000000000000000000000
remote:
remote: The branch 'other-old-branch' was deleted.
remote: It previously pointed to:
remote:
remote:  cc8d2c2... Modify `c', delete `b'.
To ../bare/repo.git
 - [deleted]         other-old-branch
"""
    testcase.assertEqual(p.status, 0, p.image)
    testcase.assertRunOutputEqual(p, expected_out)
