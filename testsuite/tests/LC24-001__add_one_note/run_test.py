from support import *

class TestRun(TestCase):
    def test_push_notes(testcase):
        """Try pushing our notes.
        """
        cd ('%s/repo' % TEST_DIR)

        p = testcase.run('git push origin notes/commits'.split())
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
To ../bare/repo.git
   bbcc356..58e8efa  refs/notes/commits -> refs/notes/commits
"""

        testcase.assertEqual(p.status, 0, p.image)
        testcase.assertRunOutputEqual(p, expected_out)

if __name__ == '__main__':
    runtests()
