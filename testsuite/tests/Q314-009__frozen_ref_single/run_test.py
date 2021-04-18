from support import *

class TestRun(TestCase):
    def test_push_retired_branch(self):
        """Try pushing a branch update on a frozen branch.
        """
        cd ('%s/repo' % TEST_DIR)

        p = Run('git push origin gdb-7.5'.split())

        self.assertTrue(p.status != 0, p.image)

        expected_out = """\
remote: *** Updates to the gdb-7.5 branch are no longer allowed because
remote: *** this branch is now frozen (see "hooks.frozen-ref" in file
remote: *** project.config, from the special branch refs/meta/config).
remote: error: hook declined to update refs/heads/gdb-7.5
To ../bare/repo.git
 ! [remote rejected] gdb-7.5 -> gdb-7.5 (hook declined)
error: failed to push some refs to '../bare/repo.git'
"""
        self.assertRunOutputEqual(p, expected_out)

    def test_force_push_retired_branch(self):
        """Try force-pushing a branch update on a retired branch.
        """
        cd ('%s/repo' % TEST_DIR)

        p = Run('git push -f origin gdb-7.5'.split())

        self.assertTrue(p.status != 0, p.image)

        expected_out = """\
remote: *** Updates to the gdb-7.5 branch are no longer allowed because
remote: *** this branch is now frozen (see "hooks.frozen-ref" in file
remote: *** project.config, from the special branch refs/meta/config).
remote: error: hook declined to update refs/heads/gdb-7.5
To ../bare/repo.git
 ! [remote rejected] gdb-7.5 -> gdb-7.5 (hook declined)
error: failed to push some refs to '../bare/repo.git'
"""
        self.assertRunOutputEqual(p, expected_out)

    def test_push_active_branch(self):
        """Try pushing a branch which has not been frozen.

        This is to verify that adding a hooks.frozen-ref does not
        inadvertantly freeze all branch updates...
        """
        cd ('%s/repo' % TEST_DIR)

        p = Run('git push origin gdb-7.6'.split())
        expected_out = """\
remote: *** cvs_check: `repo' < `a'
remote: DEBUG: Content-Type: text/plain; charset="us-ascii"
remote: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Bcc: filer@example.com
remote: Subject: [repo/gdb-7.6] Updated a.
remote: X-Act-Checkin: repo
remote: X-Git-Author: Joel Brobecker <brobecker@adacore.com>
remote: X-Git-Refname: refs/heads/gdb-7.6
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
   d065089..a605403  gdb-7.6 -> gdb-7.6
"""

        self.assertEqual(p.status, 0, p.image)
        self.assertRunOutputEqual(p, expected_out)

if __name__ == '__main__':
    runtests()
