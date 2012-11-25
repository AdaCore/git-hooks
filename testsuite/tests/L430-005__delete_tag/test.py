from support import *
import re

class TestRun(TestCase):
    def test_push_annotated_tag(self):
        """Try pushing an annotated tag.
        """
        cd ('%s/repo' % TEST_DIR)

        # Try deleting full-tag.  The remote is setup to refuse this request.
        expected_out = (
            # The header of the notification email that should be sent...
            r".*From: Test Suite <testsuite@example.com>" +
            r".*To: repo@example.com" +
            r".*Bcc: file-ci@gnat.com" +
            r".*Subject: \[repo\] Deleted tag full-tag" +
            r".*X-ACT-checkin: repo" +
            r".*X-Git-Refname: refs/tags/full-tag" +
            r".*X-Git-Oldrev: a69eaaba59ea6d7574a9c5437805a628ea652c8e" +
            r".*X-Git-Newrev: 0+" +
            # The body of that email...
            r".*The annotated tag 'full-tag' was deleted." +
            r".*It previously pointed to:" +
            r".*354383f\.\.\. Initial commit\." +
            # Output from git that confirms that the tag was deleted.
            r".*-\s+\[deleted\]\s+full-tag"
            )

        p = Run('git push origin :full-tag'.split())
        self.assertEqual(p.status, 0, p.image)
        self.assertTrue(re.match(expected_out, p.cmd_out, re.DOTALL),
                        p.image)


if __name__ == '__main__':
    runtests()
