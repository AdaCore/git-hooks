from support import *

class TestRun(TestCase):
    def test_push_commit_on_master(self):
        """Try non-fast-forward push on master.
        """
        cd ('%s/repo' % TEST_DIR)

        p = Run('git push -f origin topic/new-feature'.split())

        self.assertTrue(p.status != 0, p.image)

        expected_out = (
            r".*WARNING: This is \*NOT\* a fast-forward update." +
            r".*cvs_check: `trunk/repo/a'" +
            r".*pre-commit check failed for file `b'" +
            r".*cvs_check: `trunk/repo/b'" +
            r".*ERROR: style-check error detected" +
            r".*error: hook declined to update refs/heads/topic/new-feature" +
            r".*\[remote rejected\]\s+" +
            r"topic/new-feature\s+->\s+topic/new-feature\s+" +
                r"\(hook declined\)")

        self.assertTrue(re.match(expected_out, p.cmd_out, re.DOTALL),
                        p.image)

if __name__ == '__main__':
    runtests()
