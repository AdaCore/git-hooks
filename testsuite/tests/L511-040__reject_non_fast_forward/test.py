from support import *

class TestRun(TestCase):
    def test_push_commit_on_master(self):
        """Try non-fast-forward push on master.
        """
        cd ('%s/repo' % TEST_DIR)

        p = Run('git push -f origin master'.split())
        expected_out = """\
remote: *** Non-fast-forward updates are not allowed on this branch;
remote: *** Please rebase your changes on top of the latest HEAD,
remote: *** and then try pushing again.
remote: error: hook declined to update refs/heads/master
To ../bare/repo.git
 ! [remote rejected] master -> master (hook declined)
error: failed to push some refs to '../bare/repo.git'
"""

        self.assertTrue(p.status != 0, p.image)
        self.assertEqual(expected_out, p.cmd_out, p.image)

if __name__ == '__main__':
    runtests()
