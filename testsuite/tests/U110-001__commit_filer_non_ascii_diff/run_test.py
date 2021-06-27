# coding=utf-8
from support import *

from email.header import Header
import stat

# The contents of the script to use as a commit-email-formatter hook.
COMMIT_EMAIL_FORMATTER_HOOK = """\
#! /usr/bin/env python
import sys
import json

json.dump({'diff': u'My \\u2192 Email diff \\u2190\\n'}, sys.stdout)
"""


class TestRun(TestCase):
    def test_push_commit_on_master(testcase):
        """Try pushing ia single-file commit.

        The purpose of this testcase is to verify that the git-hooks
        behave as expected when the repository uses a file-commit-cmd
        hook, when the diff contains some non-ascii characters.

        We perform the test with two variations:

            (1) First on branch "master", where the file-commit-cmd
                hook is used, without any other hook being used.

            (2) As a second step, we then install a commit-email-formatter
                hook which returns a custom diff, and try pushing the same
                commit again to branch "with-email-formatter".

        In pratice, this non-ascii character in the diff should have
        no impact on the use of this hook since, as of today, we
        explicitly exclude the diff from the data being sent to
        the filer hook ;-). However, we're adding this testcase
        nonetheless so as to make sure we test this scenario should
        we decide to pas that inforamtion, one day...
        """
        cd("%s/repo" % TEST_DIR)

        # First, update the git-hooks configuration to install
        # the script we want to use as our file-commit-cmd.

        p = testcase.run(["git", "fetch", "origin", "refs/meta/config"])
        testcase.assertEqual(p.status, 0, p.image)

        p = testcase.run(["git", "checkout", "FETCH_HEAD"])
        testcase.assertEqual(p.status, 0, p.image)

        p = testcase.run(
            [
                "git",
                "config",
                "--file",
                "project.config",
                "hooks.file-commit-cmd",
                os.path.join(TEST_DIR, "commit-filer"),
            ]
        )
        testcase.assertEqual(p.status, 0, p.image)

        p = testcase.run(
            ["git", "commit", "-m", "Add hooks.commit-filer", "project.config"]
        )
        testcase.assertEqual(p.status, 0, p.image)

        p = testcase.run(["git", "push", "origin", "HEAD:refs/meta/config"])
        testcase.assertEqual(p.status, 0, p.image)
        # Check the last line that git printed, and verify that we have
        # another piece of evidence that the change was succesfully pushed.
        assert "HEAD -> refs/meta/config" in p.out.splitlines()[-1], p.image

        # Return our current HEAD to branch "master". Not critical for
        # our testing, but it helps the testcase be closer to the more
        # typical scenarios.
        p = testcase.run(["git", "checkout", "master"])
        testcase.assertEqual(p.status, 0, p.image)

        # Push master to the `origin' remote.  The delta should be one
        # commit with one file being modified.
        #
        # While doing so, we also force the email-sending verbosity
        # to "full". While we do not really need to verify the contents
        # of the email being sent in the context of this testcase,
        # having the full email contents allows us to verify the contents
        # of the commit's "diff", and make sure there are indeed some
        # non-ascii caracters in it.  Note that maximum email-sending
        # verbosity is currently the default, so forcing it is not
        # necessary either, but doing so reduces the chance that someone
        # (probably me) accidently reduces the verbosity without
        # at least reviewing all the considerations that went into
        # that decision.

        testcase.change_email_sending_verbosity(full_verbosity=True)

        p = testcase.run("git push origin master".split())
        expected_out = """\
remote: DEBUG: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 8bit
remote: Content-Type: text/plain; charset="utf-8"
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Bcc: filer@example.com
remote: Subject: [repo] Updated a.
remote: X-Act-Checkin: repo
remote: X-Git-Author: Joel Brobecker <brobecker@adacore.com>
remote: X-Git-Refname: refs/heads/master
remote: X-Git-Oldrev: d065089ff184d97934c010ccd0e7e8ed94cb7165
remote: X-Git-Newrev: 764f229405b41668b88611ae7b2fd9669e005843
remote:
remote: commit 764f229405b41668b88611ae7b2fd9669e005843
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Fri Apr 27 13:08:29 2012 -0700
remote:
remote:     Updated a.
remote:
remote:     Just added a little bit of text inside file a.
remote:     Thought about doing something else, but not really necessary.
remote:
remote: Diff:
remote: ---
remote:  a | 4 +++-
remote:  1 file changed, 3 insertions(+), 1 deletion(-)
remote:
remote: diff --git a/a b/a
remote: index 01d0f12..7b20acf 100644
remote: --- a/a
remote: +++ b/a
remote: @@ -1,3 +1,5 @@
remote:  Some file.
remote: -Second line.
remote: +Second line, → in the middle ←.
remote: +In the middle too!
remote:  Third line.
remote: +
remote: -----[ commit-filer start ]-----
remote: -----[ commit-filer body ]-----
remote: The master branch has been updated by Test Suite <testsuite@adacore.com>:
remote:
remote: commit 764f229405b41668b88611ae7b2fd9669e005843
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Fri Apr 27 13:08:29 2012 -0700
remote:
remote:     Updated a.
remote:
remote:     Just added a little bit of text inside file a.
remote:     Thought about doing something else, but not really necessary.
remote: -----[ commit-filer end ]-----
remote:
To ../bare/repo.git
   d065089..764f229  master -> master
"""

        testcase.assertEqual(p.status, 0, p.image)
        testcase.assertRunOutputEqual(p, expected_out)

        # Second part of the testcase: Create and then install a simple
        # commit-email-formatter hook, which changes email bodies and
        # uses non-ascii characters.

        COMMIT_EMAIL_FORMATTER_FILENAME = os.path.join(
            TEST_DIR, "commit-email-formatter.py"
        )
        with open(COMMIT_EMAIL_FORMATTER_FILENAME, "w") as f:
            f.write(COMMIT_EMAIL_FORMATTER_HOOK)
        os.chmod(
            COMMIT_EMAIL_FORMATTER_FILENAME, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR
        )

        p = testcase.run(["git", "fetch", "origin", "refs/meta/config"])
        testcase.assertEqual(p.status, 0, p.image)

        p = testcase.run(["git", "checkout", "FETCH_HEAD"])
        testcase.assertEqual(p.status, 0, p.image)

        p = testcase.run(
            [
                "git",
                "config",
                "--file",
                "project.config",
                "hooks.commit-email-formatter",
                COMMIT_EMAIL_FORMATTER_FILENAME,
            ]
        )
        testcase.assertEqual(p.status, 0, p.image)

        p = testcase.run(
            [
                "git",
                "commit",
                "-m",
                "Add hooks.commit-email-formatter",
                "project.config",
            ]
        )
        testcase.assertEqual(p.status, 0, p.image)

        p = testcase.run(["git", "push", "origin", "HEAD:refs/meta/config"])
        testcase.assertEqual(p.status, 0, p.image)
        # Check the last line that git printed, and verify that we have
        # another piece of evidence that the change was succesfully pushed.
        assert "HEAD -> refs/meta/config" in p.out.splitlines()[-1], p.image

        # Return our current HEAD to branch "master". Not critical for
        # our testing, but it helps the testcase be closer to the more
        # typical scenarios.
        p = testcase.run(["git", "checkout", "master"])
        testcase.assertEqual(p.status, 0, p.image)

        p = testcase.run("git push origin master:with-email-formatter".split())
        expected_out = """\
remote: DEBUG: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 8bit
remote: Content-Type: text/plain; charset="utf-8"
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Bcc: filer@example.com
remote: Subject: [repo/with-email-formatter] Updated a.
remote: X-Act-Checkin: repo
remote: X-Git-Author: Joel Brobecker <brobecker@adacore.com>
remote: X-Git-Refname: refs/heads/with-email-formatter
remote: X-Git-Oldrev: d065089ff184d97934c010ccd0e7e8ed94cb7165
remote: X-Git-Newrev: 764f229405b41668b88611ae7b2fd9669e005843
remote:
remote: commit 764f229405b41668b88611ae7b2fd9669e005843
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Fri Apr 27 13:08:29 2012 -0700
remote:
remote:     Updated a.
remote:
remote:     Just added a little bit of text inside file a.
remote:     Thought about doing something else, but not really necessary.
remote:
remote: Diff:
remote: My → Email diff ←
remote:
remote: -----[ commit-filer start ]-----
remote: -----[ commit-filer body ]-----
remote: The with-email-formatter branch has been updated by Test Suite <testsuite@adacore.com>:
remote:
remote: commit 764f229405b41668b88611ae7b2fd9669e005843
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Fri Apr 27 13:08:29 2012 -0700
remote:
remote:     Updated a.
remote:
remote:     Just added a little bit of text inside file a.
remote:     Thought about doing something else, but not really necessary.
remote: -----[ commit-filer end ]-----
remote:
To ../bare/repo.git
   d065089..764f229  master -> with-email-formatter
"""

        testcase.assertEqual(p.status, 0, p.image)
        testcase.assertRunOutputEqual(p, expected_out)


if __name__ == "__main__":
    runtests()
