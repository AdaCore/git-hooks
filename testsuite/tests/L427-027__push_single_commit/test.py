from support import *

class TestRun(TestCase):
    def test_push_commit_on_master(self):
        """Try pushing one single-file commit on master.
        """
        cd ('%s/repo' % TEST_DIR)

        # Push master to the `origin' remote.  The delta should be one
        # commit with one file being modified.
        p = Run('git push origin master'.split())

        self.assertTrue(p.status == 0, p.image)

        expected_out = (
            r".*cvs_check: `trunk/repo/a'" +
            ".*master\s+->\s+master")

        self.assertTrue(re.match(expected_out, p.cmd_out, re.DOTALL),
                        p.image)

if __name__ == '__main__':
    runtests()
