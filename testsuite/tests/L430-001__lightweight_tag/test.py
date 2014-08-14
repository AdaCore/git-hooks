from support import *

class TestRun(TestCase):
    def test_push_lightweight_tag(self):
        """Try pushing a lightweight tag.
        """
        cd ('%s/repo' % TEST_DIR)

        # Create a tag called 'new-tag'...
        p = Run('git tag new-tag'.split())
        self.assertEqual(p.status, 0, p.image)

        # Try pushing that new-tag.  The repository has been configured
        # to accept such updates.
        p = Run('git push origin new-tag'.split())
        self.assertEqual(p.status, 0, p.image)

        expected_out = """\
remote: DEBUG: Content-Type: text/plain; charset="us-ascii"
remote: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: From: Test Suite <testsuite@example.com>
remote: To: commits@example.com
remote: Subject: [repo] Created tag new-tag
remote: X-Act-Checkin: repo
remote: X-Git-Author: Test Suite <testsuite@example.com>
remote: X-Git-Refname: refs/tags/new-tag
remote: X-Git-Oldrev: 0000000000000000000000000000000000000000
remote: X-Git-Newrev: 8b9a0d6bf08d7a983affbee3c187adadaaedec9e
remote:
remote: The lightweight tag 'new-tag' was created pointing to:
remote:
remote:  8b9a0d6... New file: a.
To ../bare/repo.git
 * [new tag]         new-tag -> new-tag
"""

        self.assertRunOutputEqual(p, expected_out)


if __name__ == '__main__':
    runtests()
