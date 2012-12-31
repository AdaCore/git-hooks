from support import *

class TestRun(TestCase):
    def test_push_annotated_tag(self):
        """Try pushing an anotated tag.
        """
        cd ('%s/repo' % TEST_DIR)

        # Try pushing tag v0.1.
        p = Run('git push origin v0.1'.split())
        expected_out = """\
remote: ----------------------------------------------------------------------
remote: --  The hooks.no-emails config option contains `refs/tags/v0.1',
remote: --  which matches the name of the reference being updated
remote: --  (refs/tags/v0.1).
remote: --
remote: --  Commit emails will therefore not be sent.
remote: ----------------------------------------------------------------------
To ../bare/repo.git
 * [new tag]         v0.1 -> v0.1
"""

        self.assertEqual(p.status, 0, p.image)
        self.assertRunOutputEqual(p, expected_out)


if __name__ == '__main__':
    runtests()
