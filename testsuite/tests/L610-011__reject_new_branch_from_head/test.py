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

        self.assertTrue(p.status != 0, ex_run_image(p))

        expected_out = (
            r".*cvs_check: `trunk/repo/a'" +
            r".*cvs_check: `trunk/repo/d'" +
            r".*cvs_check: `trunk/repo/a'" +
            r".*pre-commit check failed for file `b' at commit: " +
                "dcc477c258baf8cf59db378fcc344dc962ad9a29" +
            r".*cvs_check: `trunk/repo/b'" +
            r".*ERROR: style-check error detected" +
            r".*ERROR: Copyright year in header is not up to date" +
            r".*\[remote rejected\]\s+" +
                r"release-0\.1-branch\s+->\s+release-0\.1-branch\s+" +
                r"\(hook declined\)")

        self.assertTrue(re.match(expected_out, p.out, re.DOTALL),
                        ex_run_image(p))

        # Verify that the branch does not exist on the remote...

        cd('%s/bare/repo.git' % TEST_DIR)

        p = Run('git show-ref -s release-0.1-branch'.split())

        self.assertTrue(p.status != 0, ex_run_image(p))


if __name__ == '__main__':
    runtests()
