from support import *
import re

class TestRun(TestCase):
    def test_push_unannotated_tag(self):
        """Try pushing an anotated tag.
        """
        cd ('%s/repo' % TEST_DIR)

        # Try pushing tag v0.1.
        p = Run('git push origin v0.1'.split())
        self.assertEqual(p.status, 0, ex_run_image(p))

        expected_out = (
            # The warning explaining that emails are not going to be sent.
            r".*The hooks\.noemails config parameter contains"
            r".*Commit emails will therefore not be sent"

            # Confirmation that the new tag was created.
            r".*\[new tag\]\s+v0.1\s+->\s+v0.1\s*")
        self.assertTrue(re.match(expected_out, p.out, re.DOTALL),
                        ex_run_image(p))

        # Check the output for anything that might look like an email
        # was sent.
        self.assertFalse('From:' in p.out, ex_run_image(p))
        self.assertFalse('To:' in p.out, ex_run_image(p))
        self.assertFalse('Subject:' in p.out, ex_run_image(p))


if __name__ == '__main__':
    runtests()
