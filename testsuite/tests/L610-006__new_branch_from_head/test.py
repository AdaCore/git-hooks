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

        self.assertTrue(p.status == 0, p.image)

        expected_out = (
            r".*cvs_check: `trunk/repo/a'" +
            r".*cvs_check: `trunk/repo/d'" +
            r".*cvs_check: `trunk/repo/a'" +
            r".*cvs_check: `trunk/repo/b'" +
            r".*\[new branch\]\s+release-0\.1-branch -> release-0\.1-branch")

        self.assertTrue(re.match(expected_out, p.cmd_out, re.DOTALL),
                        p.image)

        # Verify that the branch has been created in the remote
        # repository and that it points to the expected commit.

        cd('%s/bare/repo.git' % TEST_DIR)

        p = Run('git show-ref -s release-0.1-branch'.split())

        self.assertTrue(p.status == 0, p.image)

        expected_out = (r"dcc477c258baf8cf59db378fcc344dc962ad9a29")

        self.assertTrue(re.match(expected_out, p.cmd_out, re.DOTALL),
                        p.image)

if __name__ == '__main__':
    runtests()
