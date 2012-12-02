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
        expected_out = """\
remote: ---------------------------------------------------------------------------
remote: --  The hooks.noemails config parameter contains `refs/tags/new-tag'.
remote: --  Commit emails will therefore not be sent.
remote: ---------------------------------------------------------------------------
To ../bare/repo.git
 * [new tag]         new-tag -> new-tag
"""

        self.assertEqual(p.status, 0, p.image)
        self.assertEqual(expected_out, p.cmd_out, p.image)


if __name__ == '__main__':
    runtests()
