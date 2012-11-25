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

        self.assertTrue(p.status == 0, p.image)

        expected_out = (
            # Traces of the cvs_check updates...
            r".*check_commit.*new_rev=4f0f08f46daf6f5455cf90cdc427443fe3b32fa3"
            r".*cvs_check: `trunk/repo/a'"
            r".*cvs_check: `trunk/repo/b'"
            r".*cvs_check: `trunk/repo/c'"
            r".*check_commit.*new_rev=4a325b31f594b1dc2c66ac15c4b6b68702bd0cdf"
            r".*cvs_check: `trunk/repo/c'"
            r".*cvs_check: `trunk/repo/d'"
            r".*check_commit.*new_rev=cc8d2c2637bda27f0bc2125181dd2f8534d16222"
            r".*cvs_check: `trunk/repo/c'"
            r".*check_commit.*new_rev=dd6165c96db712d3e918fb5c61088b171b5e7cab"
            r".*cvs_check: `trunk/repo/d'"

            # The warning that explains that emails are not going to
            # be sent.
            r".*The hooks\.noemails config parameter contains"
            r".*Commit emails will therefore not be sent\."

            # Proof that the branch was updated as expected.
            r".*\s+426fba3\.\.dd6165c\s+master\s+->\s+master"
            )

        self.assertTrue(re.match(expected_out, p.cmd_out, re.DOTALL),
                        p.image)

        # Just to make sure, verify that we don't have any trace
        # of anything that looks like an email might have been sent.
        self.assertFalse("From:" in p.cmd_out, p.image)
        self.assertFalse("To:" in p.cmd_out, p.image)
        self.assertFalse("Subject:" in p.cmd_out, p.image)


if __name__ == '__main__':
    runtests()
