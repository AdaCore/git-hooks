from support import *

class TestRun(TestCase):
    def test_push_commit_on_master(self):
        """Try pushing multiple commits on master.
        """
        cd ('%s/repo' % TEST_DIR)

        # Enable debug traces.  We use them to make certain verifications,
        # such as verifying that each commit gets checked individually.
        self.set_debug_level(1)

        p = Run('git push origin master'.split())

        self.assertTrue(p.status == 0, ex_run_image(p))

        expected_out = (
            r".*\(combined style checking\)" +
            r".*check_commit\(" +
                r"old_rev=426fba3571947f6de7f967e885a3168b9df7004a, " +
                r"new_rev=dd6165c96db712d3e918fb5c61088b171b5e7cab\)" +
            r".*cvs_check: `trunk/repo/a'" +
            r".*cvs_check: `trunk/repo/c'" +
            r".*cvs_check: `trunk/repo/d'" +
            r".*\s+426fba3\.\.dd6165c\s+master\s+->\s+master")

        self.assertTrue(re.match(expected_out, p.out, re.DOTALL),
                        ex_run_image(p))

        # One of the commits being pushed delete file `b', and the file
        # is not being re-created, so verify that it never gets checked.
        self.assertTrue("cvs_check: `trunk/repo/b'" not in p.out,
                         ex_run_image(p))


if __name__ == '__main__':
    runtests()
