from support import *
import re

class TestRun(TestCase):
    def test_delete_lightweight_tag(self):
        """Try deleting a lightweight tag.
        """
        cd ('%s/repo' % TEST_DIR)

        p = Run('git push origin :some-tag'.split())
        self.assertNotEqual(p.status, 0, p.image)

        expected_out = """\
remote: *** Deleting a tag is not allowed in this repository
remote: error: hook declined to update refs/tags/some-tag
To ../bare/repo.git
 ! [remote rejected] some-tag (hook declined)
error: failed to push some refs to '../bare/repo.git'
"""

        self.assertEqual(expected_out, p.cmd_out, p.image)

if __name__ == '__main__':
    runtests()
