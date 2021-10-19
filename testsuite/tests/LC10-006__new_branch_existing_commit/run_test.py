def test_push_new_branch(testcase):
    """Try pushing a new branch which creates no new commit at all."""
    # Push master to the `origin' remote.  The delta should be one
    # commit with one file being modified.
    p = testcase.run("git push origin my-topic".split())
    expected_out = """\
remote: DEBUG: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: Content-Type: text/plain; charset="utf-8"
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Subject: [repo] Created branch 'my-topic'
remote: X-Act-Checkin: repo
remote: X-Git-Author: Test Suite <testsuite@adacore.com>
remote: X-Git-Refname: refs/heads/my-topic
remote: X-Git-Oldrev: 0000000000000000000000000000000000000000
remote: X-Git-Newrev: d065089ff184d97934c010ccd0e7e8ed94cb7165
remote:
remote: The branch 'my-topic' was created pointing to:
remote:
remote:  d065089... New file: a.
To ../bare/repo.git
 * [new branch]      my-topic -> my-topic
"""

    testcase.assertEqual(p.status, 0, p.image)
    testcase.assertRunOutputEqual(p, expected_out)
