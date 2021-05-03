from support import *

class TestRun(TestCase):
    def test_push(self):
        """Try pushing master...
        """
        cd ('%s/repo' % TEST_DIR)

        # First, try pushing the comming in the tn-missing branch
        # on fsf-master.  This is to verify that, even though,
        # style checks are disabled on this branch, other checks
        # are not.

        p = Run('git push origin tn-missing:fsf-master'.split())
        expected_out = """\
remote: *** The following commit is missing a ticket number inside
remote: *** its revision history.  If the change is sufficiently
remote: *** minor that a ticket number is not meaningful, please use
remote: *** the word "no-tn-check" in place of a ticket number.
remote: ***
remote: *** commit a60540361d47901d3fe254271779f380d94645f7
remote: *** Subject: Updated a.
remote: error: hook declined to update refs/heads/fsf-master
To ../bare/repo.git
 ! [remote rejected] tn-missing -> fsf-master (hook declined)
error: failed to push some refs to '../bare/repo.git'
"""

        self.assertNotEqual(p.status, 0, p.image)
        self.assertRunOutputEqual(p, expected_out)

        # Next, try pushing master.  We should be failing the style
        # checks.

        p = Run('git push origin master'.split())
        expected_out = """\
remote: *** pre-commit check failed for commit: 217d35d3043af4087f10cfaadfa0abf1a4b87d4b
remote: *** a: bad style, please fix.
remote: error: hook declined to update refs/heads/master
To ../bare/repo.git
 ! [remote rejected] master -> master (hook declined)
error: failed to push some refs to '../bare/repo.git'
"""

        self.assertNotEqual(p.status, 0, p.image)
        self.assertRunOutputEqual(p, expected_out)

        # And finally, try pushing master, but on fsf-master.
        # That branch has style checks disabled, so it should
        # work.

        p = Run('git push origin master:fsf-master'.split())
        expected_out = """\
remote: DEBUG: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: Content-Type: text/plain; charset="utf-8"
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Bcc: filer@example.com
remote: Subject: [repo/fsf-master] Updated a.
remote: X-Act-Checkin: repo
remote: X-Git-Author: Joel Brobecker <brobecker@adacore.com>
remote: X-Git-Refname: refs/heads/fsf-master
remote: X-Git-Oldrev: d065089ff184d97934c010ccd0e7e8ed94cb7165
remote: X-Git-Newrev: 217d35d3043af4087f10cfaadfa0abf1a4b87d4b
remote:
remote: commit 217d35d3043af4087f10cfaadfa0abf1a4b87d4b
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Fri Apr 27 13:08:29 2012 -0700
remote:
remote:     Updated a.
remote:
remote:     Just added a little bit of text inside file a.
remote:     Thought about doing something else, but not really necessary.
remote:
remote:     TN: Q608-030
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
   d065089..217d35d  master -> fsf-master
"""

        self.assertEqual(p.status, 0, p.image)
        self.assertRunOutputEqual(p, expected_out)

if __name__ == '__main__':
    runtests()
