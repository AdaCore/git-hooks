from support import *

class TestRun(TestCase):
    def test_push_commit_on_master(self):
        """Try pushing one single-file commit on master.

        The purpose of this testcase is to test combined style checking.
        """
        cd ('%s/repo' % TEST_DIR)

        self.set_debug_level(1)

        # Push master to the `origin' remote.  The delta should be one
        # commit with one file being modified.
        p = Run('git push origin master'.split())
        expected_out = """\
remote: DEBUG: validate_ref_update (refs/heads/master, d065089ff184d97934c010ccd0e7e8ed94cb7165, a60540361d47901d3fe254271779f380d94645f7)
remote: DEBUG: update base: d065089ff184d97934c010ccd0e7e8ed94cb7165
remote: DEBUG: (combined style checking)
remote: DEBUG: style_check_commit(old_rev=d065089ff184d97934c010ccd0e7e8ed94cb7165, new_rev=a60540361d47901d3fe254271779f380d94645f7)
remote: *** cvs_check: `repo' < `a'
remote: DEBUG: post_receive_one(ref_name=refs/heads/master
remote:                         old_rev=d065089ff184d97934c010ccd0e7e8ed94cb7165
remote:                         new_rev=a60540361d47901d3fe254271779f380d94645f7)
remote: DEBUG: update base: d065089ff184d97934c010ccd0e7e8ed94cb7165
remote: DEBUG: Content-Type: text/plain; charset="us-ascii"
remote: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Bcc: file-ci@gnat.com
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
"""

        self.assertTrue(p.status == 0, p.image)
        self.assertRunOutputEqual(p, expected_out)

if __name__ == '__main__':
    runtests()
