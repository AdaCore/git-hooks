from support import *
import os

class TestRun(TestCase):
    def test_push(self):
        """Try pushing head-less branch (called "headless") on master.
        Same with head-less branch (called "one-commit") on master.
        The test with the "one-commit" branch is just to test the
        situation where the new head-less branch only has one commit.
        """
        cd ('%s/repo' % TEST_DIR)

        # Enable debugs to verify that the hooks pick the correct
        # commit as the first commit.
        os.environ['GIT_HOOKS_DEBUG_LEVEL'] = '1'

        # First, push the headless branch.

        p = Run('git push origin headless'.split())

        self.assertTrue(p.status == 0, ex_run_image(p))

        expected_out = (
            r".*validate_ref_update \(refs/heads/headless, 0+, " +
                "902092ffe1cf61b28e28c86949a447b9fc2591a4\)" +
            r".*update base: None" +
            r".*\(combined style checking\)" +
            r".*check_commit\(old_rev=None, " +
                "new_rev=902092ffe1cf61b28e28c86949a447b9fc2591a4\)" +
            r".*cvs_check: `trunk/repo/that\.txt'" +
            r".*cvs_check: `trunk/repo/there'" +
            r".*cvs_check: `trunk/repo/this\.txt'" +
            ".*\[new branch\]\s+headless\s+->\s+headless")

        self.assertTrue(re.match(expected_out, p.out, re.DOTALL),
                        ex_run_image(p))

        # Next, push the one-commit branch.

        p = Run('git push origin one-commit'.split())

        self.assertTrue(p.status == 0, ex_run_image(p))

        expected_out = (
            r".*validate_ref_update \(refs/heads/one-commit, 0+, " +
                "ef3ab848df2bef804d5bd0880475d40cb6aab0bf\)" +
            r".*update base: None" +
            r".*\(combined style checking\)" +
            r".*check_commit\(old_rev=None, " +
                "new_rev=ef3ab848df2bef804d5bd0880475d40cb6aab0bf\)" +
            r".*cvs_check: `trunk/repo/contents\.txt'" +
            r".*cvs_check: `trunk/repo/stuff'" +
            ".*\[new branch\]\s+one-commit\s+->\s+one-commit")

        self.assertTrue(re.match(expected_out, p.out, re.DOTALL),
                        ex_run_image(p))

if __name__ == '__main__':
    runtests()
