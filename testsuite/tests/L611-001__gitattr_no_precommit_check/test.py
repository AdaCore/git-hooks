from support import *

class TestRun(TestCase):
    def test_push_commit_on_master(self):
        """Try pushing multi-file commit on master.
        """
        cd ('%s/repo' % TEST_DIR)

        p = Run('git push origin master'.split())

        self.assertTrue(p.status == 0, p.image)

        expected_out = (
            r".*cvs_check: `trunk/repo/a'" +
            r".*cvs_check: `trunk/repo/c'" +
            r".*\s+c8c2f45\.\.8b4778c\s+master\s+->\s+master")

        self.assertTrue(re.match(expected_out, p.cmd_out, re.DOTALL),
                        p.image)

        # Check that cvs_check was NOT called for file `b'.
        self.assertTrue("cvs_check: `trunk/repo/b'" not in p.cmd_out)

if __name__ == '__main__':
    runtests()
