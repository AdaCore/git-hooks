from support import *

class TestRun(TestCase):
    def test_push_commit_on_master(testcase):
        """Try pushing multi-file commit on master.
        """
        cd ('%s/repo' % TEST_DIR)

        # The push should fail, because the pre-commit checker will
        # refuse one of the updates.
        p = Run('git push origin master'.split())
        expected_out = """\
remote: *** pre-commit check failed for commit: 4f0f08f46daf6f5455cf90cdc427443fe3b32fa3
remote: *** cvs_check: `repo' < `a' `b' `c'
remote: *** ERROR: b: Copyright year in header is not up to date
remote: error: hook declined to update refs/heads/master
To ../bare/repo.git
 ! [remote rejected] master -> master (hook declined)
error: failed to push some refs to '../bare/repo.git'
"""

        assert p.status != 0, p.image
        testcase.assertRunOutputEqual(p, expected_out)

if __name__ == '__main__':
    runtests()
