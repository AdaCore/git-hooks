from support import *

class TestRun(TestCase):
    def test_push(self):
        """Try pushing one single-file commit on master.

        The operation should fail due to either config.debug-level
        having an invalid value, or GIT_HOOKS_DEBUG_LEVEL having
        an invalid value.
        """
        cd ('%s/repo' % TEST_DIR)

        # Push master to the `origin' remote.
        p = Run('git push origin master'.split())
        expected_out = """\
remote: *** Invalid hooks.debug-level value: zero (must be integer)
remote: error: hook declined to update refs/heads/master
To ../bare/repo.git
 ! [remote rejected] master -> master (hook declined)
error: failed to push some refs to '../bare/repo.git'
"""

        assert p.status != 0, p.image
        self.assertRunOutputEqual(p, expected_out)

        # Same thing, but with an invalid GIT_HOOKS_DEBUG_LEVEL value.
        self.set_debug_level('true')

        p = Run('git push origin master'.split())
        expected_out = """\
remote: *** Invalid value for GIT_HOOKS_DEBUG_LEVEL: true (must be integer)
remote: error: hook declined to update refs/heads/master
To ../bare/repo.git
 ! [remote rejected] master -> master (hook declined)
error: failed to push some refs to '../bare/repo.git'
"""

        assert p.status != 0, p.image
        self.assertRunOutputEqual(p, expected_out)


if __name__ == '__main__':
    runtests()
