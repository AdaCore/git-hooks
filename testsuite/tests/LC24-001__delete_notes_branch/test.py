from support import *

class TestRun(TestCase):
    def test_delete_notes(self):
        """Try deleting the notes/commits branch.
        """
        cd ('%s/repo' % TEST_DIR)

        p = Run('git push origin :refs/notes/commits'.split())
        expected_out = """\
remote: *** Deleting the Git Notes is not allowed.
remote: error: hook declined to update refs/notes/commits
To ../bare/repo.git
 ! [remote rejected] refs/notes/commits (hook declined)
error: failed to push some refs to '../bare/repo.git'
"""

        self.assertNotEqual(p.status, 0, p.image)
        self.assertRunOutputEqual(p, expected_out)

if __name__ == '__main__':
    runtests()
