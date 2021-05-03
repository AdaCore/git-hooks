from support import *
from os import environ, utime
import time

class TestRun(TestCase):
    def test_push_commit_on_master(self):
        """Try pushing one single-file commit on master.
        """
        cd ('%s/repo' % TEST_DIR)

        # Change the HOME environment variable to TEST_DIR, to get
        # the hooks to look for the .no_cvs_check file there,
        # instead of the real HOME dir.
        environ['HOME'] = TEST_DIR

        # Create an empty .no_cvs_check file in the new HOME,
        # to disable pre-commit checks.
        no_cvs_check_fullpath = '%s/.no_cvs_check' % TEST_DIR
        open(no_cvs_check_fullpath, 'w').close()

        # Make the .no_cvs_check file 1 day and 1 second old, which
        # should make it too old for the hooks to honor it.
        too_old = time.time() - 24 * 60 * 60 - 1
        utime(no_cvs_check_fullpath, (too_old, too_old))

        p = Run('git push origin master'.split())
        expected_out = """\
remote: *** %(TEST_DIR)s/.no_cvs_check is too old and will be ignored.
remote: *** pre-commit check failed for commit: a60540361d47901d3fe254271779f380d94645f7
remote: *** ERROR: a: Copyright year in header is not up to date
remote: error: hook declined to update refs/heads/master
To ../bare/repo.git
 ! [remote rejected] master -> master (hook declined)
error: failed to push some refs to '../bare/repo.git'
""" % {
    'TEST_DIR' : TEST_DIR }

        self.assertNotEqual(p.status, 0, p.image)
        self.assertRunOutputEqual(p, expected_out)

        # Set debug level to 1, in order to get the debug trace
        # when pre-commit checks are skipped due to .no_cvs_check
        # user override.
        self.set_debug_level(1)

        # Make the .no_cvs_check file 1 day minus a few seconds old,
        # which should make it just old enough to be honored.
        recent_enough = time.time() - 24 * 60 * 60 + 10
        utime(no_cvs_check_fullpath, (recent_enough, recent_enough))

        p = Run('git push origin master'.split())
        expected_out = """\
remote: DEBUG: validate_ref_update (refs/heads/master, d065089ff184d97934c010ccd0e7e8ed94cb7165, a60540361d47901d3fe254271779f380d94645f7)
remote: DEBUG: update base: d065089ff184d97934c010ccd0e7e8ed94cb7165
remote: DEBUG: %(TEST_DIR)s/.no_cvs_check found - pre-commit checks disabled
remote: SYSLOG: style_checker: Pre-commit checks disabled for a60540361d47901d3fe254271779f380d94645f7 on repo by user testsuite using %(TEST_DIR)s/.no_cvs_check
remote: DEBUG: post_receive_one(ref_name=refs/heads/master
remote:                         old_rev=d065089ff184d97934c010ccd0e7e8ed94cb7165
remote:                         new_rev=a60540361d47901d3fe254271779f380d94645f7)
remote: DEBUG: update base: d065089ff184d97934c010ccd0e7e8ed94cb7165
remote: DEBUG: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
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
""" % {
    'TEST_DIR' : TEST_DIR }

        self.assertEqual(p.status, 0, p.image)
        self.assertRunOutputEqual(p, expected_out)

if __name__ == '__main__':
    runtests()
