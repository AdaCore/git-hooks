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
remote: Subject: [notes][repo] Updated a.
remote: X-Act-Checkin: repo
remote: X-Git-Author: Joel Brobecker <brobecker@adacore.com>
remote: X-Git-Refname: refs/notes/commits
remote: X-Git-Oldrev:
remote: X-Git-Newrev: bbcc356176bb7f3104788323566c4fcef70650fc
remote:
remote: A Git note has been updated; it now contains:
remote:
remote:     This is my first note.
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
remote: new file mode 100644
remote: index 0000000..8bd95e8
remote: --- /dev/null
remote: +++ b/a60540361d47901d3fe254271779f380d94645f7
remote: @@ -0,0 +1 @@
remote: +This is my first note.
remote: DEBUG: inter-email delay...
remote: DEBUG: Content-Type: text/plain; charset="us-ascii"
remote: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Bcc: file-ci@gnat.com
remote: Subject: [notes][repo] New file: a.
remote: X-Act-Checkin: repo
remote: X-Git-Author: Joel Brobecker <brobecker@adacore.com>
remote: X-Git-Refname: refs/notes/commits
remote: X-Git-Oldrev: bbcc356176bb7f3104788323566c4fcef70650fc
remote: X-Git-Newrev: a0cd78e7b5d7bab7a956489837bf61f7a6376527
remote:
remote: A Git note has been updated; it now contains:
remote:
remote:     This is my second note.
remote:
remote: This note annotates the following commit:
remote:
remote: commit d065089ff184d97934c010ccd0e7e8ed94cb7165
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Fri Apr 27 13:06:44 2012 -0700
remote:
remote:     New file: a.
remote:
remote: Diff:
remote:
remote: diff --git a/d065089ff184d97934c010ccd0e7e8ed94cb7165 b/d065089ff184d97934c010ccd0e7e8ed94cb7165
remote: new file mode 100644
remote: index 0000000..f977f7b
remote: --- /dev/null
remote: +++ b/d065089ff184d97934c010ccd0e7e8ed94cb7165
remote: @@ -0,0 +1 @@
remote: +This is my second note.
To ../bare/repo.git
 * [new branch]      refs/notes/commits -> refs/notes/commits
"""

        self.assertEqual(p.status, 0, p.image)
        self.assertRunOutputEqual(p, expected_out)

if __name__ == '__main__':
    runtests()
