from support import *

class TestRun(TestCase):
    def test_push_commit_on_master(self):
        """Try pushing multiple commits on master.
        """
        cd ('%s/repo' % TEST_DIR)

        # Enable debug traces.  We use them to make certain verifications,
        # such as verifying that each commit gets checked individually.
        self.set_debug_level(2)

        p = Run('git push origin master'.split())

        self.assertTrue(p.status == 0, p.image)

        expected_out = (
            r".*DEBUG: deleted file ignored: foo.c" +
            r".*\s+f826248\.\.adb8ffe\s+master\s+->\s+master")

        self.assertTrue(re.match(expected_out, p.cmd_out, re.DOTALL),
                        p.image)

if __name__ == '__main__':
    runtests()
