from support import *
import re

class TestRun(TestCase):
    def test_push_annotated_tag(self):
        """Try pushing an anotated tag.
        """
        cd ('%s/repo' % TEST_DIR)

        # Try pushing tag v0.1.
        p = Run('git push origin v0.1'.split())
        self.assertEqual(p.status, 0, ex_run_image(p))

        expected_out = (
            # The email that we expect to be "sent":
            r".*From: Test Suite <testsuite@example.com>" +
            r".*To: testsuite@example.com" +
            r".*Bcc: file-ci@gnat.com" +
            r".*Subject: \[repo\] Created tag v0\.1" +
            r".*X-ACT-checkin: repo" +
            r".*X-Git-Refname: refs/tags/v0\.1" +
            r".*X-Git-Oldrev: 0+" +
            r".*X-Git-Newrev: c4c1e91cddc3d48a2aab7d454bc6537149f37dd8" +
            r"" +
            r".*The unsigned tag 'v0\.1' was created pointing to:" +
            r".*8b9a0d6... New file: a\." +
            r"" +
            r".*Tagger: Joel Brobecker <brobecker@adacore.com>" +
            r".*Date: Tue Jun 26 07:51:14 2012 -0700" +
            r"" +
            r".*This is a new tag\." +
            # Confirmation that the new tag was created.
            r".*\[new tag\]\s+v0.1\s+->\s+v0.1\s*")
        self.assertTrue(re.match(expected_out, p.out, re.DOTALL),
                        ex_run_image(p))


if __name__ == '__main__':
    runtests()
