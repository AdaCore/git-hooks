from support import *


class TestRun(TestCase):
    def test_push_commit_on_master(testcase):
        """Try pushing one single-file commit on master.

        This is just to verify that revision-log checks are enabled,
        and in particular that we get an error if the TN is missing.
        That way, we know that our repository is correctly configured
        in terms of requiring TNs in the revision log and should
        normally reject commits that don't follow this rule.
        """
        # Push master to the `origin' remote.  The delta should be one
        # commit with one file being modified.
        p = testcase.run("git push origin master".split())
        expected_out = """\
remote: *** The following commit is missing a ticket number inside
remote: *** its revision history.  If the change is sufficiently
remote: *** minor that a ticket number is not meaningful, please use
remote: *** the word "no-tn-check" in place of a ticket number.
remote: ***
remote: *** commit a60540361d47901d3fe254271779f380d94645f7
remote: *** Subject: Updated a.
remote: error: hook declined to update refs/heads/master
To ../bare/repo.git
 ! [remote rejected] master -> master (hook declined)
error: failed to push some refs to '../bare/repo.git'
"""

        testcase.assertNotEqual(p.status, 0, p.image)
        testcase.assertRunOutputEqual(p, expected_out)

    def test_push_commit_on_revert(testcase):
        """Try pushing one single-file commit on revert.

        This verifies that all checks are disabled when pushing
        a commit which has been created using "git revert". In
        particular, this commit violates a number of requirements
        in the revision log. And the cvs_check.py script is also
        set up to always return an error, so this will allow us
        to verify that no file is style-checked.
        """
        # Push master to the `origin' remote.  The delta should be one
        # commit with one file being modified.
        p = testcase.run("git push origin revert".split())
        expected_out = """\
remote: DEBUG: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: Content-Type: text/plain; charset="utf-8"
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Bcc: filer@example.com
remote: Subject: [repo/revert] Revert "New file: a."
remote: X-Act-Checkin: repo
remote: X-Git-Author: Joel Brobecker <brobecker@adacore.com>
remote: X-Git-Refname: refs/heads/revert
remote: X-Git-Oldrev: d065089ff184d97934c010ccd0e7e8ed94cb7165
remote: X-Git-Newrev: d669d669fcbdeab1eedf9756ce1ef5a62c4f97db
remote:
remote: commit d669d669fcbdeab1eedf9756ce1ef5a62c4f97db
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Thu Nov 9 06:05:21 2017 -0800
remote:
remote:     Revert "New file: a."
remote:
remote:     This reverts commit d065089ff184d97934c010ccd0e7e8ed94cb7165.
remote:
remote:     No TN included as we want to verify that revert commits don't go through any check of any kind (including lines too long like this one).
remote:
remote: Diff:
remote: ---
remote:  a | 3 ---
remote:  1 file changed, 3 deletions(-)
remote:
remote: diff --git a/a b/a
remote: deleted file mode 100644
remote: index 01d0f12..0000000
remote: --- a/a
remote: +++ /dev/null
remote: @@ -1,3 +0,0 @@
remote: -Some file.
remote: -Second line.
remote: -Third line.
To ../bare/repo.git
   d065089..d669d66  revert -> revert
"""

        testcase.assertEqual(p.status, 0, p.image)
        testcase.assertRunOutputEqual(p, expected_out)


if __name__ == "__main__":
    runtests()
