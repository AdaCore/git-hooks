from support import *


class TestRun(TestCase):
    def test_push_commits(testcase):
        """See comments below."""
        # Branch master is 2 commits ahead of the remote. But we push
        # the commits one by one, because we want to verify that the
        # push is successful with the first commit, but trips the
        # precommit-check on the second.

        # Push the first commit. The RH should normally fail the RH
        # style check, but we deactivated it for all branches, and
        # thus the push is expected to pass.
        p = testcase.run(
            "git push origin bf43717d61e2a67cf9b3d040e9c40d6041a8444d:master".split()
        )
        expected_out = """\
remote: DEBUG: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: Content-Type: text/plain; charset="utf-8"
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Bcc: filer@example.com
remote: Subject: [repo] Edit file a. Non-empty second line in RH.
remote: X-Act-Checkin: repo
remote: X-Git-Author: Joel Brobecker <brobecker@adacore.com>
remote: X-Git-Refname: refs/heads/master
remote: X-Git-Oldrev: 8fcbf01c27de0502fe9876fe898c24c628802437
remote: X-Git-Newrev: bf43717d61e2a67cf9b3d040e9c40d6041a8444d
remote:
remote: commit bf43717d61e2a67cf9b3d040e9c40d6041a8444d
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Wed Apr 17 09:49:03 2013 +0200
remote:
remote:     Edit file a.
remote:     Non-empty second line in RH.
remote:
remote:     More info goes here.
remote:
remote: Diff:
remote: ---
remote:  a | 1 +
remote:  1 file changed, 1 insertion(+)
remote:
remote: diff --git a/a b/a
remote: index ebb7782..c1dd540 100644
remote: --- a/a
remote: +++ b/a
remote: @@ -1,2 +1,3 @@
remote:  First file.
remote:  With Nothing in it.
remote: +Actually, almost nothing.
To ../bare/repo.git
   8fcbf01..bf43717  bf43717d61e2a67cf9b3d040e9c40d6041a8444d -> master
"""

        testcase.assertEqual(p.status, 0, p.image)
        testcase.assertRunOutputEqual(p, expected_out)

        # Push the second commit. This time, verify that having the RH
        # style check disabled does not prevent the precommit-check
        # checks from being applied. cvs_check has been setup to reject
        # the update, and thus cause the push to fail.
        p = testcase.run("git push origin master".split())
        expected_out = """\
remote: *** pre-commit check failed for commit: e4dede9e45c3b88fd57aab5edbce1cd4d1da0850
remote: *** cvs_check: style check violation in b
remote: error: hook declined to update refs/heads/master
To ../bare/repo.git
 ! [remote rejected] master -> master (hook declined)
error: failed to push some refs to '../bare/repo.git'
"""

        testcase.assertNotEqual(p.status, 0, p.image)
        testcase.assertRunOutputEqual(p, expected_out)


if __name__ == "__main__":
    runtests()
