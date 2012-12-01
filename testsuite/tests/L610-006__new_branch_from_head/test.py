from support import *

class TestRun(TestCase):
    def test_push_commit_on_master(self):
        """Try pushing new branch on remote.

        In this situation, release-0.1-branch is a branch containing
        several commits attached to the HEAD of the master branch
        (master does not have any commit that release-0.1-branch does
        not have).
        """
        cd ('%s/repo' % TEST_DIR)

        p = Run('git push origin release-0.1-branch'.split())
        expected_out = """\
remote: *** cvs_check: `trunk/repo/a'
remote: *** cvs_check: `trunk/repo/d'
remote: *** cvs_check: `trunk/repo/a'
remote: *** cvs_check: `trunk/repo/b'
remote: *** email notification for new commits not implemented yet.
To ../bare/repo.git
 * [new branch]      release-0.1-branch -> release-0.1-branch
"""

        self.assertTrue(p.status == 0, p.image)
        self.assertEqual(expected_out, p.cmd_out, p.image)

        # Verify that the branch has been created in the remote
        # repository and that it points to the expected commit.

        cd('%s/bare/repo.git' % TEST_DIR)

        p = Run('git show-ref -s release-0.1-branch'.split())
        expected_out = """\
dcc477c258baf8cf59db378fcc344dc962ad9a29
"""

        self.assertTrue(p.status == 0, p.image)
        self.assertEqual(expected_out, p.cmd_out, p.image)


if __name__ == '__main__':
    runtests()
