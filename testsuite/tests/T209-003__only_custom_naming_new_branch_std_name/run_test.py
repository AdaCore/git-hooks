def test_create_branch_with_standard_name(testcase):
    """Create a new branch with a standard reference name."""
    # First, try pushing with a branch name which is recognized
    # by the repository's branch namespace.

    p = testcase.run("git push origin master:branches/release-x".split())
    expected_out = """\
remote: DEBUG: Content-Type: text/plain; charset="utf-8"
remote: MIME-Version: 1.0
remote: Content-Transfer-Encoding: quoted-printable
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Subject: [repo] Created branch 'branches/release-x'
remote: X-Act-Checkin: repo
remote: X-Git-Author: Test Suite <testsuite@adacore.com>
remote: X-Git-Refname: refs/heads/branches/release-x
remote: X-Git-Oldrev: 0000000000000000000000000000000000000000
remote: X-Git-Newrev: d065089ff184d97934c010ccd0e7e8ed94cb7165
remote:
remote: The branch 'branches/release-x' was created pointing to:
remote:
remote:  d065089... New file: a.
To ../bare/repo.git
 * [new branch]      master -> branches/release-x
"""

    testcase.assertEqual(p.status, 0, p.image)
    testcase.assertRunOutputEqual(p, expected_out)

    # Next, try pushing with a branch name which is not recognized
    # by the repository's branch namespace. E.g., try creating
    # a "release-y" branch directly in "refs/heads".

    p = testcase.run("git push origin master:release-y".split())
    expected_out = """\
remote: *** Unable to determine the type of reference for: refs/heads/release-y
remote: ***
remote: *** This repository currently recognizes the following types
remote: *** of references:
remote: ***
remote: ***  * Branches:
remote: ***       refs/heads/master
remote: ***       refs/heads/branches/.*
remote: ***       refs/vendor/.*
remote: ***       refs/user/.*
remote: ***
remote: ***  * Git Notes:
remote: ***       refs/notes/.*
remote: ***
remote: ***  * Tags:
remote: ***       refs/tags/.*
remote: error: hook declined to update refs/heads/release-y
To ../bare/repo.git
 ! [remote rejected] master -> release-y (hook declined)
error: failed to push some refs to '../bare/repo.git'
"""

    testcase.assertNotEqual(p.status, 0, p.image)
    testcase.assertRunOutputEqual(p, expected_out)
