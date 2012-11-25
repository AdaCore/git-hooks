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
            r".*cvs_check: `trunk/repo/b'" +
            r".*cvs_check: `trunk/repo/c'" +
            r".*\s+426fba3\.\.4f0f08f\s+master\s+->\s+master")

        self.assertTrue(re.match(expected_out, p.cmd_out, re.DOTALL),
                        p.image)

if __name__ == '__main__':
    runtests()
