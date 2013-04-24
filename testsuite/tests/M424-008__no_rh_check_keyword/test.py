from support import *

class TestRun(TestCase):
    def test_push_commit_on_master(self):
        """Try pushing master...
        """
        cd ('%s/repo' % TEST_DIR)

        # Push a first change on master.  The revision log is violating
        # a couple of rules (empty line after subject, missing TN),
        # but the "(no-rh-check)" keyword/tag in the revision log
        # should turn all rh-checks to be accepted.
        p = Run('git push origin 67091e2b3fd5b0b072f4cb6f6f8b5d58fac891a3:master'.split())
        expected_out = """\
remote: *** cvs_check: `trunk/repo/a'
remote: DEBUG: Content-Type: text/plain; charset="us-ascii"
remote: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Bcc: file-ci@gnat.com
remote: Subject: [repo] Updated a. Non-empty line after subject (no no).
remote: X-Act-Checkin: repo
remote: X-Git-Refname: refs/heads/master
remote: X-Git-Oldrev: d065089ff184d97934c010ccd0e7e8ed94cb7165
remote: X-Git-Newrev: 67091e2b3fd5b0b072f4cb6f6f8b5d58fac891a3
remote:
remote: commit 67091e2b3fd5b0b072f4cb6f6f8b5d58fac891a3
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Fri Apr 27 13:08:29 2012 -0700
remote:
remote:     Updated a.
remote:     Non-empty line after subject (no no).
remote:
remote:     Just added a little bit of text inside file a.
remote:     Thought about doing something else, but not really necessary.
remote:
remote:     (no-rh-check)
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
   d065089..67091e2  67091e2b3fd5b0b072f4cb6f6f8b5d58fac891a3 -> master
"""

        self.assertEqual(p.status, 0, p.image)
        self.assertRunOutputEqual(p, expected_out)

        # Now, push a second change on master.  Same thing, but
        # the commit introduces some changes that the cvs_check'er
        # will reject.

        p = Run('git push origin master'.split())
        expected_out = """\
remote: *** pre-commit check failed for file `b' at commit: af07c14c3d6be423c86bbe3d4ac5327b2cdd78b9
remote: *** cvs_check: `trunk/repo/b'
remote: *** *** cvs_check: some style errors in: trunk/repo/b
remote: error: hook declined to update refs/heads/master
To ../bare/repo.git
 ! [remote rejected] master -> master (hook declined)
error: failed to push some refs to '../bare/repo.git'
"""

        self.assertNotEqual(p.status, 0, p.image)
        self.assertRunOutputEqual(p, expected_out)

if __name__ == '__main__':
    runtests()
