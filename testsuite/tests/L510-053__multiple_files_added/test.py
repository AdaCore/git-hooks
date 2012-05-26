from support import *

class TestRun(TestCase):
    def test_push_commit_on_master(self):
        """Try pushing commit on master.
        """
        cd ('%s/repo' % TEST_DIR)

        p = Run('git push origin master'.split())

        self.assertTrue(p.status == 0, ex_run_image(p))

        expected_out = (
            r".*cvs_check: `trunk/repo/pck.adb'" +
            r".*cvs_check: `trunk/repo/pck.ads'" +
            r".*cvs_check: `trunk/repo/types.ads'" +
            ".*master\s+->\s+master")

        self.assertTrue(re.match(expected_out, p.out, re.DOTALL),
                        ex_run_image(p))

if __name__ == '__main__':
    runtests()
