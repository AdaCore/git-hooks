from support import *

class TestRun(TestCase):
    def test_push_commit_on_master(self):
        """Try non-fast-forward push on master.
        """
        cd ('%s/repo' % TEST_DIR)

        p = Run('git push -f origin topic/new-feature'.split())

        self.assertTrue(p.status == 0, ex_run_image(p))

        expected_out = (
            r".*WARNING: This is \*NOT\* a fast-forward update." +
            r".*cvs_check: `trunk/repo/a'" +
            r".*cvs_check: `trunk/repo/b'" +
            r".*a605403\.\.\.14d1fa2\s+" +
                r"topic/new-feature\s+->\s+topic/new-feature\s+" +
                r"\(forced update\)")

        self.assertTrue(re.match(expected_out, p.out, re.DOTALL),
                        ex_run_image(p))

if __name__ == '__main__':
    runtests()
