from difflib import unified_diff
from support import *


class TestRun(TestCase):
    def test_multiline_git_config(testcase):
        """Check that we handle multiline configs correctly"""
        testcase.enable_unit_test()

        cd("%s/bare/repo.git" % TEST_DIR)

        import config

        # Force the default "hooks.no-emails" to the empty tuple.
        # That way, this unit test is independent of whatever default
        # we actually use in real life.
        config.GIT_CONFIG_OPTS["hooks.no-emails"]["default"] = ()

        config.initialize_git_config_map()
        no_emails = config.git_config("hooks.no-emails")

        # no_emails should be 1-element tuple. Verify that and then
        # just keep that first element.
        testcase.assertEqual(
            len(no_emails),
            1,
            "ERROR: hooks.no-emails should be 1 element only:\n%s" % str(no_emails),
        )
        no_emails = no_emails[0]

        expected_no_emails = """\
a multiline description
of my project which should be
handled properly by the git-hooks."""
        testcase.assertEqual(
            expected_no_emails,
            no_emails,
            "%s\n\nDiff:\n\n%s"
            % (
                no_emails,
                "\n".join(
                    unified_diff(
                        a=expected_no_emails.splitlines(),
                        b=no_emails.splitlines(),
                        fromfile="expected",
                        tofile="actual",
                        lineterm="",
                    )
                ),
            ),
        )


if __name__ == "__main__":
    runtests()
