from support import *
import re

class TestRun(TestCase):
    def test_delete_unannotated_tag(self):
        """Try deleting an unnanotated tag.
        """
        cd ('%s/repo' % TEST_DIR)

        p = Run('git push origin :some-tag'.split())
        self.assertEqual(p.status, 0, ex_run_image(p))

        expected_out = (
            r".*From: Test Suite <testsuite@example.com>" +
            r".*To: something-ci@example.com" +
            r".*Bcc: file-ci@gnat.com" +
            r".*Subject: \[repo\] Deleted tag some-tag" +
            r".*X-ACT-checkin: repo" +
            r".*X-Git-Refname: refs/tags/some-tag" +
            r".*X-Git-Oldrev: 8b9a0d6bf08d7a983affbee3c187adadaaedec9e" +
            r".*X-Git-Newrev: 0000000000000000000000000000000000000000" +
            r".*-\s+\[deleted\]\s+some-tag")
        self.assertTrue(re.match(expected_out, p.out, re.DOTALL),
                        ex_run_image(p))

if __name__ == '__main__':
    runtests()
