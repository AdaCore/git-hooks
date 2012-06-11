from support import *

class TestRun(TestCase):
    def test_push_commit_on_master(self):
        """Try pushing multi-file commit on master.
        """
        cd ('%s/repo' % TEST_DIR)

        p = Run('git push origin master'.split())

        self.assertTrue(p.status == 0, ex_run_image(p))

        expected_out = (
            r".*cvs_check: `trunk/repo/a'" +
            r".*cvs_check: `trunk/repo/c'" +
            r".*\s+c8c2f45\.\.8b4778c\s+master\s+->\s+master")

        self.assertTrue(re.match(expected_out, p.out, re.DOTALL),
                        ex_run_image(p))

        # Check that cvs_check was NOT called for file `b'.
        self.assertTrue("cvs_check: `trunk/repo/b'" not in p.out)

if __name__ == '__main__':
    runtests()
