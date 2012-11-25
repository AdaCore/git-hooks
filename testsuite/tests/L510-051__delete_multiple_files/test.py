from support import *

class TestRun(TestCase):
    def test_push_commit_on_master(self):
        """Try pushing commit on master.
        """
        cd ('%s/repo' % TEST_DIR)

        # Enable debug traces.  We use them to make certain verifications,
        # such as verifying that certain files are not being checked
        # because they are being deleted.
        self.set_debug_level(2)

        p = Run('git push origin master'.split())

        self.assertTrue(p.status == 0, ex_run_image(p))

        expected_out = (
            r".*check_commit.*new_rev=0c702ad3051f00b1251bca7a0241a3a9bf19bf0d" +
            r".*deleted file ignored: a\.adb" +
            r".*deleted file ignored: b\.adb" +
            r".*\s+f826248\.\.0c702ad\s+master\s+->\s+master")

        self.assertTrue(re.match(expected_out, p.out, re.DOTALL),
                        ex_run_image(p))

if __name__ == '__main__':
    runtests()
