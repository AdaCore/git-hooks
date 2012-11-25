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
            r".*cvs_check: `trunk/repo/b'" +
            r".*cvs_check: `trunk/repo/a'" +
            r".*cvs_check: `trunk/repo/c'" +
            r".*cvs_check: `trunk/repo/d'" +
            r".*\[new branch\]\s+release-0\.1-branch -> release-0\.1-branch")

        self.assertTrue(re.match(expected_out, p.cmd_out, re.DOTALL),
                        p.image)

        # Verify that the branch has been created in the remote
        # repository and that it points to the expected commit.

        cd('%s/bare/repo.git' % TEST_DIR)

        p = Run('git show-ref -s release-0.1-branch'.split())

        self.assertTrue(p.status == 0, p.image)

        expected_out = (r"4205e52273adad6b014e19fb1cf1fe1c9b8b4089")

        self.assertTrue(re.match(expected_out, p.cmd_out, re.DOTALL),
                        p.image)

if __name__ == '__main__':
    runtests()
