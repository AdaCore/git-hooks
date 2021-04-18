from support import *

class TestRun(TestCase):
    def test_push_commit_on_master(self):
        """Try pushing one single-file commit on master.
        """
        cd ('%s/repo' % TEST_DIR)

        p = Run('git push origin master'.split())

        expected_out = """\
remote: *** Error: hooks.mailinglist config option not set.
remote: *** Please contact your repository's administrator.
remote: error: hook declined to update refs/heads/master
To ../bare/repo.git
 ! [remote rejected] master -> master (hook declined)
error: failed to push some refs to '../bare/repo.git'
"""

        self.assertNotEqual(p.status, 0, p.image)
        self.assertRunOutputEqual(p, expected_out)


if __name__ == '__main__':
    runtests()
