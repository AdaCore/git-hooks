from support import *

class TestRun(TestCase):
    def test_push_commit_on_master(testcase):
        """Try non-fast-forward push on master.
        """
        cd ('%s/repo' % TEST_DIR)

        p = testcase.run('git push -f origin topic/new-feature'.split())
        expected_out = """\
remote: *** !!! WARNING: This is *NOT* a fast-forward update.
remote: *** !!! WARNING: You may have removed some important commits.
remote: *** pre-commit check failed for commit: 14d1fa28493dd548753d11729a117dadaa9905fe
remote: *** cvs_check: `repo' < `a' `b'
remote: *** ERROR: b: Copyright header is missing from this file
remote: error: hook declined to update refs/heads/topic/new-feature
To ../bare/repo.git
 ! [remote rejected] topic/new-feature -> topic/new-feature (hook declined)
error: failed to push some refs to '../bare/repo.git'
"""

        assert p.status != 0, p.image
        testcase.assertRunOutputEqual(p, expected_out)

if __name__ == '__main__':
    runtests()
