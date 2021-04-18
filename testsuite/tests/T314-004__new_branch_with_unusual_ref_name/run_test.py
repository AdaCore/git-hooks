from support import *

class TestRun(TestCase):
    def test_push_commit_on_master(self):
        """Push master as new ref with name outside standard namespace."""
        cd ('%s/repo' % TEST_DIR)

        p = Run('git push origin master:refs/for/master'.split())
        expected_out = """\
remote: *** cvs_check: `repo' < `a'
remote: DEBUG: Content-Type: text/plain; charset="us-ascii"
remote: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Subject: [repo] Created branch 'master' in namespace 'refs/for'
remote: X-Act-Checkin: repo
remote: X-Git-Author: Test Suite <testsuite@adacore.com>
remote: X-Git-Refname: refs/for/master
remote: X-Git-Oldrev: 0000000000000000000000000000000000000000
remote: X-Git-Newrev: a60540361d47901d3fe254271779f380d94645f7
remote:
remote: The branch 'master' was created in namespace 'refs/for' pointing to:
remote:
remote:  a605403... Updated a.
remote: DEBUG: inter-email delay...
remote: DEBUG: Content-Type: text/plain; charset="us-ascii"
remote: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Bcc: filer@example.com
remote: Subject: [repo(refs/for/master)] Updated a.
remote: X-Act-Checkin: repo
remote: X-Git-Author: Joel Brobecker <brobecker@adacore.com>
remote: X-Git-Refname: refs/for/master
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
 * [new branch]      master -> refs/for/master
"""

        self.assertTrue(p.status == 0, p.image)
        self.assertRunOutputEqual(p, expected_out)

        # Verify that the branch has been created in the remote
        # repository and that it points to the expected commit.

        cd('%s/bare/repo.git' % TEST_DIR)

        p = Run('git show-ref -s refs/for/master'.split())
        expected_out = """\
a60540361d47901d3fe254271779f380d94645f7
"""

        self.assertTrue(p.status == 0, p.image)
        self.assertRunOutputEqual(p, expected_out)


if __name__ == '__main__':
    runtests()
