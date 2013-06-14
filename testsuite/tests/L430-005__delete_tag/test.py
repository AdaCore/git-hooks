from support import *
import re

class TestRun(TestCase):
    def test_push_annotated_tag(self):
        """Try pushing an annotated tag.
        """
        cd ('%s/repo' % TEST_DIR)

        # Try deleting full-tag.  The remote is setup to refuse this request.
        expected_out = """\
remote: DEBUG: Content-Type: text/plain; charset="us-ascii"
remote: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: From: Test Suite <testsuite@example.com>
remote: To: repo@example.com
remote: Subject: [repo] Deleted tag full-tag
remote: X-Act-Checkin: repo
remote: X-Git-Refname: refs/tags/full-tag
remote: X-Git-Oldrev: a69eaaba59ea6d7574a9c5437805a628ea652c8e
remote: X-Git-Newrev: 0000000000000000000000000000000000000000
remote:
remote: The annotated tag 'full-tag' was deleted.
remote: It previously pointed to:
remote:
remote:  354383f... Initial commit.
To ../bare/repo.git
 - [deleted]         full-tag
"""

        p = Run('git push origin :full-tag'.split())
        self.assertEqual(p.status, 0, p.image)
        self.assertRunOutputEqual(p, expected_out)


if __name__ == '__main__':
    runtests()
