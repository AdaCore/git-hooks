# coding=utf-8
import os
import stat

# The contents of the script to use as a commit-email-formatter hook.
COMMIT_EMAIL_FORMATTER_HOOK = """\
#! /usr/bin/env python
import sys
import json

json.dump({'email_body': u'New \\u2192 Email body \\u2190\\n'}, sys.stdout)
"""


def test_push_commit_on_master(testcase):
    """Try pushing a single-file commit.

    The purpose of this testcase is to verify that the git-hooks
    behave as expected when the repository uses a file-commit-cmd
    hook, when the commit subject contains some non-ascii characters.

    We perform the test with two variations:

        (1) First on branch "master", where the file-commit-cmd
            hook is used, without any other hook being used.

        (2) As a second step, we then install a commit-email-formatter
            hook which returns a custom email body, and try pushing
            the same commit again to branch "with-email-formatter".
    """
    # First, update the git-hooks configuration to install
    # the script we want to use as our file-commit-cmd.

    testcase.update_git_hooks_config(
        [
            (
                "hooks.file-commit-cmd",
                os.path.join(testcase.work_dir, "commit-filer"),
            ),
        ]
    )

    # Push master to the `origin' remote.  The delta should be one
    # commit with one file being modified.

    p = testcase.run("git push origin master".split())
    expected_out = """\
remote: DEBUG: Content-Type: text/plain; charset="utf-8"
remote: MIME-Version: 1.0
remote: Content-Transfer-Encoding: quoted-printable
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Bcc: filer@example.com
remote: Subject: [repo] Update file a
remote: X-Act-Checkin: repo
remote: X-Git-Author: Joel Brobecker <brobecker@adacore.com>
remote: X-Git-Refname: refs/heads/master
remote: X-Git-Oldrev: d065089ff184d97934c010ccd0e7e8ed94cb7165
remote: X-Git-Newrev: 05279efab1c73898501f12093747de76785a4fd0
remote:
remote: commit 05279efab1c73898501f12093747de76785a4fd0
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Fri Apr 27 13:08:29 2012 -0700
remote:
remote:     Update file a
remote:
remote:     My → Commit Body ←
remote:
remote: Diff:
remote: ---
remote:  a | 4 +++-
remote:  1 file changed, 3 insertions(+), 1 deletion(-)
remote:
remote: diff --git a/a b/a
remote: index 01d0f12..a90d851 100644
remote: --- a/a
remote: +++ b/a
remote: @@ -1,3 +1,5 @@
remote:  Some file.
remote: -Second line.
remote: +Second line, in the middle.
remote: +In the middle too!
remote:  Third line.
remote: +
remote: -----[ commit-filer start ]-----
remote: -----[ commit-filer body ]-----
remote: The master branch has been updated by Test Suite <testsuite@adacore.com>:
remote:
remote: commit 05279efab1c73898501f12093747de76785a4fd0
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Fri Apr 27 13:08:29 2012 -0700
remote:
remote:     Update file a
remote:
remote:     My → Commit Body ←
remote: -----[ commit-filer end ]-----
remote:
To ../bare/repo.git
   d065089..05279ef  master -> master
"""

    testcase.assertEqual(p.status, 0, p.image)
    testcase.assertRunOutputEqual(p, expected_out)

    # Second part of the testcase: Create and then install a simple
    # commit-email-formatter hook, which changes email bodies and
    # uses non-ascii characters.

    COMMIT_EMAIL_FORMATTER_FILENAME = os.path.join(
        testcase.work_dir, "commit-email-formatter.py"
    )
    with open(COMMIT_EMAIL_FORMATTER_FILENAME, "w") as f:
        f.write(COMMIT_EMAIL_FORMATTER_HOOK)
    os.chmod(
        COMMIT_EMAIL_FORMATTER_FILENAME, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR
    )

    testcase.update_git_hooks_config(
        [("hooks.commit-email-formatter", COMMIT_EMAIL_FORMATTER_FILENAME)]
    )

    p = testcase.run("git push origin master:with-email-formatter".split())
    expected_out = """\
remote: DEBUG: Content-Type: text/plain; charset="utf-8"
remote: MIME-Version: 1.0
remote: Content-Transfer-Encoding: quoted-printable
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Bcc: filer@example.com
remote: Subject: [repo/with-email-formatter] Update file a
remote: X-Act-Checkin: repo
remote: X-Git-Author: Joel Brobecker <brobecker@adacore.com>
remote: X-Git-Refname: refs/heads/with-email-formatter
remote: X-Git-Oldrev: d065089ff184d97934c010ccd0e7e8ed94cb7165
remote: X-Git-Newrev: 05279efab1c73898501f12093747de76785a4fd0
remote:
remote: New → Email body ←
remote:
remote: Diff:
remote: ---
remote:  a | 4 +++-
remote:  1 file changed, 3 insertions(+), 1 deletion(-)
remote:
remote: diff --git a/a b/a
remote: index 01d0f12..a90d851 100644
remote: --- a/a
remote: +++ b/a
remote: @@ -1,3 +1,5 @@
remote:  Some file.
remote: -Second line.
remote: +Second line, in the middle.
remote: +In the middle too!
remote:  Third line.
remote: +
remote: -----[ commit-filer start ]-----
remote: -----[ commit-filer body ]-----
remote: The with-email-formatter branch has been updated by Test Suite <testsuite@adacore.com>:
remote:
remote: New → Email body ←
remote: -----[ commit-filer end ]-----
remote:
To ../bare/repo.git
   d065089..05279ef  master -> with-email-formatter
"""

    testcase.assertEqual(p.status, 0, p.image)
    testcase.assertRunOutputEqual(p, expected_out)
