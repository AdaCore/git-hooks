from support import *

class TestRun(TestCase):
    def test_push_notes(self):
        """Try pushing our notes.
        """
        cd ('%s/repo' % TEST_DIR)

        p = Run('git push origin notes/commits'.split())
        expected_out = """\
To ../bare/repo.git
 ! [rejected]        refs/notes/commits -> refs/notes/commits (non-fast-forward)
error: failed to push some refs to '../bare/repo.git'
hint: Updates were rejected because a pushed branch tip is behind its remote
hint: counterpart. Check out this branch and merge the remote changes
hint: (e.g. 'git pull') before pushing again.
hint: See the 'Note about fast-forwards' in 'git push --help' for details.
"""

        self.assertNotEqual(p.status, 0, p.image)
        self.assertEqual(expected_out, p.cmd_out, p.image)

        # Try again with -f, simulating a user trying to force
        # its way into getting this non-fast-forward update accepted.
        p = Run('git push -f origin notes/commits'.split())
        expected_out = """\
remote: *** Your Git Notes are not up to date.
remote: ***
remote: *** Please update your Git Notes and push again.
remote: error: hook declined to update refs/notes/commits
To ../bare/repo.git
 ! [remote rejected] refs/notes/commits -> refs/notes/commits (hook declined)
error: failed to push some refs to '../bare/repo.git'
"""

        self.assertNotEqual(p.status, 0, p.image)
        self.assertEqual(expected_out, p.cmd_out, p.image)

if __name__ == '__main__':
    runtests()
