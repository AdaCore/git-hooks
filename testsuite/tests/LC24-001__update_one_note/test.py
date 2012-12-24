from support import *

class TestRun(TestCase):
    def test_push_notes(self):
        """Try pushing our notes.
        """
        cd ('%s/repo' % TEST_DIR)

        p = Run('git push origin notes/commits'.split())
        expected_out = """\
remote: DEBUG: Content-Type: text/plain; charset="us-ascii"
remote: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Bcc: file-ci@gnat.com
remote: Subject: [repo] notes update for a60540361d47901d3fe254271779f380d94645f7
remote: X-ACT-checkin: repo
remote: X-Git-Refname: refs/notes/commits
remote: X-Git-Oldrev: 58e8efaaf0dee13edea66b1abbd4b669132b3d77
remote: X-Git-Newrev: da34a4b05e4d30a714577a9cc46c199df1634838
remote:
remote: A Git Notes has been updated; it now contains:
remote:
remote:     This is my first note.
remote:     Add some information about my first note.
remote:
remote: This note annotates the following commit:
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
remote:
remote: diff --git a/a60540361d47901d3fe254271779f380d94645f7 b/a60540361d47901d3fe254271779f380d94645f7
remote: index 8bd95e8..1d2e227 100644
remote: --- a/a60540361d47901d3fe254271779f380d94645f7
remote: +++ b/a60540361d47901d3fe254271779f380d94645f7
remote: @@ -1 +1,2 @@
remote:  This is my first note.
remote: +Add some information about my first note.
remote:
To ../bare/repo.git
   58e8efa..da34a4b  refs/notes/commits -> refs/notes/commits
"""

        self.assertEqual(p.status, 0, p.image)
        self.assertEqual(expected_out, p.cmd_out, p.image)

if __name__ == '__main__':
    runtests()
