from support import *
import re

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

        expected_out = (
            # The email that we expect to be "sent":
            r".*From: Test Suite <testsuite@example.com>" +
            r".*To: commits@example.com" +
            r".*Bcc: file-ci@gnat.com" +
            r".*Subject: \[repo\] Created tag new-tag" +
            r".*X-ACT-checkin: repo" +
            r".*X-Git-Refname: refs/tags/new-tag" +
            r".*X-Git-Oldrev: 0+" +
            r".*X-Git-Newrev: 8b9a0d6bf08d7a983affbee3c187adadaaedec9e" +
            # Confirmation that the new tag was created.
            r".*\[new tag\]\s+new-tag\s+->\s+new-tag\s*")
        self.assertTrue(re.match(expected_out, p.cmd_out, re.DOTALL),
                        p.image)


if __name__ == '__main__':
    runtests()
