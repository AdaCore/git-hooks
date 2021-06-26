from support import *

class TestRun(TestCase):
    def test_push_commit_on_master(testcase):
        """Try pushing new branch on remote.

        In this situation, release-0.1-branch is a branch containing
        several commits attached to the HEAD of the master branch
        (master does not have any commit that release-0.1-branch does
        not have).
        """
        cd ('%s/repo' % TEST_DIR)

        p = testcase.run('git push origin release-0.1-branch'.split())
        expected_out = """\
remote: *** cvs_check: `repo' < `b'
remote: *** pre-commit check failed for commit: 4205e52273adad6b014e19fb1cf1fe1c9b8b4089
remote: *** cvs_check: `repo' < `a' `c' `d'
remote: *** ERROR: c: Copyright year in header is not up to date
remote: error: hook declined to update refs/heads/release-0.1-branch
To ../bare/repo.git
 ! [remote rejected] release-0.1-branch -> release-0.1-branch (hook declined)
error: failed to push some refs to '../bare/repo.git'
"""

        assert p.status != 0, p.image
        testcase.assertRunOutputEqual(p, expected_out)

        # Verify that the branch does not exist on the remote...

        cd('%s/bare/repo.git' % TEST_DIR)

        p = testcase.run('git show-ref -s release-0.1-branch'.split())

        assert p.status != 0, p.image


if __name__ == '__main__':
    runtests()
