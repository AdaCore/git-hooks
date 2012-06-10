from support import *

class TestRun(TestCase):
    def test_push_commit_on_master(self):
        """Try pushing new branch on remote.

        In this situation, release-0.1-branch points to the same
        commit as the master branch.
        """
        cd ('%s/repo' % TEST_DIR)

        p = Run('git push origin release-0.1-branch'.split())

        self.assertTrue(p.status == 0, ex_run_image(p))

        expected_out = (
            r".*\[new branch\]\s+release-0\.1-branch -> release-0\.1-branch")

        self.assertTrue(re.match(expected_out, p.out, re.DOTALL),
                        ex_run_image(p))

        # Verify that the branch has been created in the remote
        # repository and that it points to the expected commit.

        cd('%s/bare/repo.git' % TEST_DIR)

        p = Run('git show-ref -s release-0.1-branch'.split())

        self.assertTrue(p.status == 0, ex_run_image(p))

        expected_out = (r"dd6165c96db712d3e918fb5c61088b171b5e7cab")

        self.assertTrue(re.match(expected_out, p.out, re.DOTALL),
                        ex_run_image(p))

if __name__ == '__main__':
    runtests()
