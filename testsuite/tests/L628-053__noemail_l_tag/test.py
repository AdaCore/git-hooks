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
            # The warning explaining that emails are not going to
            # be sent.
            r".*The hooks.noemails config parameter contains"
            r".*Commit emails will therefore not be sent"
            # Confirmation that the new tag was created.
            r".*\[new tag\]\s+new-tag\s+->\s+new-tag\s*")
        self.assertTrue(re.match(expected_out, p.cmd_out, re.DOTALL),
                        p.image)

        # Make sure that there isn't anything that looks like
        # an email got sent.
        self.assertFalse('From:' in p.cmd_out, p.image)
        self.assertFalse('To:' in p.cmd_out, p.image)
        self.assertFalse('Subject:' in p.cmd_out, p.image)


if __name__ == '__main__':
    runtests()
