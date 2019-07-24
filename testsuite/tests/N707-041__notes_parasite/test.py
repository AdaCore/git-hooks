from support import *

class TestRun(TestCase):
    def test_push_note(self):
        """Try pushing our latest git note.
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
remote: Subject: [repo] notes update for 52393869d6041893f83a32692f31313997125d5b
remote: X-Act-Checkin: repo
remote: X-Git-Author: Joel Brobecker <brobecker@adacore.com>
remote: X-Git-Refname: refs/notes/commits
remote: X-Git-Oldrev: a1debe299a88f46dd84c5f1392a0a87a17f5dac5
remote: X-Git-Newrev: a137508589e324b68734d3c7f8f4fb4fbac5e3cb
remote:
remote: A Git Notes has been updated; it now contains:
remote:
remote:     Annotating the first commit...
remote:
remote: This note annotates the following commit:
remote:
remote: commit 52393869d6041893f83a32692f31313997125d5b
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Mon Jul 7 18:49:53 2014 +0200
remote:
remote:     New file.
remote:
remote: Diff:
remote:
remote: diff --git a/52/393869d6041893f83a32692f31313997125d5b b/52/393869d6041893f83a32692f31313997125d5b
remote: new file mode 100644
remote: index 0000000..797ac20
remote: --- /dev/null
remote: +++ b/52/393869d6041893f83a32692f31313997125d5b
remote: @@ -0,0 +1 @@
remote: +Annotating the first commit...
remote: diff --git a/d9eeeaff972e85dd086c8abe8491440cca74104b b/d9/eeeaff972e85dd086c8abe8491440cca74104b
remote: similarity index 100%
remote: rename from d9eeeaff972e85dd086c8abe8491440cca74104b
remote: rename to d9/eeeaff972e85dd086c8abe8491440cca74104b
To ../bare/repo.git
   a1debe2..a137508  refs/notes/commits -> refs/notes/commits
"""

        self.assertTrue(p.status == 0, p.image)
        self.assertRunOutputEqual(p, expected_out)

if __name__ == '__main__':
    runtests()