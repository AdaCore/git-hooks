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
remote: ----------------------------------------------------------------------
remote: --  The hooks.no-emails config option contains `refs/tags/new-tag',
remote: --  which matches the name of the reference being updated
remote: --  (refs/tags/new-tag).
remote: --
remote: --  Commit emails will therefore not be sent.
remote: ----------------------------------------------------------------------
To ../bare/repo.git
 * [new tag]         new-tag -> new-tag
"""

        self.assertEqual(p.status, 0, p.image)
        self.assertRunOutputEqual(p, expected_out)


if __name__ == '__main__':
    runtests()
