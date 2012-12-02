from support import *

class TestRun(TestCase):
    def test_push_annotated_tag(self):
        """Try pushing an anotated tag.
        """
        cd ('%s/repo' % TEST_DIR)

        # Try pushing tag v0.1.
        p = Run('git push origin v0.1'.split())
        expected_out = """\
remote: ---------------------------------------------------------------------------
remote: --  The hooks.noemails config parameter contains `refs/tags/v0.1'.
remote: --  Commit emails will therefore not be sent.
remote: ---------------------------------------------------------------------------
To ../bare/repo.git
 * [new tag]         v0.1 -> v0.1
"""

        self.assertEqual(p.status, 0, p.image)
        self.assertEqual(expected_out, p.cmd_out, p.image)


if __name__ == '__main__':
    runtests()
