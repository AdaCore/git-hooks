from support import *


class TestRun(TestCase):
    def test_delete_tag(testcase):
        """Try deleting a tag."""
        # Try deleting full-tag.  The remote is setup to refuse this request.
        p = testcase.run("git push origin :full-tag".split())
        testcase.assertNotEqual(p.status, 0, p.image)

        expected_out = """\
remote: *** Deleting a tag is not allowed in this repository
remote: error: hook declined to update refs/tags/full-tag
To ../bare/repo.git
 ! [remote rejected] full-tag (hook declined)
error: failed to push some refs to '../bare/repo.git'
"""

        testcase.assertRunOutputEqual(p, expected_out)


if __name__ == "__main__":
    runtests()
