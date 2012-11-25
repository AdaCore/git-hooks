from support import *

class TestRun(TestCase):
    def test_push_commit_on_master(self):
        """Try pushing new branch on remote.

        In this testcase, the release-0.1-branch points to a commit
        that's one of the older commits in the "master" branch.
        """
        cd ('%s/repo' % TEST_DIR)

        p = Run('git push origin release-0.1-branch'.split())

        self.assertTrue(p.status == 0, p.image)

        expected_out = (
            r".*\[new branch\]\s+release-0\.1-branch -> release-0\.1-branch")

        self.assertTrue(re.match(expected_out, p.cmd_out, re.DOTALL),
                        p.image)

        # Verify that the branch has been created in the remote
        # repository and that it points to the expected commit.

        cd('%s/bare/repo.git' % TEST_DIR)

        p = Run('git show-ref -s release-0.1-branch'.split())

        self.assertTrue(p.status == 0, p.image)

        expected_out = (r"4a325b31f594b1dc2c66ac15c4b6b68702bd0cdf")

        self.assertTrue(re.match(expected_out, p.cmd_out, re.DOTALL),
                        p.image)

if __name__ == '__main__':
    runtests()
