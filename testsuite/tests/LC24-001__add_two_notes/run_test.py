from support import *

class TestRun(TestCase):
    def test_push_notes(self):
        """Try pushing our notes.
        """
        cd ('%s/repo' % TEST_DIR)

        p = Run('git push origin notes/commits'.split())
        expected_out = """\
remote: DEBUG: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: Content-Type: text/plain; charset="utf-8"
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Bcc: filer@example.com
remote: Subject: [notes][repo] New file: a.
remote: X-Act-Checkin: repo
remote: X-Git-Author: Joel Brobecker <brobecker@adacore.com>
remote: X-Git-Refname: refs/notes/commits
remote: X-Git-Oldrev: bbcc356176bb7f3104788323566c4fcef70650fc
remote: X-Git-Newrev: 58e8efaaf0dee13edea66b1abbd4b669132b3d77
remote:
remote: A Git note has been updated; it now contains:
remote:
remote:     This is my new note.
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
remote: index 0000000..0bf2266
remote: --- /dev/null
remote: +++ b/d065089ff184d97934c010ccd0e7e8ed94cb7165
remote: @@ -0,0 +1 @@
remote: +This is my new note.
remote: DEBUG: inter-email delay...
remote: DEBUG: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: Content-Type: text/plain; charset="utf-8"
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Bcc: filer@example.com
remote: Subject: [notes][repo] Separate subject from body with empty line in file a.
remote: X-Act-Checkin: repo
remote: X-Git-Author: Joel Brobecker <brobecker@adacore.com>
remote: X-Git-Refname: refs/notes/commits
remote: X-Git-Oldrev: 58e8efaaf0dee13edea66b1abbd4b669132b3d77
remote: X-Git-Newrev: 0892f7e8d41c265fc0ffcbe604f0e7ce784bd9d2
remote:
remote: A Git note has been updated; it now contains:
remote:
remote:     Another short note.
remote:
remote: This note annotates the following commit:
remote:
remote: commit 52abc3c195e80fa1713f2603290b6b202484694b
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Mon Dec 24 10:06:21 2012 +0400
remote:
remote:     Separate subject from body with empty line in file a.
remote:
remote:     A slightly more verbose description of the change.
remote:     Takes two lines, too!
remote:
remote:     For TICK-ETT.
remote:
remote: Diff:
remote:
remote: diff --git a/52abc3c195e80fa1713f2603290b6b202484694b b/52abc3c195e80fa1713f2603290b6b202484694b
remote: new file mode 100644
remote: index 0000000..1b8adce
remote: --- /dev/null
remote: +++ b/52abc3c195e80fa1713f2603290b6b202484694b
remote: @@ -0,0 +1 @@
remote: +Another short note.
To ../bare/repo.git
   bbcc356..0892f7e  refs/notes/commits -> refs/notes/commits
"""

        self.assertEqual(p.status, 0, p.image)
        self.assertRunOutputEqual(p, expected_out)

if __name__ == '__main__':
    runtests()
