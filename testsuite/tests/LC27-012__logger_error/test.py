from support import *
from os import environ

class TestRun(TestCase):
    def test_push_commit_on_master(self):
        """Try pushing one single-file commit on master.
        """
        cd ('%s/repo' % TEST_DIR)

        # Change the HOME environment variable to TEST_DIR, to get
        # the hooks to look for the .no_cvs_check file there,
        # instead of the real HOME dir.
        environ['HOME'] = TEST_DIR

        # Override the default GIT_HOOKS_LOGGER to use our own,
        # which will return an error after printing a message
        # on standard error.
        environ['GIT_HOOKS_LOGGER'] = '%s/bad-logger' % TEST_DIR

        # Create an empty .no_cvs_check file in the new HOME,
        # to disable pre-commit checks.
        no_cvs_check_fullpath = '%s/.no_cvs_check' % TEST_DIR
        open(no_cvs_check_fullpath, 'w').close()

        p = Run('git push origin master'.split())
        expected_out = """\
remote: *** Failed to file the following syslog entry:
remote: ***   - message: Pre-commit checks disabled for a60540361d47901d3fe254271779f380d94645f7 on repo by user testsuite using %(TEST_DIR)s/.no_cvs_check
remote: ***   - tag: cvs_check
remote: ***   - priority: local0.warn
remote: ***
remote: *** logger returned with error code 1:
remote: *** Error trying to connect to syslog server:
remote: *** Connection reset by peer
remote: DEBUG: Content-Type: text/plain; charset="us-ascii"
remote: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Bcc: file-ci@gnat.com
remote: Subject: [repo] Updated a.
remote: X-ACT-checkin: repo
remote: X-Git-Refname: refs/heads/master
remote: X-Git-Oldrev: d065089ff184d97934c010ccd0e7e8ed94cb7165
remote: X-Git-Newrev: a60540361d47901d3fe254271779f380d94645f7
remote:
remote: commit a60540361d47901d3fe254271779f380d94645f7
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
remote:  a |    4 +++-
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
""" % {
    'TEST_DIR' : TEST_DIR }

        self.assertEqual(p.status, 0, p.image)
        self.assertRunOutputEqual(p, expected_out)

if __name__ == '__main__':
    runtests()
