from support import *


class TestRun(TestCase):
    def test_push_lightweight_tag(self):
        """Try pushing a lightweight tag.
        """
        cd ('%s/repo' % TEST_DIR)

        # Try deleting full-tag.  The remote is setup to refuse this request.
        p = Run('git push origin :full-tag'.split())
        self.assertNotEqual(p.status, 0, p.image)

        expected_out = """\
remote: *** Deleting a tag is not allowed in this repository
remote: error: hook declined to update refs/tags/full-tag
To ../bare/repo.git
 ! [remote rejected] full-tag (hook declined)
error: failed to push some refs to '../bare/repo.git'
"""

        self.assertRunOutputEqual(p, expected_out)


if __name__ == '__main__':
    runtests()
