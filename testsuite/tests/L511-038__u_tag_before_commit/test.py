from support import *

class TestRun(TestCase):
    def test_push_commit_on_master(self):
        """Try pushing tag referencing new commit.
        """
        cd ('%s/repo' % TEST_DIR)

        # We need some debug traces to be enabled, in order to verify
        # certain assertions.
        os.environ['GIT_HOOKS_DEBUG_LEVEL'] = '1'

        # Scenario: The user made some changes, and then committed them
        # in his repo. Then created a lightweight tag (release-0.1a).
        # Next, he pushes the lightweight tag before having pushed his
        # new commit.  What the commit hooks should do in this case
        # is just accept the lightweight tag, but not check the commits
        # (see later for when these commits should be checked).
        #
        # Note: The remote repository has been configured to allow
        # unnanotated tags.

        p = Run('git push origin version-0.1a'.split())

        self.assertTrue(p.status == 0, ex_run_image(p))

        expected_out = (
            r".*\s+\[new tag\]\s+version-0.1a\s+->\s+version-0.1a")
        self.assertTrue(re.match(expected_out, p.out, re.DOTALL),
                        ex_run_image(p))

        # Also verify from the output that none of the commits get
        # checked.  For that, rely on the check_commit debug trace.

        self.assertFalse(re.match(r"DEBUG: check_commit\(", p.out, re.DOTALL),
                         ex_run_image(p))

        # Next, push the changes. Make sure that the commit gets checked.

        p = Run('git push origin master'.split())

        self.assertTrue(p.status == 0, ex_run_image(p))

        expected_out = (
            r".*check_commit(.*" \
                + "new_rev=4f0f08f46daf6f5455cf90cdc427443fe3b32fa3)"
            r".*cvs_check: `trunk/repo/a'" +
            r".*cvs_check: `trunk/repo/b'" +
            r".*cvs_check: `trunk/repo/c'" +
            r".*\s+426fba3\.\.4f0f08f\s+master\s+->\s+master")

        self.assertTrue(re.match(expected_out, p.out, re.DOTALL),
                        ex_run_image(p))

if __name__ == '__main__':
    runtests()
