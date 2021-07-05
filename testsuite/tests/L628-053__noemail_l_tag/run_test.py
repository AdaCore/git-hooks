from support import *


class TestRun(TestCase):
    def test_push_lightweight_tag(testcase):
        """Try pushing a lightweight tag."""
        # Create a tag called 'new-tag'...
        p = testcase.run("git tag new-tag".split())
        testcase.assertEqual(p.status, 0, p.image)

        # Try pushing that new-tag.  The repository has been configured
        # to accept such updates.
        p = testcase.run("git push origin new-tag".split())
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

        testcase.assertEqual(p.status, 0, p.image)
        testcase.assertRunOutputEqual(p, expected_out)


if __name__ == "__main__":
    runtests()
