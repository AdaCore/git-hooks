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
remote: X-Git-Oldrev:
remote: X-Git-Newrev: bbcc356176bb7f3104788323566c4fcef70650fc
remote:
remote: A Git Notes has been updated; it now contains:
remote:
remote:     This is my first note.
remote:
remote: This notes annotates the following commit:
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
remote: new file mode 100644
remote: index 0000000..8bd95e8
remote: --- /dev/null
remote: +++ b/a60540361d47901d3fe254271779f380d94645f7
remote: @@ -0,0 +1 @@
remote: +This is my first note.
remote:
To ../bare/repo.git
 * [new branch]      refs/notes/commits -> refs/notes/commits
"""

        self.assertEqual(p.status, 0, p.image)
        self.assertEqual(expected_out, p.cmd_out, p.image)

if __name__ == '__main__':
    runtests()
