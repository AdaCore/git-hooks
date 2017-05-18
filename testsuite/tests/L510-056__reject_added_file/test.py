from support import *

class TestRun(TestCase):
    def test_push_commit_on_master(self):
        """Try pushing multi-file commit on master.
        """
        cd ('%s/repo' % TEST_DIR)

        # The push should fail, because the pre-commit checker will
        # refuse one of the updates.
        p = Run('git push origin master'.split())
        expected_out = """\
remote: *** cvs_check: `repo' `b'
remote: *** cvs_check: `repo' `pck.adb'
remote: *** pre-commit check failed for file `pck.ads' at commit: 16c509ed1a0f8b558f8ed9664a06b8cf905fc6b2
remote: *** cvs_check: `repo' `pck.ads'
remote: *** ERROR: style-check error detected for file: `pck.ads'.
remote: *** ERROR: Copyright year in header is not up to date
remote: error: hook declined to update refs/heads/master
To ../bare/repo.git
 ! [remote rejected] master -> master (hook declined)
error: failed to push some refs to '../bare/repo.git'
"""

        self.assertTrue(p.status != 0, p.image)
        self.assertRunOutputEqual(p, expected_out)

if __name__ == '__main__':
    runtests()
