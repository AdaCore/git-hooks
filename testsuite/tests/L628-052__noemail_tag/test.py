from support import *
import re

class TestRun(TestCase):
    def test_push_annotated_tag(self):
        """Try pushing an anotated tag.
        """
        cd ('%s/repo' % TEST_DIR)

        # Try pushing tag v0.1.
        p = Run('git push origin v0.1'.split())
        self.assertEqual(p.status, 0, p.image)

        expected_out = (
            # The warning explaining that emails are not going to be sent.
            r".*The hooks\.noemails config parameter contains"
            r".*Commit emails will therefore not be sent"

            # Confirmation that the new tag was created.
            r".*\[new tag\]\s+v0.1\s+->\s+v0.1\s*")
        self.assertTrue(re.match(expected_out, p.cmd_out, re.DOTALL),
                        p.image)

        # Check the output for anything that might look like an email
        # was sent.
        self.assertFalse('From:' in p.cmd_out, p.image)
        self.assertFalse('To:' in p.cmd_out, p.image)
        self.assertFalse('Subject:' in p.cmd_out, p.image)


if __name__ == '__main__':
    runtests()
