# coding=utf-8
from support import *

from email.header import Header


class TestRun(TestCase):
    def test_push_commit_on_master(testcase):
        """Try pushing one single-file commit on master.

        The purpose of this testcase is to verify that the git-hooks
        behave as expected when the repository uses a commit-email-formatter
        hook which overrides the email_body, with the returned email body
        containing some non-ascii characters.
        """
        cd ('%s/repo' % TEST_DIR)

        # First, update the git-hooks configuration to install our
        # the script we want to use as our commit-email-formatter.

        p = testcase.run(['git', 'fetch', 'origin', 'refs/meta/config'])
        testcase.assertEqual(p.status, 0, p.image)

        p = testcase.run(['git', 'checkout', 'FETCH_HEAD'])
        testcase.assertEqual(p.status, 0, p.image)

        p = testcase.run(['git', 'config', '--file', 'project.config',
                 'hooks.commit-email-formatter',
                 os.path.join(TEST_DIR, 'commit-email-formatter.py')])
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

        # Push master to the `origin' remote.  The delta should be one
        # commit with one file being modified.

        p = testcase.run('git push origin master'.split())
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
remote: X-Git-Newrev: a60540361d47901d3fe254271779f380d94645f7
remote:
remote: My → Email body ←
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
To ../bare/repo.git
   d065089..a605403  master -> master
"""

        testcase.assertEqual(p.status, 0, p.image)
        testcase.assertRunOutputEqual(p, expected_out)

if __name__ == '__main__':
    runtests()
