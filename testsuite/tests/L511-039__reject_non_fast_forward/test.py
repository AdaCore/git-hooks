from support import *

class TestRun(TestCase):
    def test_push_commit_on_master(self):
        """Try non-fast-forward push on master.
        """
        cd ('%s/repo' % TEST_DIR)

        p = Run('git push origin master'.split())

        self.assertTrue(p.status != 0, ex_run_image(p))

        expected_out = (
            r".*\[rejected\]\s+master\s+->\s+master\s+\(non-fast-forward\)")

        self.assertTrue(re.match(expected_out, p.out, re.DOTALL),
                        ex_run_image(p))

if __name__ == '__main__':
    runtests()
