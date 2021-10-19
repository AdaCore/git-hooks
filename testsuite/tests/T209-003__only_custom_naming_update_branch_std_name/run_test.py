def test_update_branch_in_standard_namespace(testcase):
    """Create a new branch with a standard reference name."""
    # First, try pushing with a branch name which is recognized
    # by the repository's branch namespace.

    p = testcase.run("git push origin master".split())
    expected_out = """\
remote: *** cvs_check: `repo' < `a'
remote: DEBUG: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: Content-Type: text/plain; charset="utf-8"
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Bcc: filer@example.com
remote: Subject: [repo] Update a
remote: X-Act-Checkin: repo
remote: X-Git-Author: Joel Brobecker <brobecker@adacore.com>
remote: X-Git-Refname: refs/heads/master
remote: X-Git-Oldrev: d065089ff184d97934c010ccd0e7e8ed94cb7165
remote: X-Git-Newrev: 5f5c774e41a5731382823de67459efbaf69e1e71
remote:
remote: commit 5f5c774e41a5731382823de67459efbaf69e1e71
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Sun Apr 12 17:50:32 2020 -0700
remote:
remote:     Update a
remote:
remote: Diff:
remote: ---
remote:  a | 1 +
remote:  1 file changed, 1 insertion(+)
remote:
remote: diff --git a/a b/a
remote: index 01d0f12..fb08cf4 100644
remote: --- a/a
remote: +++ b/a
remote: @@ -1,3 +1,4 @@
remote:  Some file.
remote:  Second line.
remote:  Third line.
remote: +The end.
To ../bare/repo.git
   d065089..5f5c774  master -> master
"""

    testcase.assertEqual(p.status, 0, p.image)
    testcase.assertRunOutputEqual(p, expected_out)

    # Next, try pushing with a branch name which is not recognized
    # by the repository's branch namespace. E.g., try updating
    # the branch called "my-topic", which exists in the remote
    # repository, but is not recognized as a branch reference
    # (could be a legacy branch).

    p = testcase.run("git push origin my-topic".split())
    expected_out = """\
remote: *** Unable to determine the type of reference for: refs/heads/my-topic
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
remote: error: hook declined to update refs/heads/my-topic
To ../bare/repo.git
 ! [remote rejected] my-topic -> my-topic (hook declined)
error: failed to push some refs to '../bare/repo.git'
"""

    testcase.assertNotEqual(p.status, 0, p.image)
    testcase.assertRunOutputEqual(p, expected_out)
