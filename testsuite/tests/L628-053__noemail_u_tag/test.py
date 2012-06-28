from support import *
import re

class TestRun(TestCase):
    def test_push_unannotated_tag(self):
        """Try pushing an unnanotated tag.
        """
        cd ('%s/repo' % TEST_DIR)

        # Create a tag called 'new-tag'...
        p = Run('git tag new-tag'.split())
        self.assertEqual(p.status, 0, ex_run_image(p))

        # Try pushing that new-tag.  The repository has been configured
        # to accept such updates.
        p = Run('git push origin new-tag'.split())
        self.assertEqual(p.status, 0, ex_run_image(p))

        expected_out = (
            # The warning explaining that emails are not going to
            # be sent.
            r".*The hooks.noemails config parameter contains"
            r".*Commit emails will therefore not be sent"
            # Confirmation that the new tag was created.
            r".*\[new tag\]\s+new-tag\s+->\s+new-tag\s*")
        self.assertTrue(re.match(expected_out, p.out, re.DOTALL),
                        ex_run_image(p))

        # Make sure that there isn't anything that looks like
        # an email got sent.
        self.assertFalse('From:' in p.out, ex_run_image(p))
        self.assertFalse('To:' in p.out, ex_run_image(p))
        self.assertFalse('Subject:' in p.out, ex_run_image(p))


if __name__ == '__main__':
    runtests()
