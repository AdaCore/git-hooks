from support import *
import os

class TestRun(TestCase):
    def test_push_commit_on_master(self):
        """Try pushing one single-file commit on master.
        """
        cd ('%s/repo' % TEST_DIR)

        self.set_debug_level(1)

        # Push master to the `origin' remote.  The delta should be one
        # commit with one file being modified.
        p = Run('git push origin master'.split())

        self.assertTrue(p.status == 0, ex_run_image(p))

        expected_out = (
            r".*\(combined style checking\)" +
            r".*cvs_check: `trunk/repo/a'" +
            ".*master\s+->\s+master")

        self.assertTrue(re.match(expected_out, p.out, re.DOTALL),
                        ex_run_image(p))

if __name__ == '__main__':
    runtests()
