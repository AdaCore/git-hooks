from support import *

class TestRun(TestCase):
    def test_push_commit_on_master(self):
        """Try pushing one single-file commit on master.
        """
        cd ('%s/repo' % TEST_DIR)

        # Push master to the `origin' remote.  The delta should be one
        # commit with one file being modified.
        p = Run('git push origin master'.split())
        expected_out = """\
remote: *** failed to execute style checker (commit a60540361d47901d3fe254271779f380d94645f7):
remote: *** $ %s/cvs_check.py repo
remote: *** [Errno 2] No such file or directory
remote: error: hook declined to update refs/heads/master
To ../bare/repo.git
 ! [remote rejected] master -> master (hook declined)
error: failed to push some refs to '../bare/repo.git'
""" % TEST_DIR

        self.assertNotEqual(p.status, 0, p.image)
        self.assertRunOutputEqual(p, expected_out)

if __name__ == '__main__':
    runtests()
