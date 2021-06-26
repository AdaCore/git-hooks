# coding=utf-8
from support import *

from email.header import Header
import stat

# The contents of the script to use as a commit-email-formatter hook.
COMMIT_EMAIL_FORMATTER_HOOK = """\
#! /usr/bin/env python
import sys
import json

json.dump({'email_subject': u'New \\u2192 Email Subject \\u2190'}, sys.stdout)
"""


class TestRun(TestCase):
    def test_push_commit_on_master(testcase):
        """Try pushing a single-file commit.

        The purpose of this testcase is to verify that the git-hooks
        behave as expected when the repository uses a file-commit-cmd
        hook, when the commit subject contains some non-ascii characters.

        We perform the test with two variations:

            (1) First on branch "master", where the file-commit-cmd
                hook is used, without any other hook being used.

            (2) As a second step, we then install a commit-email-formatter
                hook which returns a custom email subject, and try pushing
                the same commit again to branch "with-email-formatter".

        In pratice, this non-ascii character in the subject should have
        no impact on the use of this hook since, as of today, the only
        data we pass to the filer hooks is the commit email's body ;-).
        However, we're adding this testcase nonetheless so as to make sure
        we test this scenario should we decide to pas that inforamtion,
        one day...
        """
        cd ('%s/repo' % TEST_DIR)

        # First, update the git-hooks configuration to install
        # the script we want to use as our commit-email-formatter.

        p = testcase.run(['git', 'fetch', 'origin', 'refs/meta/config'])
        testcase.assertEqual(p.status, 0, p.image)

        p = testcase.run(['git', 'checkout', 'FETCH_HEAD'])
        testcase.assertEqual(p.status, 0, p.image)

        p = testcase.run(['git', 'config', '--file', 'project.config',
                 'hooks.file-commit-cmd',
                 os.path.join(TEST_DIR, 'commit-filer')])
        testcase.assertEqual(p.status, 0, p.image)

        p = testcase.run(['git', 'commit', '-m', 'Add hooks.file-commit-cmd',
                 'project.config'])
        testcase.assertEqual(p.status, 0, p.image)

        p = testcase.run(['git', 'push', 'origin', 'HEAD:refs/meta/config'])
        testcase.assertEqual(p.status, 0, p.image)
        # Check the last line that git printed, and verify that we have
        # another piece of evidence that the change was succesfully pushed.
        assert 'HEAD -> refs/meta/config' in p.out.splitlines()[-1], p.image

        # Return our current HEAD to branch "master". Not critical for
        # our testing, but it helps the testcase be closer to the more
        # typical scenarios.
        p = testcase.run(['git', 'checkout', 'master'])
        testcase.assertEqual(p.status, 0, p.image)

        # Push master to the `origin' remote.  The delta should be one
        # commit with one file being modified.

        # The subject of the email we expect to be sent during the push.
        # As we can see, this subject has some non-ascii characters in it...
        COMMIT_EMAIL_SUBJECT = u"[repo] My \u2192 Commit Subject \u2190"

        # ... As a result of which, we expect that subject to be encoded
        # prior to transmission.
        ENCODED_COMMIT_EMAIL_SUBJECT = Header(
            COMMIT_EMAIL_SUBJECT,
            "utf-8",
        ).encode()

        p = testcase.run('git push origin master'.split())
        expected_out = """\
remote: DEBUG: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 8bit
remote: Content-Type: text/plain; charset="utf-8"
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Bcc: filer@example.com
remote: Subject: {ENCODED_COMMIT_EMAIL_SUBJECT}
remote: X-Act-Checkin: repo
remote: X-Git-Author: Joel Brobecker <brobecker@adacore.com>
remote: X-Git-Refname: refs/heads/master
remote: X-Git-Oldrev: d065089ff184d97934c010ccd0e7e8ed94cb7165
remote: X-Git-Newrev: abdeb3a46e1daba5b7ff43c43e34b748fbd437db
remote:
remote: commit abdeb3a46e1daba5b7ff43c43e34b748fbd437db
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Fri Apr 27 13:08:29 2012 -0700
remote:
remote:     My → Commit Subject ←
remote:
remote:     Just added a little bit of text inside file a.
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
remote: commit abdeb3a46e1daba5b7ff43c43e34b748fbd437db
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Fri Apr 27 13:08:29 2012 -0700
remote:
remote:     My → Commit Subject ←
remote:
remote:     Just added a little bit of text inside file a.
remote: -----[ commit-filer end ]-----
remote:
To ../bare/repo.git
   d065089..abdeb3a  master -> master
""".format(ENCODED_COMMIT_EMAIL_SUBJECT=ENCODED_COMMIT_EMAIL_SUBJECT)

        testcase.assertEqual(p.status, 0, p.image)
        testcase.assertRunOutputEqual(p, expected_out)

        # Second part of the testcase: Create and then install a simple
        # commit-email-formatter hook, which changes email bodies and
        # uses non-ascii characters.

        COMMIT_EMAIL_FORMATTER_FILENAME = os.path.join(
            TEST_DIR, "commit-email-formatter.py")
        with open(COMMIT_EMAIL_FORMATTER_FILENAME, "w") as f:
            f.write(COMMIT_EMAIL_FORMATTER_HOOK)
        os.chmod(COMMIT_EMAIL_FORMATTER_FILENAME,
                 stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)

        p = testcase.run(['git', 'fetch', 'origin', 'refs/meta/config'])
        testcase.assertEqual(p.status, 0, p.image)

        p = testcase.run(['git', 'checkout', 'FETCH_HEAD'])
        testcase.assertEqual(p.status, 0, p.image)

        p = testcase.run(['git', 'config', '--file', 'project.config',
                 'hooks.commit-email-formatter',
                 COMMIT_EMAIL_FORMATTER_FILENAME])
        testcase.assertEqual(p.status, 0, p.image)

        p = testcase.run(['git', 'commit', '-m', 'Add hooks.commit-email-formatter',
                 'project.config'])
        testcase.assertEqual(p.status, 0, p.image)

        p = testcase.run(['git', 'push', 'origin', 'HEAD:refs/meta/config'])
        testcase.assertEqual(p.status, 0, p.image)
        # Check the last line that git printed, and verify that we have
        # another piece of evidence that the change was succesfully pushed.
        assert 'HEAD -> refs/meta/config' in p.out.splitlines()[-1], p.image

        # Return our current HEAD to branch "master". Not critical for
        # our testing, but it helps the testcase be closer to the more
        # typical scenarios.
        p = testcase.run(['git', 'checkout', 'master'])
        testcase.assertEqual(p.status, 0, p.image)

        # The subject of the email we expect to be sent during the push.
        # As we can see, this subject has some non-ascii characters in it...
        COMMIT_EMAIL_SUBJECT = u"New \u2192 Email Subject \u2190"

        # ... As a result of which, we expect that subject to be encoded
        # prior to transmission.
        ENCODED_COMMIT_EMAIL_SUBJECT = Header(
            COMMIT_EMAIL_SUBJECT,
            "utf-8",
        ).encode()

        p = testcase.run('git push origin master:with-email-formatter'.split())
        expected_out = """\
remote: DEBUG: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 8bit
remote: Content-Type: text/plain; charset="utf-8"
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Bcc: filer@example.com
remote: Subject: {ENCODED_COMMIT_EMAIL_SUBJECT}
remote: X-Act-Checkin: repo
remote: X-Git-Author: Joel Brobecker <brobecker@adacore.com>
remote: X-Git-Refname: refs/heads/with-email-formatter
remote: X-Git-Oldrev: d065089ff184d97934c010ccd0e7e8ed94cb7165
remote: X-Git-Newrev: abdeb3a46e1daba5b7ff43c43e34b748fbd437db
remote:
remote: commit abdeb3a46e1daba5b7ff43c43e34b748fbd437db
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Fri Apr 27 13:08:29 2012 -0700
remote:
remote:     My → Commit Subject ←
remote:
remote:     Just added a little bit of text inside file a.
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
remote: commit abdeb3a46e1daba5b7ff43c43e34b748fbd437db
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Fri Apr 27 13:08:29 2012 -0700
remote:
remote:     My → Commit Subject ←
remote:
remote:     Just added a little bit of text inside file a.
remote: -----[ commit-filer end ]-----
remote:
To ../bare/repo.git
   d065089..abdeb3a  master -> with-email-formatter
""".format(ENCODED_COMMIT_EMAIL_SUBJECT=ENCODED_COMMIT_EMAIL_SUBJECT)

        testcase.assertEqual(p.status, 0, p.image)
        testcase.assertRunOutputEqual(p, expected_out)


if __name__ == '__main__':
    runtests()
